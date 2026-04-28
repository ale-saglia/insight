"""
Category page generation — reads README.md files from src/ and generates
category index pages.
"""

import os
from pathlib import Path

import yaml
from markdown import Markdown
from pelican.generators import Generator


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
        self.context['category_by_path'] = by_path
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
