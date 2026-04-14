# Local Build & Preview

This document describes how to build and preview the site locally using Docker.

## Prerequisites

- Docker installed and running.
- Python 3 (for serving the preview).

## Build Locally

Build the site with Jekyll using Docker:

```bash
./scripts/build-local.sh
```

Before building, the script now ensures each article in `src/*/*.md` has required front matter keys (`layout`, `title`, `created`, `category`, `keywords`, `excerpt`, `permalink`) without overwriting existing values. Missing `keywords` and `excerpt` raise warnings.

This runs Jekyll with the local config override (`_config.local.yml`) so the site builds at the root path (`/`) instead of under `/insight`.

Output is generated in `_site/`.

## Preview Locally

Start a local HTTP server to preview the built site:

```bash
./scripts/preview-local.sh
```

This will:
1. Run `./scripts/build-local.sh` if `_site` doesn't exist or is stale.
2. Start a Python HTTP server on port 4000.

Then open:

**`http://127.0.0.1:4000/`**

CSS and navigation will load correctly because the local config removes the `/insight` prefix.

## Environment & Script Customization

Both scripts support environment variable overrides:

```bash
# Use a custom Jekyll image
JEKYLL_IMAGE=jekyll/jekyll:3.9 ./scripts/build-local.sh

# Use a custom platform
DOCKER_PLATFORM=linux/arm64 ./scripts/build-local.sh

# Start preview on a different port
./scripts/preview-local.sh 8080
```

## Config Files

- **`_config.yml`**: Production config with `baseurl: ""` (empty unless deploying to subdirectory).
- **`_config.local.yml`**: Local override with `baseurl: ""` for root-level preview.

The build scripts merge both when running locally.

## Notes

- The local build respects all Jekyll templating and Liquid filters.
- Dynamic category navigation (from `src/*/README.md` metadata) works the same locally as in production.
- The static files in `_site` are ready to be deployed to GitHub Pages.
