"""Typed refusal stages from actual resolver, owned files and own-process memory."""
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = sys.platform == 'darwin' and platform.machine() == 'arm64'


class BindingDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='aehl-binding-diagnostics-')
        cls.base = Path(cls.tmp.name).resolve()
        cls.driver = cls.base / 'driver'
        cls.run_command(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                         '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                         str(ROOT / 'tests/resident_binding_diagnostics.cpp'), '-o', str(cls.driver)])
        if NATIVE:
            cls.library = cls.base / 'owned.dylib'
            source = cls.base / 'owned.cpp'
            source.write_text('extern "C" int AEHL_OwnUnused() { return 73; }\n')
            cls.run_command(['clang++', '-arch', 'arm64', '-dynamiclib', str(source),
                             '-o', str(cls.library), '-Wl,-install_name,' + str(cls.library)])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def run_command(args):
        result = subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
        if result.returncode:
            raise AssertionError(result.stderr.decode(errors='replace'))
        return result.stdout

    def test_context_preserves_specific_refusal_and_allocation(self):
        self.assertIn(b'PASS binding predicate diagnostics', self.run_command([str(self.driver), 'context']))

    @unittest.skipUnless(NATIVE, 'requires macOS arm64 self-memory and file contract')
    def test_file_and_memory_predicates_keep_strict_failures(self):
        before = self.library.read_bytes()
        self.assertIn(b'PASS binding predicate diagnostics',
                      self.run_command([str(self.driver), str(self.library), 'files-memory']))
        self.assertEqual(self.library.read_bytes(), before)

    @unittest.skipUnless(NATIVE, 'requires macOS arm64 owned resident image')
    def test_actual_resident_success_missing_export_hash_and_worker(self):
        self.assertIn(b'PASS binding predicate diagnostics',
                      self.run_command([str(self.driver), str(self.library), 'resident']))


if __name__ == '__main__':
    unittest.main()
