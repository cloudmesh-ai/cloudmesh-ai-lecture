# OSX

NVIDIA PAIR on macOS will not automatically install Ollama or LM Studio for you in the background; rather, **you must install the inference engine manually on your Mac first** for PAIR to recognize it and route traffic to it.

While documentation states that PAIR helps manage engine configurations, on macOS security boundaries and application packaging models prevent PAIR from autonomously downloading and bootstrapping third-party apps like Ollama or LM Studio directly.

### How to fix it:

1. **Download and install an engine manually:**
* Grab [Ollama for macOS](https://ollama.com) or [LM Studio for macOS](https://lmstudio.ai) and move the application to your `Applications` folder.


2. **Launch the engine:**
* Open Ollama or LM Studio at least once so its background service or local API server starts running and listening on its default port (`11434` for Ollama or `1234` for LM Studio).


3. **Restart PAIR:**
* Quit and reopen NVIDIA PAIR. It will scan your localhost, discover the running engine instance, and allow you to link it inside your node settings.

## safety on osx

**By default, Ollama is completely safe** because it binds strictly to `127.0.0.1` (localhost) on port `11434`. This means it only accepts connections originating from your local Mac, and external machines on your network cannot see or talk to it directly.

However, depending on your setup, you need to be mindful of how bindings and network access are handled:

### 1. Localhost is Secure (Standard Setup)

If Ollama is running locally on your Mac and NVIDIA PAIR is communicating with it via `http://localhost:11434`, **no extra port protection is needed**. Because the API has no built-in authentication layer, keeping it bound to localhost ensures that only local processes (like PAIR or your local terminal) can send prompts to it.

### 2. The Danger of `OLLAMA_HOST=0.0.0.0`

If you ever change Ollama's environment variables to bind to `0.0.0.0` (to allow external machines to connect directly), **anyone on your local network—or the internet, if your router has port forwarding enabled—can read your chat history, send prompts, or drain your system resources without authentication.**

### How NVIDIA PAIR Handles This Safely

NVIDIA PAIR is designed to bypass the need to expose raw engine ports across your network. When you link multiple machines in PAIR, it uses secure mDNS discovery and bootstraps encrypted communication channels (mTLS with generated certificates) for node-to-node routing. This means your underlying engines (like Ollama) can safely stay bound strictly to `127.0.0.1` locally, while PAIR safely handles any cross-device proxying.

No, NVIDIA PAIR does not officially support vLLM out of the box.  Officially, PAIR's routing and management layer is hardcoded specifically to integrate with Ollama and LM Studio as its supported inference backends.  Because vLLM typically runs via Docker containers or custom Python environments on Linux/DGX systems rather than desktop application runtimes, PAIR's native UI and auto-discovery features cannot control or manage it directly.  WorkaroundsAdvanced users looking to route traffic to a vLLM backend have bypassed this limitation by manually editing PAIR's internal, declarative JSON manifests and overriding configuration files (such as mapping health probes to vLLM's /v1/models endpoint). However, because this requires tricking the router into treating a custom endpoint as a supported service, it is entirely unofficial and prone to breaking with updates.  If you want a seamless, natively supported plug-and-play experience with PAIR, you will need to use Ollama or LM Studio.  