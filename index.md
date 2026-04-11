---
layout: default
title: Home
---

This site collects occasional notes on technical and strategic topics. Most entries focus on AI, governance, and infrastructure systems. Articles are published when ideas have been worked through and written clearly.

<div class="home-grid">
  <section class="home-section">
    <p class="section-label">Latest Articles</p>
    <ul class="article-list">
      {% assign sorted_articles = site.pages | where_exp: 'p', 'p.category' | where_exp: 'p', 'p.date' | sort: 'date' | reverse %}
      {% assign visible_categories = site.pages | where: 'layout', 'category' | where_exp: 'p', "p.path contains 'src/'" | where_exp: 'p', "p.category != 'general'" %}
      {% assign article_limit = visible_categories | size | plus: 1 %}
      {% for page in sorted_articles limit: article_limit %}
        {% if page.category and page.date %}
          <li>
            <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
            <span class="article-meta">{{ page.date | date: "%d %b %Y" }} {% if page.category != 'general' %}· {{ page.category }}{% endif %}</span>
            {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
          </li>
        {% endif %}
      {% endfor %}
    </ul>
  </section>

  <section class="home-section">
    <p class="section-label">Categories</p>
    <ul class="category-list">
      {% assign category_pages = site.pages | where: 'layout', 'category' | where_exp: 'p', "p.path contains 'src/'" | where_exp: 'p', "p.category != 'general'" | sort: 'title' %}
      {% for category_page in category_pages %}
        <li>
          <a href="{{ category_page.url | relative_url }}">{{ category_page.title }}</a>
          {% if category_page.summary %}- {{ category_page.summary }}{% endif %}
        </li>
      {% endfor %}
    </ul>
  </section>
</div>



