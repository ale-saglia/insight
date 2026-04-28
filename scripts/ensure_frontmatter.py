#!/usr/bin/env python3
"""Ensure required YAML frontmatter on all src/**/*.md article files.

Additive only — never overwrites existing values. Exits with code 1 if any
ERROR-level issue is found; warnings are non-fatal.

Rules applied to each article file (README.md excluded):
  title    — from first H1; fallback to filename stem (WARNING).
  created  — from git first-commit date; fallback to today (WARNING).
  keywords — inserted empty when missing (WARNING).
  excerpt  — inserted empty when missing (WARNING).

Body normalisation: leading blank lines stripped, duplicate H1 removed when
it matches the title, trailing blank lines stripped. EOF newline preserved.

Validation (warn-only, no mutation):
  category  — warns if frontmatter value doesn't match directory structure.
  permalink — warns if frontmatter value doesn't start with /top-domain/.
"""

import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

SRC = Path('src')
_KNOWN_FIELDS = ['title', 'created', 'modified', 'keywords', 'excerpt']

_warn_count = 0
_error_count = 0
_update_count = 0


def _emit(level, path, msg):
    global _warn_count, _error_count
    if level == 'warning':
        _warn_count += 1
        gha_level = 'warning'
    else:
        _error_count += 1
        gha_level = 'error'

    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print(f'::{gha_level} file={path}::{msg}', flush=True)
    else:
        print(f'{level.upper()}: {path}: {msg}', file=sys.stderr)


def _warn(path, msg):
    _emit('warning', path, msg)


def _error(path, msg):
    _emit('error', path, msg)


def _parse_frontmatter(text):
    """Return (meta_dict, body_str). meta is {} when frontmatter is absent."""
    if not (text.startswith('---\n') or text.startswith('---\r\n')):
        return {}, text
    lf_end = text.find('\n---\n', 4)
    crlf_end = text.find('\n---\r\n', 4)
    if lf_end == -1 and crlf_end == -1:
        return {}, text
    if lf_end != -1 and (crlf_end == -1 or lf_end <= crlf_end):
        end, skip = lf_end, 5
    else:
        end, skip = crlf_end, 6
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        return None, exc  # signals a parse error
    return meta, text[end + skip:]


def _first_commit_date(path):
    result = subprocess.run(
        ['git', 'log', '--follow', '--diff-filter=A',
         '--format=%ad', '--date=format:%Y-%m-%d', '--', str(path)],
        capture_output=True, text=True,
    )
    lines = result.stdout.strip().splitlines()
    return datetime.strptime(lines[-1], '%Y-%m-%d').date() if lines else None


def _extract_h1(body):
    for line in body.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return None


def _normalize_body(body, strip_h1=None):
    lines = body.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    if strip_h1 and lines and lines[0].startswith('# '):
        if lines[0][2:].strip() == strip_h1:
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)


def _write(path, meta, body, trailing_newline):
    global _update_count
    ordered = {k: meta[k] for k in _KNOWN_FIELDS if k in meta}
    for k, v in meta.items():
        if k not in ordered:
            ordered[k] = v
    fm = yaml.dump(ordered, default_flow_style=False, allow_unicode=True, sort_keys=False)
    content = f'---\n{fm}---\n\n{body}\n'
    if not trailing_newline:
        content = content.rstrip('\n')
    path.write_text(content, encoding='utf-8')
    _update_count += 1


def _process(path):
    text = path.read_text(encoding='utf-8')
    trailing_newline = text.endswith('\n')
    meta, body = _parse_frontmatter(text)

    if meta is None:  # YAML parse error
        _error(path, f'YAML frontmatter is malformed ({body}) — skipping file')
        return

    original_keys = set(meta)

    h1 = _extract_h1(body)

    # title (additive)
    if 'title' not in meta:
        if h1:
            meta['title'] = h1
        else:
            meta['title'] = path.stem
            _warn(path, 'title not found (missing H1): using filename fallback')

    # created (additive)
    if 'created' not in meta:
        git_date = _first_commit_date(path)
        if git_date:
            meta['created'] = git_date
        else:
            today = date.today()
            meta['created'] = today
            _warn(path, f'created not found in git history: using today ({today})')

    # layout is Jekyll migration cruft — strip it (Pelican ignores it)
    meta.pop('layout', None)

    # keywords (additive)
    if 'keywords' not in meta:
        meta['keywords'] = ''
        _warn(path, 'keywords missing: inserted empty placeholder')

    # excerpt (additive)
    if 'excerpt' not in meta:
        meta['excerpt'] = ''
        _warn(path, 'excerpt missing: inserted empty placeholder')

    # Validation: category / permalink coherence (warn-only)
    parts = path.parts  # ('src', 'top_domain', ..., 'file.md')
    top_domain = parts[1] if len(parts) > 2 else ''
    category = parts[-2] if len(parts) > 2 else ''
    if 'category' in meta:
        fm_cat = str(meta['category'])
        if fm_cat not in (category, top_domain):
            _warn(path, f'category mismatch: frontmatter has "{fm_cat}", expected "{top_domain}"')
    if 'permalink' in meta:
        fm_perm = str(meta['permalink'])
        if not fm_perm.startswith(f'/{top_domain}/'):
            _warn(path, f'permalink mismatch: "{fm_perm}" does not start with "/{top_domain}/"')

    # Determine H1 to strip (strip when it duplicates the title)
    title_val = str(meta.get('title', ''))
    strip_h1 = h1 if (h1 and h1 == title_val) else None

    normalized = _normalize_body(body, strip_h1=strip_h1)

    fields_changed = set(meta) != original_keys
    expected_body_section = f'\n{normalized}\n' if trailing_newline else f'\n{normalized}'
    if fields_changed or body != expected_body_section:
        _write(path, meta, normalized, trailing_newline)


def main():
    if subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True).returncode != 0:
        print('ERROR: not a git repository', file=sys.stderr)
        sys.exit(1)

    for md_file in sorted(SRC.rglob('*.md')):
        if md_file.name == 'README.md':
            continue
        _process(md_file)

    print(
        f'Front matter check complete. '
        f'Updated: {_update_count}. Warnings: {_warn_count}. Errors: {_error_count}.'
    )
    if _error_count:
        sys.exit(1)


if __name__ == '__main__':
    main()
