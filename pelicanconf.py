#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Tim Arnold'
SITENAME = 'reachtim'
SITEURL = 'https://reachtim.com'
PATH = 'content'
TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'

EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/.htaccess': {'path':  '.htaccess'},
    'extra/crossdomain.xml': {'path':  'crossdomain.xml'},
    'extra/favicon.ico': {'path':  'favicon.ico'},
}
ARTICLE_URL = 'articles/{slug}.html'
ARTICLE_SAVE_AS = 'articles/{slug}.html'
PAGE_URL = 'pages/{slug}.html'
PAGE_SAVE_AS = 'pages/{slug}.html'

THEME = '../pelican-themes/zurb-F5-basic'
PLUGIN_PATHS=['../pelican-plugins',]
PLUGINS = [
	'neighbors',
  'pelican_fontawesome',
	'pelican_render_math',
	'extended_sitemap',
	]

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

DISQUS_SITENAME = 'reachtim'
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

LINKS = (
         ('Planet Python', 'https://planet.python.org/'),
         ('CTAN', 'https://ctan.org/'),
         )
SOCIAL = (
          ('Github', 'https://github.com/tiarno'),
          ('Gists', 'https://gist.github.com/tiarno/'),
          ('LinkedIn', 'https://www.linkedin.com/in/jtimarnold'),
          ('Twitter', 'https://twitter.com/jtimarnold')
         )

TYPOGRIFY = True
MARKDOWN = {
  'extension_configs': {
    'markdown.extensions.toc': {
      'title': 'Table of contents:'
    },

    'markdown.extensions.codehilite': {'css_class': 'highlight'},
    'markdown.extensions.extra': {},
    'markdown.extensions.meta': {},
  },
  'output_format': 'html5',
}

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
