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

typeset -a duplicate_roots
duplicate_roots=(
  "/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"
  "$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"
  "/Library/Application Support/Adobe/Plug-Ins/CC"
  "$HOME/Library/Application Support/Adobe/Plug-Ins/CC"
)
for app_plugins in /Applications/Adobe\ After\ Effects*.app/Contents/Plug-ins; do
  [[ -d "$app_plugins" ]] && duplicate_roots+=("$app_plugins")
done

typeset -a duplicate_plugins
for root in "${duplicate_roots[@]}"; do
  [[ -d "$root" ]] || continue
  while IFS= read -r found; do
    case "$found" in
      "$PLUGIN_DEST/AEHotLoader.plugin"|      "$PLUGIN_DEST/AEHotLoaderBridge.plugin"|      "$PLUGIN_DEST/AEHotLoaderAgent.plugin"|      "$PLUGIN_DEST/AEHotLoaderControlShell.plugin")
        ;;
      *)
        duplicate_plugins+=("$found")
        ;;
    esac
  done < <(
    find "$root" -type d \(       -name "AEHotLoader.plugin" -o       -name "AEHotLoaderBridge.plugin" -o       -name "AEHotLoaderAgent.plugin" -o       -name "AEHotLoaderControlShell.plugin"     \) -prune -print 2>/dev/null
  )
done

if (( ${#duplicate_plugins[@]} > 0 )); then
  echo "ERROR: duplicate AE Hot Loader plug-in(s) found outside the managed user path:"
  for found in "${duplicate_plugins[@]}"; do
    echo "  $found"
  done
  echo
  echo "Remove those old copies first, then run INSTALL.command again."
  exit 4
fi

for required in "$AGENT" "$SHELL" "$PANEL"; do
  [[ -e "$required" ]] || { echo "Missing: $required"; exit 2; }
done

codesign --verify --deep --strict "$AGENT"
codesign --verify --deep --strict "$SHELL"

source_agent_archs="$(lipo -archs "$AGENT/Contents/MacOS/AEHotLoaderAgent" 2>/dev/null || true)"
source_shell_archs="$(lipo -archs "$SHELL/Contents/MacOS/AEHotLoaderControlShell" 2>/dev/null || true)"
[[ "$source_agent_archs" == *arm64* ]] || { echo "ERROR: packaged Agent is not arm64."; exit 5; }
[[ "$source_shell_archs" == *arm64* ]] || { echo "ERROR: packaged Control Shell is not arm64."; exit 5; }

mkdir -p "$PLUGIN_DEST"

BACKUP_ROOT="$HOME/Library/Application Support/AE Hot Loader/backups/loader"
mkdir -p "$BACKUP_ROOT"
STAMP="$(date +%Y%m%dT%H%M%S)-$$"
AGENT_BACKUP="$BACKUP_ROOT/AEHotLoaderAgent-$STAMP.plugin"
SHELL_BACKUP="$BACKUP_ROOT/AEHotLoaderControlShell-$STAMP.plugin"
AGENT_HAD_OLD=0
SHELL_HAD_OLD=0

if [[ -d "$PLUGIN_DEST/AEHotLoaderAgent.plugin" ]]; then
  cp -R "$PLUGIN_DEST/AEHotLoaderAgent.plugin" "$AGENT_BACKUP"
  AGENT_HAD_OLD=1
fi
if [[ -d "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" ]]; then
  cp -R "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" "$SHELL_BACKUP"
  SHELL_HAD_OLD=1
fi

restore_loader_on_error() {
  local rc=$?
  if (( rc != 0 )); then
    echo "Install failed; restoring previous managed AE Hot Loader plug-ins..."
    rm -rf "$PLUGIN_DEST/AEHotLoaderAgent.plugin" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"
    if (( AGENT_HAD_OLD == 1 )); then
      cp -R "$AGENT_BACKUP" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
    fi
    if (( SHELL_HAD_OLD == 1 )); then
      cp -R "$SHELL_BACKUP" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"
    fi
  fi
}
trap restore_loader_on_error EXIT

rm -rf \
  "$PLUGIN_DEST/AEHotLoader.plugin" \
  "$PLUGIN_DEST/AEHotLoaderBridge.plugin" \
  "$PLUGIN_DEST/AEHotLoaderAgent.plugin" \
  "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" \
  "$PLUGIN_DEST/AEHotLoaderProbeTest"

cp -R "$AGENT" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
cp -R "$SHELL" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"

codesign --verify --deep --strict "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
codesign --verify --deep --strict "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"

agent_archs="$(lipo -archs "$PLUGIN_DEST/AEHotLoaderAgent.plugin/Contents/MacOS/AEHotLoaderAgent" 2>/dev/null || true)"
shell_archs="$(lipo -archs "$PLUGIN_DEST/AEHotLoaderControlShell.plugin/Contents/MacOS/AEHotLoaderControlShell" 2>/dev/null || true)"
[[ "$agent_archs" == *arm64* ]] || { echo "ERROR: Agent is not arm64."; exit 5; }
[[ "$shell_archs" == *arm64* ]] || { echo "ERROR: Control Shell is not arm64."; exit 5; }

# Start each shell install from the bundled implementation. This prevents an
# older staged candidate from silently becoming active on the first AE launch.
CONTROL_IMPL_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
BRIDGE_DIR="$HOME/Library/Application Support/AE Hot Loader/bridge"
rm -f "$CONTROL_IMPL_DIR/current.dylib" "$CONTROL_IMPL_DIR/current.tmp.dylib"
rm -f "$BRIDGE_DIR/request.txt" "$BRIDGE_DIR/request.tmp" "$BRIDGE_DIR/response.txt" "$BRIDGE_DIR/response.tmp" 2>/dev/null || true

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

trap - EXIT

echo
echo "Installed native modules:"
echo "  $PLUGIN_DEST/AEHotLoaderAgent.plugin"
echo "  $PLUGIN_DEST/AEHotLoaderControlShell.plugin"
echo
echo "Installed ScriptUI panel into $installed_panels After Effects preference folder(s)."
echo "Restart After Effects once so AE registers the stable shell, then open Window → AE Hot Loader."
echo "After that, implementation dylib updates can be reloaded without restarting AE."
