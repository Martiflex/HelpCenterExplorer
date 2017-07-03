# -*- coding: utf-8 -*-

# std lib
import time, os, sys, pickle
import pprint
import logging

# 3p
from datadog import statsd

# project
from configuration import *
import crawler


log = logging.getLogger(__name__)


def load_HelpCenter(filename):
    if not os.path.exists(filename):
        print "No local HC. Launching a new crawl."
        crawler.crawl(filename)

    with open(filename, 'rb') as f:
        with SimpleStatsdTimer(METRIC_NAMES['PICKLE_LOAD']):
            print "Loading HC representation from local file copy."
            HelpCenter = pickle.load(f)
            print "HC representation successfully loaded and ready to use."
    return(HelpCenter)

HelpCenter = load_HelpCenter(HC_FILEPATH)


class Exploration(object):
    """A simple Namespace collecting functions gathering data from a HC subtree"""

    # Usage:
    # articles = Exploration.get_all_articles(HelpCenter)

    # Functions applied on nodes
    @staticmethod
    def _add_hierarchy(node):
        node.node_res = reduce((lambda x, y: x + y), node.children_res)
        for data in node.node_res:
            data[node.__class__.__name__] = node.__dict__.get('title', None)

    # Functions applied on leaves
    @staticmethod
    def _list_articles(leaf):
        data = {
                        'title': leaf.__dict__.get('title', None),
                        'author': leaf.__dict__.get('author', None),
                        'date': leaf.__dict__.get('date', None),
                        'notation': leaf.__dict__.get('notation', None),
                        'url': leaf.__dict__.get('url',None),
                        'class': unicode(leaf.__class__.__name__) #should be 'Article'
                    }
        return([data]) # should be a list

    @staticmethod
    def _get_changes(leaf): # in case a section gets all its articles removed
        data = [{
                        'url': url,
                        'class': unicode(CHILD_CLASS[leaf.__class__.__name__]),
                        'change': unicode('creation')
                    }
                for url in leaf.__dict__.get('new_child_urls', [])
                ]

        data += [{
                        'url': url,
                        'class': unicode(CHILD_CLASS[leaf.__class__.__name__]),
                        'change': unicode('deletion')
                    }
                for url in leaf.__dict__.get('deleted_child_urls', [])
                ]
        return(data)

    # public functions
    @staticmethod
    def get_all_articles(node):
        return(node.apply_function_on_subtree(
            Exploration._list_articles, Exploration._add_hierarchy, False)
        )

    @staticmethod
    def get_subtree_changes(node):
        def apply_then_hierarchy(some_node):
            some_node.children_res.append(Exploration._get_changes(some_node))
            Exploration._add_hierarchy(some_node)

        return(node.apply_function_on_subtree(
            Exploration._get_changes, apply_then_hierarchy, False)
        )

if __name__ == "__main__":
    print HelpCenter
    print "PDB mode activated so that you can explore the object 'HelpCenter'"
    import pdb; pdb.set_trace()
