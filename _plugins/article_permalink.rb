require 'open3'
require 'date'

Jekyll::Hooks.register :pages, :post_init do |page|
  parts = page.relative_path.split('/')
  next unless parts[0] == 'src' && parts.length >= 3

  category = parts[1].sub(/^_/, '')
  page.data['category'] = category
  page.data['subcategory'] = parts[2] if parts.length >= 4

  is_readme = parts.last == 'README.md'

  if is_readme
    page.data['permalink'] =
      if parts.length == 3
        "/#{category}/"
      else
        "/#{category}/#{parts[2]}/"
      end
  elsif page.data['article_id']
    article_id = page.data['article_id']
    page.data['permalink'] =
      if parts.length >= 4
        "/#{category}/#{parts[2]}/#{article_id}/"
      else
        "/#{category}/#{article_id}/"
      end

    stdout, _, status = Open3.capture3('git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d', '--', page.relative_path)
    git_date = stdout.strip
    if status.success? && !git_date.empty?
      begin
        page.data['modified'] = Date.parse(git_date)
      rescue ArgumentError
        # leave unset
      end
    end
  end
end
