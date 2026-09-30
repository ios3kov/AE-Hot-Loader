#!/bin/zsh
set -eu
cd "${0:A:h}"
exec python3 tools/run_research_checks.py --output-parent "$HOME/Desktop"
