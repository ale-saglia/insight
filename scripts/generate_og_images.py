#!/usr/bin/env python3
"""Generate Open Graph preview images for insight notes using Pillow."""

import os
import re
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent

# Palette
COLOR_BG = (255, 255, 255)
COLOR_DARK = (27, 31, 35)     # #1b1f23
COLOR_MUTED = (91, 99, 106)   # #5b636a
COLOR_LINE = (230, 232, 235)  # #e6e8eb

MARGIN = 60
W, H = 1200, 630


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

def _load_font(size: int, *, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    candidates: list[str]
    if serif and bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        ]
    elif serif:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        ]
    elif bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    # Last resort: Pillow built-in bitmap font (no size control)
    return ImageFont.load_default()


def _preload_fonts() -> dict[str, ImageFont.FreeTypeFont]:
    return {
        "serif_bold_100": _load_font(100, bold=True, serif=True),
        "serif_64":       _load_font(64,  bold=False, serif=True),
        "serif_bold_52":  _load_font(52,  bold=True,  serif=True),
        "sans_36":        _load_font(36),
        "sans_28":        _load_font(28),
        "sans_24":        _load_font(24),
    }


# ---------------------------------------------------------------------------
# Site config
# ---------------------------------------------------------------------------

def _get_site_config() -> dict:
    src = (ROOT_DIR / "pelicanconf.py").read_text()

    def get(key: str) -> str:
        m = re.search(rf"^{key}\s*=\s*['\"]([^'\"]+)['\"]", src, re.MULTILINE)
        return m.group(1) if m else ""

    return {
        "title":       get("SITENAME"),
        "description": get("SITESUBTITLE"),
        "url":         get("SITEURL") or "https://insight.ale-saglia.com",
        "author_name": get("AUTHOR"),
    }


# ---------------------------------------------------------------------------
# Article discovery
# ---------------------------------------------------------------------------

def _get_articles() -> list[dict]:
    articles: list[dict] = []
    src_dir = ROOT_DIR / "src"

    for category_dir in sorted(src_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        category_name = category_dir.name

        for md_file in sorted(category_dir.rglob("*.md")):
            if md_file.name == "README.md":
                continue

            content = md_file.read_text(encoding="utf-8")
            m = re.match(r"^---\n([\s\S]*?)\n---", content)
            if not m:
                continue
            try:
                fm: dict = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                fm = {}

            if fm.get("permalink"):
                parts = [p for p in fm["permalink"].split("/") if p]
                category = parts[0]
                slug = parts[1] if len(parts) > 1 else ""
                rel_dir = ""
            else:
                # Match Pelican plugin logic: prefer article_id from frontmatter
                if fm.get("article_id"):
                    slug = str(fm["article_id"])
                else:
                    slug = re.sub(r"^\d+-", "", md_file.stem)
                category = fm.get("category") or category_name
                rel = md_file.parent.relative_to(category_dir)
                rel_dir = "" if str(rel) == "." else str(rel)

            articles.append({
                "title":   str(fm.get("title") or slug),
                "excerpt": str(fm.get("excerpt") or ""),
                "category": category,
                "rel_dir":  rel_dir,
                "slug":     slug,
            })

    return articles


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = current + " " + word if current else word
        if len(candidate) > max_chars:
            if current:
                lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


# ---------------------------------------------------------------------------
# Image drawing
# ---------------------------------------------------------------------------

def _draw_article(
    draw: ImageDraw.ImageDraw,
    site_title: str,
    site_description: str,
    article_title: str,
    excerpt: str,
    domain: str,
    fonts: dict,
) -> None:
    y = 28

    # Header: site name + description + separator
    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["serif_64"])
    y += 72
    draw.text((MARGIN, y), site_description, fill=COLOR_MUTED, font=fonts["sans_28"])
    y += 42
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 30

    # Article title (wrapped, 32 chars/line)
    title_lines = _wrap_text(article_title, 32)
    for i, line in enumerate(title_lines):
        draw.text((MARGIN, y + i * 64), line, fill=COLOR_DARK, font=fonts["serif_bold_52"])
    y += len(title_lines) * 64 + 14

    # Excerpt (wrapped, 60 chars/line, up to 3 lines; fewer when title is long)
    max_excerpt = min(3, max(1, 5 - len(title_lines)))
    excerpt_lines = _wrap_text(excerpt, 60)[:max_excerpt]
    for i, line in enumerate(excerpt_lines):
        draw.text((MARGIN, y + i * 48), line, fill=COLOR_MUTED, font=fonts["sans_28"])
    if excerpt_lines:
        y += len(excerpt_lines) * 48 + 28

    # Footer separator + right-aligned domain
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 14
    tw = _text_width(draw, domain, fonts["sans_28"])
    draw.text((W - MARGIN - tw, y), domain, fill=COLOR_MUTED, font=fonts["sans_28"])


def _draw_homepage(
    draw: ImageDraw.ImageDraw,
    site_title: str,
    site_description: str,
    domain: str,
    author_name: str,
    fonts: dict,
) -> None:
    y = 80

    # Large site title
    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["serif_bold_100"])
    y += 118

    # Description (wrapped, 48 chars/line)
    desc_lines = _wrap_text(site_description, 48)
    for i, line in enumerate(desc_lines):
        draw.text((MARGIN, y + i * 46), line, fill=COLOR_MUTED, font=fonts["sans_36"])
    y += len(desc_lines) * 46 + 24

    # Separator
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 50

    draw.text((MARGIN, y), "Published occasionally. Written for clarity over volume.", fill=COLOR_MUTED, font=fonts["sans_28"])

    # Fixed footer
    footer_y = H - 72
    draw.line([(MARGIN, footer_y), (W - MARGIN, footer_y)], fill=COLOR_LINE, width=1)
    footer_text_y = footer_y + 20
    draw.text((MARGIN, footer_text_y), f"Written and maintained by {author_name}", fill=COLOR_MUTED, font=fonts["sans_24"])
    tw = _text_width(draw, domain, fonts["sans_24"])
    draw.text((W - MARGIN - tw, footer_text_y), domain, fill=COLOR_MUTED, font=fonts["sans_24"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_images() -> None:
    config = _get_site_config()
    articles = _get_articles()

    print(f"Found {len(articles)} articles. Generating OG images...")
    print(f'Site config - Title: "{config["title"]}", Description: "{config["description"]}"')

    domain = re.sub(r"^https?://", "", config["url"])
    author_name = config["author_name"]
    fonts = _preload_fonts()
    out_base = ROOT_DIR / "assets" / "og-images"

    # Homepage
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    _draw_homepage(draw, config["title"], config["description"], domain, author_name, fonts)
    out_base.mkdir(parents=True, exist_ok=True)
    img.save(out_base / "homepage.webp", "WEBP", quality=85)
    print("✓ Generated homepage.webp")

    # Articles
    for article in articles:
        parts = [p for p in [article["category"], article["rel_dir"]] if p]
        og_dir = out_base.joinpath(*parts) if parts else out_base
        og_dir.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGB", (W, H), COLOR_BG)
        draw = ImageDraw.Draw(img)
        _draw_article(
            draw,
            config["title"] or "Insight Notes",
            config["description"] or "Notes",
            article["title"],
            article["excerpt"],
            domain,
            fonts,
        )

        out_path = og_dir / f"{article['slug']}.webp"
        img.save(out_path, "WEBP", quality=85)

        rel = "/".join(filter(None, [article["category"], article["rel_dir"], f"{article['slug']}.webp"]))
        print(f"✓ Generated {rel}")

    print("\n✨ All OG images generated successfully!")


if __name__ == "__main__":
    try:
        generate_images()
    except Exception as exc:
        print(f"Error generating OG images: {exc}", file=sys.stderr)
        sys.exit(1)
