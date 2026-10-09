"""Keep LLDB alive until explicit safe-detach evidence; never batch or kill.

With --execute-owned-startup, install only a prepared unique own pair. All
other native state is untouched. The target remains for the user to close.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time
from core import need
from profile import read_json, validate, native_profile, transport_admission
from lldb_collector import load_native, write_once
from lifecycle import debugger_exit


def drive(profile, digest, output):
    record=validate(read_json(profile,digest))
    output=Path(output);output.mkdir(mode=0o700)
    # Collector requires an empty private directory; debugger console is a sibling.
    console=output.with_name(output.name+'-debugger.log')
    fd=os.open(console,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as log:
        env={k:v for k,v in os.environ.items() if not k.startswith('AEHL_')}
        child=subprocess.Popen(['lldb','--no-lldbinit'],stdin=subprocess.PIPE,stdout=log,stderr=log,env=env)
        commands=['command script import '+shlex.quote(str(Path(__file__).with_name('lldb_collector.py').resolve())),
                  'aehl-owned-trace '+' '.join(shlex.quote(str(x)) for x in (profile,digest,output))]
        child.stdin.write(('\n'.join(commands)+'\n').encode());child.stdin.flush()
        started=time.monotonic();attention=False
        while not (output/'result.json').exists():
            if console.stat().st_size>1048576 and not (output/'cancel').exists():
                write_once(output/'cancel',{'reason':'debugger console byte budget exceeded'})
            exitcode=child.poll()
            if exitcode is not None:
                # Separate launcher evidence never masquerades as a collector
                # result or a successful detach, even when exitcode is zero.
                failure=debugger_exit(record,exitcode,(output/'publication-intent.json').exists())
                write_once(output/'launcher-failure.json',failure)
                child.stdin.close()
                return failure
            if time.monotonic()-started>310 and not attention:
                write_once(output/'attention.json',{'status':'MANUAL_ATTENTION','reason':'No collector result; debugger preserved. Do not kill an unknown host.'});attention=True
                print('MANUAL_ATTENTION: collector result absent; debugger retained',flush=True)
            time.sleep(0.2)
        result=json.loads((output/'result.json').read_text())
        if result.get('cleanup_safe') is not True:
            print('MANUAL_ATTENTION: detach not proven; debugger retained',flush=True)
            while child.poll() is None: time.sleep(1)
            raise ValueError('manual debugger intervention; cleanup not certified')
        child.stdin.write(b'quit\n');child.stdin.flush()
        # Safe only after target detached/exited. No timeout terminate/kill fallback.
        while child.poll() is None: time.sleep(0.2)
        child.stdin.close()
    return result


def retire(manifest,digest):
    native=load_native();record=read_json(manifest,digest);base=Path(manifest).parent
    admission=read_json(base/'trace-preparation/profile.json',hashlib.sha256((base/'trace-preparation/profile.json').read_bytes()).hexdigest())
    validate(admission,check_current_source=False);need(admission['kind']=='ae-owned-startup' and admission['candidate_manifest']==str(manifest) and admission['candidate_sha256']==digest,'retirement admission differs')
    need(not native.processes(),'AE/aerender present; own installation retained in place')
    install=native.PLUGIN_ROOT/('AEHLStartupCalibration-'+record['run_id'][:12])
    need(install.is_dir() and not install.is_symlink() and set(p.name for p in install.iterdir())=={item['bundle'] for item in record['bundles']},'own retirement scope changed')
    for item in record['bundles']:need(native.common.bundle_hashes(install/item['bundle'])==item['files'],'retirement bytes changed')
    before=json.loads((base/'trace-preparation/discovery-before.json').read_text())
    after={p.name:{'inode':p.lstat().st_ino,'mtime_ns':p.lstat().st_mtime_ns} for p in native.PLUGIN_ROOT.iterdir() if p!=install}
    need(before==after,'other discovery entries changed; preserve installation')
    destination=base/'trace/retired-installation';need(not destination.exists(),'retirement destination occupied')
    need(not native.processes(),'a host opened during retirement checks')
    shutil.move(str(install),str(destination))
    write_once(base/'trace/retirement.json',{'status':'PASS','path':str(destination),'other_entries':'UNCHANGED','host_absence':'PASS'})


def execute(manifest,digest,transport,transport_digest):
    native=load_native()
    record,base,install=native.prepare(Path(manifest),digest)
    transport_admission(read_json(transport,transport_digest),record)
    need(record.get('trace_identity') is True and not native.processes(),'native admission failed')
    profile_record=native_profile(manifest,digest);validate(profile_record)
    # Persist admission and installation inventory before a possible live launch.
    preparation=base/'trace-preparation';preparation.mkdir(mode=0o700)
    profile=preparation/'profile.json';write_once(profile,profile_record)
    before={p.name:{'inode':p.lstat().st_ino,'mtime_ns':p.lstat().st_mtime_ns} for p in native.PLUGIN_ROOT.iterdir()}
    write_once(preparation/'discovery-before.json',before)
    need(not native.processes() and not install.exists(),'occupied startup admission')
    install.mkdir(mode=0o700)
    for item in record['bundles']:
        shutil.copytree(base/item['bundle'],install/item['bundle'],symlinks=True)
        need(native.common.bundle_hashes(install/item['bundle'])==item['files'],'installed own bytes differ')
        subprocess.run(['codesign','--verify','--strict',str(install/item['bundle'])],check=True,capture_output=True,timeout=30)
    write_once(preparation/'installation.json',{'status':'PASS','path':str(install),'bundles':record['bundles']})
    result=drive(str(profile),hashlib.sha256(profile.read_bytes()).hexdigest(),base/'trace')
    # This separate witness is required for the public result, even if registers matched.
    control=Path(record['config']['calibration_control']);receipt={'status':'NOT_RUN'}
    if result.get('publication')=='UNKNOWN':
        receipt={'status':'UNKNOWN','reason':'debugger ended without collector result; request outcome unknown'}
    if result.get('publication')=='SENT_ONCE':
        intent=json.loads((base/'trace/publication-intent.json').read_text())
        deadline=intent['monotonic_deadline']
        while not (control/'result').exists() and time.monotonic()<deadline:
            need(native.common.process_identity(result['pid'])==result['owned_process'],'owned process changed while awaiting receipt')
            time.sleep(0.1)
        if (control/'result').exists():
            try:
                receipt=native.verify_observation(record,native.common.read(control/'result',4096),
                     [native.common.read(control/('names-'+str(i)),32768) for i in range(3)])
                need(receipt['installed_key']==result.get('key'),'SDK key differs from trace');receipt['status']='PASS'
            except Exception as exc:receipt={'status':'FAIL_OR_UNKNOWN','reason':str(exc)}
        else:receipt={'status':'UNKNOWN','reason':'original request deadline expired; no retry'}
    write_once(base/'trace/sdk-receipt.json',receipt)
    write_once(base/'trace/final.json',{'identity':result['status'],'sdk':receipt,'host_close':'MANUAL_REQUIRED',
        'late_add':'NOT_RUN','C1':'PARTIAL','C2':'NOT_RUN','private_append':'BLOCKED'})
    print(json.dumps({'trace':str(base/'trace'),'identity':result['status'],'sdk':receipt,'pid':result.get('pid')}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--transport-proof');parser.add_argument('--transport-sha256');parser.add_argument('--profile');parser.add_argument('--manifest')
    parser.add_argument('--sha256',required=True);parser.add_argument('--output');parser.add_argument('--retire-owned-pair',action='store_true');parser.add_argument('--execute-owned-startup',action='store_true')
    args=parser.parse_args()
    if args.retire_owned_pair:
        need(args.manifest and not args.profile and not args.execute_owned_startup,'retirement mode only')
        retire(args.manifest,args.sha256)
    elif args.manifest:
        need(args.execute_owned_startup and args.transport_proof and args.transport_sha256 and not args.profile and not args.output,'explicit unique startup execution required')
        execute(args.manifest,args.sha256,args.transport_proof,args.transport_sha256)
    else:
        record=validate(read_json(args.profile,args.sha256));need(record['kind']=='owned-fixture' and args.output and not args.execute_owned_startup,'only owned fixture permitted')
        print(json.dumps(drive(args.profile,args.sha256,args.output)))
