"""Offline unit tests for the bounded Stage C1 ABI collector."""
from pathlib import Path
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "experiments/ordinary_discovery/collect_resource_search_abi.py"
spec = importlib.util.spec_from_file_location("resource_abi_collector", MODULE)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ResourceAbiCollectorTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", "requires macOS arm64 file disassembly")
    def test_real_lldb_disassembles_owned_bounded_window(self):
        with tempfile.TemporaryDirectory(prefix="aehl-owned-abi-") as tmp:
            folder = Path(tmp).resolve()
            source = folder / "owned.s"
            source.write_text(".text\n.globl _owned_abi_probe\n.p2align 2\n"
                              "_owned_abi_probe:\n add w0, w0, #1\n ret\n"
                              ".data\n.p2align 3\n.globl _owned_abi_data\n"
                              "_owned_abi_data:\n.quad 0x1234\n.quad 0x5678\n")
            binary = folder / "owned.bundle"
            subprocess.run(["/usr/bin/xcrun", "clang", "-arch", "arm64", "-bundle",
                            str(source), "-o", str(binary)], check=True,
                           capture_output=True, timeout=45)
            symbols = subprocess.check_output(["/usr/bin/nm", "-arch", "arm64", "-n",
                                               str(binary)], text=True, timeout=15)
            match = re.search(r"^([0-9a-fA-F]+)\s+T\s+_owned_abi_probe$", symbols, re.M)
            self.assertIsNotNone(match, symbols)
            start = int(match.group(1), 16)
            script = folder / "inspect.lldb"
            script.write_text(collector.lldb_script(binary, start, start + 8))
            output, diagnostics = collector.run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch", "--source", str(script)])
            self.assertNotIn("error:", (output + diagnostics).lower())
            self.assertRegex(output, r"add\s+w0, w0, #0x1")
            self.assertRegex(output, r"\bret\b")
            self.assertEqual(collector.validate_disassembly(output, start, start + 8), 2)
            data_symbol = re.search(r"^([0-9a-fA-F]+)\s+[DS]\s+_owned_abi_data$", symbols, re.M)
            self.assertIsNotNone(data_symbol, symbols)
            data_start = int(data_symbol.group(1), 16)
            data_script = folder / "data.lldb"
            data_script.write_text(collector.lldb_data_script(binary, data_start, 2))
            output, diagnostics = collector.run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch", "--source", str(data_script)])
            self.assertNotIn("error:", (output + diagnostics).lower())
            self.assertEqual(collector.validate_data(output, data_start, 2), [0x1234, 0x5678])

    def test_file_data_requires_exact_coverage(self):
        text = '0x00001000: 0x0000000000001234 0x0000000000005678\n'
        self.assertEqual(collector.validate_data(text, 0x1000, 2), [0x1234, 0x5678])
        for bad in ('', text + text, text.replace('1000', '1008'),
                    text.replace(' 0x0000000000005678', ''), text.replace('5678', 'oops')):
            with self.subTest(output=bad), self.assertRaisesRegex(ValueError, 'bounds'):
                collector.validate_data(bad, 0x1000, 2)

    def test_file_data_script_is_bounded_and_offline(self):
        script = collector.lldb_data_script(Path('/tmp/owned.bundle'), 0x1000, 2)
        self.assertIn('target create --no-dependents --arch arm64', script)
        self.assertIn('memory read --format x --size 8 --count 2 0x1000\n', script)
        self.assertNotIn('process launch', script)
        self.assertNotIn('process attach', script)
        for start, count in ((0, 2), (0x1004, 2), (0x1000, 0), (0x1000, 33)):
            with self.subTest(start=start, count=count), self.assertRaisesRegex(ValueError, 'bounded'):
                collector.lldb_data_script(Path('/tmp/owned.bundle'), start, count)

    def test_disassembly_requires_exact_decoded_coverage(self):
        text = "owned[0x1000] <+0>: add w0, w0, #0x1\nowned[0x1004] <+4>: ret\n"
        self.assertEqual(collector.validate_disassembly(text, 0x1000, 0x1008), 2)
        for bad in ("", text.splitlines()[0], text + text,
                    text.replace("0x1004", "0x1008")):
            with self.subTest(output=bad), self.assertRaisesRegex(ValueError, "bounds"):
                collector.validate_disassembly(bad, 0x1000, 0x1008)
        with self.assertRaisesRegex(ValueError, "undecoded"):
            collector.validate_disassembly(text.replace("ret", ".long 0"), 0x1000, 0x1008)

    def test_profile_pins_agree_with_header(self):
        collector.profile_agrees()

    def test_cpp_exception_comment_is_not_a_tool_error(self):
        text = ('owned[0x1000] <+0>: bl 0x2000 ; std::runtime_error::runtime_error(char const*)\n'
                'owned[0x1004] <+4>: ret\n')
        self.assertEqual(collector.verify_lldb_disassembly(text, '', 0x1000, 0x1008), 2)
        for output, diagnostics in ((text + 'error: command failed\n', ''),
                                    (text, 'error: target failed\n'),
                                    (text + 'fatal: invalid image\n', ''),
                                    (text, 'fatal: invalid image\n')):
            with self.subTest(output=output, diagnostics=diagnostics):
                with self.assertRaisesRegex(ValueError, 'inspection error'):
                    collector.verify_lldb_disassembly(output, diagnostics, 0x1000, 0x1008)

    def test_tool_comment_handling_does_not_accept_bad_decode(self):
        text = ('owned[0x1000] <+0>: nop ; error: harmless instruction comment\n'
                'owned[0x1004] <+4>: .long 0 ; error: undecoded\n')
        with self.assertRaisesRegex(ValueError, 'undecoded'):
            collector.verify_lldb_disassembly(text, '', 0x1000, 0x1008)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            collector.verify_lldb_disassembly(text.splitlines()[0], '', 0x1000, 0x1008)
        text = text.replace('.long 0', 'error: target failed')
        with self.assertRaisesRegex(ValueError, 'inspection error'):
            collector.verify_lldb_disassembly(text, '', 0x1000, 0x1008)

    def test_publication_review_covers_complete_split_functions(self):
        windows = collector.review_windows('publication')
        self.assertEqual({name for _, name, _, _ in windows}, {'PLUG', 'FLT'})
        self.assertEqual({label for label, *_ in windows}, set(collector.PUBLICATION_ANCHORS))
        for labels, start, end in ((('FLT-setup-a', 'FLT-setup-b'), 0x8d250, 0x8ef8c),
                                  (('FLT-add-a', 'FLT-add-b'), 0x8b2d4, 0x8cc70)):
            selected = [(s, e) for label, _, s, e in windows if label in labels]
            self.assertEqual(selected[0][0], start)
            self.assertEqual(selected[-1][1], end)
            self.assertEqual(selected[0][1], selected[1][0])

    def test_effect_readiness_scope_separates_constructor_and_delegate(self):
        windows = collector.review_windows('effect-readiness')
        self.assertEqual({label for label, *_ in windows}, set(collector.READINESS_ANCHORS))
        self.assertEqual(sum((end - start) // 4 for _, _, start, end in windows), 1136)
        selected = {label: (name, start, end) for label, name, start, end in windows}
        self.assertEqual(selected['PLUG-path-ctor'], ('PLUG', 0xc9b4, 0xcc9c))
        self.assertEqual(selected['PLUG-classref'], ('PLUG', 0xcc9c, 0xcd74))
        self.assertEqual(selected['PLUG-path-thunk'], ('PLUG', 0xcd74, 0xcd78))
        self.assertEqual(selected['FLT-ready-body'], ('FLT', 0x5cea8, 0x5d0dc))
        self.assertEqual(selected['FLT-lazy-setup'], ('FLT', 0x5d328, 0x5d644))
        self.assertNotIn('FLT-lazy-globals', selected)

    def test_effect_readiness_rejects_each_changed_state_or_ownership_anchor(self):
        for label, _, start, end in collector.review_windows('effect-readiness'):
            anchors = collector.READINESS_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a - start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_readiness(text, label, start, end)
            self.assertEqual(result['structural_anchors'], len(anchors))
            self.assertIn('not-safe-runtime-ABI', result['claim'])
            for address in anchors:
                with self.subTest(label=label, address=hex(address)):
                    with self.assertRaisesRegex(ValueError, 'structural'):
                        collector.verify_readiness(transcript({address: ('nop', '')}),
                                                   label, start, end)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_readiness(text + text.splitlines()[0] + '\n', label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_readiness(text, label, start, end + 4)

    def test_effect_readiness_does_not_select_placeholder_or_global_scan(self):
        selected = collector.select_symbols('external ReadyFilter\nexternal DoLazyGlobalSetup\n'
            'external DoLazyGlobals\nexternal FLTp_DoGlobal\nexternal FLTp_GetStdParams\n'
            'external PLUG_RoutineDescPriv\nexternal CreateClassRef\n'
            'external FLT_RegisterEffectIfMissing\nexternal SetupGeneralPluginScan\n',
            'effect-readiness')
        for name in ('ReadyFilter', 'DoLazyGlobalSetup', 'FLTp_DoGlobal',
                     'FLTp_GetStdParams', 'PLUG_RoutineDescPriv', 'CreateClassRef'):
            self.assertIn(name, selected)
        for name in ('DoLazyGlobals', 'FLT_RegisterEffectIfMissing', 'SetupGeneralPluginScan'):
            self.assertNotIn(name, selected)

    def test_placeholder_procedure_cannot_be_relabelled_as_real_effect(self):
        start, end = 0x993a4, 0x997e4
        text = ''.join('owned[0x%x] <+%d>: nop\n' % (a, a - start)
                       for a in range(start, end, 4))
        with self.assertRaisesRegex(ValueError, 'structural'):
            collector.verify_publication(text, 'FLT-if-missing', start, end)
        with self.assertRaisesRegex(ValueError, 'unreviewed'):
            collector.verify_publication(text, 'FLT-if-missing', start, end - 4)

    def test_dispatch_scope_includes_both_procedure_lanes_and_parameter_body(self):
        windows = collector.review_windows('effect-dispatch')
        self.assertEqual({label for label, *_ in windows}, set(collector.DISPATCH_ANCHORS))
        self.assertEqual({name for _, name, *_ in windows}, {'FLT'})
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 1939)
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)
        self.assertEqual(collector.DISPATCH_ANCHORS['FLT-dispatch-crash'][0x3b8e0],
                         ('blr', 'x8'))
        self.assertEqual(collector.DISPATCH_ANCHORS['FLT-dispatch-machine'][0x3b530],
                         ('blr', 'x8'))

    def test_dispatch_rejects_every_changed_call_or_state_anchor(self):
        for label, _, start, end in collector.review_windows('effect-dispatch'):
            anchors = collector.DISPATCH_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_dispatch(text, label, start, end)
            self.assertEqual(result['structural_anchors'], len(anchors))
            self.assertIn('not-safe-runtime-ABI', result['claim'])
            for address in anchors:
                with self.subTest(label=label, address=hex(address)):
                    with self.assertRaisesRegex(ValueError, 'structural'):
                        collector.verify_dispatch(transcript({address: ('nop', '')}),
                                                  label, start, end)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_dispatch(text + text.splitlines()[0]+'\n', label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_dispatch(text, label, start, end+4)

    def test_dispatch_symbol_scope_excludes_scan_and_registration(self):
        text = 'external FLTp_DispatchFilter\nexternal FLTp_DoParamsSetup\n' \
               'external U_GenericPluginDispatch\nexternal PLUG_Search\n' \
               'external FLT_RegisterEffectIfMissing\nexternal FLTp_FiltSetup\n'
        selected = collector.select_symbols(text, 'effect-dispatch')
        for name in ('FLTp_DispatchFilter', 'FLTp_DoParamsSetup', 'U_GenericPluginDispatch'):
            self.assertIn(name, selected)
        for name in ('PLUG_Search', 'FLT_RegisterEffectIfMissing', 'FLTp_FiltSetup'):
            self.assertNotIn(name, selected)

    def test_publication_symbol_scope_does_not_select_general_plugin_setup(self):
        selected = collector.select_symbols('external _FLT_RegisterEffectIfMissing\n'
            'external _FLTp_FiltSetup\nexternal _PLUG_RegisterRoutine\n'
            'external _SetupGeneralPluginScan\nexternal _PLUG_Search', 'publication')
        self.assertIn('FLT_RegisterEffectIfMissing', selected)
        self.assertIn('FLTp_FiltSetup', selected)
        self.assertIn('PLUG_RegisterRoutine', selected)
        self.assertNotIn('SetupGeneralPluginScan', selected)
        self.assertNotIn('PLUG_Search', selected)

    def test_review_scope_rejects_invalid_windows(self):
        self.assertEqual(collector.review_windows("search-abi"),
                         tuple((name, name, *bounds) for name, bounds in collector.WINDOWS.items()))
        windows = collector.review_windows("cleanup")
        self.assertEqual({name for _, name, _, _ in windows}, {"PLUG", "FLT", "MEE"})
        self.assertEqual(sum((end - start) // 4 for _, _, start, end in windows), 1390)
        for bad, reason in (
            ((('same', 'PLUG', 0x1000, 0x1008),) * 2, 'duplicate'),
            ((('../escape', 'PLUG', 0x1000, 0x1008),), 'identity'),
            ((('owned', 'unknown', 0x1000, 0x1008),), 'identity'),
            ((('owned', 'PLUG', 0x1000, 0x3000),), 'bounded'),
        ):
            with mock.patch.dict(collector.REVIEWS, {'invalid': bad}):
                with self.subTest(windows=bad), self.assertRaisesRegex(ValueError, reason):
                    collector.review_windows('invalid')
        with self.assertRaisesRegex(ValueError, 'unknown'):
            collector.review_windows('unbounded')

    def test_cleanup_symbol_selection_excludes_search_scope(self):
        text = '\n'.join(('external __Z16PLUG_InstallScan',
                          'non-external __ZL17PluginCleanupFunc',
                          'external __Z24CleanupGeneralPluginScan',
                          'external __Z11PLUG_Search', 'external _Unrelated'))
        selected = collector.select_symbols(text, 'cleanup')
        self.assertIn('PLUG_InstallScan', selected)
        self.assertIn('PluginCleanupFunc', selected)
        self.assertNotIn('PLUG_Search', selected)
        self.assertNotIn('Unrelated', selected)

    def test_ownership_review_has_exact_mapped_windows_and_no_registration_call(self):
        windows = collector.review_windows('ownership')
        self.assertEqual({name for _, name, _, _ in windows}, {'MEE'})
        self.assertEqual(sum((end - start) // 4 for _, _, start, end in windows), 960)
        self.assertEqual({label for label, *_ in windows}, set(collector.OWNERSHIP_ANCHORS))
        for label, name, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[name][0], start, end)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)

    def test_decoded_ownership_window_cannot_pass_with_wrong_state_operations(self):
        text = ''.join('owned[0x%x] <+%d>: nop\n' % (a, a - 0x37eec)
                       for a in range(0x37eec, 0x37f34, 4))
        with self.assertRaisesRegex(ValueError, 'structural'):
            collector.verify_ownership(text, 'MEE-finish', 0x37eec, 0x37f34)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            collector.verify_ownership(text.splitlines()[0], 'MEE-finish', 0x37eec, 0x37f34)
        with self.assertRaisesRegex(ValueError, 'unreviewed'):
            collector.verify_ownership(text, 'MEE-finish', 0x37eec, 0x37f30)

    def test_ownership_symbol_scope_excludes_ordinary_resource_search(self):
        selected = collector.select_symbols('external _SetupGeneralPluginScan\n'
            'external _PluginCleanupFunc\nexternal _PLUG_Search\nexternal _Other', 'ownership')
        self.assertIn('SetupGeneralPluginScan', selected)
        self.assertIn('PluginCleanupFunc', selected)
        self.assertNotIn('PLUG_Search', selected)
        self.assertNotIn('Other', selected)

    def test_lldb_script_is_bounded_and_offline(self):
        path = Path("/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib")
        script = collector.lldb_script(path, 0x8A6C, 0x8C20)
        self.assertIn("target create --no-dependents --arch arm64", script)
        self.assertIn("disassemble --start-address 0x8a6c --end-address 0x8c20\n", script)
        self.assertNotIn("process launch", script)
        self.assertNotIn("process attach", script)
        with self.assertRaisesRegex(ValueError, "bounded"):
            collector.lldb_script(path, 0x1000, 0x3000)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            collector.lldb_script(Path('/tmp/bad"name'), 0x1000, 0x1100)

    def test_symbol_selection_is_narrow(self):
        text = "\n".join([
            "0000000000001000 (__TEXT,__text) external _PLUG_Search",
            "0000000000002000 (__TEXT,__text) non-external __Z14Egg_PlugSearchv",
            "0000000000003000 (__TEXT,__text) non-external __Z14SearchStatFuncv",
            "0000000000004000 (__TEXT,__text) external _Unrelated",
        ])
        selected = collector.select_symbols(text)
        self.assertIn("PLUG_Search", selected)
        self.assertIn("Egg_PlugSearch", selected)
        self.assertIn("SearchStatFunc", selected)
        self.assertNotIn("Unrelated", selected)

    def test_package_has_exact_hash_manifest(self):
        with tempfile.TemporaryDirectory(prefix="aehl-resource-abi-test-") as tmp:
            folder = Path(tmp) / "evidence"
            folder.mkdir(mode=0o700)
            collector.write_exclusive(folder / "aelib-disassembly.txt", "bounded\n")
            archive = collector.package(folder, {
                "schema": "AEHL-C1-RESOURCE-ABI-1",
                "scope": "offline-bounded-resource-search-abi-only",
            })
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as z:
                names = set(z.namelist())
                self.assertEqual(names, {"aelib-disassembly.txt", "record.json", "SHA256.json"})
                hashes = json.loads(z.read("SHA256.json"))
                self.assertEqual(set(hashes), names - {"SHA256.json"})


if __name__ == "__main__":
    unittest.main()
