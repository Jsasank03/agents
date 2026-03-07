# groq.py — auto fallback agent
import json
import os
from groq import Groq
from groq import RateLimitError
from agent_related import TOOLS, TASK, SYSTEM_PROMPT, execute_tool, log_tool_call

GROQ_MODELS_FALLBACK = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
]
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
client = Groq(api_key=GROQ_API_KEY)

def run_groq_agent_with_fallback(user_message: str = TASK):
    for model in GROQ_MODELS_FALLBACK:
        try:
            print(f"\nTrying model: {model}")
            result = run_with_model(user_message, model)
            return result  # success, stop trying

        except RateLimitError:
            print(f"  ⚠ Rate limit hit on {model}, trying next...")
            continue  # try next model

    print("All models exhausted for today!")
    return None


def run_with_model(user_message: str, model: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024,
        )

        choice        = response.choices[0]
        message       = choice.message
        finish_reason = choice.finish_reason

        if finish_reason == "tool_calls":
            messages.append(message)
            for tool_call in message.tool_calls:
                name   = tool_call.function.name
                args   = json.loads(tool_call.function.arguments)
                result = execute_tool(name, args)
                log_tool_call(name, args, result)
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_call.id,
                    "content":      result,
                })

        elif finish_reason == "stop":
            print(f"Assistant ({model}): {message.content}")
            return message.content


if __name__ == "__main__":
    run_groq_agent_with_fallback()
"""

---

## Combined Free Tier Per Day (All Models Together)
```
Model                       RPD       TPD
─────────────────────────────────────────────
llama-3.3-70b-versatile     1,000     100K
llama-4-scout-17b           1,000     500K
llama-4-maverick-17b        1,000     500K
llama-3.1-8b-instant       14,400     500K
qwen3-32b                   1,000     500K
─────────────────────────────────────────────
TOTAL (combined)           19,400    2.1M tokens/day

"""