"""Admission restricted to one freshly built owned wire-buffer executable."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.resource_trace.core import need, digest
from experiments.startup_trace.image import Image

SOURCES = ('core.py', 'borrow.py', 'fixture.cpp', 'transport_profile.py', 'transport.py', 'debug_fixture.py')
DEPENDENCIES = ('image.py', 'lldb_collector.py', 'core.py', 'profile.py', 'stops.py', 'lifecycle.py', 'timeline.py')


def hashes():
    paths = [ROOT/'experiments/resource_trace'/x for x in SOURCES]
    paths += [ROOT/'experiments/startup_trace'/x for x in DEPENDENCIES]
    # The existing process identity loader and its direct support modules.
    paths += [ROOT/'experiments/startup_calibration'/x for x in
              ('run.py', 'oracle.py', 'identity.py', 'png_frame.py')]
    paths += [ROOT/'experiments/ordinary_discovery/run_no_scan_directory_probe.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def clean_source():
    need(not subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=ROOT),
         'resource transport needs clean source')
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def validate(record):
    need(type(record) is dict and set(record) == {'schema', 'kind', 'source_commit', 'sources', 'image',
         'site', 'run_id', 'match_name', 'resource', 'payload_sha256', 'origin', 'fault'}, 'transport profile fields')
    need(type(record['schema']) is int and record['schema'] == 1 and
         record['kind'] == 'owned-resource-transport', 'Adobe memory/launch not admitted')
    need(record['sources'] == hashes() and record['source_commit'] == clean_source(), 'transport source changed')
    run = record['run_id']
    need(type(run) is str and re.fullmatch('[0-9a-f]{32}', run) and
         record['match_name'] == 'AEHLR' + run[:12], 'transport run identity')
    pin = record['image']
    need(type(pin) is dict and set(pin) == {'path', 'sha256', 'uuid'}, 'image fields')
    host = Path(pin['path'])
    need(host.is_absolute() and not any(p.is_symlink() for p in (host, *host.parents)) and
         host.name == 'aehl-resource-transport' and host.parent.parent == ROOT/'build-ae-hot-loader' and
         host.parent.name == 'resource-debug-' + run and host.stat().st_uid == os.getuid() and
         host.stat().st_nlink == 1 and not host.stat().st_mode & 0o022 and
         host.parent.stat().st_mode & 0o777 == 0o700, 'owned executable scope')
    im = Image(host)
    need(pin == {'path': str(host), 'sha256': im.sha256, 'uuid': im.uuid}, 'transport image changed')
    address = im.symbol('_resource_probe_site')
    need(im.bytes(address).hex() == '1f2003d5' and
         record['site'] == {'offset': address, 'word': '1f2003d5'}, 'unreviewed probe site')
    resource = Path(record['resource'])
    need(resource == host.parent/'input.resource' and not resource.is_symlink() and resource.is_file() and
         resource.stat().st_size == 23 and resource.stat().st_nlink == 1 and
         resource.stat().st_uid == os.getuid() and resource.stat().st_mode & 0o777 == 0o600,
         'resource scope/mode')
    raw = resource.read_bytes()
    need(raw == b'eMNA:' + record['match_name'].encode() + b'\0' and digest(record['payload_sha256']) and
         hashlib.sha256(raw).hexdigest() == record['payload_sha256'], 'resource changed')
    need(record['origin'] in ('bundle-resource', 'legacy-resource', 'cache') and
         record['fault'] in ('none', 'alias', 'writer-failure', 'wrong-owner', 'read-name'), 'fixture variant')
    return record


def read_profile(path, expected):
    path = Path(path)
    need(path.is_absolute() and not any(p.is_symlink() for p in (path, *path.parents)) and
         path.stat().st_uid == os.getuid() and path.stat().st_mode & 0o777 == 0o600 and
         stat.S_ISREG(path.stat().st_mode) and path.stat().st_nlink == 1 and
         path.stat().st_size <= 32768, 'private profile scope')
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    need((before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) ==
         (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size), 'profile changed during read')
    need(digest(expected) and hashlib.sha256(raw).hexdigest() == expected, 'profile digest changed')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'duplicate profile/event key'); result[key] = value
        return result
    return validate(json.loads(raw, object_pairs_hook=unique))
