#!/bin/zsh
set -euo pipefail
umask 077

HERE="${0:A:h}"
BRANCH="research/ordinary-plugin-discovery"
HOST="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects"
APP="/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app"
PLUGIN_ROOT="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"
BUILDER="$HERE/experiments/ordinary_discovery/build_no_scan_directory_probe.py"
SUPERVISOR="$HERE/experiments/ordinary_discovery/run_no_scan_directory_probe.py"

blocked() {
  print -u2 -- "BLOCKED: $*"
  exit 2
}

require_file() {
  [[ -f "$1" ]] || blocked "missing file: $1"
}

cd "$HERE"
[[ "$(git rev-parse --show-toplevel 2>/dev/null)" == "$HERE" ]] ||
  blocked "run the checked-in launcher from the AE-Hot-Loader repository root"
[[ "$(git branch --show-current)" == "$BRANCH" ]] ||
  blocked "wrong branch; expected $BRANCH"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] ||
  blocked "local checkout has changes; nothing was reset or overwritten"

# Synchronize only by fast-forward, before any build/install/AE action.
git fetch --quiet origin "$BRANCH"
REMOTE_HEAD="$(git rev-parse "origin/$BRANCH")"
LOCAL_HEAD="$(git rev-parse HEAD)"
if [[ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]]; then
  git merge --ff-only "origin/$BRANCH" >/dev/null ||
    blocked "local checkout cannot fast-forward safely"
  exec "$HERE/RUN_LIVE_NO_SCAN_GATE.command"
fi

[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] ||
  blocked "checkout changed after synchronization"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse "origin/$BRANCH")" ]] ||
  blocked "checkout is not the current research head"

require_file "$HOST"
require_file "$APP/Contents/Info.plist"
VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$APP/Contents/Info.plist" 2>/dev/null || true)"
[[ "$VERSION" == 25.6* ]] || blocked "installed After Effects is not the reviewed 25.6 host"

# Never terminate or replace a user's existing AE session.
if pgrep -x "After Effects" >/dev/null 2>&1; then
  blocked "After Effects is already running; quit it normally before this one-shot gate"
fi

require_file "$BUILDER"
require_file "$SUPERVISOR"
command -v python3 >/dev/null 2>&1 || blocked "python3 is unavailable"
command -v Rez >/dev/null 2>&1 || blocked "Rez is unavailable; Xcode command-line tools are required"
command -v codesign >/dev/null 2>&1 || blocked "codesign is unavailable"
command -v ditto >/dev/null 2>&1 || blocked "ditto is unavailable"

find_sdk() {
  if [[ -n "${AEHL_SDK:-}" ]]; then
    local supplied="${AEHL_SDK:A}"
    [[ -f "$supplied/Headers/AE_GeneralPlug.h" && -f "$supplied/Resources/AE_General.r" ]] ||
      blocked "AEHL_SDK does not point to the extracted AE 25.6 SDK root"
    print -r -- "$supplied"
    return
  fi

  local -a roots candidates unique
  roots=("$HERE" "$HOME/Downloads" "$HOME/Documents")
  for base in "${roots[@]}"; do
    [[ -d "$base" ]] || continue
    while IFS= read -r header; do
      local root="${header:h:h}"
      [[ -f "$root/Resources/AE_General.r" ]] && candidates+=("${root:A}")
    done < <(find "$base" -maxdepth 6 -type f -path '*/Headers/AE_GeneralPlug.h' 2>/dev/null)
  done
  unique=("${(u)candidates[@]}")
  (( ${#unique[@]} == 1 )) ||
    blocked "expected exactly one extracted AE SDK; set AEHL_SDK=/absolute/path/to/sdk"
  print -r -- "$unique[1]"
}

SDK="$(find_sdk)"
mkdir -p "$PLUGIN_ROOT"

BUILD_OUTPUT="$(python3 "$BUILDER"   --sdk "$SDK"   --authorized-host "$HOST"   --authorized-plugin-root "$PLUGIN_ROOT")" ||
  blocked "no-scan helper build failed"

BUILD_DIR="$(print -r -- "$BUILD_OUTPUT" | sed -n '1p')"
MANIFEST_SHA="$(print -r -- "$BUILD_OUTPUT" | sed -n 's/^manifest_sha256=//p' | head -n 1)"
[[ -n "$BUILD_DIR" && -d "$BUILD_DIR" && -n "$MANIFEST_SHA" ]] ||
  blocked "builder did not produce an identified candidate"
MANIFEST="$BUILD_DIR/manifest.json"
require_file "$MANIFEST"

CANDIDATE_BUNDLE="$(python3 - "$MANIFEST" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['candidate_bundle'])
PY
)"
AUTHORIZED_BUNDLE="$(python3 - "$MANIFEST" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['authorized_bundle'])
PY
)"
TOKEN="$(python3 - "$MANIFEST" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['activation_env']['AEHL_NOSCAN_GATE_TOKEN'])
PY
)"

[[ -d "$CANDIDATE_BUNDLE" ]] || blocked "candidate bundle is missing"
[[ ! -e "$AUTHORIZED_BUNDLE" ]] || blocked "unique helper destination already exists"

# Install only this newly built research helper. No existing plug-in is replaced.
ditto "$CANDIDATE_BUNDLE" "$AUTHORIZED_BUNDLE"
codesign --verify --deep --strict "$AUTHORIZED_BUNDLE" ||
  blocked "installed helper signature verification failed"

# Confirm installed bytes match the candidate before launching AE.
python3 - "$MANIFEST" <<'PY'
import hashlib, json, os, pathlib, sys
record = json.load(open(sys.argv[1], encoding='utf-8'))
bundle = pathlib.Path(record['authorized_bundle'])
actual = {}
for path in sorted(bundle.rglob('*')):
    if path.is_file():
        actual[str(path.relative_to(bundle))] = hashlib.sha256(path.read_bytes()).hexdigest()
if actual != record['files']:
    raise SystemExit("installed helper bytes differ from manifest")
PY

CONTROL_DIR="$(python3 - "$MANIFEST" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['control_directory'])
PY
)"
READY="$CONTROL_DIR/ready.txt"
[[ ! -e "$READY" ]] || blocked "candidate control directory was already used"

print -- "Launching reviewed AE once for no-scan folder lifecycle gate..."
env AEHL_NOSCAN_GATE_TOKEN="$TOKEN" "$HOST" >/dev/null 2>&1 &
AE_PID=$!

# Do not kill/restart AE on failure. Preserve the installed inert helper and evidence.
for _ in {1..450}; do
  [[ -f "$READY" ]] && break
  kill -0 "$AE_PID" 2>/dev/null || blocked "After Effects exited before helper ready evidence"
  sleep 0.2
done
[[ -f "$READY" ]] || blocked "helper did not become ready; no native request was published"

print -- "Helper ready in AE PID $AE_PID. Publishing the single authorized request..."
exec python3 "$SUPERVISOR" "$MANIFEST"   --sha256 "$MANIFEST_SHA"   --pid "$AE_PID"   --timeout 45   --authorized-host "$HOST"   --authorized-bundle "$AUTHORIZED_BUNDLE"   --authorize-private-file-call   --authorize-provider-retention   --execute
