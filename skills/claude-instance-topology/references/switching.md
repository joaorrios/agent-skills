# Switching accounts

Recipes for the patterns in `SKILL.md`. Scripts live in `scripts/` relative to the skill root. Each changes only which directory is used; every login happens in the app or through `/login`.

## Switcher

One Desktop instance open at a time, every account signed in once, configuration and history shared. The default data dir `~/Library/Application Support/Claude` becomes a symlink to the active account's data dir, so the unmodified `Claude.app`, its Dock icon, app updates, and `claude://` links all open the active account. `scripts/claude-switch.py` does the switching:

- `status [--json]`: active account and whether the Desktop is running.
- `adopt <name>`: moves the current default data dir to that account's `data_dir` and links it back. Run once, with the Desktop quit.
- `use <name>`: quits the Desktop instance on the link, mirrors session records between all accounts (`--no-mirror` to skip), repoints the link, records the account for the CLI, and reopens the Desktop (`--no-open` to skip). It must run outside the Desktop, from a terminal or the menu bar, because it quits the app it would run in.
- `link-config <name>`: links the shareable files from the shared config dir into that account's `config_dir`, skipping anything already there.
- `env [name]` and `exec [--account name] -- <command>`: the active account's `CLAUDE_CONFIG_DIR`, as an export line or for one command.

The configuration file is `~/.config/claude-switch/config.json`; `--help` documents its keys. Give every account its own `config_dir`, and keep `~/.claude` as the shared config dir the Desktop uses:

```json
{
  "mirror": true,
  "accounts": {
    "work":     {"data_dir": "~/Library/Application Support/Claude-Work",     "config_dir": "~/.claude-work"},
    "personal": {"data_dir": "~/Library/Application Support/Claude-Personal", "config_dir": "~/.claude-personal"}
  }
}
```

Set up:

1. Quit the Desktop. Back up `~/Library/Application Support/Claude`.
2. `claude-switch.py adopt work`, naming the account the Desktop is signed in to now.
3. `claude-switch.py use personal`. The Desktop opens on an empty data dir; sign in to that account once.
4. For each account, `claude-switch.py link-config <name>`, then sign in once with `CLAUDE_CONFIG_DIR=<config_dir> claude` and `/login`.
5. For the CLI, add aliases per account (`alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'`), or follow the active account with `alias claude='claude-switch.py exec -- claude'`.

Setup is complete when `use` alternates between accounts without asking to sign in and each account's sidebar lists the other's sessions.

To undo, quit the Desktop, remove the symlink, and move the account's data dir back to `~/Library/Application Support/Claude`.

### Menu bar

`scripts/swiftbar/claude-switch.30s.sh` is a [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin: it shows the active account, switches on click, and opens a terminal on the active account. Copy it into the SwiftBar plugin folder and set `CLAUDE_SWITCH` in it to the path of `claude-switch.py` unless that is on the `PATH`.

To show usage limits per account, run the unmodified `claude` with each account's `CLAUDE_CONFIG_DIR` and read its `/usage` output, or count tokens from the local transcripts. Usage tools that read the stored token and call Anthropic's API themselves fall outside the authentication boundary.

## Mirroring session records

`scripts/claude-session-mirror.py` copies Desktop session records between account partitions, in one data dir or across several (`--data-dir` repeated). `--list` shows the partitions; `--partitions` picks which to sync, by `account/org` prefix, or `<data-dir-name>/account/org` when the same account appears in two data dirs. By default the newest record of each session wins in both directions; `--mode primary` copies only from the first partition. It runs as a dry run unless `--apply` is given, refuses while a listed data dir is open, backs up every store first, and copies records unchanged. `claude-switch.py use` runs it automatically.

A mirrored record points at the same transcript, so continuing the session in either account extends one conversation. Before mirroring between accounts, weigh:

- **One account at a time per session**: two writers can corrupt the transcript.
- **Organization policy**: mirroring a work organization's sessions into a personal account copies their titles and makes their history reachable there.
- **Connectors**: a record carries its account's claude.ai connector list. Whether the other account uses or replaces it is unverified.

## Side by side

For two accounts open at once, give each a wrapper `.app` with its own `--user-data-dir` (the runbook shows the launcher format) and keep both on the shared config dir. Mirror with `claude-session-mirror.py --data-dir <a> --data-dir <b> --partitions … --apply` only while both are quit.

## Orchestrators

Tools that launch Claude Code per agent can select the account through the environment. In Paseo, either define a provider per account with `"extends": "claude"` and `"env": {"CLAUDE_CONFIG_DIR": "…"}`, or one provider whose `command` is `["<path>/claude-switch.py", "exec", "--", "claude"]` to follow the active account. Agents already running keep the account they started with. The single-provider form is untested.

## Second CLI account through a token

`claude setup-token`, run under the second account's login, prints a long-lived token; Claude Code reads it from `CLAUDE_CODE_OAUTH_TOKEN` ahead of the stored login. Store it in your own Keychain item and read it in that account's alias:

```bash
security add-generic-password -a "$USER" -s claude-personal-token -w   # paste the token when prompted
alias claude-personal='CLAUDE_CODE_OAUTH_TOKEN=$(security find-generic-password -a "$USER" -s claude-personal-token -w) claude'
```

The token makes model requests only: claude.ai connectors and Remote Control are unavailable, and `--bare` mode ignores it.
