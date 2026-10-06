---
name: claude-instance-topology
description: Maps and safely changes how Claude Desktop and Claude Code CLI instances on macOS share login, configuration, and session transcripts. Use when adding or modifying an instance or switching between accounts (separate accounts, `CLAUDE_CONFIG_DIR`, `--user-data-dir`, per-instance skills/hooks), telling instances apart, cleaning up leftover launchers, aliases, and config or data dirs, recovering a session that shows "Session not found on disk" / "Sessão não encontrada no disco" or lost history after a config change or app update, or before editing any Claude Desktop session store.
license: MIT
compatibility: macOS with Claude Desktop and/or the Claude Code CLI. Scripts need Python 3; the icon script also needs Pillow, and the menu bar plugin needs SwiftBar.
---

# Claude Instance Topology

An instance's **topology** is what it shares with other instances: Desktop account and sidebar, Claude Code login, configuration, and transcripts. Two independent settings decide all of it. Conflating them is how history gets lost.

| Setting | Scope | Decides |
|---|---|---|
| `--user-data-dir` (Electron argument, set per `.app` launcher) | Claude Desktop only | The Desktop app identity: its claude.ai sign-in, sidebar session list, session metadata records, and UI state. |
| `CLAUDE_CONFIG_DIR` (environment variable, default `~/.claude`) | Desktop and CLI | Configuration (`CLAUDE.md`, `settings.json`, hooks, skills, plugins), Claude Code CLI credentials, and transcripts and auto memory under `projects/`. |

What follows from the table:

- **Accounts.** A Desktop account follows the data dir: two data dirs can stay signed in to different accounts while sharing one config dir, and the data dir may be a symlink. CLI credentials, including the macOS Keychain entry, follow the config dir, so a new config dir starts with the CLI logged out. A Console sign-in without an API key lives in the Anthropic profile directory, outside any config dir.
- **Transcripts.** Desktop and CLI both read `CONFIG_DIR/projects/<project>/<session-id>.jsonl`. Changing `CLAUDE_CONFIG_DIR` for an instance that already has sessions points it at a different, usually empty, `projects/`.
- **Credentials the Desktop reads.** It signs in with OAuth. It ignores `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `apiKeyHelper` (except under a third-party inference configuration) and never reads Anthropic profiles.
- **Synced configuration.** Skills and plugins enabled on a claude.ai account load in every instance signed in to that account, whatever its config dir.

The Desktop's data-dir behavior is observed, not documented; the config-dir behavior is documented.

## Authentication boundary

A topology changes where configuration and history live, never how authentication works. **Switch the selector, not the secret**: to change accounts, choose a different config dir (or Desktop data dir), each holding the login it received through Anthropic's own flow.

| Practice | Use |
|---|---|
| Desktop sign-in, `/login`, `/logout` in the unmodified apps | The way every login is made and retired. |
| Choosing the config dir through an alias, function, launcher, or another tool's per-agent environment | The documented way to keep several accounts. |
| `claude setup-token` with `CLAUDE_CODE_OAUTH_TOKEN`, in Claude Code itself | Documented for non-interactive environments. It cannot use claude.ai connectors or Remote Control. |
| Reading, copying, moving, or restoring stored credentials (Keychain entries, `.credentials.json`, the account fields of `.claude.json`) | Outside the native flows. Leave them where the flows put them. |
| Running OAuth or token exchanges outside the apps, or using subscription credentials in tools that handle the credential themselves | Prohibited by Anthropic's terms. |

When a requested setup needs anything outside the first three rows, say so and offer the nearest native alternative. The current rules are in the legal and compliance page listed in `references/sources.md`.

## Map the current topology

Before changing anything, build the map from the machine itself:

1. List every Claude launcher: `/Applications/Claude.app` plus any wrapper `.app` whose executable (`CFBundleExecutable` in its `Info.plist`) is a script that runs `open -n -a "Claude" …`. Read each for `--user-data-dir` and `CLAUDE_CONFIG_DIR`. With no `--user-data-dir`, the data dir is `~/Library/Application Support/Claude`.
2. List CLI entry points: shell aliases and functions that set `CLAUDE_CONFIG_DIR`, the variable in the login shell, and tools that launch Claude Code with their own per-agent environment, such as Paseo providers.
3. For each config dir, check whether `projects/` is a real directory or a symlink, where it points, and its `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`.
4. For a running Desktop instance, confirm the variable reached the process: inside one of its Code sessions, run `echo "$CLAUDE_CONFIG_DIR"`.

The map is done when each instance has a known data dir, config dir, accounts, and transcript location, and every shared or bridged `projects/` is accounted for.

## Choose a topology

Match what the user wants to share against these verified patterns:

| Want | Pattern | Result |
|---|---|---|
| Two accounts in one Desktop, same configuration and history, switched by hand | Sign out and in within the app | Each account keeps its own sidebar in the same data dir. Signing in again on every switch. |
| Two accounts, one Desktop open at a time, same configuration and history, one-click switch | **Switcher**: a data dir per account behind the default data dir as a symlink, a CLI config dir per account linked to the shared one, and `claude-switch` | Every account stays signed in. The default `Claude.app`, Dock, updates, and links open the active account. Sidebars mirrored on each switch. |
| Two accounts open side by side | A wrapper per account with its own `--user-data-dir`, both on the shared config dir | Separate sidebars; mirror them only while both are quit. |
| Two CLI accounts, same configuration and history | A config dir per account; link the shared files into the second | Each `/login` stays separate; skills, `CLAUDE.md`, settings, and history are shared. |
| A second CLI account without another config dir | `claude setup-token` for that account, set as `CLAUDE_CODE_OAUTH_TOKEN` in its command | Works, without claude.ai connectors or Remote Control. |
| Fully separate accounts | Own data dir and own config dir, nothing linked | No sharing. |
| A different account per agent in an orchestrator such as Paseo | A provider entry per account setting `CLAUDE_CONFIG_DIR`, or one provider whose command is `claude-switch exec -- claude` | Each agent runs on the selected account. |

To set up the switcher, side-by-side mirroring, or linked CLI config dirs, read [`references/switching.md`](references/switching.md).

Out of reach: two accounts signed in at once inside one Desktop instance; one sidebar across accounts without mirroring; picking the Desktop account through environment credentials, which it ignores; and a distinct Dock tile per running wrapper.

What shares and what never does:

- **Shareable**: `CLAUDE.md`, `settings.json`, `skills/`, `agents/`, `commands/`, `output-styles/`, `plugins/`, `hooks/`, and history: `projects/` (transcripts and auto memory), `file-history/`, `history.jsonl`, `plans/`. Symlinks survive logins and settings writes.
- **Account-bound**: `.claude.json` (account identity, personal MCP servers, folder trust), credentials, `policy-limits.json`, `remote-settings.json`, caches. Sharing `.claude.json` makes a config dir report the other account. The Desktop also writes its signed-in account into its config dir's `.claude.json`, so give CLI accounts their own config dirs rather than the Desktop's.
- **Desktop sidebars**: records live under `claude-code-sessions/<account>/<org>/`, one partition per account, so each account lists only its own sessions until they are mirrored.

Name each account once and reuse the name everywhere, so every artifact traces back to it: for `work`, the data dir `~/Library/Application Support/Claude-Work`, the config dir `~/.claude-work`, any wrapper `Claude Work.app`, and the CLI command `claude-work`, defined as a shell alias or function rather than a script in a `bin` directory.

Guardrails for every change:

- Quit the target Desktop instance before editing its launcher, data dir, or session store; a running app overwrites store edits when it quits. Other instances can keep running, and one instance can edit another's store.
- Back up whatever you touch: the launcher and the data dir's `claude-code-sessions/`.
- When an instance moves to a new config dir, bridge its history **before** the first launch: make the new `projects/` a symlink to the old one. A Desktop that opens with an empty `projects/` can mark its sessions as unavailable.
- Give config dirs that share history the same retention. Each sweeps the shared transcripts with its own `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`, so the shortest setting wins.
- Keep one copy of each transcript. A hand-copied duplicate in a second project directory makes `claude --resume <session-id>` report not-found from any other project directory.
- Open a session in one account at a time. Mirrored records point at the same transcript, and two writers can corrupt it. Usage counts against the account that runs the turn.

To move an existing Desktop instance onto its own config dir with history intact, follow [`references/lean-instance-runbook.md`](references/lean-instance-runbook.md). It covers apply, verify, and undo.

## Telling instances apart

In the CLI, the command name is the instance (`claude` and `claude-work`), and `/status` shows the account and login method in use. On the Desktop, every running instance shows the same Dock tile. To recolor a wrapper's icon for Finder, Spotlight, and Launchpad, or to weigh a separate bundle for the running tile, read [`references/wrapper-icons.md`](references/wrapper-icons.md).

## Cleaning up

When instances, launchers, aliases, scripts, or config and data dirs have piled up, or an instance is being retired, follow [`references/cleanup.md`](references/cleanup.md).

## Recovering a session

When a Desktop session opens empty with "Session not found on disk", or history disappears after a config dir change or app update, the transcript is usually intact and only the metadata link broke. Follow [`references/session-recovery.md`](references/session-recovery.md) before sending any message in that session; a new message overwrites the link.

## Sources

Paths, precedence rules, and retention change between releases. When a fact here conflicts with what you observe, or a decision hinges on it, check [`references/sources.md`](references/sources.md) and follow the current documentation.
