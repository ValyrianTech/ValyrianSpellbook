import tweepy
import random

from helpers.configurationhelpers import get_twitter_consumer_key, get_twitter_consumer_secret, get_twitter_access_token, get_twitter_access_token_secret

import time

# For Twitter API to work, you need to enable developer portal on your twitter account
# go to https://developer.twitter.com/
# To post tweets and follow or unfollow, you also need to apply for elevated access to the API
# Once Elevated Access is granted, also set the app permissions to read and write


def get_twitter_api():
    """
    Connect to the Twitter API using the credentials supplied in the configuration file
    :return:
    """
    # Authenticate to Twitter
    auth = tweepy.OAuth1UserHandler(consumer_key=get_twitter_consumer_key(),
                                    consumer_secret=get_twitter_consumer_secret(),
                                    access_token=get_twitter_access_token(),
                                    access_token_secret=get_twitter_access_token_secret())

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Twitter Authentication OK")
    except Exception as ex:
        print("Error during Twitter authentication: %s" % ex)
        return

    return api


def post_tweet(text):
    if api is not None:
        api.update_status(status=text)


def get_tweets(searchtext, limit=100):
    client = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAMSSdgEAAAAAvv5dDJ9usoBf0OELOGfTNWBvaSo%3DTcZhCoaeccrh3Ur2QzWqbMI2Jg23NZMRyiY60zKnn0X8VRMbWp")

    tweets = []
    for i, tweet in enumerate(tweepy.Paginator(client.search_recent_tweets, searchtext, tweet_fields=['author_id', 'public_metrics', 'lang', 'attachments'], user_fields=['public_metrics'], max_results=100).flatten(limit=limit)):
        tweets.append(tweet)

    return tweets


def get_users(ids):
    client = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAMSSdgEAAAAAvv5dDJ9usoBf0OELOGfTNWBvaSo%3DTcZhCoaeccrh3Ur2QzWqbMI2Jg23NZMRyiY60zKnn0X8VRMbWp")

    if 1 <= len(ids) <= 100:
        response = client.get_users(ids=ids, user_fields=['public_metrics'])
        return response.data

    return []


def get_trending_topics(woeid=None):
    # WOEID 1 = worldwide, see api.available_trends()
    if woeid is None:
        woeids = [trend['woeid'] for trend in api.available_trends()]
        woeid = random.choice(woeids)

    trends = api.get_place_trends(id=woeid)

    topics = [trend['name'] for trend in trends[0]['trends']]

    return topics


def get_extended_status(status_id):
    status = api.get_status(id=status_id, tweet_mode='extended')
    return status


def follow_user(username):
    api.create_friendship(screen_name=username)


api = get_twitter_api()
