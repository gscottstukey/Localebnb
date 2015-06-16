'''
Script to scrape listings

notes: make sure mongod running. use `sudo mongod` in terminal
notes: use VPN
'''

from multiprocessing import Pool
from airbnblisting import AirBnBListing
import time

DB_NAME = 'airbnb'
COLL_NAME = 'listings'


def main():
    air_listing = AirBnBListing(db_name = DB_NAME, coll_name = COLL_NAME)
    listing_dicts = list(air_listing.coll.find({'dt':{'$exists':0}},{'_id':1}))
    for listing in listing_dicts:
        listing_id = listing['_id']
        air_listing.scrape_and_insert(listing_id=listing_id, overwrite=True)
        print "Scraping & Adding %s" % listing_id
        time.sleep(3)    # AirBnB doesn't like me; also using a VPN

    

if __name__ == '__main__':
    main()