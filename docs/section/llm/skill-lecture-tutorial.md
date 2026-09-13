# Building Custom Skills for Cline: The Lecture Builder

!!! info "Learning Objectives"
    - Understand the architecture of Cline skills and how they are discovered, registered, and executed.
    - Implement a custom Python-based skill that processes command-line arguments to generate structured JSON data.
    - Configure a project directory and `cline.yaml` registry to integrate custom skills into the Cline environment.
    - Consume skill output for downstream automation, such as slide generation or markdown conversion.
    - Identify methods for extending basic skill functionality through external API integrations and templating.

Cline skills are modular, executable scripts that extend the agent's capabilities by allowing it to perform specialized tasks outside the core LLM loop. By implementing a skill, developers can create a deterministic interface for complex operations, ensuring consistent output formats and reducing the token overhead associated with prompting for structured data.

The "Lecture Builder" is a practical example of such a skill. It transforms a high-level specification—consisting of a topic, target audience, duration, and depth—into a structured lecture outline. By outputting this data in JSON format, the skill acts as a vendor-agnostic content generator that can be integrated into various downstream pipelines, such as slide generators (Marp, Reveal.js) or document converters.

## Architecture of a Cline Skill

A Cline skill is essentially any executable file located in a designated directory that the Cline agent can invoke via the shell.

### Discovery and Execution

Cline discovers skills based on the following mechanism:

1.  **Skill Directory**: By default, Cline looks for executable files in a `skills/` folder located in the project root. Alternatively, the `CLINE_SKILLS_PATH` environment variable can be used to specify a custom directory.
2.  **Executable Permissions**: For a script to be recognized as a skill, it must have the executable bit set. On Unix-like systems, this is achieved using `chmod +x <filename>`.
3.  **Invocation**: When a user or the agent calls `cline <skill_name>`, Cline executes the corresponding file in the skills directory, passing any provided arguments directly to the script.
4.  **Standard Output**: The primary communication channel is the standard output (stdout). Skills should emit their results—typically as JSON or plain text—to stdout, which Cline then captures and presents to the user.

## Implementing the Lecture Builder Skill

The Lecture Builder skill is implemented in Python, utilizing the standard library to ensure maximum portability without requiring external dependencies.

### Step 1: CLI Interface Design

The skill uses the `argparse` module to define a strict contract for inputs. This ensures that the skill receives all necessary parameters to generate a viable outline.

- `--topic`: The subject of the lecture.
- `--audience`: The target demographic (e.g., "beginners", "experts").
- `--duration`: The length of the session in minutes.
- `--depth`: The level of interactivity, which determines if a quiz is generated.

### Step 2: Outline Generation Logic

The core logic resides in a generation function that maps the input parameters to a structured dictionary. While the basic implementation uses a template, the architecture allows this function to be replaced with an LLM API call for dynamic content generation while maintaining the same output schema.

### Step 3: The Complete Implementation

Below is the full implementation of the `lecture_builder.py` skill.

```python
#!/usr/bin/env python3
import sys
import json
import argparse
from datetime import datetime

def generate_outline(topic, audience, duration, depth):
    """
    Generates a structured lecture outline based on input specifications.
    This template-driven approach ensures a consistent JSON schema.
    """
    # Estimate slide count: ~1 slide per 10 minutes (minimum 5 slides)
    slides_est = max(5, duration // 10)

    intro = f"Welcome & Motivation - Why {topic} matters for {audience}"
    agenda = "Agenda\n1. Context & Goals\n2. Core Concepts\n3. Hands-on Demo\n4. Common Pitfalls\n5. Q&A / Wrap-up"

    sections = [
        {
            "title": "Context & Goals",
            "points": [
                f"Define {topic}",
                "Real-world use-cases",
                "Learning objectives"
            ]
        },
        {
            "title": "Core Concepts",
            "points": [
                "Fundamental ideas",
                "Key terminology",
                "Simple examples"
            ]
        },
        {
            "title": "Hands-on Demo",
            "points": [
                "Step-by-step code walkthrough",
                "Live execution (Jupyter / REPL)",
                "Student exercise"
            ],
            "code_snippet": "# Example placeholder\nprint('Hello, data science!')"
        },
        {
            "title": "Common Pitfalls",
            "points": [
                "Typical mistakes",
                "Debugging tips",
                "Best-practice checklist"
            ]
        },
        {
            "title": "Q&A / Wrap-up",
            "points": [
                "Recap of key take-aways",
                "Further reading",
                "Assignment / next steps"
            ]
        }
    ]

    # Generate a quick-quiz only for hands-on sessions
    quiz = []
    if depth.lower() == "hands-on":
        quiz = [
            {
                "question": f"What is the first line you would write to import {topic.split()[0]}?",
                "answer": "import pandas as pd" if "pandas" in topic.lower() else "import numpy as np"
            },
            {
                "question": "Name one common pitfall when starting with this topic.",
                "answer": "Skipping data cleaning"
            }
        ]

    outline = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "topic": topic,
        "audience": audience,
        "duration_minutes": duration,
        "estimated_slides": slides_est,
        "intro_slide": intro,
        "agenda_slide": agenda,
        "sections": sections,
        "quiz": quiz
    }
    return outline

def main():
    parser = argparse.ArgumentParser(
        description="Generate a lecture / tutorial outline (JSON) for Cline")
    parser.add_argument("--topic", required=True, help="Lecture / tutorial topic")
    parser.add_argument("--audience", required=True, help="Target audience description")
    parser.add_argument("--duration", type=int, default=60,
                        help="Length in minutes (default: 60)")
    parser.add_argument("--depth", choices=["overview", "hands-on", "deep-dive"],
                        default="overview", help="Level of interactivity")
    args = parser.parse_args()

    outline = generate_outline(args.topic, args.audience,
                               args.duration, args.depth)

    # Emit clean JSON to stdout for Cline consumption
    print(json.dumps(outline, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## Skill Integration and Configuration

To integrate the skill into a Cline project, follow the structural and configuration steps below.

### Directory Structure

The skill must be placed in a `skills/` directory at the root of the project:

```
my-cline-project/
│
├─ cline.yaml                # Skill registry
│
├─ skills/                   # Skill implementation folder
│   └─ lecture_builder.py
│
└─ README.md
```

### Registration via cline.yaml

While Cline can automatically execute any file in the `skills/` folder, registering the skill in `cline.yaml` allows for richer help text and explicit argument definitions.

```yaml
skills:
  lecture_builder:
    command: "./skills/lecture_builder.py"
    description: "Generate a structured lecture / tutorial outline (JSON) from a short spec."
    args:
      - name: topic
        type: string
        required: true
        help: "Lecture or tutorial topic"
      - name: audience
        type: string
        required: true
        help: "Who will attend (e.g., 'undergrad beginners')"
      - name: duration
        type: int
        required: false
        default: 60
        help: "Length in minutes"
      - name: depth
        type: string
        required: false
        choices: ["overview", "hands-on", "deep-dive"]
        default: "overview"
        help: "Level of interactivity"
```

### Execution and Verification

After setting the executable permission, the skill can be invoked from the terminal:

```bash
chmod +x skills/lecture_builder.py
cline lecture_builder --topic "Introduction to Python for Data Science" --audience "undergraduate beginners" --duration 90 --depth hands-on
```

## Consuming Skill Output

The decision to use JSON as the output format enables the skill to be integrated into broader automation workflows.

### Filtering with jq

The `jq` utility can be used to extract specific parts of the generated outline for quick inspection:

```bash
cline lecture_builder --topic "Git Basics" --audience "Devs" | jq '.sections[].title'
```

### Downstream Integration

Because the output is structured, it can be piped into other tools:

- **Markdown Conversion**: A simple script can iterate through the `sections` array to create `##` headings.
- **Slide Generation**: The JSON can be mapped to a Marp or Reveal.js template to automatically generate presentation slides.
- **Database Storage**: The output can be stored in a database to track and version different iterations of a course outline.

## Extending Skill Functionality

The basic template-driven approach can be expanded to create more sophisticated tools.

| Extension Idea | Implementation Path |
| :--- | :--- |
| **AI-Generated Content** | Replace the `generate_outline` function with a call to an LLM API (e.g., OpenAI or Anthropic) using the input arguments as part of the prompt. |
| **Dynamic Slide Count** | Integrate a token-counting library (e.g., `tiktoken`) to estimate the actual length of the generated content. |
| **Image Suggestions** | Add an `image_url` field to each section by calling royalty-free image APIs like Unsplash. |
| **Template Support** | Use the `Jinja2` library to allow users to provide their own output templates instead of a hardcoded JSON structure. |
| **Multi-Format Export** | Add a `--format` flag to the CLI and integrate `pandoc` to support PDF, DOCX, or HTML exports. |

!!! tip "Summary Checklist"
    - [ ] Skill logic implemented in Python using `argparse` and `json`.
    - [ ] Script marked as executable via `chmod +x`.
    - [ ] `skills/` directory created in the project root.
    - [ ] `cline.yaml` registry configured for enhanced help and validation.
    - [ ] Skill execution verified via CLI output.
    - [ ] JSON output validated for schema consistency.

## Practical Exercises

!!! note "Exercise 1: Basic Skill Deployment"
    Implement the `lecture_builder.py` skill in a new Cline project. Run the skill using the CLI to generate an outline for a topic of your choice (e.g., "Introduction to Docker") and verify that the JSON output is correctly formatted.

!!! note "Exercise 2: Modifying the Schema"
    Modify the `lecture_builder.py` script to add a new command-line argument `--language` (e.g., "English", "French"). Update the `generate_outline` function to include this language in the final JSON output. Verify the change by running the skill with the new flag.

!!! note "Exercise 3: JSON to Markdown Pipeline"
    Create a small Python wrapper script that calls the `lecture_builder` skill using the `subprocess` module, parses the resulting JSON, and writes it to a file named `lecture.md`. The resulting markdown file should have the topic as the `#` title and each section as a `##` heading.

## Further Reading

- Python `argparse` Documentation: https://docs.python.org/3/library/argparse.html
- `jq` Manual: https://stedolan.github.io/jq/manual/
- Marp Markdown Presentation Ecosystem: https://marp.app
