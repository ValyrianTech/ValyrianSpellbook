#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
import re
import uuid
import urllib.parse
import threading
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_client')

class MCPClient:
    """
    Client for the Model Context Protocol (MCP)
    
    This client handles the HTTP+SSE transport protocol for MCP, maintaining
    a persistent SSE connection while sending messages to the server.
    """
    
    def __init__(self, base_url, client_name="Valyrian Spellbook", client_version="1.0.0", debug=False):
        """
        Initialize the MCP client
        
        Args:
            base_url (str): Base URL of the MCP server (e.g., "https://example.com")
            client_name (str): Name of the client to send in initialize message
            client_version (str): Version of the client to send in initialize message
            debug (bool): Whether to enable debug logging
        """
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.client_name = client_name
        self.client_version = client_version
        self.session_id = None
        self.messages_endpoint = None
        self.full_messages_url = None
        
        # Set up session and threading components
        self.session = requests.Session()
        self.message_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.sse_thread = None
        self.initialized = False
        
        # Set up logging
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def connect(self):
        """
        Connect to the MCP server and start the SSE listener thread
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MCP server at {self.sse_url}")
            
            # Step 1: Connect to SSE endpoint to get session ID
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
            
            # Make the initial request to get the session ID
            response = self.session.get(self.sse_url, headers=headers, stream=True, timeout=(3.05, 10))
            
            if response.status_code != 200:
                logger.error(f"Failed to connect to MCP server: {response.status_code}")
                return False
                
            logger.debug(f"Connected to SSE endpoint: {response.status_code}")
            
            # Extract the session ID from the first event
            for i, line in enumerate(response.iter_lines(decode_unicode=True)):
                if line:
                    logger.debug(f"Received line: {line}")
                    
                    # Parse SSE line
                    if line.startswith("event: endpoint"):
                        # The next line should contain the data
                        continue
                        
                    if line.startswith("data: "):
                        self.messages_endpoint = line.split("data: ", 1)[1].strip()
                        if "sessionId=" in self.messages_endpoint:
                            session_id_match = re.search(r'sessionId=([^&]+)', self.messages_endpoint)
                            if session_id_match:
                                self.session_id = session_id_match.group(1)
                                logger.info(f"Extracted session ID: {self.session_id}")
                                logger.info(f"Messages endpoint: {self.messages_endpoint}")
                                break
                
                # Limit the number of lines we read
                if i > 10:
                    break
                    
            if not self.session_id or not self.messages_endpoint:
                logger.error("Failed to extract session ID or messages endpoint")
                return False
                
            # Close the initial response
            response.close()
            
            # Construct the full URL for the messages endpoint
            if self.messages_endpoint.startswith('/'):
                self.full_messages_url = f"{self.base_url}{self.messages_endpoint}"
            else:
                self.full_messages_url = self.messages_endpoint
                
            # Step 2: Start a background thread to keep the SSE connection alive
            logger.info("Starting background SSE connection")
            self.stop_event.clear()
            self.sse_thread = threading.Thread(
                target=self._listen_for_sse_events,
                daemon=True
            )
            self.sse_thread.start()
            
            # Give the thread a moment to establish the connection
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            return False
    
    def initialize(self):
        """
        Send an initialize message to the MCP server
        
        Returns:
            dict: The server's response to the initialize message, or None if failed
        """
        if not self.session_id or not self.full_messages_url:
            logger.error("Cannot initialize: No session ID or messages endpoint")
            return None
            
        logger.info(f"Initializing MCP session: {self.session_id}")
        
        # Create initialize message
        initialize_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": self.client_name,
                    "version": self.client_version
                },
                "capabilities": {
                    "tools": True
                }
            },
            "id": str(uuid.uuid4())
        }
        
        # Store the request ID to match with the response
        request_id = initialize_message["id"]
        logger.debug(f"Initialize request ID: {request_id}")
        
        try:
            # Send the initialize message
            response = self.session.post(
                self.full_messages_url,
                json=initialize_message,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            logger.debug(f"Initialize status code: {response.status_code}")
            
            # For MCP over HTTP+SSE, the response should be 202 Accepted with no content
            # The actual response will come through the SSE connection
            if response.status_code != 202:
                logger.error(f"Unexpected status code: {response.status_code}")
                return None
                
            # Wait for the response in the SSE stream
            initialize_response = self._wait_for_response(request_id, timeout=10)
            
            if not initialize_response:
                logger.error("Did not receive initialize response within timeout")
                return None
                
            # Check if initialization was successful
            if "result" in initialize_response:
                logger.info("Successfully initialized MCP session")
                self.initialized = True
                return initialize_response
            else:
                logger.error(f"Failed to initialize MCP session: {initialize_response.get('error')}")
                return initialize_response
                
        except Exception as e:
            logger.error(f"Error initializing MCP session: {e}")
            return None
    
    def send_message(self, content, timeout=30):
        """
        Send a message to the MCP server
        
        Args:
            content (list): List of content objects to send
            timeout (int): Timeout in seconds to wait for a response
            
        Returns:
            dict: The server's response to the message, or None if failed
        """
        if not self.initialized:
            logger.error("Cannot send message: MCP session not initialized")
            return None
            
        if not self.full_messages_url:
            logger.error("Cannot send message: No messages endpoint")
            return None
            
        logger.info("Sending message to MCP server")
        
        # Create message
        message = {
            "jsonrpc": "2.0",
            "method": "message",
            "params": {
                "content": content
            },
            "id": str(uuid.uuid4())
        }
        
        # Store the request ID to match with the response
        request_id = message["id"]
        logger.debug(f"Message request ID: {request_id}")
        
        try:
            # Send the message
            response = self.session.post(
                self.full_messages_url,
                json=message,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            logger.debug(f"Message status code: {response.status_code}")
            
            # For MCP over HTTP+SSE, the response should be 202 Accepted with no content
            # The actual response will come through the SSE connection
            if response.status_code != 202:
                logger.error(f"Unexpected status code: {response.status_code}")
                return None
                
            # Wait for the response in the SSE stream
            message_response = self._wait_for_response(request_id, timeout=timeout)
            
            if not message_response:
                logger.error("Did not receive message response within timeout")
                return None
                
            return message_response
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def list_tools(self, timeout=30):
        """
        List available tools from the MCP server
        
        Args:
            timeout (int): Timeout in seconds to wait for a response
            
        Returns:
            dict: The server's response containing available tools, or None if failed
        """
        if not self.initialized:
            logger.error("Cannot list tools: MCP session not initialized")
            return None
            
        logger.info("Listing tools from MCP server")
        
        # Create tools/list request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        # Store the request ID to match with the response
        request_id = request["id"]
        logger.debug(f"List tools request ID: {request_id}")
        
        try:
            # Send the request
            response = self.session.post(
                self.full_messages_url,
                json=request,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            logger.debug(f"List tools status code: {response.status_code}")
            
            # For MCP over HTTP+SSE, the response should be 202 Accepted with no content
            # The actual response will come through the SSE connection
            if response.status_code != 202:
                logger.error(f"Unexpected status code: {response.status_code}")
                return None
                
            # Wait for the response in the SSE stream
            tools_response = self._wait_for_response(request_id, timeout=timeout)
            
            if not tools_response:
                logger.error("Did not receive tools list response within timeout")
                return None
                
            return tools_response
                
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return None
    
    def invoke_tool(self, tool_name, params, timeout=30):
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name (str): Name of the tool to invoke
            params (dict): Parameters to pass to the tool
            timeout (int): Timeout in seconds to wait for a response
            
        Returns:
            dict: The server's response from the tool invocation, or None if failed
        """
        if not self.initialized:
            logger.error("Cannot invoke tool: MCP session not initialized")
            return None
            
        logger.info(f"Invoking tool {tool_name} on MCP server")
        
        # Create tool invocation request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": str(uuid.uuid4())
        }
        
        # Store the request ID to match with the response
        request_id = request["id"]
        logger.debug(f"Tool invocation request ID: {request_id}")
        
        try:
            # Send the request
            response = self.session.post(
                self.full_messages_url,
                json=request,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            logger.debug(f"Tool invocation status code: {response.status_code}")
            
            # For MCP over HTTP+SSE, the response should be 202 Accepted with no content
            # The actual response will come through the SSE connection
            if response.status_code != 202:
                logger.error(f"Unexpected status code: {response.status_code}")
                return None
                
            # Wait for the response in the SSE stream
            tool_response = self._wait_for_response(request_id, timeout=timeout)
            
            if not tool_response:
                logger.error("Did not receive tool invocation response within timeout")
                return None
                
            return tool_response
                
        except Exception as e:
            logger.error(f"Error invoking tool: {e}")
            return None
    
    def disconnect(self):
        """
        Disconnect from the MCP server and clean up resources
        """
        logger.info("Disconnecting from MCP server")
        
        # Stop the SSE listener thread
        if self.sse_thread and self.sse_thread.is_alive():
            self.stop_event.set()
            self.sse_thread.join(timeout=2)
            
        # Close the session
        self.session.close()
        
        # Reset state
        self.initialized = False
        self.session_id = None
        self.messages_endpoint = None
        self.full_messages_url = None
    
    def _listen_for_sse_events(self):
        """
        Background thread function to keep the SSE connection alive and collect messages
        """
        try:
            # Set up headers for SSE
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
            
            # Make the request with stream=True for SSE
            with self.session.get(self.sse_url, headers=headers, stream=True, timeout=(3.05, None)) as response:
                # Process the stream directly
                current_event = {}
                
                for line in response.iter_lines(decode_unicode=True):
                    if self.stop_event.is_set():
                        logger.debug("SSE listener thread stopping as requested")
                        break
                        
                    if line:
                        logger.debug(f"SSE event received: {line}")
                        
                        # Parse SSE line
                        if line.startswith("event:"):
                            current_event["event"] = line.split(":", 1)[1].strip()
                        elif line.startswith("data:"):
                            current_event["data"] = line.split(":", 1)[1].strip()
                            
                            # If we have both event and data, process the event
                            if "event" in current_event and "data" in current_event:
                                # Put the event in the queue for the main thread to process
                                self.message_queue.put(current_event.copy())
                                
                                # Clear the current event
                                current_event = {}
                    
                    # Empty line can also mark the end of an event
                    elif current_event and "event" in current_event and "data" in current_event:
                        # Put the event in the queue for the main thread to process
                        self.message_queue.put(current_event.copy())
                        
                        # Clear the current event
                        current_event = {}
                        
        except Exception as e:
            if not self.stop_event.is_set():  # Only log error if we weren't asked to stop
                logger.error(f"Error in SSE listener thread: {e}")
        finally:
            logger.debug("SSE listener thread exiting")
    
    def _wait_for_response(self, request_id, timeout=10):
        """
        Wait for a response to a specific request
        
        Args:
            request_id (str): The ID of the request to wait for
            timeout (int): Timeout in seconds
            
        Returns:
            dict: The response, or None if timed out
        """
        response = None
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if we have any messages in the queue
                event = self.message_queue.get(block=True, timeout=0.5)
                
                # Process the event
                if event.get("event") == "message":
                    try:
                        # Parse the data as JSON
                        data = json.loads(event.get("data", "{}"))
                        
                        # Check if this is the response to our request
                        if data.get("id") == request_id:
                            response = data
                            logger.debug(f"Received response for request {request_id}")
                            break
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing event data as JSON: {event.get('data')}")
            except queue.Empty:
                # No messages in the queue, continue waiting
                pass
                
        return response


# Example usage
if __name__ == "__main__":
    # Enable debug logging
    logger.setLevel(logging.DEBUG)
    
    # Get MCP server URL from command line argument
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <server_url>")
        print("Example: python mcp_client.py https://your-mcp-server.example.com")
        sys.exit(1)
        
    server_url = sys.argv[1]
    
    print(f"Testing MCP client with server at {server_url}")
    
    # Use context manager to automatically connect and disconnect
    with MCPClient(server_url, debug=True) as client:
        # Initialize the session
        init_response = client.initialize()
        
        if init_response and "result" in init_response:
            print("\n✅ Successfully initialized MCP session")
            print(f"Server info: {init_response['result'].get('serverInfo')}")
            print(f"Protocol version: {init_response['result'].get('protocolVersion')}")
            print(f"Capabilities: {init_response['result'].get('capabilities')}")
            
            # List available tools
            print("\nListing available tools...")
            tools_response = client.list_tools()
            
            if tools_response and "result" in tools_response:
                print("\n✅ Successfully listed tools")
                print(f"Tools: {json.dumps(tools_response['result'], indent=2)}")
                
                # If we have tools, try to invoke one
                if tools_response['result'].get('tools') and len(tools_response['result']['tools']) > 0:
                    # Try the web search tool
                    web_search_tool = next((tool for tool in tools_response['result']['tools'] 
                                          if tool.get('name') == 'brave_web_search'), None)
                    
                    if web_search_tool:
                        print("\nTesting web search tool...")
                        
                        # Try with a simpler query string
                        search_params = {
                            "query": "bitcoin"
                        }
                        
                        search_response = client.invoke_tool('brave_web_search', search_params)
                        
                        if search_response and "result" in search_response:
                            print("\n✅ Successfully invoked web search tool")
                            print(f"Search results: {json.dumps(search_response['result'], indent=2)}")
                            
                            # Check if the response indicates an error
                            if search_response['result'].get('isError'):
                                print(f"\nThe tool returned an error: {search_response['result'].get('content', [{'text': 'Unknown error'}])[0].get('text')}")
                                
                                # Try with the local search tool instead
                                print("\nTrying local search tool instead...")
                                local_search_tool = next((tool for tool in tools_response['result']['tools'] 
                                                      if tool.get('name') == 'brave_local_search'), None)
                                
                                if local_search_tool:
                                    local_params = {
                                        "query": "pizza"
                                    }
                                    
                                    local_response = client.invoke_tool('brave_local_search', local_params)
                                    
                                    if local_response and "result" in local_response:
                                        print("\n✅ Successfully invoked local search tool")
                                        print(f"Search results: {json.dumps(local_response['result'], indent=2)}")
                                        
                                        if local_response['result'].get('isError'):
                                            print(f"\nThe local search tool also returned an error: {local_response['result'].get('content', [{'text': 'Unknown error'}])[0].get('text')}")
                        else:
                            print("\n❌ Failed to invoke web search tool")
                            if search_response and "error" in search_response:
                                print(f"Error: {search_response['error']}")
            elif tools_response and "error" in tools_response:
                print("\n❌ Failed to list tools")
                print(f"Error: {tools_response['error']}")
                print("This MCP server may not support the tools/list method.")
            else:
                print("\n❌ Failed to list tools - no response received")
        else:
            print("\n❌ Failed to initialize MCP session")
    
    print("\nMCP client test completed")
