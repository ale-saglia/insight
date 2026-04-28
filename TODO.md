# Code Review — Pelican Template "Insight"

## Priority Summary

| #   | Severity | Issue                                                        | Location                               | Status  |
| --- | -------- | ------------------------------------------------------------ | -------------------------------------- | ------- |
| 1   | Critical | Breadcrumb label duplicated 4x                               | index, archives, article               | ✅ Done |
| 2   | Critical | OG/Twitter/meta blocks triplicated                           | base + all children                    | ✅ Done |
| 3   | Medium   | O(n) category lookup in templates                            | all                                    | ✅ Done |
| 4   | Critical | `ensure-frontmatter.sh` is 430+ lines of bash                | scripts/ensure-frontmatter.sh          | ✅ Done |
| 5   | Medium   | `versions.env` exists only to be diff-checked                | versions.env, check-versions.yml       | ✅ Done |
| 6   | Medium   | `og_images.py` writes to source tree, not output             | plugins/og_images.py                   | ✅ Done |
| 7   | Medium   | `og_images.py` regenerates everything on each build          | plugins/og_images.py                   | ✅ Done |
| 8   | Medium   | YAML frontmatter parser duplicated across two plugins        | insight_{reader,categories}.py         | ✅ Done |
| 9   | Medium   | O(n²) tag/year counting                                      | archives                               | ✅ Done |
| 10  | Medium   | `og_images.py` Linux-only fonts (silent fail elsewhere)      | plugins/og_images.py                   | ✅ Done |
| 10b | Medium   | `og_images.py` font doesn't match design (not Georgia)       | plugins/og_images.py                   | ✅ Done |
| 11  | Medium   | Unused `ycount` variable                                     | archives:31                            | ✅ Done |
| 12  | Low      | `_get_generators` misleading parameter name                  | plugins/insight_register.py            | ✅ Done |
| 13  | Low      | `layout: article` enforced but ignored                       | ensure-frontmatter.sh, articles        | ✅ Done |
| 14  | Low      | `ARTICLE_EXCLUDES` redundant with `IGNORE_FILES`             | pelicanconf.py                         | ✅ Done |
| 15  | Low      | `_general/` reachable via direct URL despite "hidden" intent | plugins, nav filter                    | ✅ Done |
| 16  | Low      | `_git_last_modified` is O(N) subprocess calls                | plugins/insight_articles.py            | ✅ Done |
| 17  | Low      | `article_id` slug not validated (path traversal surface)     | plugins/insight_articles.py            | ✅ Done |
| 18  | Low      | Duplicate category loop in nav                               | nav                                    |         |
| 19  | Low      | ~235 lines of inline JS                                      | nav, article, archives                 |         |
| 20  | Low      | `<button>` used for navigation                               | article                                |         |
| 21  | Note     | `404.html` as TEMPLATE_PAGES                                 | —                                      |         |
| 22  | Medium   | Unpinned transitive dependencies (partial lock)              | requirements.txt, CI                   |         |

---

## Details

### 4. `ensure-frontmatter.sh` is 430+ lines of bash — wrong tool

The `MANIFESTO.md` calls out engineering proportionality (YAGNI). This script violates it directly: stateful YAML parsing in awk, body normalization, EOF-newline preservation via perl, manual quote escaping. Python is already a hard dependency (Pelican), and `pyyaml` is already in `requirements.txt`.

Rewriting in Python yields:

- Real YAML parsing (today `extract_front_matter_scalar` doesn't handle multi-line values, lists, or nested structures — works only because no article uses them yet).
- Testability (the bash version is effectively untested).
- ~60 lines instead of 430.

Highest-leverage refactor in the repo, and the most manifesto-aligned.

---

### 5. `versions.env` exists only to be diff-checked

No code reads `versions.env`. CI (`pages.yml:25`) reads `PYTHON_VERSION` from the Dockerfile. The devcontainer uses the Dockerfile directly. `check-versions.yml` exists solely to verify the two values match — but the file being checked is never consumed.

This is the worst of both worlds: two files to keep in sync plus dedicated CI infrastructure for zero functional benefit. Two proportionate options:

- Delete `versions.env` and `check-versions.yml`. Single source of truth = Dockerfile.
- Make `versions.env` actually used (CI reads it; check-versions verifies against the Dockerfile).

---

### 6. `og_images.py` writes to source tree, not build output

```python
out_base = Path(generator.path) / 'assets' / 'og-images'
```

`generator.path` is `.` (= PATH). OG images land in `./assets/og-images/`, then Pelican copies `assets/` into `_site/assets/` via STATIC_PATHS. Every build mutates the source tree. Gitignored, so nothing breaks, but:

- Pelican convention is for plugins to write into `OUTPUT_PATH`.
- On CI it's irrelevant (ephemeral runner). Locally it leaves files in the source dir.

Fix: write into `Path(generator.output_path) / 'assets' / 'og-images'`, hooking `finalized` instead of `article_generator_finalized` so the output dir exists.

---

### 7. `og_images.py` regenerates everything on each build

No caching. At 5 articles invisible; at 250 (decade target stated in README) it becomes the build bottleneck — Pillow renders 1200×630 from scratch every article, every build.

Fix: hash `(title + summary + slug)` and write a sidecar `.sha256`; skip render when hash matches. ~10 lines. Manifesto-aligned: avoid paying a growing cost for a deterministic output.

---

### 8. YAML frontmatter parser duplicated across two plugins

Same custom parser logic in:

- `plugins/insight_reader.py:18-30`
- `plugins/insight_categories.py:36-50`

Extract into `plugins/_frontmatter.py` with `parse_frontmatter(raw) -> (meta, body)`. One fix instead of two files to remember.

---

### 9. O(n²) tag/year counting — `archives.html`

In `archives.html:54-62`:

```jinja
{% for kw in all_tags %}
  {% for article in sorted_articles %}
    {% for tag in article.tags %}
      {% if tag.name | lower == kw | lower %}...{% endif %}
    {% endfor %}
  {% endfor %}
{% endfor %}
```

Complexity: `O(keywords × articles × tags_per_article)`. Year counting (lines 31-37) has the same shape — iterates all articles per year when `groupby` would do it in one pass.

**Fix:** Use Jinja2 `groupby` and `selectattr`:

```jinja
{% for year, year_articles in sorted_articles | groupby(attribute='date.year') %}
  <button ...>{{ year }} <span class="count">({{ year_articles | length }})</span></button>
{% endfor %}
```

For tags, build the count in a single pass inside the plugin and expose as a precomputed dict.

---

### 10. `og_images.py` Linux-only font paths (silent fail elsewhere)

```python
candidates = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ...
]
```

All paths are Linux. Fallback to `ImageFont.load_default()` is a tiny pixel font — OG images render unreadable on macOS dev without Docker, silently. CI is fine because the Dockerfile installs `fonts-dejavu-core`.

Three options:

- Bundle `assets/fonts/DejaVuSerif*.ttf` in-repo (~600KB) and reference explicitly.
- Fail loud if no system font is found, instead of silent fallback.
- Document explicitly that local dev requires the devcontainer.

---

### 11. Unused `ycount` variable — `archives.html:31`

```jinja
{% set ycount = sorted_articles | selectattr('date', 'defined') | selectattr('date', 'ne', none) | list %}
```

Computed and never used; counting actually happens in the next loop via `ycount_val.n`. Dead code.

---

### 12. `_get_generators` misleading parameter name

```python
def _get_generators(generators):
    return CategoryPageGenerator
```

The parameter isn't a list of generators — it's the Pelican instance. Works, but the naming is misleading. Rename to `_pelican` or `_instance`.

---

### 13. `layout: article` enforced but ignored

`insight_reader.py` comments `# layout ignored (template selection is done by Pelican)`. But `ensure-frontmatter.sh` keeps inserting it as a required field. Migration cruft from Jekyll. Drop on both sides — the field carries no information for Pelican.

---

### 14. `ARTICLE_EXCLUDES` redundant with `IGNORE_FILES`

```python
ARTICLE_EXCLUDES = ['README.md', '*README.md']
IGNORE_FILES = ['README.md', '.#*']
```

`ARCHITECTURE.md` already notes that Pelican 4.x checks `IGNORE_FILES` at the basename stage and that `ARTICLE_EXCLUDES` is not consulted there. Pick one — likely `IGNORE_FILES` only.

---

### 15. `_general/` accessible via direct URL despite "hidden" intent

`ARCHITECTURE.md` says: *"Leading underscores in directory names (e.g. `_general`) are stripped from the URL path, making those categories invisible in the nav while still generating articles."*

But `CategoryPageGenerator` still emits `_general/README.md` → `/general/index.html`. The category index page is therefore reachable by typing the URL, even though `nav.html` filters out `category_path != 'general'`. Clarify the intent:

- If "hidden" = no nav link only: current behavior is correct, doc is fine.
- If "hidden" = no public URL at all: skip categories whose original directory name starts with `_` in `CategoryPageGenerator`.

---

### 16. `_git_last_modified` is O(N) subprocess calls

One `git log` per article, every build. At 250 articles = 250 fork+exec each build. Fix: a single `git log --name-only --format=...` parsed once into a `{path: date}` dict; lookup O(1) per article. Not urgent; predictable as the archive grows.

---

### 17. `article_id` slug not validated

```python
article.slug = '/'.join(path_parts + [article_id])
```

`article_id` is read from frontmatter and joined into a path. A future article with `article_id: ../escape` would write outside the output dir. Realistically you're the only author, but defensive validation `re.match(r'^[a-z0-9-]+$', article_id)` is one line and closes the surface.

---

### 18. Duplicate category loop — `nav.html`

`nav.html:9-13` and `nav.html:19-23` contain the same loop for category links (inline + dropdown variants). Acceptable given the different surrounding HTML, but extractable into a macro.

---

### 19. Inline `<script>` in nav.html, article.html, archives.html

- ~90 lines in `nav.html:30-116`
- ~30 lines in `article.html:95-125`
- ~115 lines in `archives.html:119-234`
- **Total: ~235 lines of inline JS**

No browser caching (reloaded every page) and templates harder to read. Move to standalone `.js` files in `assets/`.

---

### 20. `<button>` used for navigation — `article.html`

```html
<button class="article-nav-link" id="back-link">← Back to articles</button>
<button class="article-nav-link" id="top-link">↑ Top</button>
```

"Back to articles" navigates via `history.back()` or `window.location.href` — semantically a link, not an action. Use `<a href>` with JS fallback for accessibility.

### 21. `404.html` used as TEMPLATE_PAGES — note

`pelicanconf.py:56` includes `'404.html': '404.html'` in `TEMPLATE_PAGES`, meaning Pelican renders it as a standalone template with full context access. Works with `extends`, no issue — just worth noting that this page is generated as a template page, not as an article.

---

### 22. Unpinned transitive dependencies

`requirements.txt` pins direct dependencies (e.g. `pelican==4.10.2`, `markdown==3.7`), but not their full tree. Pelican depends on Jinja2, MarkupSafe, Pygments, etc.: if one of those releases a breaking version, `pip install -r requirements.txt` on GitHub Actions will silently fetch it and the build will break.

**Fix:** switch to a full lock file generated by modern tools:

- `uv` (preferred for future integration): `uv pip compile requirements.in -o requirements.txt`
- or `pip-tools`: `pip-compile requirements.in`

The `requirements.in` file lists only direct dependencies; the generated `requirements.txt` freezes the entire tree with hashes. Updating dependencies becomes intentional (`uv pip compile --upgrade`) instead of implicit.

This paves the way to integrate `uv` as the single tool for install + lock in CI and the Dockerfile.

---

## Long Term

Items not urgent now but worth revisiting as the site grows.

| # | Trigger | Action |
| - | ------- | ------ |
| L1 | Article count becomes visible | Cache `_site/assets/og-images/` in CI via `actions/cache` keyed on plugin + source files hash |

---

## Suggested order of attack

By impact / effort ratio:

1. `ensure-frontmatter.sh` → Python (#4) — high value, manifesto-aligned, unblocks future content scale.
2. `versions.env` decision (#5) — 30 min, removes dead infrastructure.
3. Frontmatter parser deduplication (#8) — 15 min, DRY.
4. `og_images` caching (#7) — before it becomes visible.
5. `og_images` output path (#6) — semantic correctness.
6. `archives.html` rewrite with `groupby` (#9, #11) — knocks two items in one pass.
7. Everything else — incidental polish during normal work.
