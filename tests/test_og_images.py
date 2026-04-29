"""Tests for plugins/og_images.py — cache helpers only (no font/PIL rendering)."""

import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from plugins.og_images import _content_hash, _is_current, _save_image


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
