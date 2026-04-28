# Insight (Source)

Repository for occasional technical and strategic notes on AI, governance, and infrastructure systems.

Published via GitHub Pages. Documentation and content are in English.

---

## 🧭 Approach

Articles are published with intent. The primary aim is clear thinking, not volume.

**Topics:** AI in institutional contexts, data governance, operational infrastructure, systems design.

---

## 🏛️ Governance & Design Principles

The architecture and stack of this project are not merely technical choices, but the practical implementation of core digital governance principles (digital sovereignty, engineering proportionality, and privacy by design).

To understand the rationale and the ethical framework behind these architectural decisions, please read the **[Manifesto & Governance Principles](MANIFESTO.md)**.

---

## 🛠️ Editorial Stack

- **Format**: Markdown for authoring
- **Generation**: Pelican (Python static site generator — version in `requirements.txt`)
- **Delivery**: GitHub Pages
- **Versioning**: Git for history and editorial refinement

---

## 📂 Repository Structure

### Core (Editorial)

```text
.
├── src/
│   ├── infrastructure/           # Infrastructure and operational notes
│   │   └── zero-to-homelab/      # Homelab series (episode-ordered)
│   ├── digital-governance/       # AI and governance systems analysis
│   ├── frontier/                 # AI and emerging technology notes
│   │   ├── ai/                   # AI subcategory
│   │   └── quantum-computing/    # Quantum computing subcategory
│   └── _general/                 # Standalone cross-domain pieces
├── themes/insight/templates/     # Jinja2 templates
│   ├── base.html                 # Base shell (includes nav, head, OG/Twitter tags)
│   ├── article.html              # Article page (breadcrumbs, metadata, episode nav)
│   ├── category.html             # Category index page
│   └── archives.html             # Archive page with search and filters
├── plugins/                      # Custom Pelican plugins
│   ├── insight_register.py       # Entry point; wires Pelican signals to handlers
│   ├── insight_reader.py         # Custom MarkdownReader (YAML frontmatter + Jekyll field mapping)
│   ├── insight_articles.py       # Article enrichment (slugs, breadcrumbs, series nav, reading time)
│   ├── insight_categories.py     # CategoryPageGenerator (README.md → category index pages)
│   └── og_images.py              # OG image generation (Python/Pillow)
├── assets/
│   ├── styles.css                # Site stylesheet
│   ├── favicon.svg               # Site favicon
│   └── *.svg / *.bpmn            # Diagrams used in articles
├── pelicanconf.py                # Base Pelican config (RELATIVE_URLS = True)
├── publishconf.py                # Production overrides (SITEURL, RELATIVE_URLS = False)
└── README.md                     # This file
```

Each category (and nested subcategory) is a directory with a `README.md` that becomes the category index page, served at its natural URL path.

### Build & Deployment

```text
.
├── .devcontainer/
│   ├── Dockerfile               # Dev container image (Python 3.12 + fonts); version pin at top
│   └── devcontainer.json        # VS Code dev container config (ports, postCreateCommand)
├── scripts/
│   ├── build-local.sh           # Local build (ensure-frontmatter + pelican)
│   ├── preview-local.sh         # Build then serve on port 4000
│   └── ensure-frontmatter.sh    # Validates and adds missing article frontmatter fields
├── Makefile                     # Shortcuts: make setup / build / serve / rebuild / clean
├── requirements.txt             # Python dependencies (Pelican, Markdown, PyYAML, Pillow)
├── versions.env                 # PYTHON_VERSION pin (kept in sync with Dockerfile)
└── .github/workflows/pages.yml  # GitHub Pages CI/CD (reads Python version from Dockerfile)
```

### Version Pinning

- **Python**: pinned in `versions.env` (read by CI) and `.devcontainer/Dockerfile` (required before `FROM`). The `check-versions.yml` workflow enforces that they stay in sync. To update, change both files.
- **Python dependencies**: pinned in `requirements.txt`.

---

## ✍️ Publishing

Articles live in `src/[category]/` or `src/[category]/[subcategory]/` as Markdown files with frontmatter. Categories can be nested arbitrarily: a subcategory is just a category directory one level deeper.

Each category directory contains a `README.md` that becomes the category index page. The `insight_articles` plugin derives the permalink, category, and last-modified date directly from the file path and Git history, with no manual configuration needed.

Each article gets a permanent URL and appears in the category index and homepage feed.

---

## 📖 Article Features

- **Reading time**: estimated at build time (~200 wpm) and shown inline with the publication date.
- **Episode ordering**: articles in a series (e.g., `0-intro.md`, `1-setup.md`) are sorted by episode number and display "Episode N" in the metadata.
- **Episode navigation**: the `insight_articles` plugin injects `prev_episode` / `next_episode` data at build time; series articles render previous and next links at the bottom of the page.
- **Dynamic breadcrumbs**: article headers show the full category path as a clickable breadcrumb, regardless of nesting depth.
- **Structured data**: each article includes a JSON-LD `Article` block (Schema.org) for search engine metadata.
- **Responsive navigation**: the site nav displays domain links inline on wide viewports and collapses them into a dropdown menu on narrow ones, with no layout reflow on load (visibility toggled after font-ready).

---

## 🗃️ Archive & Search

The Archive page (`/archive/`) lists all published articles grouped by year, with three composable filters: free-text search, year selection, and keyword tags (AND logic for multi-select). Filter state is persisted in the URL via `history.replaceState`, making filtered views bookmarkable and shareable.

### Implementation: DOM-based filtering

The search is intentionally implemented as pure DOM filtering with no external dependencies. During the Pelican build, all articles are pre-rendered and embedded in the HTML as list items carrying `data-*` attributes (title, year, category, excerpt, keywords). When a filter is applied, a small inline Vanilla JS script sets `display: none` on non-matching nodes and hides empty year headings. No network request, no JSON index, no third-party library.

### Why not the "scalable" approach?

The standard enterprise pattern would be to generate a `search-index.json` at build time and query it client-side via a full-text library (Fuse.js) or a hosted service (Algolia). That approach is deliberately not used here, for three concrete reasons:

1. **The math does not justify it.** At a target rate of 20–25 articles per year, the archive will hold roughly 250 entries after a decade. Toggling `display: none` on 250 pre-loaded DOM nodes is a sub-millisecond browser operation that does not block the main thread. There is no performance problem to solve.

2. **YAGNI.** Adding an async fetch, JSON parsing logic, and an external dependency to handle a dataset this size is over-engineering by definition. The complexity cost is real; the benefit is not.

3. **Zero external dependencies.** The current approach keeps the client payload minimal, eliminates third-party points of failure, and avoids the network round-trip that fetching an index file would require.

This is a deliberate architectural choice grounded in the blog's core editorial constraint: **quality over quantity**. The simplest solution is also the most robust one for the volumes this site will ever see.

---

## 🖼️ Open Graph Images

Each article automatically gets a unique Open Graph preview image generated at build time, used when the article is shared on social media.

**Generation process:**

- `plugins/og_images.py` hooks into the `article_generator_finalized` Pelican signal
- Reads article metadata (title, excerpt) and site settings (SITENAME, SITESUBTITLE, SITEURL) from the Pelican config
- Draws a styled image (1200×630) using Python/Pillow with DejaVu system fonts
- Outputs to `assets/og-images/[category]/[slug].webp`

**Generated for:**

- `homepage.webp` — shared when the site itself is linked
- `[category]/[slug].webp` — each article (automatically tagged in `base.html`)

**Configuration:**

- Site title, subtitle, and domain read from `pelicanconf.py`
- Regenerated on every full build; images are gitignored (build artifacts)

---

## 🚀 Deployment

Automated via GitHub Pages and deployed through `.github/workflows/pages.yml`.
