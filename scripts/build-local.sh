#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${JEKYLL_IMAGE:-jekyll/jekyll:4}"
PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"
CONFIG="${1:-_config.yml,_config.local.yml}"

cd "$ROOT_DIR"

# Ensure front matter required fields before any downstream processing
echo "Checking and normalizing article front matter..."
bash "$ROOT_DIR/scripts/ensure-frontmatter.sh"

# Generate OG images before building
echo "🎨 Generating OG preview images..."
bash "$ROOT_DIR/scripts/generate-og-images.sh"

if [[ -n "${DEVCONTAINER:-}" ]]; then
  bundle exec jekyll build --config "$CONFIG"
else
  docker run --rm \
    --platform "$PLATFORM" \
    -v "$ROOT_DIR":/srv/jekyll \
    -w /srv/jekyll \
    "$IMAGE" \
    jekyll build --config "$CONFIG"
fi

echo "Build completed in $ROOT_DIR/_site"
