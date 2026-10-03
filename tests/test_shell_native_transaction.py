"""Actual shell + owned C++ libraries, outside AE; no Adobe binary is loaded.

Only log/home/temp routing is redirected in a measured private source copy.
The fixture's integer dispatch result is not an AE frame or Rust ABI proof.
"""
import ctypes
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = r'''
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <thread>
using Reload = int (*)(char*, std::size_t);
static Reload reload_callback = nullptr;
static std::atomic<int> entered{0}, release_hold{0};
static std::uint64_t generation = 0;
extern "C" int EffectMain(int cmd, void*, void*, void*, void*, void* extra) {
    if (cmd == 7 && extra) *static_cast<std::uint64_t*>(extra) = generation;
    if (cmd == 98) {
        entered.store(1);
        while (!release_hold.load()) std::this_thread::yield();
    }
    if (cmd == 99) {
        char message[512]{};
        return reload_callback ? reload_callback(message, sizeof(message)) : -9999;
    }
    return VALUE;
}
#ifndef OMIT_ABI
extern "C" std::uint32_t AEHotLoader_ImplementationABI() { return PROTOCOL; }
#endif
extern "C" std::uint64_t AEHotLoader_ImplementationStateABI() { return STATE; }
extern "C" int AEHotLoader_ImplementationKey(char* out, std::size_t n) {
    return std::snprintf(out, n, "%s", KEY) < 0 ? -1 : 0;
}
extern "C" int AEHotLoader_ImplementationLabel(char* out, std::size_t n) {
    return std::snprintf(out, n, "fixture-%d", VALUE) < 0 ? -1 : 0;
}
extern "C" int AEHotLoader_ImplementationRuntimeABI(char* out, std::size_t n) {
    return std::snprintf(out, n, "%s", RUNTIME) < 0 ? -1 : 0;
}
extern "C" void AEHotLoader_SetGeneration(std::uint64_t value) { generation = value; }
extern "C" void AEHotLoader_SetBusyTestReloadCallback(Reload fn) { reload_callback = fn; }
extern "C" int TestEntered() { return entered.load(); }
extern "C" void TestRelease() { release_hold.store(1); }
'''


class ShellNativeTransactionTests(unittest.TestCase):
    def test_actual_owned_library_transaction(self):
        compiler = shutil.which('clang++')
        self.assertIsNotNone(compiler, 'clang++ required for actual shell test')
        self.assertIn(sys.platform, ('darwin', 'linux'))
        with tempfile.TemporaryDirectory(prefix='aehl-owned-shell-') as name:
            folder = Path(name).resolve()
            binary = folder / 'OwnedShell.plugin/Contents/MacOS/OwnedShell'
            bundled = folder / 'OwnedShell.plugin/Contents/Frameworks/libae_hot_loader_core.dylib'
            binary.parent.mkdir(parents=True)
            bundled.parent.mkdir(parents=True)
            source = (ROOT / 'wrapper/AEHotLoader.cpp').read_text()
            shared_log = '"/tmp/ae-hot-loader-shell.log"'
            owned_log = '"' + str(folder / 'shell.log') + '"'
            self.assertEqual(source.count(shared_log), 1)
            replacements = [(shared_log, owned_log),
                            ('std::getenv("HOME")', 'std::getenv("AEHL_OWNED_SHELL_HOME")'),
                            ('std::getenv("TMPDIR")', 'std::getenv("AEHL_OWNED_SHELL_TEMP")')]
            isolated = source
            for original, replacement in replacements:
                self.assertEqual(isolated.count(original), 1)
                isolated = isolated.replace(original, replacement)
            restored = isolated
            for original, replacement in reversed(replacements):
                restored = restored.replace(replacement, original)
            self.assertEqual(restored, source)
            private_source = folder / 'shell.cpp'
            private_source.write_text(isolated)
            fixture = folder / 'fixture.cpp'
            fixture.write_text(FIXTURE)
            flags = ['-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic', '-Werror']
            shared = ['-dynamiclib'] if sys.platform == 'darwin' else ['-shared', '-fPIC', '-pthread']

            def build(src, out, definitions=()):
                result = subprocess.run([compiler, *flags, *shared, *definitions,
                                         str(src), '-o', str(out)],
                                        stdin=subprocess.DEVNULL, capture_output=True, timeout=45)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))

            def implementation(label, value, **overrides):
                path = folder / (label + '.dylib')
                values = dict(VALUE=value, PROTOCOL=2, STATE=1,
                              KEY='"control"', RUNTIME='"owned-cpp-test-v1"')
                values.update(overrides)
                build(fixture, path, ['-D' + k + '=' + str(v) for k, v in values.items()])
                return path

            build(private_source, binary)
            default = implementation('default', 101)
            candidate = implementation('candidate', 202)
            third = implementation('third', 303)
            bad = [('protocol', implementation('bad-protocol', 401, PROTOCOL=99), -4109),
                   ('state', implementation('bad-state', 402, STATE=99), -4110),
                   ('key', implementation('bad-key', 403, KEY='"other"'), -4111),
                   ('runtime', implementation('bad-runtime', 404, RUNTIME='"other-runtime"'), -4116),
                   ('exports', implementation('bad-exports', 405, OMIT_ABI=1), -4108)]
            shutil.copyfile(default, bundled)
            home, temp = folder / 'home', folder / 'runtime'
            current = home / 'Library/Application Support/AE Hot Loader/implementations/control/current.dylib'
            current.parent.mkdir(parents=True)
            temp.mkdir()
            old = {key: os.environ.get(key) for key in
                   ('AEHL_OWNED_SHELL_HOME', 'AEHL_OWNED_SHELL_TEMP')}
            # These settings are limited to this owned test process and restored.
            os.environ.update(AEHL_OWNED_SHELL_HOME=str(home), AEHL_OWNED_SHELL_TEMP=str(temp))
            try:
                shell = ctypes.CDLL(str(binary))
                reload = shell.AEHotLoader_ShellReload
                reload.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
                reload.restype = ctypes.c_int
                effect = shell.EffectMain
                effect.argtypes = [ctypes.c_int] + [ctypes.c_void_p] * 5
                effect.restype = ctypes.c_int

                def invoke(cmd=0, extra=None):
                    return effect(cmd, None, None, None, None, extra)

                def expect_reload(label, expected):
                    message = ctypes.create_string_buffer(2048)
                    result = reload(message, len(message))
                    self.assertEqual(result, expected, message.value.decode())
                    print('OWNED SHELL ' + label + ': PASS result=' + str(result))

                # An incompatible external candidate cannot establish the baseline.
                shutil.copyfile(bad[3][1], current)
                expect_reload('bundled baseline precedes external runtime', -4116)
                self.assertEqual(invoke(), 101)
                current.unlink()
                expect_reload('bundled repeat', 1)
                shutil.copyfile(candidate, current)
                expect_reload('A to B', 0)
                self.assertEqual(invoke(), 202)
                generation = ctypes.c_uint64()
                self.assertEqual(invoke(7, ctypes.byref(generation)), 202)
                self.assertNotEqual(generation.value, 0)
                expect_reload('repeat B', 1)
                for label, path, expected in bad:
                    with self.subTest(rejection=label):
                        shutil.copyfile(path, current)
                        expect_reload('reject ' + label, expected)
                        self.assertEqual(invoke(), 202)
                current.write_bytes(b'not an executable owned fixture\n')
                expect_reload('reject malformed image', -4104)
                self.assertEqual(invoke(), 202)
                shutil.copyfile(third, current)
                before = set(temp.rglob('*.dylib'))
                self.assertEqual(invoke(99), -4112)
                self.assertEqual(set(temp.rglob('*.dylib')), before)
                print('OWNED SHELL reentrant busy call: PASS no candidate mapping')

                # Open an already mapped OWNED image to access its test handshake.
                matches = [p for p in temp.rglob('*.dylib')
                           if hashlib.sha256(p.read_bytes()).digest() ==
                           hashlib.sha256(candidate.read_bytes()).digest()]
                self.assertEqual(len(matches), 1)
                active = ctypes.CDLL(str(matches[0]))
                active.TestEntered.restype = ctypes.c_int
                active.TestRelease.restype = None
                results = []
                worker = threading.Thread(target=lambda: results.append(invoke(98)))
                worker.start()
                try:
                    deadline = time.monotonic() + 5
                    while not active.TestEntered() and time.monotonic() < deadline:
                        time.sleep(0.001)
                    self.assertEqual(active.TestEntered(), 1, 'owned worker did not enter')
                    started = time.monotonic()
                    expect_reload('concurrent busy call', -4112)
                    self.assertLess(time.monotonic() - started, 1)
                    self.assertEqual(set(temp.rglob('*.dylib')), before)
                finally:
                    active.TestRelease()
                    worker.join(timeout=5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(results, [202])
                expect_reload('B to C after worker returns', 0)
                self.assertEqual(invoke(), 303)
                next_generation = ctypes.c_uint64()
                invoke(7, ctypes.byref(next_generation))
                self.assertNotEqual(generation.value, next_generation.value)
                current.unlink()
                expect_reload('rollback to bundled A', 0)
                self.assertEqual(invoke(), 101)
                expect_reload('repeat rollback', 1)
                self.assertTrue(matches[0].exists(), 'old owned generation must be retained')
                print('OWNED SHELL source sha256=' + hashlib.sha256(source.encode()).hexdigest())
                print('OWNED SHELL dispatch/safety PASS; AE registration/apply/render NOT RUN')
            finally:
                for key, value in old.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value


if __name__ == '__main__':
    unittest.main()
