# Switching accounts

Recipes for the patterns in `SKILL.md`. Scripts live in `scripts/` relative to the skill root; `--help` on each documents its commands and configuration. Every recipe changes only which directory is used; each login happens in the app or through `/login`.

## Switcher

`scripts/claude-switch.py` turns the default data dir into a symlink to the active account's data dir and records the active account for the CLI. Its `use` command quits the Desktop, mirrors session records between all accounts, repoints the link, and reopens the Desktop, so run it from a terminal or the menu bar, never from inside the Desktop it quits. It quits without asking, ending any turn in progress, so switch between turns. The reopened Desktop and its Code sessions inherit the environment of whatever ran `use`: a terminal's exports, or SwiftBar's minimal `PATH`.

Install it by copying `claude-switch.py` and `claude-session-mirror.py` into one directory and linking `claude-switch.py` into the `PATH` as `claude-switch`; the switcher finds the mirror script next to its own resolved path. In its configuration, give every account its own `data_dir` and its own `config_dir`, and leave `~/.claude` as the shared config dir the Desktop uses. Every account's Desktop then writes the account-bound files in `~/.claude` in turn: `.claude.json`, the cached organization policy (`policy-limits.json`, `remote-settings.json`), and synced plugins. After a switch, Code sessions can start under the previous account's cached policy until the new one is fetched, and a plain `claude` on `~/.claude` reports whichever account wrote last. Use the switcher for accounts in one organization; keep accounts in different organizations fully separate.

1. Quit the Desktop and back up `~/Library/Application Support/Claude`.
2. Run `claude-switch.py adopt <name>` for the account the Desktop is signed in to now.
   If `use` later reports that a data dir holds several partitions, list them with `claude-session-mirror.py --data-dir <data dir> --list` and set that account's `"partition"` to the full account UUID, a slash, and the start of the org UUID of the one with sessions.
3. For each other account, run `claude-switch.py use <name>`, sign in once in the Desktop it opens, and open a Code session so the account gets its partition. Records reach an account on the first switch after that, so finish with one more `use`.
4. For each account, run `claude-switch.py link-config <name>`, then sign in once with `CLAUDE_CONFIG_DIR=<config_dir> claude` and `/login`.
5. Give the CLI a command per account (`alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'`), or follow the active account with `alias claude='claude-switch.py exec -- claude'`.

Setup is complete when `use` alternates between every account without asking to sign in, each sidebar lists the other accounts' sessions, and `CLAUDE_CONFIG_DIR=<config_dir> claude auth status` shows each account's own email.

To undo, quit the Desktop, remove the symlink, and move one account's data dir back to `~/Library/Application Support/Claude`.

### Menu bar

`scripts/swiftbar/claude-switch.1h.sh` is a [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin that shows the active account, switches on click, and opens a terminal on the active account. Copy it into the SwiftBar plugin folder and set `CLAUDE_SWITCH` in it to the path of `claude-switch.py` unless that is on the `PATH`. Open SwiftBar once and turn on its Launch at login preference; the menu stays absent until SwiftBar runs. It is done when the menu lists every account and a click switches the Desktop.

Usage limits per account come from running the unmodified `claude` under each account's `CLAUDE_CONFIG_DIR` and reading `/usage`, or from token counts in the local transcripts.

## Mirroring session records

`scripts/claude-session-mirror.py` copies Desktop session records between account partitions, in one data dir or across several. `claude-switch.py use` runs it for all accounts; run it directly for side-by-side wrappers or a primary-and-alternate setup. Before mirroring, weigh:

- **Whole records travel**: the most recently active copy of a record replaces the others, with its title, archive state, model and effort, permission mode, and "always allow" grants. A grant made in one account applies in the others, and a rename or archive in one account is undone when another account's copy has newer activity.
- **Deletions do not propagate**: a session deleted in one account returns from another on the next mirror. Archive or rename it in every account instead.
- **Organization policy**: mirroring a work organization's sessions into a personal account copies their titles and makes their history reachable there.
- **Connectors**: a record carries its account's claude.ai connector list. Whether the other account uses or replaces it is unverified.

## Side by side

Give each account a wrapper `.app` with its own `--user-data-dir` (the runbook shows the launcher format), all on the shared config dir. Mirror with `claude-session-mirror.py --data-dir <a> --data-dir <b> --partitions … --apply` while every wrapper is quit. The setup is complete when each wrapper opens its own account without asking to sign in.

## Linked config dirs

When linked config dirs keep separate `settings.json` files, give them the same `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`: each sweeps the shared transcripts with its own setting, so the shortest wins.

## Orchestrators

Tools that launch Claude Code per agent run the `claude` executable directly, so shell aliases never reach them. Select the account in the tool: one provider or profile per account setting `CLAUDE_CONFIG_DIR`, or a single one whose command is the switcher, to follow the active account. Use absolute paths, since the tool's `PATH` may differ from the shell's. In Paseo, override the bundled provider in `~/.paseo/config.json` and run `paseo reload`; no daemon restart is needed:

```json
{ "agents": { "providers": { "claude": {
  "command": ["/Users/<you>/.local/bin/claude-switch", "exec", "--", "/Users/<you>/.local/bin/claude"]
} } } }
```

Agents already running keep the account they started with. It is working when `paseo provider diagnostic claude` shows the active account's config dir and email.

## Second CLI account through a token

`claude setup-token`, run under the second account's login, prints a long-lived token that Claude Code reads from `CLAUDE_CODE_OAUTH_TOKEN` ahead of the stored login. Keep it in a Keychain item of your own and read it in that account's alias:

```bash
security add-generic-password -a "$USER" -s claude-personal-token -w   # paste the token when prompted
alias claude-personal='CLAUDE_CODE_OAUTH_TOKEN=$(security find-generic-password -a "$USER" -s claude-personal-token -w) claude'
```

It is working when `/status` under the alias shows the second account. Prefer a linked config dir with its own `/login` for interactive use; the token suits scripts and other non-interactive runs, and every process the CLI starts, including hooks and MCP servers, inherits it. The token makes model requests only: claude.ai connectors and Remote Control are unavailable, and `--bare` mode ignores it.
