"""Bounded FILE metadata for reviewed writable zero-fill roots; no process/API.

VM values and offsets identify a Mach-O slice, never a current runtime object.
Format basis: Apple's loader.h / nlist.h, as recorded in the root review.
"""
from dataclasses import dataclass
import struct

MAX_FILE = 256 * 1024 * 1024
MAX64 = (1 << 64) - 1


@dataclass(frozen=True)
class RootSpec:
    symbol: str
    symbol_vm: int
    displacement: int
    extent: int
    section: str
    meaning: str


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def bounds(start, size, limit):
    need(0 <= start <= limit and 0 <= size <= limit - start, 'truncated metadata range')


def vm_end(start, size):
    need(0 <= start <= MAX64 and 0 <= size <= MAX64 - start, 'VM extent overflow')
    return start + size


def nonoverlap(ranges):
    previous = 0
    for start, end in sorted(ranges):
        need(start >= previous, 'overlapping metadata extents')
        previous = end


def name16(data):
    need(len(data) == 16, 'invalid fixed name')
    name, separator, padding = data.partition(b'\0')
    need(not separator or not any(padding), 'invalid fixed name padding')
    try:
        return name.decode('ascii')
    except UnicodeDecodeError as error:
        raise ValueError('invalid fixed name encoding') from error


def parse_roots(data, requests):
    need(isinstance(data, bytes) and 32 <= len(data) <= MAX_FILE, 'invalid metadata input')
    need(1 <= len(requests) <= 8, 'invalid root request count')
    names = set()
    for r in requests:
        need(isinstance(r, RootSpec) and r.symbol.startswith('_') and
             len(r.symbol) <= 256 and r.symbol.isascii() and '\0' not in r.symbol and
             r.symbol not in names, 'invalid or duplicate root request')
        names.add(r.symbol)
        need(r.symbol_vm > 0 and r.displacement >= 0 and 1 <= r.extent <= 4096 and
             (r.symbol_vm + r.displacement) % 8 == 0 and r.extent % 8 == 0 and
             r.section in ('__bss', '__common'), 'invalid root extent request')
        vm_end(r.symbol_vm, r.displacement + r.extent)
    offset, size = 0, len(data)
    if data[:4] == b'\xca\xfe\xba\xbe':
        count = struct.unpack_from('>I', data, 4)[0]
        need(1 <= count <= 16, 'invalid FAT count')
        table_end = 8 + count * 20
        bounds(8, count * 20, len(data))
        slices, selected = [], []
        for i in range(count):
            cpu, subtype, off, length, align = struct.unpack_from('>IIIII', data, 8 + i * 20)
            need(align <= 30 and off >= table_end and off % (1 << align) == 0 and length >= 32,
                 'invalid FAT slice extent')
            bounds(off, length, len(data)); slices.append((off, off + length))
            if cpu == 0x100000c:
                need(subtype == 0, 'unsupported arm64 subtype')
                selected.append((off, length))
        nonoverlap(slices)
        need(len(selected) == 1, 'missing or ambiguous arm64 slice')
        offset, size = selected[0]
    image = memoryview(data)[offset:offset + size]
    def unpack(fmt, at):
        bounds(at, struct.calcsize(fmt), size)
        return struct.unpack_from(fmt, image, at)
    magic, cpu, subtype, kind, commands, command_bytes, _, _ = unpack('<8I', 0)
    need(magic == 0xfeedfacf and cpu == 0x100000c and subtype == 0 and kind == 6,
         'unsupported thin image')
    need(1 <= commands <= 4096 and 8 <= command_bytes <= 2 * 1024 * 1024,
         'invalid load command count or size')
    command_end = 32 + command_bytes
    bounds(32, command_bytes, size)
    segments, sections, uuid, symtab = [], [], None, None
    position = 32
    for _ in range(commands):
        bounds(position, 8, command_end)
        command, length = unpack('<II', position)
        need(length >= 8 and length % 8 == 0, 'invalid load command size')
        bounds(position, length, command_end)
        if command == 0x19:
            need(length >= 72, 'truncated segment')
            values = unpack('<II16sQQQQiiII', position)
            _, _, raw, vm, vmsize, fileoff, filesize, maximum, initial, count, flags = values
            name = name16(raw)
            need(name and all(s['name'] != name for s in segments), 'duplicate segment')
            need(count <= 255 and length == 72 + count * 80 and len(sections) + count <= 255,
                 'invalid section count')
            need(vmsize > 0 and filesize <= vmsize and flags & ~0x10 == 0,
                 'unsupported segment mapping')
            end = vm_end(vm, vmsize); bounds(fileoff, filesize, size)
            need(initial & ~7 == 0 and maximum & ~7 == 0 and initial & ~maximum == 0,
                 'invalid segment protection')
            segment = dict(name=name, vm=vm, end=end, fileoff=fileoff,
                           filesize=filesize, initial=initial, maximum=maximum, flags=flags)
            segments.append(segment)
            local = []
            for j in range(count):
                section = unpack('<16s16sQQ8I', position + 72 + j * 80)
                raw_section, raw_segment, address, extent, off, align, reloc, nreloc, attrs, *_ = section
                section_name = name16(raw_section)
                need(name16(raw_segment) == name and section_name and align <= 31 and
                     address % (1 << align) == 0, 'invalid section identity or alignment')
                section_end = vm_end(address, extent)
                need(address >= vm and section_end <= end, 'section outside segment')
                bounds(reloc, nreloc * 8, size)
                section_type = attrs & 255
                zero = section_type in (1, 0xc, 0x12)
                if zero:
                    need(off == 0, 'zero-fill has file offset')
                else:
                    bounds(off, extent, size)
                    need(off >= fileoff and off + extent <= fileoff + filesize,
                         'section outside file segment')
                if extent:
                    local.append((address, section_end))
                sections.append(dict(name=section_name, segment=segment, vm=address,
                                     end=section_end, type=section_type, attributes=attrs, zero=zero,
                                     ordinal=len(sections) + 1))
            nonoverlap(local)
        elif command == 0x1b:
            need(uuid is None and length == 24, 'missing or duplicate UUID')
            uuid = bytes(image[position + 8:position + 24])
            need(any(uuid), 'zero UUID')
        elif command == 2:
            need(symtab is None and length == 24, 'missing or duplicate symbol table')
            _, _, symbols, count, strings, string_size = unpack('<6I', position)
            need(1 <= count <= 500000 and 1 <= string_size <= 32 * 1024 * 1024,
                 'invalid symbol table budget')
            bounds(symbols, count * 16, size); bounds(strings, string_size, size)
            symtab = (symbols, count, strings, string_size)
        position += length
    need(position == command_end and uuid is not None and symtab is not None,
         'incomplete image metadata')
    nonoverlap([(s['vm'], s['end']) for s in segments])
    text = [s for s in segments if s['name'] == '__TEXT']
    linkedit = [s for s in segments if s['name'] == '__LINKEDIT']
    need(len(text) == 1 and text[0]['fileoff'] == 0 and text[0]['filesize'] >= command_end and
         text[0]['initial'] == 5 and text[0]['maximum'] == 5 and len(linkedit) == 1,
         'missing header or linkedit segment')
    symbols, count, strings, string_size = symtab
    link = linkedit[0]
    for start, length in ((symbols, count * 16), (strings, string_size)):
        need(start >= link['fileoff'] and start + length <= link['fileoff'] + link['filesize'],
             'symbol table outside linkedit')
    nonoverlap([(symbols, symbols + count * 16), (strings, strings + string_size)])
    table = bytes(image[strings:strings + string_size])
    need(table[-1] == 0, 'unterminated string table')
    wanted = {r.symbol.encode() + b'\0': r for r in requests}
    found = {}
    for i in range(count):
        index, type_bits, ordinal, _, value = unpack('<IBBHQ', symbols + i * 16)
        need(index < string_size, 'symbol string index outside table')
        if index == 0 or type_bits & 0xe0:  # unnamed/debug entries cannot define a root
            continue
        for name, r in wanted.items():
            if not table.startswith(name, index):
                continue
            need(r.symbol not in found, 'duplicate root symbol')
            need(type_bits & 0xe0 == 0 and type_bits & 0x0e == 0x0e and
                 1 <= ordinal <= len(sections), 'root is not a section definition')
            section = sections[ordinal - 1]; segment = section['segment']
            root_vm = vm_end(value, r.displacement)
            root_end = vm_end(root_vm, r.extent)
            need(value == r.symbol_vm and section['vm'] <= value < section['end'] and
                 section['vm'] <= root_vm and root_end <= section['end'],
                 'root value or section extent mismatch')
            need(segment['name'] == '__DATA' and segment['initial'] == 3 and
                 segment['maximum'] == 3 and segment['flags'] == 0 and
                 section['name'] == r.section and section['attributes'] == 1,
                 'root is not reviewed writable zero-fill')
            need(root_vm >= text[0]['vm'], 'root precedes image header')
            found[r.symbol] = dict(symbol=r.symbol, symbol_vm=hex(value),
                displacement=hex(r.displacement), root_vm=hex(root_vm), extent=r.extent,
                image_relative_offset=hex(root_vm - text[0]['vm']), section=r.section,
                section_ordinal=ordinal, section_vm=hex(section['vm']),
                section_size=section['end'] - section['vm'], segment=segment['name'],
                zero_fill=True, serialized_root_bytes=None, meaning=r.meaning)
    need(len(found) == len(requests), 'missing root symbol')
    return dict(schema='AEHL-STATIC-ROOTS-1', scope='file-only-not-runtime',
                slice_offset=offset, slice_size=size, image_base_vm=hex(text[0]['vm']),
                uuid=uuid.hex(), roots=[found[r.symbol] for r in requests])
