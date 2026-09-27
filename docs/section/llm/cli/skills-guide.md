# Guide to Creating Custom Skills for Cline

A **Skill** in the Cline ecosystem is a self-contained executable script (written in any language like Python, Bash, or Node.js) that performs a specific task and returns structured output (usually JSON).

## 1. Example Skill: `system_info.py`
This skill collects basic system information (OS and Python version) and returns it as a JSON object.

### The Code
Create a file named `system_info.py` with the following content:

```python
#!/usr/bin/env python3
import sys
import json
import platform

def main():
    # Collect system data
    data = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version.split()[0],
        "architecture": platform.machine()
    }
    
    # Skills must output their result to stdout, preferably as JSON
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
```

---

## 2. Where to place it?

You have two options depending on whether you want the skill available only for one project or for all projects on your machine.

### Option A: Locally (Project-specific)
Place the skill in a `skills/` directory at the root of your current project.
- **Path:** `/your-project/skills/system_info.py`
- **Benefit:** The skill is version-controlled with your project and shared with other team members via Git.

### Option B: Globally (Across all projects)
Place the skill in a dedicated folder on your system and tell Cline where to find it.
1. Create a global folder: `mkdir -p ~/.cline/skills`
2. Move the file there: `mv system_info.py ~/.cline/skills/`
3. Set the environment variable in your `.bashrc` or `.zshrc`:
   ```bash
   export CLINE_SKILLS_PATH="$HOME/.cline/skills"
   ```
- **Benefit:** You don't have to duplicate common utility skills in every project.

---

## 3. Activation & Registration

### Step 1: Make it executable
Regardless of where you place it, the file **must** have execution permissions:
```bash
chmod +x skills/system_info.py 
# or for global: chmod +x ~/.cline/skills/system_info.py
```

### Step 2: Register the skill (Optional but Recommended)
While files in the `skills/` folder are discovered automatically, creating a `cline.yaml` file in your project root allows you to provide a description and define arguments, which helps the AI use the skill more accurately.

**`cline.yaml`**
```yaml
skills:
  system_info:
    command: "./skills/system_info.py"
    description: "Retrieve basic operating system and environment information."
    args: [] # No arguments needed for this specific skill
```

---

## 4. How to use it
Once placed and made executable, you can invoke the skill from your terminal:

```bash
cline system_info
```

**Expected Output:**
```json
{
  "os": "Darwin",
  "os_release": "23.0.0",
  "python_version": "3.11.5",
  "architecture": "arm64"
}
```

## Summary Checklist
| Item | Local Placement | Global Placement |
| :--- | :--- | :--- |
| **Directory** | `./skills/` | Any dir defined by `CLINE_SKILLS_PATH` |
| **Permissions** | `chmod +x` | `chmod +x` |
| **Registry** | `cline.yaml` in root | Not required (or global registry) |
| **Invocation** | `cline <filename>` | `cline <filename>` |
