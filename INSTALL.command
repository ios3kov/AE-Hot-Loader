#!/bin/zsh
set -euo pipefail
setopt null_glob

HERE="${0:A:h}"
PLUGIN="$HERE/AEHotLoader.plugin"
PANEL="$HERE/AE Hot Loader.jsx"
PLUGIN_DEST="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"

if [[ ! -d "$PLUGIN" ]]; then
  echo "AEHotLoader.plugin not found next to this installer."
  exit 2
fi

if [[ ! -f "$PANEL" ]]; then
  echo "AE Hot Loader.jsx not found next to this installer."
  exit 3
fi

mkdir -p "$PLUGIN_DEST"
rm -rf "$PLUGIN_DEST/AEHotLoader.plugin"
cp -R "$PLUGIN" "$PLUGIN_DEST/AEHotLoader.plugin"
xattr -dr com.apple.quarantine "$PLUGIN_DEST/AEHotLoader.plugin" 2>/dev/null || true

installed_panels=0

for ae_pref in "$HOME"/Library/Preferences/Adobe/After\ Effects/*; do
  [[ -d "$ae_pref" ]] || continue
  panel_dir="$ae_pref/Scripts/ScriptUI Panels"
  mkdir -p "$panel_dir"
  cp "$PANEL" "$panel_dir/AE Hot Loader.jsx"
  installed_panels=$((installed_panels + 1))
done

for ae_docs in "$HOME"/Documents/Adobe/After\ Effects*; do
  [[ -d "$ae_docs" ]] || continue
  panel_dir="$ae_docs/Scripts/ScriptUI Panels"
  mkdir -p "$panel_dir"
  cp "$PANEL" "$panel_dir/AE Hot Loader.jsx"
  installed_panels=$((installed_panels + 1))
done

echo
echo "Native helper installed:"
echo "  $PLUGIN_DEST/AEHotLoader.plugin"
echo

if (( installed_panels > 0 )); then
  echo "ScriptUI panel installed into $installed_panels After Effects user folder(s)."
else
  echo "No existing After Effects user ScriptUI folder was found."
  echo "In After Effects use: File > Scripts > Install ScriptUI Panel..."
  echo "and select: $PANEL"
fi

echo
echo "Restart After Effects once after this initial installation."
echo "Then open: Window > AE Hot Loader"
echo "Future plug-in reload tests should not require restarting AE."
