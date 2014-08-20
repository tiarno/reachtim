Title: Pelican Configuration for ReachTim.com
Category: Python
Date: 2014-Aug-20
Tags: python, web
Summary: How this site is set up

You are reading an article on a static blog site that is built with the 
Pelican static site generator. 

This article describes how the blog site is configured. 

[TOC]

You can get all the code in my GitHub project [reachtim](https://github.com/tiarno/reachtim). I use snippets of that code in this article.

I looked at several static site generators; Pelican seemed to fit my brain the best and it has a great and active community.

The documentation was another reason--the sites [Pelican Blog](http://blog.getpelican.com/) and [Pelican Docs](http://docs.getpelican.com/en/3.4.0/) were indispensible, not to mention the various blog sites that describe how they were setup. 

### The Goal {: .article-title}

I wanted a simple blog with no more machinery involved than I actually would use. I seem to lean toward [yagni](http://en.wikipedia.org/wiki/You_aren't_gonna_need_it); I like having only 'just enough' machinery to get the job done.

So a statically generated site seemed to be the right thing--I don't need a database for users or ecommerce and the site has limited interactivity.

I wanted a blog that supports the following for authoring and administration:

* Simple to use (for me to add content)
* Markdown + LaTeX math rendering 
* Code highlighting
* Automatic analytics

Of course the reading experience is just as important, and to support that end of things I wanted:    

* Simple to navigate (for readers)
* Feed subscriptions
* Commenting capability


### The Directory Structure {: .article-title}

I wasn't sure how much customization I would want to do, so I downloaded the plugin and theme zip files from [getpelican/pelican-plugins](https://github.com/getpelican/pelican-plugins) and [getpelican/pelican-themes](https://github.com/getpelican/pelican-themes). That turned out to be a good idea. The directory structure looks like this:

    projects/
        plugins/
        themes/
        reachtim/
            content/
                articles/
                images/
                pages/
                extra/

With this structure, if I want a new blog site, I can create a new directory in `projects` and set the new pelican root directory there. In the configuration file, I can then make local calls to the theme and plugins I want. 

To add content, I write in MarkDown (`*.md`) or RestructuredText (`*.rst`); if the content is a post, it goes in the `articles` directory. If it is some other type of content, like the `about` page, it goes in the `pages` directory.

For images or other special files, I add them to the `images` or `extra` directory and they are copied straight through to the static site.

### The Configuration File {: .article-title}

In the `pelicanconf.py` file, I first set up the basics. Well I actually used `pelican-quickstart` to get the initial file, but afterwards I went through it line by line, to make sure it was exactly what I wanted and to make sure I understood what was going on.

```python
AUTHOR = u'Tim Arnold'
SITENAME = u'ReachTim'
SITESUBTITLE = 'Python, LaTeX, and XML: coding together.'
SITEURL = 'http://reachtim.com'
TIMEZONE = 'America/New_York'
DEFAULT_LANG = u'en'
PATH = 'content'
```

Then I made a few changes so I can have the articles in their own subdirectory (`ARTICLE_PATHS`) and set the static paths (the directories and files that are copied over verbatim). So the `images` and `extra` directories are copied over with no other processing. The files listed in `EXTRA_PATH_METADATA` are copied to the root of the `OUTPUT_PATH` directory. 

I'm setting the output directory to be same name as the website, `reachtim`; it's my personal preference and fits my deployment scheme. The default name is `output`.

```python
OUTPUT_PATH = 'reachtim/'
ARTICLE_PATHS = ['articles',]
STATIC_PATHS = ['images', 'extra',]
    
EXTRA_PATH_METADATA = {
    'extra/404.html': {'path': '404.html'},
    'extra/403.html': {'path': '403.html'},
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/.htaccess': {'path':  '.htaccess'},
    'extra/crossdomain.xml': {'path':  'crossdomain.xml'},
    'extra/favicon.ico': {'path':  'favicon.ico'},
}
```

It was easy to change the theme or set of plugins since I had all of them in a local directory. I only have to change these lines to try a different theme or add/delete a plugin. 

```python
THEME = '../themes/zurb-F5-basic'
PLUGIN_PATHS=['../plugins',]
PLUGINS = [
    'neighbors',
    'pelican_fontawesome',
    'pelican_gist',
    'render_math',
    'sitemap',
    ]
```

I played around with a lot of themes before deciding on the `zurb-F5-basic`. I like the way it looks and operates. Other than this site, you can see another example here, from the github page: [zurb-F5-basic](https://github.com/getpelican/pelican-themes/tree/master/zurb-F5-basic)

The plugins:

* `neighbors` adds `prev_article` and `next_article` variables to the article context, so you can use them in your template.
* `pelican_fontawesome` enables you to embed FontAwesome icons in your content. This plugin was not in the getpelican plugins project, so I installed it separately from [pelican-fontawesome](https://github.com/kura/pelican-fontawesome)
* `pelican_gist` makes it easy to embed entire GitHub gists into your content.
* `render_math` enables the rendering of LaTeX style math by using the MathJax javascript engine.
* `sitemap` automatically generates your sitemap which helps search engines know about all of your pages.

The `sitemap` plugin needs a little more data:
```python
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
```

I also set things up so I have Atom feeds, Disqus commenting capability, and Google Analytics. I manually added the Google Analytics code after I registered the site with Google. Of course you need a Google account for that, and a Disqus account for commenting capability.

```python
DISQUS_SITENAME = 'reachtim'
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
```


Finally, I added these two settings to have a more attractive look. The `TYPOGRAPHY` setting provides a few changes to the typesetting by using the [Typogrify](https://code.google.com/p/typogrify/) library. 

There are a lot of choices for `MD_EXTENSIONS` and you can read about them in their [documentation](http://pythonhosted.org/Markdown/extensions/). 

```python
TYPOGRIFY = True
MD_EXTENSIONS= [
    'codehilite(css_class=highlight)',
    'extra',
    'toc',
    ]
```


### Writing Content {: .article-title}

You can write using MarkDown or RestructuredText, and each page or article you write will have some metadata at the top of the file. This article has MarkDown metadata:

    Title: Pelican Configuration for ReachTim.com
    Category: Python
    Date: 2014-Aug-20
    Tags: python, web
    Summary: How this site is set up

You can add other metadata to an article--whatever you add will be available to your template in the article's context.

The content follows the metadata after a blank line and it uses normal MarkDown syntax.

