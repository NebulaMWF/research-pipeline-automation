#!/usr/bin/env bash
set -euo pipefail
"$(dirname "$0")/install_skill.py" --platform claude-code "$@"
