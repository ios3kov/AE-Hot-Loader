#!/bin/zsh
set -u

echo "----- AE HOT LOADER AGENT -----"
cat /tmp/ae-hot-loader-agent.log 2>/dev/null || echo "(no agent log)"
echo
echo "----- SHELL RELOADER -----"
cat /tmp/ae-hot-loader-shell-reloader.log 2>/dev/null || echo "(no shell reloader log)"
echo
echo "----- CONTROL SHELL -----"
cat /tmp/ae-hot-loader-shell.log 2>/dev/null || echo "(no control shell log)"
echo
echo "----- IMPLEMENTATION -----"
cat /tmp/ae-hot-loader-implementation.log 2>/dev/null || echo "(no implementation log)"
echo
echo "----- ELASTICGRID SHELL -----"
cat /tmp/ae-hot-loader-elasticgrid-shell.log 2>/dev/null || echo "(no ElasticGrid shell log)"
echo
echo "----- STELLAR GRADIENT SHELL -----"
cat /tmp/ae-hot-loader-stellar-gradient-shell.log 2>/dev/null || echo "(no Stellar Gradient shell log)"
