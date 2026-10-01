"""Fixed profile consistency and inert diagnostic-only source policy, no AE."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/ordinary_discovery'))
import run_cleanup_observation_probe as runner
from collect_resource_roots import REQUESTS


class ObserverCandidateTests(unittest.TestCase):
    def test_cpp_profile_matches_reviewed_python_roots(self):
        compiler = shutil.which('clang++') or shutil.which('g++')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix='aehl-observer-profile-') as folder:
            binary = Path(folder) / 'profile'
            r = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                str(ROOT / 'tests/cleanup_observation_profile.cpp'), '-o', str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([str(binary)], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
            lines = r.stdout.splitlines(); self.assertEqual(len(lines), 14)
            for key, start in [('PLUG', 0), ('MEE', 7)]:
                p = runner.profile()[key]; request = REQUESTS[key][0]
                self.assertEqual(lines[start:start + 3], [p['path'], p['sha256'], p['uuid']])
                self.assertEqual(lines[start + 4], request.section)
                self.assertEqual(int(lines[start + 5]), p['root_vm'])
                self.assertEqual(int(lines[start + 6]), p['root_size'])

    def test_candidate_has_no_private_call_or_process_control_route(self):
        source = (ROOT / 'experiments/ordinary_discovery/CleanupObservationProbe.cpp').read_text()
        for forbidden in ('BindRetainedOnce', 'CreateRoundtripRelease', 'PLUG_Search(', 'MEE_GetGPList(',
                          'dlopen(', 'dlsym(', 'task_for_pid(', 'kill(', 'system(', 'execve(', 'run_directory_probe'):
            self.assertNotIn(forbidden, source)
        self.assertIn('if (consumed) return 0;', source)
        self.assertIn('consumed = true;', source)
        self.assertIn('observer.run(ae256_cleanup::Reviewed())', source)
        self.assertIn('Token() != c.token', source)
        self.assertIn('CanonicalExecutable() != c.plan.executable', source)
        self.assertIn('ModulePath() != c.plan.module_path', source)
        self.assertIn('handles.release_checked()', source)
        self.assertIn('registration.release_checked()', source)


if __name__ == '__main__':
    unittest.main()
