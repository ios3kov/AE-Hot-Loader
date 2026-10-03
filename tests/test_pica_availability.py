"""Portable policy checks only; supplied SDK/native candidate checked separately."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PicaAvailabilityTests(unittest.TestCase):
    def test_owned_policy_failure_and_one_shot(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-pica-policy-') as folder:
            binary = Path(folder) / 'policy'
            build = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic',
                                    '-Werror', str(ROOT / 'tests/pica_availability.cpp'), '-o', str(binary)],
                                   capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('23 owned/synthetic cases PASS; AE NOT RUN', result.stdout)
            print(result.stdout.strip())
