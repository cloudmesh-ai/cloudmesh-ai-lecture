# Appendix: Advanced Cline Skill Examples

!!! info "Learning Objectives"
    By studying these examples, you will be able to:

    * **Implement** skills that interact with external REST APIs.
    * **Develop** skills that wrap existing system CLI tools to provide structured data.
    * **Design** complex JSON output schemas that allow Cline to perform advanced reasoning.
    * **Handle** error states and API timeouts within a skill's execution loop.

---

## 1. Integration Skills: External API Interaction

Integration skills allow Cline to pull real-time data from the web into the local coding context.

### Example: GitHub Issue Fetcher (`skills/github_issues.py`)

This skill fetches the latest open issues from a specific GitHub repository.

```python
#!/usr/bin/env python3
import sys, json, urllib.request

def fetch_issues(repo):
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=5"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            issues = [{"title": i["title"], "url": i["html_url"]} for i in data]
            return {"status": "success", "issues": issues}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    repo_name = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-3"
    print(json.dumps(fetch_issues(repo_name)))
```

**Registry Entry (`cline.yaml`):**

```yaml
  github_issues:
    command: "./skills/github_issues.py"
    description: "Fetch the latest 5 open issues from a GitHub repository."
    args:
      - name: repo
        type: string
        required: true
        help: "GitHub repository in 'owner/repo' format."
```

---

## 2. Developer Utilities: Wrapping CLI Tools

Many powerful tools already exist in the shell. A Cline skill can act as a "wrapper" that converts messy CLI output into structured JSON.

### Example: Disk Usage Analyzer (`skills/disk_usage.sh`)

This bash skill wraps the `df` command to provide a clean JSON summary of disk health.

```bash
#!/bin/bash
# Extract the root partition usage
usage=$(df -h / | awk 'NR==2 {print $5}')
available=$(df -h / | awk 'NR==2 {print $4}')

echo "{\"partition\": \"/\", \"usage\": \"$usage\", \"available\": \"$available\"}"
```

**Registry Entry (`cline.yaml`):**

```yaml
  disk_usage:
    command: "./skills/disk_usage.sh"
    description: "Check the current disk usage of the root partition."
```

---

## 3. Data Transformation Skills

These skills take raw data and transform it into a format that is easier for a human or an AI to process.

### Example: JSON to Markdown Table (`skills/json_to_table.py`)

This skill takes a JSON list of objects and converts it into a formatted Markdown table.

```python
#!/usr/bin/env python3
import sys, json

def to_markdown_table(data):
    if not data or not isinstance(data, list):
        return "Error: Input must be a non-empty list of objects."
    
    headers = data[0].keys()
    header_row = "| " + " | ".join(headers) + " |"
    sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    body = []
    for item in data:
        row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
        body.append(row)
    
    return "\n".join([header_row, sep_row] + body)

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        print(json.dumps({"table": to_markdown_table(input_data)}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
```

**Registry Entry (`cline.yaml`):**

```yaml
  json_to_table:
    command: "./skills/json_to_table.py"
    description: "Convert a JSON list of objects into a Markdown table."
```

---

## Assignments

!!! note "Assignment 1: API Integration"
    **Task:** 

    1. Create a new skill that calls a public API (e.g., OpenWeatherMap, CoinGecko, or a random joke API).
    2. Ensure the skill returns a structured JSON object containing only the relevant data.
    3. Register the skill in `cline.yaml` with proper arguments.
    **Deliverable:** The script file and a screenshot of the successful `cline` invocation.

!!! note "Assignment 2: Tool Wrapper"
    **Task:** 

    1. Identify a CLI tool you use frequently (e.g., `git status`, `docker ps`, or `npm list`).
    2. Write a wrapper skill that parses the output of that tool and returns it as a JSON object.
    3. Use the skill to let Cline analyze the state of your system/project.
    **Deliverable:** The script and a screenshot showing Cline interpreting the JSON output.

!!! note "Assignment 3: Complex Chaining"
    **Task:** 

    1. Combine the `github_issues` skill (from this appendix) with the `json_to_table` skill.
    2. Execute a command that fetches issues and immediately transforms them into a Markdown table.
    3. Pipeline: `cline github_issues owner/repo | cline json_to_table`.
    **Deliverable:** A screenshot of the resulting Markdown table in your terminal.
