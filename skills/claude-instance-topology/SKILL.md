---
name: claude-instance-topology
description: Maps and safely changes how Claude Desktop and Claude Code CLI instances on macOS share accounts, configuration, and history. Use when adding, changing, or switching between Claude accounts or instances, including sharing skills, CLAUDE.md, or history across accounts and setting up a menu bar switcher; telling instances apart; cleaning up leftover instances; recovering a Desktop session that shows "Session not found on disk"; or before editing a Desktop session store.
license: MIT
compatibility: macOS with Claude Desktop and/or the Claude Code CLI. Scripts need Python 3; the icon script also needs Pillow, and the menu bar plugin needs SwiftBar.
---

# Claude Instance Topology

An instance's **topology** is what it shares with other instances: Desktop account and sidebar, Claude Code login, configuration, and history. Two independent settings decide all of it. Conflating them is how history gets lost.

| Setting | Scope | Decides |
|---|---|---|
| `--user-data-dir` (Electron argument; default `~/Library/Application Support/Claude`) | Claude Desktop only | The Desktop app identity: its claude.ai sign-in, sidebar session records, and UI state. |
| `CLAUDE_CONFIG_DIR` (environment variable; default `~/.claude`) | Desktop and CLI | Configuration (`CLAUDE.md`, `settings.json`, hooks, skills, plugins), Claude Code CLI credentials, and transcripts and auto memory under `projects/`. |

What follows from the table:

- **Accounts.** A Desktop account follows the data dir: several data dirs stay signed in to different accounts while sharing one config dir, and the data dir may be a symlink. CLI credentials, including the macOS Keychain entry, follow the config dir, so a new config dir starts with the CLI logged out. A Console sign-in without an API key lives in the Anthropic profile directory, outside any config dir.
- **Transcripts.** Desktop and CLI both read `CONFIG_DIR/projects/<project>/<session-id>.jsonl`. Pointing an instance that already has sessions at another config dir points it at a different, usually empty, `projects/`.
- **Desktop credentials.** It signs in with OAuth. It ignores `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `apiKeyHelper` (except under a third-party inference configuration) and never reads Anthropic profiles.
- **Synced configuration.** Skills and plugins enabled on a claude.ai account load in every instance signed in to that account, whatever its config dir.

## Authentication boundary

A topology changes where configuration and history live, never how authentication works. **Switch the selector, not the secret**: to change accounts, choose a different config dir or Desktop data dir, each holding the login it received through Anthropic's own flow.

| Practice | Use |
|---|---|
| Desktop sign-in, `/login`, `/logout` in the unmodified apps | The way every login is made and retired. |
| Choosing the config dir or data dir through an alias, launcher, symlink, or another tool's per-agent environment, including relocating a whole data dir | The documented way to keep several accounts. |
| `claude setup-token` with `CLAUDE_CODE_OAUTH_TOKEN`, in Claude Code itself | Documented for non-interactive environments. It cannot use claude.ai connectors or Remote Control. |
| Reading, extracting, or transferring the credentials the apps store, between accounts or machines (Keychain entries, `.credentials.json`, the account fields of `.claude.json`) | Outside the native flows. Leave them where the flows put them. |
| Running OAuth or token exchanges outside the apps, or using subscription credentials in tools that handle the credential themselves | Prohibited by Anthropic's terms. |

When a requested setup needs anything outside the first three rows, say so and offer the nearest native alternative. These rules cover credentials only; whether several accounts or seats may be used by one person, and how usage limits apply to them, is set by the consumer or commercial terms the accounts are under, so have the user confirm that before setting up switching. The current rules are in the legal and compliance page listed in `references/sources.md`.

## Map the current topology

Before changing anything, build the map from the machine itself:

1. List every Claude launcher: `/Applications/Claude.app` plus any wrapper `.app` whose executable (`CFBundleExecutable` in its `Info.plist`) is a script that runs `open -n -a "Claude" …`. Read each for `--user-data-dir` and `CLAUDE_CONFIG_DIR`, and check whether the default data dir is a symlink.
2. List CLI entry points: shell aliases and functions that set `CLAUDE_CONFIG_DIR`, the variable in the login shell, and tools that launch Claude Code with their own per-agent environment.
3. For each config dir, list which shareable items are symlinks and where they point.
4. For a running Desktop instance, confirm the variable reached the process: inside one of its Code sessions, run `echo "$CLAUDE_CONFIG_DIR"`.

The map is done when each instance has a known data dir, config dir, account, and transcript location, and every symlink is accounted for.

## Choose a topology

| Want | Pattern | Result |
|---|---|---|
| Accounts that share configuration and history, one Desktop open at a time, switched in one click or from the menu bar | **Switcher**: a data dir per account behind the default data dir as a symlink, a CLI config dir per account linked to the shared one, and `claude-switch.py` | Every account stays signed in. The unmodified `Claude.app`, its Dock icon, updates, and links open the active account. Sidebars mirrored on each switch. All accounts' Desktops share one config dir, so it suits accounts in one organization. |
| A primary account plus an alternate that also sees the primary's sessions | The switcher, or the mirror script with `--mode primary` | The alternate lists the primary's sessions; the primary keeps only its own. |
| Accounts in one Desktop, switched by hand | Sign out and in within the app | Each account keeps its own sidebar in the same data dir; signing in again on every switch. |
| Accounts open side by side | A wrapper per account with its own `--user-data-dir`, on the shared config dir | Separate sidebars, mirrored only while all are quit. The shared `.claude.json` names whichever account wrote last, so keep CLI logins out of that config dir. |
| CLI accounts that share configuration and history | A config dir per account, with the shareable items linked from the shared one | Separate `/login`s; shared skills, `CLAUDE.md`, settings, and history. |
| A second CLI account without another config dir | `claude setup-token` for that account, set as `CLAUDE_CODE_OAUTH_TOKEN` in its command | Works, without claude.ai connectors or Remote Control. |
| A different account per agent in an orchestrator | The orchestrator's per-agent environment sets `CLAUDE_CONFIG_DIR`, or its command is `claude-switch.py exec -- claude` | Each new agent runs on the selected account. |
| Fully separate accounts | Own data dir and own config dir, nothing linked | No sharing. |

Report these as unavailable: two accounts signed in at once inside one Desktop instance, a single sidebar across accounts without mirroring, choosing the Desktop account through environment credentials, and a distinct Dock tile per running wrapper.

Recipes for every pattern are in [`references/switching.md`](references/switching.md).

This step is complete when the user has agreed on a pattern and every account has a name, a data dir, and a config dir.

### What can be shared

- **Shareable**: `CLAUDE.md`, `settings.json`, `skills/`, `agents/`, `commands/`, `output-styles/`, `hooks/`, and history: `projects/` (transcripts and auto memory), `file-history/`, `history.jsonl`, `plans/`. Symlinks survive logins and settings writes.
- **Account-bound**: `.claude.json` (account identity, personal MCP servers, folder trust; it is `~/.claude.json` for the default config dir and inside any other config dir), credentials, `policy-limits.json`, `remote-settings.json`, `plugins/` (its `synced/` folder is per account; install plugins in each config dir), and caches. A shared `.claude.json` makes a config dir report another account, and the Desktop writes its signed-in account into its config dir's `.claude.json`.
- **Desktop sidebars**: records live under `claude-code-sessions/<account>/<org>/`, one partition per account, so each account lists only its own sessions until they are mirrored.

### Naming

Name each account once and reuse the name everywhere, so every artifact traces back to it: for `work`, the data dir `~/Library/Application Support/Claude-Work`, the config dir `~/.claude-work`, any wrapper `Claude Work.app`, and the CLI command `claude-work`, defined as a shell alias or function.

## Change safely

- Quit the target Desktop instance before editing its launcher, data dir, or session store; a running app overwrites store edits when it quits. Other instances can keep running, and one instance can edit another's store.
- Back up whatever you touch: the launcher and the data dir's `claude-code-sessions/`.
- Open a session in one account at a time. Mirrored records point at the same transcript, and two writers can corrupt it. Usage counts against the account that runs the turn.

To move an existing Desktop instance onto its own config dir with history intact, follow [`references/lean-instance-runbook.md`](references/lean-instance-runbook.md).

## Telling instances apart

In the CLI, the command name is the instance (`claude-work`, or a plain `claude` aliased to the switcher), and `/status` shows the account in use. On the Desktop, every running instance shows the same Dock tile; to recolor a wrapper's icon for Finder, Spotlight, and Launchpad, read [`references/wrapper-icons.md`](references/wrapper-icons.md).

## Cleaning up

When instances, launchers, aliases, scripts, or config and data dirs have piled up, or an account is being retired, follow [`references/cleanup.md`](references/cleanup.md).

## Recovering a session

When a Desktop session opens empty with "Session not found on disk", or history disappears after a config dir change or app update, the transcript is usually intact and only the record's link broke. Follow [`references/session-recovery.md`](references/session-recovery.md) before sending any message in that session; a new message overwrites the link.

## Sources

Paths, precedence rules, and retention change between releases. When a fact here conflicts with what you observe, or a decision hinges on it, check [`references/sources.md`](references/sources.md) and follow the current documentation.
