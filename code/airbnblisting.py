from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pickle
import time
import datetime

class AirBnBListing(object):

    def __init__(self, db_name, coll_name):
        '''
        INPUT: coll = an open connection to a MongoDB collection
        '''

        self.BASE_ROOM_URL = "https://www.airbnb.com/rooms/"

        client = MongoClient()
        self.db = client[db_name]
        self.coll = self.db[coll_name]

        self.listing_id=""
        self.url = ""
        self.r = None
        self.d = {}


    def generate_listing_data(self):
        pkl = pickle.dumps(self.r)

        self.d = {'_id': self.listing_id,
                 'url': self.url,
                 'content':self.r.content,
                 'pickle': pkl,
                 'time': time.time(),
                 'dt':datetime.datetime.utcnow(),
                 'requests_meta':{
                     'status_code': self.r.status_code,
                     'is_redirect': self.r.is_redirect,
                     'is_ok': self.r.ok,
                     'raise_for_status': self.r.raise_for_status(),
                     'reason': self.r.reason
                     }
                 }


    def scrape_from_web(self, listing_id):
        self.listing_id = listing_id
        self.url = self.BASE_ROOM_URL + str(self.listing_id)    # Ensuring listing_id is a string
        self.r = requests.get(self.url)


    def pull_from_db(self, listing_id):
        listing = self.coll.findOne({'_id':listing_id})
        self.r = pickle.loads(listing['pickle'])
        self.url = listing['url']


    def insert_into_coll(self, overwrite=False):
        if not self.is_in_collection():
            self.coll.insert(self.d)
            return True
        elif overwrite:
            self.coll.update({'_id':self.listing_id},{'$set':self.d})
            return True
        else:
            return False


    def scrape_and_insert(self, listing_id, overwrite=False):
        self.scrape_from_web(listing_id=listing_id)
        self.generate_listing_data()
        self.insert_into_coll(overwrite=overwrite)


    def is_in_collection(self):
        if not self.coll.find_one({'_id':self.listing_id}):
            return False
        else:
            return True


    def is_other_in_collection(self, listing_id):
        if not self.coll.find_one({'_id':listing_id}):
            return False
        else:
            return True

    def extract_features(self):
        pass


    def update_db_record(self):
        pass