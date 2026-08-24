---
title: "Python Queues"
---

!!! info "Learning Outcomes"
    - Understand the purpose and implementation of thread-safe queues in Python.
    - Implement a producer-consumer pattern to handle asynchronous tasks.
    - Apply queue-based architectures to cloud computing scenarios, such as task distribution for VM management.

In a cloud environment, many operations—such as creating virtual machines, taking snapshots, or deploying containers—are time-consuming and should not block the main execution thread. Python's `queue` module provides a synchronized, thread-safe way to communicate between multiple threads.

The most commonly used class is `queue.Queue`, which implements a First-In, First-Out (FIFO) data structure.

## Implementing a Cloud Task Queue

Imagine a scenario where a cloud management tool needs to process a series of VM maintenance tasks without freezing the user interface. We can use a `Queue` to decouple the task submission from the task execution.

``` python
import queue
import threading
import time
import random

# Initialize a thread-safe queue
task_queue = queue.Queue()

def vm_worker():
    """Worker thread that processes VM tasks from the queue."""
    while True:
        # Get a task from the queue
        task = task_queue.get()
        if task is None:
            break
        
        vm_name, operation = task
        print(f"[Worker] Starting {operation} on {vm_name}...")
        # Simulate cloud API latency
        time.sleep(random.uniform(1, 3))
        print(f"[Worker] Completed {operation} on {vm_name}.")
        
        # Signal that the task is done
        task_queue.task_done()

# Start a worker thread
worker = threading.Thread(target=vm_worker, daemon=True)
worker.start()

# Simulate submitting cloud tasks
tasks = [
    ("vm-web-01", "Snapshot"),
    ("vm-db-01", "Backup"),
    ("vm-app-01", "Reboot"),
    ("vm-web-02", "Snapshot"),
]

for t in tasks:
    print(f"[Main] Queueing task: {t}")
    task_queue.put(t)

# Wait for all tasks in the queue to be processed
task_queue.join()
print("[Main] All cloud tasks processed.")
```

### Key Methods
- `put(item)`: Inserts an item into the queue.
- `get()`: Removes and returns an item from the queue. This call blocks by default until an item is available.
- `task_done()`: Signals that a formerly enqueued task is complete. Used by `join()`.
- `join()`: Blocks until all items in the queue have been gotten and processed.

!!! exercise "Asynchronous Resource Monitor"
    Write a Python program that simulates a cloud resource monitor. 
    1. Use a `queue.Queue` to store "Health Check" requests for a list of 5 VM names.
    2. Implement two worker threads that consume these requests and simulate a health check (e.g., checking if a port is open) by sleeping for a random duration.
    3. Ensure the main thread waits for all health checks to complete before exiting.