"""Tests for plugins/og_images.py — cache helpers and _generate integration."""

import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
import plugins.og_images as og_mod
from plugins.og_images import _content_hash, _generate, _is_current, _RENDERER_HASH, _save_image


def _fonts_available() -> bool:
    try:
        og_mod._preload_fonts()
        return True
    except RuntimeError:
        return False


_skip_no_fonts = pytest.mark.skipif(
    not _fonts_available(),
    reason="No serif fonts available (Georgia / DejaVu / Liberation / FreeSerif)",
)


# ---------------------------------------------------------------------------
# _content_hash
# ---------------------------------------------------------------------------

class TestContentHash:
    def test_returns_hex_string(self):
        h = _content_hash('a', 'b')
        assert isinstance(h, str)
        assert all(c in '0123456789abcdef' for c in h)

    def test_deterministic(self):
        assert _content_hash('title', 'slug', 'summary') == _content_hash('title', 'slug', 'summary')

    def test_different_inputs_produce_different_hashes(self):
        assert _content_hash('a') != _content_hash('b')

    def test_order_matters(self):
        assert _content_hash('a', 'b') != _content_hash('b', 'a')

    def test_empty_string_part_is_valid(self):
        h = _content_hash('')
        assert len(h) == 64  # SHA-256 hex digest


# ---------------------------------------------------------------------------
# _is_current
# ---------------------------------------------------------------------------

class TestIsCurrent:
    def test_false_when_webp_missing(self, tmp_path):
        out = tmp_path / 'img.webp'
        assert _is_current(out, 'abc') is False

    def test_false_when_sha_file_missing(self, tmp_path):
        out = tmp_path / 'img.webp'
        out.write_bytes(b'fake')
        assert _is_current(out, 'abc') is False

    def test_false_when_hash_differs(self, tmp_path):
        out = tmp_path / 'img.webp'
        out.write_bytes(b'fake')
        out.with_suffix('.sha256').write_text('old-hash')
        assert _is_current(out, 'new-hash') is False

    def test_true_when_hash_matches(self, tmp_path):
        out = tmp_path / 'img.webp'
        out.write_bytes(b'fake')
        out.with_suffix('.sha256').write_text('abc123')
        assert _is_current(out, 'abc123') is True

    def test_true_ignores_whitespace_in_sha_file(self, tmp_path):
        out = tmp_path / 'img.webp'
        out.write_bytes(b'fake')
        out.with_suffix('.sha256').write_text('  abc123\n')
        assert _is_current(out, 'abc123') is True


# ---------------------------------------------------------------------------
# _save_image
# ---------------------------------------------------------------------------

class TestSaveImage:
    def _blank_image(self):
        return Image.new('RGB', (10, 10), (255, 255, 255))

    def test_creates_webp_file(self, tmp_path):
        out = tmp_path / 'img.webp'
        _save_image(self._blank_image(), out, 'hash123')
        assert out.exists()

    def test_creates_sha256_sidecar(self, tmp_path):
        out = tmp_path / 'img.webp'
        _save_image(self._blank_image(), out, 'hash123')
        assert out.with_suffix('.sha256').read_text() == 'hash123'

    def test_saved_image_is_current_on_next_check(self, tmp_path):
        out = tmp_path / 'img.webp'
        h = _content_hash('title', 'slug')
        _save_image(self._blank_image(), out, h)
        assert _is_current(out, h) is True

    def test_overwrite_updates_sha256(self, tmp_path):
        out = tmp_path / 'img.webp'
        _save_image(self._blank_image(), out, 'first')
        _save_image(self._blank_image(), out, 'second')
        assert out.with_suffix('.sha256').read_text() == 'second'


# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

class _FakeArticle:
    def __init__(self, slug, title, summary=''):
        self.slug = slug
        self.title = title
        self.summary = summary


class _FakeGenerator:
    def __init__(self, output_path, articles=None):
        self.output_path = str(output_path)
        self.articles = articles or []
        self.settings = {
            'SITENAME': 'Test Site',
            'SITESUBTITLE': 'Test subtitle',
            'SITEURL': 'https://example.com',
            'AUTHOR': 'Test Author',
        }


# ---------------------------------------------------------------------------
# _generate — functional tests (writes real WebP files via PIL)
# ---------------------------------------------------------------------------

@_skip_no_fonts
class TestGenerate:
    def test_creates_homepage_image_and_sidecar(self, tmp_path):
        _generate(_FakeGenerator(tmp_path))

        out_base = tmp_path / 'assets' / 'og-images'
        assert (out_base / 'homepage.webp').exists()
        assert (out_base / 'homepage.sha256').exists()

    def test_creates_article_image_and_sidecar(self, tmp_path):
        article = _FakeArticle('cat/my-article', 'My Article', 'A brief summary.')
        _generate(_FakeGenerator(tmp_path, [article]))

        out_base = tmp_path / 'assets' / 'og-images'
        assert (out_base / 'cat' / 'my-article.webp').exists()
        assert (out_base / 'cat' / 'my-article.sha256').exists()

    def test_skips_article_without_slug(self, tmp_path):
        article = _FakeArticle('', 'No Slug Article')
        _generate(_FakeGenerator(tmp_path, [article]))

        out_base = tmp_path / 'assets' / 'og-images'
        webp_files = list(out_base.rglob('*.webp'))
        assert webp_files == [out_base / 'homepage.webp']


# ---------------------------------------------------------------------------
# Caching mechanics — verifies skip-if-current and invalidation paths
# ---------------------------------------------------------------------------

@_skip_no_fonts
class TestCachingMechanics:
    """Uses monkeypatching on _save_image to track regenerations reliably
    without depending on filesystem mtime precision."""

    def _run(self, tmp_path, articles=None):
        _generate(_FakeGenerator(tmp_path, articles))

    def _track_saves(self, monkeypatch):
        """Return a list that accumulates Path objects passed to _save_image."""
        calls = []
        original = og_mod._save_image

        def _spy(img, path, h):
            calls.append(path)
            original(img, path, h)

        monkeypatch.setattr(og_mod, '_save_image', _spy)
        return calls

    # ── stored hash encodes the renderer version ──────────────────────────────

    def test_generated_sidecar_encodes_renderer_hash(self, tmp_path):
        article = _FakeArticle('cat/article', 'My Title', 'My Summary')
        self._run(tmp_path, [article])

        sha_path = tmp_path / 'assets' / 'og-images' / 'cat' / 'article.sha256'
        expected = _content_hash(_RENDERER_HASH, 'My Title', 'cat/article', 'My Summary')
        assert sha_path.read_text().strip() == expected

    # ── cache hit ─────────────────────────────────────────────────────────────

    def test_second_call_skips_up_to_date_files(self, tmp_path, monkeypatch):
        article = _FakeArticle('cat/article', 'Title', 'Summary')
        self._run(tmp_path, [article])

        # After the first run, both homepage and article are current.
        saves = self._track_saves(monkeypatch)
        self._run(tmp_path, [article])
        assert saves == [], f"unexpected regenerations: {[p.name for p in saves]}"

    # ── cache miss on content change ──────────────────────────────────────────

    def test_title_change_forces_article_regeneration(self, tmp_path, monkeypatch):
        article = _FakeArticle('cat/article', 'Original Title', 'Summary')
        self._run(tmp_path, [article])

        article.title = 'Changed Title'
        saves = self._track_saves(monkeypatch)
        self._run(tmp_path, [article])

        article_webp = tmp_path / 'assets' / 'og-images' / 'cat' / 'article.webp'
        assert article_webp in saves

    # ── cache miss when renderer hash not in sidecar ──────────────────────────

    def test_stale_renderer_hash_forces_regeneration(self, tmp_path, monkeypatch):
        """A .sha256 computed without _RENDERER_HASH is always treated as stale.

        This simulates a local cache left over from before the renderer-hash
        feature was introduced (or from a different version of og_images.py).
        """
        slug, title, summary = 'cat/article', 'My Title', 'My Summary'

        out_base = tmp_path / 'assets' / 'og-images' / 'cat'
        out_base.mkdir(parents=True)
        webp = out_base / 'article.webp'
        webp.write_bytes(b'old-image-data')
        # Old-style hash: three parts, no renderer hash prepended.
        old_hash = _content_hash(title, slug, summary)
        webp.with_suffix('.sha256').write_text(old_hash)

        saves = self._track_saves(monkeypatch)
        _generate(_FakeGenerator(tmp_path, [_FakeArticle(slug, title, summary)]))

        assert webp in saves, "article was not regenerated despite stale sidecar"
        new_hash = webp.with_suffix('.sha256').read_text().strip()
        assert new_hash == _content_hash(_RENDERER_HASH, title, slug, summary)
