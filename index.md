---
layout: default
title: Home
---

This site is a curated collection of occasional insights.
It is designed for depth, not publishing cadence.
Articles are published when there is a meaningful point to make.
The repository is the source of truth; GitHub Pages is the clean presentation layer.

## Latest Articles {#articles}

<ul class="article-list">
  {% for page in site.pages %}
    {% if page.category and page.date %}
      <li>
        <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
        - {{ page.date | date: "%d %b %Y" }}
        {% if page.category != 'general' %}<strong>[{{ page.category }}]</strong>{% endif %}
      </li>
    {% endif %}
  {% endfor %}
</ul>

**Categories:**

- [Digital Health](/digital-health/) — Insights on the intersection of artificial intelligence and healthcare systems.
- [Homelab](/homelab/) — Building and operating small-scale infrastructure teaches lifecycle responsibility and real-world trade-offs.



