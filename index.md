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
        {% assign la_url_parts = latest_article.url | split: "/" %}
        {% assign la_crumb_url = "/" %}
        {% assign la_display_label = "" %}
        {% assign la_display_url = "/" %}
        {% for part in la_url_parts %}
          {% if forloop.index0 >= 1 %}
            {% unless forloop.last %}
              {% assign la_crumb_url = la_crumb_url | append: part | append: "/" %}
              {% assign la_part_label = part | replace: "-", " " %}
              {% for p in site.pages %}
                {% if p.url == la_crumb_url %}{% assign la_part_label = p.title %}{% endif %}
              {% endfor %}
              {% if forloop.index0 == 1 %}
                {% assign la_display_label = la_part_label %}
              {% else %}
                {% assign la_display_label = la_display_label | append: ' / ' | append: la_part_label %}
              {% endif %}
              {% assign la_display_url = la_crumb_url %}
            {% endunless %}
          {% endif %}
        {% endfor %}
        {% assign la_ep_fn = latest_article.path | split: "/" | last | split: "." | first %}
        {% assign la_ep_num = la_ep_fn | split: "-" | first %}
        {% assign la_ep_str = la_ep_num | plus: 0 | append: "" %}
        {% if la_ep_str == la_ep_num %}
          {% assign la_display_label = la_display_label | append: ' · Episode ' | append: la_ep_num %}
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
          {% assign li_url_parts = page.url | split: "/" %}
          {% assign li_crumb_url = "/" %}
          {% assign li_crumb_items = "" | split: "" %}
          {% for part in li_url_parts %}
            {% if forloop.index0 >= 1 %}
              {% unless forloop.last %}
                {% assign li_crumb_url = li_crumb_url | append: part | append: "/" %}
                {% assign li_part_label = part | replace: "-", " " %}
                {% for cp in site.pages %}
                  {% if cp.url == li_crumb_url %}{% assign li_part_label = cp.title %}{% endif %}
                {% endfor %}
                {% assign li_crumb_item = li_crumb_url | append: "|" | append: li_part_label %}
                {% assign li_crumb_items = li_crumb_items | push: li_crumb_item %}
              {% endunless %}
            {% endif %}
          {% endfor %}
          {% assign li_ep_fn = page.path | split: "/" | last | split: "." | first %}
          {% assign li_ep_num = li_ep_fn | split: "-" | first %}
          {% assign li_ep_str = li_ep_num | plus: 0 | append: "" %}
          <span class="article-meta">{{ page.created | date: "%d %b %Y" }}{% if page.category != 'general' %} · {% for item in li_crumb_items %}{% assign item_parts = item | split: "|" %}{% unless forloop.first %} / {% endunless %}<a href="{{ item_parts[0] | relative_url }}">{{ item_parts[1] }}</a>{% endfor %}{% if li_ep_str == li_ep_num %} · Episode {{ li_ep_num }}{% endif %}{% endif %}</span>
          {% if page.excerpt %}<span class="article-excerpt">{{ page.excerpt }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
    <p class="latest-archive-link"><a href="{{ '/archive/' | relative_url }}">Browse all articles in the archive</a></p>
  </section>
</div>



