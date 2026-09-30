"""Bounded parser tests + real loaded OWNED Mach-O on macOS; never Adobe code."""
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / 'tests/resident_image_binding.cpp'
ASM = ROOT / 'experiments/ordinary_discovery/HostIndirectResult_arm64.S'
SYMBOL = '_AEHL_OwnedFunction'


def fixture():
    """A minimal data fixture, not an executable or an Adobe binary."""
    pad = lambda text: text.encode().ljust(16, b'\0')
    segment = struct.pack('<II16sQQQQIIII', 0x19, 152, pad('__TEXT'),
                          0, 4096, 0, 4096, 5, 5, 1, 0)
    section = struct.pack('<16s16sQQIIIIIIII', pad('__text'), pad('__TEXT'),
                          512, 8, 512, 2, 0, 0, 0x80000400, 0, 0, 0)
    # One root edge and one terminal: flags=regular, address=512.
    trie = b'\0\1' + SYMBOL.encode() + b'\0' + bytes([len(SYMBOL) + 4]) + b'\3\0\x80\x04\0'
    commands = segment + section + struct.pack('<II16s', 0x1b, 24, b'OWNED-UUID-12345!')
    commands += struct.pack('<IIII', 0x80000033, 16, 1024, len(trie))
    header = struct.pack('<IIIIIIII', 0xfeedfacf, 0x100000c, 0, 6, 3, len(commands), 0, 0)
    data = bytearray(4096); data[:len(header + commands)] = header + commands
    data[512:520] = bytes.fromhex('20098052c0035fd6')
    data[1024:1024 + len(trie)] = trie
    return data


class ResidentBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aehl-owned-export-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        self.native = sys.platform == 'darwin' and platform.machine() == 'arm64'
        compiler = shutil.which('clang++')
        self.assertIsNotNone(compiler, 'clang++ required')
        inputs = [str(CPP)]; flags = []
        if self.native:
            obj = self.folder / 'indirect.o'
            self.command(['/usr/bin/xcrun', 'clang', '-arch', 'arm64', '-c', str(ASM), '-o', str(obj)])
            inputs.append(str(obj)); flags = ['-arch', 'arm64']
        self.binary = self.folder / 'reader'
        self.command([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic',
                      '-Werror', *flags, *inputs, '-o', str(self.binary)])

    def command(self, args):
        result = subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL, timeout=45)
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr).decode(errors='replace'))
        self.assertEqual(result.stderr, b'')
        return result.stdout

    def test_parser_rejects_bad_exports_without_execution(self):
        path = self.folder / 'synthetic.data'; data = fixture(); path.write_bytes(data)
        output = self.command([str(self.binary), str(path), SYMBOL])
        self.assertIn(b'PARSE direct export', output)
        leaf = 1024 + len(SYMBOL) + 4
        for flags in (1, 2, 8, 16, 32, 128):
            with self.subTest(flags=flags):
                bad = bytearray(data); bad[leaf + 1] = flags; path.write_bytes(bad)
                result = subprocess.run([str(self.binary), str(path), SYMBOL],
                                        capture_output=True, stdin=subprocess.DEVNULL, timeout=5)
                self.assertNotEqual(result.returncode, 0)
        # Weak direct definition is still a direct export in its identified image.
        weak = bytearray(data); weak[leaf + 1] = 4; path.write_bytes(weak)
        self.command([str(self.binary), str(path), SYMBOL])
        # Reject cycles, truncated terminal and an exported address outside __text.
        for at, value in ((leaf - 1, 0), (leaf, 127), (leaf + 3, 12)):
            bad = bytearray(data); bad[at] = value; path.write_bytes(bad)
            result = subprocess.run([str(self.binary), str(path), SYMBOL],
                                    capture_output=True, stdin=subprocess.DEVNULL, timeout=5)
            self.assertNotEqual(result.returncode, 0)
        print('Portable export parsing/refusal checks PASS; no library loaded')

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'real resident Mach-O inspection requires macOS arm64')
    def test_real_owned_resident_image(self):
        source = self.folder / 'owned.cpp'
        source.write_text('extern "C" __attribute__((visibility("default"))) int AEHL_OwnedFunction() { return 73; }\n')
        library = self.folder / 'owned.dylib'
        self.command(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64', '-dynamiclib',
                      str(source), '-o', str(library), '-Wl,-install_name,' + str(library)])
        original = library.read_bytes()
        output = self.command([str(self.binary), str(library), SYMBOL, '--resident'])
        self.assertEqual(library.read_bytes(), original)
        self.assertIn(b'RESIDENT named address', output)
        self.assertIn(b'Adobe calls=0', output)
        print(output.decode().strip())
        frameworks = self.folder / 'Owned.app/Contents/Frameworks'
        paths = [frameworks / 'FILE.dylib', frameworks / 'U.dylib',
                 frameworks / 'dvacore.framework/Versions/A/dvacore']
        for role, path in enumerate(paths, 1):
            path.parent.mkdir(parents=True, exist_ok=True)
            self.command(['/usr/bin/xcrun', 'clang++', '-std=c++17', '-arch', 'arm64',
                          '-dynamiclib', '-fvisibility=hidden', '-DROLE=' + str(role),
                          str(ROOT / 'tests/directory_binding_fixture.cpp'), '-o', str(path),
                          '-Wall', '-Wextra', '-Werror', '-Wl,-install_name,' + str(path)])
        directory = self.folder / 'owned directory'; directory.mkdir()
        output = self.command([str(self.binary), str(paths[0]), '_FILE_Dispose',
                               '--profile', str(frameworks), str(directory)])
        self.assertIn(b'BOUND DIRECTORY own 3-provider create/roundtrip/release PASS', output)
        print(output.decode().strip())


if __name__ == '__main__':
    unittest.main()
