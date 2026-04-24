# Insight (Source)

Repository for occasional technical and strategic notes on AI, governance, and infrastructure systems.

Published via GitHub Pages. Documentation and content are in English.

---

## 🧭 Approach

Articles are published with intent. The primary aim is clear thinking, not volume.

**Topics:** AI in institutional contexts, data governance, operational infrastructure, systems design.

---

## 🛠️ Editorial Stack

- **Format**: Markdown for authoring
- **Generation**: Jekyll static site generator
- **Delivery**: GitHub Pages
- **Versioning**: Git for history and editorial refinement

---

## 🤖 AI Usage

AI is used as a writing aid during drafting.
It supports iteration and phrasing, but not idea generation or argument development.
All content is authored and validated manually.

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
│   │   └── ai/                   # AI subcategory
│   └── _general/                 # Standalone cross-domain pieces
├── _layouts/                     # Jekyll templates
├── _plugins/                     # Custom Jekyll plugins
├── _includes/                    # Partials
├── assets/                       # Styles and static files
├── index.md                      # Homepage
├── archive.md                    # Archive index
├── _config.yml                   # Jekyll config
└── README.md                     # This file
```

Each category (and nested subcategory) is a directory with a `README.md` that becomes the category index page, served at its natural URL path.

### Build & Deployment

```text
.
├── scripts/
│   ├── build-local.sh           # Local build script
│   ├── preview-local.sh         # Local preview server
│   ├── ensure-frontmatter.sh    # Adds missing article front matter fields + warnings
│   ├── update-modified-dates.sh # Updates file modified timestamps from Git
│   ├── generate-og-images.sh    # Generates OG images for social media
│   └── og-image-gen/
│       ├── generate.js          # Node.js OG image generator
│       ├── package.json         # Node dependencies (sharp, js-yaml)
│       └── package-lock.json    # Locked dependency versions for reproducible builds
├── feed.xml                     # Atom feed template
├── build-local.md               # Build instructions
├── .github/workflows/pages.yml  # GitHub Pages CI/CD automation
└── _site/                       # Generated static site (build output)
```

---

## ✍️ Publishing

Articles live in `src/[category]/` or `src/[category]/[subcategory]/` as Markdown files with frontmatter. Categories can be nested arbitrarily: a subcategory is just a category directory one level deeper.

Each category directory contains a `README.md` that Jekyll renders as the category index. The custom plugin `_plugins/article_permalink.rb` derives the permalink, category, and last-modified date directly from the file path and Git history, with no manual configuration needed.

Each article gets a permanent URL and appears in the category index and homepage feed.

---

## 📖 Article Features

- **Reading time**: estimated at build time (~200 wpm) and shown inline with the publication date.
- **Episode ordering**: articles in a series (e.g., `01-intro.md`, `02-setup.md`) are sorted by episode number and display "Episode N" in the metadata.
- **Dynamic breadcrumbs**: article headers show the full category path as a clickable breadcrumb, regardless of nesting depth.
- **Structured data**: each article includes a JSON-LD `Article` block (Schema.org) for search engine metadata.

---

## 🖼️ Open Graph Images

Each article automatically gets a unique Open Graph preview image generated at build time, used when the article is shared on social media.

**Generation process:**
- `scripts/og-image-gen/generate.js` reads article frontmatter (title, excerpt, category) and article metadata from `_config.yml`
- Generates an SVG template with styled site header, article title, excerpt, and domain footer
- Converts SVG → WebP via Sharp (1200×630, optimized for social media)
- Outputs to `assets/og-images/[category]/[slug].webp`

**Generated for:**
- `homepage.webp` - shared when the site itself is linked
- `[category]/[slug].webp` - each article (automatically tagged in `_layouts/default.html`)

**Configuration:**
- Site title and description read from `_config.yml`
- YAML parsing uses `js-yaml` for robust support of multiline syntax
- Regenerated on every build; images are gitignored (build artifacts)

---

## 🚀 Deployment

Automated via GitHub Pages and deployed through `.github/workflows/pages.yml`.
