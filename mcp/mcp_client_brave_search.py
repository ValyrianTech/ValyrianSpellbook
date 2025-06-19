#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from mcp_client import MCPClient


# Example usage
if __name__ == "__main__":
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
                            "query": "latest bitcoin price"
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
