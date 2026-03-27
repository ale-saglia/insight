# Insight Notes

A small, curated repository for occasional technical and strategic writing.

## What this is

This repository is not a second brain, not a personal wiki, and not a volume-driven blog.
It is a focused collection of high-quality articles published when there is something worth saying.

## Publishing approach

- Publish rarely, with intent.
- Prioritize clarity and practical reasoning.
- Keep the system simple and maintainable.
- Use this repository as source of truth and GitHub Pages as presentation layer.

## Focus areas

- AI
- Data governance
- Infrastructure
- System design

## Content model

1. Series-based articles
   - Example: src/homelab/01-why-homelab.md, src/homelab/02-architecture.md
2. Standalone articles
   - Example: src/general/ai-in-healthcare.md

## Structure

- src/homelab/: sequence-driven series articles
- src/ai-healthcare/: domain-specific standalone or short series
- src/general/: standalone cross-topic pieces
- _posts/: optional, date-based posts (kept available but not required)

## GitHub Pages

This project is configured for Jekyll on GitHub Pages with minimal dependencies.
Deployment is automated via GitHub Actions in .github/workflows/pages.yml.
