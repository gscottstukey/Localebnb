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
from nltk.stem.wordnet import WordNetLemmatizer


class AirBnBListing(object):
    """
    Initializes an AirBnBListing object
    This allows you to scrape listings or retrieve listings from MongoDB

    INPUT:
    - db_name (str): 'airbnb' or 'airbnb_test'
    - coll_name (str): 'listings'
    """

    def __init__(self, db_name, coll_name):
        self.BASE_ROOM_URL = "https://www.airbnb.com/rooms/"

        client = MongoClient()
        self.db = client[db_name]
        self.coll = self.db[coll_name]

        self.listing_id = ""
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
                  'content': self.r.content,
                  'pickle': pkl,
                  'time': time.time(),
                  'dt': datetime.datetime.utcnow(),
                  'requests_meta': {
                     'status_code': self.r.status_code,
                     'is_redirect': self.r.is_redirect,
                     'is_ok': self.r.ok,
                     'raise_for_status': self.r.raise_for_status(),
                     'reason': self.r.reason
                     }
                  }

    def scrape_from_web_for_app(self, listing_id):
        '''
        Scrapes a single listing's info from AirBnB
        note: specific for the production instance of the app

        INPUT:
        - listing_id (int or str): the id of the listing you're trying to scrape
        OUTPUT: None
        '''

        self.listing_id = str(listing_id)    # ensure listing_id is a string
        self.url = self.BASE_ROOM_URL + self.listing_id
        self.r = requests.get(self.url)
        self.d = {'_id': self.listing_id,
                  'url': self.url,
                  'content': self.r.content,
                  'time': time.time(),
                  'dt': datetime.datetime.utcnow(),
                  }

    def pull_from_db(self, listing_id):
        '''
        Pulls a previously scraped listing's data from the MongoDB collection

        INPUT:
        - listing_id (int or str): the id of the listing you're trying to pull
        OUTPUT: None
        '''
        listing = self.coll.find_one({'_id': listing_id})

        self.listing_id = listing_id
        self.url = listing['url']
        self.r = pickle.loads(listing['pickle'])
        self.d = listing

    def pull_from_db_cached(self, listing_id):
        '''
        Pulls a previously scraped listing's data from the MongoDB collection
        Used for any listing after the production db crashed

        INPUT:
        - listing_id (int or str): the id of the listing you're trying to pull
        OUTPUT: None
        '''
        listing_id = str(listing_id)
        listing = self.coll.find_one({'_id': listing_id})

        self.listing_id = listing_id
        # self.url = listing['url']
        # self.r = pickle.loads(listing['pickle'])
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
            self.coll.update({'_id': self.listing_id}, {'$set': self.d})
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
        return bool(self.coll.find_one({'_id': listing_id}))

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
        return bool(self.coll.find_one({'_id': listing_id}))

    def _lemmatize(self, s):

        lemma = WordNetLemmatizer()
        words = s.split()
        lemmatized_words = [lemma.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)

    def _expand_contractions(self, s):
        '''
        Helper Function to expand contractions:

        INPUT:
        - s (str): raw description text
        OUTPUT:
        - str: the text with the contractions expanded
        '''
        # edited from
        # http://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python

        contractions_dict = {
            "ain't": "am not",
            "aren't": "are not",
            "can't": "cannot",
            "can't've": "cannot have",
            "'cause": "because",
            "could've": "could have",
            "couldn't": "could not",
            "couldn't've": "could not have",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hadn't've": "had not have",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'd've": "he would have",
            "he'll": "he will",
            "he'll've": "he shall have / he will have",
            "he's": "he is",
            "how'd": "how did",
            "how'd'y": "how do you",
            "how'll": "how will",
            "how's": "how is",
            "i'd": "I would",
            "i'd've": "I would have",
            "i'll": "I will",
            "i'll've": "i will have",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'd've": "it would have",
            "it'll": "it shall / it will",
            "it'll've": "it shall have / it will have",
            "it's": "it has / it is",
            "let's": "let us",
            "ma'am": "madam",
            "mayn't": "may not",
            "might've": "might have",
            "mightn't": "might not",
            "mightn't've": "might not have",
            "must've": "must have",
            "mustn't": "must not",
            "mustn't've": "must not have",
            "needn't": "need not",
            "needn't've": "need not have",
            "o'clock": "of the clock",
            "oughtn't": "ought not",
            "oughtn't've": "ought not have",
            "shan't": "shall not",
            "sha'n't": "shall not",
            "shan't've": "shall not have",
            "she'd": "she would",
            "she'd've": "she would have",
            "she'll": "she shall / she will",
            "she'll've": "she shall have / she will have",
            "she's": "she has / she is",
            "should've": "should have",
            "shouldn't": "should not",
            "shouldn't've": "should not have",
            "so've": "so have",
            "so's": "so as / so is",
            "that'd": "that would",
            "that'd've": "that would have",
            "that's": "tthat is",
            "there'd": "there had / there would",
            "there'd've": "there would have",
            "there's": "there is",
            "they'd": "they would",
            "they'd've": "they would have",
            "they'll": "they will",
            "they'll've": "they shall have / they will have",
            "they're": "they are",
            "they've": "they have",
            "to've": "to have",
            "wasn't": "was not",
            "we'd": "we would",
            "we'd've": "we would have",
            "we'll": "we will",
            "we'll've": "we will have",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what shall / what will",
            "what'll've": "what shall have / what will have",
            "what're": "what are",
            "what's": "what has / what is",
            "what've": "what have",
            "when's": "when has / when is",
            "when've": "when have",
            "where'd": "where did",
            "where's": "where has / where is",
            "where've": "where have",
            "who'll": "who shall / who will",
            "who'll've": "who shall have / who will have",
            "who's": "who has / who is",
            "who've": "who have",
            "why's": "why is",
            "why've": "why have",
            "will've": "will have",
            "won't": "will not",
            "won't've": "will not have",
            "would've": "would have",
            "wouldn't": "would not",
            "wouldn't've": "would not have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
            "y'all're": "you all are",
            "y'all've": "you all have",
            "you'd": "you would",
            "you'd've": "you would have",
            "you'll": "you will",
            "you'll've": "you shall have / you will have",
            "you're": "you are",
            "you've": "you have"
            }

        contractions_re = re.compile('(%s)' % '|'.join(contractions_dict.keys()))

        def replace(match):
            return contractions_dict[match.group(0)]
        return contractions_re.sub(replace, s)

    def _clean_description(self, d):
        '''
        Cleans up an AirBnB description as defined by:
            soup.find('div', {'class':'row description'}) /
            .find('div', {'class':'expandable-content expandable-content-long'}) /
            .get_text()
        where soup is the BeautifulSoup of the page content

        INPUT:
        - d (str): see above for how d is defined
        OUTPUT:
        - str: returns the cleaned up string
        '''
        # remove section Names/headers of the AirBnB description
        d = d.replace('\nThe Space\n', "", 1)
        d = d.replace('\nGuest Access\n', "", 1)
        d = d.replace('\nInteraction with Guests\n', "", 1)
        d = d.replace('\nThe Neighbourhood\n', "", 1)    # CA specific
        d = d.replace('\nThe Neighborhood\n', "", 1)    # US specific
        d = d.replace('\nGetting Around\n', "", 1)
        d = d.replace('\nOther Things to Note\n', "", 1)

        # convert the string to lowercase
        d = d.lower()
        # expand all contractions
        d = self._expand_contractions(d)
        # remove all non words
        d = re.sub("[^a-zA-Z]"," ", d)
        # remove punctuation
        # d = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', d)
        # lemmatize
        d = self._lemmatize(d)
        # remove line breaks
        d = d.replace('\n', " ")
        # remove multiple spaces
        d = ' '.join(d.split())

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
            listing_name = soup.find('div', {'class': "rich-toggle wish_list_button"})['data-name']
            features['listing_name'] = listing_name
        except TypeError:
            pass

        try:
            address = soup.find('div', {'class': "rich-toggle wish_list_button"})['data-address']
            features['address'] = address
        except TypeError:
            pass

        try:
            num_saved = soup.find('div', {'class': "rich-toggle wish_list_button"})['title']
            features['num_saved'] = num_saved
        except (TypeError, KeyError):
            pass

        try:
            headline = soup.find('meta', {'property': "og:description"})['content']
            features['headline'] = headline
        except TypeError:
            pass

        try:
            description_raw = soup.find('div', {'class': 'row description'}).find('div', {'class': 'expandable-content expandable-content-long'}).get_text()
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
            hood = soup.find('div', {'id': 'neighborhood-seo-link'}).h3.a.get_text().strip()
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
          * if we're able to clean up the string, returns cleaned description
          * if we error out, we return an empty string
        '''

        soup = BeautifulSoup(self.r.content)

        try:
            description_raw = soup.find('div', {'class': 'row description'}).find('div', {'class': 'expandable-content expandable-content-long'}).get_text()
            return self._clean_description(description_raw)
        except:
            return ""

    def extract_clean_description_cached(self):
        '''
        Extracts and returns the clean_description of the current listing
        Used for any listing after the production db crashed

        INPUT: None
        OUTPUT:
        - str:
          * if we're able to clean up the string, returns cleaned description
          * if we error out, we return an empty string
        '''

        try:
            description_raw = self.d['description_raw']
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
        # self.coll.update({'_id': self.listing_id}, new_features)
        self.coll.update({'_id': self.listing_id}, {'$set:': new_features})

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
            error_warning = {'error': 1, 'message': 'NO FEATURES EXTRACTED'}
            self.add_features(new_features=error_warning)
