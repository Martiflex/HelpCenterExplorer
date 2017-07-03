# -*- coding: utf-8 -*-

# std lib
import time, os, sys, pickle
import pprint
from functools import wraps

# 3p
from datadog import statsd

# project

project_folder = os.path.dirname(os.path.realpath(__file__))
hc_filename = 'HC.Pickle'
HC_FILEPATH = os.path.join(project_folder,hc_filename)

METRIC_NAMES = {
    'CRAWL_DURATION': 'hc.crawl_duration',
    'PICKLE_LOAD': 'hc.pickle.load',
    'PICKLE_SAVE': 'hc.pickle.save',
    # 'CRAWL_DURATION': 'hc.crawl_duration',
    # 'REQUEST_HISTO': 'hc.crawl.requests',
    # 'ARTICLES': 'hc.articles',
    # 'NEW_ARTICLES': 'hc.new_articles'
}

SITE = "https://help.datadoghq.com"
HOME_PAGE = "https://help.datadoghq.com/hc/en-us"

sys.setrecursionlimit(4000) # for the pickle caching. 3000 works.

# class AllRequestsTimer(object):
#     """Monkey patching the requests function to capture a histogram"""
#     timings = []
#     @staticmethod
#     def timer_decorator(func):
#         @wraps(func)
#         def decorated(*args, **kwargs):
#             time_start = time.time()
#             res = func(*args, **kwargs)
#             AllRequestsTimer.timings.append(time.time() - time_start)
#         return decorated

#     @staticmethod
#     def monkey_patch():
#         """Apply the timing decorator to the request method of the HC base class"""
#         HelpCenterElement._requests_soup = AllRequestsTimer.timer_decorator(HelpCenterElement._requests_soup)

###     for t in AllRequestsTimer.timings:
###        statsd.histogram(METRIC_NAMES['REQUEST_HISTO'], t)

class SimpleStatsdTimer(object):
    """Context manager printing & sending duration values via statsd"""
    def __init__(self, metric_name, tags=[]):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = time.time()
    def __enter__(self):
        return self # unnecessary
    def __exit__(self, type, value, traceback):
        time_elapsed = time.time() - self.start_time
        statsd.gauge(self.metric_name, time_elapsed, tags=self.tags)
        print "Operation done in %s seconds, i.e. %s min. Duration metric %s was sent via dogstatsd" %(int(time_elapsed), int(time_elapsed) / 60, self.metric_name)

