import asyncio
from fastmcp import Client


async def example():
    async with Client("http://127.0.0.1:8000/mcp/") as client:
        await client.ping()
        result = await client.call_tool("get_current_time")
        print(result)
        tools = await client.list_tools()
    # tools -> list[mcp.types.Tool]
    
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")


if __name__ == "__main__":
    asyncio.run(example())
