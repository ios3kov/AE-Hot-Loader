"""Fresh-target LLDB register observer. No attach, expression, memory read or Kill.

Uses SBTarget.Launch, SBFrame register values and image-relative breakpoints.
Removes its breakpoints and Detach(False) on exit; a detach failure preserves the
session/debugger for manual attention. Do not run LLDB in batch/auto-quit mode.
"""
from pathlib import Path
import importlib.util
import json
import os
import shlex
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import Trace, need
from profile import validate, read_json, ROOT


def load_native():
    spec=importlib.util.spec_from_file_location('aehl_trace_native_controller',ROOT/'experiments/startup_calibration/run.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def write_once(path, record):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as out: json.dump(record,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())


def reg(frame, name, api):
    part=name.split('.'); value=frame.FindRegister(part[0]);need(value.IsValid(),'register unavailable')
    error=api.SBError()
    if len(part)==2:
        data=value.GetData();need(data.GetByteSize()==16,'unexpected vector register width')
        result=data.GetUnsignedInt64(error,0 if part[1]=='low' else 8)
    else: result=value.GetValueAsUnsigned(error)
    need(error.Success(),'register decode failed');return result


def observe(debugger, profile_path, digest, output):
    import lldb
    record=validate(read_json(profile_path,digest)); output=Path(output)
    need(output.is_absolute() and output.is_dir() and output.stat().st_uid==os.getuid() and
         output.stat().st_mode&0o777==0o700 and not any(p.is_symlink() for p in (output,*output.parents)), 'output is not private/owned')
    need(not any(output.iterdir()),'trace replay/output occupied')
    native=load_native();is_ae=record['kind']=='ae-owned-startup'
    need(not is_ae or not native.processes(),'AE/aerender already running; no launch')
    candidate=None
    if is_ae:
        candidate=read_json(record['candidate_manifest'],record['candidate_sha256'])
        need(candidate.get('trace_identity') is True,'wrong candidate')
        for item in candidate['bundles']:
            installed=Path(candidate['config']['calibration_module']).parents[2].parent/item['bundle']
            need(native.common.bundle_hashes(installed)==item['files'],'installed own bytes changed')
        need(not any((Path(candidate['config']['calibration_control'])/leaf).exists() for leaf in ('ready','request','consumed','result','begin')),'candidate request already used')
    need(debugger.GetNumTargets()==0,'debugger already has another target')
    debugger.SetAsync(True);error=lldb.SBError()
    target=debugger.CreateTarget(record['host']['path'],'arm64-apple-macosx',None,False,error)
    need(error.Success() and target.IsValid(),'target creation failed')
    modules={};breaks={};roles={};process=None;observed=None;trace=None
    started=time.monotonic();deadline=started+180;publication='NOT_SENT';report={'status':'UNKNOWN','cleanup_safe':False,'kind':record['kind'],'source_commit':record['source_commit'],'collector_sha256':record['collector_sha256']}
    try:
        for label,pin in record['modules'].items():
            path=pin.get('loaded_path',pin['path']);module=target.AddModule(path,'arm64-apple-macosx',pin['uuid'])
            need(module.IsValid() and module.GetUUIDString().lower()==pin['uuid'],'LLDB module differs');modules[label]=module
        for role,site in record['sites'].items():
            address=modules[site['module']].ResolveFileAddress(site['offset']);need(address.IsValid(),'site resolution failed')
            bp=target.BreakpointCreateBySBAddress(address);need(bp.IsValid() and bp.GetNumLocations()==1,'breakpoint unresolved/ambiguous')
            bp.SetEnabled(role=='marker');breaks[role]=bp;roles[bp.GetID()]=role
        listener=debugger.GetListener();launch=target.GetLaunchInfo()
        launch.SetArguments([],False);launch.SetExecutableFile(lldb.SBFileSpec(record['host']['path']),True)
        launch.SetDetachOnError(True)
        launch.SetLaunchFlags(lldb.eLaunchFlagDebug | lldb.eLaunchFlagStopAtEntry)
        launch.SetWorkingDirectory(str(output));launch.AddOpenFileAction(0,'/dev/null',True,False)
        for leaf in ('host-stdout.log','host-stderr.log'):
            fd=os.open(output/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
        launch.AddOpenFileAction(1,str(output/'host-stdout.log'),False,True);launch.AddOpenFileAction(2,str(output/'host-stderr.log'),False,True)
        if candidate:launch.SetEnvironmentEntries(['AEHL_STARTUP_CALIBRATION_TOKEN='+candidate['token']],True)
        need(not is_ae or not native.processes(),'a session opened before launch')
        write_once(output/'launch-intent.json',{'state':'OUTCOME_UNKNOWN','executable':record['host']['path']})
        process=target.Launch(launch,error);report['launch_error']=str(error) if not error.Success() else None
        if process.IsValid() and process.GetProcessID()>0:report['pid']=int(process.GetProcessID())
        need(error.Success() and process.IsValid() and process.GetProcessID()>0,'launch refused; preserve any partially launched process')
        observed=native.common.process_identity(int(process.GetProcessID()))
        need(observed['executable']==record['host']['path'],'launched executable differs');report['owned_process']=observed;report['launch_state']=int(process.GetState());report['launch_flags']=int(launch.GetLaunchFlags())
        write_once(output/'launch.json',report)
        last_stop=None;entry_stop=True
        def pointer(which):
            spec=record[which];value=modules[spec['module']].ResolveFileAddress(spec['offset']).GetLoadAddress(target)
            need(value!=lldb.LLDB_INVALID_ADDRESS and value>0,'provider function not mapped');return value
        while True:
            now=time.monotonic();need(now<deadline,'original trace deadline exceeded')
            need(not (output/'cancel').exists(),'trace cancelled; no retry')
            need(sum(p.stat().st_size for p in output.iterdir() if p.is_file())<=1024*1024,'trace/log byte budget exceeded')
            need(native.common.process_identity(observed['pid'])==observed,'owned PID/birth/executable changed')
            if is_ae:
                need(native.processes()==[observed['pid']],'AE process exclusivity changed')
                control=Path(candidate['config']['calibration_control'])
                if publication=='NOT_SENT' and (control/'ready').exists():
                    native.ready_identity(native.common.read(control/'ready',512),candidate,observed)
                    need(not any((control/x).exists() for x in ('request','consumed','result','begin')),'publication replay')
                    publication='OUTCOME_UNKNOWN';deadline=now+120
                    write_once(output/'publication-intent.json',{'state':'OUTCOME_UNKNOWN','pid':observed['pid'],'build_id':candidate['build_id'],'monotonic_deadline':deadline})
                    native.publish(control,native.request(candidate,observed,int(time.time())+110,observation_mode=True))
                    publication='SENT_ONCE'
            state=process.GetState()
            if state==lldb.eStateExited:
                report['exit_status']=process.GetExitStatus();report['exit_description']=process.GetExitDescription()
                raise ValueError('owned process exited before complete identity trace')
            if state==lldb.eStateStopped:
                stopid=process.GetStopID()
                if stopid!=last_stop:
                    last_stop=stopid;stopped=[t for t in process if t.GetStopReason()==lldb.eStopReasonBreakpoint]
                    if not stopped and entry_stop:
                        entry_stop=False
                        write_once(output/'initial-stop.json',{'state':int(state),'stop':int(stopid),'breakpoints':{r:[{'address':int(bp.GetLocationAtIndex(i).GetAddress().GetLoadAddress(target)),'enabled':bool(bp.IsEnabled())} for i in range(bp.GetNumLocations())] for r,bp in breaks.items()}})
                        need(process.Continue().Success(),'initial continue failed')
                    else:
                        entry_stop=False;need(len(stopped)==1,'unexpected stop or simultaneous breakpoints')
                        thread=stopped[0];need(thread.GetStopReasonDataCount()==2,'breakpoint stop shape')
                        role=roles.get(thread.GetStopReasonDataAtIndex(0));need(role is not None,'unowned breakpoint')
                        frame=thread.GetFrameAtIndex(0);pc=frame.GetPCAddress();site=record['sites'][role];pin=record['modules'][site['module']]
                        need(pc.GetModule().GetUUIDString().lower()==pin['uuid'] and pc.GetFileAddress()==site['offset'],'mapped PC/module changed')
                        actual=str(Path(pc.GetModule().GetFileSpec().fullpath).resolve());need(actual==pin.get('loaded_path',pin['path']),'mapped module path differs')
                        if trace is None:trace=Trace(observed['pid'],native.birth(observed),pointer('callback'),None)
                        if role=='reader':trace.match_function=pointer('match_function')
                        values={name:reg(frame,r,lldb) for name,r in site['registers'].items()}
                        accepted=trace.feed({'pid':observed['pid'],'birth':native.birth(observed),'thread':int(thread.GetThreadID()),'role':role,'values':values})
                        if accepted:write_once(output/('event-%03d.json'%len(trace.events)),trace.events[-1])
                        for r,bp in breaks.items():bp.SetEnabled(r in trace.enabled)
                        if trace.phase=='complete':report.update(trace.result());break
                        need(process.Continue().Success(),'owned continue failed')
            event=lldb.SBEvent();listener.WaitForEvent(1,event)
    except Exception as exc:
        report.update(status='BLOCKED_OR_INCOMPLETE',reason=str(exc))
        if trace:report['partial_trace']=trace.result()
    finally:
        # Delete our own breakpoints before detach; never quit/kill an attached
        # process on failure. The external launcher keeps debugger stdin open.
        for bp in breaks.values():target.BreakpointDelete(bp.GetID())
        if process is None or not process.IsValid() or process.GetProcessID()<=0:
            report.update(cleanup_safe=True,detach='NO_PROCESS')
        elif process.GetState()==lldb.eStateExited:
            report.update(cleanup_safe=True,detach='ALREADY_EXITED')
        else:
            detached=process.Detach(False)
            report.update(cleanup_safe=detached.Success(),detach='PASS' if detached.Success() else 'BLOCKED: '+str(detached))
        report['publication']=publication
        report['scope']='normal startup identity only; late-add/Apply/render NOT_RUN'
        write_once(output/'result.json',report)
    return report


def command(debugger, text, result, _):
    args=shlex.split(text)
    if len(args)!=3:result.SetError('expected absolute profile, SHA256, private output');return
    try:
        report=observe(debugger,*args);result.PutCString(json.dumps({k:report.get(k) for k in ('status','pid','cleanup_safe','reason','detach')}))
    except Exception as exc:
        output=Path(args[2])
        if output.is_dir() and not (output/'result.json').exists() and not (output/'launch-intent.json').exists():
            write_once(output/'result.json',{'status':'REFUSED_BEFORE_LAUNCH','reason':str(exc),'cleanup_safe':True})
        result.SetError(str(exc))


def __lldb_init_module(debugger, _):
    debugger.HandleCommand('command script add -s asynchronous -f lldb_collector.command aehl-owned-trace')
