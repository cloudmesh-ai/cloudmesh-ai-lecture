#!/usr/bin/env python3
import re
import os
import sys

def extract_paths_from_yaml(content):
    """
    A simple, regex-based parser to extract file paths from the 'nav' section of mkdocs.yml.
    """
    nav_start = content.find('nav:')
    if nav_start == -1:
        return []

    nav_content = content[nav_start + 4:]
    
    paths = []
    # Improved regex to handle paths more accurately
    pattern = re.compile(r'(?:[:\s]\s*|^)([a-zA-Z0-9._/-]+\.md)')
    
    for line in nav_content.splitlines():
        if line.strip() and (line.startswith(' ') or line.startswith('\t')):
            match = pattern.search(line)
            if match:
                paths.append(match.group(1))
                
    return paths

def main():
    mkdocs_path = 'mkdocs.yml'
    if not os.path.exists(mkdocs_path):
        print(f"Error: {mkdocs_path} not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(mkdocs_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    all_files = extract_paths_from_yaml(content)
    
    if not all_files:
        print("No navigation files found to check.", file=sys.stderr)
        sys.exit(1)

    # IMPORTANT: Linkinator expects paths relative to where it's run.
    # The Docker container is run with -v "$(pwd)":/app -w /app
    # Our mkdocs.yml paths are usually like 'section/devops/devops.md'
    # Linkinator should be able to find them if we pass them correctly.
    
    md_files = sorted(list(set(all_files)))
    
    # We print the files. We also include 'index.md' explicitly if it's missing 
    # but common, though our regex should find it if it's in the nav.
    
    print(" ".join(md_files))

if __name__ == "__main__":
    main()
