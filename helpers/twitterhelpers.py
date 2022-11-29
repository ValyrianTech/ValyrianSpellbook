import tweepy
import random
import requests
import os

from helpers.configurationhelpers import get_twitter_consumer_key, get_twitter_consumer_secret, get_twitter_access_token, get_twitter_access_token_secret, get_twitter_bearer_token

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


def update_status(text, url=None):
    if api is not None:
        print('\nPosting new tweet:')
        print('text: %s' % text)
        print('url: %s' % url)

        api.update_status(status=text, attachment_url=url)


def update_status_with_media(url, message):
    if api is None:
        return

    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_status_with_media(filename=filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download media")


def get_tweets(searchtext, limit=100):
    """
    Get most recent tweets about given search text

    :param searchtext: String - text to search twitter
    :param limit: Int - number of tweets to retrieve (default=100)
    :return: a list of Tweet objects, each with following attributes:
        - id
        - text
        - author_id
        - public_metrics
        - lang
        - attachments
        - conversation_id
        - entities
        - in_reply_to_user_id
    """
    client = tweepy.Client(bearer_token=get_twitter_bearer_token())

    tweets = []
    for i, tweet in enumerate(tweepy.Paginator(client.search_recent_tweets, searchtext, tweet_fields=['author_id', 'public_metrics', 'lang', 'attachments', 'conversation_id', 'entities', 'in_reply_to_user_id'], user_fields=['public_metrics'], max_results=100).flatten(limit=limit)):
        tweets.append(tweet)

    return tweets


def get_users(ids):
    client = tweepy.Client(bearer_token=get_twitter_bearer_token())

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
