"""Diagnostic gate transport/claim tests, not actual native capture evidence."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CleanupObservationGateTests(unittest.TestCase):
    def test_scope_runtime_replay_deadline_and_durable_records(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-observer-gate-') as folder:
            folder = str(Path(folder).resolve())
            binary = Path(folder) / 'gate'
            r = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                str(ROOT / 'tests/cleanup_observation_gate.cpp'), '-o', str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([str(binary), folder], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(r.stderr, '')
            self.assertIn('CLEANUP_OBSERVATION_GATE_CASES=21 PASS; synthetic_transport_only; Adobe_calls=0', r.stdout)


if __name__ == '__main__':
    unittest.main()
