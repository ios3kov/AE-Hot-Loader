"""Static and executable safety checks for the controlled RSMB harness."""
import ast
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
JSX=ROOT/"experiments/ordinary_discovery/render_rsmb.jsx"
CMD=ROOT/"experiments/host_preflight/RUN_RSMB_APPLY_RENDER.command"

class Tests(unittest.TestCase):
    def launcher_python_helpers(self):
        text=CMD.read_text()
        marker='REPORT="$(python3 - "$PRE" "$APP" "$JSX" <<\'PY\'\n'
        code=text.split(marker,1)[1].split("\nPY\n",1)[0]
        tree=ast.parse(code)
        keep=(ast.Import,ast.ImportFrom,ast.FunctionDef)
        module=ast.Module(body=[node for node in tree.body if isinstance(node,keep)],
                          type_ignores=[])
        namespace={}
        exec(compile(module,"<launcher-python>","exec"),namespace)
        return namespace

    def run_preflight_check(self, project):
        text=CMD.read_text()
        marker='python3 - "$report" <<\'PY\'\n'
        code=text.split(marker,1)[1].split("\nPY\n",1)[0]
        report={
            "checks":{
                "agent_identity":{"status":"PASS"},
                "registry":{"status":"PASS"},
                "project_unchanged":{"status":"PASS"},
            },
            "before":{"project":project},
            "after":{"project":project},
        }
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"report.json"
            path.write_text(json.dumps(report),encoding="utf-8")
            return subprocess.run(["python3","-",str(path)],input=code,
                                  text=True,capture_output=True,timeout=10)

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

    def test_preflight_accepts_collector_revision_metadata(self):
        project={"dirty":False,"items":0,"queued":0,"rendering":False,
                 "saved":False,"revision":1}
        r=self.run_preflight_check(project)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("PASS: preflight Agent/RSMB/blank-project",r.stdout)

    def test_preflight_still_rejects_nonblank_project(self):
        project={"dirty":False,"items":1,"queued":0,"rendering":False,
                 "saved":False,"revision":2}
        r=self.run_preflight_check(project)
        self.assertNotEqual(r.returncode,0)
        self.assertIn("STOP: before project is not blank/clean",r.stderr)

    def test_launcher_locates_new_owned_report_without_doscript_return_value(self):
        helpers=self.launcher_python_helpers()
        with tempfile.TemporaryDirectory() as directory:
            downloads=Path(directory)
            existing=downloads/"aehl-rsmb-existing"
            existing.mkdir()
            before=set(helpers["evidence_dirs"](downloads))
            created=downloads/"aehl-rsmb-new"
            created.mkdir()
            report=created/"report.json"
            report.write_text("{}\n",encoding="utf-8")
            self.assertEqual(helpers["locate_report"](downloads,before),report)
            second=downloads/"aehl-rsmb-second"
            second.mkdir()
            (second/"report.json").write_text("{}\n",encoding="utf-8")
            with self.assertRaises(SystemExit):
                helpers["locate_report"](downloads,before)

    def test_exact_js_runs_in_mock(self):
        r=subprocess.run(["node",str(ROOT/"tests/rsmb-render-js.cjs"),str(JSX)],
                         text=True,capture_output=True,timeout=10)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("RSMB JSX mocks: 6/6",r.stdout)

if __name__=="__main__":
    unittest.main()
