"""Scope/refusal controls; only the explicit CLI launches an owned debugger."""
import copy
import contextlib
import io
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.resource_trace.fsref_ipc import Chain, build, ipc, compare
from experiments.resource_trace.fsref_debug import preserve_debugger


def event(phase,inv=1,parent=0,**kwargs):
    row={'sequence':0,'phase':phase,'invocation':inv,'parent':parent,'pointer':0,
         'size':0,'status':0,'same':None,'value':None,'payload_sha256':None}
    row.update(kwargs); return row


def invocation(inv=1,parent=0,same=True,allocation=100):
    return [event(1,inv,parent),event(2,inv,parent,pointer=200,size=80,status=1,same=same),
            event(3,inv,parent,pointer=300,size=4,value=42),event(4,inv,parent,pointer=400,size=8,value=23),
            event(5,inv,parent,pointer=allocation,size=23),
            event(6,inv,parent,pointer=500,size=24,value={'allocation':allocation,'actual':23,'fork':42}),
            event(7,inv,parent,pointer=600,size=23,payload_sha256='a'*64 if same else None),
            event(8,inv,parent,pointer=allocation),event(9,inv,parent)]


def nested():
    outer=invocation(); rows=outer[:2]+invocation(2,1,False)+outer[2:]+[event(10,0,0)]
    for i,row in enumerate(rows): row['sequence']=i
    return rows


class ChainTests(unittest.TestCase):
    def test_nested_twin_and_reused_allocation_address(self):
        chain=Chain()
        for row in nested(): chain.feed(row)
        self.assertTrue(chain.complete)
        self.assertTrue(chain.rows[1]['same']); self.assertFalse(chain.rows[2]['same'])

    def reject(self,rows,reason):
        chain=Chain()
        with self.assertRaisesRegex(ValueError,'^'+reason+'$'):
            for row in rows: chain.feed(row)
        self.assertEqual(chain.reason,reason)
        with self.assertRaisesRegex(ValueError,'TERMINAL_CHAIN'): chain.feed(rows[0])

    def test_twin_allocation_cannot_join_outer(self):
        rows=nested(); next(r for r in rows if r['invocation']==2 and r['phase']==5).update(invocation=1,parent=0)
        self.reject(rows,'INVOCATION_MISMATCH')

    def test_read_from_another_allocation(self):
        rows=nested(); next(r for r in rows if r['phase']==6)['value']['allocation']=999
        self.reject(rows,'SOURCE_GENERATION_MISMATCH')

    def test_recycled_fork_reference(self):
        rows=nested(); next(r for r in rows if r['phase']==6)['value']['fork']=43
        self.reject(rows,'SOURCE_GENERATION_MISMATCH')

    def test_full_64_bit_actual_count(self):
        rows=nested(); next(r for r in rows if r['phase']==6)['value']['actual']=2**32+23
        self.reject(rows,'READ_COUNT')

    def test_failed_read_not_success_from_later_copy(self):
        rows=nested(); next(r for r in rows if r['phase']==6)['status']=65535
        self.reject(rows,'CALL_FAILED')

    def test_twin_payload_capture_refused(self):
        rows=nested(); next(r for r in rows if r['phase']==7)['payload_sha256']='a'*64
        self.reject(rows,'PAYLOAD_SCOPE')

    def test_replay_refused(self):
        rows=nested(); rows.insert(2,copy.deepcopy(rows[1])); self.reject(rows,'EVENT_SEQUENCE')

    def test_missing_release_refused(self):
        rows=nested(); index=next(i for i,r in enumerate(rows) if r['phase']==8); del rows[index]
        for i,row in enumerate(rows): row['sequence']=i
        self.reject(rows,'PHASE_MISMATCH')

    def test_unwind_ends_only_active_scope(self):
        rows=invocation()[:5]+[event(11),event(10,0,0)]
        for i,row in enumerate(rows): row['sequence']=i
        chain=Chain()
        for row in rows: chain.feed(row)
        self.assertTrue(chain.complete); self.assertEqual(chain.rows[1]['phase'],11)

    def test_no_normal_read_after_unwind(self):
        rows=invocation()[:5]+[event(11),invocation()[5]]
        for i,row in enumerate(rows): row['sequence']=i
        self.reject(rows,'INVOCATION_MISMATCH')

    def test_truncated_ipc_refused_before_exec(self):
        with self.assertRaisesRegex(ValueError,'FSREF_WIRE_LENGTH'):
            compare(Path('/not-launched'),Path('/not-read'),b'x'*79,Path('/not-written'))

    def test_ambiguous_detach_keeps_debugger_input_open(self):
        class OwnedDebugger:
            pid=77
            def __init__(self): self.stdin=io.BytesIO(); self.polls=0
            def poll(self):
                if self.stdin.closed: raise AssertionError('EOF while debugger still supervised')
                if self.stdin.getvalue(): raise AssertionError('implicit quit sent')
                self.polls+=1
                return 0 if self.polls==3 else None
        child=OwnedDebugger()
        with tempfile.TemporaryDirectory(prefix='aehl-attention-model-') as directory:
            with patch('experiments.resource_trace.fsref_debug.time.sleep'),contextlib.redirect_stdout(io.StringIO()):
                result=preserve_debugger(child,Path(directory),'detach UNKNOWN')
        self.assertFalse(result['cleanup_safe']); self.assertEqual(child.polls,3)
        self.assertTrue(child.stdin.closed)


class NativeIPCTests(unittest.TestCase):
    @unittest.skipUnless(platform.system()=='Darwin' and platform.machine()=='arm64','native macOS arm64 control')
    def test_exec_emitter_controller_and_identical_twin(self):
        with tempfile.TemporaryDirectory(prefix='aehl-fsref-ipc-') as directory:
            result=ipc(build(Path(directory).resolve()/'controls'))
            self.assertEqual(result['status'],'FSREF_IPC_PASS')
            self.assertEqual(result['twin']['status'],-1420)
            self.assertEqual(result['AE_run'],'NOT_RUN')


if __name__=='__main__': unittest.main()
