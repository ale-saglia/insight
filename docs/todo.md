# Code Review — Pelican Template "Insight"

Updated state after senior review. Issues closed in previous rounds are archived at the bottom for historical reference.

## Priority Summary

| #  | Severity  | Issue                                                                                                  | Location                                              | Status |
| -- | --------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- | ------ |
| 34 | High      | `_episode_number` + `or 0` pattern rejected in #33 but replicated in `insight_categories.py` (4 spots) | plugins/insight_categories.py:80, 86, 88, 92          | Open   |
| 35 | High      | `og_images.py` cache hash does not include rendering version: edits to `_draw_*` don't invalidate cache | plugins/og_images.py                                  | Open   |
| 36 | High      | `InsightMarkdownReader` subclasses `MarkdownReader` but never calls `super().read()`: fake inheritance | plugins/insight_reader.py                             | Open   |
| 37 | Medium    | #26 fix changed tag display in archive: buttons now always render lowercase, regardless of source tag  | themes/insight/templates/archives.html                | Open   |
| 38 | Medium    | `CategoryPageGenerator`: child article sort happens only in `generate_output`, not in `generate_context` | plugins/insight_categories.py                       | Open   |
| 39 | Medium    | `_enrich_article` returns silently on failed precondition: no log, debugging impossible                | plugins/insight_articles.py:91                        | Open   |
| 40 | Medium    | No E2E build test: nothing guarantees `_site/index.html` is generated correctly                        | tests/                                                | Open   |
| 41 | Low       | `_build_git_date_map` reads the entire git history, not just `src/`                                    | plugins/insight_articles.py:14                        | Open   |
| 42 | Low       | `_first_commit_date` doesn't check `result.returncode`: git error indistinguishable from new file      | scripts/ensure_frontmatter.py                         | Open   |
| 43 | Low       | `nav.js` uses `setTimeout(checkLayout, 100)` as font fallback: dropdown flicker on slow connections    | assets/js/nav.js                                      | Open   |
| 44 | Low       | `archives.js`: no debounce on search input; expensive recomputation on every keystroke                 | assets/js/archives.js                                 | Open   |
| 46 | Note      | #31 marked "Done" but only partial: `HOMEPAGE_INTRO` still in `pelicanconf.py`, not in `src/`          | pelicanconf.py                                        | Open   |
| 47 | Note      | OG image generation runs single-threaded; ~10s on 250 articles                                         | plugins/og_images.py                                  | Open   |
| 48 | Note      | `ensure_frontmatter.py` parses YAML and rewrites the file, then `InsightMarkdownReader` reparses it    | scripts/ensure_frontmatter.py + plugins/insight_reader.py | Open |
| 49 | Note      | `make check-links` and CI need `CHECK_PORT` documented in `local-development.md` (default 4567)        | Makefile + docs/local-development.md                  | Open   |

---

## Details

### 34. `or 0` replicated after being rejected in #33

In #33 you removed `_episode_number(...) or 0` from `insight_articles.py` because it was defensive and misleading. The same pattern exists in `insight_categories.py:80,86,88,92`:

```python
direct = sorted(direct, key=lambda a: getattr(a, 'episode_num', 0) or 0)
```

`getattr(a, 'episode_num', 0)` already covers the "missing attribute" case. The trailing `or 0` only handles `episode_num is None`, which is exactly what the surrounding `if any(... is not None ...)` guard already excludes.

**Fix:** drop `or 0` from all four spots, or rewrite the guard to handle None explicitly:

```python
key=lambda a: a.episode_num if a.episode_num is not None else 0
```

Internal consistency first: either zero-sentinels everywhere or nowhere.

---

### 35. OG cache doesn't invalidate on rendering changes

```python
hp_hash = _content_hash(site_title, site_desc, domain, author)
art_hash = _content_hash(article.title or slug, slug, summary)
```

The hash depends only on content. If you change `_draw_article` (font, layout, palette, dimensions), the cache stays "current" and images are not regenerated until `make rebuild`. On CI it's not a problem (`DELETE_OUTPUT_DIRECTORY = True`), locally it is.

**Fix:** add a version tag to the module:

```python
_RENDERER_VERSION = "v1"  # bump when you change _draw_*
hp_hash = _content_hash(_RENDERER_VERSION, site_title, ...)
```

Or more robust: hash the contents of `og_images.py` itself (computed once at load time).

---

### 36. `InsightMarkdownReader` doesn't call `super().read()`

```python
class InsightMarkdownReader(MarkdownReader):
    def read(self, source_path):
        with open(source_path, encoding='utf-8') as f:
            raw = f.read()
        # ... custom parsing, super() never called
```

You subclass `MarkdownReader` but override `read()` entirely. That's not inheritance — it's polymorphism in disguise. If Pelican adds logic to `MarkdownReader.read()` (encoding handling, plugin hooks, internal signals), you don't get it.

**Fix:** pick one of two options:
1. Subclass `BaseReader` directly — more honest about what you're doing.
2. Call `super().read()` and then remap metadata — safer against Pelican upgrades.

The current setup is the worst of both: you declare an inheritance you don't honor.

---

### 37. #26 fix changed tag display in archive

After lowercasing `tag_counts`, `archives.html` renders:

```jinja
<button class="keyword-btn" data-keyword="{{ kw | lower }}" ...>{{ kw }} <span class="count">...</span></button>
```

Where `kw` is now already lowercase. If you ever had a tag like `Python`, the button used to read "Python". Now it reads "python". Your tags happen to be all lowercase already, so you don't see it — but the #26 fix changed UI behavior without declaring it.

**Fix options:**
- Lowercase only the *matching key*, keep the *display* original: `tag_counts[tag.name] = ...` and compare with `.toLowerCase()` on both sides in JS.
- Document the choice: "all tags rendered in lowercase for visual consistency" (legitimate editorial decision).

I'd take the second. But the choice should be explicit.

---

### 38. Child articles sorted only in `generate_output`

`CategoryPageGenerator.generate_context` populates `category_pages` with `child_categories` but **without** sorted `direct_articles`. That sort happens later, in `generate_output`. So if any other template (e.g. a future `index.html`) accesses `child.direct_articles` from a render phase invoked before `generate_output`, it sees `[]`.

**Fix:** move the sort into `generate_context`. Cost is zero (single pass over articles, already happening) and removes an implicit ordering dependency.

---

### 39. `_enrich_article` returns silently

```python
if len(parts) < 3 or parts[0] != 'src':
    return
```

An article that violates this precondition ends up in the site without `slug`, without `breadcrumbs`, without `category_path`. Pelican doesn't complain. The template hits `{{ article.slug }}` and produces an empty string or an `AttributeError` at runtime in unpredictable ways.

**Fix:**

```python
if len(parts) < 3 or parts[0] != 'src':
    logger.warning('Article %s skipped: path does not match src/<category>/<file>', source_rel)
    return
```

If you want to be more aggressive, raise. For a personal site I'd prefer the warning.

---

### 40. No E2E build test

You have 66 plugin tests, but nothing verifies that a Pelican build actually produces valid HTML. A minimal test:

```python
def test_build_produces_index(tmp_path):
    # copy a minimal src/ fixture, run pelican, assert _site/index.html exists
    ...
```

Mostly valuable as a safety net for Pelican upgrades or dependency bumps.

---

### 41. `git log` runs against entire repo

```python
result = subprocess.run(
    ['git', 'log', '--name-only', '--format=COMMIT %cd', ...],
)
```

Adding `'--', 'src/'` limits the parsing work to the path that actually matters. Three characters, scaling becomes linear with `src/` history rather than the whole repo.

---

### 42. `_first_commit_date` ignores `returncode`

```python
result = subprocess.run([...], capture_output=True, text=True)
lines = result.stdout.strip().splitlines()
return ... if lines else None
```

A git error becomes indistinguishable from "file not yet committed". Practical difference is zero today, but if git starts misbehaving you'll have no signal.

**Fix:** check `result.returncode != 0`, log a warning, return None.

---

### 43. `nav.js` font fallback is fragile

```javascript
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(checkLayout);
} else {
  setTimeout(checkLayout, 100);
}
```

`document.fonts.ready` is supported everywhere except IE (which you don't target). The `setTimeout(100)` is a guess. On a 3G connection the font may take 300-500ms, the first `checkLayout` runs against system fonts, and the dropdown flickers.

**Fix:** drop the fallback, or hard-cap with `Promise.race` at 500ms.

---

### 44. `archives.js` has no debounce

At 250 articles, every keystroke recomputes the count on N year buttons + N keyword buttons. Not blocking now, will be at 500+. A 100ms debounce is 4 lines.

---

### 46. #31 is only partial

You moved `HOMEPAGE_INTRO` from `index.html` into `pelicanconf.py`. Better, but it's still "editorial content inside a config file". Full resolution is reading it from `src/_general/_intro.md` (or similar). For the current site volume, accepting the compromise and marking #31 as "partial" is honest.

---

### 47. OG single-threaded

`_generate` iterates over articles serially. ~40ms per article in Pillow → ~10s at 250 articles. `multiprocessing.Pool` with N=cores brings it to ~2s. Not urgent, but the refactor is trivial.

---

### 48. Double YAML parsing

`ensure_frontmatter.py` parses YAML on every `.md`, normalizes, rewrites. Then `InsightMarkdownReader` parses the same YAML again. At current volume the cost is invisible. Future evolution: the pre-step could expose already-parsed metadata via a cache file (e.g. `.frontmatter-cache.json`) that the reader consumes directly.

---

### 49. Document the `CHECK_PORT` choice for link checking

After migrating from lychee to linkchecker (#45), `make check-links` spins up a local HTTP server because linkchecker on `file://` does not resolve absolute paths like `/feed.xml`. The check server runs on port `CHECK_PORT` (default `4567`), deliberately distinct from `PORT` (default `4000`, used by `make serve`/`make preview`) to avoid collisions when a preview is already running in another shell.

**Fix:** document the new variable in `docs/local-development.md` and in the `make help` output. Edge case to mention: if `CHECK_PORT` is already in use on the developer's machine, `make check-links CHECK_PORT=NNNN` is the override.

---

## Long Term

| # | Trigger | Action |
| - | ------- | ------ |
| L1 | Article count > 50 | Cache `_site/assets/og-images/` in CI via `actions/cache` |
| L2 | Article count > 100 | Multiprocess OG generation (#47) |
| L3 | Article count > 250 | Debounce + virtualization in archives.js (#44) |
| L4 | Pelican major upgrade | E2E build test (#40) becomes mandatory, not optional |

---

## Suggested order of attack

By impact / effort:

1. **#34** Cleanup `or 0` — consistency with #33, 5 minutes.
2. **#39** Logging in `_enrich_article` — future debugging, 5 minutes.
3. **#37** Explicit decision on lowercase tag display — documentation or UI fix.
4. **#35** Versioned OG hash — local-build robustness, 10 minutes.
5. **#41, #42** Git ops polish — 10 minutes total.
6. **#49** Document `CHECK_PORT` — closing the loop on the linkchecker migration, 5 minutes.
7. **#36** Refactor `InsightMarkdownReader` — riskier, do after writing #40.
8. **#40** E2E build test — serious investment, but unlocks all future refactors.
9. **#38, #43, #44, #47, #48** — incidental polish, as before.

---

## Archive (closed issues)

| #   | Issue | Status |
| --- | ----- | ------ |
| 23  | Three inconsistent install paths for dependencies | ✅ Done |
| 24  | Plugins without tests (slug, breadcrumbs, category gen, OG cache) | ✅ Done |
| 25  | No internal link checker in CI | ✅ Done |
| 26  | `tag_counts` case mismatch | ✅ Done (but see #37) |
| 27  | LICENSE referenced non-existent Jekyll files | ✅ Done |
| 28  | `.gitignore` referenced obsolete OG path | ✅ Done |
| 29  | `ensure_frontmatter.py` validated dead `category` and `permalink` fields | ✅ Done |
| 30  | `robots.txt` hardcoded production URL | ✅ Done |
| 31  | Homepage intro hardcoded in template | ⚠️ Partial (see #46) |
| 32  | `DEFAULT_DATE_FORMAT` unused | ✅ Done |
| 33  | Dead `or 0` defensive code in series sort | ✅ Done (but see #34) |
| 45  | `Dockerfile` pulled lychee from `latest` without checksum | ✅ Done — migrated to `linkchecker` (Python, hash-pinned via `requirements-dev.txt`); see #49 for the documentation follow-up |