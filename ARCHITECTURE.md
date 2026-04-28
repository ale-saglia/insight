# Architecture

Insight Notes is a static site built with [Pelican](https://getpelican.com) (Python — version pinned in `requirements.txt`). The published output is a set of plain HTML files deployed to GitHub Pages.

---

## Repository layout

```text
insight/
├── src/                        # Content (Markdown articles + README category pages)
│   ├── _general/               # Leading underscore = hidden from nav, stripped from URLs
│   ├── digital-governance/
│   ├── frontier/
│   │   ├── ai/
│   │   └── quantum-computing/
│   └── infrastructure/
│       └── zero-to-homelab/
├── themes/insight/templates/   # Jinja2 templates
├── plugins/                    # Custom Pelican plugins (modular)
│   ├── insight_register.py     # Entry point; wires Pelican signals to handlers
│   ├── insight_reader.py       # InsightMarkdownReader (YAML frontmatter + Jekyll field mapping)
│   ├── insight_articles.py     # Article enrichment (slugs, breadcrumbs, series nav, reading time)
│   ├── insight_categories.py   # CategoryPageGenerator (README.md → category index pages)
│   └── og_images.py            # OG image generation (Python/Pillow)
├── assets/                     # Static files (CSS, SVGs, OG images)
├── scripts/                    # Build and utility scripts
├── pelicanconf.py              # Local config (RELATIVE_URLS = True)
├── publishconf.py              # Production overrides (RELATIVE_URLS = False)
├── requirements.txt            # Python dependencies
└── versions.env                # PYTHON_VERSION pin (kept in sync with .devcontainer/Dockerfile)
```

---

## Content model

### Articles

Each `.md` file under `src/` (excluding `README.md`) is an article. Frontmatter uses Jekyll-style field names; the plugin maps them to Pelican equivalents:

| Frontmatter key | Pelican field |
|-----------------|---------------|
| `created`       | `date`        |
| `keywords`      | `tags`        |
| `excerpt`       | `summary`     |
| `article_id`    | slug stem     |
| `modified`      | `modified`    |

### Category pages

Each `README.md` in a `src/` subdirectory defines a category index page. These are **not** processed by Pelican's article pipeline; the custom `CategoryPageGenerator` handles them independently via `os.walk`.

---

## URL structure

URLs are derived entirely from the file path, not from the title. The plugin computes `article.slug` as:

```text
<path segments relative to src/> / <article_id>
```

Example: `src/infrastructure/zero-to-homelab/0-why-homelab-matters.md`
→ `article_id = why-homelab-matters` (strips leading `N-` numeric prefix)
→ slug = `infrastructure/zero-to-homelab/why-homelab-matters`
→ URL = `infrastructure/zero-to-homelab/why-homelab-matters/`

Leading underscores in directory names (e.g. `_general`) are stripped from the URL path, making those categories invisible in the nav while still generating articles.

Pelican's built-in category/tag/author index pages are disabled (`*_SAVE_AS = ''`).

---

## The `insight` plugins (`plugins/`)

Site-specific logic is split across four modules, registered by a single entry point. `pelicanconf.py` lists `insight_register` and `og_images` under `PLUGINS`.

### `insight_register.py` — entry point

Wires three Pelican signals:

| Signal | Handler | Purpose |
| -------- | --------- | --------- |
| `readers_init` | `_add_reader` | Registers `InsightMarkdownReader` for `.md` files |
| `article_generator_finalized` | `process_articles` | Enriches every article after Pelican loads them |
| `get_generators` | `_get_generators` | Registers `CategoryPageGenerator` |

### `insight_reader.py` — `InsightMarkdownReader`

Subclasses Pelican's `MarkdownReader`. Parses the YAML frontmatter block itself (using `pyyaml`) rather than relying on Pelican's key=value metadata format. Maps field names and passes processed metadata back to Pelican's standard pipeline.

### `insight_articles.py` — `process_articles` / `_enrich_article`

Runs after all articles are loaded. For each article:

- Computes `slug`, `category_path`, `category_top` from `article.get_relative_source_path()`
  (Note: `article.source_path` is absolute — `get_relative_source_path()` is relative to `PATH`)
- Builds `breadcrumbs` list for the template
- Sets `episode_num` from the leading `N-` in the filename (used for series ordering)
- Calculates `reading_time` (words ÷ 200, minimum 1)
- Populates `modified` from `git log` if not set in frontmatter

After enrichment, articles are grouped by parent directory and sorted by episode number to set `prev_episode` / `next_episode` for series navigation.

### `insight_categories.py` — `CategoryPageGenerator`

Subclasses Pelican's `Generator`. Walks `src/` for `README.md` files, parses their frontmatter, and derives URLs by the same path-based logic. Populates `category_pages` and `top_level_categories` in the shared Pelican context (used by `nav.html` and `article.html`).

During output, injects `direct_articles` and `child_categories` into each category page's template context.

### `og_images.py` — OG image generation

Hooks into `article_generator_finalized` (runs after `process_articles` has set `slug` and `summary`). For each article and the homepage:

- Creates a 1200×630 WebP image using Python/Pillow
- Draws site title, description, article title, excerpt, and domain using DejaVu system fonts
- Outputs to `assets/og-images/[slug].webp` (gitignored)

Reads `SITENAME`, `SITESUBTITLE`, `SITEURL`, and `AUTHOR` from the Pelican settings dict.

---

## Templates (`themes/insight/templates/`)

| Template | Output | Notes |
| ---------- | -------- | ------- |
| `base.html` | — | Layout with meta, OG/Twitter tags, canonical URL |
| `nav.html` | — | Top nav; excludes `general` category |
| `article.html` | Article pages | Breadcrumbs, JSON-LD schema, episode nav, reading time |
| `category.html` | Category index pages | Child categories + direct articles |
| `index.html` | `index.html` | Latest article + 5-article list (hardcoded intro) |
| `archives.html` | `archive/index.html` | JS search/filter with year grouping, URL state |
| `sitemap.xml` | `sitemap.xml` | Via `TEMPLATE_PAGES` |
| `404.html` | `404.html` | Via `TEMPLATE_PAGES` |

Breadcrumb label resolution happens at render time in `article.html`: the template iterates `category_pages` to look up the human-readable title for each path segment, using the Jinja2 namespace trick (`{% set ns = namespace(...) %}`) to mutate a variable inside a loop.

---

## Configuration

`pelicanconf.py` is the base config used for local builds (`RELATIVE_URLS = True`).

`publishconf.py` imports it and overrides for production:

```python
from pelicanconf import *
SITEURL = 'https://insight.ale-saglia.com'
RELATIVE_URLS = False
DELETE_OUTPUT_DIRECTORY = True
```

`README.md` files are excluded via `IGNORE_FILES = ['README.md', ...]`. Pelican 4.x's `_include_path()` checks `IGNORE_FILES` against the basename; `ARTICLE_EXCLUDES` is not checked at that stage.

---

## Build pipeline

### Local

```bash
make setup          # creates .venv, installs requirements.txt
make build          # ensure-frontmatter.sh → pelican (OG images generated by plugin)
make serve          # pelican build → python3 -m http.server 4000
make rebuild        # rm -rf _site && make build
make clean          # rm -rf _site
```

VS Code tasks mirror these under "Pelican: *".

OG images are generated automatically during the Pelican build by the `og_images` plugin (no separate script required).

### CI (GitHub Actions)

`.github/workflows/pages.yml`:

1. Checkout with `fetch-depth: 0` (needed for `git log` modified-date enrichment)
2. Read `PYTHON_VERSION` from `.devcontainer/Dockerfile`
3. `setup-python` with that version
4. `pip install -r requirements.txt`
5. `bash scripts/ensure-frontmatter.sh`
6. `pelican --settings publishconf.py` (OG images generated by plugin during this step)
7. Upload `_site/` as GitHub Pages artifact

`.github/workflows/check-versions.yml` verifies that `PYTHON_VERSION` in `versions.env` matches the `ARG PYTHON_VERSION` in `.devcontainer/Dockerfile`.

---

## Adding content

### New article

Create `src/<category>[/<subcategory>]/<N>-<article-id>.md` with frontmatter:

```yaml
---
layout: article
title: The Title
created: 2026-05-01
keywords: tag1, tag2
excerpt: One-sentence summary shown in listings.
article_id: article-id
---
```

`article_id` sets the URL slug stem. If omitted, the plugin strips the leading `N-` from the filename stem.

### New category

Create `src/<category>/README.md`:

```yaml
---
title: Category Title
summary: Short description shown on the category page.
---
```

The directory name becomes the URL path segment. Prefix with `_` to hide from the nav while still publishing.

### New series

Place numbered articles (`0-intro.md`, `1-setup.md`, …) in the same directory. The plugin detects the numeric prefix, sorts them, and wires up `prev_episode` / `next_episode` automatically.
