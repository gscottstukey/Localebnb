'''
Script ran once we've grabbed the search listings.
Inserts all of the listings found in the search result into the listings collection.

notes: make sure mongod is running. use `sudo mongod` in terminal
'''

from bs4 import BeautifulSoup
import pickle
from pymongo import MongoClient


DB_NAME = 'airbnb'
SEARCH_COLL_NAME = 'search'
LISTING_COLL_NAME = 'listings'


def main():


    client = MongoClient()
    db = client[DB_NAME]
    search_coll = db[SEARCH_COLL_NAME]
    listing_coll = db[LISTING_COLL_NAME]

    for x in search_coll.find({},{'pickle':1}):
        r = pickle.loads(x['pickle'])
        soup = BeautifulSoup(r.content)
        for listing in soup.find_all("div", {"class": "listing"}):
            try:
                listing_id = listing['data-id']
                listing_ids.append(listing_id)
                if not listing_coll.find_one({'_id':listing_id}):
                    listing_coll.insert({'_id':listing_id})
                    print "SUCCESS: Added %s to database" % listing_id
                else:
                    "DUPLICATE: Already added %s to database" % listing_id
            except:
                "ERROR: No listings" 


if __name__=="__main__":
    main()