# Recover a Desktop session

Use when a Claude Desktop Code session opens empty with "Session not found on disk" ("Sessão não encontrada no disco"), its record shows `transcriptUnavailable: true`, or history vanished after a config dir change or app update.

The Desktop's startup scan can fail to validate a transcript, for example when its config dir's `projects/` is empty after a `CLAUDE_CONFIG_DIR` change. When that happens it clears `cliSessionId` and sets `transcriptUnavailable: true` in the session record, while the transcript usually stays intact on disk. Tracked upstream as [anthropics/claude-code#63082](https://github.com/anthropics/claude-code/issues/63082). This is observed app behavior, not documented behavior, so confirm it against the current app before relying on the details.

## Where things live

- `<data-dir>/claude-code-sessions/<ws>/<ws2>/local_<id>.json`: the session **record**, with `title`, `cwd`, `cliSessionId`, `transcriptUnavailable`, and `lastActivityAt` (epoch milliseconds).
- `<data-dir>/local-agent-mode-sessions/…`: Cowork and agent-mode sessions, each with its own `.claude/` home.
- `<data-dir>/Session Storage/`: Electron UI state only, never transcripts.
- `CONFIG_DIR/projects/<project>/<session-id>.jsonl`: the **transcript**. `<project>` is the absolute working directory with every non-alphanumeric character replaced by `-`; past 200 characters it is truncated with a hash appended, so match on the first 200 characters. `CLAUDE_CODE_PROJECT_DIR_NAME`, set together with `CLAUDE_CONFIG_DIR`, overrides the name. Only top-level `<uuid>.jsonl` files are transcripts; set-aside copies (`*.orphaned-*.jsonl`, `*.jsonl.superseded-*`) and `<session>/subagents/` are not.

The Desktop loads a session by reading `cliSessionId` and `cwd` from the record and opening the matching transcript. Restoring the record's link restores the session.

## Steps

1. Leave the empty session untouched. Sending a message writes a fresh `cliSessionId` over the link you need to restore.
2. Quit the affected instance, then back up the record and its `claude-code-sessions` workspace.
3. Search `projects/<project>/` for the record's `cwd` in every config dir on the topology map, starting with the one the instance used before the change. Rank candidates by how close each transcript's **last-entry `timestamp`** is to the record's `lastActivityAt`:

   ```bash
   python3 - "$RECORD" "$PROJECT_DIR" <<'PY' | sort -n | head
   import glob, json, os, re, sys
   from datetime import datetime
   record, project_dir = sys.argv[1:]
   target = json.load(open(record))["lastActivityAt"]
   for path in glob.glob(os.path.join(project_dir, "*.jsonl")):
       name = os.path.basename(path)
       if not re.fullmatch(r"[0-9a-f-]{36}\.jsonl", name):
           continue
       last = None
       for line in open(path, errors="replace"):
           try:
               last = json.loads(line).get("timestamp") or last
           except ValueError:
               pass
       if last:
           ms = datetime.fromisoformat(last.replace("Z", "+00:00")).timestamp() * 1000
           print(f"{abs(ms - target):>12.0f} ms  {name[:-6]}")
   PY
   ```

   The right transcript usually ends within 100 ms of `lastActivityAt`, always within 5 s. File modification time and turn counts are unreliable and have picked the wrong transcript; when several sessions share one `cwd`, the last-entry timestamp is the only reliable signal.
4. If no transcript ends within 5 s, the transcript is gone from disk; report that rather than linking a loose match. Retention settings can delete transcripts; `references/sources.md` points to the current rules.
5. Edit the record with the instance still quit:

   ```python
   import json
   p = "<data-dir>/claude-code-sessions/<ws>/<ws2>/local_<id>.json"
   d = json.load(open(p))
   d["cliSessionId"] = "<transcript-uuid>"
   d["transcriptUnavailable"] = False
   json.dump(d, open(p, "w"), ensure_ascii=False)
   ```

6. Reopen the instance and confirm the session shows its history.

Recovery is complete when every affected session opens with its full history, or is reported as unrecoverable with the reason.

If the scan clears links again on a later launch, fix the cause first, usually a missing `projects/` bridge (see `references/lean-instance-runbook.md`), then reapply these steps.

Without editing records, the same transcript can be reopened as a new entry: from the CLI with `claude --resume <session-id>` or `claude --resume <absolute-transcript-path>`, run under the config dir that holds the transcript, or from a Desktop session with `/resume`, which lists sessions started from the CLI.
