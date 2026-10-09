"""Exact image/site admission. Preparing a profile performs no host operation."""
import hashlib
import json
import os
import stat
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import FIELDS, need
from image import Image

ROOT = Path(__file__).resolve().parents[2]
HOST = Path('/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects')
HOST_SHA = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'
BASE = HOST.parents[1]
COLLECTOR_SOURCES=tuple('experiments/startup_trace/'+name for name in ('core.py','image.py','profile.py','lldb_collector.py','launch.py','fixture.py','fixture.cpp','stops.py'))

def collector_hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in COLLECTOR_SOURCES}

def transport_admission(proof, candidate):
    need(proof.get('kind')=='owned-fixture' and proof.get('status')=='IDENTITY_OBSERVED' and proof.get('phase')=='complete' and
         proof.get('cleanup_safe') is True and proof.get('accepted_events')==12 and proof.get('stops')==15 and
         proof.get('collector_sha256')==collector_hashes() and proof.get('source_commit')==candidate['source']['commit'],
         'exact collector transport proof missing or stale; AE install/launch prohibited')
    host=Path(proof.get('owned_process',{}).get('executable',''))
    need(host.name=='aehl-trace-fixture' and host.parent.parent==ROOT/'build-ae-hot-loader' and host.parent.name.startswith('trace-fixture-'), 'transport process outside fixture scope')
PINS = {
 'PS': (BASE/'Frameworks/PluginSupport.framework/Versions/A/PluginSupport', '4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832', '64c01ac4-2413-3463-8822-17ee5543052a'),
 'FLT': (BASE/'Frameworks/FLT.dylib', '227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256', 'c8786a71-e313-3b20-9494-359fb56d705a'),
 'AEGP': (BASE/'Required/AEGPDriver.plugin/Contents/MacOS/AEGPDriver', '3d7a4a24505bb06d19509da4bacf963cf5e0b2b647a0791cbfdeccf6f496e778', 'a1e61d11-11e0-31e5-80fc-1a594c5d1f31'),
}
# Each offset is immediately before the pinned instruction. Register operands
# were checked against complete original bodies, not inferred from names.
SITES = {
 'convert': ('PS', 0x4b754, 'ff4303d1', {'context':'x0'}),
 'pipl': ('PS', 0x4b87c, 'e02700f9', {'pipl':'x0'}),
 'spec': ('FLT', 0x8d2f0, 'c80640f9', {'pipl':'x0','descriptor':'x24'}),
 'writer': ('FLT', 0x50a0, '080040f9', {'descriptor':'x0','root':'x20'}),
 'index': ('FLT', 0x5304, 'e00314aa', {'descriptor':'x9','index':'w8','root':'x20'}),
 'writer_return': ('FLT', 0x5320, 'fd7b4aa9', {'root':'x20'}),
 'match': ('AEGP', 0x42554, 'ff0303d1', {'key':'w0'}),
 'lookup': ('FLT', 0x4c14, '8002803d', {'descriptor':'v0.low','owner':'v0.high','root':'x21','index':'w22'}),
}
BOUNDARIES = {
 'marker': {'stage':'w0','context':'x1','callback':'x2','status':'w3','main':'w4'},
 'reader': {'stage':'w0','key':'w1','function':'x2','status':'w3','main':'w4'},
}


def fixture_site(im, role):
    offset=im.symbol('_lookup_probe' if role=='lookup' else '_'+role)
    registers={'descriptor':'v0.low','owner':'v0.high','root':'x21','index':'w22'} if role=='lookup' else {field:'x'+str(i) for i,field in enumerate(FIELDS[role])}
    return {'module':'fixture','offset':offset,'word':im.bytes(offset).hex(),'registers':registers}


def read_json(path, digest):
    p=Path(path); need(p.is_absolute() and not any(q.is_symlink() for q in (p,*p.parents)), 'profile path/symlink')
    st=p.stat();need(stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and st.st_mode&0o077==0 and st.st_size<=4*1024*1024, 'profile ownership/mode/byte budget'); raw=p.read_bytes()
    after=p.stat();need((st.st_dev,st.st_ino,st.st_mtime_ns,st.st_size)==(after.st_dev,after.st_ino,after.st_mtime_ns,after.st_size),'profile changed')
    need(hashlib.sha256(raw).hexdigest()==digest, 'profile digest differs')
    def unique(pairs):
        d={}
        for k,v in pairs: need(k not in d, 'duplicate JSON key'); d[k]=v
        return d
    return json.loads(raw, object_pairs_hook=unique)


def image_record(path):
    im=Image(path); return {'path':str(im.path),'sha256':im.sha256,'uuid':im.uuid}


def native_profile(manifest, digest):
    # Use existing exact candidate/bundle/source/config checks; no install or run.
    import importlib.util
    sp=importlib.util.spec_from_file_location('trace_calibration_run', ROOT/'experiments/startup_calibration/run.py')
    native=importlib.util.module_from_spec(sp);sp.loader.exec_module(native)
    record,base,install=native.prepare(Path(manifest),digest)
    need(record.get('trace_identity') is True, 'candidate has no trace sentinels')
    modules={}; sites={}
    for label,(p,h,u) in PINS.items():
        pin=image_record(p);need(pin['sha256']==h and pin['uuid']==u,'provider pin differs');modules[label]=pin
    for role,(label,offset,word,regs) in SITES.items():
        need(Image(modules[label]['path']).bytes(offset).hex()==word, 'decoded site changed')
        sites[role]={'module':label,'offset':offset,'word':word,'registers':regs}
    for role,item,symbol in [('marker',record['bundles'][0],'_AEHL_TraceMarkerBoundary'),('reader',record['bundles'][1],'_AEHL_TraceReaderBoundary')]:
        path=base/item['bundle']/'Contents/MacOS'/Path(item['bundle']).stem; im=Image(path)
        need(im.sha256==item['binary_sha256'],'candidate image differs');offset=im.symbol(symbol)
        modules[role]=image_record(path);modules[role]['loaded_path']=str(install/item['bundle']/'Contents/MacOS'/Path(item['bundle']).stem)
        sites[role]={'module':role,'offset':offset,'word':im.bytes(offset).hex(),'registers':BOUNDARIES[role]}
    host=image_record(HOST);need(host['sha256']==HOST_SHA,'host pin differs')
    return {'schema':1,'kind':'ae-owned-startup','collector_sha256':collector_hashes(),'host':host,'modules':modules,'sites':sites,
            'callback':{'module':'PS','offset':0x4b194}, 'match_function':{'module':'AEGP','offset':0x42554},
            'candidate_manifest':str(Path(manifest)),'candidate_sha256':digest,
            'source_commit':record['source']['commit'],'build_id':record['build_id'],
            'limits':{'startup_seconds':180,'operation_seconds':120,'native_seconds':110,'events':256,'stops':256,'bytes':1048576},
            'scope':'register-only own normal-startup identity observation; no private calls/expressions/memory/attach/kill/render'}


def validate(record, verify_files=True, check_current_source=True):
    need(set(record)=={'schema','kind','host','modules','sites','callback','match_function',
         'candidate_manifest','candidate_sha256','source_commit','build_id','limits','scope','collector_sha256'},'profile fields differ')
    if verify_files and check_current_source:need(record['collector_sha256']==collector_hashes(),'collector source changed')
    need(record['schema']==1 and record['kind'] in ('ae-owned-startup','owned-fixture'),'profile kind')
    need(record['limits']=={'startup_seconds':180,'operation_seconds':120,'native_seconds':110,'events':256,'stops':256,'bytes':1048576},'unreviewed limits')
    need(set(record['sites'])==set(FIELDS),'site inventory differs')
    for role,site in record['sites'].items():
        need(set(site)=={'module','offset','word','registers'} and site['module'] in record['modules'],'site fields')
        need(type(site['offset']) is int and site['offset']>=0 and site['offset']%4==0,'unaligned site')
        need(isinstance(site['word'],str) and len(site['word'])==8 and set(site['word'])<=set('0123456789abcdef'),'site word')
        need(set(site['registers'])==set(FIELDS[role]) and
             all(r in {*(f'x{i}' for i in range(31)),*(f'w{i}' for i in range(31)),'v0.low','v0.high'} for r in site['registers'].values()),'register map')
        if record['kind']=='ae-owned-startup' and role in SITES:
            m,o,w,r=SITES[role];need(site=={'module':m,'offset':o,'word':w,'registers':r},'unreviewed Adobe site')
    if record['kind']=='ae-owned-startup':
        need(record['host']['path']==str(HOST) and record['host']['sha256']==HOST_SHA,'unexpected AE host')
        for label,(p,h,u) in PINS.items():need(record['modules'][label]=={'path':str(p),'sha256':h,'uuid':u},'unreviewed provider')
        need(record['callback']=={'module':'PS','offset':0x4b194} and record['match_function']=={'module':'AEGP','offset':0x42554},'provider function differs')
    else:
        host=Path(record['host']['path'])
        need(host.name=='aehl-trace-fixture' and host.parent.parent==ROOT/'build-ae-hot-loader' and
             host.parent.name.startswith('trace-fixture-') and record['host']['sha256']!=HOST_SHA,'fixture target escaped owned scope')
    if record['kind']=='ae-owned-startup':
        need(set(record['modules'])=={*PINS,'marker','reader'},'module inventory differs')
        candidate=read_json(record['candidate_manifest'],record['candidate_sha256'])
        need(candidate.get('trace_identity') is True and candidate['source']['commit']==record['source_commit'] and candidate['build_id']==record['build_id'],'candidate identity differs')
        for role,item,symbol in [('marker',candidate['bundles'][0],'_AEHL_TraceMarkerBoundary'),('reader',candidate['bundles'][1],'_AEHL_TraceReaderBoundary')]:
            source=Path(record['candidate_manifest']).parent/item['bundle']/'Contents/MacOS'/Path(item['bundle']).stem
            im=Image(source);offset=im.symbol(symbol);pin=record['modules'][role]
            loaded=candidate['config']['calibration_marker_module' if role=='marker' else 'calibration_module']
            need(pin=={'path':str(source),'sha256':item['binary_sha256'],'uuid':im.uuid,'loaded_path':loaded},'own module binding differs')
            need(record['sites'][role]=={'module':role,'offset':offset,'word':im.bytes(offset).hex(),'registers':BOUNDARIES[role]},'own sentinel differs')
        for name,digest in candidate['source']['tracked_sha256'].items():
            path=Path(name);need(not path.is_absolute() and '..' not in path.parts,'source path escape')
            if check_current_source and path.suffix!='.md':need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,'candidate source changed')
    else:
        need(record['modules']=={'fixture':record['host']} and record['candidate_manifest'] is None and record['candidate_sha256'] is None,'fixture module/source escape')
        if verify_files:
            im=Image(record['host']['path'])
            for role in FIELDS:
                need(record['sites'][role]==fixture_site(im,role),'fixture sentinel escape')
            need(record['callback']=={'module':'fixture','offset':im.symbol('_callback')} and record['match_function']=={'module':'fixture','offset':im.symbol('_match')},'fixture function escape')
    if verify_files:
        for pin in [record['host'],*record['modules'].values()]:
            im=Image(pin['path']);need(im.sha256==pin['sha256'] and im.uuid==pin['uuid'],'image digest/UUID differs')
        for role,site in record['sites'].items():
            need(Image(record['modules'][site['module']]['path']).bytes(site['offset']).hex()==site['word'],'site bytes differ')
    return record
