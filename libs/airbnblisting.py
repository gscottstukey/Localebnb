from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pickle
import time
import datetime
import string
import re

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
        listing = self.coll.find_one({'_id':listing_id})
        self.listing_id = listing_id
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
        return bool(self.coll.find_one({'_id':self.listing_id}))


    def is_other_in_collection(self, listing_id):
        return bool(self.coll.find_one({'_id':listing_id}))


    def _clean_description(self, d):
        # d = d.replace('\nThe Space\n', "", 1)
        # d = d.replace('\nGuest Access\n', "", 1)
        # d = d.replace('\nInteraction with Guests\n', "", 1)
        # d = d.replace('\nThe Neighbourhood\n', "", 1)    # CA specific
        # d = d.replace('\nThe Neighborhood\n', "", 1)    # US specific
        # d = d.replace('\nGetting Around\n', "", 1)   
        # d = d.replace('\nOther Things to Note\n', "", 1)
        d = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', d)
        d = d.replace('\n', " ")    # Remove line breaks
        d = ' '.join(d.split())    # Remove multiple spaces
        d = d.lower()
        return d


    def extract_features(self):
        features = {}

        soup = BeautifulSoup(self.r.content)

        try:
            listing_name = soup.find('div', {'class':"rich-toggle wish_list_button"})['data-name']
            features['listing_name'] = listing_name
        except TypeError:
            pass

        try:
            address = soup.find('div', {'class':"rich-toggle wish_list_button"})['data-address']
            features['address'] = address
        except TypeError:
            pass

        try:
            num_saved = soup.find('div', {'class':"rich-toggle wish_list_button"})['title']
            features['num_saved'] = num_saved
        except (TypeError, KeyError):
            pass

        try:
            headline = soup.find('meta', {'property':"og:description"})['content']
            features['headline'] = headline
        except TypeError:
            pass

        try:
            description_raw = soup.find('div', {'class':'row description'}).find('div', {'class':'expandable-content expandable-content-long'}).get_text()
            features['description_raw'] = description_raw
            features['description_clean'] = self._clean_description(description_raw)
        except AttributeError:
            pass

        try:
            price_currency = soup.find('meta', {'itemprop': 'priceCurrency'})['content']
            features['price_currency'] = price_currency
        except TypeError:
            pass

        try:
            price = soup.find('meta', {'itemprop': 'price'})['content']
            features['price'] = price
        except TypeError:
            pass

        try:
            hood = soup.find('div',{'id':'neighborhood-seo-link'}).h3.a.get_text().strip()
        except (AttributeError):
            hood = "N/A"
        features['neighborhood'] = hood

        return features


    def _extract_clean_description(self):

        soup = BeautifulSoup(self.r.content)

        try:
            description_raw = soup.find('div', {'class':'row description'}).find('div', {'class':'expandable-content expandable-content-long'}).get_text()
            return self._clean_description(description_raw)
        except:
            return ""

    def add_features(self, new_features):
        '''
        add features to the currently loaded neighborhood
        INPUT: new_features = dict of features
        OUTPUT: None
        '''
        self.coll.update({'_id':self.listing_id},{'$set':new_features})


    def extract_and_add_features(self):
        new_features = self.extract_features()
        if new_features != {}:
            self.add_features(new_features=new_features)
        else:
            error_warning = {'error':1, 'message':'NO FEATURES EXTRACTED'}
            self.add_features(new_features=error_warning)





