from flask import Flask
from flask import render_template
from flask import request
from pymongo import MongoClient
import pickle
app = Flask(__name__)
from libs.airbnb.airbnbsearchresult import AirBnBSearchResult 
from libs.airbnb.airbnblisting import AirBnBListing
from libs.app_helper import initialize_rank_scores
import numpy as np
import time

DB_NAME = 'airbnb2'
SEARCH_COLL_NAME = 'search'
LISTING_COLL_NAME = 'listings'
DEFAULT_RANK_SCORES = initialize_rank_scores()

AIR_S = AirBnBSearchResult(db_name=DB_NAME, coll_name=SEARCH_COLL_NAME)
AIR_L = AirBnBListing(db_name=DB_NAME, coll_name=LISTING_COLL_NAME)
PAUSE_BETWEEN_LISTING_SCRAPES = 1

# Load my pickled models into the app
# TFIDF = pickle.load(open('models/tfidf.pkl'))
# MODEL_ARTSY = pickle.load(open('models/mnb_artsy.pkl'))
# MODEL_DINING = pickle.load(open('models/mnb_dining.pkl'))
# MODEL_NIGHTLIFE = pickle.load(open('models/mnb_nightlife.pkl'))
# MODEL_SHOPPING = pickle.load(open('models/mnb_shopping.pkl'))

TFIDF = pickle.load(open('models/tfidf_svc.pkl'))
MODEL_ARTSY = pickle.load(open('models/svc_artsy_final.pkl'))
MODEL_DINING = pickle.load(open('models/svc_dining_final.pkl'))
MODEL_NIGHTLIFE = pickle.load(open('models/svc_nightlife_final.pkl'))
MODEL_SHOPPING = pickle.load(open('models/svc_shopping_final.pkl'))
WORDS_ARTSY = pickle.load(open('models/top_words_artsy.pkl'))
WORDS_DINING = pickle.load(open('models/top_words_dining.pkl'))
WORDS_NIGHTLIFE = pickle.load(open('models/top_words_nightlife.pkl'))
WORDS_SHOPPING = pickle.load(open('models/top_words_shopping.pkl'))

DEFAULT_VAL = 0.1


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

def score_function(default_score, 
                   is_artsy, artsy_weight, 
                   is_shopping, shopping_weight, 
                   is_dining, dining_weight, 
                   is_nightlife, nightlife_weight):
    score_multiplier = is_artsy * artsy_weight + \
                       is_shopping * shopping_weight + \
                       is_dining * dining_weight + \
                       is_nightlife * nightlife_weight
    return default_score + score_multiplier

@app.route('/')
def index():
    return render_template('index.html', cities=CITIES, traits=TRAITS, trait_weights=WEIGHTS)


@app.route('/search', methods=['POST'])
def search():
    # liveflag = request.form['livecacheRadio'] == "live"

    if request.form['cityRadio'] != "live":
        city = request.form['cityRadio']
        state = CITY_DICT[city]['state']
        liveflag = False
        if city == "New-York":
            checkin = '06-23-2015'
            checkout = '06-25-2015'
        else:
            checkin = '06-30-2015'
            checkout = '07-02-2015'
    else:
        city_input = request.form['cityWriteIn']
        city, state = [x.strip() for x in city_input.split(', ')]
        city = city.replace(' ','-')    # Turn the city into AirBnB format
        liveflag = True
        checkin_input = request.form['checkinDate'].split('-')
        checkout_input = request.form['checkoutDate'].split('-')
        checkin = "-".join([checkin_input[1], checkin_input[2], checkin_input[0]])
        checkout = "-".join([checkout_input[1], checkout_input[2], checkout_input[0]])
    # checkin = '06-30-2015'    # Update with less contrived example
    num_guests = request.form['numGuests']

    artsy_weight_input = request.form['artsyRadio']
    artsy_weight = float(artsy_weight_input)
    shopping_weight_input = request.form['shoppingRadio']
    shopping_weight = float(shopping_weight_input)
    dining_weight_input = request.form['diningRadio']
    dining_weight = float(dining_weight_input)
    nightlife_weight_input = request.form['nightlifeRadio']
    nightlife_weight = float(nightlife_weight_input)
    
    
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
        AIR_S.scrape_from_web_for_app()    # Need to confirm that the scrape went well
        listings = AIR_S.extract_listing_ids()
        if len(listings) > 10:
            listings = listings[:10]
    else:
        AIR_S.pull_one_from_db_cached(city=city)
        if city == "San-Francisco":
            listings = AIR_S.extract_listing_ids()[:11]
        else:
            listings = AIR_S.extract_listing_ids()[:9]


    
    listing_dict = {l:{'id':l} for l in listings}
    thumbnail_data = AIR_S.extract_thumbnail_data()

    #initialize values for finding the middle of the map
    max_lat = -360.0
    min_lat = 360.0
    max_lng = -360.0
    min_lng = 360.0

    for i, listing in enumerate(listings):
        if liveflag:
            AIR_L.scrape_from_web_for_app(listing_id=listing)
            listing_dict[listing]['url'] = AIR_L.url
            time.sleep(PAUSE_BETWEEN_LISTING_SCRAPES)
        else:
            AIR_L.pull_from_db_cached(listing_id=listing)
            # added this after the production DB errored out
            listing_dict[listing]['url'] = AIR_L.BASE_ROOM_URL + listing

        # listing_dict[listing]['url'] = AIR_L.url
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
            description_clean = AIR_L.extract_clean_description()
            if description_clean != "":
                vectorized_desc = TFIDF.transform([description_clean]).toarray()
                listing_dict[listing]['is_artsy'] = int(MODEL_ARTSY.predict(vectorized_desc)[0])
                listing_dict[listing]['is_shopping'] = int(MODEL_SHOPPING.predict(vectorized_desc)[0])
                listing_dict[listing]['is_dining'] = int(MODEL_DINING.predict(vectorized_desc)[0])
                listing_dict[listing]['is_nightlife'] = int(MODEL_NIGHTLIFE.predict(vectorized_desc)[0])
            else:
                listing_dict[listing]['is_artsy'] = DEFAULT_VAL
                listing_dict[listing]['is_shopping'] = DEFAULT_VAL
                listing_dict[listing]['is_dining'] = DEFAULT_VAL
                listing_dict[listing]['is_nightlife'] = DEFAULT_VAL   
                      
        elif 'description_clean' in AIR_L.d:
            description_clean = AIR_L.d['description_clean']
            vectorized_desc = TFIDF.transform([description_clean]).toarray()
            listing_dict[listing]['is_artsy'] = int(MODEL_ARTSY.predict(vectorized_desc)[0])
            listing_dict[listing]['is_shopping'] = int(MODEL_SHOPPING.predict(vectorized_desc)[0])
            listing_dict[listing]['is_dining'] = int(MODEL_DINING.predict(vectorized_desc)[0])
            listing_dict[listing]['is_nightlife'] = int(MODEL_NIGHTLIFE.predict(vectorized_desc)[0])
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

        listing_dict[listing]['score'] = score_function(default_score = DEFAULT_RANK_SCORES[i],
                                                        is_artsy = listing_dict[listing]['is_artsy'], 
                                                        artsy_weight = artsy_weight, 
                                                        is_shopping = listing_dict[listing]['is_shopping'], 
                                                        shopping_weight = shopping_weight, 
                                                        is_dining = listing_dict[listing]['is_dining'], 
                                                        dining_weight = dining_weight, 
                                                        is_nightlife = listing_dict[listing]['is_nightlife'], 
                                                        nightlife_weight = nightlife_weight)


    sorted_listings = sorted(listing_dict, key=lambda x:listing_dict[x]['score'], reverse=True)
    for i, listing in enumerate(sorted_listings):
        listing_dict[listing]['position'] = i+1

    map_center = ((max_lat+min_lat)/2, (max_lng+min_lng)/2)
    # return str(checkin_test)
    # return city_text
    # return str(city['value'])
    return render_template('search.html', sorted_listings = sorted_listings, listing_dict=listing_dict, map_center=map_center, city=city, state=state, traits=TRAITS, trait_weights=WEIGHTS, artsy_weight=artsy_weight, shopping_weight=shopping_weight, dining_weight=dining_weight, nightlife_weight=nightlife_weight)
    # return str(listing_dict)
    # return AIR_S.r.content    # For debugging: used to show the cached AirBnB search from MongoDB
    

@app.route('/listing/<listing_id>')
def listing(listing_id):
    # cached scenario
    # AIR_L.
    # thumbnail_data = AIR_S.extract_thumbnail_data()
    # listing_index = listings.index(listing_id)
    # return str(listing_index)

    AIR_L.pull_from_db_cached(listing_id=listing_id)
    description_raw = AIR_L.d['description_raw']
    description_raw_html = description_raw.replace('\n', "<br>")
    description_clean = AIR_L._clean_description(description_raw)
    artsy_words=[]
    shopping_words=[]
    dining_words=[]
    nightlife_words=[]
    for word in description_clean.split():
        if word in WORDS_ARTSY:
            artsy_words.append(word)
        if word in WORDS_SHOPPING:
            shopping_words.append(word)
        if word in WORDS_DINING:
            dining_words.append(word)
        if word in WORDS_NIGHTLIFE:
            nightlife_words.append(word)

    listing_words_artsy = set(artsy_words)
    listing_words_shopping = set(shopping_words)
    listing_words_dining = set(dining_words)
    listing_words_nightlife = set(nightlife_words)

    # return description_raw_html
    return render_template('listing.html', description_raw_html=description_raw_html, listing_words_artsy=listing_words_artsy, listing_words_shopping=listing_words_shopping, listing_words_dining=listing_words_dining, listing_words_nightlife=listing_words_nightlife)


@app.route('/about')
def about():
    return "https://www.linkedin.com/in/gscottstukey"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

