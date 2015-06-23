from flask import Flask
from flask import render_template
from flask import request
from pymongo import MongoClient
import pickle
app = Flask(__name__)
from libs.airbnb.airbnbsearchresult import AirBnBSearchResult 
from libs.airbnb.airbnblisting import AirBnBListing
from libs.airbnb.app_helper import initialize_rank_scores
import numpy as np

DB_NAME = 'airbnb'
SEARCH_COLL_NAME = 'search'
LISTING_COLL_NAME = 'listings'
DEFAULT_RANK_SCORES = initialize_rank_scores()

AIR_S = AirBnBSearchResult(db_name=DB_NAME, coll_name=SEARCH_COLL_NAME)
AIR_L = AirBnBListing(db_name=DB_NAME, coll_name=LISTING_COLL_NAME)

# Load my pickled models into the app
TFIDF = pickle.load(open('models/tfidf.pkl'))
MNB_ARTSY = pickle.load(open('models/mnb_artsy.pkl'))
MNB_DINING = pickle.load(open('models/mnb_dining.pkl'))
MNB_NIGHTLIFE = pickle.load(open('models/mnb_nightlife.pkl'))
MNB_SHOPPING = pickle.load(open('models/mnb_shopping.pkl'))
DEFAULT_VAL = .1


# G SCOTT: Is this the most efficient way to do this?
CITIES = [{'id':1, 'label':"San Francisco", 'city':'San-Francisco', 'state':'CA', 'country':'United-States'},
          {'id':2, 'label':"New York", 'city':'New-York', 'state':'NY', 'country':'United-States'}]

CITY_DICT = {x['city']:{'id':x['id'], 'label':x['label'], 'state':x['state'], 'country':x['country']} for x in CITIES}

TRAITS = ['artsy', 'shopping', 'dining', 'nightlife']
# G SCOTT: Make this a function
WEIGHTS = [{'id':'1', 'value':-1.0, 'label':"hate"},
           {'id':'2', 'value':-0.5, 'label':"meh"},
           {'id':'3', 'value':0.0, 'label':"average"},
           {'id':'4', 'value':0.5, 'label':"like"},
           {'id':'5', 'value':1.0, 'label':"love"}]


@app.route('/')
def index():
    return render_template('index.html', cities=CITIES, traits=TRAITS, trait_weights=WEIGHTS)


@app.route('/search', methods=['POST'])
def search():
    liveflag = request.form['livecacheRadio'] == "live"

    if request.form['cityRadio'] != "OTHER":
        city = request.form['cityRadio']
        state = CITY_DICT[city]['state']
    else:
        city_input = request.form['cityWriteIn']
        city, state = [x.strip() for x in city_input.split(', ')]
        city = city.replace(' ','-')    # Turn the city into AirBnB format

    checkin_input = request.form['checkinDate'].split('-')
    checkout_input = request.form['checkoutDate'].split('-')
    checkin = "-".join([checkin_input[1], checkin_input[2], checkin_input[0]])
    checkout = "-".join([checkout_input[1], checkout_input[2], checkout_input[0]])
    # checkin = '06-30-2015'    # Update with less contrived example
    num_guests = request.form['numGuests']

    artsy_weight = float(request.form['artsyRadio'])
    shopping_weight = float(request.form['shoppingRadio'])
    dining_weight = float(request.form['diningRadio'])
    nightlife_weight = float(request.form['nightlifeRadio'])
    
    
    # G SCOTT: Add checkout to params
    params = {'city':city,
              'state':state,
              'country':'United-States',
              'checkin': checkin, 
              'checkout': checkout,
              'guests':num_guests,
              'price_max':400}

    AIR_S.set_params(params)

    if liveflag:
        AIR_S.scrape_from_web(insert_into_db = False)    # Need to confirm that the scrape went well
    else:
        AIR_S.pull_one_from_db()

    listings = AIR_S.extract_listing_ids()
    listing_dict = {l:{'id':l} for l in listings}
    thumbnail_data = AIR_S.extract_thumbnail_data()

    #initialize values for finding the middle of the map
    max_lat = -360.0
    min_lat = 360.0
    max_lng = -360.0
    min_lng = 360.0

    for i, listing in enumerate(listings):
        if liveflag:
            AIR_L.scrape_from_web(listing_id=listing, pause_between_pages=2)
        else:
            AIR_L.pull_from_db(listing_id=listing)

        listing_dict[listing]['url'] = AIR_L.url
        listing_dict[listing]['default_position'] = i+1
        listing_dict[listing]['default_score'] = DEFAULT_RANK_SCORES[i]
        
        listing_dict[listing]['thumbnail_img'] = thumbnail_data[listing]['thumbnail_img']
        listing_dict[listing]['blurb'] = thumbnail_data[listing]['blurb']
        listing_dict[listing]['thumbnail_price'] = thumbnail_data[listing]['thumbnail_price']
        listing_dict[listing]['listing_type'] = thumbnail_data[listing]['listing_type']
        listing_dict[listing]['lng'] = thumbnail_data[listing]['lng']        
        listing_dict[listing]['lat'] = thumbnail_data[listing]['lat']

        max_lng = max(max_lng, float(listing_dict[listing]['lng']))
        min_lng = min(min_lng, float(listing_dict[listing]['lng']))
        max_lat = max(max_lat, float(listing_dict[listing]['lat']))
        min_lat = min(min_lat, float(listing_dict[listing]['lat']))


        if liveflag:
            description_clean = AIR_L._extract_clean_description()
            if description_clean != "":
                vectorized_desc = TFIDF.transform([description_clean]).toarray()
                listing_dict[listing]['is_artsy'] = int(MNB_ARTSY.predict(vectorized_desc)[0])
                listing_dict[listing]['is_shopping'] = int(MNB_SHOPPING.predict(vectorized_desc)[0])
                listing_dict[listing]['is_dining'] = int(MNB_DINING.predict(vectorized_desc)[0])
                listing_dict[listing]['is_nightlife'] = int(MNB_NIGHTLIFE.predict(vectorized_desc)[0])
            else:
                listing_dict[listing]['is_artsy'] = DEFAULT_VAL
                listing_dict[listing]['is_shopping'] = DEFAULT_VAL
                listing_dict[listing]['is_dining'] = DEFAULT_VAL
                listing_dict[listing]['is_nightlife'] = DEFAULT_VAL   
                      
        elif not liveflag and 'description_clean' in AIR_L.d:
            description_clean = AIR_L.d['description_clean']
            vectorized_desc = TFIDF.transform([description_clean]).toarray()
            listing_dict[listing]['is_artsy'] = int(MNB_ARTSY.predict(vectorized_desc)[0])
            listing_dict[listing]['is_shopping'] = int(MNB_SHOPPING.predict(vectorized_desc)[0])
            listing_dict[listing]['is_dining'] = int(MNB_DINING.predict(vectorized_desc)[0])
            listing_dict[listing]['is_nightlife'] = int(MNB_NIGHTLIFE.predict(vectorized_desc)[0])
        else:
            # G SCOTT: consider checking to see if the neighborhood is artsy or not based on my data
            listing_dict[listing]['is_artsy'] = DEFAULT_VAL
            listing_dict[listing]['is_shopping'] = DEFAULT_VAL
            listing_dict[listing]['is_dining'] = DEFAULT_VAL
            listing_dict[listing]['is_nightlife'] = DEFAULT_VAL

        score_multiplier = listing_dict[listing]['is_artsy'] * artsy_weight + \
                         listing_dict[listing]['is_shopping'] * shopping_weight + \
                         listing_dict[listing]['is_dining'] * dining_weight + \
                         listing_dict[listing]['is_nightlife'] * nightlife_weight

        listing_dict[listing]['score'] = DEFAULT_RANK_SCORES[i] + score_multiplier


    sorted_listings = sorted(listing_dict, key=lambda x:listing_dict[x]['score'], reverse=True)
    for i, listing in enumerate(sorted_listings):
        listing_dict[listing]['position'] = i+1

    map_center = ((max_lat+min_lat)/2, (max_lng+min_lng)/2)
    # return str(checkin_test)
    # return city_text
    # return str(city['value'])
    return render_template('search.html', sorted_listings = sorted_listings, listing_dict=listing_dict, map_center=map_center)
    # return str(listing_dict)
    # return AIR_S.r.content    # For debugging: used to show the cached AirBnB search from MongoDB
    

@app.route('/listing/<listing_id>')
def listing_page(listing_id):
    return listing_id

@app.route('/about', methods=['POST'])
def about():
    return "https://www.linkedin.com/in/gscottstukey"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)