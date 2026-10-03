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

    def test_dvacore_symbol_budget_is_bounded_and_does_not_relax_other_outputs(self):
        nm=['/usr/bin/nm','-arch','arm64','-n','-m',str(collector.INPUTS['dvacore'][0])]
        large='x'*(collector.MAX_OUTPUT+1)
        result=subprocess.CompletedProcess(nm,0,stdout=large,stderr='')
        with mock.patch.object(collector.subprocess,'run',return_value=result):
            with self.assertRaisesRegex(ValueError,'exceeded limit'):
                collector.run_tool(nm)
            output,_=collector.run_tool(nm,output_limit=4*1024*1024)
            self.assertEqual(output,large)
            for command,limit in ((nm,True),(nm,0),(nm,4*1024*1024+1),
                                  (['/usr/bin/xcrun','lldb'],4*1024*1024),
                                  (nm[:-1]+[str(collector.INPUTS['MEE'][0])],4*1024*1024)):
                with self.assertRaisesRegex(ValueError,'output budget'):
                    collector.run_tool(command,output_limit=limit)
        oversized=subprocess.CompletedProcess(nm,0,stdout='x'*(4*1024*1024+1),stderr='')
        with mock.patch.object(collector.subprocess,'run',return_value=oversized):
            with self.assertRaisesRegex(ValueError,'exceeded limit'):
                collector.run_tool(nm,output_limit=4*1024*1024)

    def test_transitive_factory_scope_covers_owner_and_guid_dependencies(self):
        windows = collector.review_windows('factory-transitive')
        self.assertEqual(len(windows), 24)
        self.assertEqual(sum((end-start)//4 for _,_,start,end in windows), 1369)
        self.assertEqual({name for _,name,_,_ in windows}, {'dvacore', 'MEE'})
        self.assertEqual({label for label,*_ in windows}, set(collector.TRANSITIVE_ANCHORS))
        selected={label:(name,start,end) for label,name,start,end in windows}
        self.assertEqual(selected['trans-map-init'], ('dvacore',0xb0f94,0xb1008))
        self.assertEqual(selected['trans-map-dtor'], ('dvacore',0xb1008,0xb1030))
        self.assertEqual(selected['trans-map-destroy'], ('dvacore',0xb1030,0xb1078))
        self.assertEqual(selected['trans-mee-guid-init'], ('MEE',0x45214,0x45a08))
        self.assertEqual(selected['trans-weak-lock-stub'], ('dvacore',0x2fef34,0x2fef40))
        self.assertNotIn('factory-transitive', collector.DATA_WINDOWS)
        self.assertLessEqual(max(end-start for _,_,start,end in windows),4096)

    def test_transitive_factory_rejects_changed_creation_lock_owner_and_guid(self):
        for label,_,start,end in collector.review_windows('factory-transitive'):
            anchors=collector.TRANSITIVE_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a,a-start,*overrides.get(a,anchors.get(a,('nop',''))))
                    for a in range(start,end,4))
            good=transcript({})
            result=collector.verify_transitive(good,label,start,end)
            self.assertEqual(result['decoded_instructions'],(end-start)//4)
            self.assertIn('not-supported-host-ownership',result['claim'])
            for address in anchors:
                with self.subTest(label=label,address=address),self.assertRaisesRegex(ValueError,'anchors'):
                    collector.verify_transitive(transcript({address:('nop','tampered')}),label,start,end)
            for bad in (good+good,good.splitlines()[0],good.replace(': nop',': .long',1) if ': nop' in good else ''):
                with self.assertRaises(ValueError):collector.verify_transitive(bad,label,start,end)
            with self.assertRaisesRegex(ValueError,'unreviewed'):
                collector.verify_transitive(good,label,start,end+4)

    def test_transitive_factory_catalog_and_dvacore_pin_are_explicit(self):
        lines=('00000000000abbfc (__TEXT,__text) external __ZN7dvacore8classref12ClassFactory13RegisterClass\n'
               '00000000000b14d8 (__TEXT,__text) external __ZN7dvacore8classref11UnknownBase17GetSharedFromThisEv\n'
               '0000000000045214 (__TEXT,__text) non-external __GLOBAL__sub_I_MEE_Plugins.cpp\n'
               '0000000000004000 (__TEXT,__text) external unrelated\n')
        selected=collector.select_symbols(lines,'factory-transitive')
        self.assertIn('RegisterClass',selected)
        self.assertIn('GetSharedFromThis',selected)
        self.assertIn('sub_I_MEE_Plugins',selected)
        self.assertNotIn('unrelated',selected)
        path,pin=collector.INPUTS['dvacore']
        self.assertEqual(pin,'cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0')
        self.assertNotIn('dvacore',collector.FILE_ONLY_INPUTS)
        self.assertIn(str(path),collector.PROFILE.read_text())
        collector.profile_agrees()

    def test_factory_receiver_scope_is_complete_and_excludes_live_calls(self):
        windows=collector.review_windows('factory-receiver')
        self.assertEqual(len(windows),14)
        self.assertEqual(sum((b-a)//4 for _,_,a,b in windows),563)
        self.assertEqual({image for _,image,*_ in windows},{'MEE'})
        self.assertEqual({label for label,*_ in windows},set(collector.RECEIVER_ANCHORS))
        self.assertIn(('recv-register','MEE',0x3dfb8,0x3e150),windows)
        for _,image,a,b in windows:
            script=collector.lldb_script(collector.INPUTS[image][0],a,b)
            self.assertIn('target create --no-dependents --arch arm64',script)
            self.assertNotRegex(script,r'process|expression|call ')
        self.assertEqual(collector.DATA_WINDOWS['factory-receiver'],
                         (('recv-base-adjust','MEE',0xef608,1),('recv-shared-adjust','MEE',0xef628,1)))

    def test_factory_receiver_refuses_changed_query_creation_retention_and_destruction(self):
        for label,_,start,end in collector.review_windows('factory-receiver'):
            anchors=collector.RECEIVER_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n'%
                    (a,a-start,*overrides.get(a,anchors.get(a,('nop','')))) for a in range(start,end,4))
            text=transcript({})
            self.assertEqual(collector.verify_receiver(text,label,start,end)['claim'],
                             'file-only-receiver-acquisition-not-supported-host-ownership-or-call-ABI')
            for address,(op,args) in anchors.items():
                for wrong in [('nop',''),(op,args+'x0')]:
                    with self.subTest(label=label,address=hex(address)),self.assertRaises(ValueError):
                        collector.verify_receiver(transcript({address:wrong}),label,start,end)
            for bad in (text+text.splitlines()[0]+'\n','\n'.join(text.splitlines()[:-1]),
                        text.replace(': ',': .long ',1)):
                with self.assertRaises(ValueError):collector.verify_receiver(bad,label,start,end)
            with self.assertRaises(ValueError):collector.verify_receiver(text,label,start,end+4)

    def test_factory_receiver_adjustments_are_distinct_signed_metadata_not_pointers(self):
        chains='pointer_format: 6 (DYLD_CHAINED_PTR_64_OFFSET)'
        for label,_,start,count in collector.DATA_WINDOWS['factory-receiver']:
            expected=0 if label=='recv-base-adjust' else 0x38
            result=collector.verify_receiver_adjustment([expected],'',chains,label)
            self.assertEqual(result['signed_adjustment'],expected)
            self.assertEqual(result['claim'],'file-header-adjustment-not-live-pointer-or-lifetime')
            for words,fixups,formats,name in [([False],'',chains,label),([expected^1],'',chains,label),([], '',chains,label),
                    ([expected,expected],'',chains,label),([expected],'__DATA_CONST __const 0x%x rebase 0x0'%start,chains,label),
                    ([expected],'',chains.replace('6 (','2 ('),label),([expected],'',chains,'unreviewed')]:
                with self.assertRaises(ValueError):collector.verify_receiver_adjustment(words,fixups,formats,name)

    def test_factory_receiver_catalog_keeps_registration_acquisition_and_owner_boundaries(self):
        names=['MEE_RegisterVideoFilterFactory','AELibraryVideoFilterFactoryInstance',
               'AELibraryVideoFilterFactoryQueryMap','AELibraryVideoFilterFactoryCreateInstanceRef',
               'AELibraryVideoFilterFactoryD2Ev','shared_ptrAELibraryVideoFilterFactoryD1Ev',
               'UnknownBaseGetSharedFromThis','ClassFactoryRegisterClass','CreateClassInstanceRef']
        chosen=collector.select_symbols('\n'.join('external '+n for n in names)+
                                        '\nexternal PLUG_Search\n','factory-receiver')
        for name in names:self.assertIn(name,chosen)
        self.assertNotIn('PLUG_Search',chosen)

    def test_factory_identity_scope_is_complete_offline_and_separate_from_receiver(self):
        windows = collector.review_windows('factory-identity')
        self.assertEqual(len(windows), 9)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 643)
        self.assertEqual({image for _, image, *_ in windows}, {'PluginSupport', 'MEE'})
        self.assertEqual({label for label, *_ in windows}, set(collector.FACTORY_IDENTITY_ANCHORS))
        self.assertEqual(collector.DATA_WINDOWS['factory-identity'],
                         (('factory-primary-table', 'MEE', 0xef640, 11),))
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')

    def test_factory_identity_refuses_changed_ownership_guards_and_base_adjustment(self):
        for label, _, start, end in collector.review_windows('factory-identity'):
            anchors = collector.FACTORY_IDENTITY_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertEqual(collector.verify_factory_identity(text, label, start, end)['claim'],
                             'file-only-factory-identity-not-runtime-receiver-or-registration-ABI')
            for address, (op, args) in anchors.items():
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address)), self.assertRaises(ValueError):
                        collector.verify_factory_identity(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1]),
                        text.replace(': ', ': .long ', 1)]:
                with self.assertRaises(ValueError):
                    collector.verify_factory_identity(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'unreviewed'):
                collector.verify_factory_identity(text, label, start, end+4)

    def test_factory_primary_table_refuses_retargeting_binding_and_incomplete_fixups(self):
        label = 'factory-primary-table'; start = 0xef640
        targets = collector.FACTORY_TABLE_TARGETS
        words = [(2 << 51) | target for target in targets]
        rows = ['__DATA_CONST __const 0x%x rebase 0x%x' % (start+i*8, target)
                for i, target in enumerate(targets)]
        fixups = '\n'.join(rows); chains = 'pointer_format: 6 (DYLD_CHAINED_PTR_64_OFFSET)'
        result = collector.verify_factory_table(words, fixups, chains, label)
        self.assertEqual(result['rebases'], 11)
        self.assertEqual(result['file_targets'][5], '0x7b1c')
        for i in range(11):
            for mask in (1, 1 << 44, 1 << 63):
                bad = list(words); bad[i] ^= mask
                with self.subTest(index=i, mask=mask), self.assertRaises(ValueError):
                    collector.verify_factory_table(bad, fixups, chains, label)
        for bad in (fixups+'\n'+rows[0], '\n'.join(rows[1:]), fixups.replace('rebase', 'bind')):
            with self.assertRaises(ValueError):
                collector.verify_factory_table(words, bad, chains, label)
        for bad_words, bad_chains, bad_label in [(words[:-1], chains, label),
                (words, chains.replace('6 (', '2 ('), label), (words, chains, 'unknown')]:
            with self.assertRaises(ValueError):
                collector.verify_factory_table(bad_words, fixups, bad_chains, bad_label)

    def test_factory_catalog_keeps_metadata_holder_distinct_and_excludes_scan(self):
        names = ['RegisterPluginModuleFactory', 'GetKnownPluginsHolder',
                 'KnownPluginsHolder', 'AELibraryVideoFilterFactoryC1Ev',
                 'AELibraryVideoFilterFactoryCreateClassRefInternal',
                 'AELibraryVideoFilterFactoryCreateUnknown']
        chosen = collector.select_symbols('\n'.join('external '+n for n in names)+
                                          '\nexternal PLUG_Search\n', 'factory-identity')
        for name in names:
            self.assertIn(name, chosen)
        self.assertNotIn('PLUG_Search', chosen)

    def test_loader_dispatch_scope_requires_complete_fixed_bodies(self):
        windows = collector.review_windows('loader-dispatch')
        self.assertEqual(len(windows), 23)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 11754)
        self.assertEqual({image for _, image, *_ in windows}, {'PluginSupport'})
        self.assertEqual({label for label, *_ in windows}, set(collector.LOADER_DISPATCH_ANCHORS))
        self.assertIn(('dispatch-create-plugin', 'PluginSupport', 0x156f0, 0x15a54), windows)
        self.assertIn(('dispatch-add-7', 'PluginSupport', 0x128a4, 0x12cf8), windows)
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')
        self.assertNotIn('loader-dispatch', collector.DATA_WINDOWS)
        for prefix, first, last, count in [('dispatch-list-', 0x7ee8, 0xa6d0, 3),
                                          ('dispatch-add-', 0xc8a4, 0x12cf8, 7)]:
            parts = [(start, end) for label, _, start, end in windows if label.startswith(prefix)]
            self.assertEqual(len(parts), count)
            self.assertEqual((parts[0][0], parts[-1][1]), (first, last))
            self.assertTrue(all(a[1] == b[0] for a, b in zip(parts, parts[1:])))

    def test_loader_dispatch_refuses_changed_admission_failure_and_ownership(self):
        # Owned synthetic parser refusal controls, not Adobe runtime evidence.
        for label, _, start, end in collector.review_windows('loader-dispatch'):
            anchors = collector.LOADER_DISPATCH_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertEqual(collector.verify_loader_dispatch(text, label, start, end)['claim'],
                             'file-only-loader-dispatch-not-safe-late-registration')
            for address, (op, args) in anchors.items():
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address), wrong=wrong):
                        with self.assertRaisesRegex(ValueError, 'structural'):
                            collector.verify_loader_dispatch(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1])]:
                with self.assertRaisesRegex(ValueError, 'bounds'):
                    collector.verify_loader_dispatch(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'undecoded'):
                collector.verify_loader_dispatch(text.replace(': ', ': .long ', 1), label, start, end)
            for wrong_label, wrong_end in [('unknown', end), (label, end+4)]:
                with self.assertRaisesRegex(ValueError, 'unreviewed'):
                    collector.verify_loader_dispatch(text, wrong_label, start, wrong_end)

    def test_loader_dispatch_catalog_separates_list_from_effect_publication(self):
        names = ['__ZN2ML11LoadPluginsE', '__ZN2ML12_GLOBAL__N_114LoadPluginListE',
                 '__ZN2ML12_GLOBAL__N_19AddPluginE', '__ZN2ML12_GLOBAL__N_112CreatePluginE',
                 '__ZN2ML13PluginSupport28FindPluginFactoriesForModuleE',
                 '__ZN2ML13PluginSupport31GetFactoryListForModuleNFiltersE',
                 '__ZN2ML16MetaPluginLoader10LoadPluginE']
        chosen = collector.select_symbols('\n'.join('external '+n for n in names)+
                                          '\nexternal PLUG_Search\n', 'loader-dispatch')
        for name in names:
            self.assertIn(name, chosen)
        self.assertNotIn('PLUG_Search', chosen)

    def test_module_admission_scope_requires_complete_fixed_bodies(self):
        windows = collector.review_windows('module-admission')
        self.assertEqual(len(windows), 12)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 3446)
        self.assertEqual({image for _, image, *_ in windows}, {'MEE', 'PluginSupport'})
        self.assertEqual({label for label, *_ in windows}, set(collector.ADMISSION_ANCHORS))
        self.assertIn(('admit-init', 'MEE', 0x408c, 0x45ac), windows)
        self.assertIn(('admit-impl-b', 'MEE', 0x8dc8, 0x8dfc), windows)
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')
        self.assertNotIn('module-admission', collector.DATA_WINDOWS)

    def test_module_admission_refuses_changed_admission_failure_and_ownership(self):
        # Owned synthetic parser refusal controls, not Adobe runtime evidence.
        for label, _, start, end in collector.review_windows('module-admission'):
            anchors = collector.ADMISSION_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            self.assertEqual(collector.verify_admission(text, label, start, end)['claim'],
                             'file-only-module-admission-not-late-host-transaction')
            for address, (op, args) in anchors.items():
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address), wrong=wrong):
                        with self.assertRaisesRegex(ValueError, 'structural'):
                            collector.verify_admission(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1])]:
                with self.assertRaisesRegex(ValueError, 'bounds'):
                    collector.verify_admission(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'undecoded'):
                collector.verify_admission(text.replace(': ', ': .long ', 1), label, start, end)
            for wrong_label, wrong_end in [('unknown', end), (label, end+4)]:
                with self.assertRaisesRegex(ValueError, 'unreviewed'):
                    collector.verify_admission(text, wrong_label, start, wrong_end)

    def test_module_admission_catalog_separates_list_from_effect_publication(self):
        names = ['__ZN2ML11LoadPluginsE', '__ZN2ML27AELibraryVideoFilterFactory6CreateE',
                 '__ZN2ML27AELibraryVideoFilterFactory17CreateUnknownImplE',
                 '__ZN2ML27AELibraryVideoFilterFactory10GetModulesE',
                 '__ZN2ML32AELibraryPluginVideoFilterModule4InitE',
                 '__ZN2ML20IPluginModuleFactory12SetdownAsyncEv']
        chosen = collector.select_symbols('\n'.join('external '+n for n in names)+
                                          '\nexternal PLUG_Search\n', 'module-admission')
        for name in names:
            self.assertIn(name, chosen)
        self.assertNotIn('PLUG_Search', chosen)

    def test_routine_handoff_scope_pins_startup_handoff_and_complete_windows(self):
        windows = collector.review_windows('routine-handoff')
        self.assertEqual(len(windows), 17)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 4707)
        self.assertEqual({image for _, image, *_ in windows}, {'aelib', 'MEE', 'PluginSupport', 'FLT', 'PLUG'})
        self.assertEqual({label for label, *_ in windows}, set(collector.HANDOFF_ANCHORS))
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')
        self.assertNotIn('routine-handoff', collector.DATA_WINDOWS)

    def test_routine_handoff_refuses_changed_cache_status_transfer_and_cleanup(self):
        # Owned synthetic parser controls. Cannot establish Adobe execution semantics.
        for label, _, start, end in collector.review_windows('routine-handoff'):
            anchors = collector.HANDOFF_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_handoff(text, label, start, end)
            self.assertEqual(result['claim'], 'file-only-startup-handoff-not-safe-late-registration')
            for address, (op, args) in anchors.items():
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address), wrong=wrong):
                        with self.assertRaisesRegex(ValueError, 'structural'):
                            collector.verify_handoff(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1])]:
                with self.assertRaisesRegex(ValueError, 'bounds'):
                    collector.verify_handoff(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'undecoded'):
                collector.verify_handoff(text.replace(': ', ': .long ', 1), label, start, end)
            for wrong_label, wrong_end in [('unknown', end), (label, end+4)]:
                with self.assertRaisesRegex(ValueError, 'unreviewed'):
                    collector.verify_handoff(text, wrong_label, start, wrong_end)

    def test_routine_handoff_catalog_keeps_callback_handoff_not_global_search(self):
        names = ['__Z17FLT_SetupAEPluginN7dvacore',
                 '__Z24MEE_GetAELibPluginSetterv',
                 '__ZN2ML26AELibraryVideoFilterModule11SetupFilterE',
                 '__ZN2ML13PluginSupport13LoadAEPluginsEb',
                 '__ZN10FLT_FCSpec15SetRoutineDescHE',
                 '__Z18FLTp_DisposeFCSpecN5boost',
                 '__Z24PLUGp_DisposeRoutineDescRN5boost',
                 '__ZN5aelib12InitIteratorppEv']
        chosen = collector.select_symbols('\n'.join('external '+n for n in names)+
                                          '\nexternal PLUG_Search\n', 'routine-handoff')
        for name in names:
            self.assertIn(name, chosen)
        self.assertNotIn('PLUG_Search', chosen)

    def test_publication_owner_scope_pins_both_files_and_complete_windows(self):
        windows = collector.review_windows('publication-owner')
        self.assertEqual(len(windows), 12)
        self.assertEqual(sum((end-start)//4 for _, _, start, end in windows), 2403)
        self.assertEqual({image for _, image, *_ in windows}, {'PLUG', 'PluginSupport'})
        self.assertEqual({label for label, *_ in windows}, set(collector.OWNER_ANCHORS))
        for _, image, start, end in windows:
            script = collector.lldb_script(collector.INPUTS[image][0], start, end)
            self.assertIn('target create --no-dependents --arch arm64', script)
            self.assertNotRegex(script, r'process|expression|call ')
        self.assertNotIn('publication-owner', collector.DATA_WINDOWS)

    def test_publication_owner_refuses_wrong_owner_lock_release_and_completion(self):
        # Owned synthetic parser controls. Cannot establish Adobe execution semantics.
        for label, _, start, end in collector.review_windows('publication-owner'):
            anchors = collector.OWNER_ANCHORS[label]
            def transcript(overrides):
                return ''.join('owned[0x%x] <+%d>: %s %s\n' %
                    (a, a-start, *overrides.get(a, anchors.get(a, ('nop', ''))))
                    for a in range(start, end, 4))
            text = transcript({})
            result = collector.verify_owner(text, label, start, end)
            self.assertEqual(result['claim'], 'file-only-routine-owner-not-effect-publication-lease')
            for address, (op, args) in anchors.items():
                for wrong in [('nop', ''), (op, args+'x0')]:
                    with self.subTest(label=label, address=hex(address), wrong=wrong):
                        with self.assertRaisesRegex(ValueError, 'structural'):
                            collector.verify_owner(transcript({address: wrong}), label, start, end)
            for bad in [text+text.splitlines()[0]+'\n', '\n'.join(text.splitlines()[:-1])]:
                with self.assertRaisesRegex(ValueError, 'bounds'):
                    collector.verify_owner(bad, label, start, end)
            with self.assertRaisesRegex(ValueError, 'undecoded'):
                collector.verify_owner(text.replace(': ', ': .long ', 1), label, start, end)
            for wrong_label, wrong_end in [('unknown', end), (label, end+4)]:
                with self.assertRaisesRegex(ValueError, 'unreviewed'):
                    collector.verify_owner(text, wrong_label, start, wrong_end)

    def test_publication_owner_catalog_keeps_private_overloads_not_global_search(self):
        names = ['PLUG_RegisterRoutine', 'PLUG_RegisterRoutineMinimal', 'PLUG_UnregisterRoutine',
                 'PLUG_RoutineDescPrivC2', 'PLUGp_NewRoutineDesc', 'PLUGp_GetPiPL',
                 'PluginImplInternalLoadPiPLs', 'PluginImplLoadPiPLs',
                 'PiPLPopulateFromPluginData', 'PiPLCreateClassRef']
        chosen = collector.select_symbols('\n'.join('external '+n for n in names)+
                                          '\nexternal PLUG_Search\n', 'publication-owner')
        for name in names:
            self.assertIn(name, chosen)
        self.assertNotIn('PLUG_Search', chosen)

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
