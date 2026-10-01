import os
import re

def fix_image_links():
    # Find all markdown files in docs
    all_files = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                all_files.append(os.path.join(root, file))

    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all images: ![alt](path)
        images = re.findall(r'(!\[.*?\]\((.*?)\))', content)
        if not images:
            continue

        new_content = content
        changed = False

        for full_match, img_path in images:
            # Only process image files
            if not any(img_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                continue

            # 1. Absolute paths starting with /section/ or /lecture/
            if img_path.startswith('/section/') or img_path.startswith('/lecture/'):
                # If the file is in docs/section/something, /section/images/x.png should be images/x.png
                # if it's in the same directory level as the images folder.
                
                # Let's check if the image exists at the absolute path (relative to docs root)
                resolved_path = os.path.join('docs', img_path.lstrip('/'))
                if os.path.exists(resolved_path):
                    # Try to convert to relative 'images/...' path
                    # Get directory of current file
                    current_dir = os.path.dirname(file_path)
                    
                    # If the image is in a subdirectory called 'images' of the same folder
                    # we want to replace /section/path/to/folder/images/img.png with images/img.png
                    if '/images/' in img_path:
                        parts = img_path.split('/images/')
                        img_name = parts[-1]
                        
                        # Check if images/img_name exists relative to current file
                        if os.path.exists(os.path.join(current_dir, 'images', img_name)):
                            new_img_path = f"images/{img_name}"
                            new_content = new_content.replace(img_path, new_img_path)
                            changed = True
                continue

            # 2. Relative paths that don't start with images/ but should
            if not img_path.startswith('images/') and not img_path.startswith('..'):
                # Check if adding 'images/' makes it exist
                if os.path.exists(os.path.join(os.path.dirname(file_path), 'images', img_path)):
                    new_content = new_content.replace(img_path, f"images/{img_path}")
                    changed = True

        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated image links in {file_path}")

if __name__ == "__main__":
    fix_image_links()
