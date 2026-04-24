require 'open3'
require 'date'

Jekyll::Hooks.register :pages, :post_init do |page|
  parts = page.relative_path.split('/')
  next unless parts[0] == 'src' && parts.length >= 3

  category = parts[1].sub(/^_/, '')
  page.data['category'] = category

  is_readme = parts.last == 'README.md'
  page.data['top_level'] = true if is_readme && parts.length == 3

  if is_readme
    segments = parts[1..-2].map { |p| p.sub(/^_/, '') }
    page.data['permalink'] = '/' + segments.join('/') + '/'
  elsif page.data['article_id']
    article_id = page.data['article_id']
    segments = parts[1..-2].map { |p| p.sub(/^_/, '') }
    page.data['permalink'] = '/' + segments.join('/') + '/' + article_id + '/'
  end

  unless is_readme
    begin
      stdout, _, status = Open3.capture3('git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d', '--', page.relative_path)
      git_date = stdout.strip
      page.data['modified'] = Date.parse(git_date) if status.success? && !git_date.empty?
    rescue StandardError
      # git unavailable or failed — modified left unset
    end
  end
end
