"""One authorized public PICA inventory; does not install, launch or stop AE."""
import argparse
import hashlib
import json
import os
import plistlib
from pathlib import Path
import re
import time
import run_no_scan_directory_probe as common
from build_pica_availability_probe import EXPECTED_HOST, HOST_SHA
from run_pica_availability_probe import private_read, fields, decode_hex, unique_json, envelope

SPECS=[('SP Plug-ins Suite',4),('SP Adapters Suite',3)]


def request(r,identity):
    token=r['activation_env']['AEHL_PICA_INVENTORY_TOKEN']
    return ('schema=PICA-REQUEST-1\nkind=pica-inventory\nrun='+r['run_id']+'\nsource='+r['source_commit']+
      '\nbuild='+r['build_id']+'\npid='+str(identity['pid'])+'\nstart='+identity['start']+'\ntoken='+token+
      '\nbinary_sha256='+r['binary_sha256']+'\npotential_suite_load=authorized\nplugin_inventory=authorized\n').encode()


def known_files(r):
    common.require(len(r['known_effects'])==2,'changed known-effect scope')
    specs=[('AEHotLoaderControlShell','OS3KOV.AEHotLoader.ControlShell','core/build.rs'),
           ('AEHotLoaderRustProbe','OS3KOV.AEHotLoader.RustProbe','experiments/rust_effect_probe/build.rs')]
    root=Path('/Users/os3kov/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore')
    repo=Path(__file__).resolve().parents[2]
    for k,(stem,match,source) in zip(r['known_effects'],specs):
        bundle=root/(stem+'.plugin')
        common.require(k['bundle']==str(bundle) and k['module']==str(bundle/'Contents/MacOS'/stem) and
          k['resource']==str(bundle/'Contents/Resources'/(stem+'.rsrc')) and k['match']==match and
          k['match_source']==source and k['info']==str(bundle/'Contents/Info.plist'),'known-effect retargeted')
        common.require(common.sha_trusted_binary(k['module'])==k['sha'] and
          common.sha_trusted_binary(k['resource'])==k['resource_sha'] and
          common.sha_trusted_binary(k['info'])==k['info_sha256'] and
          plistlib.loads(Path(k['info']).read_bytes()).get('CFBundleExecutable')==stem and
          match.encode('ascii') in Path(k['resource']).read_bytes() and
          hashlib.sha256((repo/source).read_bytes()).hexdigest()==k['match_source_sha256'], 'known-effect/source bytes changed')


def manifest(path,digest):
    path=Path(path);raw=private_read(path,2*1024*1024)
    common.require(hashlib.sha256(raw).hexdigest()==digest,'manifest hash changed')
    r=json.loads(raw,object_pairs_hook=unique_json)
    common.require(r['kind']=='research-only-pica-inventory-aegp' and r['source_clean'] is True and
      r['target']=='aarch64-apple-darwin' and re.fullmatch('inventory-[0-9a-f]{12}',r['build_id']) is not None and
      re.fullmatch('pica-inventory-[0-9a-f]{32}',r['run_id']) is not None and
      re.fullmatch('[0-9a-f]{40}',r['source_commit']) is not None and r['host_executable']==str(EXPECTED_HOST) and
      r['host_sha256']==HOST_SHA and r['installation_performed'] is False and r['ae_launch_performed'] is False,
      'unsupported identity/scope')
    common.require(r['checks']==dict(build_sign_exports='PASS',identity_getter='PASS',inert_entrypoint='PASS',live_ae='NOT RUN') and
      r['native_timeout_ms']==10000 and r['external_timeout_ms']==30000 and r['plugin_limit']==2048 and r['inventory_payload_limit']==1024*1024 and
      r['path_contract']=='revision-4 value FSRef, FSRefMakePath; no CFURL' and
      r['suite_scope']==[dict(name=n,version=v) for n,v in SPECS],'changed scope/prerequisites')
    folder=path.parent.resolve();stem='AEHLInventory'+r['build_id'][10:]
    common.require(Path(r['control_directory'])==folder/'control' and Path(r['candidate_bundle'])==folder/(stem+'.plugin') and
      Path(r['module_path'])==Path(r['prospective_bundle'])/'Contents/MacOS'/stem,'retargeted paths')
    common.require(common.bundle_hashes(r['candidate_bundle'])==r['files'] and
      common.sha_trusted_binary(Path(r['candidate_bundle'])/'Contents/MacOS'/stem)==r['binary_sha256'],'candidate changed')
    common.require(re.fullmatch('[0-9a-f]{32}',r['activation_env']['AEHL_PICA_INVENTORY_TOKEN']) is not None,'bad token')
    known_files(r);common.private_directory(r['control_directory']);return r


def prepare(r,expected_bundle,identity_fn=common.process_identity):
    common.require(str(expected_bundle)==r['prospective_bundle'] and
      common.bundle_hashes(expected_bundle)==r['files'],'installed candidate changed/retargeted')
    common.require(common.sha_trusted_binary(EXPECTED_HOST)==HOST_SHA,'host changed');known_files(r)
    ready=private_read(Path(r['control_directory'])/'ready.txt',4096).decode().splitlines()
    common.require(len(ready)==4 and json.loads(ready[0],object_pairs_hook=unique_json)==
      {k:r[k] for k in ('build_id','run_id','source_commit','source_clean','target','kind')},'wrong readiness')
    common.require(re.fullmatch('pid=[1-9][0-9]*',ready[1]) is not None and
      re.fullmatch(r'start=[0-9]+\.[0-9]+',ready[2]) is not None and
      ready[3]=='module_hex='+os.fsencode(r['module_path']).hex(),'runtime binding changed')
    observed=identity_fn(int(ready[1][4:]))
    common.require(observed==dict(pid=int(ready[1][4:]),start=ready[2][6:],executable=r['host_executable']), 'process changed')
    common.require({p.name for p in Path(r['control_directory']).iterdir()}=={'ready.txt'},'stale/consumed control')
    return observed,request(r,observed)


def correlation(plugins,known):
    result=[]
    for k in known:
        expected={os.fsencode(k['bundle']),os.fsencode(k['module'])}
        hits=[i for i,p in enumerate(plugins) if bytes.fromhex(p['path_hex']) in expected]
        state='LISTED' if hits else 'UNKNOWN' if any(not p['path_hex'] for p in plugins) else 'NOT_LISTED'
        result.append(dict(match=k['match'],state=state,entry_indices=hits,
                           meaning='exact known-file correlation; no publication/apply/render proof'))
    return result


def verify(r,observed):
    control=Path(r['control_directory']);terminal=private_read(control/'terminal.txt',4*1024*1024)
    pairs=fields(terminal)
    common.require(envelope(r,observed,'result')==terminal and envelope(r,observed,'claim')==request(r,observed),'result/claim differ')
    for name in ('before-started','after-started','iterator-started','iterator-delete-started','iterator-deleted'):envelope(r,observed,name)
    before=envelope(r,observed,'before');common.require(before==envelope(r,observed,'after'),'host/project/registry changed')
    lines=before.splitlines();common.require(len(lines)==3,'bad observation')
    identity,project,registry=[decode_hex(x.decode(),1024*1024) for x in lines]
    expected=(str(observed['pid'])+':'+observed['start']+':'+r['host_executable']+':'+r['module_path']+':'+r['binary_sha256']).encode()
    common.require(identity==expected and re.fullmatch(rb'25\.6x101:blank-clean-idle:[1-9][0-9]*',project) is not None and registry,'bad baseline')
    known_payload=''.join(k['module'].encode().hex()+','+k['sha']+','+k['resource_sha']+','+k['match'].encode().hex()+'\n' for k in r['known_effects']).encode()
    common.require(envelope(r,observed,'known-before')==known_payload and envelope(r,observed,'known-after')==known_payload and
      all(k['match'].encode() in registry.splitlines() for k in r['known_effects']),'known-file/registry evidence differs')
    at=0
    def take(key):
        nonlocal at
        common.require(at<len(pairs) and pairs[at][0]==key,'missing/out-of-order '+key)
        v=pairs[at][1];at+=1;return v
    def integer(key):
        v=take(key);common.require(re.fullmatch('-?[0-9]+',v) is not None and -(2**31)<=int(v)<2**31,'bad integer');return int(v)
    common.require(take('schema')=='PICA-INVENTORY-1' and take('status')=='COMPLETE' and take('stage')=='complete' and
      take('reason_hex')=='' and take('suite_count')=='2','stopped/incomplete inventory')
    for i,(name,version) in enumerate(SPECS):
        for phase in ('acquire-started-','acquire-finished-'):envelope(r,observed,phase+str(i))
        common.require(take('suite_name_hex')==name.encode().hex() and integer('suite_version')==version and
          integer('acquire_error')==0 and take('provider_present')=='1','suite unavailable/changed')
    common.require(take('enumeration_complete')=='1','incomplete enumeration');count=integer('plugin_count')
    common.require(0<=count<=2048,'plugin count out of bounds');plugins=[]
    for i in range(count):
        start=at;file_error=integer('file_error');path_error=integer('path_error');path=decode_hex(take('path_hex'),4095)
        adapter_error=integer('adapter_error');name_error=integer('name_error');version_error=integer('version_error')
        adapter=decode_hex(take('adapter_name_hex'),256);version=integer('adapter_version')
        common.require((file_error==0 and path_error==0)==bool(path) and (not path or path.startswith(b'/')) and
          b'\0' not in path and b'\0' not in adapter and
          (adapter_error==0 and name_error==0 and version_error==0)==bool(adapter) and
          not(file_error!=0 and path_error!=0) and not(adapter_error!=0 and (name_error!=0 or version_error!=0)), 'getter-contract mismatch')
        envelope(r,observed,'next-started-'+str(i))
        delta=''.join(k+'='+v+'\n' for k,v in pairs[start:at]).encode()
        common.require(envelope(r,observed,'next-finished-'+str(i))==delta,'entry delta differs from terminal')
        plugins.append(dict(file_error=file_error,path_error=path_error,path_hex=path.hex(),adapter_error=adapter_error,
          name_error=name_error,version_error=version_error,adapter_name_hex=adapter.hex(),adapter_version=version))
    common.require(at==len(pairs),'trailing fields');envelope(r,observed,'next-started-'+str(count))
    images=[]
    for i in range(2):
        values=[]
        for line in private_read(control/('images-'+str(i)+'.txt')).decode('ascii').splitlines():
            path,header,slide=line.split(',');raw=decode_hex(path,4096)
            common.require(raw.startswith(b'/') and header.isdigit() and int(header)>0 and
              re.fullmatch('-?[0-9]+',slide) is not None,'bad image')
            values.append((raw,header,slide))
        common.require(values and len(set(values))==len(values),'bad image inventory');images.append(values)
    common.require(set(images[0])<=set(images[1]),'preexisting image removed/changed')
    return dict(status='COMPLETE',scope='public PICA plug-in inventory/correlation only',plugins=plugins,
      known_effects=correlation(plugins,r['known_effects']),
      added_image_paths_hex=[x[0].hex() for x in images[1] if x not in images[0]],
      evidence_sha256={p.name:hashlib.sha256(private_read(p)).hexdigest() for p in control.iterdir() if p.is_file()},
      ordinary_effect_registration='NOT RUN',apply_render='NOT RUN')


def supervise(r,observed,publish_fn=common.publish,clock=time.monotonic,sleep=time.sleep):
    control=Path(r['control_directory']);publish_fn(control,request(r,observed));deadline=clock()+30
    while not (control/'terminal.txt').exists() and clock()<deadline:sleep(0.1)
    result=dict(status='TIMEOUT',scope='preserve process and partial evidence; no retry')
    if (control/'terminal.txt').exists():
        try:result=verify(r,observed)
        except (ValueError,KeyError,OSError,UnicodeError):result=dict(status='STOPPED',scope='incomplete native evidence; preserve')
    result.update(source=r['source_commit'],build=r['build_id'],run=r['run_id'],pid=observed['pid'],start=observed['start'])
    common.write_json_exclusive(control/'external-result.json',result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--manifest-sha256',required=True);p.add_argument('--expected-bundle',type=Path,required=True)
    p.add_argument('--authorize-potential-suite-load',action='store_true');p.add_argument('--authorize-plugin-inventory',action='store_true')
    args=p.parse_args()
    if not(args.authorize_potential_suite_load and args.authorize_plugin_inventory):p.error('explicit authorized scope required')
    r=manifest(args.manifest,args.manifest_sha256);observed,_=prepare(r,args.expected_bundle)
    result=supervise(r,observed);print(json.dumps(result,indent=2));return 0 if result['status']=='COMPLETE' else 2


if __name__=='__main__':raise SystemExit(main())
