"""Compile/run the unbound resource-gate model, not After Effects or Adobe code."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


class ResourcePassGateTests(unittest.TestCase):
    def test_native_transaction_contract(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler, 'C++ compiler required; not a silently skipped gate')
        source = Path(__file__).with_name('resource_pass_gate.cpp')
        with tempfile.TemporaryDirectory(prefix='aehl-resource-policy-') as directory:
            executable = Path(directory) / 'resource-policy-tests'
            build = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(source), '-o', str(executable)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            result = subprocess.run([str(executable)], stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, '')
            lines = result.stdout.splitlines()
            passed = [line for line in lines if line.startswith('PASS ')]
            self.assertEqual(len(passed), 94)
            self.assertEqual(len(set(passed)), 94)
            self.assertRegex(lines[-1], re.compile(
                r'^RESOURCE_GATE_TESTS=94 PASS; scope=synthetic-unbound-backend$'))
            print(result.stdout, end='')


if __name__ == '__main__':
    unittest.main()
