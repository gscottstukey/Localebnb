import pandas as pd
from pandas.tseries.offsets import DateOffset
from airbnbneighborhood import AirBnBNeighborhood
import time

DB = 'airbnb'
COLL = 'neighborhoods'
NEIGHBORHOOD_FILEPATH = '../data/neighborhood_list.csv'

def import_neighborhoods(filepath):
    df = pd.read_csv(filepath)
    return df.to_dict('records')


def main():
    air_hoods = AirBnBNeighborhood(db=DB, coll=COLL)

    hood_list = import_neighborhoods(NEIGHBORHOOD_FILEPATH)

    for hood in hood_list:
        air_hoods.scrape_and_insert(neighborhood_id = hood['neighborhood_id'], 
                                    neighborhood = hood['neighborhood'], 
                                    neighborhood_url = hood['neighborhood_url'],
                                    city_id = hood['city_id'], 
                                    city = hood['city'])

        print "%s > %s" % (hood['city'], hood['neighborhood'])

        time.sleep(2.5)    # so hopefully I don't get booted from AirBnB


if __name__=="__main__":
    main()