"""
This script is used to grab neighborhoods from cities
* takes in a file ('../data/city_list.csv')
* grabs the neighborhoods we wish to scrape from the file
* scrapes AirBnB's city guide for each of the cities to grab the hoods

DEPENDENCIES:
1) '../data/city_list.csv'

    import pandas as pd
    df = pd.read_csv('../data/city_list.csv')
    print df.head(2)

       city_id           city state        country
    0        1  San-Francisco    CA  United-States
    1        2       New-York    NY  United-States

POTENTIAL ISSUES:
1) city_id:
    * city_id is unique to this project; it is not based on AirBnB's city ids 
2) neighborhood_id:
    * arbitrarily assigns neighborhood_ids based on the order they were scraped 
    * if content changes, then all dependencies are impacted
    * if were to recreate, AirBnB's neighborhood_ids on the scrape and use that field

NOTES: make sure mongod running. use `sudo mongod` in terminal
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

NEIGHBORHOOD_URL = 'https://www.airbnb.com/locations/'
CITY_FILEPATH = '../data/city_list.csv'
NEIGHBORHOOD_OUTPUT = '../data/neighborhood_list.csv'

def main():
    df = pd.read_csv(CITY_FILEPATH)
    city_tuples = [(city_id, city.lower()) for city_id, city in zip(df['city_id'], df['city'])]
    
    neighborhoods = []

    for city_id, city in city_tuples:
        r = requests.get(NEIGHBORHOOD_URL + city)
        soup = BeautifulSoup(r.content)
        neighborhood_list_raw = soup.find('div', {'class':'neighborhood-list'}).find_all('a')[1:]
        for hood in neighborhood_list_raw:
            hood_name = hood.get_text()
            hood_url = hood['href']
            neighborhoods.append((hood_name, hood_url, city_id, city))

    hood_df = pd.DataFrame(neighborhoods, columns=["neighborhood", "neighborhood_url", "city_id", "city"])
    hood_df.to_csv(NEIGHBORHOOD_OUTPUT, index=True, index_label='neighborhood_id')


if __name__=="__main__":
    main()

