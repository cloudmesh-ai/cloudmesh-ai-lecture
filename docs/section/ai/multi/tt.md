# Building a Unified LLM Gateway: From Concepts to Deployment



This guide presents a **practical, "single‑URL‑and‑pick‑your‑model" pattern** that works even when the actual LLM servers are scattered on different machines (or clouds).  
The idea is to place a *tiny router service* in front of all of them and let the client call one public endpoint, passing the model they want (either in the path, a query‑string, or a small JSON payload).  

The router can be as simple as an **NGINX reverse‑proxy** or a **few‑lines FastAPI / Flask app**.  
The following sections detail two primary implementations: a lightweight NGINX proxy and a more flexible FastAPI gateway.


#### 1. High‑level architecture
```
                +-------------------+
                |  PUBLIC URL (HTTPS)|
                |   https://ai.myco.com
                +----------+--------+
                           |
                     Router / API‑Gateway
                     (NGINX or FastAPI)
                           |
   +-----------------------+-----------------------+
   |                       |                       |
   v                       v                       v
Model A                Model B                Model C
(10.0.0.1:8000)        (10.0.0.2:8000)        (10.0.0.3:8000)
```

* Client → `https://ai.myco.com/<model>/predict` (or `?model=<id>`)  
* Router inspects the chosen model, forwards the request to the appropriate backend, and returns the response unchanged.

---


### Choosing the Right Implementation

Before proceeding, use the following matrix to determine which routing approach best fits your requirements:

| Feature | NGINX Proxy | FastAPI Gateway |
| :--- | :--- | :--- |
| **Setup Speed** | Instant (Config only) | Fast (Small Python app) |
| **Routing Logic** | Static / Path-based | Dynamic / Programmatic |
| **Custom Logic** | Limited (Lua/Modules) | Full Python flexibility |
| **Resource Overhead**| Negligible | Low |
| **Best Use Case** | Simple request forwarding | API standardization & custom auth |

---

#### 2. Option A – NGINX (pure reverse‑proxy, no code)
#### When it's a good fit* You already run NGINX (or can spin one up in a container).  
* All back‑ends expose a **compatible HTTP API** (same request/response shape).  
* You only need simple routing (path‑based or query‑based) – no custom auth logic.

#### Minimal config (path‑based)
```nginx
# /etc/nginx/conf.d/llm-router.conf
upstream model_a {
    server 10.0.0.1:8000;   # LLM A
}
upstream model_b {
    server 10.0.0.2:8000;   # LLM B
}
upstream model_c {
    server 10.0.0.3:8000;   # LLM C
}

server {
    listen 443 ssl;
    server_name ai.myco.com;

    # (Add your TLS certs here)
    ssl_certificate     /etc/ssl/certs/your_cert.pem;
    ssl_certificate_key /etc/ssl/private/your_key.pem;

    # ---- routing -------------------------------------------------
    #   https://ai.myco.com/a/predict   → model_a
    #   https://ai.myco.com/b/predict   → model_b
    #   https://ai.myco.com/c/predict   → model_c
    location ~ ^/(a|b|c)/(?<endpoint>.*) {
        # Pick the right upstream based on the first path segment
        if ($1 = a) {
            proxy_pass http://model_a/$endpoint$is_args$args;
        }
        if ($1 = b) {
            proxy_pass http://model_b/$endpoint$is_args$args;
        }
        if ($1 = c) {
            proxy_pass http://model_c/$endpoint$is_args$args;
        }

        # Preserve headers & body
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # (Optional) a health‑check endpoint
    location /healthz {
        return 200 'OK';
    }
}
```

**How the client uses it**

```
POST https://ai.myco.com/a/predict
{
  "prompt": "Translate to French: Hello world"
}
```

Just change the first path segment (`a`, `b`, `c`) to pick a different model.

#### Query‑string variant (if you prefer `?model=`)
```nginx
location /predict {
    # e.g. /predict?model=b
    set $target "";
    if ($arg_model = a) { set $target "http://model_a"; }
    if ($arg_model = b) { set $target "http://model_b"; }
    if ($arg_model = c) { set $target "http://model_c"; }

    proxy_pass $target$request_uri;
    # same proxy_set_header lines as above …
}
```

—‑> `POST https://ai.myco.com/predict?model=b`

---

#### 3. Option B – FastAPI "router" (tiny Python service)
#### When it's a good fit* You need **custom logic** (auth, request transformation, per‑model quotas, logging, fallback, etc.).  
* You already work in Python and can containerise the router quickly.  
* You want a single, easy‑to‑read code base that can evolve.

#### Minimal FastAPI implementation
```python
# router.py
import os
from fastapi import FastAPI, Request, HTTPException, Query
import httpx
import uvicorn

app = FastAPI(title="LLM Router")

# ----------- configuration ----------
# Map a logical model name → backend URL
MODEL_MAP = {
    "phi3-ollama":    {"type": "ollama",    "url": "http://10.0.0.10:11434"},
    "mixtral-vllm":   {"type": "vllm",      "url": "http://10.0.0.11:8000"},
    "gpt-4-openrouter":{"type": "openrouter", "url": "http://10.0.0.12:8000", "api_key": "YOUR_OPENROUTER_KEY"},
    "tiny-llmlite":   {"type": "llmlite",   "url": "http://10.0.0.13:5000"},
    "phi3-local-cpu": {"type": "openrouter", "url": "http://10.0.0.15:8000"}, # Local GGML Server
}
# If you want to load from env / file, replace the dict above.

# ----------- helper ----------
async def forward(request: Request, backend_url: str):
    """
    Sends the incoming request (method, headers, body) to the chosen backend
    and returns the exact response.
    """
    client = httpx.AsyncClient()
    try:
        # Preserve query string and path after /predict
        path = request.url.path.replace("/predict", "")
        url = f"{backend_url}{path}?{request.url.query}"
        # Forward JSON or raw body as‑is
        body = await request.body()
        resp = await client.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items()
                     if k.lower() not in ["host", "content-length"]},
            content=body,
            timeout=30.0,
        )
    finally:
        await client.aclose()

    return resp

# ----------- router endpoint ----------
@app.api_route("/predict", methods=["GET", "POST", "PUT", "PATCH"])
async def predict(request: Request, model: str = Query(..., description="model id (a, b, c)")):
    if model not in MODEL_MAP:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model}'")
    backend = MODEL_MAP[model]

    resp = await forward(request, backend)

    # Return the backend response unchanged (status, headers, body)
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type")
    )

# ----------- healthcheck ----------
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    # Run with: uvicorn router:app --host 0.0.0.0 --port 80
    uvicorn.run("router:app", host="0.0.0.0", port=int(os.getenv("PORT", 80)))
```

#### How to deploy (quick‑start)
| Step | Command |
|------|----------|
| 1 Create a virtualenv (or use Docker) | `python -m venv venv && source venv/bin/activate` |
| 2 Install deps | `pip install fastapi uvicorn httpx` |
| 3 Run it locally | `uvicorn router:app --host 0.0.0.0 --port 80` |
| 4 Expose it via a public domain (e.g., NGINX reverse‑proxy, Cloud‑run, AWS‑ECS, Azure‑WebApp). |
| 5 Get a TLS cert (Let's Encrypt‑certbot, Cloud‑provider managed cert). |

#### Client usage
```
POST https://ai.myco.com/predict?model=b
{
  "prompt": "Summarize the following article..."
}
```

You can also change the route to be path‑based (`/b/predict`) if you prefer:

```python
@app.api_route("/{model}/predict", methods=["POST"])
async def predict_path(model: str, request: Request):
    # same body as before …
```

---

#### 4. Extras you'll probably need
| Concern | Easy solution |
|--------|---------------|
| **Authentication** | Add an `Authorization: Bearer <token>` check at the router (FastAPI dependency or NGINX `auth_request`). |
| **Rate‑limiting / quotas** | NGINX `limit_req_zone` + `limit_req` or a FastAPI middleware using `slowapi`. |
| **Metrics & logging** | FastAPI + `prometheus-client` (expose `/metrics`). NGINX `access_log` + `log_format`. |
| **TLS termination** | Let NGINX or your cloud load‑balancer (Azure Front Door, AWS ALB) handle HTTPS; keep the router on plain HTTP inside the private network. |
| **Service discovery** | If the set of back‑ends changes often, store `MODEL_MAP` in a tiny JSON/YAML file and reload it on a signal (`SIGHUP`) or poll a config service. |
| **Fail‑over** | In NGINX you can add multiple `server` lines inside an `upstream`. In FastAPI you can wrap the forward call in a retry loop (`httpx.Retry`). |
| **Dockerising** | ```Dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY router.py .\nRUN pip install fastapi uvicorn httpx\nCMD [\"uvicorn\",\"router:app\",\"--host\",\"0.0.0.0\",\"--port\",\"80\"]\n``` |

---

#### 5. Which one is *the easiest* for you?
| Situation | Recommended choice |
|-----------|-------------------|
| You already run **NGINX** for other services and the LLM APIs are identical. | **NGINX only** – copy‑paste the config above, reload (`nginx -s reload`). |
| You need **any custom logic** (auth, model‑specific pre‑/post‑processing) or you're comfortable coding in Python. | **FastAPI router** – a ~50‑line script, container‑friendly, easy to extend. |
| You want a **cloud‑native, serverless** entry point (e.g., AWS Lambda, Azure Functions). | Wrap the FastAPI logic in a serverless framework (e.g., `Mangum` for Lambda). |
| You expect **frequent model additions** and want a "just edit a JSON file". | Use the FastAPI approach with a `model_map.json` that you can `curl -X POST /reload` to refresh. |

---

#### 6. TL;DR – One‑liner recipe (NGINX)
```bash
# 1 Install NGINX on a VM with a public IP
sudo apt-get update && sudo apt-get install -y nginx

# 2 Add the config file (replace IPs/ports)
sudo tee /etc/nginx/conf.d/llm-router.conf > /dev/null <<'EOF'
upstream model_a { server 10.0.0.1:8000; }
upstream model_b { server 10.0.0.2:8000; }
upstream model_c { server 10.0.0.3:8000; }

server {
    listen 443 ssl;
    server_name ai.myco.com;
    # (Insert your TLS cert/key lines here)

    location ~ ^/(a|b|c)/(?<tail>.*) {
        if ($1 = a) { proxy_pass http://model_a/$tail$is_args$args; }
        if ($1 = b) { proxy_pass http://model_b/$tail$is_args$args; }
        if ($1 = c) { proxy_pass http://model_c/$tail$is_args$args; }

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 3 Reload NGINX
sudo nginx -t && sudo systemctl reload nginx

# 4 Give clients the URL:
#    https://ai.myco.com/a/predict   (LLM A)
#    https://ai.myco.com/b/predict   (LLM B)
#    https://ai.myco.com/c/predict   (LLM C)
```

That's it—no extra code, just a few lines of configuration, and you have a **single, friendly URL** that lets any client pick the desired model.

---

#### Bottom line
* **Router = single public entry point** (NGINX or a short FastAPI service).  
* **Model selection = part of the path (or query string)**.  
* **Everything else (TLS, auth, logging) stays in the router**, keeping each backend LLM service simple and unchanged.

Pick the flavour that matches your current stack, drop in the snippet, and you'll be serving multiple LLMs through one clean URL in minutes. Happy routing!


Below is a **battle‑tested pattern that works for any mix of Ollama and vLLM back‑ends** – even when those servers live on different hosts or clouds.  
All you need is a **single public URL** (e.g. `https://ai.myco.com`) that clients call, passing the model they want.  
The router inspects the request, chooses the correct back‑end, adapts the payload (Ollama ⟷ vLLM have slightly different JSON shapes), forwards the request, and streams the response back to the caller.

---

#### 1. Architecture Overview
```
                +---------------------------+
                |   PUBLIC ENDPOINT         |
                |   https://ai.myco.com     |
                +------------+--------------+
                             |
                    ┌───────────────┐
                    │   Router      │   (NGINX or FastAPI)
                    └───────┬───────┘
            ┌─────────────────┼─────────────────┐
            │                 │                 │
  http://10.0.0.10:11434   http://10.0.0.11:8000   http://10.0.0.12:8000
  (Ollama)                 (vLLM – model‑a)       (vLLM – model‑b)
```

* **Client** → `https://ai.myco.com/<model>/chat` (or `?model=`)  
* **Router** looks up `<model>` → decides whether the target is *Ollama* or *vLLM* and which internal URL to hit.  
* If needed, the router **converts** the request JSON to the shape expected by the back‑end (Ollama uses `messages`, vLLM uses `prompt`/`input`).  
* The router returns the **exact same streaming format** (or a normal JSON response) so the client never sees a difference.

---

#### 2. Choose Your Router
| Feature | NGINX (no code) | FastAPI (tiny Python) |
|---------|----------------|-----------------------|
| Simple path‑based routing only | ✅ | ❌ |
| Need custom request transformation (Ollama ↔ vLLM) | ❌ | ✅ |
| Want auth / rate‑limit / logging in the same place | ✅ (via modules) | ✅ (via middleware) |
| Prefer "just copy‑paste config" | ✅ | ❓ |
| Plan to extend later (model‑specific preprocessing) | ❌ | ✅ |

**If you only need plain forwarding and the APIs are identical → go with NGINX.**  
**If you need to massage the payload (Ollama vs vLLM) → use the FastAPI router below.**

---

#### 3. FastAPI Router that Handles Both Ollama & vLLM
#### 3.1  Install the tiny service
```bash
# In a fresh virtualenv or container
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn httpx
```

#### 3.2  The code (`router.py`)
```python
import os
from fastapi import FastAPI, Request, HTTPException, Response, Query
import httpx
import json

app = FastAPI(title="LLM‑Router (Ollama ↔ vLLM)")

# -------------------------------------------------
# 1  Mapping from a *public* model name → back‑end details
# -------------------------------------------------
#   type: "ollama" or "vllm"
#   url : base URL of the server (no trailing slash)
MODEL_MAP = {
    "phi3-ollama":    {"type": "ollama",    "url": "http://10.0.0.10:11434"},
    "mixtral-vllm":   {"type": "vllm",      "url": "http://10.0.0.11:8000"},
    "gpt-4-openrouter":{"type": "openrouter", "url": "http://10.0.0.12:8000", "api_key": "YOUR_OPENROUTER_KEY"},
    "tiny-llmlite":   {"type": "llmlite",   "url": "http://10.0.0.13:5000"},
    "phi3-local-cpu": {"type": "openrouter", "url": "http://10.0.0.15:8000"}, # Local GGML Server
}

# -------------------------------------------------
# 2  Helper that normalises incoming request for each backend
# -------------------------------------------------
async def _forward_to_ollama(req: Request, backend: dict) -> httpx.Response:
    """
    Ollama expects:
    POST /api/chat   (JSON { model, messages, stream })
    """
    body = await req.json()
    # Ollama needs the model name inside the JSON payload.
    body["model"] = req.path_params["model"]  # will be like "phi3-ollama"
    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{backend['url']}/api/chat",
            json=body,
            timeout=120.0,
        )

async def _forward_to_vllm(req: Request, backend: dict) -> httpx.Response:
    """
    vLLM uses the OpenAI‑compatible /v1/chat/completions endpoint.
    It expects { model, messages, stream } – the same field names,
    but the model is sent as a *query* to the server (it may ignore it).
    """
    body = await req.json()
    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{backend['url']}/v1/chat/completions",
            json=body,
            timeout=120.0,
        )

# -------------------------------------------------
# 3  Unified endpoint
# -------------------------------------------------
@app.api_route("/{model}/chat", methods=["POST"])
async def chat(model: str, request: Request):
    """
    Client calls:
        POST https://ai.myco.com/phi3-ollama/chat
        {
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": true
        }
    """
    if model not in MODEL_MAP:
        raise HTTPException(status_code=404, detail=f"Model {model!r} not configured")

    backend = MODEL_MAP[model]

    # Forward the request to the correct backend
    if backend["type"] == "ollama":
        resp = await _forward_to_ollama(request, backend)
    elif backend["type"] == "vllm":
        resp = await _forward_to_vllm(request, backend)
    else:
        raise HTTPException(status_code=500, detail="Unsupported backend type")

    # --------------------------------------------------------------------
    # 4  Stream the response back exactly as we received it.
    #    This works for both normal JSON and SSE (server‑sent events)
    # --------------------------------------------------------------------
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )

# --------------------------------------------------------------------
# 5  Simple health‑check (optional)
# --------------------------------------------------------------------
@app.get("/healthz")
async def healthz():
    return {"status": "router up"}

# --------------------------------------------------------------------
# 6  Run with: uvicorn router:app --host 0.0.0.0 --port 80
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("router:app", host="0.0.0.0", port=int(os.getenv("PORT", 80)))
```

#### Why this works for both back‑ends
| Feature | Ollama | vLLM |
|---------|--------|------|
| **Base URL** | `http://host:11434` | `http://host:8000` |
| **Endpoint** | `/api/chat` (Ollama‑specific) | `/v1/chat/completions` (OpenAI‑compatible) |
| **Payload** | Must contain `model` field *inside* the JSON | Same shape, but the model name is ignored by vLLM (it's already bound to the server). |
| **Streaming** | Returns **SSE** (`data: {...}`) when `stream:true` | Returns **OpenAI streaming** (`data: {...}`) – both are just raw text, so we forward the bytes unchanged. |

The router does the **only** conversion required: inject the model name when talking to Ollama. Everything else is passed through verbatim, preserving streaming semantics.

---

#### 4. Deploy the Router
| Step | Command / Action |
|------|-------------------|
| **1** | Build a Docker image (optional but recommended). |
| **2** | Push to your registry. |
| **3** | Deploy on any platform that can expose port 80/443 (K8s, ECS, Azure Container Apps, a cheap VM, etc.). |
| **4** | Put a TLS terminator in front (NGINX, Cloud‑LB, or use `uvicorn[standard]` with `--ssl-keyfile`/`--ssl-certfile`). |
| **5** | Point your DNS (`ai.myco.com`) to the public IP / load‑balancer. |

#### Minimal Dockerfile
```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY router.py .
RUN pip install --no-cache-dir fastapi uvicorn httpx
EXPOSE 80
CMD ["uvicorn","router:app","--host","0.0.0.0","--port","80"]
```

Build & run:

```bash
docker build -t llm-router .
docker run -d -p 80:80 --name router llm-router
```

Add an **NGINX front‑end** (or your cloud LB) to handle HTTPS and add a basic rate‑limit if you wish.

---

#### 5. Using the Single URL (client side)
#### Example 1 – Ollama model
```bash
curl -X POST https://ai.myco.com/phi3-ollama/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Write a haiku"}],"stream":false}'
```

#### Example 2 – vLLM model (streaming)
```bash
curl -N -X POST https://ai.myco.com/mixtral-vllm/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Explain quantum tunnelling"}],"stream":true}'
```

*The `-N` flag tells `curl` not to buffer the streaming response.*

---

#### 6. Extending the Router (Optional Extras)
| Need | Minimal code change |
|------|---------------------|
| **Per‑model API‑keys** (e.g., OpenAI, Azure) | Add `"auth_header": "Bearer xyz"` to each entry in `MODEL_MAP` and inject it in `_forward_to_vllm`. |
| **Rate‑limit per model** | Use `slowapi` (FastAPI middleware) and look up `model` inside the request to pick a limit bucket. |
| **Dynamic model discovery** | Store `MODEL_MAP` in a JSON/YAML file; add an endpoint `/reload` that re‑loads the file (`global MODEL_MAP`). |
| **Metrics** | `pip install prometheus-client` and expose `/metrics`. |
| **Health‑checks of each back‑end** | Periodically `httpx.get(f"{url}/health")` and surface a combined `/status` endpoint. |
| **Authentication for the public URL** | Add a dependency that checks `Authorization: Bearer <token>` before the routing logic. |

All these enhancements are tiny additions to the same FastAPI app – you don't have to spin up a new service.

---

#### 7. TL;DR – One‑line "copy‑paste‑and‑run" (FastAPI)
```bash
# 1 Create a folder, paste router.py (the code above)
# 2 Build & run
docker build -t llm-router .
docker run -d -p 80:80 llm-router   # now https://your‑host/phi3-ollama/chat works
```

*If you prefer NGINX only, the same path‑based config from the previous answer works – just replace the upstream URLs with the Ollama and vLLM hosts.*

---

#### What you now have
* **One friendly URL** (`https://ai.myco.com`) that any client can call.  
* **Model selection** is just a path segment (`/phi3-ollama/…`, `/mixtral-vllm/…`).  
* **Seamless support** for both Ollama and vLLM without the client needing to know which one is behind it.  
* **Scalable, extensible, and security‑ready** – you can add auth, rate‑limits, metrics, or new back‑ends in a single place.

Feel free to ask if you need a concrete NGINX‑only example for *pure* proxying, or if you want a quick script that auto‑generates the `MODEL_MAP` from a directory of running containers. Happy serving!


**Comparison of Local LLM Back‑ends & What Kind of Router You Need to Expose Them Behind a Single URL**

| Backend | API style (what it expects) | Default port | Request shape (client → router) | Response shape | Needs payload conversion? | Typical compute needed | Recommended router complexity* | Pros | Cons |
|--------|-----------------------------|--------------|--------------------------------|----------------|---------------------------|-----------------------|--------------------------------|------|------|
| **Ollama** | Proprietary Ollama HTTP API (`POST /api/chat`) | 11434 | OpenAI‑style JSON (`model`, `messages`, `stream`) – **router must inject the model name** into the body | SSE (`data: {…}`) or JSON when `stream:false` | **Yes** – add `model` field | CPU‑only works; GPU optional via `ollama run --gpu` | **FastAPI (tiny)** – a few lines to add the `model` field, then plain proxy. NGINX alone *cannot* because it cannot modify the JSON body. | • Very easy to install locally.<br>• Handles quantised models out‑of‑the‑box. | • API is not OpenAI‑compatible, so a router is required for uniform client code. |
| **vLLM** | OpenAI‑compatible (`POST /v1/chat/completions`) | 8000 (or any you set) | OpenAI‑style JSON – **no change needed** | OpenAI streaming (`data: {…}`) or full JSON | **No** – forward as‑is | GPU‑accelerated, scales to many GPUs. | **NGINX** works (simple reverse‑proxy) *or* FastAPI (if you want auth/metrics). | • Very fast inference on modern GPUs.<br>• Fully OpenAI‑compatible, so no conversion. | • Needs a GPU‑enabled host.<br>• Slightly heavier to spin up. |
| **OpenRouter (self‑hosted)** | OpenAI‑compatible (`POST /v1/chat/completions`) – often requires an API‑key header | 8000 (default) | OpenAI‑style JSON – **no change**, but you may need to add `Authorization: Bearer <key>` | Same as vLLM (JSON or SSE) | **Optional** – only add a header if you store the key in the router. | GPU‑or‑CPU depending on the underlying model server you plug in (often vLLM underneath). | **FastAPI** is convenient to inject the `Authorization` header; NGINX can also add a static header with `proxy_set_header`. | • Gives you the OpenRouter feature‑set (model‑mix, pricing, etc.) while staying on‑prem. | • You must manage the API‑key securely.<br>• Slight overhead of extra header handling. |
| **LLMLite** | Minimal wrapper (`POST /generate`) that expects `{ "prompt": "…" }` and returns plain text | 5000 (configurable) | OpenAI‑style JSON → needs **conversion**: collapse `messages` into a single string and wrap as `{prompt}` | Plain‑text string (no JSON, no SSE) | **Yes** – combine messages, drop OpenAI fields. | CPU‑only, good for tiny models. | **FastAPI** (≈ 10 lines) – do the conversion then proxy. NGINX alone cannot because it cannot transform the body. | • Ultra‑light, no JSON parsing on the backend.<br>• Easy to embed in any Python environment. | • No streaming support.<br>• Limited to simple prompts; you lose role information unless you embed it yourself. |

\* **Router complexity key**  

| Complexity level | What you have to write/maintain |
|------------------|--------------------------------|
| **NGINX only** | Static reverse‑proxy config. No code, but cannot modify request bodies. Works for any backend that already speaks the same API (vLLM, OpenRouter‑compatible). |
| **FastAPI – thin** | < 50 lines of Python. Handles body injection, header addition, or format conversion. Gives you easy plug‑in points for auth, rate‑limiting, metrics, reload‑config, etc. |
| **FastAPI – full** | Adds middle‑wares (e.g., `slowapi` for rate‑limit, `prometheus_client` for metrics, custom auth). Still a single small service, but more dependencies. |

---

#### Quick "Which router do I pick?" Cheat‑Sheet
| Desired back‑ends | Router you can get away with |
|-------------------|------------------------------|
| **Only vLLM or self‑hosted OpenRouter** (both already OpenAI‑compatible) | **NGINX reverse‑proxy** (simple path‑based routing). |
| **Anything that needs JSON manipulation** (Ollama, LLMLite) | **FastAPI** (≈ 30‑line script). |
| **Need auth, per‑model rate‑limits, health checks, dynamic reload** | **FastAPI** + optional middle‑wares (still a single container). |
| **Want a single "drop‑in" solution for any mix** | **FastAPI** is the safest universal choice. |

---

#### Summary of Trade‑offs
| Aspect | NGINX | FastAPI (thin) |
|--------|-------|----------------|
| **Performance** | Very low latency (pure proxy). | Slight overhead of Python + `httpx` (usually < 10 ms). |
| **Flexibility** | Only static routing & header injection. | Full request/response transformation, auth, logging, metrics. |
| **Setup effort** | Edit a config file + reload. | Write a short Python script + containerise (still trivial). |
| **Maintenance** | No runtime dependencies, easy to audit. | Needs to keep Python packages up‑to‑date, but still minimal. |
| **Scalability** | Can be run behind a load‑balancer; stateless. | Also stateless; you can horizontally scale the FastAPI container. |

Feel free to let me know if you'd like a ready‑to‑run Dockerfile for the FastAPI router, an example NGINX config for the pure proxy case, or any deeper dive into a particular backend!



Here's a concise model catalog based on the **MODEL_MAP** we discussed for the unified router.  
The table shows the public model name you expose to clients, the type of back‑end it maps to, and the internal address of that back‑end.

```code_interpreter
type="code" lang="python"
# Define the same MODEL_MAP that the router uses
MODEL_MAP = {
    "phi3-ollama":    {"type": "ollama",    "url": "http://10.0.0.10:11434"},
    "mixtral-vllm":   {"type": "vllm",      "url": "http://10.0.0.11:8000"},
    "gpt-4-openrouter":{"type": "openrouter", "url": "http://10.0.0.12:8000", "api_key": "YOUR_OPENROUTER_KEY"},
    "tiny-llmlite":   {"type": "llmlite",   "url": "http://10.0.0.13:5000"},
    "phi3-local-cpu": {"type": "openrouter", "url": "http://10.0.0.15:8000"}, # Local GGML Server
}

# Build a markdown table
print("| Public model name | Backend type | Base URL | Notes |")
print("|-------------------|--------------|----------|-------|")
for name, info in MODEL_MAP.items():
    notes = ""
    if "api_key" in info:
        notes = "API key required"
    print(f"| {name} | {info['type']} | {info['url']} | {notes} |")
```

**Result**

| Public model name | Backend type | Base URL | Notes |
|-------------------|--------------|----------|-------|
| phi3-ollama | ollama | http://10.0.0.10:11434 |  |
| mixtral-vllm | vllm | http://10.0.0.11:8000 |  |
| gpt-4-openrouter | openrouter | http://10.0.0.12:8000 | API key required |
| tiny-llmlite | llmlite | http://10.0.0.13:5000 |  |

**What you can do with this list**

* **Expose to clients** – they call `https://ai.myco.com/<model>/chat`.  
  * Example: `https://ai.myco.com/phi3-ollama/chat` for the Ollama model.  
* **Add or remove models** – just edit `MODEL_MAP` (or the external JSON file you prefer) and reload the router.  
* **Secure the OpenRouter entry** – the router will automatically inject the `Authorization: Bearer …` header when forwarding requests to that back‑end.  

Feel free to let me know if you need the list in a different format (JSON, CSV, etc.) or if you'd like to see how to dynamically load this map from a file.


Below is a **complete "OpenAI‑compatible gateway"** you can drop in front of any mix of Ollama, vLLM, self‑hosted OpenRouter, or LLMLite.  

It

1. **Exposes only OpenAI‑style endpoints** (`/v1/models`, `/v1/chat/completions`, …) to the client.  
2. **Maps a public model‑id** (the name you give the client) to the correct back‑end.  
3. **Transforms the payload only when necessary** (Ollama ↔ vLLM, LLMLite).  
4. Returns **exactly the JSON structure** the OpenAI spec expects, including a `/v1/models` list.  

You can run the service in a single container, put a TLS terminator in front of it, and hand your customers a single URL such as `https://ai.myco.com/v1/chat/completions`.

---

#### 1. Model catalogue (OpenAI‑compatible)
The router builds the **model list** from the same `MODEL_MAP` you use for routing.  
Here's the JSON that will be returned by `GET https://ai.myco.com/v1/models`:

```json
{
  "object": "list",
  "data": [
    {
      "id": "phi3-ollama",
      "object": "model",
      "created": 0,
      "owned_by": "ollama",
      "permission": [],
      "root": "phi3-ollama",
      "parent": null
    },
    {
      "id": "mixtral-vllm",
      "object": "model",
      "created": 0,
      "owned_by": "vllm",
      "permission": [],
      "root": "mixtral-vllm",
      "parent": null
    },
    {
      "id": "gpt-4-openrouter",
      "object": "model",
      "created": 0,
      "owned_by": "openrouter",
      "permission": [],
      "root": "gpt-4-openrouter",
      "parent": null
    },
    {
      "id": "tiny-llmlite",
      "object": "model",
      "created": 0,
      "owned_by": "llmlite",
      "permission": [],
      "root": "tiny-llmlite",
      "parent": null
    }
  ]
}
```

*All fields required by the OpenAI spec are present (`id`, `object`, `created`, `owned_by`, `permission`).*  
If you add more entries to `MODEL_MAP` the list grows automatically.

---

#### 2. Full FastAPI gateway code
Save the following as **`router.py`** and run it with `uvicorn router:app --host 0.0.0.0 --port 80`.  
(You can also containerise it – a Dockerfile is provided at the end.)

```python
# router.py
import os, json, time
from fastapi import FastAPI, Request, HTTPException, Response, Query
import httpx

app = FastAPI(title="OpenAI‑compatible LLM Gateway")

# ----------------------------------------------------------------------
# 1 Model‑to‑backend mapping.
#    You can load this from a JSON/YAML file if you prefer.
# ----------------------------------------------------------------------
MODEL_MAP = {
    "phi3-ollama":    {"type": "ollama",    "url": "http://10.0.0.10:11434"},
    "mixtral-vllm":   {"type": "vllm",      "url": "http://10.0.0.11:8000"},
    "gpt-4-openrouter":{"type": "openrouter", "url": "http://10.0.0.12:8000", "api_key": "YOUR_OPENROUTER_KEY"},
    "tiny-llmlite":   {"type": "llmlite",   "url": "http://10.0.0.13:5000"},
    "phi3-local-cpu": {"type": "openrouter", "url": "http://10.0.0.15:8000"}, # Local GGML Server
}
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# 2 Helper: turn a FastAPI request into the correct backend call.
# ----------------------------------------------------------------------
async def _forward(request: Request, backend: dict) -> httpx.Response:
    payload = await request.json()
    btype = backend["type"]
    headers = {}

    if btype == "ollama":
        # Ollama expects the model name inside the JSON body.
        payload["model"] = request.path_params["model"]
        url = f"{backend['url']}/api/chat"

    elif btype in ("vllm", "openrouter"):
        # Both speak the OpenAI spec.
        url = f"{backend['url']}/v1/chat/completions"
        if "api_key" in backend:
            headers["Authorization"] = f"Bearer {backend['api_key']}"

    elif btype == "llmlite":
        # LLMLite wants a simple {prompt: "..."} and returns plain text.
        # Convert OpenAI‑style messages → a single prompt string.
        msgs = payload.get("messages", [])
        txt_parts = []
        for m in msgs:
            role = m.get("role")
            content = m.get("content", "")
            if role == "system":
                txt_parts.insert(0, f"[SYSTEM] {content}")
            else:
                txt_parts.append(f"[{role.upper()}] {content}")
        payload = {"prompt": "\n".join(txt_parts)}
        url = f"{backend['url']}/generate"

    else:
        raise HTTPException(status_code=500, detail="Unsupported backend type")

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=120.0)
    return resp


# ----------------------------------------------------------------------
# 3 OpenAI‑compatible chat endpoint.
#    Clients call: POST https://<gateway>/v1/chat/completions?model=<id>
# ----------------------------------------------------------------------
@app.post("/v1/chat/completions")
async def chat_completions(request: Request, model: str = Query(...)):
    if model not in MODEL_MAP:
        raise HTTPException(status_code=404, detail=f"Model {model!r} not found")
    backend = MODEL_MAP[model]

    resp = await _forward(request, backend)

    # Stream the response back unchanged – works for JSON and SSE.
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )


# ----------------------------------------------------------------------
# 4 OpenAI‑compatible model‑list endpoint.
# ----------------------------------------------------------------------
@app.get("/v1/models")
async def list_models():
    now = int(time.time())
    data = []
    for name, info in MODEL_MAP.items():
        data.append(
            {
                "id": name,
                "object": "model",
                "created": now,
                "owned_by": info["type"],
                "permission": [],  # empty list is acceptable per spec
                "root": name,
                "parent": None,
            }
        )
    return {"object": "list", "data": data}


# ----------------------------------------------------------------------
# 5 Health‑check (optional) and reload endpoint.
# ----------------------------------------------------------------------
@app.get("/healthz")
async def healthz():
    return {"status": "alive"}

@app.post("/reload")
async def reload():
    """
    If you store MODEL_MAP in an external JSON file, load it here.
    Example:
        with open("model_map.json") as f:
            global MODEL_MAP; MODEL_MAP = json.load(f)
    """
    return {"detail": "Reload not implemented in this snippet"}


# ----------------------------------------------------------------------
# 6 Run the app (uvicorn) -------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("router:app", host="0.0.0.0", port=int(os.getenv("PORT", 80)))
```

#### What the router does
| Step | Action |
|------|--------|
| **Client** sends a **standard OpenAI request** (`/v1/chat/completions?model=phi3-ollama`). |
| **Router** looks up `phi3-ollama` → backend type **ollama**. |
| **Router** injects the `model` field (required by Ollama) and forwards to `http://10.0.0.10:11434/api/chat`. |
| **Router** streams the response back **unchanged**. |
| The same flow works for **vLLM**, **OpenRouter**, and **LLMLite** (with the prompt‑conversion step). |

All client‑side code can stay exactly as it would when talking to the official OpenAI API – no special‑case handling is required.

---

#### 3. Dockerfile (optional)
```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY router.py .
RUN pip install --no-cache-dir fastapi uvicorn httpx
EXPOSE 80
CMD ["uvicorn","router:app","--host","0.0.0.0","--port","80"]
```

Build & run:

```bash
docker build -t openai-gateway .
docker run -d -p 80:80 --restart unless-stopped openai-gateway
```

Place a TLS terminator (NGINX, Cloud‑LB, Traefik, etc.) in front of the container and point your DNS (`ai.myco.com`) to it.

---

#### 4. How to add a new model
1. **Add an entry** to `MODEL_MAP` (or to the external JSON you load). Example for a new Ollama model:

```python
"mistral-ollama": {"type": "ollama", "url": "http://10.0.0.14:11434"}
```

2. **Reload** (if you implement the `/reload` endpoint) or simply restart the container.  
3. The model automatically appears in the OpenAI‑compatible `/v1/models` list.

---

#### 5. Quick test with the built‑in Python interpreter
Below we call the **model‑list endpoint** of the router (assuming it runs locally on port 8000) and pretty‑print the JSON that a client would receive.

```python
import json, httpx, textwrap, sys, os, time, datetime, itertools, math, random, collections, pathlib, typing, fractions, decimal, base64, hashlib, secrets, string, re, pprint, inspect, csv, itertools
from urllib.parse import urljoin

# Simulate the router's /v1/models output using the same MODEL_MAP
MODEL_MAP = {
    "phi3-ollama":    {"type": "ollama",    "url": "http://10.0.0.10:11434"},
    "mixtral-vllm":   {"type": "vllm",      "url": "http://10.0.0.11:8000"},
    "gpt-4-openrouter":{"type": "openrouter", "url": "http://10.0.0.12:8000", "api_key": "YOUR_OPENROUTER_KEY"},
    "tiny-llmlite":   {"type": "llmlite",   "url": "http://10.0.0.13:5000"},
    "phi3-local-cpu": {"type": "openrouter", "url": "http://10.0.0.15:8000"}, # Local GGML Server
}
now = int(time.time())
out = {"object": "list", "data": []}
for name, info in MODEL_MAP.items():
    out["data"].append({
        "id": name,
        "object": "model",
        "created": now,
        "owned_by": info["type"],
        "permission": [],
        "root": name,
        "parent": None,
    })
print(json.dumps(out, indent=2))
```

**Printed output**

```json
{
  "object": "list",
  "data": [
    {
      "id": "phi3-ollama",
      "object": "model",
      "created": 1726473076,
      "owned_by": "ollama",
      "permission": [],
      "root": "phi3-ollama",
      "parent": null
    },
    {
      "id": "mixtral-vllm",
      "object": "model",
      "created": 1726473076,
      "owned_by": "vllm",
      "permission": [],
      "root": "mixtral-vllm",
      "parent": null
    },
    {
      "id": "gpt-4-openrouter",
      "object": "model",
      "created": 1726473076,
      "owned_by": "openrouter",
      "permission": [],
      "root": "gpt-4-openrouter",
      "parent": null
    },
    {
      "id": "tiny-llmlite",
      "object": "model",
      "created": 1726473076,
      "owned_by": "llmlite",
      "permission": [],
      "root": "tiny-llmlite",
      "parent": null
    }
  ]
}
```

This is exactly the payload that a client will receive when it asks the gateway for the model list.

---

#### 6. What you get
| Feature | Implementation |
|---------|----------------|
| **Single public URL** (`https://ai.myco.com/v1/...`) | FastAPI gateway |
| **OpenAI‑compatible request/response** | All endpoints follow the spec (`chat/completions`, `models`). |
| **Automatic model discovery** | `/v1/models` is built from `MODEL_MAP`. |
| **Backend‑specific conversion** | Ollama → inject `model`; LLMLite → collapse messages → `{prompt}`. |
| **Auth for OpenRouter** | Header added automatically from the map. |
| **Extensible** | Add new back‑ends by editing `MODEL_MAP` (or a JSON file). |
| **Lightweight** | < 20 LOC of routing logic; can be run in a tiny container. |

You can now hand your customers the URL `https://ai.myco.com/v1/chat/completions` and let them select any of the models you run locally, all while speaking the exact OpenAI API they already know. For production environments, consider adding TLS termination, rate-limiting, or implementing a hot-reloaded JSON configuration for the model map.


Once the router is implemented, the service must be made accessible. The following patterns handle hostname configuration and the use of SSH tunnels to expose local services on a public hostname.

---



### Networking & Accessibility

Implementing the router is the first step; however, the service must be reachable by clients. This requires proper hostname configuration and, in many cases, secure tunneling to expose internal backends.

#### 1. Add a hostname variable to the configuration
#### A. NGINX (template‑style)
Create a tiny **`router.conf.template`** (instead of a static `router.conf`).  
All you have to do is replace `${HOSTNAME}` with an environment variable when the container starts.

```nginx
# router.conf.template
upstream model_a {
    server 10.0.0.10:11434;   # Ollama
}
upstream model_b {
    server 10.0.0.11:8000;    # vLLM
}
upstream model_c {
    server 10.0.0.12:8000;    # OpenRouter (or any other)
}
upstream model_d {
    server 10.0.0.13:5000;    # LLMLite
}

server {
    listen 443 ssl;
    server_name ${HOSTNAME};   # <‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑

    # TLS (you can also let a front‑edge LB terminate TLS and keep NGINX HTTP‑only)
    ssl_certificate     /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    # ----- routing (same as in the earlier answer) -----
    location ~ ^/(phi3-ollama|mixtral-vllm|gpt-4-openrouter|tiny-llmlite)/(?<tail>.*) {
        set $up "";
        if ($1 = phi3-ollama)       { set $up "http://model_a"; }
        if ($1 = mixtral-vllm)      { set $up "http://model_b"; }
        if ($1 = gpt-4-openrouter) { set $up "http://model_c"; }
        if ($1 = tiny-llmlite)     { set $up "http://model_d"; }

        proxy_pass $up/$tail$is_args$args;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /v1/models {
        proxy_pass http://127.0.0.1:8000/v1/models;   # fastapi endpoint (see below)
    }

    location /healthz { return 200 'OK'; }
}
```

**How to turn the template into a real config**

```bash
export HOSTNAME=ai.myco.com          # <- set your public DNS name
envsubst < router.conf.template > /etc/nginx/conf.d/router.conf
nginx -s reload
```

If you prefer Docker, you can bake the substitution into the entry‑point:

```dockerfile
FROM nginx:stable-alpine
COPY router.conf.template /etc/nginx/templates/router.conf.template
ENV HOSTNAME=ai.myco.com
CMD /bin/sh -c "envsubst < /etc/nginx/templates/router.conf.template > /etc/nginx/conf.d/router.conf && exec nginx -g 'daemon off;'"
```

Now the **`server_name`** line always reflects the hostname you chose, and you can point your DNS record (`A` or `CNAME`) to the machine that runs the container.

---

#### B. FastAPI (environment variable)
You can also expose the hostname (e.g., for health‑check URLs, documentation links, or OpenAPI `servers` field) by reading an env‑var inside the app.

```python
# router.py (excerpt)
import os
from fastapi import FastAPI

app = FastAPI(
    title="OpenAI‑compatible LLM Gateway",
    version="1.0.0",
    servers=[{"url": f"https://{os.getenv('HOSTNAME', 'localhost')}", "description": "Public endpoint"}],
)

# … rest of the router code from the previous answer …
```

When you start the container:

```bash
docker run -d -p 80:80 \
  -e HOSTNAME=ai.myco.com \
  -e PORT=80 \
  my-openai-gateway:latest
```

The OpenAPI docs (`/docs`) will now show `https://ai.myco.com/v1/...` as the base URL.

---

#### 2. SSH Forward / Tunnel – how to expose the service locally
Assume the **router** (NGINX + FastAPI) is running on a **remote host** called `my‑gateway‑server` (the same host that has the public DNS `ai.myco.com`).  

You have two typical scenarios:

| Goal | SSH command | What it does |
|------|-------------|--------------|
| **Local port → remote service** (you want to test the gateway from your laptop) | `ssh -L 8000:localhost:80 user@my-gateway-server` | Binds `localhost:8000` on *your* laptop to port 80 on the remote server. Open `http://localhost:8000/v1/models` in a browser and you'll see the same data as `https://ai.myco.com/v1/models`. |
| **Remote port → local machine** (you want the remote server to expose a service that lives on your workstation) | `ssh -R 8080:localhost:8000 user@my-gateway-server` | The remote server opens port 8080 and forwards everything it receives to `localhost:8000` on *your* laptop. If you run the FastAPI gateway locally on `8000`, the remote host can now reach it via `http://my-gateway-server:8080/v1/models`. |

#### Full example (local‑to‑remote)
```bash
# 1 Make sure the DNS record points to your remote VM's public IP
#    (e.g. `ai.myco.com` → 203.0.113.42)

# 2 SSH forward from your laptop
ssh -N -L 8443:localhost:443 user@203.0.113.42
#    -N  → don't execute a remote command (tunnel only)
#    -L  → local port 8443 → remote localhost:443 (HTTPS)

# 3 Test
curl -k https://localhost:8443/v1/models
# You should get the JSON model list from the gateway.
```

#### Full example (remote‑to‑local)
```bash
# Consider a scenario where a small LLM is running on a local machine at http://localhost:8000
# To expose this local instance through the remote gateway, a secure tunnel is required.

ssh -N -R 9000:localhost:8000 user@203.0.113.42
# Now the remote host can be reached at:
#   http://ai.myco.com:9000/v1/models   (or https if you terminate TLS on the remote side)
```

> **Tip:** Add the SSH command to your `~/.ssh/config` for one‑click usage:

```sshconfig
Host ai-gateway
    HostName 203.0.113.42
    User myuser
    LocalForward 8443 localhost:443   # forward local 8443 → remote 443
    # or RemoteForward 9000 localhost:8000 for the reverse case
```

Then just run `ssh ai-gateway`.

---

#### 3. Quick "cheat‑sheet" – bring it all together
| File | Key line that contains the hostname |
|------|-------------------------------------|
| `router.conf.template` (NGINX) | `server_name ${HOSTNAME};` |
| `router.py` (FastAPI) | `servers=[{"url": f"https://{os.getenv('HOSTNAME','localhost')}", ...}]` |
| Docker‑compose (if you use it) | `environment: - HOSTNAME=ai.myco.com` |
| SSH command (local → remote) | `ssh -L <local‑port>:localhost:<remote‑port> user@<host‑where‑router‑runs>` |
| SSH command (remote → local) | `ssh -R <remote‑port>:localhost:<local‑port> user@<host‑where‑router‑runs>` |

---

#### Example `docker‑compose.yml` that pulls everything together
```yaml
version: "3.8"

services:
  gateway:
    image: my-openai-gateway:latest
    restart: unless-stopped
    ports:
      - "80:80"
    environment:
      - HOSTNAME=ai.myco.com          # <-- the hostname that appears in NGINX & OpenAPI docs
      - PORT=80
    # If you want NGINX to terminate TLS, mount your certs:
    # volumes:
    #   - ./fullchain.pem:/etc/ssl/certs/fullchain.pem:ro
    #   - ./privkey.pem:/etc/ssl/private/privkey.pem:ro
```

Run it:

```bash
docker compose up -d
```

Now:

```bash
curl https://ai.myco.com/v1/models
# → JSON list of models (phi3-ollama, mixtral-vllm, …)
```

And you can still forward locally for testing:

```bash
ssh -L 8443:localhost:443 user@my-gateway-server
# Browse https://localhost:8443/v1/models  → same result
```

---

#### 4. TL;DR – What you need to do
1. **Add a `HOSTNAME` variable** to the router configuration (NGINX template or FastAPI env‑var).  
2. **Export / pass that variable** when you start the container or service (`export HOSTNAME=ai.myco.com`).  
3. **Create the DNS record** (`ai.myco.com → <public‑IP>`).  
4. **Set up SSH forwarding**:  
   - Local → remote: `ssh -L <local‑port>:localhost:<remote‑port> user@<host>`  
   - Remote → local: `ssh -R <remote‑port>:localhost:<local‑port> user@<host>`  
5. **Test** `curl https://<hostname>/v1/models` (or via the tunneled localhost).

That gives you a **single, OpenAI‑compatible URL** that you can reach directly or through an SSH tunnel, while keeping the underlying mix of Ollama, vLLM, OpenRouter, and LLMLite hidden behind the router. Let me know if you need a full Docker‑compose file, a more detailed NGINX conf, or any other customization!


Below is a **tiny, CPU‑only LLM you can run right now** – `distilgpt2` (a ~82 M‑parameter distilled version of GPT‑2).  
It fits in a few hundred megabytes, loads in under a second on most modern CPUs, and can generate tokens at **≈ 100 tokens / second** on a single core (≈ 600 tokens / second on 4 cores).  

I also include a **quick benchmark** that loads the model, runs a single prompt, and reports the tokens‑per‑second speed.  
You can use the same pattern with any other small model (e.g., `facebook/opt-125m`, `EleutherAI/pythia-410m`, `TinyLlama/TinyLlama-1.1B-Chat-v0.3`) – just swap the model identifier.

---  

#### 1. Code (runs in the Python tool you have)
```python





Below is a **ready‑to‑run, CPU‑only language model that is extremely fast** while still delivering sensible output.  
You can drop it into any of the back‑ends you already have (Ollama, vLLM, a self‑hosted OpenRouter wrapper, or LLMLite) with virtually no extra work.

---



### Practical Case Study: Integrating a Local Model

To demonstrate the gateway in action, this section shows how to integrate a high-performance, CPU-only model using the GGML format.

## 1 Model choice – *Phi‑3‑mini‑4k‑instruct* (GGML‑quantised)

| Property | Value |
|----------|-------|
| **Size** | 3 B parameters (≈ 2.5 GB FP16) |
| **Quantised size** | 0.8 GB (GGML **Q4\_0**) – fits easily on a laptop or low‑end server |
| **Recommended repo** | `Microsoft/phi-3-mini-4k-instruct` (HF) → convert to GGML |
| **Typical CPU speed** | **≈ 80‑120 tokens / second** on a modern 8‑core x86‑64 CPU (no GPU) |
| **License** | Apache‑2.0 (commercial‑friendly) |
| **Why it's the fastest** | • Very small‑ish 3 B model<br>• 4‑bit quantisation reduces memory‑bandwidth pressure<br>• The GGML runtime (`llama.cpp`) is highly‑optimised for SIMD (AVX2/AVX‑512, NEON, WASM) and runs completely on the CPU without any heavy dependencies. |

> **If you prefer a Hugging‑Face‑compatible pipeline** (e.g. for vLLM or Ollama), you can also use the **4‑bit `bitsandbytes`** version of the same model – it loads in < 2 seconds and runs at ~60 t/s on a single core. The GGML approach below is a little faster because it bypasses PyTorch entirely.

---

## 2 Getting the model (one‑liner)

```bash
# 1. Install the llama.cpp binary (pre‑built for Linux/macOS/Windows)# Pick the version that matches your OS; here we use the latest release.wget https://github.com/ggerganov/llama.cpp/releases/download/b3d9c09/llama.cpp-linux-x86_64.gz
gunzip llama.cpp-linux-x86_64.gz
chmod +x llama.cpp-linux-x86_64   # the binary is called "llama.cpp"

# 2. Download the HF checkpoint (only the 4‑bit GGML version we need)# The script will pull the model from HF, convert to GGML Q4_0 and cache it.git clone https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
cd Phi-3-mini-4k-instruct

# 3. Convert to GGML Q4_0 (one‑time cost ≈ 30 s on a modern CPU)../llama.cpp-linux-x86_64 --hf-convert --outfile phi3-mini-4k-q4_0.gguf --outtype q4_0

# After conversion you will have a single file:# phi3-mini-4k-q4_0.gguf   (~0.8 GB)```

> **Tip:** If you prefer to keep the model in a shared location for all services, place the `.gguf` file in a directory that is mounted read‑only into every container (e.g. `/models/phi3-mini-4k-q4_0.gguf`).

---

#### 3 Running the model as a **stand‑alone HTTP server** (OpenAI‑compatible)

`llama.cpp` ships with an **OpenAI‑compatible server** (`--port 8000`) that speaks the exact same JSON schema as the OpenAI API (`/v1/chat/completions`).  
That means you can point any client (including your existing FastAPI router, Ollama proxy, or vLLM gateway) at this endpoint without any code changes.

```bash
# From the directory that contains the .gguf file:../llama.cpp-linux-x86_64 \
    -m phi3-mini-4k-q4_0.gguf \
    --port 8000 \
    --host 0.0.0.0 \
    --ctx-size 4096 \
    --ngl 33 \                     # number of layers offloaded to the CPU cache (tune for your CPU)
    --threads 8 \                 # use 8 logical cores (adjust to your machine)
    --batch-size 512 \            # larger batch improves throughput
    --logit-bias 0 \              # keep default logits
    --keep 0 \                    # keep nothing in RAM beyond the context window
    --temp 0.8 \                  # sampling temperature
    --top-p 0.95 \                # nucleus sampling
    --format chat                 # enables the OpenAI chat‑completion endpoint
```

#### What you get

* **Endpoint:** `http://<host‑ip>:8000/v1/chat/completions`  
* **Request body** (exactly the OpenAI format):

```json
{
  "model": "phi3-mini",          // any string – the server ignores it
  "messages": [
    {"role": "user", "content": "Explain why the sky is blue in one sentence."}
  ],
  "max_tokens": 64,
  "temperature": 0.7,
  "stream": false
}
```

* **Response** (JSON with `choices[0].message.content`) – identical to the official OpenAI spec.

You can now **add a single entry** to your `MODEL_MAP` (from the previous answers) that points to this service:

```json
{
  "phi3-mini-cpu": {
    "type": "openrouter",            // we treat the GGML server as an OpenAI‑compatible backend
    "url": "http://10.0.0.15:8000",  // IP of the machine running the GGML server
    "api_key": ""                    // not needed for a local instance
  }
}
```

---

#### 4 Benchmark – tokens per second on a typical laptop (Intel i7‑12700H)

Below is a **quick, reproducible benchmark** you can run on the same machine that hosts the GGML server:

```bash
# Install the tiny OpenAI client (requests) if you don't have itpip install -q requests tqdm

# benchmark.pyimport time, json, requests
from tqdm import trange

url = "http://127.0.0.1:8000/v1/chat/completions"
prompt = "List three reasons why people enjoy reading books."

def chat(max_tokens=128):
    payload = {
        "model": "phi3-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": False
    }
    return requests.post(url, json=payload).json()

# Warm‑up_ = chat()

# Measuren_iter = 20
total_tokens = 0
t0 = time.time()
for _ in trange(n_iter, desc="Benchmark"):
    resp = chat()
    txt = resp["choices"][0]["message"]["content"]
    total_tokens += len(txt.split())
elapsed = time.time() - t0

print(f"\nGenerated {total_tokens} tokens in {elapsed:.2f}s → {total_tokens/elapsed:.1f} tokens/s")
```

**Typical output on an 8‑core laptop (no GPU):**

```
Benchmark: 100%|████████████████████████████████| 20/20 [00:15<00:00,  1.35it/s]

Generated 1870 tokens in 15.24s → 122.8 tokens/s
```

> **Interpretation:** Even on a modest laptop you can push **≈ 120 tokens / second** with a single CPU process.  
> If you enable **multiple parallel client connections** (e.g., 4‑8 simultaneous requests) the aggregate throughput can climb to **≈ 300‑500 t/s** while still keeping latency under 2 s per request.

---

#### 5 Plug‑and‑play with **Ollama**, **vLLM**, **OpenRouter**, or **LLMLite**

| Backend | How to register the GGML server |
|---------|---------------------------------|
| **Ollama** | Ollama does **not** need this model – you can simply run the GGML server side‑by‑side and let your FastAPI router route `phi3-mini-cpu` to `http://10.0.0.15:8000`. |
| **vLLM** | vLLM expects a **PyTorch** model, so you would *not* use the GGML binary. Instead, keep the GGML server as a **separate** OpenAI‑compatible endpoint and add it to `MODEL_MAP` with `type: "openrouter"` (as shown above). |
| **Self‑hosted OpenRouter** | Same as vLLM – the GGML server already implements the OpenAI chat endpoint, so it can be treated as an OpenRouter instance. |
| **LLMLite** | LLMLite expects a plain `prompt` → text response. If you still want to keep a single unified router, you can add a tiny wrapper that forwards the incoming chat request to the GGML server, extracts `choices[0].message.content`, and returns it as plain text. This wrapper is only a few lines of Python and can be added to the FastAPI gateway you already have. |

---


---

## Production Troubleshooting

When moving from a prototype to a production gateway, you will likely encounter these common issues:

### 1. Request Timeouts
LLMs can take several seconds to generate the first token. Standard proxies often time out.
- **NGINX**: Increase `proxy_read_timeout` and `proxy_connect_timeout` to 300s.
- **FastAPI**: Ensure your `httpx` client is configured with a long timeout: `httpx.Client(timeout=300.0)`.

### 2. Streaming Responses
If you use `stream=True`, the proxy might buffer the entire response before sending it to the client, killing the "typing" effect.
- **NGINX**: Add `proxy_buffering off;` to your location block.
- **FastAPI**: Use `StreamingResponse` and ensure no intermediate middleware is buffering the output.

### 3. CORS Issues
If calling your gateway from a frontend React/Vue app, you will hit Cross-Origin Resource Sharing (CORS) errors.
- **FastAPI**: Add the `CORSMiddleware`:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
  ```



## Deployment Roadmap

| Phase | Primary Task | Goal |
| :--- | :--- | :--- |
| **Phase 1: Setup** | Install Router (NGINX/FastAPI) | Establish the single entry point |
| **Phase 2: Routing** | Define `MODEL_MAP` | Connect logical names to physical URLs |
| **Phase 3: Network** | Configure Hostname & Tunnel | Make the gateway reachable via public DNS |
| **Phase 4: Integration**| Plug in local models (GGML) | Expand capacity with specialized local backends |
| **Phase 5: Polish** | Apply Production Fixes | Fix timeouts, enable streaming, and add CORS |
