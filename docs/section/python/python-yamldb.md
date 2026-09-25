# Working with YAMLDB (the Cloudmesh YAML Database)

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Set up the `cloudmesh-yamldb` library in a Python environment.
    - Create, read, update, and delete (CRUD) records stored in YAML files.
    - Query the database using a Pythonic syntax similar to NoSQL engines.
    - Persist changes safely and merge multiple YAML sources.

In this chapter you will discover how the **YAMLDB** package from the Cloudmesh ecosystem turns plain YAML files into a lightweight, searchable key-value store.

---

## Why YAMLDB?

| Situation | Traditional Choice | Why YAMLDB shines |
|-----------|-------------------|-------------------|
| **Rapid prototyping** – you need a quick, human-readable store. | SQLite, JSON files. | YAML is both human-friendly and supports complex data structures (lists, nested dicts) without extra quoting. |
| **Configuration versioning** – you want Git-friendly files. | .ini, .conf files. | YAML's indentation makes diffing clean; each record can be a top-level key. |
| **Small-scale catalogs** – e.g., a list of experiments, datasets, or services. | CSV, Excel. | Query language lets you filter without loading everything into a DataFrame. |
| **Learning NoSQL concepts** – you need a sandbox before moving to MongoDB. | Learn MongoDB directly. | YAMLDB lets you practice query patterns with zero server setup. |

---

## Installing the Library

Open a terminal (or a notebook cell) and run:

```bash
pip install cloudmesh-yamldb
```

If you are inside an isolated environment (e.g., a Jupyter notebook) you can use the magic command:

```python
!pip install -q cloudmesh-yamldb
```

The installation pulls in PyYAML and a few helper packages.

!!! note "Tip"
    `cloudmesh-yamldb` works with Python 3.8+; it does not require a running MongoDB server.

---

## A First-Look Example

Below is a minimal script that creates a database, inserts a few records, and queries them. You can copy-paste it into a Jupyter cell or a `.py` file.

```python
from cloudmesh.yaml.db import YamlDatabase

# 1. Create (or open) a YAML file that will host our database.
# It will be created in the current working directory if it doesn't exist.
db = YamlDatabase("catalog.yaml")

# 2. Insert some records. Each record is a Python dict.
db.insert_one({"name": "alpha",   "type": "sensor",   "value": 12.5, "tags": ["temp", "outdoor"]})
db.insert_one({"name": "beta",    "type": "actuator", "value": 3,    "tags": ["valve"]})
db.insert_one({"name": "gamma",   "type": "sensor",   "value": 7.8,  "tags": ["temp", "indoor"]})
db.insert_one({"name": "delta",   "type": "sensor",   "value": 15.2, "tags": ["humidity"]})

# 3. Query – find all sensors with value > 10, sorted by name.
results = db.find(
    where   = {"type": "sensor", "value": {"$gt": 10}},
    order_by= "name",
    limit   = 5
)

print("Query result (sensors with value > 10):")
for r in results:
    print(r)
```

### What you should see

Running the script prints something like:

```
Query result (sensors with value > 10):
{'name': 'alpha', 'type': 'sensor', 'value': 12.5, 'tags': ['temp', 'outdoor']}
{'name': 'delta', 'type': 'sensor', 'value': 15.2, 'tags': ['humidity']}
```

**Explanation of the query syntax**

| Operator | Meaning | Example |
|----------|---------|---------|
| `"$gt"`  | greater than | `"value": {"$gt": 10}` |
| `"$lt"`  | less than | `"value": {"$lt": 5}` |
| `"$in"`  | element in list | `"tags": {"$in": ["temp"]}` |
| `"$contains"` | substring in string or element in list | `"name": {"$contains": "a"}` |

These operators mimic MongoDB's query language, making the transition to a real NoSQL DB painless.

---

## CRUD in Detail

### Create

```python
# Insert a single document
db.insert_one({"id": 101, "title": "Experiment A", "status": "running"})

# Insert many at once (list of dicts)
batch = [
    {"id": 102, "title": "Experiment B", "status": "queued"},
    {"id": 103, "title": "Experiment C", "status": "finished"},
]
db.insert_many(batch)
```

### Read

```python
# Fetch by exact match
doc = db.find_one({"id": 102})
print("Found:", doc)

# Complex filter – all finished experiments
finished = db.find(where={"status": "finished"})
print("Finished experiments:", finished)
```

### Update

```python
# Increment a numeric field
db.update_one(
    query   = {"id": 101},
    update  = {"$inc": {"run_time": 5}}
)

# Replace an entire document (except the _id field)
db.replace_one(
    query  = {"id": 103},
    newdoc = {"id": 103, "title": "Experiment C", "status": "archived"}
)
```

### Delete

```python
# Remove a single record
db.delete_one({"id": 102})

# Purge everything (use with caution!)
# db.delete_many({})
```

---

## Merging Multiple YAML Sources

Imagine you have two YAML files that describe hardware inventories for two labs. You can unite them safely:

```python
from cloudmesh.yaml.db import YamlDatabase

lab_a = YamlDatabase("lab_a.yaml")
lab_b = YamlDatabase("lab_b.yaml")

# Merge lab_b into lab_a, keeping lab_a's records when there is a conflict
lab_a.merge(lab_b, on="serial_number", how="left")
```

- `on` specifies the unique key (similar to a primary key).
- `how` can be `"left"` (keep left-hand side on conflict), `"right"` or `"inner"` (keep only matching records).

After the merge `lab_a` now contains the combined inventory, written back to `lab_a.yaml`.

---

## Safe Persistence – Backups & Context Managers

YAMLDB writes to the file every time you call a mutating method. To guard against accidental corruption you can use the built-in context manager that creates a temporary backup:

```python
from cloudmesh.yaml.db import YamlDatabase

with YamlDatabase("catalog.yaml", backup=True) as db:
    db.insert_one({"name": "epsilon", "type": "sensor", "value": 9.1})
```

When `backup=True`, a file named `catalog.yaml.bak` is created before any write operation.

---

## Common Pitfalls & Debugging Tips

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **YAMLParseError** when loading a file | Indentation error or stray tab characters. | Run `yamllint yourfile.yaml` or open the file in a YAML-aware editor. |
| **Missing updates after `update_one`** | The query did not match any document (wrong field name). | Print `db.find_one(query)` before updating to confirm a match. |
| **Concurrent writes corrupt the file** | Two processes edit the same YAML simultaneously. | Serialize access (e.g., using `filelock` or the built-in backup/context manager). |
| **Performance slowdown with >10k records** | YAML is not a binary format; every operation reads the whole file. | Consider chunking the data into multiple files or switching to a proper DB for large scale. |

---

## Assignments

!!! note "Assignment 4.1 – Build a Mini-Catalog"
    1. **Data collection** – Create a YAML file named `books.yaml` that holds at least 12 books. Each record must contain:
       - `isbn` (string, unique)
       - `title`
       - `authors` (list of strings)
       - `year`
       - `tags` (list, e.g., `["science", "history"]`)
    2. **Queries** – Using `YamlDatabase`, write Python functions that answer the following:
       - `books_by_author(author_name)`
       - `books_between_years(start, end)`
       - `books_with_tag(tag)`
    3. **Update challenge** – Add a new tag `"classic"` to every book published before the year 2000, without rewriting the whole file manually.
    4. **Report** – Export the results of each query to separate JSON files.

!!! note "Assignment 4.2 – Concurrent-Write Simulation"
    Write a short script that spawns 5 Python threads. Each thread should:
    - Open the same `catalog.yaml` file via `YamlDatabase(…, backup=True)`.
    - Insert a unique record five times with a small random sleep between inserts.

    Verify that 25 new records exist and that the file is still valid YAML. Discuss how the backup/context manager handled the concurrent access.

---

## Self-Evaluation

??? note "How do you create a new YAML database in Python?"
    By instantiating the `YamlDatabase` class with the filename, e.g., `db = YamlDatabase("data.yaml")`.

??? note "What is the purpose of the `$gt` operator in a `find` query?"
    It stands for "greater than" and filters records where the specified field value is higher than the provided threshold.

??? note "How can you prevent data loss during a crash during write operations?"
    Use the context manager with `backup=True`, which creates a `.bak` file and restores it if an exception occurs.

??? note "What is the primary performance limitation of YAMLDB?"
    Since YAML is a text format, the entire file is read into memory for every operation, which causes slowdowns as the number of records grows (e.g., >10k records).

---

## Recap

| Concept | Quick Cheat-Sheet |
|---------|-------------------|
| **Installation** | `pip install cloudmesh-yamldb` |
| **Open / create DB** | `db = YamlDatabase("my.db")` |
| **Insert** | `db.insert_one(dict)`, `db.insert_many([dict,…])` |
| **Find** | `db.find(where={…}, order_by="field", limit=n)` |
| **Update** | `db.update_one(query, {"$set": {...}})` |
| **Delete** | `db.delete_one(query)` |
| **Merge** | `db1.merge(db2, on="key", how="left")` |
| **Backup** | `with YamlDatabase(file, backup=True) as db: …` |
