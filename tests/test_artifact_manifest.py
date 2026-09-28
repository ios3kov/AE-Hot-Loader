"""Filesystem tests only; not native or After Effects validation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("manifest", Path(__file__).parents[1] / "tools/artifact_manifest.py")
manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manifest)
SHA = "a" * 40
BUILD = "native-123-1"


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Пакет с пробелами"
        self.root.mkdir()
        self.file = self.root / "компонент.jsx"
        self.file.write_bytes(b"test bytes\x00\xff")

    def make(self):
        return manifest.create(self.root, SHA, BUILD)

    def check(self):
        return manifest.verify(self.root, SHA, BUILD)

    def test_roundtrip_and_no_absolute_paths(self):
        record = self.make()
        self.assertEqual(record, self.check())
        self.assertEqual(set(record["files"]), {"компонент.jsx"})
        self.assertFalse(record["runtime_identity_verified"])

    def test_deterministic_manifest(self):
        self.make()
        first = (self.root / manifest.NAME).read_bytes()
        (self.root / manifest.NAME).unlink()
        self.make()
        self.assertEqual(first, (self.root / manifest.NAME).read_bytes())

    def test_changed_bytes_rejected(self):
        self.make()
        self.file.write_bytes(b"tampered")
        with self.assertRaises(ValueError): self.check()

    def test_added_file_rejected(self):
        self.make()
        (self.root / "extra").write_text("unexpected")
        with self.assertRaises(ValueError): self.check()

    def test_missing_file_rejected(self):
        (self.root / "keep").write_text("keep")
        self.make()
        self.file.unlink()
        with self.assertRaises(ValueError): self.check()

    def test_manifest_not_overwritten(self):
        self.make()
        with self.assertRaises(FileExistsError): self.make()

    def test_invalid_commit_rejected(self):
        with self.assertRaises(ValueError): manifest.create(self.root, "main", BUILD)

    def test_invalid_build_id_rejected(self):
        with self.assertRaises(ValueError): manifest.create(self.root, SHA, "../other")

    def test_wrong_expected_identity_rejected(self):
        self.make()
        with self.assertRaises(ValueError): manifest.verify(self.root, "b" * 40, BUILD)
        with self.assertRaises(ValueError): manifest.verify(self.root, SHA, "other")

    def test_symlink_file_rejected(self):
        (self.root / "link").symlink_to(self.file)
        with self.assertRaises(ValueError): self.make()

    def test_symlink_root_rejected(self):
        link = Path(self.temp.name) / "alias"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError): manifest.create(link, SHA, BUILD)

    def test_symlink_manifest_rejected(self):
        self.make()
        path = self.root / manifest.NAME
        elsewhere = Path(self.temp.name) / "record.json"
        path.rename(elsewhere)
        path.symlink_to(elsewhere)
        with self.assertRaises(ValueError): self.check()

    def test_traversal_and_release_claim_rejected(self):
        self.make()
        path = self.root / manifest.NAME
        record = json.loads(path.read_text())
        record["files"] = {"../../outside": "a" * 64}
        path.write_text(json.dumps(record))
        with self.assertRaises(ValueError): self.check()
        record["files"] = manifest.payload(self.root)
        record["runtime_identity_verified"] = True
        path.write_text(json.dumps(record))
        with self.assertRaises(ValueError): self.check()

    def test_empty_package_rejected(self):
        self.file.unlink()
        with self.assertRaises(ValueError): self.make()


if __name__ == "__main__":
    unittest.main()
