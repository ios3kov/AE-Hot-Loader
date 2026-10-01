"""Offline unit tests for the bounded Stage C1 ABI collector."""
from pathlib import Path
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "experiments/ordinary_discovery/collect_resource_search_abi.py"
spec = importlib.util.spec_from_file_location("resource_abi_collector", MODULE)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ResourceAbiCollectorTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", "requires macOS arm64 file disassembly")
    def test_real_lldb_disassembles_owned_bounded_window(self):
        with tempfile.TemporaryDirectory(prefix="aehl-owned-abi-") as tmp:
            folder = Path(tmp).resolve()
            source = folder / "owned.s"
            source.write_text(".text\n.globl _owned_abi_probe\n.p2align 2\n"
                              "_owned_abi_probe:\n add w0, w0, #1\n ret\n")
            binary = folder / "owned.bundle"
            subprocess.run(["/usr/bin/xcrun", "clang", "-arch", "arm64", "-bundle",
                            str(source), "-o", str(binary)], check=True,
                           capture_output=True, timeout=45)
            symbols = subprocess.check_output(["/usr/bin/nm", "-arch", "arm64", "-n",
                                               str(binary)], text=True, timeout=15)
            match = re.search(r"^([0-9a-fA-F]+)\s+T\s+_owned_abi_probe$", symbols, re.M)
            self.assertIsNotNone(match, symbols)
            start = int(match.group(1), 16)
            script = folder / "inspect.lldb"
            script.write_text(collector.lldb_script(binary, start, start + 8))
            output, diagnostics = collector.run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch", "--source", str(script)])
            self.assertNotIn("error:", (output + diagnostics).lower())
            self.assertRegex(output, r"add\s+w0, w0, #0x1")
            self.assertRegex(output, r"\bret\b")

    def test_profile_pins_agree_with_header(self):
        collector.profile_agrees()

    def test_lldb_script_is_bounded_and_offline(self):
        path = Path("/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib")
        script = collector.lldb_script(path, 0x8A6C, 0x8C20)
        self.assertIn("target create --no-dependents --arch arm64", script)
        self.assertIn("disassemble --start-address 0x8a6c --end-address 0x8c20\n", script)
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
