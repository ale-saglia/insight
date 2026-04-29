# Code Review — Pelican Template "Insight"

## Priority Summary

| #   | Severity | Issue                                                                                | Location                                  | Status     |
| --- | -------- | ------------------------------------------------------------------------------------ | ----------------------------------------- | ---------- |
| 23  | Critical | Three different ways to install dependencies (uv hashed / pip plain / wipe & reinstall) | Dockerfile, devcontainer.json, Makefile   | ✅ Done    |
| 24  | Medium   | Pelican plugins have no tests (slug, breadcrumbs, category gen, OG cache)            | tests/, plugins/                          | ✅ Done    |
| 25  | Medium   | No internal link checker in CI: renaming an `article_id` silently breaks inbound links | .github/workflows/, src/*.md cross-refs   | ✅ Done    |
| 26  | Medium   | `tag_counts` does not lowercase tag names; `archives.html` filter compares with `lower()` → potential mismatch | plugins/insight_articles.py, themes/insight/templates/archives.html | ⬜ Open    |
| 27  | Low      | LICENSE references Jekyll-era files (`_layouts/`, `_includes/`) that don't exist in this repo | LICENSE                                   | ⬜ Open    |
| 28  | Low      | `.gitignore` ignores `assets/og-images/` but the plugin now writes into `_site/assets/og-images/` | .gitignore                                | ⬜ Open    |
| 29  | Low      | `ensure_frontmatter.py` validates `category` and `permalink` but no article uses these fields anymore | scripts/ensure_frontmatter.py             | ⬜ Open    |
| 30  | Low      | `robots.txt` hardcodes `https://insight.ale-saglia.com/sitemap.xml` instead of using `SITEURL` | robots.txt, pelicanconf.py                | ✅ Done    |
| 31  | Low      | Homepage intro hardcoded in template instead of a content file                       | themes/insight/templates/index.html       | ⬜ Open    |
| 32  | Note     | `DEFAULT_DATE_FORMAT` likely unused (templates call `strftime` directly)             | pelicanconf.py                            | ⬜ Open    |
| 33  | Note     | `_episode_number(...) or 0` is dead defensive code: in `series_groups` the value is never `None` | plugins/insight_articles.py               | ⬜ Open    |

---

## Details

### 23. Three different ways to install dependencies

There are three independent install paths for the Python environment, and they don't agree:

1. **Makefile** (`make setup` / `make setup-dev`) → `uv venv` + `uv pip install --require-hashes` from `requirements.txt` / `requirements-dev.txt`. Hashed, locked, deterministic.
2. **Dockerfile** → `uv venv .venv` + `uv pip install --require-hashes -r requirements.txt`. Same approach, only direct deps (no test deps).
3. **devcontainer.json `postCreateCommand`** → `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`. **Wipes the venv created by the Dockerfile** and rebuilds it with plain `pip`, no hash verification, no `uv`.

This is the worst of both worlds: the Dockerfile does work that gets thrown away, and the actual venv used by the developer bypasses the hash pinning that exists everywhere else. Drift waiting to happen.

**Fix:** make the Dockerfile install `requirements-dev.txt` directly (it's a superset of `requirements.in`), and let `postCreateCommand` be a no-op or a `make` sanity check. Single install path, single source of truth.

---

### 24. Pelican plugins have no tests

✅ **Done** (commit `8ecbb71`) — 66 new tests in three files:

- `tests/test_insight_articles.py` — `_episode_number`, `_enrich_article` (slug, underscore stripping, breadcrumbs, reading time, git date, series placeholders)
- `tests/test_insight_categories.py` — `CategoryPage`, `CategoryPageGenerator.generate_context` (filesystem walk, parent resolution, child_categories)
- `tests/test_og_images.py` — `_content_hash`, `_is_current`, `_save_image`

---

### 25. No internal link checker in CI

✅ **Done** — added `lycheeverse/lychee-action@v2` step in `.github/workflows/pages.yml` after the Pelican build, before the artifact upload. Runs offline (no HTTP requests), resolves absolute paths against `_site/`, excludes `mailto:` links. Breaks CI before deploy if any internal link is dead.

---

### 26. `tag_counts` case mismatch

In `plugins/insight_articles.py:75-78`:

```python
for tag in getattr(article, 'tags', None) or []:
    tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
```

Tags are counted with their original case. But the frontend filter in `archives.html` uses `data-keyword="{{ kw | lower }}"` and the JS in `archives.js` compares lowercased values. If two articles tag `Python` and `python`, `tag_counts` shows two separate entries; the filter merges them.

**Fix:** lowercase in the plugin: `tag_counts[tag.name.lower()] = ...`. Two-line change, eliminates a class of latent bugs.

---

### 27. LICENSE references files that don't exist

The MIT section lists "`_layouts/`, `_includes/`, `scripts/`, `assets/`" as files covered. `_layouts/` and `_includes/` are Jekyll conventions; this repo uses `themes/insight/templates/` and `plugins/`. The license is technically still valid, but the file list is misleading and looks like the LICENSE was copied from a Jekyll repo without updating.

**Fix:** replace with the actual paths: `themes/`, `plugins/`, `scripts/`, `assets/`, `pelicanconf.py`, `publishconf.py`, `Makefile`, `.github/`, `.devcontainer/`.

---

### 28. `.gitignore` references obsolete OG images path

```gitignore
# --- Build Artifacts ---
_site/
assets/og-images/
```

After issue #6 was fixed, `og_images.py` writes to `_site/assets/og-images/` (already covered by `_site/`). The `assets/og-images/` line is now dead.

**Fix:** remove the line. Either it's redundant with `_site/`, or — if the path is gone entirely — it's obsolete documentation.

---

### 29. `ensure_frontmatter.py` validates dead fields

In `scripts/ensure_frontmatter.py:172-181`, the script warns on `category` / `permalink` mismatches:

```python
if 'category' in meta:
    fm_cat = str(meta['category'])
    if fm_cat not in (category, top_domain):
        _warn(path, f'category mismatch: ...')
```

These were Jekyll fields. None of the current articles use them — Pelican derives category from path, and slugs come from `article_id`. The validation can never fire on real content; it only adds maintenance surface.

**Fix:** drop both blocks (same logic as #13 — strip Jekyll cruft on both sides).

---

### 30. `robots.txt` hardcodes the production URL

```
Sitemap: https://insight.ale-saglia.com/sitemap.xml
```

Every other URL in the build is derived from `SITEURL`. This one is hardcoded, which means:
- Local builds advertise the production sitemap URL.
- Changing the domain requires editing two places (`publishconf.py` and `robots.txt`).

**Fix:** move `robots.txt` to `TEMPLATE_PAGES` and use `{{ SITEURL }}/sitemap.xml`. Same pattern already used for `sitemap.xml` and `404.html`.

---

### 31. Homepage intro hardcoded in template

The opening paragraph in `themes/insight/templates/index.html:5` ("There is a threshold where engineering becomes governance...") is a piece of editorial content embedded in a Jinja2 template. Editing it means touching the theme.

**Fix:** move it to a content file (`src/_general/_intro.md` or similar), load via the page system or a template variable. Editorial content lives in `src/`, not in `themes/`.

---

### 32. `DEFAULT_DATE_FORMAT` likely unused

`pelicanconf.py:13` sets `DEFAULT_DATE_FORMAT = '%d %b %Y'`. Templates call `article.date.strftime('%d %b %Y')` directly everywhere — they don't go through the Pelican locale formatting pipeline.

**Fix:** verify by deleting the line and rebuilding. If output is identical, remove permanently.

---

### 33. Dead defensive code in series sort

In `plugins/insight_articles.py:53`:

```python
sorted_series = sorted(articles, key=lambda a: _episode_number(a.get_relative_source_path()) or 0)
```

The `or 0` handles a `None` from `_episode_number`. But articles only enter `series_groups` after the same function returned a non-None value (line 47). The fallback can never trigger.

**Fix:** drop the `or 0`. If the assumption ever changes, a `TypeError` is more informative than a silent zero.

---

## Long Term

Items not urgent now but worth revisiting as the site grows.

| # | Trigger | Action |
| - | ------- | ------ |
| L1 | Article count becomes visible | Cache `_site/assets/og-images/` in CI via `actions/cache` keyed on plugin + source files hash |

---

## Suggested order of attack

By impact / effort ratio:

1. ~~**#23 Unify dependency setup**~~ ✅
2. ~~**#25 Link checker in CI**~~ ✅
3. ~~**#24 Plugin tests**~~ ✅
4. **#26 Tag case-normalization** — latent bug, two-line fix.
5. **#27–#33** — incidental polish during normal work.