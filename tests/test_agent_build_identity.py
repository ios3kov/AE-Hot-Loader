"""Generator tests use owned temporary Git repositories, not user state or AE."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("agent_build_identity", Path(__file__).parents[1] / "tools/agent_build_identity.py")
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aehl-identity-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Identity Test")
        self.run_git("config", "user.email", "test@example.invalid")
        for component in ("core", "agent"):
            (self.root / component).mkdir()
            (self.root / component / "Cargo.lock").write_text("version = 4\n")
        self.commit()
        self.env = {"TARGET": "aarch64-apple-darwin", "CARGO_PKG_VERSION": "0.1.0", "PACKAGE_BUILD_ID": "test-123-1"}

    def run_git(self, *args):
        return identity.git(self.root, *args)

    def commit(self):
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "fixture")

    def test_clean_identity_and_lock_hash(self):
        data = identity.make_identity(self.root, self.env)
        self.assertEqual(data["git_commit"], self.run_git("rev-parse", "HEAD"))
        self.assertIs(data["source_clean"], True)
        self.assertEqual(data["dependency_lock_sha256"], hashlib.sha256(b"version = 4\n").hexdigest())
        self.assertEqual(data["loader_path_id"], "ordinary-discovery-v1")

    def test_deterministic_and_json_roundtrip(self):
        lines = identity.cargo_lines(self.root, self.env)
        self.assertEqual(lines, identity.cargo_lines(self.root, self.env))
        self.assertEqual(json.loads(lines[0].split("=", 2)[2]), identity.make_identity(self.root, self.env))

    def test_uncommitted_source_rejected(self):
        (self.root / "agent/Cargo.lock").write_text("version = 3\n")
        with self.assertRaises(ValueError):
            identity.make_identity(self.root, self.env)

    def test_untracked_source_rejected(self):
        (self.root / "surprise.rs").write_text("untracked")
        with self.assertRaises(ValueError):
            identity.make_identity(self.root, self.env)

    def test_explicit_dirty_experiment_is_marked(self):
        (self.root / "surprise.rs").write_text("untracked")
        self.env["AEHL_ALLOW_DIRTY"] = "1"
        self.assertIs(identity.make_identity(self.root, self.env)["source_clean"], False)

    def test_ci_never_accepts_dirty_override(self):
        (self.root / "surprise.rs").write_text("untracked")
        self.env.update(CI="true", AEHL_ALLOW_DIRTY="1")
        with self.assertRaises(ValueError):
            identity.make_identity(self.root, self.env)

    def test_foreign_expected_commit_rejected(self):
        self.env["GITHUB_SHA"] = "0" * 40
        with self.assertRaises(ValueError):
            identity.make_identity(self.root, self.env)

    def test_build_id_injection_and_length_rejected(self):
        for value in ("bad\nidentity", "a=b", "x" * 129, "", "../../bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                identity.make_identity(self.root, {**self.env, "PACKAGE_BUILD_ID": value})

    def test_invalid_target_and_version_rejected(self):
        for key, value in (("TARGET", "x86_64-apple-darwin"), ("CARGO_PKG_VERSION", "0.1\nFAIL")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                identity.make_identity(self.root, {**self.env, key: value})

    def test_detached_checkout_watches_head(self):
        self.run_git("checkout", "-q", "--detach")
        lines = identity.cargo_lines(self.root, self.env)
        self.assertTrue(any(line.endswith("/.git/HEAD") for line in lines))

    def test_ref_and_environment_inputs_are_watched(self):
        lines = identity.cargo_lines(self.root, self.env)
        self.assertIn("cargo:rerun-if-env-changed=PACKAGE_BUILD_ID", lines)
        self.assertTrue(any("/.git/refs/heads/" in line for line in lines))
        self.assertTrue(any(line.endswith("/agent/Cargo.lock") for line in lines))

    def test_no_git_source_cannot_claim_identity(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(subprocess.SubprocessError):
            identity.make_identity(Path(folder), self.env)

    def test_untracked_lock_cannot_establish_baseline(self):
        self.run_git("rm", "--cached", "agent/Cargo.lock")
        self.run_git("commit", "-qm", "remove lock from Git")
        self.env["AEHL_ALLOW_DIRTY"] = "1"
        with self.assertRaises(subprocess.SubprocessError):
            identity.make_identity(self.root, self.env)

    def test_commit_change_changes_metadata(self):
        before = identity.make_identity(self.root, self.env)
        self.run_git("commit", "--allow-empty", "-qm", "new source identity")
        after = identity.make_identity(self.root, self.env)
        self.assertNotEqual(before["git_commit"], after["git_commit"])


if __name__ == "__main__":
    unittest.main()
