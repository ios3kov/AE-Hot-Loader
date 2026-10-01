"""Isolated snapshot sampler; native cases are nested within one Python test."""
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


class CleanupSnapshotTests(unittest.TestCase):
    def test_bounded_reads_mutations_and_owned_memory(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-cleanup-snapshot-') as tmp:
            binary = Path(tmp) / 'snapshot'
            build = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(Path(__file__).with_name('cleanup_snapshot.cpp')), '-o', str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(run.stderr, '')
            self.assertIn('CLEANUP_SNAPSHOT_CASES=44 PASS; host_calls=0', run.stdout)
            if platform.system() == 'Darwin' and platform.machine() == 'arm64':
                self.assertIn('OWNED_SELF_SNAPSHOT PASS; foreign_processes=0; Adobe_calls=0', run.stdout)


if __name__ == '__main__':
    unittest.main()
