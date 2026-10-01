import os
import re

def check_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    issues = []
    for i in range(len(lines)):
        line = lines[i]
        # Admonition header
        if line.startswith('!!!'):
            if i + 1 < len(lines):
                next_line = lines[i+1]
                # Rule 1: Blank line between header and content
                if next_line.strip() != "" and next_line.startswith('    '):
                    issues.append(f"Line {i+1}: Admonition missing blank line before content")
                elif next_line.strip() != "" and not next_line.startswith('    '):
                    issues.append(f"Line {i+1}: Admonition content not indented by 4 spaces")
        
        # Details block header
        if line.startswith('???'):
            if i + 1 < len(lines):
                next_line = lines[i+1]
                # Rule 2: Content starts on next line, indented 4 spaces
                if next_line.strip() == "":
                    issues.append(f"Line {i+1}: Details block should NOT have blank line before content")
                elif not next_line.startswith('    '):
                    issues.append(f"Line {i+1}: Details block content not indented by 4 spaces")

    return issues

with open('batch_aa', 'r') as f:
    files = [line.strip() for line in f if line.strip()]

for file_path in files:
    if os.path.exists(file_path):
        issues = check_file(file_path)
        if issues:
            print(f"{file_path}:")
            for issue in issues:
                print(f"  {issue}")
