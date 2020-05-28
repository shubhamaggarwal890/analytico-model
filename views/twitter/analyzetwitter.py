import time

import tweepy
import re
from ..tokens.tokens import TWITTER_ACCESS_TOKEN as ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET as ACCESS_TOKEN_SECRET, \
    TWITTER_CONSUMER_KEY as CONSUMER_KEY, TWITTER_CONSUMER_SECRET_KEY as CONSUMER_SECRET_KEY


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("Rate limit error hit")
            time.sleep(15 * 60)


def get_user_timeline(api, username):
    tweets = []
    try:
        for status in limit_handled(tweepy.Cursor(api.user_timeline, id=username, tweet_mode='extended',
                                                  count=100).items(30)):
            information = {'screen_name': status.user.screen_name, 'link': get_url_from_tweet(status.full_text),
                           'post': status.full_text}
            hashtags = []
            for hashtag in status.entities.get('hashtags'):
                hashtags.append({'name': '#'+hashtag.get('text')})
            information['hashtags'] = hashtags
            information['hashtag_count'] = len(hashtags)
            tweets.append(information)
    except tweepy.error.TweepError as error:
        print(error)
    return tweets


def get_tweets_based_hashtag(api, query):
    tweets = []
    try:
        for status in limit_handled(tweepy.Cursor(api.search, q=query, tweet_mode='extended', count=100).items(30)):
            information = {'screen_name': status.user.screen_name, 'link': get_url_from_tweet(status.full_text),
                           'post': status.full_text}
            hashtags = []
            for hashtag in status.entities.get('hashtags'):
                hashtags.append({'name': '#'+hashtag.get('text')})
            information['hashtags'] = hashtags
            information['hashtag_count'] = len(hashtags)
            tweets.append(information)
    except tweepy.error.TweepError as error:
        print(error)

    return tweets


def get_url_from_tweet(tweet):
    url = re.search(r'(?P<url>https?://[^\s]+)', tweet)
    if url:
        return url.group("url")
    return None


def get_user_data(api, screen_name):
    information = {}
    try:
        user = api.get_user(screen_name)
        information = {'followers': user.followers_count, 'following': user.friends_count}
    except tweepy.error.TweepError as error:
        print(error)
    return information


def setup_twitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    twitter_api = tweepy.API(auth)
    return twitter_api
