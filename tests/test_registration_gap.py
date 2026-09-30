"""Synthetic evidence only. These tests do not reproduce or run After Effects."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from urllib.parse import quote

SOURCE = Path(__file__).resolve().parents[1] / 'experiments/ordinary_discovery/analyze_registration_gap.py'
spec = importlib.util.spec_from_file_location('registration_gap', SOURCE)
gap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gap)
ROOT = '/owned/run/scan root'
IMAGE = ROOT + '/Fixture.plugin/Contents/MacOS/Fixture'
MATCH = 'AEHL.Embedded.synthetic'


def snap(names=('ADBE A', 'ADBE B'), revision=1):
    encoded = sorted(quote(name, safe="~()*!.'-_") for name in names)
    return ('AEHL-SNAPSHOT-1\n' + str(revision) + '\n' + '\n'.join(encoded) + '\n').encode()


def log(added=0):
    lines = [
        f'internal-loader: calling ML::LoadPlugins root={ROOT} fn=0x1000',
        'internal-loader: returned=1 output=[0x2000,0x2018,0x2030]',
        f'internal-loader: dyld image={IMAGE} PluginDataEntryFunction2=0x0 EffectMain=0x3000',
        f'internal-loader: dyld root={ROOT} matched_images=1',
        f'internal-loader: video modules before=339 after={339 + added} added={added}',
    ]
    if added:
        lines.append(f'internal-loader: FLT_NotifyFilterLoadingDone returned added={added}')
    lines.append(f'internal-loader: ordinary registration complete loaded=1 added_modules={added}')
    return ('\n'.join(lines) + '\n').encode()


def analyze(raw=None, before=None, after=None):
    return gap.analyze(raw if raw is not None else log(), before if before is not None else snap(),
                       after if after is not None else snap(), ROOT, IMAGE, MATCH)


class RegistrationGapTests(unittest.TestCase):
    def test_loaded_but_missing_is_not_registration_pass(self):
        result = analyze()
        self.assertEqual(result['analysis_status'], 'PASS')
        self.assertEqual(result['registry']['exact_addition_check'], 'FAIL')
        self.assertEqual(result['notifier_dispatch_inference'], 'SKIPPED_ZERO_NEW_MODULES')
        self.assertEqual(result['returned_vector_bytes'], 24)
        self.assertEqual(result['returned_vector_element_type'], 'UNOBSERVED')
        self.assertEqual(result['current_host_state'], 'BLOCKED')
        self.assertEqual(result['live_registration_gate'], 'NOT RUN')
        self.assertEqual(result['apply_render'], 'NOT RUN')
        self.assertNotIn(ROOT, json.dumps(result))
        self.assertNotIn('0x2000', json.dumps(result))
        self.assertNotIn('ADBE A', json.dumps(result))

    def test_exact_addition_is_only_a_registry_check(self):
        result = analyze(log(1), after=snap(('ADBE A', 'ADBE B', MATCH)))
        self.assertEqual(result['registry']['exact_addition_check'], 'PASS')
        self.assertEqual(result['notifier_dispatch_inference'], 'RETURN_LOGGED')
        self.assertEqual(result['live_registration_gate'], 'NOT RUN')

    def test_other_root_is_not_selected(self):
        other = log().replace(ROOT.encode(), b'/other/run')
        self.assertEqual(analyze(other + log())['loader_return'], 1)

    def test_following_other_transaction_is_not_mixed(self):
        other = log(1).replace(ROOT.encode(), b'/other/run')
        self.assertEqual(analyze(log() + other)['notifier_dispatch_inference'], 'SKIPPED_ZERO_NEW_MODULES')

    def test_null_vector_is_valid_but_not_registry_proof(self):
        result = analyze(log().replace(b'0x2000,0x2018,0x2030', b'(nil),(nil),(nil)'))
        self.assertEqual(result['returned_vector_bytes'], 0)
        self.assertEqual(result['registry']['exact_addition_check'], 'FAIL')

    def test_equal_counts_do_not_prove_equal_registry(self):
        result = analyze(after=snap(('ADBE A', 'ADBE C')))
        self.assertFalse(result['registry']['identities_unchanged'])
        self.assertEqual(result['registry']['exact_addition_check'], 'FAIL')

    def test_unicode_match_roundtrip(self):
        text = 'AEHL.Embedded.тест (A)!'
        result = gap.analyze(log(1), snap(), snap(('ADBE A', 'ADBE B', text)), ROOT, IMAGE, text)
        self.assertEqual(result['registry']['exact_addition_check'], 'PASS')

    def test_dynamic_export_is_not_called_entrypoint(self):
        result = analyze(log().replace(b'PluginDataEntryFunction2=0x0', b'PluginDataEntryFunction2=0x9876'))
        self.assertTrue(result['dynamic_export_address_observed'])
        self.assertEqual(result['parsed_pipl_evidence'], 'BLOCKED')


# Named cases remain separate unittest results, not hidden subtest totals.
def bad_log_test(transform):
    def test(self):
        with self.assertRaises(ValueError):
            analyze(transform(log()))
    return test


BAD_LOGS = {
    'replay': lambda raw: raw + raw,
    'root_prefix_collision': lambda raw: raw.replace(ROOT.encode(), (ROOT + '-other').encode()),
    'missing_return': lambda raw: b'\n'.join(line for line in raw.split(b'\n') if not line.startswith(b'internal-loader: returned=')),
    'missing_modules': lambda raw: b'\n'.join(line for line in raw.split(b'\n') if b'video modules before=' not in line),
    'missing_completion': lambda raw: raw.split(b'internal-loader: ordinary registration complete')[0],
    'duplicate_modules': lambda raw: raw + b'internal-loader: video modules before=339 after=339 added=0\n',
    'notify_without_modules': lambda raw: raw + b'internal-loader: FLT_NotifyFilterLoadingDone returned added=0\n',
    'completion_count_mismatch': lambda raw: raw.replace(b'added_modules=0', b'added_modules=1'),
    'loader_count_mismatch': lambda raw: raw.replace(b'complete loaded=1', b'complete loaded=2'),
    'impossible_module_delta': lambda raw: raw.replace(b'after=339 added=0', b'after=340 added=0'),
    'invalid_vector': lambda raw: raw.replace(b'0x2000,0x2018,0x2030', b'0x2018,0x2000,0x2030'),
    'null_nonempty_vector': lambda raw: raw.replace(b'0x2000,0x2018,0x2030', b'0x0,0x2018,0x2030'),
    'extra_fixture_image': lambda raw: raw + f'internal-loader: dyld image={ROOT}/Other.plugin PluginDataEntryFunction2=0x0 EffectMain=0x0\n'.encode(),
    'wrong_image_count': lambda raw: raw.replace(b'matched_images=1', b'matched_images=2'),
    'out_of_order': lambda raw: b'\n'.join([raw.splitlines()[0], *reversed(raw.splitlines()[1:])]) + b'\n',
    'unmatched_notification': lambda raw: log(1).replace(b'LoadingDone returned added=1', b'LoadingDone returned added=2'),
    'missing_notification': lambda raw: b'\n'.join(line for line in log(1).split(b'\n') if b'LoadingDone returned' not in line),
}
for name, transform in BAD_LOGS.items():
    setattr(RegistrationGapTests, 'test_reject_' + name, bad_log_test(transform))


def fail_registry_test(before, after):
    def test(self):
        self.assertEqual(analyze(log(1), before, after)['registry']['exact_addition_check'], 'FAIL')
    return test


BAD_REGISTRY = {
    'preexisting_target': (snap(('ADBE A', MATCH)), snap(('ADBE A', MATCH))),
    'unrelated_addition': (snap(), snap(('ADBE A', 'ADBE B', 'OTHER'))),
    'duplicate_target': (snap(), snap(('ADBE A', 'ADBE B', MATCH, MATCH))),
    'removed_identity': (snap(), snap(('ADBE A', MATCH))),
    'changed_revision': (snap(), snap(('ADBE A', 'ADBE B', MATCH), revision=2)),
}
for name, pair in BAD_REGISTRY.items():
    setattr(RegistrationGapTests, 'test_registry_reject_' + name, fail_registry_test(*pair))


class EvidenceInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.path = self.base / 'evidence.txt'
        self.raw = log()
        self.path.write_bytes(self.raw)
        self.sha = hashlib.sha256(self.raw).hexdigest()

    def test_verified_read_preserves_file(self):
        before = self.path.stat()
        self.assertEqual(gap.read_verified(self.path, self.sha), self.raw)
        after = self.path.stat()
        self.assertEqual((before.st_mtime_ns, before.st_size), (after.st_mtime_ns, after.st_size))

    def test_wrong_hash(self):
        with self.assertRaises(ValueError):
            gap.read_verified(self.path, '0' * 64)

    def test_invalid_hash(self):
        with self.assertRaises(ValueError):
            gap.read_verified(self.path, 'not-a-hash')

    def test_oversize(self):
        with self.assertRaises(ValueError):
            gap.read_verified(self.path, self.sha, limit=1)

    def test_symlink(self):
        link = self.base / 'linked'
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            gap.read_verified(link, self.sha)

    def test_parent_symlink(self):
        link = self.base / 'parent-link'
        link.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ValueError):
            gap.read_verified(link / self.path.name, self.sha)

    def test_hardlink(self):
        linked = self.base / 'hardlink'
        os.link(self.path, linked)
        with self.assertRaises(ValueError):
            gap.read_verified(linked, self.sha)

    def test_fifo_rejected_without_blocking(self):
        fifo = self.base / 'fifo'
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            gap.read_verified(fifo, self.sha)

    def cli(self, corrupt=False):
        argv = []
        for name, raw in (('loader-log', self.raw), ('before', snap()), ('after', snap())):
            path = self.base / name
            path.write_bytes(raw)
            argv += ['--' + name, str(path), '--' + name + '-sha256',
                     '0' * 64 if corrupt else hashlib.sha256(raw).hexdigest()]
        argv += ['--scan-root', ROOT, '--fixture-image', IMAGE, '--fixture-match', MATCH]
        originals = {p.name: p.read_bytes() for p in self.base.iterdir()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = gap.main(argv)
        self.assertEqual(originals, {p.name: p.read_bytes() for p in self.base.iterdir()})
        return code, json.loads(output.getvalue())

    def test_cli_success_does_not_write_or_claim_live_pass(self):
        code, report = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(report['registry']['exact_addition_check'], 'FAIL')
        self.assertEqual(report['live_registration_gate'], 'NOT RUN')
        self.assertEqual(len(report['input_sha256']), 3)

    def test_cli_bad_hash_is_blocked(self):
        code, report = self.cli(corrupt=True)
        self.assertEqual(code, 2)
        self.assertEqual(report['analysis_status'], 'BLOCKED')
        self.assertNotIn(str(self.base), json.dumps(report))

    def test_malformed_snapshots(self):
        cases = [b'', snap()[:-1], snap().replace(b'\n1\n', b'\n0\n'),
                 b'AEHL-SNAPSHOT-1\n1\nB\nA\n', b'AEHL-SNAPSHOT-1\n1\nA%zz\n',
                 b'AEHL-SNAPSHOT-1\n1\nA%00\n', b'AEHL-SNAPSHOT-1\n1\nA%FF\n']
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                gap.snapshot(raw)

    def test_unsafe_saved_paths(self):
        for path in ('relative', '/owned/../scan', '/owned//scan', '/owned/scan\n', '/'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                gap.saved_path(path)

    def test_fixture_outside_root(self):
        with self.assertRaises(ValueError):
            gap.analyze(log(), snap(), snap(), ROOT, '/other/Fixture', MATCH)


if __name__ == '__main__':
    unittest.main()
