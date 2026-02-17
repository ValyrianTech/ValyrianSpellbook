from fastmcp import Client

async def main():
    # Connect to the SSE server
    async with Client("https://x2srptru005vf3-8080.proxy.runpod.net/sse/") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        # Call the add tool
        result = await client.call_tool("brave_web_search", {"query": "latest bitcoin price"})
        print(f"query result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
