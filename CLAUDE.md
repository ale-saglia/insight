# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A static blog built with Pelican (Python). Articles in `src/`, output in `_site/`, deployed to GitHub Pages.

- Architecture, content model, plugin pipeline, URL rules, CI: see [docs/architecture.md](docs/architecture.md)
- Local setup and build commands: see [docs/local-development.md](docs/local-development.md) or run `make help`

---

## What's not in other docs

**Tests** (not covered by `make help`):

```bash
make setup-dev                              # includes pytest
.venv/bin/pytest                            # all tests
.venv/bin/pytest tests/test_og_images.py   # single file
```

**`publishconf.py`** is used by CI only. Local builds always use `pelicanconf.py` (via `make build` / `make serve`).

**Python version** is authoritative in `.devcontainer/Dockerfile`. When changing it, update both `versions.env` and `.python-version` to keep CI happy (`check-versions.yml` verifies the sync).
