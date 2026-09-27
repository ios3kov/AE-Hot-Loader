#!/bin/zsh
set -euo pipefail
setopt null_glob

HERE="${0:A:h}"
AGENT="$HERE/AEHotLoaderAgent.plugin"
PANEL="$HERE/AE Hot Loader.jsx"
PLUGIN_DEST="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"

for required in "$AGENT" "$PANEL"; do
  [[ -e "$required" ]] || { echo "Missing: $required"; exit 2; }
done

mkdir -p "$PLUGIN_DEST"
rm -rf \
  "$PLUGIN_DEST/AEHotLoader.plugin" \
  "$PLUGIN_DEST/AEHotLoaderBridge.plugin" \
  "$PLUGIN_DEST/AEHotLoaderAgent.plugin"

cp -R "$AGENT" "$PLUGIN_DEST/AEHotLoaderAgent.plugin"

xattr -dr com.apple.quarantine "$PLUGIN_DEST/AEHotLoaderAgent.plugin" 2>/dev/null || true

installed_panels=0
for ae_pref in "$HOME"/Library/Preferences/Adobe/After\ Effects/*; do
  [[ -d "$ae_pref" ]] || continue
  panel_dir="$ae_pref/Scripts/ScriptUI Panels"
  mkdir -p "$panel_dir"
  cp "$PANEL" "$panel_dir/AE Hot Loader.jsx"
  installed_panels=$((installed_panels + 1))
done

echo
echo "Installed native module:"
echo "  $PLUGIN_DEST/AEHotLoaderAgent.plugin"
echo
echo "Installed ScriptUI panel into $installed_panels After Effects preference folder(s)."
echo "Restart After Effects once for the Agent update, then open Window → AE Hot Loader."
