"""Exec-based owned FSRef IPC and nested producer event validation. Never AE."""
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
from experiments.startup_trace.lldb_collector import write_once


def execute(binary, arguments, output, wire=None):
    """Only a pinned owned executable. Timeout preserves it, never implicitly kills."""
    child=subprocess.Popen([str(binary),*map(str,arguments)],stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try: stdout,stderr=child.communicate(wire,timeout=12)
    except subprocess.TimeoutExpired as error:
        write_once(output/'attention.json',{'pid':child.pid,'status':'ATTENTION','executable':str(binary)})
        raise ValueError('owned FSRef process retained') from error
    return {'pid':child.pid,'code':child.returncode,'stdout':stdout,'stderr':stderr}


def compare(binary, resource, raw, output):
    need(type(raw) is bytes and len(raw)==80,'FSREF_WIRE_LENGTH')
    result=execute(binary,['compare',resource,resource],output,raw)
    need(result['code']==0 and result['stderr']==b'','FSREF_COMPARE_INCONCLUSIVE')
    row=json.loads(result['stdout'])
    need(set(row)=={'pid','status','same'} and row['pid']==result['pid'] and
         type(row['same']) is bool and type(row['status']) is int and
         ((row['status']==0 and row['same']) or (row['status']==-1420 and not row['same'])),
         'FSREF_COMPARE_INCONCLUSIVE')
    return row


def sources():
    paths=[Path(__file__),Path(__file__).with_suffix('.cpp'),Path(__file__).with_name('fsref_debug.py')]
    from experiments.resource_trace.transport_profile import hashes
    return {**hashes(),**{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def build(output,sanitizers=False):
    need(platform.system()=='Darwin' and platform.machine()=='arm64','native macOS arm64 control')
    need(type(sanitizers) is bool,'instrumentation choice')
    output=Path(output).absolute()
    need(not any(p.is_symlink() for p in (output,*output.parents)),'owned output path')
    output.mkdir(mode=0o700,parents=True,exist_ok=False)
    before=sources(); run=uuid.uuid4().hex
    binary=output/'aehl-fsref-ipc'
    command=['clang++','-std=c++17','-arch','arm64','-O0','-Wall','-Wextra','-Werror',
             str(Path(__file__).with_suffix('.cpp')),'-framework','CoreFoundation',
             '-framework','CoreServices','-o',str(binary)]
    if sanitizers: command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    compile_result=subprocess.run(command,capture_output=True,timeout=60)
    (output/'compiler.stdout').write_bytes(compile_result.stdout)
    (output/'compiler.stderr').write_bytes(compile_result.stderr)
    need(compile_result.returncode==0,'native compile failed; preserved compiler logs')
    need(before==sources(),'source changed during build')
    payload=b'eMNA:AEHLR'+run[:12].encode()+b'\0'
    for leaf in ('A.resource','B.resource'):
        with os.fdopen(os.open(output/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb') as out:
            out.write(payload)
    from experiments.startup_trace.image import Image
    image=Image(binary)
    site=image.symbol('_fsref_probe_site')
    need(image.bytes(site).hex()=='1f2003d5','probe site differs')
    record={'schema':1,'kind':'OWNED_FSREF_ONLY','run_id':run,
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'sources':before,'image':{'path':str(binary),'sha256':image.sha256,'uuid':image.uuid},
            'site':site,'payload_sha256':hashlib.sha256(payload).hexdigest(),
            'sanitizers':['ASan','UBSan'] if sanitizers else [],'command':command}
    write_once(output/'build.json',record)
    return record


def ipc(record):
    binary=Path(record['image']['path']); output=binary.parent
    need(hashlib.sha256(binary.read_bytes()).hexdigest()==record['image']['sha256'] and
         sources()==record['sources'],'IPC source/binary changed')
    a,b=output/'A.resource',output/'B.resource'
    for path in (a,b):
        need(not path.is_symlink() and path.stat().st_nlink==1 and path.stat().st_uid==os.getuid() and
             path.stat().st_size==23 and hashlib.sha256(path.read_bytes()).hexdigest()==record['payload_sha256'],
             'owned IPC resource changed')
    need((a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino) and
         a.read_bytes()==b.read_bytes(),'twin control differs')
    emitted=execute(binary,['emit',a,b],output)
    need(emitted['code']==0 and len(emitted['stdout'])==160,'FSREF_EMIT_FAILED')
    emitter=json.loads(emitted['stderr'])
    need(emitter=={'pid':emitted['pid'],'bytes':160},'emitter identity differs')
    first=compare(binary,a,emitted['stdout'][:80],output)
    twin=compare(binary,a,emitted['stdout'][80:],output)
    need(first['same'] and not twin['same'] and len({emitter['pid'],first['pid'],twin['pid']})==3,
         'intended cross-process identity control not observed')
    need(sources()==record['sources'] and hashlib.sha256(binary.read_bytes()).hexdigest()==record['image']['sha256'] and
         all(hashlib.sha256(path.read_bytes()).hexdigest()==record['payload_sha256'] for path in (a,b)),
         'IPC source/binary changed')
    receipt={'status':'FSREF_IPC_PASS','emitter':emitter,'first':first,'twin':twin,
             'same_bytes_different_inode':True,'source_commit':record['source_commit'],
             'image':record['image'],'sources':record['sources'],'sanitizers':record['sanitizers'],
             'AE_run':'NOT_RUN','AE_output_admission':'BLOCKED'}
    write_once(output/'ipc.json',receipt)
    return receipt


class Chain:
    """Instrumented owned invocation stack, not inferred Adobe frames/lifetimes."""
    def __init__(self):
        self.sequence=0; self.stack=[]; self.rows={}; self.complete=False; self.reason=None

    def feed(self,row):
        need(self.reason is None and not self.complete,'TERMINAL_CHAIN')
        try: self._feed(row)
        except ValueError as error:
            self.reason=str(error); raise

    def _feed(self,row):
        need(type(row) is dict and set(row)=={'sequence','phase','invocation','parent','pointer','size','status','same','value','payload_sha256'},'EVENT_SHAPE')
        need(all(type(row[k]) is int and 0<=row[k]<2**64 for k in
                 ('sequence','phase','invocation','parent','pointer','size','status')),'EVENT_VALUES')
        need(row['sequence']==self.sequence,'EVENT_SEQUENCE'); self.sequence+=1
        phase,inv,parent=row['phase'],row['invocation'],row['parent']
        if phase==10:
            need(not self.stack and inv==0 and parent==0 and self.rows,'INCOMPLETE_CHAIN')
            need(all(item['phase'] in (9,11) for item in self.rows.values()),'INCOMPLETE_CHAIN')
            self.complete=True; return
        if phase==1:
            need(inv>0 and inv not in self.rows and parent==(self.stack[-1] if self.stack else 0),'INVOCATION_MISMATCH')
            self.stack.append(inv); self.rows[inv]={'phase':1,'parent':parent}; return
        need(self.stack and self.stack[-1]==inv and self.rows[inv]['parent']==parent,'INVOCATION_MISMATCH')
        state=self.rows[inv]
        if phase==11:
            need(state['phase']==5,'UNEXPECTED_UNWIND'); state['phase']=11; self.stack.pop(); return
        need(phase==state['phase']+1,'PHASE_MISMATCH')
        need(row['status']==(1 if phase==2 else 0),'CALL_FAILED')
        if phase==2:
            need(row['size']==80 and row['pointer']>0 and type(row['same']) is bool,'REF_OUTPUT')
            state['same']=row['same']
        elif phase==3:
            need(row['size']==4 and type(row['value']) is int,'FORK_OUTPUT')
            state['fork']=row['value']
        elif phase==4:
            need(row['size']==8 and type(row['value']) is int and 0<row['value']<=4096,'FORK_SIZE')
            state['extent']=row['value']
        elif phase==5:
            need(row['pointer']>0 and row['size']==state['extent'],'ALLOCATION_EXTENT')
            state['allocation']=row['pointer']
        elif phase==6:
            need(row['size']==24 and type(row['value']) is dict and
                 set(row['value'])=={'allocation','actual','fork'} and
                 all(type(value) is int and 0<=value<2**64 for value in row['value'].values()),'READ_OUTPUT')
            need(row['value']['allocation']==state['allocation'] and
                 row['value']['fork']==state['fork'],'SOURCE_GENERATION_MISMATCH')
            need(row['value']['actual']==state['extent'],'READ_COUNT')
        elif phase==7:
            need(row['pointer']>0 and row['pointer']!=state['allocation'] and row['size']==state['extent'],'COPY_EXTENT')
            need((state['same'] and type(row['payload_sha256']) is str and
                  re.fullmatch('[0-9a-f]{64}',row['payload_sha256'])) or
                 (not state['same'] and row['payload_sha256'] is None),'PAYLOAD_SCOPE')
        elif phase==8:
            need(row['pointer']==state['allocation'] and row['size']==0,'ALLOCATION_GENERATION_MISMATCH')
        elif phase==9: self.stack.pop()
        state['phase']=phase


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path); parser.add_argument('--sanitizers',action='store_true')
    args=parser.parse_args(); print(json.dumps(ipc(build(args.output,args.sanitizers)),indent=2))
