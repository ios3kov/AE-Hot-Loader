"""Resource copy/ownership/provenance refusals plus a real owned native model.

Native model evidence is intentionally rejected by the existing AE transport gate.
It does not use Adobe layouts, memory, modules, suites or registration calls.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.resource_trace import core, fixture


def profile():
    name = 'AEHLR0123456789ab'
    return {'schema': 'AEHL-RESOURCE-FIXTURE-1', 'kind': 'owned-fixture',
            'run_id': 'a' * 32, 'pid': 123, 'thread': 1, 'origin': 'bundle-resource',
            'module_sha256': 'b' * 64,
            'payload_sha256': hashlib.sha256(b'eMNA:' + name.encode() + b'\0').hexdigest(), 'match_name': name}


def events():
    p = profile(); n = p['match_name']
    values = [
        (10, 'bundle-resource', p['module_sha256'], (b'eMNA:' + n.encode() + b'\0').hex()),
        (10, 20, 21, 22, n), (10, 20, 22, n),
        (10, 20, 30, 31, 32, 22, 33, n), (30, 31, 32, 40, 33, n),
        (30, 40, 6), (40, 0), (709, 50), (30, 31, 32, 40, 7), (709, 50, 0, 60, n)]
    return [{'run_id': p['run_id'], 'pid': p['pid'], 'thread': p['thread'], 'sequence': i,
             'role': role, 'values': dict(zip(core.FIELDS[role], row))}
            for i, (role, row) in enumerate(zip(core.ROLES, values))]


class ResourceTraceTests(unittest.TestCase):
    def test_copy_bridge_uses_different_storage_and_keeps_unknowns(self):
        t = core.Trace(profile())
        for row in events(): t.feed(row)
        r = t.result()
        self.assertEqual(r['status'], 'FIXTURE_CHAIN_OBSERVED')
        self.assertEqual(r['accepted_events'], 10)
        self.assertEqual(r['transport_admission'], 'BLOCKED')
        self.assertEqual(r['AE_observation'], 'NOT_RUN')
        for key in ('complete_lifetime', 'atomic_commit', 'render_readset', 'failure_recovery'):
            self.assertEqual(r[key], 'UNKNOWN')

    def test_cache_cannot_claim_current_resource_read(self):
        p = profile(); p['origin'] = 'cache'; rows = events(); rows[0]['values']['origin'] = 'cache'
        t = core.Trace(p)
        for row in rows: t.feed(row)
        self.assertEqual(t.result()['current_resource_read'], 'NOT_ESTABLISHED')

    def test_legacy_resource_is_distinct(self):
        p = profile(); p['origin'] = 'legacy-resource'; rows = events(); rows[0]['values']['origin'] = 'legacy-resource'
        t = core.Trace(p)
        for row in rows: t.feed(row)
        self.assertEqual(t.result()['origin'], 'legacy-resource')

    def test_ae_profiles_are_not_admitted(self):
        p = profile(); p['kind'] = 'ae-owned-startup'
        with self.assertRaisesRegex(ValueError, 'not admitted'): core.Trace(p)
        p = profile(); p['schema'] = 'AEHL-RESOURCE-AE-1'
        with self.assertRaisesRegex(ValueError, 'not admitted'): core.Trace(p)

    def test_input_profile_is_copied(self):
        p = profile(); t = core.Trace(p); p['pid'] = 999
        t.feed(events()[0]); self.assertEqual(t.profile['pid'], 123)

    def test_identity_and_order_are_terminal(self):
        for field, value in (('pid', 124), ('pid', True), ('thread', 2), ('run_id', 'c' * 32),
                             ('sequence', True), ('sequence', 1), ('role', 'pipl')):
            t = core.Trace(profile()); row = events()[0]; row[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError): t.feed(row)
                with self.assertRaisesRegex(ValueError, 'already refused'): t.feed(events()[0])
                self.assertEqual(t.result()['status'], 'REFUSED')

    def test_all_object_transfers_and_names_are_checked(self):
        cases = [(0,'module_sha256','c'*64), (0,'origin','cache'), (0,'payload_hex','00'),
                 (1,'call',11), (2,'pipl',99), (2,'source_storage',99),
                 (3,'source_storage',99), (3,'target_storage',22), (3,'name','AEHLRffffffffffff'),
                 (4,'descriptor',99), (4,'descriptor_owner',99), (4,'routine_owner',99),
                 (4,'target_storage',99), (5,'root',99), (5,'descriptor',99), (5,'index',8192),
                 (6,'root',99), (6,'status',1), (7,'key',77), (8,'descriptor',99),
                 (8,'descriptor_owner',99), (8,'routine_owner',99), (8,'root',99), (8,'index',6),
                 (9,'key',77), (9,'function',99), (9,'status',1), (9,'output_storage',33),
                 (9,'name','AEHLRffffffffffff')]
        for i, field, value in cases:
            rows = events(); rows[i]['values'][field] = value; t = core.Trace(profile())
            for row in rows[:i]: t.feed(row)
            with self.subTest(i=i, field=field), self.assertRaises(ValueError): t.feed(rows[i])
            self.assertEqual(t.result()['status'], 'REFUSED')
            self.assertEqual(t.position, i)

    def test_value_types_fields_and_bounds_refuse(self):
        for value in (True, -1, 2**64, '1', None, []):
            t=core.Trace(profile()); row=events()[0]; row['values']['call']=value
            with self.subTest(value=value), self.assertRaises(ValueError): t.feed(row)
        for value in ('0' * 258, '0', 'zz', 'AB'):
            t=core.Trace(profile()); row=events()[0]; row['values']['payload_hex']=value
            with self.subTest(value=value), self.assertRaises(ValueError): t.feed(row)
        row=events()[0]; row['values']['extra']=1
        with self.assertRaises(ValueError): core.Trace(profile()).feed(row)

    def test_missing_event_cannot_complete_and_replay_refuses(self):
        t=core.Trace(profile())
        for row in events()[:-1]: t.feed(row)
        self.assertEqual(t.result()['status'], 'INCOMPLETE')
        t.feed(events()[-1])
        with self.assertRaises(ValueError): t.feed(events()[-1])
        self.assertEqual(t.result()['status'], 'REFUSED')

    def test_accepted_inputs_cannot_be_mutated(self):
        row=events()[0]; t=core.Trace(profile()); t.feed(row); row['values']['call']=999
        self.assertEqual(t.events[0]['values']['call'], 10)

    def test_limits_refuse_before_advancing(self):
        for limit in ('MAX_BYTES', 'MAX_EVENTS'):
            t=core.Trace(profile())
            with patch.object(core, limit, 0), self.assertRaises(ValueError): t.feed(events()[0])
            self.assertEqual(t.position, 0); self.assertEqual(t.result()['status'], 'REFUSED')


@unittest.skipUnless(shutil.which('clang++'), 'native fixture compiler unavailable; no transport proof')
class ResourceNativeFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aehl-resource-contract-')
        cls.directory = Path(cls.temp.name).resolve()
        cls.target = fixture.build(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_real_owned_copy_writer_reader_and_three_origins(self):
        for origin in core.ORIGINS:
            with self.subTest(origin=origin):
                receipt=fixture.run(self.target, self.directory, origin)
                self.assertEqual(receipt['result']['status'], 'FIXTURE_CHAIN_OBSERVED')
                self.assertTrue(receipt['process_exited']); self.assertEqual(receipt['exit_code'], 0)
                self.assertEqual(receipt['debugger'], 'NOT_RUN')
                self.assertNotEqual(receipt['events'][3]['values']['source_storage'], receipt['events'][3]['values']['target_storage'])
                self.assertEqual(receipt['result']['transport_admission'], 'BLOCKED')

    def test_real_failure_alias_owner_and_output_controls(self):
        for fault in ('alias', 'writer-failure', 'wrong-owner', 'read-name'):
            with self.subTest(fault=fault):
                receipt=fixture.run(self.target, self.directory, fault=fault)
                self.assertEqual(receipt['result']['status'], 'REFUSED')
                self.assertTrue(receipt['process_exited'])
                self.assertEqual(receipt['result']['failure_recovery'], 'UNKNOWN')

    def test_unknown_executable_refused_before_launch(self):
        with tempfile.TemporaryDirectory(prefix='aehl-other-fixture-') as d:
            other=Path(d).resolve()/'aehl-resource-fixture'; shutil.copy2(self.target, other)
            with patch.object(fixture.subprocess, 'Popen') as launch:
                with self.assertRaisesRegex(ValueError, 'not built here'): fixture.run(other, other.parent)
                launch.assert_not_called()

    def test_changed_registered_binary_refused_before_launch(self):
        with tempfile.TemporaryDirectory(prefix='aehl-changed-resource-') as d:
            directory=Path(d).resolve(); target=fixture.build(directory)
            with target.open('ab') as file: file.write(b'changed')
            with patch.object(fixture.subprocess, 'Popen') as launch:
                with self.assertRaisesRegex(ValueError, 'has changed'): fixture.run(target, directory)
                launch.assert_not_called()

    def test_timeout_preserves_identity_and_does_not_kill(self):
        from subprocess import TimeoutExpired
        with patch.object(fixture.subprocess, 'Popen') as launch:
            process=launch.return_value; process.pid=12345
            process.communicate.side_effect=TimeoutExpired('owned fixture', 10)
            with self.assertRaises(TimeoutExpired): fixture.run(self.target, self.directory)
            process.kill.assert_not_called(); process.terminate.assert_not_called()
        pending=list(self.directory.glob('*-pending.json'))
        self.assertEqual(len(pending), 1)
        record=json.loads(pending[0].read_text())
        self.assertEqual(record['status'], 'MANUAL_ATTENTION')
        self.assertEqual(record['pid'], 12345)

    def test_fixture_does_not_satisfy_existing_debugger_admission(self):
        import importlib.util
        root=Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root/'experiments/startup_trace'))
        spec=importlib.util.spec_from_file_location('resource_existing_profile', root/'experiments/startup_trace/profile.py')
        prior=importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
        receipt=fixture.run(self.target, self.directory)
        with self.assertRaisesRegex(ValueError, 'transport proof'):
            prior.transport_admission(receipt, {'source': {'commit': 'a'*40}})
