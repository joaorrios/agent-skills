# Reload hook

The hook reinjects the protocol and the state after compaction or resume.
It runs on every session start in the project and stays silent unless the
session id matches the state's "Coordinator session" line, so other
sessions and workers never receive the role.

Register it in personal configuration, outside git, and merge it into any
hooks already there. `<skill>` is the absolute path of this skill's
folder. As of 2026-10-08.

## Claude Code

In the project's `.claude/settings.local.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "<skill>/scripts/resume.sh" } ] }
    ]
  }
}
```

Output past 10,000 characters is replaced by a 2,000-character preview
and a file path, which is why the script sends only the state when the
two together are too long.

## Codex

In `~/.codex/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "resume|compact",
        "hooks": [ { "type": "command", "command": "<skill>/scripts/resume.sh", "additionalContextLimit": 4000 } ]
      }
    ]
  }
}
```

- The user must trust the hook through `/hooks` before it runs.
- Subagent hooks receive the parent's session id, so a subagent starting
  up would match the coordinator. The matcher leaves out `startup` for
  that reason; a new coordinator session gets the protocol from the skill
  itself.
- Output past about 2,500 tokens spills to a file with a preview. The
  limit above raises that threshold; whether it covers plain stdout as
  well as JSON `additionalContext` is not documented, so confirm with the
  test below.

Docs: <https://learn.chatgpt.com/docs/hooks>.

## Test

With the registered session id the script prints the state and the
protocol; with any other id it prints nothing:

```sh
printf '{"session_id":"<id>","source":"compact","cwd":"%s"}' "$PWD" | <skill>/scripts/resume.sh
```

The hook stops recognising the coordinator if a runtime changes the
session id on resume or compaction. When a reload fails to arrive, check
that first.
