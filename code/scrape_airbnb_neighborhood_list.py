import pandas as pd
import requests
from bs4 import BeautifulSoup

NEIGHBORHOOD_URL = 'https://www.airbnb.com/locations/'
CITYLIST_FILEPATH = '../data/city_list.csv'
NEIGHBORHOOD_OUTPUT = '../data/neighborhood_list.csv'

def import_cities(filepath):
    df = pd.read_csv(filepath)
    city_list_tuples = [(city_id, city.lower()) for city_id, city in zip(df['city_id'], df['city'])]
    return city_list_tuples


def main():
    city_list_tuples = import_cities(CITYLIST_FILEPATH)
    
    neighborhoods = []

    for city_id, city in city_list_tuples:
        r = requests.get(NEIGHBORHOOD_URL + city)
        soup = BeautifulSoup(r.content)
        neighborhood_list_raw = soup.find('div', {'class':'neighborhood-list'}).find_all('a')[1:]
        for hood in neighborhood_list_raw:
            neighborhoods.append((hood.get_text(), hood['href'], city_id, city))


    df = pd.DataFrame(neighborhoods, columns=["neighborhood", "neighborhood_url", "city_id", "city"])
    df.to_csv(NEIGHBORHOOD_OUTPUT, index=True, index_label='neighborhood_id')


if __name__=="__main__":
    main()