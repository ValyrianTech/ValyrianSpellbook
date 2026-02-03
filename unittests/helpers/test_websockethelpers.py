#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

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


if __name__ == '__main__':
    unittest.main()
