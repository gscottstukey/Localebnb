import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.cross_validation import train_test_split
from airbnb.airbnbneighborhood import AirBnBNeighborhood
from airbnb.airbnblisting import AirBnBListing

# Ran rto find models
# MAX_DF_LIST = [.5, .66, .75, .83, .90, 1.0]
# MAX_FEATURE_LIST = [500, 1000, 2000, 3000, 4000, 5000, 8000]
# MIN_DF_LIST = [1,2]
# RANDOM_STATE_LIST = [1, 42, 1337]    # lulz

# Ran as final solution
MAX_DF_LIST = [.90]
MAX_FEATURE_LIST = [8000]
MIN_DF_LIST = [2]
RANDOM_STATE_LIST = [55]

TRAIT_LIST = ['artsy', 'shopping', 'dining', 'nightlife']


def load_data():
    air_hood = AirBnBNeighborhood(db_name='airbnb', coll_name='neighborhoods')
    hood_df = pd.DataFrame(list(air_hood.coll.find({})))

    air_listing = AirBnBNeighborhood(db_name='airbnb', coll_name='listings')
    listing_df = pd.DataFrame(list(air_listing.coll.find({})))
    listing_df = listing_df[listing_df['description_raw'].isnull() == False]

    merged_df = listing_df.merge(right=hood_df[['neighborhood', 'city', 'traits']],
                                 on='neighborhood', suffixes=('', '_copy'))
    return merged_df


def add_features(df):
    new_df = df.copy()
    new_df['artsy'] = ['Artsy' in x for x in new_df['traits']]
    new_df['shopping'] = ['Shopping' in x for x in new_df['traits']]
    new_df['dining'] = ['Dining' in x for x in new_df['traits']]
    new_df['nightlife'] = ['Nightlife' in x for x in new_df['traits']]
    return new_df


def run_svc(X_doc, y, svc, max_df, max_features, min_df, random_state):
    # split the data
    X_train_doc, X_test_doc, y_train, y_test = train_test_split(X_doc, y, random_state=random_state)

    # Vectorize the training data
    tfidf = TfidfVectorizer(max_df=max_df, max_features=max_features, min_df=min_df)
    vectorized_corpus = tfidf.fit_transform(X_train_doc)
    X_train = vectorized_corpus.toarray()

    # fit the SVM model
    svc.fit(X_train, y_train)
    train_score = svc.score(X_train, y_train)

    # score it against the test data
    X_test = tfidf.transform(X_test_doc).toarray()
    test_score = svc.score(X_test, y_test)

    return (max_df, max_features, min_df, random_state, train_score, test_score)


def run_grid_search(X_doc, y, svc, trait):
    results = []

    for max_df in MAX_DF_LIST:
        for max_features in MAX_FEATURE_LIST:
            for min_df in MIN_DF_LIST:
                for random_state in RANDOM_STATE_LIST:
                    result = run_svc(X_doc, y, svc, max_df, max_features, min_df, random_state)
                    print result
                    results.append(result)

    results_df = pd.DataFrame(results, columns=['max_df', 'max_features', 'min_df', 'random_state', 'train_score', 'test_score'])    
    results_df.to_csv('../models/%s_svc_results.csv' % trait)

    results_df = results_df.groupby(by=['max_df', 'max_features', 'min_df', 'random_state'], 
                                    as_index=False).mean()

    max_test_score = max(results_df['test_score'])
    max_test_results_df = results_df[results_df['test_score'] == max_test_score]

    return max_test_results_df.reset_index()


def tiebreaker(svc, max_test_results_df, X_doc, y):
    tiebreaker_df = max_test_results_df.copy()
    tiebreaker_df['final_score'] = 0
    for i in tiebreaker_df.index:
        max_df = tiebreaker_df['max_df'][i]
        max_features = tiebreaker_df['max_features'][i]
        min_df = tiebreaker_df['min_df'][i]
        random_state = tiebreaker_df['random_state'][i]

        tfidf = TfidfVectorizer(max_df=max_df, max_features=max_features, min_df=min_df)
        vectorized_corpus = tfidf.fit_transform(X_doc)
        X = vectorized_corpus.toarray()

        svc.fit(X, y)
        tiebreaker_df['full_score'] = svc.score(X, y)

    tiebreaker_df.sort('full_score', inplace=True)

    return tiebreaker_df.reset_index()


def run_winning_model(X_doc, y, max_df, max_features, min_df, svc, trait):
    print
    print "THE WINNING MODEL IS FOR %s IS: %s, %s, %s" % (trait, max_df, max_features, min_df)

    tfidf = TfidfVectorizer(max_df=max_df, max_features=max_features, min_df=min_df)
    vectorized_corpus = tfidf.fit_transform(X_doc)

    tfidf_pickle_file = open('../models/tfidf_svc_%s.pkl' % trait, 'w')
    pickle.dump(tfidf, tfidf_pickle_file)
    tfidf_pickle_file.close()

    X = vectorized_corpus.toarray()

    svc.fit(X, y)
    svc_pickle_file = open('../models/svc_%s_final.pkl' % trait, 'w')
    pickle.dump(svc, svc_pickle_file)
    svc_pickle_file.close()


def main():
    df = load_data()
    feature_df = add_features(df)
    X_doc = list(feature_df['description_clean'])
    svc = LinearSVC()

    for trait in TRAIT_LIST:
        y = feature_df[trait]
        max_test_results_df = run_grid_search(X_doc, y, svc, trait)

        if len(max_test_results_df) > 1:
            max_test_results_df = tiebreaker(svc, max_test_results_df, X_doc, y)

        max_df = max_test_results_df['max_df'][0]
        max_features = max_test_results_df['max_features'][0]
        min_df = max_test_results_df['min_df'][0]

        run_winning_model(X_doc=X_doc, y=y, max_df=max_df, 
                          max_features=max_features, min_df=min_df, 
                          svc=svc, trait=trait)


if __name__ == "__main__":
    main()
