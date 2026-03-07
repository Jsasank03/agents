"""
gemini.py
---------
Agent using Google Gemini API (free tier).
Model: gemini-2.0-flash

Setup:
    pip install google-generativeai
    Get free API key → https://aistudio.google.com/app/apikey
"""

import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# Import shared tools and task from agent_related.py
from agent_related import TASK, SYSTEM_PROMPT, execute_tool, log_tool_call

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
MODEL   = "gemini-2.0-flash"

# ─────────────────────────────────────────────
# Gemini-format tool definitions
# (Gemini uses FunctionDeclaration instead of JSON dicts)
# ─────────────────────────────────────────────

get_weather_func = FunctionDeclaration(
    name="get_weather",
    description="Get the current weather for a given city.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city, e.g. Tokyo"
            }
        },
        "required": ["city"]
    }
)

calculate_func = FunctionDeclaration(
    name="calculate",
    description="Evaluate a mathematical expression and return the result.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A valid math expression, e.g. '15 * 24'"
            }
        },
        "required": ["expression"]
    }
)

gemini_tools = Tool(function_declarations=[get_weather_func, calculate_func])

# ─────────────────────────────────────────────
# Gemini Agent
# ─────────────────────────────────────────────

def run_gemini_agent(user_message: str = TASK):
    print("\n" + "=" * 55)
    print("         GEMINI AGENT  (gemini-2.0-flash)")
    print("=" * 55)
    print(f"User: {user_message}\n")

    genai.configure(api_key=API_KEY)

    model = genai.GenerativeModel(
        model_name=MODEL,
        tools=[gemini_tools],
        system_instruction=SYSTEM_PROMPT,
    )

    chat    = model.start_chat()
    message = user_message

    while True:
        response = chat.send_message(message)
        part     = response.candidates[0].content.parts[0]

        # ── Agent wants to call a tool ──
        if hasattr(part, "function_call") and part.function_call.name:
            fc     = part.function_call
            name   = fc.name
            args   = dict(fc.args)
            result = execute_tool(name, args)
            log_tool_call(name, args, result)

            # Send tool result back as a function response
            from google.generativeai.types import content_types
            message = content_types.to_contents({
                "role": "function",
                "parts": [{
                    "function_response": {
                        "name": name,
                        "response": {"result": result}
                    }
                }]
            })

        # ── Agent is done ──
        else:
            final = response.text
            print(f"\nAssistant: {final}")
            return final


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_gemini_agent()