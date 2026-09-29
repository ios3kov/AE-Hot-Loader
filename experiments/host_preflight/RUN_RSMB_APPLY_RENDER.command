#!/bin/zsh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
JSX="$HERE/render_rsmb.jsx"
[[ -f "$JSX" ]] || { echo "STOP: render_rsmb.jsx not found next to this launcher"; exit 2; }

if [[ -f "$HERE/AEHL_Preflight_1f8c7fc.py" ]]; then
  PRE="$HERE/AEHL_Preflight_1f8c7fc.py"
elif [[ -f "$HOME/Downloads/AEHL_Preflight_1f8c7fc.py" ]]; then
  PRE="$HOME/Downloads/AEHL_Preflight_1f8c7fc.py"
elif [[ -f "$HERE/../../tools/collect_ae_host.py" ]]; then
  PRE="$HERE/../../tools/collect_ae_host.py"
else
  echo "STOP: preflight collector not found"
  exit 3
fi

pids=($(pgrep -x "After Effects" || true))
(( $#pids == 1 )) || { echo "STOP: exactly one After Effects process required"; exit 4; }
PID="$pids[1]"

check_preflight() {
  local report="$1"
  python3 - "$report" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding="utf-8"))
need={
  "agent_identity":"PASS",
  "registry":"PASS",
  "project_unchanged":"PASS",
}
for k,v in need.items():
    if d.get("checks",{}).get(k,{}).get("status") != v:
        raise SystemExit("STOP: preflight "+k+" is not PASS")
want={"dirty":False,"items":0,"queued":0,"rendering":False,"saved":False}
for phase in ("before","after"):
    project=d.get(phase,{}).get("project")
    if not isinstance(project,dict) or any(
        type(project.get(k)) is not type(v) or project.get(k) != v
        for k,v in want.items()
    ):
        raise SystemExit("STOP: "+phase+" project is not blank/clean")
print("PASS: preflight Agent/RSMB/blank-project")
PY
}

PRE_OUT="$(python3 "$PRE")"
print -r -- "$PRE_OUT"
PRE_REPORT="$(print -r -- "$PRE_OUT" | sed -n 's/^Report: //p' | tail -1)"
[[ -f "$PRE_REPORT" ]] || { echo "STOP: preflight report missing"; exit 5; }
check_preflight "$PRE_REPORT"

pids2=($(pgrep -x "After Effects" || true))
(( $#pids2 == 1 && pids2[1] == PID )) || { echo "STOP: AE process changed after preflight"; exit 6; }

APP="$(python3 - "$PID" <<'PY'
import subprocess,sys
pid=sys.argv[1]
p=subprocess.run(["/bin/ps","-p",pid,"-o","comm="],check=True,capture_output=True,text=True,timeout=5).stdout.strip()
suffix=".app/Contents/MacOS/After Effects"
if suffix not in p:
    raise SystemExit("STOP: cannot identify AE app")
print(p.split(suffix,1)[0]+".app")
PY
)"

REPORT="$(python3 - "$PRE" "$APP" "$JSX" <<'PY'
import importlib.util,os,pathlib,stat,subprocess,sys

def evidence_dirs(downloads):
    result={}
    try:
        entries=downloads.iterdir()
    except OSError as error:
        raise SystemExit("STOP: cannot inspect evidence root: "+str(error))
    for path in entries:
        if not path.name.startswith("aehl-rsmb-"):
            continue
        try:
            info=path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid():
            result[path.name]=path
    return result

def locate_report(downloads,before):
    after=evidence_dirs(downloads)
    created=sorted(set(after)-set(before))
    if len(created) != 1:
        raise SystemExit("STOP: expected exactly one new RSMB evidence directory")
    report=after[created[0]]/"report.json"
    try:
        info=report.lstat()
    except FileNotFoundError:
        raise SystemExit("STOP: RSMB report missing")
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_size <= 0 or info.st_size > 65536):
        raise SystemExit("STOP: invalid RSMB report file")
    return report

pre,app,jsx=sys.argv[1:]
spec=importlib.util.spec_from_file_location("aehl_preflight",pre)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
code=m.applescript(pathlib.Path(app)).replace("with timeout of 20 seconds","with timeout of 45 seconds")
downloads=pathlib.Path.home()/"Downloads"
root_info=downloads.lstat()
if not stat.S_ISDIR(root_info.st_mode) or root_info.st_uid != os.getuid():
    raise SystemExit("STOP: invalid evidence root")
before=set(evidence_dirs(downloads))
subprocess.run(["/usr/bin/osascript","-e",code,jsx],check=True,
               capture_output=True,text=True,timeout=50)
print(locate_report(downloads,before))
PY
)"
[[ -f "$REPORT" ]] || { echo "STOP: RSMB report missing"; exit 7; }

python3 - "$REPORT" <<'PY'
import json,sys
p=sys.argv[1]
d=json.load(open(p,encoding="utf-8"))
for k in ("baseline","apply","render","cleanup"):
    if d.get(k,{}).get("status") not in ("PASS","N/A"):
        raise SystemExit("FAIL: "+k+" -> "+str(d.get(k)))
if d.get("status") != "PASS":
    raise SystemExit("FAIL: "+str(d.get("reason","unknown")))
print("PASS: RSMB apply + one-frame render + cleanup")
print("Report:",p)
PY

DIR="$(dirname "$REPORT")"
files=("$DIR"/rsmb-render-*)
(( $#files > 0 )) || { echo "STOP: rendered output not found"; exit 8; }
shasum -a 256 "${files[@]}" > "$DIR/render.sha256"

pids3=($(pgrep -x "After Effects" || true))
(( $#pids3 == 1 && pids3[1] == PID )) || { echo "STOP: AE process changed during render"; exit 9; }

POST_OUT="$(python3 "$PRE")"
print -r -- "$POST_OUT"
POST_REPORT="$(print -r -- "$POST_OUT" | sed -n 's/^Report: //p' | tail -1)"
[[ -f "$POST_REPORT" ]] || { echo "STOP: postflight report missing"; exit 10; }
check_preflight "$POST_REPORT"

echo
echo "PASS: controlled RSMB apply/render gate"
echo "Evidence: $DIR"
