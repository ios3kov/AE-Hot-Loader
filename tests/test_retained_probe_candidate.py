"""Owned capture/binding tests and offline-only native candidate policy."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / 'experiments/ordinary_discovery'
sys.path.insert(0, str(EXPERIMENT))
import build_retained_identity_probe as builder

class RetainedProbeCandidateTests(unittest.TestCase):
    def test_real_capture_refuses_changed_scope_images_exceptions_and_replay(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-retained-probe-') as folder:
            binary = Path(folder) / 'probe'
            build = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                str(ROOT / 'tests/retained_probe_contract.cpp'), '-o', str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, 'RETAINED_PROBE_CASES=41 PASS; Adobe_calls=0; installs=0\n')

    def test_measured_native_source_route_and_inert_boundary(self):
        native = (EXPERIMENT / 'RetainedIdentityProbe.cpp').read_text()
        host = (EXPERIMENT / 'RetainedProbeHost.hpp').read_text()
        for forbidden in ('BindRetainedOnce', 'CreateRoundtripRelease', 'PLUG_Search(', 'MEE_GetGPList(',
                          'dlopen(', 'dlsym(', 'task_for_pid(', 'kill(', 'system(', 'execve('):
            self.assertNotIn(forbidden, native + host)
        gate = native.index('if (!suites || Token() != c.token')
        sdk = native.index('Suite<AEGP_RegisterSuite5>', gate)
        self.assertLess(gate, sdk)
        self.assertIn('CanonicalExecutable() != c.executable', native)
        self.assertIn('ModulePath() != c.module', native)
        self.assertLess(native.index('consumed = true; // Consume'), native.index('retained_probe::ApproveRequest'))
        self.assertIn('resident_binding::Resolve({module, ae256_cleanup::Decode<32>(binary_)}', native)
        self.assertIn('reinterpret_cast<void*>(&AEHL_RetainedBuildIdentity)', native)
        self.assertIn('resident_data_root::Bind(ae256_cleanup::Profile(ae256_cleanup::kMee))', native)
        self.assertIn('transaction.run(plan, {plan, true, true}, backend)', native)
        self.assertIn('mapped_memory::SelfBackend memory', native)
        # Public SDK snapshot is byte-for-byte the already reviewed project safety script.
        old = (EXPERIMENT / 'CleanupObservationProbe.cpp').read_text()
        def script(text):
            return text.split('snapshot_script = R"JS(', 1)[1].split(')JS";', 1)[0]
        self.assertEqual(script(host), script(old))

    def test_builder_records_only_fixed_mee_and_base_address(self):
        digest = builder.INPUTS['MEE'][1]
        metadata = {'uuid': builder.UUIDS['MEE'], 'image_base_vm': '0x1000'}
        with patch.object(builder, 'profile_agrees'), patch.object(builder, 'validate_input') as validate, \
             patch.object(builder, 'read_trusted_binary', return_value=b'fixture'), \
             patch.object(builder, 'parse_roots', return_value=metadata):
            profile = builder.reviewed_roots()
            self.assertEqual(set(profile), {'MEE'})
            self.assertEqual(profile['MEE']['base_vm'], 4096)
            self.assertEqual(profile['MEE']['root_vm'], 0x10fd70)
            self.assertEqual(profile['MEE']['sha256'], digest)
            self.assertEqual(validate.call_count, 2)
            metadata['uuid'] = '0' * 32
            with self.assertRaises(ValueError): builder.reviewed_roots()

if __name__ == '__main__': unittest.main()
