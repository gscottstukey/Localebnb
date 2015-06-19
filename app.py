from flask import Flask
from flask import render_template
from flask import request
from pymongo import MongoClient
import pickle
app = Flask(__name__)
from libs.airbnbsearchresult import AirBnBSearchResult 
from libs.airbnblisting import AirBnBListing

DB_NAME = 'airbnb'
SEARCH_COLL_NAME = 'search'
LISTING_COLL_NAME = 'listings'
AIR_S = AirBnBSearchResult(db_name=DB_NAME, coll_name=SEARCH_COLL_NAME)
AIR_L = AirBnBListing(db_name=DB_NAME, coll_name=LISTING_COLL_NAME)

# Load my pickled models into the app
# TFIDF = pickle.load(open('models/tfidf.pkl'))
# MNB_ARTSY = pickle.load(open('models/mnb_artsy.pkl'))
# MNB_DINING = pickle.load(open('models/mnb_dining.pkl'))
# MNB_NIGHTLIFE = pickle.load(open('models/mnb_nightlife.pkl'))
# MNB_SHOPPING = pickle.load(open('models/mnb_shopping.pkl'))


# G SCOTT: Is this the most efficient way to do this?
CITIES = [{'id':1, 'label':"San Francisco", 'city':'San-Francisco', 'state':'CA', 'country':'United-States'},
          {'id':2, 'label':"New York", 'city':'New-York', 'state':'NY', 'country':'United-States'}]

CITY_DICT = {x['city']:{'id':x['id'], 'label':x['label'], 'state':x['state'], 'country':x['country']} for x in CITIES}

TRAITS = ['artsy', 'shopping', 'dining', 'nightlife']
# G SCOTT: Make this a function
WEIGHTS = [{'id':'0', 'value':0.0, 'label':"exclude"},
                   {'id':'1', 'value':0.5, 'label':"light"},
                   {'id':'2', 'value':1.0, 'label':"average"},
                   {'id':'3', 'value':2.0, 'label':"heavy"}]


@app.route('/')
def page():
    return render_template('index.html', cities=CITIES, traits=TRAITS, trait_weights=WEIGHTS)


@app.route('/search', methods=['POST'])
def page2():
    city = request.form['cityRadio']
    num_guests = request.form['numGuests']
    artsy_weight = request.form['artsyRadio']
    shopping_weight = request.form['shoppingRadio']
    dining_weight = request.form['nightlifeRadio']
    nightlife_weight = request.form['nightlifeRadio']
    checkin = '06-16-2015'
    
    params = {'city':city,
              'state':CITY_DICT[city]['state'],
              'country':CITY_DICT[city]['country'],
              'checkin': checkin, 
              'checkout': checkin,
              'guests':num_guests}

    AIR_S.set_params(params)
    AIR_S.pull_one_from_df()

    # return render_template('index.html')
    # return ' '.join([city, str(num_guests), artsy_weight, shopping_weight, dining_weight, nightlife_weight])
    return AIR_S.r.content


@app.route('/classified', methods=['POST'])
def model_results():
    # data = request.form['article']
    data = "YAY"
    data = str(data)

    # return "Your article should be included in the <b>%s</b> section" % model.predict(vectorized_data)[0]
    return "YAY"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)