---
layout: default
title: Home
---

This site collects occasional notes on technical and strategic topics. Most entries focus on AI, governance, and infrastructure systems. Articles are published when ideas have been worked through and written clearly.

{% assign sorted_articles = site.pages | where_exp: 'p', 'p.category' | where_exp: 'p', 'p.created' | sort: 'created' | reverse %}
{% assign latest_article = sorted_articles | first %}

{% if latest_article %}
  <section class="featured-article" aria-labelledby="featured-article-title">
    <p class="section-label">Start Here</p>
    <a class="featured-article-card" href="{{ latest_article.url | relative_url }}">
      <div class="featured-article-content">
        {% assign la_cat_url = '/' | append: latest_article.category | append: '/' %}
        {% assign la_cat_label = latest_article.category %}
        {% for p in site.pages %}
          {% if p.url == la_cat_url %}{% assign la_cat_label = p.title %}{% endif %}
        {% endfor %}
        <p class="featured-article-meta">{{ latest_article.created | date: "%d %b %Y" }}{% if latest_article.category != 'general' %} · <span class="featured-article-category">{{ la_cat_label }}</span>{% endif %}</p>
        <h2 id="featured-article-title">{{ latest_article.title }}</h2>
        {% if latest_article.excerpt %}<p class="featured-article-excerpt">{{ latest_article.excerpt }}</p>{% endif %}
      </div>
    </a>
  </section>
{% endif %}

<div class="home-latest">
  <section class="home-section">
    <p class="section-label">Latest Articles</p>
    <ul class="article-list">
      {% for page in sorted_articles offset: 1 limit: 5 %}
        <li>
          <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
          {% assign li_cat_url = '/' | append: page.category | append: '/' %}
          {% assign li_cat_label = page.category %}
          {% for cp in site.pages %}
            {% if cp.url == li_cat_url %}{% assign li_cat_label = cp.title %}{% endif %}
          {% endfor %}
          <span class="article-meta">{{ page.created | date: "%d %b %Y" }}{% if page.category != 'general' %} · <a href="{{ li_cat_url | relative_url }}">{{ li_cat_label }}</a>{% endif %}</span>
          {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
    <p class="latest-archive-link"><a href="{{ '/archive/' | relative_url }}">Browse all articles in the archive</a></p>
  </section>
</div>



