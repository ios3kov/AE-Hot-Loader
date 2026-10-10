"""Only freshly built owned Carbon fixture; existing stop/borrow/detach transport."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.resource_trace.core import need
from experiments.resource_trace.fsref_ipc import Chain, build, compare, ipc, sources
from experiments.resource_trace.transport_profile import clean_source
from experiments.resource_trace.borrow import read
from experiments.startup_trace.image import Image
from experiments.startup_trace.lldb_collector import load_native, reg, write_once, finalize
from experiments.startup_trace.stops import capture, select
from experiments.startup_trace.lifecycle import same_stop, stopped_event


def admitted(profile,digest):
    profile=Path(profile)
    need(profile.is_absolute() and not any(p.is_symlink() for p in (profile,*profile.parents)) and
         profile.name=='build.json' and profile.parent.parent==ROOT/'build-ae-hot-loader' and
         profile.parent.name.startswith('fsref-debug-') and profile.stat().st_uid==os.getuid() and
         profile.stat().st_nlink==1 and profile.stat().st_mode&0o777==0o600 and
         profile.parent.stat().st_mode&0o777==0o700 and profile.stat().st_size<=32768,'owned FSRef profile scope')
    raw=profile.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==digest,'profile digest changed')
    row=json.loads(raw)
    need(set(row)=={'schema','kind','run_id','source_commit','sources','image','site',
                   'payload_sha256','sanitizers','command'} and row['schema']==1 and
         row['kind']=='OWNED_FSREF_ONLY' and row['sources']==sources() and
         row['source_commit']==clean_source(),'owned FSRef source admission')
    pin=row['image']; binary=profile.parent/'aehl-fsref-ipc'
    need(not binary.is_symlink() and binary.stat().st_uid==os.getuid() and binary.stat().st_nlink==1 and
         not binary.stat().st_mode&0o022,'owned binary scope')
    image=Image(binary)
    need(pin=={'path':str(binary),'sha256':image.sha256,'uuid':image.uuid} and
         row['site']==image.symbol('_fsref_probe_site') and image.bytes(row['site']).hex()=='1f2003d5',
         'owned image/site changed')
    for leaf in ('A.resource','B.resource'):
        resource=profile.parent/leaf
        need(not resource.is_symlink() and resource.stat().st_uid==os.getuid() and
             resource.stat().st_nlink==1 and resource.stat().st_mode&0o777==0o600 and
             resource.stat().st_size==23 and hashlib.sha256(resource.read_bytes()).hexdigest()==row['payload_sha256'],
             'own resource changed')
    return row


def observe(debugger,profile,digest,mode,output):
    import lldb
    record=admitted(profile,digest); output=Path(output)
    need(mode in ('nested','unwind') and debugger.GetNumTargets()==0,'owned launch scope')
    need(output==Path(profile).parent/('capture-'+mode) and output.is_dir() and not output.is_symlink() and
         output.stat().st_mode&0o777==0o700 and not any(output.iterdir()),'private capture output')
    debugger.SetAsync(True); error=lldb.SBError(); pin=record['image']
    target=debugger.CreateTarget(pin['path'],'arm64-apple-macosx',None,False,error)
    need(error.Success() and target.IsValid(),'target creation')
    process=None; breaks={}; native=load_native(); chain=Chain(); observed=None
    report={'status':'INCOMPLETE','cleanup_safe':False,'source_commit':record['source_commit'],
            'image':pin,'mode':mode,'events':[],'reads':[],'AE_run':'NOT_RUN','AE_output_admission':'BLOCKED'}
    try:
        module=target.GetModuleAtIndex(0)
        need(module.GetUUIDString().lower()==pin['uuid'] and
             str(Path(module.GetFileSpec().fullpath).resolve())==pin['path'],'mapped own image')
        bp=target.BreakpointCreateBySBAddress(module.ResolveFileAddress(record['site'])); breaks['probe']=bp
        need(bp.IsValid() and bp.GetNumLocations()==1,'own probe ambiguity')
        listener=lldb.SBListener('aehl-fsref-owned'); launch=target.GetLaunchInfo(); launch.SetListener(listener)
        launch.SetArguments([mode,str(Path(profile).parent/'A.resource'),str(Path(profile).parent/'B.resource')],False)
        launch.SetExecutableFile(lldb.SBFileSpec(pin['path']),True); launch.SetDetachOnError(True)
        launch.SetWorkingDirectory(str(output)); launch.SetLaunchFlags(lldb.eLaunchFlagDebug)
        launch.AddOpenFileAction(0,'/dev/null',True,False)
        for fd,leaf in ((1,'fixture.stdout'),(2,'fixture.stderr')):
            handle=os.open(output/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            os.close(handle); launch.AddOpenFileAction(fd,str(output/leaf),False,True)
        admitted(profile,digest)
        write_once(output/'launch-intent.json',{'executable':pin['path'],'state':'OUTCOME_UNKNOWN'})
        process=target.Launch(launch,error)
        report['launch_outcome']={'error':str(error),'pid':int(process.GetProcessID()),'state':int(process.GetState())}
        need(error.Success() and process.IsValid() and process.GetProcessID()>0,'owned launch refused')
        observed=native.common.process_identity(int(process.GetProcessID()))
        need(observed['executable']==pin['path'],'launched executable differs')
        report['owned_process']=observed; write_once(output/'launch.json',observed)
        unique=process.GetUniqueID(); last=None; thread_id=None; deadline=time.monotonic()+60
        def identity():
            need(process.GetUniqueID()==unique and process.GetProcessID()==observed['pid'] and
                 native.common.process_identity(observed['pid'])==observed,'owned process identity changed')
        while not chain.complete:
            need(time.monotonic()<deadline and len(report['events'])<24 and not (output/'cancel').exists(),
                 'capture budget/cancel')
            identity(); event=lldb.SBEvent(); received=listener.WaitForEvent(1,event)
            need(process.GetState()!=lldb.eStateExited,'fixture exited before complete chain')
            if not received or not stopped_event(event,process,lldb): continue
            stop=process.GetStopID()
            if stop==last: continue
            last=stop; snapshot=capture(process,lldb)
            try: selected,_=select(snapshot,lldb.eStateStopped,{bp.GetID():'probe'},thread_id)
            except ValueError as exc:
                # Bounded debugger metadata of this owned fixture, no byte reads.
                for item in snapshot['threads']:
                    if item['none']: continue
                    stopped=process.GetThreadAtIndex(item['index']); top=stopped.GetFrameAtIndex(0)
                    item['owned_exception_metadata']={'pc':int(top.GetPC()),'function':top.GetFunctionName(),
                        'reason_words':[int(stopped.GetStopReasonDataAtIndex(i)) for i in
                                        range(min(stopped.GetStopReasonDataCount(),3))]}
                snapshot['refusal']=str(exc); write_once(output/'unexpected-stop.json',snapshot); raise
            identity(); same_stop(process,stop,lldb)
            thread=process.GetThreadAtIndex(selected); frame=thread.GetFrameAtIndex(0); pc=frame.GetPCAddress()
            need(pc.GetFileAddress()==record['site'] and pc.GetModule().GetUUIDString().lower()==pin['uuid'] and
                 str(Path(pc.GetModule().GetFileSpec().fullpath).resolve())==pin['path'],'own PC/image changed')
            phase,inv,parent,address,size,status,main,sequence=[reg(frame,'x'+str(i),lldb) for i in range(8)]
            need(main==1,'not own OS main thread'); thread_id=int(thread.GetThreadID())
            row={'sequence':sequence,'phase':phase,'invocation':inv,'parent':parent,'pointer':address,
                 'size':size,'status':status,'same':None,'value':None,'payload_sha256':None}
            # Validate metadata and call success BEFORE any scoped target byte read.
            need(phase in range(1,12) and phase!=0,'unknown phase')
            need(sequence==chain.sequence,'EVENT_SEQUENCE')
            if phase not in (1,10):
                need(chain.stack and chain.stack[-1]==inv and chain.rows[inv]['parent']==parent,'INVOCATION_MISMATCH')
            if phase in (2,3,4,6):
                need(status==(1 if phase==2 else 0),'CALL_FAILED')
                need(size=={2:80,3:4,4:8,6:24}[phase],'typed output extent')
                raw,receipt=read(process,lldb,identity,stop,address,size,address,size)
                receipt.update(phase=phase,invocation=inv,sha256=hashlib.sha256(raw).hexdigest())
                report['reads'].append(receipt)
                if phase==2:
                    comparison=compare(Path(pin['path']),Path(profile).parent/'A.resource',raw,output)
                    row['same']=comparison['same']; row['comparison']=comparison
                elif phase==3: row['value']=struct.unpack('<I',raw)[0]
                elif phase==4: row['value']=struct.unpack('<q',raw)[0]
                else:
                    allocation,actual,fork=struct.unpack('<QQQ',raw)
                    row['value']={'allocation':allocation,'actual':actual,'fork':fork}
            if phase==7:
                need(chain.rows[inv]['phase']==6 and size==chain.rows[inv]['extent'] and
                     0<size<=4096 and address!=chain.rows[inv]['allocation'] and status==0,'copy scope')
                if chain.rows[inv]['same']:
                    raw,receipt=read(process,lldb,identity,stop,address,size,address,size)
                    row['payload_sha256']=hashlib.sha256(raw).hexdigest()
                    need(row['payload_sha256']==record['payload_sha256'],'own copy payload differs')
                    receipt.update(phase=phase,invocation=inv,sha256=row['payload_sha256']); report['reads'].append(receipt)
            comparison=row.pop('comparison',None); chain.feed(row)
            report['events'].append(copy.deepcopy(row))
            write_once(output/('event-%02d.json'%sequence),{'event':row,'comparison':comparison,'stop_id':stop,'thread':thread_id})
            if not chain.complete: need(process.Continue().Success(),'continue refused')
        admitted(profile,digest)
        if mode=='nested':
            need(len(report['events'])==19 and chain.rows[1]['same'] and not chain.rows[2]['same'] and
                 chain.rows[1]['phase']==9 and chain.rows[2]['phase']==9,'intended nested control differs')
            changed=copy.deepcopy(report['events']); twin_allocation=next(r for r in changed if r['invocation']==2 and r['phase']==5)
            twin_allocation.update(invocation=1,parent=0)
            negative=Chain()
            try:
                for row in changed: negative.feed(row)
            except ValueError as exc:
                need(str(exc)=='INVOCATION_MISMATCH','unrelated negative refusal')
            else: raise ValueError('twin allocation incorrectly joined outer chain')
            report.update(status='OWNED_NESTED_FSREF_OBSERVED',negative_replay='INVOCATION_MISMATCH')
        else:
            need(len(report['events'])==7 and chain.rows[1]['phase']==11 and
                 all(r['phase'] not in (6,7,8,9) for r in report['events']),'unwind continued normal chain')
            report.update(status='OWNED_UNWIND_OBSERVED')
    except Exception as exc: report.update(status='REFUSED_OR_INCOMPLETE',reason=str(exc))
    finally: finalize(target,process,breaks,report,output,lldb)
    return report


def command(debugger,arguments,result,_):
    args=shlex.split(arguments)
    if len(args)!=4: result.SetError('expected profile, digest, mode, output'); return
    try: result.PutCString(json.dumps(observe(debugger,*args)))
    except Exception as exc:
        output=Path(args[3])
        if output.is_dir() and not (output/'launch-intent.json').exists() and not (output/'result.json').exists():
            write_once(output/'result.json',{'status':'REFUSED_BEFORE_LAUNCH','reason':str(exc),
                                           'cleanup_safe':True,'detach':'NO_LAUNCH'})
        result.SetError(str(exc))


def __lldb_init_module(debugger,_):
    debugger.HandleCommand('command script add -s asynchronous -f fsref_debug.command aehl-fsref-fixture')


def preserve_debugger(child,output,reason):
    # Keep stdin and the supervising process alive. Returning/destroying Popen
    # could send EOF to LLDB and implicitly quit a still-attached debugger.
    failure={'status':'ATTENTION','debugger_pid':child.pid,'reason':reason,'cleanup_safe':False}
    if not (output/'attention.json').exists(): write_once(output/'attention.json',failure)
    print('ATTENTION: owned debugger retained; no automatic quit or kill',flush=True)
    while child.poll() is None: time.sleep(0.25)
    child.stdin.close()
    return failure


def drive(profile,mode):
    profile=Path(profile); digest=hashlib.sha256(profile.read_bytes()).hexdigest(); record=admitted(profile,digest)
    output=profile.parent/('capture-'+mode); output.mkdir(mode=0o700)
    console=output.with_name('debugger-'+mode+'.log')
    with os.fdopen(os.open(console,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb') as log:
        child=subprocess.Popen(['lldb','--no-lldbinit'],stdin=subprocess.PIPE,stdout=log,stderr=log,
                               env={k:v for k,v in os.environ.items() if not k.startswith('AEHL_')})
        commands=['command script import '+shlex.quote(str(Path(__file__))),
                  'aehl-fsref-fixture '+' '.join(shlex.quote(str(x)) for x in (profile,digest,mode,output))]
        child.stdin.write(('\n'.join(commands)+'\n').encode()); child.stdin.flush(); deadline=time.monotonic()+85
        while not (output/'result.json').exists():
            if time.monotonic()>deadline or child.poll() is not None:
                return preserve_debugger(child,output,'missing final receipt; detach UNKNOWN')
            if console.stat().st_size>1048576 and not (output/'cancel').exists():
                write_once(output/'cancel',{'reason':'console budget'})
            time.sleep(0.2)
        result=json.loads((output/'result.json').read_text())
        if not result.get('cleanup_safe'): return preserve_debugger(child,output,'detach not proven')
        child.stdin.write(b'quit\n'); child.stdin.flush()
        try: child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            return preserve_debugger(child,output,'debugger quit did not finish')
        child.stdin.close(); result['debugger_exit_code']=child.returncode
    owned=result.get('owned_process')
    if owned:
        deadline=time.monotonic()+10
        while True:
            try: os.kill(owned['pid'],0)
            except ProcessLookupError: break
            need(time.monotonic()<deadline,'owned process still present; preserve'); time.sleep(0.1)
        result['process_absence']='PASS'
        if result['status'] in ('OWNED_NESTED_FSREF_OBSERVED','OWNED_UNWIND_OBSERVED'):
            stdout=(output/'fixture.stdout').read_bytes(); stderr=(output/'fixture.stderr').read_bytes()
            need(stderr==b'' and stdout and json.loads(stdout)=={'pid':owned['pid'],'status':'OWNED_COMPLETE'},
                 'owned fixture did not complete normally')
    admitted(profile,digest); write_once(output/'supervisor.json',result)
    expected='OWNED_NESTED_FSREF_OBSERVED' if mode=='nested' else 'OWNED_UNWIND_OBSERVED'
    need(result['status']==expected and result['cleanup_safe'] and result.get('process_absence')=='PASS' and
         result['debugger_exit_code']==0,'intended debugger control not observed: '+str(result.get('reason')))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--sanitizers',action='store_true')
    args=parser.parse_args(); clean_source()
    folder=ROOT/'build-ae-hot-loader'/('fsref-debug-'+uuid.uuid4().hex)
    record=build(folder,args.sanitizers); print(json.dumps({'output':str(folder),'ipc':ipc(record)}),flush=True)
    for mode in ('nested','unwind'):
        result=drive(folder/'build.json',mode)
        print(json.dumps({k:result.get(k) for k in ('status','mode','cleanup_safe','process_absence','reason')}),flush=True)
        need(result.get('cleanup_safe') is True,'stop: debugger needs attention')
