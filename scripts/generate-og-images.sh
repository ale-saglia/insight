#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "📸 Generating OG preview images..."

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
  PYTHON="python3"
else
  echo "Error: python3 not found. Run: make setup"
  exit 1
fi

"$PYTHON" "$ROOT_DIR/scripts/generate_og_images.py"

echo "✅ OG image generation complete"
