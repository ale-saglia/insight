---
layout: default
title: Home
---

There is a threshold where engineering becomes governance and infrastructure becomes policy. It is rarely marked, often crossed without noticing. I write here to think at that boundary: the hidden mechanics of digital public systems, the friction between technical possibility and institutional reality, and the quiet decisions that shape both.

{% assign sorted_articles = site.pages | where_exp: 'p', 'p.category' | where_exp: 'p', 'p.created' | sort: 'created' | reverse %}
{% assign latest_article = sorted_articles | first %}

{% if latest_article %}
  <section class="featured-article" aria-labelledby="featured-article-title">
    <p class="section-label">Start Here</p>
    <a class="featured-article-card" href="{{ latest_article.url | relative_url }}">
      <div class="featured-article-content">
        {% assign la_parts = latest_article.path | split: "/" %}
        {% assign la_cat_url = '/' | append: latest_article.category | append: '/' %}
        {% assign la_cat_label = latest_article.category %}
        {% for p in site.pages %}
          {% if p.url == la_cat_url %}{% assign la_cat_label = p.title %}{% endif %}
        {% endfor %}
        {% assign la_display_label = la_cat_label %}
        {% assign la_display_url = la_cat_url %}
        {% if la_parts.size >= 4 %}
          {% assign la_sub_slug = la_parts[2] %}
          {% assign la_sub_url = la_cat_url | append: la_sub_slug | append: '/' %}
          {% assign la_sub_label = la_sub_slug | replace: '-', ' ' %}
          {% for p in site.pages %}
            {% if p.url == la_sub_url %}{% assign la_sub_label = p.title %}{% endif %}
          {% endfor %}
          {% assign la_display_label = la_cat_label | append: ' / ' | append: la_sub_label %}
          {% assign la_display_url = la_sub_url %}
          {% assign la_ep_fn = latest_article.path | split: "/" | last | split: "." | first %}
          {% assign la_ep_num = la_ep_fn | split: "-" | first %}
          {% assign la_ep_str = la_ep_num | plus: 0 | append: "" %}
          {% if la_ep_str == la_ep_num %}
            {% assign la_display_label = la_display_label | append: ' · Episode ' | append: la_ep_num %}
          {% endif %}
        {% endif %}
        <p class="featured-article-meta">{{ latest_article.created | date: "%d %b %Y" }}{% if latest_article.category != 'general' %} · <span class="featured-article-category">{{ la_display_label }}</span>{% endif %}</p>
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
          {% assign li_parts = page.path | split: "/" %}
          {% assign li_cat_url = '/' | append: page.category | append: '/' %}
          {% assign li_cat_label = page.category %}
          {% for cp in site.pages %}
            {% if cp.url == li_cat_url %}{% assign li_cat_label = cp.title %}{% endif %}
          {% endfor %}
          {% if li_parts.size >= 4 %}
            {% assign li_sub_slug = li_parts[2] %}
            {% assign li_sub_url = li_cat_url | append: li_sub_slug | append: '/' %}
            {% assign li_sub_label = li_sub_slug | replace: '-', ' ' %}
            {% for cp in site.pages %}
              {% if cp.url == li_sub_url %}{% assign li_sub_label = cp.title %}{% endif %}
            {% endfor %}
            {% assign li_ep_fn = page.path | split: "/" | last | split: "." | first %}
            {% assign li_ep_num = li_ep_fn | split: "-" | first %}
            {% assign li_ep_str = li_ep_num | plus: 0 | append: "" %}
          {% endif %}
          <span class="article-meta">{{ page.created | date: "%d %b %Y" }}{% if page.category != 'general' %} · <a href="{{ li_cat_url | relative_url }}">{{ li_cat_label }}</a>{% if li_parts.size >= 4 %} / <a href="{{ li_sub_url | relative_url }}">{{ li_sub_label }}</a>{% if li_ep_str == li_ep_num %} · Episode {{ li_ep_num }}{% endif %}{% endif %}{% endif %}</span>
          {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
    <p class="latest-archive-link"><a href="{{ '/archive/' | relative_url }}">Browse all articles in the archive</a></p>
  </section>
</div>



