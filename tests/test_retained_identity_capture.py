"""One-shot bounded capture on synthetic/owned data; not an Adobe host run."""
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


class RetainedIdentityCaptureTests(unittest.TestCase):
    def test_bounded_capture_mutation_refusal_and_consumed_failure(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-retained-capture-') as tmp:
            binary = Path(tmp) / 'capture'
            build = subprocess.run(
                [compiler, '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(Path(__file__).with_name('retained_identity_capture.cpp')),
                 '-o', str(binary)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(run.stderr, '')
            self.assertIn('RETAINED_CAPTURE_CASES=46 PASS; Adobe_calls=0; callbacks_invoked=0',
                          run.stdout)
            if platform.system() == 'Darwin' and platform.machine() == 'arm64':
                self.assertIn('OWNED_RETAINED_CAPTURE PASS; foreign_processes=0; Adobe_calls=0',
                              run.stdout)


if __name__ == '__main__':
    unittest.main()
