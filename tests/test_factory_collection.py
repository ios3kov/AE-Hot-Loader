"""Synthetic offline collector checks, not After Effects runtime evidence."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/collect_factory_image.py'
spec = importlib.util.spec_from_file_location('factory_collect', PATH)
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


def table(*names):
    return '\n'.join('%016x t %s' % (0x1000 + i * 16, name) for i, name in enumerate(names))


class CollectionTests(unittest.TestCase):
    def test_short_symbol_selection(self):
        result = collect.choose_symbols(table('__ZN2AE13PluginFactory4LoadEv', '_other'))
        self.assertEqual(result['matched_addresses'], 1)
        self.assertEqual(result['functions'][0]['end'], 0x1010)

    def test_verbose_nm_selection(self):
        result = collect.choose_symbols('0000000000001000 (__TEXT,__text) non-external (was a private external) __ZN2AE13PluginFactory4LoadEv\n0000000000001010 (__TEXT,__text) external _other')
        self.assertEqual(result['functions'][0]['start'], 0x1000)
        self.assertEqual(result['functions'][0]['end'], 0x1010)

    def test_undefined_is_never_a_target(self):
        result = collect.choose_symbols(table('_other') + '\n (undefined) external _PluginFactory (from Elsewhere)\n U _MEE_GetVideoFilterModules')
        self.assertEqual(result['functions'], [])

    def test_data_symbols_excluded(self):
        result = collect.choose_symbols(table('_other') + '\n0000000000001030 d _PluginFactory\n0000000000001040 (__DATA,__data) external _PluginFactory')
        self.assertEqual(result['functions'], [])

    def test_aliases_disassembled_once(self):
        result = collect.choose_symbols('0000000000001000 t _PluginFactoryA\n0000000000001000 t _PluginFactoryB\n0000000000001010 t _other')
        self.assertEqual(len(result['functions']), 1)
        self.assertEqual(len(result['functions'][0]['names']), 2)

    def test_templates_are_not_direct_factories(self):
        result = collect.choose_symbols(table('__ZNSt6vectorIPluginFactoryEE3endEv', '__ZNKSt6vectorIPluginFactoryEE3endEv', '__ZN5boost10shared_ptrIPluginFactoryEED1Ev', '__ZTVPluginFactory', '_other'))
        self.assertEqual(result['functions'], [])

    def test_window_is_capped(self):
        result = collect.choose_symbols('0000000000001000 t _PluginFactory\n0000000000100000 t _other')
        self.assertEqual(result['functions'][0]['end'], 0x2000)
        self.assertTrue(result['functions'][0]['window_capped'])

    def test_last_symbol_unknown_extent(self):
        result = collect.choose_symbols(table('_PluginFactory'))
        self.assertTrue(result['functions'][0]['window_capped'])
        self.assertIsNone(result['functions'][0]['next_text_symbol'])

    def test_limit_is_reported(self):
        result = collect.choose_symbols(table(*['_PluginFactory%d' % i for i in range(collect.MAX_FUNCTIONS + 10)]))
        self.assertEqual(len(result['functions']), collect.MAX_FUNCTIONS)
        self.assertEqual(result['omitted_by_limit'], 10)

    def test_critical_mappings_prioritized(self):
        result = collect.choose_symbols(table(*(['_OtherFactory%d' % i for i in range(120)] + ['_MEE_GetVideoFilterModules', '_FLT_NotifyFilterLoadingDone', '_PluginFactory'])) )
        chosen = str(result['functions'])
        self.assertIn('_MEE_GetVideoFilterModules', chosen)
        self.assertIn('_FLT_NotifyFilterLoadingDone', chosen)
        self.assertIn('_PluginFactory', chosen)

    def test_unaligned_records_not_selected(self):
        result = collect.choose_symbols('0000000000001001 t _PluginFactory\n0000000000001004 t _other')
        self.assertEqual(result['functions'], [])

    def test_empty_symbol_table_rejected(self):
        with self.assertRaises(ValueError):
            collect.choose_symbols('no symbol data')

    def test_commands_use_addresses_not_untrusted_names(self):
        chosen = collect.choose_symbols(table('_PluginFactory;quit'))
        result = collect.commands(Path('/owned/image with spaces'), chosen)
        self.assertEqual(result[:3], ['settings set target.load-cwd-lldbinit false', 'settings set target.load-script-from-symbol-file false', 'target create --no-dependents --arch arm64 "/owned/image with spaces"'])
        self.assertEqual(result[3], 'disassemble --start-address 0x1000 --end-address 0x2000')
        self.assertEqual(result[-1], 'quit')
        self.assertNotIn('PluginFactory', '\n'.join(result))

    def test_injection_paths_rejected(self):
        for path in ('relative', '/tmp/a"', '/tmp/a\nquit', '/tmp/a\\'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                collect.commands(Path(path), {'functions': []})

    def test_invalid_numeric_windows_rejected(self):
        for start, end in ((True, 3), ('0x1000', 8), (0, 4), (8, 4), (4, 10000)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                collect.commands(Path('/tmp/image'), {'functions': [{'start': start, 'end': end}]})

    def test_hash_is_content_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'owned'; path.write_bytes(b'owned')
            self.assertEqual(collect.digest(path), hashlib.sha256(b'owned').hexdigest())

    def test_linux_refuses_before_process_or_output(self):
        with mock.patch.object(collect.sys, 'platform', 'linux'), mock.patch.object(collect.subprocess, 'run') as run, mock.patch.object(collect.tempfile, 'mkdtemp') as mkdtemp, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(collect.main(), 2)
            run.assert_not_called(); mkdtemp.assert_not_called()

    def test_tool_invocation_is_bounded_and_has_no_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(collect.subprocess, 'run', return_value=mock.Mock(returncode=0)) as run:
                collect.run_tool(['fixed-reader', 'fixed-input'], Path(tmp), 'test.txt', timeout=7)
                kwargs = run.call_args.kwargs
                self.assertEqual(kwargs['timeout'], 7)
                self.assertNotIn('shell', kwargs)
                self.assertEqual(kwargs['stdin'], collect.subprocess.DEVNULL)

    def test_tool_error_stops_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(collect.subprocess, 'run', return_value=mock.Mock(returncode=1)), self.assertRaises(ValueError):
                collect.run_tool(['fixed-reader'], Path(tmp), 'error.txt')

    def test_tool_will_not_overwrite_old_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'old.txt'; p.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                collect.run_tool(['must-not-run'], Path(tmp), 'old.txt')
            self.assertEqual(p.read_bytes(), b'keep')

    def test_cli_explicit_modules(self):
        with mock.patch.object(collect, 'main', return_value=0) as run:
            self.assertEqual(collect.entry(['--module', 'MEE', '--module', 'FLT']), 0)
            self.assertEqual(run.call_args_list, [mock.call('MEE'), mock.call('FLT')])

    def test_cli_rejects_unknown_or_duplicate_modules(self):
        with mock.patch.object(collect, 'main') as run, contextlib.redirect_stderr(io.StringIO()):
            for args in (['--module', '../other'], ['--module', 'MEE', '--module', 'MEE']):
                with self.subTest(args=args), self.assertRaises(SystemExit):
                    collect.entry(args)
            run.assert_not_called()

    def test_cli_stops_on_failure_without_retry(self):
        with mock.patch.object(collect, 'main', return_value=2) as run:
            self.assertEqual(collect.entry(['--module', 'MEE', '--module', 'FLT']), 2)
            run.assert_called_once_with('MEE')

    def test_default_module_is_unchanged(self):
        with mock.patch.object(collect, 'main', return_value=0) as run:
            self.assertEqual(collect.entry([]), 0)
            run.assert_called_once_with('AfterFXLib')

    def test_failure_retains_identity_for_allowlisted_modules(self):
        import json
        for module in ('MEE', 'FLT'):
            with self.subTest(module=module), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp).resolve()
                app = base / 'app'
                image = app / collect.IMAGE_PATHS[module]
                image.parent.mkdir(parents=True)
                image.write_bytes(b'owned synthetic image')
                host = app / 'Contents/MacOS/After Effects'
                host.parent.mkdir(parents=True)
                host.write_bytes(b'owned synthetic host')
                (base / 'Desktop').mkdir()
                image_hash, host_hash = collect.digest(image), collect.digest(host)

                def fail(argv, folder, name, timeout=60):
                    record = json.loads((folder / 'record.json').read_text())
                    self.assertEqual(record['image_before_sha256'], image_hash)
                    self.assertEqual(record['module'], module)
                    self.assertEqual(record['capture_status'], 'NOT RUN')
                    self.assertEqual(argv[-1], str(image))
                    raise OSError('synthetic inspection failure')

                with mock.patch.object(collect.sys, 'platform', 'darwin'), \
                        mock.patch.object(collect, 'APP', app), \
                        mock.patch.object(collect, 'MAIN_SHA256', host_hash), \
                        mock.patch.object(Path, 'home', return_value=base), \
                        mock.patch.object(collect, 'run_tool', side_effect=fail), \
                        contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(collect.main(module), 2)
                records = list((base / 'Desktop').glob('*/record.json'))
                self.assertEqual(len(records), 1)
                record = json.loads(records[0].read_text())
                self.assertEqual(record['capture_status'], 'FAIL')
                self.assertEqual(record['runtime_registration'], 'NOT RUN')
                self.assertEqual(record['image_before_sha256'], image_hash)
                self.assertIsNone(record['image_after_sha256'])
                self.assertNotIn('record.json', record['files_sha256'])
                self.assertEqual(collect.digest(image), image_hash)
                self.assertEqual(collect.digest(host), host_hash)


if __name__ == '__main__':
    unittest.main()
