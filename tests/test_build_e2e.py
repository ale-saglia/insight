"""E2E build test — verifies that a real Pelican build produces valid HTML.

Runs once per module via a module-scoped fixture; individual tests assert
specific outputs without re-invoking the build.
"""

import os
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def _create_fixture(tmp: Path) -> None:
    """Populate tmp/ with a minimal src/ structure."""
    (tmp / "src" / "_general").mkdir(parents=True)
    (tmp / "src" / "test-cat").mkdir(parents=True)

    (tmp / "src" / "_general" / "README.md").write_text(
        "---\nlayout: category\ntitle: General\nsummary: General articles.\n---\n"
    )
    (tmp / "src" / "test-cat" / "README.md").write_text(
        "---\nlayout: category\ntitle: Test Category\nsummary: A test category.\n---\n"
    )
    (tmp / "src" / "test-cat" / "test-article.md").write_text(
        "---\n"
        "title: Hello E2E World\n"
        "created: 2026-01-15\n"
        "keywords: testing, e2e\n"
        "excerpt: A minimal article for the E2E build test.\n"
        "article_id: hello-e2e-world\n"
        "---\n\n"
        "This is the article body.\n"
    )


def _pelican_settings(tmp: Path) -> dict:
    return {
        "PATH": str(tmp),
        "ARTICLE_PATHS": ["src"],
        "IGNORE_FILES": ["README.md", ".#*"],
        "PAGE_PATHS": [],
        "OUTPUT_PATH": str(tmp / "_site"),
        "THEME": str(PROJECT_ROOT / "themes" / "insight"),
        "PLUGIN_PATHS": [str(PROJECT_ROOT)],
        # og_images skipped: PIL/font-heavy and not needed for a smoke test
        "PLUGINS": ["plugins.insight_register"],
        "SITENAME": "Test Site",
        "SITESUBTITLE": "Test subtitle",
        "HOMEPAGE_INTRO": "Test intro.",
        "SITEURL": "",
        "AUTHOR": "Test Author",
        "AUTHOR_URL": "https://example.com",
        "TIMEZONE": "UTC",
        "DEFAULT_LANG": "en",
        "RELATIVE_URLS": True,
        "FEED_ATOM": None,
        "FEED_ALL_ATOM": None,
        "CATEGORY_FEED_ATOM": None,
        "TAG_FEED_ATOM": None,
        "AUTHOR_FEED_ATOM": None,
        "AUTHOR_FEED_RSS": None,
        "TRANSLATION_FEED_ATOM": None,
        "ARTICLE_URL": "{slug}/",
        "ARTICLE_SAVE_AS": "{slug}/index.html",
        "PAGE_URL": "{slug}/",
        "PAGE_SAVE_AS": "{slug}/index.html",
        "CATEGORY_SAVE_AS": "",
        "CATEGORY_URL": "",
        "TAG_SAVE_AS": "",
        "TAG_URL": "",
        "AUTHOR_SAVE_AS": "",
        "AUTHOR_URL_FORMAT": "",
        "AUTHORS_SAVE_AS": "",
        "TAGS_SAVE_AS": "",
        "CATEGORIES_SAVE_AS": "",
        "ARCHIVES_SAVE_AS": "archive/index.html",
        "INDEX_SAVE_AS": "index.html",
        "STATIC_PATHS": [],
        "TEMPLATE_PAGES": {},
        "DELETE_OUTPUT_DIRECTORY": False,
        "DEFAULT_PAGINATION": False,
        "MARKDOWN": {
            "extension_configs": {
                "markdown.extensions.codehilite": {"css_class": "highlight"},
                "markdown.extensions.extra": {},
                "markdown.extensions.fenced_code": {},
                "markdown.extensions.tables": {},
            },
            "output_format": "html5",
        },
    }


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    """Run a full Pelican build once; yield the _site/ path.

    CategoryPageGenerator opens README.md files with paths relative to PATH,
    so the CWD must equal tmp during the build.
    """
    tmp = tmp_path_factory.mktemp("e2e_build")
    _create_fixture(tmp)

    from pelican import Pelican
    from pelican.settings import read_settings

    original_cwd = os.getcwd()
    os.chdir(tmp)
    try:
        settings = read_settings(override=_pelican_settings(tmp))
        Pelican(settings).run()
    finally:
        os.chdir(original_cwd)

    return tmp / "_site"


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def test_index_exists(site):
    assert (site / "index.html").exists()


def test_index_contains_article_title(site):
    assert "Hello E2E World" in (site / "index.html").read_text()


def test_archive_exists(site):
    assert (site / "archive" / "index.html").exists()


def test_article_page_exists(site):
    assert (site / "test-cat" / "hello-e2e-world" / "index.html").exists()


def test_article_page_contains_body(site):
    html = (site / "test-cat" / "hello-e2e-world" / "index.html").read_text()
    assert "Hello E2E World" in html
    assert "This is the article body" in html


def test_category_page_exists(site):
    assert (site / "test-cat" / "index.html").exists()
