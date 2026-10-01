import os
import re

base_dir = 'docs/section/llm'
file_map = {
    'llm-service.md': 'services/llm-service.md',
    'llm-white.md': 'services/llm-white.md',
    'llm-routing.md': 'services/llm-routing.md',
    'llm-buisiness.md': 'services/llm-buisiness.md',
    'llm-gpu-service.md': 'services/llm-gpu-service.md',
    'llm-spark.md': 'hardware/llm-spark.md',
    'llm-jetstream.md': 'hardware/llm-jetstream.md',
    'llm-cpu-all.md': 'hardware/llm-cpu-all.md',
    'llm-amsc.md': 'hardware/llm-amsc.md',
    'openclaw.md': 'hardware/openclaw.md',
    'agentic-ai.md': 'agents/agentic-ai.md',
    'langchain.md': 'agents/langchain.md',
    'slang.md': 'agents/slang.md',
    'skill-lecture-tutorial.md': 'skills/skill-lecture-tutorial.md',
    'cline-skills.md': 'skills/cline-skills.md',
    'cline-skills-appendix.md': 'skills/cline-skills-appendix.md',
    'skills-llm-jetstream.md': 'skills/skills-llm-jetstream.md',
    'claude-code.md': 'cli/claude-code.md',
    'codex.md': 'cli/codex.md',
    'gemini.md': 'cli/gemini.md',
    'opencode.md': 'cli/opencode.md',
    'opencode-new.md': 'cli/opencode-new.md',
    'opencode-skills.md': 'cli/opencode-skills.md',
    'skills-guide.md': 'cli/skills-guide.md',
    'lmlink.md': 'lms/lmlink.md',
    'llm-link-ansible.md': 'lms/llm-link-ansible.md',
    'lm-link-studi-vscode.md': 'lms/lm-link-studi-vscode.md',
    'lmlink-gemini.md': 'lms/lmlink-gemini.md',
    'lmlink2.md': 'lms/lmlink2.md',
    'lmlink3.md': 'lms/lmlink3.md',
}

def update_links(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Find all markdown links [text](url)
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        
        # We only care about links to .md files that don't start with http, /, or ../
        if url.endswith('.md') and not (url.startswith('http') or url.startswith('/') or url.startswith('..')):
            # Extract filename from url (e.g., 'llm-service.md' or 'cli/claude-code.md')
            filename = os.path.basename(url)
            if filename in file_map:
                new_rel_path = file_map[filename]
                
                # Calculate relative path from current file's directory to the new_rel_path
                curr_dir = os.path.dirname(file_path)
                # Relative to base_dir
                rel_curr_dir = os.path.relpath(curr_dir, base_dir)
                
                if rel_curr_dir == '.':
                    # File is in base_dir (like llm-chapter.md), so new_rel_path is correct
                    final_url = new_rel_path
                else:
                    # File is in a subdirectory, need to go up one level first
                    # If the file is in a deep subdir, we might need more ../
                    # But our structure is only 1 level deep (except examples)
                    depth = rel_curr_dir.count(os.sep) + 1
                    prefix = '../' * depth
                    final_url = prefix + new_rel_path
                
                return f'[{text}]({final_url})'
        
        return match.group(0)

    new_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        return True
    return False

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md'):
            update_links(os.path.join(root, file))

