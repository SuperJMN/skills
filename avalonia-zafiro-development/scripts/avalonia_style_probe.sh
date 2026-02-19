#!/usr/bin/env bash
set -euo pipefail

PROBE="/home/jmn/skills/avalonia-layout-zafiro/scripts/avalonia_style_probe.py"

if [[ ! -f "$PROBE" ]]; then
  echo "Probe script not found: $PROBE" >&2
  exit 2
fi

exec python3 "$PROBE" "$@"
