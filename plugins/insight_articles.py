"""
Article enrichment — custom slugs, breadcrumbs, reading time, git dates,
and series navigation (prev_episode / next_episode).
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path


def _git_last_modified(path):
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d', '--', path],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return datetime.strptime(result.stdout.strip(), '%Y-%m-%d').date()
    except Exception:
        pass
    return None


def _episode_number(source_path):
    """Return the integer episode number if the filename begins with digits, else None."""
    stem = Path(source_path).stem  # e.g. '0-why-homelab-matters'
    m = re.match(r'^(\d+)-', stem)
    return int(m.group(1)) if m else None


def process_articles(generator):
    """Set custom slugs, breadcrumbs, reading time, git dates, and series nav."""

    for article in generator.articles:
        _enrich_article(article)

    # Series navigation: group numbered articles by parent directory
    series_groups = {}
    for article in generator.articles:
        rel = article.get_relative_source_path()
        ep = _episode_number(rel)
        if ep is not None:
            parent = str(Path(rel).parent)
            series_groups.setdefault(parent, []).append(article)

    for articles in series_groups.values():
        sorted_series = sorted(articles, key=lambda a: _episode_number(a.get_relative_source_path()) or 0)
        for i, article in enumerate(sorted_series):
            article.prev_episode = None
            article.next_episode = None
            if i > 0:
                prev = sorted_series[i - 1]
                article.prev_episode = {'url': prev.slug + '/', 'title': prev.title}
            if i < len(sorted_series) - 1:
                nxt = sorted_series[i + 1]
                article.next_episode = {'url': nxt.slug + '/', 'title': nxt.title}

    tag_counts = {}
    for article in generator.articles:
        for tag in getattr(article, 'tags', None) or []:
            tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
    generator.context['tag_counts'] = tag_counts


def _enrich_article(article):
    """Compute and attach all custom attributes to a single article."""

    # Use get_relative_source_path() to get a path relative to PATH,
    # e.g. 'src/infrastructure/zero-to-homelab/0-why.md'
    # (article.source_path is the absolute filesystem path)
    source_rel = article.get_relative_source_path()
    parts = Path(source_rel).parts  # ('src', 'infrastructure', 'zero-to-homelab', '0-why.md')

    if len(parts) < 3 or parts[0] != 'src':
        return

    # Strip leading underscore from path segments (handles _general → general)
    path_parts = [p.lstrip('_') for p in parts[1:-1]]

    # Determine article_id / slug stem
    article_id = getattr(article, 'article_id', None)
    if not article_id:
        stem = Path(parts[-1]).stem        # e.g. '0-why-homelab-matters'
        article_id = re.sub(r'^\d+-', '', stem)  # strip leading 'N-'

    # Full slug used for ARTICLE_URL = '{slug}/'
    article.slug = '/'.join(path_parts + [article_id])

    # Helpers for templates
    article.category_path = '/'.join(path_parts)          # e.g. 'infrastructure/zero-to-homelab'
    article.category_top = path_parts[0] if path_parts else ''

    # Breadcrumbs: [{url: 'infrastructure/', label: 'Infrastructure'}, ...]
    crumb_url = ''
    breadcrumbs = []
    for part in path_parts:
        crumb_url = (crumb_url + '/' + part).lstrip('/') if crumb_url else part
        breadcrumbs.append({'url': crumb_url + '/', 'label': part.replace('-', ' ').title()})
    article.breadcrumbs = breadcrumbs

    # Episode number (None for non-series articles)
    article.episode_num = _episode_number(source_rel)

    # Placeholders set by series loop later
    if not hasattr(article, 'prev_episode'):
        article.prev_episode = None
    if not hasattr(article, 'next_episode'):
        article.next_episode = None

    # Reading time (200 wpm on stripped HTML)
    text = re.sub(r'<[^>]+>', ' ', article.content)
    words = len(text.split())
    article.reading_time = max(1, words // 200)

    # Git modified date (only when not already set from frontmatter)
    if not getattr(article, 'modified', None):
        git_date = _git_last_modified(source_rel)
        if git_date:
            article.modified = datetime(git_date.year, git_date.month, git_date.day)
