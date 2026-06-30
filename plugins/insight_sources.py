"""Structured article sources for Insight Markdown articles."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass


_SOURCE_HEADING_RE = re.compile(r'^(?P<marker>#{2})\s+(?P<title>sources|fonti)\s*$', re.IGNORECASE)
_SOURCE_ITEM_RE = re.compile(r'^\s*(?P<number>\d+)\.\s+(?P<text>.+?)\s*$')
_SOURCE_REF_RE = re.compile(r'(?<!!)(?<!\[)\[(?P<number>\d+)\](?![(:])')
_URL_RE = re.compile(r'https?://[^\s<>"\']+')
_FENCE_RE = re.compile(r'^\s*(```+|~~~+)')


@dataclass(frozen=True)
class ArticleSource:
    number: int
    text: str
    url: str | None


def prepare_article_sources(body: str) -> tuple[str, list[ArticleSource]]:
    """Turn a terminal ``## Sources`` block into inline source popovers."""

    split = _split_sources(body)
    if split is None:
        return body, []

    article_body, _title, source_lines = split
    note_lines, sources = _parse_sources(source_lines)
    if not sources:
        return body, []

    sources_by_number = {source.number: source for source in sources}
    linked_body = _link_source_refs(article_body, sources_by_number, note_lines)
    return f'{linked_body.rstrip()}\n', sources


def _split_sources(body: str) -> tuple[str, str, list[str]] | None:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        match = _SOURCE_HEADING_RE.match(line)
        if match:
            title = match.group('title').capitalize()
            article_body = '\n'.join(lines[:index])
            return article_body, title, lines[index + 1:]
    return None


def _parse_sources(lines: list[str]) -> tuple[list[str], list[ArticleSource]]:
    note_lines: list[str] = []
    sources: list[ArticleSource] = []
    current_number: int | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_number, current_lines
        if current_number is None:
            return

        raw_text = ' '.join(part.strip() for part in current_lines if part.strip())
        if raw_text:
            url = _first_url(raw_text)
            text = _remove_url(raw_text, url) if url else raw_text
            sources.append(ArticleSource(current_number, text, url))
        current_number = None
        current_lines = []

    for line in lines:
        match = _SOURCE_ITEM_RE.match(line)
        if match:
            flush_current()
            current_number = int(match.group('number'))
            current_lines = [match.group('text')]
            continue

        if current_number is not None:
            if line.startswith((' ', '\t')) or not line.strip():
                current_lines.append(line)
            continue

        if line.strip():
            note_lines.append(line.strip())

    flush_current()
    return note_lines, sources


def _first_url(text: str) -> str | None:
    match = _URL_RE.search(text)
    if not match:
        return None
    return match.group(0).rstrip('.,);]')


def _remove_url(text: str, url: str | None) -> str:
    if not url:
        return text

    return text.replace(url, '').strip().rstrip('.,;')


def _link_source_refs(
    markdown_text: str,
    sources_by_number: dict[int, ArticleSource],
    note_lines: list[str],
) -> str:
    in_fence = False
    linked_lines = []

    for line in markdown_text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            linked_lines.append(line)
            continue

        if in_fence:
            linked_lines.append(line)
        else:
            linked_lines.append(_link_source_refs_in_line(line, sources_by_number, note_lines))

    return '\n'.join(linked_lines)


def _link_source_refs_in_line(
    line: str,
    sources_by_number: dict[int, ArticleSource],
    note_lines: list[str],
) -> str:
    parts = re.split(r'(`+[^`]*`+)', line)
    for index in range(0, len(parts), 2):
        parts[index] = _SOURCE_REF_RE.sub(
            lambda match: _render_source_ref(match, sources_by_number, note_lines),
            parts[index],
        )
    return ''.join(parts)


def _render_source_ref(
    match: re.Match[str],
    sources_by_number: dict[int, ArticleSource],
    note_lines: list[str],
) -> str:
    number = int(match.group('number'))
    source = sources_by_number.get(number)
    if source is None:
        return match.group(0)

    return (
        f'<sup class="source-ref" data-source-number="{number}">'
        f'<button type="button" class="source-ref-trigger" aria-label="Source {number}" aria-expanded="false">[{number}]</button>'
        f'{_render_source_popover(source, note_lines)}'
        f'</sup>'
    )


def _render_source_popover(source: ArticleSource, note_lines: list[str]) -> str:
    html_lines = [
        '<span class="source-popover" role="tooltip">',
        f'<span class="source-popover-index">Source {source.number}</span>',
        f'<span class="source-popover-title">{html.escape(source.text)}</span>',
    ]

    for note in note_lines:
        html_lines.append(f'<span class="source-popover-note">{_link_urls(note)}</span>')

    if source.url:
        safe_url = html.escape(source.url, quote=True)
        display_url = html.escape(source.url)
        html_lines.append(
            f'<a class="source-popover-link" href="{safe_url}" title="{safe_url}" '
            f'target="_blank" rel="noopener noreferrer">{display_url}</a>'
        )
    html_lines.append('</span>')
    return '\n'.join(html_lines)


def _link_urls(text: str) -> str:
    escaped = html.escape(text)

    def replace(match: re.Match[str]) -> str:
        url = match.group(0).rstrip('.,);]')
        suffix = match.group(0)[len(url):]
        return (
            f'<a class="source-url" href="{html.escape(url, quote=True)}" '
            f'rel="noopener noreferrer">{html.escape(url)}</a>{html.escape(suffix)}'
        )

    return _URL_RE.sub(replace, escaped)
