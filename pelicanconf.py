#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Tim Arnold'
SITENAME = 'ReachTim'
SITEURL = 'https://reachtim.com'
PATH = 'content'
TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
STATIC_PATHS = ['images']
EXTRA_PATH_METADATA = {
    'favicon.ico': {'path': 'extra'},
    'robots.txt': {'path': 'extra'}
}
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

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True