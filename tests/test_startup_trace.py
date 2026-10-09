"""Identity/order/lifetime-boundary controls; synthetic input is never AE proof."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/startup_trace'))
# Use unique module names: the suite also imports stdlib/other project profiles.
spec=importlib.util.spec_from_file_location('startup_trace_core',ROOT/'experiments/startup_trace/core.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
spec=importlib.util.spec_from_file_location('startup_trace_profile',ROOT/'experiments/startup_trace/profile.py')
profile=importlib.util.module_from_spec(spec);spec.loader.exec_module(profile)


def events():
    rows=[('marker',[1,10,20,0,1]),('marker',[2,10,20,0,1]),('convert',[10]),('pipl',[30]),
          ('adapter',[30]),('spec',[30,40]),('writer',[40,50]),('index',[40,6,50]),('writer_return',[50]),
          ('reader',[1,77,60,0,1]),('match',[77]),('lookup',[40,70,50,7]),('reader',[2,77,60,0,1])]
    return [{'pid':123,'birth':456,'thread':789,'role':role,'values':dict(zip(core.FIELDS[role],values))} for role,values in rows]


class StartupTraceTests(unittest.TestCase):
    def test_complete_chain_has_no_product_or_lifetime_claim(self):
        t=core.Trace(123,456,20,60)
        for e in events():self.assertTrue(t.feed(e))
        r=t.result();self.assertEqual(r['status'],'IDENTITY_OBSERVED');self.assertEqual(r['accepted_events'],13)
        self.assertEqual((r['late_add'],r['atomic_commit'],r['complete_lifetime'],r['render_readset']),('NOT_RUN','UNKNOWN','UNKNOWN','UNKNOWN'))

    def test_other_context_interface_descriptor_ignored_with_budget(self):
        t=core.Trace(123,456,20,60)
        for e in events():
            if e['role'] in ('convert','adapter','spec','writer'):
                other=copy.deepcopy(e);field={'convert':'context','adapter':'pipl','spec':'pipl','writer':'descriptor'}[e['role']]
                other['values'][field]=999;self.assertFalse(t.feed(other))
                if e['role']=='adapter':
                    other['values'][field]=0;self.assertFalse(t.feed(other))
            t.feed(e)
        self.assertEqual(t.stops,18);self.assertEqual(len(t.events),13)
        self.assertEqual(t.result()['ignored_stops_by_role'],{'convert':1,'adapter':2,'spec':1,'writer':1})
        self.assertEqual(t.result()['resource_vs_metadata_lane'],'UNKNOWN')

    def test_adapter_is_required_before_descriptor_even_with_same_interface(self):
        t=core.Trace(123,456,20,60)
        for e in events()[:4]:t.feed(e)
        with self.assertRaisesRegex(ValueError,'unexpected'):t.feed(events()[5])
        self.assertEqual(t.result()['metadata_adapter'],'UNKNOWN')
        self.assertIsNone(t.descriptor)

    def test_adapter_partial_success_is_not_writer_or_resource_identity(self):
        t=core.Trace(123,456,20,60)
        for e in events()[:5]:t.feed(e)
        r=t.result()
        self.assertEqual(r['metadata_adapter'],'SAME_POINTER_OBSERVED')
        self.assertEqual((r['status'],r['pipl_bridge'],r['resource_vs_metadata_lane']),('INCOMPLETE','UNKNOWN','UNKNOWN'))
        self.assertIsNone(r['descriptor'])
        with self.assertRaisesRegex(ValueError,'replayed'):t.feed(events()[4])

    def test_adapter_mismatch_cannot_expand_scope_or_reset_budget(self):
        t=core.Trace(123,456,20,60)
        for e in events()[:4]:t.feed(e)
        other=copy.deepcopy(events()[4]);other['values']['pipl']=999
        with patch.object(core,'MAX_STOPS',5):
            self.assertFalse(t.feed(other))
            with self.assertRaisesRegex(ValueError,'stop budget'):t.feed(events()[4])
        self.assertEqual(t.result()['metadata_adapter'],'UNKNOWN')
        self.assertEqual(t.phase,'adapter')

    def test_changed_pid_birth_or_thread_refuses(self):
        for field in ('pid','birth','thread'):
            t=core.Trace(123,456,20,60);t.feed(events()[0]);e=events()[1];e[field]+=1
            with self.subTest(field=field),self.assertRaises(ValueError):t.feed(e)
            self.assertNotEqual(t.result()['status'],'IDENTITY_OBSERVED')

    def test_wrong_callback_main_key_lookup_root_owner_or_index_refuses(self):
        cases=[(0,'callback',99),(0,'main',0),(1,'status',1),(3,'pipl',0),(5,'descriptor',0),
               (6,'root',0),(7,'index',8192),(8,'root',99),(9,'function',99),(9,'main',0),
               (10,'key',99),(11,'root',99),(11,'descriptor',99),(11,'owner',0),(11,'index',6),(12,'status',1),(12,'key',99)]
        for index,field,value in cases:
            t=core.Trace(123,456,20,60);rows=events();rows[index]['values'][field]=value
            for e in rows[:index]:t.feed(e)
            with self.subTest(index=index,field=field),self.assertRaises(ValueError):t.feed(rows[index])
            self.assertNotEqual(t.result()['status'],'IDENTITY_OBSERVED')

    def test_missing_stage_reorder_and_replay_refuse(self):
        t=core.Trace(123,456,20,60)
        with self.assertRaises(ValueError):t.feed(events()[4])
        t.feed(events()[0])
        with self.assertRaises(ValueError):t.feed(events()[0])
        self.assertEqual(t.result()['status'],'INCOMPLETE')

    def test_payload_exhaustion_cannot_set_complete(self):
        t=core.Trace(123,456,20,60)
        for e in events()[:-1]:t.feed(e)
        with patch.object(core,'MAX_BYTES',t.size),self.assertRaisesRegex(ValueError,'payload'):t.feed(events()[-1])
        self.assertEqual(t.phase,'reader-end')

    def test_ignored_events_exhaust_stop_budget(self):
        t=core.Trace(123,456,20,60)
        for e in events()[:2]:t.feed(e)
        other=events()[2];other['values']['context']=999
        with patch.object(core,'MAX_STOPS',3):
            self.assertFalse(t.feed(other))
            with self.assertRaisesRegex(ValueError,'stop budget'):t.feed(other)

    def test_unsigned_values_and_exact_fields(self):
        for value in (-1,2**64,True,'1'):
            e=events()[0];e['values']['stage']=value
            with self.subTest(value=value),self.assertRaises(ValueError):core.Trace(123,456,20,60).feed(e)
        e=events()[0];e['extra']='unbounded'
        with self.assertRaises(ValueError):core.Trace(123,456,20,60).feed(e)

    def test_digest_duplicate_mode_and_symlink_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve()/'p.json';p.write_text('{"x":1}');p.chmod(0o600)
            digest=hashlib.sha256(p.read_bytes()).hexdigest();self.assertEqual(profile.read_json(p,digest),{'x':1})
            with self.assertRaisesRegex(ValueError,'digest'):profile.read_json(p,'0'*64)
            p.chmod(0o644)
            with self.assertRaisesRegex(ValueError,'ownership'):profile.read_json(p,digest)
            p.chmod(0o600);q=p.with_name('link');q.symlink_to(p)
            with self.assertRaisesRegex(ValueError,'symlink'):profile.read_json(q,digest)
            p.write_text('{"x":1,"x":2}')
            with self.assertRaisesRegex(ValueError,'duplicate'):profile.read_json(p,hashlib.sha256(p.read_bytes()).hexdigest())

    def test_transport_refusal_prevents_ae_admission(self):
        proof={'kind':'owned-fixture','status':'IDENTITY_OBSERVED','phase':'complete','cleanup_safe':True,
               'accepted_events':13,'stops':18,'metadata_adapter':'SAME_POINTER_OBSERVED','collector_sha256':profile.collector_hashes(),'source_commit':'a'*40,
               'owned_process':{'executable':str(ROOT/'build-ae-hot-loader/trace-fixture-own/aehl-trace-fixture')}}
        candidate={'source':{'commit':'a'*40}}
        profile.transport_admission(proof,candidate)
        for field,value in [('status','UNKNOWN'),('cleanup_safe',False),('accepted_events',12),('stops',15),('metadata_adapter','UNKNOWN'),
                            ('source_commit','b'*40),('collector_sha256',{}),('kind','ae-owned-startup')]:
            bad=copy.deepcopy(proof);bad[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'transport proof'):profile.transport_admission(bad,candidate)
        proof['owned_process']['executable']='/Applications/Other.app/Contents/MacOS/Other'
        with self.assertRaisesRegex(ValueError,'outside fixture'):profile.transport_admission(proof,candidate)

    def test_journal_publication_is_complete_and_never_replaces(self):
        import os
        from lldb_collector import write_once
        original=os.link
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'result.json';record={'cleanup_safe':True,'status':'fixture'}
            def publish(source,target,**kwargs):
                self.assertFalse(Path(target).exists())
                self.assertEqual(json.loads(Path(source).read_text()),record)
                return original(source,target,**kwargs)
            with patch('lldb_collector.os.link',side_effect=publish):write_once(path,record)
            self.assertEqual(json.loads(path.read_text()),record)
            self.assertEqual(path.stat().st_mode&0o777,0o600)
            self.assertFalse(path.with_name('result.json.pending').exists())
            with self.assertRaises(FileExistsError):write_once(path,{'cleanup_safe':False})
            self.assertEqual(json.loads(path.read_text()),record)

    def test_failed_journal_publication_preserves_pending_without_final(self):
        from lldb_collector import write_once
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'result.json'
            with patch('lldb_collector.os.link',side_effect=OSError('control refusal')),self.assertRaises(OSError):
                write_once(path,{'cleanup_safe':False})
            self.assertFalse(path.exists());self.assertTrue(path.with_name('result.json.pending').is_file())


class StopMetadataTests(unittest.TestCase):
    def snapshot(self):
        return {'state':5,'state_after':5,'stop_id':9,'stop_id_after':9,'total_threads':1,
                'threads':[{'index':0,'id':77,'reason':3,'none':False,'breakpoint':True,
                            'reason_data_count':2,'breakpoint_id':4,'location_id':1}]}

    def test_isolated_owned_breakpoint_selects_exact_proven_thread(self):
        from stops import select
        self.assertEqual(select(self.snapshot(),5,{4:'spec'},77),(0,'spec'))
        with self.assertRaisesRegex(ValueError,'main thread'):select(self.snapshot(),5,{4:'spec'},78)
        with self.assertRaisesRegex(ValueError,'unowned'):select(self.snapshot(),5,{5:'writer'})

    def test_zero_multiple_and_mixed_stop_reasons_refuse(self):
        from stops import select
        for kind in ('none','multiple','exception'):
            r=self.snapshot()
            if kind=='none':r['threads'][0].update(none=True,breakpoint=False)
            else:
                other=copy.deepcopy(r['threads'][0]);other['index']=1;other['id']=78
                if kind=='exception':other.update(reason=6,breakpoint=False)
                r['threads'].append(other);r['total_threads']=2
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'isolated'):select(r,5,{4:'spec'})

    def test_transient_state_or_stop_id_never_selects_a_frame(self):
        from stops import select
        for field,value in (('state_after',6),('stop_id_after',10)):
            r=self.snapshot();r[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'changed'):select(r,5,{4:'spec'})

    def test_ambiguous_breakpoint_shape_and_incomplete_inventory_refuse(self):
        from stops import select
        r=self.snapshot();r['threads'][0]['reason_data_count']=4
        with self.assertRaisesRegex(ValueError,'shape'):select(r,5,{4:'spec'})
        r=self.snapshot();r['total_threads']=2
        with self.assertRaisesRegex(ValueError,'inventory'):select(r,5,{4:'spec'})

    def test_launch_stop_never_continues_unknown_signal_or_exception(self):
        from stops import initial
        from types import SimpleNamespace
        api=SimpleNamespace(eStateStopped=5,eStopReasonExec=7,eStopReasonSignal=5)
        r=self.snapshot();r['threads'][0].update(reason=5,breakpoint=False,signal_number=17,reason_data_count=1)
        initial(r,api,17)
        for reason,signal_number in ((5,11),(6,17),(0,17)):
            r['threads'][0].update(reason=reason,signal_number=signal_number)
            with self.assertRaisesRegex(ValueError,'expected launch'):initial(r,api,17)

    def test_capture_is_bounded_and_does_not_request_frames(self):
        from stops import capture,select
        from types import SimpleNamespace
        api=SimpleNamespace(eStopReasonBreakpoint=3,eStopReasonNone=0,eStopReasonSignal=5)
        class Thread:
            def GetStopReason(self):return 0
            def GetStopReasonDataCount(self):return 0
            def GetThreadID(self):return 77
        class Process:
            visits=0
            def GetState(self):return 5
            def GetStopID(self):return 9
            def GetNumThreads(self):return 257
            def GetThreadAtIndex(self,index):self.visits+=1;return Thread()
        p=Process();r=capture(p,api);self.assertEqual(p.visits,8)
        with self.assertRaisesRegex(ValueError,'bound'):select(r,5,{4:'spec'})


if __name__=='__main__':unittest.main()
