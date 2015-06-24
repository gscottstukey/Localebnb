"""
This script is used to scrape AirBnB's listings pages for its content
* scrapes every listing found in the listing collection

DEPENDENCIES:
1) extract_listings_from_search_results.py > MongoDB 'listing' collection

POTENTIAL ISSUES:
1) Gettign Blocked/Banned:
    * While I did this file, I got stopped several times. 
    * At a certain point, I used a VPN from Canada to scrape
    * Thankfully, I had a 3500+ chunk that I was able to do overnight

NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

from airbnb.airbnblisting import AirBnBListing
import time

DB_NAME = 'airbnb'
COLL_NAME = 'listings'

def main():
    air_listing = AirBnBListing(db_name=DB_NAME, coll_name=COLL_NAME)
    
    # grab a dict of listings that haven't yet been scraped
    # based off of the existings of the 'dt' field 
    listing_dicts = list(air_listing.coll.find({'dt':{'$exists':0}},{'_id':1}))

    # for each listing not yet pulled, attempt to scrape & insert into the db

    for listing in listing_dicts:
        listing_id = listing['_id']
        air_listing.scrape_and_insert(listing_id=listing_id, overwrite=True)
        
        # print "Scraping & Adding %s" % listing_id
        
        time.sleep(3)    # as to not get banned from AirBnB


if __name__ == '__main__':
    main()