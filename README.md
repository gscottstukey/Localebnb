# [Localebnb](http://www.localebnb.co): An Airbnb Contexual Recommendation App

### G Scott Stukey, Zipfian Academy, April 2015 - July 2015

![](/static/img/presentation_title.jpg)


## Overview

The motivation was: When booking a private residence, how do you find the perfect neighborhood?

It stems from my personal frustrations with Airbnb's search functionality while booking in Montreal.  I knew that I wanted to stay in an trendy neighborhood, but away from tourists & nightlife.  While I could search & filter Airbnb's search results by neighborhood, I had no idea what neighborhoods met my criteria!

Localebnb aims to be that contextual recommender for Airbnb.

Using Airbnb listing descriptions (features) + Airbnb's neighborhood guides for traits (target ), I built an app that predicts whether a listing is in a neighborhood with a specified trait, and then I use that information to score & re-sort the default search results provided by Airbnb.

![](/static/img/presentation_solution.jpg)

##How to Use

*Note: it is best to use this app on desktop with a large window*
* Go to the [Localebnb app](http://localebnb.co)
* Enter in your search criteria (city, dates, guests), as well as neighborhood trait preferences ('is artsy, 'has shopping', etc)
* Click "Search Airbnb" - this scrapes Airbnb's search results & listings, predicts the traits for each listing, then scores & re-sorts the search results
* On the search result page, you can resort by the column header. You can also change your preferences and see how that changes the search results.
* If you hover over a listing, a pop-up appears in the map. You can click to the Airbnb page of the listing, as well as additional information about the listing's description


## Dataset

![](/img/presentation_methodology.jpg)

I scraped 4 types of pages across Airbnb for data:
* Search Result Pages (e.g. https://www.airbnb.com/s/Portland--OR--United-States?checkin=09%2F18%2F2015&checkout=09%2F21%2F2015)
* ~4000 Listing Pages (e.g. https://www.airbnb.com/rooms/14584)
* [City Guides](https://www.airbnb.com/locations) for SF & NYC (e.g. https://www.airbnb.com/locations/san-francisco)
* Neighborhood Guides for all neighborhoods(https://www.airbnb.com/locations/san-francisco/duboce-triangle)

I mapped listings to neighborhoods & neighborhoods to traits to come up with my labeled dataset (listings -> traits). I then cleaned up the description using NLP techniques, vectorized the description using TF-IDF, and used a variety of models on this information. SVM's provided the highest accuracy (~78-82%, a 5 pt lift over naive bayes). Interestingly enough, when attempting to create a 'majority vote' ensemble (NB + SVM + Random Forest), the accuracty decreased slight against individual models. This denotes that each of these 3 models are able to pick up features that neither of the other 2 are able to.

I also ran a Doc2Vec (Word2Vec) model using the cleaned descriptions as sentences & the neighborhood traits & cities as label. Howerver, due to the size of my corpus, this data proved insufficient for for use in Localebnb.  With a much larger training set, I'd love to revisit this method.


## Additional Applications of this methodology.

There are many applications for this data & methodology.

Why Airbnb should implement this:
* **User Value:** Increase user satisfaction by increasing relevance
* **Business Value (revenue):** Increase booking rate by reducing bounces (click fatigue)
* **Business Value (content team):** Guide creation of neighborhood guides in new cities
* ***Word2Vec Bonus
note: The inclusion of a trait model for search results would need to be tested against existing systems. The potential negatives may include the increase of options (i.e. the paradox of choice) and/or the contextualized search lowers the costs of the listings that people book at.

reference:

* https://www.airbnb.com/support/article/39
* http://nerds.airbnb.com/location-relevance/
* http://nerds.airbnb.com/host-preferences/


## Extensions
* Scrape more descriptions across more cities beyond SF & NYC (as neighborhood names & major street names were highly predictive in most models)
* Include additional listing information in models
* Make neighborhood traits more fluid by giving partial weight to nearby neighborhoods (utilizing graph analytics)
* Revisit Doc2Vec model on a larger corpus & potential applications of Doc2Vec


## Toolkit + Credits
1. [iPython & iPython Notebook](http://ipython.org/notebook.html) - IDE for python; used to test code snippets & explore data
2. [MongoDB](http://www.mongodb.org/) - a NoSQL database; used for storing my scrapes
  * [pymongo](https://github.com/mongodb/mongo-python-driver) - A python wrapper for MongoDB
3. [Requests](http://docs.python-requests.org/en/latest/) - A python library used in scraping tasks for getting webpage html.
4. [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) - A python html-parsing library. It makes it much easier to pull out particular elements from a complex webpage.
5. [pickle](https://docs.python.org/2/library/pickle.html) - A python library for serializing objects; used for saving requests objects for later parsing
6. [time](https://docs.python.org/2/library/time.html) & [datetime](https://docs.python.org/2/library/datetime.html) - Python libraries for time related functions; used for logging times of scrapes & pausing the scripts between scraping
7.  - A python library for datetime related functions; used for parsing datetime objects in Pandas
8. [pandas](http://pandas.pydata.org/) - provides high-performance, easy-to-use data structures and data analysis tools for Python; used for basic data manipulation & some file reading
9. [NumPy](http://www.numpy.org/) - the fundamental package for scientific computing with Python.; used for math functionality
10. [scikit-learn](http://scikit-learn.org/stable/) - data modeling library
11. [nltk](http://www.nltk.org/) - library for NLP
10. [Flask](http://flask.pocoo.org/) - a python framework for creating web apps.
11. [gensim's Word2Vec & Doc2Vec](* Word2Vec - [https://radimrehurek.com/gensim/models/word2vec.html]) - a deep learning modeling library to help discern the definition of words. while not included in the final app, some EDA & testing was used with this model. With a larger corpus, it's likely that a Doc2Vec model would be used.
12. [moz](https://moz.com/blog/google-organic-click-through-rates-in-2014) - the Google SERP CTR by position served as an inspiration & starting point for my scoring system.

Also, [Galvanize (a.k.a. Zipfian Academy)](http://www.zipfianacademy.com/) & its instructors for an amazing education. 

A special thank you (/slash/ apology) to Airbnb, whose amazing service was an inspiration for this project. I hope you are inspired by Localebnb to explore include neighborhood description search/filtering functionality in your search

-G Scott Stukey
* @gscottstukey
"I like my data like I like my denim... raw"

## Glossary of Terms
* [TF-IDF aka Term Frequency - Inverse Document Frequency](http://en.wikipedia.org/wiki/Tf%E2%80%93idf)
* [Naive-Bayes Classification](https://en.wikipedia.org/wiki/Naive_Bayes_classifier)
* [Support Vector Machines](https://en.wikipedia.org/wiki/Support_vector_machine)
* [Word2Vec](http://code.google.com/p/word2vec/) - I ::heartemoji:: Word2Vec so hard