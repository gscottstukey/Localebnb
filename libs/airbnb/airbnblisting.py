"""
NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pickle
import time
import datetime
import string
import re

class AirBnBListing(object):
    '''
    Initializes an AirBnBListing object 
    This allows you to scrape listings or retrieve listings from MongoDB

    INPUT: 
    - db_name (str): 'airbnb' or 'airbnb_test'
    - coll_name (str): 'listings'
    '''

    def __init__(self, db_name, coll_name):
        self.BASE_ROOM_URL = "https://www.airbnb.com/rooms/"

        client = MongoClient()
        self.db = client[db_name]
        self.coll = self.db[coll_name]

        self.listing_id=""
        self.url = ""
        self.r = None
        self.d = {}


    def scrape_from_web(self, listing_id):
        '''
        Scrapes a single listing's info from AirBnB

        INPUT: 
        - listing_id (int or str): the id of the listing you're trying to scrape
        OUTPUT: None
        '''

        self.listing_id = str(listing_id)    # ensure listing_id is a string
        self.url = self.BASE_ROOM_URL + self.listing_id
        self.r = requests.get(self.url)
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


    def pull_from_db(self, listing_id):
        '''
        Pulls a previously scraped listing's data from the MongoDB collection

        INPUT: 
        - listing_id (int or str): the id of the listing you're trying to pull
        OUTPUT: None
        '''
        listing = self.coll.find_one({'_id':listing_id})

        self.listing_id = listing_id
        self.url = listing['url']
        self.r = pickle.loads(listing['pickle'])
        self.d = listing


    def insert_into_coll(self, overwrite=False):
        '''
        Inserts the current listing's data into the MongoDB collection
        - If the listing does not exist, it gets inserted
        - If the listing exists, the insertion depends on if we wish to overwrite

        INPUT: 
        - overwrite (bool): whether to overwrite if the listing already exists
        OUTPUT:
        - bool: 
          * Returns True if a listing was inserted (new or overwriten)
          * Return False if the listing existed and overwrite=False
        '''
        if not self.is_in_collection():
            self.coll.insert(self.d)
            return True
        elif overwrite:
            self.coll.update({'_id':self.listing_id},{'$set':self.d})
            return True
        else:
            return False


    def scrape_and_insert(self, listing_id, overwrite=False):
        '''
        Runs scrape_from_web() & insert_into_coll() with parameters provided
        NOTE: this method does NOT return what insert_into_coll returns

        INPUT: 
        - listing_id (int or str): the id of the listing you're trying to pull
        - overwrite (bool): whether to overwrite if the listing already exists
        OUTPUT: None
        '''
        self.scrape_from_web(listing_id=listing_id)
        self.insert_into_coll(overwrite=overwrite)



    def is_in_collection(self, listing_id=None):
        '''
        Checks to see if the current listing's data is in the MongoDB collection
        NOTE: this method is only useful in conjunction with scrape_from_web()

        INPUT: 
        - listing_id (None or int or str): 
          * the id of the listing you're trying to pull
          * if None (default), uses self.listing_id
        OUTPUT: None
        '''
        if not listing_id:
            listing_id = self.listing_id
        else:
            listing_id = str(listing_id)
        return bool(self.coll.find_one({'_id':listing_id}))


    def is_other_in_collection(self, listing_id):
        '''
        ********** DEPRECIATED ***********
        REASON: more efficient to combine this method wth is_in_collection()
        SOLUTION: use is_in_collection() with explicit listing_id)
        **********************************

        Checks to see if an explicit listing's data is in the MongoDB collection
        NOTE: this method is only useful in conjunction with scrape_from_web()

        INPUT: None
        OUTPUT: None
        '''
        return bool(self.coll.find_one({'_id':listing_id}))


    def _clean_description(self, d):
        '''
        Cleans up an AirBnB description as defined by:
            soup.find('div', {'class':'row description'}) \
            .find('div', {'class':'expandable-content expandable-content-long'}) \
            .get_text()
        where soup is the BeautifulSoup of the page content

        INPUT: 
        - d (str): see above for how d is defined 
        OUTPUT:
        - str: returns the cleaned up string
        '''
        # remove section Names/headers of the AirBnB description
        # d = d.replace('\nThe Space\n', "", 1)
        # d = d.replace('\nGuest Access\n', "", 1)
        # d = d.replace('\nInteraction with Guests\n', "", 1)
        # d = d.replace('\nThe Neighbourhood\n', "", 1)    # CA specific
        # d = d.replace('\nThe Neighborhood\n', "", 1)    # US specific
        # d = d.replace('\nGetting Around\n', "", 1)   
        # d = d.replace('\nOther Things to Note\n', "", 1)

        # remove putuation
        d = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', d)
        # remove line breaks
        d = d.replace('\n', " ") 
        # remove multiple spaces   
        d = ' '.join(d.split()) 
        # convert the string to lowercase
        d = d.lower()

        return d


    def extract_features(self):
        '''
        Extracts all of the predefined features of the currently loaded listing

        INPUT: None
        OUTPUT:
        - dict: the dictionary of the predefined features extracted 
        '''
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


    def extract_clean_description(self):
        '''
        Extracts and returns the clean_description of the current listing

        INPUT: None
        OUTPUT:
        - str: 
          * if we're able to clean up the string, returns the cleaned description
          * if we error out, we return an empty string
        '''

        soup = BeautifulSoup(self.r.content)

        try:
            description_raw = soup.find('div', {'class':'row description'}).find('div', {'class':'expandable-content expandable-content-long'}).get_text()
            return self._clean_description(description_raw)
        except:
            return ""


    def add_features(self, new_features):
        '''
        Adds new features to the currently loaded listing's data
        Note: The listing must already exist in the MongoDB collection

        INPUT: 
        - new_features (dict): a dictionary of new features to add the the listing
        OUTPUT: None
        '''
        self.coll.update({'_id':self.listing_id},{'$set':new_features})


    def extract_and_add_features(self):
        '''
        Runs extract_features() on the currently loaded listing's data, 
        and tthen runs add_features() to add them
        Note: The listing must already exist in the MongoDB collection

        INPUT: None
        OUTPUT: None
        '''
        new_features = self.extract_features()
        if new_features != {}:
            self.add_features(new_features=new_features)
        else:
            error_warning = {'error':1, 'message':'NO FEATURES EXTRACTED'}
            self.add_features(new_features=error_warning)

