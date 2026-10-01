"""Offline unit tests for the bounded Stage C1 ABI collector."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "experiments/ordinary_discovery/collect_resource_search_abi.py"
spec = importlib.util.spec_from_file_location("resource_abi_collector", MODULE)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ResourceAbiCollectorTests(unittest.TestCase):
    def test_profile_pins_agree_with_header(self):
        collector.profile_agrees()

    def test_lldb_script_is_bounded_and_offline(self):
        path = Path("/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib")
        script = collector.lldb_script(path, 0x8A6C, 0x8C20)
        self.assertIn("target create --no-dependents --arch arm64", script)
        self.assertIn("disassemble --start-address 0x8a6c --end-address 0x8c20 --force", script)
        self.assertNotIn("process launch", script)
        self.assertNotIn("process attach", script)
        with self.assertRaisesRegex(ValueError, "bounded"):
            collector.lldb_script(path, 0x1000, 0x3000)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            collector.lldb_script(Path('/tmp/bad"name'), 0x1000, 0x1100)

    def test_symbol_selection_is_narrow(self):
        text = "\n".join([
            "0000000000001000 (__TEXT,__text) external _PLUG_Search",
            "0000000000002000 (__TEXT,__text) non-external __Z14Egg_PlugSearchv",
            "0000000000003000 (__TEXT,__text) non-external __Z14SearchStatFuncv",
            "0000000000004000 (__TEXT,__text) external _Unrelated",
        ])
        selected = collector.select_symbols(text)
        self.assertIn("PLUG_Search", selected)
        self.assertIn("Egg_PlugSearch", selected)
        self.assertIn("SearchStatFunc", selected)
        self.assertNotIn("Unrelated", selected)

    def test_package_has_exact_hash_manifest(self):
        with tempfile.TemporaryDirectory(prefix="aehl-resource-abi-test-") as tmp:
            folder = Path(tmp) / "evidence"
            folder.mkdir(mode=0o700)
            collector.write_exclusive(folder / "aelib-disassembly.txt", "bounded\n")
            archive = collector.package(folder, {
                "schema": "AEHL-C1-RESOURCE-ABI-1",
                "scope": "offline-bounded-resource-search-abi-only",
            })
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as z:
                names = set(z.namelist())
                self.assertEqual(names, {"aelib-disassembly.txt", "record.json", "SHA256.json"})
                hashes = json.loads(z.read("SHA256.json"))
                self.assertEqual(set(hashes), names - {"SHA256.json"})


if __name__ == "__main__":
    unittest.main()
