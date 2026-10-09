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
          ('spec',[30,40]),('writer',[40,50]),('index',[40,6,50]),('writer_return',[50]),
          ('reader',[1,77,60,0,1]),('match',[77]),('lookup',[40,70,50,7]),('reader',[2,77,60,0,1])]
    return [{'pid':123,'birth':456,'thread':789,'role':role,'values':dict(zip(core.FIELDS[role],values))} for role,values in rows]


class StartupTraceTests(unittest.TestCase):
    def test_complete_chain_has_no_product_or_lifetime_claim(self):
        t=core.Trace(123,456,20,60)
        for e in events():self.assertTrue(t.feed(e))
        r=t.result();self.assertEqual(r['status'],'IDENTITY_OBSERVED');self.assertEqual(r['accepted_events'],12)
        self.assertEqual((r['late_add'],r['atomic_commit'],r['complete_lifetime'],r['render_readset']),('NOT_RUN','UNKNOWN','UNKNOWN','UNKNOWN'))

    def test_other_context_interface_descriptor_ignored_with_budget(self):
        t=core.Trace(123,456,20,60)
        for e in events():
            if e['role'] in ('convert','spec','writer'):
                other=copy.deepcopy(e);field={'convert':'context','spec':'pipl','writer':'descriptor'}[e['role']]
                other['values'][field]=999;self.assertFalse(t.feed(other))
            t.feed(e)
        self.assertEqual(t.stops,15);self.assertEqual(len(t.events),12)

    def test_changed_pid_birth_or_thread_refuses(self):
        for field in ('pid','birth','thread'):
            t=core.Trace(123,456,20,60);t.feed(events()[0]);e=events()[1];e[field]+=1
            with self.subTest(field=field),self.assertRaises(ValueError):t.feed(e)
            self.assertNotEqual(t.result()['status'],'IDENTITY_OBSERVED')

    def test_wrong_callback_main_key_lookup_root_owner_or_index_refuses(self):
        cases=[(0,'callback',99),(0,'main',0),(1,'status',1),(3,'pipl',0),(4,'descriptor',0),
               (5,'root',0),(6,'index',8192),(7,'root',99),(8,'function',99),(8,'main',0),
               (9,'key',99),(10,'root',99),(10,'descriptor',99),(10,'owner',0),(10,'index',6),(11,'status',1),(11,'key',99)]
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
               'accepted_events':12,'stops':15,'collector_sha256':profile.collector_hashes(),'source_commit':'a'*40,
               'owned_process':{'executable':str(ROOT/'build-ae-hot-loader/trace-fixture-own/aehl-trace-fixture')}}
        candidate={'source':{'commit':'a'*40}}
        profile.transport_admission(proof,candidate)
        for field,value in [('status','UNKNOWN'),('cleanup_safe',False),('accepted_events',11),('stops',14),
                            ('source_commit','b'*40),('collector_sha256',{}),('kind','ae-owned-startup')]:
            bad=copy.deepcopy(proof);bad[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'transport proof'):profile.transport_admission(bad,candidate)
        proof['owned_process']['executable']='/Applications/Other.app/Contents/MacOS/Other'
        with self.assertRaisesRegex(ValueError,'outside fixture'):profile.transport_admission(proof,candidate)


if __name__=='__main__':unittest.main()
