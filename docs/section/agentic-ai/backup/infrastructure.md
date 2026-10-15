# Raw Notes: Cloud Infrastructure & DevOps for Agents

## Deployment Strategies
- Serverless: AWS Lambda, Azure Functions.
    - Pros: Scale to zero, cost effective for sporadic use.
    - Cons: Cold starts, hard timeouts (15m for Lambda).
    - Scenario: Event-driven agent (e.g. email triage).
- Persistent: Kubernetes, ECS.
    - Pros: Long running, stateful, GPU access.
    - Cons: Management overhead, cost if idle.
    - Scenario: Research agent running for hours.
- Comparison: Serverless = stateless/short; Persistent = stateful/long.

## The Sandbox Requirement
- Risk: RCE (Remote Code Execution) via LLM prompt injection.
- Isolation Levels:
    - Docker: Namespaces/Cgroups (shared kernel = risk).
    - gVisor: User-space kernel (Sentry/Gofer), intercepts syscalls.
    - Firecracker: MicroVMs, hardware isolation, fast boot.
- Resource Limiting:
    - CPU/RAM: prevent OOM and CPU exhaustion.
    - Network: Disable or use allowlist to stop exfiltration.
    - Disk: Read-only root + tmpfs.
- Scenario: Analyzing a CSV in a restricted Firecracker VM.

## Observability & Tracing
- Thought Chain/Trajectories: (State, Action, Observation) sequences.
- Why: Detect looping, hallucinations, inefficiency.
- Tools:
    - LangSmith: Trace hierarchy, production monitoring.
    - Arize Phoenix: Open-source, local-first.
    - OpenTelemetry (OTel): Industry standard, Spans/Traces.
- Scenario: Debugging "Permission Denied" loop in a sandbox.
- Implementation: Wrap tool calls in OTel spans.
