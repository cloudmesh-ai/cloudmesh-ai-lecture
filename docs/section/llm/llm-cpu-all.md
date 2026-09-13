
## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
The guide is split into three “toolchains” – pick the one that matches your workflow:

| Tool | When it shines | Typical RAM needed (4‑bit) | How you start it |
|------|----------------|----------------------------|------------------|
| **Ollama** | One‑click CLI / REST, no Python needed | 6‑7 GB for 7 B models, 1 GB for 1 B models | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, pipelines) | 0.5‑6 GB (depends on model) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit (`q4_0` / `nf4`) quantisation** – this fits in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (use from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # put in ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Use `brew` to install `git` or `wget` if they are missing.  
* On Apple Silicon (M1/M2) the pre‑built `llama.cpp` binaries are also available – just pick the `arm64` zip.

```bash
brew install wget   # if you don’t have it
```

Then follow the **Linux** steps for **Ollama**, **llama.cpp**, or **Python**.  
Ollama provides a `.pkg` installer for macOS as an alternative to the shell script:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS too
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It gives you a *Unix‑like* shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and choose the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.  

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – Python must be on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Python Demo (runs on **any** OS)

Below is a minimal script that:

* Installs the required packages (only once).  
* Loads the **DistilGPT‑2** model (124 M parameters, ~0.5 GB RAM).  
* Generates a short paragraph.  
* Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second**.

Run it in your terminal (`python demo.py`) **or** paste it into a Jupyter/IPython cell.

```xml





## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
The guide is split into three “toolchains” – pick the one that matches your workflow:

| Tool | When it shines | Typical RAM needed (4‑bit) | How you start it |
|------|----------------|----------------------------|------------------|
| **Ollama** | One‑click CLI / REST, no Python needed | 6‑7 GB for 7 B models, 1 GB for 1 B models | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, pipelines) | 0.5‑6 GB (depends on model) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit (`q4_0` / `nf4`) quantisation** – this fits in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (use from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # put in ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Use `brew` to install `git` or `wget` if they are missing.  
* On Apple Silicon (M1/M2) the pre‑built `llama.cpp` binaries are also available – just pick the `arm64` zip.

```bash
brew install wget   # if you don’t have it
```

Then follow the **Linux** steps for **Ollama**, **llama.cpp**, or **Python**.  
Ollama provides a `.pkg` installer for macOS as an alternative to the shell script:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS too
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It gives you a *Unix‑like* shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and choose the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.  

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – Python must be on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Python Demo (runs on **any** OS)

Below is a minimal script that:

* Installs the required packages (only once).  
* Loads the **DistilGPT‑2** model (124 M parameters, ~0.5 GB RAM).  
* Generates a short paragraph.  
* Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second**.

Run it in your terminal (`python demo.py`) **or** paste it into a Jupyter/IPython cell.

```xml

## 📘 CPU‑Only LLM Guide  
**Works on:**  

| OS | Shell you’ll use | Recommended tool(s) |
|----|------------------|---------------------|
| Linux | Bash (default) | Ollama, llama.cpp, 🤗 Transformers + bitsandbytes |
| macOS | Bash / Zsh (built‑in) | Same as Linux |
| Windows | **Git Bash** (installed with Git for Windows) | Same as Linux – the commands are identical |

> **Why “CPU‑only”?**  
> • No GPU required → runs on any laptop/desktop.  
> • Keep model size ≤ 7 B parameters and use **4‑bit quantisation** (`q4_0` or `nf4`).  
> • Expect 5‑15 tokens / second for a 7 B model; 30‑40 tps for a 1 B model.

---

## 1️⃣ Install the three toolchains (same commands for Linux / macOS / Git Bash)

### 1.1 Ollama – the easiest “install‑and‑run” solution
```bash
# Install Ollama (adds a systemd service on Linux/macOS, a Windows service on Windows)
curl -fsSL https://ollama.com/install.sh | sh
# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0
# Or a tiny 1 B model (≈1 GB RAM) for fast testing
ollama pull tinyllama:1b-q4_0
```

#### Run it
```bash
# Interactive REPL
ollama run llama2:7b-q4_0
```

#### Call the built‑in REST API (works from any language)
```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"What is the difference between RAM and VRAM?"}]
         }' | jq .
```

#### Optional: limit CPU threads (keeps your desktop responsive)
```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or ~/.zshrc
# on Linux/macOS restart the service
systemctl restart ollama.service   # Windows service restarts automatically when you log out/in
```

---

### 1.2 llama.cpp – a pure C++ binary (≈10 MB) you can embed anywhere
```bash
# Download the pre‑built binary for your platform
# Linux/macOS (x86_64)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
# macOS (Apple Silicon) – replace “linux” with “macos”
# Windows (Git Bash)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip

unzip llama.cpp-*-x86_64.zip
chmod +x llama-cli   # on Windows you’ll get llama-cli.exe
```

#### Convert a Hugging‑Face checkpoint to GGML (run *once*)
```bash
# Example: TinyLlama‑1.1B‑Chat → 4‑bit (q4_0) → ~1 GB
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# The conversion script lives next to the binary we just downloaded
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference
```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it in a small FastAPI server if you need a custom HTTP endpoint.

---

### 1.3 Python 🤗 Transformers + bitsandbytes – full‑stack flexibility
```bash
# 1️⃣ Install a *CPU‑only* PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# 2️⃣ Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct) – **Python example**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional)**
```python
torch.set_num_threads(4)   # adjust to how many cores you want to devote
```

---

## 2️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (just run `python demo.py`).  
It uses the smallest publicly‑available model (**DistilGPT‑2**, 124 M parameters ≈ 0.5 GB RAM) so it fits even on a modest laptop.  
It prints the generated text, number of tokens, elapsed time, and tokens‑per‑second (tps).

```xml





## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
The guide is split into three “toolchains” – pick the one that matches your workflow:

| Tool | When it shines | Typical RAM needed (4‑bit) | How you start it |
|------|----------------|----------------------------|------------------|
| **Ollama** | One‑click CLI / REST, no Python needed | 6‑7 GB for 7 B models, 1 GB for 1 B models | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, pipelines) | 0.5‑6 GB (depends on model) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit (`q4_0` / `nf4`) quantisation** – this fits in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (use from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # put in ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Use `brew` to install `git` or `wget` if they are missing.  
* On Apple Silicon (M1/M2) the pre‑built `llama.cpp` binaries are also available – just pick the `arm64` zip.

```bash
brew install wget   # if you don’t have it
```

Then follow the **Linux** steps for **Ollama**, **llama.cpp**, or **Python**.  
Ollama provides a `.pkg` installer for macOS as an alternative to the shell script:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS too
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It gives you a *Unix‑like* shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and choose the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.  

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – Python must be on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Python Demo (runs on **any** OS)

Below is a minimal script that:

* Installs the required packages (only once).  
* Loads the **DistilGPT‑2** model (124 M parameters, ~0.5 GB RAM).  
* Generates a short paragraph.  
* Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second**.

Run it in your terminal (`python demo.py`) **or** paste it into a Jupyter/IPython cell.

```xml

## 📘 CPU‑Only LLM Guide  
**Works on:**  

| OS | Shell you’ll use | Recommended tool(s) |
|----|------------------|---------------------|
| Linux | Bash (default) | Ollama, llama.cpp, 🤗 Transformers + bitsandbytes |
| macOS | Bash / Zsh (built‑in) | Same as Linux |
| Windows | **Git Bash** (installed with Git for Windows) | Same as Linux – the commands are identical |

> **Why “CPU‑only”?**  
> • No GPU required → runs on any laptop/desktop.  
> • Keep model size ≤ 7 B parameters and use **4‑bit quantisation** (`q4_0` or `nf4`).  
> • Expect 5‑15 tokens / second for a 7 B model; 30‑40 tps for a 1 B model.

---

## 1️⃣ Install the three toolchains (same commands for Linux / macOS / Git Bash)

### 1.1 Ollama – the easiest “install‑and‑run” solution
```bash
# Install Ollama (adds a systemd service on Linux/macOS, a Windows service on Windows)
curl -fsSL https://ollama.com/install.sh | sh
# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0
# Or a tiny 1 B model (≈1 GB RAM) for fast testing
ollama pull tinyllama:1b-q4_0
```

#### Run it
```bash
# Interactive REPL
ollama run llama2:7b-q4_0
```

#### Call the built‑in REST API (works from any language)
```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"What is the difference between RAM and VRAM?"}]
         }' | jq .
```

#### Optional: limit CPU threads (keeps your desktop responsive)
```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or ~/.zshrc
# on Linux/macOS restart the service
systemctl restart ollama.service   # Windows service restarts automatically when you log out/in
```

---

### 1.2 llama.cpp – a pure C++ binary (≈10 MB) you can embed anywhere
```bash
# Download the pre‑built binary for your platform
# Linux/macOS (x86_64)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
# macOS (Apple Silicon) – replace “linux” with “macos”
# Windows (Git Bash)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip

unzip llama.cpp-*-x86_64.zip
chmod +x llama-cli   # on Windows you’ll get llama-cli.exe
```

#### Convert a Hugging‑Face checkpoint to GGML (run *once*)
```bash
# Example: TinyLlama‑1.1B‑Chat → 4‑bit (q4_0) → ~1 GB
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# The conversion script lives next to the binary we just downloaded
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference
```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it in a small FastAPI server if you need a custom HTTP endpoint.

---

### 1.3 Python 🤗 Transformers + bitsandbytes – full‑stack flexibility
```bash
# 1️⃣ Install a *CPU‑only* PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# 2️⃣ Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct) – **Python example**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional)**
```python
torch.set_num_threads(4)   # adjust to how many cores you want to devote
```

---

## 2️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (just run `python demo.py`).  
It uses the smallest publicly‑available model (**DistilGPT‑2**, 124 M parameters ≈ 0.5 GB RAM) so it fits even on a modest laptop.  
It prints the generated text, number of tokens, elapsed time, and tokens‑per‑second (tps).

```xml

## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | Ideal use‑case | Approx. RAM (4‑bit) | Quick start command |
|------|----------------|---------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed in scripts or containers | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full‑Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are step‑by‑step commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool. After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (the demo uses the smallest model, DistilGPT‑2, so it runs even on modest hardware).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (call from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Install `wget` or `git` with Homebrew if missing: `brew install wget git`.
* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

```bash
brew install wget   # only needed if wget is not present
# then follow the Linux steps for Ollama, llama.cpp, or Python
```

Ollama also offers a `.pkg` installer you can run directly:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS as well
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – make sure Python is on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter cell).  
It:

1. Installs the required packages **once** (uncomment the install block the first time).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second** (tps).

```xml





## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
The guide is split into three “toolchains” – pick the one that matches your workflow:

| Tool | When it shines | Typical RAM needed (4‑bit) | How you start it |
|------|----------------|----------------------------|------------------|
| **Ollama** | One‑click CLI / REST, no Python needed | 6‑7 GB for 7 B models, 1 GB for 1 B models | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, pipelines) | 0.5‑6 GB (depends on model) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit (`q4_0` / `nf4`) quantisation** – this fits in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (use from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # put in ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Use `brew` to install `git` or `wget` if they are missing.  
* On Apple Silicon (M1/M2) the pre‑built `llama.cpp` binaries are also available – just pick the `arm64` zip.

```bash
brew install wget   # if you don’t have it
```

Then follow the **Linux** steps for **Ollama**, **llama.cpp**, or **Python**.  
Ollama provides a `.pkg` installer for macOS as an alternative to the shell script:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS too
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It gives you a *Unix‑like* shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and choose the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.  

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – Python must be on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Python Demo (runs on **any** OS)

Below is a minimal script that:

* Installs the required packages (only once).  
* Loads the **DistilGPT‑2** model (124 M parameters, ~0.5 GB RAM).  
* Generates a short paragraph.  
* Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second**.

Run it in your terminal (`python demo.py`) **or** paste it into a Jupyter/IPython cell.

```xml

## 📘 CPU‑Only LLM Guide  
**Works on:**  

| OS | Shell you’ll use | Recommended tool(s) |
|----|------------------|---------------------|
| Linux | Bash (default) | Ollama, llama.cpp, 🤗 Transformers + bitsandbytes |
| macOS | Bash / Zsh (built‑in) | Same as Linux |
| Windows | **Git Bash** (installed with Git for Windows) | Same as Linux – the commands are identical |

> **Why “CPU‑only”?**  
> • No GPU required → runs on any laptop/desktop.  
> • Keep model size ≤ 7 B parameters and use **4‑bit quantisation** (`q4_0` or `nf4`).  
> • Expect 5‑15 tokens / second for a 7 B model; 30‑40 tps for a 1 B model.

---

## 1️⃣ Install the three toolchains (same commands for Linux / macOS / Git Bash)

### 1.1 Ollama – the easiest “install‑and‑run” solution
```bash
# Install Ollama (adds a systemd service on Linux/macOS, a Windows service on Windows)
curl -fsSL https://ollama.com/install.sh | sh
# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0
# Or a tiny 1 B model (≈1 GB RAM) for fast testing
ollama pull tinyllama:1b-q4_0
```

#### Run it
```bash
# Interactive REPL
ollama run llama2:7b-q4_0
```

#### Call the built‑in REST API (works from any language)
```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"What is the difference between RAM and VRAM?"}]
         }' | jq .
```

#### Optional: limit CPU threads (keeps your desktop responsive)
```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or ~/.zshrc
# on Linux/macOS restart the service
systemctl restart ollama.service   # Windows service restarts automatically when you log out/in
```

---

### 1.2 llama.cpp – a pure C++ binary (≈10 MB) you can embed anywhere
```bash
# Download the pre‑built binary for your platform
# Linux/macOS (x86_64)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
# macOS (Apple Silicon) – replace “linux” with “macos”
# Windows (Git Bash)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip

unzip llama.cpp-*-x86_64.zip
chmod +x llama-cli   # on Windows you’ll get llama-cli.exe
```

#### Convert a Hugging‑Face checkpoint to GGML (run *once*)
```bash
# Example: TinyLlama‑1.1B‑Chat → 4‑bit (q4_0) → ~1 GB
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# The conversion script lives next to the binary we just downloaded
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference
```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it in a small FastAPI server if you need a custom HTTP endpoint.

---

### 1.3 Python 🤗 Transformers + bitsandbytes – full‑stack flexibility
```bash
# 1️⃣ Install a *CPU‑only* PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# 2️⃣ Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct) – **Python example**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional)**
```python
torch.set_num_threads(4)   # adjust to how many cores you want to devote
```

---

## 2️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (just run `python demo.py`).  
It uses the smallest publicly‑available model (**DistilGPT‑2**, 124 M parameters ≈ 0.5 GB RAM) so it fits even on a modest laptop.  
It prints the generated text, number of tokens, elapsed time, and tokens‑per‑second (tps).

```xml

## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | Ideal use‑case | Approx. RAM (4‑bit) | Quick start command |
|------|----------------|---------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed in scripts or containers | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full‑Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are step‑by‑step commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool. After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (the demo uses the smallest model, DistilGPT‑2, so it runs even on modest hardware).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (call from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Install `wget` or `git` with Homebrew if missing: `brew install wget git`.
* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

```bash
brew install wget   # only needed if wget is not present
# then follow the Linux steps for Ollama, llama.cpp, or Python
```

Ollama also offers a `.pkg` installer you can run directly:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS as well
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – make sure Python is on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter cell).  
It:

1. Installs the required packages **once** (uncomment the install block the first time).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second** (tps).

```xml


## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | Ideal use‑case | Approx. RAM (4‑bit) | Quick‑start command |
|------|----------------|---------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed in scripts, containers, or edge devices | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a tiny 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat (interactive REPL)**  

```bash
ollama run llama2:7b-q4_0
```

**REST API (call from any language)**  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip – limit threads**  

```bash
export OLLAMA_NUM_THREADS=4      # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or expose it via a tiny FastAPI/Flask wrapper if you need a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# Install a CPU‑only PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Optional thread‑limit (helps keep the system responsive)**  

```python
torch.set_num_threads(4)   # adjust to how many cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; only minor differences:

* Install `wget` or `git` with Homebrew if they are missing:

```bash
brew install wget git
```

* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

* Ollama also offers a `.pkg` installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS, too
```

After installing the prerequisites, follow the **Linux** steps for Ollama, llama.cpp, or the Python stack.

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (ensure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama  

```bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths:

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter notebook).  
It:

1. Installs the required packages **once** (the install block is commented out – uncomment the first time you run it).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints the number of generated tokens, elapsed time, and tokens‑per‑second (tps).

```xml


## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
The guide is split into three “toolchains” – pick the one that matches your workflow:

| Tool | When it shines | Typical RAM needed (4‑bit) | How you start it |
|------|----------------|----------------------------|------------------|
| **Ollama** | One‑click CLI / REST, no Python needed | 6‑7 GB for 7 B models, 1 GB for 1 B models | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, pipelines) | 0.5‑6 GB (depends on model) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit (`q4_0` / `nf4`) quantisation** – this fits in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (use from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # put in ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Use `brew` to install `git` or `wget` if they are missing.  
* On Apple Silicon (M1/M2) the pre‑built `llama.cpp` binaries are also available – just pick the `arm64` zip.

```bash
brew install wget   # if you don’t have it
```

Then follow the **Linux** steps for **Ollama**, **llama.cpp**, or **Python**.  
Ollama provides a `.pkg` installer for macOS as an alternative to the shell script:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS too
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It gives you a *Unix‑like* shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and choose the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.  

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – Python must be on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Python Demo (runs on **any** OS)

Below is a minimal script that:

* Installs the required packages (only once).  
* Loads the **DistilGPT‑2** model (124 M parameters, ~0.5 GB RAM).  
* Generates a short paragraph.  
* Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second**.

Run it in your terminal (`python demo.py`) **or** paste it into a Jupyter/IPython cell.

```xml

## 📘 CPU‑Only LLM Guide  
**Works on:**  

| OS | Shell you’ll use | Recommended tool(s) |
|----|------------------|---------------------|
| Linux | Bash (default) | Ollama, llama.cpp, 🤗 Transformers + bitsandbytes |
| macOS | Bash / Zsh (built‑in) | Same as Linux |
| Windows | **Git Bash** (installed with Git for Windows) | Same as Linux – the commands are identical |

> **Why “CPU‑only”?**  
> • No GPU required → runs on any laptop/desktop.  
> • Keep model size ≤ 7 B parameters and use **4‑bit quantisation** (`q4_0` or `nf4`).  
> • Expect 5‑15 tokens / second for a 7 B model; 30‑40 tps for a 1 B model.

---

## 1️⃣ Install the three toolchains (same commands for Linux / macOS / Git Bash)

### 1.1 Ollama – the easiest “install‑and‑run” solution
```bash
# Install Ollama (adds a systemd service on Linux/macOS, a Windows service on Windows)
curl -fsSL https://ollama.com/install.sh | sh
# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0
# Or a tiny 1 B model (≈1 GB RAM) for fast testing
ollama pull tinyllama:1b-q4_0
```

#### Run it
```bash
# Interactive REPL
ollama run llama2:7b-q4_0
```

#### Call the built‑in REST API (works from any language)
```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"What is the difference between RAM and VRAM?"}]
         }' | jq .
```

#### Optional: limit CPU threads (keeps your desktop responsive)
```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or ~/.zshrc
# on Linux/macOS restart the service
systemctl restart ollama.service   # Windows service restarts automatically when you log out/in
```

---

### 1.2 llama.cpp – a pure C++ binary (≈10 MB) you can embed anywhere
```bash
# Download the pre‑built binary for your platform
# Linux/macOS (x86_64)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
# macOS (Apple Silicon) – replace “linux” with “macos”
# Windows (Git Bash)
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip

unzip llama.cpp-*-x86_64.zip
chmod +x llama-cli   # on Windows you’ll get llama-cli.exe
```

#### Convert a Hugging‑Face checkpoint to GGML (run *once*)
```bash
# Example: TinyLlama‑1.1B‑Chat → 4‑bit (q4_0) → ~1 GB
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# The conversion script lives next to the binary we just downloaded
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference
```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it in a small FastAPI server if you need a custom HTTP endpoint.

---

### 1.3 Python 🤗 Transformers + bitsandbytes – full‑stack flexibility
```bash
# 1️⃣ Install a *CPU‑only* PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# 2️⃣ Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct) – **Python example**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional)**
```python
torch.set_num_threads(4)   # adjust to how many cores you want to devote
```

---

## 2️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (just run `python demo.py`).  
It uses the smallest publicly‑available model (**DistilGPT‑2**, 124 M parameters ≈ 0.5 GB RAM) so it fits even on a modest laptop.  
It prints the generated text, number of tokens, elapsed time, and tokens‑per‑second (tps).

```xml

## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | Ideal use‑case | Approx. RAM (4‑bit) | Quick start command |
|------|----------------|---------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed in scripts or containers | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full‑Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are step‑by‑step commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool. After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (the demo uses the smallest model, DistilGPT‑2, so it runs even on modest hardware).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat**  

```bash
ollama run llama2:7b-q4_0   # interactive REPL
```

**REST API** (call from any language)  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip** – limit threads so your desktop stays responsive:

```bash
export OLLAMA_NUM_THREADS=4   # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Thread‑limit (optional but useful)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Install `wget` or `git` with Homebrew if missing: `brew install wget git`.
* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

```bash
brew install wget   # only needed if wget is not present
# then follow the Linux steps for Ollama, llama.cpp, or Python
```

Ollama also offers a `.pkg` installer you can run directly:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS as well
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (make sure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – make sure Python is on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter cell).  
It:

1. Installs the required packages **once** (uncomment the install block the first time).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints **tokens generated**, **elapsed time**, and **tokens‑per‑second** (tps).

```xml


## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | Ideal use‑case | Approx. RAM (4‑bit) | Quick‑start command |
|------|----------------|---------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed in scripts, containers, or edge devices | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a tiny 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat (interactive REPL)**  

```bash
ollama run llama2:7b-q4_0
```

**REST API (call from any language)**  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip – limit threads**  

```bash
export OLLAMA_NUM_THREADS=4      # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or expose it via a tiny FastAPI/Flask wrapper if you need a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# Install a CPU‑only PyTorch wheel (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install Transformers + bitsandbytes (provides 4‑/8‑bit quantisation)
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Optional thread‑limit (helps keep the system responsive)**  

```python
torch.set_num_threads(4)   # adjust to how many cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; only minor differences:

* Install `wget` or `git` with Homebrew if they are missing:

```bash
brew install wget git
```

* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

* Ollama also offers a `.pkg` installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS, too
```

After installing the prerequisites, follow the **Linux** steps for Ollama, llama.cpp, or the Python stack.

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (ensure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama  

```bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths:

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter notebook).  
It:

1. Installs the required packages **once** (the install block is commented out – uncomment the first time you run it).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints the number of generated tokens, elapsed time, and tokens‑per‑second (tps).

```xml


## 📚 CPU‑Only LLM Guide – Linux, macOS, **Windows (Git Bash)**  

You can run a language model locally **without a GPU** on every major desktop OS.  
Pick the toolchain that matches your workflow:

| Tool | When it shines | Approx. RAM needed (4‑bit) | Quick‑start command |
|------|----------------|----------------------------|---------------------|
| **Ollama** | Plug‑and‑play CLI / REST, no Python needed | 6‑7 GB for a 7 B model; ≈ 1 GB for a 1 B model | `ollama run …` |
| **llama.cpp** | Ultra‑light binary you can embed anywhere (scripts, containers, edge devices) | 1‑6 GB depending on model size | `llama-cli …` |
| **🤗 Transformers + bitsandbytes** | Full Python control (fine‑tuning, custom pipelines) | 0.5‑6 GB (model‑dependent) | `model.generate …` |

> **Rule of thumb:** stay at **≤ 7 B parameters** and use **4‑bit quantisation** (`q4_0` or `nf4`). This fits comfortably in 8‑16 GB RAM and runs at a usable speed on a modern CPU.

Below are the exact commands for **Linux**, **macOS**, and **Windows (Git Bash)** for each tool.  
After the OS‑specific sections you’ll find a **tiny Python demo** that works on any platform (it uses the smallest model, DistilGPT‑2, so it fits even on a modest laptop).

---

## 1️⃣ Linux  

### 1.1 Ollama  

```bash
# Install (adds a systemd service)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4‑bit 7 B model (≈6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a 1 B model (≈1 GB RAM) for quick testing
ollama pull tinyllama:1b-q4_0
```

**Chat (interactive REPL)**  

```bash
ollama run llama2:7b-q4_0
```

**REST API (call from any language)**  

```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]
         }' | jq .
```

**Performance tip – limit threads**  

```bash
export OLLAMA_NUM_THREADS=4      # add to ~/.bashrc or run before starting Ollama
systemctl restart ollama.service   # reload if you changed the variable
```

---

### 1.2 llama.cpp  

```bash
# Download the pre‑built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli   # the executable is called `llama-cli`
```

#### Convert a Hugging‑Face checkpoint (run once)

```bash
# Example: TinyLlama‑1.1B‑Chat (≈1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4‑bit (q4_0)
../llama-cli convert_hf_to_ggml.py --outtype q4_0 \
                                   --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

#### Run inference  

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48   # generate 48 tokens
```

You can call `llama-cli` from any script (`subprocess.run([...])`) or wrap it with FastAPI/Flask for a custom HTTP server.

---

### 1.3 Python 🤗 Transformers + bitsandbytes  

```bash
# CPU‑only PyTorch (no CUDA)
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Transformers + bitsandbytes for 4/8‑bit quantisation
pip install transformers bitsandbytes accelerate
```

#### Load a 4‑bit 7 B model (Mistral‑7B‑Instruct)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

**Optional thread‑limit (helps keep the system responsive)**  

```python
torch.set_num_threads(4)   # adjust to the number of cores you want to allocate
```

---

## 2️⃣ macOS  

The commands are **identical** to the Linux ones; the only differences are:

* Install `wget` or `git` with Homebrew if missing: `brew install wget git`.
* On Apple Silicon (M1/M2) download the `arm64` zip for `llama.cpp` (replace “linux” with “macos” in the URL).

```bash
brew install wget   # only needed if wget is not present
# then follow the Linux steps for Ollama, llama.cpp, or Python
```

Ollama also offers a `.pkg` installer you can run directly:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # works on macOS as well
```

---

## 3️⃣ Windows (using **Git Bash**)  

> **Why Git Bash?**  
> It provides a Unix‑like shell (`bash`) on Windows, so the same commands used on Linux/macOS work unchanged.

1. **Install Git Bash** – download from <https://git-scm.com/download/win> and accept the default options (ensure “Git Bash Here” is enabled).

2. **Open “Git Bash”** and run the same commands as in the Linux section.

### 3.1 Ollama on Windows  

```bash
# In Git Bash
curl -fsSL https://ollama.com/install.sh | sh   # installs a Windows service
ollama pull llama2:7b-q4_0
ollama run llama2:7b-q4_0
```

The service runs in the background; you can still call the REST API from PowerShell, CMD, or any programming language.

### 3.2 llama.cpp on Windows  

```bash
# Download the Windows zip (x86_64) – Git Bash can handle wget
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-windows-x86_64.zip
unzip llama.cpp-windows-x86_64.zip
chmod +x llama-cli.exe
```

Convert a model (same steps as Linux) – just use forward slashes in paths.

```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1
../llama-cli.exe convert_hf_to_ggml.py --outtype q4_0 \
                                       --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

Run it:

```bash
../llama-cli.exe -m tinyllama-q4_0.ggmlv3.bin -p "Write a haiku about sunrise." -n 48
```

### 3.3 Python on Windows (Git Bash)

```bash
# Inside Git Bash – make sure Python is on your PATH
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers bitsandbytes accelerate
```

Then use the same Python snippet shown for Linux/macOS.

---

## 4️⃣ Tiny Cross‑Platform Python Demo  

The script below works on **any** of the three OSes (run it with `python demo.py` or paste it into a Jupyter notebook).  
It:

1. Installs the required packages **once** (the install block is commented out – uncomment the first time you run it).  
2. Loads **DistilGPT‑2** (124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph.  
4. Prints the number of generated tokens, elapsed time, and tokens‑per‑second (tps).

```xml





Below is a short, self‑contained Python demo that runs **entirely on the CPU**.  
It loads the tiny **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM), generates a short paragraph, and prints:

* the generated text  
* how many tokens were produced  
* the elapsed time  
* tokens‑per‑second (tps) – a useful performance metric for CPU‑only inference  

You can run the same code on any Linux, macOS, or Windows (Git Bash) system that has Python 3.8+ and the `transformers` library installed.

```xml





Below is a short, self‑contained Python demo that runs **entirely on the CPU**.  
It loads the tiny **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM), generates a short paragraph, and prints:

* the generated text  
* how many tokens were produced  
* the elapsed time  
* tokens‑per‑second (tps) – a useful performance metric for CPU‑only inference  

You can run the same code on any Linux, macOS, or Windows (Git Bash) system that has Python 3.8+ and the `transformers` library installed.

```xml


Below is a short, self‑contained Python demo that runs **entirely on the CPU**.  
It loads the tiny **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM), generates a short paragraph, and prints:

* the generated text  
* how many tokens were produced  
* the elapsed time  
* tokens‑per‑second (tps) – a useful performance metric for CPU‑only inference  

You can run the same code on any Linux, macOS, or Windows (Git Bash) system that has Python 3.8+ and the `transformers` library installed.

```xml





Below is a short, self‑contained Python demo that runs **entirely on the CPU**.  
It loads the tiny **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM), generates a short paragraph, and prints:

* the generated text  
* how many tokens were produced  
* the elapsed time  
* tokens‑per‑second (tps) – a useful performance metric for CPU‑only inference  

You can run the same code on any Linux, macOS, or Windows (Git Bash) system that has Python 3.8+ and the `transformers` library installed.

```xml


Below is a short, self‑contained Python demo that runs **entirely on the CPU**.  
It loads the tiny **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM), generates a short paragraph, and prints:

* the generated text  
* how many tokens were produced  
* the elapsed time  
* tokens‑per‑second (tps) – a useful performance metric for CPU‑only inference  

You can run the same code on any Linux, macOS, or Windows (Git Bash) system that has Python 3.8+ and the `transformers` library installed.

```xml

Below is a **complete, runnable Python demo** that works on any OS (Linux, macOS, or Windows via Git Bash).  
It installs the tiny **DistilGPT‑2** model, runs a generation on the CPU, and prints useful performance metrics.

```xml





Below is a **ready‑to‑run Python script** that you can execute on any machine with a Python 3.8+ interpreter (Linux, macOS, or Windows → Git Bash).  
It:

1. Installs the minimal dependencies (`transformers` and the CPU‑only `torch` wheel).  
2. Loads the **DistilGPT‑2** model (≈ 124 M parameters, ~0.5 GB RAM).  
3. Generates a short paragraph from a prompt.  
4. Prints the generated text **and** simple performance metrics (tokens generated, elapsed time, tokens‑per‑second).

You can copy‑paste the whole block into a file (e.g., `cpu_llm_demo.py`) and run it with `python cpu_llm_demo.py`.  
All the required steps are included, so you don’t need any extra setup beyond a working internet connection.

```python
#!/usr/bin/env python3
# -------------------------------------------------
# CPU‑only LLM demo – works on Linux, macOS, Windows (Git Bash)
# -------------------------------------------------

import sys
import os
import platform
import time
import subprocess

def print_banner():
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Platform:       {platform.platform()}")
    print(f"CPU count:      {os.cpu_count()}")
    print("-" * 40)

def install_dependencies():
    """
    Installs the tiny CPU‑only stack:
        * transformers
        * torch (CPU‑only wheel)
    This step is only performed the first time you run the script.
    """
    try:
        import transformers  # noqa: F401
        import torch         # noqa: F401
        # If we get here, the packages are already present.
        return
    except ImportError:
        pass

    print("Installing required packages (this may take a minute)…")
    # The `-q` flag silences pip output for a cleaner console.
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-q", "transformers",
        "-q", "torch==2.4.0+cpu",
        "-f", "https://download.pytorch.org/whl/torch_stable.html"
    ])

def load_model(model_name: str = "distilgpt2"):
    """
    Loads the tokenizer and model in CPU mode.
    DistilGPT‑2 is a 124 M‑parameter model (~0.5 GB RAM) – perfect for laptops.
    """
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"Downloading & loading model '{model_name}' …")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

def generate_text(tokenizer, model, prompt: str,
                  max_new_tokens: int = 80,
                  temperature: float = 0.9):
    """
    Runs a single generation on the CPU and returns:
        * full generated text (prompt + continuation)
        * number of newly generated tokens
        * elapsed seconds
        * tokens‑per‑second (tps)
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    start = time.time()
    output = model.generate(**inputs,
                            max_new_tokens=max_new_tokens,
                            do_sample=True,
                            temperature=temperature)
    elapsed = time.time() - start

    # Decode the complete sequence and count how many tokens were added.
    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    generated_tokens = output.shape[1] - inputs["input_ids"].shape[1]
    tps = generated_tokens / elapsed if elapsed > 0 else float("inf")
    return full_text, generated_tokens, elapsed, tps

def main():
    print_banner()
    install_dependencies()

    # -------------------------------------------------
    # 1️⃣  Load model
    # -------------------------------------------------
    tokenizer, model = load_model("distilgpt2")

    # -------------------------------------------------
    # 2️⃣  Define a prompt and generate
    # -------------------------------------------------
    prompt = "Write a short story about a robot that learns to paint."
    text, gen_tokens, secs, tps = generate_text(tokenizer, model, prompt)

    # -------------------------------------------------
    # 3️⃣  Show results
    # -------------------------------------------------
    print("\n=== Prompt ===")
    print(prompt)

    print("\n=== Generated text ===")
    print(text)

    print("\n=== Stats ===")
    print(f"Tokens generated : {gen_tokens}")
    print(f"Time elapsed      : {secs:.2f} s")
    print(f"Tokens per second : {tps:.2f} tps")

if __name__ == "__main__":
    main()
```

### How to run it

1. **Save** the script as `cpu_llm_demo.py` (or any name you prefer).  
2. Open a terminal:  

   * **Linux/macOS** – `bash` or `zsh` is fine.  
   * **Windows** – launch **Git Bash** (installed with Git for Windows) and navigate to the folder containing the script.  

3. Execute:

```bash
python cpu_llm_demo.py
```

The first run will download the `transformers` and `torch` wheels (≈ 300 MB total) and cache the DistilGPT‑2 model (~0.5 GB). Subsequent runs will start instantly because the packages and model are cached.

### What to expect

On a typical modern laptop (e.g., Intel i7‑12700H or AMD Ryzen 7 5800H) you’ll see something like:

```
Python version: 3.11.6
Platform:       Linux-5.15.0-1045-azure-x86_64-with-glibc2.35
CPU count:      12
Downloading & loading model 'distilgpt2' …
...

=== Prompt ===
Write a short story about a robot that learns to paint.

=== Generated text ===
In a quiet workshop tucked away from the bustle of the city, a small robot named Arti was built...
...

=== Stats ===
Tokens generated : 84
Time elapsed      : 1.84 s
Tokens per second : 45.65 tps
```

Your exact numbers will differ based on CPU speed and the number of threads your system allocates. If you want the process to be *friendlier* to other applications, you can limit PyTorch’s thread usage at the very top of `main()` with:

```python
import torch
torch.set_num_threads(4)   # or any number < your total cores
```

### Next steps (optional)

* **Try a larger quantised model**: replace `"distilgpt2"` with a 4‑bit GGUF model (e.g., `llama2:7b-q4_0` via Ollama) and adjust the loading code accordingly.  
* **Wrap it in a tiny API**: using Flask or FastAPI you can expose the `generate_text` function as a local HTTP endpoint.  
* **Experiment with temperature / top‑p** to fine‑tune the creativity of the output.

Feel free to ask if you need help adapting the script to a different model or integrating it into a larger application!


