#!/usr/bin/env python3
"""Collect static PLUG/MEE root provenance; never reads or attaches to AE."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

from collect_resource_search_abi import (
    ROOT, INPUTS, source_identity, profile_agrees, validate_input,
    write_exclusive, package,
)
from mach_o_root_metadata import MAX_FILE, RootSpec, parse_roots

REQUESTS = {
    'PLUG': (RootSpec('_PLUGp_G', 0x18488, 8, 8, '__common',
                      'sack-handle pointer slot; read slot then handle before sack'),),
    'MEE': (RootSpec('__MergedGlobals.195', 0x10fa00, 0x370, 16, '__bss',
                     'general-plugin vector begin/end pair; allocation/lifetime unknown'),),
}


def collect():
    commit = source_identity()
    profile_agrees()
    parent = ROOT / 'build-ae-hot-loader'
    parent.mkdir(mode=0o700, exist_ok=True)
    if parent.is_symlink() or not parent.is_dir() or parent.stat().st_uid != os.getuid():
        raise ValueError('unsafe owned output directory')
    folder = Path(tempfile.mkdtemp(prefix='resource-roots-' + uuid.uuid4().hex[:8] + '-', dir=parent))
    folder.chmod(0o700)
    results = {}
    for name, requests in REQUESTS.items():
        path, digest = INPUTS[name]
        before = validate_input(path, digest)
        with path.open('rb') as stream:
            data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise ValueError('metadata input exceeded bounded size')
        if hashlib.sha256(data).hexdigest() != before:
            raise ValueError('input changed during metadata read')
        metadata = parse_roots(data, requests)
        after = validate_input(path, digest)
        if before != after:
            raise ValueError('input changed after metadata read')
        write_exclusive(folder / (name + '-roots.json'), json.dumps(metadata, indent=2, sort_keys=True) + '\n')
        results[name] = dict(path=str(path), sha256_before=before, sha256_after=after,
                             metadata_file=name + '-roots.json')
    if source_identity() != commit:
        raise ValueError('source changed during collection')
    record = dict(schema='AEHL-STATIC-ROOT-COLLECTION-1', source_commit=commit,
                  scope='file-only-not-runtime', status='PASS', inputs=results,
                  foreign_process_reads=0, adobe_calls=0, serialized_root_state_read=False)
    archive = package(folder, record)
    print('PASS: static root metadata only; AE operations=0')
    print('Report: ' + str(archive))
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if sys.platform != 'darwin':
        parser.exit(2, 'BLOCKED: pinned input collection requires macOS.\n')
    try:
        collect()
    except (OSError, ValueError) as error:
        parser.exit(2, 'BLOCKED: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
