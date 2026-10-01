"""Static safety contract for the one-shot live no-scan launcher."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "RUN_LIVE_NO_SCAN_GATE.command"


class LiveNoScanLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = LAUNCHER.read_text(encoding="utf-8")

    def test_launcher_is_fail_closed_and_fast_forward_only(self):
        self.assertIn("set -euo pipefail", self.text)
        self.assertIn("git merge --ff-only", self.text)
        self.assertIn("git status --porcelain=v1 --untracked-files=all", self.text)
        self.assertIn('pgrep -x "After Effects"', self.text)

    def test_launcher_never_calls_old_registration_paths(self):
        for forbidden in ("PLUG_Search", "ML::LoadPlugins", "STAGE_TEST_PROBES", "INSTALL.command"):
            self.assertNotIn(forbidden, self.text)

    def test_launcher_installs_only_unique_research_helper(self):
        self.assertIn('[[ ! -e "$AUTHORIZED_BUNDLE" ]]', self.text)
        self.assertIn('ditto "$CANDIDATE_BUNDLE" "$AUTHORIZED_BUNDLE"', self.text)

    def test_launcher_performs_one_authorized_request(self):
        self.assertEqual(
            self.text.count('env AEHL_NOSCAN_GATE_TOKEN="$TOKEN" "$HOST"'),
            1,
        )
        self.assertEqual(self.text.count("--execute"), 1)
        self.assertEqual(self.text.count("--authorize-private-file-call"), 1)
        self.assertEqual(self.text.count("--authorize-provider-retention"), 1)
        self.assertIn('exec python3 "$SUPERVISOR"', self.text)

    def test_launcher_uses_reviewed_builder_and_supervisor(self):
        self.assertIn("build_no_scan_directory_probe.py", self.text)
        self.assertIn("run_no_scan_directory_probe.py", self.text)
        self.assertIn("manifest_sha256=", self.text)
        self.assertIn("codesign --verify --deep --strict", self.text)


if __name__ == "__main__":
    unittest.main()
