import os
import re
from pathlib import Path

LINK_REGEX = re.compile(r'(\[.*?\]\()(.+?)(\))')
DOCS_ROOT = Path('docs')

def is_external(url):
    return url.startswith(('http://', 'https://', 'mailto:', 'ftp://'))

def fix_links():
    all_md_files = list(Path('.').rglob('*.md'))
    files_changed = 0

    for md_file in all_md_files:
        if 'auto_fix_links' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Could not read {md_file}: {e}")
            continue

        new_content = content
        
        # We find all links and process them
        # Using finditer to avoid issues with replacements changing offsets
        matches = list(LINK_REGEX.finditer(content))
        
        # Process matches in reverse to maintain offsets
        for match in reversed(matches):
            prefix, link, suffix = match.groups()
            
            # Strip anchor
            clean_link = link.split('#')[0].split('?')[0]
            anchor = link[len(clean_link):]
            
            if not clean_link or is_external(clean_link):
                continue

            # If it's already absolute, we don't change it here (just verify it exists in a separate pass)
            if clean_link.startswith(('/section', '/lecture')):
                continue

            # Resolve relative link
            try:
                target_path = (md_file.parent / clean_link).resolve()
                docs_root_abs = DOCS_ROOT.resolve()
                
                if target_path.is_relative_to(docs_root_abs):
                    rel_to_root = target_path.relative_to(docs_root_abs)
                    rel_str = str(rel_to_root)
                    
                    if rel_str.startswith(('section', 'lecture')):
                        # It should be an absolute link
                        abs_link = '/' + rel_str + anchor
                        
                        # Only replace if the target actually exists
                        if target_path.exists():
                            # Replace only this specific link
                            start, end = match.span(2)
                            new_content = new_content[:start] + abs_link + new_content[end:]
            except Exception:
                continue

        if new_content != content:
            md_file.write_text(new_content, encoding='utf-8')
            files_changed += 1
            print(f"Fixed links in {md_file}")

    return files_changed

if __name__ == "__main__":
    changed = fix_links()
    print(f"Changed {changed} files.")
