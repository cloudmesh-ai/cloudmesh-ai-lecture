
# Tutorial – Using an OpenAI Large Language Model (LLM)

This guide walks through the complete workflow for accessing OpenAI’s LLMs (GPT‑4, GPT‑3.5‑Turbo, etc.) from the command line and Python. It covers:

* required setup and credentials  
* installing the OpenAI SDK  
* making requests with **cURL** and with the **Python client** (including streaming)  
* integrating the model with **LangChain** for higher‑level workflows  
* cost‑management and reliability best practices  
* clean‑up steps to avoid accidental charges  

Everything is written in markdown without emojis or numbered lists.

---

## Prerequisites  

* An **OpenAI account** with API access.  
* An **API key** that begins with `sk-`.  
* **Python 3.9+** installed on your workstation.  
* **cURL** (generally pre‑installed on macOS and Linux).  
* (Optional) a virtual environment to isolate dependencies.  

---

## Obtaining and Securing the API Key  

1. Sign in to the OpenAI console at <https://platform.openai.com/account/api-keys>.  
2. Click **Create new secret key**, give it a descriptive name, and copy the generated key.  
3. Store the key in an environment variable so it is not hard‑coded in scripts:  

   ```bash
   export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

   Add the `export` line to your shell profile (`~/.bashrc`, `~/.zshrc`) if you want it persisted across sessions.

4. Treat the key like a password – never commit it to source control and rotate it periodically.

---

## Installing the OpenAI Python SDK  

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade openai
```

If you plan to use higher‑level abstractions (prompt chaining, retrieval‑augmented generation), install LangChain as well:

```bash
pip install langchain[all]
```

---

## Making a Simple Request with cURL  

The raw HTTP request is useful for quick tests or when you cannot install the Python client.

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
        "model": "gpt-4o-mini",
        "messages": [
          {"role": "user", "content": "Write a 4‑line poem about a sunrise over a mountain range."}
        ],
        "max_tokens": 128,
        "temperature": 0.7
      }'
```

The response is a JSON object that contains a `choices[0].message.content` field with the generated text.

---

## Using the OpenAI Python SDK  

### Basic synchronous completion  

```python
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain why the sky appears blue in simple terms."}],
    max_tokens=150,
    temperature=0.7,
)

print(response.choices[0].message.content.strip())
```

### Streaming response (real‑time output)  

```python
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

stream = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a funny story about a cat learning to paint."}],
    max_tokens=200,
    temperature=0.7,
    stream=True,
)

for chunk in stream:
    if chunk.get("choices"):
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            print(delta["content"], end="", flush=True)
print()  # final newline after the stream ends
```

### Managing conversation history  

```python
conversation = [
    {"role": "system", "content": "You are a helpful technical assistant."},
    {"role": "user", "content": "How does a neural network learn?"},
]

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=conversation,
    max_tokens=250,
    temperature=0.6,
)

assistant_reply = response.choices[0].message.content.strip()
conversation.append({"role": "assistant", "content": assistant_reply})

# Continue the dialogue by adding new user messages to `conversation` and calling the API again.
```

---

## Integrating Claude‑Style Prompting with LangChain  

LangChain provides a uniform interface for many LLM providers, including OpenAI. The example below shows a simple prompt‑template chain.

```python
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import os

llm = OpenAI(
    model_name="gpt-4o-mini",
    temperature=0.7,
    max_tokens=200,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

template = PromptTemplate(
    input_variables=["topic"],
    template="Write a concise Wikipedia‑style summary of the following topic: {topic}."
)

chain = LLMChain(prompt=template, llm=llm)

result = chain.run(topic="quantum entanglement")
print(result)
```

LangChain also supports agents, retrieval‑augmented generation, and tool usage. Consult the LangChain documentation for advanced patterns.

---

## Cost Management  

OpenAI bills per 1 000 tokens (input + output). Approximate pricing (as of October 2024) for the most common models:

| Model            | Input price (USD / 1 K tokens) | Output price (USD / 1 K tokens) |
|------------------|--------------------------------|---------------------------------|
| gpt‑4o‑mini      | $0.00015                        | $0.00060                        |
| gpt‑4o           | $0.00075                        | $0.00300                        |
| gpt‑4‑turbo      | $0.00100                        | $0.00300                        |
| gpt‑3.5‑turbo    | $0.00050                        | $0.00150                        |

Tips to keep spend under control:

* Set a **hard token limit** (`max_tokens`) appropriate for the expected answer length.  
* Use a **lower temperature** for deterministic outputs, reducing the need for multiple retries.  
* When streaming, stop reading as soon as the answer is sufficient to avoid extra output tokens.  
* Enable **budget alerts** in the OpenAI dashboard (Billing → Budgets).  
* Periodically export usage data (OpenAI console → Usage → Export CSV) and review token consumption.

---

## Reliability and Best Practices  

* **Retry logic** – network glitches or transient 5xx errors are common with any cloud API. Wrap calls in a retry loop with exponential back‑off. The official SDK already retries on server errors; for custom `requests` usage you need to implement it yourself.  
* **Rate limits** – OpenAI enforces per‑minute request caps per API key. If you receive a `429 Too Many Requests` response, pause for a few seconds before retrying. Consider applying for higher throughput via the OpenAI support portal if your workload requires it.  
* **Prompt design** – place instructions that guide model behavior at the **beginning** of the message list (system message). Keep prompts concise to reduce input token usage.  
* **Safety** – add a system message that explicitly forbids disallowed content. OpenAI’s moderation endpoint can be used to double‑check generated text if you need extra assurance.  
* **Version pinning** – specify the exact model name (`gpt-4o-mini`, `gpt-4o`, etc.) in every request to avoid accidental upgrades that might change behavior or pricing.  

Example of a safety‑oriented system prompt:

```json
{
  "role": "system",
  "content": "You are a helpful assistant. Do not generate content that is violent, hateful, self‑harm encouraging, or that violates OpenAI's usage policies."
}
```

---

## Cleaning Up  

OpenAI is a pure SaaS offering; there are no compute resources to delete. The only clean‑up steps are:

* **Revoke unused API keys** – go to the OpenAI console → **API Keys** → delete any keys you no longer need.  
* **Delete temporary files** – if you saved prompts, responses, or logs locally, remove them to free disk space.  

```bash
rm -rf ./prompts/
rm -f ./responses.json
```

---

## Full End‑to‑End Example (script)  

```python
#!/usr/bin/env python3
import os
import sys
import openai
from time import sleep

def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        sys.stderr.write("Error: OPENAI_API_KEY environment variable not set.\n")
        sys.exit(1)
    return key

def ask_question(question):
    client = openai.ChatCompletion
    response = client.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise technical writer."},
            {"role": "user", "content": question}
        ],
        max_tokens=200,
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()

def main():
    openai.api_key = get_api_key()
    question = "Provide a short explanation of how DNS works."
    answer = ask_question(question)
    print("\nAnswer:\n")
    print(answer)

if __name__ == "__main__":
    main()
```

Run the script after setting the environment variable:

```bash
chmod +x openai_demo.py
./openai_demo.py
```

---

## Recap  

* Obtain and protect an OpenAI API key.  
* Install the `openai` (and optionally `langchain`) Python packages.  
* Use **cURL** for quick tests or the **Python SDK** for programmatic interaction, including streaming.  
* Manage costs by limiting token usage and monitoring the dashboard.  
* Implement retries, respect rate limits, and include safety system messages.  
* Revoke unused keys when finished.  

With these steps you can reliably integrate OpenAI’s LLMs into scripts, applications, or larger AI pipelines. Happy building!