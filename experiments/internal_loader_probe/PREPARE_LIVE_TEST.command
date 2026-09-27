#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h}"
PLUGIN="$ROOT/AEHotLoaderDualPiPL.plugin"
PROBE="$ROOT/libAEHotLoaderInternalProbe.dylib"
DEST="/private/tmp/AEHotLoaderProbe"

if [[ ! -d "$PLUGIN" ]]; then
  print -u2 "Missing: $PLUGIN"
  exit 2
fi
if [[ ! -f "$PROBE" ]]; then
  print -u2 "Missing: $PROBE"
  exit 3
fi

rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$PLUGIN" "$DEST/"

xattr -dr com.apple.quarantine "$PLUGIN" "$PROBE" "$DEST" 2>/dev/null || true
codesign --verify --deep --strict "$DEST/AEHotLoaderDualPiPL.plugin"
codesign --verify --strict "$PROBE"

rm -f /tmp/ae-hot-loader-internal-probe.log /tmp/ae-hot-loader-dualpipl.log

print ""
print "Prepared:"
print "  $DEST/AEHotLoaderDualPiPL.plugin"
print ""
print "Probe dylib:"
print "  $PROBE"
print ""
print "In LLDB, after AE 25.6 has finished starting, pause on the main thread and run:"
print ""
print "expr (void*)dlopen(\"$PROBE\", 2)"
print "expr (int)((int(*)(const char*))dlsym((void*)-2, \"AEHotLoader_InternalLoaderProbe\"))(\"/tmp/AEHotLoaderProbe\")"
print ""
print "Then in Terminal:"
print "  cat /tmp/ae-hot-loader-internal-probe.log"
print "  cat /tmp/ae-hot-loader-dualpipl.log"
