
# Using an Anthropic LLM (Claude) – Step‑by‑Step Tutorial  

This document shows how to run Anthropic’s Claude models from your own environment.  
It covers obtaining credentials, installing the required tools, making API calls with **curl** and **Python**, integrating the model with **LangChain**, and best‑practice tips for cost and reliability.  
All commands are written for a Unix‑like shell (Linux/macOS). Adjust paths as needed for Windows.

---

## Overview  

Anthropic provides a hosted inference service that exposes Claude‑3 (sonnet, opus, haiku) and earlier Claude‑2 families via a simple HTTPS API.  
You interact with the service by sending a JSON payload that contains a prompt (or series of messages) and receiving a generated response.  
The service is token‑based: you are charged for the number of input and output tokens processed.

---

## Prerequisites  

* An **Anthropic account** with API access.  
* A **valid API key** (starts with `sk-`).  
* **Python 3.9+** installed.  
* Optional but recommended: a virtual environment to keep dependencies isolated.  
* **cURL** (generally pre‑installed on macOS/Linux).  

---

## Obtaining an Anthropic API Key  

1. Sign in to the Anthropic console at https://console.anthropic.com/.  
2. Navigate to **API Keys** in the sidebar.  
3. Click **Create a key**, give it a descriptive name, and copy the generated secret.  
4. Store the key securely; treat it like a password. A common practice is to place it in an environment variable:  

   ```bash
   export ANTHROPIC_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

   Add the `export` line to your shell profile (`~/.bashrc`, `~/.zshrc`) if you want it persisted.

---

## Installing the Required Libraries  

Create a virtual environment (optional but encouraged):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the official Anthropic Python client and supporting packages:

```bash
pip install --upgrade anthropic requests tqdm
```

If you plan to use **LangChain**, install the extra dependency:

```bash
pip install langchain[anthropic]
```

---

## Making a Simple Request with cURL  

The raw HTTP request is useful for quick testing or when you cannot install the Python client.

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 256,
        "temperature": 0.7,
        "messages": [
          {"role": "user", "content": "Write a short poem about a sunrise over a mountain range."}
        ]
      }'
```

The response is a JSON object containing a `content` field with the generated text.

---

## Using the Anthropic Python SDK  

The SDK wraps the HTTP API and handles retries, timeouts, and streaming responses.

### Basic synchronous call

```python
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.completions.create(
    model="claude-3-sonnet-20240229",
    max_tokens_to_sample=256,
    temperature=0.7,
    prompt=HUMAN_PROMPT + "Explain why the sky appears blue in simple terms." + AI_PROMPT
)

print(response.completion)
```

### Chat‑style interaction (preferred for multi‑turn dialogs)

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

messages = [
    {"role": "user", "content": "I need a meal plan for a vegetarian diet for a week."}
]

response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=512,
    temperature=0.6,
    messages=messages
)

print(response.content[0].text)
```

### Streaming responses (real‑time UI)

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

stream = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=256,
    temperature=0.7,
    messages=[{"role": "user", "content": "Tell me a funny story about a cat."}],
    stream=True
)

for event in stream:
    if event.type == "content_block_delta":
        print(event.delta.text, end="", flush=True)
print()   # final newline after the stream ends
```

---

## Integrating Claude with LangChain  

LangChain provides a unified interface for many LLM providers, making it easy to chain prompts, retrieve knowledge, or build agents.

```python
from langchain.llms import Anthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialise the LangChain wrapper
llm = Anthropic(
    model="claude-3-sonnet-20240229",
    temperature=0.7,
    max_tokens=256,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Simple prompt template
template = PromptTemplate(
    input_variables=["topic"],
    template="Write a concise Wikipedia‑style summary of {topic}."
)

chain = LLMChain(prompt=template, llm=llm)

# Execute the chain
result = chain.run(topic="quantum entanglement")
print(result)
```

LangChain also supports **agents**, **retrieval‑augmented generation**, and **tool‑use** patterns with Claude. Refer to the LangChain documentation for advanced use cases.

---

## Cost Considerations  

Anthropic bills per 1 000 tokens (input + output). Approximate pricing (as of 2024‑10; verify the latest rates on the Anthropic pricing page):

| Model               | Input price (USD / 1 K tokens) | Output price (USD / 1 K tokens) |
|---------------------|-------------------------------|---------------------------------|
| Claude‑3‑haiku      | $0.0002                       | $0.0006                         |
| Claude‑3‑sonnet     | $0.0008                       | $0.0024                         |
| Claude‑3‑opus       | $0.0015                       | $0.0045                         |
| Claude‑2‑100k       | $0.0010                       | $0.0030                         |

Tips to keep costs under control  

* Set a **hard token limit** (`max_tokens`) that matches the expected answer length.  
* Use a **lower‑temperature** setting for deterministic output, which can reduce the need for multiple retries.  
* Enable **streaming** when building interactive UI; you can stop the stream early if the answer is sufficient, saving output tokens.  
* Periodically audit your usage via the Anthropic console → **Usage** → **Export CSV**.

---

## Reliability and Best Practices  

* **Retries** – network failures are common when calling external APIs. The official SDK automatically retries on 5xx errors; for custom `requests` calls, implement exponential back‑off.  
* **Rate limits** – Anthropic enforces per‑minute request caps per API key. If you receive a `429 Too Many Requests` response, back off for a few seconds before retrying.  
* **Prompt design** – keep system messages concise, and place the most important instruction at the beginning of the message list.  
* **Token budgeting** – the `max_tokens` field caps output length, but input tokens still count toward billing. Trim long histories or use summarization steps when maintaining long conversations.  
* **Safety** – Anthropic’s models respect the `system` message for content‑policy steering. Use it to explicitly disallow disallowed content.  

Example system prompt:

```json
{
  "role": "system",
  "content": "You are a helpful assistant. Do not generate any content that is violent, hateful, or self‑harm encouraging."
}
```

---

## Troubleshooting  

| Symptom | Likely cause | Resolution |
|---------|--------------|------------|
| `401 Unauthorized` response | Invalid or missing API key | Verify `ANTHROPIC_API_KEY` is set correctly and not expired |
| `429 Too Many Requests` | Exceeded rate limit | Add a delay (`time.sleep`) before retrying; consider requesting a higher quota from Anthropic |
| Empty `completion` field | Prompt too short or malformed | Ensure the prompt includes the required `\n\nAssistant:` marker when using the completions endpoint; for messages endpoint, use a proper `messages` list |
| Connection timeout | Network instability or firewall blocking `api.anthropic.com:443` | Test connectivity with `curl -v https://api.anthropic.com/v1/models`; open outbound HTTPS if blocked |

---

## Clean‑up  

Anthropic is a pure SaaS offering—there are no compute resources to delete. The only clean‑up steps involve revoking API keys you no longer need:

```bash
# In the Anthropic console → API Keys → Delete the key
```

If you created temporary storage (e.g., files with prompts or logs), delete them locally:

```bash
rm -rf ./prompt_logs/
```

---

## Full Example Script (end‑to‑end)  

```python
#!/usr/bin/env python3
import os
import sys
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.stderr.write("Error: ANTHROPIC_API_KEY environment variable not set.\n")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Build a multi‑turn conversation
    messages = [
        {"role": "system", "content": "You are a concise technical writer."},
        {"role": "user", "content": "Explain the difference between TCP and UDP in two sentences."}
    ]

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=128,
        temperature=0.5,
        messages=messages
    )

    print("\nClaude response:\n")
    print(response.content[0].text.strip())

if __name__ == "__main__":
    main()
```

Run the script after setting `ANTHROPIC_API_KEY`:

```bash
chmod +x claude_demo.py
./claude_demo.py
```

---

## Recap  

* Obtain an API key from the Anthropic console.  
* Install the `anthropic` Python package (or use plain `curl`).  
* Choose a model (`claude-3-haiku`, `claude-3-sonnet`, `claude-3-opus`, or older Claude‑2 variants).  
* Send a prompt via the **messages** endpoint for chat‑style interaction or **completions** for simple text generation.  
* Manage costs by limiting `max_tokens`, monitoring usage, and using streaming when appropriate.  
* Apply best‑practice patterns for retries, rate‑limit handling, and safety prompts.  

You now have a complete, production‑ready workflow for leveraging Anthropic’s Claude models from the command line or within Python applications. Happy building!