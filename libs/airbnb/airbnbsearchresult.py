"""
NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

import datetime
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import pickle


class AirBnBSearchResult(object):
    """
    Initializes an AirBnBSearchResult object 
    This allows you to scrape search result pages or retrieve them from MongoDB

    INPUT: 
    - db_name (str): 'airbnb' or 'airbnb_test'
    - coll_name (str): 'search'
    """

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
        self.db = client[db_name]
        self.coll = self.db[coll_name]


    def set_params(self, params):
        """
        Sets the initial parameters of the search result

        INPUT: 
        - params (dict): this should include:
          * city, state, country (strings)
          * checkin, checkout (strings, in mm-dd-yyyy format)
          * guests (int)
          * price_max (int or float)

        """
        self.params = params

        self.city = self.params['city']
        self.state = self.params['state']
        self.country = self.params['country']
        self.checkin = self.params['checkin']
        self.checkout = self.params['checkout']
        self.guests = self.params['guests']
        # self.price_min = params['price_min']
        if 'price_max' in params:
            self.price_max = params['price_max']


    def scrape_all_results(self, start_page=1, end_page=1, insert_into_db = True, pause_between_pages=1.0):
        """
        Scrapes multiple pages of a search result info from AirBnB
        Runs scrape_from_web() on the currently loaded params,
        for each page from start_page to end_page
        note: requires set_params() to have been run

        INPUT: 
        - start_pagem, end_page (ints): the page numbers to add to the url parameters
        - insert_into_db (bool): whether or not to insert the data into the db
        - pause_between_pages (float): How long to wait between pages
        OUTPUT: None
        """

        self.start_page = start_page
        self.end_page = end_page

        for page in xrange(start_page, end_page+1): 
            scrape = self.scrape_from_web(page=page, insert_into_db=insert_into_db)
            if insert_into_db: self.coll.insert(d)

            time.sleep(pause_between_pages)

    def scrape_from_web(self, page=1, insert_into_db = True):
        """
        Scrapes a search result's info from AirBnB
        note: requires set_params() to have been run

        INPUT: 
        - page (int): the page number to add to the url parameters
        - insert_into_db (bool): whether or not to insert the data into the db
        OUTPUT: None
        """

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


    def pull_one_from_db(self):
        """
        Pulls a previously scraped search result data from the MongoDB collection
        The query is based off of the city, state, country & checkin information
        Note: requires the user to have run set_params()

        INPUT: None
        OUTPUT: None
        """
        self.d = self.coll.find_one({'city':self.city,
                            'state':self.state,
                            'country':self.country,
                            'params.checkin':self.checkin})

        self.r = pickle.loads(self.d['pickle'])


    def extract_listing_ids(self):
        """
        Creates a list of all the listing_ids found on the Search Result page

        INPUT: None
        OUTPUT: list (of strs)
        """
        listing_ids = []
        soup = BeautifulSoup(self.r.content)

        for listing in soup.find_all("div", {"class": "listing"}):
            listing_ids.append(listing['data-id'])
            
        return listing_ids

    def extract_thumbnail_data(self):
        """
        Creates a dictionary for each listing filled with all its critical data 
        Note: This requires self.r.content to exist,
          i.e. a search result to have been scraped or pulled

        INPUT: None
        OUTPUT: dict (of dicts)
        """
        thumbnail_data = {}
        soup = BeautifulSoup(self.r.content)

        for listing in soup.find_all("div", {"class": "listing"}):
            cur_data = {}
            listing_id = listing['data-id']
            cur_data['listing_id'] = listing_id

            cur_data['lat'] = listing['data-lat']
            cur_data['lng'] = listing['data-lng']

            if listing.find('img') != None:
                tmp_img = listing.find('img')['data-urls'][2:]
                tmp_img = tmp_img[:tmp_img.find("\"")]
                cur_data['thumbnail_img'] = tmp_img
            else:
                cur_data['thumbnail_img'] = "/no_thumbnail.jpg"
            
            cur_data['blurb'] = listing['data-name']
            
            if listing.find("span"):
                cur_data['thumbnail_price'] = listing.find("span").get_text()
            else:
                cur_data['thumbnail_price'] = "n/a"

            if listing.find("div", {'itemprop':"description"}):
                if listing.find("div", {'itemprop':"description"}).find('a'):
                    tmp = listing.find("div", {'itemprop':"description"}).find('a').get_text()
                    if tmp.find(u'\xb7') != -1:
                        tmp=tmp[:tmp.find(u'\xb7')]
                    cur_data['listing_type'] = tmp
                else:
                    cur_data['listing_type'] = "not available"
            else:
                cur_data['listing_type'] = "not available"

            thumbnail_data[listing_id] = cur_data

        return thumbnail_data


    def insert_into_coll(self, overwrite=False):
        """
        Inserts the current search result's data into the MongoDB collection

        INPUT: 
        - overwrite (bool): whether to overwrite if the listing already exists
        OUTPUT: None
        """

        self.coll.insert(self.d)


