"""Tests for scripts/ensure_frontmatter.py"""
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
import ensure_frontmatter as ef


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    """Reset module-level counters and stub out git before every test."""
    monkeypatch.setattr(ef, '_warn_count', 0)
    monkeypatch.setattr(ef, '_error_count', 0)
    monkeypatch.setattr(ef, '_update_count', 0)
    monkeypatch.setattr(ef, '_first_commit_date', lambda _: date(2024, 1, 1))


@pytest.fixture
def make_article(tmp_path, monkeypatch):
    """
    Factory: create an article file and return its relative Path.
    CWD is set to tmp_path so Path('src/...') resolves correctly.
    """
    monkeypatch.chdir(tmp_path)
    article_dir = tmp_path / 'src' / 'infrastructure'
    article_dir.mkdir(parents=True)

    def _write(content, name='article.md'):
        p = article_dir / name
        p.write_text(content, encoding='utf-8')
        return Path('src') / 'infrastructure' / name

    return _write


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        text = '---\ntitle: Hello\ncreated: 2024-01-01\n---\n\nBody text'
        meta, body = ef._parse_frontmatter(text)
        assert meta['title'] == 'Hello'
        assert 'Body text' in body

    def test_no_frontmatter_returns_empty_dict(self):
        text = 'Just a plain markdown file.'
        meta, body = ef._parse_frontmatter(text)
        assert meta == {}
        assert body == text

    def test_malformed_yaml_returns_none(self):
        text = '---\ntitle: [unclosed\n---\n\nBody'
        meta, _ = ef._parse_frontmatter(text)
        assert meta is None

    def test_no_closing_delimiter(self):
        text = '---\ntitle: Hello\n'
        meta, body = ef._parse_frontmatter(text)
        assert meta == {}
        assert body == text

    def test_empty_frontmatter(self):
        text = '---\n---\n\nBody'
        meta, _ = ef._parse_frontmatter(text)
        assert meta == {}

    def test_yaml_date_parsed_as_python_date(self):
        text = '---\ncreated: 2024-01-15\n---\n'
        meta, _ = ef._parse_frontmatter(text)
        assert meta['created'] == date(2024, 1, 15)

    def test_body_separated_correctly(self):
        text = '---\ntitle: T\n---\n\nFirst line.\n'
        _, body = ef._parse_frontmatter(text)
        assert body == '\nFirst line.\n'


# ---------------------------------------------------------------------------
# _extract_h1
# ---------------------------------------------------------------------------

class TestExtractH1:
    def test_h1_at_start(self):
        assert ef._extract_h1('# My Title\n\nContent') == 'My Title'

    def test_h1_in_middle(self):
        assert ef._extract_h1('Intro\n# Second\nContent') == 'Second'

    def test_h2_not_matched(self):
        assert ef._extract_h1('## Only H2\nContent') is None

    def test_empty_body(self):
        assert ef._extract_h1('') is None

    def test_h1_with_extra_spaces_stripped(self):
        assert ef._extract_h1('#  Padded  ') == 'Padded'


# ---------------------------------------------------------------------------
# _normalize_body
# ---------------------------------------------------------------------------

class TestNormalizeBody:
    def test_strips_leading_blank_lines(self):
        assert ef._normalize_body('\n\nContent') == 'Content'

    def test_strips_trailing_blank_lines(self):
        assert ef._normalize_body('Content\n\n') == 'Content'

    def test_strips_matching_h1_and_following_blank(self):
        body = '# My Title\n\nContent'
        assert ef._normalize_body(body, strip_h1='My Title') == 'Content'

    def test_keeps_non_matching_h1(self):
        body = '# Different Title\n\nContent'
        assert ef._normalize_body(body, strip_h1='My Title') == '# Different Title\n\nContent'

    def test_no_strip_h1_when_not_requested(self):
        body = '# Title\n\nContent'
        assert ef._normalize_body(body) == '# Title\n\nContent'

    def test_preserves_internal_blank_lines(self):
        body = 'Para 1\n\nPara 2'
        assert ef._normalize_body(body) == 'Para 1\n\nPara 2'

    def test_already_clean_body_unchanged(self):
        body = 'Content here.'
        assert ef._normalize_body(body) == body


# ---------------------------------------------------------------------------
# _process — integration tests using real tmp files
# ---------------------------------------------------------------------------

class TestProcess:
    def test_complete_file_is_not_modified(self, make_article):
        content = (
            '---\nlayout: article\ntitle: My Article\ncreated: 2024-01-01\n'
            'keywords: python\nexcerpt: A summary\n---\n\nContent here.\n'
        )
        path = make_article(content)
        ef._process(path)
        assert path.read_text(encoding='utf-8') == content
        assert ef._warn_count == 0
        assert ef._error_count == 0
        assert ef._update_count == 0

    def test_adds_missing_keywords_with_warning(self, make_article):
        content = (
            '---\nlayout: article\ntitle: Test\ncreated: 2024-01-01\n'
            'excerpt: ok\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        meta, _ = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert 'keywords' in meta
        assert ef._warn_count == 1
        assert ef._update_count == 1

    def test_adds_missing_excerpt_with_warning(self, make_article):
        content = (
            '---\nlayout: article\ntitle: Test\ncreated: 2024-01-01\n'
            'keywords: py\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        meta, _ = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert 'excerpt' in meta
        assert ef._warn_count == 1

    def test_derives_title_from_h1_and_strips_h1(self, make_article):
        content = (
            '---\nlayout: article\ncreated: 2024-01-01\nkeywords: py\n'
            'excerpt: ok\n---\n\n# Auto Title\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        meta, body = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert meta['title'] == 'Auto Title'
        assert '# Auto Title' not in body

    def test_title_fallback_to_filename_warns(self, make_article):
        content = (
            '---\nlayout: article\ncreated: 2024-01-01\nkeywords: py\n'
            'excerpt: ok\n---\n\nNo H1 here.\n'
        )
        path = make_article(content, name='my-slug.md')
        ef._process(path)
        meta, _ = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert meta['title'] == 'my-slug'
        assert ef._warn_count >= 1

    def test_derives_created_from_git_no_warning(self, make_article, monkeypatch):
        monkeypatch.setattr(ef, '_first_commit_date', lambda _: date(2023, 6, 15))
        content = (
            '---\nlayout: article\ntitle: Test\nkeywords: py\n'
            'excerpt: ok\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        meta, _ = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert meta['created'] == date(2023, 6, 15)
        assert ef._warn_count == 0

    def test_created_fallback_to_today_warns(self, make_article, monkeypatch):
        monkeypatch.setattr(ef, '_first_commit_date', lambda _: None)
        content = (
            '---\nlayout: article\ntitle: Test\nkeywords: py\n'
            'excerpt: ok\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        assert ef._warn_count >= 1

    def test_no_frontmatter_creates_complete_fm(self, make_article):
        content = '# My Article\n\nBody content.\n'
        path = make_article(content)
        ef._process(path)
        meta, body = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert meta['title'] == 'My Article'
        assert meta['created'] == date(2024, 1, 1)
        assert 'keywords' in meta
        assert 'excerpt' in meta
        assert '# My Article' not in body

    def test_malformed_yaml_emits_error_and_skips_file(self, make_article):
        original = '---\ntitle: [unclosed\n---\n\nBody.\n'
        path = make_article(original)
        ef._process(path)
        assert path.read_text(encoding='utf-8') == original
        assert ef._error_count == 1
        assert ef._update_count == 0

    def test_strips_duplicate_h1_matching_title(self, make_article):
        content = (
            '---\nlayout: article\ntitle: My Article\ncreated: 2024-01-01\n'
            'keywords: py\nexcerpt: ok\n---\n\n# My Article\n\nReal content.\n'
        )
        path = make_article(content)
        ef._process(path)
        _, body = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert '# My Article' not in body
        assert 'Real content.' in body

    def test_keeps_non_duplicate_h1(self, make_article):
        content = (
            '---\nlayout: article\ntitle: My Article\ncreated: 2024-01-01\n'
            'keywords: py\nexcerpt: ok\n---\n\n# Different Heading\n\nContent.\n'
        )
        path = make_article(content)
        ef._process(path)
        _, body = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert '# Different Heading' in body

    def test_preserves_trailing_newline(self, make_article):
        content = (
            '---\ntitle: T\ncreated: 2024-01-01\nkeywords: py\n'
            'excerpt: ok\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        assert path.read_text(encoding='utf-8').endswith('\n')

    def test_preserves_no_trailing_newline(self, make_article):
        content = (
            '---\ntitle: T\ncreated: 2024-01-01\nkeywords: py\n'
            'excerpt: ok\n---\n\nBody.'
        )
        path = make_article(content)
        ef._process(path)
        assert not path.read_text(encoding='utf-8').endswith('\n')

    def test_category_mismatch_warns_without_modifying_file(self, make_article):
        content = (
            '---\nlayout: article\ntitle: T\ncreated: 2024-01-01\n'
            'keywords: py\nexcerpt: ok\ncategory: wrong\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        assert ef._warn_count >= 1
        assert ef._update_count == 0

    def test_idempotent_after_normalization(self, make_article):
        """A second run on an already-normalized file produces no changes."""
        content = (
            '---\nlayout: article\ntitle: Test\ncreated: 2024-01-01\n'
            'keywords: python\nexcerpt: A summary\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        after_first = path.read_text(encoding='utf-8')
        ef._process(path)
        assert path.read_text(encoding='utf-8') == after_first

    def test_never_overwrites_existing_fields(self, make_article):
        content = (
            '---\nlayout: article\ntitle: Original\ncreated: 2020-05-10\n'
            'keywords: existing\nexcerpt: existing summary\n---\n\nBody.\n'
        )
        path = make_article(content)
        ef._process(path)
        meta, _ = ef._parse_frontmatter(path.read_text(encoding='utf-8'))
        assert meta['title'] == 'Original'
        assert meta['created'] == date(2020, 5, 10)
        assert meta['keywords'] == 'existing'
        assert meta['excerpt'] == 'existing summary'
