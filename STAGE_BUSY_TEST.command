#!/bin/zsh
set -euo pipefail

HERE="${0:A:h}"
SOURCE="$HERE/AEHotLoaderControlImpl-candidate-v3.dylib"
DEST_DIR="$HOME/Library/Application Support/AE Hot Loader/implementations/control"
DEST="$DEST_DIR/current.dylib"
SENTINEL="/tmp/ae-hot-loader-slow-render-once"

[[ -f "$SOURCE" ]] || { echo "Missing busy-test candidate: $SOURCE"; exit 2; }

if ! pgrep -x "After Effects" >/dev/null 2>&1; then
  echo "ERROR: After Effects must already be running."
  exit 3
fi

codesign --verify --strict "$SOURCE"

archs="$(lipo -archs "$SOURCE" 2>/dev/null || true)"
[[ "$archs" == *arm64* ]] || {
  echo "ERROR: candidate-v3 is not arm64."
  exit 4
}

xcrun vtool -show-build "$SOURCE" | grep -Eq 'minos[[:space:]]+11\.0' || {
  echo "ERROR: candidate-v3 has an unexpected macOS deployment target."
  exit 5
}

mkdir -p "$DEST_DIR"
tmp="$DEST_DIR/current.tmp.dylib"
rm -f "$tmp"
cp "$SOURCE" "$tmp"
xattr -d com.apple.quarantine "$tmp" 2>/dev/null || true
codesign --verify --strict "$tmp"
mv -f "$tmp" "$DEST"

rm -f "$SENTINEL"
touch "$SENTINEL"

echo "Busy-render live gate armed."
echo
echo "1. Make sure candidate-v2 is already active."
echo "2. In AE, purge cache if needed and start a fresh Preview/render of the Control Shell."
echo "3. Do NOT click Reload during the ~8 second hold; the in-process self-test triggers it automatically."
echo "4. After render finishes, run: cat /tmp/ae-hot-loader-implementation.log"
echo "5. Expected: BusySelfTest result=-4112 with a busy/in-flight message."
echo "6. Then click Reload Plugins once."
echo "7. Expected: candidate-v3 reload succeeds."
