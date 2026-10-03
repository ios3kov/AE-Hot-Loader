"""Offline orchestration: real subprocesses/files, no Adobe host or library."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / 'tools/run_research_checks.py'
spec = importlib.util.spec_from_file_location('unified_research', SOURCE)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class UnifiedRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-unified-test-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / 'repo with spaces'
        self.repo.mkdir()
        self.output = self.base / 'private output'
        self.output.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Owned Test')
        self.git('config', 'user.email', 'owned@example.invalid')
        (self.repo / 'owned.txt').write_text('source')
        self.git('add', 'owned.txt')
        self.git('commit', '-qm', 'owned fixture')
        self.commit = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, text=True,
                                       stderr=subprocess.STDOUT, timeout=15)

    def command(self, code, **kwargs):
        return runner.run_command([sys.executable, '-c', code], self.repo,
                                  self.output / 'owned.log', **kwargs)

    def flow(self, plan, identity=None):
        with mock.patch.object(runner, 'stages', return_value=plan), \
             mock.patch.object(runner.shutil, 'which', return_value=sys.executable), \
             contextlib.redirect_stdout(io.StringIO()):
            code, archive = runner.run(self.repo, self.output, identity or self.commit)
        with zipfile.ZipFile(archive) as zipped:
            report = json.loads(zipped.read('report.json'))
            manifest = json.loads(zipped.read('manifest.json'))
            self.assertEqual(set(zipped.namelist()), set(manifest) | {'manifest.json'})
            for path, digest in manifest.items():
                self.assertEqual(hashlib.sha256(zipped.read(path)).hexdigest(), digest)
            self.assertFalse(any(name.startswith('work/') for name in zipped.namelist()))
        self.assertEqual(archive.stat().st_mode & 0o777, 0o600)
        return code, archive, report

    def test_source_identity_pins_bytes_and_commit(self):
        identity = runner.source_identity(self.repo, self.commit)
        self.assertEqual(identity['commit'], self.commit)
        self.assertEqual(identity['tracked_sha256']['owned.txt'], hashlib.sha256(b'source').hexdigest())
        self.assertTrue(identity['clean'])

    def test_python_suite_budget_does_not_extend_individual_stage_limits(self):
        def plan(root,work,system):
            counts = {'status':'PASS','tests_run':1,'skipped':[]}
            code = 'import pathlib; pathlib.Path(%r).write_text(%r)' % (
                str(work/'python.json'),json.dumps(counts))
            return [('python',[sys.executable,'-c',code]),
                    ('individual',[sys.executable,'-c','pass'])]
        with mock.patch.object(runner,'stages',side_effect=plan), \
             mock.patch.object(runner.shutil,'which',return_value=sys.executable), \
             mock.patch.object(runner,'run_command',wraps=runner.run_command) as commands, \
             contextlib.redirect_stdout(io.StringIO()):
            code,archive = runner.run(self.repo,self.output,self.commit)
        self.assertEqual(code,0)
        self.assertEqual([call.kwargs.get('timeout') for call in commands.call_args_list],[480,120])
        with zipfile.ZipFile(archive) as z:
            report=json.loads(z.read('report.json'))
        self.assertEqual([step['timeout_seconds'] for step in report['steps']],[480,120])
        self.assertEqual(report['python_tests']['tests_run'],1)

    def test_dirty_source_rejected_without_reset(self):
        (self.repo / 'owned.txt').write_text('keep my changes')
        with self.assertRaises(runner.Blocked):
            runner.source_identity(self.repo)
        self.assertEqual((self.repo / 'owned.txt').read_text(), 'keep my changes')

    def test_untracked_source_rejected(self):
        (self.repo / 'unknown.py').write_text('not reviewed')
        with self.assertRaises(runner.Blocked):
            runner.source_identity(self.repo)

    def test_assume_unchanged_cannot_hide_foreign_source(self):
        self.git('update-index', '--assume-unchanged', 'owned.txt')
        (self.repo / 'owned.txt').write_text('hidden modification')
        self.assertEqual(self.git('status', '--porcelain'), '')
        with self.assertRaises(runner.Blocked):
            runner.source_identity(self.repo, self.commit)

    def test_missing_python_evidence_fails_even_on_zero_exit(self):
        code, _, report = self.flow([('python', [sys.executable, '-c', 'pass']),
                                    ('never', [sys.executable, '-c', 'pass'])])
        self.assertEqual(code, 2)
        self.assertEqual(report['steps'][0]['status'], 'FAIL')
        self.assertEqual(report['steps'][1]['status'], 'NOT RUN')

    def test_wrong_commit_rejected(self):
        with self.assertRaises(runner.Blocked):
            runner.source_identity(self.repo, '0' * 40)

    def test_nested_checkout_path_rejected(self):
        child = self.repo / 'nested'
        child.mkdir()
        with self.assertRaises(runner.Blocked):
            runner.source_identity(child)

    def test_real_success_error_text_is_only_output(self):
        result = self.command("print('error: ordinary test payload')")
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['returncode'], 0)
        self.assertIn(b'error:', (self.output / 'owned.log').read_bytes())

    def test_real_failed_process_preserves_output(self):
        result = self.command("print('partial data', flush=True); raise SystemExit(3)")
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['returncode'], 3)
        self.assertIn(b'partial data', (self.output / 'owned.log').read_bytes())

    def test_real_timeout_stops_owned_child(self):
        result = runner.run_command(['/bin/sh', '-c', 'printf "%s\\n" "$$"; exec sleep 15'],
                                    self.repo, self.output / 'owned.log', timeout=1)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('time limit', result['reason'])
        pid = int((self.output / 'owned.log').read_text().strip())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_real_output_limit(self):
        result = self.command("print('x' * 10000)", limit=128)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual((self.output / 'owned.log').stat().st_size, 128)

    def test_exited_child_permission_race_keeps_failed_bounded_result(self):
        started = []
        original = runner.subprocess.Popen
        def spawn(*args, **kwargs):
            proc = original(*args, **kwargs)
            started.append(proc)
            return proc
        def denied(pid, sig):
            self.assertEqual((pid, sig), (started[0].pid, signal.SIGKILL))
            started[0].wait(timeout=5)
            raise PermissionError('group signal denied after child exit')
        with mock.patch.object(runner.subprocess, 'Popen', side_effect=spawn), \
             mock.patch.object(runner.os, 'killpg', side_effect=denied):
            result = self.command("print('x' * 10000)", limit=128)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual((self.output / 'owned.log').stat().st_size, 128)
        self.assertEqual(started[0].returncode, 0)
        self.assertTrue(started[0].stdout.closed)

    def test_live_child_permission_denial_is_not_ignored(self):
        started = []
        original = runner.subprocess.Popen
        def spawn(*args, **kwargs):
            proc = original(*args, **kwargs)
            started.append(proc)
            return proc
        try:
            with mock.patch.object(runner.subprocess, 'Popen', side_effect=spawn), \
                 mock.patch.object(runner.os, 'killpg', side_effect=PermissionError('denied')):
                with self.assertRaises(PermissionError):
                    self.command("import time; print('x' * 10000, flush=True); time.sleep(15)", limit=128)
            self.assertIsNone(started[0].poll())
        finally:
            if started:
                os.killpg(started[0].pid, signal.SIGKILL)
                started[0].wait(timeout=5)
                started[0].stdout.close()

    def test_missing_tool_is_blocked(self):
        result = runner.run_command([str(self.base / 'absent')], self.repo, self.output / 'owned.log')
        self.assertEqual(result['status'], 'BLOCKED')

    def test_existing_log_not_replaced(self):
        path = self.output / 'owned.log'
        path.write_text('keep')
        with mock.patch.object(runner.subprocess, 'Popen') as popen:
            result = self.command("print('wrong')")
            popen.assert_not_called()
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(path.read_text(), 'keep')

    def test_one_zip_and_no_live_success_claim(self):
        good = [sys.executable, '-c', "print('owned')"]
        code, _, report = self.flow([('one', good), ('two', good)])
        self.assertEqual(code, 0)
        self.assertEqual(report['offline_status'], 'PASS')
        self.assertEqual(report['full_pipeline_status'], 'BLOCKED')
        self.assertFalse(report['live_ae_operations_requested'])
        self.assertEqual(report['product_package_status'], 'NOT RUN')
        self.assertTrue(report['source_unchanged_after'])
        self.assertEqual(len(list(self.output.glob('*.zip'))), 1)

    def test_failure_stops_remaining_stages_with_one_report(self):
        code, _, report = self.flow([
            ('first', [sys.executable, '-c', 'print(1)']),
            ('second', [sys.executable, '-c', 'raise SystemExit(5)']),
            ('never', [sys.executable, '-c', 'raise AssertionError()'])])
        self.assertEqual(code, 2)
        self.assertEqual([s['status'] for s in report['steps']], ['PASS', 'FAIL', 'NOT RUN'])
        self.assertEqual(len(list(self.output.glob('*.zip'))), 1)

    def test_source_change_stops_next_stage(self):
        cmd = [sys.executable, '-c', "from pathlib import Path; Path('owned.txt').write_text('changed')"]
        code, _, report = self.flow([('mutate-owned-fixture', cmd), ('never', cmd)])
        self.assertEqual(code, 2)
        self.assertEqual(report['offline_status'], 'BLOCKED')
        self.assertEqual(report['steps'][1]['status'], 'NOT RUN')
        self.assertEqual((self.repo / 'owned.txt').read_text(), 'changed')

    def test_dirty_source_still_reports_without_tests(self):
        (self.repo / 'owned.txt').write_text('dirty')
        with mock.patch.object(runner, 'run_command') as execute:
            code, _, report = self.flow([('never', [sys.executable, '-c', 'pass'])])
            execute.assert_not_called()
        self.assertEqual(code, 2)
        self.assertEqual(report['offline_status'], 'BLOCKED')

    def test_runs_never_reuse_previous_zip(self):
        plan = [('one', [sys.executable, '-c', 'print(1)'])]
        first = self.flow(plan)[1]
        original = first.read_bytes()
        second = self.flow(plan)[1]
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_bytes(), original)

    def test_output_inside_checkout_refused(self):
        with self.assertRaises(runner.Blocked):
            runner.run(self.repo, self.repo)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_worker_counts_skips_without_inflation(self):
        tests = self.repo / 'tests'; tests.mkdir()
        (tests / 'test_owned_worker.py').write_text(
            "import unittest\nclass Owned(unittest.TestCase):\n"
            " def test_ok(self): self.assertTrue(True)\n"
            " @unittest.skip('owned skip')\n def test_skip(self): pass\n")
        out = self.output / 'counts.json'
        with contextlib.redirect_stderr(io.StringIO()):
            code = runner.python_worker(self.repo, out)
        data = json.loads(out.read_text())
        self.assertEqual(code, 0)
        self.assertEqual(data['tests_run'], 2)
        self.assertEqual(len(data['skipped']), 1)
        self.assertTrue(data['nested_native_cases_not_added_to_python_count'])

    def test_worker_empty_suite_not_success(self):
        tests = self.repo / 'tests'; tests.mkdir()
        out = self.output / 'empty.json'
        with contextlib.redirect_stderr(io.StringIO()):
            code = runner.python_worker(self.repo, out)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.read_text())['status'], 'FAIL')

    def test_fixed_plan_never_executes_installer_or_ae(self):
        for system in ('linux', 'darwin'):
            plan = runner.stages(SOURCE.parents[1], self.output, system)
            for name, command in plan:
                text = ' '.join(command)
                self.assertNotIn('osascript', text)
                self.assertNotIn('aerender', text)
                self.assertNotIn('PLUG_Search', text)
                if any(arg.endswith('.command') for arg in command):
                    self.assertEqual(command[:2], ['/bin/zsh', '-n'])
            self.assertEqual(len({name for name, _ in plan}), len(plan))


if __name__ == '__main__':
    unittest.main()
