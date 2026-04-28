# Local Build & Preview

This document describes how to build and preview the site locally using Python.

## Prerequisites

- Python — version pinned in `versions.env` and `.devcontainer/Dockerfile`
- Recommended: use the VS Code dev container, which sets up the environment automatically

## First-time setup

Create the virtual environment and install dependencies:

```bash
make setup
```

This creates `.venv/` and installs all dependencies from `requirements.txt`.

## Build

```bash
make build
```

This runs `scripts/build-local.sh`, which:

1. Runs `scripts/ensure-frontmatter.sh` — validates and normalises frontmatter on all articles under `src/`
2. Runs `pelican --settings pelicanconf.py` — builds the site into `_site/`

OG images are generated automatically during the Pelican build by the `og_images` plugin (no separate step required).

## Preview

```bash
make serve
```

Builds the site and starts a local HTTP server on port 4000.

Then open: **`http://127.0.0.1:4000/`**

To use a different port:

```bash
./scripts/preview-local.sh 8080
```

## Rebuild from scratch

```bash
make rebuild
```

Deletes `_site/` and runs a full build.

## Clean

```bash
make clean
```

Removes `_site/` only. Does not touch `.venv/`.

## Config files

- **`pelicanconf.py`**: Base config used for local builds (`RELATIVE_URLS = True`).
- **`publishconf.py`**: Production overrides (`SITEURL`, `RELATIVE_URLS = False`, `DELETE_OUTPUT_DIRECTORY = True`). Used by CI only.

## Notes

- The local build uses relative URLs, so all links and assets work correctly when served from the root.
- Dynamic category navigation (from `src/*/README.md` metadata) works the same locally as in production.
- The `_site/` directory is gitignored and ready to be deployed to GitHub Pages.
