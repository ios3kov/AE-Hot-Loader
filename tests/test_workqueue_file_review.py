"""Malformed original-file controls; no Adobe code is loaded or executed."""
import importlib.util
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workqueue_review', ROOT /
    'experiments/ordinary_discovery/workqueue_file_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def fixture():
    # One FAT arm64 dylib, one file-backed text section, three named symbols.
    raw = bytearray(0x500)
    struct.pack_into('>7I', raw, 0, 0xcafebabe, 1, 0x100000c, 0, 0x100, 0x400, 8)
    struct.pack_into('<8I', raw, 0x100, 0xfeedfacf, 0x100000c, 0, 6, 3, 200, 0, 0)
    struct.pack_into('<II16sQQQQiiII', raw, 0x120, 0x19, 152, b'__TEXT',
                     0x1000, 0x400, 0, 0x400, 5, 5, 1, 0)
    struct.pack_into('<16s16sQQ8I', raw, 0x168, b'__text', b'__TEXT',
                     0x1100, 0x20, 0x100, 2, 0, 0, 0x80000400, 0, 0, 0)
    struct.pack_into('<6I', raw, 0x1b8, 2, 24, 0x200, 3, 0x230, 16)
    struct.pack_into('<II16s', raw, 0x1d0, 0x1b, 24, b'0123456789abcdef')
    for i, (name, address) in enumerate([(1, 0x1100), (6, 0x1108), (11, 0x1110)]):
        struct.pack_into('<IBBHQ', raw, 0x300+i*16, name, 0xe, 1, 0, address)
    raw[0x330:0x340] = b'\0_job\0_mid\0_end\0'
    raw[0x200:0x220] = b'\x1f\x20\x03\xd5' * 8
    return raw


class WorkQueueFileReviewTests(unittest.TestCase):
    def inspect(self, raw):
        return review.inspect_text_symbols(bytes(raw), b'0123456789abcdef'.hex(),
                                           {'_job': (0x1100, 0x1108)})

    def test_selected_bounds_and_body_are_original_file_only(self):
        result = self.inspect(fixture())
        self.assertEqual(result['nlist_symbols'], 3)
        self.assertEqual(result['text_section_index'], 1)
        self.assertEqual(result['selected']['_job']['end'], '0x1108')
        self.assertEqual(result['selected']['_job']['instruction_bytes'], 8)

    def test_refuse_malformed_architecture_commands_and_file_ranges(self):
        controls = [(0, '>I', 0), (4, '>I', 2), (8, '>I', 0x1000007),
                    (16, '>I', 0), (20, '>I', 0x1000), (24, '>I', 32),
                    (0x100, '<I', 0), (0x104, '<I', 0x1000007),
                    (0x108, '<I', 1), (0x10c, '<I', 2), (0x110, '<I', 0),
                    (0x114, '<I', 0x1000), (0x124, '<I', 0),
                    (0x160, '<I', 2), (0x140, '<Q', 0),
                    (0x150, '<Q', 0x1000), (0x194, '<I', 0x1000),
                    (0x190, '<I', 0x3fc), (0x198, '<I', 32),
                    (0x1a4, '<I', 1), (0x1c0, '<I', 0xfffffff0),
                    (0x1c4, '<I', 400001), (0x1c8, '<I', 0x208),
                    (0x1cc, '<I', 0x1000), (0x1d0, '<I', 2),
                    (0x1d4, '<I', 16)]
        for at, fmt, value in controls:
            bad = fixture(); struct.pack_into(fmt, bad, at, value)
            with self.subTest(at=hex(at), value=value), self.assertRaises(ValueError):
                self.inspect(bad)
        for length in [0, 27, 0x11f, 0x1e0, 0x338]:
            with self.subTest(length=length), self.assertRaises(ValueError):
                self.inspect(fixture()[:length])

    def test_refuse_uuid_name_section_symbol_and_next_boundary_drift(self):
        for at, fmt, value in [(0x1d8, 'B', 0), (0x300, '<I', 15),
                              (0x304, 'B', 0x20), (0x305, 'B', 2),
                              (0x308, '<Q', 0x1104), (0x318, '<Q', 0x1104),
                              (0x310, '<I', 1), (0x318, '<Q', 0x1100)]:
            bad = fixture(); struct.pack_into(fmt, bad, at, value)
            with self.subTest(at=hex(at), value=value), self.assertRaises(ValueError):
                self.inspect(bad)
        bad = fixture(); bad[0x331:0x336] = b'_evil'
        with self.assertRaises(ValueError): self.inspect(bad)
        bad = fixture(); bad[0x33f] = 65
        with self.assertRaises(ValueError): self.inspect(bad)
        with self.assertRaises(ValueError):
            review.inspect_text_symbols(bytes(fixture()), '0'*32, {'_job': (0x1100, 0x1108)})
        with self.assertRaises(ValueError):
            review.inspect_text_symbols(bytes(fixture()), b'0123456789abcdef'.hex(),
                                        {'_job': (0x1100, 0x1110)})

    def test_alias_does_not_hide_new_interior_text_symbol(self):
        # Aliases at one start are legal; a new distinct start shortens the body.
        raw = fixture(); struct.pack_into('<Q', raw, 0x328, 0x1100)
        self.assertEqual(self.inspect(raw)['selected']['_job']['end'], '0x1108')
        struct.pack_into('<Q', raw, 0x328, 0x1104)
        with self.assertRaises(ValueError): self.inspect(raw)

    def test_zero_index_is_empty_even_when_table_byte_is_not_null(self):
        raw = fixture(); raw[0x330] = 32
        struct.pack_into('<I',raw,0x320,0)
        self.assertEqual(self.inspect(raw)['selected']['_job']['end'],'0x1108')

    def test_fixed_inventory_refuses_body_bytes_and_symbol_metadata_drift(self):
        from unittest import mock
        row = review.WINDOWS['queue-cancel']
        good = {'nlist_symbols':271537,'string_bytes':7871712,'text_symbols':58390,
                'selected':{r[2]:{'body_sha256':r[3]} for r in review.WINDOWS.values()}}
        with mock.patch.object(review,'inspect_text_symbols',return_value=good):
            self.assertIs(review.collect_symbols(b'owned parser control'),good)
        for field in ['nlist_symbols','string_bytes','text_symbols']:
            bad = dict(good);bad[field] += 1
            with mock.patch.object(review,'inspect_text_symbols',return_value=bad), self.assertRaises(ValueError):
                review.collect_symbols(b'owned parser control')
        bad = dict(good);bad['selected'] = dict(good['selected'])
        bad['selected'][row[2]] = {'body_sha256':'0'*64}
        with mock.patch.object(review,'inspect_text_symbols',return_value=bad), self.assertRaises(ValueError):
            review.collect_symbols(b'owned parser control')

    def test_complete_transcript_checks_refuse_cancel_branch_fields_and_unwind(self):
        text = 'owned[0x1100] <+0>: ldr x0, [x1, #0xd0]\nowned[0x1104] <+4>: ret\n'
        expected = review.transcript_digest(text, 0x1100, 0x1108)
        for bad in [text.replace('0xd0','0x220'), text.replace('ldr','str'),
                    text.replace('ret','bl 0x2000'), text+text.splitlines()[0]+'\n',
                    text.splitlines()[0]+'\n', text.replace('ldr','.long')]:
            with self.assertRaises(ValueError):
                review.verify_transcript(bad, 0x1100, 0x1108, expected)
        formatted = text.replace('owned','BEE.dylib').replace(', ', ',').replace('ret\n','ret ; comment\n')
        self.assertEqual(review.verify_transcript(formatted,0x1100,0x1108,expected),2)

    def test_fixed_scope_remains_fourteen_complete_file_windows(self):
        self.assertEqual(len(review.WINDOWS), 14)
        self.assertEqual(sum((row[1]-row[0])//4 for row in review.WINDOWS.values()), 2546)
        for row in review.WINDOWS.values():
            self.assertLessEqual(row[1]-row[0],4096)
        self.assertEqual(review.BEE_UUID,'161300f373f83ebca751959df40a073b')


if __name__ == '__main__': unittest.main()
