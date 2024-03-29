from typing import Union, List
from helpers.configurationhelpers import get_enable_mastodon, get_mastodon_client_id, get_mastodon_client_secret, get_mastodon_access_token, get_mastodon_api_base_url

import mastodon

from helpers.loghelpers import LOG


def get_mastodon_api():
    """
    Get the Mastodon API client

    :return: Mastodon API client
    """
    if get_enable_mastodon():
        return mastodon.Mastodon(
            client_id=get_mastodon_client_id(),
            client_secret=get_mastodon_client_secret(),
            access_token=get_mastodon_access_token(),
            api_base_url=get_mastodon_api_base_url()
        )
    else:
        return None


def get_trending_topics(woeid: Union[int, None] = None) -> List[tuple]:
    """
    Get trending topics of a location

    :param woeid: Int - Not used for Mastodon
    :return: A sorted List of tuples (<topic>, <tweet_count>, <query>, <url>) in descending order by tweet count
    """
    trends = api.trending_tags()

    topics = [(trend['name'], int(trend['history'][0]['uses']) if trend['history'] is not None else 0, trend['name'], trend['url']) for trend in trends]

    topics.sort(key=lambda x: -x[1])
    return topics


def get_popular_toot_ids(topic: str, limit: int = 1000) -> List:
    """
    Get a sorted list of toots on given topic in descending order of volume

    :param topic: String - the text to search for
    :param limit: Int - the number of items
    :return: List
    """
    toot_ids = []

    timeline = api.timeline_hashtag(topic, limit=40)

    items = len(timeline)
    LOG.debug(f'Got {items}/{limit} toots for topic {topic}')

    for status in timeline:
        if status['in_reply_to_id'] is not None:
            toot_ids.append(status['in_reply_to_id'])

    while items < limit and len(timeline) != 0:
        timeline = api.fetch_next(timeline)
        items += len(timeline)
        LOG.debug(f'Got {items}/{limit} toots for topic {topic}')
        for status in timeline:

            if status['in_reply_to_id'] is not None:
                toot_ids.append(status['in_reply_to_id'])

    return toot_ids


def get_toots_by_id(toot_ids: List) -> dict:
    """
    Get toots by their IDs

    :param toot_ids: List - a list of toot IDs
    :return: Dict - a dictionary of toots
    """
    toots = [api.status(id=toot_id) for toot_id in toot_ids]

    return {'data': toots}


def post_toot(text: str, media_ids: List = None, sensitive: bool = False, spoiler_text: str = None, visibility: str = 'public'):
    """
    Post a toot

    :param text: String - the text of the toot
    :param media_ids: List - a list of media IDs to attach to the toot
    :param sensitive: Bool - whether the toot is sensitive
    :param spoiler_text: String - the text to show before the toot
    :param visibility: String - the visibility of the toot
    :return: None
    """
    api.status_post(text, media_ids=media_ids, sensitive=sensitive, spoiler_text=spoiler_text, visibility=visibility)


api = get_mastodon_api()
