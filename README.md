# Insight (Source)

This repository contains the source files for a curated collection of technical and strategic articles on digital systems.
The objective is low-frequency, high-signal publishing with a clear separation between content, structure, and presentation.

Repository note: documentation and published content are kept in English for consistency.

## 🛠️ Editorial Stack

- **Format:** Markdown for article authoring.
- **Site layer:** Jekyll for static site generation.
- **Presentation:** GitHub Pages as the public delivery layer.
- **Versioning:** Git for editorial history and iterative refinement.

## 🏛️ Rationale

Most technical writing optimizes for volume.
This repository does not.

Insight is designed to preserve reasoning: trade-offs, constraints, and operational implications behind digital decisions.
Articles are published only when there is something worth structuring and keeping.

## 🧭 Scope

Topics covered:

- AI in real-world contexts (especially public sector and healthcare)
- Data governance and regulatory implications
- Infrastructure, system design, and operational complexity

## 📚 Content Model

1. **Series-based articles**
	- Example: `src/homelab/01-why-homelab.md`, `src/homelab/02-architecture.md`
2. **Standalone articles**
	- Example: `src/general/ai-in-healthcare.md`

Tutorial-style content is out of scope unless explicitly requested.

## 📂 Repository Structure

```text
.
├── src/
│   ├── homelab/        # Sequence-driven series
│   ├── digital-health/ # Domain-focused analysis
│   └── general/        # Standalone cross-topic pieces
├── _posts/             # Optional date-based posts
├── _layouts/           # Jekyll layouts
├── _includes/          # Jekyll partials
├── assets/             # Shared styles and static assets
├── index.md            # Public homepage content
├── README.md
└── _config.yml         # Jekyll configuration
```

## ✍️ Publishing Approach

- Publish rarely, with intent.
- Prioritize clarity over completeness.
- Keep structure minimal and maintainable.
- Prefer analytical framing over commentary.

## 🌐 GitHub Pages

The site is configured for Jekyll on GitHub Pages.
Deployment is automated via GitHub Actions in `.github/workflows/pages.yml`.

For local build and preview instructions, see [build-local.md](build-local.md).
