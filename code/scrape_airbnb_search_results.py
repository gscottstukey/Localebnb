import pandas as pd
from pandas.tseries.offsets import DateOffset
from airbnbsearchresult import AirBnBSearchResult
import time

START_DATE = '06-15-2015'
# NUM_WEEKS = 1    # Testing
NUM_WEEKS = 26    # All Runs

# NUM_GUESTS = {1}    # Testing
# NUM_GUESTS = {1,2,4}    # First Run
NUM_GUESTS = {1,4}    # 2nd Run, 3rd Run, 4th rerun

# NUM_PAGES = 1    # Testing
# NUM_PAGES = 10    # First Run
NUM_PAGES = 25    # 2nd Run, 3rd Run, 4th rerun

DB = 'airbnb'
COLL = 'search'

def import_city_list(filepath):
    df = pd.read_csv(filepath)
    return df.to_dict('records')


def create_date_list():
    dates = pd.date_range(START_DATE, periods=7*NUM_WEEKS, freq='D')
    day_of_weeks = [1,4]    # Want only Tuesdays & Fridays
    cond = [d.dayofweek in day_of_weeks for d in dates]
    sampled_dates = dates[cond]
    return sampled_dates


def main():
    city_list = import_city_list('../data/city_list.csv')
    date_list = create_date_list()

    for city in city_list:
        for num_guests in NUM_GUESTS:
            for date in date_list:
                params = {
                    'city' : city['city'],
                    'state' : city['state'],
                    'country' : city['country'],
                    'checkin' : date.date().strftime('%m-%d-%Y'),
                    'checkout': (date + DateOffset(2)).strftime('%m-%d-%Y'),
                    'guests'  : num_guests,
                    'start_page' : 1,
                    'end_page'   : NUM_PAGES
                    }

                print "%s > %s > %s" % (city['city'], num_guests, date.date().strftime('%m-%d-%Y'))
                
                air_sr = AirBnBSearchResult(db=DB, coll=COLL, params=params)
                air_sr.scrape_all_results()

                time.sleep(2.5)    # so hopefully I don't get booted from AirBnB


if __name__=="__main__":
    main()