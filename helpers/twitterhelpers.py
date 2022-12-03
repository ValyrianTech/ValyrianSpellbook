from typing import Union, List

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
    """Deprecated: use create_tweet instead"""
    if api is not None:
        print('\nPosting new tweet:')
        print('text: %s' % text)
        print('url: %s' % url)

        api.update_status(status=text, attachment_url=url)


def update_status_with_media(url, message):
    """
    Create a tweet with an image file, must use V1 because not implemented in V2 yet

    :param url: the url of the image
    :param message: the text of the tweet
    :return:
    """
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


def get_tweets(searchtext, limit=100) -> List[tweepy.tweet.Tweet]:
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


def follow_user(target_user_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Follow a user on Twitter

    :param target_user_id: Int | String - The user ID of the user that you would like to follow. (without the @)
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with keys 'following' and 'pending_follow', both booleans
    """
    response = client.follow_user(target_user_id=target_user_id, user_auth=user_auth)
    return response.data


def unfollow_user(target_user_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Unfollow a user on Twitter

    :param target_user_id: Int | String - The user ID of the user that you would like to unfollow. (without the @)
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with keys 'following' and 'pending_follow', both booleans
    """
    response = client.unfollow_user(target_user_id=target_user_id, user_auth=user_auth)
    return response.data


def get_user(user_id: Union[int, str, None] = None,
             user_name: Union[str, None] = None) -> tweepy.user.User:
    """
    Get information about a specific user by giving either a user_id or user_name

    :param user_id: The user id
    :param user_name: The user name
    :return: A User object containing the following attributes:
        - id
        - username
        - name
        - created_at
        - description
        - entities
        - location
        - pinned_tweet_id
        - profile_image_url
        - protected
        - public_metrics
        - url
        - verified
        - withheld
    """
    if user_id is None and user_name is None:
        raise Exception('Must supply either user_id or user_name')

    response = client.get_user(id=user_id,
                               username=user_name,
                               user_fields=['created_at', 'description', 'entities', 'location', 'pinned_tweet_id', 'profile_image_url', 'protected', 'public_metrics', 'url', 'verified', 'withheld'])

    return response.data


def like_tweet(tweet_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Like a tweet on Twitter

    :param tweet_id: Int | String - The ID of the Tweet that you would like to Like.
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with key 'Liked' (boolean)
    """
    response = client.like(tweet_id=tweet_id, user_auth=user_auth)
    return response.data


def unlike_tweet(tweet_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Unlike a tweet on Twitter

    :param tweet_id: Int | String - The ID of the Tweet that you would like to unlike.
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with key 'Liked' (boolean)
    """
    response = client.unlike(tweet_id=tweet_id, user_auth=user_auth)
    return response.data


def delete_tweet(tweet_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Delete a tweet on Twitter

    :param tweet_id: Int | String - The ID of the Tweet that you would like to delete.
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict
    """
    response = client.delete_tweet(id=tweet_id, user_auth=user_auth)
    return response.data


def retweet(tweet_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Causes the user ID to Retweet the target Tweet.

    :param tweet_id: Int | String - The ID of the Tweet that you would like to Retweet.
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with key 'retweeted' (boolean)
    """
    response = client.retweet(tweet_id=tweet_id, user_auth=user_auth)
    return response.data


def unretweet(tweet_id: Union[int, str], user_auth: bool = True) -> dict:
    """
    Allows an authenticated user ID to remove the Retweet of a Tweet.

    :param tweet_id: Int | String - he ID of the Tweet that you would like to remove the Retweet of.
    :param user_auth: bool - Whether or not to use OAuth 1.0a User Context to authenticate (default=True)
    :return: Dict - a dict with key 'retweeted' (boolean)
    """
    response = client.unretweet(source_tweet_id=tweet_id, user_auth=user_auth)
    return response.data


def create_tweet(text: Union[str, None] = None,
                 in_reply_to_tweet_id: Union[int, str, None] = None,
                 reply_settings: Union[str, None] = None,
                 exclude_reply_user_ids: Union[List[Union[int, str]], None] = None,
                 quote_tweet_id: Union[int, str, None] = None,
                 poll_options: Union[List[str], None] = None,
                 poll_duration_minutes: Union[int, None] = None,
                 media_tagged_user_ids: Union[List[Union[int, str]], None] = None,
                 media_ids: Union[List[Union[int, str]], None] = None,
                 place_id: Union[str, None] = None,
                 for_super_followers_only: Union[bool, None] = None,
                 direct_message_deep_link: Union[str, None] = None,
                 user_auth: bool = True) -> dict:
    """
    Creates a Tweet on behalf of an authenticated user.

    :param text: Text of the Tweet being created. This field is required if media.media_ids is not present.
    :param in_reply_to_tweet_id: Tweet ID of the Tweet being replied to. Please note that in_reply_to_tweet_id needs to be in the request if exclude_reply_user_ids is present.
    :param reply_settings: Settings to indicate who can reply to the Tweet. Limited to “mentionedUsers” and “following”. If the field isn’t specified, it will default to everyone.
    :param exclude_reply_user_ids:  A list of User IDs to be excluded from the reply Tweet thus removing a user from a thread.
    :param quote_tweet_id: Link to the Tweet being quoted.
    :param poll_options: A list of poll options for a Tweet with a poll.
    :param poll_duration_minutes: Duration of the poll in minutes for a Tweet with a poll. This is only required if the request includes poll.options.
    :param media_tagged_user_ids: A list of User IDs being tagged in the Tweet with Media. If the user you’re tagging doesn’t have photo-tagging enabled, their names won’t show up in the list of tagged users even though the Tweet is successfully created.
    :param media_ids: A list of Media IDs being attached to the Tweet. This is only required if the request includes the tagged_user_ids.
    :param place_id: Place ID being attached to the Tweet for geo location.
    :param for_super_followers_only: Allows you to Tweet exclusively for Super Followers.
    :param direct_message_deep_link: Tweets a link directly to a Direct Message conversation with an account.
    :param user_auth: Whether or not to use OAuth 1.0a User Context to authenticate
    :return: dict with keys 'id' and 'text'
    """
    response = client.create_tweet(text=text,
                                   in_reply_to_tweet_id=in_reply_to_tweet_id,
                                   reply_settings=reply_settings,
                                   exclude_reply_user_ids=exclude_reply_user_ids,
                                   quote_tweet_id=quote_tweet_id,
                                   poll_options=poll_options,
                                   poll_duration_minutes=poll_duration_minutes,
                                   media_tagged_user_ids=media_tagged_user_ids,
                                   media_ids=media_ids,
                                   place_id=place_id,
                                   for_super_followers_only=for_super_followers_only,
                                   direct_message_deep_link=direct_message_deep_link,
                                   user_auth=user_auth)

    return response.data


def get_direct_message_events(dm_conversation_id: Union[str, None] = None,
                              participant_id: Union[int, str, None] = None,
                              dm_event_fields: Union[List[str], str, None] = None,
                              event_types: Union[str, None] = None,
                              expansions: Union[List[str], str, None] = None,
                              max_results: Union[int, None] = None,
                              media_fields: Union[List[str], str, None] = None,
                              pagination_token: Union[str, None] = None,
                              tweet_fields: Union[List[str], str, None] = None,
                              user_fields: Union[List[str], str, None] = None,
                              user_auth: bool = True) -> Union[List[tweepy.direct_message_event.DirectMessageEvent], None]:
    """
    If dm_conversation_id is passed, returns a list of Direct Messages within the conversation specified. Messages are returned in reverse chronological order.

    If participant_id is passed, returns a list of Direct Messages (DM) events within a 1-1 conversation with the user specified. Messages are returned in reverse chronological order.

    If neither is passed, returns a list of Direct Messages for the authenticated user, both sent and received. Direct Message events are returned in reverse chronological order. Supports retrieving events from the previous 30 days.

    :param dm_conversation_id: The id of the Direct Message conversation for which events are being retrieved.
    :param participant_id: The participant_id of the user that the authenicating user is having a 1-1 conversation with.
    :param dm_event_fields: Extra fields to include in the event payload. id, text, and event_type are returned by default.
    :param event_types: The type of Direct Message event to returm. If not included, all types are returned.
    :param expansions: expansions
    :param max_results: The maximum number of results to be returned in a page. Must be between 1 and 100. The default is 100.
    :param media_fields: media_fields
    :param pagination_token: Contains either the next_token or previous_token value.
    :param tweet_fields: tweet_fields
    :param user_fields: user_fields
    :param user_auth: Whether or not to use OAuth 1.0a User Context to authenticate
    :return: List of DirectMessageEvent objects
    """
    response = client.get_direct_message_events(dm_conversation_id=dm_conversation_id,
                                                participant_id=participant_id,
                                                dm_event_fields=dm_event_fields,
                                                event_types=event_types,
                                                expansions=expansions,
                                                max_results=max_results,
                                                media_fields=media_fields,
                                                pagination_token=pagination_token,
                                                tweet_fields=tweet_fields,
                                                user_fields=user_fields,
                                                user_auth=user_auth)
    return response.data


def create_direct_message(dm_conversation_id: Union[str, None] = None,
                          participant_id: Union[int, str, None] = None,
                          media_id: Union[int, str, None] = None,
                          text: Union[str, None] = None,
                          user_auth: bool = True) -> dict:
    """
    If dm_conversation_id is passed, creates a Direct Message on behalf of the authenticated user, and adds it to the specified conversation.

    If participant_id is passed, creates a one-to-one Direct Message and adds it to the one-to-one conversation. This method either creates a new one-to-one conversation or retrieves the current conversation and adds the Direct Message to it.

    :param dm_conversation_id: The dm_conversation_id of the conversation to add the Direct Message to. Supports both 1-1 and group conversations.
    :param participant_id: The User ID of the account this one-to-one Direct Message is to be sent to.
    :param media_id: A single Media ID being attached to the Direct Message. This field is required if text is not present. For this launch, only 1 attachment is supported.
    :param text: Text of the Direct Message being created. This field is required if media_id is not present. Text messages support up to 10,000 characters.
    :param user_auth: Whether or not to use OAuth 1.0a User Context to authenticate
    :return: Dict
    """
    response = client.create_direct_message(dm_conversation_id=dm_conversation_id,
                                            participant_id=participant_id,
                                            media_id=media_id,
                                            text=text,
                                            user_auth=user_auth)
    return response.data


api = get_twitter_api()
client = tweepy.Client(bearer_token=get_twitter_bearer_token(),
                       access_token=get_twitter_access_token(),
                       access_token_secret=get_twitter_access_token_secret(),
                       consumer_key=get_twitter_consumer_key(),
                       consumer_secret=get_twitter_consumer_secret())
