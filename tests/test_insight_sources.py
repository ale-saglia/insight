"""Tests for structured article source popovers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from plugins.insight_sources import prepare_article_sources


def test_sources_block_becomes_inline_popover():
    body = """Claim with a source [1].

## Sources

All sources accessed 30 June 2026.

1. Example Publisher, "Useful report". https://example.com/report
"""

    rendered, sources = prepare_article_sources(body)

    assert len(sources) == 1
    assert sources[0].number == 1
    assert sources[0].text == 'Example Publisher, "Useful report"'
    assert sources[0].url == 'https://example.com/report'
    assert '## Sources' not in rendered
    assert 'class="source-ref"' in rendered
    assert 'class="source-popover-title">Example Publisher, &quot;Useful report&quot;' in rendered
    assert 'href="https://example.com/report"' in rendered
    assert 'target="_blank"' in rendered
    assert 'aria-expanded="false"' in rendered
    assert '>https://example.com/report</a>' in rendered
    assert 'Open source' not in rendered
    assert 'All sources accessed 30 June 2026.' in rendered


def test_refs_without_matching_source_are_left_alone():
    body = """Known [1], unknown [2].

## Sources

1. Example. https://example.com/one
"""

    rendered, _sources = prepare_article_sources(body)

    assert 'data-source-number="1"' in rendered
    assert 'unknown [2]' in rendered


def test_refs_inside_code_and_reference_definitions_are_not_rewritten():
    body = """Inline `[1]` stays literal.

```text
[1] also stays literal.
```

[1]: https://example.com/reference-definition

Visible [1].

## Sources

1. Example. https://example.com/one
"""

    rendered, _sources = prepare_article_sources(body)

    assert 'Inline `[1]` stays literal.' in rendered
    assert '[1] also stays literal.' in rendered
    assert '[1]: https://example.com/reference-definition' in rendered
    assert rendered.count('class="source-ref"') == 1
