"""
This script is used to scrape AirBnB's search result pages for its content
* takes in a file ('../data/city_list.csv')
* generates a sampling of dates
* scrapes AirBnB's searchlings

DEPENDENCIES:
1) '../data/city_list.csv'

    import pandas as pd
    df = pd.read_csv('../data/city_list.csv')
    print df.head(2)

       city_id           city state        country
    0        1  San-Francisco    CA  United-States
    1        2       New-York    NY  United-States

NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

import pandas as pd
from pandas.tseries.offsets import DateOffset
from airbnb.airbnbsearchresult import AirBnBSearchResult
import time

START_DATE = '06-15-2015'

# NUM_WEEKS = 1    # test runs
NUM_WEEKS = 26    # all other runs

# NUM_GUESTS = {1}    # test runs
# NUM_GUESTS = {1, 2, 4}    # used for 1st run
NUM_GUESTS = {1, 4}    # used for subsequent runs

# NUM_PAGES = 1    # test runs
# NUM_PAGES = 10    # used for 1st run
NUM_PAGES = 25    # used for subsequent runs

CITY_FILEPATH = '../data/city_list.csv'
DB_NAME = 'airbnb'
COLL_NAME = 'search'


def import_city_list(filepath):
    df = pd.read_csv(filepath)
    return df.to_dict('records')


def create_date_list():
    dates = pd.date_range(START_DATE, periods=7*NUM_WEEKS, freq='D')
    day_of_weeks = [1, 4]    # we want only Tuesdays & Fridays
    cond = [d.dayofweek in day_of_weeks for d in dates]
    sampled_dates = dates[cond]
    # for the purposes of scraping, checkout will always be 2 days later
    return sampled_dates


def main():
    city_list = import_city_list(CITY_FILEPATH)
    date_list = create_date_list()

    air_search = AirBnBSearchResult(db_name=DB_NAME, coll_name=COLL_NAME)

    for city in city_list:
        for num_guests in NUM_GUESTS:
            for date in date_list:
                params = {'city': city['city'],
                          'state': city['state'],
                          'country': city['country'],
                          'checkin': date.date().strftime('%m-%d-%Y'),
                          'checkout': (date + DateOffset(2)).strftime('%m-%d-%Y'),
                          'guests': num_guests,
                          'start_page': 1,
                          'end_page': NUM_PAGES
                          }

                air_search.set_params(params)
                air_sr.scrape_all_results(pause, pause_between_pages=1)

                # print "%s > %s > %s" % (city['city'], num_guests, date.date().strftime('%m-%d-%Y'))

                time.sleep(2.5)    # as to not get banned from AirBnB


if __name__ == "__main__":
    main()
