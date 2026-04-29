"""Tests for plugins/insight_articles.py"""

import sys
from datetime import date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from plugins.insight_articles import _enrich_article, _episode_number


class FakeArticle:
    def __init__(self, source_path, content='', **kwargs):
        self._source_path = source_path
        self.content = content
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_relative_source_path(self):
        return self._source_path


# ---------------------------------------------------------------------------
# _episode_number
# ---------------------------------------------------------------------------

class TestEpisodeNumber:
    def test_zero_prefix_returns_zero(self):
        assert _episode_number('src/infra/series/0-intro.md') == 0

    def test_single_digit_prefix(self):
        assert _episode_number('src/infra/series/3-advanced.md') == 3

    def test_multi_digit_prefix(self):
        assert _episode_number('src/infra/series/12-epilogue.md') == 12

    def test_no_digit_prefix_returns_none(self):
        assert _episode_number('src/infra/standalone.md') is None

    def test_digit_not_at_start_returns_none(self):
        # 'part-1-intro' does not start with digits followed by '-'
        assert _episode_number('src/infra/part-1-intro.md') is None

    def test_only_digits_no_dash_returns_none(self):
        assert _episode_number('src/infra/123.md') is None


# ---------------------------------------------------------------------------
# _enrich_article
# ---------------------------------------------------------------------------

class TestEnrichArticle:
    def _make(self, source_path, content='word ' * 400, **kwargs):
        return FakeArticle(source_path, content=content, **kwargs)

    # --- early-return guards ---

    def test_path_too_short_returns_early(self):
        art = self._make('src/only-two.md')
        _enrich_article(art, {})
        assert not hasattr(art, 'slug')

    def test_non_src_prefix_returns_early(self):
        art = self._make('content/infrastructure/my.md')
        _enrich_article(art, {})
        assert not hasattr(art, 'slug')

    # --- slug computation ---

    def test_basic_slug(self):
        art = self._make('src/infrastructure/my-article.md')
        _enrich_article(art, {})
        assert art.slug == 'infrastructure/my-article'

    def test_episode_digit_prefix_stripped_from_slug(self):
        art = self._make('src/infrastructure/series/0-intro.md')
        _enrich_article(art, {})
        assert art.slug == 'infrastructure/series/intro'

    def test_underscore_prefix_stripped_from_dir(self):
        art = self._make('src/_general/my-article.md')
        _enrich_article(art, {})
        assert art.slug == 'general/my-article'

    def test_custom_article_id_overrides_filename(self):
        art = self._make('src/infrastructure/0-intro.md', article_id='custom-id')
        _enrich_article(art, {})
        assert art.slug == 'infrastructure/custom-id'

    def test_invalid_article_id_raises_value_error(self):
        art = self._make('src/infrastructure/my.md', article_id='Has Spaces!')
        with pytest.raises(ValueError):
            _enrich_article(art, {})

    # --- category helpers ---

    def test_category_path_single_dir(self):
        art = self._make('src/infrastructure/my.md')
        _enrich_article(art, {})
        assert art.category_path == 'infrastructure'

    def test_category_path_nested(self):
        art = self._make('src/infrastructure/zero-to-homelab/0-intro.md')
        _enrich_article(art, {})
        assert art.category_path == 'infrastructure/zero-to-homelab'

    def test_category_top_is_first_segment(self):
        art = self._make('src/infrastructure/zero-to-homelab/0-intro.md')
        _enrich_article(art, {})
        assert art.category_top == 'infrastructure'

    # --- breadcrumbs ---

    def test_breadcrumbs_single_dir(self):
        art = self._make('src/infrastructure/my.md')
        _enrich_article(art, {})
        assert art.breadcrumbs == [{'url': 'infrastructure/', 'label': 'Infrastructure'}]

    def test_breadcrumbs_nested(self):
        art = self._make('src/infrastructure/zero-to-homelab/0-intro.md')
        _enrich_article(art, {})
        assert art.breadcrumbs == [
            {'url': 'infrastructure/', 'label': 'Infrastructure'},
            {'url': 'infrastructure/zero-to-homelab/', 'label': 'Zero To Homelab'},
        ]

    def test_breadcrumb_label_from_underscore_stripped_dir(self):
        art = self._make('src/_general/my.md')
        _enrich_article(art, {})
        assert art.breadcrumbs[0] == {'url': 'general/', 'label': 'General'}

    # --- episode_num ---

    def test_episode_num_set_for_numbered_file(self):
        art = self._make('src/infrastructure/series/3-advanced.md')
        _enrich_article(art, {})
        assert art.episode_num == 3

    def test_episode_num_none_for_regular_file(self):
        art = self._make('src/infrastructure/standalone.md')
        _enrich_article(art, {})
        assert art.episode_num is None

    # --- prev/next episode placeholders ---

    def test_prev_next_episode_initialized_to_none(self):
        art = self._make('src/infrastructure/standalone.md')
        _enrich_article(art, {})
        assert art.prev_episode is None
        assert art.next_episode is None

    def test_prev_episode_not_overwritten_if_already_set(self):
        art = self._make('src/infrastructure/standalone.md')
        art.prev_episode = 'sentinel'
        _enrich_article(art, {})
        assert art.prev_episode == 'sentinel'

    # --- reading time ---

    def test_reading_time_two_minutes_for_400_words(self):
        art = self._make('src/infra/my.md', content='word ' * 400)
        _enrich_article(art, {})
        assert art.reading_time == 2

    def test_reading_time_minimum_one(self):
        art = self._make('src/infra/my.md', content='short content')
        _enrich_article(art, {})
        assert art.reading_time == 1

    def test_reading_time_strips_html_tags(self):
        # 200 actual words wrapped in HTML tags
        art = self._make('src/infra/my.md', content='<p>' + 'word ' * 200 + '</p>')
        _enrich_article(art, {})
        assert art.reading_time == 1

    # --- git date ---

    def test_git_date_applied_when_modified_not_set(self):
        art = self._make('src/infra/my.md')
        git_dates = {'src/infra/my.md': date(2024, 6, 15)}
        _enrich_article(art, git_dates)
        assert art.modified == datetime(2024, 6, 15)

    def test_git_date_not_overwritten_when_modified_exists(self):
        existing = datetime(2023, 1, 1)
        art = self._make('src/infra/my.md', modified=existing)
        git_dates = {'src/infra/my.md': date(2024, 6, 15)}
        _enrich_article(art, git_dates)
        assert art.modified == existing

    def test_no_git_date_leaves_modified_unset(self):
        art = self._make('src/infra/my.md')
        _enrich_article(art, {})
        assert not getattr(art, 'modified', None)
