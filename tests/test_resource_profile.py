"""Compile/run the data-only AE 25.6 Stage C1 image profile."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ResourceProfileTests(unittest.TestCase):
    def test_profile_is_complete_and_inert(self):
        compiler = shutil.which("clang++") or shutil.which("g++")
        self.assertIsNotNone(compiler)
        source = Path(__file__).with_name("resource_profile.cpp")
        with tempfile.TemporaryDirectory(prefix="aehl-resource-profile-") as tmp:
            binary = Path(tmp) / "profile"
            build = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                 str(source), "-o", str(binary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=45, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(binary)], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True,
                                 timeout=10, check=False)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(run.stderr, "")
            self.assertEqual(run.stdout.strip(),
                             "RESOURCE_PROFILE_TESTS=9 PASS; calls=0")


if __name__ == "__main__":
    unittest.main()
