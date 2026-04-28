"""
InsightMarkdownReader — reads Markdown files with YAML frontmatter,
mapping Jekyll field names to Pelican equivalents.
"""

import logging
import os
from copy import copy
from datetime import date, datetime

from markdown import Markdown
from pelican.readers import MarkdownReader

from ._frontmatter import parse_frontmatter

logger = logging.getLogger(__name__)


def _build_warn(source_path, msg):
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print(f'::warning file={source_path}::{msg}', flush=True)
    else:
        logger.warning('%s: %s', source_path, msg)


def _build_error(source_path, msg):
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print(f'::error file={source_path}::{msg}', flush=True)
    else:
        logger.error('%s: %s', source_path, msg)


class InsightMarkdownReader(MarkdownReader):
    """Reads Markdown files with YAML frontmatter, mapping Jekyll field names."""

    enabled = MarkdownReader.enabled

    def read(self, source_path):
        with open(source_path, encoding='utf-8') as f:
            raw = f.read()

        fm_meta, body = parse_frontmatter(
            raw,
            on_error=lambda _: _build_error(source_path, 'YAML frontmatter is malformed — article will have no metadata'),
        )

        # Validate required frontmatter fields
        if not fm_meta.get('created'):
            _build_error(source_path, 'missing frontmatter "created" — article will have no date and may break category sort')
        if not fm_meta.get('keywords'):
            _build_warn(source_path, 'missing frontmatter "keywords" — article will have no tags')
        if not fm_meta.get('excerpt'):
            _build_warn(source_path, 'missing frontmatter "excerpt" — article will have no summary')

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
