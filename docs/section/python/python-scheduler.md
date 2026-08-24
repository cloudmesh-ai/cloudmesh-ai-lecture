---
title: "Python Schedulers"
---

!!! info "Learning Outcomes"
    - Understand the functionality of the `sched` module for event scheduling.
    - Implement delayed execution of functions using priority queues.
    - Apply scheduling concepts to cloud management tasks, such as automated health checks and resource cleanup.

While `time.sleep()` is useful for simple pauses, it blocks the execution of the entire thread and is impractical for managing multiple timed events. Python's `sched` module provides a general-purpose event scheduler that allows you to schedule functions to be executed at specific times in the future.

The `sched.scheduler` class uses a priority queue to keep track of events, ensuring that the event with the earliest scheduled time is executed first.

## Implementing a Cloud Resource Health Checker

In a cloud environment, you often need to perform periodic tasks, such as verifying that a VM is still responsive or ensuring a load balancer is healthy. The `sched` module allows you to schedule these checks without manually calculating sleep intervals.

``` python
import sched
import time
import random

# Create a scheduler instance
scheduler = sched.scheduler(time.time, time.sleep)

def check_vm_health(vm_name):
    """Simulates checking the health of a cloud VM."""
    print(f"[{time.strftime('%H:%M:%S')}] Checking health of {vm_name}...")
    status = random.choice(["Healthy", "Unresponsive", "Degraded"])
    print(f"[{time.strftime('%H:%M:%S')}] VM {vm_name} status: {status}")
    
    # Schedule the next check for this VM in 5-10 seconds
    next_check = random.uniform(5, 10)
    scheduler.enter(next_check, 1, check_vm_health, argument=(vm_name,))
    print(f"Next check for {vm_name} scheduled in {next_check:.2f}s")

# List of VMs to monitor
vms = ["web-server-01", "db-master-01", "cache-node-01"]

print("Starting Cloud Resource Health Monitor...")
for vm in vms:
    # Schedule the first check for each VM
    # We stagger the start times slightly to avoid a thundering herd problem
    delay = random.uniform(1, 3)
    scheduler.enter(delay, 1, check_vm_health, argument=(vm))
    print(f"Scheduled initial check for {vm} in {delay:.2f}s")

# Run the scheduler until all events are processed
# Note: In a real application, you would run this in a separate thread
try:
    scheduler.run()
except KeyboardInterrupt:
    print("\nStopping Health Monitor...")
```

### Key Concepts
- `scheduler.enter(delay, priority, action, argument=(), kwargs={})`: Schedules an event to happen after `delay` seconds.
- `priority`: Used to break ties between events scheduled for the same time.
- `scheduler.run()`: Blocks the main thread and executes all scheduled events in order.

!!! exercise "Delayed VM Shutdown Sequence"
    Create a cloud maintenance script using the `sched` module that implements a graceful shutdown sequence:
    1. Schedule a "Notification" event to be sent to users 60 seconds from now.
    2. Schedule a "Stop Application" event 120 seconds from now.
    3. Schedule a "Power Off VM" event 180 seconds from now.
    4. Ensure the script prints a timestamp for each event as it occurs.