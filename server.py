import os
import json
import sys
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from controller_wrapper import *

# 初始化 MCP 服务
mcp = FastMCP("WeatherAndSearchAPI")

# ============================
# 第一步：定义工具结构并立即输出（必须是 stdout 的第一行）
# ============================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_brave",
            "description": "Search the web using Brave Search API",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move",
            "description": "Move robot arm to a specific position",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"}
                },
                "required": ["x", "y", "z"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open",
            "description": "Open the gripper",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close",
            "description": "Close the gripper",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "position",
            "description": "Get current position of robot arm",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ✅ 输出 tools JSON 到 stdout（MCP 客户端会读取这行）
print(json.dumps({"tools": tools}), flush=True)

# ============================
# 工具注册（@mcp.tool）定义
# ============================

@mcp.tool()
def move(x: float, y: float, z: float) -> str:
    """Move robot arm to a specific (x, y, z) position"""
    postion = [x,y,z]
    move_to_xyz(position=postion)
    return f"Moved to ({x}, {y}, {z})"

@mcp.tool()
def open() -> str:
    """Open the gripper of the robot"""
    gripper_servo_open()
    return "Gripper opened."

@mcp.tool()
def close() -> str:
    """Close the gripper of the robot"""
    gripper_servo_close()
    return "Gripper closed."

@mcp.tool()
def position() -> str:
    """Get current position of robot arms"""
    pos = get_pose()
    return f"Current position: x={pos[0]}, y={pos[1]}, z={pos[2]}"

# ============================
# 异步工具定义
# ============================

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

@mcp.tool()
async def get_weather(city: str) -> str:
    print(f"[CALL] get_weather(city={city})", file=sys.stderr)
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"{city} weather: {desc}, {temp}°C"
    except Exception as e:
        return f"Failed to get weather for {city}: {e}"

@mcp.tool()
async def search_brave(query: str) -> str:
    print(f"[CALL] search_brave(query={query})", file=sys.stderr)
    url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            results = response.sjson()["web"]["results"]
            if not results:
                return f"No results found for '{query}'"
            top = results[0]
            return f"Top result: {top['title']} - {top['url']}"
    except Exception as e:
        return f"Search failed: {e}"

# ============================
# 启动 MCP 服务
# ============================
if __name__ == "__main__":
    print("[MCP] Server is starting...", file=sys.stderr)
    mcp.run()

