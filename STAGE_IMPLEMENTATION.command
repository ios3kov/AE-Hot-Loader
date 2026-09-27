#!/bin/zsh
set -euo pipefail

HERE="${0:A:h}"
SOURCE="$HERE/AEHotLoaderControlImpl-candidate.dylib"
DEST_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
DEST="$DEST_DIR/current.dylib"

[[ -f "$SOURCE" ]] || { echo "Missing candidate implementation: $SOURCE"; exit 2; }

mkdir -p "$DEST_DIR"
tmp="$DEST_DIR/current.tmp.dylib"
rm -f "$tmp"
cp "$SOURCE" "$tmp"
mv -f "$tmp" "$DEST"
xattr -d com.apple.quarantine "$DEST" 2>/dev/null || true

echo "Staged implementation:"
echo "  $DEST"
echo
echo "Keep After Effects open and click Reload Plugins in Window → AE Hot Loader."
