import tweepy
from helpers.configurationhelpers import get_twitter_consumer_key, get_twitter_consumer_secret, get_twitter_access_token, get_twitter_access_token_secret

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
    api = get_twitter_api()

    if api is not None:
        api.update_status(status=text)
