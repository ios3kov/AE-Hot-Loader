"""Portable no-scan transaction/journal gate; no Adobe code is loaded."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NoScanDirectoryGateTests(unittest.TestCase):
    def test_native_gate_and_journal(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler, 'C++ compiler is required')
        root = Path(__file__).resolve().parents[1]
        source = root / 'tests/no_scan_directory_gate.cpp'
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-gate-') as temporary:
            binary = Path(temporary) / 'gate-tests'
            result = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(source), '-o', str(binary)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=25, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(result.stdout.strip(),
                             'NO_SCAN_DIRECTORY_GATE_TESTS=11 PASS; Adobe calls=0')
            print(result.stdout, end='')


if __name__ == '__main__':
    unittest.main()
