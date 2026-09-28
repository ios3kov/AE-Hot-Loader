"""Passive bridge inspection tests; no live After Effects evidence."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import inspect_ae_bridge as probe

REQUEST = b'version=1\nrequest_id=test-request\ncommand=reload_plugins\ntimestamp=1\n'
RESPONSE = b'version=1\nrequest_id=test-request\nstatus=success\nmessage=PRIVATE/path/token\n'


class BridgeInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.bridge = self.root / 'Library/Application Support/AE Hot Loader/bridge'
        self.bridge.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def inspect(self):
        with patch.object(probe, 'agent_query', side_effect=AssertionError('No requests allowed'), create=True), \
             patch('subprocess.run', side_effect=AssertionError('No host calls allowed')):
            return probe.inspect_bridge(self.bridge, 'owned-test')

    def write(self, name, data):
        path = self.bridge / name
        path.write_bytes(data)
        return path

    def test_missing_directory_is_not_created(self):
        missing = self.root / 'absent'
        record = probe.inspect_bridge(missing, 'owned-test')
        self.assertEqual(record['collection_status'], 'BLOCKED')
        self.assertFalse(missing.exists())

    def test_empty_bridge_does_not_publish_request(self):
        report = self.inspect()
        self.assertEqual(report['disposition'], 'EMPTY_AT_SNAPSHOT')
        self.assertEqual(list(self.bridge.iterdir()), [])
        self.assertEqual(report['live_agent_identity']['status'], 'NOT RUN')

    def test_response_only_is_not_deleted_or_treated_as_live_identity(self):
        path = self.write('response.txt', RESPONSE)
        before = path.stat()
        report = self.inspect()
        self.assertEqual(report['disposition'], 'RESPONSE_PRESENT')
        self.assertEqual(path.read_bytes(), RESPONSE)
        self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(path.stat().st_mode, before.st_mode)
        self.assertEqual(report['live_agent_identity']['status'], 'NOT RUN')
        self.assertEqual(report['request_execution_state'], 'UNKNOWN')

    def test_request_only_is_not_consumed(self):
        path = self.write('request.txt', REQUEST)
        report = self.inspect()
        self.assertEqual(report['disposition'], 'REQUEST_PRESENT')
        self.assertEqual(report['files']['request.txt']['record']['command'], 'reload_plugins')
        self.assertEqual(path.read_bytes(), REQUEST)

    def test_matching_pair_does_not_prove_completion(self):
        self.write('request.txt', REQUEST)
        self.write('response.txt', RESPONSE)
        report = self.inspect()
        self.assertEqual(report['disposition'], 'REQUEST_AND_RESPONSE_PRESENT')
        self.assertTrue(report['stored_request_ids_match'])
        self.assertEqual(report['request_execution_state'], 'UNKNOWN')
        self.assertEqual(len(list(self.bridge.iterdir())), 2)

    def test_unmatched_pair_is_reported_without_deletion(self):
        self.write('request.txt', REQUEST)
        self.write('response.txt', RESPONSE.replace(b'test-request', b'other'))
        report = self.inspect()
        self.assertFalse(report['stored_request_ids_match'])
        self.assertEqual(len(list(self.bridge.iterdir())), 2)

    def test_matching_stored_build_id_is_not_resident_verification(self):
        raw = RESPONSE + ''.join(k + '=' + v + '\n' for k, v in probe.EXPECTED.items()).encode()
        self.write('response.txt', raw)
        report = self.inspect()
        record = report['files']['response.txt']['record']
        self.assertTrue(record['matches_reference_record'])
        self.assertEqual(record['stored_agent_identity'], probe.EXPECTED)
        self.assertEqual(report['live_agent_identity']['status'], 'NOT RUN')

    def test_missing_and_changed_identity_are_not_relabelled_as_matching(self):
        for key in probe.EXPECTED:
            for missing in (True, False):
                values = dict(probe.EXPECTED)
                if missing:
                    del values[key]
                else:
                    values[key] = 'other'
                self.write('response.txt', RESPONSE + ''.join(k + '=' + v + '\n' for k, v in values.items()).encode())
                with self.subTest(key=key, missing=missing):
                    record = self.inspect()['files']['response.txt']['record']
                    self.assertFalse(record['matches_reference_record'])

    def test_messages_unknown_fields_and_raw_ids_are_not_disclosed(self):
        self.write('response.txt', RESPONSE + b'private_field=/PRIVATE/secret\nagent_git_commit=/PRIVATE/secret\n')
        report = self.inspect()
        text = json.dumps(report)
        self.assertNotIn('PRIVATE', text)
        self.assertNotIn('test-request', text)
        self.assertNotIn('private_field', text)
        record = report['files']['response.txt']['record']
        self.assertEqual(record['request_id_sha256'], hashlib.sha256(b'test-request').hexdigest())
        self.assertEqual(record['identity_fields_invalid'], ['agent_git_commit'])

    def test_unknown_command_and_status_values_are_not_echoed(self):
        self.write('request.txt', REQUEST.replace(b'reload_plugins', b'/PRIVATE/secret'))
        self.write('response.txt', RESPONSE.replace(b'success', b'/PRIVATE/secret'))
        report = self.inspect()
        self.assertEqual(report['files']['request.txt']['record']['command'], 'unrecognized')
        self.assertEqual(report['files']['response.txt']['record']['status'], 'unrecognized')
        self.assertNotIn('PRIVATE', json.dumps(report))

    def test_invalid_or_incomplete_records_stay_untouched(self):
        variants = [b'', RESPONSE.rstrip(), RESPONSE + b'status=error\n', RESPONSE + b'bad line\n',
                    RESPONSE.replace(b'version=1', b'version=2'), RESPONSE + b'nul=\0\n',
                    RESPONSE + b'invalid=\xff\n', RESPONSE.replace(b'test-request', b''),
                    RESPONSE.replace(b'test-request', b'a' * 129)]
        for raw in variants:
            path = self.write('response.txt', raw)
            with self.subTest(raw=raw[:30]):
                report = self.inspect()
                self.assertEqual(report['collection_status'], 'BLOCKED')
                self.assertEqual(path.read_bytes(), raw)
                self.assertNotIn('record', report['files']['response.txt'])

    def test_bom_and_crlf_are_supported(self):
        self.write('response.txt', b'\xef\xbb\xbf' + RESPONSE.replace(b'\n', b'\r\n'))
        self.assertEqual(self.inspect()['files']['response.txt']['status'], 'PASS')

    def test_oversized_file_is_not_read_or_truncated(self):
        path = self.write('response.txt', RESPONSE + b'X' * probe.MAX_REPLY)
        report = self.inspect()
        self.assertEqual(report['collection_status'], 'BLOCKED')
        self.assertEqual(path.stat().st_size, len(RESPONSE) + probe.MAX_REPLY)

    def test_symlink_file_does_not_read_target(self):
        target = self.root / 'private'; target.write_bytes(RESPONSE)
        (self.bridge / 'response.txt').symlink_to(target)
        with patch.object(probe, 'read_regular', side_effect=AssertionError('Target must not be opened')):
            report = self.inspect()
        self.assertEqual(report['collection_status'], 'BLOCKED')
        self.assertTrue((self.bridge / 'response.txt').is_symlink())

    def test_symlink_parent_is_blocked(self):
        link = self.root / 'link'; link.symlink_to(self.bridge, target_is_directory=True)
        self.assertEqual(probe.inspect_bridge(link, 'owned-test')['collection_status'], 'BLOCKED')

    def test_pipe_or_directory_at_reply_path_never_opens(self):
        path = self.bridge / 'response.txt'
        os.mkfifo(path)
        with patch.object(probe, 'read_regular', side_effect=AssertionError('Pipe must not be opened')):
            self.assertEqual(self.inspect()['collection_status'], 'BLOCKED')
        path.unlink(); path.mkdir()
        self.assertEqual(self.inspect()['collection_status'], 'BLOCKED')

    def test_wrong_owner_is_rejected_before_read(self):
        self.write('response.txt', RESPONSE)
        with patch.object(probe.os, 'getuid', return_value=os.getuid() + 1), \
             patch.object(probe, 'read_regular', side_effect=AssertionError('Wrong owner must not be read')):
            self.assertEqual(self.inspect()['collection_status'], 'BLOCKED')

    def test_changed_file_during_read_is_not_used(self):
        path = self.write('response.txt', RESPONSE)
        read = probe.read_regular
        def changed(p):
            raw = read(p)
            path.write_bytes(RESPONSE + b'extra=new\n')
            return raw
        with patch.object(probe, 'read_regular', side_effect=changed):
            report = self.inspect()
        self.assertEqual(report['collection_status'], 'BLOCKED')
        self.assertNotIn('record', report['files']['response.txt'])

    def test_disappearing_file_is_not_success(self):
        path = self.write('response.txt', RESPONSE)
        def gone(p):
            path.unlink()
            raise FileNotFoundError('PRIVATE')
        with patch.object(probe, 'read_regular', side_effect=gone):
            report = self.inspect()
        self.assertEqual(report['collection_status'], 'BLOCKED')
        self.assertNotIn('PRIVATE', json.dumps(report))

    def test_file_age_never_proves_stale_or_completed_request(self):
        path = self.write('request.txt', REQUEST)
        for when in (1, 4000000000):
            os.utime(path, (when, when))
            report = self.inspect()
            self.assertEqual(report['request_execution_state'], 'UNKNOWN')
            self.assertEqual(report['disposition'], 'REQUEST_PRESENT')

    def test_unrelated_files_are_not_read(self):
        self.write('unrelated-secret.txt', b'PRIVATE')
        report = self.inspect()
        self.assertEqual(set(report['files']), {'request.txt', 'response.txt'})
        self.assertNotIn('PRIVATE', json.dumps(report))

    def test_cli_mode_does_not_call_host_or_publish_and_writes_private_report(self):
        response = self.write('response.txt', RESPONSE)
        args = ['inspector', '--output-parent', str(self.root)]
        with patch.object(sys, 'argv', args), patch.object(probe.Path, 'home', return_value=self.root), \
             patch.object(probe, 'collect', side_effect=AssertionError('Active preflight forbidden'), create=True), \
             patch('subprocess.run', side_effect=AssertionError('No process commands')), \
             patch.object(probe, 'agent_query', side_effect=AssertionError('No request'), create=True), \
             contextlib.redirect_stdout(io.StringIO()):
            code = probe.main()
        self.assertEqual(code, 0)
        reports = list(self.root.glob('aehl-bridge-*/report.json'))
        self.assertEqual(len(reports), 1)
        self.assertEqual(stat.S_IMODE(reports[0].parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(reports[0].stat().st_mode), 0o600)
        self.assertEqual(json.loads(reports[0].read_text())['scope'], 'passive-bridge-files-only')
        self.assertEqual(response.read_bytes(), RESPONSE)
        self.assertFalse((self.bridge / 'request.txt').exists())


if __name__ == '__main__':
    unittest.main()
