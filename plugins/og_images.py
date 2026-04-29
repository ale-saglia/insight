"""
OG image generation — produces WebP images in assets/og-images/ for every
article and the site homepage, triggered during the Pelican build.

Hooks into article_generator_finalized so articles are already enriched
(slug, summary) by insight_articles.process_articles.

Design notes:
    - 1200x630 px, the universal OG standard.
    - 80 px safe margin on all sides (= GitHub's recommended 40 pt).
    - Site title / subtitle proportions mirror the website (~1.8:1).
    - Article OG: anchor-top layout — the article title always sits in
      the same vertical position, so different OGs feel cohesive.
"""

import hashlib
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pelican import signals
from PIL import Image, ImageDraw, ImageFont


# ── Palette & dimensions ──────────────────────────────────────────────────────

COLOR_BG    = (255, 255, 255)
COLOR_DARK  = (27, 31, 35)     # #1b1f23
COLOR_MUTED = (91, 99, 106)    # #5b636a
COLOR_LINE  = (230, 232, 235)  # #e6e8eb

W, H = 1200, 630

# GitHub recommends 40 pt safe margin around social cards. In standard
# web pt-to-px conversion (2x design density) this is ~80 px. Verified
# against GitHub's official repo card template.
SAFE = 80
CONTENT_W = W - 2 * SAFE


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
        # Homepage: site is the protagonist.
        "hp_title":    _load_font(100, bold=True),
        "hp_subtitle": _load_font(36),

        # Article: site identity is small (the publisher), article title dominates.
        "art_site_title":    _load_font(36, bold=True),
        "art_site_subtitle": _load_font(20),
        "art_title":         _load_font(54, bold=True),
        "art_excerpt":       _load_font(26),

        # Footer (shared).
        "footer": _load_font(20),
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


def _line_height(font):
    """Line height tuned for serif body text — a touch generous for readability."""
    bbox = font.getbbox("Aj")
    return int((bbox[3] - bbox[1]) * 1.25)


# ── Drawing ───────────────────────────────────────────────────────────────────

def _draw_homepage(draw, site_title, site_subtitle, domain, author, fonts):
    """
    Layout:
        - Site title + subtitle, vertically centered (slightly above center
          for visual balance).
        - Footer: thin separator + author (left) + domain (right).
    """
    # Compose the central block first to compute its height
    title_lines = _wrap_text(draw, site_title, fonts["hp_title"], CONTENT_W)
    subtitle_lines = _wrap_text(draw, site_subtitle, fonts["hp_subtitle"], CONTENT_W)

    title_lh = _line_height(fonts["hp_title"])
    subtitle_lh = _line_height(fonts["hp_subtitle"])
    gap = 24

    block_h = (
        len(title_lines) * title_lh
        + gap
        + len(subtitle_lines) * subtitle_lh
    )

    # Center vertically, slightly above the geometric middle
    block_y = (H - block_h) // 2 - 30

    # Title
    y = block_y
    for line in title_lines:
        draw.text((SAFE, y), line, fill=COLOR_DARK, font=fonts["hp_title"])
        y += title_lh

    y += gap

    # Subtitle
    for line in subtitle_lines:
        draw.text((SAFE, y), line, fill=COLOR_MUTED, font=fonts["hp_subtitle"])
        y += subtitle_lh

    # Footer band
    footer_line_y = H - SAFE - 50
    draw.line(
        [(SAFE, footer_line_y), (W - SAFE, footer_line_y)],
        fill=COLOR_LINE, width=1,
    )
    footer_text_y = footer_line_y + 16
    draw.text(
        (SAFE, footer_text_y),
        f"by {author}",
        fill=COLOR_MUTED, font=fonts["footer"],
    )
    domain_w = _text_width(draw, domain, fonts["footer"])
    draw.text(
        (W - SAFE - domain_w, footer_text_y),
        domain, fill=COLOR_MUTED, font=fonts["footer"],
    )


def _draw_article(draw, site_title, site_subtitle, article_title, excerpt, domain, fonts):
    """
    Anchor-top layout:
        - Header: site identity (title + subtitle, ratio 1.8:1 like the website).
        - Separator.
        - Article title (always at the same Y) and excerpt (truncated with
          ellipsis if it would collide with the footer).
        - Footer: separator + domain right-aligned.
    """
    # ── Header (site identity) ──
    y = SAFE
    draw.text((SAFE, y), site_title, fill=COLOR_DARK, font=fonts["art_site_title"])
    y += _line_height(fonts["art_site_title"])

    sub_lines = _wrap_text(draw, site_subtitle, fonts["art_site_subtitle"], CONTENT_W)
    sub_lh = _line_height(fonts["art_site_subtitle"])
    for line in sub_lines:
        draw.text((SAFE, y), line, fill=COLOR_MUTED, font=fonts["art_site_subtitle"])
        y += sub_lh

    # Separator under header
    y += 18
    draw.line([(SAFE, y), (W - SAFE, y)], fill=COLOR_LINE, width=1)
    y += 32

    # ── Article title (cap at 3 lines to leave room for excerpt) ──
    title_lh = _line_height(fonts["art_title"])
    title_lines = _wrap_text(draw, article_title, fonts["art_title"], CONTENT_W)[:3]
    for line in title_lines:
        draw.text((SAFE, y), line, fill=COLOR_DARK, font=fonts["art_title"])
        y += title_lh

    y += 16  # space between title and excerpt

    # ── Footer band reservation (compute now so we know how much room excerpt has) ──
    footer_line_y = H - SAFE - 36
    footer_band_top = footer_line_y - 16  # leave breathing room above the line

    # ── Excerpt (truncate with ellipsis if it would overflow into the footer) ──
    if excerpt:
        excerpt_lh = _line_height(fonts["art_excerpt"])
        max_lines = max(1, (footer_band_top - y) // excerpt_lh)

        all_lines = _wrap_text(draw, excerpt, fonts["art_excerpt"], CONTENT_W)
        excerpt_lines = all_lines[:max_lines]

        if len(all_lines) > len(excerpt_lines) and excerpt_lines:
            # Truncate the last line and append an ellipsis that fits the width
            last = excerpt_lines[-1].rstrip(".,;:")
            while last and _text_width(draw, last + "…", fonts["art_excerpt"]) > CONTENT_W:
                last = last[:-1]
            excerpt_lines[-1] = last + "…"

        for line in excerpt_lines:
            draw.text((SAFE, y), line, fill=COLOR_MUTED, font=fonts["art_excerpt"])
            y += excerpt_lh

    # ── Footer: separator + domain right-aligned ──
    draw.line(
        [(SAFE, footer_line_y), (W - SAFE, footer_line_y)],
        fill=COLOR_LINE, width=1,
    )
    footer_text_y = footer_line_y + 14
    domain_w = _text_width(draw, domain, fonts["footer"])
    draw.text(
        (W - SAFE - domain_w, footer_text_y),
        domain, fill=COLOR_MUTED, font=fonts["footer"],
    )


# ── Renderer fingerprint — invalidates cache when this file changes ───────────

_RENDERER_HASH = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


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
    hp_hash = _content_hash(_RENDERER_HASH, site_title, site_desc, domain, author)
    hp_out  = out_base / 'homepage.webp'
    if not _is_current(hp_out, hp_hash):
        img = Image.new('RGB', (W, H), COLOR_BG)
        _draw_homepage(ImageDraw.Draw(img), site_title, site_desc, domain, author, fonts)
        _save_image(img, hp_out, hp_hash)
        print('✓ OG: homepage.webp')

    # Articles — slug already set by insight_articles.process_articles
    def _render(task):
        title, slug, summary, out_path, art_hash = task
        img = Image.new('RGB', (W, H), COLOR_BG)
        _draw_article(ImageDraw.Draw(img), site_title, site_desc, title, summary, domain, fonts)
        _save_image(img, out_path, art_hash)
        return slug

    tasks = []
    for article in generator.articles:
        slug = getattr(article, 'slug', '')
        if not slug:
            continue
        summary = re.sub(r'<[^>]+>', '', getattr(article, 'summary', '') or '')
        out_path = out_base / f'{slug}.webp'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        art_hash = _content_hash(_RENDERER_HASH, article.title or slug, slug, summary)
        if not _is_current(out_path, art_hash):
            tasks.append((article.title or slug, slug, summary, out_path, art_hash))

    if tasks:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
            for slug in pool.map(_render, tasks):
                print(f'✓ OG: {slug}.webp')


def register():
    signals.article_generator_finalized.connect(_generate)