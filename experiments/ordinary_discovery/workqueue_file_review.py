"""Bounded original BEE file review, never a callable host ABI or drain contract.

Layouts: local Apple SDK mach-o/{fat,loader,nlist}.h. Only the reviewed FAT32
single arm64 MH_DYLIB shape is accepted. Output contains selected names and body
hashes, rather than the multi-megabyte nm inventory. No loader/process APIs.
"""
import hashlib
import re
import struct

BEE_UUID = '161300f373f83ebca751959df40a073b'
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_SYMBOLS = 400000
MAX_STRING_BYTES = 16 * 1024 * 1024
MAX_NAME_BYTES = 4096


def require(value, reason):
    if not value:
        raise ValueError(reason)


def inspect_text_symbols(raw, expected_uuid, requested):
    """Validate slice/commands/tables and exact next-defined-text body bounds."""
    require(28 <= len(raw) <= MAX_FILE_BYTES, 'file size outside bounded scope')
    magic, count, cpu, subtype, base, size, align = struct.unpack_from('>7I', raw)
    require(magic == 0xcafebabe and count == 1 and cpu == 0x100000c,
            'unreviewed FAT architecture')
    require(align <= 30 and base >= 28 and base % (1 << align) == 0 and
            size >= 32 and base+size <= len(raw), 'invalid FAT slice bounds')
    magic, inner_cpu, inner_subtype, kind, ncmd, nbytes, _, _ = struct.unpack_from('<8I', raw, base)
    require(magic == 0xfeedfacf and inner_cpu == cpu and inner_subtype == subtype and
            kind == 6 and 0 < ncmd <= 256 and 8*ncmd <= nbytes <= 65536 and
            32+nbytes <= size, 'unreviewed Mach-O header or commands')
    require(re.fullmatch('[0-9a-f]{32}', expected_uuid) and
            0 < len(requested) <= 64, 'invalid selected symbol scope')
    text = None; symtab = None; observed_uuid = None; section_index = 0
    cursor = base+32; command_end = cursor+nbytes
    for _ in range(ncmd):
        require(cursor+8 <= command_end, 'truncated load command')
        cmd, length = struct.unpack_from('<II', raw, cursor)
        require(length >= 8 and length % 8 == 0 and cursor+length <= command_end,
                'invalid load command bounds')
        if cmd == 0x19:
            require(length >= 72, 'truncated segment')
            _, _, segment, vm, vmsize, fileoff, filesize, _, _, sections, _ = struct.unpack_from('<II16sQQQQiiII', raw, cursor)
            require(length == 72+80*sections and sections <= 255 and
                    fileoff+filesize <= size, 'invalid segment sections or file range')
            for i in range(sections):
                section_index += 1
                values = struct.unpack_from('<16s16sQQ8I', raw, cursor+72+80*i)
                name, parent, address, width, offset, alignment, reloc, nreloc, flags, *_ = values
                if segment.rstrip(b'\0') == b'__TEXT' and name.rstrip(b'\0') == b'__text':
                    require(text is None and parent == segment and width > 0 and
                            address % 4 == 0 and width % 4 == 0 and alignment <= 30 and
                            offset % (1 << alignment) == 0 and
                            32+nbytes <= offset and fileoff <= offset and
                            offset+width <= fileoff+filesize and vm <= address and
                            address+width <= vm+vmsize and address-vm == offset-fileoff and
                            reloc == nreloc == 0 and flags & 0xff == 0 and flags & 0x80000000,
                            'invalid file-backed instruction section')
                    text = (section_index, address, width, offset)
        elif cmd == 2:
            require(length == 24 and symtab is None, 'duplicate or malformed symtab')
            symtab = struct.unpack_from('<4I', raw, cursor+8)
        elif cmd == 0x1b:
            require(length == 24 and observed_uuid is None, 'duplicate or malformed UUID')
            observed_uuid = raw[cursor+8:cursor+24].hex()
        cursor += length
    require(cursor == command_end and text is not None and symtab is not None and
            observed_uuid == expected_uuid, 'missing sections/tables or UUID drift')
    so, symbols, st, string_bytes = symtab
    section, address, width, offset = text
    require(0 < symbols <= MAX_SYMBOLS and 0 < string_bytes <= MAX_STRING_BYTES and
            so >= offset+width and so+16*symbols <= size and
            st >= so+16*symbols and st+string_bytes <= size,
            'invalid or overlapping symbol/string table bounds')
    all_addresses = set(); selected = {}; text_count = 0
    for i in range(symbols):
        strx, typ, sect, _, value = struct.unpack_from('<IBBHQ', raw, base+so+16*i)
        if typ & 0xe0 or typ & 0xe != 0xe or sect != section:
            continue
        text_count += 1
        require(address <= value < address+width and value % 4 == 0 and
                strx < string_bytes, 'invalid defined text symbol')
        all_addresses.add(value)
        start = base+st+strx
        # nlist.h defines index zero as the empty name independent of its byte.
        stop = start if strx == 0 else raw.find(
            b'\0', start, min(base+st+string_bytes, start+MAX_NAME_BYTES+1))
        require(stop >= start, 'unbounded or unterminated text symbol name')
        try:
            name = raw[start:stop].decode('ascii')
        except UnicodeDecodeError as error:
            raise ValueError('invalid text symbol name') from error
        if name in requested:
            require(name not in selected, 'duplicate selected text symbol')
            selected[name] = value
    require(set(selected) == set(requested), 'selected text symbols missing')
    ordered = sorted(all_addresses)
    next_address = dict(zip(ordered, ordered[1:]))
    result = {}
    for name, (start, end) in requested.items():
        require(selected[name] == start and next_address.get(start) == end and
                0 < end-start <= 4096, 'selected start or next-defined-text boundary drift')
        payload = raw[base+offset+start-address:base+offset+end-address]
        require(len(payload) == end-start, 'truncated instruction bytes')
        result[name] = {'start': hex(start), 'end': hex(end),
                        'instruction_bytes': len(payload),
                        'body_sha256': hashlib.sha256(payload).hexdigest()}
    return {'scope': 'selected-original-file-symbols-not-host-contract',
            'uuid_arm64': observed_uuid, 'nlist_symbols': symbols,
            'string_bytes': string_bytes, 'text_symbols': text_count,
            'text_section_index': section, 'selected': result}


def transcript_digest(text, start, end):
    rows = [(int(a,16), op, re.sub(r'\s+', '', args.split(';')[0]))
            for a, op, args in re.findall(
                r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M)]
    require([a for a, *_ in rows] == list(range(start,end,4)),
            'incomplete or duplicate transcript instructions')
    require(all(op not in ('.long','.word','.inst','<unknown>') for _,op,_ in rows),
            'undecoded transcript instruction')
    canonical = ''.join('%x:%s:%s\n' % row for row in rows).encode('ascii')
    return hashlib.sha256(canonical).hexdigest()


def verify_transcript(text, start, end, expected):
    require(transcript_digest(text,start,end) == expected,
            'complete workqueue structural instructions differ')
    return (end-start)//4


# Fixed complete bodies selected and manually reviewed before implementation.
# Tuple: start, next-defined-text end, original nlist name, byte hash, transcript hash.
WINDOWS = {
    'queue-add': (0x7975b4, 0x797778,
        '__ZL24BEEp_WorkQueue_Table_AddRKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEE',
        '894465f8ca30e1d3bbee3f004cb0864f8a972366fb2bd571f42b9198a8cd22ad',
        '5cfc9e9d13221868014dd30c22c4e6c04e2601a7ab8898e9ebf2136dd22622f8'),
    'queue-cancel': (0x78e840, 0x78ea80,
        '__Z20BEE_WorkQueue_Cancely',
        'dabd2741a0533d3a2ef56a0cda5600ca89a936dd659b32f4f326930fa22878fb',
        '2b4f3d8711a1ead2274df9fbd003d79b8b487371866d818c5756fa3bffece705'),
    'queue-cancel-handler': (0x7e16e4, 0x7e17b0,
        '__ZNK3bee14WorkQueue_Item20GetCancelHandlerCopyEv',
        '170f712abb0bce0a51abcec79b69605bb1c35fd51f4296e03410bd284b51f396',
        '2c9d2ec542089a24b7743375ca223bd67b01df0dc67874446b620dbc1de8703a'),
    'queue-canceled': (0x7e1fcc, 0x7e1fe0,
        '__ZNK3bee14WorkQueue_Item8CanceledEv',
        '4594a782a7cfcf98c2ce24fb37db28e71b80c351c71cd7babc3efa06f4ffef83',
        'a0340f9bd542c926021de2af249fcfdd17dc3ec5ca73c175f3c5e29b2d714738'),
    'queue-execute': (0x7ac8f4, 0x7acde4,
        '__Z21BEE_WorkQueue_ExecuteRKN5boost10shared_ptrI20BEE_WorkQueue_ClientEERKNS0_I19BEE_WorkQueueIdListEERKNS_8functionIFvyEEEb',
        'f33848b4d7e1c859d60bbd3134d170f9cdaf2bba029a2e074692fd757372193a',
        '9cded918d981b1b322ad9fef26ee5fe72b103348170c6771a35a7645a7713715'),
    'queue-inner-cancel': (0x7b8d34, 0x7b9b38,
        '__ZL32BEEp_WorkQueue_Table_Cancel_ItemN5boost10shared_ptrIN3bee14WorkQueue_ItemEEE',
        'd87ed1dc7a6343f4639fd3f8fde05bb0bd8821da093b07437e96aaa337da952d',
        '3b8b853863ce71ba1ed00a811411dbd02e9c106d5a5201fa00508cecdb3e72b9'),
    'queue-item-cancel': (0x7e2250, 0x7e2374,
        '__ZN3bee14WorkQueue_Item9SetCancelEv',
        'eaeb5103008b5ab4dc85bc89916a68363c6fafdd4476a1a07d0cbed6809a45b5',
        'd4f605e772f5d2c59ee1a2c23e256e5d201fac177b301d7cab907af661181ae2'),
    'queue-pause': (0x78ec34, 0x78f100,
        '__Z19BEE_WorkQueue_Pausey',
        'a319954b54a829f9a24054058edf932f70367977d3a5b9490578f5f3b0c72296',
        'e06501c620b73bdd545a9c2eb7b9eab75e773e6d8be54df53f134a0a2d36593e'),
    'queue-remove': (0x7b4e48, 0x7b5028,
        '__ZL24BEE_WorkQueue_RemoveItemRKN5boost10shared_ptrIN3bee14WorkQueue_ItemEEE',
        'fa36b48fc447f0867388b4ca31037a97bc41be7cca39ec29cd013db0bd9f8c29',
        '01d8f662a5a818c9ab2d1bfa4b2b4defe67d263141cc9f446ada206950c12b13'),
    'queue-resume': (0x78f2b4, 0x78f7b4,
        '__Z20BEE_WorkQueue_Resumey',
        '84bbe90668b0f7eaa54a752a26d449b47ab9caa877418de8274460290916f8a8',
        'd26e699352e09ee35a8ab117c438454a516c131b0a77f2d646111589a3cfc2e9'),
    'queue-scheduler-pause': (0x7e1fe0, 0x7e2048,
        '__ZN3bee14WorkQueue_Item14SchedulerPauseEv',
        'fdfd69361ed99a14c4dfa4e35f2a99119c294dd11672e9389e11e05c60a9ab58',
        '0429f866027a9b83e01e6b02ddc999b7e50ea36a9ff23d1de61ba72a6425270e'),
    'queue-scheduler-paused': (0x7e2048, 0x7e2100,
        '__ZN3bee14WorkQueue_Item15SchedulerPausedEv',
        'ce0721841c3aca9c6c8bd420bead0d6f4011855cbe99f15ca9e661886c260a92',
        '34cf0c6949c9b746a1f349aaeb25d233b29384b1a14cfb461dcfd068fe55f8bd'),
    'queue-scheduler-started': (0x7e2100, 0x7e21d4,
        '__ZN3bee14WorkQueue_Item16SchedulerStartedEv',
        'd2912455dec11732118e81f95c83f8ea365996061b0e6bfc6dbeb2141dbbf1a3',
        'fef76235d52e81f11405bcef1672f09c72b047c6415777c4eb5d7ff520efc1f0'),
    'queue-stage': (0x7e18b4, 0x7e19e0,
        '__ZN3bee14WorkQueue_Item8SetStageE9ItemStage',
        '595a6c91109b8fa72b38a7836a81c8847ee1b906a672a80613e0b600f3de6157',
        'f73a6000df23d8661519ba6eccfda0eb1fb9830ede8f38596ffa0b563d653b35'),
}


def collect_symbols(raw):
    result = inspect_text_symbols(raw, BEE_UUID,
        {row[2]: (row[0],row[1]) for row in WINDOWS.values()})
    require(result['nlist_symbols'] == 271537 and result['string_bytes'] == 7871712 and
            result['text_symbols'] == 58390, 'BEE original inventory drift')
    for label, (start,end,name,body_hash,_) in WINDOWS.items():
        require(result['selected'][name]['body_sha256'] == body_hash,
                'original instruction bytes differ: '+label)
    return result
