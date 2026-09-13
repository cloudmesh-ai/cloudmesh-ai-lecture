---
title: "StopWatch"
---

Often you find yourself in a situation where you like to measure the time between two events. We provide a simple `StopWatch` that allows you not only to measure a number of times but also to print them out in a convenient format.

The `cloudmesh.common.StopWatch` module provides a robust mechanism for measuring execution time, managing benchmarks, and logging progress in Python applications. It is particularly useful for researchers and developers working in high-performance computing (HPC) and cloud environments.

### Basic Usage

The simplest way to use `StopWatch` is via the `start` and `stop` class methods. Timers are referenced by a unique string name.

```         
from cloudmesh.common.StopWatch import StopWatch
import time

# Start a named timer
StopWatch.start("data-processing")

# Perform your task
time.sleep(0.5)

# Stop the timer
StopWatch.stop("data-processing")

# Retrieve the elapsed time (in seconds)
elapsed = StopWatch.get("data-processing")
print(f"Time taken: {elapsed}s")
```

To print a summary of the results instead of a specific value, you can simply also use:

``` python
StopWatch.benchmark()
```

For more features, please see [StopWatch](https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.common.html?highlight=stopwatch#module-cloudmesh.common.StopWatch)

### The Context Manager (`StopWatchBlock`)

For smaller blocks of code, the `StopWatchBlock` provides a cleaner `with` statement interface. This ensures the timer is automatically stopped even if an exception occurs.

```         
from cloudmesh.common.StopWatch import StopWatchBlock

with StopWatchBlock("total-runtime"):
    # Code to benchmark
    time.sleep(1.0)
```

**Advanced Logging with Context Blocks:**

You can also log timing data directly to a file and include custom metadata.

```         
metadata = {"iteration": 1, "threshold": 0.05}

with StopWatchBlock("io-operation", data=metadata, log="benchmark.log", mode="a"):
    # Perform file writing or networking
    time.sleep(0.2)
```

### Decorators for Automated Benchmarking

If you want to benchmark entire functions, you can use the `@benchmark` decorator. This automatically creates a timer using the function's name.

```         
from cloudmesh.common.StopWatch import benchmark

@benchmark
def expensive_computation():
    time.sleep(1.5)

expensive_computation()
# A timer named "expensive_computation" is now stored in StopWatch
```

### Reporting and System Information

One of the most powerful features of `StopWatch` is its ability to generate formatted benchmark tables that include system metadata (OS, node name, CPU info). Without parameters it prints the default table. However you can also customize the columns and select the specific result

```         
StopWatch.benchmark(
    tag="experiment-v1",
    user="gregor",
    node="workstation-01",
    sysinfo=True
)
```

#### Key Parameters for `benchmark()`:

|  |  |  |
|----|----|----|
| **Parameter** | **Type** | **Description** |
| `sysinfo` | bool | If `True`, includes a table of system hardware and OS details. |
| `csv` | bool | If `True`, prints a machine-readable CSV version of the data. |
| `total` | bool | Calculates and prints the sum of all recorded timers. |
| `filename` | str | Saves the entire benchmark output to the specified file. |

### Managing Cumulative Timers

If you run a timer inside a loop, `StopWatch` tracks both the most recent duration and the cumulative sum.

```         
for i in range(5):
    StopWatch.start("loop-step")
    time.sleep(0.1)
    StopWatch.stop("loop-step")

print(f"Last duration: {StopWatch.get('loop-step')}s")
print(f"Total duration: {StopWatch.sum('loop-step')}s")
```

### Progress Tracking

The `progress()` function creates standardized log entries for monitoring long-running tasks, compatible with SLURM and LSF job IDs. It is used to write the result to STDOUT so you can include them in logg files that you can then parse.

```         
from cloudmesh.common.StopWatch import progress

progress(status="processing", progress=50, filename="job.progress")
# Output: 
# cloudmesh status=processing progress=50 pid=1234 time='2026-03-24 16:32:43'
```