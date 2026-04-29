"""Tests for plugins/insight_categories.py"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from plugins.insight_categories import CategoryPage, CategoryPageGenerator


def _write_readme(directory: Path, title='', summary='', body=''):
    directory.mkdir(parents=True, exist_ok=True)
    content = f'---\ntitle: {title}\nsummary: {summary}\n---\n\n{body}'
    (directory / 'README.md').write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# CategoryPage
# ---------------------------------------------------------------------------
# CategoryPage receives a relative path like 'src/infrastructure/README.md'
# and opens it relative to CWD. Tests use monkeypatch.chdir(tmp_path).

class TestCategoryPage:
    def test_title_and_summary_parsed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infrastructure', summary='Homelab stuff')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.title == 'Infrastructure'
        assert page.summary == 'Homelab stuff'

    def test_markdown_body_rendered_to_html(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T', body='Some **bold** text.')
        page = CategoryPage('src/infrastructure/README.md')
        assert '<strong>bold</strong>' in page.content

    def test_empty_body_leaves_content_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.content == ''

    def test_category_path_top_level(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.category_path == 'infrastructure'

    def test_category_path_nested(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='T')
        page = CategoryPage('src/infrastructure/zero-to-homelab/README.md')
        assert page.category_path == 'infrastructure/zero-to-homelab'

    def test_underscore_prefix_stripped_from_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / '_general', title='T')
        page = CategoryPage('src/_general/README.md')
        assert page.category_path == 'general'

    def test_url_and_save_as(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.url == 'infrastructure/'
        assert page.save_as == 'infrastructure/index.html'

    def test_slug_equals_category_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.slug == page.category_path

    def test_depth_one_for_top_level(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.depth == 1
        assert page.top_level is True

    def test_depth_two_for_nested(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='T')
        page = CategoryPage('src/infrastructure/zero-to-homelab/README.md')
        assert page.depth == 2
        assert page.top_level is False

    def test_parent_path_none_for_top_level(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.parent_path is None

    def test_parent_path_set_for_nested(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='T')
        page = CategoryPage('src/infrastructure/zero-to-homelab/README.md')
        assert page.parent_path == 'infrastructure'

    def test_child_categories_empty_on_init(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='T')
        page = CategoryPage('src/infrastructure/README.md')
        assert page.child_categories == []


# ---------------------------------------------------------------------------
# CategoryPageGenerator.generate_context
# ---------------------------------------------------------------------------
# Bypass Generator.__init__ via __new__ and set only the attributes that
# generate_context reads: self.path and self.context.

class TestCategoryPageGeneratorContext:
    def _make_generator(self, project_path):
        gen = CategoryPageGenerator.__new__(CategoryPageGenerator)
        gen.path = str(project_path)
        gen.context = {}
        return gen

    def test_finds_readme_and_creates_page(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infrastructure')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        assert len(gen.category_pages) == 1
        assert gen.category_pages[0].category_path == 'infrastructure'

    def test_skips_dirs_without_readme(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        (tmp_path / 'src' / 'other').mkdir(parents=True)  # no README.md
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        assert len(gen.category_pages) == 1

    def test_sorted_by_depth_then_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='Series')
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        _write_readme(tmp_path / 'src' / 'digital-governance', title='Gov')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        paths = [p.category_path for p in gen.category_pages]
        assert paths == ['digital-governance', 'infrastructure', 'infrastructure/zero-to-homelab']

    def test_parent_title_resolved_from_known_parent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infrastructure')
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='Series')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        nested = next(p for p in gen.category_pages if p.depth == 2)
        assert nested.parent_title == 'Infrastructure'

    def test_parent_title_fallback_when_parent_has_no_readme(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Create nested without a parent README
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='Series')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        nested = gen.category_pages[0]
        assert nested.parent_title == 'Infrastructure'  # formatted from path segment

    def test_child_categories_populated(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='Series')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        parent = next(p for p in gen.category_pages if p.depth == 1)
        assert len(parent.child_categories) == 1
        assert parent.child_categories[0].category_path == 'infrastructure/zero-to-homelab'

    def test_context_keys_populated(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        assert 'category_pages' in gen.context
        assert 'category_by_path' in gen.context
        assert 'top_level_categories' in gen.context

    def test_top_level_categories_filter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        _write_readme(tmp_path / 'src' / 'infrastructure' / 'zero-to-homelab', title='Series')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        top = gen.context['top_level_categories']
        assert len(top) == 1
        assert top[0].category_path == 'infrastructure'

    def test_category_by_path_index(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_readme(tmp_path / 'src' / 'infrastructure', title='Infra')
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        assert 'infrastructure' in gen.context['category_by_path']

    def test_empty_src_dir_produces_no_pages(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'src').mkdir()
        gen = self._make_generator(tmp_path)
        gen.generate_context()
        assert gen.category_pages == []
