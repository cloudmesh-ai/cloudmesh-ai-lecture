import re

file_path = "/Users/grey/work/cloudmesh-ai-lecture/docs/section/rest/rest-new.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace icon numbers (1️⃣, etc.) with regular numbers
icon_map = {
    "1️⃣": "1", "2️⃣": "2", "3️⃣": "3", "4️⃣": "4", "5️⃣": "5", 
    "6️⃣": "6", "7️⃣": "7", "8️⃣": "8", "9️⃣": "9", "🔟": "10"
}
for icon, num in icon_map.items():
    content = content.replace(icon, num)

# 2. Replace table emojis with text for better readability
content = content.replace("✅", "Yes")
content = content.replace("❌", "No")

# 3. Remove remaining emojis
# Remove most common emoji ranges
content = re.sub(r'[\U00010000-\U0010ffff]', '', content)

# 4. Process Assignments section
if "!!! Assignments" in content:
    parts = content.split("!!! Assignments", 1)
    before = parts[0]
    after = parts[1]
    
    # Find assignments starting with "    1. ", "    2. ", etc.
    pattern = r'\n\s*(\d+)\.\s+'
    matches = list(re.finditer(pattern, after))
    
    if matches:
        processed_after = ""
        for i in range(len(matches)):
            start_of_marker = matches[i].start()
            end_of_marker = matches[i].end()
            
            next_match_start = matches[i+1].start() if i+1 < len(matches) else len(after)
            
            num = matches[i].group(1)
            assignment_text = after[end_of_marker:next_match_start].strip()
            
            processed_after += f'\n\n!!! note "Assignment {num}"\n\n{assignment_text}\n'
        
        # We need to check if there was any text before the first assignment in the 'after' part
        # but usually "!!! Assignments" is followed by the list.
        # Also we need to preserve text that comes after the last assignment (e.g. "Submit your solutions...")
        
        # Wait, the loop above consumes everything up to the end of 'after'.
        # If "Submit your solutions" was part of the last assignment's text, it's fine.
        # If it was after the last match, it's already included in the last `assignment_text`.
        
        content = before + processed_after
    else:
        # If no matches found, just keep it as is but without the marker
        content = before + after

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
