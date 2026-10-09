"""Keep LLDB alive until explicit safe-detach evidence; never batch or kill.

With --execute-owned-startup, install only a prepared unique own pair. All
other native state is untouched. The target remains for the user to close.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time
from core import need
from profile import read_json, validate, native_profile, transport_admission
from lldb_collector import load_native, write_once
from lifecycle import debugger_exit
import timeline


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


def observation_receipt(native, record, control, key):
    raw=native.common.read(control/'result',4096)
    result=native.fields(raw,'AEHL-CAL-RESULT-2')
    need(result.get('build')==record['build_id'],'native result build differs')
    if result.get('status') in ('REFUSED','PARTIAL_UNKNOWN'):
        stage=result.get('stage','')
        need(re.fullmatch(r'[a-z][a-z0-9-]{0,79}',stage) is not None,'invalid refusal stage')
        cleanup=result.get('cleanup','UNKNOWN')
        need(cleanup in ('PASS','FAIL','UNKNOWN'),'invalid refusal cleanup')
        receipt={'status':result['status'],'stage':stage,'cleanup':cleanup,
                 'scope':'native observation refusal; no samples accepted'}
        if 'suite' in result:
            need(re.fullmatch(r'[A-Za-z][A-Za-z0-9 ._-]{0,79}',result['suite']) is not None,'invalid suite diagnostic')
            version=result.get('suite_version','')
            need(re.fullmatch(r'[1-9][0-9]{0,8}',version) is not None,'invalid suite version')
            receipt.update(suite=result['suite'],suite_version=int(version))
        if 'host_error' in result:
            error=result['host_error']
            need(re.fullmatch(r'-?(0|[1-9][0-9]{0,9})',error) is not None and
                 -(2**31)<=int(error)<2**31,'invalid host error diagnostic')
            receipt['host_error']=int(error)
        keys = ('mismatch_relative_offset', 'mismatch_file_offset', 'mismatch_expected_word', 'mismatch_actual_word')
        if any(k.startswith('mismatch_') for k in result):
            need(stage == 'resident-text-mismatch' and all(k in result for k in keys) and
                 {k for k in result if k.startswith('mismatch_')} == set(keys), 'invalid mismatch schema')
            values = {}
            for k, limit in zip(keys, (64*1024*1024, 256*1024*1024, 2**32, 2**32)):
                value = result[k]
                need(re.fullmatch(r'0|[1-9][0-9]{0,9}', value) is not None and int(value) < limit,
                     'invalid mismatch diagnostic')
                values[k] = int(value)
            need(values[keys[1]] >= values[keys[0]] and
                 (values[keys[1]] - values[keys[0]]) % 4 == 0 and
                 values[keys[2]] != values[keys[3]], 'inconsistent mismatch diagnostic')
            byte = values[keys[0]] % 4
            need((values[keys[2]] >> (8*byte)) & 255 != (values[keys[3]] >> (8*byte)) & 255,
                 'reported first byte is equal')
            mask = (1 << (8*byte)) - 1
            need(values[keys[2]] & mask == values[keys[3]] & mask, 'earlier instruction byte differs')
            receipt['own_text_difference'] = {k.removeprefix('mismatch_'): v for k,v in values.items()}
        return receipt
    need(result.get('status')=='LISTED_OBSERVED' and result.get('cleanup')=='PASS' and
         result.get('cleanup_safe')=='YES' and result.get('stage')=='registry-observation' and
         result.get('render')==result.get('apply')=='NOT_RUN','read-only observation incomplete')
    # Only a matching successful header permits reading the three sample files.
    receipt=native.verify_observation(record,raw,
        [native.common.read(control/('names-'+str(i)),32768) for i in range(3)])
    need(receipt['installed_key']==key,'SDK key differs from trace')
    receipt['status']='PASS'
    return receipt


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
                receipt=observation_receipt(native,record,control,result.get('key'))
            except Exception as exc:receipt={'status':'FAIL_OR_UNKNOWN','reason':str(exc)}
        else:receipt={'status':'UNKNOWN','reason':'original request deadline expired; no retry'}
    write_once(base/'trace/sdk-receipt.json',receipt)
    # Independent optional evidence; a malformed/missing timing record never
    # converts a refused/unknown SDK operation into success or a replay.
    timing={'status':'UNKNOWN','scope':'timing only; SDK receipt unchanged'}
    try:
        published=read_json(base/'trace/publication-timing.json',
            hashlib.sha256((base/'trace/publication-timing.json').read_bytes()).hexdigest())
        owned=result['owned_process'];birth=native.birth(owned)
        need(published['status']=='OBSERVED' and (published['pid'],published['birth'],published['build_id'])==
             (owned['pid'],birth,record['build_id']),'publication timing identity differs')
        rows={}
        for phase,leaf in enumerate(timeline.LEAVES):
            if (control/leaf).exists():
                rows[leaf]=timeline.parse_native(native.common.read(control/leaf,2048),record['build_id'],owned['pid'],birth,phase)
        need('request-received' in rows,'first receipt timing absent')
        timing={'status':'OBSERVED','publication':published,'native':rows,
                'delivery':timeline.compare(published['sample'],rows['request-received']['sample'],published['deadline'])}
        if 'request-deadline-check' in rows:
            need(rows['request-deadline-check']['deadline']==published['deadline'],'native timing deadline differs')
            timing['deadline_check']=timeline.compare(published['sample'],rows['request-deadline-check']['sample'],published['deadline'])
    except Exception:
        timing={'status':'UNKNOWN','scope':'missing/invalid timing; SDK receipt unchanged; no retry'}
    write_once(base/'trace/request-timeline.json',timing)
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
