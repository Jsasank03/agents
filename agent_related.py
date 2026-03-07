"""
agent_related.py
----------------
Shared tools, tool definitions, and execution logic used by all agents.
Task: Ask about the weather in Tokyo AND calculate 15 * 24.
"""

import json

# ─────────────────────────────────────────────
# Tool definitions (OpenAI-compatible format)
# ─────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city, e.g. Tokyo"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A valid math expression, e.g. '15 * 24'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ─────────────────────────────────────────────
# Tool implementations
# ─────────────────────────────────────────────

def get_weather(city: str) -> str:
    """Simulated weather tool. Replace with a real API (e.g. OpenWeatherMap)."""
    mock_data = {
        "tokyo":   "Tokyo: 22°C, partly cloudy.",
        "london":  "London: 15°C, overcast.",
        "new york":"New York: 18°C, sunny.",
    }
    return mock_data.get(city.lower(), f"{city}: 25°C, clear skies.")


def calculate(expression: str) -> str:
    """Safely evaluate a basic math expression."""
    try:
        # Restrict to safe characters only
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Error: unsafe characters in expression."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"


# ─────────────────────────────────────────────
# Tool executor (call by name)
# ─────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> str:
    if name == "get_weather":
        return get_weather(**args)
    elif name == "calculate":
        return calculate(**args)
    return f"Unknown tool: {name}"


# ─────────────────────────────────────────────
# Shared task prompt
# ─────────────────────────────────────────────

TASK = "What is the weather in Tokyo? Also, what is 15 * 24?"

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Use the available tools to answer the user's question accurately."
)


# ─────────────────────────────────────────────
# Shared pretty-printer for tool calls
# ─────────────────────────────────────────────

def log_tool_call(name: str, args: dict, result: str):
    print(f"  [Tool Called]  {name}({json.dumps(args)})")
    print(f"  [Tool Result]  {result}")