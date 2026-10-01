import os
import re
from pathlib import Path

# Replacements to make
REPLACEMENTS = {
    '/section/devops/make-wsl2.md': '/section/devops/make.md',
    '/section/devops/ansible-need.md': '/section/devops/ansible.md',
}

def fix_links():
    all_md_files = list(Path('.').rglob('*.md'))
    files_changed = 0

    for md_file in all_md_files:
        if 'final_link_fixes' in str(md_file) or 'verify_links' in str(md_file) or 'auto_fix_links' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Could not read {md_file}: {e}")
            continue

        new_content = content
        changed = False
        for old, new in REPLACEMENTS.items():
            if old in new_content:
                new_content = new_content.replace(old, new)
                changed = True
        
        if changed:
            md_file.write_text(new_content, encoding='utf-8')
            files_changed += 1
            print(f"Updated links in {md_file}")

    return files_changed

if __name__ == "__main__":
    changed = fix_links()
    print(f"Updated {changed} files.")
