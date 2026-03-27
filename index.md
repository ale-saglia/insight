---
layout: default
title: Home
---

This site collects occasional notes on technical and strategic topics.
Most entries focus on AI, governance, and infrastructure systems.
Articles are published when ideas have been worked through and written clearly.
The repository is the source of truth; GitHub Pages is the presentation layer.

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

<ul class="category-list">
  {% assign category_pages = site.pages | where: 'layout', 'category' | where_exp: 'p', "p.path contains 'src/'" | where_exp: 'p', "p.category != 'general'" | sort: 'title' %}
  {% for category_page in category_pages %}
    <li>
      <a href="{{ category_page.url | relative_url }}">{{ category_page.title }}</a>
      {% if category_page.summary %}— {{ category_page.summary }}{% endif %}
    </li>
  {% endfor %}
</ul>



