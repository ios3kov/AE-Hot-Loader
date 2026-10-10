"""Public startup protocol/pixel refusals; synthetic records are not AE evidence."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_live', ROOT / 'experiments/startup_calibration/run.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class StartupLiveTests(unittest.TestCase):
    def test_resource_only_requires_r_listing_and_zero_exact_resident_metadata_witness(self):
        result, samples = self.route_observation()
        samples = [s.replace(b'exact=1',b'exact=0').replace(b'AEHL.M.fixture'.hex().encode(),
                   b'AEHL.R.fixture'.hex().encode()) for s in samples]
        self.record['resource_only_marker'] = True
        self.assertEqual(live.verify_observation(self.record, result, samples)['resource_key'], 42)
        witness = ('AEHL-CAL-MARKER-STARTUP-1\nbuild=' + self.record['build_id'] +
            '\nbinding=EXACT_OWN_RESIDENT_IMAGE\n' + ''.join(f'{key}=0\n' for key in
            ('registration_started','registration_completed','last_callback_result','callback_address',
             'registration_on_main','metadata_entry_present','context_ready','host_name_status','host_version_status')) +
            'host_name_hex=\nhost_version_hex=\n').encode()
        self.assertEqual(live.verify_resource_only_marker(self.record,witness)['registration'],'ZERO')
        for old, new in [(b'binding=EXACT_OWN_RESIDENT_IMAGE',b'binding=UNKNOWN'),
                         (b'build=',b'build=wrong'), (b'host_name_hex=',b'host_name_hex=41')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                live.verify_resource_only_marker(self.record,witness.replace(old,new))
        for key in ('registration_started','registration_completed','last_callback_result','callback_address',
                    'registration_on_main','metadata_entry_present','context_ready','host_name_status','host_version_status'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                live.verify_resource_only_marker(self.record,witness.replace((key+'=0').encode(),(key+'=1').encode()))
        result, samples = self.route_observation(43)
        self.record['resource_only_marker'] = True
        with self.assertRaisesRegex(ValueError,'resource-only'): live.verify_observation(self.record,result,samples)

    def test_resource_only_flag_requires_strict_boolean_and_explicit_contrast_before_host_checks(self):
        import hashlib
        run = 'a'*32
        record = {'schema':'AEHL-STARTUP-CALIBRATION-1','source':{'clean':True,'commit':'d'*40},
                  'observer_host_binding':'PROSPECTIVE_ONLY_NOT_AUTHORIZATION','install':'NOT RUN',
                  'AE_load':'NOT RUN','AE_render':'NOT RUN','late_registration':'NOT RUN','run_id':run,
                  'token':'c'*32,'build_id':'d'*40+':'+run,'match_name':live.identity.marker_match(run),
                  'seed':int(run[:6],16),'resource_only_marker':True,'registration_route_discriminator':False}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'manifest.json'
            for flag in (True,1,'yes'):
                record['resource_only_marker']=flag
                raw=json.dumps(record).encode();path.write_bytes(raw);path.chmod(0o600)
                with patch.object(live.common,'no_links') as check, self.assertRaisesRegex(ValueError,'resource-only'):
                    live.prepare(path,hashlib.sha256(raw).hexdigest())
                self.assertEqual(check.call_count,1)

    def test_compiled_resource_binary_comments_do_not_change_hex_payload(self):
        spec = importlib.util.spec_from_file_location('startup_build', ROOT / 'experiments/startup_calibration/build.py')
        builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
        dump = b'data \'PiPL\' (16000) {\n $"0080 FF00" /* \x80\xff */\n $"1234"\n};'
        self.assertEqual(builder.compiled_pipl(dump), b'\x00\x80\xff\x00\x12\x34')
        self.assertNotEqual(builder.compiled_pipl(dump.replace(b'1234', b'1235')), b'\x00\x80\xff\x00\x12\x34')
        self.assertEqual(builder.compiled_pipl(b'/* \x80 */'), b'')

    def test_compact_identity_preserves_96_bits_and_refuses_invalid_nonce(self):
        run = '9e09478c2faf48819b4d61f4e34a3103'
        match = live.identity.marker_match(run)
        self.assertEqual(len(match.encode('ascii')), 31)
        self.assertEqual(match, 'AEHL.M.' + run[:24])
        for offset in (0, 11, 23):
            other = run[:offset] + ('0' if run[offset] != '0' else '1') + run[offset+1:]
            self.assertNotEqual(match, live.identity.marker_match(other))
        for bad in (None, 32, '', 'a'*31, 'a'*33, 'A'*32, 'g'*32, 'é'*32):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                live.identity.marker_match(bad)

    def test_old_overlong_candidate_refuses_before_host_or_filesystem_checks(self):
        import hashlib, json
        run = 'a'*32
        record = {'schema': 'AEHL-STARTUP-CALIBRATION-1', 'source': {'clean': True, 'commit': 'b'*40},
                  'observer_host_binding': 'PROSPECTIVE_ONLY_NOT_AUTHORIZATION',
                  'install': 'NOT RUN', 'AE_load': 'NOT RUN', 'AE_render': 'NOT RUN',
                  'late_registration': 'NOT RUN', 'run_id': run, 'token': 'c'*32,
                  'build_id': 'b'*40+':'+run, 'match_name': 'AEHL.Marker.'+run,
                  'seed': int(run[:6], 16)}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder).resolve()/'manifest.json'; raw = json.dumps(record).encode(); path.write_bytes(raw); path.chmod(0o600)
            with self.assertRaisesRegex(ValueError, 'candidate identity differs'):
                live.prepare(path, hashlib.sha256(raw).hexdigest())

    def setUp(self):
        self.record = {'token': 'a' * 32, 'build_id': 'b' * 40 + ':' + 'c' * 32,
                       'seed': 0x345678, 'bundles': [{}, {'binary_sha256': 'd' * 64}]}
        self.process = {'pid': 123, 'start': '456.000007'}
        self.result = ('AEHL-CAL-RESULT-2\nbuild=' + self.record['build_id'] +
            '\nstatus=LISTED_APPLIED_FRAME_CAPTURED\nkey=42\ncleanup=PASS\ncleanup_safe=YES\nrender=CAPTURED_PIXEL_CHECK_PENDING\n').encode()
        self.metadata = ('AEHL-CAL-FRAME-1\nbuild=' + self.record['build_id'] +
            '\nwidth=64\nheight=48\norder=ARGB8\nstride=256\nworld_type=8\ntime=1/24\nworking_space=NONE\n'
            'source_rowbytes=272\ncounter_before=0\ncounter_after=1\n').encode()
        self.pixels = live.oracle.expected(64, 48, self.record['seed'])
        self.proof = ('AEHL-CAL-CLEANUP-1\nbuild=' + self.record['build_id'] +
            '\npid=123\nbirth=456000007\nAEHL-CAL-OWNED-1\n9\n').encode()

    def test_exact_transport_pixel_assertions_are_not_host_proof(self):
        result = live.verify_capture(self.record, self.result, self.metadata, self.pixels)
        self.assertEqual(result['installed_key'], 42)
        self.assertEqual(result['pixels']['pixel_status'], 'PASS')
        self.assertIn('additionally requires owned launch', result['scope'])

    def test_wrong_build_status_key_cleanup_refuses(self):
        for old, new in [(b'build=b', b'build=a'), (b'LISTED_APPLIED_FRAME_CAPTURED', b'PARTIAL_UNKNOWN'),
                         (b'key=42', b'key=0'), (b'cleanup=PASS', b'cleanup=FAIL'),
                         (b'cleanup_safe=YES', b'cleanup_safe=NO')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                live.verify_capture(self.record, self.result.replace(old, new), self.metadata, self.pixels)

    def test_wrong_route_depth_shape_counter_and_pixels_refuse(self):
        for old, new in [(b'ARGB8', b'RGBA8'), (b'width=64', b'width=63'), (b'world_type=8', b'world_type=16'),
                         (b'time=1/24', b'time=0'), (b'working_space=NONE', b'working_space=sRGB'),
                         (b'counter_after=1', b'counter_after=0'), (b'source_rowbytes=272', b'source_rowbytes=255')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                live.verify_capture(self.record, self.result, self.metadata.replace(old, new), self.pixels)
        corrupted = bytearray(self.pixels); corrupted[-1] ^= 1
        for data in (bytes(corrupted), self.pixels[:-1], self.pixels + b'x'):
            with self.assertRaises(ValueError): live.verify_capture(self.record, self.result, self.metadata, data)

    def test_one_exact_ready_and_request_process_identity(self):
        ready = ('AEHL-CAL-READY-1\nbuild=' + self.record['build_id'] + '\npid=123\nbirth=456000007\n').encode()
        live.ready_identity(ready, self.record, self.process)
        for old, new in [(b'pid=123', b'pid=124'), (b'birth=456000007', b'birth=456000008')]:
            with self.assertRaises(ValueError): live.ready_identity(ready.replace(old, new), self.record, self.process)
        parts = live.request(self.record, self.process, 1000).decode().split()
        self.assertEqual(parts, ['AEHL-CAL-REQUEST-2', 'a'*32, '123', '456000007', '1000',
                                 'OWNED-STARTUP-APPLY-RENDER', 'd'*64])

    def observation(self):
        self.record.update(match_name='AEHL.M.fixture', config={'calibration_name': 'AEHL Fixture'})
        result = ('AEHL-CAL-RESULT-2\nbuild=' + self.record['build_id'] +
            '\nstatus=LISTED_OBSERVED\nstage=registry-observation\nkey=42\ncleanup=PASS\ncleanup_safe=YES\nrender=NOT_RUN\napply=NOT_RUN\n').encode()
        samples = [('AEHL-CAL-NAMES-1\nbuild=' + self.record['build_id'] +
            f'\nsample={i}\ncount=2\ntraversed=2\nexact=1\nrevision=9\ncomplete=YES\nstage=name-observation-complete\n'
            'own_observations=1\nown_0_key=42\nown_0_name_hex=' + b'AEHL Fixture'.hex() +
            '\nown_0_match_hex=' + b'AEHL.M.fixture'.hex() + '\n').encode() for i in range(3)]
        return result, samples

    def test_read_only_observation_accepts_three_consistent_own_samples(self):
        result, samples = self.observation()
        self.assertEqual(live.verify_observation(self.record, result, samples)['installed_key'], 42)
        self.assertIn('REGISTRY-OBSERVATION', live.request(self.record, self.process, 1000, observation_mode=True).decode())
        with self.assertRaises(ValueError): live.request(self.record, self.process, 1000, True, True)

    def route_observation(self, resource_key=None):
        result, samples = self.observation()
        self.record.update(registration_route_discriminator=True, resource_match_name='AEHL.R.fixture')
        if resource_key is not None:
            samples = [s.replace(b'own_observations=1', b'own_observations=2') +
                       (f'own_1_key={resource_key}\nown_1_name_hex=' + b'AEHL Fixture'.hex() +
                        '\nown_1_match_hex=' + b'AEHL.R.fixture'.hex() + '\n').encode() for s in samples]
        return result, samples

    def test_route_discriminator_names_are_bounded_and_default_is_unchanged(self):
        run = 'c'*32
        self.assertEqual(live.identity.resource_match(run), live.identity.marker_match(run))
        resource = live.identity.resource_match(run, True)
        self.assertEqual(resource, 'AEHL.R.' + run[:24])
        self.assertEqual(len(resource), 31)
        self.assertNotEqual(resource, live.identity.marker_match(run))
        for invalid in (1, 'true', None):
            with self.assertRaises(ValueError): live.identity.resource_match(run, invalid)

    def test_route_discriminator_classifies_complete_metadata_only_and_both(self):
        for key, expected in ((None, 'METADATA_NAME_LISTED_RESOURCE_NAME_ABSENT'), (43, 'BOTH_NAMES_LISTED')):
            result, samples = self.route_observation(key)
            answer = live.verify_observation(self.record, result, samples)
            self.assertEqual(answer['route_observation'], expected)
            self.assertEqual(answer['resource_key'], key)
            self.assertIn('NOT PROVED', answer['scope'])

    def test_route_discriminator_resource_only_requires_three_complete_consistent_samples(self):
        result, samples = self.route_observation()
        samples = [s.replace(b'exact=1', b'exact=0').replace(b'AEHL.M.fixture'.hex().encode(),
                   b'AEHL.R.fixture'.hex().encode()) for s in samples]
        answer = live.verify_observation(self.record, result, samples)
        self.assertEqual(answer['route_observation'], 'RESOURCE_NAME_LISTED_METADATA_NAME_ABSENT')
        self.assertIsNone(answer['metadata_key']); self.assertEqual(answer['resource_key'], 42)
        with self.assertRaises(ValueError): live.verify_observation(self.record, result, samples[:1])
        for old, new in ((b'exact=0', b'exact=1'), (b'own_0_key=42', b'own_0_key=43')):
            with self.assertRaises(ValueError):
                live.verify_observation(self.record, result, [*samples[:2],samples[2].replace(old,new)])
        self.record['registration_route_discriminator'] = False
        with self.assertRaises(ValueError): live.verify_observation(self.record, result, samples)

    def test_observation_native_refusal_is_reported_before_missing_sample_files(self):
        result, _ = self.observation()
        refused = result.replace(b'status=LISTED_OBSERVED', b'status=REFUSED').replace(
            b'stage=registry-observation', b'stage=registry-observation-own-marker')
        with self.assertRaisesRegex(ValueError, 'REFUSED; stage=registry-observation-own-marker'):
            live.observation_complete(self.record, refused)

    def test_route_discriminator_forbids_apply_and_queue_requests(self):
        self.route_observation()
        for queue in (False, True):
            with self.assertRaisesRegex(ValueError, 'read-only'):
                live.request(self.record, self.process, 1000, queue_mode=queue)
        self.assertIn(b'REGISTRY-OBSERVATION', live.request(self.record, self.process, 1000, observation_mode=True))

    def test_route_discriminator_rejects_mutating_mode_before_process_or_install(self):
        self.route_observation()
        with patch.object(live, 'prepare', return_value=(self.record, Path('/unused'), Path('/unused'))), \
             patch.object(live.platform, 'system', return_value='Darwin'), \
             patch.object(live.platform, 'machine', return_value='arm64'), \
             patch.object(live, 'processes') as processes:
            for queue in (False, True):
                with self.assertRaisesRegex(ValueError, 'read-only'):
                    live.run(Path('/unused'), 'unused', True, queue_mode=queue)
            processes.assert_not_called()

    def test_route_candidate_bad_resource_and_mixed_trace_refuse_before_host_checks(self):
        import hashlib
        run = 'a'*32
        record = {'schema': 'AEHL-STARTUP-CALIBRATION-1', 'source': {'clean': True, 'commit': 'b'*40},
                  'observer_host_binding': 'PROSPECTIVE_ONLY_NOT_AUTHORIZATION',
                  'install': 'NOT RUN', 'AE_load': 'NOT RUN', 'AE_render': 'NOT RUN', 'late_registration': 'NOT RUN',
                  'run_id': run, 'token': 'c'*32, 'build_id': 'b'*40+':'+run,
                  'match_name': live.identity.marker_match(run), 'seed': int(run[:6],16),
                  'registration_route_discriminator': True, 'resource_match_name': live.identity.resource_match(run,True),
                  'trace_identity': False}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder).resolve()/'manifest.json'
            for field, value, message in (('resource_match_name', record['match_name'], 'resource route'),
                                          ('trace_identity', True, 'mix debugger'),
                                          ('registration_route_discriminator', 1, 'resource route'),
                                          ('resource_pipl_identity', {}, 'compiled resource')):
                altered = dict(record); altered[field] = value
                raw = json.dumps(altered).encode(); path.write_bytes(raw); path.chmod(0o600)
                with patch.object(live.common, 'no_links') as host_check, self.assertRaisesRegex(ValueError,message):
                    live.prepare(path,hashlib.sha256(raw).hexdigest())
                # Reading the owned manifest checks its path first; no host or
                # installation-root validation is reached by these refusals.
                self.assertEqual(host_check.call_count, 1)
                self.assertEqual(host_check.call_args.args, (path,))

    def test_route_discriminator_rejects_resource_alias_wrong_name_and_changed_key(self):
        for key in (0, -1, 42, 2**31):
            result, samples = self.route_observation(key)
            with self.assertRaisesRegex(ValueError, 'resource|distinct'):
                live.verify_observation(self.record, result, samples)
        result, samples = self.route_observation(43)
        for old, new in ((b'own_1_key=43', b'own_1_key=44'),
                         (b'own_1_name_hex=', b'own_1_name_hex=ff')):
            with self.assertRaises((ValueError, UnicodeError)):
                live.verify_observation(self.record, result, [*samples[:2], samples[2].replace(old, new)])

    def test_route_discriminator_rejects_duplicate_and_incomplete_resource_evidence(self):
        result, samples = self.route_observation(43)
        duplicate = [s.replace(b'own_observations=2', b'own_observations=3') +
                     b'own_2_key=44\nown_2_name_hex=' + b'AEHL Fixture'.hex().encode() +
                     b'\nown_2_match_hex=' + b'AEHL.R.fixture'.hex().encode() + b'\n' for s in samples]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            live.verify_observation(self.record, result, duplicate)
        with self.assertRaises(ValueError):
            live.verify_observation(self.record, result, [s.replace(b'complete=YES', b'complete=NO') for s in samples])

    def test_observation_rejects_mutation_claim_missing_samples_and_wrong_scope(self):
        result, samples = self.observation()
        for old, new in [(b'apply=NOT_RUN', b'apply=PASS'), (b'cleanup=PASS', b'cleanup=FAIL'),
                         (b'status=LISTED_OBSERVED', b'status=LISTED_APPLIED_FRAME_CAPTURED'),
                         (b'key=42', b'key=0'), (b'build=b', b'build=a')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                live.verify_observation(self.record, result.replace(old, new), samples)
        with self.assertRaises(ValueError): live.verify_observation(self.record, result, samples[:2])

    def test_observation_rejects_key_count_revision_name_and_encoding_changes(self):
        result, samples = self.observation()
        for old, new in [(b'own_0_key=42', b'own_0_key=43'), (b'count=2', b'count=3'),
                         (b'revision=9', b'revision=10'), (b'exact=1', b'exact=0'),
                         (b'complete=YES', b'complete=NO'), (b'own_observations=1', b'own_observations=17'),
                         (b'own_0_name_hex=', b'own_0_name_hex=ff'), (b'own_0_match_hex=', b'own_0_match_hex=z')]:
            altered = [*samples[:2], samples[2].replace(old, new)]
            with self.subTest(new=new), self.assertRaises((ValueError, UnicodeError)):
                live.verify_observation(self.record, result, altered)

    def test_stale_wrong_process_or_unreleased_cleanup_refuses(self):
        live.cleanup_proof(self.proof, self.record, self.process, 0.1, self.result)
        for age in (-1, 2.01):
            with self.assertRaises(ValueError): live.cleanup_proof(self.proof, self.record, self.process, age, self.result)
        with self.assertRaises(ValueError):
            live.cleanup_proof(self.proof.replace(b'pid=123', b'pid=999'), self.record, self.process, 0, self.result)
        with self.assertRaises(ValueError):
            live.cleanup_proof(self.proof, self.record, self.process, 0, self.result.replace(b'cleanup=PASS', b'cleanup=FAIL'))

    def test_fresh_owned_proof_preserves_host_and_never_signals_or_waits(self):
        child = Mock(pid=123)
        child.poll.return_value = None
        with tempfile.TemporaryDirectory() as folder:
            control = Path(folder).resolve()
            live.write(control / 'cleanup-safe', self.proof)
            live.write(control / 'result', self.result)
            with patch.object(live.common, 'process_identity', return_value=self.process), \
                 patch.object(live, 'processes', return_value=[123]):
                status = live.preserve_owned_host(child, control, self.record, self.process)
                self.assertIn('MANUAL CLOSE REQUIRED', status)
                self.assertIn('no signal sent', status)
            with patch.object(live.common, 'process_identity', return_value=dict(self.process, pid=124)), \
                 patch.object(live, 'processes', return_value=[123]):
                with self.assertRaisesRegex(ValueError, 'process changed'):
                    live.preserve_owned_host(child, control, self.record, self.process)
            with patch.object(live.time, 'time', return_value=(control / 'cleanup-safe').stat().st_mtime + 3):
                with self.assertRaisesRegex(ValueError, 'stale'):
                    live.preserve_owned_host(child, control, self.record, self.process)
            (control / 'cleanup-safe').unlink()
            self.assertIn('host preserved', live.preserve_owned_host(child, control, self.record, self.process))
            child.poll.return_value = 0
            self.assertIn('normal exit not certified',
                          live.preserve_owned_host(child, control, self.record, self.process))
        child.terminate.assert_not_called()
        child.kill.assert_not_called()
        child.send_signal.assert_not_called()
        child.wait.assert_not_called()

    def test_native_refusal_precedes_nonexistent_frame_read(self):
        refused = ('AEHL-CAL-RESULT-2\nbuild=' + self.record['build_id'] +
                   '\nstatus=REFUSED\nstage=project-guard\ncleanup=PASS\nrender=UNKNOWN\n').encode()
        with self.assertRaisesRegex(ValueError, 'status=REFUSED; stage=project-guard'):
            live.native_complete(self.record, refused)

    def test_cleanup_proof_failure_still_records_other_plugins_without_host_signal(self):
        # Run the real supervisor on owned files and fake SDK/process boundaries.
        # A malformed proof must preserve the host and still compare other entries.
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder).resolve()
            control = base / 'control'; control.mkdir(mode=0o700)
            plugins = base / 'plugins'; plugins.mkdir()
            foreign = plugins / 'existing.plugin'; foreign.write_bytes(b'unchanged')
            install = plugins / 'unique-owned'
            record = dict(self.record, source={'commit': 'b' * 40})
            record['bundles'] = [{'bundle': name, 'files': {}, 'binary_sha256': 'd' * 64}
                                 for name in ('marker.plugin', 'observer.plugin')]
            for item in record['bundles']:
                (base / item['bundle']).mkdir()
            child = Mock(pid=123); child.poll.return_value = None
            process = dict(self.process, executable=str(live.HOST))
            started = False
            def launch(*args, **kwargs):
                nonlocal started
                started = True
                live.write(control / 'ready', ('AEHL-CAL-READY-1\nbuild=' + record['build_id'] +
                           '\npid=123\nbirth=456000007\n').encode())
                return child
            def publish(*args):
                live.write(control / 'result', self.result.replace(
                    b'LISTED_APPLIED_FRAME_CAPTURED', b'REFUSED'))
                live.write(control / 'cleanup-safe', b'wrong-proof\n')
            with patch.object(live, 'prepare', return_value=(record, base, install)), \
                 patch.object(live.platform, 'system', return_value='Darwin'), \
                 patch.object(live.platform, 'machine', return_value='arm64'), \
                 patch.object(live, 'PLUGIN_ROOT', plugins), \
                 patch.object(live, 'processes', side_effect=lambda: [123] if started else []), \
                 patch.object(live.common, 'process_identity', return_value=process), \
                 patch.object(live.common, 'sha_trusted_binary', return_value=live.HOST_SHA), \
                 patch.object(live.common, 'bundle_hashes', return_value={}), \
                 patch.object(live.subprocess, 'run'), \
                 patch.object(live.subprocess, 'Popen', side_effect=launch), \
                 patch.object(live, 'publish', side_effect=publish), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(live.run(base / 'manifest.json', '0' * 64, True), 1)
            report = json.loads((base / 'live/result.json').read_text())
            self.assertEqual(report.get('other_plugin_entries'), 'UNCHANGED')
            self.assertIn('BLOCKED_OR_UNKNOWN', report['cleanup'])
            self.assertEqual(json.loads((base / 'live/plugin-entry-baseline.json').read_text()).keys(),
                             {'existing.plugin'})
            self.assertEqual(foreign.read_bytes(), b'unchanged')
            self.assertTrue(install.is_dir())
            child.terminate.assert_not_called()
            child.kill.assert_not_called()
            child.wait.assert_not_called()

    def test_exclusive_journals_duplicates_and_missing_execution_authority(self):
        for data in (b'wrong\na=b\n', b'schema\na=b\na=c\n', b'schema\nbad\n'):
            with self.assertRaises(ValueError): live.fields(data, 'schema')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'record'; live.write(path, b'first')
            with self.assertRaises(FileExistsError): live.write(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')
        with self.assertRaisesRegex(ValueError, 'execution authority'):
            live.run(Path('does-not-exist'), '0'*64, False)


if __name__ == '__main__':
    unittest.main()
