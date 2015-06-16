"""
Script for scraping AirBnB's search results and inserting the raw HTML into a MongoDB database

notes: make sure mongod running. use `sudo mongod` in terminal
"""

import requests
from pymongo import MongoClient
import time
import datetime

try:
   import cPickle as pickle
except:
   import pickle

class AirBnBNeighborhood(object):

    def __init__(self, db, coll):
        """
        This is a class for searching AirBnBNeighborhood
        """

        self.BASE_URL = "https://www.airbnb.com"

        client = MongoClient()
        self.db = client[db]
        self.coll = self.db[coll]
        


    def scrape_and_insert(self, neighborhood_id, neighborhood, neighborhood_url, city_id, city):
        """
        G SCOTT TO FILL IN
        """

        url = self.BASE_URL + neighborhood_url

        r = requests.get(url)

        if r.status_code == 200:
            pkl = pickle.dumps(r)    # pickling the requests object to allow parsing via Beautiful Soup later 

            d = {'content':r.content,
                 'pickle': pkl,
                 'time': time.time(),
                 'dt':datetime.datetime.utcnow(),
                 '_id': neighborhood_id,
                 'neighborhood': neighborhood,
                 'url': url,
                 'requests_meta':{
                     'status_code': r.status_code,
                     'is_redirect': r.is_redirect,
                     'is_ok': r.ok,
                     'raise_for_status': r.raise_for_status(),
                     'reason': r.reason
                     }
                 }
    
        else:
            d = {'time': time.time(),
                 'dt':datetime.datetime.utcnow(),
                 '_id': neighborhood_id,
                 'neighborhood': neighborhood,
                 'url': url,
                 'error': True,
                 'requests_meta':{
                     'status_code': r.status_code,
                     'is_redirect': r.is_redirect,
                     'is_ok': r.ok,
                     'raise_for_status': r.raise_for_status(),
                     'reason': r.reason
                     }
                }

        self.coll.insert(d)