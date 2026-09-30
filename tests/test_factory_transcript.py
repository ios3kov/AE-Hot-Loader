"""Synthetic transcript regression: diagnostic status is not an instruction string."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/collect_factory_image.py'
spec = importlib.util.spec_from_file_location('factory_transcript_collect', PATH)
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)
SELECTION = {'functions': [{'start': 0x1000, 'end': 0x1008}]}
GOOD = (b'(lldb) disassemble --start-address 0x1000 --end-address 0x1008\n'
        b'owned[0x1000] <+0>: mov w0, #7 ; "error: owned payload"\n'
        b'owned[0x1004] <+4>: ret ; std::runtime_error::runtime_error()\n(lldb) quit\n')


class TranscriptTests(unittest.TestCase):
    def test_instruction_strings_are_not_diagnostics(self):
        self.assertIn(b'error:', GOOD.lower())  # Reproduces the old bad condition.
        result = collect.validate_disassembly(GOOD, b'', SELECTION)
        self.assertEqual(result, dict(status='PASS', windows=1, instruction_count=2,
                                     scope='transcript-only-not-runtime-proof'))

    def test_true_errors_on_either_stream_block(self):
        for error in (b'error: cannot read\n', b'  error: failed\n',
                      b'\x1b[31merror:\x1b[0m failed\n', b'(lldb) error: failed\n',
                      b'fatal error: failed\n'):
            for stdout, stderr in ((error + GOOD, b''), (GOOD, error)):
                with self.subTest(error=error, stderr=bool(stderr)), self.assertRaises(ValueError):
                    collect.validate_disassembly(stdout, stderr, SELECTION)

    def test_empty_output_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(b'', b'', SELECTION)

    def test_missing_quit_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD.replace(b'(lldb) quit\n', b''), b'', SELECTION)

    def test_missing_instruction_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(b'\n'.join(GOOD.splitlines()[:-2]) + b'\n(lldb) quit\n', b'', SELECTION)

    def test_wrong_address_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD.replace(b'owned[0x1004]', b'owned[0x1008]'), b'', SELECTION)

    def test_mismatched_window_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD.replace(b'end-address 0x1008', b'end-address 0x100c'), b'', SELECTION)

    def test_repeated_transaction_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD + GOOD, b'', SELECTION)

    def test_duplicate_selection_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD, b'', {'functions': SELECTION['functions'] * 2})

    def test_reordered_instructions_cannot_pass(self):
        lines = GOOD.splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        with self.assertRaises(ValueError):
            collect.validate_disassembly(b'\n'.join(lines), b'', SELECTION)

    def test_no_instruction_output_cannot_pass(self):
        lines = GOOD.splitlines()
        with self.assertRaises(ValueError):
            collect.validate_disassembly(lines[0] + b'\n(lldb) quit\n', b'', SELECTION)

    def test_instruction_outside_windows_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD + b'owned[0x1008] <+8>: ret\n', b'', SELECTION)

    def test_malformed_command_cannot_pass(self):
        with self.assertRaises(ValueError):
            collect.validate_disassembly(GOOD.replace(b' --end-address 0x1008', b' --count 2'), b'', SELECTION)

    def test_styles_supported_without_hiding_errors(self):
        self.assertEqual(collect.validate_disassembly(b'\x1b[0m' + GOOD, b'', SELECTION)['status'], 'PASS')

    def test_multiple_windows(self):
        second = GOOD.replace(b'0x100', b'0x200').replace(b'(lldb) quit\n', b'')
        data = GOOD.replace(b'(lldb) quit\n', b'') + second + b'(lldb) quit\n'
        selection = {'functions': SELECTION['functions'] + [{'start': 0x2000, 'end': 0x2008}]}
        self.assertEqual(collect.validate_disassembly(data, b'', selection)['windows'], 2)


class FactoryFocusTests(unittest.TestCase):
    def table(self):
        names = ['_MEE_Unrelated%03d' % i for i in range(120)] + [
            '__ZN2ML27AELibraryVideoFilterFactory17CreateUnknownImplEv',
            '__ZN2ML26AELibraryVideoFilterModule11SetupFilterEv',
            '__Z25MEE_GetVideoFilterModulesv', '_MEE_GetAELibPluginSetter', '_end']
        return '\n'.join('%016x t %s' % (0x1000 + i * 16, n) for i, n in enumerate(names))

    def test_generic_mee_functions_no_longer_starve_factory(self):
        result = collect.choose_symbols(self.table())
        names = str(result['functions'])
        self.assertIn('AELibraryVideoFilterFactory17CreateUnknownImpl', names)
        self.assertIn('MEE_GetVideoFilterModules', names)
        self.assertEqual(len(result['functions']), collect.MAX_FUNCTIONS)

    def test_focus_keeps_only_identified_factory_and_anchors(self):
        result = collect.choose_symbols(self.table(), factory_only=True)
        self.assertEqual(result['matched_addresses'], 4)
        self.assertEqual(result['omitted_by_limit'], 0)
        self.assertNotIn('Unrelated', str(result))
        self.assertIn('AELibraryVideoFilterModule11SetupFilter', str(result))

    def test_known_4148_byte_method_not_truncated_at_4096(self):
        result = collect.choose_symbols('0000000000007dc8 t _AELibraryVideoFilterFactory_Create\n'
                                        '0000000000008dfc t _next', factory_only=True)
        self.assertEqual(result['functions'][0]['end'], 0x8dfc)
        self.assertFalse(result['functions'][0]['window_capped'])

    def test_focus_cli_is_explicitly_mee_only(self):
        with mock.patch.object(collect, 'main', return_value=0) as run:
            self.assertEqual(collect.entry(['--module', 'MEE', '--factory-only']), 0)
            run.assert_called_once_with('MEE', factory_only=True)

    def test_focus_rejects_other_modules_before_execution(self):
        with mock.patch.object(collect, 'main') as run, contextlib.redirect_stderr(io.StringIO()):
            for args in (['--factory-only'], ['--module', 'FLT', '--factory-only'],
                         ['--module', 'MEE', '--module', 'FLT', '--factory-only']):
                with self.subTest(args=args), self.assertRaises(SystemExit):
                    collect.entry(args)
            run.assert_not_called()

    def test_unaligned_address_windows_rejected(self):
        with self.assertRaises(ValueError):
            collect.commands(Path('/owned/image'), {'functions': [{'start': 0x1001, 'end': 0x1008}]})


if __name__ == '__main__':
    unittest.main()
