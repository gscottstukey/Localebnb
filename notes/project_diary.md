#project notes:

###Before 6.12:



###6.12

DID:
I created '1_clean_explore_mongo_results.ipynb', to explore the results from my previous scrape. Low & behold, I find that when I look at the number of listings, I actually don't have that many... FUCK!

    ''''
        print len(listing_ids)    # list of all ids I've found
        29851

        print len(set(listing_ids))    # unique ids
        2779
    '''

So with that, I went back and ran my scrape_search_results.py a a 2nd time using updated NUM_PAGES in *searchresult.py. I also added a pause_between_pages parameter to the scrape_all_results method (in case I want to pause). I also made the pickling & record insertion dependent on whether there was a 200 status code.  

WANT:
* Still wish I had an easier way to check if the scrape errored out or not.  Perhaps after run 3 I'll be able to find that out


###6.15

So I was able to scrape all the neighborhoods! YAY!
    '''
    MongoDB (console):
    > db.neighborhoods.count()
    102
    '''

This was done by creating *neighborhood.py and running it with scrape_*_neighborhood_list.py & scrape_*_neighborhoods. I got some good information that's ready to parse, which I might do tonight or tomorrow.

In addition, I reran my scrape_*_search_results.py after my mongodb database got corrupted. I also grabbed all the listings. I put all the id's in the 'listings' collection. This was done using parse_listings_from_search.py

    '''
    MongoDB (console):
    > db.search.count()
    5200

    iPython (workbook 1):
    print len(listing_ids)    # list of all ids I've found
    44985
    print len(set(listing_ids))    # unique ids
    4217

    > db.listings.count()
    4228
    '''
 

I also made great headway into *listing.py class. It's the cleanest class I have. Unfortunately, I'm getting blcoked is blocking me. Womps. I've pull ~ 500 of my 4k. I have enough to play around with while I run the script sporadically.

    '''
    iPython (workbook 2):
    air_listing.coll.find({'time':{'$gt':0}},{'content':1}).count()
    523    # As of Mon, 6/15 @ 744
    '''

TODO:
* Create methods to parse through a listing & save that information back to MongoDB
* Create methods to parse through a neighborhood & save that information back to MongoDB
* Create a file that maps the neighborhood to the listing
* explore the words
* Keep Calm & Scrape On

Night update - SUCCESS! I ran multi_listing_scrape.py and it's been running for hours. 
'''
Mongo (console):
> db.listings.find({'time':{'$gt':0}}).count()
3599   # as of midnight
'''

### 6.18

The last few days have been a blur. I tested a crap ton of models, landing on NB as a nice basic NLP model to start with.  I created models across 4 labels (artsy, dining, shopping, nightlife), as well as my tfidf fit on y entire corpus. 

I'm starting my web app now!  It will likely entail updating my searchresult class. 

Here goes nothing!