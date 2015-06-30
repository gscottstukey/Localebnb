# [Localebnb](http://github.com/gscottstukey/Localebnb): Airbnb Contexual Recommendation App


### G Scott Stukey, Zipfian Academy, April 2015 - July 2015


## Overview
The motivation for my project stems from my frustrations with Airbnb's search functionality while booking in Montreal.  I knew that I wanted to stay in an artsy neighborhood & away from touristy areas.  While I could filter by neighborhood, I had no idea what neighborhoods met my criteria!

Localebnb aims to be a contextual recommender for Airbnb.

Using neighborhood guides put together for NYC & SF, I built an app that predicts the whether the neighborhood has a specified trait, and use that information to score & sort the search results provided by Airbnb.


##How to Use
TBD


## Dataset
I scraped 4 types of pages across Airbnb for data:
* Search Result Pages (e.g. https://www.airbnb.com/s/Portland--OR--United-States?checkin=09%2F18%2F2015&checkout=09%2F21%2F2015)
* Listing Pages (e.g. https://www.airbnb.com/rooms/14584)
* [City Guides](https://www.airbnb.com/locations) (e.g. https://www.airbnb.com/locations/san-francisco)
* Neighborhood Guides (https://www.airbnb.com/locations/san-francisco/duboce-triangle)

I mapped listings to neighborhoods & neighborhoods to traits to come up with my labeled dataset (listings -> traits). I then cleaned up the description using NLP techniques, vectorized the description using TF-IDF, and used a Naive Bayes model on the vectorized description to make the predictions. Interestingly enough, this methodology ourperformed Random Forests & Gradient Boosted Trees against the same TF-IDF data, which might denote overfitting on the part of the tree-based model. 

I also ran a Word2Vec model against the cleaned description & the neighborhood, howerver due to the size of my corpus, as well as the attributes I was trying to model, this data proved to not be of high value to me.


## Additional Applications of this methodology.

There are many applications for this data & methodology.

First, for the business & user, is the inclusion of additional context into the search result & direct business outcomes derived from the added relevence. Under an assumption of users having scroll fatigue & page fatigue, surfacing the most relevent searches earlier could drive incremental rentals. In addition, all things equal this would likely increase a user's satisfaction with the Airbnb app.

note: the above would need to be tested against existing systems, as the potential negatives may include the increase of options (i.e. the paradox of choice) and/or the contextualized search lowers the costs of the listings that people book at.

Second would be for the content team, who could leverage a neighborhood model to help create content for '2nd-tier cities' (i.e. cities without a neighborhood guide), as well as new cities that Airbnb expands into.  They could use this model to create content, or give them some initial content to work with.

Thirdly, as a lister resource, provide suggestions on key words in the listing, and provide recommendations on alternatives that might have been shown to drive higher booking rates. For (a contrived) example, stating an "artisanal coffee shop" is nearby may drive higher bookings than if a "hipster coffee shop" is near, assuming that "artisanal" shows up in the set of similar words to "hipster". The counter argument may be that this would make listings more homogenous, an assumed negative to people.

Word2Vec Bonus: I'd be excited to see what Word2Vec & Doc2Vec could do with Airbnb's description & comment corpus.  Imagine LabeledSenteces() with labels of the neighborhood, listing_id, city, etc. Airbnb could find listing similarities across neighborhoods, cities, etc. Of interest might be flags for whether the listing is a "successful" listing (by whatever definition of "successful" Airbnb might want to use). Airbnb could find word flags that are most-similar to successful (& unsucessful) listings.  They might offer paid services for active users who are deemed unsuccessful, to improve their listing description based on successful words across Airbnb, as well as words successful for the listing's neighborhood. 


## Potential Next Steps
1. Data-related:
  * Scrape more data across more cities & retrain models based on a larger training set

2. Code-related:
  * As of now, the features are hard coded into the app. Considerations could be made to ensure that any number of each features could be accomodated.

3. Analysis-related:
  * Currently the app only uses the description to model artsy. One could reduce the dimentionality of the text and encorporate additional features to predict neighborhood traits (e.g. the % of listings that are a room vs. a full home, ammeneties offered, price, price relative to nearby hoods/neighborhood averages, etc)
  * Of interest, it would be interesting to use a larger corpus's Doc2Vec model trained against the neighborhood trait, give the search results rankings for their similarity to the trait, and use those predictions as features into a new prediction model. 

4. App-related:
  * TBD


## Toolkit + Credits
1. [MongoDB](http://www.mongodb.org/) - a NoSQL database; used for storing my scrapes
  * [pymongo](https://github.com/mongodb/mongo-python-driver) - A python wrapper for MongoDB
2. [Requests](http://docs.python-requests.org/en/latest/) - A python library used in scraping tasks for getting webpage html.
3. [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) - A python html-parsing library. It makes it much easier to pull out particular elements from a complex webpage.
4. [pickle](https://docs.python.org/2/library/pickle.html) - A python library for serializing objects; used for saving requests objects for later parsing
5. [Flask](http://flask.pocoo.org/) - a python framework for creating web apps.
6. [NumPy](http://www.numpy.org/) - the fundamental package for scientific computing with Python.; used for math functionality
7. [time](https://docs.python.org/2/library/time.html) - A python library for time related functions; used for pausing the app
8. [datetime](https://docs.python.org/2/library/datetime.html) - A python library for datetime related functions; used for parsing datetime objects in Pandas
9. [pandas](http://pandas.pydata.org/) - provides high-performance, easy-to-use data structures and data analysis tools for Python; used for basic data manipulation & some file reading
10. [iPython & iPython Notebook](http://ipython.org/notebook.html) - IDE for python; used to test code snippets & explore data
11. [gensim's Word2Vec & Doc2Vec](* Word2Vec - [https://radimrehurek.com/gensim/models/word2vec.html]) - a deep learning modeling library to help discern the definition of words. while not included in the final app, some EDA & testing was used with this model. With a larger corpus, it's likely that a Doc2Vec model would be used.

Also, [Galvanize (a.k.a. Zipfian Academy)](http://www.zipfianacademy.com/) for an amazing education. 

A special thank you (& apology) to Airbnb, whose amazing service was an inspiration for this project. I hope you are inspired by this project enough to include this functionality in your search

## Glossary of Terms
* [TF-IDF aka Term Frequency - Inverse Document Frequency](http://en.wikipedia.org/wiki/Tf%E2%80%93idf)
* [Naive-Bayes Classification](https://en.wikipedia.org/wiki/Naive_Bayes_classifier)
* [Word2Vec](http://code.google.com/p/word2vec/) - I *::heartemoji::* Word2Vec