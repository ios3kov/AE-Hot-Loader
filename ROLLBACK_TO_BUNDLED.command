#!/bin/zsh
set -euo pipefail

DEST_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
DEST="$DEST_DIR/current.dylib"

if ! pgrep -x "After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects must already be running."
  exit 3
fi

rm -f "$DEST" "$DEST_DIR/current.tmp.dylib" /tmp/ae-hot-loader-slow-render-once

echo "External control implementation removed."
echo "Keep AE open and click Reload Plugins."
echo "Expected: reloaded=1 and bundled implementation default-v1 becomes active."
