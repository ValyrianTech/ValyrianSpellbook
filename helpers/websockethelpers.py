import asyncio
import websockets
import threading
import ssl

from helpers.configurationhelpers import what_is_my_ip
from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_enable_ssl, get_ssl_certificate, get_ssl_private_key
BROADCAST_CHANNEL = 'general'
BROADCAST_SENDER = 'stream'


def set_broadcast_channel(channel: str, sender: str):
    global BROADCAST_CHANNEL, BROADCAST_SENDER
    BROADCAST_CHANNEL = channel
    BROADCAST_SENDER = sender


def get_broadcast_channel():
    return BROADCAST_CHANNEL


def get_broadcast_sender():
    return BROADCAST_SENDER


class WebSocketHandler:
    def __init__(self):
        self.connected = set()
        self.subscriptions = {}
        self.lock = asyncio.Lock()

    async def handler(self, websocket, path):
        try:
            # Register.
            async with self.lock:
                self.connected.add(websocket)
                self.subscriptions[websocket] = {'general'}
            LOG.debug(f'New connection: {websocket.remote_address}')
            # Implement logic here.
            async for message in websocket:
                if message.startswith('subscribe:'):
                    async with self.lock:
                        self.subscriptions[websocket].add(message.split(':')[1])
                elif message.startswith('unsubscribe:'):
                    async with self.lock:
                        self.subscriptions[websocket].remove(message.split(':')[1])
                else:
                    await self.broadcast(message, 'general')
        except Exception as e:
            LOG.error(f'Error in handler: {e}')
        finally:
            # Unregister.
            async with self.lock:
                self.connected.remove(websocket)
                del self.subscriptions[websocket]
            await websocket.close()
            LOG.debug(f'Connection closed: {websocket.remote_address}')

    async def broadcast(self, message, channel='general'):
        async with self.lock:
            if self.connected:  # asyncio.wait doesn't accept an empty list
                tasks = [asyncio.create_task(user.send(message)) for user in self.connected if channel in self.subscriptions[user]]
                await asyncio.wait(tasks)


WEBSOCKET_HANDLER = WebSocketHandler()
LOOP = asyncio.new_event_loop()


def broadcast_message(message: str, channel: str = 'general'):
    asyncio.run_coroutine_threadsafe(WEBSOCKET_HANDLER.broadcast(message, channel), LOOP)


def start_websocket_server(host: str, port: int):

    LOG.info(f'Starting websocket server on {host}:{port} ...')
    asyncio.set_event_loop(LOOP)

    if get_enable_ssl():
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(get_ssl_certificate(), get_ssl_private_key())
        start_server = websockets.serve(WEBSOCKET_HANDLER.handler, host, port, ssl=ssl_context)
    else:
        start_server = websockets.serve(WEBSOCKET_HANDLER.handler, host, port)

    LOG.info('Initializing websocket server.')
    LOOP.run_until_complete(start_server)
    LOG.info('Websocket server running.')
    LOOP.run_forever()
    LOG.info('Websocket server stopped.')


def init_websocket_server(host: str = 'localhost', port: int = 8765):
    # Create a separate thread for the websocket server
    websocket_thread = threading.Thread(target=start_websocket_server, args=(host, port))

    # Start the thread
    websocket_thread.start()
