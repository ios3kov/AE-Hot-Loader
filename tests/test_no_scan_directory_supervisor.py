"""External no-scan supervisor tests with owned files only; no AE process or Adobe libraries."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'experiments/ordinary_discovery/run_no_scan_directory_probe.py'
spec = importlib.util.spec_from_file_location('noscan_supervisor', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def field(name, value):
    raw = str(value).encode()
    return name.encode() + b'=' + str(len(raw)).encode() + b':' + raw + b'\n'


def journal_file(path, payload):
    data = mod.MAGIC + path.name.encode() + b'\n' + str(len(payload)).encode() + b'\n' + payload + b'\nEND-AEHL-RECORD\n'
    path.write_bytes(data); path.chmod(0o600)


class Fixture:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.base = self.root / 'noscan-build'; self.base.mkdir(mode=0o700)
        self.control = self.base / 'control'; self.journal = self.base / 'journal'; self.probe = self.base / 'probe-directory'
        for path in (self.control, self.journal, self.probe): path.mkdir(mode=0o700)
        self.host = self.root / 'After Effects'; self.host.write_bytes(b'host'); self.host.chmod(0o700)
        self.bundle = self.root / 'Installed.plugin'
        binary = self.bundle / 'Contents/MacOS/AEHLNoScan123456789abc'
        binary.parent.mkdir(parents=True); binary.write_bytes(b'candidate-binary'); binary.chmod(0o700)
        resource = self.bundle / 'Contents/Resources/Test.rsrc'; resource.parent.mkdir(parents=True); resource.write_bytes(b'resource')
        files = mod.bundle_hashes(self.bundle)
        self.record = {
            'build_id': 'noscan-123456789abc', 'run_id': 'directory-probe-' + '1' * 32,
            'source_commit': '2' * 40, 'source_clean': True, 'target': 'aarch64-apple-darwin',
            'kind': 'research-only-no-scan-directory-aegp', 'installation_performed': False,
            'ae_launch_performed': False, 'host_mode': 'authorized-user-host',
            'host_executable': str(self.host), 'authorized_bundle': str(self.bundle),
            'module_path': str(binary), 'candidate_bundle': str(self.root / 'Candidate.plugin'),
            'native_timeout_ms': 15000,
            'probe_directory': str(self.probe), 'control_directory': str(self.control),
            'journal_directory': str(self.journal), 'activation_env': {'AEHL_NOSCAN_GATE_TOKEN': 'a' * 32},
            'provider_profile': {'frameworks': '/owned/frameworks', 'FILE_sha256': '3' * 64,
                                 'U_sha256': '4' * 64, 'dvacore_sha256': '5' * 64},
            'files': files,
        }
        identity = {k: self.record[k] for k in ('build_id', 'source_commit', 'source_clean', 'target', 'kind', 'run_id')}
        (self.control / 'ready.txt').write_text(json.dumps(identity, sort_keys=True) +
                                                '\npid=4321\nimage=' + str(binary) +
                                                '\nstart=123.456\n')
        (self.control / 'ready.txt').chmod(0o600)
        self.manifest = self.base / 'manifest.json'; self.manifest.write_text(json.dumps(self.record, sort_keys=True) + '\n'); self.manifest.chmod(0o600)
        self.manifest_hash = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.identity = {'pid': 4321, 'executable': str(self.host), 'start': 'owned-start'}
        self.providers = {'FILE': '3' * 64, 'U': '4' * 64, 'dvacore': '5' * 64}

    def identity_fn(self, pid):
        if pid != 4321: raise ValueError('wrong pid')
        return dict(self.identity)

    def provider_verifier(self, record):
        self.assert_record(record)
        return dict(self.providers)

    def assert_record(self, record):
        if record['build_id'] != self.record['build_id']: raise ValueError('wrong record')

    def prepared(self):
        return mod.prepare(self.manifest, self.manifest_hash, 4321,
                           identity_fn=self.identity_fn, authorized_host=self.host,
                           authorized_bundle=self.bundle, provider_verifier=self.provider_verifier)

    def write_pass(self, request):
        (self.control / 'request.txt').write_bytes(request); (self.control / 'request.txt').chmod(0o600)
        before = (field('pid', 4321) + field('start', '123.456') + field('executable', self.record['host_executable']) +
                  field('module', self.record['module_path']) + field('version', '25.6x101') + field('arch', 'arm64') +
                  field('build', 101) + field('main_thread', 1) + field('unsaved', 1) + field('dirty', 0) +
                  field('rendering', 0) + field('items', 0) + field('queued', 0) + field('revision', 7) +
                  field('registry_count', 1) + field('effect', 'ADBE.Test') + field('image_count', 1) +
                  field('image_path', self.record['module_path']) + field('image_header', 4096) + field('image_slide', 0))
        plan = (field('scope', 'no-scan-directory') + field('run', self.record['run_id']) +
                field('source', self.record['source_commit']) + field('build', self.record['build_id']) +
                field('executable', self.record['host_executable']) + field('module', self.record['module_path']) +
                field('directory', self.record['probe_directory']) + field('timeout_ms', 15000))
        claim = plan + before
        started = plan + before
        result = (field('scope', 'no-scan-directory') + field('status', 'PASS') + field('stage', 'complete') +
                  field('reason', 'directory-roundtrip-release-only') + field('claimed', 1) + field('call_started', 1) +
                  field('postflight_observed', 1) + field('cleanup_ok', 1))
        journal_file(self.journal / 'claim.txt', claim)
        journal_file(self.journal / 'before.txt', before)
        journal_file(self.journal / 'call-started.txt', started)
        journal_file(self.journal / 'after.txt', before)
        journal_file(self.journal / 'result.txt', result)


class NoScanSupervisorTests(unittest.TestCase):
    def test_trusted_provider_policy_allows_root_readonly_but_not_writable(self):
        readonly = os.stat_result((stat.S_IFREG | 0o755, 1, 1, 1, 0, 0, 1, 0, 0, 0))
        writable = os.stat_result((stat.S_IFREG | 0o777, 1, 1, 1, 0, 0, 1, 0, 0, 0))
        self.assertTrue(mod.trusted_binary_stat(readonly))
        self.assertFalse(mod.trusted_binary_stat(writable))

    def test_prepare_is_read_only_and_binds_exact_request(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp)
            prepared = f.prepared()
            self.assertEqual(prepared[4], f.identity)
            self.assertEqual(prepared[0]['loaded_process_start'], '123.456')
            self.assertIn(b'private_file_call=authorized', prepared[5])
            self.assertEqual({p.name for p in f.control.iterdir()}, {'ready.txt'})
            self.assertFalse(any(f.journal.iterdir()))
            self.assertFalse(any(f.probe.iterdir()))

    def test_supervise_pass_packages_one_zip_without_request_token(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp); prepared = f.prepared()
            def publish(control, request):
                self.assertEqual(control, f.control); f.write_pass(request)
            report = f.base / 'one-report.zip'
            result, archive = mod.supervise(*prepared, 20, identity_fn=f.identity_fn,
                                            provider_verifier=f.provider_verifier, publish_fn=publish,
                                            clock=lambda: 0.0, sleep=lambda _: None, report_path=report)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(archive, report); self.assertTrue(report.is_file())
            import zipfile
            with zipfile.ZipFile(report) as z:
                names = set(z.namelist())
                self.assertIn('journal/result.txt', names)
                self.assertNotIn('request.txt', names)
                self.assertNotIn('manifest.json', names)
                self.assertNotIn('a' * 32, b''.join(z.read(n) for n in names).decode(errors='ignore'))

    def test_native_process_start_must_match_loaded_aegp_ready_record(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp)
            identity = {k: f.record[k] for k in (
                'build_id', 'source_commit', 'source_clean', 'target', 'kind', 'run_id')}
            (f.control / 'ready.txt').write_text(
                json.dumps(identity, sort_keys=True) + '\npid=4321\nimage=' +
                f.record['module_path'] + '\nstart=999.000\n')
            (f.control / 'ready.txt').chmod(0o600)
            prepared = f.prepared()
            def publish(control, request):
                f.write_pass(request)
            report = f.base / 'start-mismatch.zip'
            result, archive = mod.supervise(*prepared, 20, identity_fn=f.identity_fn,
                                            provider_verifier=f.provider_verifier,
                                            publish_fn=publish, clock=lambda: 0.0,
                                            sleep=lambda _: None, report_path=report)
            self.assertEqual(result['status'], 'FAIL')
            self.assertIn('process-start differs', result['reason'])
            self.assertTrue(archive.is_file())

    def test_package_report_keeps_adapter_stop_evidence(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp)
            stopped = f.control / 'adapter-stopped.txt'
            stopped.write_text('status=FAIL\\nstage=directory-call\\n'); stopped.chmod(0o600)
            report = f.base / 'stopped-report.zip'
            archive = mod.package_report(f.record, f.control, f.journal, report)
            self.assertEqual(archive, report)
            import zipfile
            with zipfile.ZipFile(report) as z:
                self.assertIn('adapter-stopped.txt', set(z.namelist()))

    def test_short_supervisor_timeout_is_rejected_before_publication(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp); prepared = f.prepared(); calls = []
            with self.assertRaisesRegex(ValueError, 'shorter than reviewed native deadline'):
                mod.supervise(*prepared, 19, publish_fn=lambda *_: calls.append(1),
                              report_path=f.base / 'must-not-exist.zip')
            self.assertEqual(calls, [])
            self.assertFalse((f.control / 'supervisor-claim.json').exists())
            self.assertFalse((f.base / 'must-not-exist.zip').exists())

    def test_timeout_is_fail_and_never_retries(self):
        with tempfile.TemporaryDirectory(prefix='aehl-noscan-supervisor-') as tmp:
            f = Fixture(tmp); prepared = f.prepared(); calls = []
            def publish(control, request):
                calls.append(request); (control / 'request.txt').write_bytes(request); (control / 'request.txt').chmod(0o600)
            times = iter([0.0, 21.0])
            report = f.base / 'timeout-report.zip'
            result, archive = mod.supervise(*prepared, 20, identity_fn=f.identity_fn,
                                            provider_verifier=f.provider_verifier, publish_fn=publish,
                                            clock=lambda: next(times), sleep=lambda _: None, report_path=report)
            self.assertEqual(result['status'], 'FAIL')
            self.assertIn('no retry', result['reason']); self.assertEqual(len(calls), 1)
            self.assertTrue(archive.is_file())


if __name__ == '__main__':
    unittest.main()
