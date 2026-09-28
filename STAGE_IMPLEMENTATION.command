#!/bin/zsh
set -euo pipefail

HERE="${0:A:h}"
SOURCE="$HERE/AEHotLoaderControlImpl-candidate.dylib"
DEST_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
DEST="$DEST_DIR/current.dylib"

[[ -f "$SOURCE" ]] || { echo "Missing candidate implementation: $SOURCE"; exit 2; }

if ! pgrep -x "After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects must already be running."
  exit 3
fi

codesign --verify --strict "$SOURCE"

archs="$(lipo -archs "$SOURCE" 2>/dev/null || true)"
[[ "$archs" == *arm64* ]] || {
  echo "ERROR: candidate implementation is not arm64."
  exit 4
}

xcrun vtool -show-build "$SOURCE" | grep -Eq 'minos[[:space:]]+11\.0' || {
  echo "ERROR: candidate implementation has an unexpected macOS deployment target."
  xcrun vtool -show-build "$SOURCE"
  exit 5
}

mkdir -p "$DEST_DIR"
tmp="$DEST_DIR/current.tmp.dylib"
rm -f "$tmp"
cp "$SOURCE" "$tmp"
xattr -d com.apple.quarantine "$tmp" 2>/dev/null || true
codesign --verify --strict "$tmp"
mv -f "$tmp" "$DEST"

echo "Staged implementation:"
echo "  $DEST"
echo
echo "Keep After Effects open and click Reload Plugins in Window → AE Hot Loader."
