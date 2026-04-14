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

## 📂 Repository Structure

### Core (Editorial)

```text
.
├── src/
│   ├── homelab/        # Infrastructure and operational notes
│   ├── digital-health/ # AI and healthcare systems analysis
│   └── general/        # Standalone cross-domain pieces
├── _layouts/           # Jekyll templates
├── _includes/          # Partials
├── assets/             # Styles and static files
├── index.md            # Homepage
├── archive.md          # Archive index
├── _config.yml         # Jekyll config
└── README.md           # This file
```

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

Articles live in `src/[category]/` as Markdown files with frontmatter (title, date, category).

Each article gets a permanent URL and appears in the category index and homepage feed.

---

## 🖼️ Open Graph Images

Each article automatically gets a unique Open Graph preview image generated at build time, used when the article is shared on social media.

**Generation process:**
- `scripts/og-image-gen/generate.js` reads article frontmatter (title, excerpt, category) and article metadata from `_config.yml`
- Generates an SVG template with styled site header, article title, excerpt, and domain footer
- Converts SVG → PNG via Sharp (1200×630, optimized for social media)
- Outputs to `assets/og-images/[category]/[slug].png`

**Generated for:**
- `homepage.png` — shared when the site itself is linked
- `[category]/[slug].png` — each article (automatically tagged in `_layouts/default.html`)

**Configuration:**
- Site title and description read from `_config.yml`
- YAML parsing uses `js-yaml` for robust support of multiline syntax
- Regenerated on every build; images are gitignored (build artifacts)

---

## 🚀 Deployment

Automated via GitHub Pages and deployed through `.github/workflows/pages.yml`.
