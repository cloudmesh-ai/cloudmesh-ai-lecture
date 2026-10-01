import os
import re
from pathlib import Path

# Regex to find markdown links: [text](url)
LINK_REGEX = re.compile(r'\[.*?\]\((.*?)\)')

# Docs root directory
DOCS_ROOT = Path('docs')

def is_external(url):
    return url.startswith(('http://', 'https://', 'mailto:', 'ftp://'))

def verify_links():
    all_md_files = list(Path('.').rglob('*.md'))
    broken_links = []
    should_be_absolute = []

    for md_file in all_md_files:
        if 'verify_links' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Could not read {md_file}: {e}")
            continue

        links = LINK_REGEX.findall(content)
        for link in links:
            # Strip anchor/query params
            clean_link = link.split('#')[0].split('?')[0]
            
            if not clean_link or is_external(clean_link):
                continue

            # Absolute link check
            if clean_link.startswith(('/section', '/lecture')):
                target_path = DOCS_ROOT / clean_link.lstrip('/')
                if not target_path.exists():
                    broken_links.append((md_file, link, target_path))
            else:
                # Relative link
                try:
                    target_path = (md_file.parent / clean_link).resolve()
                    
                    # Check if it points to docs/section or docs/lecture
                    # Resolve the absolute path of the target and see if it's under docs/section or docs/lecture
                    docs_root_abs = DOCS_ROOT.resolve()
                    if target_path.is_relative_to(docs_root_abs):
                        rel_to_root = target_path.relative_to(docs_root_abs)
                        if str(rel_to_root).startswith(('section', 'lecture')):
                            should_be_absolute.append((md_file, link, rel_to_root))
                    
                    if not target_path.exists():
                        broken_links.append((md_file, link, target_path))
                except Exception:
                    broken_links.append((md_file, link, "Invalid Path"))

    return broken_links, should_be_absolute

if __name__ == "__main__":
    broken, should_abs = verify_links()
    if not broken and not should_abs:
        print("All links are correct!")
    else:
        if broken:
            print("\n--- Broken Links ---")
            for src, link, target in broken:
                print(f"{src} -> {link} (Target: {target})")
        if should_abs:
            print("\n--- Should be Absolute Links (pointing to /section or /lecture) ---")
            for src, link, rel_root in should_abs:
                print(f"{src} -> {link} (Suggested: /{rel_root})")
