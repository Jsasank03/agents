# 🦙 Ollama Complete Guide
> Everything you need to know about running LLMs locally with Ollama

---

## 📋 Table of Contents
1. [What is Ollama](#what-is-ollama)
2. [How Ollama Works](#how-ollama-works)
3. [Installation](#installation)
4. [Hardware Requirements](#hardware-requirements)
5. [Your GPU — RTX 3050 4GB](#your-gpu--rtx-3050-4gb)
6. [GPU vs CPU — Auto Detection](#gpu-vs-cpu--auto-detection)
7. [Models — Pull & Run](#models--pull--run)
8. [Creating Custom Models](#creating-custom-models)
9. [Using Ollama in Python](#using-ollama-in-python)
10. [Using with LiteLLM](#using-with-litellm)
11. [Troubleshooting](#troubleshooting)
12. [Quick Reference](#quick-reference)

---

## What is Ollama

Ollama is a tool that lets you **download and run LLMs (Large Language Models) locally** on your own machine — like having a mini ChatGPT running entirely on your computer with:

- ✅ No internet required (after download)
- ✅ No API key needed
- ✅ No rate limits
- ✅ 100% private — data never leaves your machine
- ✅ Completely free forever

---

## How Ollama Works

```
You (Python / CLI / API)
        │
        ▼
Ollama Python SDK  (or HTTP request)
        │
        ▼
Ollama Server  (localhost:11434)
        │
        ▼
llama.cpp  (inference engine — written in C++)
        │
        ├──→ GPU (VRAM)   ← model layers if GPU available  ⚡ fast
        └──→ CPU (RAM)    ← remaining layers or fallback   🐢 slow
        │
        ▼
Token stream → response back to you
```

### Key Components

| Component | Role |
|---|---|
| **Ollama Server** | Local HTTP server at `localhost:11434`, manages models |
| **llama.cpp** | Inference engine under the hood, optimized C++ |
| **GGUF format** | Compressed quantized model format stored locally |
| **Quantization** | Reduces model size (32-bit → 4-bit), saves VRAM |

### Where Models Are Stored

```
Mac/Linux:   ~/.ollama/models
Windows:     C:\Users\<you>\.ollama\models
```

---

## Installation

### Linux / Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download the installer from [https://ollama.com/download](https://ollama.com/download)

### Verify Installation
```bash
ollama --version
ollama serve        # start the server manually (auto-starts on most systems)
```

---

## Hardware Requirements

### By Model Size (CPU Only — No GPU needed)

| Model | Disk Size | Min RAM | Speed (CPU) |
|---|---|---|---|
| llama3.2:1b | 1.3GB | 4GB | ~10 tok/sec |
| llama3.2:3b | 2.0GB | 6GB | ~7 tok/sec |
| llama3.1:8b | 4.7GB | 8GB | ~3 tok/sec |
| mistral:7b | 4.1GB | 8GB | ~3 tok/sec |
| phi4 | 9.1GB | 16GB | ~2 tok/sec |
| llama3.3:70b | 43GB | 64GB | ~0.5 tok/sec |

> CPU works on any laptop/desktop but is slow. Even a basic GPU makes it 10–20× faster.

### By GPU VRAM

| GPU VRAM | Best Model | Speed |
|---|---|---|
| 4GB | llama3.2:3b (Q4) | ~35 tok/sec |
| 6GB | llama3.1:8b (Q4) | ~40 tok/sec |
| 8GB | llama3.1:8b (Q8) | ~50 tok/sec |
| 12GB | mistral:7b full | ~60 tok/sec |
| 16GB | llama3.1:13b | ~55 tok/sec |
| 24GB | llama3.3:70b (Q2/Q3) | ~20 tok/sec |
| 48GB | llama3.3:70b (Q4) ✅ | ~40 tok/sec |
| 80GB | llama3.3:70b (FP16) | ~60 tok/sec |

### Apple Silicon (Best Local Performance)

| Chip | Unified Memory | Best Model |
|---|---|---|
| M1 | 8GB | 7B models |
| M2 | 16GB | 13B models |
| M3 Pro | 18–36GB | 30B models |
| M3 Max | 48–96GB | 70B models ✅ |

> Apple Silicon uses **unified memory** (shared CPU+GPU). 16GB Mac = 16GB effective "VRAM". Very efficient.

### Quantization Levels Explained

| Quant | Size (7B model) | RAM Needed | Quality |
|---|---|---|---|
| Q2 | ~2.5GB | ~4GB | Lower |
| Q4 | ~4GB | ~6GB | Good balance ✅ |
| Q8 | ~7GB | ~10GB | Near full |
| FP16 | ~14GB | ~18GB | Full quality |

```bash
# Pull specific quantization
ollama pull llama3.2            # default (Q4)
ollama pull llama3.2:3b-fp16   # full precision (needs more RAM)
ollama pull llama3.2:1b        # smallest version
```

---

## Your GPU — RTX 3050 4GB

```
GPU:         NVIDIA GeForce RTX 3050 (Laptop)
VRAM:        4096 MiB = 4GB
CUDA:        13.0  ✅
Driver:      580.126.09  ✅
```

### What You Can Run

| Model | VRAM Needed | Fits? | Speed | Recommended? |
|---|---|---|---|---|
| llama3.2:1b (Q4) | ~1.3GB | ✅ Full GPU | ~50 tok/sec | ⚡ Fastest |
| llama3.2:3b (Q4) | ~2.0GB | ✅ Full GPU | ~35 tok/sec | ⭐ Sweet spot |
| phi4-mini (Q4) | ~2.5GB | ✅ Full GPU | ~30 tok/sec | 💻 Best for coding |
| llama3.1:8b (Q4) | ~4.7GB | ⚠️ Split | ~15 tok/sec | Partial GPU |
| mistral:7b (Q4) | ~4.1GB | ⚠️ Split | ~15 tok/sec | Partial GPU |
| llama3.3:70b (Q4) | ~43GB | ❌ CPU only | ~2 tok/sec | Not recommended |

### Recommended Models for RTX 3050 4GB

```bash
ollama pull llama3.2:3b    # ⭐ best overall for 4GB
ollama pull llama3.2:1b    # ⚡ fastest, very light
ollama pull phi4-mini      # 💻 best for coding tasks
```

---

## GPU vs CPU — Auto Detection

Ollama **automatically** detects and uses your GPU. You don't need to configure anything.

### Decision Flow

```
Ollama starts a model
        │
        ▼
Does model fit in VRAM?
        │
      YES ──→ 100% GPU  ⚡  (~30–50 tok/sec on RTX 3050)
        │
       NO ──→ Fits partially?
                │
             YES ──→ Split (GPU layers + CPU layers)  ~15 tok/sec
                │
               NO ──→ 100% CPU  🐢  (~3–5 tok/sec)
```

### Verify GPU is Being Used

```bash
# Terminal 1 — start a model
ollama run llama3.2:3b

# Terminal 2 — check processor
ollama ps
```

```
# GPU in use ✅
NAME           SIZE    PROCESSOR
llama3.2:3b    2.0GB   100% GPU

# CPU only ⚠️
NAME           SIZE    PROCESSOR
llama3.2:3b    2.0GB   100% CPU
```

```bash
# Watch nvidia-smi live — GPU-Util should spike when chatting
watch -n 1 nvidia-smi
```

---

## Models — Pull & Run

### Basic Commands

```bash
# Download a model
ollama pull llama3.2

# Chat in terminal
ollama run llama3.2

# Run with a one-shot prompt
ollama run llama3.2 "Explain quantum computing in 2 lines"

# List all downloaded models
ollama list

# Delete a model
ollama rm llama3.2

# See currently loaded models + which processor
ollama ps

# Show model info (size, quantization, parameters)
ollama show llama3.2

# Stop a specific running model (free up VRAM/RAM)
ollama stop llama3.1:8b
```

### Popular Models

| Model | Best For | Size | Pull Command |
|---|---|---|---|
| llama3.2:3b | General use | 2GB | `ollama pull llama3.2:3b` |
| llama3.2:1b | Speed / light use | 1.3GB | `ollama pull llama3.2:1b` |
| llama3.1:8b | High quality | 4.7GB | `ollama pull llama3.1:8b` |
| mistral:7b | General / fast | 4.1GB | `ollama pull mistral` |
| phi4-mini | Coding | 2.5GB | `ollama pull phi4-mini` |
| phi4 | Coding (bigger) | 9.1GB | `ollama pull phi4` |
| qwen2.5:7b | Multilingual | 4.7GB | `ollama pull qwen2.5:7b` |
| deepseek-r1:7b | Reasoning | 4.7GB | `ollama pull deepseek-r1:7b` |
| nomic-embed-text | Embeddings/RAG | 274MB | `ollama pull nomic-embed-text` |

---

## Creating Custom Models

You can create your own model with a custom system prompt, personality, and parameters **baked in permanently**.

### Step 1 — Create a Modelfile

```bash
nano Modelfile
```

```dockerfile
# ── Modelfile ──────────────────────────────────────

# Base model
FROM llama3.2:3b

# Temperature: 0.0 = focused/deterministic, 1.0 = creative/random
PARAMETER temperature 0.7

# Context window (how much conversation it remembers)
PARAMETER num_ctx 4096

# Max tokens to generate per response
PARAMETER num_predict 512

# Reduce repetition
PARAMETER repeat_penalty 1.1

# System prompt — baked into every conversation
SYSTEM """
You are an expert Python developer and AI agent specialist.
You write clean, well-commented, production-ready code.
You always explain your reasoning step by step.
When given a task, break it into small manageable steps.
Never write code without explaining what it does.
"""
```

### Step 2 — Build the Model

```bash
ollama create my-python-expert -f Modelfile
```

### Step 3 — Run It

```bash
ollama run my-python-expert
```

### Full Modelfile Reference

```dockerfile
FROM llama3.2:3b             # base model (required)

# ── Sampling Parameters ───────────────────────
PARAMETER temperature    0.8   # creativity (0.0–1.0)
PARAMETER top_p          0.9   # nucleus sampling
PARAMETER top_k          40    # top-k sampling
PARAMETER num_ctx        8192  # context window
PARAMETER num_predict    512   # max output tokens
PARAMETER repeat_penalty 1.1   # reduce repetition
PARAMETER seed           42    # fixed seed (reproducible output)

# ── Stop Sequences ───────────────────────────
PARAMETER stop "User:"
PARAMETER stop "<|end|>"

# ── System Prompt ────────────────────────────
SYSTEM """
Your custom instructions here.
Can be multiple lines.
"""

# ── Few-shot Examples ────────────────────────
MESSAGE user "What is 2+2?"
MESSAGE assistant "2+2 = 4."

MESSAGE user "Write hello world in Python"
MESSAGE assistant """
```python
print("Hello, World!")
```
"""
```

### Custom Model Examples

#### Customer Support Bot
```dockerfile
FROM llama3.2:3b
PARAMETER temperature 0.3
PARAMETER num_ctx 8192
SYSTEM """
You are a customer support agent for TechCorp.
Only answer questions about our products.
Always be polite and professional.
If unsure, say "Let me check that for you."
Never make up information.
"""
```

#### Code Reviewer
```dockerfile
FROM phi4-mini
PARAMETER temperature 0.1
SYSTEM """
You are a strict senior code reviewer.
Review code for: bugs, security issues, performance, readability.
Always reference specific line numbers.
Suggest improvements with code examples.
"""
```

#### Bilingual Hindi-English Assistant
```dockerfile
FROM qwen2.5:7b
PARAMETER temperature 0.7
SYSTEM """
You are a bilingual assistant fluent in Hindi and English.
Respond in the same language the user writes in.
If the user writes in Hinglish, respond in Hinglish.
"""
```

---

## Using Ollama in Python

### Install SDK
```bash
pip install ollama
```

### Basic Chat
```python
import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {"role": "user", "content": "What is Python?"}
    ]
)
print(response["message"]["content"])
```

### Streaming Response
```python
import ollama

stream = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)
```

### With Tool Calling (Agent)
```python
import ollama
import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }
]

response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Weather in Tokyo?"}],
    tools=tools,
)

if response["message"].get("tool_calls"):
    for tool_call in response["message"]["tool_calls"]:
        name = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]
        print(f"Tool: {name}, Args: {args}")
```

### REST API (No SDK needed)
```bash
curl http://localhost:11434/api/chat \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

---

## Using with LiteLLM

```python
import litellm

# Ollama models are prefixed with "ollama/"
response = litellm.completion(
    model="ollama/llama3.2:3b",
    messages=[{"role": "user", "content": "Hello!"}],
    api_base="http://localhost:11434"  # point to local server
)

print(response.choices[0].message.content)
```

### In litellm_ai.py — Best Models for RTX 3050 4GB
```python
OLLAMA_MODELS = [
    "ollama/llama3.2:3b",    # ⭐ best overall for 4GB VRAM
    "ollama/phi4-mini",      # 💻 great for coding
    "ollama/llama3.2:1b",    # ⚡ fastest fallback
]
```

---

## Troubleshooting

### Ollama Not Using GPU

```bash
# 1. Verify CUDA is visible
nvidia-smi                          # should show your GPU ✅

# 2. Check Ollama detects GPU
ollama info                         # should list CUDA devices

# 3. Reinstall Ollama (re-detects CUDA)
curl -fsSL https://ollama.com/install.sh | sh

# 4. Check Ollama service logs
journalctl -u ollama -f
```

### Model Too Slow

```bash
# Check if running on CPU instead of GPU
ollama ps
# If shows "100% CPU" → model too big for your VRAM

# Solution: use a smaller model
ollama pull llama3.2:1b     # fits easily in 4GB
ollama run llama3.2:1b
```

### Out of Memory Error

```bash
# Free up VRAM — stop loaded models
ollama stop llama3.2:3b

# Use smaller quantization
ollama pull llama3.2:3b     # Q4 by default (smaller)

# Check what's loaded
ollama ps
```

### Server Not Running

```bash
# Start server manually
ollama serve

# Check if running
curl http://localhost:11434
# Should return: "Ollama is running"

# Enable auto-start on Linux
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Connection Refused in Python

```python
# Make sure server is running first
# ollama serve

import ollama
try:
    response = ollama.chat(model="llama3.2:3b", messages=[...])
except Exception as e:
    print(f"Is ollama serve running? Error: {e}")
```

---

## Quick Reference

### Commands Cheat Sheet

```bash
# ── Setup ─────────────────────────────────────
ollama serve                          # start server
ollama --version                      # check version

# ── Models ────────────────────────────────────
ollama pull llama3.2:3b               # download model
ollama run  llama3.2:3b               # chat in terminal
ollama run  llama3.2:3b "your prompt" # one-shot prompt
ollama list                           # show downloaded models
ollama rm   llama3.2:3b               # delete model
ollama show llama3.2:3b               # model details
ollama ps                             # currently loaded models

# ── Custom Models ─────────────────────────────
ollama create mymodel -f Modelfile    # create custom model
ollama run mymodel                    # run custom model
ollama rm mymodel                     # delete custom model

# ── Monitoring ────────────────────────────────
watch -n 1 nvidia-smi                 # live GPU stats
ollama ps                             # check GPU vs CPU usage
journalctl -u ollama -f               # server logs (Linux)
```

### Your RTX 3050 4GB — Best Setup

```bash
# Install recommended models
ollama pull llama3.2:3b    # ⭐ primary model
ollama pull llama3.2:1b    # ⚡ fast backup
ollama pull phi4-mini      # 💻 coding tasks

# Verify GPU usage
ollama run llama3.2:3b
# In another terminal:
ollama ps                  # should show "100% GPU"
```

### Hardware Decision Guide

| Your Hardware | Best Model | Command |
|---|---|---|
| Old laptop (4GB RAM, no GPU) | llama3.2:1b | `ollama pull llama3.2:1b` |
| Normal laptop (8GB RAM) | llama3.2:3b | `ollama pull llama3.2:3b` |
| RTX 3050 4GB ← You are here | llama3.2:3b | `ollama pull llama3.2:3b` |
| Gaming PC (8GB VRAM) | llama3.1:8b | `ollama pull llama3.1:8b` |
| Gaming PC (16GB VRAM) | llama3.1:13b | `ollama pull llama3.1:13b` |
| M2 MacBook Pro (16GB) | llama3.1:8b | `ollama pull llama3.1:8b` |
| M3 Max / RTX 4090 | llama3.3:70b | `ollama pull llama3.3:70b` |

---

*Generated for NVIDIA GeForce RTX 3050 4GB — CUDA 13.0 — Driver 580.126.09*

# open-webui

pip install open-webui

# Start it
open-webui serve

# Open browser → http://localhost:8080