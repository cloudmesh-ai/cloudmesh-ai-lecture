import os
import re

def check_files():
    list_pattern = re.compile(r'^\s*([-*+]|\d+\.)\s+')
    violations = []

    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i in range(len(lines) - 1):
                            current_line = lines[i].strip()
                            next_line = lines[i+1]
                            
                            if current_line and list_pattern.match(next_line):
                                violations.append((file_path, i + 1))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return violations

if __name__ == "__main__":
    results = check_files()
    if not results:
        print("No violations found.")
    else:
        for path, line in results:
            print(f"{path}:{line}")
