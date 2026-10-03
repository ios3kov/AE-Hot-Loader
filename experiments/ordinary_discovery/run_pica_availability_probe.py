"""Explicit one-shot PICA request/observer. Does not install, launch or stop AE.

Runtime preparation reads the identified process only after an explicit live
invocation. Core byte/manifest verification functions are usable offline.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time

import run_no_scan_directory_probe as common
from build_pica_availability_probe import EXPECTED_HOST, HOST_SHA

SPECS = [('SP Plug-ins Suite', 4), ('SP Plug-ins Suite', 6), ('SP Access Suite', 3), ('SP Adapters Suite', 3)]


def unique_json(pairs):
    result = {}
    for key, value in pairs:
        common.require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def private_read(path, limit=4*1024*1024):
    common.no_links(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        common.require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and
                       before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600 and
                       0 <= before.st_size <= limit, 'invalid private evidence')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        after = os.fstat(fd)
        common.require(len(data) == before.st_size and
                       (before.st_dev,before.st_ino,before.st_mode,before.st_size,before.st_mtime_ns,before.st_ctime_ns) ==
                       (after.st_dev,after.st_ino,after.st_mode,after.st_size,after.st_mtime_ns,after.st_ctime_ns),
                       'private evidence changed during read')
        return data
    finally:
        os.close(fd)


def fields(data):
    text = data.decode('ascii')
    common.require(text.endswith('\n') and len(text) <= 4*1024*1024, 'incomplete fields')
    out = []
    for line in text.splitlines():
        key, sep, value = line.partition('=')
        common.require(sep and re.fullmatch('[a-z0-9_-]+', key) is not None, 'bad field')
        out.append((key, value))
    return out


def decode_hex(value, limit):
    common.require(len(value) <= limit*2 and len(value)%2 == 0 and
                   re.fullmatch('[0-9a-f]*', value) is not None, 'invalid hex')
    return bytes.fromhex(value)


def request(record, identity):
    token = record['activation_env']['AEHL_PICA_AVAILABILITY_TOKEN']
    return ('schema=PICA-REQUEST-1\nkind=pica-availability\nrun='+record['run_id']+
            '\nsource='+record['source_commit']+'\nbuild='+record['build_id']+
            '\npid='+str(identity['pid'])+'\nstart='+identity['start']+'\ntoken='+token+
            '\nbinary_sha256='+record['binary_sha256']+
            '\npotential_suite_load=authorized\nadapter_enumeration=authorized\n').encode()


def manifest(path, expected_hash):
    path = Path(path)
    raw = private_read(path, 2*1024*1024)
    common.require(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash changed')
    r = json.loads(raw, object_pairs_hook=unique_json)
    common.require(r['kind'] == 'research-only-pica-availability-aegp' and r['source_clean'] is True and
                   r['target'] == 'aarch64-apple-darwin' and
                   re.fullmatch('pica-[0-9a-f]{12}', r['build_id']) is not None and
                   re.fullmatch('pica-availability-[0-9a-f]{32}', r['run_id']) is not None and
                   re.fullmatch('[0-9a-f]{40}', r['source_commit']) is not None and
                   r['host_executable'] == str(EXPECTED_HOST) and r['host_sha256'] == HOST_SHA and
                   r['installation_performed'] is False and r['ae_launch_performed'] is False,
                   'unsupported candidate identity/scope')
    for key in ('build_sign_exports','identity_getter','inert_entrypoint'):
        common.require(r['checks'][key] == 'PASS', 'candidate prerequisite missing')
    common.require(r['checks']['live_ae'] == 'NOT RUN' and r['native_timeout_ms'] == 10000 and
                   r['external_timeout_ms'] == 30000 and
                   r['suite_scope'] == [{'name':n,'version':v} for n,v in SPECS], 'changed diagnostic scope')
    folder = path.parent.resolve()
    common.require(Path(r['control_directory']) == folder/'control', 'control retargeted')
    bundle = Path(r['candidate_bundle']);stem = 'AEHLPica'+r['build_id'][5:]
    common.require(bundle == folder/(stem+'.plugin') and
                   Path(r['module_path']) == Path(r['prospective_bundle'])/'Contents/MacOS'/stem,
                   'candidate path retargeted')
    common.require(common.bundle_hashes(bundle) == r['files'], 'candidate bytes changed')
    common.require(common.sha_trusted_binary(bundle/'Contents/MacOS'/stem) == r['binary_sha256'],
                   'candidate executable changed')
    token = r['activation_env']['AEHL_PICA_AVAILABILITY_TOKEN']
    common.require(re.fullmatch('[0-9a-f]{32}', token) is not None, 'bad token')
    common.private_directory(r['control_directory'])
    return r


def prepare(r, expected_bundle, identity_fn=common.process_identity):
    common.require(str(expected_bundle) == r['prospective_bundle'], 'installation scope differs')
    common.require(common.bundle_hashes(expected_bundle) == r['files'], 'installed candidate changed')
    common.require(common.sha_trusted_binary(EXPECTED_HOST) == HOST_SHA, 'host file changed')
    ready = private_read(Path(r['control_directory'])/'ready.txt', 4096).decode().splitlines()
    common.require(len(ready) == 4, 'invalid readiness')
    identity = json.loads(ready[0], object_pairs_hook=unique_json)
    common.require(identity == {k:r[k] for k in ('build_id','run_id','source_commit','source_clean','target','kind')},
                   'wrong loaded build')
    common.require(re.fullmatch('pid=[1-9][0-9]*',ready[1]) is not None and
                   re.fullmatch(r'start=[0-9]+\.[0-9]+',ready[2]) is not None and
                   ready[3] == 'module_hex='+os.fsencode(r['module_path']).hex(), 'invalid runtime binding')
    pid=int(ready[1][4:]);observed=identity_fn(pid)
    common.require(observed == {'pid':pid,'start':ready[2][6:],'executable':r['host_executable']},
                   'host PID/start/executable changed')
    control=Path(r['control_directory'])
    common.require({p.name for p in control.iterdir()} == {'ready.txt'}, 'stale/consumed control')
    return observed, request(r,observed)


def envelope(r, observed, name):
    pairs=fields(private_read(Path(r['control_directory'])/(name+'.txt')))
    common.require(len({k for k,v in pairs}) == len(pairs), 'duplicate journal field')
    d=dict(pairs)
    expected=dict(schema='PICA-JOURNAL-1',run=r['run_id'],source=r['source_commit'],build=r['build_id'],
                  pid=str(observed['pid']),start=observed['start'],module_hex=os.fsencode(r['module_path']).hex(),
                  binary_sha256=r['binary_sha256'],phase=name)
    common.require(set(d)==set(expected)|{'data_hex'} and all(d[k]==v for k,v in expected.items()),
                   'journal identity changed')
    return decode_hex(d['data_hex'],2*1024*1024)


def verify(r, observed):
    terminal=private_read(Path(r['control_directory'])/'terminal.txt', 65536)
    pairs=fields(terminal)
    common.require(len(pairs)>=2 and pairs[:2] == [('schema','PICA-AVAILABILITY-1'),('status','COMPLETE')],
                   'diagnostic stopped/incomplete; preserve evidence')
    common.require(envelope(r,observed,'result')==terminal and
                   envelope(r,observed,'claim')==request(r,observed), 'terminal/claim differ')
    envelope(r,observed,'before-started');envelope(r,observed,'after-started')
    before=envelope(r,observed,'before');after=envelope(r,observed,'after')
    common.require(before==after and len(before.splitlines())==3, 'host/project/registry changed')
    observation=[decode_hex(x.decode(),1024*1024) for x in before.splitlines()]
    expected=(str(observed['pid'])+':'+observed['start']+':'+r['host_executable']+':'+r['module_path']+':'+r['binary_sha256']).encode()
    common.require(observation[0]==expected and re.fullmatch(rb'25\.6x101:blank-clean-idle:[1-9][0-9]*',observation[1])
                   is not None and observation[2], 'invalid native baseline')
    at=0
    def take(key):
        nonlocal at
        common.require(at<len(pairs) and pairs[at][0]==key,'missing/out-of-order '+key)
        value=pairs[at][1];at+=1;return value
    common.require(take('schema')=='PICA-AVAILABILITY-1' and take('status')=='COMPLETE' and
                   take('stage')=='complete' and take('reason_hex')=='' and take('suite_count')=='4', 'incomplete result')
    suites=[]
    for i,(name,version) in enumerate(SPECS):
        envelope(r,observed,'acquire-started-'+str(i));envelope(r,observed,'acquire-finished-'+str(i))
        common.require(take('suite_name_hex')==name.encode().hex() and take('suite_version')==str(version),'wrong suite')
        error=take('acquire_error');present=take('provider_present')
        common.require(re.fullmatch('-?[0-9]+',error) is not None and -(2**31)<=int(error)<2**31 and
                       present in ('0','1') and (int(error)==0)==(present=='1'),'invalid acquisition result')
        suites.append(dict(name=name,version=version,error=int(error),provider_present=present=='1'))
    enumeration=take('enumeration_complete');count=take('adapter_count')
    common.require(enumeration in ('0','1') and count.isdigit() and int(count)<=64 and
                   (enumeration=='1')==suites[-1]['provider_present'] and
                   (enumeration=='1' or count=='0'),'incomplete enumeration')
    adapters=[]
    for i in range(int(count)):
        name=decode_hex(take('adapter_name_hex'),256);version=take('adapter_version')
        common.require(name and b'\0' not in name and re.fullmatch('-?[0-9]+',version) is not None and
                       -(2**31)<=int(version)<2**31,'bad adapter')
        adapters.append(dict(name_hex=name.hex(),version=int(version)))
        envelope(r,observed,'next-started-'+str(i));envelope(r,observed,'next-finished-'+str(i))
    common.require(at==len(pairs), 'trailing result fields')
    if enumeration=='1':
        for name in ('iterator-started','iterator-delete-started','iterator-deleted','next-started-'+count):
            envelope(r,observed,name)
    images=[]
    for i in range(2):
        lines=private_read(Path(r['control_directory'])/('images-'+str(i)+'.txt')).decode('ascii').splitlines()
        parsed=[]
        for line in lines:
            path,header,slide=line.split(',');raw=decode_hex(path,4096)
            common.require(raw.startswith(b'/') and header.isdigit() and int(header)>0 and
                           re.fullmatch('-?[0-9]+',slide) is not None,'invalid image')
            parsed.append((raw,header,slide))
        common.require(parsed and len(set(parsed))==len(parsed), 'invalid image inventory')
        images.append(parsed)
    common.require(set(images[0])<=set(images[1]), 'preexisting image removed/changed')
    evidence={p.name:hashlib.sha256(private_read(p)).hexdigest() for p in Path(r['control_directory']).iterdir() if p.is_file()}
    return dict(evidence_sha256=evidence,status='COMPLETE',scope='suite availability/adapter enumeration only',suites=suites,adapters=adapters,
                added_image_paths_hex=[x[0].hex() for x in images[1] if x not in images[0]],
                ordinary_effect_registration='NOT RUN',apply_render='NOT RUN')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--manifest-sha256',required=True)
    p.add_argument('--expected-bundle',type=Path,required=True)
    p.add_argument('--authorize-potential-suite-load',action='store_true')
    p.add_argument('--authorize-adapter-enumeration',action='store_true')
    args=p.parse_args()
    if not (args.authorize_potential_suite_load and args.authorize_adapter_enumeration):
        p.error('explicit authorized diagnostic scope required')
    r=manifest(args.manifest,args.manifest_sha256);observed,body=prepare(r,args.expected_bundle)
    control=Path(r['control_directory']);common.publish(control,body)
    deadline=time.monotonic()+30
    while not (control/'terminal.txt').exists() and time.monotonic()<deadline:time.sleep(0.1)
    result=dict(status='TIMEOUT',scope='no process termination; no retry')
    if (control/'terminal.txt').exists():
        try:result=verify(r,observed)
        except (ValueError,KeyError,OSError,UnicodeError):result=dict(status='STOPPED',scope='native evidence incomplete; preserve')
    result.update(source=r['source_commit'],build=r['build_id'],run=r['run_id'],pid=observed['pid'],start=observed['start'])
    common.write_json_exclusive(control/'external-result.json',result)
    print(json.dumps(result,indent=2));return 0 if result['status']=='COMPLETE' else 2


if __name__=='__main__':raise SystemExit(main())
