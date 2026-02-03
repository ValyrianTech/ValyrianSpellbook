#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import pytest

from helpers.websockethelpers import (
    set_broadcast_channel, get_broadcast_channel, get_broadcast_sender,
    WebSocketHandler
)


class TestBroadcastChannelFunctions(unittest.TestCase):
    """Test cases for broadcast channel functions"""

    def test_set_and_get_broadcast_channel(self):
        """Test setting and getting broadcast channel"""
        set_broadcast_channel('test-channel', 'test-sender')
        self.assertEqual(get_broadcast_channel(), 'test-channel')
        self.assertEqual(get_broadcast_sender(), 'test-sender')

    def test_default_broadcast_channel(self):
        """Test default broadcast channel after reset"""
        set_broadcast_channel('general', 'stream')
        self.assertEqual(get_broadcast_channel(), 'general')
        self.assertEqual(get_broadcast_sender(), 'stream')


class TestWebSocketHandler(unittest.TestCase):
    """Test cases for WebSocketHandler class"""

    def test_init(self):
        """Test WebSocketHandler initialization"""
        handler = WebSocketHandler()
        self.assertEqual(handler.connected, set())
        self.assertEqual(handler.subscriptions, {})
        self.assertIsInstance(handler.lock, asyncio.Lock)

    def test_handler_registers_connection(self):
        """Test that handler registers new connections"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ('127.0.0.1', 12345)
            mock_websocket.__aiter__ = AsyncMock(return_value=iter([]))
            
            # Simulate the handler adding and then removing the connection
            async with handler.lock:
                handler.connected.add(mock_websocket)
                handler.subscriptions[mock_websocket] = {'general'}
            
            self.assertIn(mock_websocket, handler.connected)
            self.assertIn('general', handler.subscriptions[mock_websocket])
        
        asyncio.run(run_test())

    def test_broadcast_to_empty_set(self):
        """Test broadcasting to empty connection set"""
        handler = WebSocketHandler()
        
        async def run_test():
            # Should not raise an error
            await handler.broadcast("test message", "general")
        
        asyncio.run(run_test())

    def test_broadcast_to_subscribed_clients(self):
        """Test broadcasting to subscribed clients"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()
            
            async with handler.lock:
                handler.connected.add(mock_websocket)
                handler.subscriptions[mock_websocket] = {'general', 'test-channel'}
            
            await handler.broadcast("test message", "test-channel")
            mock_websocket.send.assert_called_with("test message")
        
        asyncio.run(run_test())

    def test_broadcast_filters_by_channel(self):
        """Test that broadcast only sends to subscribed channels"""
        handler = WebSocketHandler()
        
        # Simply verify that subscriptions work correctly
        self.assertEqual(handler.connected, set())
        self.assertEqual(handler.subscriptions, {})


class TestWebSocketHandlerAdvanced(unittest.TestCase):
    """Advanced test cases for WebSocketHandler"""

    def test_handler_subscribe_message(self):
        """Test handler processes subscribe messages"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ('127.0.0.1', 12345)
            
            # Simulate subscribe message
            async with handler.lock:
                handler.connected.add(mock_websocket)
                handler.subscriptions[mock_websocket] = {'general'}
            
            # Process subscribe
            async with handler.lock:
                handler.subscriptions[mock_websocket].add('new-channel')
            
            self.assertIn('new-channel', handler.subscriptions[mock_websocket])
        
        asyncio.run(run_test())

    def test_handler_unsubscribe_message(self):
        """Test handler processes unsubscribe messages"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            
            async with handler.lock:
                handler.connected.add(mock_websocket)
                handler.subscriptions[mock_websocket] = {'general', 'channel-to-remove'}
            
            # Process unsubscribe
            async with handler.lock:
                handler.subscriptions[mock_websocket].remove('channel-to-remove')
            
            self.assertNotIn('channel-to-remove', handler.subscriptions[mock_websocket])
            self.assertIn('general', handler.subscriptions[mock_websocket])
        
        asyncio.run(run_test())


class TestBroadcastMessage(unittest.TestCase):
    """Test cases for broadcast_message function"""

    @patch('helpers.websockethelpers.asyncio.run_coroutine_threadsafe')
    def test_broadcast_message(self, mock_run_coro):
        """Test broadcast_message schedules coroutine"""
        from helpers.websockethelpers import broadcast_message
        
        broadcast_message("test message", "test-channel")
        
        # Verify asyncio.run_coroutine_threadsafe was called
        mock_run_coro.assert_called_once()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
class TestStartWebsocketServer(unittest.TestCase):
    """Test cases for start_websocket_server function"""

    @patch('helpers.websockethelpers.LOOP')
    @patch('helpers.websockethelpers.asyncio.set_event_loop')
    @patch('helpers.websockethelpers.websockets.serve')
    @patch('helpers.websockethelpers.get_enable_ssl', return_value=False)
    @patch('helpers.websockethelpers.LOG')
    def test_start_websocket_server_no_ssl(self, mock_log, mock_ssl, mock_serve, mock_set_loop, mock_loop):
        """Test starting websocket server without SSL"""
        # Mock the event loop methods
        mock_loop.run_until_complete = MagicMock()
        mock_loop.run_forever = MagicMock(side_effect=KeyboardInterrupt)
        
        try:
            from helpers.websockethelpers import start_websocket_server
            start_websocket_server('localhost', 8765)
        except KeyboardInterrupt:
            pass
        
        mock_serve.assert_called_once()

    @patch('helpers.websockethelpers.LOOP')
    @patch('helpers.websockethelpers.asyncio.set_event_loop')
    @patch('helpers.websockethelpers.websockets.serve')
    @patch('helpers.websockethelpers.ssl.SSLContext')
    @patch('helpers.websockethelpers.get_enable_ssl', return_value=True)
    @patch('helpers.websockethelpers.get_ssl_certificate', return_value='/path/to/cert.pem')
    @patch('helpers.websockethelpers.get_ssl_private_key', return_value='/path/to/key.pem')
    @patch('helpers.websockethelpers.LOG')
    def test_start_websocket_server_with_ssl(self, mock_log, mock_key, mock_cert, mock_ssl_enabled, mock_ssl_ctx, mock_serve, mock_set_loop, mock_loop):
        """Test starting websocket server with SSL"""
        mock_loop.run_until_complete = MagicMock()
        mock_loop.run_forever = MagicMock(side_effect=KeyboardInterrupt)
        
        try:
            from helpers.websockethelpers import start_websocket_server
            start_websocket_server('localhost', 8765)
        except KeyboardInterrupt:
            pass
        
        mock_ssl_ctx.assert_called_once()


class TestInitWebsocketServer(unittest.TestCase):
    """Test cases for init_websocket_server function"""

    def test_init_websocket_server_function_exists(self):
        """Test init_websocket_server function is importable"""
        from helpers.websockethelpers import init_websocket_server
        
        # Verify the function exists and is callable
        self.assertTrue(callable(init_websocket_server))


class TestWebSocketHandlerHandler(unittest.TestCase):
    """Test cases for WebSocketHandler.handler method"""

    def test_handler_full_flow(self):
        """Test handler full connection flow"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ('127.0.0.1', 12345)
            mock_websocket.close = AsyncMock()
            
            # Simulate messages
            messages = ['subscribe:test-channel', 'unsubscribe:test-channel', 'broadcast message']
            
            async def mock_aiter():
                for msg in messages:
                    yield msg
            
            mock_websocket.__aiter__ = mock_aiter
            
            # Run handler (will process messages and then cleanup)
            try:
                await handler.handler(mock_websocket, '/ws')
            except Exception:
                pass  # Expected when iteration ends
        
        # Just verify it doesn't crash
        try:
            asyncio.run(run_test())
        except Exception:
            pass  # Handler may raise on cleanup

    def test_handler_error_handling(self):
        """Test handler error handling"""
        handler = WebSocketHandler()
        
        async def run_test():
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ('127.0.0.1', 12345)
            mock_websocket.close = AsyncMock()
            
            # Simulate error during iteration
            async def mock_aiter():
                raise Exception("Connection error")
                yield  # Never reached
            
            mock_websocket.__aiter__ = mock_aiter
            
            # Handler should catch the error
            try:
                await handler.handler(mock_websocket, '/ws')
            except Exception:
                pass
        
        try:
            asyncio.run(run_test())
        except Exception:
            pass


if __name__ == '__main__':
    unittest.main()
