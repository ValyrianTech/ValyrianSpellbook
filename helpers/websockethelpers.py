import asyncio
import websockets
import threading
import ssl
from contextvars import ContextVar

from helpers.configurationhelpers import what_is_my_ip
from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_enable_ssl, get_ssl_certificate, get_ssl_private_key

# Use ContextVars instead of global variables to support concurrent conversations
# Each execution context (thread/async task) maintains its own isolated values
BROADCAST_CHANNEL: ContextVar[str] = ContextVar('broadcast_channel', default='general')
BROADCAST_SENDER: ContextVar[str] = ContextVar('broadcast_sender', default='stream')


def set_broadcast_channel(channel: str, sender: str):
    """Set the broadcast channel and sender for the current execution context."""
    BROADCAST_CHANNEL.set(channel)
    BROADCAST_SENDER.set(sender)


def get_broadcast_channel() -> str:
    """Get the broadcast channel for the current execution context."""
    return BROADCAST_CHANNEL.get()


def get_broadcast_sender() -> str:
    """Get the broadcast sender for the current execution context."""
    return BROADCAST_SENDER.get()


class WebSocketHandler:
    def __init__(self):
        self.connected = set()
        self.subscriptions = {}
        self.lock = asyncio.Lock()

    async def handler(self, websocket):
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


async def run_websocket_server(host: str, port: int):
    """Async function to run the websocket server using websockets 16.0+ API."""
    LOG.info(f'Starting websocket server on {host}:{port} ...')

    if get_enable_ssl():
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(get_ssl_certificate(), get_ssl_private_key())
        async with websockets.serve(WEBSOCKET_HANDLER.handler, host, port, ssl=ssl_context):
            LOG.info('Websocket server running.')
            await asyncio.get_running_loop().create_future()  # Run forever
    else:
        async with websockets.serve(WEBSOCKET_HANDLER.handler, host, port):
            LOG.info('Websocket server running.')
            await asyncio.get_running_loop().create_future()  # Run forever


def start_websocket_server(host: str, port: int):
    LOG.info(f'Initializing websocket server on {host}:{port} ...')
    asyncio.set_event_loop(LOOP)
    try:
        LOOP.run_until_complete(run_websocket_server(host, port))
    except Exception as e:
        LOG.error(f'Websocket server error: {e}')
    finally:
        LOG.info('Websocket server stopped.')


def init_websocket_server(host: str = 'localhost', port: int = 8765):
    # Create a separate thread for the websocket server
    websocket_thread = threading.Thread(target=start_websocket_server, args=(host, port))

    # Start the thread
    websocket_thread.start()
