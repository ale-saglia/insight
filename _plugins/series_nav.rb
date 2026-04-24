Jekyll::Hooks.register :site, :post_read do |site|
  series_groups = Hash.new { |h, k| h[k] = [] }

  site.pages.each do |page|
    parts = page.relative_path.split('/')
    next unless parts[0] == 'src' && parts.length >= 3
    next if parts.last == 'README.md'
    next unless parts.last.match?(/^\d+-/)

    parent_dir = parts[0..-2].join('/')
    series_groups[parent_dir] << page
  end

  series_groups.each_value do |pages|
    sorted = pages.sort_by { |p| p.relative_path.split('/').last.to_i }
    sorted.each_with_index do |page, idx|
      if idx > 0
        prev_p = sorted[idx - 1]
        page.data['prev_episode'] = {
          'url' => prev_p.data['permalink'],
          'title' => prev_p.data['title'].to_s
        }
      end
      if idx < sorted.length - 1
        next_p = sorted[idx + 1]
        page.data['next_episode'] = {
          'url' => next_p.data['permalink'],
          'title' => next_p.data['title'].to_s
        }
      end
    end
  end
end
