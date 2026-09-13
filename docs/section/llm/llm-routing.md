
# 📚 Litellm vs OpenRouter (and the rest of the LLM‑routing ecosystem)

**Litellm** is a **Python SDK** that lets you **talk to many LLM providers through a single, unified API** (OpenAI‑style, Azure‑style, etc.) and adds handy extras (cost tracking, rate‑limit handling, caching, tracing).  
**OpenRouter** is a **hosted gateway** that aggregates dozens of model providers **behind a single OpenAI‑compatible endpoint**. It provides its own **pricing tier, quota management, and safety‑layers** but doesn’t give you a full‑featured SDK.

Both solve the **“vendor lock‑in”** problem, but they sit at different layers:

| Layer | What it does | Primary artifact | Who you are |
|-------|--------------|------------------|-------------|
| **SDK / library** | Unified client, helpers, middleware | `litellm` (Python package) | Want code‑level control, custom routing, caching, analytics |
| **Hosted gateway** | Single endpoint that forwards requests to many back‑ends | OpenRouter API (OpenAI‑compatible) | Want a quick drop‑in endpoint, no self‑hosting, built‑in safety & billing |
| **Full‑stack platform** | End‑to‑end workflow, UI, logging, prompting tools | LangChain, LlamaIndex, CrewAI, etc. | Building a product / research pipeline that needs orchestration, memory, agents |

Below is a **step‑by‑step tutorial** that:

1. Explains each tool and the landscape.
2. Shows how to **install and get started** with Litellm and OpenRouter.
3. Walks through **basic and advanced usage** (routing, cost tracking, prompt caching, safety filters).
4. Provides a **quick comparison** with other common options.
5. Offers **best‑practice recommendations** for production.

---  

## 1️⃣ The Landscape: Why “router” libraries / services exist

| Problem | Traditional approach (single provider) | Router‑centric solution |
|---------|----------------------------------------|--------------------------|
| **Provider lock‑in** | Hard‑coded `openai.ChatCompletion` → switch needs code changes | Unified API (same request shape for OpenAI, Anthropic, Cohere, etc.) |
| **Cost optimisation** | You must manually compare prices & switch | Centralised cost‑tracking, auto‑fallback to cheaper models |
| **Rate‑limit handling** | Individual retry logic per provider | Global retry/back‑off middleware |
| **Observability** | Scatter‑gather logs per SDK | Centralised tracing, latency & token usage metrics |
| **Safety & policy** | Custom guardrails per provider | Optional safety layer (OpenRouter) or plug‑ins (Litellm) |

Two major patterns emerge:

| Pattern | Example | Typical use‑case |
|---------|---------|------------------|
| **Self‑hosted SDK** | `litellm`, `openai‑proxy`, `llama‑cpp‑python` | You run the code, you control caching, logging, custom routing |
| **Hosted gateway** | **OpenRouter**, **RapidAPI LLM Hub**, **Cohere Platform** | You prefer a managed endpoint, minimal ops, built‑in safety tiers |

---

## 2️⃣ Litellm – The “Swiss‑army knife” Python SDK

### 2.1 What is Litellm?

* **Open‑source (MIT) Python package** that implements a **single function `completion()` / `chat_completion()`** accepting the OpenAI request schema.
* Internally maps the call to the appropriate provider (`openai`, `anthropic`, `cohere`, `groq`, `mistral`, `google`, `together`, `huggingface`, Azure, etc.).
* Provides **optional add‑ons**:
  * **Cost tracking** (`litellm.get_model_cost_map()`, `litellm.token_counter`)
  * **Caching** (in‑memory, Redis, DynamoDB, or custom)
  * **Rate‑limit & retry middleware**
  * **Safety/Content‑filter plug‑ins** (moderation, profanity, custom regex)
  * **Telemetry** (OpenTelemetry, LangChain callbacks)

### 2.2 Install & basic usage

```bash
pip install litellm
```

```python
import litellm

# 1️⃣ Set your API keys (environment variables or dict)
# Example: mix of OpenAI and Anthropic keys
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

# 2️⃣ Simple chat with OpenAI's gpt‑4o
resp = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about sunrise"}],
)

print(resp.choices[0].message.content)
```

### 2.3 Routing to multiple providers

Litellm’s **`model="provider/model"`** syntax picks the backend:

| Syntax | Meaning |
|--------|---------|
| `gpt-4o` | OpenAI (default) |
| `anthropic/claude-3-5-sonnet` | Anthropic |
| `groq/llama3-70b` | Groq |
| `together/meta-llama/Meta-Llama-3.1-8B-Instruct` | Together.ai |

> **Tip:** You can create a **router map** to automatically fall back to a cheaper model if the primary one is overloaded or too expensive.

```python
router_map = {
    # primary model
    "primary": "anthropic/claude-3-5-sonnet",
    # fallback order
    "fallbacks": ["groq/llama3-70b", "openai/gpt-3.5-turbo"]
}
```

Litellm supplies a helper **`router`**:

```python
from litellm import Router

router = Router(router_map=router_map)

response = router.completion(
    model="primary",                 # name from router_map
    messages=[{"role":"user","content":"Explain quantum tunneling in 2 sentences"}],
)

print(response.choices[0].message.content)
```

If the primary model returns a **429 (rate‑limit)** or **500** error, Litellm will retry the request on the next fallback model automatically.

### 2.4 Cost‑tracking & token counting

```python
from litellm import get_model_cost_map, token_counter

costs = get_model_cost_map()
print(costs["gpt-4o"])   # => {"input_cost_per_token": 0.000005, "output_cost_per_token": 0.000015}

# Count tokens for a request (useful for budgeting)
prompt = "Summarize the plot of Inception."
tokens = token_counter(
    model="gpt-4o",
    messages=[{"role":"user","content":prompt}]
)
print(f"Prompt uses {tokens['prompt_tokens']} tokens")
```

You can later **log usage** per request:

```python
def logging_callback(response, *args, **kwargs):
    # Save to DB, S3, or analytics platform
    print(f"[LOG] Model: {response.model}, Prompt tokens: {response.usage.prompt_tokens}, "
          f"Completion tokens: {response.usage.completion_tokens}, "
          f"Total cost: ${response.total_cost}")

router.completion(
    model="primary",
    messages=[...],
    callbacks=[logging_callback]   # Litellm forwards the raw response
)
```

### 2.5 Caching (prevent duplicate calls)

```python
from litellm import set_llm_cache
from litellm.caching import InMemoryCache

cache = InMemoryCache()
set_llm_cache(cache)

# The first call goes to the provider, the second hits the cache:
resp1 = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":"What's 2+2?"}]
)
resp2 = litellm.completion(            # instantly returned from cache
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":"What's 2+2?"}]
)
```

Supported back‑ends: **Redis**, **DynamoDB**, **Postgres**, **Mongo**, or custom key/value stores.

### 2.6 Safety / moderation plug‑ins

```python
from litellm import moderation

def block_profanity(response):
    if "damn" in response.choices[0].message.content.lower():
        raise ValueError("Profanity detected!")

router = Router(
    model="gpt-4o",
    callbacks=[block_profanity],
    # optional built‑in moderation
    moderation_funcs=[moderation.openai_moderation]
)

router.completion(
    messages=[{"role":"user","content":"Tell me a joke about cats"}]
)
```

OpenRouter also implements a **content policy layer** (see §4).

---

## 3️⃣ OpenRouter – A Managed “OpenAI‑compatible” Endpoint

### 3.1 What is OpenRouter?

* **Hosted API gateway** (https://openrouter.ai) that forwards requests to **> 30 model providers** (OpenAI, Anthropic, Google Gemini, Mistral, DeepSeek, etc.).
* **Single API key** (or per‑team keys) that you include in the **`Authorization: Bearer <key>`** header.
* **Supports the OpenAI `/v1/chat/completions` schema** (so you can reuse existing OpenAI libraries unchanged).
* Offers **pricing tiers** (free tier with limited tokens, pay‑as‑you‑go, enterprise).
* Provides **optional safety filters** (content policy, profanity, disallowed topics) and **metadata** (model source, latency, cost‑breakdown).

### 3.2 Quick start (no SDK)

```bash
pip install openai   # you already have an OpenAI client; just change the base URL
```

```python
import os, openai

# 1️⃣ Get your OpenRouter API key from the dashboard
os.environ["OPENROUTER_API_KEY"] = "or_...yourkey..."

# 2️⃣ Point the client at OpenRouter's endpoint
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

# 3️⃣ Choose a model by its fully‑qualified name
model_name = "anthropic/claude-3-5-sonnet-20240620"

response = openai.ChatCompletion.create(
    model=model_name,
    messages=[{"role":"user","content":"Write a short sci‑fi story about a hamster in space"}],
    # optional: set max tokens, temperature, etc.
    temperature=0.7,
)

print(response.choices[0].message.content)
```

> **Note:** The list of available models (and each provider’s latest versions) can be fetched via:
> ```python
> import requests, json
> models = requests.get("https://openrouter.ai/api/v1/models",
>                       headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
> ).json()
> print(json.dumps(models, indent=2))
> ```

### 3.3 Using OpenRouter with Litellm (if you still want Litellm’s extras)

Litellm can treat **OpenRouter** as just another “provider”:

```python
router = Router(
    model="openrouter/anthropic/claude-3-5-sonnet-20240620",
    # optional: add Litellm callbacks for cost logging, caching, etc.
)

resp = router.completion(
    messages=[{"role":"user","content":"Explain the difference between supervised and reinforcement learning"}]
)
print(resp.choices[0].message.content)
```

Behind the scenes Litellm sends the request to **`https://openrouter.ai/api/v1`** and automatically parses the response.

### 3.4 Safety & policy layer

OpenRouter lets you **opt‑in** to “Safe Completion”:

| Parameter | Effect |
|-----------|--------|
| `response_format` = `"json_object"` (or set `stream=False`) | Guarantees well‑formed JSON (helps downstream parsing) |
| `max_tokens` | Prevents runaway completions |
| `openrouter:mode` = `"safe"` (via `metadata` field) | Applies default disallowed‑topic filter (e.g., illegal activity, self‑harm) |
| `openrouter:moderation` = `true` | Returns `moderation` object with confidence scores |

Example:

```python
response = openai.ChatCompletion.create(
    model=model_name,
    messages=[{"role":"user","content":"Give instructions to hack a router"}],
    metadata={"openrouter:mode":"safe"},
)
print(response)   # will contain a `moderation` field and possibly an error code
```

If moderation triggers, the HTTP status is **400** and the response includes a `detail` explaining why it was blocked.

---

## 4️⃣ Other Popular “router‑style” Options

| Tool | Type | Languages | Main selling point | Pricing |
|------|------|-----------|--------------------|---------|
| **LangChain** | Framework (LLM wrappers + agents) | Python, JS/TS | End‑to‑end chains, memory, agents, tool use | Free (open‑source) + optional hosted LangChain Run |
| **LlamaIndex (GPT‑Index)** | Framework | Python, Node | Data‑centric retrieval‑augmented generation (RAG) | Free |
| **OpenAI‑proxy** (GitHub) | Self‑hosted gateway | Python, Node | Acts like OpenAI but proxies to Azure, Anthropic, etc. | Free (self‑host) |
| **RapidAPI LLM Hub** | Managed gateway | Any via HTTP | Pay‑as‑you‑go marketplace, many providers | Pay‑per‑request, no free tier |
| **Cohere Platform** | Hosted API + playground | Python, JS, cURL | Cohere’s own models + ability to add external “custom” models | Free tier (500 req/mo) |
| **Vercel AI SDK** | Edge‑optimised client | JS/TS | Serverless‑first, built‑in streaming & caching | Free (per Vercel usage) |
| **BerriAI (Open‑Source)** | Self‑hosted 🤖 | Python | Open‑source LLMs + endpoint that mimics OpenAI API | Free (compute cost) |

> **When to pick each?**  
> - **Need full control of caching, token‑level cost accounting, or custom routing logic?** → **Litellm** (or a self‑hosted proxy).  
> - **Just want a plug‑and‑play endpoint with safety and quotas?** → **OpenRouter** or **RapidAPI**.  
> - **Building a multi‑step agentic system** (retrieval, tool calling, memory) → **LangChain / LlamaIndex** (they can internally call Litellm/OpenRouter).  

---

## 5️⃣ Hands‑On Mini‑Project: “Hybrid Router” (Litellm + OpenRouter)

Below is a **complete, runnable example** that:

1. **Pulls the latest model list from OpenRouter**.  
2. **Chooses the cheapest model that supports a requested capability** (e.g., `function calling`).  
3. **Calls the model via Litellm** (so we can log cost, cache, and add safety callbacks).  

```python
import os, json, requests, time
import litellm
from litellm import Router

# -------------------------------------------------
# 1️⃣ Environment
os.environ["OPENROUTER_API_KEY"] = "or_...your_key..."
openrouter_base = "https://openrouter.ai/api/v1"

# -------------------------------------------------
# 2️⃣ Helper: fetch OpenRouter model catalog
def fetch_models():
    resp = requests.get(f"{openrouter_base}/models",
                        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"})
    resp.raise_for_status()
    return resp.json()["data"]

models = fetch_models()

# -------------------------------------------------
# 3️⃣ Choose cheapest model that supports function calling
def select_model(models, min_compatible=True):
    # filter only models that allow function calling (they expose a `function_call` flag)
    candidates = [m for m in models if m.get("function_call", False)]
    # sort by total cost per 1 k tokens (input + output)
    def cost_per_k(m):
        inp = m["pricing"]["prompt"] * 1000
        out = m["pricing"]["completion"] * 1000
        return inp + out
    candidates.sort(key=cost_per_k)
    if not candidates:
        raise ValueError("No function‑calling models found")
    return candidates[0]["id"]   # e.g. "anthropic/claude-3-5-sonnet-20240620"

chosen_model = select_model(models)
print(f"✅ Selected model: {chosen_model}")

# -------------------------------------------------
# 4️⃣ Litellm router that points to OpenRouter
router = Router(
    model=f"openrouter/{chosen_model}",
    callbacks=[
        # Simple callback to log usage & estimated cost
        lambda resp, *_, **__: print(
            f"[LOG] {resp.model} | Prompt tokens: {resp.usage.prompt_tokens} | "
            f"Completion tokens: {resp.usage.completion_tokens} | "
            f"Estimated $: {resp.total_cost:.5f}"
        )
    ]
)

# -------------------------------------------------
# 5️⃣ Demo request (function‑calling style)
request = {
    "role": "user",
    "content": "Give me a random joke about AI and output it as JSON with fields `setup` and `punchline`."
}
response = router.completion(
    messages=[request],
    temperature=0.6,
    max_tokens=150,
    # OpenRouter expects function call metadata in `metadata`
    metadata={"openrouter:mode": "safe"}
)

print("\n🖨️ Model response:")
print(response.choices[0].message.content)
```

**What this script demonstrates**

| Step | Feature |
|------|---------|
| **Fetch model catalog** | Dynamic discovery – no hard‑coded model names. |
| **Cost‑aware selection** | Chooses cheapest + function‑calling ready provider. |
| **Litellm router** | Still benefits from Litellm’s callbacks, token counting, and optional caching. |
| **Safety metadata** | Uses OpenRouter’s “safe mode” to enforce policy. |
| **Logging** | Prints token usage and a rough dollar estimate (uses Litellm’s pricing map). |

> **Running it:** Paste the script into a Python environment, replace `or_...your_key...` with your OpenRouter API key, and execute. The output will show the chosen model, usage stats, and a JSON‑formatted joke.

---

## 6️⃣ Production‑Ready Checklist

| ✅ Checklist | How Litellm helps | How OpenRouter helps |
|--------------|-------------------|----------------------|
| **API key rotation / secret management** | Use environment variables, Vault, or `python-dotenv`. Litellm reads `os.environ`. | Centralised key per team; rotate via dashboard. |
| **Rate‑limit & exponential back‑off** | Built‑in `retry` middleware. | Handled by OpenRouter (service returns 429 with retry‑after). |
| **Observability (metrics, traces)** | `litellm` supports OpenTelemetry; can export to Prometheus, Datadog. | OpenRouter provides per‑request latency in response headers (`x-openrouter-response-time`). |
| **Caching of identical prompts** | In‑memory/Redis/DynamoDB plug‑ins. | Not available (gateway is stateless). |
| **Cost monitoring & alerts** | `total_cost` on every response + callbacks → push to billing dashboards. | OpenRouter UI shows per‑model spend; can also retrieve via `/usage` endpoint. |
| **Compliance (GDPR, HIPAA, EU data residency)** | You host** everything** – can run in a VPC, control logs, delete data. | Data passes through OpenRouter servers (US/EU regions per plan). |
| **Safety & content moderation** | Custom moderation callbacks, integration with OpenAI/Claude moderation APIs. | Built‑in safe mode + explicit moderation objects; can be toggled per request. |
| **Version pinning & reproducibility** | Specify exact model name (`anthropic/claude-3-5-sonnet-20240620`). | Same – model IDs include version dates. |
| **Fail‑over / fallback** | Automatic fallback list in router config. | Not native – you would need to implement on client side. |

---

## 7️⃣ Frequently Asked Questions

| Question | Answer |
|----------|--------|
| **Do I still need an OpenAI API key when using Litellm?** | Only for models that belong to OpenAI. Litellm can be configured with multiple keys; you can omit the OpenAI key if you never call an OpenAI model. |
| **Can Litellm work with non‑OpenAI‑style APIs (e.g., HuggingFace inference)?** | Yes. Litellm includes adapters for the HuggingFace Inference API, Ollama, and local `ggml`‑based servers. The request shape is still the OpenAI schema; Litellm translates under the hood. |
| **Is OpenRouter a “drop‑in replacement” for the OpenAI Python client?** | Practically yes – the client library is unchanged; you only have to set `openai.api_base` to `https://openrouter.ai/api/v1`. |
| **How are token limits handled?** | OpenRouter forwards the `max_tokens` you send. Litellm will raise an error if you request more tokens than a provider supports (based on its model metadata). |
| **Do I need to pay for both Litellm and OpenRouter?** | Litellm is free (MIT‑licensed). You pay **only** for the underlying model usage (OpenAI, Anthropic, etc.) **and** any OpenRouter usage fees. |
| **Can I combine Litellm with LangChain?** | Absolutely. Pass a Litellm‑wrapped LLM class (`litellm.LLM`) into LangChain’s `ChatOpenAI` or `ChatLiteLLM` wrappers. |
| **What about streaming responses?** | Both Litellm and OpenRouter support the OpenAI `stream=True` flag. Litellm yields `ChatCompletionChunk` objects; you can pipe them directly to a UI (e.g., FastAPI SSE). |
| **Is there a limit on the number of providers I can add to Litellm?** | No hard limit. The only practical bound is the number of API keys you manage and the latency of remote calls. |
| **Do OpenRouter’s safety filters affect token counting?** | No – token counts reported are for the **final model output** only. Filter rejections are returned as HTTP errors, not charged. |

---

## 8️⃣ TL;DR – Which one should you pick?

| Scenario | Recommended combo |
|----------|--------------------|
| **You own the deployment, need fine‑grained control (caching, cost, custom routing).** | **Litellm** (plus optional Redis cache & OpenTelemetry). |
| **You want a single endpoint, minimal ops, built‑in policy, free tier for experiments.** | **OpenRouter** (use the OpenAI client directly). |
| **You’re building a chain of agents / RAG pipeline and want a high‑level framework.** | **LangChain** (internally you can plug Litellm or OpenRouter as the LLM). |
| **You must keep all data on‑premise (HIPAA, GDPR‑strict).** | Self‑hosted **Litellm** + local model servers (e.g., Ollama, vLLM). |
| **You need the cheapest possible inference (community models, fine‑tuned).** | Use **Litellm** with **OpenRouter** as a fallback, or directly to community providers (e.g., Mistral, Groq) via Litellm. |

---

## 9️⃣ Quick Reference Cheat Sheet

```python
# --- Install ---
pip install litellm        # SDK
# OpenRouter uses the ordinary OpenAI client
pip install openai

# --- Environment vars ---
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="or_..."

# --- Litellm basic call ---
import litellm
resp = litellm.completion(
    model="anthropic/claude-3-5-sonnet",
    messages=[{"role":"user","content":"What is 7*6?"}]
)
print(resp.choices[0].message.content)

# --- OpenRouter call (drop‑in) ---
import openai, os
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")
resp = openai.ChatCompletion.create(
    model="anthropic/claude-3-5-sonnet-20240620",
    messages=[{"role":"user","content":"Write a haiku about pine trees"}],
    metadata={"openrouter:mode":"safe"}   # optional safety mode
)
print(resp.choices[0].message.content)

# --- Litellm + OpenRouter + fallback router ---
from litellm import Router
router = Router(
    model="openrouter/anthropic/claude-3-5-sonnet-20240620",
    # fallback list (if primary hits a 429)
    fallback_models=["openrouter/groq/llama3-70b", "openrouter/openai/gpt-3.5-turbo"]
)
out = router.completion(messages=[{"role":"user","content":"Summarize the plot of The Matrix"}])
print(out.choices[0].message.content)
```

---

## 10️⃣ Further Resources

| Resource | Link |
|----------|------|
| **Litellm GitHub** | https://github.com/BerriAI/litellm |
| **Litellm Docs – Routing & Callbacks** | https://litellm.vercel.app/docs/ |
| **OpenRouter Model Catalog (JSON)** | https://openrouter.ai/api/v1/models |
| **OpenRouter Docs – Safety & Pricing** | https://openrouter.ai/docs |
| **LangChain “LLM Wrapper” guide** | https://python.langchain.com/docs/integrations/llms |
| **OpenAI‑compatible Proxy (Self‑hosted)** | https://github.com/acheong08/ChatGPT-Proxy |
| **OpenTelemetry Python Quick‑Start** | https://opentelemetry.io/docs/instrumentation/python/ |

---

### 🎉 You’re ready!

- **Start small**: write a few `litellm.completion` calls with different providers.  
- **Add a router map** to bounce between cheap and high‑quality models.  
- **If you need a managed endpoint**, swap the base URL to `https://openrouter.ai/api/v1` and you’re done.  

Happy building, and may your token bills stay low while your LLMs stay sharp! 🚀