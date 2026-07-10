# Editorial taxonomy

Article tags describe governance questions, not products or technologies. The authoritative registry is `config/editorial-taxonomy.yml`.

## Rules

- Use no more than three tags per article.
- Use the exact lowercase spelling from the registry.
- Prefer tags that connect multiple articles and express the governance lens of the argument.
- Keep technologies, products, standards, and case-specific terms in titles, excerpts, and article text.

## Adding a tag

Add the new tag and a concise definition to `config/editorial-taxonomy.yml`, then use it in article frontmatter. The registry is intentionally editable: validation prevents accidental taxonomy drift, not deliberate editorial evolution.

Run `make build` to validate every article after changing the registry.
