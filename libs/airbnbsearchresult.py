
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

    def __init__(self, db_name, coll_name):
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


    def set_params(self, params):
        self.params = params

        self.city = self.params['city']
        self.state = self.params['state']
        self.country = self.params['country']
        self.checkin = self.params['checkin']
        self.checkout = self.params['checkout']
        self.guests = self.params['guests']
        # self.price_min = params['price_min']
        # self.price_max = params['price_max']


    def scrape_all_results(self, start_page=1, end_page=1, insert_into_db = True, verbose = False, pause_between_pages=2.5):
        """
        G SCOTT TO FILL IN
        """        

        self.start_page = start_page
        self.end_page = end_page

        for page in xrange(start_page, end_page+1): 
            scrape = self.scrape_from_db(page=page, insert_into_db=insert_into_db)
            if insert_into_db: self.coll.insert(d)

            time.sleep(pause_between_pages)

    def scrape_from_web(self, page=1, insert_into_db = True):
        city_url = '%s--%s--%s' % (self.city, self.state, self.country)

        url_params = {'checkin': self.checkin, 
              'checkout': self.checkout,
              'guests': self.guests, 
              'price_max': self.price_max}

        if page != 1:
            url_params['page'] = page

        self.r = requests.get(self.SEARCH_RESULT_URL + city_url, params=url_params)

        if self.r.status_code == 200:
            pkl = pickle.dumps(self.r)    # pickling the requests object to allow parsing via Beautiful Soup later 

            self.d = {'content':self.r.content,
                 'pickle': pkl,
                 'time': time.time(),
                 'dt':datetime.datetime.utcnow(),
                 'city': self.city,
                 'state': self.state,
                 'country': self.country,
                 'params':url_params,
                 'requests_meta':{
                     'status_code': self.r.status_code,
                     'is_redirect': self.r.is_redirect,
                     'is_ok': self.r.ok,
                     'raise_for_status': self.r.raise_for_status(),
                     'reason': self.r.reason
                     },
                 'url': self.r.url,
                 'page': page}

        if insert_into_db: self.insert_into_coll()


    def pull_from_db(self):
        pass

    def pull_one_from_df(self):
        self.d = self.coll.find_one({'city':self.city,
                            'state':self.state,
                            'country':self.country,
                            'params.checkin':self.checkin})

        self.r = pickle.loads(self.d['pickle'])


    def extract_listing_ids(self):
        listing_ids = []
        soup = BeautifulSoup(self.r.content)

        for listing in soup.find_all("div", {"class": "listing"}):
            listing_ids.append(listing['data-id'])
            
        return listing_ids


    def insert_into_coll(self, overwrite=False):
        self.coll.insert(self.d)


