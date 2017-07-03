# -*- coding: utf-8 -*-
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# std lib

# 3p

# project
from explorer import *
import crawler

# HelpCenter == data from previous crawl
# HelpCenter2 will be data from the new crawl

new_filename = HC_FILEPATH + "2" # HC.Pickle2

print "Crawling the HC to compute the diff."
print "New crawl will be available as 'HelpCenter2', saved in %s" %new_filename

crawler.crawl(new_filename)
HelpCenter2 = load_HelpCenter(new_filename)




articles = Exploration.get_all_articles(HelpCenter2)
articles_old = Exploration.get_all_articles(HelpCenter)

article_old_urls = [article['url'] for article in articles_old]

new_articles = [art for art in articles if art["url"] not in article_old_urls]

if len(new_articles) == 0:
    print "############# No new articles since last crawl #############"
else:
    print "%s new articles published:\n" %len(new_articles)
    pprint.pprint(new_articles)

    def send_event(article):
        EVENT_TITLE = 'New public KB article!'
        EVENT_TEXT = 'A new article has been added to "%s". \
Check it out here: %s.'
        location = "%s > %s" %(article['Category'],article['Section'])
        statsd.event(EVENT_TITLE, EVENT_TEXT %(location, article['url']))

    for art in new_articles:
        send_event()
