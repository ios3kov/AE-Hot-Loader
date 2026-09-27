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

mkdir -p "$PLUGIN_DEST"
rm -rf \
  "$PLUGIN_DEST/AEHotLoader.plugin" \
  "$PLUGIN_DEST/AEHotLoaderBridge.plugin" \
  "$PLUGIN_DEST/AEHotLoaderAgent.plugin" \
  "$PLUGIN_DEST/AEHotLoaderControlShell.plugin" \
  "$PLUGIN_DEST/AEHotLoaderProbeTest"

cp -R "$AGENT" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"
cp -R "$SHELL" "$PLUGIN_DEST/AEHotLoaderControlShell.plugin"

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

echo
echo "Installed native modules:"
echo "  $PLUGIN_DEST/AEHotLoaderAgent.plugin"
echo "  $PLUGIN_DEST/AEHotLoaderControlShell.plugin"
echo
echo "Installed ScriptUI panel into $installed_panels After Effects preference folder(s)."
echo "Restart After Effects once so AE registers the stable shell, then open Window → AE Hot Loader."
echo "After that, implementation dylib updates can be reloaded without restarting AE."
