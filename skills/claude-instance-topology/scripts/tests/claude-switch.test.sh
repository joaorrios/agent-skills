#!/usr/bin/env bash
# Deterministic behavior witness for scripts/claude-switch.py.
#
# Runs every command against throwaway directories through CLAUDE_SWITCH_CONFIG.
# It never opens, quits, or reads a real Claude instance or config dir.
#
# Run from the skill root: bash scripts/tests/claude-switch.test.sh
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SWITCH="$ROOT/scripts/claude-switch.py"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
failures=0

check() {
  if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 — got '$2', expected '$3'"; failures=$((failures + 1)); fi
}

mkdir -p "$T/Claude/claude-code-sessions/acct-a/org" "$T/shared/skills" "$T/shared/projects"
echo '{"cliSessionId":"1","lastActivityAt":5,"title":"from a"}' > "$T/Claude/claude-code-sessions/acct-a/org/local_x.json"
echo "# shared" > "$T/shared/CLAUDE.md"
echo '{}' > "$T/shared/settings.json"
cat > "$T/config.json" <<EOF
{
  "desktop_link": "$T/Claude",
  "shared_config_dir": "$T/shared",
  "accounts": {
    "a": {"data_dir": "$T/Claude-A", "config_dir": "$T/shared"},
    "b": {"data_dir": "$T/Claude-B", "config_dir": "$T/cfg-b"}
  }
}
EOF
export CLAUDE_SWITCH_CONFIG="$T/config.json" CLAUDE_INSTANCE_BACKUP_DIR="$T/backups"
run() { python3 -B "$SWITCH" "$@"; }

run adopt a >/dev/null
check "adopt moves the data dir behind a symlink" "$(readlink "$T/Claude")" "$T/Claude-A"
check "adopt keeps the session records" "$(ls "$T/Claude-A/claude-code-sessions/acct-a/org")" "local_x.json"
check "adopt marks the account active" "$(run status --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["desktop"])')" "a"
if run adopt a >/dev/null 2>&1; then check "adopt refuses a second run" "ran" "refused"; else check "adopt refuses a second run" "refused" "refused"; fi

mkdir -p "$T/Claude-B/claude-code-sessions/acct-b/org"
run use b --no-open >/dev/null
check "use repoints the link" "$(readlink "$T/Claude")" "$T/Claude-B"
check "use mirrors records into the other account" "$(ls "$T/Claude-B/claude-code-sessions/acct-b/org")" "local_x.json"
check "use records the CLI account" "$(run env)" "export CLAUDE_CONFIG_DIR=$T/cfg-b"
check "exec runs with the active config dir" "$(run exec -- sh -c 'echo $CLAUDE_CONFIG_DIR')" "$T/cfg-b"
check "exec honours --account" "$(run exec --account a -- sh -c 'echo $CLAUDE_CONFIG_DIR')" "$T/shared"

python3 - "$T/config.json" "$T" <<'PY2'
import json, sys
path, root = sys.argv[1:]
config = json.load(open(path))
config["accounts"]["c"] = {"data_dir": f"{root}/Claude-C", "config_dir": f"{root}/cfg-c"}
json.dump(config, open(path, "w"))
PY2
mkdir -p "$T/Claude-C/claude-code-sessions/acct-c/org"
echo '{"cliSessionId":"2","lastActivityAt":9,"title":"from c"}' > "$T/Claude-C/claude-code-sessions/acct-c/org/local_y.json"
run use c --no-open >/dev/null
check "a third account becomes active" "$(readlink "$T/Claude")" "$T/Claude-C"
check "three accounts mirror into each other" "$(ls "$T/Claude-A/claude-code-sessions/acct-a/org" "$T/Claude-B/claude-code-sessions/acct-b/org" "$T/Claude-C/claude-code-sessions/acct-c/org" | grep -c local_)" "6"

check "backups stay in the test directory" "$(ls "$T/backups" | grep -c records-mirror)" "5"

run link-config b >/dev/null
check "link-config links shared files" "$(readlink "$T/cfg-b/CLAUDE.md")" "$T/shared/CLAUDE.md"
check "link-config links shared history" "$(readlink "$T/cfg-b/projects")" "$T/shared/projects"
check "link-config leaves account state alone" "$( [ -e "$T/cfg-b/.claude.json" ] && echo linked || echo absent)" "absent"
if run link-config a >/dev/null 2>&1; then check "link-config refuses the shared dir itself" "ran" "refused"; else check "link-config refuses the shared dir itself" "refused" "refused"; fi

python3 - "$T/config.json" <<'PY2'
import json, sys
config = json.load(open(sys.argv[1]))
config["accounts"]["bad name"] = config["accounts"]["a"]
json.dump(config, open(sys.argv[1], "w"))
PY2
if run status >/dev/null 2>&1; then check "rejects account names SwiftBar cannot pass" "ran" "refused"; else check "rejects account names SwiftBar cannot pass" "refused" "refused"; fi

echo
if [ "$failures" -gt 0 ]; then echo "$failures failing assertion(s)"; exit 1; fi
echo "all assertions passed"
