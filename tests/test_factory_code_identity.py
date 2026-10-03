"""File/code address identity and actual owned native binding; no Adobe invocation."""
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from test_resident_image_binding import fixture, SYMBOL

ROOT = Path(__file__).resolve().parents[1]

class FactoryCodeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-factory-code-')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name).resolve()
        compiler = shutil.which('clang++')
        self.assertIsNotNone(compiler)
        self.binary = self.folder / 'binder-test'
        self.command([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                      str(ROOT / 'tests/factory_code_identity.cpp'), '-o', str(self.binary)])

    def command(self, argv, success=True):
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
        if success:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(r.stderr, '')
        else:
            self.assertNotEqual(r.returncode, 0)
        return r.stdout

    def test_portable_exact_text_extent_and_duplicate_bounds_refusals(self):
        path = self.folder / 'owned.data'; path.write_bytes(fixture())
        self.assertIn('FACTORY_CODE_LAYOUT PASS', self.command(
            [str(self.binary), str(path), SYMBOL, '512', '516', '--describe']))
        for first, second in [('0', '516'), ('512', '520'), ('516', '512'), ('511', '516')]:
            with self.subTest(first=first, second=second):
                self.command([str(self.binary), str(path), SYMBOL, first, second, '--describe'], False)

    def test_parser_rejects_non_executable_or_wrong_architecture(self):
        path = self.folder / 'bad.data'; original = fixture()
        for offset, value in [(4, 0x1000007), (32+56, 3), (32+60, 3)]:
            with self.subTest(offset=offset):
                bad = bytearray(original); struct.pack_into('<I', bad, offset, value); path.write_bytes(bad)
                self.command([str(self.binary), str(path), SYMBOL, '512', '516', '--describe'], False)

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'owned native factory code binding requires macOS arm64')
    def test_actual_owned_resident_addresses_hash_uuid_spans_and_thread(self):
        src = self.folder / 'owned.cpp'; lib = self.folder / 'owned.dylib'
        src.write_text('extern "C" int AEHL_OwnedFunction() { return 73; }\n'
                       'extern "C" int AEHL_OwnedSecond() { return 19; }\n')
        self.command(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64', '-dynamiclib', str(src),
                      '-o', str(lib), '-Wl,-install_name,'+str(lib)])
        original = lib.read_bytes()
        out = self.command(['/usr/bin/xcrun', 'nm', '-arch', 'arm64', '-n', str(lib)])
        addresses = {line.split()[-1]: line.split()[0] for line in out.splitlines() if len(line.split()) == 3}
        a = '0x'+addresses[SYMBOL]; b = '0x'+addresses['_AEHL_OwnedSecond']
        text = self.command([str(self.binary), str(lib), SYMBOL, a, b, '--resident'])
        self.assertIn('OWNED_FACTORY_CODE_BIND PASS; Adobe_calls=0; binder_loads=0; callable_pointers=0', text)
        self.assertEqual(lib.read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
