"""
test_ollama.py
Simple test to run a prompt directly via LiteLLM proxy to Ollama
"""

import litellm
import os
from dotenv import load_dotenv

load_dotenv()

# Get proxy URL
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")

print("\n🚀 Testing Ollama via LiteLLM Proxy...\n")
print(f"   Proxy: {LITELLM_PROXY_URL}")
print(f"   Model: ollama/llama3.1:8b\n")
# Enable debug logs
#litellm.set_verbose = True
os.environ['LITELLM_LOG'] = 'DEBUG'
litellm._turn_on_debug()
try:
    response = litellm.completion(
        model="ollama/llama3.1:8b",
        messages=[
            {"role": "user", "content": "What is the weather in Tokyo? Also, what is 15 * 24?"}
        ],
        #api_base="http://localhost:11434"
        api_base="http://localhost:4000"  # via LiteLLM Proxy
    )
    
    print("✅ Response:")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ Error: {e}")