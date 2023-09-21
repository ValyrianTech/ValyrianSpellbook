import asyncio
import websockets
import threading

from loghelpers import LOG


class WebSocketHandler:
    def __init__(self):
        self.connected = set()
        self.lock = asyncio.Lock()

    async def handler(self, websocket, path):
        try:
            # Register.
            async with self.lock:
                self.connected.add(websocket)
            LOG.debug(f'New connection: {websocket.remote_address}')
            # Implement logic here.
            async for message in websocket:
                await self.broadcast(message)
        except Exception as e:
            LOG.error(f'Error in handler: {e}')
        finally:
            # Unregister.
            async with self.lock:
                self.connected.remove(websocket)
            await websocket.close()
            LOG.debug(f'Connection closed: {websocket.remote_address}')

    async def broadcast(self, message):
        LOG.info(f'Broadcasting {message}')
        async with self.lock:
            if self.connected:  # asyncio.wait doesn't accept an empty list
                await asyncio.wait([user.send(message) for user in self.connected])


WEBSOCKET_HANDLER = WebSocketHandler()
LOOP = asyncio.new_event_loop()


def broadcast_message(message: str):
    asyncio.run_coroutine_threadsafe(WEBSOCKET_HANDLER.broadcast(message), LOOP)


def start_websocket_server(host: str, port: int):
    LOG.info(f'Starting websocket server on {host}:{port} ...')
    asyncio.set_event_loop(LOOP)
    start_server = websockets.serve(WEBSOCKET_HANDLER.handler, host, port)
    LOG.info('Initializing websocket server.')
    LOOP.run_until_complete(start_server)
    LOG.info('Websocket server running.')
    LOOP.run_forever()
    LOG.info('Websocket server stopped.')


# Create a separate thread for the websocket server
websocket_thread = threading.Thread(target=start_websocket_server, args=('localhost', 8765))

# Start the thread
websocket_thread.start()
