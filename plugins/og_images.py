"""
OG image generation — produces WebP images in assets/og-images/ for every
article and the site homepage, triggered during the Pelican build.

Hooks into article_generator_finalized so articles are already enriched
(slug, summary) by insight_articles.process_articles.
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from pelican import signals
from PIL import Image, ImageDraw, ImageFont


# ── Palette & dimensions ──────────────────────────────────────────────────────

COLOR_BG   = (255, 255, 255)
COLOR_DARK = (27, 31, 35)     # #1b1f23
COLOR_MUTED = (91, 99, 106)   # #5b636a
COLOR_LINE  = (230, 232, 235) # #e6e8eb

MARGIN = 60
W, H = 1200, 630


# ── Fonts ─────────────────────────────────────────────────────────────────────

def _load_font(size, *, bold=False, serif=False):
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
    return ImageFont.load_default()


def _preload_fonts():
    return {
        "serif_bold_100": _load_font(100, bold=True, serif=True),
        "serif_64":       _load_font(64,  serif=True),
        "serif_bold_52":  _load_font(52,  bold=True, serif=True),
        "sans_36":        _load_font(36),
        "sans_28":        _load_font(28),
        "sans_24":        _load_font(24),
    }


# ── Text helpers ──────────────────────────────────────────────────────────────

def _wrap_text(text, max_chars):
    lines, current = [], ""
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


def _text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


# ── Drawing ───────────────────────────────────────────────────────────────────

def _draw_article(draw, site_title, site_description, article_title, excerpt, domain, fonts):
    y = 28

    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["serif_64"])
    y += 72
    draw.text((MARGIN, y), site_description, fill=COLOR_MUTED, font=fonts["sans_28"])
    y += 42
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 30

    title_lines = _wrap_text(article_title, 32)
    for i, line in enumerate(title_lines):
        draw.text((MARGIN, y + i * 64), line, fill=COLOR_DARK, font=fonts["serif_bold_52"])
    y += len(title_lines) * 64 + 14

    max_excerpt = min(3, max(1, 5 - len(title_lines)))
    excerpt_lines = _wrap_text(excerpt, 60)[:max_excerpt]
    for i, line in enumerate(excerpt_lines):
        draw.text((MARGIN, y + i * 48), line, fill=COLOR_MUTED, font=fonts["sans_28"])
    if excerpt_lines:
        y += len(excerpt_lines) * 48 + 28

    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 14
    tw = _text_width(draw, domain, fonts["sans_28"])
    draw.text((W - MARGIN - tw, y), domain, fill=COLOR_MUTED, font=fonts["sans_28"])


def _draw_homepage(draw, site_title, site_description, domain, author_name, fonts):
    y = 80

    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["serif_bold_100"])
    y += 118

    desc_lines = _wrap_text(site_description, 48)
    for i, line in enumerate(desc_lines):
        draw.text((MARGIN, y + i * 46), line, fill=COLOR_MUTED, font=fonts["sans_36"])
    y += len(desc_lines) * 46 + 24

    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 50
    draw.text((MARGIN, y), "Published occasionally. Written for clarity over volume.", fill=COLOR_MUTED, font=fonts["sans_28"])

    footer_y = H - 72
    draw.line([(MARGIN, footer_y), (W - MARGIN, footer_y)], fill=COLOR_LINE, width=1)
    footer_text_y = footer_y + 20
    draw.text((MARGIN, footer_text_y), f"Written and maintained by {author_name}", fill=COLOR_MUTED, font=fonts["sans_24"])
    tw = _text_width(draw, domain, fonts["sans_24"])
    draw.text((W - MARGIN - tw, footer_text_y), domain, fill=COLOR_MUTED, font=fonts["sans_24"])


# ── Plugin hook ───────────────────────────────────────────────────────────────

def _generate(generator):
    settings   = generator.settings
    site_title = settings.get('SITENAME', '')
    site_desc  = settings.get('SITESUBTITLE', '')
    site_url   = settings.get('SITEURL', '') or 'https://insight.ale-saglia.com'
    author     = settings.get('AUTHOR', '')
    domain     = re.sub(r'^https?://', '', site_url)

    fonts    = _preload_fonts()
    out_base = Path(generator.path) / 'assets' / 'og-images'

    # Homepage
    img = Image.new('RGB', (W, H), COLOR_BG)
    _draw_homepage(ImageDraw.Draw(img), site_title, site_desc, domain, author, fonts)
    out_base.mkdir(parents=True, exist_ok=True)
    img.save(out_base / 'homepage.webp', 'WEBP', quality=85)
    print('✓ OG: homepage.webp')

    # Articles — slug already set by insight_articles.process_articles
    for article in generator.articles:
        slug = getattr(article, 'slug', '')
        if not slug:
            continue

        # Strip HTML from summary to get plain text for the image
        summary = re.sub(r'<[^>]+>', '', getattr(article, 'summary', '') or '')

        out_path = out_base / f'{slug}.webp'
        out_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.new('RGB', (W, H), COLOR_BG)
        _draw_article(
            ImageDraw.Draw(img),
            site_title, site_desc,
            article.title or slug,
            summary,
            domain,
            fonts,
        )
        img.save(out_path, 'WEBP', quality=85)
        print(f'✓ OG: {slug}.webp')


def register():
    signals.article_generator_finalized.connect(_generate)
