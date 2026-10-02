"""Real copied-byte C++ fixtures + synthetic host transport; no AE contact."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/ordinary_discovery'))
import run_retained_identity_probe as runner
import test_retained_host_journal as fixtures


class RetainedSupervisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('clang++') or shutil.which('g++')
        if compiler is None: raise RuntimeError('required C++17 compiler unavailable')
        cls.tmp = tempfile.TemporaryDirectory(prefix='aehl-retained-sup-fixture-')
        cls.addClassCleanup(cls.tmp.cleanup); base = Path(cls.tmp.name).resolve(); binary = base / 'producer'
        build = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            str(ROOT / 'tests/retained_host_journal.cpp'), '-o', str(binary)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
        if build.returncode: raise RuntimeError(build.stderr)
        run = subprocess.run([str(binary), str(base)], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=15)
        if run.returncode: raise RuntimeError(run.stderr)
        cls.raw = {n: (base / 'inline' / n).read_bytes() for n in runner.host.NAMES}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-retained-supervisor-')
        self.addCleanup(self.tmp.cleanup); self.base = Path(self.tmp.name).resolve()
        self.control, self.journal = self.base / 'control', self.base / 'journal'
        self.control.mkdir(mode=0o700); self.journal.mkdir(mode=0o700)
        bundle = self.base / 'owned.plugin'; module = bundle / 'Contents/MacOS/helper'
        module.parent.mkdir(parents=True); module.write_bytes(b'owned-placeholder-not-native')
        host = self.base / 'owned-host'; host.write_bytes(b'owned-placeholder-not-AE')
        self.record = {'build_id': 'identity-' + 'c' * 12, 'run_id': 'retained-identity-' + 'a' * 32,
            'source_commit': 'b' * 40, 'source_clean': True, 'target': 'aarch64-apple-darwin',
            'kind': 'research-only-retained-identity-aegp', 'host_mode': 'authorized-user-host',
            'host_executable': str(host), 'module_path': str(module), 'authorized_bundle': str(bundle),
            'control_directory': str(self.control), 'journal_directory': str(self.journal), 'native_timeout_ms': 15000,
            'installation_performed': False, 'ae_launch_performed': False,
            'external_supervisor': 'AVAILABLE-NOT-RUN', 'files': runner.common.bundle_hashes(bundle),
            'provider_profile': runner.profile(), 'host_sha256': runner.HOST_SHA256,
            'checks': {'build_sign_exports': 'PASS', 'identity_getter': 'PASS', 'inert_entrypoint': 'PASS', 'live_ae': 'NOT RUN'},
            'activation_env': {'AEHL_RETAINED_IDENTITY_TOKEN': '0123456789abcdef0123456789abcdef'}}
        self.observed = {'pid': 73, 'start': '1.2', 'executable': str(host)}
        ready = {k: self.record[k] for k in ('build_id', 'source_commit', 'source_clean', 'target', 'kind', 'run_id')}
        self.ready = json.dumps(ready) + '\npid=73\nimage=' + str(module) + '\nstart=1.2\n'
        (self.control / 'ready.txt').write_text(self.ready)
        self.manifest = self.base / 'manifest.json'; self.manifest.write_text(json.dumps(self.record))
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.providers = {'owned-fixture-only': 'injected-file-check'}
        self.time = 1; self.published = []

    def prepare(self, digest=None, identity=None):
        return runner.prepare(self.manifest, digest or self.digest, 73, Path(self.record['host_executable']),
            Path(self.record['authorized_bundle']), identity_fn=lambda _: identity or self.observed,
            provider_verifier=lambda _: self.providers, signature_fn=lambda _: None)

    def records(self, record):
        policy = runner.policy(record, self.observed); pin = runner.profile()['MEE']
        policy['root'] = str(0x200000 + pin['root_vm'])
        out = {}
        for name, raw in self.raw.items():
            fields = runner.host.fields(runner.host.unwrap(raw, name), count_limit=50000)
            scope = runner.copied.SCOPE_KEYS if name == 'native.txt' else runner.host.PLAN_KEYS
            fields[:len(scope)] = [(k, policy[k]) for k in scope]
            if name in ('claim.txt', 'call-started.txt', 'after.txt'):
                inner = runner.host.fields(bytes.fromhex(fields[-1][1]), count_limit=50000)
                inner[:len(runner.copied.SCOPE_KEYS)] = [(k, policy[k]) for k in runner.copied.SCOPE_KEYS]
                changes = {'observed_executable_hex': policy['executable_hex'], 'observed_module_hex': policy['module_hex']}
                # Retain real safe project/registry fixture; inject explicitly synthetic image transport.
                image_at = next(i for i, (k, _) in enumerate(inner) if k == 'image_count')
                inner = [(k, changes.get(k, v)) for k, v in inner[:image_at]] + [('image_count', '2'),
                    ('image_path_hex', policy['module_hex']), ('image_header', '36864'), ('image_slide', '36864'),
                    ('image_path_hex', os.fsencode(pin['path']).hex()), ('image_header', str(0x200000)),
                    ('image_slide', str(0x200000 - pin['base_vm']))]
                fields[-1] = (fields[-1][0], fixtures.payload(inner).hex())
            if name == 'native.txt':
                # Relocate only the four copied root ranges and their mapping containment.
                fields = [(k, policy['root'] if k == 'frame_address' and v == '4096' else
                    '4096,4194304,0,1,2,0,3,3' if k == 'frame_mapping' else v) for k, v in fields]
            out[name] = fixtures.envelope(name, fixtures.payload(fields))
        return out, policy

    def native(self, record, edit=None):
        records, policy = self.records(record)
        if edit: edit(records)
        for name, raw in records.items():
            path = self.journal / name; path.write_bytes(raw); path.chmod(0o600)
        return policy

    def supervise(self, prepared, publish=None, identity=None, provider=None, bundle=None, sleep=None, authorized=True):
        def default_publish(control, request):
            self.published.append(request); (control / 'request.txt').write_bytes(request); self.native(prepared[0])
        return runner.supervise(*prepared, authorized=authorized,
            identity_fn=identity or (lambda _: self.observed), provider_verifier=provider or (lambda _: self.providers),
            bundle_fn=bundle or runner.common.bundle_hashes, publish_fn=publish or default_publish,
            clock_ns=lambda: self.time, sleep=sleep or (lambda _: None))

    def test_one_request_real_copied_names_separate_verifier_and_token_free_zip(self):
        prepared = self.prepare(); out, archive = self.supervise(prepared)
        self.assertEqual(out['status'], 'PASS'); self.assertEqual(len(self.published), 1)
        self.assertEqual(out['native']['record_names_hex'], ['4fff005a'] * 2)
        self.assertFalse(out['host_execution_verified']); self.assertFalse(out['private_adobe_call_requested'])
        self.assertFalse(out['process_stopped'])
        with zipfile.ZipFile(archive) as z:
            self.assertIsNone(z.testzip()); hashes = json.loads(z.read('report-hashes.json'))
            self.assertEqual(set(z.namelist()), set(hashes) | {'report-hashes.json'})
            for n, digest in hashes.items(): self.assertEqual(hashlib.sha256(z.read(n)).hexdigest(), digest)
            for n in z.namelist(): self.assertNotIn(self.record['activation_env']['AEHL_RETAINED_IDENTITY_TOKEN'].encode(), z.read(n))
            self.assertNotIn('request.txt', z.namelist())
        with self.assertRaises(ValueError): self.supervise(prepared)
        self.assertEqual(len(self.published), 1)

    def test_prepare_scope_candidate_hash_process_and_consumed_refusals(self):
        prepared = self.prepare(); self.assertIn(b'binary_sha256=', prepared[4])
        with self.assertRaises(ValueError): self.prepare('0' * 64)
        with self.assertRaises(ValueError): self.prepare(identity={**self.observed, 'start': '2.3'})
        (self.control / 'request.txt').write_bytes(b'consumed')
        with self.assertRaises(ValueError): self.prepare()

    def test_authority_and_path_request_retarget_refuse_before_claim(self):
        prepared = self.prepare()
        with self.assertRaises(ValueError): self.supervise(prepared, authorized=False)
        bad = list(prepared); bad[4] += b'\n'
        with self.assertRaises(ValueError): self.supervise(bad)
        bad = list(prepared); bad[1] = self.base
        with self.assertRaises(ValueError): self.supervise(bad)
        self.assertEqual({p.name for p in self.control.iterdir()}, {'ready.txt'})
        self.assertEqual(self.published, [])

    def test_root_is_derived_from_image_header_not_echoed_producer_root(self):
        prepared = self.prepare(); records, policy = self.records(prepared[0])
        derived = runner.derived_policy(records, {**policy, 'root': '8'})
        self.assertEqual(derived['root'], policy['root'])
        for name in records:
            fields = runner.host.fields(runner.host.unwrap(records[name], name), count_limit=50000)
            fields = [(k, '8' if k == 'root' else v) for k, v in fields]
            if name in ('claim.txt', 'call-started.txt', 'after.txt'):
                inner = runner.host.fields(bytes.fromhex(fields[-1][1]), count_limit=50000)
                inner = [(k, '8' if k == 'root' else v) for k, v in inner]
                fields[-1] = (fields[-1][0], fixtures.payload(inner).hex())
            records[name] = fixtures.envelope(name, fixtures.payload(fields))
        self.assertEqual(runner.derived_policy(records, {**policy, 'root': '8'})['root'], policy['root'])
        for name, raw in records.items(): (self.journal / name).write_bytes(raw); (self.journal / name).chmod(0o600)
        with self.assertRaises(ValueError): runner.verify_native_pass(prepared[0], self.journal, self.observed,
            started_ns=0, now_ns=lambda: 1)

    def test_provider_helper_inventory_and_slide_root_mutations_refuse(self):
        prepared = self.prepare(); records, policy = self.records(prepared[0]); original = records['claim.txt']
        for key, value in [('image_slide', '-1'), ('image_header', '18446744073709551615'),
                           ('image_path_hex', b'/tmp/unrelated'.hex())]:
            with self.subTest(key=key):
                claim = runner.host.fields(runner.host.unwrap(original, 'claim.txt'))
                inner = runner.host.fields(bytes.fromhex(claim[-1][1]), count_limit=50000)
                indices = [i for i, (k, _) in enumerate(inner) if k == key]
                index = indices[-1]; inner[index] = (key, value)
                claim[-1] = (claim[-1][0], fixtures.payload(inner).hex())
                altered = {**records, 'claim.txt': fixtures.envelope('claim.txt', fixtures.payload(claim))}
                with self.assertRaises(ValueError): runner.derived_policy(altered, {**policy, 'root': '8'})

    def test_publication_unknown_is_consumed_preserves_files_never_retries(self):
        prepared = self.prepare()
        def publish(control, request):
            self.published.append(request); (control / 'request.txt').write_bytes(request)
            raise OSError('unknown publication outcome')
        out, archive = self.supervise(prepared, publish=publish)
        self.assertEqual(out['status'], 'FAIL'); self.assertTrue(out['publication_unknown'])
        self.assertTrue(archive.exists()); self.assertTrue((self.control / 'request.txt').exists())
        with self.assertRaises(ValueError): self.supervise(prepared)
        self.assertEqual(len(self.published), 1)

    def test_expired_before_publication_consumes_claim_without_request(self):
        prepared = self.prepare()
        def provider(_): self.time = 15000000001; return self.providers
        out, archive = self.supervise(prepared, provider=provider)
        self.assertEqual(out['status'], 'FAIL'); self.assertFalse(out['request_attempted'])
        self.assertTrue(archive.exists()); self.assertEqual(self.published, [])
        with self.assertRaises(ValueError): self.supervise(prepared)

    def test_timeout_preserves_partial_evidence_and_one_request(self):
        prepared = self.prepare()
        def publish(control, request):
            self.published.append(request); (control / 'request.txt').write_bytes(request)
            p = self.journal / 'claim.txt'; p.write_bytes(b'partial'); p.chmod(0o600)
        def sleep(_): self.time = 15000000001
        out, archive = self.supervise(prepared, publish=publish, sleep=sleep)
        self.assertEqual(out['status'], 'FAIL'); self.assertEqual(len(self.published), 1)
        self.assertEqual((self.journal / 'claim.txt').read_bytes(), b'partial')
        with zipfile.ZipFile(archive) as z: self.assertEqual(z.read('journal/claim.txt'), b'partial')

    def test_deadline_after_semantics_and_after_final_bundle_recheck_cannot_pass(self):
        prepared = self.prepare(); self.native(prepared[0])
        original = runner.host.verify_records
        def late(*args, **kwargs):
            result = original(*args, **kwargs); self.time = 15000000001; return result
        with patch.object(runner.host, 'verify_records', side_effect=late), self.assertRaises(ValueError):
            runner.verify_native_pass(prepared[0], self.journal, self.observed, started_ns=1, now_ns=lambda: self.time)
        for p in self.journal.iterdir(): p.unlink() # Owned fixture reset only; production never deletes.
        self.time = 1; calls = []
        def bundle(path):
            calls.append(path); result = runner.common.bundle_hashes(path)
            if len(calls) == 2: self.time = 15000000001
            return result
        out, _ = self.supervise(prepared, bundle=bundle)
        self.assertEqual(out['status'], 'FAIL'); self.assertIn('deadline', out['reason'])

    def test_identity_changed_after_verification_refuses(self):
        prepared = self.prepare(); calls = []
        def identity(_):
            calls.append(1); return self.observed if len(calls) < 3 else {**self.observed, 'start': '2.3'}
        out, _ = self.supervise(prepared, identity=identity)
        self.assertEqual(out['status'], 'FAIL'); self.assertIn('identity changed', out['reason'])

    def test_backward_clock_before_publication_refuses_and_consumes(self):
        prepared = self.prepare()
        def provider(_): self.time = 0; return self.providers
        out, _ = self.supervise(prepared, provider=provider)
        self.assertEqual(out['status'], 'FAIL'); self.assertFalse(out['request_attempted'])
        self.assertIn('clock', out['reason']); self.assertEqual(self.published, [])
        with self.assertRaises(ValueError): self.supervise(prepared)

    def test_candidate_installed_payload_tamper_and_ready_change_refuse(self):
        prepared = self.prepare(); (self.control / 'ready.txt').write_text(self.ready.replace('start=1.2', 'start=2.3'))
        with self.assertRaises(ValueError): self.prepare()
        out, _ = self.supervise(prepared)
        self.assertEqual(out['status'], 'FAIL'); self.assertFalse(out['request_attempted'])

    def test_changed_installed_payload_refuses_preparation_and_publication(self):
        prepared = self.prepare()
        Path(self.record['module_path']).write_bytes(b'changed-inert-fixture')
        with self.assertRaises(ValueError): self.prepare()
        out, _ = self.supervise(prepared)
        self.assertEqual(out['status'], 'FAIL'); self.assertFalse(out['request_attempted'])
        self.assertEqual(self.published, [])

if __name__ == '__main__': unittest.main()
