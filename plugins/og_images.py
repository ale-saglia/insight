"""
OG image generation — produces WebP images in assets/og-images/ for every
article and the site homepage, triggered during the Pelican build.

Hooks into article_generator_finalized so articles are already enriched
(slug, summary) by insight_articles.process_articles.
"""

import hashlib
import os
import re
from pathlib import Path

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

def _load_font(size, *, bold=False):
    if bold:
        candidates = [
            # Linux
            "/usr/share/fonts/truetype/msttcorefonts/Georgiab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
            # macOS
            "/Library/Fonts/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            # Windows
            "C:/Windows/Fonts/georgiab.ttf",
            "C:/Windows/Fonts/Georgia Bold.ttf",
        ]
    else:
        candidates = [
            # Linux
            "/usr/share/fonts/truetype/msttcorefonts/Georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            # macOS
            "/Library/Fonts/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            # Windows
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/Georgia.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    raise RuntimeError(
        f"No usable serif {'bold' if bold else 'regular'} font found. "
        "OG image generation requires Georgia, DejaVu, Liberation, or FreeSerif fonts. "
        "Install one of these or use the devcontainer."
    )


def _preload_fonts():
    return {
        "bold_100": _load_font(100, bold=True),
        "bold_64":  _load_font(64,  bold=True),
        "bold_52":  _load_font(52,  bold=True),
        "reg_36":   _load_font(36),
        "reg_28":   _load_font(28),
        "reg_24":   _load_font(24),
    }


# ── Text helpers ──────────────────────────────────────────────────────────────

def _wrap_text(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = current + " " + word if current else word
        if draw.textlength(candidate, font=font) > max_width:
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

    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["bold_64"])
    y += 72
    draw.text((MARGIN, y), site_description, fill=COLOR_MUTED, font=fonts["reg_28"])
    y += 42
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 30

    title_lines = _wrap_text(draw, article_title, fonts["bold_52"], W - 2 * MARGIN)
    for i, line in enumerate(title_lines):
        draw.text((MARGIN, y + i * 64), line, fill=COLOR_DARK, font=fonts["bold_52"])
    y += len(title_lines) * 64 + 14

    max_excerpt = min(3, max(1, 5 - len(title_lines)))
    excerpt_lines = _wrap_text(draw, excerpt, fonts["reg_28"], W - 2 * MARGIN)[:max_excerpt]
    for i, line in enumerate(excerpt_lines):
        draw.text((MARGIN, y + i * 48), line, fill=COLOR_MUTED, font=fonts["reg_28"])
    if excerpt_lines:
        y += len(excerpt_lines) * 48 + 28

    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 14
    tw = _text_width(draw, domain, fonts["reg_28"])
    draw.text((W - MARGIN - tw, y), domain, fill=COLOR_MUTED, font=fonts["reg_28"])


def _draw_homepage(draw, site_title, site_description, domain, author_name, fonts):
    y = 80

    draw.text((MARGIN, y), site_title, fill=COLOR_DARK, font=fonts["bold_100"])
    y += 118

    desc_lines = _wrap_text(draw, site_description, fonts["reg_36"], W - 2 * MARGIN)
    for i, line in enumerate(desc_lines):
        draw.text((MARGIN, y + i * 46), line, fill=COLOR_MUTED, font=fonts["reg_36"])
    y += len(desc_lines) * 46 + 24

    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=COLOR_LINE, width=1)
    y += 50
    draw.text((MARGIN, y), "Published occasionally. Written for clarity over volume.", fill=COLOR_MUTED, font=fonts["reg_28"])

    footer_y = H - 72
    draw.line([(MARGIN, footer_y), (W - MARGIN, footer_y)], fill=COLOR_LINE, width=1)
    footer_text_y = footer_y + 20
    draw.text((MARGIN, footer_text_y), f"Written and maintained by {author_name}", fill=COLOR_MUTED, font=fonts["reg_24"])
    tw = _text_width(draw, domain, fonts["reg_24"])
    draw.text((W - MARGIN - tw, footer_text_y), domain, fill=COLOR_MUTED, font=fonts["reg_24"])


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _content_hash(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()

def _is_current(path: Path, hash_val: str) -> bool:
    sha_file = path.with_suffix('.sha256')
    return path.exists() and sha_file.exists() and sha_file.read_text().strip() == hash_val

def _save_image(img: Image.Image, path: Path, hash_val: str) -> None:
    img.save(path, 'WEBP', quality=85)
    path.with_suffix('.sha256').write_text(hash_val)


# ── Plugin hook ───────────────────────────────────────────────────────────────

def _generate(generator):
    settings   = generator.settings
    site_title = settings.get('SITENAME', '')
    site_desc  = settings.get('SITESUBTITLE', '')
    site_url   = settings.get('SITEURL', '') or 'https://insight.ale-saglia.com'
    author     = settings.get('AUTHOR', '')
    domain     = re.sub(r'^https?://', '', site_url)

    fonts    = _preload_fonts()
    out_base = Path(generator.output_path) / 'assets' / 'og-images'
    out_base.mkdir(parents=True, exist_ok=True)

    # Homepage
    hp_hash = _content_hash(site_title, site_desc, domain, author)
    hp_out  = out_base / 'homepage.webp'
    if not _is_current(hp_out, hp_hash):
        img = Image.new('RGB', (W, H), COLOR_BG)
        _draw_homepage(ImageDraw.Draw(img), site_title, site_desc, domain, author, fonts)
        _save_image(img, hp_out, hp_hash)
        print('✓ OG: homepage.webp')

    # Articles — slug already set by insight_articles.process_articles
    for article in generator.articles:
        slug = getattr(article, 'slug', '')
        if not slug:
            continue

        summary = re.sub(r'<[^>]+>', '', getattr(article, 'summary', '') or '')

        out_path = out_base / f'{slug}.webp'
        out_path.parent.mkdir(parents=True, exist_ok=True)

        art_hash = _content_hash(article.title or slug, slug, summary)
        if not _is_current(out_path, art_hash):
            img = Image.new('RGB', (W, H), COLOR_BG)
            _draw_article(
                ImageDraw.Draw(img),
                site_title, site_desc,
                article.title or slug,
                summary,
                domain,
                fonts,
            )
            _save_image(img, out_path, art_hash)
            print(f'✓ OG: {slug}.webp')


def register():
    signals.article_generator_finalized.connect(_generate)
