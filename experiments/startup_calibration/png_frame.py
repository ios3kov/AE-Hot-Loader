"""Bounded raw PNG decoder for the owned 64x48 RGB/RGBA8 queue control only.

No gamma/color conversion, resampling or premultiplication. RGB exports supply
implicit opaque alpha; they do not independently verify the native alpha channel.
"""
import struct
import zlib

MAX_FILE = 1024 * 1024


def decode(data):
    if not isinstance(data, bytes) or not 45 <= len(data) <= MAX_FILE or data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a bounded PNG')
    offset = 8
    shape = None
    compressed = bytearray()
    ended = False
    idat_closed = False
    chunks = []
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('truncated chunk')
        length, = struct.unpack('>I', data[offset:offset+4])
        kind = data[offset+4:offset+8]
        if length > MAX_FILE or offset + 12 + length > len(data) or not all(65 <= c <= 90 or 97 <= c <= 122 for c in kind):
            raise ValueError('invalid chunk bounds/type')
        payload = data[offset+8:offset+8+length]
        crc, = struct.unpack('>I', data[offset+8+length:offset+12+length])
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('chunk CRC mismatch')
        offset += 12 + length
        chunks.append(kind.decode('ascii'))
        if len(chunks) > 128:
            raise ValueError('too many chunks')
        if shape is None and kind != b'IHDR':
            raise ValueError('IHDR must be first')
        if kind == b'IHDR':
            if shape is not None or length != 13:
                raise ValueError('duplicate/invalid IHDR')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            if (width, height, depth, compression, filtering, interlace) != (64, 48, 8, 0, 0, 0) or color not in (2, 6):
                raise ValueError('unsupported image scope')
            shape = (width, height, 3 if color == 2 else 4)
        elif kind == b'IDAT':
            if idat_closed:
                raise ValueError('nonconsecutive IDAT')
            compressed.extend(payload)
        elif kind == b'IEND':
            if length or not compressed or offset != len(data):
                raise ValueError('invalid end/trailing data')
            ended = True
            break
        else:
            if compressed:
                idat_closed = True
            if kind in (b'PLTE', b'tRNS') or not kind[0] & 32:
                raise ValueError('unsupported critical/palette/transparency chunk')
    if not ended:
        raise ValueError('missing IEND')
    width, height, channels = shape
    stride = width * channels
    raw_size = (stride + 1) * height
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(bytes(compressed), raw_size + 1)
    except zlib.error as error:
        raise ValueError('invalid compressed pixels') from error
    if len(raw) != raw_size or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
        raise ValueError('incomplete/oversized compressed pixels')
    previous = bytearray(stride)
    rgba = bytearray()
    for y in range(height):
        start = y * (stride + 1)
        filter_type = raw[start]
        if filter_type > 4:
            raise ValueError('invalid PNG filter')
        row = bytearray(raw[start+1:start+1+stride])
        for x in range(stride):
            left = row[x-channels] if x >= channels else 0
            up = previous[x]
            upper_left = previous[x-channels] if x >= channels else 0
            prediction = 0
            if filter_type == 1:
                prediction = left
            elif filter_type == 2:
                prediction = up
            elif filter_type == 3:
                prediction = (left + up) // 2
            elif filter_type == 4:
                p = left + up - upper_left
                distances = (abs(p-left), abs(p-up), abs(p-upper_left))
                prediction = (left, up, upper_left)[distances.index(min(distances))]
            row[x] = (row[x] + prediction) & 255
        if channels == 4:
            rgba.extend(row)
        else:
            for x in range(0, stride, 3):
                rgba.extend(row[x:x+3]); rgba.append(255)
        previous = row
    return bytes(rgba), {'width': width, 'height': height, 'source_channels': channels,
                        'depth': 8, 'order': 'RGBA8', 'stride': width * 4,
                        'alpha': 'EXPORTED_RGBA' if channels == 4 else 'IMPLICIT_OPAQUE_RGB',
                        'color_conversion': 'NONE', 'chunks': chunks}
