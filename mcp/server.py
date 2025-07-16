# server.py
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")


@mcp.tool(
    name="get_current_time",
    description="Get the current time",
)
def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
