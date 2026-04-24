#!/usr/bin/env bash
set -euo pipefail

# Ensure required front matter fields exist on article markdown files.
# Rules:
# - Never overwrite existing keys.
# - layout defaults to "article".
# - title from first H1; fallback to filename (with warning).
# - created from first commit date (file add commit).
# - category from parent folder name.
# - permalink from /category/slug/ where slug is filename without .md.
# - keywords and excerpt trigger warnings when missing.

git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: Not a git repository"
  exit 1
}

warn_count=0
updated_count=0
TMPFILES=()

cleanup_tmpfiles() {
  if ((${#TMPFILES[@]})); then
    rm -f "${TMPFILES[@]}"
  fi
}

trap cleanup_tmpfiles EXIT

warn() {
  local file="$1"
  local msg="$2"
  warn_count=$((warn_count + 1))

  if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
    echo "::warning file=${file}::${msg}" >&2
  else
    echo "WARNING: ${file}: ${msg}" >&2
  fi
}

escape_double_quotes() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

extract_h1() {
  local file="$1"
  awk '
    NR==1 && $0=="---" { in_fm=1; next }
    in_fm && $0=="---" { in_fm=0; next }
    in_fm { next }
    $0 ~ /^# / {
      sub(/^# /, "")
      print
      exit
    }
  ' "$file"
}

first_commit_date() {
  local file="$1"
  git log --follow --diff-filter=A --format=%ad --date=format:%Y-%m-%d -- "$file" | tail -n 1
}

has_valid_front_matter() {
  local file="$1"

  if [[ "$(sed -n '1p' "$file")" != "---" ]]; then
    return 1
  fi

  awk 'NR > 1 && $0 == "---" { found=1; exit } END { exit(found ? 0 : 1) }' "$file"
}

extract_front_matter_block() {
  local file="$1"
  awk '
    NR==1 && $0=="---" { in_fm=1; next }
    in_fm && $0=="---" { exit }
    in_fm { print }
  ' "$file"
}

front_matter_end_line() {
  local file="$1"
  awk 'NR > 1 && $0 == "---" { print NR; exit }' "$file"
}

has_key() {
  local key="$1"
  local fm_block="$2"
  printf '%s\n' "$fm_block" | grep -Eq "^${key}:[[:space:]]*"
}

extract_front_matter_scalar() {
  local key="$1"
  local fm_block="$2"

  printf '%s\n' "$fm_block" | awk -v key="$key" '
    $0 ~ "^" key ":[[:space:]]*" {
      line = $0
      sub("^" key ":[[:space:]]*", "", line)
      print line
      exit
    }
  '
}

collect_custom_front_matter_lines() {
  local fm_block="$1"

  printf '%s\n' "$fm_block" | awk '
    !/^(layout|title|created|modified|keywords|excerpt):[[:space:]]*/ {
      if ($0 !~ /^[[:space:]]*$/) print
    }
  '
}

build_front_matter_block() {
  local fm_block="$1"
  local fallback_title="$2"
  local fallback_created="$3"
  local layout_value title_value created_value modified_value keywords_value excerpt_value custom_lines

  layout_value="$(extract_front_matter_scalar layout "$fm_block")"
  [[ -z "$layout_value" ]] && layout_value="article"

  title_value="$(extract_front_matter_scalar title "$fm_block")"
  [[ -z "$title_value" ]] && title_value="$fallback_title"

  created_value="$(extract_front_matter_scalar created "$fm_block")"
  [[ -z "$created_value" ]] && created_value="$fallback_created"

  modified_value="$(extract_front_matter_scalar modified "$fm_block")"

  keywords_value="$(extract_front_matter_scalar keywords "$fm_block")"
  excerpt_value="$(extract_front_matter_scalar excerpt "$fm_block")"
  [[ -z "$excerpt_value" ]] && excerpt_value='""'

  custom_lines="$(collect_custom_front_matter_lines "$fm_block")"

  {
    echo "---"
    printf 'layout: %s\n' "$layout_value"
    printf 'title: %s\n' "$title_value"
    printf 'created: %s\n' "$created_value"
    if [[ -n "$modified_value" ]]; then
      printf 'modified: %s\n' "$modified_value"
    fi
    if [[ -n "$keywords_value" ]]; then
      printf 'keywords: %s\n' "$keywords_value"
    else
      printf 'keywords: \n'
    fi
    printf 'excerpt: %s\n' "$excerpt_value"
    if [[ -n "$custom_lines" ]]; then
      printf '%s\n' "$custom_lines"
    fi
    echo "---"
  }
}

file_has_trailing_newline() {
  local file="$1"
  local last_hex

  [[ -s "$file" ]] || return 1
  last_hex="$(tail -c 1 "$file" | od -An -t x1 | tr -d '[:space:]')"
  [[ "$last_hex" == "0a" ]]
}

preserve_eof_newline_style() {
  local original_file="$1"
  local rewritten_file="$2"

  if ! file_has_trailing_newline "$original_file"; then
    perl -0777 -i -pe 's/\n\z//' "$rewritten_file"
  fi
}

extract_title_from_fm_block() {
  local fm_block="$1"
  local raw_title

  raw_title="$(printf '%s\n' "$fm_block" | awk '
    /^title:[[:space:]]*/ {
      line = $0
      sub(/^title:[[:space:]]*/, "", line)
      if (line ~ /^".*"[[:space:]]*$/) {
        sub(/^"/, "", line)
        sub(/"[[:space:]]*$/, "", line)
      }
      print line
      exit
    }
  ')"
  printf '%s' "$raw_title"
}

normalize_body() {
  local file="$1"
  local start_line="$2"
  local strip_h1="$3"
  local title_for_h1="$4"

  tail -n "+${start_line}" "$file" | awk -v strip_h1="$strip_h1" -v title="$title_for_h1" '
    BEGIN {
      started = 0
      h1_removed = 0
      pending_blank_count = 0
    }

    function flush_pending_blanks() {
      for (i = 1; i <= pending_blank_count; i++) {
        print pending_blank_lines[i]
      }
      pending_blank_count = 0
    }

    {
      line = $0

      # Remove empty lines immediately after front matter.
      if (!started && line ~ /^[[:space:]]*$/) {
        next
      }
      started = 1

      # Remove first H1 only when it duplicates the front matter title.
      if (strip_h1 == "1" && !h1_removed && line ~ /^# /) {
        h1 = line
        sub(/^# /, "", h1)
        if (h1 == title) {
          h1_removed = 1
          next
        }
      }

      if (line ~ /^[[:space:]]*$/) {
        # Buffer blank lines; they are flushed only if followed by content,
        # so trailing blank lines at EOF are dropped.
        pending_blank_count++
        pending_blank_lines[pending_blank_count] = line
        next
      }

      flush_pending_blanks()
      print line
    }

    END {
      # Do not flush pending blank lines: this trims blank lines at EOF.
    }
  '
}

while read -r file; do
  slug="$(basename "$file" .md)"
  category="$(basename "$(dirname "$file")")"
  # Top-level domain folder under src/ (handles nested paths like src/domain/sub/file.md)
  top_domain="$(echo "$file" | cut -d'/' -f2)"

  created_cache=""
  resolve_created() {
    if [[ -n "$created_cache" ]]; then
      printf '%s' "$created_cache"
      return
    fi

    created_cache="$(first_commit_date "$file")"
    if [[ -z "$created_cache" ]]; then
      created_cache="$(date +%F)"
      warn "$file" "created not found in git history: using current date ${created_cache}"
    fi

    printf '%s' "$created_cache"
  }

  h1_title="$(extract_h1 "$file")"

  if ! has_valid_front_matter "$file"; then
    strip_h1="0"
    if [[ -n "$h1_title" ]]; then
      title_value="$h1_title"
      strip_h1="1"
    else
      title_value="$slug"
      warn "$file" "title not found (missing H1): using filename fallback"
    fi

    warn "$file" "keywords missing: inserted empty placeholder"
    warn "$file" "excerpt missing: inserted empty placeholder"

    escaped_title="$(escape_double_quotes "$title_value")"
    created="$(resolve_created)"
    tmp_file="$(mktemp)"
    TMPFILES+=("$tmp_file")
    processed_body_tmp="$(mktemp)"
    TMPFILES+=("$processed_body_tmp")
    front_matter_tmp="$(mktemp)"
    TMPFILES+=("$front_matter_tmp")

    normalize_body "$file" 1 "$strip_h1" "$title_value" > "$processed_body_tmp"
    build_front_matter_block "" "\"${escaped_title}\"" "$created" > "$front_matter_tmp"

    {
      cat "$front_matter_tmp"
      echo
      cat "$processed_body_tmp"
    } > "$tmp_file"

    preserve_eof_newline_style "$file" "$tmp_file"

    mv "$tmp_file" "$file"
    rm -f "$processed_body_tmp" "$front_matter_tmp"
    updated_count=$((updated_count + 1))
    continue
  fi

  fm_block="$(extract_front_matter_block "$file")"
  end_line="$(front_matter_end_line "$file")"

  # Validate category/permalink coherence with folder structure
  if has_key "category" "$fm_block"; then
    fm_category="$(extract_front_matter_scalar category "$fm_block")"
    if [[ "$fm_category" != "$category" && "$fm_category" != "$top_domain" ]]; then
      warn "$file" "category mismatch: frontmatter has '${fm_category}', expected '${top_domain}' (or subcategory '${category}')"
    fi
  fi
  if has_key "permalink" "$fm_block"; then
    fm_permalink="$(extract_front_matter_scalar permalink "$fm_block")"
    expected_prefix="/${top_domain}/"
    if [[ "$fm_permalink" != "${expected_prefix}"* ]]; then
      warn "$file" "permalink mismatch: '${fm_permalink}' does not start with '${expected_prefix}'"
    fi
  fi

  missing_lines=()
  missing_count=0
  title_added_from_h1="0"
  title_value=""

  if ! has_key "layout" "$fm_block"; then
    missing_lines+=("layout: article")
    missing_count=$((missing_count + 1))
  fi

  if ! has_key "title" "$fm_block"; then
    if [[ -n "$h1_title" ]]; then
      title_value="$h1_title"
      title_added_from_h1="1"
    else
      title_value="$slug"
      warn "$file" "title not found (missing H1): using filename fallback"
    fi
    escaped_title="$(escape_double_quotes "$title_value")"
    missing_lines+=("title: \"${escaped_title}\"")
    missing_count=$((missing_count + 1))
  fi

  if ! has_key "created" "$fm_block"; then
    created="$(resolve_created)"
    missing_lines+=("created: ${created}")
    missing_count=$((missing_count + 1))
  fi

  if ! has_key "keywords" "$fm_block"; then
    missing_lines+=("keywords: ")
    missing_count=$((missing_count + 1))
    warn "$file" "keywords missing: inserted empty placeholder"
  fi

  if ! has_key "excerpt" "$fm_block"; then
    missing_lines+=("excerpt: \"\"")
    missing_count=$((missing_count + 1))
    warn "$file" "excerpt missing: inserted empty placeholder"
  fi

  strip_h1="0"
  title_for_body="$(extract_title_from_fm_block "$fm_block")"
  if [[ "$title_added_from_h1" == "1" ]]; then
    strip_h1="1"
    title_for_body="$title_value"
  elif [[ -n "$title_for_body" ]]; then
    strip_h1="1"
  fi

  current_body_tmp="$(mktemp)"
  TMPFILES+=("$current_body_tmp")
  processed_body_tmp="$(mktemp)"
  TMPFILES+=("$processed_body_tmp")
  tail -n "+$((end_line + 1))" "$file" > "$current_body_tmp"
  normalize_body "$file" "$((end_line + 1))" "$strip_h1" "$title_for_body" > "$processed_body_tmp"

  if [[ "$missing_count" -gt 0 ]] || ! cmp -s "$current_body_tmp" "$processed_body_tmp"; then
    tmp_file="$(mktemp)"
    TMPFILES+=("$tmp_file")
    front_matter_tmp="$(mktemp)"
    TMPFILES+=("$front_matter_tmp")

    if [[ "$title_added_from_h1" == "1" ]]; then
      rewritten_title="\"$(escape_double_quotes "$title_value")\""
    else
      rewritten_title="$(extract_front_matter_scalar title "$fm_block")"
      if [[ -z "$rewritten_title" ]]; then
        rewritten_title="\"$(escape_double_quotes "$title_value")\""
      fi
    fi

    build_front_matter_block "$fm_block" "$rewritten_title" "$(extract_front_matter_scalar created "$fm_block")" > "$front_matter_tmp"

    {
      cat "$front_matter_tmp"
      echo
      cat "$processed_body_tmp"
    } > "$tmp_file"

    preserve_eof_newline_style "$file" "$tmp_file"

    mv "$tmp_file" "$file"
    rm -f "$front_matter_tmp"
    updated_count=$((updated_count + 1))
  fi

  rm -f "$current_body_tmp" "$processed_body_tmp"
done < <(find src -name "*.md" -type f ! -name "README.md")

echo "Front matter check completed. Updated files: ${updated_count}. Warnings: ${warn_count}."
