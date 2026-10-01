"""One-shot portable diagnostic composition and two actual OWNED providers."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CleanupObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aehl-cleanup-observer-')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name).resolve()
        self.compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(self.compiler)
        self.binary = self.folder / 'observer'
        self.command([self.compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                      str(ROOT / 'tests/cleanup_observer.cpp'), '-o', str(self.binary)])

    def command(self, argv):
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=45)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stderr, '')
        return r.stdout

    def test_bounded_chain_mutation_failure_and_consumed_attempt(self):
        out = self.command([str(self.binary)])
        self.assertIn('CLEANUP_OBSERVER_CASES=27 PASS; callbacks_invoked=0; records_copied=0', out)

    @unittest.skipUnless(sys.platform == 'darwin' and platform.machine() == 'arm64',
                         'actual owned resident observer requires macOS arm64')
    def test_two_owned_resident_roots_and_heap_chain(self):
        args = []
        original = []
        for name, words in [('plug', 1), ('mee', 2)]:
            source = self.folder / (name + '.cpp')
            library = self.folder / (name + '.dylib')
            source.write_text('extern "C" { unsigned long long AEHL_OwnedRoot[' + str(words) + '];\n'
                              'int AEHL_OwnedAnchor() { return 73; } }\n')
            self.command(['/usr/bin/xcrun', 'clang++', '-arch', 'arm64', '-dynamiclib', str(source),
                          '-o', str(library), '-Wl,-install_name,' + str(library)])
            original.append((library, library.read_bytes()))
            symbols = self.command(['/usr/bin/xcrun', 'nm', '-arch', 'arm64', '-n', str(library)])
            vm = int(next(line.split()[0] for line in symbols.splitlines()
                          if line.endswith(' _AEHL_OwnedRoot')), 16)
            args += [str(library), hex(vm)]
        out = self.command([str(self.binary)] + args)
        self.assertIn('OWNED_RESIDENT_OBSERVER PASS; Adobe_calls=0; provider_loads_by_observer=0', out)
        for library, before in original:
            self.assertEqual(library.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
