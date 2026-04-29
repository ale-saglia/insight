# Local Build & Preview

This document describes how to build and preview the site locally using Python.

## Prerequisites

- Python — version pinned in `.python-version` (authoritative source); `.devcontainer/Dockerfile` is kept in sync by `check-versions.yml`
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

This:

1. Runs `scripts/ensure_frontmatter.py` — validates and normalises frontmatter on all articles under `src/`
2. Runs `pelican --settings pelicanconf.py` — builds the site into `_site/`

OG images are generated automatically during the Pelican build by the `og_images` plugin (no separate step required).

## Preview

### Live-reload (recommended for authoring)

```bash
make serve
```

Builds the site and starts Pelican's live-reload server on port 4000. Changes to content or templates are picked up automatically.

### Static preview

```bash
make preview
```

Builds the site and serves `_site/` as a plain static directory — closest to production behaviour.

Then open: **`http://127.0.0.1:4000/`**

To use a different port:

```bash
make serve PORT=8080
make preview PORT=8080
```

## Rebuild from scratch

```bash
make rebuild
```

Deletes `_site/` and runs a full build.

## Recompile dependencies

```bash
make compile
```

Recompiles `requirements.txt` and `requirements-dev.txt` from their `.in` source files using `uv`. Run after editing a `.in` file, then re-run `make setup` or `make setup-dev` to install the updated packages.

## Check internal links

```bash
make check-links
```

Requires a prior build and dev dependencies (`make setup-dev`).

Spins up a temporary HTTP server on `CHECK_PORT` (default `4567`) and runs linkchecker against it. A local server is needed because linkchecker does not resolve absolute paths (e.g. `/feed.xml`) on `file://` URLs. Port `4567` is intentionally different from `PORT` (`4000`) so the check can run while a preview server is already up.

To override the port:

```bash
make check-links CHECK_PORT=9000
```

The same check runs automatically in CI after every push.

## Run tests

```bash
make setup-dev   # includes pytest
make test        # run the full test suite
```

To run a single file directly:

```bash
.venv/bin/pytest tests/test_og_images.py
```

## Clean

```bash
make clean
```

Removes `_site/` only. Does not touch `.venv/`.

## Config files

- **`pelicanconf.py`**: Base config used for local builds (`RELATIVE_URLS = True`).
- **`publishconf.py`**: Production overrides (`SITEURL`, `RELATIVE_URLS = False`, `DELETE_OUTPUT_DIRECTORY = False`). Used by CI only.

## Notes

- The local build uses relative URLs, so all links and assets work correctly when served from the root.
- Dynamic category navigation (from `src/*/README.md` metadata) works the same locally as in production.
- The `_site/` directory is gitignored and ready to be deployed to GitHub Pages.
