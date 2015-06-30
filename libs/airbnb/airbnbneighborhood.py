"""
NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

import requests
from pymongo import MongoClient
import time
import datetime
from bs4 import BeautifulSoup
from unidecode import unidecode
import pickle


class AirBnBNeighborhood(object):
    """
    Initializes an AirBnBNeighborhood object
    This allows you to scrape neighborhood pages or retrieve them from MongoDB

    INPUT:
    - db_name (str): 'airbnb' or 'airbnb_test'
    - coll_name (str): 'neighborhoods'
    """

    def __init__(self, db_name, coll_name):
        """
        This is a class for searching AirBnBNeighborhood
        """

        self.BASE_URL = "https://www.airbnb.com"

        client = MongoClient()
        self.db = client[db_name]
        self.coll = self.db[coll_name]

        self.neighborhood_id = None
        self.neighborhood = ""
        self.url = ""
        self.city_id = None
        self.city = ""

        self.r = None
        self.d = {}

    def scrape_and_insert(self, neighborhood_id, neighborhood, neighborhood_url, city_id, city):
        """
        Scrapes a neighborhood & inserts the neighborhood into the collection

        INPUT:
        (per the 'neighborhood_list.csv' file)
        - neighborhood_id (int):
        - neighborhoold (str):
        - neighborhood_url (str):
        - city_id (int):
        - city (str):
        OUTPUT:
        - None
        """
        self.neighborhood_id = neighborhood_id
        self.neighborhood = neighborhood
        self.url = self.BASE_URL + neighborhood_url
        self.city_id = city_id
        self.city = city

        self.r = requests.get(self.url)

        if self.r.status_code == 200:
            pkl = pickle.dumps(self.r)

            self.d = {'content': self.r.content,
                      'pickle': pkl,
                      'time': time.time(),
                      'dt': datetime.datetime.utcnow(),
                      '_id': neighborhood_id,
                      'neighborhood': neighborhood,
                      'city_id': city_id,
                      'city': city,
                      'url': url,
                      'requests_meta': {
                          'status_code': self.r.status_code,
                          'is_redirect': self.r.is_redirect,
                          'is_ok': self.r.ok,
                          'raise_for_status': self.r.raise_for_status(),
                          'reason': self.r.reason
                          }
                      }

        else:
            self.d = {'time': time.time(),
                      'dt': datetime.datetime.utcnow(),
                      '_id': neighborhood_id,
                      'neighborhood': neighborhood,
                      'city_id': city_id,
                      'city': city,
                      'url': url,
                      'error': True,
                      'requests_meta': {
                          'status_code': self.r.status_code,
                          'is_redirect': self.r.is_redirect,
                          'is_ok': self.r.ok,
                          'raise_for_status': self.r.raise_for_status(),
                          'reason': self.r.reason
                          }
                      }

        self.coll.insert(self.d)

    def pull_from_db(self, neighborhood_id):
        """
        Pulls a previously scraped neighborhood's data from the MongoDB collection

        INPUT:
        - neighborhood_id (int or str): the id of the neighborhood you're trying to pull
        OUTPUT: None
        """
        hood = self.coll.find_one({'_id': neighborhood_id})

        self.neighborhood_id = hood['_id']
        self.neighborhood = hood['neighborhood']
        self.url = hood['url']

        self.r = pickle.loads(hood['pickle'])
        self.d = hood

    def is_in_collection(self, neighborhood_id=None):
        """
        Checks to see if the current neighborhood's data is in the MongoDB collection
        Note: This requires self.neighborhood_id to exist,
          i.e. a neighborhood to have been scraped or pulled

        INPUT:
        - neighborhood_id (None or int):
          * the id of the neighborhood you're trying to pull
          * if None (default), uses self.neighborhood_id
        OUTPUT: None
        """
        if not neighborhood_id:
            hood_id = self.neighborhood_id
        else:
            hood_id = neighborhood_id
        return bool(self.coll.find_one({'_id': hood_id}))

    def is_other_in_collection(self, neighborhood_id):
        """
        ********** DEPRECIATED ***********
        REASON: more efficient to combine this method wth is_in_collection()
        SOLUTION: use is_in_collection() with explicit neighborhood_id)
        **********************************

        Checks to see if an explicit neighborhood's data is in the MongoDB collection

        INPUT: None
        OUTPUT: None
        """
        if not self.coll.find_one({'_id': neighborhood_id}):
            return False
        else:
            return True

    def extract_features(self):
        """
        Extracts all of the predefined features of the currently loaded neighborhood

        INPUT: None
        OUTPUT:
        - dict: the dictionary of the predefined features extracted
        """
        features = {}

        soup = BeautifulSoup(self.r.content)

        headline = soup.find('div', {'class': 'center description'}).get_text().strip()
        features['headline'] = unidecode(headline)

        description = soup.find('meta', {'name': 'description'})['content']
        features['description'] = unidecode(description)

        traits = []
        traits_html = soup.find('ul', {'class': 'traits'})
        if traits_html is not None:
            for trait in traits_html.find_all('span'):
                traits.append(trait.get_text())
        features['traits'] = traits

        tags = []
        for tag in soup.find_all('div', {'class': 'neighborhood-tag'}):
            tags.append(tag.get_text().strip())
        features['tags'] = tags

        similar_hoods = []
        similar_hood_html = soup.find('ul', {'class': 'trait-neighborhoods neighborhoods'})
        if similar_hood_html is not None:
            for similar_hood in similar_hood_html.find_all('li'):
                similar_hoods.append(similar_hood['data-neighborhood-permalink'])
        features['similar_hoods'] = similar_hoods

        # This code doesn't parse out hoods "within" hoods
        neighboring_hoods = []
        for neighboring_hood in soup.find('p', {'class': 'lede center'}).find_all('a'):
            neighboring_hoods.append(neighboring_hood.get_text())
        features['neighboring_hoods'] = neighboring_hoods

        caption_bar = soup.find('div', {'class': 'caption bar'}).find_all('li')
        if caption_bar != []:
            public_trans = soup.find('div', {'class': 'caption bar'}).find_all('li')[0].strong.get_text()
            features['public_trans'] = public_trans
            having_a_car = soup.find('div', {'class': 'caption bar'}).find_all('li')[1].strong.get_text()
            features['having_a_car'] = having_a_car

        data_bbox = soup.find('div', {'id': 'inner-map'})['data-bbox']
        features['data_bbox'] = data_bbox
        data_x = float(soup.find('div', {'id': 'inner-map'})['data-x'])
        features['data_x'] = data_x
        data_y = float(soup.find('div', {'id': 'inner-map'})['data-y'])
        features['data_y'] = data_y

        return features

    def add_features(self, new_features):
        """
        Add features to the currently loaded neighborhood
        Note: The neighborhood must already exist in the MongoDB collection

        INPUT: new_features (dict) - a dict of features to add
        OUTPUT: None
        """

        self.coll.update({'_id': self.neighborhood_id}, {'$set': new_features})

    def extract_and_add_features(self):
        """
        Runs extract_features() on the currently loaded neighborhood's data,
        and then runs add_features() to add them
        Note: The neighborhood must already exist in the MongoDB collection

        INPUT: None
        OUTPUT: None
        """
        new_features = self.extract_features()
        self.add_features(new_features=new_features)
