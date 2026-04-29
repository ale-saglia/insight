import yaml


def parse_frontmatter(raw: str, on_error=None) -> tuple[dict, str]:
    """Parse YAML frontmatter. Returns (meta, body). Calls on_error(exc) if YAML is malformed."""
    if not (raw.startswith('---\n') or raw.startswith('---\r\n')):
        return {}, raw

    end = raw.find('\n---\n', 4)
    if end == -1:
        end = raw.find('\n---\r\n', 4)
    if end == -1:
        return {}, raw

    skip = 5 if raw[end + 4:end + 5] == '\n' else 6
    body = raw[end + skip:].lstrip('\n')

    try:
        meta = yaml.safe_load(raw[4:end]) or {}
    except yaml.YAMLError as exc:
        if on_error:
            on_error(exc)
        return {}, body

    return meta, body


def split_body(raw: str) -> str:
    """Return only the body of a frontmatter document, without parsing YAML."""
    if not (raw.startswith('---\n') or raw.startswith('---\r\n')):
        return raw
    end = raw.find('\n---\n', 4)
    if end == -1:
        end = raw.find('\n---\r\n', 4)
    if end == -1:
        return raw
    skip = 5 if raw[end + 4:end + 5] == '\n' else 6
    return raw[end + skip:].lstrip('\n')
