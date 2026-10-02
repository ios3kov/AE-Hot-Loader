"""Actual owned C++ disk producer -> independent Python host/copy verification."""
from copy import deepcopy
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/ordinary_discovery'))
import verify_retained_host_journal as verifier
import verify_retained_identity_journal as copied


def expected(folder):
    values = ('retained-identity', 'mee-25.6-arm64-1', 'owned-fixture',
        'retained-identity-' + 'a' * 32, 'b' * 40, 'identity-' + 'c' * 12,
        'd' * 64, '73', '1', '2', 'e' * 64, 'f' * 32, '4096')
    return {**dict(zip(copied.SCOPE_KEYS, values)), 'protocol': 'retained-host-1',
        'executable_hex': b'/Applications/AE/AE'.hex(), 'module_hex': b'/tmp/identity.plugin'.hex(),
        'journal_hex': os.fsencode(folder).hex(), 'timeout_ms': '15000'}


def payload(data):
    return b''.join(k.encode() + b'=' + str(len(v.encode())).encode() + b':' + v.encode() + b'\n'
                    for k, v in data)


def envelope(name, data):
    return (b'AEHL-RESOURCE-JOURNAL-1\n' + name.encode() + b'\n' + str(len(data)).encode() +
            b'\n' + data + b'\nEND-AEHL-RECORD\n')


class RetainedHostJournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('clang++') or shutil.which('g++')
        if compiler is None:
            raise RuntimeError('required C++17 compiler unavailable')
        cls.tmp = tempfile.TemporaryDirectory(prefix='aehl-retained-host-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name).resolve()
        binary = cls.base / 'producer'
        build = subprocess.run([compiler, '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Wpedantic',
            '-Werror', str(ROOT / 'tests/retained_host_journal.cpp'), '-o', str(binary)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(binary), str(cls.base)], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=15)
        if run.returncode or run.stderr or run.stdout != 'RETAINED_HOST_JOURNAL_CASES=19 PASS; Adobe_calls=0; installs=0\n':
            raise RuntimeError(run.stdout + run.stderr)
        cls.folder = cls.base / 'inline'
        cls.plan = expected(cls.folder)
        cls.records = {n: (cls.folder / n).read_bytes() for n in verifier.NAMES}

    def verify(self, records=None, plan=None, now_ns=lambda: 1):
        return verifier.verify_records(self.records if records is None else records,
            self.plan if plan is None else plan, started_ns=0, now_ns=now_ns)

    def mutate(self, name, action, records=None):
        out = deepcopy(self.records if records is None else records)
        data = verifier.fields(verifier.unwrap(out[name], name))
        action(data)
        out[name] = envelope(name, payload(data))
        return out

    def mutate_observation(self, name, action):
        def edit(data):
            inner = verifier.fields(bytes.fromhex(data[-1][1]), verifier.OBSERVATION_LIMIT, 50000)
            action(inner)
            data[-1] = (data[-1][0], payload(inner).hex())
        return self.mutate(name, edit)

    def replace(self, fields, key, value):
        index = next(i for i, (k, _) in enumerate(fields) if k == key)
        fields[index] = (key, value)

    def test_actual_disk_transaction_capture_and_three_observations(self):
        for name, count in [('empty', 0), ('inline', 2), ('maximum', 8), ('lazy-system', 2), ('large-host', 2)]:
            with self.subTest(name=name):
                folder = self.base / name
                result = verifier.verify_directory(folder, expected(folder), started_ns=0, now_ns=lambda: 1)
                self.assertEqual(result['record_count'], count)
                self.assertEqual(result['registry_count'], 785 if name == 'large-host' else 2)
                self.assertEqual(result['origin'], 'owned-fixture')
                self.assertFalse(result['host_execution_verified'])
                if count == 2:
                    self.assertEqual(result['record_names_hex'], ['4fff005a'] * 2)
                if count == 8:
                    self.assertEqual((result['read_calls'], result['read_bytes']), (22, 6976))

    def test_partial_failed_changed_replayed_poisoned_evidence_cannot_pass(self):
        for name in ('changed-before', 'changed-after', 'failed-post', 'failed-capture', 'expired-marker',
                     'poison', 'path', 'replayed-marker', 'changed-plan', 'oversize', 'invalid-native', 'forged-pass', 'large-bytes'):
            folder = self.base / name
            with self.subTest(name=name), self.assertRaises(ValueError):
                verifier.verify_directory(folder, expected(folder), started_ns=0, now_ns=lambda: 1)

    def test_late_final_producer_pass_requires_independent_external_deadline(self):
        folder = self.base / 'expired-final'
        # A producer record remains provisional if its final save exhausted time.
        with self.assertRaises(ValueError):
            verifier.verify_directory(folder, expected(folder), started_ns=0, now_ns=lambda: 15000000000)
        self.assertEqual(verifier.fields(verifier.unwrap((folder / 'result.txt').read_bytes(), 'result.txt'))[18],
                         ('status', 'PASS'))

    def test_expected_plan_is_frozen_before_supplied_clock_callbacks(self):
        for directory in (False, True):
            plan = dict(self.plan)
            def clock():
                plan['binary'] = '0' * 64
                plan['journal_hex'] = b'/tmp/elsewhere'.hex()
                return 1
            if directory:
                result = verifier.verify_directory(self.folder, plan, started_ns=0, now_ns=clock)
            else:
                result = verifier.verify_records(self.records, plan, started_ns=0, now_ns=clock)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(plan['binary'], '0' * 64)

    def test_each_plan_field_is_bound_in_every_outer_record(self):
        for name in ('claim.txt', 'call-started.txt', 'after.txt', 'result.txt'):
            for key in verifier.PLAN_KEYS:
                with self.subTest(name=name, key=key), self.assertRaises(ValueError):
                    self.verify(self.mutate(name, lambda f: self.replace(f, key, 'wrong')))
        bad = dict(self.plan)
        bad['root'] = '4104'
        with self.assertRaises(ValueError):
            self.verify(plan=bad)

    def test_every_measured_host_and_safety_scalar_is_checked_in_all_three_snapshots(self):
        changes = {k: '0' for k in copied.SCOPE_KEYS + verifier.HOST_KEYS}
        changes.update(dirty='1', rendering='1', items='1', queued='1', revision='2')
        for name in ('claim.txt', 'call-started.txt', 'after.txt'):
            for key, value in changes.items():
                with self.subTest(name=name, key=key), self.assertRaises(ValueError):
                    self.verify(self.mutate_observation(name, lambda f: self.replace(f, key, value)))

    def test_registry_images_ambiguous_inventories_and_unknown_fields_refuse(self):
        actions = [lambda f: self.replace(f, 'registry_count', '20001'),
            lambda f: self.replace(f, 'effect_hex', b'effect-changed'.hex()),
            lambda f: self.replace(f, 'effect_hex', b'effect-\xff'.hex()),
            lambda f: self.replace(f, 'image_header', '0'),
            lambda f: self.replace(f, 'image_slide', '-0'),
            lambda f: self.replace(f, 'image_count', '8193'),
            lambda f: self.replace(f, 'image_path_hex', b'/tmp/../alien'.hex()),
            lambda f: self.replace(f, 'image_path_hex', b'/tmp/alien.plugin'.hex()),
            lambda f: f.append(('eligible', '1'))]
        for action in actions:
            with self.assertRaises(ValueError):
                self.verify(self.mutate_observation('after.txt', action))
        with self.assertRaises(ValueError):
            self.verify(self.mutate('claim.txt', lambda f: f.append(f[-1])))

    def test_ordered_copied_bytes_are_verified_not_just_native_or_result_flags(self):
        for key, value in [('success', '0'), ('failure', 'failed'), ('read_calls', '3'),
                           ('read_bytes', '0'), ('frame_hex', '00' * 16)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(self.mutate('native.txt', lambda f: self.replace(f, key, value)))
        for key, value in [('status', 'FAIL'), ('stage', 'read'), ('claim', 'registration-success'),
                           ('host_execution_verified', '1'), ('evidence_failure', 'failed'),
                           ('diagnostic_saved', '0'), ('postflight_saved', '0')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(self.mutate('result.txt', lambda f: self.replace(f, key, value)))

    def test_strict_framing_inventory_and_bounded_payloads(self):
        for name in verifier.NAMES:
            for raw in (self.records[name][:-1], self.records[name] + b'x', b'x' * (verifier.PAYLOAD_LIMIT + 129)):
                out = dict(self.records)
                out[name] = raw
                with self.assertRaises(ValueError):
                    self.verify(out)
            out = dict(self.records)
            del out[name]
            with self.assertRaises(ValueError):
                self.verify(out)
        with self.assertRaises(ValueError):
            self.verify(self.mutate('result.txt', lambda f: f.append(('unknown', 'x'))))
        with self.assertRaises(ValueError):
            self.verify(self.mutate('claim.txt', lambda f: self.replace(f, 'before_hex', '00' * (verifier.OBSERVATION_LIMIT + 1))))

    def test_deadline_before_during_after_verification_and_backwards_clock_refuse(self):
        for ticks in ((15000000000,), (1, 15000000000), (1, 0), (True,), (-1,)):
            stream = iter(ticks)
            with self.subTest(ticks=ticks), self.assertRaises(ValueError):
                self.verify(now_ns=lambda: next(stream))
        ticks = iter((1, 2, 3, 15000000000))
        with self.assertRaises(ValueError):
            verifier.verify_directory(self.folder, self.plan, started_ns=0, now_ns=lambda: next(ticks))
        for started in (-1, True, copied.MAX_ADDRESS):
            with self.assertRaises(ValueError):
                verifier.verify_records(self.records, self.plan, started_ns=started, now_ns=lambda: 1)

    def test_bad_expected_plan_or_expired_budget_never_opens_files(self):
        for key, value in [('binary', 'x'), ('journal_hex', b'/tmp/../x'.hex()),
                           ('timeout_ms', '1'), ('origin', 'ae-diagnostic')]:
            bad = dict(self.plan)
            bad[key] = value
            with patch.object(copied.os, 'open', side_effect=AssertionError('unexpected IO')):
                with self.assertRaises(ValueError):
                    verifier.verify_directory(self.folder, bad, started_ns=0, now_ns=lambda: 1)
        with patch.object(copied.os, 'open', side_effect=AssertionError('wrong path IO')):
            with self.assertRaises(ValueError):
                verifier.verify_directory(self.base / 'elsewhere', self.plan, started_ns=0, now_ns=lambda: 1)
        with patch.object(copied.os, 'open', side_effect=AssertionError('expired IO')):
            with self.assertRaises(ValueError):
                verifier.verify_directory(self.folder, self.plan, started_ns=0, now_ns=lambda: 15000000000)

    def write_copy(self, folder):
        folder.mkdir(mode=0o700)
        for name, raw in self.records.items():
            if name != 'native.txt':
                values = verifier.fields(verifier.unwrap(raw, name))
                self.replace(values, 'journal_hex', os.fsencode(folder).hex())
                raw = envelope(name, payload(values))
            (folder / name).write_bytes(raw)
            (folder / name).chmod(0o600)

    def test_shared_safe_reader_refuses_special_files_modes_inventory_and_parent_links(self):
        with tempfile.TemporaryDirectory(prefix='aehl-host-corrupt-') as tmp:
            base = Path(tmp).resolve()
            for kind in ('symlink', 'hardlink', 'fifo', 'mode', 'directory', 'extra', 'oversize'):
                folder = base / kind
                self.write_copy(folder)
                target = folder / 'native.txt'
                if kind in ('symlink', 'hardlink', 'fifo', 'directory'):
                    target.unlink()
                if kind == 'symlink': target.symlink_to(self.folder / 'native.txt')
                elif kind == 'hardlink': os.link(self.folder / 'native.txt', target)
                elif kind == 'fifo': os.mkfifo(target, 0o600)
                elif kind == 'mode': target.chmod(0o644)
                elif kind == 'directory': target.mkdir(mode=0o700)
                elif kind == 'extra': (folder / 'extra').touch()
                elif kind == 'oversize': target.write_bytes(b'x' * (verifier.PAYLOAD_LIMIT + 129))
                with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                    verifier.verify_directory(folder, expected(folder), started_ns=0, now_ns=lambda: 1)
                if kind == 'hardlink': target.unlink()
            parent = base / 'parent'
            parent.symlink_to(self.base)
            with self.assertRaises(OSError):
                verifier.verify_directory(parent / 'inline', expected(parent / 'inline'), started_ns=0, now_ns=lambda: 1)

    def test_shared_reader_rechecks_entries_and_directory_after_semantic_verification(self):
        actual = verifier._verify
        with tempfile.TemporaryDirectory(prefix='aehl-host-race-') as tmp:
            base = Path(tmp).resolve()
            for kind in ('entry', 'directory'):
                folder = base / kind
                self.write_copy(folder)
                def mutate(records, plan, budget):
                    out = actual(records, plan, budget)
                    if kind == 'entry': (folder / 'native.txt').write_bytes(b'changed')
                    else:
                        folder.rename(base / 'preserved')
                        folder.mkdir(mode=0o700)
                    return out
                with patch.object(verifier, '_verify', mutate), self.assertRaises(ValueError):
                    verifier.verify_directory(folder, expected(folder), started_ns=0, now_ns=lambda: 1)


if __name__ == '__main__':
    unittest.main()
