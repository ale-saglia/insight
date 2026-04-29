# Insight Notes (Source)

Personal publishing platform for technical and strategic notes on AI, governance, and infrastructure systems.

Content is authored in Markdown, enriched by a custom Python plugin layer, and deployed to GitHub Pages via CI. Repository note: all documentation, comments, and configuration are kept in English for consistency.

## 🛠️ Tech Stack

- **Authoring**: Markdown with YAML frontmatter (Jekyll-compatible field names)
- **Generator**: [Pelican](https://getpelican.com) — Python static site generator
- **Plugins**: Custom Python layer — content enrichment, OG image generation, category pages
- **Delivery**: GitHub Pages
- **CI/CD**: GitHub Actions (build, link check, deploy on push to `main`)
- **Dependency management**: [uv](https://github.com/astral-sh/uv) with hash-pinned lockfiles

## 🏛️ Design rationale

### Content as code
Articles live in version-controlled Markdown files with structured YAML frontmatter. The same discipline applied to software — commit history, diffs, deliberate changes — applies to writing. Editorial evolution is explicit and reproducible.

### Static by default
No database, no server runtime, no CMS. The entire site is a set of pre-rendered HTML files. This eliminates operational surface area and makes the output auditable: what you deploy is exactly what you built.

### Proportionate engineering
Features are sized to actual requirements. Client-side archive search runs on pre-rendered DOM nodes with a small script — no search API, no JSON index, no third-party library. The design criteria are captured in the [Manifesto](docs/manifesto.md).

## 📁 Repository structure

``` text
├── src/       # Source content (Markdown files)
├── plugins/   # Custom Python extension layer for Pelican
├── scripts/   # CI/CD and pre-flight validation utilities
├── docs/      # Architecture, local dev guide, and manifesto
├── tests/     # End-to-end and unit tests suite (pytest)
└── Makefile   # Centralized task runner commands
```

For a full description of the architecture, plugin pipeline, URL rules, and CI steps, see [docs/architecture.md](docs/architecture.md).

## 🔄 Getting started

```bash
make setup    # Create .venv and install dependencies
make build    # Validate frontmatter and build the site into _site/
make serve    # Build + live-reload server on :4000
make preview  # Build + static server on :4000 (closest to production)
```

See [docs/local-development.md](docs/local-development.md) for the full reference, or run `make help`.

## 🌐 Published site

The site is published at [insight.ale-saglia.com](https://insight.ale-saglia.com) via GitHub Pages on every push to `main`.

Each article includes a generated OG image (1200×630 WebP), structured data (Schema.org JSON-LD), reading time, and series navigation where applicable.

## 📄 License

Repository content and generated articles are proprietary.
The build tooling under `plugins/` and `scripts/` is released under the MIT License.
