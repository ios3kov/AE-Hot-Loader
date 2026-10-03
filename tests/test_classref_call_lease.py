"""Actual owned nontrivial C++ return via arm64 carrier; never calls Adobe code."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
ACQUIRE='__ZN21aehl_classref_control7AcquireEb'
DESTROY='_AEHL_ClassRefControlDestroy'

@unittest.skipUnless(sys.platform=='darwin' and platform.machine()=='arm64','native carrier requires macOS arm64')
class ClassRefCallLeaseTests(unittest.TestCase):
    def run_owned(self,defines=(),mode='--good',sanitize=False,expected=0):
        compiler=shutil.which('clang++');self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-classref-call-') as tmp:
            folder=Path(tmp).resolve();lib=folder/'owned.dylib';binary=folder/'consumer'
            flags=['-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror']
            if sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            commands=[[compiler,*flags,'-dynamiclib',*defines,str(ROOT/'tests/classref_call_module.cpp'),'-o',str(lib),'-Wl,-install_name,'+str(lib)],
                      [compiler,*flags,str(ROOT/'tests/classref_call_lease.cpp'),str(ROOT/'experiments/ordinary_discovery/ClassRefCallBridge.S'),'-o',str(binary)]]
            for cmd in commands:
                r=subprocess.run(cmd,capture_output=True,text=True,timeout=45);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            nm=subprocess.run(['/usr/bin/xcrun','nm','-arch','arm64','-n',str(lib)],capture_output=True,text=True,timeout=30)
            self.assertEqual(nm.returncode,0,nm.stderr)
            symbols={line.split()[-1]:int(line.split()[0],16) for line in nm.stdout.splitlines() if len(line.split())==3 and line.split()[1].lower()=='t'}
            a=symbols[ACQUIRE]
            # Missing export control uses another valid direct-code span; binder's
            # exact export requirement must refuse before either target is called.
            d=symbols.get(DESTROY,symbols['_AEHL_TestDrop'])
            extent=lambda address:min(v for v in symbols.values() if v>address)-address
            original=lib.read_bytes()
            r=subprocess.run([str(binary),str(lib),hex(a),str(extent(a)),hex(d),str(extent(d)),mode],cwd=folder,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,expected,r.stdout+r.stderr);self.assertEqual(r.stderr,'');self.assertEqual(lib.read_bytes(),original)
            return r.stdout

    def test_real_nontrivial_result_whole_destructor_base_stable_moves_and_unwind(self):
        self.assertIn('CLASSREF_CALL_LEASE PASS',self.run_owned())
    def test_actual_module_lifetime_and_unwind_with_sanitizers(self):
        self.assertIn('CLASSREF_CALL_LEASE PASS',self.run_owned(sanitize=True))
    def test_wrong_version_or_missing_destructor_refuse_before_target_calls(self):
        for defines in (['-DAEHL_TEST_BRIDGE_VERSION=2'],['-DAEHL_TEST_MISSING_DESTROY=1']):
            with self.subTest(defines=defines):
                self.assertIn('CLASSREF_BIND_REFUSAL PASS; target_calls=0',self.run_owned(defines,'--bad'))
    def test_wrong_thread_destructor_or_move_stops_before_module_callbacks(self):
        for mode in ('--wrong-reset','--wrong-move'):
            with self.subTest(mode=mode):self.assertEqual(self.run_owned(mode=mode,expected=86),'')
if __name__=='__main__':unittest.main()
