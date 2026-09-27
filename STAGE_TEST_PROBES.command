#!/bin/zsh
set -euo pipefail

HERE="${0:A:h}"
STRICT="$HERE/AEHotLoaderRustProbe.plugin"
PERMISSIVE="$HERE/AEHotLoaderRustProbePermissive.plugin"
DEST="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/AEHotLoaderProbeTest"

for required in "$STRICT" "$PERMISSIVE"; do
  [[ -d "$required" ]] || { echo "Missing: $required"; exit 2; }
done

if ! pgrep -x "Adobe After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects must already be running before staging the probes."
  echo "Open AE first, wait until it is fully loaded, then run this script again."
  exit 3
fi

rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$STRICT" "$DEST/AEHotLoaderRustProbe.plugin"
cp -R "$PERMISSIVE" "$DEST/AEHotLoaderRustProbePermissive.plugin"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true

echo
echo "Staged test probes while After Effects is running:"
echo "  $DEST/AEHotLoaderRustProbe.plugin"
echo "  $DEST/AEHotLoaderRustProbePermissive.plugin"
echo
echo "Now click Reload Plugins in AE Hot Loader."
