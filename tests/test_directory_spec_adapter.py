"""Concrete directory operations with OWNED producers; no Adobe calls or process attach."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / 'tests/directory_spec_adapter.cpp'
ASM = ROOT / 'experiments/ordinary_discovery/HostIndirectResult_arm64.S'


class DirectorySpecAdapterTests(unittest.TestCase):
    def exercise(self, native=False):
        compiler = shutil.which('clang++')
        self.assertIsNotNone(compiler, 'clang++ required')
        with tempfile.TemporaryDirectory(prefix='aehl-directory-owned-') as tmp:
            inputs = [str(CPP)]
            flags = []
            if native:
                obj = Path(tmp) / 'indirect.o'
                built = subprocess.run(['/usr/bin/xcrun', 'clang', '-arch', 'arm64',
                                        '-c', str(ASM), '-o', str(obj)],
                                       capture_output=True, timeout=30)
                self.assertEqual(built.returncode, 0, built.stderr.decode(errors='replace'))
                inputs.append(str(obj))
                flags = ['-arch', 'arm64', '-DAEHL_TEST_REAL_ARM64=1']
            for optimization in ('-O0', '-O2'):
                binary = Path(tmp) / ('directory-' + optimization)
                built = subprocess.run([compiler, '-std=c++17', optimization, '-Wall', '-Wextra',
                                        '-Wpedantic', '-Werror', *flags, *inputs, '-o', str(binary)],
                                       capture_output=True, timeout=45)
                self.assertEqual(built.returncode, 0, built.stderr.decode(errors='replace'))
                ran = subprocess.run([str(binary)], capture_output=True, timeout=15)
                self.assertEqual(ran.returncode, 0, (ran.stdout + ran.stderr).decode(errors='replace'))
                self.assertEqual(ran.stderr, b'')
                self.assertIn(b'27/27 OWNED DIRECTORY CASES PASS; Adobe calls=0', ran.stdout)
                self.assertEqual(sum(line.startswith(b'PASS ') for line in ran.stdout.splitlines()), 27)
                if native:
                    self.assertIn(b'SELF READER invalid-pointer/bounds PASS', ran.stdout)
                print(('arm64 thunk/self reader' if native else 'portable owned adapter') +
                      ' ' + optimization + ': ' + ran.stdout.decode().strip())

    def test_owned_lifecycle_and_failures(self):
        self.exercise()

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'owned macOS arm64 thunk and self-memory read only')
    def test_native_transport_and_self_memory(self):
        self.exercise(native=True)


if __name__ == '__main__':
    unittest.main()
