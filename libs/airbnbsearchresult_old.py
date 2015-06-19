
"""
Script for scraping AirBnB's search results and inserting the raw HTML into a MongoDB database

notes: make sure mongod running. use `sudo mongod` in terminal
"""

import datetime
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

import pickle


class AirBnBSearchResult(object):

    def __init__(self, db_name, coll_name, params):
        """
        This is a class for searching AirBnBSearchResults

        required params:
            strings: city, state, country
            dates (as strings in mm-dd-yyyy format): checkin, checkout
            ints: guests, start_page, end_page, price_max
        """

        self.SEARCH_RESULT_URL = "https://www.airbnb.com/s/"

        client = MongoClient()

        #mandatory parameters
        self.db = client[db_name]
        self.coll = self.db[coll_name]
        self.city = params['city']
        self.state = params['state']
        self.country = params['country']
        self.checkin = params['checkin']
        self.checkout = params['checkout']
        self.guests = params['guests']

        # the rest of the params
        self.start_page = params['start_page']    # GSCOTT: Update this later to default to 1
        self.end_page = params['end_page']
        # self.price_min = params['price_min']
        # self.price_max = params['price_max']

        # for safe keeping
        self.params = params    # GSCOTT: Update this later


    def scrape_all_results(self, insert_into_db = True, verbose = False, pause_between_pages=0):
        """
        G SCOTT TO FILL IN
        """

        city_url = '%s--%s--%s' % (self.city, self.state, self.country)

        url_params = {'checkin': self.checkin, 
              'checkout': self.checkout,
              'guests': self.guests}

        for page in xrange(self.start_page, self.end_page+1): 
            url_params['page'] = page 

            r = requests.get(self.SEARCH_RESULT_URL + city_url, params=url_params)

            if r.status_code == 200:
                pkl = pickle.dumps(r)    # pickling the requests object to allow parsing via Beautiful Soup later 

                d = {'content':r.content,
                     'pickle': pkl,
                     'time': time.time(),
                     'dt':datetime.datetime.utcnow(),
                     'city': self.city,
                     'state': self.state,
                     'country': self.country,
                     'params':url_params,
                     'requests_meta':{
                         'status_code': r.status_code,
                         'is_redirect': r.is_redirect,
                         'is_ok': r.ok,
                         'raise_for_status': r.raise_for_status(),
                         'reason': r.reason
                         },
                     'url': r.url,
                     'page': page}

            if verbose: print d

            if insert_into_db: self.coll.insert(d)

            time.sleep(pause_between_pages)
            

    def test_insert(self):
        self.coll.insert({'foo':'bar'})


