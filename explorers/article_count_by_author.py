# -*- coding: utf-8 -*-
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# std lib
import pprint

# 3p
from datadog import statsd

# project
from explorer import *


metric_names = {
    'ARTICLES': 'hc.articles'
}


articles = Exploration.get_all_articles(HelpCenter)


statsd.gauge(metric_names['ARTICLES'] + '.total', len(articles))


authors, author_count = [], []
for art in articles:
    if art["author"] in authors:
        author_count[authors.index(art["author"])] += 1
    else:
        authors.append(art["author"])
        author_count.append(1)

for i in range(len(authors)):
    statsd.gauge(metric_names['ARTICLES'], author_count[i], tags=['author:%s' %authors[i]])

print '%s public articles in the Help Center' %len(articles)
print '\n\nAuthor, #articles, perc of the total:'
pprint.pprint([ [authors[i], author_count[i], '%.1f' %(
    100.0 * author_count[i] / len(articles))  ] for i in range(len(authors)) ])
