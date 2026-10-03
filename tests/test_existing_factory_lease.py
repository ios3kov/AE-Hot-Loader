"""Real owned dylib ABI/object/code lifetime; never loads or calls Adobe code."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                     'resident code lease requires macOS arm64')
class ExistingFactoryLeaseTests(unittest.TestCase):
    def run_owned(self, defines=(), mode='--good', sanitize=False, expected=0):
        compiler = shutil.which('clang++'); self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-existing-factory-') as tmp:
            folder = Path(tmp).resolve(); lib = folder/'owned.dylib'; binary = folder/'consumer'
            flags = ['-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror']
            if sanitize: flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
            commands = [[compiler, *flags, '-dynamiclib', *defines,
                         str(ROOT/'tests/owned_factory_module.cpp'), '-o', str(lib),
                         '-Wl,-install_name,'+str(lib)],
                        [compiler, *flags, str(ROOT/'tests/existing_factory_lease.cpp'), '-o', str(binary)]]
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            original = lib.read_bytes()
            result = subprocess.run([str(binary), str(lib), mode], cwd=folder,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, expected, result.stdout+result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(lib.read_bytes(), original)
            return result.stdout

    def test_actual_noncreating_acquisition_and_cross_module_object_code_lifetime(self):
        self.assertIn('OWNED_FACTORY_LEASE PASS', self.run_owned())

    def test_real_lifetime_with_address_and_undefined_behavior_sanitizers(self):
        self.assertIn('OWNED_FACTORY_LEASE PASS', self.run_owned(sanitize=True))

    def test_wrong_version_refuses_before_acquisition(self):
        self.assertIn('OWNED_FACTORY_ABI_REFUSAL PASS; acquire_calls=0',
                      self.run_owned(['-DAEHL_TEST_VERSION=2'], '--bad'))

    def test_missing_release_export_refuses_before_acquisition(self):
        self.assertIn('OWNED_FACTORY_ABI_REFUSAL PASS; acquire_calls=0',
                      self.run_owned(['-DAEHL_TEST_MISSING_RELEASE=1'], '--bad'))

    def test_wrong_thread_release_or_transfer_stops_before_module_callbacks(self):
        for mode in ('--wrong-reset', '--wrong-move'):
            with self.subTest(mode=mode):
                self.assertEqual(self.run_owned(mode=mode, expected=86), '')

if __name__ == '__main__': unittest.main()
