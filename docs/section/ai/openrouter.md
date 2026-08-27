
# OpenRouter – Self‑Hosted Multi‑LLM Gateway**  

**Content**  

- OpenRouter – Self‑Hosted Gateway for Multiple Large Language Models  
- Presenter: Gregor von Laszewski

**Speaker notes**  

> Welcome. Over the next 20‑25 minutes I’ll walk you through why a router is useful, how you can host it yourself, and the step‑by‑step process for wiring together dozens of LLM providers under a single, unified API.  

**Visual hint** – Title centered, OpenRouter logo (or placeholder), faint background of connected nodes.  

---  

## Slide 2 – The Problem Landscape  

**Content**  

- Rapid growth of LLM providers (OpenAI, Anthropic, Google DeepMind, Meta, Mistral, Cohere, AI21, …)  
- Each provider has its own:  
  - Authentication model (API keys, OAuth)  
  - Request/response schema (different field names, token limits)  
  - Pricing and quota mechanisms  
  - Safety / moderation settings  
- Engineering effort spent on:  
  - Maintaining separate SDKs / wrappers  
  - Reconciling disparate error handling  
  - Building custom routing, cost‑control, and compliance logic  

**Speaker notes**  

> The LLM ecosystem is now more diverse than the web‑browser market in 2005. If you need to experiment with three different models you already have three code paths, three secrets, and three billing dashboards. This fragmentation wastes time and creates hidden operational risk.  

**Visual hint** – Timeline of provider releases + “spaghetti” diagram of multiple API arrows converging on a single application.  

---  

## Slide 3 – What a Router Does  

**Content**  

- Provides a **single HTTP endpoint** and **single API key** for all downstream models.  
- Normalises request/response payloads to a **canonical schema** (compatible with OpenAI’s `chat/completions` format).  
- Evaluates **routing policies** (cost, latency, capability, custom tags) to select the appropriate provider at runtime.  
- Enforces **centralised safety and moderation** before forwarding the request.  
- Returns a **transparent cost breakdown** per request.  

**Speaker notes**  

> Think of the router as the traffic controller for LLM calls. Your client sends a request once; the router decides which provider should answer, applies any safety filters, forwards the call, and normalises the response back to your client.  

**Visual hint** – Flow diagram: Client → Router → Provider Adapters → Provider APIs → Router (response).  

---  

## Slide 4 – Why Host Your Own Router?  

**Content**  

| Reason | Benefit |
|--------|---------|
| Data residency | Keep traffic inside a specific region or VPC. |
| Custom policies | Implement proprietary compliance or business rules that the SaaS version cannot express. |
| Performance control | Deploy edge nodes close to your users or to a specific provider’s data centre. |
| Cost optimisation | Eliminate the SaaS platform‑level markup (only provider fees remain). |
| Extensibility | Add private or on‑premise LLMs that are not publicly listed. |

**Speaker notes**  

> For regulated industries, for ultra‑low‑latency use‑cases, or when you have a private model you want to expose through the same API, a self‑hosted router is the only viable option.  

**Visual hint** – Table with check‑marks; world‑map highlighting “region‑locked traffic”.  

---  

## Slide 5 – High‑Level Architecture (Self‑Hosted)  

**Content**  

```
+-------------------+       +-------------------+       +-------------------+
|   Client App      |  <-->|   Router API GW   |<----->|   AuthN / AuthZ   |
+-------------------+       +-------------------+       +-------------------+
                                 |
                         +-------------------+
                         |   Routing Engine  |
                         +-------------------+
                                 |
               +-----------------+-----------------+
               |                 |                 |
+-------------------+ +-------------------+ +-------------------+
| Provider Adapter  | | Provider Adapter  | | Provider Adapter  |
+-------------------+ +-------------------+ +-------------------+
      |                     |                     |
Provider API (OpenAI)  Provider API (Anthropic)  Provider API (Gemini) …
```

**Speaker notes**  

> The Router API Gateway handles TLS termination, request validation, and rate limiting. The Routing Engine evaluates the policy you configure. Each Provider Adapter translates the canonical request into the provider‑specific HTTP call and back again. All components are stateless and can be scaled independently.  

**Visual hint** – Same diagram rendered as a block diagram with colour‑coded layers.  

---  

## Slide 6 – Core OpenRouter Open‑Source Repository  

**Content**  

- Repository: `github.com/openrouter/openrouter` (MIT License)  
- Languages: **Go** (router core) + **Python** (reference SDK) + **YAML** configuration files.  
- Key directories:  
  - `cmd/router` – entry point (binary)  
  - `internal/router` – request parsing, policy engine  
  - `internal/adapters` – one sub‑folder per provider (OpenAI, Anthropic, etc.)  
  - `configs/` – sample YAML files for routing, safety, and billing  
  - `docker/` – Dockerfile & compose templates  
- CI/CD: GitHub Actions build multi‑arch images (linux/amd64, linux/arm64).  

**Speaker notes**  

> The repo is deliberately modular: adding a new provider is just a matter of dropping a new adapter implementation into `internal/adapters` and wiring it up in the config. The Go codebase is < 10 k lines, making it easy to audit for security.  

**Visual hint** – Screenshot of the repository tree with highlighted folders.  

---  

## Slide 7 – Deployment Options  

**Content**  

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| Docker Compose | Single‑node deployment on any machine. | Quick start, useful for development. | Limited scaling, no built‑in HA. |
| Kubernetes (Helm Chart) | Deploy as a set of pods behind an Ingress. | Auto‑scaling, rolling upgrades, native observability. | Requires a K8s cluster. |
| Serverless (AWS Lambda + API Gateway) | Stateless function per request. | Pay‑per‑use, minimal ops. | Cold‑start latency, limited execution time. |
| Edge (Cloudflare Workers, Fastly Compute@Edge) | Run the gateway on the CDN edge. | Sub‑50 ms added latency for end‑users. | More complex build pipeline, limited binary size. |

**Speaker notes**  

> For most production workloads I recommend the Helm chart on a managed K8s service (EKS, GKE, AKS). It gives you auto‑scaling, built‑in support for secrets, and native Prometheus metrics.  

**Visual hint** – Icons representing Docker, K8s, Lambda, Edge.  

---  

## Slide 8 – Prerequisites (Kubernetes Example)  

**Content**  

1. **K8s cluster** – version ≥ 1.25, at least 2 CPU & 4 GiB per node.  
2. **kubectl** configured with cluster admin rights.  
3. **Helm 3** installed locally.  
4. **External secret store** (AWS Secrets Manager, HashiCorp Vault, or K8s sealed secrets).  
5. **Domain name** and TLS certificate (Let’s Encrypt via cert‑manager is supported).  

**Speaker notes**  

> Because the router deals with API keys for each provider, storing them in a dedicated secret manager is essential. The Helm chart includes a secret‑injector sidecar that pulls secrets at pod start‑up, avoiding hard‑coded credentials.  

**Visual hint** – Checklist graphic with tick marks.  

---  

## Slide 9 – Step‑by‑Step: Deploying via Helm  

**Content**  

```bash
# 1. Add the OpenRouter Helm repo
helm repo add openrouter https://charts.openrouter.ai
helm repo update

# 2. Create a secret that contains provider API keys (example for OpenAI & Anthropic)
kubectl create secret generic openrouter-providers \
  --from-literal=openai_api_key=sk-... \
  --from-literal=anthropic_api_key=sk-anthropic-...

# 3. Install the chart with a custom values file
helm install openrouter openrouter/openrouter \
  -f values.yaml   # see next slide for key sections
```

**Speaker notes**  

> The `values.yaml` file contains the routing policies, safety settings, and telemetry configuration. By separating provider keys into a K8s secret we keep them out of version control.  

**Visual hint** – Terminal screenshot of the commands.  

---  

## Slide 10 – Sample `values.yaml` (Core Sections)  

**Content**  

```yaml
replicaCount: 3

service:
  type: LoadBalancer
  port: 443

gateway:
  # JWT secret for the router’s own auth
  jwtSecret: "super-secret-jwt"

routing:
  defaultModel: "auto"
  policies:
    - name: "cost-optimised"
      criteria:
        maxCostPer1kTokens: 0.015
      fallbackOrder:
        - provider: "mistralai"
          model: "mistral-large"
        - provider: "anthropic"
          model: "claude-3-sonnet"
    - name: "low-latency-eu"
      region: "eu-central-1"
      fallbackOrder:
        - provider: "openai"
          model: "gpt-4o-mini"

safety:
  enableModeration: true
  customBlocklist: |
    # Regex patterns (one per line)
    (?i)credit\s*card
    (?i)social\s*security

monitoring:
  prometheus:
    enabled: true
    port: 9090
```

**Speaker notes**  

> This file shows three important blocks: the `gateway` JWT secret, `routing` policies, and `safety` configuration. The router will first try the Mistral‑Large model as long as the per‑token cost stays below $0.015, otherwise it falls back to Claude‑3‑Sonnet. The `low-latency-eu` policy forces the router to use providers that have edge nodes in the EU region.  

**Visual hint** – Highlighted YAML sections with call‑outs pointing to each block.  

---  

## Slide 11 – Provider Adapter Design  

**Content**  

```go
type ProviderAdapter interface {
    // Translate the canonical request into the provider‑specific HTTP payload
    BuildRequest(ctx context.Context, in *OpenRouterRequest) (*http.Request, error)

    // Parse the provider response back to the canonical format
    ParseResponse(ctx context.Context, resp *http.Response) (*OpenRouterResponse, error)

    // Optional health‑check endpoint
    HealthCheck(ctx context.Context) error
}
```

*Implementation steps for a new provider*  

1. Create a new folder under `internal/adapters/<provider>`  
2. Implement the `ProviderAdapter` interface.  
3. Register the adapter in `internal/router/registry.go`.  
4. Add provider‑specific configuration fields to `configs/provider.yaml`.  

**Speaker notes**  

> The adapter isolates all provider‑specific quirks: token‑counting algorithms, model naming conventions, pagination, and streaming semantics. By conforming to the `ProviderAdapter` interface the router can treat every LLM as interchangeable.  

**Visual hint** – Diagram showing the interface in the centre, arrows to concrete implementations (OpenAI, Anthropic, Gemini, etc.).  

---  

## Slide 12 – Integrating a New LLM (Example: Cohere)  

**Content**  

1. **Add configuration schema** (`configs/cohere.yaml`)  

```yaml
apiKey: "<REDACTED>"
endpoint: "https://api.cohere.com/v1"
defaultModel: "command-r-plus"
```

2. **Implement adapter (`cohere_adapter.go`)**  

```go
func (a *CohereAdapter) BuildRequest(ctx context.Context, in *OpenRouterRequest) (*http.Request, error) {
    payload := map[string]any{
        "model": a.cfg.DefaultModel,
        "prompt": in.Messages.ToCoherePrompt(),
        "max_tokens": in.MaxTokens,
        "temperature": in.Temperature,
    }
    body, _ := json.Marshal(payload)
    req, _ := http.NewRequestWithContext(ctx, http.MethodPost,
        a.cfg.Endpoint+"/chat", bytes.NewReader(body))
    req.Header.Set("Authorization", "Bearer "+a.cfg.ApiKey)
    req.Header.Set("Content-Type", "application/json")
    return req, nil
}

func (a *CohereAdapter) ParseResponse(ctx context.Context, resp *http.Response) (*OpenRouterResponse, error) {
    var cohereResp struct {
        Text string `json:"text"`
    }
    json.NewDecoder(resp.Body).Decode(&cohereResp)
    return &OpenRouterResponse{
        Choices: []Choice{
            {Message: Message{Role: "assistant", Content: cohereResp.Text}},
        },
    }, nil
}
```

3. **Register the adapter**  

```go
router.RegisterAdapter("cohere", NewCohereAdapter(cfg.Cohere))
```

4. **Update `values.yaml`** to expose the Cohere API key in the secret and, if desired, add a routing rule that references `cohere/command-r-plus`.  

**Speaker notes**  

> This example shows the minimal code required: map the incoming `messages` array to Cohere’s prompt format, forward the request, then wrap Cohere’s `text` field back into the standard OpenRouter response structure.  

**Visual hint** – Side‑by‑side code snippets with annotations.  

---  

## Slide 13 – Tokenisation & Length Normalisation  

**Content**  

- Different providers use distinct tokenisers (e.g., tiktoken for OpenAI, BPE for Llama).  
- OpenRouter normalises token counts by:  
  1. Detecting the target provider from the routing decision.  
  2. Instantiating the provider‑specific tokeniser (`github.com/pkoukos/tokenizer`).  
  3. Converting the canonical message list to a raw string, then measuring tokens.  
- Token count is stored in request metadata and exposed in the cost breakdown.  

**Speaker notes**  

> Accurate token accounting is essential for billing and for respecting provider limits (e.g., 8 k vs. 32 k context windows). The router performs this conversion once per request, regardless of how many providers you have configured.  

**Visual hint** – Flowchart: Canonical messages → Provider‑specific tokenizer → token count → routing decision.  

---  

## Slide 14 – Safety & Moderation Pipeline  

**Content**  

1. **Pre‑routing moderation** – Unified filter that runs before any provider call.  
   - Built‑in OpenAI moderation endpoint (optional).  
   - Custom regex / blocklist (configurable).  
2. **Provider‑level safety flags** – The router can set provider‑specific parameters (e.g., Anthropic’s `use_safe_prompt=true`).  
3. **Post‑response sanitisation** – Strip disallowed patterns from the model output (PII redaction, profanity mask).  

**Speaker notes**  

> The safety pipeline runs entirely inside your trusted environment, so you keep full control over what is blocked or allowed before the request leaves your network. This is especially important for industries with strict compliance obligations.  

**Visual hint** – Three‑stage diagram: Input → Moderation → Provider → Post‑processing → Output.  

---  

## Slide 15 – Observability & Monitoring  

**Content**  

- **Metrics (Prometheus)** exported by the router:  
  - `router_requests_total{provider,model,result}`  
  - `router_latency_seconds_bucket{provider,model}`  
  - `router_tokens_input_total`, `router_tokens_output_total`  
- **Logs** (structured JSON) include request ID, provider, token counts, cost, and any moderation actions.  
- **Tracing** (OpenTelemetry) optional – injects a trace ID that propagates to the downstream provider (if supported).  
- **Dashboard** (Grafana) – pre‑built panels for cost per provider, latency heatmaps, error rates.  

**Speaker notes**  

> Because the router is stateless, all observability data lives outside the process. Exporting metrics to Prometheus lets you set alerts (e.g., latency > 200 ms for a particular provider) and use Grafana to visualise cost trends over time.  

**Visual hint** – Screenshot of a Grafana dashboard with panels for latency, cost, request volume.  

---  

## Slide 16 – Scaling the Router  

**Content**  

- **Horizontal Pod Autoscaling (HPA)** based on:  
  - CPU utilisation (default)  
  - Custom metric `router_requests_per_second`  
- **Pod Disruption Budgets** to guarantee minimum availability during upgrades.  
- **Geographic distribution** – Deploy separate Helm releases per region (e.g., `openrouter-eu`, `openrouter-us`) and use DNS‑based traffic routing.  
- **Caching layer (optional)** – Deploy a sidecar Redis to memoise identical prompts; cache TTL configurable per routing policy.  

**Speaker notes**  

> The router’s design is deliberately stateless, enabling you to scale out with a simple `kubectl scale` command or an HPA policy that reacts to request volume. If you need sub‑regional latency you spin up another replica set in the desired cloud region and point your DNS to the nearest IP.  

**Visual hint** – Kubernetes autoscaling diagram with a load balancer distributing traffic across multiple pods.  

---  

## Slide 17 – Security Considerations  

**Content**  

| Aspect | Implementation |
|--------|----------------|
| Transport | TLS 1.3 termination at the Ingress; mutual TLS optional for internal service‑to‑service calls. |
| Authentication | JWT bearer token for client calls; secret stored in a Kubernetes secret and rotated via a cronjob. |
| Authorization | RBAC rules on the router (e.g., read‑only token for analytics, full‑access token for production). |
| Secret Management | Provider API keys loaded from external secret manager at pod startup; never checked into source control. |
| Audit Logging | Immutable log storage (CloudWatch, ELK) with request ID, user ID, provider, and cost. |
| Compliance | Ability to disable prompt logging, enforce region‑specific routing, and apply GDPR‑compatible data‑handling policies. |

**Speaker notes**  

> Treat the router as a critical security boundary. By enforcing JWT authentication and keeping provider secrets out of the container image, you reduce the attack surface dramatically.  

**Visual hint** – Shield icons with labels for each security control.  

---  

## Slide 18 – End‑to‑End Example: From Client to Provider  

**Content** – Numbered flow  

1. **Client** sends a POST to `https://router.mycompany.com/v1/chat/completions` with JWT.  
2. **Gateway** validates JWT, extracts `user_id`.  
3. **Routing Engine** reads the policy:  
   - If `user_id` belongs to `premium` tier → prefer `anthropic/claude-3-opus`.  
   - Otherwise cost‑optimised fallback order.  
4. **Safety Layer** runs the input through regex blocklist; request approved.  
5. **Adapter** for the chosen provider builds the provider‑specific HTTP request.  
6. **Provider** returns a response; adapter translates it back to canonical format.  
7. **Post‑processing** redacts any PII detected in the output.  
8. **Response** sent back to client with additional fields: `usage.input_tokens`, `usage.output_tokens`, `cost_per_provider`.  

**Speaker notes**  

> This slide ties together everything we’ve covered: authentication, policy evaluation, safety, provider translation, and cost reporting—all happening within a few hundred milliseconds.  

**Visual hint** – Numbered flow diagram with icons for each component.  

---  

## Slide 19 – Testing & Validation  

**Content**  

- **Unit tests** – each adapter has a test suite with mocked provider responses.  
- **Integration tests** – spin up a local Docker Compose stack (`router`, `redis`, `prometheus`) and run end‑to‑end scenarios.  
- **Contract testing** – use OpenAPI spec (`openrouter.yaml`) to verify that external clients receive the expected schema.  
- **Load testing** – `k6` script that simulates 10 k RPS across multiple routing policies; monitor latency and error rate.  

**Speaker notes**  

> Because the router is a critical piece of infrastructure, we recommend a CI pipeline that runs the full suite on every PR. Contract testing guarantees backward compatibility for downstream clients.  

**Visual hint** – CI pipeline diagram with stages: lint → unit → integration → contract → load → deploy.  

---  

## Slide 20 – Upgrading the Router  

**Content**  

- **Semantic versioning** – major version bump only for breaking changes.  
- **Rolling upgrade** – Helm `--set image.tag=…` triggers a rolling restart; existing connections are drained gracefully.  
- **Feature flags** – stored in a ConfigMap; can be toggled without redeploy (e.g., enable new safety filter).  
- **Database‑less** – all state lives in external stores (Redis cache, Prometheus); upgrade does not require migrations.  

**Speaker notes**  

> Upgrading is painless because the router does not keep any internal state. You can test a new version in a “canary” namespace, route a fraction of traffic to it, and promote once confidence is established.  

**Visual hint** – Diagram of blue‑green deployment with traffic split.  

---  

## Slide 21 – Limitations & Open Issues  

**Content**  

| Limitation | Mitigation / Future Work |
|------------|--------------------------|
| Streaming support – current release provides only full‑response mode. | Experimental streaming adapter being added (WebSocket + SSE). |
| Provider‑specific features (e.g., tool calling) need explicit mapping. | Extend canonical schema to include a generic `tool_calls` array. |
| Model metadata freshness – provider model list must be refreshed manually. | Add background job that polls provider APIs daily and updates the catalog. |
| Edge‑only deployments – size constraints on some edge runtimes. | Offer a minimal “router‑lite” binary that strips out metrics and health checks. |

**Speaker notes**  

> Being transparent about current gaps builds trust. Most of these shortcomings are on our roadmap and have concrete implementation plans.  

**Visual hint** – Table with highlighted rows.  

---  

## Slide 22 – Recap & Call to Action  

**Content**  

- **Why host?** Data residency, custom policies, performance, cost.  
- **How to host?** Docker Compose for dev, Helm on K8s for production.  
- **Integrate any LLM** by implementing the `ProviderAdapter` interface; sample code for Cohere provided.  
- **Operate safely** with built‑in moderation, JWT auth, secret management, and full observability.  

**Speaker notes**  

> If you have a use‑case that demands control over where your prompts travel, or you simply want a single API for dozens of models, the self‑hosted OpenRouter gives you that flexibility. The code is open source, the Helm chart is production‑ready, and the adapter pattern makes adding new providers trivial.  

**Visual hint** – Bullet list with a bold “Get Started” button graphic and a QR code linking to the GitHub repo.  

---  

## Slide 23 – Q&A  

**Content**  

- Contact: *Your Name* – *email* – *GitHub @yourhandle*  
- Additional resources:  
  - Repository: `https://github.com/openrouter/openrouter`  
  - Documentation: `https://docs.openrouter.ai`  
  - Community Slack: `https://slack.openrouter.ai`  

**Speaker notes**  

> Thank you for your attention. I’m happy to dive deeper into any of the topics—whether it’s the Helm deployment, writing a new adapter, or configuring advanced safety policies.  

**Visual hint** – Simple, clean slide with contact icons (email, GitHub, Slack).  

---  

## Slide 24 – Quick‑Start: Call OpenRouter from **cURL**  

**Content**  

```bash
curl https://router.mycompany.com/v1/chat/completions \
  -H "Authorization: Bearer sk-or-xxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "auto",
        "messages": [{"role": "user", "content": "Summarise the latest AI research trends"}],
        "max_tokens": 512,
        "temperature": 0.7,
        "fallbacks": [
          {"model": "mistralai/mistral-large"},
          {"model": "anthropic/claude-3-sonnet"}
        ]
      }'
```

**Speaker notes**  

> If you just need a one‑off test or you’re working from a CI pipeline that doesn’t have a language runtime, a raw `curl` command works perfectly. The JSON payload mirrors the OpenAI chat‑completion format, and the `fallbacks` array tells the router its routing policy for this request.  

**Visual hint** – Show terminal output (JSON response containing `choices[0].message.content` and a `usage` object).  

---  

## Slide 25 – Quick‑Start: Call OpenRouter from **Node.js / JavaScript**  

**Content**  

```javascript
// ----------------------------------------------------
// 1️⃣ Install the SDK
// ----------------------------------------------------
npm install openrouter   // or: yarn add openrouter

// ----------------------------------------------------
// 2️⃣ Minimal client code (ESM syntax)
// ----------------------------------------------------
import OpenRouter from "openrouter";

const client = new OpenRouter({
  apiKey: "sk-or-xxxxxxxxxxxxxxxxxxxx",          // from https://router.mycompany.com/dashboard
  baseURL: "https://router.mycompany.com/api/v1" // your self‑hosted endpoint
});

const routing = {
  model: "auto",
  fallbacks: [
    { model: "mistralai/mistral-large" },
    { model: "anthropic/claude-3-sonnet" }
  ],
  max_tokens: 512,
  temperature: 0.7
};

(async () => {
  const resp = await client.chat.completions.create(
    {
      messages: [{ role: "user", content: "Summarise the latest AI research trends" }]
    },
    routing               // ← routing options are passed as a second argument
  );

  console.log(resp.choices[0].message.content);
})();
```

**Speaker notes**  

> The JavaScript SDK follows the same design as the Python one: a `Client` object, a `chat.completions.create` method, and a plain‑object `routing` configuration. The only difference is the import syntax (`import … from …`) and the use of async/await.  

**Visual hint** – Screenshot of VS Code showing the file, with the output printed in the integrated terminal.  

---  

## Slide 26 – Quick‑Start: Call OpenRouter from **Go**  

**Content**  

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/openrouter/openrouter-go" // hypothetical official Go SDK
)

// ---------------------------------------------------------------------
// Helper to build the request payload (same shape as the Python/JS SDK)
// ---------------------------------------------------------------------
type Routing struct {
	Model     string   `json:"model"`
	Fallbacks []Model  `json:"fallbacks,omitempty"`
	MaxTokens int      `json:"max_tokens,omitempty"`
	Temp      float64  `json:"temperature,omitempty"`
}

type Model struct {
	Model string `json:"model"`
}

func main() {
	// -----------------------------------------------------------------
	// 1️⃣ Initialise the client (base URL points to your self‑hosted router)
	// -----------------------------------------------------------------
	cfg := openrouter.Config{
		APIKey:  "sk-or-xxxxxxxxxxxxxxxxxxxx",
		BaseURL: "https://router.mycompany.com/api/v1",
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
	client := openrouter.NewClient(cfg)

	// -----------------------------------------------------------------
	// 2️⃣ Define routing options
	// -----------------------------------------------------------------
	routing := Routing{
		Model: "auto",
		Fallbacks: []Model{
			{Model: "mistralai/mistral-large"},
			{Model: "anthropic/claude-3-sonnet"},
		},
		MaxTokens: 512,
		Temp:      0.7,
	}

	// -----------------------------------------------------------------
	// 3️⃣ Build the request body
	// -----------------------------------------------------------------
	reqBody := map[string]any{
		"messages": []map[string]string{
			{"role": "user", "content": "Summarise the latest AI research trends"},
		},
		"max_tokens":  routing.MaxTokens,
		"temperature": routing.Temp,
		"model":       routing.Model,
		"fallbacks":   routing.Fallbacks,
	}
	// Marshal to JSON for the SDK's generic Create method
	payload, _ := json.Marshal(reqBody)

	// -----------------------------------------------------------------
	// 4️⃣ Call the router (the generic Create method accepts raw JSON)
	// -----------------------------------------------------------------
	resp, err := client.Post(context.Background(),
		"/v1/chat/completions",
		"application/json",
		strings.NewReader(string(payload)),
	)
	if err != nil {
		log.Fatalf("router call failed: %v", err)
	}
	defer resp.Body.Close()

	// -----------------------------------------------------------------
	// 5️⃣ Decode the OpenRouter response (same schema as OpenAI)
	// -----------------------------------------------------------------
	var result struct {
		Choices []struct {
			Message struct {
				Role    string `json:"role"`
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		log.Fatalf("decode failed: %v", err)
	}
	fmt.Println(result.Choices[0].Message.Content)
}
```

**Speaker notes**  

> In Go we don’t have a fully‑fledged high‑level SDK yet (the community is building one), so the example uses the generic `Post` method on a thin client wrapper. The request payload is identical to the Python/JS versions – the router only cares about the JSON shape, not the language that produced it.  

**Visual hint** – IDE screenshot (GoLand or VS Code) showing the compiled binary output.  

---  

## Slide 27 – Python Alternative (Reference)  

**Content**  

```python
# ----------------------------------------------------
# 1️⃣ Install the SDK
# ----------------------------------------------------
# pip install openrouter

import openrouter

client = openrouter.Client(
    api_key="sk-or-xxxxxxxxxxxxxxxxxxxx",
    base_url="https://router.mycompany.com/api/v1"
)

routing = {
    "model": "auto",
    "fallbacks": [
        {"model": "mistralai/mistral-large"},
        {"model": "anthropic/claude-3-sonnet"}
    ],
    "max_tokens": 512,
    "temperature": 0.7
}

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Summarise the latest AI research trends"}],
    **routing
)

print(response.choices[0].message.content)
```

**Speaker notes**  

> The Python version is the most compact because the official SDK hides the HTTP layer. Notice how the routing dictionary is splatted (`**routing`) into the method call – this is the same mechanism used by the other SDKs, only the syntax differs.  

**Visual hint** – Jupyter‑style output cell showing the generated summary.  

---  

## Slide 28 – Adding a New Provider Adapter (Go **vs** Node)  

### Go – Adapter Skeleton  

```go
type CohereAdapter struct {
    cfg CohereConfig
}

func NewCohereAdapter(cfg CohereConfig) *CohereAdapter {
    return &CohereAdapter{cfg: cfg}
}

func (a *CohereAdapter) BuildRequest(ctx context.Context, in *OpenRouterRequest) (*http.Request, error) {
    // Build provider‑specific JSON payload …
}
func (a *CohereAdapter) ParseResponse(ctx context.Context, resp *http.Response) (*OpenRouterResponse, error) {
    // Map Cohere's response back to the canonical format …
}
```

### Node.js – Adapter Skeleton (using **express** + **axios**)  

```javascript
// file: adapters/cohereAdapter.js
import axios from "axios";

export class CohereAdapter {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.endpoint = config.endpoint; // e.g. "https://api.cohere.com/v1"
    this.defaultModel = config.defaultModel;
  }

  // Build the provider‑specific HTTP request
  async buildRequest(openRouterReq) {
    const payload = {
      model: this.defaultModel,
      prompt: openRouterReq.messages
        .map(m => (m.role === "assistant" ? "" : m.content))
        .join("\n"),
      max_tokens: openRouterReq.max_tokens,
      temperature: openRouterReq.temperature,
    };

    return {
      method: "POST",
      url: `${this.endpoint}/chat`,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      data: payload,
    };
  }

  // Translate Cohere's response to the canonical shape
  parseResponse(cohereResp) {
    return {
      choices: [
        {
          message: {
            role: "assistant",
            content: cohereResp.text,
          },
        },
      ],
    };
  }
}
```

**Speaker notes**  

> Both languages expose the same two core methods: `buildRequest` (creates the outbound HTTP call) and `parseResponse` (maps the provider’s response back to the OpenRouter schema). The Go version returns an `*http.Request`; the Node version returns an Axios config object – the router core can consume either because it only needs the HTTP verb, URL, headers, and body.  

**Visual hint** – Side‑by‑side diff view with highlighted sections (`BuildRequest` & `ParseResponse`).  

---  

## Slide 29 – Running the Example in a Docker Container (Language‑agnostic)  

**Content**  

```dockerfile
# ----------------------------------------------------
# Multi‑stage Dockerfile that supports Python, Node, or Go
# ----------------------------------------------------
ARG LANG=python   # change to "node" or "go" as needed

# ---------- Python ----------
FROM python:3.11-slim AS python-builder
WORKDIR /app
COPY ./python_demo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./python_demo/ .

# ---------- Node ----------
FROM node:20-alpine AS node-builder
WORKDIR /app
COPY ./node_demo/package*.json .
RUN npm ci --omit=dev
COPY ./node_demo/ .

# ---------- Go ----------
FROM golang:1.22-alpine AS go-builder
WORKDIR /src
COPY ./go_demo/go.mod ./go_demo/go.sum .
RUN go mod download
COPY ./go_demo/ .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app/router-demo .

# ---- Runtime ----
FROM alpine:3.19 AS runtime
ARG LANG=python
WORKDIR /app

# Choose runtime based on the build argument
COPY --from=python-builder /app /app   / # for Python
COPY --from=node-builder   /app /app   / # for Node
COPY --from=go-builder     /app/router-demo /app/router-demo   # for Go

EXPOSE 8080

ENTRYPOINT ["/bin/sh", "-c", "\
  if [ \"$LANG\" = \"python\" ]; then exec python main.py; \
  elif [ \"$LANG\" = \"node\" ]; then exec node index.js; \
  elif [ \"$LANG\" = \"go\" ]; then exec /app/router-demo; \
  else echo \"Unsupported LANG=$LANG\" && exit 1; \
  fi"]
```

**Speaker notes**  

> The same Dockerfile can be used to build a container for any of the three runtimes. Just pass `--build-arg LANG=node` (or `go`, `python`) to `docker build`. This demonstrates that the router itself is language‑agnostic – the client code can be written in whatever stack your team prefers.  

**Visual hint** – Docker build command line:  

```bash
docker build -t openrouter-demo --build-arg LANG=node .
docker run -p 8080:8080 openrouter-demo
```

---  

## Slide 30 – Summary of Language Options  

| Language | SDK Availability | Typical Use‑Case | Example Command |
|----------|------------------|------------------|-----------------|
| Python | `openrouter` (pip) | Prototyping, data‑science notebooks | `python demo.py` |
| Node.js | `openrouter` (npm) | Web services, serverless functions | `node index.js` |
| Go | Community wrapper (`openrouter-go`) or raw HTTP | High‑throughput micro‑services, compiled binaries | `go run main.go` |
| cURL | No SDK needed | Quick sanity checks, CI verification | `curl …` |

**Speaker notes**  

> Pick the language that matches the rest of your stack. The router treats every request as a plain JSON payload, so you can even use `curl` for ad‑hoc testing. The SDKs simply hide the boiler‑plate HTTP handling and expose the same routing‑policy object across languages.  

**Visual hint** – Logos of the four languages side‑by‑side with checkmarks.  

---  

## Slide 31 – Final Thought  

**Content**  

- OpenRouter provides a **single source of truth** for LLM access across providers.  
- Self‑hosting gives you **control over data residency, cost, performance, and custom policies**.  
- Adding new models is a matter of writing a small adapter that implements two methods.  
- Full observability, safety, and compliance features are baked in.  

**Speaker notes**  

> Whether you are a startup experimenting with several APIs or an enterprise that must keep data inside a private network, the self‑hosted OpenRouter turns the fragmented LLM landscape into a unified, manageable service.  

**Visual hint** – Closing graphic: a highway metaphor with many model “cars” merging onto a single “router” lane, heading toward a destination labeled “Your Application”.  

---  

### How to Use This Markdown File  

1. Save the whole content as `openrouter_presentation.md`.  
2. Run your preferred Markdown‑to‑slides converter, e.g.:  

   ```bash
   # Marp (npm)
   npx @marp-team/marp-cli openrouter_presentation.md --pdf -o openrouter.pdf
   # Pandoc
   pandoc openrouter_presentation.md -t pptx -o openrouter.pptx --slide-level=2
   ```  

3. Edit the placeholder values (`sk-or-…`, domain names, repo paths) with your real data.  
4. Add the actual images/diagrams referenced in the “Visual hint” notes.  

You now have a complete, ready‑to‑present slide deck covering the **self‑hosted OpenRouter gateway**, its architecture, deployment, security, and **multi‑language client examples**. Good luck!