"""Independent exact pixel oracle for a declared, untransformed ARGB8/RGBA8 frame.

Raw pixel agreement is not evidence of an AE render or of loaded build identity.
Host capture provenance must be established separately. No image conversion occurs.
"""
import argparse
import hashlib
import json
from pathlib import Path


def expected(width, height, seed, order="ARGB8"):
    if type(width) is not int or type(height) is not int or not (1 <= width <= 4096 and 1 <= height <= 4096):
        raise ValueError("dimensions outside declared scope")
    if type(seed) is not int or not 0 <= seed <= 0xffffff or order not in ("ARGB8", "RGBA8"):
        raise ValueError("invalid seed or pixel order")
    pixels = bytearray()
    for row in range(height):
        for column in range(width):
            red = (column * 17 + row * 3 + seed) % 256
            green = (column * 5 + row * 29 + seed // 256) % 256
            blue = ((column ^ (row * 7)) + seed // 65536) % 256
            pixels.extend((255, red, green, blue) if order == "ARGB8" else (red, green, blue, 255))
    return bytes(pixels)


def compare(data, width, height, seed, order="ARGB8", stride=None):
    wanted = expected(width, height, seed, order)
    stride = width * 4 if stride is None else stride
    if type(stride) is not int or not width * 4 <= stride <= 65536 or len(data) != stride * height:
        raise ValueError("invalid stride or incomplete/trailing frame")
    packed = b"".join(data[y * stride:y * stride + width * 4] for y in range(height))
    different = sum(a != b for a, b in zip(packed, wanted))
    return {"schema": "AEHL-MARKER-PIXELS-1", "pixel_status": "PASS" if not different else "FAIL",
            "ae_render_status": "NOT ESTABLISHED BY PIXELS", "differing_channels": different,
            "width": width, "height": height, "stride": stride, "seed": seed, "order": order,
            "packed_sha256": hashlib.sha256(packed).hexdigest(),
            "expected_sha256": hashlib.sha256(wanted).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame", type=Path)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--seed", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--order", choices=("ARGB8", "RGBA8"), required=True)
    parser.add_argument("--stride", type=int)
    args = parser.parse_args()
    try:
        # Validate scope before reading a bounded frame; refuse symlinks and oversized files.
        expected(args.width, args.height, args.seed, args.order)
        if args.frame.is_symlink() or not args.frame.is_file() or args.frame.stat().st_size > 65536 * args.height:
            raise ValueError("frame is not a bounded regular file")
        with args.frame.open("rb") as stream:
            data = stream.read(65536 * args.height + 1)
        result = compare(data, args.width, args.height, args.seed, args.order, args.stride)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0 if result["pixel_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
