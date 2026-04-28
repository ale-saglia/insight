"""
Pelican plugin for Insight Notes — entry point.

Wires up signals to logic modules:
  insight_reader     → InsightMarkdownReader  (YAML frontmatter + Jekyll field mapping)
  insight_articles   → process_articles       (slugs, breadcrumbs, reading time, series nav)
  insight_categories → CategoryPageGenerator  (README.md → category index pages)
"""

import os
import sys

# Ensure the plugins directory is importable regardless of Pelican's sys.path order
sys.path.insert(0, os.path.dirname(__file__))

from pelican import signals

from insight_articles import process_articles
from insight_categories import CategoryPageGenerator
from insight_reader import InsightMarkdownReader


def _add_reader(readers):
    readers.reader_classes['md'] = InsightMarkdownReader
    readers.reader_classes['markdown'] = InsightMarkdownReader


def _get_generators(generators):
    return CategoryPageGenerator


def register():
    signals.readers_init.connect(_add_reader)
    signals.article_generator_finalized.connect(process_articles)
    signals.get_generators.connect(_get_generators)
