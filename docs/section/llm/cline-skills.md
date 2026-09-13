# Extending Cline with Custom Skills

!!! info "Learning Objectives"
    By the end of this section, you will be able to:

    * **Understand** the architecture of Cline skills and how they extend the AI's capabilities.
    * **Develop** reusable skills using various programming languages (Python, Bash, etc.).
    * **Register** and manage skills using the `skills/` directory and `cline.yaml` registry.
    * **Invoke** and chain skills from the terminal to build complex AI workflows.
    * **Implement** the Cline output contract to ensure structured and predictable results.

---

## How Cline Works with Skills

Cline's extensibility allows you to move beyond general-purpose prompts by providing the AI with specialized, programmable "skills" (reusable functions or plugins).

| Concept | What it means for Cline |
| :--- | :--- |
| **Skill** | A self-contained piece of logic (function, script, API call) that performs a specific task – e.g., “summarise a document” or “look up a stock price”. |
| **Skill Registration** | Exposing the skill via a **skill-registry file** (`cline.yaml`) or by placing the script in a designated **`skills/`** folder. |
| **Invocation Syntax** | Calling the skill from the terminal: `cline summarise --file report.txt`. |
| **Parameters & Output** | Skills define their own arguments and return structured output (JSON or plain text). |
| **Composability** | Skills can be chained using standard shell pipes: `cline fetch-price TSLA \| cline trend-plot`. |
| **Extensibility** | Any language executable from the shell (Python, Node.js, Bash, Go) can be a skill. |
| **Built-in Helpers** | Optional libraries (like `cline-skills` for Python) that simplify argument parsing and JSON validation. |

---

## Step-by-Step Implementation

Follow these steps to create and deploy your first custom skills.

### 1. Create a simple Python skill

First, create a file at `skills/summarise.py`. This skill uses a transformer pipeline to summarize text files.

```python
#!/usr/bin/env python3
import sys, json, pathlib
from transformers import pipeline

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error":"Usage: summarise <path-to-text-file>"}))
        sys.exit(1)

    path = pathlib.Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    summariser = pipeline("summarization")
    summary = summariser(text, max_length=120, min_length=30, do_sample=False)[0]["summary_text"]

    print(json.dumps({"summary": summary.strip()}))

if __name__ == "__main__":
    main()
```

### 2. Make the skill executable

For Cline to discover and run the skill, the file must have execution permissions.

```bash
chmod +x skills/summarise.py
```

### 3. Register the skill in the registry

While files in `skills/` are automatically discovered, using a `cline.yaml` registry allows you to provide rich descriptions and argument validation.

```yaml
skills:
  summarise:
    command: "./skills/summarise.py"
    description: "Generate a concise summary of a text file using an LLM."
    args:
      - name: file
        type: string
        required: true
        help: "Path to the .txt file to summarise"
```

### 4. Invoke the skill from the terminal

You can now call your skill directly.

```bash
$ cline summarise report.txt
{
  "summary": "The quarterly report shows a 12% revenue increase driven by..."
}
```

You can also pipe the result to other tools for further processing:

```bash
$ cline summarise report.txt | jq -r .summary | clip
```

---

## Project Architecture and Configuration

### Typical Project Layout

Organizing your skills in a consistent structure ensures maintainability as your library grows.

```
my-cline-project/
│
├─ cline.yaml                # Optional central registry
│
├─ skills/                   # <-- Put every skill file here
│   ├─ summarise.py
│   ├─ fetch_price.py
│   ├─ plot_trend.sh
│   └─ … (any language)
│
├─ venv/                     # Optional virtual-env for Python skills
│
└─ README.md
```

* **`skills/`**: Any file that is **executable** (`chmod +x`) in this folder is automatically discoverable.
* **`cline.yaml`**: Optional; used for adding rich descriptions and argument validation.

### Advanced Registry Configuration

For complex skills, use the registry to define mandatory arguments and help text.

```yaml
skills:
  summarise:
    command: "./skills/summarise.py"
    description: "Summarise a plain-text file with an LLM."
    args:
      - name: file
        type: string
        required: true
        help: "Path to the .txt file to summarise."
  fetch_price:
    command: "./skills/fetch_price.py"
    description: "Get the latest stock price for a ticker symbol."
    args:
      - name: ticker
        type: string
        required: true
        help: "Stock ticker symbol, e.g. AAPL."
```

### Global Skills Path

To make skills available across all your projects without duplicating files, set the `CLINE_SKILLS_PATH` environment variable.

```bash
export CLINE_SKILLS_PATH="/opt/my-shared-skills"
```

---

## Minimal Example: Hello World

A minimal skill requires no registry entry; the filename itself becomes the skill name.

Create `skills/hello.py`:

```python
#!/usr/bin/env python3
import sys, json

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "world"
    print(json.dumps({"message": f"Hello, {name}!"}))

if __name__ == "__main__":
    main()
```

**Activation and Usage:**

```bash
chmod +x skills/hello.py
$ cline hello Alice
{
  "message": "Hello, Alice!"
}
```

---

## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the basic requirement for a script to be discoverable as a Cline skill?"
    Place the script in the `skills/` directory (or a path defined by `CLINE_SKILLS_PATH`) and ensure it has execution permissions (`chmod +x`).

??? question "What is the purpose of the `cline.yaml` registry file?"
    It allows you to provide rich descriptions and argument validation for skills, improving the AI's ability to use them correctly.

??? question "How do you invoke a registered Cline skill from the terminal?"
    Use the syntax `cline <skill-name>`, where `<skill-name>` is the filename (without extension) of the skill script.

??? question "How can you make your Cline skills available across different projects without duplicating files?"
    Set the `CLINE_SKILLS_PATH` environment variable to point to a shared directory containing your skill scripts.

---

## Assignments

!!! note "Assignment 1: Your First Skill"
    **Task:** 

    1. Create a `skills/` directory.
    2. Write a simple Python or Bash script called `system_info` that returns the current OS and uptime in JSON format.
    3. Make the script executable.
    4. Run it using `cline system_info`.
    **Deliverable:** The source code of the script and a screenshot of the terminal output.

!!! note "Assignment 2: Registry and Validation"
    **Task:** 

    1. Create a `cline.yaml` file.
    2. Register your `system_info` skill with a detailed description and a required argument (e.g., `--detail`).
    3. Test the skill with and without the argument to verify that the registry handles the input.
    **Deliverable:** The `cline.yaml` file and a screenshot showing the help text when the argument is missing.

!!! note "Assignment 3: Skill Chaining"
    **Task:** 

    1. Create a second skill (e.g., `uppercase`) that takes a JSON string and returns the text in all caps.
    2. Chain the two skills together using a pipe: `cline system_info | cline uppercase`.
    **Deliverable:** A screenshot of the chained command output.
