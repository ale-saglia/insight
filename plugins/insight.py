"""
Pelican plugin for Insight Notes.

Handles:
- YAML frontmatter parsing and Jekyll field-name mapping
  (created→date, keywords→tags, excerpt→summary, article_id preserved)
- Custom URL generation derived from file path + article_id
- Git-based `modified` date population
- Series navigation (prev_episode / next_episode)
- Category page generation from README.md files in src/
- Breadcrumb data on articles
"""

import os
import re
import subprocess
from copy import copy
from datetime import date, datetime
from pathlib import Path

import yaml
from markdown import Markdown
from pelican import signals
from pelican.generators import Generator
from pelican.readers import MarkdownReader


# ── Custom Markdown reader ────────────────────────────────────────────────────

class InsightMarkdownReader(MarkdownReader):
    """Reads Markdown files with YAML frontmatter, mapping Jekyll field names."""

    enabled = MarkdownReader.enabled

    def read(self, source_path):
        with open(source_path, encoding='utf-8') as f:
            raw = f.read()

        fm_meta = {}
        body = raw

        if raw.startswith('---\n') or raw.startswith('---\r\n'):
            end = raw.find('\n---\n', 4)
            if end == -1:
                end = raw.find('\n---\r\n', 4)
            if end != -1:
                try:
                    fm_meta = yaml.safe_load(raw[4:end]) or {}
                except yaml.YAMLError:
                    fm_meta = {}
                # Skip past closing delimiter
                skip = 5 if raw[end + 4:end + 5] == '\n' else 6
                body = raw[end + skip:].lstrip('\n')

        # Map Jekyll / custom fields to Pelican field names
        meta_strings = {}

        if 'title' in fm_meta:
            meta_strings['title'] = str(fm_meta['title'])

        # created → date
        if 'created' in fm_meta:
            d = fm_meta['created']
            if isinstance(d, datetime):
                meta_strings['date'] = d.strftime('%Y-%m-%dT%H:%M:%S')
            elif isinstance(d, date):
                meta_strings['date'] = d.strftime('%Y-%m-%d')
            else:
                meta_strings['date'] = str(d)

        # modified → modified
        if 'modified' in fm_meta:
            d = fm_meta['modified']
            if isinstance(d, datetime):
                meta_strings['modified'] = d.strftime('%Y-%m-%dT%H:%M:%S')
            elif isinstance(d, date):
                meta_strings['modified'] = d.strftime('%Y-%m-%d')
            else:
                meta_strings['modified'] = str(d)

        # excerpt → summary (also handle native 'summary' key in README pages)
        if 'excerpt' in fm_meta and fm_meta['excerpt']:
            meta_strings['summary'] = str(fm_meta['excerpt'])
        elif 'summary' in fm_meta and fm_meta['summary']:
            meta_strings['summary'] = str(fm_meta['summary'])

        # keywords → tags
        if 'keywords' in fm_meta and fm_meta['keywords']:
            kw = fm_meta['keywords']
            meta_strings['tags'] = kw if isinstance(kw, str) else ', '.join(str(k) for k in kw)

        # article_id preserved for slug computation in process_articles
        if 'article_id' in fm_meta:
            meta_strings['article_id'] = str(fm_meta['article_id'])

        # layout ignored (template selection is done by Pelican)

        # Convert to Pelican-typed metadata
        processed = {}
        for key, value in meta_strings.items():
            processed[key] = self.process_metadata(key, value)

        # Render body through Markdown
        md_config = copy(self.settings.get('MARKDOWN', {}))
        md = Markdown(**md_config)
        content_html = md.convert(body)

        return content_html, processed


# ── Git helpers ───────────────────────────────────────────────────────────────

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


# ── Article post-processor ────────────────────────────────────────────────────

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


# ── Category page ─────────────────────────────────────────────────────────────

class CategoryPage:
    """Represents a category index page derived from a README.md file."""

    def __init__(self, source_path):
        self.source_path = source_path
        self.title = ''
        self.summary = ''
        self.content = ''
        self.category_path = ''   # e.g. 'infrastructure/zero-to-homelab'
        self.slug = ''
        self.url = ''
        self.save_as = ''
        self.depth = 0
        self.top_level = False
        self.parent_path = None
        self.parent_title = None
        self.child_categories = []
        self.direct_articles = []
        self._parse()

    def _parse(self):
        with open(self.source_path, encoding='utf-8') as f:
            raw = f.read()

        fm_meta = {}
        body = raw
        if raw.startswith('---\n') or raw.startswith('---\r\n'):
            end = raw.find('\n---\n', 4)
            if end == -1:
                end = raw.find('\n---\r\n', 4)
            if end != -1:
                try:
                    fm_meta = yaml.safe_load(raw[4:end]) or {}
                except yaml.YAMLError:
                    fm_meta = {}
                body = raw[end + 5:].lstrip('\n')

        self.title = str(fm_meta.get('title', ''))
        self.summary = str(fm_meta.get('summary', ''))

        if body.strip():
            md = Markdown()
            self.content = md.convert(body)

        # Derive URL from file path: src/infrastructure/zero-to-homelab/README.md
        parts = Path(self.source_path).parts
        path_parts = [p.lstrip('_') for p in parts[1:-1]]  # strip 'src' and 'README.md'

        self.category_path = '/'.join(path_parts)
        self.slug = self.category_path
        self.url = self.category_path + '/'
        self.save_as = self.category_path + '/index.html'
        self.depth = len(path_parts)
        self.top_level = (self.depth == 1)

        if self.depth > 1:
            self.parent_path = '/'.join(path_parts[:-1])


# ── Category page generator ───────────────────────────────────────────────────

class CategoryPageGenerator(Generator):
    """Generates category index pages from README.md files in src/."""

    def generate_context(self):
        src_path = os.path.join(self.path, 'src')
        category_pages = []

        for root, dirs, files in os.walk(src_path):
            dirs.sort()
            if 'README.md' in files:
                readme_path = os.path.join(root, 'README.md')
                rel_path = os.path.relpath(readme_path, self.path)
                page = CategoryPage(rel_path)
                if page.category_path:
                    category_pages.append(page)

        category_pages.sort(key=lambda p: (p.depth, p.category_path))

        # Resolve parent titles and populate child_categories
        by_path = {p.category_path: p for p in category_pages}
        for page in category_pages:
            if page.parent_path and page.parent_path in by_path:
                page.parent_title = by_path[page.parent_path].title
            elif page.parent_path:
                page.parent_title = page.parent_path.split('/')[-1].replace('-', ' ').title()

            # Direct children (one level deeper)
            page.child_categories = [
                p for p in category_pages
                if p.parent_path == page.category_path
            ]

        self.category_pages = category_pages
        self.context['category_pages'] = category_pages
        self.context['top_level_categories'] = [p for p in category_pages if p.top_level]

    def generate_output(self, writer):
        articles = self.context.get('articles', [])

        # Index articles by category_path
        arts_by_path = {}
        for article in articles:
            cp = getattr(article, 'category_path', '')
            arts_by_path.setdefault(cp, []).append(article)

        template = self.get_template('category')

        for page in self.category_pages:
            direct = arts_by_path.get(page.category_path, [])
            # Sort: episodes by number, others by date descending
            if any(getattr(a, 'episode_num', None) is not None for a in direct):
                direct = sorted(direct, key=lambda a: getattr(a, 'episode_num', 0) or 0)
            else:
                direct = sorted(direct, key=lambda a: a.date, reverse=True)

            # Populate child category article lists
            for child in page.child_categories:
                child_arts = arts_by_path.get(child.category_path, [])
                if any(getattr(a, 'episode_num', None) is not None for a in child_arts):
                    child.direct_articles = sorted(
                        child_arts, key=lambda a: getattr(a, 'episode_num', 0) or 0
                    )
                else:
                    child.direct_articles = sorted(
                        child_arts, key=lambda a: a.date, reverse=True
                    )

            ctx = self.context.copy()
            ctx['page'] = page
            ctx['direct_articles'] = direct
            ctx['child_categories'] = page.child_categories

            writer.write_file(
                page.save_as,
                template,
                ctx,
                page=page,
                relative_urls=self.settings.get('RELATIVE_URLS'),
            )


# ── Plugin registration ───────────────────────────────────────────────────────

def _add_reader(readers):
    readers.reader_classes['md'] = InsightMarkdownReader
    readers.reader_classes['markdown'] = InsightMarkdownReader


def _get_generators(generators):
    return CategoryPageGenerator


def register():
    signals.readers_init.connect(_add_reader)
    signals.article_generator_finalized.connect(process_articles)
    signals.get_generators.connect(_get_generators)
