"""Assemble a native-call ABI primitive; execute only owned code on macOS arm64.

Cross-assembly reads a Mach-O object and does not execute it. Neither test
loads, resolves or executes any Adobe library or contacts After Effects.
"""
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASM = ROOT / 'experiments/ordinary_discovery/HostIndirectResult_arm64.S'
CPP = ROOT / 'tests/host_indirect_result.cpp'


def text_section(raw):
    """Extract exactly one __text section from an owned little-endian Mach-O."""
    if len(raw) < 32 or struct.unpack_from('<I', raw)[0] != 0xfeedfacf:
        raise ValueError('not a Mach-O object')
    magic, cpu, subtype, kind, count, commands_size, flags, reserved = struct.unpack_from('<8I', raw)
    if cpu != 0x100000c or kind != 1 or count > 1000 or 32 + commands_size > len(raw):
        raise ValueError('wrong object architecture or bounds')
    pos, sections = 32, []
    for _ in range(count):
        if pos + 8 > 32 + commands_size:
            raise ValueError('truncated command')
        command, size = struct.unpack_from('<II', raw, pos)
        if size < 8 or pos + size > 32 + commands_size:
            raise ValueError('invalid command')
        if command == 0x19:
            if size < 72:
                raise ValueError('truncated segment')
            nsections = struct.unpack_from('<I', raw, pos + 64)[0]
            if 72 + nsections * 80 != size:
                raise ValueError('section bounds')
            for i in range(nsections):
                off = pos + 72 + 80 * i
                sect, seg, address, nbytes, offset = struct.unpack_from('<16s16sQQI', raw, off)
                if sect.rstrip(b'\0') == b'__text' and seg.rstrip(b'\0') == b'__TEXT':
                    if offset + nbytes > len(raw):
                        raise ValueError('text bounds')
                    sections.append(raw[offset:offset + nbytes])
        pos += size
    if pos != 32 + commands_size or len(sections) != 1:
        raise ValueError('missing/ambiguous text section')
    return sections[0]


class HostIndirectResultTests(unittest.TestCase):
    def test_cross_assembly_exact_register_transfer(self):
        cc = shutil.which('clang')
        self.assertIsNotNone(cc, 'clang required for the cross-assembly check')
        with tempfile.TemporaryDirectory(prefix='aehl-abi-object-') as tmp:
            obj = Path(tmp) / 'bridge.o'
            run = subprocess.run([cc, '-target', 'arm64-apple-macos11', '-Wall', '-Wextra',
                                  '-Werror', '-c', str(ASM), '-o', str(obj)],
                                 capture_output=True, timeout=30, check=False)
            self.assertEqual(run.returncode, 0, run.stderr.decode(errors='replace'))
            # mov x16,x0; mov x0,x1; mov x8,x2; br x16. No guessed host offsets.
            self.assertEqual(text_section(obj.read_bytes()),
                             struct.pack('<4I', 0xaa0003f0, 0xaa0103e0, 0xaa0203e8, 0xd61f0200))

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'owned arm64 macOS execution only')
    def test_native_cpp_return_ownership_and_exception(self):
        with tempfile.TemporaryDirectory(prefix='aehl-owned-abi-') as tmp:
            obj = Path(tmp) / 'bridge.o'
            command = ['/usr/bin/xcrun', 'clang', '-arch', 'arm64', '-Wall', '-Wextra',
                       '-Werror', '-c', str(ASM), '-o', str(obj)]
            built = subprocess.run(command, capture_output=True, timeout=30, check=False)
            self.assertEqual(built.returncode, 0, built.stderr.decode(errors='replace'))
            for optimize in ('-O0', '-O2'):
                with self.subTest(optimize=optimize):
                    binary = Path(tmp) / ('owned-producer' + optimize)
                    built = subprocess.run(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64',
                                            '-std=c++17', optimize, '-Wall', '-Wextra',
                                            '-Wpedantic', '-Werror', str(CPP), str(obj),
                                            '-o', str(binary)], capture_output=True, timeout=45,
                                           check=False)
                    self.assertEqual(built.returncode, 0, built.stderr.decode(errors='replace'))
                    run = subprocess.run([str(binary)], capture_output=True, timeout=10, check=False)
                    self.assertEqual(run.returncode, 0, (run.stdout + run.stderr).decode(errors='replace'))
                    self.assertEqual(run.stderr, b'')
                    self.assertEqual(sum(line.startswith(b'PASS ') for line in run.stdout.splitlines()), 6)
                    self.assertIn(b'6/6 OWNED ABI CASES PASS; Adobe calls=0', run.stdout)
                    print('owned ABI ' + optimize + ': ' + run.stdout.decode().strip())


if __name__ == '__main__':
    unittest.main()
