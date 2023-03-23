import time
import uuid
from pynostr.event import Event
from pynostr.relay_manager import RelayManager
from pynostr.filters import FiltersList, Filters
from pynostr.key import PrivateKey, PublicKey
from helpers.configurationhelpers import get_nostr_nsec


def get_nostr_private_key() -> PrivateKey:
    private_key = PrivateKey.from_nsec(get_nostr_nsec())

    return private_key


def get_nostr_public_key() -> PublicKey:
    private_key = get_nostr_private_key()
    public_key = private_key.public_key

    return public_key


def post_note(text: str) -> None:

    relay_manager = RelayManager(timeout=6)
    relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    relay_manager.add_relay("wss://relay.damus.io")
    private_key = get_nostr_private_key()

    filters = FiltersList([Filters(authors=[private_key.public_key.hex()], limit=100)])
    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)

    event = Event(text)
    event.sign(private_key.hex())

    relay_manager.publish_event(event)
    relay_manager.run_sync()
    time.sleep(5) # allow the messages to send
    while relay_manager.message_pool.has_ok_notices():
        ok_msg = relay_manager.message_pool.get_ok_notice()
        print(ok_msg)
    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        print(event_msg.event.to_dict())

