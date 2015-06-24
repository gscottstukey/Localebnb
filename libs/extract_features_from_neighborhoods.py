"""
Script to extract features from the Neighborhoods

DEPENDENCIES:
1) scrape_neighborhoods.py > MongoDB 'neighborhoods' collection

NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

from airbnb.airbnbneighborhood import AirBnBNeighborhood

DB_NAME = 'airbnb'
COLL_NAME = 'neighborhoods'

def main():
    air_hood = AirBnBNeighborhood(db_name = DB_NAME, coll_name = COLL_NAME)
    hoods_dict = list(air_hood.coll.find({},{'_id':1}))

    for hood in hoods_dict:
        hood_id = hood['_id']
        air_hood.pull_from_db(neighborhood_id=hood_id)
        air_hood.extract_and_add_features()
        print "Extracting Features for %s" % hood_id


if __name__ == '__main__':
    main()