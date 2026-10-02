"""Refuse wrong identities, incomplete windows and changed PIN structural evidence."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/ordinary_discovery'))
spec = importlib.util.spec_from_file_location('pin_cleanup_collector',
    ROOT / 'experiments/ordinary_discovery/collect_pin_cleanup.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

SYMBOL_TEXT = ('0000000000113c94 t __ZL16PINp_CleanupFuncPvPFisPKcS_PhES_\n'
               '0000000000113c98 t __ZL16PINp_SortModulesv\n'
               '0000000000113d7c T __ZN15PIN_GlobalState6CreateEP9U_Context\n')
METADATA = ('Load command 0\n cmd LC_SEGMENT_64\n segname __TEXT\n'
            ' vmaddr 0x0\n vmsize 0x224000\n maxprot 0x5\n initprot 0x5\n'
            'Load command 1\n cmd LC_UUID\n uuid 11A71CEB-5A06-3FB7-92C7-0037233B101B\n')
TAIL = 'owned[0x113c94] <+0>: b 0x113c98 ; next function\n'


class PinCleanupCollectorTests(unittest.TestCase):
    def test_exact_symbol_boundaries_reject_aliases_missing_and_shifted_definitions(self):
        self.assertIn('PINp_CleanupFunc', collector.validate_symbols(SYMBOL_TEXT))
        for bad in ('', SYMBOL_TEXT.replace('113c98', '113c9c'),
                    SYMBOL_TEXT + SYMBOL_TEXT.splitlines()[0] + '\n',
                    SYMBOL_TEXT.replace('PINp_SortModulesv', 'OtherSymbol'),
                    SYMBOL_TEXT + '0000000000113ca0 t _unexpected_boundary\n'):
            with self.subTest(text=bad), self.assertRaisesRegex(ValueError, 'boundaries'):
                collector.validate_symbols(bad)

    def test_metadata_refuses_wrong_duplicate_uuid_or_text_protection(self):
        self.assertEqual(collector.validate_metadata(METADATA)['uuid'], collector.PIN_UUID)
        for bad in ('', METADATA.replace('11A71CEB', '00A71CEB'),
                    METADATA + ' uuid ' + collector.PIN_UUID + '\n',
                    METADATA.replace('initprot 0x5', 'initprot 0x7'),
                    METADATA.replace('vmsize 0x224000', 'vmsize 0x1000'),
                    METADATA.replace(' vmaddr 0x0\n', '')):
            with self.subTest(text=bad), self.assertRaises(ValueError):
                collector.validate_metadata(bad)

    def test_cleanup_tail_requires_exact_coverage_and_branch_target(self):
        result = collector.validate_window(TAIL, 'PIN-cleanup', 0x113c94, 0x113c98)
        self.assertEqual(result['decoded_instructions'], 1)
        for bad in ('', TAIL + TAIL, TAIL.replace('b 0x113c98', 'ret'),
                    TAIL.replace('b 0x113c98', 'b 0x113c9c'),
                    TAIL.replace('b 0x113c98', '.long 0')):
            with self.subTest(text=bad), self.assertRaises(ValueError):
                collector.validate_window(bad, 'PIN-cleanup', 0x113c94, 0x113c98)

    def test_full_decoded_sort_coverage_does_not_substitute_for_structural_checks(self):
        fake = ''.join('owned[0x%x] <+%d>: nop\n' % (a, a - 0x113c98)
                       for a in range(0x113c98, 0x113d7c, 4))
        with self.assertRaisesRegex(ValueError, 'structural'):
            collector.validate_window(fake, 'PIN-sort', 0x113c98, 0x113d7c)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            collector.validate_window(fake.splitlines()[0], 'PIN-sort', 0x113c98, 0x113d7c)

    def test_unreviewed_window_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'unknown'):
            collector.validate_window(TAIL, 'arbitrary', 0x113c94, 0x113c98)


if __name__ == '__main__':
    unittest.main()
