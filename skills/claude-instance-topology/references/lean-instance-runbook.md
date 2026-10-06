# Runbook: move a Desktop instance onto its own config dir

Gives one Desktop instance its own `CLAUDE_CONFIG_DIR` (its own configuration and CLI login) while its existing sessions keep loading through a transcript bridge. Every step leaves a backup, so the change can be undone without data loss.

Run it from the CLI or from a different Desktop instance; the target instance must be quit, and the user relaunches it. Run each block as a script with `bash`, since its `set -e` and `exit` would close an interactive shell.

Set these at the top of each block, from the topology map:

- `WRAPPER`: the target wrapper `.app`. To change the default `/Applications/Claude.app` instance, create a wrapper for it instead of editing the signed bundle.
- `DD`: that instance's data dir, the `--user-data-dir` its launcher passes, or `~/Library/Application Support/Claude` when it passes none.
- `OLD_CONFIG_DIR`: the config dir the instance uses now (`~/.claude` unless its launcher sets one).
- `NEW_CONFIG_DIR`: the new config dir. Populate its configuration first.

## Apply

```bash
set -euo pipefail
WRAPPER="/Applications/Claude Work.app"
DD="$HOME/Library/Application Support/Claude"
OLD_CONFIG_DIR="$HOME/.claude"
NEW_CONFIG_DIR="$HOME/.claude-work"

DEFAULT_DD="$HOME/Library/Application Support/Claude"
LAUNCHER="$WRAPPER/Contents/MacOS/$(defaults read "$WRAPPER/Contents/Info" CFBundleExecutable)"
TS=$(date +%Y%m%d-%H%M%S); BK="$HOME/.claude-instance-backups"; mkdir -p "$BK" "$NEW_CONFIG_DIR"

# 0. The target instance must be quit. Other instances may keep running.
target_running() {
  local c hits=""
  while IFS= read -r c; do
    if [[ "$c" == *--user-data-dir=* ]]; then
      [[ "$c" == *"--user-data-dir=$DD"* ]] && hits=1
    elif [ "$DD" = "$DEFAULT_DD" ]; then
      hits=1
    fi
  done < <(ps -axo command= | grep -E '^/.+\.app/Contents/MacOS/Claude( |$)' | grep -v -- '--type=' || true)
  [ -n "$hits" ]
}
if target_running; then echo "Quit the target instance first"; exit 1; fi
ORIG="$LAUNCHER.orig-backup"; [ -f "$ORIG" ] || ORIG="$LAUNCHER"   # rebuild from the original on reruns
grep -q CLAUDE_CONFIG_DIR "$ORIG" && { echo "Original launcher already sets CLAUDE_CONFIG_DIR; edit it by hand"; exit 1; }
head -1 "$ORIG" | grep -q '^#!' || { echo "Launcher is not a script"; exit 1; }

# 1. Transcript bridge, before any launch under the new config dir.
P="$NEW_CONFIG_DIR/projects"
if [ -L "$P" ]; then
  [ "$(readlink "$P")" = "$OLD_CONFIG_DIR/projects" ] || { echo "$P points to $(readlink "$P")"; exit 1; }
elif [ -d "$P" ] && [ -n "$(ls -A "$P")" ]; then
  echo "$P already holds transcripts; merge or move them before bridging"; exit 1
else
  rmdir "$P" 2>/dev/null || true
  ln -s "$OLD_CONFIG_DIR/projects" "$P"
fi

# 2. Match retention so the new config dir does not sweep shared transcripts sooner.
#    Skip when settings.json will be linked from the shared config dir instead.
python3 - "$OLD_CONFIG_DIR/settings.json" "$NEW_CONFIG_DIR/settings.json" <<'PY'
import json, os, sys
old_path, new_path = sys.argv[1:]
load = lambda p: json.load(open(p)) if os.path.exists(p) else {}
old, new = load(old_path), load(new_path)
for key in ("cleanupPeriodDays", "desktopSessionCleanupPeriodDays"):
    if key in old and key not in new:
        new[key] = old[key]
        print(f"copied {key}={old[key]}")
json.dump(new, open(new_path, "w"), indent=2)
PY

# 3. Back up the session records and record the healthy count.
tar czf "$BK/records-$TS.tgz" -C "$DD" claude-code-sessions
python3 - "$DD" <<'PY' | tee "$BK/count-$TS.txt"
import glob, json, sys
records = glob.glob(f"{sys.argv[1]}/claude-code-sessions/**/local_*.json", recursive=True)
healthy = unreadable = 0
for path in records:
    try:
        d = json.load(open(path))
    except ValueError:
        unreadable += 1
        continue
    healthy += bool(d.get("cliSessionId") and not d.get("transcriptUnavailable"))
print(len(records), "records", healthy, "healthy", unreadable, "unreadable")
PY

# 4. Back up the launcher, then rebuild it from the backup with one added line.
[ -f "$LAUNCHER.orig-backup" ] || cp -p "$LAUNCHER" "$LAUNCHER.orig-backup"
{ head -1 "$LAUNCHER.orig-backup"
  printf 'export CLAUDE_CONFIG_DIR=%q\n' "$NEW_CONFIG_DIR"
  tail -n +2 "$LAUNCHER.orig-backup"; } > "$LAUNCHER"
bash -n "$LAUNCHER"
diff "$LAUNCHER.orig-backup" "$LAUNCHER" || true   # expect exactly one added export line
```

Then give the CLI side of the new config dir a login: run `CLAUDE_CONFIG_DIR="$NEW_CONFIG_DIR" claude` once and sign in. Ask the user to relaunch the wrapper.

## Verify

1. In a Code session of the relaunched instance, `echo "$CLAUDE_CONFIG_DIR"` prints `NEW_CONFIG_DIR`, and the instance did not ask for a new Desktop sign-in. If the variable is missing, use `open -n -a "Claude" --env CLAUDE_CONFIG_DIR=…` in the launcher instead.
2. Rerun the count from Apply step 3 with the same `DD`. The healthy count must equal the one in `count-<TS>.txt`. A drop means the Desktop marked sessions unavailable: undo, restore the records, and check the bridge.

Verification is complete when both checks pass and an older session opens with its full history. Repeat check 1 after the next app update, since the update's relaunch may not go through the wrapper.

## Undo

```bash
set -euo pipefail
WRAPPER="/Applications/Claude Work.app"; DD="$HOME/Library/Application Support/Claude"
LAUNCHER="$WRAPPER/Contents/MacOS/$(defaults read "$WRAPPER/Contents/Info" CFBundleExecutable)"
# Quit the target instance first (see target_running in Apply).
cp -p "$LAUNCHER.orig-backup" "$LAUNCHER"
# Only if Verify showed a drop: restore the newest records backup.
# tar xzf "$(ls -t "$HOME"/.claude-instance-backups/records-*.tgz | head -1)" -C "$DD"
```

The bridge and the copied retention keys can stay. Remove the bridge with `rm "$NEW_CONFIG_DIR/projects"` only when retiring the new config dir.
