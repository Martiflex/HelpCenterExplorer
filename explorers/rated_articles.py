# -*- coding: utf-8 -*-
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# std lib

# 3p

# project
from explorer import *



articles = Exploration.get_all_articles(HelpCenter)

print "\nnotation (X,Y) means X people out of Y found it useful\n"
noted_articles = [art for art in articles if art['notation'][0]]
for art in noted_articles:
    pprint.pprint(art)
