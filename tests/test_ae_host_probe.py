"""Owned temporary filesystem and process mocks. No live After Effects evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import collect_ae_host as probe

RUN = 'aehl-preflight-' + 'a' * 32
REPLY = 'version=1\nrequest_id=' + RUN + '\nstatus=success\nmessage=identity\n'


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def test_reply_matches(self):
        self.assertEqual(probe.parse_reply(REPLY.encode())['request_id'], RUN)

    def test_utf8_bom_supported(self):
        self.assertEqual(probe.parse_reply(b'\xef\xbb\xbf' + REPLY.encode())['status'], 'success')

    def test_invalid_replies_rejected(self):
        for raw in (b'', REPLY.rstrip().encode(), b'x' * 20000, REPLY.replace('version=1', 'version=2').encode(),
                    (REPLY + 'status=error\n').encode(), b'version=1\ninvalid\n',
                    REPLY.replace('success', 'mystery').encode(), (REPLY + 'message=evil\0\n').encode()):
            with self.subTest(raw=raw[:50]), self.assertRaises((probe.Blocked, ValueError)):
                probe.parse_reply(raw)

    def test_identity_match_is_not_render_evidence(self):
        record = probe.identity_check(dict(probe.EXPECTED, status='success'))
        self.assertEqual(record['status'], 'PASS')
        self.assertIn('not ScriptUI or render', record['scope'])

    def test_every_missing_or_changed_identity_field_fails(self):
        for key in probe.EXPECTED:
            for value in (None, 'wrong'):
                data = dict(probe.EXPECTED, status='success')
                if value is None: del data[key]
                else: data[key] = value
                with self.subTest(key=key, value=value):
                    self.assertEqual(probe.identity_check(data)['status'], 'FAIL')

    def test_error_with_matching_identity_cannot_pass(self):
        self.assertEqual(probe.identity_check(dict(probe.EXPECTED, status='error'))['status'], 'FAIL')

    def test_read_regular_rejects_symlink_and_large_file(self):
        target = self.root / 'target'
        target.write_bytes(b'content')
        self.assertEqual(probe.read_regular(target), b'content')
        link = self.root / 'link'
        link.symlink_to(target)
        with self.assertRaises(OSError): probe.read_regular(link)
        with self.assertRaises(probe.Blocked): probe.read_regular(target, 3)
        with self.assertRaises(probe.Blocked): probe.read_regular(self.root)

    def test_fifo_cannot_block_read(self):
        fifo = self.root / 'fifo'
        os.mkfifo(fifo)
        with self.assertRaises(probe.Blocked): probe.read_regular(fifo)

    def test_symlink_parent_rejected(self):
        link = self.root / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(probe.Blocked): probe.no_symlinks(link / 'child')

    def test_missing_bridge_not_created(self):
        missing = self.root / 'missing'
        with self.assertRaises(probe.Blocked): probe.agent_query(missing, RUN)
        self.assertFalse(missing.exists())

    def test_run_id_cannot_inject_command_or_path(self):
        for token in ('../escape', RUN + '\ncommand=reload_plugins', 'arbitrary'):
            with self.assertRaises(probe.Blocked): probe.agent_query(self.root, token)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_bridge_files_preserved(self):
        for name in ('request.txt', 'response.txt'):
            p = self.root / name; p.write_text('foreign data')
            with self.assertRaises(probe.Blocked): probe.agent_query(self.root, RUN)
            self.assertEqual(p.read_text(), 'foreign data')
            p.unlink()

    def test_diagnostic_only_request_and_response_consumption(self):
        def answer(_):
            request = self.root / 'request.txt'
            body = request.read_text()
            self.assertIn('command=get_build_identity\n', body)
            self.assertNotIn('reload_plugins', body)
            request.unlink()  # mock Agent consumes its input
            (self.root / 'response.txt').write_text(REPLY)
        with patch.object(probe.time, 'sleep', side_effect=answer):
            self.assertEqual(probe.agent_query(self.root, RUN)['status'], 'success')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_timeout_preserves_request_without_scan(self):
        with self.assertRaises(probe.Blocked): probe.agent_query(self.root, RUN, timeout=0)
        self.assertIn('command=get_build_identity', (self.root / 'request.txt').read_text())
        self.assertFalse(list(self.root.glob('*.tmp')))

    def test_atomic_publish_does_not_replace_concurrent_request(self):
        def occupied(*_):
            (self.root / 'request.txt').write_text('concurrent')
            raise FileExistsError('already present')
        with patch.object(probe.os, 'link', side_effect=occupied), self.assertRaises(FileExistsError):
            probe.agent_query(self.root, RUN)
        self.assertEqual((self.root / 'request.txt').read_text(), 'concurrent')
        self.assertFalse(list(self.root.glob('*.tmp')))

    def test_foreign_reply_never_satisfies_or_gets_deleted(self):
        ticks = iter([0, 0, 2])
        def foreign(_):
            (self.root / 'response.txt').write_text(REPLY.replace(RUN, 'other-run'))
        with patch.object(probe.time, 'monotonic', side_effect=lambda: next(ticks)), \
             patch.object(probe.time, 'sleep', side_effect=foreign), self.assertRaises(probe.Blocked):
            probe.agent_query(self.root, RUN, timeout=1)
        self.assertIn('other-run', (self.root / 'response.txt').read_text())

    def test_host_selection_requires_one_real_main_process(self):
        path = '/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects'
        sample = '12 /usr/bin/osascript\n42 ' + path + '\n43 /Applications/Test.app/Contents/MacOS/aerender\n'
        self.assertEqual(probe.find_host(sample), (42, Path(path.split('/Contents/')[0])))
        with self.assertRaises(probe.Blocked): probe.find_host('')
        with self.assertRaises(probe.Blocked): probe.find_host(sample + '\n99 ' + path)

    def test_applescript_escapes_paths_and_does_not_control_processes(self):
        text = probe.applescript(Path('/Applications/A "quote" \\ name.app'))
        self.assertIn('\\"quote\\"', text)
        self.assertIn('is not running then error', text)
        self.assertIn('DoScriptFile', text)
        for token in ('activate', 'quit', 'launch', 'do shell script'):
            self.assertNotIn(token, text)
        with self.assertRaises(probe.Blocked): probe.applescript(Path('/A\nB.app'))

    def test_non_mac_records_blocked_not_pass_without_subprocess(self):
        with patch.object(probe.sys, 'platform', 'linux'), patch.object(probe.subprocess, 'run') as child:
            report = probe.collect(self.root, RUN)
        child.assert_not_called()
        self.assertEqual(report['collection_status'], 'BLOCKED')
        self.assertTrue(all(c['status'] == 'NOT RUN' for c in report['checks'].values()))

    def test_snapshot_rejects_stale_result(self):
        with patch.object(probe.subprocess, 'run'):
            (self.root / 'before.json').write_text(json.dumps({'schema_version': 1, 'run_id': 'stale', 'status': 'PASS'}))
            with self.assertRaises(probe.Blocked): probe.snapshot(Path('/AE.app'), self.root, RUN, 'before')

    def test_host_process_change_invalidates_collection(self):
        snapshot = {'host_version': '25.6x101', 'project': {'rendering': False}}
        with patch.object(probe.sys, 'platform', 'darwin'), \
             patch.object(probe, 'process_list', side_effect=['1 /AE.app/Contents/MacOS/After Effects', '2 /AE.app/Contents/MacOS/After Effects']), \
             patch.object(probe, 'process_start', return_value='same'), \
             patch.object(probe, 'snapshot', return_value=snapshot), patch.object(probe, 'agent_query') as agent:
            report = probe.collect(self.root, RUN)
        agent.assert_not_called()
        self.assertEqual(report['collection_status'], 'BLOCKED')

    def test_no_product_operations_in_snapshot(self):
        for token in ('addComp', 'addProperty', 'app.newProject', 'app.open(', '.render()', '.purge(', 'reload_plugins'):
            self.assertNotIn(token, probe.SNAPSHOT)

    def test_actual_snapshot_js_under_mock_host(self):
        script = ROOT / 'tests/ae-host-snapshot.cjs'
        result = subprocess.run(['node', str(script)], input=probe.SNAPSHOT, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('snapshot mocks: 9/9', result.stdout)


if __name__ == '__main__':
    unittest.main()
