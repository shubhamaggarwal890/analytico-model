import pickle
import re
from nltk import TweetTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def normalize_tweet(tweet):
    # convert the tweet to lower case
    tweet.lower()
    # convert all urls to sting "URL"
    tweet = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)

    # correct all multiple white spaces and punctuations to a single white space/punctuation
    tweet = re.sub(r'\.{2,}', ' ', tweet)
    tweet = re.sub(r'[\s]+', ' ', tweet)
    tweet = re.sub(r'\!{2,}', '!', tweet)

    # convert "#topic" to just "topic"
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

    # Extracting words(tokens) from the tweet
    twt_token = TweetTokenizer(strip_handles=True)
    token = twt_token.tokenize(tweet)

    # Removing stop words
    stop_words = set(stopwords.words('english'))
    word_list = [tkn for tkn in token if tkn not in stop_words]

    # Using Rule Based Stemmer to find word stems
    stemmer = PorterStemmer()
    stems = [stemmer.stem(word) for word in word_list]

    # Creating a sentence from the stems
    norm_tweet = " ".join(stems)

    return norm_tweet


def model_load(model_path):
    pipeline = pickle.load(open(model_path, 'rb'))
    return pipeline


def prediction(tweet, pipeline):
    normalized_tweet = normalize_tweet(tweet)
    return pipeline.predict_proba([normalized_tweet])[:, 1][0]
