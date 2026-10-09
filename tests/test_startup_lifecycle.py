"""Owned launcher/process-event failure controls; never Adobe runtime proof."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/startup_trace'))
from lifecycle import stopped_event, debugger_exit, same_stop
from lldb_collector import finalize, write_once
import launch


class ProcessEventTests(unittest.TestCase):
    def setUp(self):
        self.process=Mock()
        self.process.GetUniqueID.return_value=17
        self.process.GetProcessID.return_value=123
        self.process.GetState.return_value=5
        self.owner=Mock()
        self.owner.IsValid.return_value=True
        self.owner.GetUniqueID.return_value=17
        self.owner.GetProcessID.return_value=123
        self.event=Mock();self.event.GetType.return_value=1
        self.calls=SimpleNamespace(EventIsProcessEvent=Mock(return_value=True),
            GetProcessFromEvent=Mock(return_value=self.owner),GetStateFromEvent=Mock(return_value=5),
            GetRestartedFromEvent=Mock(return_value=False),eBroadcastBitStateChanged=1)
        self.api=SimpleNamespace(SBProcess=self.calls,eStateStopped=5)

    def test_owned_stop_admits_metadata_only(self):
        self.assertTrue(stopped_event(self.event,self.process,self.api))
        self.process.GetThreadAtIndex.assert_not_called()
        self.process.Continue.assert_not_called()

    def test_unrelated_and_nonstate_events_do_not_inspect_threads(self):
        self.calls.EventIsProcessEvent.return_value=False
        self.assertFalse(stopped_event(self.event,self.process,self.api))
        self.calls.GetProcessFromEvent.assert_not_called()
        self.calls.EventIsProcessEvent.return_value=True;self.event.GetType.return_value=2
        self.assertFalse(stopped_event(self.event,self.process,self.api))
        self.calls.GetStateFromEvent.assert_not_called()

    def test_foreign_pid_or_same_pid_different_process_instance_refuses(self):
        for method in ('GetProcessID','GetUniqueID'):
            owner=Mock();owner.IsValid.return_value=True
            owner.GetUniqueID.return_value=17;owner.GetProcessID.return_value=123
            getattr(owner,method).return_value=99;self.calls.GetProcessFromEvent.return_value=owner
            with self.subTest(method=method),self.assertRaisesRegex(ValueError,'identity'):
                stopped_event(self.event,self.process,self.api)
        self.process.GetThreadAtIndex.assert_not_called()

    def test_loader_restart_or_running_event_never_continues(self):
        self.calls.GetRestartedFromEvent.return_value=True
        self.assertFalse(stopped_event(self.event,self.process,self.api))
        self.calls.GetRestartedFromEvent.return_value=False;self.calls.GetStateFromEvent.return_value=6
        self.assertFalse(stopped_event(self.event,self.process,self.api))
        self.process.Continue.assert_not_called();self.process.GetState.assert_not_called()

    def test_stopped_event_with_now_running_process_refuses_before_frame(self):
        self.process.GetState.return_value=6
        with self.assertRaisesRegex(ValueError,'no longer'):stopped_event(self.event,self.process,self.api)
        self.process.GetThreadAtIndex.assert_not_called();self.process.Continue.assert_not_called()

    def test_stop_id_changed_after_metadata_cannot_admit_registers(self):
        self.process.GetStopID.return_value=10
        with self.assertRaisesRegex(ValueError,'left'):same_stop(self.process,9,self.api)
        self.process.GetThreadAtIndex.assert_not_called()

    def test_same_stop_requires_both_state_and_id(self):
        self.process.GetStopID.return_value=9;same_stop(self.process,9,self.api)
        self.process.GetState.return_value=6
        with self.assertRaisesRegex(ValueError,'left'):same_stop(self.process,9,self.api)


class CleanupJournalTests(unittest.TestCase):
    def run_cleanup(self, target=None, process=None, writer=None):
        self.target=target or Mock();self.target.BreakpointDelete.return_value=True
        self.process=process or Mock();self.process.IsValid.return_value=True
        self.process.GetProcessID.return_value=123;self.process.GetState.return_value=5
        self.process.Detach.return_value.Success.return_value=True
        self.report={'status':'INCOMPLETE','cleanup_safe':False,'partial_trace':{'phase':'adapter'}}
        self.breakpoints={n:Mock() for n in ('marker','adapter')}
        for i,bp in enumerate(self.breakpoints.values()):bp.GetID.return_value=i+1
        return self.target,self.process

    def test_observation_saved_before_removal_then_detach_then_final(self):
        target,process=self.run_cleanup()
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            def remove(_):
                self.assertEqual(json.loads((output/'observation.json').read_text())['cleanup_safe'],False)
                return True
            target.BreakpointDelete.side_effect=remove
            finalize(target,process,self.breakpoints,self.report,output,SimpleNamespace(eStateExited=10))
            self.assertEqual(json.loads((output/'result.json').read_text())['detach'],'PASS')
            process.Detach.assert_called_once_with(False)
            process.Kill.assert_not_called()

    def test_failed_removal_tries_all_own_breakpoints_and_preserves_target(self):
        target,process=self.run_cleanup();target.BreakpointDelete.side_effect=[False,True]
        with tempfile.TemporaryDirectory() as d:
            finalize(target,process,self.breakpoints,self.report,Path(d),SimpleNamespace(eStateExited=10))
            r=json.loads((Path(d)/'result.json').read_text())
            self.assertFalse(r['cleanup_safe']);self.assertEqual(target.BreakpointDelete.call_count,2)
            process.Detach.assert_not_called();process.Kill.assert_not_called()

    def test_detach_exception_remains_unknown_but_final_journal_exists(self):
        target,process=self.run_cleanup();process.Detach.side_effect=RuntimeError('owned control failure')
        with tempfile.TemporaryDirectory() as d:
            finalize(target,process,self.breakpoints,self.report,Path(d),SimpleNamespace(eStateExited=10))
            r=json.loads((Path(d)/'result.json').read_text())
            self.assertFalse(r['cleanup_safe']);self.assertEqual(r['detach'],'UNKNOWN_CLEANUP_FAILURE')

    def test_observation_filesystem_failure_does_not_skip_cleanup(self):
        target,process=self.run_cleanup()
        with tempfile.TemporaryDirectory() as d:
            def writer(path,record):
                if path.name=='observation.json':raise OSError('owned control journal failure')
                write_once(path,record)
            with patch('lldb_collector.write_once',side_effect=writer):
                finalize(target,process,self.breakpoints,self.report,Path(d),SimpleNamespace(eStateExited=10))
            self.assertTrue(json.loads((Path(d)/'result.json').read_text())['cleanup_safe'])
            self.assertEqual(self.report['observation_journal'],'FAIL');process.Detach.assert_called_once()

    def test_invalid_process_is_not_certified_as_no_launch(self):
        target,process=self.run_cleanup();process.IsValid.return_value=False
        with tempfile.TemporaryDirectory() as d:
            finalize(target,process,self.breakpoints,self.report,Path(d),SimpleNamespace(eStateExited=10))
            self.assertFalse(self.report['cleanup_safe']);self.assertEqual(self.report['detach'],'UNKNOWN_INVALID_PROCESS')
            process.Detach.assert_not_called()


class LauncherFailureTests(unittest.TestCase):
    def test_real_owned_child_exit_retains_separate_failure_not_collector_success(self):
        # The child is a disposable Python stdin control, never LLDB or AE.
        original=subprocess.Popen;children=[]
        def child(_argv,**kwargs):
            p=original([sys.executable,'-c','import sys;sys.stdin.readline();sys.stdin.readline();raise SystemExit(23)'],**kwargs)
            children.append(p);return p
        record={'kind':'owned-fixture','source_commit':'a'*40,'collector_sha256':{'control':'b'*64}}
        try:
            with tempfile.TemporaryDirectory() as d,patch.object(launch,'read_json',return_value=record),patch.object(launch,'validate',side_effect=lambda r:r),patch.object(launch.subprocess,'Popen',side_effect=child):
                output=Path(d)/'trace'
                result=launch.drive('owned-control','digest',output)
                self.assertFalse(result['cleanup_safe']);self.assertEqual(result['debugger_exit_code'],23)
                self.assertEqual(json.loads((output/'launcher-failure.json').read_text()),result)
                self.assertFalse((output/'result.json').exists());self.assertEqual(children[0].wait(timeout=2),23)
        finally:
            for p in children:
                if not p.stdin.closed:p.stdin.close()
                p.wait(timeout=2)

    def test_zero_debugger_exit_and_uncertain_request_are_not_pass(self):
        record={'kind':'owned-fixture','source_commit':'a'*40,'collector_sha256':{}}
        r=debugger_exit(record,0,True)
        self.assertFalse(r['cleanup_safe']);self.assertEqual(r['publication'],'UNKNOWN')
        self.assertNotEqual(r['status'],'IDENTITY_OBSERVED')


if __name__=='__main__':unittest.main()
