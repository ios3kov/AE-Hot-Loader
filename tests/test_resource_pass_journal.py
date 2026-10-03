"""Real POSIX journal files/processes; native AE observations and scan are synthetic."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ResourcePassJournalTests(unittest.TestCase):
    def test_real_files_and_process_exclusion(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler, 'C++ compiler is required')
        source = Path(__file__).with_name('resource_pass_journal.cpp')
        with tempfile.TemporaryDirectory(prefix='aehl-resource-journal-') as temporary:
            base = Path(temporary).resolve()  # macOS /var is a symlink; pass its real path.
            executable = base / 'journal-tests'
            result = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 str(source), '-o', str(executable)], stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=45, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = base / 'cases'
            evidence.mkdir(mode=0o700)
            result = subprocess.run([str(executable), str(evidence)], stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=25, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, '')
            passed = [line for line in result.stdout.splitlines() if line.startswith('PASS ')]
            self.assertEqual(len(passed), 38)
            self.assertEqual(len(set(passed)), 38)
            self.assertEqual(result.stdout.splitlines()[-1],
                             'RESOURCE_JOURNAL_TESTS=38 PASS; scope=real-files-processes-synthetic-host')
            print(result.stdout, end='')


if __name__ == '__main__':
    unittest.main()
