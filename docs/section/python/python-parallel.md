# Parallel Computing in Python

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Compare multi-threading and multi-processing approaches to determine the optimal concurrency strategy for I/O-bound versus CPU-bound tasks.
    - Implement thread and process synchronization using locks to prevent race conditions and ensure safe data access in shared memory environments.
    - Utilize advanced multiprocessing utilities, including worker pools (`Pool`), shared values, and arrays, to coordinate distributed execution across multiple cores.

Parallel computing in Python can be implemented using either multi-threading or multi-processing. In a multi-threading approach, threads run within the same shared memory heap. In contrast, multi-processing uses separate and independent memory heaps for each process, making inter-process communication more complex.

---

## Multi-threading in Python

Threading is suitable for I/O operations where the process is expected to be idle regularly, such as web scraping. This allows the processor to handle multiple independent network or data I/O requests in parallel and join the results at the end.

### Thread vs Threading

Python provides two modules for threading: `_thread` (the low-level API) and `threading` (the high-level interface). The `threading.Thread()` class is the primary tool for creating threads, using the `target` argument to specify the callable object and `args` to pass arguments.

```python
import threading

def hello_thread(thread_num):
    print("Hello from Thread ", thread_num)

if __name__ == '__main__':
    for thread_num in range(5):
        t = threading.Thread(target=hello_thread, args=(thread_num,))
        t.start()
```

The `if __name__ == '__main__':` block ensures that the code runs only when the module is executed as a program, not when it is imported into another file.

### Locks

Because threads share memory space, concurrent modifications to the same variable can lead to unpredictable results. A `Lock` ensures that only one thread can access a critical section of code at a time. Other threads must wait until the lock is released.

```python
import threading

global counter
counter = 0

def incrementer1():
    global counter
    for j in range(2):
        for i in range(3):
            counter += 1
            print("Greeter 1 incremented the counter by 1")
        print("Counter is %d" % counter)

def incrementer2():
    global counter
    for j in range(2):
        for i in range(3):
            counter += 1
            print("Greeter 2 incremented the counter by 1")
        print("Counter is now %d" % counter)

if __name__ == '__main__':
    t1 = threading.Thread(target=incrementer1)
    t2 = threading.Thread(target=incrementer2)

    t1.start()
    t2.start()
```

Without a lock, the output of the above code will vary across runs due to race conditions during the increment operation.

To fix this, we use `threading.Lock()` to acquire and release access to the shared counter:

```python
import threading

increment_by_3_lock = threading.Lock()
global counter
counter = 0

def incrementer1():
    global counter
    for j in range(2):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter += 1
            print("Greeter 1 incremented the counter by 1")
        print("Counter is %d" % counter)
        increment_by_3_lock.release()

def incrementer2():
    global counter
    for j in range(2):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter += 1
            print("Greeter 2 incremented the counter by 1")
        print("Counter is %d" % counter)
        increment_by_3_lock.release()

if __name__ == '__main__':
    t1 = threading.Thread(target=incrementer1)
    t2 = threading.Thread(target=incrementer2)

    t1.start()
    t2.start()
```

---

## Multi-processing in Python

The `multiprocessing` module provides an API for spawning processes. Unlike threads, processes have their own memory space, which bypasses the Global Interpreter Lock (GIL) and allows for true parallelism on multi-core systems.

### Process

The `Process` class is used to spawn a new process.

```python
from multiprocessing import Process
import os

def greeter(name):
    proc_idx = os.getpid()
    print("Process {0}: Hello {1}!".format(proc_idx, name))

if __name__ == '__main__':
    name_list = ['Harry', 'George', 'Dirk', 'David']
    process_list = []
    for name in name_list:
        current_process = Process(target=greeter, args=(name,))
        process_list.append(current_process)
        current_process.start()
    for process in process_list:
        process.join()
```

The `join()` method tells the main program to wait for the process to terminate before proceeding.

### Pool

The `Pool` class manages a fixed set of worker processes to execute a batch of jobs.

#### Synchronous `Pool.map()`

`Pool.map()` is a blocking call that distributes an iterable across the process pool.

```python
from multiprocessing import Pool
import os

def greeter(name):
    pid = os.getpid()
    print("Process {0}: Hello {1}!".format(pid, name))

if __name__ == '__main__':
    names = ['Jenna', 'David', 'Marry', 'Ted', 'Jerry', 'Tom', 'Justin']
    pool = Pool(processes=3)
    pool.map(greeter, names)
    print("Done!")
```

#### Asynchronous `Pool.map_async()`

`Pool.map_async()` is non-blocking; it returns immediately, and the order of results is not guaranteed. A `wait()` call is required to ensure the process completes before the script terminates.

```python
from multiprocessing import Pool
import os

def greeter(name):
    pid = os.getpid()
    print("Process {0}: Hello {1}!".format(pid, name))

if __name__ == '__main__':
    names = ['Jenna', 'David', 'Marry', 'Ted', 'Jerry', 'Tom', 'Justin']
    pool = Pool(processes=3)
    async_map = pool.map_async(greeter, names)
    print("Done!")
    async_map.wait()
```

---

## Process Communication

Processes do not share memory by default. To share state, the `multiprocessing` module provides `Value`, `Array`, `Queue`, and `Pipe`.

### Value

`Value` creates a shared `ctypes` object allocated in shared memory.

```python
from multiprocessing import Process, Lock, Value
import time

increment_by_3_lock = Lock()

def incrementer1(counter):
    for j in range(3):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter.value += 1
            time.sleep(0.1)
        print("Greeter1: Counter is %d" % counter.value)
        increment_by_3_lock.release()

def incrementer2(counter):
    for j in range(3):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter.value += 1
            time.sleep(0.05)
        print("Greeter2: Counter is %d" % counter.value)
        increment_by_3_lock.release()

if __name__ == '__main__':
    counter = Value('i', 0)
    t1 = Process(target=incrementer1, args=(counter,))
    t2 = Process(target=incrementer2, args=(counter,))
    t2.start()
    t1.start()
```

### Array

`Array` provides a shared array of a specific `ctype` data type.

```python
from multiprocessing import Process, Lock, Value, Array
import time
from ctypes import c_char_p

increment_by_3_lock = Lock()

def incrementer1(counter_and_names):
    counter = counter_and_names[0]
    names = counter_and_names[1]
    for j in range(2):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter.value += 1
            time.sleep(0.1)
        name_idx = counter.value // 3 - 1
        print("Greeter1: Greeting {0}! Counter is {1}".format(names.value[name_idx], counter.value))
        increment_by_3_lock.release()

def incrementer2(counter_and_names):
    counter = counter_and_names[0]
    names = counter_and_names[1]
    for j in range(2):
        increment_by_3_lock.acquire(True)
        for i in range(3):
            counter.value += 1
            time.sleep(0.05)
        name_idx = counter.value // 3 - 1
        print("Greeter2: Greeting {0}! Counter is {1}".format(names.value[name_idx], counter.value))
        increment_by_3_lock.release()

if __name__ == '__main__':
    counter = Value('i', 0)
    names = Array(c_char_p, 4)
    names.value = ['James', 'Tom', 'Sam', 'Larry']
    t1 = Process(target=incrementer1, args=((counter, names),))
    t2 = Process(target=incrementer2, args=((counter, names),))
    t2.start()
    t1.start()
```

---

## Assignments

!!! note "Assignment: Parallel Data Processor"
    1. **I/O Bound Task**: Create a script that downloads content from five different URLs using `threading` and `Lock` to synchronize the writing of results to a shared file.
    2. **CPU Bound Task**: Create a script that calculates the sum of squares for a large range of numbers (e.g., 1 to 10,000,000) using `multiprocessing.Pool`. Compare the execution time with a single-threaded implementation.
    3. **Shared State**: Implement a producer-consumer pattern where a producer process adds items to a `multiprocessing.Queue` and a consumer process processes them.

---

## Self-Evaluation

??? note "Why is multi-threading suitable for I/O-bound tasks but not for CPU-bound tasks in Python?"
    Due to the Global Interpreter Lock (GIL), only one thread can execute Python bytecode at a time. I/O tasks frequently yield control while waiting, allowing other threads to run. CPU tasks would compete for the GIL, resulting in no real parallelism.

??? note "What is a \"race condition\" and how does a `Lock` prevent it?"
    A race condition occurs when multiple threads or processes attempt to modify shared data simultaneously, leading to unpredictable results. A `Lock` ensures that only one thread or process can access the critical section of code at a time.

??? note "How do `multiprocessing.Value` and `multiprocessing.Array` enable communication between independent processes?"
    They allocate memory in a shared segment accessible to all child processes, providing a way to share state using `ctypes` types without the overhead of passing messages through pipes or queues.
