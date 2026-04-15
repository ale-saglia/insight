---
layout: default
title: Home
---

This site collects occasional notes on technical and strategic topics. Most entries focus on AI, governance, and infrastructure systems. Articles are published when ideas have been worked through and written clearly.

<div class="home-latest">
  <section class="home-section">
    <p class="section-label">Latest Articles</p>
    <ul class="article-list">
      {% assign sorted_articles = site.pages | where_exp: 'p', 'p.category' | where_exp: 'p', 'p.created' | sort: 'created' | reverse %}
      {% for page in sorted_articles limit: 5 %}
        <li>
          <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
          <span class="article-meta">{{ page.created | date: "%d %b %Y" }}{% if page.category != 'general' %} · <a href="{{ '/' | append: page.category | relative_url }}">{{ page.category }}</a>{% endif %}</span>
          {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
  </section>
</div>



