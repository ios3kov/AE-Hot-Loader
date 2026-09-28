"""Tests for the generated ScriptUI artifact; no After Effects runtime involved."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build_panel as panel


class PanelBuildTests(unittest.TestCase):
    def setUp(self):
        self.identity = {
            "component": "agent", "git_commit": "a" * 40, "build_id": "native-123-1",
            "source_clean": True, "target": "aarch64-apple-darwin", "version": "0.1.0",
        }
        self.source = "(function(){\n" + panel.MARKER + "\n})();\n"

    def test_embeds_shared_package_identity_as_panel(self):
        result = panel.render(self.source, self.identity)
        record = json.loads(result.split("var PANEL_IDENTITY = ")[1].split(";")[0])
        self.assertEqual(record, {**self.identity, "component": "panel", "schema_version": 1})
        self.assertNotIn("@AEHL_PANEL_IDENTITY@", result)

    def test_output_deterministic(self):
        self.assertEqual(panel.render(self.source, self.identity), panel.render(self.source, self.identity))

    def test_missing_or_duplicate_marker_rejected(self):
        for source in ("", self.source * 2):
            with self.subTest(source=source), self.assertRaises(ValueError):
                panel.render(source, self.identity)

    def test_already_stamped_panel_cannot_be_relabelled(self):
        with self.assertRaises(ValueError):
            panel.render(panel.render(self.source, self.identity), {**self.identity, "build_id": "another"})

    def test_dirty_or_unknown_agent_identity_rejected(self):
        for change in ({"source_clean": False}, {"source_clean": "true"}, {"component": "other"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                panel.render(self.source, {**self.identity, **change})

    def test_invalid_values_cannot_inject_javascript(self):
        for field, value in (("build_id", '";attack();//'), ("build_id", "x" * 129),
                             ("git_commit", "not-a-commit"), ("version", "0.1.0\nattack"),
                             ("target", "x86_64-apple-darwin"), ("build_id", None)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                panel.render(self.source, {**self.identity, field: value})

    def fixture(self, root):
        for directory in ("agent", "core", "ui", "package"):
            (root / directory).mkdir()
        for directory in ("agent", "core"):
            (root / directory / "Cargo.lock").write_text("version = 4\n")
        (root / "agent/Cargo.toml").write_text('[package]\nversion = "0.1.0"\n')
        (root / "ui/AE Hot Loader.jsx").write_text(self.source)
        (root / ".gitignore").write_text("package/\n")
        for args in (("init", "-q"), ("config", "user.email", "test@example.invalid"),
                     ("config", "user.name", "test"), ("add", "."), ("commit", "-qm", "fixture")):
            subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    def test_real_generator_reads_git_and_does_not_modify_template(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); self.fixture(root)
            source = root / "ui/AE Hot Loader.jsx"
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            output = root / "package/panel.jsx"
            panel.build(root, output, {"PACKAGE_BUILD_ID": "ci-123-1", "CI": "true"})
            head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            self.assertIn(head, output.read_text())
            self.assertIn("ci-123-1", output.read_text())
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            self.assertEqual(subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True), "")

    def test_generator_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); self.fixture(root)
            output = root / "package/panel.jsx"; output.write_text("preserve")
            with self.assertRaises(FileExistsError):
                panel.build(root, output, {})
            self.assertEqual(output.read_text(), "preserve")

    def test_generator_refuses_symlink_destination(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); self.fixture(root)
            output = root / "package/panel.jsx"; output.symlink_to(root / "ui/AE Hot Loader.jsx")
            with self.assertRaises(FileExistsError):
                panel.build(root, output, {})
            self.assertEqual((root / "ui/AE Hot Loader.jsx").read_text(), self.source)

    def test_generator_blocks_dirty_build_before_creating_output(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); self.fixture(root)
            (root / "untracked").write_text("dirty")
            output = root / "package/panel.jsx"
            with self.assertRaises(ValueError):
                panel.build(root, output, {"AEHL_ALLOW_DIRTY": "1"})
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
