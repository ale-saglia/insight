# Code Review — Pelican Template "Insight"

## Priority Summary

| #   | Severity | Issue                              | Location                 | Status  |
| --- | -------- | ---------------------------------- | ------------------------ | ------- |
| 1   | Critical | Breadcrumb label duplicated 4x     | index, archives, article | ✅ Done |
| 2   | Critical | OG/Twitter/meta blocks triplicated | base + all children      | ✅ Done |
| 3   | Medium   | O(n) category lookup in templates  | all                      | ✅ Done |
| 4   | Medium   | O(n²) tag/year counting            | archives                 |         |
| 5   | Medium   | Unused `ycount` variable           | archives:31              |         |
| 6   | Medium   | Note on 404 as TEMPLATE_PAGES      | —                        |         |
| 7   | Low      | Duplicate category loop in nav     | nav                      |         |
| 8   | Low      | ~235 lines of inline JS            | nav, article, archives   |         |
| 9   | Low      | `<button>` used for navigation     | article                  |         |

---

## Details

### 4. O(n²) tag/year counting — `archives.html`

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

For each keyword, iterates over all articles and all their tags.
Complexity: `O(keywords × articles × tags_per_article)`.

The year counting (lines 31-37) has the same problem: it iterates over all articles for each year, when `groupby` would do it in one pass.

**Fix:** Use Jinja2 `groupby` and `selectattr` filters:

```jinja
{% for year, year_articles in sorted_articles | groupby(attribute='date.year') %}
  <button ...>{{ year }} <span class="count">({{ year_articles | length }})</span></button>
{% endfor %}
```

For tags, build the count in a single pass inside the plugin.

---

### 5. Unused `ycount` variable — `archives.html:31`

```jinja
{% set ycount = sorted_articles | selectattr('date', 'defined') | selectattr('date', 'ne', none) | list %}
```

This variable is computed but never used — the actual counting is done by the subsequent loop with `ycount_val.n`. Dead code.

---

### 6. `404.html` used as TEMPLATE_PAGES — note

In `pelicanconf.py:56`, `'404.html': '404.html'` is in `TEMPLATE_PAGES`, meaning Pelican renders it as a standalone template with context access. It works with `extends`, but worth noting this page is generated as a template page, not as an article — which is correct. No issue here, just a note.

---

### 7. Duplicate category loop — `nav.html`

`nav.html:9-13` and `nav.html:19-23` contain the exact same loop to generate category links (inline version and dropdown version). The duplication is acceptable given the context (different HTML), but could be extracted into a macro.

---

### 8. Inline `<script>` in nav.html and article.html

- ~90 lines of JS in `nav.html:30-116`
- ~30 lines in `article.html:95-125`
- ~115 lines in `archives.html:119-234`
- **Total: ~235 lines of inline JS**

No browser caching benefit (reloaded on every page) and makes templates harder to read. Consider moving to separate `.js` files in `assets/`.

---

### 9. `<button>` tags used for navigation — `article.html`

In `article.html:91-92`:

```html
<button class="article-nav-link" id="back-link">← Back to articles</button>
<button class="article-nav-link" id="top-link">↑ Top</button>
```

"Back to articles" navigates via `history.back()` or `window.location.href` — semantically it's a link, not an action. For accessibility, `<a>` with `role="link"` would be more appropriate, or use `<a href>` with a JS fallback.
