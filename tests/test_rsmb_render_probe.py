"""Static safety checks for the controlled RSMB JSX/launcher."""
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
JSX=ROOT/"experiments/ordinary_discovery/render_rsmb.jsx"
CMD=ROOT/"experiments/host_preflight/RUN_RSMB_APPLY_RENDER.command"

class Tests(unittest.TestCase):
    def test_no_reload_or_process_control(self):
        text=JSX.read_text()+CMD.read_text()
        self.assertNotIn("reload_plugins",text)
        self.assertNotIn("app.quit",text)
        self.assertNotIn("kill ",text)

    def test_exact_match_and_disposable_cleanup(self):
        text=JSX.read_text()
        self.assertIn('"Smart Motion Blur 3.x"',text)
        self.assertIn("canAddProperty(MATCH)",text)
        self.assertIn("addProperty(MATCH)",text)
        self.assertIn("CloseOptions.DO_NOT_SAVE_CHANGES",text)
        self.assertGreaterEqual(text.count("app.newProject()"),2)

    def test_blank_baseline_guard_precedes_mutation(self):
        text=JSX.read_text()
        self.assertLess(text.index("Unsafe baseline"),text.index("app.newProject()"))

    def test_exact_js_runs_in_mock(self):
        r=subprocess.run(["node",str(ROOT/"tests/rsmb-render-js.cjs"),str(JSX)],
                         text=True,capture_output=True,timeout=10)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("RSMB JSX mocks: 6/6",r.stdout)

if __name__=="__main__":
    unittest.main()
