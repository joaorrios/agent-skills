# Clean up instances

Use when Claude instances, launchers, aliases, scripts, or directories have accumulated, or when retiring an instance.

## 1. Inventory

Build the topology map from `SKILL.md`, then extend it with every artifact that can belong to an instance:

- **Launchers**: `.app` bundles in `/Applications` and `~/Applications` whose executable launches Claude.
- **Shell entry points**: aliases, functions, and `CLAUDE_CONFIG_DIR` exports in shell startup files (`~/.zshrc`, `~/.zprofile`, `~/.bashrc`, `~/.bash_profile`, fish config), and `claude*` scripts in `~/bin`, `~/.local/bin`, `/usr/local/bin`, and `/opt/homebrew/bin`. Tell wrapper scripts apart from official installations: `which -a claude` lists every `claude` on the `PATH`, and `claude doctor` reports the installation in use.
- **Tool configurations**: agent orchestrators and editors that launch Claude Code with their own environment, such as Paseo provider entries in `~/.paseo/config.json`, can set `CLAUDE_CONFIG_DIR` per agent.
- **Config dirs**: `~/.claude` and every `~/.claude-*` or other directory any entry point passes as `CLAUDE_CONFIG_DIR`.
- **Data dirs**: `~/Library/Application Support/Claude*`, including a default data dir that is a symlink, and the switcher's `~/.config/claude-switch/`.
- **Links**: symlinks inside config dirs, including `projects/` bridges, and any whose target no longer exists.
- **Backups**: `*.orig-backup` files, `AppIcon.icns.orig-backup`, and tarball folders such as `~/.claude-instance-backups`.

The inventory is complete when every artifact is attributed to an instance, or marked as orphaned.

## 2. Decide

Present the inventory to the user grouped by instance, and agree on one decision per artifact:

- **Keep**: in use and named by the convention in `SKILL.md`.
- **Rename**: in use under a name that hides which instance it belongs to.
- **Consolidate**: a duplicate, such as two aliases for one config dir or a `bin` script that repeats an alias.
- **Retire**: belongs to an instance the user no longer wants, or to none.

This step is complete when the user has agreed to a decision for every artifact.

## 3. Act

Archive before removing. Retire an instance in this order:

1. Quit it.
2. End its logins natively: run `/logout` under its config dir (`CLAUDE_CONFIG_DIR=… claude`), which removes and revokes the CLI credential, and sign out of its Desktop data dir from the app.
3. Move any transcripts worth keeping into the config dir that stays. Move only sessions whose ID is not already there, since duplicate copies break resume by ID.
4. Remove its launcher, aliases, and scripts.
5. Archive its config and data dirs with `tar`, then delete them once the user confirms nothing is missing.

Remove symlinks whose targets are gone, and delete backups only after the change they protect has been verified.

Cleanup is complete when the rebuilt map matches the agreed decisions and no entry point refers to a missing directory.
