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

    def test_plugin_metadata_scope_is_complete_and_offline(self):
        windows = collector.review_windows('plugin-metadata')
        self.assertEqual(len(windows), 6)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 744)
        self.assertEqual({image for _, image, *_ in windows}, {'PluginSupport'})
        self.assertEqual({label for label, *_ in windows}, set(collector.METADATA_ANCHORS))
        self.assertNotIn('plugin-metadata', collector.DATA_WINDOWS)
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')

    def test_plugin_metadata_rejects_changed_context_conversion_and_teardown(self):
        # Synthetic parser/refusal controls only, never evidence about Adobe execution.
        for label, _, start, end in collector.review_windows('plugin-metadata'):
            anchors = collector.METADATA_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_metadata(text, label, start, end)
            self.assertEqual(result['claim'], 'file-only-metadata-flow-not-registry-publication')
            for address, (op, args) in anchors.items():
                # Same mnemonic with wrong receiver/target must fail as well as removed operation.
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address), wrong=wrong):
                        with self.assertRaisesRegex(ValueError, 'structural'):
                            collector.verify_metadata(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1])]:
                with self.assertRaisesRegex(ValueError, 'bounds'):
                    collector.verify_metadata(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'undecoded'):
                collector.verify_metadata(text.replace(': ', ': .long ', 1), label, start, end)
            for wrong_label, wrong_end in [('unreviewed', end), (label, end+4)]:
                with self.assertRaisesRegex(ValueError, 'unreviewed'):
                    collector.verify_metadata(text, wrong_label, start, wrong_end)

    def test_plugin_metadata_catalog_limits_symbols(self):
        names = ['PluginDataCallback2', 'PluginDataCallback', 'GetPFPluginData',
                 'PFPluginDataToPiPL', 'PluginImplGetPiPLs', 'PF_PluginDataD2']
        selected = collector.select_symbols('\n'.join('external '+n for n in names)+
                                            '\nexternal PLUG_Search\n', 'plugin-metadata')
        for name in names:
            self.assertIn(name, selected)
        self.assertNotIn('PLUG_Search', selected)

    def test_registry_consumers_keeps_fixed_file_scope_and_no_host_calls(self):
        windows = collector.review_windows('registry-consumers')
        self.assertEqual({key for _, key, *_ in windows}, {'FLT'})
        self.assertEqual({label for label, *_ in windows}, set(collector.CONSUMER_ANCHORS))
        self.assertEqual(len(windows), 14)
        for label, key, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[key][0], start, end)
            self.assertNotIn('process launch', script)
            self.assertNotIn('process attach', script)
            self.assertLessEqual((end-start)//4, 4096)

    def test_registry_consumers_rejects_changed_mutation_lock_and_tls_paths(self):
        for label, _, start, end in collector.review_windows('registry-consumers'):
            anchors = collector.CONSUMER_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertEqual(collector.verify_consumers(text, label, start, end)['claim'],
                             'file-only-no-global-barrier-or-rollback-proof')
            for address in anchors:
                with self.subTest(label=label, address=hex(address)), self.assertRaisesRegex(ValueError, 'structural'):
                    collector.verify_consumers(transcript({address: ('nop', '')}), label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_consumers(text, label, start, end+4)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_consumers(text+text.splitlines()[0]+'\n', label, start, end)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_consumers('\n'.join(text.splitlines()[:-1]), label, start, end)

    def test_registry_consumers_catalog_includes_project_tls_and_registry_paths(self):
        names = ('FLT_FilterRegistryD2', 'FLT_FilterRegistryUpdateEffectFromPrefs',
                 'FLT_FilterRegistryReplaceByNewerFilter',
                 'FLT_FilterRegistryGetAllEffectSettingsForPluginManager',
                 'FLT_ScBeginProjectRead', 'FLT_ScBeginProjectWrite')
        text = '\n'.join('external '+name for name in names)+ '\nexternal PLUG_Search\n'
        selected = collector.select_symbols(text, 'registry-consumers')
        for name in names:
            self.assertIn(name, selected)
        self.assertNotIn('PLUG_Search', selected)

    def test_registry_catalog_contains_notifier_counter_and_wrapper_symbols(self):
        names = ('__ZN15FLT_RenderState12RenderScoperD1Ev',
                 '__ZN15FLT_RenderState29CreateScoper_RenderingEffectsEv',
                 '__ZN15FLT_RenderState29GetNumThreadsRenderingEffectsEv',
                 '__Z33FLT_GetNumThreadsRenderingEffectsv',
                 '__Z27FLT_NotifyFilterLoadingDoneRKSt3__16vector')
        text = '\n'.join('0000000000000000 (__TEXT,__text) external '+n for n in names)
        selected = collector.select_symbols(text, 'registry-transaction')
        for name in names:
            self.assertIn(name, selected)

    def test_registry_transaction_scope_is_complete_and_file_only(self):
        windows = collector.review_windows('registry-transaction')
        self.assertEqual(len(windows), 17)
        self.assertEqual(sum((b-a)//4 for _, _, a, b in windows), 3063)
        self.assertEqual({label for label, *_ in windows}, set(collector.REGISTRY_ANCHORS))
        self.assertEqual({key for _, key, *_ in windows}, {'aelib', 'FLT'})
        for _, key, a, b in windows:
            script = collector.lldb_script(collector.INPUTS[key][0], a, b)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)
        self.assertEqual(collector.REGISTRY_ANCHORS['FLT-render-count'][0x30e6c],
                         ('ldr', 'w0,[x8,#0xaf8]'))
        self.assertEqual(collector.REGISTRY_ANCHORS['FLT-registry-done'][0x6098],
                         ('strb', 'w8,[x20,#0x48]'))

    def test_registry_transaction_refuses_altered_lock_counter_and_completion_paths(self):
        for label, _, start, end in collector.review_windows('registry-transaction'):
            anchors = collector.REGISTRY_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertIn('not-native-exclusion',
                          collector.verify_registry_transaction(text, label, start, end)['claim'])
            for a in anchors:
                with self.subTest(label=label, address=hex(a)), self.assertRaisesRegex(ValueError, 'structural'):
                    collector.verify_registry_transaction(transcript({a: ('nop', '')}), label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_registry_transaction(text, label, start, end+4)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_registry_transaction(text+text.splitlines()[0]+'\n', label, start, end)

    def test_provider_isolation_scope_is_complete_and_keeps_live_boundary(self):
        windows = collector.review_windows('provider-isolation')
        self.assertEqual({key for _, key, *_ in windows}, {'PluginSupport', 'PLUG', 'FLT'})
        self.assertEqual({label for label, *_ in windows}, set(collector.ISOLATION_ANCHORS))
        self.assertEqual(len(windows), 16)
        self.assertEqual(sum((b-a)//4 for _, _, a, b in windows), 884)
        self.assertEqual({x[0] for x in collector.DATA_WINDOWS['provider-isolation']},
                         set(collector.ISOLATION_SLOTS))
        for _, key, a, b in windows:
            script = collector.lldb_script(collector.INPUTS[key][0], a, b)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)

    def test_provider_isolation_refuses_changed_counter_and_owner_paths(self):
        for label, _, start, end in collector.review_windows('provider-isolation'):
            anchors = collector.ISOLATION_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertIn('not-host-wide', collector.verify_isolation(text, label, start, end)['claim'])
            for a in anchors:
                with self.subTest(label=label, address=hex(a)), self.assertRaisesRegex(ValueError, 'structural'):
                    collector.verify_isolation(transcript({a: ('nop', '')}), label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_isolation(text, label, start, end+4)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_isolation(text+text.splitlines()[0]+'\n', label, start, end)

    def test_provider_slots_require_exact_bind_or_rebase_and_unique_fixup(self):
        chains = 'pointer_format: 6 (DYLD_CHAINED_PTR_64_OFFSET)'
        for label, _, start, _ in collector.DATA_WINDOWS['provider-isolation']:
            raw, kind, target = collector.ISOLATION_SLOTS[label]
            fixup = '__DATA_CONST __const 0x%x %s %s\n' % (start, kind, target)
            result = collector.verify_isolation_slot([raw], fixup, chains, label)
            self.assertEqual(result['target'], target)
            self.assertIn('not-runtime-receiver', result['claim'])
            for words in ([], [raw, raw], [raw ^ 1], [raw ^ (1 << 63)]):
                with self.subTest(label=label, words=words), self.assertRaisesRegex(ValueError, 'serialized'):
                    collector.verify_isolation_slot(words, fixup, chains, label)
            for bad in ('', fixup+fixup, fixup.replace(target, 'WrongTarget'),
                        fixup.replace(' %s ' % kind, ' wrong '),
                        fixup.replace('0x%x' % start, '0x%x' % (start+8))):
                with self.subTest(label=label, fixup=bad), self.assertRaisesRegex(ValueError, 'fixup target'):
                    collector.verify_isolation_slot([raw], bad, chains, label)
            with self.assertRaisesRegex(ValueError, 'format'):
                collector.verify_isolation_slot([raw], fixup, chains.replace('6 (', '2 ('), label)

    def test_provider_slot_unknown_label_cannot_extend_review_scope(self):
        with self.assertRaisesRegex(ValueError, 'unreviewed'):
            collector.verify_isolation_slot([0], '', '', 'unreviewed-live-slot')

    def test_provider_factory_scope_is_complete_and_file_only(self):
        windows = collector.review_windows('provider-factory')
        self.assertEqual({name for _, name, *_ in windows}, {'PluginSupport', 'TDB'})
        self.assertEqual({label for label, *_ in windows}, set(collector.RETENTION_ANCHORS))
        self.assertEqual(sum((b-a)//4 for _, _, a, b in windows), 1365)
        self.assertEqual(collector.RETENTION_ANCHORS['PS-free'], {0x4c55c: ('ret', '')})
        for _, key, a, b in windows:
            script = collector.lldb_script(collector.INPUTS[key][0], a, b)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)

    def test_retention_rejects_changed_ownership_or_erasure_instructions(self):
        for label, key, start, end in collector.review_windows('provider-factory'):
            anchors = collector.RETENTION_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_retention(text, label, start, end)
            self.assertEqual(result['structural_anchors'], len(anchors))
            self.assertIn('not-runtime-lifetime-or-rollback', result['claim'])
            for address in anchors:
                with self.subTest(label=label, address=hex(address)):
                    with self.assertRaisesRegex(ValueError, 'structural'):
                        collector.verify_retention(transcript({address: ('nop', '')}),
                                                   label, start, end)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_retention(text + text.splitlines()[0]+'\n', label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_retention(text, label, start, end+4)

    def test_file_only_pins_cannot_change_scope_or_native_profile(self):
        record = json.loads(collector.FILE_ONLY_PROFILE.read_text())
        self.assertEqual(set(record['inputs']), {'TDB', 'ASLFoundation'})
        self.assertNotIn('TDB.dylib', collector.PROFILE.read_text())
        self.assertNotIn('ASLFoundation.framework', collector.PROFILE.read_text())
        with tempfile.TemporaryDirectory(prefix='aehl-file-pins-') as tmp:
            path = Path(tmp)/'pins.json'
            with mock.patch.object(collector, 'FILE_ONLY_PROFILE', path):
                path.write_text(json.dumps(record)); collector.profile_agrees()
                for field, value in (('scope', 'live'), ('schema', 'unreviewed'),
                                     ('extra', True), ('inputs', {})):
                    bad = dict(record); bad[field] = value
                    path.write_text(json.dumps(bad))
                    with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'file-only'):
                        collector.profile_agrees()
                for name in record['inputs']:
                    bad = json.loads(json.dumps(record)); bad['inputs'][name]['sha256'] = '0'*64
                    path.write_text(json.dumps(bad))
                    with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'file-only'):
                        collector.profile_agrees()
                    path.write_text(json.dumps(record))
                    with mock.patch.dict(collector.INPUTS, {name: (Path('/tmp/other'), '0'*64)}):
                        with self.assertRaisesRegex(ValueError, 'file-only'):
                            collector.profile_agrees()

    def test_provider_factory_symbols_exclude_scans(self):
        text = 'external ML_PluginImpl_Load\nexternal TDB_StreamFactory_RegisterCanonicalInstance\n' \
               'external Get_AE_StreamFactory\nexternal PLUG_Search\nexternal SetupGeneralPluginScan\n'
        selected = collector.select_symbols(text, 'provider-factory')
        for name in ('PluginImpl', 'RegisterCanonicalInstance', 'Get_AE_StreamFactory'):
            self.assertIn(name, selected)
        for name in ('PLUG_Search', 'SetupGeneralPluginScan'):
            self.assertNotIn(name, selected)

    def test_entry_lifetime_scope_keeps_destructors_and_thunk_separate(self):
        windows = collector.review_windows('entry-lifetime')
        self.assertEqual({name for _, name, *_ in windows}, {'ASLFoundation', 'FLT', 'PLUG'})
        self.assertEqual({label for label, *_ in windows}, set(collector.ENTRY_ANCHORS))
        self.assertEqual(len(windows), 23)
        self.assertEqual(sum((b-a)//4 for _, _, a, b in windows), 1351)
        self.assertIn(('FLT-desc-release', 'FLT', 0x5cbec, 0x5cc60), windows)
        self.assertIn(('FLT-ctor-thunk', 'FLT', 0x5cc60, 0x5cc64), windows)
        self.assertEqual(collector.ENTRY_ANCHORS['PLUG-unload-plugin'], {0x87a0: ('ret', '')})
        self.assertEqual(sum(n for _, _, _, n in collector.DATA_WINDOWS['entry-lifetime']), 32)
        for _, key, a, b in windows:
            script = collector.lldb_script(collector.INPUTS[key][0], a, b)
            self.assertNotIn('process attach', script)
            self.assertNotIn('process launch', script)

    def test_entry_lifetime_rejects_changed_lifetime_or_cached_procedure_anchors(self):
        for label, key, start, end in collector.review_windows('entry-lifetime'):
            anchors = collector.ENTRY_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_entry_lifetime(text, label, start, end)
            self.assertIn('not-live-lifetime-or-safe-rollback', result['claim'])
            for address in anchors:
                with self.subTest(label=label, address=hex(address)):
                    with self.assertRaisesRegex(ValueError, 'structural'):
                        collector.verify_entry_lifetime(transcript({address: ('nop', '')}),
                                                        label, start, end)
            with self.assertRaisesRegex(ValueError, 'bounds'):
                collector.verify_entry_lifetime(text + text.splitlines()[0]+'\n', label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_entry_lifetime(text, label, start, end+4)

    def test_entry_tables_reject_retargeted_bound_reserved_or_missing_fixups(self):
        for label, key, start, count in collector.DATA_WINDOWS['entry-lifetime']:
            targets = collector.ENTRY_TABLE_TARGETS[label]
            words = [0] + [(2 << 51) | target for target in targets[1:]]
            rows = ['__DATA_CONST __const 0x%x rebase 0x%x' % (start+i*8, target)
                    for i, target in enumerate(targets) if i]
            fixups = '\n'.join(rows)
            chains = 'pointer_format: 6 (DYLD_CHAINED_PTR_64_OFFSET)'
            result = collector.verify_entry_table(words, fixups, chains, label)
            self.assertEqual(result['rebases'], count-1)
            self.assertEqual(result['claim'], 'file-table-correspondence-not-runtime-receiver')
            for i in range(count):
                for mask in (1, 1 << 44, 1 << 63):
                    bad = list(words); bad[i] ^= mask
                    with self.subTest(label=label, index=i, mask=mask), self.assertRaises(ValueError):
                        collector.verify_entry_table(bad, fixups, chains, label)
            for bad in (fixups+'\n'+rows[0], '\n'.join(rows[1:]),
                        fixups.replace('rebase', 'bind'), fixups.replace('0x%x' % targets[1], '0x0')):
                with self.assertRaises(ValueError):
                    collector.verify_entry_table(words, bad, chains, label)
            with self.assertRaises(ValueError):
                collector.verify_entry_table(words[:-1], fixups, chains, label)
            with self.assertRaises(ValueError):
                collector.verify_entry_table(words, fixups, chains.replace('6 (', '2 ('), label)
            with self.assertRaises(ValueError):
                collector.verify_entry_table(words, fixups, chains, 'unreviewed')

    def test_entry_lifetime_symbols_exclude_registration_and_scan(self):
        text = 'external ASL_Module_GetProcAddress\nexternal FLT_FCSpec_GetEffectProc\n' \
               'external PLUGp_LoadPlatRoutine\nexternal PLUG_Search\n' \
               'external RegisterCanonicalInstance\nexternal SetupGeneralPluginScan\n'
        selected = collector.select_symbols(text, 'entry-lifetime')
        for name in ('GetProcAddress', 'GetEffectProc', 'LoadPlatRoutine'):
            self.assertIn(name, selected)
        for name in ('PLUG_Search', 'RegisterCanonicalInstance', 'SetupGeneralPluginScan'):
            self.assertNotIn(name, selected)

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
