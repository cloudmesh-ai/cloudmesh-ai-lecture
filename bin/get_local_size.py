import subprocess
import os

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def get_github_size():
    try:
        result = subprocess.run(
            ['curl', '-s', 'https://api.github.com/repos/cloudmesh-ai/cloudmesh-ai-lecture'],
            capture_output=True,
            text=True,
            check=True
        )
        import json
        data = json.loads(result.stdout)
        return data.get('size')
    except Exception as e:
        print(f"Error fetching GitHub size: {e}")
        return None


def get_local_folder_size():
    total_size = 0
    local_dir = 'LOCAL'
    if os.path.exists(local_dir):
        for dirpath, dirnames, filenames in os.walk(local_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
    return total_size


def get_size():
    try:
        # Use git ls-files to list all files tracked by git or not ignored
        # -c: cached (tracked files)
        # -o: others (untracked files)
        # --exclude-standard: use .gitignore, .git/info/exclude, and global gitignore
        result = subprocess.run(
            ['git', 'ls-files', '-c', '-o', '--exclude-standard'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.splitlines()
        
        total_size = 0
        for file_path in files:
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
        
        return total_size
    except subprocess.CalledProcessError as e:
        print(f"Error running git ls-files: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    local_size = get_size()
    if local_size is not None:
        print(f"Local size (ignoring gitignore): {format_size(local_size)}")
    
    local_folder_size = get_local_folder_size()
    print(f"Local size (LOCAL folder): {format_size(local_folder_size)}")
    
    github_size = get_github_size()
    if github_size is not None:
        print(f"Github size: {format_size(github_size)}")
