import re
import os

def format_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Rule 3: Self-Assessment Redundancy
        # Check if we are in a Self-Assessment section
        if line.strip() == "## Self-Assessment" or line.strip() == "## Self Assessment":
            new_lines.append(line)
            i += 1
            # Look for redundant !!! tip "Self-Assessment"
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped == '!!! tip "Self-Assessment"' or stripped == '!!! tip "Self Assessment"':
                    # Skip the header and the indented content
                    i += 1
                    while i < len(lines) and (not lines[i].strip() or lines[i].startswith(' ')):
                        i += 1
                    changed = True
                    break
                elif stripped and not stripped.startswith(' '):
                    break
                else:
                    i += 1
            continue

        # Rule 1: Admonitions (!!!)
        if line.startswith('!!!'):
            new_lines.append(line)
            i += 1
            # Ensure blank line
            if i < len(lines) and lines[i].strip():
                new_lines.append('\n')
                changed = True
            
            # Ensure indentation of content
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith(' ')):
                l = lines[i]
                if l.strip():
                    if not l.startswith('    '):
                        l = '    ' + l.lstrip()
                        changed = True
                new_lines.append(l)
                i += 1
            continue

        # Rule 2 & 4: Details Blocks (???)
        if line.startswith('???'):
            # Flattening nested questions: if we see a ??? question, it should be at the start of the line.
            # If it's indented, it should have been handled by the parent's loop or it's a mistake.
            # The rule says "Ensure subsequent ??? question blocks start at the beginning of the line".
            
            # If this is the redundant "Self Assessment" wrapper, remove it
            if 'question "Self Assessment"' in line or 'question "Self-Assessment"' in line:
                i += 1
                # Skip its content until the next ??? question or a non-indented line
                while i < len(lines) and (not lines[i].strip() or lines[i].startswith(' ')):
                    if lines[i].strip().startswith('??? question'):
                        break
                    i += 1
                changed = True
                continue

            new_lines.append(line)
            i += 1
            # Ensure indentation of content
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith(' ')):
                l = lines[i]
                if l.strip():
                    # If we encounter another ??? question, stop and let the outer loop handle it
                    if l.strip().startswith('???'):
                        break
                    if not l.startswith('    '):
                        l = '    ' + l.lstrip()
                        changed = True
                new_lines.append(l)
                i += 1
            continue

        new_lines.append(line)
        i += 1

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    return changed

def main():
    with open('batch_ad', 'r') as f:
        files = [line.strip() for line in f if line.strip() and line.strip().endswith('.md')]
    
    modified = []
    for f in files:
        if os.path.exists(f):
            if format_file(f):
                modified.append(f)
    
    print(f"Modified files: {len(modified)}")
    for m in modified:
        print(m)

if __name__ == "__main__":
    main()
