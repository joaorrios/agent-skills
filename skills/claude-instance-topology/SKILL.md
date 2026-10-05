---
name: claude-instance-topology
description: Maps and safely changes how Claude Desktop and Claude Code CLI instances on macOS share login, configuration, and session transcripts. Use when adding or modifying an instance (separate accounts, `CLAUDE_CONFIG_DIR`, `--user-data-dir`, per-instance skills/hooks), telling running instances apart by icon, recovering a session that shows "Session not found on disk" / "Sessão não encontrada no disco" or lost history after a config change or app update, or before editing any Claude Desktop session store.
license: MIT
compatibility: macOS with Claude Desktop and/or the Claude Code CLI. The icon script needs Python 3 and Pillow.
---

# Claude Instance Topology

An instance's **topology** is what it shares with other instances: Desktop account and sidebar, Claude Code login, configuration, and transcripts. Two independent settings decide all of it. Conflating them is how history gets lost.

| Setting | Scope | Decides |
|---|---|---|
| `--user-data-dir` (Electron argument, set per `.app` launcher) | Claude Desktop only | The Desktop app identity: its claude.ai sign-in, sidebar session list, session metadata records, and UI state. |
| `CLAUDE_CONFIG_DIR` (environment variable, default `~/.claude`) | Desktop and CLI | Configuration (`CLAUDE.md`, `settings.json`, hooks, skills, plugins), Claude Code CLI credentials, and transcripts and auto memory under `projects/`. |

What follows from the table:

- **Accounts.** A Desktop account follows the data dir: two wrappers with different data dirs can sign in to different accounts while sharing one config dir. CLI credentials, including the macOS Keychain entry, follow the config dir, so a new config dir starts with the CLI logged out. A Console sign-in without an API key lives in the Anthropic profile directory, outside any config dir.
- **Transcripts.** Desktop and CLI both read `CONFIG_DIR/projects/<project>/<session-id>.jsonl`. Changing `CLAUDE_CONFIG_DIR` for an instance that already has sessions points it at a different, usually empty, `projects/`.
- **Credentials the Desktop reads.** It signs in with OAuth. It ignores `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `apiKeyHelper` (except under a third-party inference configuration) and never reads Anthropic profiles.
- **Synced configuration.** Skills and plugins enabled on a claude.ai account load in every instance signed in to that account, whatever its config dir.

The Desktop's data-dir behavior is observed, not documented; the config-dir behavior is documented.

## Authentication boundary

Every login completes through Anthropic's own flows: the Desktop sign-in, `/login`, `/logout`, or `claude setup-token`, used with the unmodified apps. A topology changes where configuration and history live, never how authentication works. Credentials stay where those flows put them: leave Keychain entries, `.credentials.json`, and the account fields of `.claude.json` untouched, and to retire a login, run `/logout` under its config dir. Subscription credentials serve only Claude Code and native Anthropic apps, never the Agent SDK or other tools. When a requested setup needs anything beyond this, say so and offer the nearest native alternative. The current rules are in the legal and compliance page listed in `references/sources.md`.

## Map the current topology

Before changing anything, build the map from the machine itself:

1. List every Claude launcher: `/Applications/Claude.app` plus any wrapper `.app` whose executable (`CFBundleExecutable` in its `Info.plist`) is a script that runs `open -n -a "Claude" …`. Read each for `--user-data-dir` and `CLAUDE_CONFIG_DIR`. With no `--user-data-dir`, the data dir is `~/Library/Application Support/Claude`.
2. List CLI entry points: shell aliases and functions that set `CLAUDE_CONFIG_DIR`, and the variable in the login shell.
3. For each config dir, check whether `projects/` is a real directory or a symlink, where it points, and its `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`.
4. For a running Desktop instance, confirm the variable reached the process: inside one of its Code sessions, run `echo "$CLAUDE_CONFIG_DIR"`.

The map is done when each instance has a known data dir, config dir, accounts, and transcript location, and every shared or bridged `projects/` is accounted for.

## Change an instance safely

Choose the setting by what should differ:

- **Separate Desktop account or sidebar**, same configuration and transcripts: give a wrapper launcher its own `--user-data-dir`.
- **Separate configuration or CLI account** (different skills, plugins, hooks, `CLAUDE.md`): give the instance its own `CLAUDE_CONFIG_DIR`. Only a separate config dir changes the skill, plugin, and hook set for a whole instance; inside one instance, use project-level configuration instead.
- **Separate configuration with shared history**: give it its own config dir, then **bridge** transcripts back by making its `projects/` a symlink to the old config dir's `projects/`. Session records store only `cliSessionId` and `cwd` and build the transcript path at load time, so the bridge resolves existing sessions. The bridge shares auto memory too.

Guardrails for every change:

- Quit the target Desktop instance before editing its launcher or session store; a running app overwrites store edits when it quits. Other instances can keep running, and one instance can edit another's store.
- Back up whatever you touch: the launcher and the data dir's `claude-code-sessions/`.
- Create the bridge **before** the first launch under a new config dir. A Desktop that opens with an empty `projects/` can mark its sessions as unavailable.
- Give bridged config dirs the same retention. Each config dir sweeps the shared transcripts with its own `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`, so the shortest setting wins.
- Keep one copy of each transcript. A hand-copied duplicate in a second project directory makes `claude --resume <session-id>` report not-found from any other project directory.

To move an existing Desktop instance onto its own config dir with history intact, follow [`references/lean-instance-runbook.md`](references/lean-instance-runbook.md). It covers apply, verify, and undo.

## Telling instances apart

Every running instance shows the same Dock tile. To recolor a wrapper's icon for Finder, Spotlight, and Launchpad, or to weigh a separate bundle for the running tile, read [`references/wrapper-icons.md`](references/wrapper-icons.md).

## Recovering a session

When a Desktop session opens empty with "Session not found on disk", or history disappears after a config dir change or app update, the transcript is usually intact and only the metadata link broke. Follow [`references/session-recovery.md`](references/session-recovery.md) before sending any message in that session; a new message overwrites the link.

## Sources

Paths, precedence rules, and retention change between releases. When a fact here conflicts with what you observe, or a decision hinges on it, check [`references/sources.md`](references/sources.md) and follow the current documentation.
