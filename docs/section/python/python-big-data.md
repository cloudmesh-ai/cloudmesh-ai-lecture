# Data Analysis and Big Data with Python

!!! info "Learning Objectives"
    - Utilize the SciPy ecosystem (NumPy, Pandas, Matplotlib) for data manipulation and visualization.
    - Load, clean, and explore large datasets using Pandas DataFrames.
    - Perform statistical analysis and generate data visualizations.
    - Implement data parsing techniques for semi-structured files.
    - Understand and apply parallel computing concepts using Dask for larger-than-memory datasets.

Working with large datasets in Python requires a move away from standard lists and loops toward vectorized operations and specialized data structures. The "Big Data" challenge in Python primarily revolves around memory management; since Python objects have significant overhead, loading a multi-gigabyte CSV into a standard list can quickly exhaust system RAM.

The SciPy ecosystem provides a standardized stack of libraries—NumPy, Pandas, and Matplotlib—that allow Python to perform high-performance numerical computing. For datasets that exceed available memory, distributed computing frameworks like Dask extend these familiar APIs to parallelize execution across multiple CPU cores or cluster nodes.

## The SciPy Ecosystem

The foundation of data science in Python is built upon three primary libraries that work in tandem.

### NumPy: Numerical Computing

NumPy provides the `ndarray` (n-dimensional array), which is far more memory-efficient than Python lists. It enables vectorization, allowing operations to be performed on entire arrays without explicit `for` loops.

### Pandas: Data Manipulation

Pandas introduces the `DataFrame`, a two-dimensional labeled data structure similar to a SQL table or an Excel spreadsheet. It is the primary tool for data cleaning, filtering, and aggregation.

### Matplotlib: Data Visualization

Matplotlib is the standard library for creating static, animated, and interactive visualizations. It is typically used in conjunction with NumPy and Pandas to identify trends and outliers in data.

## Practical Data Analysis Workflow

The following workflow demonstrates how to use the SciPy stack to analyze real-world data. In this case study, we use traffic citation data from the city of Bloomington, Indiana.

### Step 1: Data Acquisition and Setup

Data is often distributed across multiple files (e.g., by quarter). The first step is to organize the local environment and acquire the raw CSV files.

```bash
# Create a project directory for the dataset
mkdir btown-citations
cd btown-citations

# Download the first quarter citations data
wget https://data.bloomington.in.gov/dataset/c543f0c1-1e37-46ce-a0ba-e0a949bd248a/resource/24841976-fd35-4483-a2b4-573bd1e77cfb/download/2016-first-quarter-citations.csv
```

### Step 2: Loading and Exploring Data

Using Pandas, we can load CSV files into a DataFrame and inspect their internal structure. The following example shows how to use the Python interpreter to explore a new dataset.

Example: Exploring the DataFrame structure.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset into a Pandas DataFrame
data = pd.read_csv('2016-first-quarter-citations.csv')

# Verify the object type
print(f"Object Type: {type(data)}")
# Output: <class 'pandas.core.frame.DataFrame'>

# Inspect the index (the row labels)
print(f"Index: {data.index}")

# Inspect the columns (the column names)
print(f"Columns: {data.columns}")

# Preview the first few rows of data
print(data.head())

# Check for data types and identify missing values (nulls)
print(data.info())

# Generate a summary of central tendency and dispersion for numerical columns
print(data.describe())
```

### Step 3: Data Cleaning and Preprocessing

Raw data is rarely clean. Common tasks include handling missing values (NaNs) and converting strings to numerical types.

Example: Cleaning the \"Cited Person Age\" column.

```python
# Identify the number of missing values in the age column
missing_ages = data['Cited Person Age'].isnull().sum()
print(f"Number of missing ages: {missing_ages}")

# Fill missing values with the median age to maintain statistical distribution
median_age = data['Cited Person Age'].median()
data['Cited Person Age'] = data['Cited Person Age'].fillna(median_age)

# Convert the column to an integer type for analysis
data['Cited Person Age'] = data['Cited Person Age'].astype(int)
```

### Step 4: Generating Visualizations

Visualizations help in understanding the distribution of data. A histogram is ideal for viewing the frequency of specific values.

Example: Plotting the distribution of cited person ages.

```python
plt.figure(figsize=(10, 6))
plt.hist(data['Cited Person Age'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribution of Cited Person Age - Bloomington 2016')
plt.xlabel('Age')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.savefig('age_distribution.png')
plt.show()
```

## Data Parsing and Extraction

Not all data arrives in clean CSV formats. Semi-structured data, such as Markdown files or LaTeX source code, requires custom parsing logic to extract useful information.

### Parsing Semi-Structured Text

A common task is parsing a `notebook.md` file to track student progress. In a professional automation context, this is often implemented as a CLI command.

Example: CLI specification for a notebook parser.

```text
cms class notebook [--git=GITREPONAME] --verify hid
    verifies the correctness of the notebook.md file

cms class notebook [--git=GITREPONAME] --log
    displays the log of the notebook.md

cms class notebook [--git=GITREPONAME] --history
    displays a true or false for each week since the first occurrence
    of the notebook.md file in the git repository
```

Example: Basic implementation of a line-by-line parser.

```python
import re

def parse_notebook(filepath):
    results = []
    with open(filepath, 'r') as f:
        for line in f:
            # Search for lines indicating a completed task
            if "Completed:" in line:
                # Extract the task name after the marker
                task = line.split("Completed:")[1].strip()
                results.append(task)
    return results
```

### Extracting Data from LaTeX

Extracting video lengths from LaTeX macros requires identifying specific command patterns. This is useful for calculating the total viewing time of a course.

Example: Using regular expressions to extract `\\video{name}{length}`.

```python
import re

# Sample LaTeX content containing video macros
latex_content = r"This section covers basics in \video{Introduction to Python}{10:30} and advanced topics in \video{Asyncio Deep Dive}{15:45}"

# Pattern explanation:
# \\video matches the literal '\video'
# \{([^}]*)\} captures everything inside the first curly braces (the name)
# \{([^}]*)\} captures everything inside the second curly braces (the length)
pattern = r"\\\\video\{([^}]*)\}\{([^}]*)\}"

matches = re.findall(pattern, latex_content)
for name, length in matches:
    print(f"Video: {name}, Length: {length}")
```

## Scaling with Dask

When datasets exceed available RAM, Pandas becomes inefficient. Dask provides a way to scale Python code by partitioning a large DataFrame into many smaller Pandas DataFrames.

### Dynamic Task Scheduling

Dask uses a dynamic task scheduler to execute operations in parallel. Instead of executing a command immediately, Dask builds a graph of tasks and executes them only when `compute()` is called.

### Comparing Pandas and Dask

Dask mimics the Pandas API, making the transition straightforward.

Example: Parallel sum using Dask vs. Sequential sum using Pandas.

```python
import pandas as pd
import dask.dataframe as dd

# Pandas: Loads the entire file into memory (Sequential execution)
df_pandas = pd.read_csv('large_dataset.csv')
pandas_sum = df_pandas['value'].sum()

# Dask: Loads data lazily and processes in parallel (Distributed execution)
df_dask = dd.read_csv('large_dataset.csv')
dask_sum = df_dask['value'].sum().compute()

print(f"Pandas Sum: {pandas_sum}, Dask Sum: {dask_sum}")
```

!!! tip "Summary Checklist"
    - Used NumPy for efficient array operations and vectorization.
    - Loaded and explored datasets using Pandas DataFrames.
    - Performed data cleaning by handling missing values and type conversion.
    - Generated statistical visualizations using Matplotlib.
    - Implemented custom text parsers using regex for semi-structured files.
    - Transitioned from Pandas to Dask for larger-than-memory datasets.

!!! note "Exercise 1: Data Exploration"
    Download a public dataset from data.gov. Use Pandas to load the data, identify columns with the most missing values, and generate a histogram for one of the numerical columns.

!!! note "Exercise 2: Custom Log Parser"
    Write a tool that parses a system log file. The tool should identify all lines containing "ERROR" or "CRITICAL", extract the timestamp, and output the results to a CSV file.

!!! note "Exercise 3: Dask Performance Study"
    Create a large CSV file (e.g., 1 million rows). Implement the same aggregation logic (e.g., mean of a column) using both Pandas and Dask. Measure the execution time and memory usage for both and report the findings.
