---
title: "Language"
jupyter: env3.12
#execute:
#  cache: true
---

!!! info "Learning Outcomes"
    - Master foundational Python syntax, including variables, basic data types, and standard operators.
    - Implement robust data structures such as lists, sets, dictionaries, and specialized hostlists for infrastructure management.
    - Write reusable functions, classes and commandline tools to streamline cloud and data automation workflows.

## Comments

Comments in Python are followed by a `#`:

```{python}
# This is a comment
```

## Statements and Strings

Let us explore the syntax of Python while starting with a print statement

```{python}
print("Hello world from Python!")
```

The print function was given a **string** to process. A string is a sequence of characters. A **character** can be an alphabetic (A through Z, lower and upper case), numeric (any of the digits), white space (spaces, tabs, newlines, etc), syntactic directives (comma, colon, quotation, exclamation, etc), and so forth. A string is just a sequence of the character and typically indicated by surrounding the characters in double-quotes.

## Variables

You can store data into a **variable** to access it later. For instance:

```{python}
hello = 'Hello world from Python!'
print(hello)
```

## Simple Data Types

In addition to `strings` we have more simple data types, such as boolean, and numbers in various formats such as integers and floats.

### Booleans

A **boolean** is a value that can have the values `True` or `False`. You can combine booleans with **boolean operators** such as `and` and `or`

```{python}
print(True and True) # True
print(True and False) # False
print(False and False) # False
print(True or True) # True
print(True or False) # True
print(False or False) # False
```

### Numbers

The interactive interpreter can also be used as a calculator. For instance, say we wanted to compute a multiple of 21:

```{python}
print(21 * 2) # 42
```

We saw here the print statement again. We passed in the result of the operation 21 \* 2. An **integer** (or **int**) in Python is a numeric value without a fractional component (those are called **floating point** numbers, or **float** for short).

The mathematical operators compute the related mathematical operation to the provided numbers. Some operators are:

| Operator | Function       |     |
|----------|----------------|-----|
| \*       | multiplication |     |
| /        | division       |     |
| \+       | addition       |     |
| \-       | subtraction    |     |
| \*\*     | exponent       |     |

Exponentiation $x^y$ is written as x\*\*y is x to the yth power.

You can combine **float**s and **int**s:

```{python}
print(3.14 * 42 / 11 + 4 - 2) # 13.9890909091
print(2**3) # 8
```

Note that **operator precedence** is important. Using parenthesis to indicate affect the order of operations gives a difference results, as expected:

```{python}
print(3.14 * (42 / 11) + 4 - 2) # 11.42
print(1 + 2 * 3 - 4 / 5.0) # 6.2
print( (1 + 2) * (3 - 4) / 5.0 ) # -0.6
```

## Imports

Imports allow you to load modules that provide preexisting code packaged in a convenient way for you to reuse.

### Import Statement

When the interpreter encounters an import statement, it imports the module if the module is present in the search path. A search path is a list of directories that the interpreter searches before importing a module. It is preferred to use for each import its own line such as:

```{python}
import numpy
import matplotlib
```

### The from ... import Statement

Python's from statement lets you import specific attributes from a module into the current namespace. The from ... import has the following syntax:

```{python}
from datetime import datetime
```

## Date Time in Python

The `datetime` module supplies classes for manipulating dates and times in both simple and complex ways. While date and time arithmetic is supported, the focus of the implementation is on efficient attribute extraction for output formatting and manipulation. For related functionality, see also the time and calendar modules.

```{python}
from datetime import datetime
```

This module offers a generic date/time string parser which is able to parse most known formats to represent a date and/or time.

```{python}
from dateutil.parser import parse
```

Create a string variable with the class start time

```{python}
fall_start = '08-24-2026'
```

Convert the string to datetime format

```{python}
print(datetime.strptime(fall_start, '%m-%d-%Y'))
```

```{python}
from datetime import datetime

# No need for datetime.datetime
d = datetime(2017, 8, 21, 0, 0)
print(d)
```

Creating a list of strings as dates

```{python}
class_dates = [
    '8/25/2017',
    '9/1/2017',
    '9/8/2017',
    '9/15/2017',
    '9/22/2017',
    '9/29/2017']
```

Convert Class_dates strings into `datetime` format and save the list into variable a

```{python}
[datetime.strptime(x, '%m/%d/%Y') for x in class_dates]
```

Use parse() to attempt to auto-convert common string formats. Parser must be a string or character stream, not list.

```{python}
parse(fall_start) 
```

Use parse() on every element of the Class_dates string.

```{python}
[parse(x) for x in class_dates]
```

Use parse, but designate that the day is first.

```{python}
parse (fall_start, dayfirst=True)
```

Create a `dataframe`. A DataFrame is a tabular data structure comprised of rows and columns, akin to a spreadsheet, database table. DataFrame is a group of Series objects that share an index (the column names). We use pandas is an open-source Python library for data analysis that needs to be imported.

```{python}
import pandas as pd
data = {
  'dates': [
    '8/25/2017 18:47:05.069722',
    '9/1/2017 18:47:05.119994',
    '9/8/2017 18:47:05.178768',
    '9/15/2017 18:47:05.230071',
    '9/22/2017 18:47:05.230071',
    '9/29/2017 18:47:05.280592'],
  'complete': [1, 0, 1, 1, 0, 1]}
df = pd.DataFrame(
  data,
  columns = ['dates','complete'])
print(df)
```

Convert `` df[`date`] `` from string to datetime

```{python}
import pandas as pd
pd.to_datetime(df['dates'])
```

## Control Statements

### Comparison

Computer programs do not only execute instructions. Occasionally, a choice needs to be made. Such as a choice is based on a condition. Python has several conditional operators:

| Operator | Function     |     |
|----------|--------------|-----|
| \>       | greater than |     |
| \<       | smaller than |     |
| ==       | equals       |     |
| !=       | is not       |     |

Conditions are always combined with variables. A program can make a choice using the if keyword. For example:

``` python
x = int(input("Guess x:"))
if x == 4:
   print('Correct!')
```

In this example, *You guessed correctly!* will only be printed if the variable x equals four. Python can also execute multiple conditions using the `elif` and `else` keywords.

``` python
x = int(input("Guess x:"))
if x == 4:
    print('Correct!')
elif abs(4 - x) == 1:
    print('Wrong, but close!')
else:
    print('Wrong, way off!')
```

### Iteration

To repeat code, the `for` keyword can be used. For example, to display the numbers from 1 to 3, we could write something like this:

```{python}
for i in range(1, 3):
   print('Hello!')
```

The second argument to the `range`, *3*, is not inclusive, meaning that the loop will only get to *2* before it finishes. Python itself starts counting from 0, so this code will also work:

```{python}
for i in range(0, 3):
   print(i + 1)
```

In fact, the range function defaults to starting value of *0*, so it is equivalent to:

```{python}
for i in range(3):
   print(i + 1)
```

We can also nest loops inside each other:

```{python}
for i in range(0,3):
    for j in range(0,3):
        print(i,' ',j)
```

In this case, we have two nested loops. The code will iterate over the entire coordinate range (0,0) to (2,2)

## Advanced Datatypes

### Lists

Lists in Python are ordered sequences of elements, where each element can be accessed using a 0-based index.

To define a list, you simply list its elements between square brackets \[ \]:

```{python}
computers = [
  'Workstation-01',
  'Server-Alpha',
  'Laptop-Pro',
  'Backup-Unit',
  'Gateway-02']
```

To access the first element of the list use

```{python}
computers[0]
```

To access the third element of the list use

```{python}
computers[2]    
```

You can also use a negative index if you want to start counting elements from the end of the list. Thus, the last element has index -1, the second before the last element has index -2, and so on:

To access the last element of the list use

```{python}
computers[-1]
```

To access the second last element of the list use

```{python}
computers[-2]
```

Python also allows you to take whole slices of the list by specifying a beginning and end of the slice separated by a colon:

To access the middle elements, excluding first and last use

```{python}
computers[1:-1]
```

As you can see from the example, the starting index in the slice is inclusive and the ending one, exclusive.

Python provides a variety of methods for manipulating the members of a list.

You can add elements with append:

To adds an element to the end use

```{python}
computers.append('Laptop-Pro')
```

As you can see, the elements in a list need not be unique.

Merge two lists with extend:

```{python}
computers.extend(['Node-05', 'Node-06'])
```

Find the index of the first occurrence of an element with index:

```{python}
computers.index('Laptop-Pro') 
```

Remove elements by value with remove:

To remove only the first occurrence of the value

```{python}
computers.remove('Gateway-02')
```

Remove elements by index with pop:

```{python}
computers.pop(1)
computers
```

Notice that pop returns the element being removed, while remove does not.

If you are familiar with stacks from other programming languages, you can use insert and pop:

Insert 'Mainframe' at the very beginning:

```{python}
computers.insert(0, 'Mainframe')
computers
```

To pop() without an index removes the last element:

```{python}
computers.pop()
computers
```

The Python documentation contains a [full list of list operations]().

To go back to the range function you used earlier, it simply creates a list of numbers:

```{python}
range(10)
```

```{python}
range(2, 10, 2)
```

### Hostlists

When managing **Cloud Computing** clusters or **High-Performance Computing (HPC)** environments, you often need to address groups of machines. Instead of listing `server01, server02, server03...` manually, we use **Hostlists**.

A Hostlist is a compressed representation of network hosts, commonly used in job schedulers (like Slurm) and cluster management tools.

### Understanding the Syntax

Hostlists use **bracket expansion** to group ranges of numbers or letters.

|                         |                                        |
|-------------------------|----------------------------------------|
| **Compressed Hostlist** | **Expanded Result**                    |
| `server[01-03]`         | `server01, server02, server03`         |
| `node[1,5,10-12]`       | `node1, node5, node10, node11, node12` |
| `gpu-[a-c]`             | `gpu-a, gpu-b, gpu-c`                  |

### 2. Using Hostlists in Python

The most robust way to handle these in Python is via the `python-hostlist` library. It allows you to expand strings into lists and compress lists back into strings. Hostlist can be installed with

``` bash
pip install python-hostlist
```

### Basic Operations

```{python}
import hostlist
```

#### 1. Expand a hostlist string into a Python list

```{python}
#| label: hostlist-expansion
#| echo: true
#| output: true

import hostlist
hosts = hostlist.expand_hostlist("node[01-03]")
print(hosts) 
```

```{python}
import hostlist
hosts = hostlist.expand_hostlist("red[01-03,05]-compute")
print(hosts)
```

#### 2. Compress a list of hosts into a hostlist string

```{python}
import hostlist
my_nodes = ['node10', 'node11', 'node12', 'node15']
compressed = hostlist.collect_hostlist(my_nodes)
print(compressed)
```

#### 3. Practical Cloud/AI Use Case: GPU Clusters

In AI training, you might need to run a distributed training job across specific GPU nodes. Using hostlists prevents configuration errors.

```{python}
import hostlist
def setup_distributed_training(host_string):
    nodes = hostlist.expand_hostlist(host_string)
    print(f"Initializing training on {len(nodes)} nodes...")
    for node in nodes:
        # Logic to trigger ssh or container execution
        print(f" -> Connecting to {node}")
setup_distributed_training("gpu-cluster-[001-004]")
```

#### 4. Key Functions Reference

- **expand_hostlist(string):** Returns a list of individual hostnames.
- **collect_hostlist(list):** Returns the shortest possible bracket-syntax string.
- **find_common_prefix(list):** Useful for identifying the cluster name from a list of nodes.

**Common Pitfalls:**
- **Padding:** `node[1-3]` yields node1, node2, node3, while `node[01-03]` yields node01, node02, node03. Ensure your script matches your DNS/Inventory naming.
- **Non-Sequential Nodes:** If your cluster has "holes" (e.g., node 4 is down), use commas: `node[1-3,5-10]`.

### Sets

Python lists can contain duplicates, as you saw previously. We see that the name Laptop-Pro occurs twice. To just use unique names, we can use a set.

```{python}
computers = [
  'Workstation-01', 'Server-Alpha', 'Laptop-Pro', 
  'Backup-Unit', 'Laptop-Pro', 'Workstation-01'
]
unique_computers = set(computers)
print(unique_computers)
```

Keep in mind that a *set* is an **unordered** collection of objects; therefore, we cannot access them by index:

``` python
unique_computers[0]
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   TypeError: 'set' object does not support indexing
```

However, we can convert a set back to a list easily:

```{python}
unique_list = list(unique_computers)
# ['Backup-Unit', 'Server-Alpha', 'Workstation-01', 'Laptop-Pro']

print(unique_list[0])
```

Notice that in this case, the order of elements in the new list matches the order in which the elements were displayed when the set was created. However, **you should not assume this is the case in general**. Do not make any assumptions about the order of elements in a set when it is converted to any type of sequential data structure.

### Set Operations

You can change a set's contents using the `add`, `remove`, and `update` methods, which correspond to the `append`, `remove`, and `extend` methods in a list.

In addition to these, *set* objects support the operations you may be familiar with from mathematical sets: **union**, **intersection**, and **difference**.

```{python}
office_a = {'Workstation-01', 'Server-Alpha'}
office_b = {'Server-Alpha', 'Laptop-Pro'}

print("Union: All unique computers across both offices:\n\t", office_a | office_b)
print ("Intersection: Computers present in both offices:\n\t", office_a & office_b)
print ("Difference: Computers in office_a but NOT in office_b:\n\t", office_a - office_b)
```

You can read more about these in the [Python documentation for sets](https://www.google.com/search?q=https://docs.python.org/3/library/stdtypes.html%23set).

### Removal and Testing for Membership in Sets

One important advantage of a `set` over a `list` is that **access to elements is fast**. If you are familiar with different data structures from a Computer Science class, the Python list is implemented by an array, while the set is implemented by a hash table.

We will demonstrate this with an example. Let us say we have a list and a set of the same number of elements (approximately 100 thousand):

``` python
import sys, random, timeit
nums_set = set([random.randint(0, sys.maxvalue) for _ in range(10**5)])
nums_list = list(nums_set)
len(nums_set)
# 100000
```

We will use the [timeit](https://docs.python.org/2/library/timeit.html) Python module to time 100 operations that test for the existence of a member in either the list or set:

``` python
import timeit
timeit.timeit('random.randint(0, sys.maxint) in nums',
              setup='import random; nums=%s' % str(nums_set), number=100)
# 0.0004038810729980469
timeit.timeit('random.randint(0, sys.maxint) in nums',
              setup='import random; nums=%s' % str(nums_list), number=100)
# 0.398054122924804
```

The exact duration of the operations on your system will be different, but the takeaway will be the same: searching for an element in a set is orders of magnitude faster than in a list. This is important to keep in mind when you work with large amounts of data.

### Dictionaries

One of the very important data structures in python is a dictionary also referred to as `dict`.

A dictionary represents a key value store:

```{python}
computer = {
  'name': 'mycomputer',
  'memory': 16,
  'kind': 'Laptop'
  }
print("computer['name']: ", computer['name'])
print("computer['memory']: ", computer['memory'])

# A convenient for to print by named attributes is

print("{name} {memory}".format(**computer))

```

This form of printing with the format statement and a reference to data increases the readability of the print statements.

You can delete elements with the following commands:

```{python}
del computer['name'] # remove entry with key 'name'
computer.clear()     # remove all entries in dict
del computer         # delete entire dictionary
# computer
# Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
#  NameError: name 'computer' is not defined
```

You can iterate over a dict:

```{python}
computer = {
  'name': 'mycomputer',
  'memory': 16,
  'kind': 'Laptop'
  }
for item in computer:
  print(item, computer[item])
```

### Dictionary Keys and Values

You can retrieve both the keys and values of a dictionary using the keys() and values() methods of the dictionary, respectively:

```{python}
computer.keys()
```

```{python}
computer.values() 
```

Both methods return lists. Please remember however that the keys and order in which the elements are returned are not necessarily the same. It is important to keep this in mind:

!!! warning
    *You cannot make any assumptions about the order in which the elements of a dictionary will be returned by the keys() and values() methods*.

    However, you can use ordered_dict that preserves the order

However, you can assume that if you call `keys()` and `values()` in sequence, the order of elements will at least correspond in both methods.

### Counting with Dictionaries

One application of dictionaries that frequently comes up is counting the elements in a sequence. For example, say we have a sequence of coin flips:

```{python}
import random
die_rolls = [
  random.choice(['heads', 'tails']) for _ in range(10)
]
print(die_rolls)
```

The actual list die_rolls will likely be different when you execute this on your computer since the outcomes of the die rolls are random.

To compute the probabilities of heads and tails, we could count how many heads and tails we have in the list:

```{python}
counts = {'heads': 0, 'tails': 0}
for outcome in die_rolls:
   assert outcome in counts
   counts[outcome] += 1
print('Probability of heads: %.2f' % (counts['heads'] / len(die_rolls)))
print('Probability of tails: %.2f' % (counts['tails'] / sum(counts.values())))
```

In addition to how we use the dictionary counts to count the elements of coin_flips, notice a couple of things about this example:

1.  We used the assert outcome in the `count` statement. The assert statement in Python allows you to easily insert debugging statements in your code to help you discover errors more quickly. assert statements are executed whenever the internal Python `__debug__` variable is set to True, which is always the case unless you start Python with the -O option which allows you to run *optimized* Python.

2.  When we computed the probability of tails, we used the built-in `sum` function, which allowed us to quickly find the total number of coin flips. The `sum` is one of many built-in functions you can [read about here](https://docs.python.org/2/library/functions.html).

## Functions

You can reuse code by putting it inside a function that you can call in other parts of your programs. Functions are also a good way of grouping code that logically belongs together in one coherent whole. A function has a unique name in the program. Once you call a function, it will execute its body which consists of one or more lines of code:

```{python}
names = ["gpu-node-01", "GPU-node-02"]
def is_valid_node_name(name):
    """Checks if a cloud node name is lowercase and within length limits."""
    is_lowercase = name.islower()
    correct_length = 3 <= len(name) <= 63
    
    return is_lowercase and correct_length

# Testing the function
for name in names:
    print(f"{name}:", is_valid_node_name(name))
```

The def keyword tells Python we are defining a function. As part of the definition, we have the function name, is_valid_node_name, and the parameters of the function -- variables that will be populated when the function is called.

### Type Hinting

In professional cloud automation, it is critical to know exactly what data types a function expects and returns. Python's `typing` module allows you to add "hints" to your code. While Python remains dynamically typed, these hints are used by IDEs and static analysis tools to catch bugs before the code even runs.

```{python}
from typing import List, Dict, Optional

def process_nodes(nodes: List[str], config: Dict[str, int]) -> Optional[int]:
    """
    Processes a list of nodes based on a config dictionary.
    Returns the number of processed nodes, or None if the list is empty.
    """
    if not nodes:
        return None
    
    count = 0
    for node in nodes:
        if config.get("enabled", 0) == 1:
            count += 1
    return count

# Usage
node_list = ["node-01", "node-02"]
settings = {"enabled": 1}
result = process_nodes(node_list, settings)
print(f"Processed {result} nodes.")
```

## Classes

A class is an encapsulation of data and the processes that work on them. The data is represented in member variables, and the processes are defined in the methods of the class (methods are functions inside the class). For example, let's see how to define a class for a computer:

```{python}
class CloudNode:
    """Represents a virtual machine in a cloud cluster."""

    def __init__(self, name, cpu_cores, ram_gb):
        # Encapsulation and Validation
        if not self._is_valid_config(cpu_cores, ram_gb):
            print(f"Invalid configuration for node: {name}")
            return

        # Member Variables (Data)
        self.name = name
        self.cpu_cores = cpu_cores
        self.ram_gb = ram_gb
        self.status = "stopped"

    def _is_valid_config(self, cpu, ram):
        """Internal process to validate hardware specs."""
        # Rules: Must have at least 1 core and 2GB RAM
        return cpu >= 1 and ram >= 2

    def start(self):
        """Method to change the state of the object."""
        self.status = "running"
        print(f"Node {self.name} is now {self.status}.")

# Creating an instance (Object)
my_node = CloudNode("ai-processor-01", 8, 32)
my_node.start()
```

## Commandline Programs

In the world of Cloud Computing and AI, automation is key. Instead of using a graphical interface to click buttons, which is not scalable, we write scripts that can be triggered from a terminal (command line). These scripts allow us to manage hundreds of servers or trigger massive AI training jobs with a single command. They can be integrated in shell scripts as well as called from other languages or frameworks

### The `docopt`Advantage

A popular way to create command line interfaces in Python is using a library called `docopt`. Unlike other libraries where you have to write complex code to define your flags and arguments, `docopt` follows a unique philosophy: **the documentation is the code.** You simply write a standard help message (a "docstring") at the top of your file, and `docopt` automatically:

1.  **Parses** the arguments you type in the terminal.

2.  **Validates** that the user provided the correct number of inputs.

3.  **Generates** a help menu automatically when the user types `--help`.

### Anatomy of a Cloud Script

In the following program, we define a "Cloud Quota" checker. This is a common task in enterprise environments where we must ensure a user isn't trying to spin up a Virtual Machine that is too large for their budget or service tier.

We use three key components:

- **The Docstring:** Defines the "Usage" pattern.

- **The Logic Function:** A reusable block of code (`is_valid_quota`) that can be imported into other programs.

- **The Main Guard:** The `if __name__ == '__main__':` block, which ensures the script only runs its CLI logic when executed directly, not when imported as a library.

``` python
"""Usage: check_quota.py [-h] CPU RAM STORAGE

Check if a Cloud Node configuration fits within the Free Tier quota.

Arguments:
  CPU        Number of CPU cores.
  RAM        Amount of RAM in GB.
  STORAGE    Disk storage in GB.

Options:
  -h --help  Show this screen.
"""
from docopt import docopt

def is_valid_quota(cpu, ram, storage):
    """
    Business Logic: 
    Max 4 Cores, Max 16GB RAM, Max 100GB Storage.
    """
    return (cpu <= 4 and 
            ram <= 16 and 
            storage <= 100)

if __name__ == '__main__':
    # docopt parses the docstring above to create the CLI
    arguments = docopt(__doc__)
    
    # Extract and convert arguments
    c = int(arguments['CPU'])
    r = int(arguments['RAM'])
    s = int(arguments['STORAGE'])
    
    valid = is_valid_quota(c, r, s)
    
    # Modern f-string formatting (preferred over % operator)
    print(f"Node config (CPU:{c}, RAM:{r}GB, Disk:{s}GB) valid: {valid}")
```

Here is an example on how to use it.

``` bash
python check_quota.py 2 8 50
# Output: Node config (CPU:2, RAM:8GB, Disk:50GB) valid: True

python check_quota.py 8 32 500
# Output: Node config (CPU:8, RAM:32GB, Disk:500GB) valid: False
```

## Lambda Expressions {#s-python-lambda}

As opposed to normal functions in Python which are defined using the `def` keyword, lambda functions in Python are anonymous functions that do not have a name and are defined using the `lambda` keyword. The generic syntax of a lambda function is in the form of `lambda arguments: expression`, as shown in the following example:

```{python}
greeter = lambda x: print('Hello %s!'%x)
print(greeter('Albert'))
```

Now consider the following examples:

```{python}
power2 = lambda x: x ** 2
```

The `power2` function defined in the expression, is equivalent to the following definition:

```{python}
def power2(x):
    return x ** 2
```

Lambda functions are useful when you need a function for a short period.

Why use Lambdas in Cloud & Data Science? In cloud monitoring or data processing, you often use lambdas to transform data on the fly. For example, if you have a list of server memory capacities in GB and need to convert them to MB for a report:

```{python}
memory_gb = [8, 16, 32, 64]
# Use map with a lambda to multiply each element by 1024
memory_mb = list(map(lambda x: x * 1024, memory_gb))
print(memory_mb)
```

In Python, the filter function returns a filter object or the iterator which gets lazily evaluated which means neither we can access the elements of the filter object with index nor we can use `len()` to find the length of the filter object.

```{python}
list_a = [1, 2, 3, 4, 5]
filter_obj = filter(lambda x: x % 2 == 0, list_a)
# Convert the filer obj to a list
even_num = list(filter_obj)
print(even_num)
# Output: [2, 4]
```

The filter() function combined with a lambda expression is a powerful way to process data. To make this more readable and "Pythonic," you can often replace it with a List Comprehension, which is generally preferred in modern Python for its speed and clarity.

However, the Pythonic "List Comprehension" is the standard way to filter lists in Python. It reads almost like plain English: "Give me x for every x in list_a if x is even." THis illustrates, although python as many other languages have many advanced features, often the most straight forward are better, and in this case even faster.

```{python}
list_a = [1, 2, 3, 4, 5]

# More readable and usually faster than filter()
even_num = [x for x in list_a if x % 2 == 0]

print(even_num) 
```

In Python, we can have a small usually a single linear anonymous function called Lambda function which can have any number of arguments just like a normal function but with only one expression with no return statement. The result of this expression can be applied to a value.

Basic Syntax:

```{python}
lambda arguments : expression
```

For example, a function in python

``` python
def multiply(a, b):
   return a*b

#call the function
multiply(3, 5) #outputs: 15
```

The same function can be written as Lambda function. This function named as multiply is having 2 arguments and returns their multiplication.

Lambda equivalent for this function would be:

``` python
multiply = lambda a, b : a*b

print(multiply(3, 5))
# outputs: 15
```

Here a and b are the 2 arguments and a\*b is the expression whose value is returned as an output.

Also, we don't need to assign the Lambda function to a variable.

``` python
(lambda a, b : a*b)(3, 5)
```

Lambda functions are mostly passed as a parameter to a function which expects a function objects like in map or filter.

### Decorators

A decorator is a function that takes another function and extends its behavior without explicitly modifying it. In cloud engineering, decorators are frequently used for logging, authentication, and timing the execution of API calls.

```{python}
import time
from functools import wraps

def timer_decorator(func):
    """Decorator that prints the execution time of the function it wraps."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timer_decorator
def simulate_cloud_api_call():
    """Simulates a network request to a cloud provider."""
    time.sleep(0.5)
    print("API Response: Node status is 'running'")

simulate_cloud_api_call()
```

### map {#s-python-map}

The basic syntax of the map function is

``` python
map(function_object, iterable1, iterable2,...)
```

map functions expect a function object and any number of iterable like a list or dictionary. It executes the function_object for each element in the sequence and returns a list of the elements modified by the function object.

Example:

``` python
def multiply(x):
   return x * 2

map(multiply, [2, 4, 6, 8])
# Output [4, 8, 12, 16]
```

If we want to write the same function using Lambda

``` python
map(lambda x: x*2, [2, 4, 6, 8])
# Output [4, 8, 12, 16]
```

### Dictionary

When managing a multi-cloud environment (using AWS, Azure, or Google Cloud), you often receive data as a list of dictionaries. Using `map` and `lambda` allows you to "pluck" specific metadata—like hostnames or regions—out of those complex objects for reporting.

Let's assume we have a list of active cloud instances:

Code snippet

```{python}
# A list of dictionaries representing our multi-cloud inventory
cloud_nodes = [
    {'hostname': 'ubuntu-web-01', 'provider': 'aws', 'status': 'running'},
    {'hostname': 'fedora-db-02', 'provider': 'gcp', 'status': 'stopped'},
    {'hostname': 'win-ad-01', 'provider': 'azure', 'status': 'running'}
]
```

We can now extract specific attributes applying them to all cloud_nodes. We use `map` to create a simple list of all hostnames or all providers.

```{python}
# Extract all hostnames
hostnames = list(map(lambda x: x['hostname'], cloud_nodes))
# Output: ['ubuntu-web-01', 'fedora-db-02', 'win-ad-01']

# Extract all providers
providers = list(map(lambda x: x['provider'], cloud_nodes))
# Output: ['aws', 'gcp', 'azure']
```

We can also define tests and return a List with their results. For that we can use `map. Here`we generate "health checks" or status flags across your entire fleet.

```{python}
# Check which nodes are currently 'running'
is_running = list(map(lambda x: x['status'] == 'running', cloud_nodes))
# Output: [True, False, True]
```

### Important Note

In Python, `map()` returns a **map object** (an iterator) rather than a list. This is a memory-saving feature designed for high-performance computing. To see the actual values in a print statement or to use them as a standard list, you must wrap the call in `list()`, as shown above: `list(map(...))`.

Now, let us see how we can iterate over a dictionary using map and lambda Let us say we have a dictionary object

```{python}
dict_movies = [
    {'movie': 'avengers', 'comic': 'marvel'},
    {'movie': 'superman', 'comic': 'dc'}
]
```

We can iterate over this dictionary and read the elements of it using map and lambda functions in following way:

```{python}
map(lambda x : x['movie'], dict_movies)  # Output: ['avengers', 'superman']
map(lambda x : x['comic'],  dict_movies)  # Output: ['marvel', 'dc']
map(lambda x : x['movie'] == "avengers", dict_movies)
# Output: [True, False]
```

In Python, map function returns an iterator or map object which gets lazily evaluated which means neither we can access the elements of the map object with index nor we can use len() to find the length of the map object. We can force convert the map output i.e. the map object to list as shown next:

``` python
map_output = map(lambda x: x*2, [1, 2, 3, 4])
print(map_output)
# Output: map object: <map object at 0x04D6BAB0>
list_map_output = list(map_output)
print(list_map_output) # Output: [2, 4, 6, 8]
```

## Iterators

In Python, an iterator protocol is defined using two methods: `__iter()__` and `next()`. The former returns the iterator object and latter returns the next element of a sequence. Some advantages of iterators are as follows:

- Readability
- Supports sequences of infinite length
- Saving resources

There are several built-in objects in Python which implement iterator protocol, e.g. string, list, dictionary. In the following example, we create a new class that follows the iterator protocol. We then use the class to generate `log2` of numbers:

```{python}
from math import log2

class LogTwo:
    "Implements an iterator of log two"

    def __init__(self,last = 0):
        self.last = last

    def __iter__(self):
        self.current_num = 1
        return self

    def __next__(self):
        if self.current_num <= self.last:
            result = log2(self.current_num)
            self.current_num += 1
            return result
        else:
            raise StopIteration

L = LogTwo(5)
i = iter(L)
print(next(i))
print(next(i))
print(next(i))
print(next(i))
```

As you can see, we first create an instance of the class and assign its `__iter()__` function to a variable called `i`. Then by calling the `next()` function four times, we get the following output:

``` bash
$ python iterator.py
0.0
1.0
1.584962500721156
2.0
```

As you probably noticed, the lines are `log2()` of 1, 2, 3, 4 respectively.

## Generators

Before we go to Generators, please understand Iterators. Generators are also Iterators but they can only be iterated over once. That is because generators do not store the values in memory instead they generate the values on the go. If we want to print those values then we can either simply iterate over them or use the for loop.

### Generators with function

For example, we have a function named as multiplyBy10 which prints all the input numbers multiplied by 10.

```{python}
def multiplyBy10(numbers):
   result = []
   for i in numbers:
      result.append(i*10)
   return result

new_numbers = multiplyBy10([1,2,3,4,5])

print(new_numbers)
```

Now, if we want to use Generators here then we will make the following changes.

```{python}
def multiplyBy10(numbers):
   for i in numbers:
      yield(i*10)

new_numbers = multiplyBy10([1,2,3,4,5])

print(new_numbers)
#Output: Generators object
```

In Generators, we use yield() function in place of return(). So when we try to print new_numbers list now, it just prints Generators object. The reason for this is because Generators do not hold any value in memory, it yields one result at a time. So essentially it is just waiting for us to ask for the next result. To print the next result we can just say `print(next(new_numbers))`. Here, the generator reads the first value, multiplies it by 10, and yields the result. Also in this case, we can just print next(new_numbers) 5 times to print all numbers and if we do it for the 6th time then we will get an error StopIteration which means Generators has exhausted its limit and it has no 6th element to print.

``` python
print(next(new_numbers))  #Output: 1
```

### Generators using for loop

If we now want to print the complete list of multiplied values then we can just do:

```{python}
def multiplyBy10(numbers):
   for i in numbers:
      yield(i*10)

new_numbers = multiplyBy10([1,2,3,4,5])

for num in new_numbers:
   print(num)
```

### Generators with List Comprehension

Python has something called List Comprehension, if we use this then we can replace the complete function def with just:

```{python}
new_numbers = [x*10 for x in [1,2,3,4,5]]
print (new_numbers)  #Output: [10, 20, 30, 40 ,50]
```

Here the point to note is square brackets \[\] in line 1 is very important. If we change it to () then again we will start getting Generators object.

```{python}
new_numbers = (x*10 for x in [1,2,3,4,5])
print (new_numbers)  #Output: Generators object
```

We can get the individual elements again from Generators if we do a for loop over `new_numbers`, as we did previously. Alternatively, we can convert it into a list and then print it.

```{python}
new_numbers = (x*10 for x in [1,2,3,4,5])
print (list(new_numbers))  #Output: [10, 20, 30, 40 ,50]
```

But here if we convert this into a list then we lose performance. So it is important to think beforehand which datstructures you need.

## Asynchronous Programming (`asyncio`)

In traditional synchronous programming, if your script calls a cloud API, it stops and waits for the response before moving to the next line. In cloud automation, where you might be managing 1,000 VMs, this is incredibly inefficient.

Asynchronous programming allows your script to "pause" a task that is waiting for I/O (like a network response) and work on other tasks in the meantime.

```{python}
import asyncio

async def fetch_node_status(node_id):
    print(f"Requesting status for {node_id}...")
    await asyncio.sleep(1) # Simulate network latency
    print(f"Node {node_id} responded: Online")
    return f"{node_id}: Online"

async def main():
    # Schedule multiple calls concurrently
    nodes = ["node-01", "node-02", "node-03"]
    tasks = [fetch_node_status(n) for n in nodes]
    
    print("Starting concurrent API calls...")
    results = await asyncio.gather(*tasks)
    print(f"All results: {results}")

# Run the async event loop
asyncio.run(main())
```

### Why use Generators?

Generators are highly efficient for handling large datasets because they use **Lazy Evaluation**. Instead of computing all values upfront and storing them in memory (which would consume significant RAM for millions of records), a generator computes each value only when it is requested. 

This is particularly useful in Cloud and AI pipelines where you might be streaming logs or processing massive datasets that exceed the available system memory.

Let us see an example of how Generators help in Performance. First, without Generators, normal function taking 1 million records and returns the result for 1 million entries.

```{python}
import random
import time
import os
import psutil
from pprint import pprint
# Configuration for our Cloud Cluster
regions = ['us-east-1', 'us-west-2', 'eu-central-1', 'ap-southeast-1']
node_types = ['t3.medium', 'm5.large', 'g4dn.xlarge', 'p4d.24xlarge']
statuses = ['running', 'stopped', 'terminated', 'provisioning']

def get_memory_usage():
    """Returns current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# 1. Record Initial State
mem_before = get_memory_usage()
print(f'Memory Baseline: {mem_before:.2f} MB')

def generate_inventory(num_nodes):
    """Creates a list of cloud node dictionaries."""
    inventory = []
    for i in range(num_nodes):
        node = {
            'node_id': f"i-{random.getrandbits(32):x}", # Simulated AWS Instance ID
            'hostname': f"node-{i:06d}",
            'type': random.choice(node_types),
            'region': random.choice(regions),
            'status': random.choice(statuses),
            'cpu_cores': random.choice([2, 4, 8, 16, 32, 64])
        }
        inventory.append(node)
    return inventory

# 2. Execute and Time the Generation
t1 = time.perf_counter()
cloud_inventory = generate_inventory(100000) 
t2 = time.perf_counter()

# 3. Record Final State
mem_after = get_memory_usage()
mem_used = mem_after - mem_before

print(f'Memory After Loading 100k Nodes: {mem_after:.2f} MB')
print(f'Actual RAM consumed by List: {mem_used:.2f} MB')
print(f'Inventory generation took: {t2-t1:.4f} seconds')

# Example: Peek at the first node
print("\nSample Node Data:")
pprint(cloud_inventory[0])
```

## Exceptions

In cloud automation and systems programming, **Exceptions** are not just "errors"—they are a critical part of the workflow. They allow your scripts to handle unpredictable events, such as a server being down, a network timeout, or a disk being full, without crashing the entire management suite.

In Python, we use the `try...except` block to manage these events. This is essential when you are making API calls to cloud providers or connecting to remote HPC nodes.

### Basic Exception Handling

Imagine a script that attempts to connect to a specific Cloud Node. If the node is unreachable, we don't want the script to stop; we want it to log the error and move to the next node.

Code snippet

``` python
def connect_to_node(node_name):
    # Simulating a connection failure for a specific node
    if node_name == "db-server-01":
        raise ConnectionError(f"Could not reach {node_name} via SSH.")
    return f"Connected to {node_name}"

nodes = ["web-01", "db-server-01", "storage-01"]

for node in nodes:
    try:
        status = connect_to_node(node)
        print(status)
    except ConnectionError as e:
        print(f"Warning: {e} Skipping to next task...")
```

### Specific vs. General Exceptions

It is a "best practice" in systems engineering to catch specific errors rather than using a blanket `except:`. This prevents you from accidentally hiding bugs in your code.

|  |  |
|------------------------------------|------------------------------------|
| **Exception Type** | **Common Infrastructure Cause** |
| `FileNotFoundError` | Missing configuration file or SSH key. |
| `ConnectionError` | Network timeout or firewall blocking a port. |
| `PermissionError` | Attempting to start a service without `sudo` privileges. |
| `KeyError` | Looking up a VM attribute that doesn't exist in the metadata. |

### The `finally` Clause

The `finally` block is used for "cleanup" tasks that **must** happen regardless of whether an error occurred—such as closing a database connection or deleting a temporary credential file.

Code snippet

``` python
try:
    print("Opening connection to the HPC Cluster...")
    # Logic that might fail
    result = 10 / 0 
except ZeroDivisionError:
    print("Error: Calculation failed.")
finally:
    print("Closing connection and clearing cache.") # This always runs
```

### Custom Exceptions

To handle environmental monitoring—such as in a server room, a laboratory, or even a specialized bird incubation environment—you can define a custom exception that triggers when a thermal threshold is exceeded.

We demonstrate this on a simple example. In high-performance computing (HPC) environments, this logic is often used to trigger an automated "graceful shutdown" or to send an alert to the facility manager.

In this example, we define a `HighTemperatureError` that carries the current temperature and the defined limit as metadata.

```{python}
class HighTemperatureError(Exception):
    """Exception raised when the ambient temperature exceeds safety limits."""
    
    def __init__(self, current_temp, limit=80):
        self.current_temp = current_temp
        self.limit = limit
        self.message = (f"CRITICAL: Temperature {current_temp}°C "
                        f"exceeds safety limit of {limit}°C!")
        super().__init__(self.message)

def monitor_server_room(sensor_reading):
    SAFE_LIMIT = 28 # Celsius
    if sensor_reading > SAFE_LIMIT:
        raise HighTemperatureError(sensor_reading, limit=SAFE_LIMIT)
    return f"Status Nominal: {sensor_reading}°C"
```

When you catch this exception, you can perform specific emergency actions, such as logging the event to a file or triggering a cooling system.

```{python}
# Simulated sensor readings over time
room_readings = [22, 25, 27, 31, 26]

for reading in room_readings:
    try:
        status = monitor_server_room(reading)
        print(status)
    except HighTemperatureError as e:
        print(f"  ALERT: {e}")
        print("  ACTION: Increasing fan speed and notifying administrator.")
        # Logic to act upon and send a msg the facility team to check the situation
```

Key Benefits of Custom Exceptions are

- **Granular Data:** By passing `current_temp` into the exception, the error handler knows exactly how severe the breach was.

- **Separation of Concerns:** Your monitoring logic doesn't need to know *how* to fix the problem; it only needs to know *when* to call for help.

## Context Managers (`with` statement)

When dealing with external resources—such as opening a configuration file, connecting to a database, or locking a cloud resource—it is vital that the resource is closed regardless of whether the code succeeds or fails.

The `with` statement simplifies this by using **Context Managers**, which automatically handle the setup and teardown of resources.

```{python}
# Traditional way (Risky if an error occurs before .close())
f = open("config.yaml", "w")
f.write("region: us-east-1")
f.close()

# The Pythonic way (Safe and Clean)
with open("config.yaml", "w") as f:
    f.write("region: us-east-1")
# File is automatically closed here, even if an exception was raised inside the block
```

For cloud practitioners, this is essential when using libraries like `boto3` or `pymongo` to ensure connections aren't leaked, which could otherwise lead to "Too many connections" errors in production.
