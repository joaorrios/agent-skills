#!/usr/bin/env bash
# Deterministic behavior witness for scripts/claude-session-mirror.py.
#
# Builds throwaway session stores and checks the copy plan for both modes. It
# never touches a real data dir and never applies changes.
#
# Run from the skill root: bash scripts/tests/claude-session-mirror.test.sh
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SCRIPT="$ROOT/scripts/claude-session-mirror.py"

python3 - "$SCRIPT" <<'PY'
import sys

sys.dont_write_bytecode = True

import importlib.util
import json
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("claude_session_mirror", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

failures = []


def check(label, actual, expected):
    if actual == expected:
        print(f"ok   {label}")
    else:
        failures.append(label)
        print(f"FAIL {label} — got {actual!r}, expected {expected!r}")


def write(partition, name, **record):
    partition.mkdir(parents=True, exist_ok=True)
    (partition / f"local_{name}.json").write_text(json.dumps(record))


def summary(copies):
    return sorted((s.parent.parent.name, t.parent.parent.name, t.name) for s, t, _ in copies)


with tempfile.TemporaryDirectory() as tmp:
    store = Path(tmp) / "claude-code-sessions"
    a, b = store / "acct-a" / "org", store / "acct-b" / "org"
    write(a, "only-a", cliSessionId="1", lastActivityAt=10, title="only a")
    write(b, "only-b", cliSessionId="2", lastActivityAt=10, title="only b")
    write(a, "shared", cliSessionId="3", lastActivityAt=30, title="shared")
    write(b, "shared", cliSessionId="3", lastActivityAt=20, title="shared")
    write(a, "newer-in-b", cliSessionId="4", lastActivityAt=5, title="newer in b")
    write(b, "newer-in-b", cliSessionId="4", lastActivityAt=50, title="newer in b")
    write(a, "broken", transcriptUnavailable=True, title="broken")
    write(b, "stripped", cliSessionId="5", lastActivityAt=1, title="stripped")
    write(a, "stripped", transcriptUnavailable=True, lastActivityAt=99, title="stripped")
    (b / "local_garbage.json").write_text("not json")

    found = module.partitions(store)
    check("finds both partitions", [p.parent.name for p in found], ["acct-a", "acct-b"])
    chosen = module.select(found, ["acct-a", "acct-b"])

    check(
        "newest mode copies each newer healthy record both ways",
        summary(module.plan(chosen, "newest")),
        sorted([
            ("acct-a", "acct-b", "local_only-a.json"),
            ("acct-a", "acct-b", "local_shared.json"),
            ("acct-b", "acct-a", "local_only-b.json"),
            ("acct-b", "acct-a", "local_newer-in-b.json"),
            ("acct-b", "acct-a", "local_stripped.json"),
        ]),
    )
    check(
        "primary mode copies only from the first partition and never over newer records",
        summary(module.plan(chosen, "primary")),
        sorted([
            ("acct-a", "acct-b", "local_only-a.json"),
            ("acct-a", "acct-b", "local_shared.json"),
        ]),
    )

    try:
        module.select(found, ["acct"])
    except SystemExit:
        print("ok   refuses an ambiguous prefix")
    else:
        failures.append("ambiguous prefix")
        print("FAIL refuses an ambiguous prefix")

    target = b / "local_only-a.json"
    module.copy(a / "local_only-a.json", target)
    check("copy writes the record unchanged", target.read_text(), (a / "local_only-a.json").read_text())
    check("copy leaves no temporary files", sorted(p.name for p in b.iterdir() if not p.name.startswith("local_")), [])

print()
if failures:
    print(f"{len(failures)} failing assertion(s)")
    sys.exit(1)
print("all assertions passed")
PY
