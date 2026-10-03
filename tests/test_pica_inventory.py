"""Portable public-inventory policy, no AE/SDK calls."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PicaInventoryPolicyTests(unittest.TestCase):
    def test_policy_owned_synthetic_cases(self):
        compiler=shutil.which('clang++') or shutil.which('g++');self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-inventory-policy-') as folder:
            binary=Path(folder)/'policy'
            built=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror',
              str(ROOT/'tests/pica_inventory.cpp'),'-o',str(binary)],capture_output=True,text=True,timeout=45)
            self.assertEqual(built.returncode,0,built.stderr)
            result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('27 owned/synthetic scenarios PASS; AE NOT RUN',result.stdout)
            print(result.stdout.strip())
