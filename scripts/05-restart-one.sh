#!/bin/bash
# Restart ONE named gateway. Never --all.
set -euo pipefail
SLUG="${1:?usage: 04-restart-one.sh SLUG}"
if [[ "$SLUG" == "default" ]]; then
  hermes gateway restart
  hermes gateway status
else
  hermes -p "$SLUG" gateway restart
  hermes -p "$SLUG" gateway status
fi
