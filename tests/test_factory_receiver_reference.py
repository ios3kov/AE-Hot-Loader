"""Copied reference refusals and real owned native lifetime; no Adobe ABI claim."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
class FactoryReceiverReferenceTests(unittest.TestCase):
    def run_owned(self, mode, sanitizer=False):
        compiler=shutil.which('clang++'); self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-receiver-reference-') as tmp:
            binary=Path(tmp)/'owned'
            flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if sanitizer else []
            result=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror',
                                   *flags,str(ROOT/'tests/factory_receiver_reference.cpp'),'-o',str(binary)],
                                  capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=subprocess.run([str(binary),mode],capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(result.stderr,'')
            return result.stdout
    def test_copied_shape_refuses_null_partial_wrong_adjustment_and_overflow(self):
        self.assertIn('COPIED_RECEIVER_REFERENCE PASS; diagnostic_shape_only',self.run_owned('--copied'))
    def test_real_owned_lifetime_alias_transfer_replacement_and_stale_bytes_with_sanitizers(self):
        self.assertIn('OWNED_RECEIVER_LIFETIME PASS; std_cpp_owner_only; stale_shape_is_not_liveness; Adobe_calls=0',
                      self.run_owned('--owned',True))
if __name__=='__main__':unittest.main()
