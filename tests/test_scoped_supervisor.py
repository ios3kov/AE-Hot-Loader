import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


spec = importlib.util.spec_from_file_location('supervisor', Path(__file__).resolve().parents[1] /
                                           'experiments/ordinary_discovery/run_scoped_discovery.py')
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)


class ScopedSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.evidence = self.base / 'evidence'
        self.evidence.mkdir(mode=0o700)
        self.observed = {'pid': 42, 'start': 'test start', 'executable': '/owned/test-host'}
        self.record = {'build_id': 'scoped-test', 'source_commit': 'test-source',
                       'scan_root': '/owned/scan-root', 'match': 'AEHL.Embedded.test'}
        self.request = b'test-request\n'

    def native_pass(self):
        for name, text in {
            'claim.txt': self.request.decode(),
            'call-started.txt': 'root=/owned/scan-root\npid=42\n',
            'loader-result.txt': '1\n',
            'before.txt': 'AEHL-SNAPSHOT-1\n1\nADBE.Test\n',
            'after.txt': 'AEHL-SNAPSHOT-1\n1\nADBE.Test\nAEHL.Embedded.test\n',
            'result.txt': 'status=PASS\nscope=registration-only\nbuild_id=scoped-test\nsource=test-source\npid=42\n',
        }.items():
            (self.evidence / name).write_text(text)

    def test_result_requires_independent_delta_and_pid(self):
        self.native_pass()
        supervisor.verify_result(self.record, self.evidence, 42, self.request)
        with self.assertRaisesRegex(ValueError, 'native gate did not pass'):
            supervisor.verify_result(self.record, self.evidence, 43, self.request)
        (self.evidence / 'after.txt').write_text('AEHL-SNAPSHOT-1\n1\nADBE.Test\n')
        with self.assertRaisesRegex(ValueError, 'registry/project'):
            supervisor.verify_result(self.record, self.evidence, 42, self.request)

    def test_wrong_process_blocks_before_ready_or_request(self):
        record = {**self.record, 'source_clean': True, 'kind': 'research-only-scoped-aegp',
                  'evidence': str(self.evidence), 'host_executable': str(self.base / 'host/After Effects')}
        manifest = self.base / 'manifest.json'
        raw = json.dumps(record).encode()
        manifest.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'PID is not the pinned test host'):
            supervisor.prepare(manifest, hashlib.sha256(raw).hexdigest(), 42,
                               identity_fn=lambda pid: self.observed)
        self.assertEqual(list(self.evidence.iterdir()), [])

    def test_user_host_needs_explicit_matching_authorization(self):
        record = {**self.record, 'source_clean': True, 'kind': 'research-only-scoped-aegp',
                  'evidence': str(self.evidence), 'host_executable': '/authorized/After Effects',
                  'host_mode': 'authorized-user-host', 'authorized_bundle': '/authorized/Test.plugin'}
        manifest = self.base / 'manifest.json'
        raw = json.dumps(record).encode()
        manifest.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, 'explicit authorized'):
            supervisor.prepare(manifest, digest, 42)
        with self.assertRaisesRegex(ValueError, 'paths differ'):
            supervisor.prepare(manifest, digest, 42, authorized_host=Path('/wrong'),
                               authorized_bundle=Path('/authorized/Test.plugin'))
        with self.assertRaisesRegex(ValueError, 'PID is not'):
            supervisor.prepare(manifest, digest, 42, identity_fn=lambda pid: self.observed,
                               authorized_host=Path('/authorized/After Effects'),
                               authorized_bundle=Path('/authorized/Test.plugin'))
        self.assertEqual(list(self.evidence.iterdir()), [])

    def test_authorized_bundle_identity_and_hashes(self):
        bundle = self.base / 'installed/Test.plugin'
        image = bundle / 'Contents/MacOS/Test'
        image.parent.mkdir(parents=True)
        image.write_bytes(b'identified test binary')
        host = self.base / 'ordinary/After Effects'
        record = {**self.record, 'source_clean': True, 'target': 'aarch64-apple-darwin',
                  'kind': 'research-only-scoped-aegp', 'fixture_build_id': 'fixture',
                  'fixture_manifest_sha256': 'fixture-hash', 'evidence': str(self.evidence),
                  'host_executable': str(host), 'host_mode': 'authorized-user-host',
                  'authorized_bundle': str(bundle),
                  'activation_env': {'AEHL_SCOPED_GATE_TOKEN': 'test-token'},
                  'files': {'Contents/MacOS/Test': hashlib.sha256(image.read_bytes()).hexdigest()}}
        identity = {k: record[k] for k in ('build_id', 'source_commit', 'source_clean', 'target',
                    'kind', 'fixture_build_id', 'fixture_manifest_sha256')}
        (self.evidence / 'ready.txt').write_text(json.dumps(identity) + '\npid=42\nimage=' + str(image) + '\n')
        raw = json.dumps(record).encode()
        manifest = self.base / 'manifest.json'
        manifest.write_bytes(raw)
        def prepare():
            return supervisor.prepare(manifest, hashlib.sha256(raw).hexdigest(), 42,
                identity_fn=lambda pid: {**self.observed, 'executable': str(host)},
                authorized_host=host, authorized_bundle=bundle)
        self.assertEqual(prepare()[0], record)
        self.assertFalse((self.evidence / 'request.txt').exists())
        image.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'file/hash mismatch'):
            prepare()

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS exclusive rename API')
    def test_atomic_request_never_replaces_existing_and_has_one_link(self):
        supervisor.publish(self.evidence, self.request)
        self.assertEqual(supervisor.read(self.evidence / 'request.txt'), self.request)
        with self.assertRaises(OSError):
            supervisor.publish(self.evidence, b'replacement')
        self.assertEqual(supervisor.read(self.evidence / 'request.txt'), self.request)
        self.assertEqual(list(self.evidence.iterdir()), [self.evidence / 'request.txt'])

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS request publication')
    def test_timeout_preserves_request_and_prevents_replay(self):
        times = iter([0, 0, 2])
        result = supervisor.supervise(self.record, self.evidence, self.observed, self.request, 1,
                                     identity_fn=lambda pid: self.observed,
                                     clock=lambda: next(times), sleep=lambda duration: None)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('timeout', result['reason'])
        self.assertFalse(result['process_stopped'])
        self.assertEqual(supervisor.read(self.evidence / 'request.txt'), self.request)
        with self.assertRaises(FileExistsError):
            supervisor.supervise(self.record, self.evidence, self.observed, self.request, 1)

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS request publication')
    def test_process_exit_never_passes(self):
        calls = []
        def identity(pid):
            calls.append(pid)
            if len(calls) > 1:
                raise ValueError('test host is absent')
            return self.observed
        result = supervisor.supervise(self.record, self.evidence, self.observed, self.request, 1,
                                     identity_fn=identity)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['reason'], 'test host is absent')
        self.assertTrue(result['request_published'])

    @unittest.skipUnless(sys.platform == 'darwin', 'macOS request publication')
    def test_complete_result_passes_without_stopping_host(self):
        times = iter([0, 0, 0.1])
        result = supervisor.supervise(self.record, self.evidence, self.observed, self.request, 1,
                                     identity_fn=lambda pid: self.observed,
                                     clock=lambda: next(times), sleep=lambda duration: self.native_pass())
        self.assertEqual(result['status'], 'PASS')
        self.assertFalse(result['process_stopped'])
