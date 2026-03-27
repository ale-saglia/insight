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
├── _config.yml         # Jekyll config
└── README.md           # This file
```

---

## ✍️ Publishing

Articles live in `src/[category]/` as Markdown files with frontmatter (title, date, category).

Each article gets a permanent URL and appears in the category index and homepage feed.

---

## 🌐 Local Build and Preview

See [build-local.md](build-local.md) for instructions.

---

## 🚀 Deployment

Automated via GitHub Pages and deployed through `.github/workflows/pages.yml`.
