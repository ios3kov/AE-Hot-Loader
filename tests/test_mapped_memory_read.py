"""Bounded mapping reader: nested native cases, actual own pages on macOS."""
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


class MappedMemoryTests(unittest.TestCase):
    def test_bounds_changes_failures_and_owned_pages(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-mapped-memory-') as folder:
            binary = Path(folder) / 'mapped'
            r = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                str(Path(__file__).with_name('mapped_memory_read.cpp')), '-o', str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(r.stderr, '')
            self.assertIn('MAPPED_MEMORY_CASES=29 PASS; host_calls=0', r.stdout)
            if platform.system() == 'Darwin' and platform.machine() == 'arm64':
                self.assertIn('OWNED_MAPPED_MEMORY PASS; foreign_reads=0; Adobe_calls=0', r.stdout)


if __name__ == '__main__':
    unittest.main()
