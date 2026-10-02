"""Native producer -> independent Python verifier, plus corrupt private evidence."""
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
import verify_retained_identity_journal as verifier


def expected():
    return dict(zip(verifier.SCOPE_KEYS, ('retained-identity', 'mee-25.6-arm64-1',
        'owned-fixture', 'retained-identity-' + 'a' * 32, 'b' * 40, 'identity-' + 'c' * 12,
        'd' * 64, '73', '1', '2', 'e' * 64, 'f' * 32, '4096')))


def payload(fields):
    return b''.join(k.encode() + b'=' + str(len(v.encode())).encode() + b':' + v.encode() + b'\n'
                    for k, v in fields)


def envelope(name, data):
    return (b'AEHL-RESOURCE-JOURNAL-1\n' + name.encode() + b'\n' + str(len(data)).encode() +
            b'\n' + data + b'\nEND-AEHL-RECORD\n')


class RetainedIdentityJournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('clang++') or shutil.which('g++')
        if compiler is None:
            raise RuntimeError('required C++17 compiler unavailable')
        cls.tmp = tempfile.TemporaryDirectory(prefix='aehl-retained-journal-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name).resolve()
        binary = cls.base / 'journal'
        build = subprocess.run([compiler, '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Wpedantic',
            '-Werror', str(ROOT / 'tests/retained_identity_journal.cpp'), '-o', str(binary)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(binary), str(cls.base)], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=10)
        if run.returncode or run.stderr or run.stdout != 'RETAINED_JOURNAL_CASES=17 PASS; Adobe_calls=0\n':
            raise RuntimeError(run.stdout + run.stderr)
        cls.inline = {n: (cls.base / 'inline' / n).read_bytes() for n in verifier.NAMES}
        cls.maximum = {n: (cls.base / 'maximum' / n).read_bytes() for n in verifier.NAMES}

    def mutate(self, raw, name, action):
        out = deepcopy(raw)
        fields = verifier.fields(verifier.unwrap(out[name], name))
        action(fields)
        out[name] = envelope(name, payload(fields))
        return out

    def test_cpp_disk_journals_independently_decode_ordered_raw_names(self):
        for name, count in [('empty', 0), ('inline', 2), ('maximum', 8)]:
            with self.subTest(name=name):
                out = verifier.verify_directory(self.base / name, expected())
                self.assertEqual(out['record_count'], count)
                self.assertFalse(out['host_execution_verified'])
                self.assertEqual(out['origin'], 'owned-fixture')
                if count == 2:
                    self.assertEqual(out['record_names_hex'], ['4fff005a'] * 2)
                if count == 8:
                    self.assertEqual(out['read_calls'], 22)
                    self.assertEqual(out['read_bytes'], 6976)
                    self.assertEqual(out['record_names_hex'], ['ff00' + 'ff' * 253] * 8)

    def test_failed_producer_cannot_become_pass(self):
        with self.assertRaises(ValueError):
            verifier.verify_directory(self.base / 'failed', expected())
        failed = {n: (self.base / 'failed' / n).read_bytes() for n in verifier.NAMES}
        forged = self.mutate(failed, 'result.txt', lambda f:
                             f.__setitem__(-2, ('status', 'PASS')))
        with self.assertRaises(ValueError):
            verifier.verify_records(forged, expected())
        for folder in ['order', 'scope', 'origin', 'bad-native']:
            with self.subTest(folder=folder), self.assertRaises(ValueError):
                verifier.verify_directory(self.base / folder, expected())

    def test_run_candidate_process_provider_and_origin_are_independently_bound(self):
        for key in ['run', 'source', 'build', 'binary', 'pid', 'start_sec', 'start_usec',
                    'provider_sha', 'provider_uuid', 'root', 'origin']:
            with self.subTest(key=key):
                altered = expected()
                altered[key] = '1' if key in ('pid', 'start_sec', 'start_usec', 'root') else 'x'
                if key == 'start_sec':
                    altered[key] = '2'
                if key == 'origin':
                    altered[key] = 'ae-diagnostic'
                with self.assertRaises(ValueError):
                    verifier.verify_records(self.inline, altered)

    def test_marker_scope_duplicates_unknown_fields_and_final_status_refuse(self):
        cases = [('claim.txt', lambda f: f.append(('complete', '1'))),
                 ('call-started.txt', lambda f: f.append(f[-1])),
                 ('native.txt', lambda f: f.insert(0, ('success', '1'))),
                 ('native.txt', lambda f: f.append(('eligible', '1'))),
                 ('result.txt', lambda f: f.__setitem__(-2, ('status', 'FAIL')))]
        for name, action in cases:
            with self.subTest(name=name), self.assertRaises(ValueError):
                verifier.verify_records(self.mutate(self.inline, name, action), expected())

    def test_both_captures_rechecks_read_order_mapping_and_budgets_refuse_corruption(self):
        name = 'native.txt'
        original = verifier.fields(verifier.unwrap(self.maximum[name], name))
        positions = {k: [i for i, (key, _) in enumerate(original) if key == k]
                     for k in ('frame_hex', 'frame_address', 'frame_size', 'frame_mapping',
                               'frame_count', 'read_calls', 'read_bytes', 'success', 'failure')}
        changes = [(positions['read_calls'][0], '21'), (positions['read_bytes'][0], '6975'),
                   (positions['frame_count'][0], '21'), (positions['success'][0], '0'),
                   (positions['failure'][0], 'failed'), (positions['frame_address'][1], '12288'),
                   (positions['frame_size'][1], '1407'), (positions['frame_hex'][0], '00' * 16),
                   (positions['frame_mapping'][0], '4096,20480,0,1,2,0,5,7'),
                   (positions['frame_mapping'][-1], '4096,20480,0,99,2,0,3,3')]
        for frame in (10, 11, 12, 13, 21):
            pos = positions['frame_hex'][frame]
            data = bytearray.fromhex(original[pos][1])
            data[0] ^= 8
            changes.append((pos, data.hex()))
        for index, value in changes:
            with self.subTest(index=index), self.assertRaises(ValueError):
                verifier.verify_records(self.mutate(self.maximum, name,
                    lambda f: f.__setitem__(index, (f[index][0], value))), expected())

    def test_name_capacity_termination_state_overlap_and_alias_corruption_refuse(self):
        original = verifier.fields(verifier.unwrap(self.maximum['native.txt'], 'native.txt'))
        hex_positions = [i for i, (k, _) in enumerate(original) if k == 'frame_hex']
        for frame, offset, replacement in [(1, 0x98, (256).to_bytes(8, 'little')),
            (1, 0x90, (4096).to_bytes(8, 'little')), (2, 255, b'x'), (3, 0, b'x')]:
            with self.subTest(frame=frame, offset=offset):
                position = hex_positions[frame]
                data = bytearray.fromhex(original[position][1])
                data[offset:offset + len(replacement)] = replacement
                corrupt = self.mutate(self.maximum, 'native.txt', lambda f:
                    f.__setitem__(position, ('frame_hex', data.hex())))
                with self.assertRaises(ValueError):
                    verifier.verify_records(corrupt, expected())

    def test_framing_truncation_noncanonical_lengths_and_inventory_refuse(self):
        name = 'native.txt'
        inner = verifier.unwrap(self.inline[name], name)
        for bad in [self.inline[name][:-1], self.inline[name] + b'x',
                    envelope(name, inner.replace(b'success=1:1', b'success=01:1')),
                    envelope(name, inner.replace(b'success=1:1', b'success=-1:1')),
                    b'x' * (verifier.PAYLOAD_LIMIT + 129)]:
            raw = dict(self.inline)
            raw[name] = bad
            with self.assertRaises(ValueError):
                verifier.verify_records(raw, expected())
        for name in verifier.NAMES:
            raw = dict(self.inline)
            del raw[name]
            with self.assertRaises(ValueError):
                verifier.verify_records(raw, expected())

    def test_allocated_empty_vector_keeps_four_root_reads(self):
        raw = {n: (self.base / 'empty' / n).read_bytes() for n in verifier.NAMES}
        vector = ((8192).to_bytes(8, 'little') * 2).hex()
        def change(fields):
            for i, (key, _) in enumerate(fields):
                if key == 'frame_hex':
                    fields[i] = (key, vector)
        out = verifier.verify_records(self.mutate(raw, 'native.txt', change), expected())
        self.assertEqual((out['record_count'], out['read_calls'], out['read_bytes']), (0, 4, 64))

    def test_invalid_expected_scope_refuses_before_any_file_access(self):
        bad = expected()
        bad['binary'] = 'unknown'
        with patch.object(verifier.os, 'open', side_effect=AssertionError('unexpected file read')):
            with self.assertRaises(ValueError):
                verifier.verify_directory(self.base / 'inline', bad)

    def test_entry_change_and_directory_replacement_after_read_refuse(self):
        actual = verifier.verify_records
        with tempfile.TemporaryDirectory(prefix='aehl-journal-race-') as tmp:
            base = Path(tmp).resolve()
            for kind in ('entry', 'directory'):
                folder = base / kind
                folder.mkdir(mode=0o700)
                for name, raw in self.inline.items():
                    (folder / name).write_bytes(raw)
                    (folder / name).chmod(0o600)
                def mutate(records, scope):
                    summary = actual(records, scope)
                    if kind == 'entry':
                        (folder / 'native.txt').write_bytes(b'changed after read')
                    else:
                        folder.rename(base / 'preserved')
                        folder.mkdir(mode=0o700)
                    return summary
                with self.subTest(kind=kind), patch.object(verifier, 'verify_records', mutate):
                    with self.assertRaises(ValueError):
                        verifier.verify_directory(folder, expected())

    def test_private_files_symlinks_hardlinks_fifo_modes_and_extra_entries_refuse(self):
        with tempfile.TemporaryDirectory(prefix='aehl-journal-corrupt-') as tmp:
            base = Path(tmp).resolve()
            for kind in ['symlink', 'hardlink', 'fifo', 'mode', 'directory', 'extra', 'oversize']:
                folder = base / kind
                folder.mkdir(mode=0o700)
                for name, raw in self.inline.items():
                    (folder / name).write_bytes(raw)
                    (folder / name).chmod(0o600)
                target = folder / 'native.txt'
                if kind in ('symlink', 'hardlink', 'fifo', 'directory'):
                    target.unlink()
                if kind == 'symlink':
                    target.symlink_to(self.base / 'inline/native.txt')
                elif kind == 'hardlink':
                    os.link(self.base / 'inline/native.txt', target)
                elif kind == 'fifo':
                    os.mkfifo(target, 0o600)
                elif kind == 'mode':
                    target.chmod(0o644)
                elif kind == 'directory':
                    target.mkdir(mode=0o700)
                elif kind == 'extra':
                    (folder / 'extra').touch()
                elif kind == 'oversize':
                    target.write_bytes(b'x' * (verifier.PAYLOAD_LIMIT + 129))
                with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                    verifier.verify_directory(folder, expected())
                if kind == 'hardlink':
                    target.unlink()
            link = base / 'parent'
            link.symlink_to(self.base)
            with self.assertRaises(OSError):
                verifier.verify_directory(link / 'inline', expected())


if __name__ == '__main__':
    unittest.main()
