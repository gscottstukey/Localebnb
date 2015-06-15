'''6.6.2015: Scrap when testing out the airbnbsearchresult class'''

%load_ext autoreload
%autoreload 2

from airbnbsearchresult import AirBnBSearchResult

params = {}
params['city'] = "San-Francisco"
params['state'] = "CA"
params['country'] = "United-States"

params['checkin'] = "06/25/2015"
params['checkout'] = "06/27/2015"

params['guests'] = 2
params['start_page'] = 1
params['end_page'] = 1
params['price_max'] = 400

airsr = AirBnBSearchResult(db = 'airbnb_test', coll = 'search', params=params)