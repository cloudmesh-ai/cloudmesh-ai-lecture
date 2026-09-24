#!/usr/bin/env python
"""
Meeting Countdown Widget
Usage:
  session-timer.py run [options]
  session-timer.py add <name> <day> <start> <stop> [options]
  session-timer.py list [options]
  session-timer.py remove <name> [options]
  session-timer.py (-h | --help)
  session-timer.py --version
Options:
  -h --help                Show this help message.
  --version                Show version.
  --config=PATH            Path to YAML file that stores meetings.
                           [default: ~/.meeting_countdown.yaml]
Example (new compact syntax):
  - name: Team Sync
    day: 2024-10-02
    start: 5:15pm
    stop: 7:45pm
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------
import argparse
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

# ----------------------------------------------------------------------
# Third‑party imports
# ----------------------------------------------------------------------
import PySimpleGUI as sg      # FreeSimpleGUI works the same – just change the import
import yaml                  # pip install pyyaml

# ----------------------------------------------------------------------
# Logging – tiny file in the home folder, handy for debugging
# ----------------------------------------------------------------------
log_path = Path.home() / ".meeting_countdown.log"
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Persistence helpers (YAML)
# ----------------------------------------------------------------------
def load_meetings(cfg: Path) -> List[dict]:
    """Return a list of raw dicts from the YAML file (empty list if missing)."""
    if cfg.is_file():
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            return data or []
        except Exception as exc:               # pragma: no cover
            log.error("Failed to read %s – %s", cfg, exc)
    return []


def save_meetings(cfg: Path, data: List[dict]) -> None:
    """Write ``data`` (list of dicts) to ``cfg`` as YAML."""
    try:
        cfg.write_text(
            yaml.safe_dump(
                data, sort_keys=False, explicit_start=True, indent=2
            ),
            encoding="utf-8",
        )
    except Exception as exc:                   # pragma: no cover
        log.error("Failed to write %s – %s", cfg, exc)

# ----------------------------------------------------------------------
# Time‑zone helpers
# ----------------------------------------------------------------------
try:
    # Python 3.9+ – built‑in IANA zone database
    from zoneinfo import ZoneInfo          # std‑lib
except ImportError:                         # pragma: no cover
    # Back‑port for older versions (install via `pip install backports.zoneinfo`)
    from backports.zoneinfo import ZoneInfo


def resolve_tz(tz_name: str) -> timezone:
    """
    Convert a user‑supplied string into a ``tzinfo`` object.

    * Full IANA identifiers (e.g. ``America/New_York``) are used directly.
    * Common three‑letter abbreviations (``EST``, ``CET`` …) are mapped to a
      sensible IANA zone via ``_TZ_ABBREV_MAP``.
    * Raises ``ValueError`` if the name cannot be resolved.
    """
    _TZ_ABBREV_MAP = {
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "UTC": "UTC",
        "GMT": "GMT",
        "CET": "Europe/Paris",
        "CEST": "Europe/Paris",
        # Add more abbreviations if you need them
    }

    key = tz_name.strip().upper()
    try:
        # Try a direct IANA zone name first
        return ZoneInfo(key)
    except Exception:
        # Fall back to the abbreviation map
        if key in _TZ_ABBREV_MAP:
            return ZoneInfo(_TZ_ABBREV_MAP[key])
        raise ValueError(f"Unknown timezone specifier: {tz_name!r}")


def as_utc(dt: datetime, fallback_tz: Optional[timezone] = None) -> datetime:
    """
    Return an *aware* datetime in UTC.

    * If ``dt`` already has ``tzinfo`` → simply convert to UTC.
    * If ``dt`` is naïve → treat it as ``fallback_tz`` (or the system local
      zone when ``fallback_tz`` is ``None``) and then convert to UTC.
    """
    if dt.tzinfo is None:
        if fallback_tz is None:
            fallback_tz = datetime.now().astimezone().tzinfo  # local zone
        dt = dt.replace(tzinfo=fallback_tz)
    return dt.astimezone(timezone.utc)


# ----------------------------------------------------------------------
# Helper: combine a date (day) with a 12‑hour time string → UTC datetime
# ----------------------------------------------------------------------
def parse_day_time(day_str: str,
                   time_str: str,
                   tz_name: Optional[str] = None) -> datetime:
    """
    Build a **UTC** datetime from ``day`` + ``time`` strings.

    * ``tz_name`` – if supplied – is resolved with ``resolve_tz`` and the
      resulting zone is used as the *fallback* when the parsed datetime is
      naïve.
    * If ``tz_name`` is ``None`` the system local zone is used (the original
      behaviour).
    """
    # ---- Normalise the time component (12‑hour or 24‑hour) ----------
    time_clean = time_str.strip().lower().replace(" ", "")
    if "am" in time_clean or "pm" in time_clean:
        # 12‑hour clock
        if ":" not in time_clean:               # e.g. “5pm” → “5:00pm”
            time_clean = time_clean.replace("am", ":00am").replace("pm", ":00pm")
        dt = datetime.strptime(f"{day_str} {time_clean}", "%Y-%m-%d %I:%M%p")
    else:
        # 24‑hour clock
        if ":" not in time_clean:               # e.g. “17” → “17:00”
            time_clean = f"{time_clean}:00"
        dt = datetime.strptime(f"{day_str} {time_clean}", "%Y-%m-%d %H:%M")

    # Resolve the requested zone (if any)
    tzinfo: Optional[timezone] = None
    if tz_name:
        tzinfo = resolve_tz(tz_name)

    # Convert to UTC
    return as_utc(dt, fallback_tz=tzinfo)


# ----------------------------------------------------------------------
# Data model – now understands the compact syntax & optional timezone
# ----------------------------------------------------------------------
@dataclass
class Meeting:
    name: str
    start: datetime                 # stored internally as UTC
    stop: datetime                  # stored internally as UTC
    _raw: dict = field(default_factory=dict, repr=False)

    @staticmethod
    def _to_utc(ts: str, tz_name: Optional[str] = None) -> datetime:
        """Legacy ISO‑8601 → UTC (now also respects a supplied ``timezone``)."""
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError as exc:
            raise ValueError(f"Invalid timestamp: {ts}") from exc
        return as_utc(dt, fallback_tz=resolve_tz(tz_name) if tz_name else None)

    @classmethod
    def from_dict(cls, raw: dict) -> "Meeting":
        """
        Accepts both the *compact* layout (with optional ``timezone``) and the
        legacy ISO‑8601 layout.  The optional ``timezone`` key, when present,
        is used to interpret the times; otherwise the local timezone is assumed.
        """
        tz_name = raw.get("timezone")          # may be None

        if "day" in raw and "start" in raw and "stop" in raw:
            day = raw["day"]
            start = parse_day_time(day, raw["start"], tz_name)
            stop = parse_day_time(day, raw["stop"], tz_name)
            return cls(name=raw["name"], start=start, stop=stop, _raw=raw)

        # Legacy format – timestamps may be ISO‑8601 *or* plain strings
        return cls(
            name=raw["name"],
            start=cls._to_utc(raw["start"], tz_name),
            stop=cls._to_utc(raw["stop"], tz_name),
            _raw=raw,
        )

    def to_dict(self) -> dict:
        """When persisting, always write ISO‑8601 UTC timestamps."""
        return {
            "name": self.name,
            "start": self.start.isoformat(),
            "stop": self.stop.isoformat(),
        }

    @property
    def duration(self) -> timedelta:
        return self.stop - self.start


# ----------------------------------------------------------------------
# Small utility helpers (unchanged)
# ----------------------------------------------------------------------
def fmt_td(td: timedelta) -> str:
    secs = int(td.total_seconds())
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def build_layout(meetings: List[Meeting]) -> List[List[sg.Element]]:
    names = [m.name for m in meetings] or ["<no meetings>"]
    
    # Tab 1: Dominant Countdown View
    countdown_tab = [
        [sg.Text("", key="-STATUS-", size=(40, 1), font=("Helvetica", 11, "bold"))],
        [
            sg.Text(
                "00:00:00",
                key="-CLOCK-",
                font=("Helvetica", 36, "bold"),
                text_color="#ff4500",
                justification="center",
                expand_x=True,
            )
        ],
        [
            sg.ProgressBar(
                100,
                orientation="h",
                size=(35, 20),
                key="-PROG-",
                bar_color=("#00509e", "#d3d3d3"),
            )
        ],
    ]

    # Tab 2: Edit & Form Details View
    edit_tab = [
        [sg.Text("Name:", size=(9, 1)), sg.Input(key="-NAME-", size=(30, 1))],
        [
            sg.Text("Start:", size=(9, 1)),
            sg.Input(key="-START-", size=(30, 1)),
            sg.Button("Now", key="-NOW-"),
        ],
        [
            sg.Text("Stop:", size=(9, 1)),
            sg.Input(key="-STOP-", size=(30, 1)),
            sg.Button("+15 m", key="-PLUS15-"),
            sg.Button("+30 m", key="-PLUS30-"),
            sg.Button("+60 m", key="-PLUS60-"),
        ],
        [sg.Button("Save", button_color=("white", "#00509e"), expand_x=True)],
    ]

    return [
        [sg.Text("Meeting Countdown", font=("Helvetica", 14, "bold"))],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Select:", size=(9, 1)),
            sg.Combo(
                names,
                default_value=names[0],
                key="-SELECT-",
                enable_events=True,
                readonly=True,
                size=(22, 1),
            ),
            sg.Button("Add", key="-ADD-"),
            sg.Button("Delete", key="-DELETE-"),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Countdown", countdown_tab),
                        sg.Tab("Edit Meeting", edit_tab),
                    ]
                ],
                key="-TABGROUP-",
            )
        ],
        [sg.HorizontalSeparator()],
        [sg.Button("Exit", button_color=("white", "#c00000"), expand_x=True)],
    ]


def sync_ui(win: sg.Window, meeting: Meeting) -> None:
    """Populate the input fields with a meeting’s data."""
    win["-NAME-"].update(meeting.name)
    win["-START-"].update(
        meeting.start.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    )
    win["-STOP-"].update(
        meeting.stop.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    )


def refresh_combo(win: sg.Window, meetings: List[Meeting]) -> None:
    names = [m.name for m in meetings] or ["<no meetings>"]
    win["-SELECT-"].update(values=names)


def get_by_name(meetings: List[Meeting], name: str) -> Optional[Meeting]:
    for m in meetings:
        if m.name == name:
            return m
    return None


# ----------------------------------------------------------------------
# GUI – **THIS IS THE REAL IMPLEMENTATION**
# ----------------------------------------------------------------------
def run_gui(meetings: List[Meeting]) -> None:
    sg.theme("Topanga")
    win = sg.Window(
        "Meeting Countdown",
        build_layout(meetings),
        keep_on_top=True,
        finalize=True,
        margins=(10, 10),
    )
    # Pick the first meeting (or create a dummy one if the list is empty)
    current: Optional[Meeting] = meetings[0] if meetings else None
    if current:
        win["-SELECT-"].update(value=current.name)
        sync_ui(win, current)

    def ensure_current() -> Meeting:
        """Guarantee a meeting exists – create a dummy one if the list is empty."""
        nonlocal current
        if current is None:
            now = datetime.now(timezone.utc)
            current = Meeting(
                name="Untitled",
                start=now,
                stop=now + timedelta(minutes=15),
            )
            meetings.append(current)
            refresh_combo(win, meetings)
            win["-SELECT-"].update(value=current.name)
        return current

    while True:
        event, vals = win.read(timeout=1000)   # one‑second tick
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        # ------------------- UI actions -------------------
        if event == "-SELECT-":
            sel = vals["-SELECT-"]
            current = get_by_name(meetings, sel)
            if current:
                sync_ui(win, current)

        elif event == "-NOW-":
            cur = ensure_current()
            cur.start = datetime.now(timezone.utc)
            sync_ui(win, cur)

        elif event in ("-PLUS15-", "-PLUS30-", "-PLUS60-"):
            cur = ensure_current()
            minutes = int(event.split("-PLUS")[1].replace("-", ""))
            # Try to respect a manually edited start time
            try:
                start_local = datetime.strptime(
                    vals["-START-"].strip(), "%Y-%m-%d %H:%M:%S"
                )
                cur.start = start_local.replace(tzinfo=timezone.utc)
            except Exception:
                cur.start = datetime.now(timezone.utc)
            cur.stop = cur.start + timedelta(minutes=minutes)
            sync_ui(win, cur)

        elif event == "Save":
            cur = ensure_current()
            try:
                cur.name = vals["-NAME-"].strip() or cur.name
                cur.start = datetime.strptime(
                    vals["-START-"].strip(), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                cur.stop = datetime.strptime(
                    vals["-STOP-"].strip(), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                if cur.start >= cur.stop:
                    raise ValueError("Start must be before stop")
                refresh_combo(win, meetings)
                win["-SELECT-"].update(value=cur.name)
                sg.popup_ok("Meeting saved.", title="Success")
            except Exception as exc:
                log.exception("Save failed")
                sg.popup_error(f"Invalid input:\n{exc}")

        elif event == "-ADD-":
            new_meeting = Meeting(
                name="New Meeting",
                start=datetime.now(timezone.utc),
                stop=datetime.now(timezone.utc) + timedelta(minutes=30),
            )
            meetings.append(new_meeting)
            refresh_combo(win, meetings)
            win["-SELECT-"].update(value=new_meeting.name)
            sync_ui(win, new_meeting)
            current = new_meeting

        elif event == "-DELETE-":
            cur = ensure_current()
            if sg.popup_yes_no(f"Delete “{cur.name}”?", title="Confirm") == "Yes":
                meetings.remove(cur)
                refresh_combo(win, meetings)
                if meetings:
                    current = meetings[0]
                    win["-SELECT-"].update(value=current.name)
                    sync_ui(win, current)
                else:
                    current = None
                    for k in ("-NAME-", "-START-", "-STOP-"):
                        win[k].update("")
                    win["-SELECT-"].update(value="")

        # ------------------- Countdown logic -------------------
        cur = ensure_current()
        now = datetime.now(timezone.utc)

        if now < cur.start:
            remaining = cur.start - now
            win["-STATUS-"].update(f"⏳ {cur.name} – starts in")
            win["-CLOCK-"].update(fmt_td(remaining))
            win["-PROG-"].update(0)

        elif cur.start <= now < cur.stop:
            remaining = cur.stop - now
            elapsed = now - cur.start
            pct = (elapsed.total_seconds() / cur.duration.total_seconds()) * 100
            win["-STATUS-"].update(f"🔴 {cur.name} – in progress")
            win["-CLOCK-"].update(fmt_td(remaining))
            win["-PROG-"].update(int(pct))

        else:
            win["-STATUS-"].update(f"✅ {cur.name} – finished")
            win["-CLOCK-"].update("00:00:00")
            win["-PROG-"].update(100)

    win.close()


# ----------------------------------------------------------------------
# Argument‑parsing with argparse
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """
    Construct the top‑level parser and sub‑parsers that mimic the original
    docopt usage.  The function returns the ready‑to‑use ``ArgumentParser``.
    """
    parser = argparse.ArgumentParser(
        prog="session-timer.py",
        description="Meeting Countdown Widget",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example (new compact syntax):\n"
               "  - name: Team Sync\n"
               "    day: 2024-10-02\n"
               "    start: 5:15pm\n"
               "    stop: 7:45pm",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("~/.meeting_countdown.yaml").expanduser(),
        help="Path to YAML file that stores meetings "
             "(default: %(default)s)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Meeting Countdown 1.2",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ------------------- run -------------------
    sub.add_parser("run", help="Start the GUI")

    # ------------------- add -------------------
    add_parser = sub.add_parser("add", help="Add a new meeting")
    add_parser.add_argument("name", help="Meeting name")
    add_parser.add_argument("day", help="Date of the meeting (YYYY-MM-DD)")
    add_parser.add_argument("start", help="Start time (e.g. 5:15pm or 17:15)")
    add_parser.add_argument("stop", help="Stop time (same format as start)")

    # ------------------- list -------------------
    sub.add_parser("list", help="List all meetings (as YAML)")

    # ------------------- remove -------------------
    rm_parser = sub.add_parser("remove", help="Remove a meeting by name")
    rm_parser.name = rm_parser.add_argument("name", help="Name of the meeting to delete")

    return parser


# ---------------------------------------------------
# Entry point – parse args and dispatch sub‑commands
# ---------------------------------------------------
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cfg_path: Path = args.config.expanduser()
    raw = load_meetings(cfg_path)
    meetings = [Meeting.from_dict(item) for item in raw]

    if args.command == "run":
        run_gui(meetings)

    elif args.command == "add":
        try:
            start = parse_day_time(args.day, args.start)
            stop = parse_day_time(args.day, args.stop)
            new = Meeting(name=args.name, start=start, stop=stop)
            meetings.append(new)
            save_meetings(cfg_path, [m.to_dict() for m in meetings])
            print(f"✔ Added meeting “{new.name}”.")
        except Exception as exc:
            log.exception("add command failed")
            print(f"❌ {exc}")

    elif args.command == "list":
        print(
            yaml.safe_dump(
                [m.to_dict() for m in meetings],
                sort_keys=False,
                explicit_start=True,
                indent=2,
            )
        )

    elif args.command == "remove":
        name = args.name
        before = len(meetings)
        meetings = [m for m in meetings if m.name != name]
        if len(meetings) == before:
            print(f"⚠ No meeting named “{name}” found.")
        else:
            save_meetings(cfg_path, [m.to_dict() for m in meetings])
            print(f"🗑 Removed meeting “{name}”.")
    else:  # pragma: no cover
        parser.print_help()


if __name__ == "__main__":
    main()

