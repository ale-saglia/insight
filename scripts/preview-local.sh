#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-4000}"

cd "$ROOT_DIR"
# build-local.sh already updates modified dates"$ROOT_DIR/scripts/build-local.sh"

echo "Preview available at: http://127.0.0.1:${PORT}/"
cd "$ROOT_DIR/_site"
python3 -m http.server "$PORT"
