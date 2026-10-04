"""Public startup protocol/pixel refusals; synthetic records are not AE evidence."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_live', ROOT / 'experiments/startup_calibration/run.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class StartupLiveTests(unittest.TestCase):
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

    def test_stale_wrong_process_or_unreleased_cleanup_refuses(self):
        live.cleanup_proof(self.proof, self.record, self.process, 0.1, self.result)
        for age in (-1, 2.01):
            with self.assertRaises(ValueError): live.cleanup_proof(self.proof, self.record, self.process, age, self.result)
        with self.assertRaises(ValueError):
            live.cleanup_proof(self.proof.replace(b'pid=123', b'pid=999'), self.record, self.process, 0, self.result)
        with self.assertRaises(ValueError):
            live.cleanup_proof(self.proof, self.record, self.process, 0, self.result.replace(b'cleanup=PASS', b'cleanup=FAIL'))

    def test_native_refusal_precedes_nonexistent_frame_read(self):
        refused = ('AEHL-CAL-RESULT-2\nbuild=' + self.record['build_id'] +
                   '\nstatus=REFUSED\nstage=project-guard\ncleanup=PASS\nrender=UNKNOWN\n').encode()
        with self.assertRaisesRegex(ValueError, 'status=REFUSED; stage=project-guard'):
            live.native_complete(self.record, refused)

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
