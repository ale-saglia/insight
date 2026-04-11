#!/bin/bash
# Update 'modified:' field in all markdown files from git history
# Usage: ./scripts/update-modified-dates.sh

find src/ -name "*.md" -type f | while read file; do
  # Get last commit date for this file in YYYY-MM-DD format
  last_modified=$(git log -1 --format=%ai -- "$file" 2>/dev/null | cut -d' ' -f1)
  
  if [ -n "$last_modified" ]; then
    if grep -q "^modified:" "$file"; then
      # Replace existing modified: line
      if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed requires -i ''
        sed -i '' "s/^modified:.*$/modified: $last_modified/" "$file"
      else
        # Linux sed
        sed -i "s/^modified:.*$/modified: $last_modified/" "$file"
      fi
    else
      # Add modified: after created: line if it doesn't exist
      if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "/^created:.*$/a \\
modified: $last_modified" "$file"
      else
        sed -i "/^created:.*$/a modified: $last_modified" "$file"
      fi
    fi
    echo "Updated: $file -> $last_modified"
  fi
done

echo "Done!"
