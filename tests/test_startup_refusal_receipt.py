"""Actual launch supervisor on owned files; SDK/debugger boundaries are fake."""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/startup_trace'))
import launch

spec = importlib.util.spec_from_file_location('refusal_sdk_verifier', ROOT / 'experiments/startup_calibration/run.py')
native_verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native_verifier)


class RefusalReceiptTests(unittest.TestCase):
    def test_binding_predicate_survives_supervisor_without_samples(self):
        for stage in ('resident-snapshot-first', 'resident-file-open', 'resident-image-parse',
                      'resident-header-mismatch', 'resident-text-mismatch', 'resident-snapshot-final-stability'):
            with self.subTest(stage=stage):
                raw = ('AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=' + stage +
                       '\ncleanup=PASS\nrender=UNKNOWN\n').encode('ascii')
                receipt, reads, verifier = self.run_supervisor(raw)
                self.assertEqual(receipt['stage'], stage)
                self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_bounded_own_code_difference_survives_actual_supervisor(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=resident-text-mismatch\n'
               b'cleanup=PASS\nmismatch_relative_offset=6\nmismatch_file_offset=4102\n'
               b'mismatch_expected_word=67305985\nmismatch_actual_word=67699201\n')
        receipt, reads, verifier = self.run_supervisor(raw)
        self.assertEqual(receipt['own_text_difference'], {'relative_offset':6, 'file_offset':4102,
                         'expected_word':67305985, 'actual_word':67699201})
        self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_partial_out_of_range_and_wrong_stage_difference_are_refused(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=resident-text-mismatch\n'
               b'cleanup=PASS\nmismatch_relative_offset=6\nmismatch_file_offset=4102\n'
               b'mismatch_expected_word=67305985\nmismatch_actual_word=67699201\n')
        for old,new in [(b'resident-text-mismatch',b'resident-text-read'),
                        (b'mismatch_relative_offset=6',b'mismatch_relative_offset=-1'),
                        (b'mismatch_relative_offset=6',b'mismatch_relative_offset=67108864'),
                        (b'mismatch_file_offset=4102',b'mismatch_file_offset=4103'),
                        (b'mismatch_file_offset=4102',b'mismatch_file_offset=4'),
                        (b'mismatch_expected_word=67305985',b'mismatch_expected_word=4294967296'),
                        (b'mismatch_actual_word=67699201',b'mismatch_actual_word=67305985'),
                        (b'mismatch_actual_word=67699201',b'mismatch_actual_word=67699202'),
                        (b'mismatch_actual_word=67699201\n',b''),
                        (b'mismatch_actual_word=67699201',b'mismatch_actual_word=private-bytes'),
                        (b'mismatch_actual_word=67699201',b'mismatch_actual_word=67699201\nmismatch_extra=1')]:
            with self.subTest(new=new):
                receipt, reads, verifier = self.run_supervisor(raw.replace(old,new))
                self.assertEqual(receipt['status'],'FAIL_OR_UNKNOWN')
                self.assertNotIn('own_text_difference',receipt)
                self.assertEqual(reads,['result']);verifier.assert_not_called()

    def test_actual_supervisor_retains_sleep_timeline_without_changing_refusal(self):
        raw=b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=request-deadline\ncleanup=PASS\n'
        receipt,reads,verifier,timing=self.run_supervisor(raw,timing_mode='sleep')
        self.assertEqual(receipt['stage'],'request-deadline');verifier.assert_not_called()
        self.assertEqual(timing['status'],'OBSERVED')
        self.assertTrue(timing['delivery']['suspension_observed'])
        self.assertEqual(timing['deadline_check']['deadline_window'],'EXPIRED')
        self.assertNotIn('names-0',reads)

    def test_foreign_timing_stays_unknown_without_losing_actual_refusal(self):
        raw=b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=request-deadline\ncleanup=PASS\n'
        receipt,reads,verifier,timing=self.run_supervisor(raw,timing_mode='foreign')
        self.assertEqual(receipt['stage'],'request-deadline');verifier.assert_not_called()
        self.assertEqual(timing['status'],'UNKNOWN');self.assertNotIn('names-0',reads)

    def run_supervisor(self, raw, samples=None, key=42, verified_key=42, timing_mode=None):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder).resolve()
            control = base / 'control'; control.mkdir(mode=0o700)
            plugins = base / 'plugins'; plugins.mkdir()
            record = {'trace_identity': True, 'build_id': 'owned-build',
                      'source': {'commit': 'a' * 40}, 'config': {'calibration_control': str(control)},
                      'bundles': [{'bundle': name, 'files': {}} for name in ('marker.plugin', 'observer.plugin')]}
            for item in record['bundles']:
                (base / item['bundle']).mkdir()
            (control / 'result').write_bytes(raw)
            for i, sample in enumerate(samples or []):
                (control / ('names-' + str(i))).write_bytes(sample)
            reads = []
            def read(path, limit):
                reads.append(path.name)
                data = path.read_bytes()
                self.assertLessEqual(len(data), limit)
                return data
            common = SimpleNamespace(bundle_hashes=lambda _: {}, read=read)
            verifier = Mock(return_value={'installed_key': verified_key})
            native = SimpleNamespace(prepare=lambda *_: (record, base, plugins / 'own-pair'),
                PLUGIN_ROOT=plugins, common=common, processes=lambda: [],
                fields=native_verifier.fields, verify_observation=verifier, birth=lambda _:99)
            published={'status':'OBSERVED','pid':123,'birth':99,'build_id':'owned-build','deadline':1110,
                'sample':dict(zip(launch.timeline.FIELDS,(1000000,1000,1000000000,2000000000,1,1)))}
            def drive(*_):
                trace = base / 'trace'; trace.mkdir()
                (trace / 'publication-intent.json').write_text(json.dumps({'monotonic_deadline': time.monotonic() + 1}))
                if timing_mode:
                    (trace/'publication-timing.json').write_text(json.dumps(published))
                    for phase,leaf in [(0,'request-received'),(2,'request-deadline-check')]:
                        stamp=dict(zip(launch.timeline.FIELDS,(1180000,3000,3000000000,182000000000,1,1)))
                        data='AEHL-CAL-TIMING-1\nbuild=owned-build\npid='+('456' if timing_mode=='foreign' else '123')+'\nbirth=99\nphase='+str(phase)+'\ndeadline='+('0' if phase==0 else '1110')+'\n'
                        (control/leaf).write_text(data+''.join(k+'='+str(v)+'\n' for k,v in stamp.items()))
                return {'status': 'INCOMPLETE', 'publication': 'SENT_ONCE', 'pid': 123, 'key': key,
                        'owned_process':{'pid':123}}
            with contextlib.ExitStack() as stack:
                for name, value in [('load_native', lambda: native), ('native_profile', lambda *_: {'kind': 'own-control'}),
                                    ('transport_admission', lambda *_: None), ('validate', lambda r: r),
                                    ('read_json', lambda path,*_: published if Path(path).name=='publication-timing.json' else {}), ('drive', drive)]:
                    stack.enter_context(patch.object(launch, name, value))
                stack.enter_context(patch.object(launch.subprocess, 'run', return_value=SimpleNamespace(returncode=0)))
                launch.execute(base / 'manifest.json', 'digest', base / 'transport.json', 'transport-digest')
            output=json.loads((base / 'trace/sdk-receipt.json').read_text()), reads, verifier
            return (*output,json.loads((base/'trace/request-timeline.json').read_text())) if timing_mode else output

    def test_refused_original_response_precedes_absent_samples(self):
        raw = b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=idle-registration\ncleanup=PASS\nrender=UNKNOWN\n'
        receipt, reads, verifier = self.run_supervisor(raw)
        self.assertEqual(receipt['status'], 'REFUSED')
        self.assertEqual(receipt['stage'], 'idle-registration')
        self.assertEqual(receipt['cleanup'], 'PASS')
        self.assertEqual(reads, ['result'])
        verifier.assert_not_called()

    def test_suite_host_error_is_preserved_without_samples_or_raw_errors(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=sdk-suite-acquire\n'
               b'cleanup=PASS\nrender=UNKNOWN\nsuite=AEGP Color Settings Suite\nsuite_version=7\n'
               b'host_error=-123\nreason=do-not-copy-private-error\n')
        receipt, reads, verifier = self.run_supervisor(raw)
        self.assertEqual(receipt['host_error'], -123)
        self.assertEqual(receipt['suite_version'], 7)
        self.assertEqual(receipt['suite'], 'AEGP Color Settings Suite')
        self.assertNotIn('do-not-copy-private-error', json.dumps(receipt))
        self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_partial_failure_stays_partial_without_reading_samples(self):
        raw = b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=PARTIAL_UNKNOWN\nstage=backend-prepare\ncleanup=FAIL\n'
        receipt, reads, verifier = self.run_supervisor(raw)
        self.assertEqual(receipt['status'], 'PARTIAL_UNKNOWN')
        self.assertEqual(receipt['cleanup'], 'FAIL')
        self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_foreign_malformed_or_mutating_header_never_reads_samples(self):
        raw = b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=request-read\ncleanup=PASS\n'
        mutations = [(b'build=owned-build', b'build=foreign'), (b'stage=request-read', b'stage=/private/path'),
                     (b'cleanup=PASS', b'cleanup=unsafe'), (b'status=REFUSED', b'status=UNKNOWN'),
                     (b'stage=request-read', b'stage=request-read\nstage=another')]
        for old, new in mutations:
            with self.subTest(new=new):
                receipt, reads, verifier = self.run_supervisor(raw.replace(old,new))
                self.assertEqual(receipt['status'], 'FAIL_OR_UNKNOWN')
                self.assertEqual(reads, ['result']); verifier.assert_not_called()
        mutating = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=LISTED_OBSERVED\nstage=registry-observation\n'
                    b'cleanup=PASS\ncleanup_safe=YES\nrender=PASS\napply=NOT_RUN\n')
        receipt, reads, verifier = self.run_supervisor(mutating)
        self.assertEqual(receipt['status'], 'FAIL_OR_UNKNOWN')
        self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_invalid_optional_diagnostics_are_not_published(self):
        prefix = b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=REFUSED\nstage=sdk-suite-acquire\ncleanup=PASS\n'
        for suffix in (b'host_error=2147483648\n',b'host_error=private-error\n',
                       b'suite=/private/path\nsuite_version=7\n',b'suite=AEGP Effect Suite\nsuite_version=-1\n'):
            with self.subTest(suffix=suffix):
                receipt, reads, verifier = self.run_supervisor(prefix+suffix)
                self.assertEqual(receipt['status'], 'FAIL_OR_UNKNOWN')
                self.assertEqual(reads, ['result']); verifier.assert_not_called()

    def test_success_keeps_all_three_samples_and_key_comparison(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=LISTED_OBSERVED\nstage=registry-observation\n'
               b'cleanup=PASS\ncleanup_safe=YES\nrender=NOT_RUN\napply=NOT_RUN\n')
        receipt, reads, verifier = self.run_supervisor(raw,[b'own-0',b'own-1',b'own-2'])
        self.assertEqual(receipt['status'], 'PASS');self.assertEqual(receipt['installed_key'],42)
        self.assertEqual(reads, ['result','names-0','names-1','names-2'])
        verifier.assert_called_once()

    def test_success_without_samples_remains_incomplete(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=LISTED_OBSERVED\nstage=registry-observation\n'
               b'cleanup=PASS\ncleanup_safe=YES\nrender=NOT_RUN\napply=NOT_RUN\n')
        receipt, reads, verifier = self.run_supervisor(raw)
        self.assertEqual(receipt['status'], 'FAIL_OR_UNKNOWN')
        self.assertEqual(reads, ['result','names-0']);verifier.assert_not_called()

    def test_success_with_different_collector_key_is_refused(self):
        raw = (b'AEHL-CAL-RESULT-2\nbuild=owned-build\nstatus=LISTED_OBSERVED\nstage=registry-observation\n'
               b'cleanup=PASS\ncleanup_safe=YES\nrender=NOT_RUN\napply=NOT_RUN\n')
        receipt, reads, verifier = self.run_supervisor(raw, [b'own-0', b'own-1', b'own-2'], key=43)
        self.assertEqual(receipt['status'], 'FAIL_OR_UNKNOWN')
        self.assertEqual(reads, ['result', 'names-0', 'names-1', 'names-2'])
        verifier.assert_called_once()


if __name__ == '__main__':
    unittest.main()
