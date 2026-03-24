# LiteLLM Proxy Setup

This guide explains how to run the LiteLLM Proxy server with your configuration and environment variables.

---

## 1. Install Requirements

```bash
pip install -r requirements.in
```

---

## 2. Prepare Your `.env` File

Create a `.env` file in this directory with your API keys:

```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 3. Start the LiteLLM Proxy

Run the following command to load environment variables and start the proxy with your config:

```bash
export $(cat .env | xargs) && litellm --config litellm_proxy_config.yaml
```

- This command ensures your API keys are available to the proxy via environment variables.
- The proxy will start at `http://localhost:4000` by default.

---

## 4. Usage

Configure your client code to use the proxy endpoint (`http://localhost:4000`) and the model names defined in `litellm_proxy_config.yaml`.

### Example: Chat Completion Request

```bash
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Example Response:**

```json
{
  "id": "chatcmpl-f79ec535-c66b-4243-8b18-f27c324a631e",
  "created": 1774176675,
  "model": "ollama/llama3.1:8b",
  "object": "chat.completion",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "Hello! How are you today? Is there something I can help you with or would you like to chat?",
        "role": "assistant"
      }
    }
  ],
  "usage": {
    "completion_tokens": 23,
    "prompt_tokens": 15,
    "total_tokens": 38
  }
}
```

---

## 5. Notes

- You can add or remove models in `litellm_proxy_config.yaml` as needed.
- Make sure your Ollama server is running if you use local models.

---