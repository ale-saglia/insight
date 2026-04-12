#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "📸 Generating OG preview images..."

# Check if node_modules exists, if not install dependencies
if [ ! -d "scripts/og-image-gen/node_modules" ]; then
  echo "Installing dependencies..."
  cd "$ROOT_DIR/scripts/og-image-gen"
  npm install
  cd "$ROOT_DIR"
fi

# Run the image generator
cd "$ROOT_DIR/scripts/og-image-gen"
npm run generate

echo "✅ OG image generation complete"
