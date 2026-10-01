"""Portable data containment and actual owned resident root identity, no Adobe."""
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


def data_fixture():
    data = fixture()
    command_size = struct.unpack_from('<I', data, 20)[0]
    segment = struct.pack('<II16sQQQQIIII', 0x19, 152, b'__DATA'.ljust(16, b'\0'),
                          4096, 4096, 4096, 0, 3, 3, 1, 0)
    section = struct.pack('<16s16sQQIIIIIIII', b'__common'.ljust(16, b'\0'),
                          b'__DATA'.ljust(16, b'\0'), 4096, 128, 0, 3, 0, 0, 1, 0, 0, 0)
    data[32 + command_size:32 + command_size + 152] = segment + section
    struct.pack_into('<II', data, 16, 4, command_size + 152)
    data.extend(bytes(4096))
    return data, 32 + command_size


class ResidentDataRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-resident-data-root-')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name).resolve()
        self.compiler = shutil.which('clang++')
        self.assertIsNotNone(self.compiler)
        self.binary = self.folder / 'root-test'
        self.command([self.compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                      str(ROOT / 'tests/resident_data_root_binding.cpp'), '-o', str(self.binary)])

    def command(self, argv, success=True):
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
        if success:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(r.stderr, '')
        else:
            self.assertNotEqual(r.returncode, 0, r.stdout)
        return r.stdout

    def test_portable_data_extent_and_zero_fill_guards(self):
        original, start = data_fixture(); path = self.folder / 'synthetic.data'
        path.write_bytes(original)
        self.assertIn('DATA_ROOT_LAYOUT PASS', self.command(
            [str(self.binary), str(path), SYMBOL, '0x1008', '__common', '--describe']))
        for at, fmt, value in (
            (start + 60, '<I', 1), (start + 56, '<I', 7), (start + 68, '<I', 0x10),
            (start + 72 + 48, '<I', 4096), (start + 72 + 64, '<I', 0),
            (start + 72 + 40, '<Q', 8), (start + 72 + 32, '<Q', 8192),
            (start + 32, '<Q', 8), (start + 24, '<Q', 0),
            (start + 32, '<Q', (1 << 64) - 1), (start + 72 + 60, '<I', 1)):
            with self.subTest(offset=at):
                bad = bytearray(original); struct.pack_into(fmt, bad, at, value); path.write_bytes(bad)
                self.command([str(self.binary), str(path), SYMBOL, '0x1008', '__common', '--describe'], False)

    def test_ambiguous_data_segment_or_section_refused(self):
        original, start = data_fixture(); path = self.folder / 'ambiguous.data'
        for duplicate_segment in (True, False):
            bad = bytearray(original)
            old_size = struct.unpack_from('<I', bad, 20)[0]
            if duplicate_segment:
                bad[32 + old_size:32 + old_size + 152] = bad[start:start + 152]
                struct.pack_into('<II', bad, 16, 5, old_size + 152)
            else:
                bad[32 + old_size:32 + old_size + 80] = bad[start + 72:start + 152]
                struct.pack_into('<I', bad, start + 4, 232)
                struct.pack_into('<I', bad, start + 64, 2)
                struct.pack_into('<I', bad, 20, old_size + 80)
            path.write_bytes(bad)
            self.command([str(self.binary), str(path), SYMBOL, '0x1008', '__common', '--describe'], False)

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'owned resident data binding requires macOS arm64')
    def test_real_owned_root_identity_absence_hash_and_thread(self):
        source = self.folder / 'owned.cpp'; library = self.folder / 'owned.dylib'
        source.write_text('extern "C" { unsigned long long AEHL_TestRoot[4];\n'
                          'int AEHL_OwnedFunction() { return 73; } }\n')
        self.command(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64', '-dynamiclib', str(source),
                      '-o', str(library), '-Wl,-install_name,' + str(library)])
        original = library.read_bytes()
        out = self.command(['/usr/bin/xcrun', 'nm', '-arch', 'arm64', '-n', str(library)])
        value = int(next(line.split()[0] for line in out.splitlines() if line.endswith(' _AEHL_TestRoot')), 16)
        output = self.command([str(self.binary), str(library), '_AEHL_OwnedFunction', hex(value + 8),
                               '__common', '--resident'])
        self.assertIn('OWNED_RESIDENT_DATA_ROOT PASS; Adobe_calls=0; provider_loads_by_binder=0', output)
        self.assertEqual(library.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
