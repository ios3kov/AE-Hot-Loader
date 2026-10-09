"""Classify one own-code refusal against exact original file bytes only.

Never opens a process, reads target memory, accepts a mismatching binding or
executes the analyzed image. Caller must supply an owned artifact and its pin.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'startup_trace'))
from image import Image, need


def validate_difference(difference):
    keys = ('relative_offset', 'file_offset', 'expected_word', 'actual_word')
    need(type(difference) is dict and set(difference) == set(keys), 'difference schema')
    for key, limit in zip(keys, (64*1024*1024, 256*1024*1024, 2**32, 2**32)):
        need(type(difference[key]) is int and 0 <= difference[key] < limit, 'difference bounds')
    relative, offset, expected, actual = (difference[k] for k in keys)
    need(offset >= relative and (offset-relative) % 4 == 0 and expected != actual, 'difference consistency')
    shift = 8*(relative % 4)
    need((expected >> shift) & 255 != (actual >> shift) & 255 and
         expected & ((1 << shift)-1) == actual & ((1 << shift)-1), 'first byte consistency')


def classify(path, sha256, difference, inventory=None, module='observer'):
    validate_difference(difference)
    need(re.fullmatch('[0-9a-f]{64}', sha256 or '') is not None, 'file digest schema')
    image = Image(path)
    need(image.sha256 == sha256, 'file digest differs')
    # Image.b is the selected arm64 slice. Recover its position from the fat
    # header only; no guessed runtime address or slide enters the calculation.
    raw = Path(path).read_bytes()
    import hashlib
    need(hashlib.sha256(raw).hexdigest() == sha256, 'file changed after parsing')
    slice_offset = 0
    if raw[:4] == bytes.fromhex('cafebabe'):
        count = struct.unpack_from('>I', raw, 4)[0]
        matches = [struct.unpack_from('>5I', raw, 8+20*i) for i in range(count)]
        slice_offset = next(x[2] for x in matches if x[0] == 0x100000c)
    b = image.b
    _, _, _, _, count, command_size, _, _ = struct.unpack_from('<8I', b)
    at = 32; text = []; fixups = []
    for _ in range(count):
        cmd, size = struct.unpack_from('<II', b, at)
        if cmd == 0x19:
            sections = struct.unpack_from('<I', b, at+64)[0]
            need(size == 72+80*sections, 'section bounds')
            for j in range(sections):
                s = at+72+80*j
                if b[s:s+16].rstrip(b'\0') == b'__text' and b[s+16:s+32].rstrip(b'\0') == b'__TEXT':
                    vm, length, offset = struct.unpack_from('<QQI', b, s+32)
                    relocations = struct.unpack_from('<I', b, s+60)[0]
                    need(offset+length <= len(b) and length % 4 == 0, 'text bounds')
                    text.append((vm, length, offset, relocations))
        elif cmd in (0x22, 0x80000022):
            need(size == 48, 'dyld command size')
            fixups.append({'command':'dyld_info', 'rebase_bytes':struct.unpack_from('<I',b,at+12)[0],
                           'bind_bytes':struct.unpack_from('<I',b,at+20)[0]})
        elif cmd == 0x80000034:
            need(size == 16, 'chained fixup command size')
            fixups.append({'command':'chained_fixups', 'bytes':struct.unpack_from('<I',b,at+12)[0]})
        at += size
    need(at == 32+command_size and len(text) == 1, 'unique text section')
    vm, length, offset, relocations = text[0]
    relative = difference['relative_offset']
    need(relative < length and difference['file_offset'] == slice_offset+offset+relative, 'section mapping differs')
    word_relative = relative-relative % 4
    expected = struct.unpack_from('<I', b, offset+word_relative)[0]
    need(expected == difference['expected_word'], 'original instruction differs')
    address = vm+word_relative
    symbols = sorted((v, n) for n, values in image.symbols.items() for v in values if vm <= v <= address)
    nearest = max((v for v,n in symbols), default=None)
    names = [n for v,n in symbols if v == nearest][:8] if nearest is not None else []
    need(all(len(n) <= 1024 for n in names), 'symbol name budget')
    matches = []
    if inventory is not None:
        need(type(inventory) is dict and type(inventory.get('breakpoints')) is list and
             len(inventory['breakpoints']) <= 16, 'inventory bounds')
        for row in inventory['breakpoints']:
            need(type(row) is dict, 'inventory row')
            if row.get('module') != module or row.get('uuid') != image.uuid: continue
            need(type(row.get('file_address')) is int and type(row.get('enabled')) is bool and
                 type(row.get('location_enabled')) is bool and type(row.get('hardware')) is bool,
                 'inventory fields')
            if row['file_address'] == address:
                need(re.fullmatch(r'[a-z][a-z0-9-]{0,39}', row.get('role','')) is not None, 'inventory role')
                matches.append({k:row[k] for k in ('role','enabled','location_enabled','hardware')})
    actual = difference['actual_word']
    return {'status':'CLASSIFIED', 'artifact_sha256':sha256, 'uuid':image.uuid,
            'difference':difference, 'instruction_file_offset':slice_offset+offset+word_relative,
            'instruction_file_address':address, 'nearest_own_symbols':names,
            'symbol_distance':address-nearest if nearest is not None else None,
            'symbol_limit':'symtab proximity; actual function boundaries UNKNOWN',
            'actual_is_arm64_brk':actual & 0xffe0001f == 0xd4200000,
            'matching_own_breakpoint_metadata':matches, 'text_relocations':relocations,
            'fixup_commands':fixups, 'fixup_effect_on_text':'UNKNOWN', 'cause':'UNKNOWN',
            'binding':'REFUSED; classification never authorizes changed code'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--owned-image',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    need(args.receipt.stat().st_size <= 4096, 'receipt bounds')
    receipt=json.loads(args.receipt.read_text())
    need(receipt.get('stage') == 'resident-text-mismatch', 'wrong receipt stage')
    print(json.dumps(classify(args.owned_image,args.sha256,receipt['own_text_difference']),indent=2))
