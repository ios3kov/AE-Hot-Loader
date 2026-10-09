"""Build an isolated owned arm64 executable and its exact debugger profile."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import uuid
from core import FIELDS, need
from profile import ROOT, image_record, validate, collector_hashes, fixture_site
from image import Image


def build():
    need(platform.system()=='Darwin' and platform.machine()=='arm64','fixture needs native macOS arm64')
    need(not subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=ROOT),'fixture source must be clean')
    directory=ROOT/'build-ae-hot-loader'/('trace-fixture-'+uuid.uuid4().hex)
    directory.mkdir(mode=0o700)
    target=directory/'aehl-trace-fixture'
    subprocess.run(['clang++','-std=c++17','-arch','arm64','-O0','-Wall','-Wextra','-Werror',
                    str(Path(__file__).with_name('fixture.cpp')),'-o',str(target)],check=True,timeout=60)
    pin=image_record(target);im=Image(target)
    sites={role:fixture_site(im,role) for role in FIELDS}
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    record={'schema':1,'kind':'owned-fixture','collector_sha256':collector_hashes(),'host':pin,'modules':{'fixture':pin},'sites':sites,
        'callback':{'module':'fixture','offset':im.symbol('_callback')},
        'match_function':{'module':'fixture','offset':im.symbol('_match')},
        'candidate_manifest':None,'candidate_sha256':None,'source_commit':source,'build_id':directory.name,
        'limits':{'startup_seconds':180,'operation_seconds':120,'native_seconds':110,'events':256,'stops':256,'bytes':1048576},
        'scope':'own debugger transport control; no Adobe target or registry'}
    validate(record)
    profile=directory/'profile.json';profile.write_text(json.dumps(record,indent=2)+'\n');profile.chmod(0o600)
    return profile,hashlib.sha256(profile.read_bytes()).hexdigest()


if __name__=='__main__':
    p,d=build();print(json.dumps({'profile':str(p),'sha256':d}))
