# -*- coding: utf-8 -*-

# std lib
import logging
import pickle

# 3p
from bs4 import BeautifulSoup
import requests

# project
from configuration import *

log = logging.getLogger(__name__)

SITE = SITE           # "https://help.datadoghq.com"
HOME_PAGE = HOME_PAGE # "https://help.datadoghq.com/hc/en-us"

CHILD_CLASS = {
    'HelpCenterElement': None,
    'HomePage': 'Category',
    'Category': 'Section',
    'Section': 'Article',
    'Article': None
}

INDENTATION = {
    'HelpCenterElement': '',
    'HomePage': '',
    'Category': '    ',
    'Section': '        ',
    'Article': '            '
}

class HelpCenterElement(object):
    """Represents a KB folder or Article"""

    def __init__(self, url, parent=None):
        self.url = url
        self.soup = None

        # Data crawled from the page
        self.title = None
        self.children_urls = None # urls crawled from the current HelpCenterElement page

        # Tree
        self.parent = parent
        self.children = None # list of direct child objects

    def crawl(self):
        """Actions to perform on this HelpCenterElement and all its descendance."""
        log.debug("Crawling %s" %self.url)
        self._requests_soup()
        self._set_metadata()
        log.debug("Title found: %s" %self.title)

        self.children_urls = self._get_children_urls()

        if self.children_urls and self._should_update_children():
            self.children = [eval(CHILD_CLASS[self.__class__.__name__])(url,self)
                            for url in self.children_urls]

        if self.children and self._should_crawl_children():
            for child in self.children:
                child.crawl()

    def _requests_soup(self):
        """Wrapper adding exceptions when opening a url + soup"""
        try:
            page = requests.get(self.url)
        # except ConnectionError:
        #     raise "Page doesn't exist"
        except Exception as e:
            # import pdb; pdb.set_trace()
            raise
        self.soup = BeautifulSoup(page.content, 'html.parser')

    def _set_metadata(self):
        """Captures the title of the folder"""
        # <title>Frequently Asked Questions &ndash; Datadog</title>
        # <title>Datadog</title>  # <-- for the home page
        if self.soup is None:
            self._requests_soup()
        title = self.soup.title.string

        if title == u'Datadog':
            self.title = u'Datadog'
        elif title.find(u'&ndash') >= 0:
            self.title = title[:(title.find(u'&ndash;')-1)]
        elif title.find(u'\u2013') >= 0:
            self.title = title[:(title.find(u'\u2013')-1)]
        else:
            self.title = title

    def _get_children_urls(self):
        """Captures all subfolders/articles based on a parsing function passed"""
        if self.soup is None:
            self._requests_soup()
        children_url_tags = self.soup.find_all(self._parsing_function)
        # <a href="/hc/en-us/categories/200273899-Agent">
        children_urls = [SITE + tag['href'] for tag in children_url_tags]

        # Pagination: "pagination-next" class, see the Dashboard > Graphing section. That has more than 30 articles.
        # <li class="pagination-next">
        #   <a href="/hc/en-us/sections/200763645-Graphing?page=2#articles" rel="next">›</a>
        # </li>
        pagination = self.soup.find_all(lambda tag: (tag.parent.attrs.get('class') == [u'pagination-next']) and tag.name == 'a')
        if pagination:
            next_url = SITE + pagination[0].attrs['href']
            next_page = eval(self.__class__.__name__)(next_url)
            children_urls += next_page._get_children_urls()  # recursion
        return(children_urls)

    def _should_update_children(self): #yes for everything but Articles and HelpCenterElement as it's an abstract class.
        return(CHILD_CLASS[self.__class__.__name__] is not None)

    def _should_crawl_children(self): #can be monkeypatched for tests
        return True

    @staticmethod
    def _parsing_function(tag):
        """Interface: parsing adapted to each folder level"""
        raise NotImplementedError()

    def apply_function_on_subtree(self, func_leave=None, func_node=None, before=True):
        """Go vertically through the tree.
        Apply func_leave to leaves only.
            func_leave should return a list
        Apply func_node to non-leave nodes.
            func_node shall manipulate self.node_res which'll be returned
        The before parameter controls when func_node is applied.

        """
        if not self.children and func_leave: # this is a leaf
            return(func_leave(self)) # this should be a list
        if self.children:
            self.node_res = None
            if before and func_node:
                func_node(self)
            self.children_res = [child.apply_function_on_subtree(func_leave, func_node, before)\
                    for child in self.children]
            if not before and func_node:
                func_node(self)

            res = self.node_res
            del self.__dict__['node_res']
            del self.__dict__['children_res']
            return(res)

    def apply_function_on_leaves(self,func):
        def func_node(node):
            children_res = node.children_res
            node.node_res = reduce((lambda x, y: x + y), children_res)

        return(self.apply_function_on_subtree(
            func,
            func_node,
            False))

    def apply_function_on_nodes(self, func):
        def func_node(node):
            node.node_res = func(node)

        return(self.apply_function_on_subtree(
            None,
            func_node
            ))

    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        """Prints the object class + its title"""
        # unicode problems with certain article titles!
        # u'I\u2019m loving Datadog and would like to use this at work! Who can I talk to?',
        # https://help.datadoghq.com/hc/en-us/articles/213211006-I-m-loving-Datadog-and-would-like-to-use-this-at-work-Who-can-I-talk-to-
        if self.title:
            format = INDENTATION[self.__class__.__name__] +\
                self.__class__.__name__ + ": " + (self.title)
        else:
            format = INDENTATION[self.__class__.__name__] +\
                        "NODE_NOT_SET:" + self.url.split('/')[-1]
        if self.children:
            format = format + "\n" + \
                "\n".join([child.__unicode__() for child in self.children])
        return(format)
    __repr__ = __str__




class HomePage(HelpCenterElement):
    """The homepage of the HC"""

    def __init__(self, url, parent=None):
        HelpCenterElement.__init__(self,url,parent)

    @staticmethod
    def _parsing_function(tag):
    # <section class="category">
    #         <h2><a href="/hc/en-us/categories/200273899-Agent">Agent</a></h2>
        return(
                (tag.name == 'a') and (tag.parent.name == 'h2')
                # and (tag.parent.parent.name == 'section') and (tag.parent.parent.attrs.get('class') == 'category')
        )

class Category(HelpCenterElement):
    """2nd level i.e. folders that contain sections."""

    def __init__(self, url, parent=None):
        HelpCenterElement.__init__(self,url,parent)

    @staticmethod
    def _parsing_function(tag):
     # <section class="section">
     # <h3>
     #    <a href="/hc/en-us/sections/200817785-Installation">Installation</a>
     # </h3>
        return(
                (tag.name == 'a') and (tag.parent.name == 'h3')
                # and (tag.parent.parent.name == 'section') and (tag.parent.parent.attrs.get('class') == 'section')
            )

class Section(HelpCenterElement):
    """3rd level i.e. folder that contains articles."""

    def __init__(self, url, parent=None):
        HelpCenterElement.__init__(self,url,parent)

    @staticmethod
    def _parsing_function(tag):
     # <ul class="article-list">
     #  <li >
     #    <a href="/hc/en-us/articles/214642023-How-can-students-join-the-Datadog-Student-Developer-Program-">How can students join the Datadog Student Developer Program?</a>
     #  </li>
        return(
                (tag.name == 'a') and (tag.parent.name == 'li')
                and (tag.parent.parent.name == 'ul') and (tag.parent.parent.attrs.get('class') == [u'article-list'])
            )

class Article(HelpCenterElement):
    """Represents a KB article, grabs article metadata from the html code"""

    def __init__(self, url, parent=None):
        HelpCenterElement.__init__(self,url,parent)
        # Specific metadata
        self.title = None
        self.author = None
        self.date = None
        # self.word_count = None

    def _set_metadata(self):
        """Surcharge: Captures the title, author and date of the Article."""
        # """Surcharge: Captures the title, author and date of the Article, plus the number of thumbsup/down."""
        if self.soup is None:
            self._requests_soup()
        # <title>How do I install the agent on a server with limited internet connectivity? \u2013 Datadog</title>
        title = self.soup.title.string
        self.title = title[:(title.find(u'\u2013')-1)]
        #  <strong class="article-author" title="Patrick Barker">
        self.author = self.soup.select("strong[class=article-author]")[0].attrs['title']
        # <time data-datetime="calendar" datetime="2016-12-12T19:15:20Z" title="2016-12-12T19:15:20Z">
        self.date = self.soup.select('time[data-datetime="calendar"]')[0].attrs['title']

        # body = self.soup.body.text; body = body[:body.find("Was this article helpful?")]
        # self.word_count = len(body)

        self.notation = self._get_notation() # (1,1) as 1 out of 1 found this helpful

    def _get_notation(self):
        # <span class="article-vote-label">0 out of 0 found this helpful</span>
        part = self.soup.select("span[class=article-vote-label]")[0].text
        part = part.split(' ')
        return(int(part[0]),int(part[3]))


    def _get_children_urls(self): #important: no children for articles
        return(None)


def crawl(filename):
    """ Crawls the targetted Zendesk HelpCenter and save its representation into a Pickle file"""
    # AllRequestsTimer.monkey_patch()

    with SimpleStatsdTimer(METRIC_NAMES['CRAWL_DURATION']):
        print "Crawling the HelpCenter, this may take 8+ min ..."
        HelpCenter = HomePage(HOME_PAGE)
        HelpCenter.crawl()
        print "HC successfully crawled!"

    with SimpleStatsdTimer(METRIC_NAMES['PICKLE_SAVE']):
        with open(filename, 'wb') as f:
            print "Saving crawl results locally in %s" %filename
            pickle.dump(HelpCenter,f)
            print "HC representation successfully saved in %s for future usage" %filename
    return(HelpCenter)

if __name__ == "__main__":
    crawl(HC_FILEPATH)
