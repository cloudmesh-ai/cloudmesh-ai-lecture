# cloudmesh-ai-common

The `cloudmesh-ai-common` library is the foundational layer for the Cloudmesh AI ecosystem. It provides a standardized set of shared utilities for system introspection, structured telemetry, configuration management, and remote execution, ensuring consistency across all AI components.

## Learning Objectives

By the end of this chapter, you will be able to:
- Manage complex, nested configurations using `DotDict` and `FlatDict`.
- Execute shell commands and transfer files on remote hosts using `RemoteExecutor`.
- Perform system introspection to detect hardware capabilities and OS environment.
- Implement structured telemetry to record and aggregate performance metrics.
- Manage local shell operations and administrative privileges using `Shell` and `Sudo`.
- Utilize general helpers for I/O, GitHub integration, and performance benchmarking.

---

## 0. Prerequisits

Install cloudmesh-ai-commom in a python virtual envirnment with  

```bash
pip install cloudmesh-ai-common
```

## 1. Configuration Management

AI projects often require deeply nested configurations. `cloudmesh-ai-common` provides three distinct tools depending on whether you need easy access, flat representation, or file-based management.

### Comparison: DotDict vs. FlatDict vs. Config

| Feature | `DotDict` | `FlatDict` | `Config` |
| :--- | :--- | :--- | :--- |
| **Core Nature** | A "Smart" Dictionary | A "Flattening" Utility | A Configuration Manager |
| **Primary Goal** | **Easy Access**: Avoid `dict['a']['b']`. | **Simple Representation**: Flat keys. | **Lifecycle**: Load, validate, and save. |
| **Key Strength** | Attribute access (`config.a.b`). | External expansion (`{os.HOME}`). | YAML file and Env Var integration. |
| **Use Case** | Clean access to nested data. | Mapping to env vars/external vars. | Persistent config files. |

### DotDict: Attribute-Style Access
`DotDict` allows accessing nested values using dot notation. It also supports `merge()` for recursive updates and `smart_get()` for searching keys recursively.

```python
from cloudmesh.ai.common.dotdict import DotDict

data = {"cloudmesh": {"ai": {"server": "uva", "port": 8000}}}
config = DotDict(data)

# Access via attribute or dot-notation key
print(config.cloudmesh.ai.server)      # 'uva'
print(config["cloudmesh.ai.port"])     # 8000

# Assignment auto-creates nested structures
config["cloudmesh.ai.timeout"] = 30
print(config.cloudmesh.ai.timeout)     # 30
```

### FlatDict: Flattening and Expansion
`FlatDict` turns nested structures into flat maps (e.g., `{"a.b.c": 1}`). Its most powerful feature is `expand_config_parameters`, which supports:
- **Internal**: `{key}` replaced by another value in the dict.
- **OS Env**: `{os.VARIABLE}` replaced by system environment variables.
- **Cloudmesh**: `{cm.VAR}` replaced by Cloudmesh registry.
- **Math**: `eval(1 + 1)` replaced by the result.

```python
from cloudmesh.ai.common.flatdict import FlatDict

data = {
    "user": "grey",
    "home": "{os.HOME}",
    "path": "{home}/models/{user}",
    "nodes": "eval(2 * 4)"
}
flat = FlatDict(data)
flat.load(content=data, expand=True)

print(flat.path)  # '/home/grey/models/grey' (assuming HOME is /home/grey)
print(flat.nodes)  # '8'
```

### The Config Class: File-Based Management
The `Config` class is a high-level wrapper that manages the lifecycle of a configuration file (typically YAML). It handles loading from disk, applying `DEFAULTS`, and allowing environment variables to override specific values.

```python
from cloudmesh.ai.common.config import Config

class MyAIConfig(Config):
    # Default values if not found in YAML or Env
    DEFAULTS = {"telemetry": {"enabled": True, "level": "INFO"}}
    # Type validation schema
    SCHEMA = {"telemetry.enabled": {"type": bool}}

# Loads from ~/.config/cloudmesh/cmc.yaml by default
config = MyAIConfig()

# Priority: Env Var (AI_TELEMETRY_ENABLED) -> YAML File -> DEFAULTS
enabled = config.get("telemetry.enabled")

# Update and save back to file
config.set("telemetry.level", "DEBUG")
config.save()
```

---

## 2. Unified Remote Execution

The `RemoteExecutor` provides a high-level wrapper around SSH and SFTP, designed to be used as a context manager.

### Basic Command Execution
```python
from cloudmesh.ai.common.remote import RemoteExecutor

host = "dgx-node-1"
with RemoteExecutor(host) as executor:
    result = executor.execute("nvidia-smi")
    print(f"Exit Code: {result.exit_code}")
    print(f"Stdout: {result.stdout}")
```

### Live Streaming and File Transfers
For long-running tasks, `monitor_output=True` streams output in real-time.

```python
from cloudmesh.ai.common.remote import RemoteExecutor
from pathlib import Path

host = "dgx-node-1"
with RemoteExecutor(host, monitor_output=True) as executor:
    # Live stream a training script
    executor.execute("bash long_training_script.sh")
    
    # Upload and Download
    executor.upload(Path("local_config.yaml"), "/home/user/remote_config.yaml")
    executor.download("/home/user/training.log", Path("local_training.log"))
```

---

## 3. System Introspection

The `sys` module provides cross-platform tools to detect hardware and OS environments.

### OS and Hardware Detection
```python
from cloudmesh.ai.common.sys import os_is_linux, systeminfo, has_window_manager

if os_is_linux():
    print("Running on Linux")

info = systeminfo()
print(f"CPU: {info.get('cpu')}")
print(f"Total Memory: {info.get('memory_total')}")

if has_window_manager():
    print("GUI environment detected.")
```

---

## 4. Telemetry and Aggregation

Telemetry is used to record performance metrics (e.g., inference latency) and system state.

### Recording Metrics
```python
from cloudmesh.ai.common.telemetry import Telemetry

t = Telemetry(backend="sqlite", path="telemetry.db")

# Emit a simple metric
t.emit(metric="inference_latency", value=0.125, status="completed")

# Emit multiple metrics
t.emit(metrics={"tokens_per_sec": 45.2, "gpu_util": 88}, status="completed")
```

### Analyzing Data with Aggregator
The `TelemetryAggregator` transforms raw records into statistical summaries.

```python
from cloudmesh.ai.common.aggregation import TelemetryAggregator

agg = TelemetryAggregator("telemetry.db")
summary = agg.get_summary()
print(f"Success Rate: {summary['success_rate']}")

# Aggregate specific metric
stats = agg.aggregate_metric("inference_latency")
print(f"Average Latency: {stats['avg']}")
```

---

## 5. Shell and Security

`Shell` and `Sudo` simplify local system operations and administrative tasks.

### Local Shell Execution
```python
from cloudmesh.ai.common.Shell import Shell

# Capture output
output = Shell.run("ls -la")

# Live output to console
Shell.live("ping -c 4 google.com")

# Open URL in browser
Shell.browser("https://github.com/cloudmesh-ai/cloudmesh-ai-common")
```

### Privileged Operations
The `Sudo` class handles password caching and root-level file access.

```python
from cloudmesh.ai.common.sudo import Sudo

# Execute privileged command
result = Sudo.execute("apt-get update")

# Read/Write restricted files
content = Sudo.readfile("/etc/shadow")
Sudo.writefile("/etc/hostname", "ai-node-01")
```

---

## 6. General Utilities

### I/O and Path Handling
```python
from cloudmesh.ai.common.io import path_expand, load_yaml, dump_yaml
from pathlib import Path

# Expand ~ and environment variables
path = path_expand("~/my_project/$VERSION/config.yaml")

# Safe YAML handling
config_path = Path("config.yaml")
data = load_yaml(config_path)
dump_yaml(config_path, data)
```

### Performance Tracking

The `StopWatch` utility is a thread-aware benchmarking suite. Each thread maintains its own set of timers using `threading.local()`, allowing for precise measurement of concurrent operations.

#### Core Timing Methods
- `StopWatch.start(name)`: Starts a timer.
- `StopWatch.stop(name)`: Stops a timer and records elapsed time.
- `StopWatch.get(name, precision=3)`: Returns the last recorded elapsed time for the timer.
- `StopWatch.sum(name, precision=3)`: Returns the total accumulated time spent in this timer across all calls.

```python
from cloudmesh.ai.common.stopwatch import StopWatch
import time

# Manual timing for a specific operation
StopWatch.start("data_load")
time.sleep(0.5) # Simulate loading
StopWatch.stop("data_load")

# Run it again to demonstrate accumulation
StopWatch.start("data_load")
time.sleep(0.7) # Simulate loading
StopWatch.stop("data_load")

# Get the last duration vs the total sum
last_run = StopWatch.get("data_load")
total_time = StopWatch.sum("data_load")

print(f"Last run: {last_run}s")   # Approx 0.7
print(f"Total time: {total_time}s") # Approx 1.2
```

#### Realistic AI Workflow Example

The following example demonstrates how to use `StopWatch` to profile a typical AI pipeline, including model loading, data preprocessing, and iterative inference.

```python
import time
import random
from cloudmesh.ai.common.stopwatch import StopWatch, benchmark

# 1. Use the @benchmark decorator for utility functions
@benchmark
def preprocess_data(item):
    """Simulates data cleaning and tokenization."""
    time.sleep(random.uniform(0.01, 0.05)) 

def run_ai_pipeline():
    # 2. Use StopWatch.timer with a specific name for a major phase
    with StopWatch.timer("Model Loading"):
        print("Loading LLM into GPU memory...")
        time.sleep(1.5) # Simulate heavy I/O
    
    # 3. Use StopWatch.timer WITHOUT a name
    # StopWatch will automatically name this timer 'run_ai_pipeline' 
    # because it detects the calling function name.
    with StopWatch.timer():
        print("Initializing pipeline...")
        time.sleep(0.2)

    # 4. Demonstrate Accumulation (Sum vs Get)
    print("Processing batch...")
    for i in range(5):
        # The 'inference' timer will be started and stopped 5 times.
        with StopWatch.timer("inference"):
            time.sleep(random.uniform(0.1, 0.3))
            preprocess_data(f"item_{i}")

    # --- Analyzing Results ---
    
    # get() returns the duration of the LAST inference call
    last_inf = StopWatch.get("inference")
    # sum() returns the TOTAL time spent across all 5 inference calls
    total_inf = StopWatch.sum("inference")
    
    print(f"\nLast inference: {last_inf}s")
    print(f"Total inference time for batch: {total_inf}s")

# Execute the pipeline
run_ai_pipeline()

# 5. Generate the final comprehensive benchmark report
StopWatch.benchmark(sysinfo=True)
```

**What this example demonstrates:**
- **`@benchmark`**: Automatically wraps `preprocess_data` to track every time it is called.
- **Automatic Naming**: The second `StopWatch.timer()` call doesn't have a name, so it uses the function name `run_ai_pipeline` automatically.
- **Accumulation**: By using the same name `"inference"` inside a loop, `StopWatch` tracks both the individual duration of the last call (`get`) and the cumulative time spent in that block (`sum`).
- **System Integration**: `StopWatch.benchmark(sysinfo=True)` prints a table that correlates these timings with the host's CPU and RAM specifications.

---


## Summary Checklist

- [ ] Can you access a nested dictionary value using dot notation with `DotDict`?
- [ ] Do you know how to expand environment variables in a `FlatDict`?
- [ ] Can you execute a remote command and stream its output using `RemoteExecutor`?
- [ ] Are you able to retrieve the current system's CPU and RAM using `systeminfo()`?
- [ ] Can you emit a performance metric using `Telemetry` and analyze it with `TelemetryAggregator`?
- [ ] Do you know how to execute a command with root privileges using `Sudo`?
- [ ] Can you benchmark a function using the `@benchmark` decorator?

## Practical Exercises

1. **Config Expansion**: Create a `FlatDict` with placeholders for your username and home directory, and expand them.
2. **Remote Monitor**: Write a script that connects to a remote host, runs `nvidia-smi`, and saves the output to a local file.
3. **Benchmarking Suite**: Create a function that simulates a heavy AI workload (e.g., a large loop) and use `StopWatch` to report the elapsed time.
4. **Telemetry Pipeline**: Implement a simple loop that emits a random "inference_time" metric every second for 10 seconds, then use `TelemetryAggregator` to find the average time.

