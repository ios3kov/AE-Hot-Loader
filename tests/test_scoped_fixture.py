import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "scoped", Path(__file__).resolve().parents[1] /
    "experiments/ordinary_discovery/verify_scoped_fixture.py")
scoped = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoped)


class ScopedFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.base.chmod(0o700)
        self.root = self.base / "scan-root"
        self.bundle = self.root / "AEHLPairEmbedded123456789abc.plugin"
        resource = self.bundle / "Contents/Resources/AEHLPairEmbedded123456789abc.rsrc"
        resource.parent.mkdir(parents=True)
        self.root.chmod(0o700)
        resource.write_bytes(b"embedded")
        self.manifest = self.base / "manifest.json"
        self.record = {
            "pair_kind": "embedded", "fixture_scope": "single-owned-embedded-root",
            "scan_root": "scan-root", "source_state": "",
            "run_id": "123456789abc", "commit": "f" * 40,
            "probes": [{"bundle": "scan-root/" + self.bundle.name,
                        "resource_representation": "rsrc",
                        "match": "AEHL.Embedded.123456789abc",
                        "files": {"Contents/Resources/AEHLPairEmbedded123456789abc.rsrc":
                                  hashlib.sha256(b"embedded").hexdigest()}}],
        }
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.record))
        self.manifest.chmod(0o600)

    def test_exact_owned_root_passes(self):
        self.assertEqual(scoped.verify(self.manifest, self.base.parent)["status"], "PASS")

    def test_extra_bundle_fails(self):
        (self.root / "other.plugin").mkdir()
        with self.assertRaisesRegex(ValueError, "extra entries"):
            scoped.verify(self.manifest, self.base.parent)

    def test_changed_bytes_fail(self):
        (self.bundle / "Contents/Resources/AEHLPairEmbedded123456789abc.rsrc").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            scoped.verify(self.manifest, self.base.parent)

    def test_flat_resource_fails(self):
        flat = self.bundle / "Contents/Resources/16000.PiPL"
        flat.write_bytes(b"flat")
        self.record["probes"][0]["files"][str(flat.relative_to(self.bundle))] = scoped.sha256(flat)
        self.save()
        with self.assertRaisesRegex(ValueError, "flat .PiPL"):
            scoped.verify(self.manifest, self.base.parent)

    def test_symlink_fails(self):
        (self.bundle / "Contents/Resources/link").symlink_to("AEHLPairEmbedded123456789abc.rsrc")
        with self.assertRaisesRegex(ValueError, "symlink"):
            scoped.verify(self.manifest, self.base.parent)

    def test_dirty_or_escape_fails(self):
        self.record["source_state"] = " M source.cpp"
        self.save()
        with self.assertRaisesRegex(ValueError, "dirty"):
            scoped.verify(self.manifest, self.base.parent)
        self.record["source_state"] = ""
        self.record["probes"][0]["bundle"] = "../other.plugin"
        self.save()
        with self.assertRaisesRegex(ValueError, "escapes"):
            scoped.verify(self.manifest, self.base.parent)

    def test_historical_or_malformed_identity_fails(self):
        self.record["probes"][0]["match"] = "AEHL.Embedded.88019a1a01a7"
        self.save()
        with self.assertRaisesRegex(ValueError, "not fresh"):
            scoped.verify(self.manifest, self.base.parent)
        self.record["probes"][0]["match"] = "AEHL.Embedded.123456789abc"
        self.record["run_id"] = "abc"
        self.save()
        with self.assertRaisesRegex(ValueError, "run id"):
            scoped.verify(self.manifest, self.base.parent)

    def test_private_modes_required(self):
        self.manifest.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "manifest must be owned/private"):
            scoped.verify(self.manifest, self.base.parent)
        self.manifest.chmod(0o600)
        self.root.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "scan root must be owned/private"):
            scoped.verify(self.manifest, self.base.parent)

    def test_unowned_base_fails(self):
        with self.assertRaisesRegex(ValueError, "owned base"):
            scoped.verify(self.manifest, self.base)
