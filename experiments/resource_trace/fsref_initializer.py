"""Owned initializer observation and return-window MODEL. No debugger or AE admission."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.resource_trace.core import need
from experiments.resource_trace.fsref_ipc import compare, execute, sources as ipc_sources
from experiments.startup_trace.lldb_collector import write_once


class ReturnWindow:
    """Only source-labelled owned invocation metadata; cannot infer a live AE frame."""
    def __init__(self):
        self.last=0; self.active=None; self.ready=None; self.captured=False; self.reason=None

    def _check(self,condition,reason):
        need(self.reason is None,'TERMINAL_WINDOW')
        if not condition:
            self.reason=reason
            raise ValueError(reason)

    def enter(self,generation,pointer):
        self._check(type(generation) is int and generation>self.last and
                    type(pointer) is int and 0<pointer<2**64 and self.active is None,'ENTRY_MISMATCH')
        self.last=generation; self.active=(generation,pointer); self.ready=None; self.captured=False

    def returned(self,generation,pointer,ready):
        self._check(self.active is not None,'MISSING_ENTRY')
        self._check(self.active==(generation,pointer),'STALE_INVOCATION')
        self._check(self.ready is None and type(ready) is bool,'RETURN_MISMATCH')
        self.ready=ready

    def capture(self,generation,pointer):
        self._check(self.active is not None,'NO_ACTIVE_INVOCATION')
        self._check(self.active==(generation,pointer),'STALE_INVOCATION')
        self._check(self.ready is not None,'MISSING_NORMAL_RETURN')
        self._check(self.ready,'CALL_FAILED')
        self._check(not self.captured,'ALREADY_CAPTURED')
        self.captured=True

    def close(self,generation,pointer):
        self._check(self.active==(generation,pointer),'EXIT_MISMATCH')
        self.active=None; self.ready=None; self.captured=False


def pins():
    files=[Path(__file__),Path(__file__).with_suffix('.cpp'),ROOT/'tests/test_fsref_initializer.py']
    return {**ipc_sources(),**{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}


def expected_pattern(index):
    if index==0: return bytes(80)
    if index==1: return bytes([0xa5])*80
    if index==2: return bytes([0x55,0xaa])*40
    need(index in (3,4),'PREFILL_INDEX')
    state=0x12345678 if index==3 else 0x98765432; out=[]
    for _ in range(80):
        state^=(state<<13)&0xffffffff; state^=state>>17; state^=(state<<5)&0xffffffff
        out.append(state&255)
    return bytes(out)


def inspect(rows):
    need(type(rows) is list and len(rows)==44,'NATIVE_ROW_COUNT')
    matrix=rows[:40]; groups={}; refusals=[]
    fields={'id','kind','alignment','repeat','prefill','generation','pointer','ready','guards',
            'before','after','compare_a','compare_b'}
    expected_order=[(alignment,repeat,fill,kind) for alignment in (0,8)
                    for repeat in range(2) for fill in range(5) for kind in ('A','B')]
    for i,row in enumerate(rows):
        need(type(row) is dict and set(row)==fields,'NATIVE_ROW_SHAPE')
        need(all(type(row[k]) is int for k in ('id','alignment','repeat','prefill','generation','pointer')),
             'NATIVE_ROW_VALUES')
        need(row['id']==i and row['generation']==i+1 and 0<row['pointer']<2**64 and
             type(row['ready']) is bool and row['guards'] is True,'NATIVE_SCOPE')
        need(all(type(row[k]) is str and re.fullmatch('[0-9a-f]{160}',row[k])
                 for k in ('before','after')),'NATIVE_SNAPSHOT')
        need(row['pointer']%16==row['alignment'],'ALIGNMENT_CLASS')
        if i<40:
            need((row['alignment'],row['repeat'],row['prefill'],row['kind'])==expected_order[i],
                 'MATRIX_COVERAGE')
            need(bytes.fromhex(row['before'])==expected_pattern(row['prefill']),'PREFILL_CONTENT')
            need(all(type(row[key]) is int for key in ('compare_a','compare_b')),'COMPARE_VALUES')
            need(row['ready'] and (row['compare_a'],row['compare_b'])==
                 ((0,-1420) if row['kind']=='A' else (-1420,0)),'SEMANTIC_IDENTITY')
            groups.setdefault((row['kind'],row['alignment']),[]).append(bytes.fromhex(row['after']))
        else:
            step=i-40; need(row['kind']==('missing' if step==2 else 'reuse_A') and
                          row['alignment']==8 and row['repeat']==step and row['prefill']==5,'REUSE_COVERAGE')
            need(row['pointer']==rows[40]['pointer'],'REUSE_ADDRESS')
            if step==2:
                need(not row['ready'] and row['compare_a'] is None and row['compare_b'] is None,
                     'MISSING_FILE_CONTROL')
            else: need(row['ready'] and all(type(row[key]) is int for key in ('compare_a','compare_b')) and
                       (row['compare_a'],row['compare_b'])==(0,-1420),'REUSE_IDENTITY')
    need(len({row['before'] for row in matrix if row['kind']=='A' and row['alignment']==0})==5,
         'PREFILL_DISTINCT')
    # No requirement that opaque representations be canonical or equal across valid calls.
    variation={f'{kind}/{alignment}':[i for i in range(80) if len({raw[i] for raw in values})>1]
               for (kind,alignment),values in groups.items()}
    failed=rows[42]
    # Each deliberate replay below has one independent expected failure; errors cannot mask each other.
    def rejected(name,setup,action,reason):
        window=ReturnWindow(); setup(window)
        try: action(window)
        except ValueError as error:
            need(str(error)==reason,'UNEXPECTED_MODEL_REFUSAL')
        else: raise ValueError('MODEL_ACCEPTED_STALE_OUTPUT')
        refusals.append({'case':name,'reason':reason,'scope':'MODEL_REPLAY_ONLY'})
    a,b=rows[40],rows[41]; p=a['pointer']; ga=a['generation']; gb=b['generation']
    def current(window):
        window.enter(ga,p); window.returned(ga,p,True); window.close(ga,p)
        window.enter(gb,p); window.returned(gb,p,True)
    rejected('same_address_same_A_old_generation',current,lambda w:w.capture(ga,p),'STALE_INVOCATION')
    rejected('return_without_entry',lambda w:None,lambda w:w.returned(ga,p,True),'MISSING_ENTRY')
    def failure(window):
        window.enter(failed['generation'],p); window.returned(failed['generation'],p,False)
    rejected('false_even_if_old_bytes_valid',failure,lambda w:w.capture(failed['generation'],p),'CALL_FAILED')
    def closed(window):
        window.enter(ga,p); window.returned(ga,p,True); window.close(ga,p)
    rejected('capture_after_close',closed,lambda w:w.capture(ga,p),'NO_ACTIVE_INVOCATION')
    def duplicate(window):
        window.enter(ga,p); window.returned(ga,p,True); window.capture(ga,p)
    rejected('duplicate_capture',duplicate,lambda w:w.capture(ga,p),'ALREADY_CAPTURED')
    positive=ReturnWindow()
    for row in rows[40:]:
        g,p=row['generation'],row['pointer']; positive.enter(g,p); positive.returned(g,p,row['ready'])
        if row['ready']: positive.capture(g,p)
        positive.close(g,p)
    return {'matrix_calls':len(matrix),'successful_reuses':3,'same_address':True,
            'representation_variation_indices':variation,
            'all_tested_outputs_identical_within_group':not any(variation.values()),
            'failed_call_retains_prefill':failed['after']==failed['before'],
            'model_refusals':refusals,'full_write_coverage':'UNKNOWN','AE_output_admission':'BLOCKED'}


def run(output,sanitizers=False):
    need(platform.system()=='Darwin' and platform.machine()=='arm64','native macOS arm64 only')
    need(type(sanitizers) is bool,'instrumentation choice')
    output=Path(output).absolute()
    need(not any(p.is_symlink() for p in (output,*output.parents)),'owned output path')
    output.mkdir(mode=0o700,parents=True,exist_ok=False)
    before=pins(); compiled=[]
    write_once(output/'source-before.json',{'source_commit':subprocess.check_output(
               ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sources':before,
               'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT))})
    for stem,source in [('aehl-fsref-initializer',Path(__file__).with_suffix('.cpp')),
                        ('aehl-fsref-comparator',Path(__file__).with_name('fsref_ipc.cpp'))]:
        binary=output/stem
        command=['clang++','-std=c++17','-arch','arm64','-O0','-Wall','-Wextra','-Werror',str(source),
                 '-framework','CoreFoundation','-framework','CoreServices','-o',str(binary)]
        if sanitizers: command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
        result=subprocess.run(command,capture_output=True,timeout=60)
        (output/(stem+'.compiler.stdout')).write_bytes(result.stdout)
        (output/(stem+'.compiler.stderr')).write_bytes(result.stderr)
        need(result.returncode==0,'NATIVE_BUILD')
        from experiments.startup_trace.image import Image
        img=Image(binary)
        compiled.append({'path':str(binary),'sha256':img.sha256,'uuid':img.uuid,'command':command})
    write_once(output/'build.json',{'sources':before,'binaries':compiled,
                                  'sanitizers':['ASan','UBSan'] if sanitizers else []})
    need(pins()==before,'SOURCE_CHANGED')
    payload=b'eMNA:AEHLR'+uuid.uuid4().hex[:12].encode()+b'\0'
    a,b,missing=(output/leaf for leaf in ('A.resource','B.resource','MISSING.resource'))
    for path in (a,b):
        with os.fdopen(os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600),'wb') as stream:
            stream.write(payload)
    need(not missing.exists() and (a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino),
         'TWIN_OR_MISSING_CONTROL')
    result=execute(Path(compiled[0]['path']),[a,b,missing],output)
    (output/'native.stdout').write_bytes(result['stdout']); (output/'native.stderr').write_bytes(result['stderr'])
    need(result['code']==0 and result['stderr']==b'','NATIVE_RUNTIME')
    native=json.loads(result['stdout']); need(set(native)=={'pid','images','rows'} and native['pid']==result['pid'],
                                            'NATIVE_IDENTITY')
    need(set(native['images'])=={'initializer','comparator'} and all(
        type(row) is dict and set(row)=={'path','uuid'} and row['path'].startswith('/System/Library/') and
        re.fullmatch('[0-9a-f]{32}',row['uuid']) for row in native['images'].values()),'SYSTEM_IMAGE_IDENTITY')
    observed=inspect(native['rows']); comparisons=[]; ordered=[]
    comparator=Path(compiled[1]['path'])
    for row in native['rows']:
        if row['ready']:
            raw=bytes.fromhex(row['after']); resource=b if row['kind']=='B' else a
            accepted=compare(comparator,resource,raw,output)
            twin=compare(comparator,a if resource==b else b,raw,output)
            write_once(output/('compare-%02d.json'%row['id']),{'id':row['id'],'kind':row['kind'],
                       'accepted':accepted,'twin':twin})
            comparisons.append({'id':row['id'],'accepted':accepted,'twin':twin})
            for order in ('AB','BA'):
                pair_result=execute(Path(compiled[0]['path']),['compare_AB',a,b,order],output,raw)
                (output/('ordered-%02d-%s.stdout'%(row['id'],order))).write_bytes(pair_result['stdout'])
                (output/('ordered-%02d-%s.stderr'%(row['id'],order))).write_bytes(pair_result['stderr'])
                need(pair_result['code']==0 and pair_result['stderr']==b'','ORDERED_COMPARE_RUNTIME')
                pair=json.loads(pair_result['stdout'])
                need(set(pair)=={'pid','order','compare_a','compare_b','images'} and
                     pair['pid']==pair_result['pid'] and pair['order']==order and
                     pair['images']==native['images'] and all(type(pair[key]) is int and
                     pair[key] in (0,-1420) for key in ('compare_a','compare_b')),'ORDERED_COMPARE_SHAPE')
                wanted=(0,-1420) if row['kind']!='B' else (-1420,0)
                ordered.append({'id':row['id'],'kind':row['kind'],'result':pair,
                                'identity_correct':(pair['compare_a'],pair['compare_b'])==wanted})
    failed=native['rows'][42]
    stale=None
    if failed['before']==failed['after']:
        # Known prior valid A representation only; never feed arbitrary failed output to File Manager.
        stale=compare(comparator,a,bytes.fromhex(failed['after']),output)
        need(stale['same'],'KNOWN_STALE_REF_COMPARE')
    need(pins()==before and all(hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
                              for item in compiled) and a.read_bytes()==b.read_bytes()==payload and
         not missing.exists(),'ARTIFACT_CHANGED')
    receipt={'status':'OWNED_INITIALIZER_OBSERVED','source_commit':subprocess.check_output(
             ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
             'sources':before,'binaries':compiled,'environment':platform.platform(),
             'sanitizers':['ASan','UBSan'] if sanitizers else [],'pid':native['pid'],
             'system_images':native['images'],'file_identity':{
                 p.name:{'device':p.stat().st_dev,'inode':p.stat().st_ino,'sha256':hashlib.sha256(payload).hexdigest()}
                 for p in (a,b)},'observation':observed,'comparisons':comparisons,
             'ordered_comparisons':ordered,
             'cross_exec_identity':{'status':'OBSERVED_MISMATCH' if any(not x['identity_correct'] for x in ordered)
                                    or any(not x['accepted']['same'] or x['twin']['same'] for x in comparisons)
                                    else 'BOUNDED_OBSERVATION_PASS',
                                    'ordered_mismatches':sum(not x['identity_correct'] for x in ordered),
                                    'legacy_wrong_twin_matches':sum(x['twin']['same'] for x in comparisons),
                                    'AE_source_selector':'BLOCKED'},
             'known_stale_compare':stale,'AE_run':'NOT_RUN','AE_capture':'BLOCKED',
             'entry_return_observation':'NOT_RUN; return-window checks are models'}
    write_once(output/'receipt.json',receipt)
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path); parser.add_argument('--sanitizers',action='store_true')
    args=parser.parse_args()
    result=run(args.output,args.sanitizers)
    print(json.dumps({key:result[key] for key in ('status','source_commit','dirty','pid','observation','AE_run')},indent=2))
