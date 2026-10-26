#!/usr/bin/env bash
set -euo pipefail

# Run from any directory while using the project's currently active Python.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

for argument in "$@"; do
  case "$argument" in
    --simulations|--simulations=*)
      echo "Error: run_million.sh always runs exactly 1,000,000 simulations." >&2
      exit 2
      ;;
  esac
done

exec python -m name_picker.simulation --simulations 1000000 "$@"
