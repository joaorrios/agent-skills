# Switching accounts

Recipes for the patterns in `SKILL.md`. Scripts live in `scripts/` relative to the skill root; `--help` on each documents its commands and configuration. Every recipe follows *switch the selector, not the secret*.

## Switcher

`scripts/claude-switch.py` turns the default data dir into a symlink to the active account's data dir and records the active account for the CLI. Its `use` command quits the Desktop, mirrors session records between all accounts, repoints the link, and reopens the Desktop, so run it from a terminal or the menu bar, never from inside the Desktop it quits. It quits without asking, ending any turn in progress, so switch between turns. The reopened Desktop and its Code sessions inherit the environment of whatever ran `use`: a terminal's exports, or SwiftBar's minimal `PATH`.

Install it by copying `claude-switch.py` and `claude-session-mirror.py` into one directory and linking `claude-switch.py` into the `PATH` as `claude-switch`; the switcher finds the mirror script next to its own resolved path. In its configuration, give every account its own `data_dir` and its own `config_dir`, and leave `~/.claude` as the shared config dir the Desktop uses. Every account's Desktop then writes the account-bound files in `~/.claude` in turn, including the cached organization policy (`policy-limits.json`, `remote-settings.json`), so after a switch Code sessions can start under the previous account's policy until the new one is fetched.

1. Quit the Desktop and back up `~/Library/Application Support/Claude`.
2. Run `claude-switch.py adopt <name>` for the account the Desktop is signed in to now.
   If `use` later reports that a data dir holds several partitions, list them with `claude-session-mirror.py --data-dir <data dir> --list` and set that account's `"partition"` to the full account UUID, a slash, and the start of the org UUID of the one with sessions.
3. For each other account, run `claude-switch.py use <name>`, sign in once in the Desktop it opens, and open a Code session so the account gets its partition. Records reach an account on the first switch after that, so finish with one more `use`.
4. For each account, run `claude-switch.py link-config <name>`, then sign in once with `CLAUDE_CONFIG_DIR=<config_dir> claude` and `/login`.
5. Make `claude` follow the active account with a shim: a `claude` script in its own directory, placed first in the `PATH`, that runs the real executable by absolute path (a bare `claude` would call the shim again):

   ```bash
   mkdir -p ~/.local/share/claude-switch/bin
   printf '#!/bin/sh\nexec "$HOME/.local/bin/claude-switch" exec -- "$HOME/.local/bin/claude" "$@"\n' > ~/.local/share/claude-switch/bin/claude
   chmod +x ~/.local/share/claude-switch/bin/claude
   for f in ~/.zprofile ~/.zshrc; do echo 'export PATH="$HOME/.local/share/claude-switch/bin:$PATH"' >> "$f"; done
   ```

   Both files matter: tools resolve `claude` through a login shell (`~/.zprofile`), and `~/.zshrc` may prepend other directories later in an interactive one. It is in place when `zsh -lc 'command -v claude'` and `zsh -lic 'command -v claude'` both print the shim.

   Every tool that finds `claude` through that `PATH` follows the menu, including orchestrators once restarted, and Claude Code updates leave the shim alone. For a fixed account per command instead, add aliases such as `alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'`.

Setup is complete when `use` alternates between every account without asking to sign in, each sidebar lists the other accounts' sessions, and `CLAUDE_CONFIG_DIR=<config_dir> claude auth status` shows each account's own email.

To undo, quit the Desktop, remove the symlink, and move one account's data dir back to `~/Library/Application Support/Claude`.

### Menu bar

`scripts/swiftbar/claude-switch.1h.sh` is a [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin that shows the active account, switches on click, and opens a terminal on the active account. Copy it into the SwiftBar plugin folder and set `CLAUDE_SWITCH` in it to the path of `claude-switch.py` unless that is on the `PATH`. Open SwiftBar once and turn on its Launch at login preference; the menu stays absent until SwiftBar runs. It is done when the menu lists every account and a click switches the Desktop.

## Mirroring session records

`scripts/claude-session-mirror.py` copies Desktop session records between account partitions, in one data dir or across several. `claude-switch.py use` runs it for all accounts; run it directly for side-by-side wrappers or a primary-and-alternate setup. Before mirroring, weigh:

- **Whole records travel**: the most recently active copy of a record replaces the others, with its title, archive state, model and effort, permission mode, and "always allow" grants. A grant made in one account applies in the others, and a rename or archive in one account is undone when another account's copy has newer activity.
- **Deletions do not propagate**: a session deleted in one account returns from another on the next mirror. Archive or rename it in every account instead.
- **Organization policy**: mirroring a work organization's sessions into a personal account copies their titles and makes their history reachable there.
- **Connectors**: a record carries its account's claude.ai connector list. Whether the other account uses or replaces it is unverified.

Mirroring is complete when a dry run prints `partitions already in sync` and each sidebar lists the expected sessions.

## Side by side

Give each account a wrapper `.app`, all on the shared config dir: a bundle such as `Claude Work.app` whose `Contents/Info.plist` names an executable script in `Contents/MacOS/` (`CFBundleExecutable`, plus a `CFBundleIdentifier` of its own), the script being `#!/bin/sh` followed by `exec open -n -a "Claude" --args --user-data-dir="$HOME/Library/Application Support/Claude-Work"`. Mirror with `claude-session-mirror.py --data-dir <a> --data-dir <b> --partitions … --apply` while every wrapper is quit. The setup is complete when each wrapper opens its own account without asking to sign in.

## Linked config dirs

Run `claude-switch.py link-config <name>` for each account (it needs only that account's entry in the switcher's configuration), then sign in once with `CLAUDE_CONFIG_DIR=<config_dir> claude` and `/login`. When linked config dirs keep separate `settings.json` files, give them the same `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`: each sweeps the shared transcripts with its own setting, so the shortest wins.

Complete when every shareable item in each account's config dir is a symlink into the shared one, any separate `settings.json` files hold the same retention values, and `CLAUDE_CONFIG_DIR=<config_dir> claude auth status` shows each account's own email.

## Orchestrators

Tools that launch Claude Code per agent, such as Paseo, run the `claude` executable directly, so shell aliases never reach them. With the shim from step 5, they follow the active account with no change of their own once their long-running process is restarted from a shell that has the new `PATH`. Restarting a desktop app may leave a separate daemon running with its old `PATH`; in Paseo, run `paseo daemon stop` and then `zsh -lic 'paseo daemon start'`, and confirm with `paseo provider diagnostic claude`. Otherwise select the account in the tool: one provider or profile per account setting `CLAUDE_CONFIG_DIR`, or a provider command of `claude-switch.py exec -- <absolute path to claude>`. Agents already running keep the account they started with. It is working when a new agent reports the active account's config dir and email.

## Second CLI account through a token

`claude setup-token`, run under the second account's login, prints a long-lived token that Claude Code reads from `CLAUDE_CODE_OAUTH_TOKEN` ahead of the stored login. Keep it in a Keychain item of your own and read it in that account's alias:

```bash
security add-generic-password -a "$USER" -s claude-personal-token -w   # paste the token when prompted
alias claude-personal='CLAUDE_CODE_OAUTH_TOKEN=$(security find-generic-password -a "$USER" -s claude-personal-token -w) claude'
```

It is working when `/status` under the alias shows the second account. Prefer a linked config dir with its own `/login` for interactive use; the token suits scripts and other non-interactive runs, and every process the CLI starts, including hooks and MCP servers, inherits it. `--bare` mode ignores it.
