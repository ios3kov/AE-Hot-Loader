#!/bin/zsh
set -euo pipefail

HERE="${0:A:h}"
STRICT="$HERE/AEHotLoaderRustProbe.plugin"
PERMISSIVE="$HERE/AEHotLoaderRustProbePermissive.plugin"
ELASTIC="/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/FSTR FX/ElasticGrid.plugin"
STELLAR="/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/FSTR FX/StellarGradient.plugin"
DEST="$HOME/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/AEHotLoaderProbeTest"

for required in "$STRICT" "$PERMISSIVE" "$ELASTIC" "$STELLAR"; do
  [[ -d "$required" ]] || { echo "Missing: $required"; exit 2; }
done

if ! pgrep -x "After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects must already be running before staging the probes."
  echo "Open AE first, wait until it is fully loaded, then run this script again."
  exit 3
fi

rm -f /tmp/ae-hot-loader-rust-probe-permissive.log
rm -f /tmp/ae-hot-loader-diagnostic-report.log
rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$ELASTIC" "$DEST/ElasticGrid.plugin"
cp -R "$STELLAR" "$DEST/StellarGradient.plugin"
cp -R "$STRICT" "$DEST/AEHotLoaderRustProbe.plugin"
cp -R "$PERMISSIVE" "$DEST/AEHotLoaderRustProbePermissive.plugin"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true

echo
echo "Staged all four diagnostic bundles while After Effects is running:"
echo "  $DEST/ElasticGrid.plugin"
echo "  $DEST/StellarGradient.plugin"
echo "  $DEST/AEHotLoaderRustProbe.plugin"
echo "  $DEST/AEHotLoaderRustProbePermissive.plugin"
echo
echo "Now click Reload Plugins in AE Hot Loader."

echo
echo "Verification:"
for bundle in ElasticGrid.plugin StellarGradient.plugin AEHotLoaderRustProbe.plugin AEHotLoaderRustProbePermissive.plugin; do
  if [[ -d "$DEST/$bundle" ]]; then
    echo "  OK  $bundle"
  else
    echo "  MISSING  $bundle"
    exit 4
  fi
done

echo
echo "All 4 bundles are staged. Now click Reload Plugins exactly once."
