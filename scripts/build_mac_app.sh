#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

python -m pip install pyinstaller
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Baby Name Picker" \
  --icon assets/baby-name-picker.icns \
  --paths src \
  scripts/launch_gui.py

echo
echo "Built: $PROJECT_DIR/dist/Baby Name Picker.app"
echo "Open it with: open \"$PROJECT_DIR/dist/Baby Name Picker.app\""
