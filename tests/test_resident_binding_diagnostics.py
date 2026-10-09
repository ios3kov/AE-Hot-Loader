"""Typed refusal stages from actual resolver, owned files and own-process memory."""
from pathlib import Path
import hashlib
import importlib.util
import platform
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('owned_text_mismatch', ROOT / 'experiments/startup_calibration/text_mismatch.py')
mismatch = importlib.util.module_from_spec(spec); spec.loader.exec_module(mismatch)
NATIVE = sys.platform == 'darwin' and platform.machine() == 'arm64'


class BindingDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='aehl-binding-diagnostics-')
        cls.base = Path(cls.tmp.name).resolve()
        cls.driver = cls.base / 'driver'
        cls.run_command(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                         '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                         str(ROOT / 'tests/resident_binding_diagnostics.cpp'), '-o', str(cls.driver)])
        if NATIVE:
            cls.library = cls.base / 'owned.dylib'
            source = cls.base / 'owned.cpp'
            source.write_text('extern "C" int AEHL_OwnUnused() { return 73; }\n')
            cls.run_command(['clang++', '-arch', 'arm64', '-dynamiclib', str(source),
                             '-o', str(cls.library), '-Wl,-install_name,' + str(cls.library)])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def run_command(args):
        result = subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
        if result.returncode:
            raise AssertionError(result.stderr.decode(errors='replace'))
        return result.stdout

    def test_context_preserves_specific_refusal_and_allocation(self):
        self.assertIn(b'PASS binding predicate diagnostics', self.run_command([str(self.driver), 'context']))

    def test_compile_when_native_branch_is_excluded(self):
        # Exercise the portable branch with macOS's compiler too, retaining its
        # standard-library platform macros. This is not a Linux runtime claim.
        driver = self.base / 'portable-driver'
        self.run_command(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                          *(['-D__arm64e__'] if NATIVE else []),
                          str(ROOT / 'tests/resident_binding_diagnostics.cpp'), '-o', str(driver)])
        self.assertIn(b'PASS binding predicate diagnostics', self.run_command([str(driver), 'context']))

    def test_difference_schema_and_first_byte_bounds(self):
        good = {'relative_offset':6,'file_offset':4102,'expected_word':0x04030201,'actual_word':0x04090201}
        mismatch.validate_difference(good)
        for key,value in [('relative_offset',True),('relative_offset',-1),('relative_offset',2**26),
                          ('file_offset',4103),('file_offset',4),('expected_word',2**32),
                          ('actual_word',0x04030201),('actual_word',0x04090202)]:
            bad={**good,key:value}
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):mismatch.validate_difference(bad)
        with self.assertRaises(ValueError):mismatch.validate_difference({**good,'extra':1})

    @unittest.skipUnless(NATIVE, 'requires own macOS arm64 library artifact')
    def test_exact_original_file_mapping_and_metadata_limits(self):
        raw=self.library.read_bytes();image=mismatch.Image(self.library)
        address=image.symbol('_AEHL_OwnUnused')
        expected=struct.unpack('<I',image.bytes(address))[0]
        at=32;vm=offset=None
        count=struct.unpack_from('<I',image.b,16)[0]
        for _ in range(count):
            cmd,size=struct.unpack_from('<II',image.b,at)
            if cmd==0x19:
                sections=struct.unpack_from('<I',image.b,at+64)[0]
                for j in range(sections):
                    start=at+72+80*j
                    if image.b[start:start+16].rstrip(b'\0')==b'__text':
                        vm,_,offset=struct.unpack_from('<QQI',image.b,start+32)
            at+=size
        actual=0xd4200000
        first=next(i for i in range(4) if (expected>>(8*i))&255 != (actual>>(8*i))&255)
        relative=address-vm+first
        difference={'relative_offset':relative,'file_offset':offset+relative,
                    'expected_word':expected,'actual_word':actual}
        inventory={'breakpoints':[{'role':'own','module':'observer','uuid':image.uuid,
                    'file_address':address,'enabled':True,'location_enabled':True,'hardware':False}]}
        report=mismatch.classify(self.library,hashlib.sha256(raw).hexdigest(),difference,inventory)
        self.assertTrue(report['actual_is_arm64_brk']);self.assertIn('_AEHL_OwnUnused',report['nearest_own_symbols'])
        self.assertEqual(report['matching_own_breakpoint_metadata'][0]['enabled'],True)
        self.assertEqual(report['cause'],'UNKNOWN');self.assertEqual(report['fixup_effect_on_text'],'UNKNOWN')
        for mutation in ({**difference,'file_offset':difference['file_offset']+4},
                         {**difference,'expected_word':expected^0x1000000}):
            with self.assertRaises(ValueError):mismatch.classify(self.library,hashlib.sha256(raw).hexdigest(),mutation)
        with self.assertRaises(ValueError):mismatch.classify(self.library,'0'*64,difference)
        # Same selected bytes inside an explicitly owned fat container.
        fat=self.base/'owned-fat';header=struct.pack('>II5I',0xcafebabe,1,0x100000c,0,4096,len(raw),12)
        fat.write_bytes(header+bytes(4096-len(header))+raw)
        fat_report=mismatch.classify(fat,hashlib.sha256(fat.read_bytes()).hexdigest(),
            {**difference,'file_offset':difference['file_offset']+4096})
        self.assertEqual(fat_report['instruction_file_offset'],report['instruction_file_offset']+4096)

    @unittest.skipUnless(NATIVE, 'requires macOS arm64 self-memory and file contract')
    def test_file_and_memory_predicates_keep_strict_failures(self):
        before = self.library.read_bytes()
        self.assertIn(b'PASS binding predicate diagnostics',
                      self.run_command([str(self.driver), str(self.library), 'files-memory']))
        self.assertEqual(self.library.read_bytes(), before)

    @unittest.skipUnless(NATIVE, 'requires macOS arm64 owned resident image')
    def test_actual_resident_success_missing_export_hash_and_worker(self):
        self.assertIn(b'PASS binding predicate diagnostics',
                      self.run_command([str(self.driver), str(self.library), 'resident']))


if __name__ == '__main__':
    unittest.main()
