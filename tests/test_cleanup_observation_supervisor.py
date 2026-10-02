"""Synthetic independent diagnostic journal verifier and one-shot supervision."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/ordinary_discovery'))
import run_cleanup_observation_probe as runner


def fields_bytes(fields):
    return b''.join(k.encode() + b'=' + str(len(v.encode())).encode() + b':' + v.encode() + b'\n'
                    for k, values in fields.items() for v in values)


def word(value, size=8):
    return value.to_bytes(size, 'little')


def diagnostic(callbacks=1, records=1):
    root = {'PLUG': 0x100000 + 0x18490, 'MEE': 0x200000 + 0x10fd70}
    header = bytearray(72); header[:4] = word(0x00d00bee, 4)
    header[16:20] = word(callbacks, 4); header[24:28] = word(16, 4)
    sack = bytes(16) + word(0x4200)
    frames = [(0x4000, word(0x4100)), (0x4100, sack), (0x4200, word(0x4300)), (0x4300, bytes(header))]
    targets = [0x9000 + i * 4 for i in range(callbacks)]; contexts = [42 + i for i in range(callbacks)]
    if callbacks:
        frames.append((0x4348, b''.join(word(t) + word(c) for t, c in zip(targets, contexts))))
    begin = 0x6000 if records else 0; end = begin + records * 0xb0
    frames.append((root['MEE'], word(begin) + word(end)))
    reads = [(root['PLUG'], 8)] + [(a, len(b)) for a, b in frames] * 3 + [(root['PLUG'], 8)]
    mapping = '4096,7340032,0,1,2,0,3,3'
    d = {'scope': ['cleanup-observer'], 'success': ['1'], 'failure': [''],
         'read_calls': [str(len(reads))], 'read_bytes': [str(sum(s for _, s in reads))],
         'global_address': [str(root['PLUG'])], 'global_hex': [word(0x4000).hex()],
         'general_plugin_records': [str(records)], 'callback_count': [str(callbacks)], 'frame_count': [str(len(frames))],
         'frame_address': [str(a) for a, _ in frames], 'frame_hex': [b.hex() for _, b in frames],
         'callback_target': [str(t) for t in targets], 'callback_context': [str(c) for c in contexts],
         'read_count': [str(len(reads))], 'read_address': [str(a) for a, _ in reads], 'read_size': [str(s) for _, s in reads],
         'read_mapping': [mapping] * len(reads), 'containment_count': ['1' if begin else '0']}
    if begin:
        d.update(containment_address=[str(begin)], containment_size=[str(end - begin)], containment_mapping=[mapping])
    return d, root


class ObserverSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-observer-supervisor-')
        self.addCleanup(self.tmp.cleanup); self.base = Path(self.tmp.name).resolve()
        self.control = self.base / 'control'; self.journal = self.base / 'journal'
        self.control.mkdir(mode=0o700); self.journal.mkdir(mode=0o700)
        bundle = self.base / 'owned.plugin'; module = bundle / 'Contents/MacOS/helper'
        module.parent.mkdir(parents=True); module.write_bytes(b'owned-inert-placeholder-not-native')
        host = self.base / 'owned-host'; host.write_bytes(b'owned-host-placeholder')
        self.record = {'build_id': 'observe-' + 'c' * 12, 'run_id': 'cleanup-observer-' + 'a' * 32,
            'source_commit': 'b' * 40, 'source_clean': True, 'target': 'aarch64-apple-darwin',
            'kind': 'research-only-cleanup-observer-aegp', 'host_mode': 'authorized-user-host',
            'host_executable': str(host), 'module_path': str(module), 'authorized_bundle': str(bundle),
            'control_directory': str(self.control), 'journal_directory': str(self.journal), 'native_timeout_ms': 15000,
            'installation_performed': False, 'ae_launch_performed': False, 'files': runner.common.bundle_hashes(bundle),
            'provider_profile': runner.profile(), 'host_sha256': runner.HOST_SHA256, 'loaded_process_start': '1.2',
            'checks': {'build_sign_exports': 'PASS', 'identity_getter': 'PASS', 'inert_entrypoint': 'PASS', 'live_ae': 'NOT RUN'},
            'activation_env': {'AEHL_CLEANUP_OBSERVER_TOKEN': 'private-placeholder-token'}}
        self.observed = {'pid': 73, 'start': '1.2', 'executable': str(host)}
        ready = {k: self.record[k] for k in ('build_id', 'source_commit', 'source_clean', 'target', 'kind', 'run_id')}
        (self.control / 'ready.txt').write_text(json.dumps(ready) + '\npid=73\nimage=' + str(module) + '\nstart=1.2\n')
        self.manifest = self.base / 'manifest.json'; self.manifest.write_text(json.dumps(self.record))
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()

    def native(self, mutate=None):
        r = self.record
        o = {k: [v] for k, v in {'pid': '73', 'start': '1.2', 'executable': r['host_executable'],
            'module': r['module_path'], 'version': '25.6x101', 'arch': 'arm64', 'build': '101',
            'main_thread': '1', 'unsaved': '1', 'dirty': '0', 'rendering': '0', 'items': '0', 'queued': '0',
            'revision': '1', 'registry_count': '1', 'effect': 'Owned', 'image_count': '3'}.items()}
        o.update(image_path=[r['module_path'], runner.profile()['PLUG']['path'], runner.profile()['MEE']['path']],
                 image_header=['4096', str(0x100000), str(0x200000)], image_slide=['0', '0', '0'])
        plan = {k: [v] for k, v in {'scope': 'cleanup-observer', 'run': r['run_id'], 'source': r['source_commit'],
            'build': r['build_id'], 'executable': r['host_executable'], 'module': r['module_path'],
            'journal': r['journal_directory'], 'timeout_ms': '15000'}.items()}
        d, _ = diagnostic()
        final = {k: [v] for k, v in {'scope': 'cleanup-observer', 'status': 'PASS', 'stage': 'complete',
            'reason': 'matching-diagnostic-only', 'claimed': '1', 'read_started': '1', 'diagnostic_saved': '1', 'postflight_saved': '1'}.items()}
        payloads = {'before.txt': fields_bytes(o), 'after.txt': fields_bytes(o),
                    'claim.txt': fields_bytes(plan) + fields_bytes(o), 'call-started.txt': fields_bytes(plan) + fields_bytes(o),
                    'native.txt': fields_bytes(d), 'result.txt': fields_bytes(final)}
        if mutate: mutate(payloads)
        for name, payload in payloads.items():
            (self.journal / name).write_bytes(runner.common.MAGIC + name.encode() + b'\n' +
                str(len(payload)).encode() + b'\n' + payload + b'\nEND-AEHL-RECORD\n')

    def test_diagnostic_boundaries_order_and_no_authority(self):
        for callbacks, records in [(0, 0), (1, 1), (256, 2)]:
            with self.subTest(callbacks=callbacks):
                d, root = diagnostic(callbacks, records); out = runner.verify_diagnostic(d, root)
                self.assertEqual(out['callback_count'], callbacks); self.assertEqual(out['general_plugin_records'], records)
        original, root = diagnostic()
        for key, value in [('callback_count', ['257']), ('read_calls', ['21']), ('read_bytes', ['16385']),
            ('global_hex', [word(0x4008).hex()]), ('global_address', ['1']), ('callback_target', ['0']),
            ('callback_context', ['43']), ('general_plugin_records', ['0']), ('frame_address', ['0'] * 6),
            ('frame_hex', ['ff'] * 6), ('read_mapping', ['4096,7340032,0,1,2,0,5,7'] * 20),
            ('containment_size', ['1']), ('read_address', ['1'] * 20), ('success', ['0']),
            ('failure', ['failed']), ('scope', ['no-scan-directory']), ('complete', ['1']), ('success', ['1', '1'])]:
            with self.subTest(key=key):
                d = deepcopy(original); d[key] = value
                with self.assertRaises(ValueError): runner.verify_diagnostic(d, root)

    def test_native_journal_and_marker_binding(self):
        self.native(); out = runner.verify_native_pass(self.record, self.journal, self.observed)
        self.assertEqual(out['general_plugin_records'], 1)
        for name, replacement in [('after.txt', b'bad'), ('native.txt', b'bad'), ('result.txt', b'bad'), ('call-started.txt', b'bad')]:
            with self.subTest(name=name):
                self.native(lambda p: p.update({name: replacement}))
                with self.assertRaises(ValueError): runner.verify_native_pass(self.record, self.journal, self.observed)
        self.native(); (self.journal / 'unexpected.txt').write_bytes(b'extra')
        with self.assertRaises(ValueError): runner.verify_native_pass(self.record, self.journal, self.observed)

    def prepare(self, digest=None, identity=None):
        return runner.prepare(self.manifest, digest or self.digest, 73, Path(self.record['host_executable']),
            Path(self.record['authorized_bundle']), identity_fn=lambda _: identity or self.observed,
            provider_verifier=lambda _: {'owned': 'bytes'}, signature_fn=lambda _: None)

    def test_prepare_identity_hash_and_reuse_refusals(self):
        prepared = self.prepare(); self.assertIn(b'read_only=authorized', prepared[4])
        with self.assertRaises(ValueError): self.prepare('0' * 64)
        with self.assertRaises(ValueError): self.prepare(identity={**self.observed, 'start': '2.3'})
        (self.control / 'request.txt').write_bytes(b'consumed')
        with self.assertRaises(ValueError): self.prepare()

    def test_supervise_single_publish_and_token_free_report(self):
        prepared = self.prepare(); published = []
        def publish(control, request): published.append(request); (control / 'request.txt').write_bytes(request); self.native()
        out, archive = runner.supervise(*prepared, 20, identity_fn=lambda _: self.observed,
            provider_verifier=lambda _: {'owned': 'bytes'}, publish_fn=publish)
        self.assertEqual(out['status'], 'PASS'); self.assertEqual(len(published), 1)
        self.assertFalse(out['private_adobe_call_requested']); self.assertFalse(out['process_stopped'])
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist(): self.assertNotIn(b'private-placeholder-token', z.read(name))
        with self.assertRaises((ValueError, FileExistsError)): runner.supervise(*prepared, 20,
            identity_fn=lambda _: self.observed, provider_verifier=lambda _: {'owned': 'bytes'}, publish_fn=publish)
        self.assertEqual(len(published), 1)

    def test_timeout_keeps_native_state_and_never_retries(self):
        prepared = self.prepare(); published = []; ticks = iter([0, 0, 21])
        out, _ = runner.supervise(*prepared, 20, identity_fn=lambda _: self.observed,
            provider_verifier=lambda _: {'owned': 'bytes'}, publish_fn=lambda c, r: published.append(r),
            clock=lambda: next(ticks), sleep=lambda _: None)
        self.assertEqual(out['status'], 'FAIL'); self.assertIn('timeout', out['reason']); self.assertEqual(len(published), 1)
        self.assertFalse(out['process_stopped']); self.assertFalse(out['installation_performed'])

    def test_expired_preflight_does_not_publish_and_consumes_attempt(self):
        prepared = self.prepare(); published = []; now = [0]
        def providers(_):
            now[0] = 20
            return {'owned': 'bytes'}
        out, archive = runner.supervise(*prepared, 20, identity_fn=lambda _: self.observed,
            provider_verifier=providers, publish_fn=lambda c, r: published.append(r),
            clock=lambda: now[0], sleep=lambda _: None)
        self.assertEqual(published, [])
        self.assertEqual(out['status'], 'FAIL'); self.assertIn('timeout', out['reason'])
        self.assertFalse(out['request_published']); self.assertTrue(archive.is_file())
        self.assertTrue((self.control / 'supervisor-claim.json').is_file())
        with self.assertRaises(FileExistsError):
            runner.supervise(*prepared, 20, identity_fn=lambda _: self.observed,
                provider_verifier=providers, publish_fn=lambda c, r: published.append(r),
                clock=lambda: now[0], sleep=lambda _: None)
        self.assertEqual(published, [])

    def test_verification_at_deadline_cannot_report_pass(self):
        prepared = self.prepare(); published = []; now = [0]; checks = []
        def providers(_):
            checks.append(True)
            if len(checks) == 2: now[0] = 20
            return {'owned': 'bytes'}
        def publish(control, request):
            published.append(request)
            (control / 'request.txt').write_bytes(request)
            self.native()
        out, archive = runner.supervise(*prepared, 20, identity_fn=lambda _: self.observed,
            provider_verifier=providers, publish_fn=publish,
            clock=lambda: now[0], sleep=lambda _: None)
        self.assertEqual(out['status'], 'FAIL'); self.assertIn('timeout', out['reason'])
        self.assertEqual(len(published), 1); self.assertTrue(out['request_published'])
        self.assertIsNotNone(out['native']); self.assertTrue(archive.is_file())
        self.assertEqual({p.name for p in self.journal.iterdir()}, runner.NATIVE_NAMES)
        self.assertFalse(out['process_stopped'])


if __name__ == '__main__':
    unittest.main()
