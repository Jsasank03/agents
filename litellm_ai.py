"""
litellm_ai.py
-------------
Smart agent with 3-tier fallback:
  Tier 1 → Groq free models      (fastest, cloud)
  Tier 2 → Gemini free models    (if Groq exhausted)
  Tier 3 → Ollama local models   (if Gemini exhausted, always works)

Setup:
    pip install litellm python-dotenv
    Create a .env file (see .env.example below)
"""

import json
import os
import litellm
from dotenv import load_dotenv
from litellm.exceptions import RateLimitError, AuthenticationError, APIError

from agent_related import TOOLS, TASK, SYSTEM_PROMPT, execute_tool, log_tool_call

# ─────────────────────────────────────────────
# Load secrets from .env
# ─────────────────────────────────────────────

load_dotenv()

# Set LiteLLM Proxy URL (default: http://localhost:4000)
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")

# ─────────────────────────────────────────────
# Model tiers (priority order) — use proxy model names
# ─────────────────────────────────────────────

# Tier 1: Groq free models (best quality first, most daily tokens last as backup)
GROQ_MODELS = [
    "groq/llama-3.3-70b-versatile",           # 1,000 RPD | 100K TPD  ← best quality
    "groq/meta-llama/llama-4-scout-17b-16e-instruct",  # 1,000 RPD | 500K TPD
    "groq/meta-llama/llama-4-maverick-17b-128e-instruct",  # 1,000 RPD | 500K TPD
    "groq/qwen/qwen3-32b",                    # 1,000 RPD | 500K TPD
    "groq/llama-3.1-8b-instant",              # 14,400 RPD | 500K TPD ← highest RPD
]

# Tier 2: Gemini free models
GEMINI_MODELS = [
    "gemini/gemini-2.0-flash",                # 1,500 RPD free
    "gemini/gemini-2.0-flash-lite",           # 1,500 RPD free (lighter)
    "gemini/gemini-1.5-flash",                # 1,500 RPD free
    "gemini/gemini-1.5-flash-8b",             # 1,500 RPD free (smallest/fastest)
]

# Tier 3: Ollama local models (unlimited, always works if server is running)
OLLAMA_MODELS = [
    "ollama/llama3.1:8b",                     # pull: ollama pull llama3.1:8b
    "ollama/llama3.2:3b",                     # pull: ollama pull llama3.2:3b
    "ollama/llama3.2",                        # pull: ollama pull llama3.2
    "ollama/llama3.1",                        # pull: ollama pull llama3.1
    "ollama/mistral",                         # pull: ollama pull mistral
    "ollama/phi4",                            # pull: ollama pull phi4
]

# Full fallback chain: Groq → Gemini → Ollama
#ALL_MODELS = GROQ_MODELS + GEMINI_MODELS + OLLAMA_MODELS

ALL_MODELS = ["ollama/llama3.1:8b"]
# ─────────────────────────────────────────────
# Single model runner (via proxy)
# ─────────────────────────────────────────────

def run_with_model(messages: list, model: str) -> str:
    """Run the agentic loop with a specific model via LiteLLM Proxy."""
    while True:
        response = litellm.completion(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            api_base=LITELLM_PROXY_URL
        )

        message       = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # ── Tool call ──
        if finish_reason == "tool_calls" and message.tool_calls:
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

        # ── Done ──
        elif finish_reason == "stop":
            return message.content

        else:
            return message.content or "No response."

# ─────────────────────────────────────────────
# Main agent with 3-tier fallback
# ─────────────────────────────────────────────

def run_agent(user_message: str = TASK):
    print("\n" + "=" * 60)
    print("   LITELLM AGENT  —  3-Tier Fallback")
    print("   Groq  →  Gemini  →  Ollama (local)")
    print("=" * 60)
    print(f"User: {user_message}\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message},
    ]

    current_tier = None

    for model in ALL_MODELS:
        # Print tier banner when switching
        tier = get_tier(model)
        if tier != current_tier:
            current_tier = tier
            print(f"\n{'─'*60}")
            print(f"  Entering {tier}")
            print(f"{'─'*60}")

        print(f"\n  Trying → {model}")

        try:
            result = run_with_model(messages.copy(), model)
            print(f"\n✅ Success with: {model}")
            print(f"\nAssistant: {result}")
            return result

        except RateLimitError:
            print(f"  ⚠  Rate limit hit — moving to next model...")
            continue

        except AuthenticationError:
            print(f"  ✗  Auth error (check API key) — skipping {model}")
            continue

        except Exception as e:
            err = str(e).lower()
            # Treat connection errors as "not available"
            if "connection" in err or "refused" in err:
                print(f"  ✗  Model not available at proxy — skipping {model}")
                continue
            print(f"  ✗  Unexpected error: {e} — skipping...")
            continue

    print("\n❌ All models exhausted. No response available.")
    return None


def get_tier(model: str) -> str:
    if model in GROQ_MODELS:
        return "Tier 1 — Groq (Cloud Free)"
    elif model in GEMINI_MODELS:
        return "Tier 2 — Gemini (Cloud Free)"
    else:
        return "Tier 3 — Ollama (Local)"


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_agent()