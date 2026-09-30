"""Real macOS LLDB option regression on an owned synthetic arm64 Mach-O.

Compiles but NEVER executes the fixture. No After Effects, process attachment,
expression evaluation or Adobe library is used. Linux explicitly skips it.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/collect_factory_image.py'
spec = importlib.util.spec_from_file_location('factory_lldb_collect', SOURCE)
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)

if os.environ.get('AEHL_REQUIRE_REAL_LLDB') == '1' and sys.platform != 'darwin':
    raise RuntimeError('The required real macOS LLDB gate must not be skipped')


@unittest.skipUnless(sys.platform == 'darwin', 'requires real macOS developer tools')
class RealLLDBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aehl-lldb-test-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name).resolve()
        source = cls.base / 'fixture.s'
        source.write_text('.text\n.p2align 2\n.globl _AEHL_PluginFactoryFixture\n'
                          '_AEHL_PluginFactoryFixture:\n mov w0, #7\n ret\n'
                          '.globl _main\n_main:\n mov w0, #0\n ret\n')
        cls.image = cls.base / 'fixture'
        subprocess.run(['/usr/bin/xcrun', 'clang', '-arch', 'arm64', str(source),
                        '-o', str(cls.image)], check=True, capture_output=True, timeout=30)
        symbols = subprocess.run(['/usr/bin/nm', '-arch', 'arm64', '-n', '-m', str(cls.image)],
                                 check=True, capture_output=True, text=True, timeout=15).stdout
        cls.selection = collect.choose_symbols(symbols)
        if len(cls.selection['functions']) != 1:
            raise AssertionError('The owned fixture must select exactly one function')
        cls.image_hash = collect.digest(cls.image)
        version = subprocess.run(['/usr/bin/xcrun', 'lldb', '--version'], check=True,
                                 capture_output=True, text=True, timeout=15)
        print('REAL_LLDB_VERSION:', version.stdout.strip(), flush=True)

    def inspect(self, legacy):
        cmds = collect.commands(self.image, self.selection)
        if legacy:
            cmds = [c + ' --force' if c.startswith('disassemble ') else c for c in cmds]
        script = self.base / ('legacy.lldb' if legacy else 'fixed.lldb')
        script.write_text('\n'.join(cmds) + '\n')
        result = subprocess.run(['/usr/bin/xcrun', 'lldb', '--no-lldbinit', '--batch',
                                 '--source', str(script)], cwd=self.base, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(collect.digest(self.image), self.image_hash)
        return result

    def test_legacy_force_combination_reproduces_real_parser_failure(self):
        result = self.inspect(legacy=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid combination of options', result.stdout + result.stderr)
        print('REAL_LLDB_LEGACY: expected option failure reproduced; no fixture executed', flush=True)

    def test_fixed_explicit_address_range_disassembles_without_execution(self):
        result = self.inspect(legacy=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('error:', (result.stdout + result.stderr).lower())
        self.assertIn('AEHL_PluginFactoryFixture', result.stdout)
        self.assertRegex(result.stdout, r'\bmov\s+w0,\s*#(?:0x)?7\b')
        self.assertRegex(result.stdout, r'\bret\b')
        self.assertNotIn('Process ', result.stdout)
        print('REAL_LLDB_FIXED: arm64 mov/ret decoded; no fixture executed', flush=True)


if __name__ == '__main__':
    unittest.main()
