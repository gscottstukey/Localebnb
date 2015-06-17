'''
Script to extract features from Listings

notes: make sure mongod running. use `sudo mongod` in terminal
'''

from airbnblisting import AirBnBListing

DB_NAME = 'airbnb'
COLL_NAME = 'listings'

def main():
    air_listing = AirBnBListing(db_name = DB_NAME, coll_name = COLL_NAME)
    listing_dict = list(air_listing.coll.find({},{'_id':1}))

    for listing in listing_dict:
        listing_id = listing['_id']
        air_listing.pull_from_db(listing_id=listing_id)
        air_listing.extract_and_add_features()
        print "Extracting Features for %s" % listing_id

if __name__ == '__main__':
    main()