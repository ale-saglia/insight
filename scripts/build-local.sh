#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Ensure front matter required fields before any downstream processing
echo "Checking and normalizing article front matter..."
bash "$ROOT_DIR/scripts/ensure-frontmatter.sh"

echo "Building with Pelican..."
if [[ -x "$ROOT_DIR/.venv/bin/pelican" ]]; then
  "$ROOT_DIR/.venv/bin/pelican" --settings pelicanconf.py
elif command -v pelican &>/dev/null; then
  pelican --settings pelicanconf.py
else
  echo "Error: pelican not found. Run: make setup"
  exit 1
fi

echo "Build completed in $ROOT_DIR/_site"
