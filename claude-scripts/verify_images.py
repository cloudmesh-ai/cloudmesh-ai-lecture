import os
import re

def check_images():
    # Find all files in docs
    all_files = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                all_files.append(os.path.join(root, file))

    broken = []
    
    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Regex for images: ![alt](path)
        images = re.findall(r'!\[.*?\]\((.*?)\)', content)
        
        for img_path in images:
            # Only check image files
            if not any(img_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                continue
                
            # Resolve path
            actual_path = None
            if img_path.startswith('/'):
                # Absolute path from root of docs (assuming /section -> docs/section)
                # The project structure has docs/ at the root
                resolved = img_path.lstrip('/')
                # If the link is /section/... it should be docs/section/...
                # But in the repo, it's docs/section/...
                # Let's try common mappings
                potential = [
                    os.path.join('docs', resolved),
                    resolved # in case it's already relative to root
                ]
                for p in potential:
                    if os.path.exists(p):
                        actual_path = p
                        break
            else:
                # Relative path
                dir_name = os.path.dirname(file_path)
                potential = os.path.join(dir_name, img_path)
                if os.path.exists(potential):
                    actual_path = potential
            
            if not actual_path:
                broken.append((file_path, img_path))
                
    return broken

if __name__ == "__main__":
    broken_links = check_images()
    if broken_links:
        print("Broken Image Links Found:")
        for file, link in broken_links:
            print(f"{file} -> {link}")
    else:
        print("All image links verified!")
