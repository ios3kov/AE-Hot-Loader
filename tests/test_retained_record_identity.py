"""Owned-buffer record decoder; native cases are nested in one Python test."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class RetainedRecordIdentityTests(unittest.TestCase):
    def test_owned_identity_bounds_inventory_and_raw_bytes(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-retained-identity-') as tmp:
            binary = Path(tmp) / 'identity'
            build = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(Path(__file__).with_name('retained_record_identity.cpp')),
                 '-o', str(binary)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(run.stderr, '')
            self.assertEqual(run.stdout,
                             'RETAINED_IDENTITY_CASES=38 PASS; host_calls=0; record_calls=0\n')


if __name__ == '__main__':
    unittest.main()
