SITENAME = 'Insight Notes'
SITESUBTITLE = 'Exploring the invisible architectures where code meets regulation.'
SITEURL = ''
AUTHOR = 'Alessandro Saglia'
AUTHOR_URL = 'https://ale-saglia.com'

PATH = '.'
ARTICLE_PATHS = ['src']
ARTICLE_EXCLUDES = ['README.md', '*README.md']
IGNORE_FILES = ['README.md', '.#*']
PAGE_PATHS = []

TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%d %b %Y'

THEME = 'themes/insight'
PLUGIN_PATHS = ['plugins']
PLUGINS = ['insight_register', 'og_images']

OUTPUT_PATH = '_site'

FEED_DOMAIN = SITEURL
FEED_ATOM = 'feed.xml'
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TAG_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
TRANSLATION_FEED_ATOM = None

ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
CATEGORY_SAVE_AS = ''
CATEGORY_URL = ''
TAG_SAVE_AS = ''
TAG_URL = ''
AUTHOR_SAVE_AS = ''
AUTHOR_URL_FORMAT = ''
AUTHORS_SAVE_AS = ''
TAGS_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
ARCHIVES_SAVE_AS = 'archive/index.html'
INDEX_SAVE_AS = 'index.html'

RELATIVE_URLS = True

STATIC_PATHS = ['assets', 'robots.txt']
EXTRA_PATH_METADATA = {
    'robots.txt': {'path': 'robots.txt'},
}

TEMPLATE_PAGES = {
    'sitemap.xml': 'sitemap.xml',
    '404.html': '404.html',
}

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.fenced_code': {},
        'markdown.extensions.tables': {},
    },
    'output_format': 'html5',
}

DEFAULT_PAGINATION = False
