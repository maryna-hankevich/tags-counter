#!/usr/bin/env python

from distutils.core import setup

setup(
    name='tags_counter',
    version='0.1',
    description='Get tags number by url',
    author='Maryna Hankevich',
    author_email='maryna.hankevich@gmail.com',
    url='https://github.com/maryna-hankevich/tags-counter',
    py_modules=['PyYAML', 'requests', 'BeautifulSoup4', 'peewee', 'click', 'tk', 'logging', 'json', 'datetime',
                'tldextract', 'collections'],
    license="MIT License",
)
