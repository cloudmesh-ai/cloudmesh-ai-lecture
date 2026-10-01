import os
import re

def fix_indentation(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match !!! [type] "Assignment ..."
        if re.match(r'^\s*!!!\s+\w+\s+".*Assignment.*"', line):
            new_lines.append(line)
            i += 1
            
            # Ensure blank line after header
            if i < len(lines) and lines[i].strip() != "":
                new_lines.append("\n")
            
            # Indent content until next block or header
            while i < len(lines):
                curr_line = lines[i]
                # Stop if we hit another admonition, a header, or a horizontal rule
                if re.match(r'^\s*(!\?\?\s*|!!!\s*|#\s*|---)', curr_line):
                    break
                
                # Indent if not already indented by 4 spaces
                if curr_line.strip() == "":
                    new_lines.append("\n")
                elif not curr_line.startswith("    "):
                    new_lines.append("    " + curr_line)
                else:
                    new_lines.append(curr_line)
                i += 1
        else:
            new_lines.append(line)
            i += 1
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

files = [
    "docs/section/cloud/fundamentals/virtualization.md",
    "docs/section/network/network.md",
    "docs/lecture/assignments/assignments.md"
]

for f in files:
    if os.path.exists(f):
        fix_indentation(f)
        print(f"Fixed {f}")
