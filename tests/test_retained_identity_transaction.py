"""Guarded transaction on injected fixture boundaries; no AE/Adobe execution."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class RetainedIdentityTransactionTests(unittest.TestCase):
    def test_one_shot_authority_identity_deadlines_and_evidence_failures(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-retained-transaction-') as tmp:
            binary = Path(tmp) / 'transaction'
            build = subprocess.run(
                [compiler, '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(Path(__file__).with_name('retained_identity_transaction.cpp')),
                 '-o', str(binary)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(run.stderr, '')
            self.assertIn('RETAINED_TRANSACTION_CASES=101 PASS; Adobe_calls=0; captures_one_shot=1',
                          run.stdout)


if __name__ == '__main__':
    unittest.main()
