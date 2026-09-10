# Data Management and Serialization in Python

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Select and implement the appropriate data format (JSON, YAML, CSV, XML) based on the use case.
    - Perform efficient text file operations, including line-by-line processing for large datasets.
    - Extract structured data from HTML and XML using BeautifulSoup and ElementTree.
    - Implement data serialization using Pickle while understanding its security implications.
    - Apply asymmetric encryption to secure sensitive data using RSA keys via OpenSSL and Python.
    - Integrate diverse data sources into a cohesive Python-based data processing pipeline.

In modern cloud and AI engineering, data rarely exists in a single format. A typical pipeline might ingest JSON from a REST API, read configuration from a YAML file, parse a CSV dataset for training, and store the final results in a database or an encrypted file. The ability to seamlessly translate between these formats—a process known as serialization and deserialization—is a fundamental skill for any backend or data engineer.

Choosing the wrong format can lead to significant issues: using Pickle for long-term storage may cause version incompatibility; using CSV for complex hierarchical data leads to fragile parsing logic; and failing to encrypt sensitive credentials creates critical security vulnerabilities.

## Text-Based Data Formats

Text-based formats are human-readable and widely supported across different programming languages, making them the ideal choice for configuration and data interchange.

### Plain Text Files

The most basic form of data storage is the plain text file. Python provides several ways to interact with these files, depending on the file size and the required granularity.

The `with` statement is the industry standard for file I/O, as it ensures the file is properly closed even if an exception occurs.

```python
# Reading the entire content of a file
with open('filename.txt', 'r') as file:
    content = file.read()

# Splitting content into a list of lines
with open('filename.txt', 'r') as file:
    lines = file.read().splitlines()
```

For large files that exceed available memory, reading the file line-by-line is mandatory to prevent system crashes.

```python
# Memory-efficient line-by-line processing
with open('filename.txt', 'r') as file:
    for line in file:
        print(line.strip())
```

### Comma Separated Values (CSV)

CSV files are used for tabular data. While a simple `.split(',')` might seem convenient, it fails when a field contains a comma enclosed in quotes. The `csv` module handles these edge cases correctly.

```python
import csv

# Reading a CSV file using the csv module
with open('data.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

For more complex data analysis, the `pandas` library provides a more powerful abstraction.

```python
import pandas as pd

# Reading CSV directly into a DataFrame
df = pd.read_csv("example.csv")
```

### JSON and YAML

JSON (JavaScript Object Notation) is the standard for web APIs, while YAML (YAML Ain't Markup Language) is preferred for configuration due to its support for comments and hierarchical structures.

```python
import json
import yaml

# JSON: Serialization and Deserialization
data = {"project": "cloudmesh", "version": 1.0}
json_string = json.dumps(data)  # Serialize to string
parsed_data = json.loads(json_string)  # Deserialize back to dict

# YAML: Reading a configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

## Structured and Web Data

When dealing with semi-structured data from the web or enterprise systems, specialized parsers are required to navigate the document tree.

### XML and ElementTree

XML is widely used in legacy enterprise systems and configuration formats. Python's `xml.etree.ElementTree` provides an efficient way to parse and modify XML documents.

```python
import xml.etree.ElementTree as ET

# Parsing an XML file
tree = ET.parse('data.xml')
root = tree.getroot()

# Searching for specific elements
for elem in root.findall('item'):
    print(elem.text)
```

### HTML and BeautifulSoup

Web scraping involves extracting data from HTML, which is often malformed. `BeautifulSoup` provides a robust way to navigate the HTML DOM using search methods and CSS selectors.

```python
from bs4 import BeautifulSoup
from pprint import pprint

html_doc = "<html><body><a class='sample' href='http://example.com'>Link 1</a></body></html>"
soup = BeautifulSoup(html_doc, 'html.parser')

# Find the first 'a' tag
search_elem = soup.find('a')
print(search_elem.prettify())

# Find all 'a' tags with a specific class
search_elems = soup.find_all("a", class_="sample")
pprint(search_elems)

# Use CSS selectors for precise targeting
a_tag_elems = soup.select('a.sample')
print(a_tag_elems)
```

### Excel Spreadsheets

For business data, `pandas` integrates with Excel through the `ExcelFile` class.

```python
import pandas as pd

filename = 'data.xlsx'
data = pd.ExcelFile(filename)
df = data.parse('Sheet1')
```

## Serialization and Internal Formats

Serialization is the process of converting a Python object into a byte stream for storage or transmission.

### Python Pickle

The `pickle` module allows for the serialization of almost any Python object. However, it has two major drawbacks: it is not portable across Python versions, and it is **insecure**. Loading a pickle file from an untrusted source can lead to arbitrary code execution.

```python
import pickle

flavor = {
    "small": 100,
    "medium": 1000,
    "large": 10000
}

# Serialize to a file
with open("data.p", "wb") as f:
    pickle.dump(flavor, f)

# Deserialize from a file
with open("data.p", "rb") as f:
    loaded_flavor = pickle.load(f)
```

### Configuration Management

For application settings, `ConfigParser` handles standard `.ini` files. Cloudmesh provides a specialized `ConfigDict` for more advanced configuration needs.

- **ConfigParser**: Standard library tool for INI files.
- **ConfigDict**: Cloudmesh implementation for hierarchical configuration management.

## Data Security and Encryption

Protecting data at rest is a critical requirement for any production system, especially when handling "Big Data" where a breach can have systemic impacts.

### Asymmetric Encryption with RSA

Asymmetric encryption uses a public key for encryption and a private key for decryption. This allows data to be encrypted by anyone with the public key, but only read by the owner of the private key.

#### Shell-Based Implementation (OpenSSL)

In a Linux environment, this is often achieved using the `openssl` CLI:

```bash
#! /bin/sh

# 1. Create data
echo "Sensitive Cloud Data" > file.txt

# 2. Extract the public key into PEM format
openssl rsa -in ~/.ssh/id_rsa -pubout > ~/.ssh/id_rsa.pub.pem

# 3. Encrypt the file using the public key
openssl rsautl -encrypt -pubin -inkey ~/.ssh/id_rsa.pub.pem -in file.txt -out secret.txt

# 4. Decrypt the file using the private key
openssl rsautl -decrypt -inkey ~/.ssh/id_rsa -in secret.txt
```

#### Python Implementation via Cloudmesh

The `cloudmesh.common.ssh.encrypt` module simplifies this process by wrapping the OpenSSL logic into a Python class.

```python
from cloudmesh.common.ssh.encrypt import EncryptFile

# Initialize with source and destination paths
e = EncryptFile('file.txt', 'secret.txt')

# Encrypt the file using the default system SSH key
e.encrypt()

# Decrypt the file back to its original form
e.decrypt()
```

## Persistent Storage and Databases

For structured data that requires complex querying, flat files are replaced by database engines.

- **Relational Databases**: Standard SQL databases (e.g., PostgreSQL, MariaDB) are used for ACID-compliant storage.
- **SQLite**: A serverless, file-based database engine integrated into Python via the `sqlite3` module. It is ideal for local caching and small-scale applications.

!!! tip "Summary Checklist"

    - [ ] Implemented efficient file reading using the `with` statement.
    - [ ] Used `csv.reader` instead of `.split(',')` to handle quoted fields.
    - [ ] Applied `json.dumps()` and `json.loads()` for API data interchange.
    - [ ] Used `BeautifulSoup` CSS selectors to extract data from HTML.
    - [ ] Avoided `pickle` for untrusted data due to security risks.
    - [ ] Implemented RSA encryption for sensitive files using `EncryptFile`.
    - [ ] Selected the appropriate storage (CSV, JSON, or SQLite) based on data complexity.

!!! note "Exercise 1: Format Conversion"

    **Task**: Create a CSV file with three columns (Name, Role, Email). Write a Python script that reads this CSV and converts it into a JSON array of objects.
    **Goal**: Practice basic data transformation between two common interchange formats.

!!! note "Exercise 2: Web Data Extraction"

    **Task**: Write a script using `BeautifulSoup` to fetch a webpage and extract all links (`<a>` tags) that have a specific class or are located within a specific `div` ID.
    **Goal**: Master the use of CSS selectors and the DOM tree for data extraction.

!!! note "Exercise 3: Secure Data Pipeline"

    **Task**: Implement a pipeline that:
    1. Reads a sensitive configuration from a YAML file.
    2. Serializes the configuration to a JSON string.
    3. Encrypts the resulting JSON file using the `EncryptFile` class.
    4. Decrypts the file and verifies the content matches the original YAML.
    **Goal**: Integrate serialization and encryption into a single secure workflow.
