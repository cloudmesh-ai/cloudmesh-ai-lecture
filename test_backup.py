import subprocess
import datetime
import sys
from pathlib import Path

def get_latest_backup_path() -> Path | None:
    """Run `tmutil latestbackup` and return the Path object, or None if nothing."""
    try:
        out = subprocess.check_output(["tmutil", "latestbackup"], text=True).strip()
        return Path(out) if out else None
    except subprocess.CalledProcessError:
        return None

def get_mod_time(p: Path) -> datetime.datetime:
    """Return the modification time of the path as a naive datetime (local time)."""
    ts = p.stat().st_mtime   # seconds since epoch
    return datetime.datetime.fromtimestamp(ts)

def main():
    latest = get_latest_backup_path()
    if not latest:
        sys.stderr.write("⛔ No Time Machine backups found.\n")
        sys.exit(1)

    when = get_mod_time(latest)
    print(f"🕒 Last Time Machine backup: {when:%Y-%m-%d %H:%M:%S}")

if __name__ == "__main__":
    main()
