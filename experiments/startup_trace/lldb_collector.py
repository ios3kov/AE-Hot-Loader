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
import signal
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import Trace, need
from stops import capture, select, initial as initial_stop
from profile import validate, read_json, ROOT
from lifecycle import stopped_event, same_stop


def load_native():
    spec=importlib.util.spec_from_file_location('aehl_trace_native_controller',ROOT/'experiments/startup_calibration/run.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def write_once(path, record):
    path=Path(path);temporary=path.with_name(path.name+'.pending')
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as out: json.dump(record,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    # Publish complete bytes without replacement; preserve pending on failure.
    os.link(temporary,path,follow_symlinks=False);temporary.unlink()


def reg(frame, name, api):
    part=name.split('.'); value=frame.FindRegister(part[0]);need(value.IsValid(),'register unavailable')
    error=api.SBError()
    if len(part)==2:
        data=value.GetData();need(data.GetByteSize()==16,'unexpected vector register width')
        result=data.GetUnsignedInt64(error,0 if part[1]=='low' else 8)
    else: result=value.GetValueAsUnsigned(error)
    need(error.Success(),'register decode failed');return result


def own_breakpoint_inventory(record, breaks):
    # Debugger metadata only, not a read of target code or a proof that a patch
    # was installed. Own images only; disabled locations remain observable.
    rows=[]
    for role, bp in breaks.items():
        site=record['sites'][role]
        if site['module'] not in ('marker','observer','fixture'): continue
        need(bp.IsValid() and bp.GetNumLocations()==1, 'own inventory breakpoint differs')
        location=bp.GetLocationAtIndex(0);address=location.GetAddress()
        pin=record['modules'][site['module']]
        need(address.IsValid() and address.GetModule().GetUUIDString().lower()==pin['uuid'] and
             address.GetFileAddress()==site['offset'], 'own inventory location differs')
        rows.append({'role':role,'module':site['module'],'uuid':pin['uuid'],
                     'file_address':int(address.GetFileAddress()),'enabled':bool(bp.IsEnabled()),
                     'location_enabled':bool(location.IsEnabled()),'hardware':bool(bp.IsHardware())})
    return {'scope':'own debugger metadata; actual patch bytes UNKNOWN','breakpoints':rows}


def finalize(target, process, breaks, report, output, api):
    # Evidence failure cannot prevent attempted cleanup. Preserve an incomplete
    # observation before touching debugger state; final result stays separate.
    try:
        write_once(output/'observation.json',report)
    except OSError:
        report['observation_journal']='FAIL'
    try:
        removed=[target.BreakpointDelete(bp.GetID()) for bp in breaks.values()]
        need(all(removed), 'own breakpoint removal failed')
        if process is None:
            report.update(cleanup_safe=True,detach='NO_LAUNCH')
        elif not process.IsValid() or process.GetProcessID()<=0:
            report.update(cleanup_safe=False,detach='UNKNOWN_INVALID_PROCESS')
        elif process.GetState()==api.eStateExited:
            report.update(cleanup_safe=True,detach='ALREADY_EXITED')
        else:
            detached=process.Detach(False)
            report.update(cleanup_safe=detached.Success(),detach='PASS' if detached.Success() else 'BLOCKED: '+str(detached))
    except Exception as exc:
        report.update(cleanup_safe=False,detach='UNKNOWN_CLEANUP_FAILURE',cleanup_reason=str(exc))
    write_once(output/'result.json',report)


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
        # The command interpreter must not consume this observer's process
        # events. A dedicated listener is installed before the fresh launch.
        listener=lldb.SBListener('aehl-owned-startup');launch=target.GetLaunchInfo()
        launch.SetListener(listener)
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
                    write_once(output/'publication-breakpoints.json', own_breakpoint_inventory(record,breaks))
                    publication='OUTCOME_UNKNOWN';deadline=now+120
                    write_once(output/'publication-intent.json',{'state':'OUTCOME_UNKNOWN','pid':observed['pid'],'build_id':candidate['build_id'],'monotonic_deadline':deadline})
                    native.publish(control,native.request(candidate,observed,int(time.time())+110,observation_mode=True))
                    publication='SENT_ONCE'
            event=lldb.SBEvent();received=listener.WaitForEvent(1,event)
            state=process.GetState()
            if state==lldb.eStateExited:
                report['exit_status']=process.GetExitStatus();report['exit_description']=process.GetExitDescription()
                raise ValueError('owned process exited before complete identity trace')
            if received and stopped_event(event,process,lldb):
                stopid=process.GetStopID()
                if stopid!=last_stop:
                    last_stop=stopid
                    initial=capture(process,lldb) if entry_stop else None
                    if entry_stop and initial['total_threads']<=256 and not any(t['breakpoint'] for t in initial['threads']):
                        entry_stop=False
                        try:
                            initial_stop(initial,lldb,int(signal.SIGSTOP))
                        except ValueError as exc:
                            initial['refusal']=str(exc)
                            write_once(output/'unexpected-stop.json',initial)
                            raise
                        write_once(output/'initial-stop.json',{'state':int(state),'stop':int(stopid),'metadata':initial,'breakpoints':{r:[{'address':int(bp.GetLocationAtIndex(i).GetAddress().GetLoadAddress(target)),'enabled':bool(bp.IsEnabled())} for i in range(bp.GetNumLocations())] for r,bp in breaks.items()}})
                        need(process.Continue().Success(),'initial continue failed')
                    else:
                        entry_stop=False
                        snapshot=capture(process,lldb)
                        try:
                            selected,role=select(snapshot,lldb.eStateStopped,roles,trace.thread if trace else None)
                        except ValueError as exc:
                            snapshot['refusal']=str(exc)
                            write_once(output/'unexpected-stop.json',snapshot)
                            raise
                        same_stop(process,snapshot['stop_id'],lldb)
                        thread=process.GetThreadAtIndex(selected)
                        frame=thread.GetFrameAtIndex(0);pc=frame.GetPCAddress();site=record['sites'][role];pin=record['modules'][site['module']]
                        need(pc.GetModule().GetUUIDString().lower()==pin['uuid'] and pc.GetFileAddress()==site['offset'],'mapped PC/module changed')
                        actual=str(Path(pc.GetModule().GetFileSpec().fullpath).resolve());need(actual==pin.get('loaded_path',pin['path']),'mapped module path differs')
                        if trace is None:trace=Trace(observed['pid'],native.birth(observed),pointer('callback'),None)
                        if role=='reader':trace.match_function=pointer('match_function')
                        values={name:reg(frame,r,lldb) for name,r in site['registers'].items()}
                        same_stop(process,snapshot['stop_id'],lldb)
                        accepted=trace.feed({'pid':observed['pid'],'birth':native.birth(observed),'thread':int(thread.GetThreadID()),'role':role,'values':values})
                        if accepted:write_once(output/('event-%03d.json'%len(trace.events)),trace.events[-1])
                        for r,bp in breaks.items():bp.SetEnabled(r in trace.enabled)
                        if accepted:write_once(output/('own-breakpoints-%03d.json'%len(trace.events)), own_breakpoint_inventory(record,breaks))
                        if trace.phase=='complete':report.update(trace.result());break
                        need(process.Continue().Success(),'owned continue failed')
    except Exception as exc:
        report.update(status='BLOCKED_OR_INCOMPLETE',reason=str(exc))
        if trace:report['partial_trace']=trace.result()
    finally:
        # Preserve the observation before cleanup touches the debugger again.
        # A debugger crash during cleanup must not erase the partial evidence.
        report['publication']=publication
        report['scope']='normal startup identity only; late-add/Apply/render NOT_RUN'
        try:write_once(output/'final-breakpoints.json', own_breakpoint_inventory(record,breaks))
        except Exception:report['own_breakpoint_inventory']='UNKNOWN'
        # Delete our own breakpoints before detach; never quit/kill an attached
        # process on failure. The external launcher keeps debugger stdin open.
        finalize(target,process,breaks,report,output,lldb)
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
