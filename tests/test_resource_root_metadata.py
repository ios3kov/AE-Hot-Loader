"""Static Mach-O root metadata; owned compiled files are never loaded."""
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery'))
import mach_o_root_metadata as roots
import collect_resource_roots as collector

SYMBOL = '_AEHL_TestRoot'
REQUEST = roots.RootSpec(SYMBOL, 0x1000, 8, 16, '__bss', 'owned test data')


def fixture():
    pad = lambda s: s.encode().ljust(16, b'\0')
    segment = lambda name, vm, off, length, protection, count: struct.pack(
        '<II16sQQQQiiII', 0x19, 72 + count * 80, pad(name), vm, 4096, off,
        length, protection, protection, count, 0)
    section = lambda name, segment_name, vm, length, off, flags: struct.pack(
        '<16s16sQQ8I', pad(name), pad(segment_name), vm, length, off, 3, 0, 0, flags, 0, 0, 0)
    strings = b'\0' + SYMBOL.encode() + b'\0'
    commands = segment('__TEXT', 0, 0, 4096, 5, 1) + section('__text', '__TEXT', 512, 8, 512, 0x80000400)
    commands += segment('__DATA', 4096, 4096, 0, 3, 1) + section('__bss', '__DATA', 4096, 512, 0, 1)
    commands += segment('__LINKEDIT', 8192, 4096, 4096, 1, 0)
    commands += struct.pack('<II16s', 0x1b, 24, b'OWNED-UUID-12345!')
    commands += struct.pack('<6I', 2, 24, 4096, 1, 4112, len(strings))
    data = bytearray(8192)
    data[:32] = struct.pack('<8I', 0xfeedfacf, 0x100000c, 0, 6, 5, len(commands), 0, 0)
    data[32:32 + len(commands)] = commands
    data[4096:4112] = struct.pack('<IBBHQ', 1, 0x0f, 2, 0, 4096)
    data[4112:4112 + len(strings)] = strings
    return data


def fat(data, *, cpu=0x100000c, subtype=0):
    header = struct.pack('>7I', 0xcafebabe, 1, cpu, subtype, 4096, len(data), 12)
    return header.ljust(4096, b'\0') + bytes(data)


class RootMetadataTests(unittest.TestCase):
    def parse(self, data, requests=(REQUEST,)):
        return roots.parse_roots(bytes(data), requests)

    def refuse(self, data, reason, requests=(REQUEST,)):
        with self.assertRaisesRegex(ValueError, reason):
            self.parse(data, requests)

    def test_thin_and_fat_zero_fill_is_metadata_only(self):
        for data in (fixture(), fat(fixture())):
            with self.subTest(fat=data[:4] == b'\xca\xfe\xba\xbe'):
                m = self.parse(data)
                self.assertEqual(m['scope'], 'file-only-not-runtime')
                self.assertEqual(m['roots'][0]['root_vm'], '0x1008')
                self.assertEqual(m['roots'][0]['image_relative_offset'], '0x1008')
                self.assertEqual(m['roots'][0]['section_ordinal'], 2)
                self.assertIsNone(m['roots'][0]['serialized_root_bytes'])
                self.assertTrue(m['roots'][0]['zero_fill'])

    def test_linker_string_table_prefix_is_not_a_root(self):
        data = fixture(); data[4112] = ord(' ')
        self.assertEqual(self.parse(data)['roots'][0]['symbol'], SYMBOL)

    def test_invalid_input_and_requests(self):
        self.refuse(b'', 'invalid metadata input')
        self.refuse(fixture(), 'request count', ())
        self.refuse(fixture(), 'duplicate root', (REQUEST, REQUEST))
        for r in (roots.RootSpec(SYMBOL, 0x1000, 1, 8, '__bss', ''),
                  roots.RootSpec(SYMBOL, roots.MAX64 - 7, 8, 8, '__bss', ''),
                  roots.RootSpec(SYMBOL, 0x1000, 0, 8, '__text', '')):
            with self.subTest(request=r):
                self.refuse(fixture(), 'invalid root|overflow', (r,))

    def test_wrong_architecture_and_kind(self):
        for at, value in ((0, 0xfeedface), (4, 7), (8, 2), (12, 2)):
            data = fixture(); struct.pack_into('<I', data, at, value)
            self.refuse(data, 'unsupported thin image')
        self.refuse(fat(fixture(), cpu=7), 'missing or ambiguous')
        self.refuse(fat(fixture(), subtype=2), 'unsupported arm64 subtype')

    def test_fat_truncation_overlap_and_ambiguity(self):
        self.refuse(bytes.fromhex('cafebabe00000011') + bytes(32), 'invalid FAT count')
        data = bytearray(fat(fixture())); struct.pack_into('>I', data, 16, 8)
        self.refuse(data, 'invalid FAT slice extent')
        data = bytearray(fat(fixture())); struct.pack_into('>I', data, 20, len(data))
        self.refuse(data, 'truncated metadata range')
        header = struct.pack('>2I', 0xcafebabe, 2)
        header += struct.pack('>5I', 0x100000c, 0, 4096, 8192, 12) * 2
        self.refuse(header.ljust(4096, b'\0') + bytes(fixture()), 'overlapping metadata extents')
        header = struct.pack('>2I', 0xcafebabe, 2)
        header += struct.pack('>5I', 0x100000c, 0, 4096, 8192, 12)
        header += struct.pack('>5I', 0x100000c, 0, 12288, 8192, 12)
        self.refuse(header.ljust(4096, b'\0') + bytes(fixture()) * 2, 'missing or ambiguous')

    def test_command_truncation_and_missing_metadata(self):
        for at, value, reason in ((16, 4097, 'command count'), (20, 0xffffff, 'command count'),
                                   (36, 0, 'command size'), (36, 144, 'section count'),
                                   (16, 4, 'incomplete image')):
            data = fixture(); struct.pack_into('<I', data, at, value)
            self.refuse(data, reason)
        self.refuse(fixture()[:400], 'truncated metadata range')
        data = fixture(); data[416:432] = bytes(16); self.refuse(data, 'zero UUID')

    def test_section_mapping_and_protection(self):
        for at, value, fmt, reason in (
            (184 + 60, 1, '<I', 'reviewed writable zero-fill'),
            (256 + 48, 16, '<I', 'zero-fill has file offset'),
            (256 + 32, 0x5000, '<Q', 'section outside segment'),
            (256 + 40, roots.MAX64, '<Q', 'overflow'),
            (184 + 32, 256, '<Q', 'section outside segment'),
            (256 + 64, 0, '<I', 'section outside file segment'),
            (184 + 68, 1, '<I', 'unsupported segment mapping'),
            (184 + 68, 0x10, '<I', 'reviewed writable zero-fill'),
            (256 + 64, 0x80000001, '<I', 'reviewed writable zero-fill'),
            (184 + 56, 1, '<I', 'invalid segment protection')):
            with self.subTest(offset=at):
                data = fixture(); struct.pack_into(fmt, data, at, value); self.refuse(data, reason)
        data = fixture(); data[256 + 16] = ord('X'); self.refuse(data, 'section identity')
        data = fixture(); data[32 + 8 + 15] = ord('X'); self.refuse(data, 'fixed name padding')
        data = fixture(); struct.pack_into('<Q', data, 336 + 24, 4096)
        self.refuse(data, 'overlapping metadata extents')

    def test_symbol_table_and_definition(self):
        for at, value, fmt, reason in (
            (432 + 12, 500001, '<I', 'symbol table budget'),
            (432 + 8, 512, '<I', 'outside linkedit'),
            (432 + 16, 4096, '<I', 'overlapping metadata extents'),
            (4096, 1000, '<I', 'string index'),
            (4096 + 4, 1, '<B', 'section definition'),
            (4096 + 4, 0xef, '<B', 'missing root'),
            (4096 + 5, 0, '<B', 'section definition'),
            (4096 + 5, 3, '<B', 'section definition'),
            (4096 + 8, 0x1008, '<Q', 'root value')):
            with self.subTest(offset=at):
                data = fixture(); struct.pack_into(fmt, data, at, value); self.refuse(data, reason)
        data = fixture(); data[4113] = ord('X'); self.refuse(data, 'missing root')
        data = fixture(); data[4112 + len(SYMBOL) + 1] = 1
        self.refuse(data, 'unterminated string table')
        bad_request = roots.RootSpec(SYMBOL, 4096, 512, 8, '__bss', '')
        self.refuse(fixture(), 'section extent mismatch', (bad_request,))

    def test_full_length_section_name_and_debug_alias(self):
        data = fixture(); data[104:120] = b'__gcc_except_tab'
        self.assertEqual(self.parse(data)['roots'][0]['symbol'], SYMBOL)
        data = fixture()
        strings = bytes(data[4112:4112 + len(SYMBOL) + 2])
        data[4112:4128] = struct.pack('<IBBHQ', 1, 0x20, 0, 0, 0)
        data[4128:4128 + len(strings)] = strings
        struct.pack_into('<II', data, 444, 2, 4128)
        self.assertEqual(self.parse(data)['roots'][0]['symbol'], SYMBOL)

    def test_zero_string_index_is_unnamed(self):
        data = fixture()
        name = SYMBOL.encode() + b'\0'
        data[4112:4112 + len(name)] = name
        struct.pack_into('<I', data, 4096, 0)
        self.refuse(data, 'missing root')

    def test_duplicate_symbol_and_uuid_refused(self):
        data = fixture()
        strings = bytes(data[4112:4112 + len(SYMBOL) + 2])
        data[4112:4128] = data[4096:4112]
        data[4128:4128 + len(strings)] = strings
        struct.pack_into('<II', data, 444, 2, 4128)
        self.refuse(data, 'duplicate root symbol')
        data = fixture()
        data[432:456] = data[408:432]
        self.refuse(data, 'duplicate UUID')

    def test_pinned_root_indirection_is_explicit(self):
        plug = collector.REQUESTS['PLUG'][0]
        mee = collector.REQUESTS['MEE'][0]
        self.assertEqual(plug.symbol_vm + plug.displacement, 0x18490)
        self.assertIn('read slot then handle', plug.meaning)
        self.assertEqual(mee.symbol_vm + mee.displacement, 0x10fd70)
        self.assertEqual(mee.extent, 16)

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'owned compiled Mach-O metadata requires macOS arm64')
    def test_owned_compiled_zero_fill_file_never_loaded(self):
        with tempfile.TemporaryDirectory(prefix='aehl-owned-root-') as folder:
            path = Path(folder)
            source = path / 'owned.cpp'; library = path / 'owned.dylib'
            source.write_text('extern "C" { unsigned long long AEHL_TestRoot[4]; }\n')
            result = subprocess.run(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64', '-dynamiclib',
                str(source), '-o', str(library)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = library.read_bytes()
            result = subprocess.run(['/usr/bin/xcrun', 'nm', '-arch', 'arm64', '-n', str(library)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = int(next(line.split()[0] for line in result.stdout.splitlines()
                             if line.endswith(' ' + SYMBOL)), 16)
            request = roots.RootSpec(SYMBOL, value, 8, 16, '__common', 'owned file only')
            metadata = self.parse(data, (request,))
            self.assertEqual(metadata['roots'][0]['root_vm'], hex(value + 8))
            self.assertEqual(library.read_bytes(), data)
            self.assertIsNone(metadata['roots'][0]['serialized_root_bytes'])


if __name__ == '__main__':
    unittest.main()
