"""Actual owned factory teardown calls two dynamically supplied resident modules."""
from pathlib import Path
import platform,shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(sys.platform=='darwin' and platform.machine()=='arm64','owned dependency ABI requires macOS arm64')
class DependencyLeaseTests(unittest.TestCase):
    def run_owned(self,defines=(),mode='--good',sanitize=False,expected=0):
        compiler=shutil.which('clang++');self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-dependency-lease-') as tmp:
            folder=Path(tmp).resolve();flags=['-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror']
            if sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            libs=[folder/'factory.dylib',folder/'first.dylib',folder/'second.dylib'];binary=folder/'consumer'
            args=[];original=[]
            for i,lib in enumerate(libs):
                source='classref_call_module.cpp' if i==0 else 'factory_dependency_provider.cpp'
                extra=[] if i==0 else ['-DAEHL_PROVIDER_ID='+str(20+i*10)]
                if i==2:extra+=list(defines)
                r=subprocess.run([compiler,*flags,'-dynamiclib',*extra,str(ROOT/'tests'/source),'-o',str(lib),'-Wl,-install_name,'+str(lib)],capture_output=True,text=True,timeout=45)
                self.assertEqual(r.returncode,0,r.stderr);original.append(lib.read_bytes())
                nm=subprocess.run(['/usr/bin/xcrun','nm','-arch','arm64','-n',str(lib)],capture_output=True,text=True,timeout=30);self.assertEqual(nm.returncode,0,nm.stderr)
                symbols={s.split()[-1]:int(s.split()[0],16) for s in nm.stdout.splitlines() if len(s.split())==3 and s.split()[1].lower()=='t'}
                a=symbols['__ZN21aehl_classref_control7AcquireEb' if i==0 else '_AEHL_OwnedDependencyVersion']
                d=symbols['_AEHL_ClassRefControlDestroy'] if i==0 else symbols.get('_AEHL_OwnedDependencyTeardown',symbols['_AEHL_TestDependencyEvent'])
                extent=lambda value:min(v for v in symbols.values() if v>value)-value
                args += [str(lib),hex(a),str(extent(a)),hex(d),str(extent(d))]
            r=subprocess.run([compiler,*flags,str(ROOT/'tests/factory_dependency_lease.cpp'),str(ROOT/'experiments/ordinary_discovery/ClassRefCallBridge.S'),'-o',str(binary)],capture_output=True,text=True,timeout=45);self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([str(binary),*args,mode],cwd=folder,capture_output=True,text=True,timeout=45)
            self.assertEqual(r.returncode,expected,r.stdout+r.stderr);self.assertEqual(r.stderr,'')
            for lib,b in zip(libs,original):self.assertEqual(lib.read_bytes(),b)
            return r.stdout
    def test_actual_callbacks_then_reverse_unload_after_factory_release(self):
        self.assertIn('DEPENDENCY_LEASE PASS',self.run_owned())
    def test_native_lifetime_with_sanitizers(self):
        self.assertIn('DEPENDENCY_LEASE PASS',self.run_owned(sanitize=True))
    def test_partial_acquisition_bad_version_or_missing_export_no_factory_calls(self):
        for defines in (['-DAEHL_DEPENDENCY_VERSION=2'],['-DAEHL_DEPENDENCY_MISSING_TEARDOWN=1']):
            with self.subTest(defines=defines):self.assertIn('DEPENDENCY_BIND_REFUSAL PASS',self.run_owned(defines,'--bad'))
    def test_absent_providers_are_not_loaded_or_factory_acquired(self):
        self.assertIn('DEPENDENCY_ABSENCE PASS',self.run_owned(mode='--absent'))
    def test_worker_release_or_transfer_stops_before_callbacks(self):
        for mode in ('--wrong-reset','--wrong-move','--reentrant-move'):
            with self.subTest(mode=mode):self.assertEqual(self.run_owned(mode=mode,expected=86),'')
if __name__=='__main__':unittest.main()
