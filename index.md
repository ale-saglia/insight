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
        <p class="featured-article-meta">{{ latest_article.created | date: "%d %b %Y" }}{% if latest_article.category != 'general' %} · <span class="featured-article-category">{{ latest_article.category }}</span>{% endif %}</p>
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
          <span class="article-meta">{{ page.created | date: "%d %b %Y" }}{% if page.category != 'general' %} · <a href="{{ '/' | append: page.category | relative_url }}">{{ page.category }}</a>{% endif %}</span>
          {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
  </section>
</div>



