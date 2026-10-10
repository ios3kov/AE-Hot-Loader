"""Fresh owned fixture LLDB capture. No Adobe target, attach or expression."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.resource_trace.core import Trace, need
from experiments.resource_trace.transport_profile import read_profile, validate
from experiments.resource_trace.borrow import read
# Reuse the reviewed event classification, PID/birth identity and cleanup paths.
from experiments.startup_trace.lldb_collector import load_native, reg, write_once, finalize
from experiments.startup_trace.stops import capture, select
from experiments.startup_trace.lifecycle import same_stop, stopped_event


def observe(debugger, profile_path, expected, output):
    import lldb
    record = read_profile(profile_path, expected)
    output = Path(output)
    need(output.is_absolute() and output.is_dir() and not any(p.is_symlink() for p in (output, *output.parents)) and
         output.stat().st_uid == os.getuid() and output.stat().st_mode & 0o777 == 0o700 and
         not any(output.iterdir()), 'private output/replay')
    need(debugger.GetNumTargets() == 0, 'debugger already owns a target')
    debugger.SetAsync(True)
    error = lldb.SBError()
    pin = record['image']
    target = debugger.CreateTarget(pin['path'], 'arm64-apple-macosx', None, False, error)
    need(error.Success() and target.IsValid(), 'fixture target creation failed')
    native = load_native()
    process = None; breaks = {}; trace = None; observed = None
    report = {'kind': record['kind'], 'source_commit': record['source_commit'], 'sources': record['sources'],
              'status': 'INCOMPLETE', 'cleanup_safe': False, 'AE_observation': 'NOT_RUN',
              'AE_admission': 'BLOCKED', 'reads': [], 'stops': 0}
    try:
        module = target.GetModuleAtIndex(0)
        need(module.GetUUIDString().lower() == pin['uuid'] and
             str(Path(module.GetFileSpec().fullpath).resolve()) == pin['path'], 'fixture mapped module differs')
        address = module.ResolveFileAddress(record['site']['offset'])
        need(address.IsValid(), 'probe address unavailable')
        bp = target.BreakpointCreateBySBAddress(address); breaks['probe'] = bp
        need(bp.IsValid() and bp.GetNumLocations() == 1, 'fixture breakpoint ambiguity')
        listener = lldb.SBListener('aehl-resource-fixture')
        launch = target.GetLaunchInfo(); launch.SetListener(listener)
        launch.SetArguments([record['resource'], record['run_id'], pin['sha256'], record['origin'], record['fault']], False)
        launch.SetExecutableFile(lldb.SBFileSpec(pin['path']), True)
        launch.SetWorkingDirectory(str(output)); launch.SetDetachOnError(True)
        # The probe is armed before launch. Do not request an extra entry stop:
        # Apple debugserver may deliver a second startup SIGSTOP after resume.
        # Only owned probe stops are accepted; unknown stops still refuse.
        launch.SetLaunchFlags(lldb.eLaunchFlagDebug)
        launch.AddOpenFileAction(0, '/dev/null', True, False)
        for fd, leaf in ((1, 'fixture-stdout.log'), (2, 'fixture-stderr.log')):
            handle = os.open(output/leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            os.close(handle); launch.AddOpenFileAction(fd, str(output/leaf), False, True)
        validate(record)
        write_once(output/'launch-intent.json', {'executable': pin['path'], 'state': 'OUTCOME_UNKNOWN'})
        process = target.Launch(launch, error)
        need(error.Success() and process.IsValid() and process.GetProcessID() > 0, 'fixture launch refused')
        observed = native.common.process_identity(int(process.GetProcessID()))
        need(observed['executable'] == pin['path'], 'launched executable differs')
        report['owned_process'] = observed
        write_once(output/'launch.json', observed)
        unique = process.GetUniqueID(); last = None; thread_id = None
        deadline = time.monotonic() + 60

        def identity():
            need(process.GetUniqueID() == unique and process.GetProcessID() == observed['pid'] and
                 native.common.process_identity(observed['pid']) == observed, 'owned process identity changed')

        while True:
            need(time.monotonic() < deadline and report['stops'] <= 12 and
                 not (output/'cancel').exists(), 'transport deadline/stop budget/cancel')
            need(sum(p.stat().st_size for p in output.iterdir() if p.is_file()) <= 1048576, 'transport log budget')
            identity()
            event = lldb.SBEvent(); received = listener.WaitForEvent(1, event)
            need(process.GetState() != lldb.eStateExited, 'fixture exited before complete trace')
            if not received or not stopped_event(event, process, lldb):
                continue
            stop = process.GetStopID()
            if stop == last: continue
            last = stop; snapshot = capture(process, lldb)
            report['stops'] += 1
            try:
                selected, _ = select(snapshot, lldb.eStateStopped, {bp.GetID(): 'probe'}, thread_id)
            except ValueError as exc:
                snapshot['refusal'] = str(exc); write_once(output/'unexpected-stop.json', snapshot)
                raise
            same_stop(process, stop, lldb); identity()
            thread = process.GetThreadAtIndex(selected); frame = thread.GetFrameAtIndex(0)
            pc = frame.GetPCAddress()
            need(pc.GetFileAddress() == record['site']['offset'] and
                 pc.GetModule().GetUUIDString().lower() == pin['uuid'] and
                 str(Path(pc.GetModule().GetFileSpec().fullpath).resolve()) == pin['path'], 'probe PC/image changed')
            values = [reg(frame, 'x' + str(i), lldb) for i in range(5)]
            need(values[4] == 1, 'fixture probe is not on OS main thread')
            current_thread = int(thread.GetThreadID())
            if thread_id is None: thread_id = current_thread
            same_stop(process, stop, lldb)
            raw, receipt = read(process, lldb, identity, stop, *values[:4])
            receipt['sha256'] = hashlib.sha256(raw).hexdigest(); receipt['thread'] = current_thread
            report['reads'].append(receipt)
            def unique_keys(pairs):
                row = {}
                for key, value in pairs:
                    need(key not in row, 'duplicate event key'); row[key] = value
                return row
            row = json.loads(raw, object_pairs_hook=unique_keys)
            if trace is None:
                trace = Trace({'schema': 'AEHL-RESOURCE-FIXTURE-2', 'kind': 'owned-fixture',
                               'run_id': record['run_id'], 'pid': observed['pid'], 'thread': thread_id,
                               'origin': record['origin'], 'module_sha256': pin['sha256'],
                               'payload_sha256': record['payload_sha256'], 'match_name': record['match_name']})
            trace.feed(row)
            write_once(output/('event-%02d.json' % len(trace.events)), {'event': row, 'read': receipt})
            if trace.result()['phase'] == 'complete':
                report.update(status='OWNED_RESOURCE_TRANSPORT_OBSERVED', trace=trace.result()); break
            need(process.Continue().Success(), 'fixture continue refused')
    except Exception as exc:
        report.update(status='REFUSED_OR_INCOMPLETE', reason=str(exc))
        if trace: report['trace'] = trace.result()
    finally:
        finalize(target, process, breaks, report, output, lldb)
    return report


def command(debugger, arguments, result, _):
    args = shlex.split(arguments)
    if len(args) != 3: result.SetError('expected profile, digest, private output'); return
    try:
        report = observe(debugger, *args)
        result.PutCString(json.dumps({k: report.get(k) for k in ('status', 'cleanup_safe', 'reason', 'detach')}))
    except Exception as exc:
        output = Path(args[2])
        if output.is_dir() and not (output/'launch-intent.json').exists() and not (output/'result.json').exists():
            write_once(output/'result.json', {'status': 'REFUSED_BEFORE_LAUNCH', 'reason': str(exc),
                                             'cleanup_safe': True, 'detach': 'NO_LAUNCH'})
        result.SetError(str(exc))


def __lldb_init_module(debugger, _):
    debugger.HandleCommand('command script add -s asynchronous -f transport.command aehl-resource-fixture')
