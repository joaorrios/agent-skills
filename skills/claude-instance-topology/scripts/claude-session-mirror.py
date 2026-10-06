#!/usr/bin/env python3
"""Mirror Claude Desktop Code session records between account partitions.

The Desktop keeps one sidebar per signed-in account, as session records under
<data-dir>/claude-code-sessions/<account>/<org>/local_<id>.json. Transcripts
live in the shared config dir, so copying a record into another partition makes
that account list and continue the same conversation.

    claude-session-mirror.py --list
    claude-session-mirror.py --partitions 33e47bcc 207c0f42            # dry run
    claude-session-mirror.py --partitions 33e47bcc 207c0f42 --apply

Pass --data-dir once per data dir when each account has its own Desktop data dir.

By default the newest record of each session (by lastActivityAt) wins and is
copied to every listed partition. With --mode primary, the first partition is
the only source. Records are copied unchanged; credentials are never read.
The instance using the data dir must be quit, and --apply backs up first.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

DEFAULT_DATA_DIR = Path.home() / "Library/Application Support/Claude"
BACKUP_DIR = Path(os.environ.get("CLAUDE_INSTANCE_BACKUP_DIR", Path.home() / ".claude-instance-backups")).expanduser()
BACKUP_KEEP = 20
MAIN_PROCESS = re.compile(r"^/.+?\.app/Contents/MacOS/Claude( |$)")


def fail(message):
    sys.exit(f"error: {message}")


def partitions(store):
    """Every <account>/<org> directory under the session store."""
    return sorted(p for p in store.glob("*/*") if p.is_dir())


def select(found, prefixes):
    chosen = []
    for prefix in prefixes:
        matches = [
            p for p in found
            if f"{p.parent.name}/{p.name}".startswith(prefix)
            or f"{p.parent.parent.parent.name}/{p.parent.name}/{p.name}".startswith(prefix)
        ]
        if len(matches) != 1:
            fail(f"--partitions {prefix!r} matches {len(matches)} partitions; use --list and a longer prefix")
        if matches[0] in chosen:
            fail(f"partition {prefix!r} listed twice")
        chosen.append(matches[0])
    return chosen


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def healthy(record):
    return bool(record and record.get("cliSessionId") and not record.get("transcriptUnavailable"))


def activity(record):
    return record.get("lastActivityAt") or record.get("createdAt") or 0


def plan(chosen, mode):
    """(source, target) copies that bring every partition up to date."""
    records = {}
    for partition in chosen:
        for path in partition.glob("local_*.json"):
            records.setdefault(path.name, {})[partition] = path

    copies = []
    for name, by_partition in sorted(records.items()):
        loaded = {p: load(path) for p, path in by_partition.items()}
        if mode == "primary":
            source = chosen[0] if healthy(loaded.get(chosen[0])) else None
        else:
            candidates = [p for p in by_partition if healthy(loaded[p])]
            source = max(candidates, key=lambda p: activity(loaded[p]), default=None)
        if source is None:
            continue
        newest = activity(loaded[source])
        for target in chosen:
            if target == source:
                continue
            current = loaded.get(target)
            if current is None or not healthy(current) or activity(current) < newest:
                copies.append((by_partition[source], target / name, loaded[source]))
    return copies


def running_data_dirs():
    """Resolved data dir of every running Claude Desktop main process."""
    output = subprocess.run(["ps", "-axo", "command="], capture_output=True, text=True).stdout
    found = set()
    for command in output.splitlines():
        if not MAIN_PROCESS.match(command) or "--type=" in command:
            continue
        if "--user-data-dir=" in command:
            path = command.split("--user-data-dir=", 1)[1].split(" --", 1)[0]
        else:
            path = DEFAULT_DATA_DIR
        found.add(Path(path).expanduser().resolve())
    return found


def instance_running(data_dir):
    return Path(data_dir).expanduser().resolve() in running_data_dirs()


def backup(store):
    """Archive a session store, keeping the newest BACKUP_KEEP archives per data dir."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    label = store.parent.name.replace(" ", "_")
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"-{time.time_ns() % 10**9:09d}"
    target = BACKUP_DIR / f"records-mirror-{label}-{stamp}.tgz"
    with tarfile.open(target, "w:gz") as archive:
        archive.add(store, arcname=store.name)
    for old in sorted(BACKUP_DIR.glob(f"records-mirror-{label}-*.tgz"))[:-BACKUP_KEEP]:
        old.unlink()
    return target


def copy(source, target):
    """Write through a temporary file so a crash never leaves half a record."""
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
    shutil.copy2(source, temporary)
    os.replace(temporary, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, action="append", help="repeat for several data dirs")
    parser.add_argument("--list", action="store_true", help="list partitions and exit")
    parser.add_argument("--partitions", nargs="+", metavar="PREFIX",
                        help="account/org prefixes to keep in sync; prefix with the data dir name to disambiguate")
    parser.add_argument("--mode", choices=("newest", "primary"), default="newest")
    parser.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    args = parser.parse_args()

    data_dirs = [d.expanduser() for d in (args.data_dir or [DEFAULT_DATA_DIR])]
    stores = [d / "claude-code-sessions" for d in data_dirs]
    for store in stores:
        if not store.is_dir():
            fail(f"{store} not found")
    found = [p for store in stores for p in partitions(store)]

    if args.list or not args.partitions:
        for partition in found:
            titles = [(load(p) or {}).get("title", "?") for p in sorted(partition.glob("local_*.json"))]
            where = f"  [{partition.parent.parent.parent.name}]" if len(stores) > 1 else ""
            print(f"{partition.parent.name}/{partition.name}{where}  {len(titles)} sessions  {', '.join(titles[:3])}")
        return

    chosen = select(found, args.partitions)
    if len(chosen) < 2:
        fail("list at least two partitions")
    copies = plan(chosen, args.mode)
    for source, target, record in copies:
        print(f"{record.get('title', '?')!r}: {source.parent.parent.name[:8]} -> {target.parent.parent.name[:8]}")
    if not copies:
        print("partitions already in sync")
        return
    if not args.apply:
        print(f"dry run: {len(copies)} record(s) would be copied; rerun with --apply")
        return
    for data_dir in data_dirs:
        if instance_running(data_dir):
            fail(f"quit the Claude instance using {data_dir} first")
    for store in stores:
        print(f"backup: {backup(store)}")
    for source, target, _ in copies:
        copy(source, target)
    print(f"copied {len(copies)} record(s)")


if __name__ == "__main__":
    main()
