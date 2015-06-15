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

So with that, I went back and ran my scrape_airbnb_search_results.py a a 2nd time using updated NUM_PAGES in airbnbsearchresult. I also added a pause_between_pages parameter to the scrape_all_results method (in case I want to pause). I also made the pickling & record insertion dependent on whether there was a 200 status code.  

WANT:
Still wish I had an easier way to check if the scrape errored out or not.  Perhaps after run 3 I'll be able to find that out

