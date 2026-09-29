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
        self.root = self.base / "scan-root"
        self.bundle = self.root / "AEHLPairEmbeddedabc.plugin"
        resource = self.bundle / "Contents/Resources/AEHLPairEmbeddedabc.rsrc"
        resource.parent.mkdir(parents=True)
        resource.write_bytes(b"embedded")
        self.manifest = self.base / "manifest.json"
        self.record = {
            "pair_kind": "embedded", "scan_root": "scan-root",
            "source_state": "", "run_id": "abc", "commit": "f" * 40,
            "probes": [{"bundle": "scan-root/" + self.bundle.name,
                        "resource_representation": "rsrc", "match": "AEHL.Embedded.abc",
                        "files": {"Contents/Resources/AEHLPairEmbeddedabc.rsrc":
                                  hashlib.sha256(b"embedded").hexdigest()}}],
        }
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.record))

    def test_exact_owned_root_passes(self):
        self.assertEqual(scoped.verify(self.manifest, self.base.parent)["status"], "PASS")

    def test_extra_bundle_fails(self):
        (self.root / "other.plugin").mkdir()
        with self.assertRaisesRegex(ValueError, "extra entries"):
            scoped.verify(self.manifest, self.base.parent)

    def test_changed_bytes_fail(self):
        (self.bundle / "Contents/Resources/AEHLPairEmbeddedabc.rsrc").write_bytes(b"changed")
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
        (self.bundle / "Contents/Resources/link").symlink_to("AEHLPairEmbeddedabc.rsrc")
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

    def test_unowned_base_fails(self):
        with self.assertRaisesRegex(ValueError, "owned base"):
            scoped.verify(self.manifest, self.base)
