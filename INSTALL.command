#!/bin/zsh
set -euo pipefail
setopt null_glob

HERE="${0:A:h}"
AGENT="$HERE/AEHotLoaderAgent.plugin"
SHELL="$HERE/AEHotLoaderControlShell.plugin"
PANEL="$HERE/AE Hot Loader.jsx"
PLUGIN_DEST="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"

if pgrep -x "After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects is running."
  echo "Fully quit AE before installing/updating AE Hot Loader."
  exit 3
fi

for required in "$AGENT" "$SHELL" "$PANEL"; do
  [[ -e "$required" ]] || { echo "Missing: $required"; exit 2; }
done

echo "Validating packaged build..."
codesign --verify --deep --strict "$AGENT"
codesign --verify --deep --strict "$SHELL"

source_agent_archs="$(lipo -archs "$AGENT/Contents/MacOS/AEHotLoaderAgent" 2>/dev/null || true)"
source_shell_archs="$(lipo -archs "$SHELL/Contents/MacOS/AEHotLoaderControlShell" 2>/dev/null || true)"
[[ "$source_agent_archs" == *arm64* ]] || { echo "ERROR: packaged Agent is not arm64."; exit 5; }
[[ "$source_shell_archs" == *arm64* ]] || { echo "ERROR: packaged Control Shell is not arm64."; exit 5; }

mkdir -p "$PLUGIN_DEST"

STAMP="$(date +%Y%m%dT%H%M%S)-$$"
USER_BACKUP_ROOT="$HOME/Library/Application Support/AE Hot Loader/backups/install-$STAMP"
SYSTEM_BACKUP_ROOT="/Library/Application Support/AE Hot Loader Legacy Backup/$STAMP"
mkdir -p "$USER_BACKUP_ROOT"

typeset -a scan_roots
scan_roots=(
  "/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"
  "$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"
  "/Library/Application Support/Adobe/Plug-Ins/CC"
  "$HOME/Library/Application Support/Adobe/Plug-Ins/CC"
)
for app_plugins in /Applications/Adobe\ After\ Effects*.app/Contents/Plug-ins; do
  [[ -d "$app_plugins" ]] && scan_roots+=("$app_plugins")
done

is_inside_scan_root() {
  local candidate="$1"
  local root
  for root in "${scan_roots[@]}"; do
    case "$candidate" in
      "$root"|"$root"/*) return 0 ;;
    esac
  done
  return 1
}

is_current_managed() {
  case "$1" in
    "$PLUGIN_DEST/AEHotLoaderAgent.plugin"|"$PLUGIN_DEST/AEHotLoaderControlShell.plugin")
      return 0 ;;
  esac
  return 1
}

typeset -a legacy_targets
typeset -A legacy_seen

record_legacy() {
  local found="$1"
  [[ -n "$found" ]] || return
  is_current_managed "$found" && return

  if ! is_inside_scan_root "$found"; then
    echo "ERROR: refusing to touch path outside known Adobe plug-in roots:"
    echo "  $found"
    exit 6
  fi

  local existing
  for existing in "${legacy_targets[@]}"; do
    case "$found" in
      "$existing"/*) return ;;
    esac
  done

  if [[ -z "${legacy_seen[$found]-}" ]]; then
    legacy_seen[$found]=1
    legacy_targets+=("$found")
  fi
}

for root in "${scan_roots[@]}"; do
  [[ -d "$root" ]] || continue

  while IFS= read -r found; do
    record_legacy "$found"
  done < <(
    find "$root" -type d \(
      -name "AEHotLoaderLiveTest" -o
      -name "AEHotLoaderProbeTest" -o
      -name "AEHotLoader.plugin" -o
      -name "AEHotLoaderBridge.plugin" -o
      -name "AEHotLoaderDualPiPL.plugin" -o
      -name "AEHotLoaderRustProbe.plugin" -o
      -name "AEHotLoaderRustProbePermissive.plugin" -o
      -name "AEHotLoaderSinglePiPLCpp.plugin" -o
      -name "AEHotLoaderAgent.plugin" -o
      -name "AEHotLoaderControlShell.plugin"
    \) -prune -print 2>/dev/null
  )

  while IFS= read -r found; do
    is_current_managed "$found" && continue
    plist="$found/Contents/Info.plist"
    [[ -f "$plist" ]] || continue
    bundle_id="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist" 2>/dev/null || true)"
    case "$bundle_id" in
      com.os3kov.AEHotLoader.*) record_legacy "$found" ;;
    esac
  done < <(find "$root" -type d -name "*.plugin" -prune -print 2>/dev/null)
done

AGENT_OLD="$PLUGIN_DEST/AEHotLoaderAgent.plugin"
SHELL_OLD="$PLUGIN_DEST/AEHotLoaderControlShell.plugin"
AGENT_BACKUP="$USER_BACKUP_ROOT/managed-AEHotLoaderAgent.plugin"
SHELL_BACKUP="$USER_BACKUP_ROOT/managed-AEHotLoaderControlShell.plugin"
AGENT_HAD_OLD=0
SHELL_HAD_OLD=0

if [[ -d "$AGENT_OLD" ]]; then
  mv "$AGENT_OLD" "$AGENT_BACKUP"
  AGENT_HAD_OLD=1
fi
if [[ -d "$SHELL_OLD" ]]; then
  mv "$SHELL_OLD" "$SHELL_BACKUP"
  SHELL_HAD_OLD=1
fi

restore_loader_on_error() {
  local rc=$?
  if (( rc != 0 )); then
    echo
    echo "Install failed; restoring previous managed AE Hot Loader plug-ins..."
    [[ -d "$PLUGIN_DEST/AEHotLoaderAgent.plugin" ]] && mv "$PLUGIN_DEST/AEHotLoaderAgent.plugin" "$USER_BACKUP_ROOT/failed-new-Agent.plugin"
    [[ -d "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" ]] && mv "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" "$USER_BACKUP_ROOT/failed-new-ControlShell.plugin"
    if (( AGENT_HAD_OLD == 1 )) && [[ -d "$AGENT_BACKUP" ]]; then
      mv "$AGENT_BACKUP" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
    fi
    if (( SHELL_HAD_OLD == 1 )) && [[ -d "$SHELL_BACKUP" ]]; then
      mv "$SHELL_BACKUP" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"
    fi
  fi
}
trap restore_loader_on_error EXIT

needs_sudo=0
for found in "${legacy_targets[@]}"; do
  case "$found" in
    /Library/*|/Applications/*) needs_sudo=1 ;;
  esac
done

if (( ${#legacy_targets[@]} > 0 )); then
  echo
  echo "Moving old AE Hot Loader diagnostic/legacy copies out of Adobe plug-in folders:"
  for found in "${legacy_targets[@]}"; do
    echo "  $found"
  done

  if (( needs_sudo == 1 )); then
    echo
    echo "macOS may ask for your password once for old system-wide copies."
    sudo -v
    sudo mkdir -p "$SYSTEM_BACKUP_ROOT"
  fi

  mkdir -p "$USER_BACKUP_ROOT/legacy"
  legacy_index=0
  for found in "${legacy_targets[@]}"; do
    is_inside_scan_root "$found" || { echo "ERROR: cleanup safety check failed: $found"; exit 6; }
    legacy_index=$((legacy_index + 1))
    base="${found:t}"
    case "$found" in
      /Library/*|/Applications/*)
        dest="$SYSTEM_BACKUP_ROOT/${legacy_index}-$base"
        sudo mv "$found" "$dest"
        ;;
      *)
        dest="$USER_BACKUP_ROOT/legacy/${legacy_index}-$base"
        mv "$found" "$dest"
        ;;
    esac
  done
else
  echo
  echo "No old diagnostic/legacy AE Hot Loader copies found."
fi

# Move user-path legacy names out of the active plug-in folder if any remain.
for old_name in AEHotLoader.plugin AEHotLoaderBridge.plugin AEHotLoaderProbeTest AEHotLoaderLiveTest; do
  old_path="$PLUGIN_DEST/$old_name"
  if [[ -e "$old_path" ]]; then
    mv "$old_path" "$USER_BACKUP_ROOT/legacy-user-$old_name"
  fi
done

cp -R "$AGENT" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
cp -R "$SHELL" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"

codesign --verify --deep --strict "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
codesign --verify --deep --strict "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"

agent_archs="$(lipo -archs "$PLUGIN_DEST/AEHotLoaderAgent.plugin/Contents/MacOS/AEHotLoaderAgent" 2>/dev/null || true)"
shell_archs="$(lipo -archs "$PLUGIN_DEST/AEHotLoaderControlShell.plugin/Contents/MacOS/AEHotLoaderControlShell" 2>/dev/null || true)"
[[ "$agent_archs" == *arm64* ]] || { echo "ERROR: Agent is not arm64."; exit 5; }
[[ "$shell_archs" == *arm64* ]] || { echo "ERROR: Control Shell is not arm64."; exit 5; }

CONTROL_IMPL_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
BRIDGE_DIR="$HOME/Library/Application Support/AE Hot Loader/bridge"
mkdir -p "$CONTROL_IMPL_DIR" "$BRIDGE_DIR"

for stale in   "$CONTROL_IMPL_DIR/current.dylib"   "$CONTROL_IMPL_DIR/current.tmp.dylib"   "$BRIDGE_DIR/request.txt"   "$BRIDGE_DIR/request.tmp"   "$BRIDGE_DIR/response.txt"   "$BRIDGE_DIR/response.tmp"; do
  [[ -e "$stale" ]] && mv "$stale" "$USER_BACKUP_ROOT/${stale:t}"
done

for stale_log in /tmp/ae-hot-loader-*.log /tmp/ae-hot-loader-slow-render-once; do
  [[ -e "$stale_log" ]] && mv "$stale_log" "$USER_BACKUP_ROOT/${stale_log:t}"
done

if [[ -d "${TMPDIR:-/tmp}/AEHotLoaderShell" ]]; then
  mv "${TMPDIR:-/tmp}/AEHotLoaderShell" "$USER_BACKUP_ROOT/runtime-AEHotLoaderShell"
fi
if [[ -d "/private/tmp/AEHotLoaderRuntime" ]]; then
  mv "/private/tmp/AEHotLoaderRuntime" "$USER_BACKUP_ROOT/runtime-AEHotLoaderRuntime"
fi

xattr -dr com.apple.quarantine "$PLUGIN_DEST/AEHotLoaderAgent.plugin" 2>/dev/null || true
xattr -dr com.apple.quarantine "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" 2>/dev/null || true

installed_panels=0
for ae_pref in "$HOME"/Library/Preferences/Adobe/After\ Effects/*; do
  [[ -d "$ae_pref" ]] || continue
  panel_dir="$ae_pref/Scripts/ScriptUI Panels"
  mkdir -p "$panel_dir"
  cp "$PANEL" "$panel_dir/AE Hot Loader.jsx"
  installed_panels=$((installed_panels + 1))
done

typeset -a leftovers
for root in "${scan_roots[@]}"; do
  [[ -d "$root" ]] || continue
  while IFS= read -r found; do
    is_current_managed "$found" && continue
    leftovers+=("$found")
  done < <(
    find "$root" -type d \(
      -name "AEHotLoaderLiveTest" -o
      -name "AEHotLoaderProbeTest" -o
      -name "AEHotLoader.plugin" -o
      -name "AEHotLoaderBridge.plugin" -o
      -name "AEHotLoaderDualPiPL.plugin" -o
      -name "AEHotLoaderRustProbe.plugin" -o
      -name "AEHotLoaderRustProbePermissive.plugin" -o
      -name "AEHotLoaderSinglePiPLCpp.plugin" -o
      -name "AEHotLoaderAgent.plugin" -o
      -name "AEHotLoaderControlShell.plugin"
    \) -prune -print 2>/dev/null
  )

  while IFS= read -r found; do
    is_current_managed "$found" && continue
    plist="$found/Contents/Info.plist"
    [[ -f "$plist" ]] || continue
    bundle_id="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist" 2>/dev/null || true)"
    case "$bundle_id" in
      com.os3kov.AEHotLoader.*) leftovers+=("$found") ;;
    esac
  done < <(find "$root" -type d -name "*.plugin" -prune -print 2>/dev/null)
done

if (( ${#leftovers[@]} > 0 )); then
  echo
  echo "ERROR: old AE Hot Loader copy still remains:"
  for found in "${leftovers[@]}"; do
    echo "  $found"
  done
  exit 7
fi

trap - EXIT

echo
echo "CLEAN INSTALL COMPLETE"
echo
echo "Installed:"
echo "  $PLUGIN_DEST/AEHotLoaderAgent.plugin"
echo "  $PLUGIN_DEST/AEHotLoaderControlShell.plugin"
echo
echo "ScriptUI panel installed into $installed_panels After Effects preference folder(s)."
echo "Old Loader diagnostics were moved out of Adobe plug-in folders into backup locations."
echo
echo "Next:"
echo "  1. Start After Effects."
echo "  2. Open Window → AE Hot Loader."
echo "  3. Search Effects & Presets for AE Hot Loader Control Shell."
echo "See QUICK_START.md in this package for the full live-test instructions."
