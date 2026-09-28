#!/bin/zsh
set -eu
HERE="${0:A:h}"
if [[ -f "$HERE/collect_ae_host.py" ]]; then
  SCRIPT="$HERE/collect_ae_host.py"
else
  SCRIPT="$HERE/../../tools/collect_ae_host.py"
fi
if ! command -v python3 >/dev/null 2>&1; then
  print -u2 'Python 3 is required. Nothing was installed or changed.'
  exit 2
fi
python3 "$SCRIPT"
