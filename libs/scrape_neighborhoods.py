"""
This script is used to scrape the neighborhood pages for its content
* takes in a file ('../data/neighborhood_list.csv')
* scrapes AirBnB's neighborhood guide for neighborhoods

DEPENDENCIES:
1) scrape_neighborhood_list.py > '../data/neighborhood_list.csv'

    import pandas as pd
    df = pd.read_csv('../data/neighborhood_list.csv')
    print df.head(2)


       neighborhood_id    neighborhood                         neighborhood_url  \
    0                0    Alamo Square    /locations/san-francisco/alamo-square
    1                1         Bayview         /locations/san-francisco/bayview

       city_id           city
    0        1  san-francisco
    1        1  san-francisco


    print df.tail(2)

         neighborhood_id     neighborhood                     neighborhood_url  \
    100              100     Williamsburg     /locations/new-york/williamsburg
    101              101  Windsor Terrace  /locations/new-york/windsor-terrace

         city_id      city
    100        2  new-york
    101        2  new-york


POTENTIAL ISSUES:
1) city_id:
    * city_id is unique to this project; it is not based on AirBnB's city ids
2) neighborhood_id:
    * arbitrarily assigned neighborhood_ids based on the orderscraped
    * if content changes, then all dependencies are impacted

NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

import pandas as pd
from airbnb.airbnbneighborhood import AirBnBNeighborhood
import time

DB_NAME = 'airbnb'
COLL_NAME = 'neighborhoods'
NEIGHBORHOOD_FILEPATH = '../data/neighborhood_list.csv'


def main():
    air_hood = AirBnBNeighborhood(db_name=DB, coll_name=COLL)

    df = pd.read_csv(NEIGHBORHOOD_FILEPATH)
    hood_list = df.to_dict('records')

    for hood in hood_list:
        air_hood.scrape_and_insert(neighborhood_id=hood['neighborhood_id'],
                                   neighborhood=hood['neighborhood'],
                                   neighborhood_url=hood['neighborhood_url'],
                                   city_id=hood['city_id'],
                                   city=hood['city'])

        # print "%s > %s" % (hood['city'], hood['neighborhood'])

        time.sleep(2.5)    # as to not get banned from AirBnB


if __name__ == "__main__":
    main()
