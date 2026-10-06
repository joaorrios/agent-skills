#!/usr/bin/env python3
"""Switch which Claude account the Desktop app and the CLI use.

Each account keeps its own Desktop data dir and CLI config dir, each signed in
once through a native flow. Switching changes which directory is used,
never a credential: the default Desktop data dir becomes a symlink to the
active account's data dir, and the CLI reads the active account's config dir.

    claude-switch.py status
    claude-switch.py adopt work          # turn the current Desktop data dir into account "work"
    claude-switch.py link-config personal  # share configuration and history into personal's config dir
    claude-switch.py use personal        # quit the Desktop, mirror sessions, switch, reopen
    claude-switch.py exec -- claude      # run a command with the active account's config dir
    claude-switch.py env                 # print the export line for the active account

Configuration lives in ~/.config/claude-switch/config.json (or $CLAUDE_SWITCH_CONFIG):

    {
      "mirror": true,
      "accounts": {
        "work":     {"data_dir": "~/Library/Application Support/Claude-Work",
                     "config_dir": "~/.claude-work"},
        "personal": {"data_dir": "~/Library/Application Support/Claude-Personal",
                     "config_dir": "~/.claude-personal"}
      }
    }

Accounts appear in the menu bar in this order, under an optional "label".

Optional keys: "desktop_link" (the symlinked data dir the Desktop opens;
default: the Desktop's default data dir), "desktop_config_dir" (CLAUDE_CONFIG_DIR
for the Desktop; default: unset, so ~/.claude), "shared_config_dir" (the
directory link-config shares from; default ~/.claude), and per-account
"partition" (full account UUID, a slash, and the start of the org UUID of its
session records, needed only when its data dir holds more than one).
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CONFIG_FILE = Path(os.environ.get("CLAUDE_SWITCH_CONFIG", Path.home() / ".config/claude-switch/config.json")).expanduser()
STATE_FILE = CONFIG_FILE.with_name("active")
DEFAULT_DATA_DIR = Path.home() / "Library/Application Support/Claude"
# Configuration and history an account can share. Account-bound state
# (.claude.json, credentials, policy and remote settings, caches) stays per dir.
# plugins/ is left out: its synced/ folder holds account-synced plugins.
SHAREABLE = (
    "CLAUDE.md", "settings.json", "skills", "agents", "commands", "output-styles",
    "hooks", "projects", "file-history", "history.jsonl", "plans",
)
ACCOUNT_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def fail(message):
    sys.exit(f"error: {message}")


def load_mirror():
    path = Path(__file__).resolve().with_name("claude-session-mirror.py")
    spec = importlib.util.spec_from_file_location("claude_session_mirror", path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


def expand(value):
    return Path(value).expanduser() if value else None


def load_config():
    if not CONFIG_FILE.is_file():
        fail(f"{CONFIG_FILE} not found; see --help for its format")
    config = json.loads(CONFIG_FILE.read_text())
    accounts = config.get("accounts") or {}
    if not accounts:
        fail(f"{CONFIG_FILE} defines no accounts")
    for name, account in accounts.items():
        if not ACCOUNT_NAME.match(name):
            fail(f"account name {name!r} may use only letters, digits, '-' and '_'")
        for key in ("data_dir", "config_dir"):
            if key not in account:
                fail(f"account {name!r} needs {key!r}")
    return config


def account(config, name):
    if name not in config["accounts"]:
        fail(f"unknown account {name!r}; known: {', '.join(config['accounts'])}")
    return config["accounts"][name]


def link_path(config):
    return expand(config.get("desktop_link")) or DEFAULT_DATA_DIR


def active_desktop(config):
    link = link_path(config)
    if not link.is_symlink():
        return None
    target = link.resolve()
    for name, entry in config["accounts"].items():
        if expand(entry["data_dir"]).resolve() == target:
            return name
    return None


def active_cli(config):
    name = STATE_FILE.read_text().strip() if STATE_FILE.is_file() else ""
    return name if name in config["accounts"] else active_desktop(config)


def desktop_running(config, mirror):
    return link_path(config).resolve() in mirror.running_data_dirs()


def quit_desktop(config, mirror):
    """Ask the Desktop instance on the link to quit, as Cmd-Q would, and wait."""
    target = link_path(config).resolve()
    output = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True).stdout
    pids = []
    for line in output.splitlines():
        pid, _, command = line.strip().partition(" ")
        if not mirror.MAIN_PROCESS.match(command) or "--type=" in command:
            continue
        if "--user-data-dir=" in command:
            path = command.split("--user-data-dir=", 1)[1].split(" --", 1)[0]
        else:
            path = DEFAULT_DATA_DIR
        if Path(path).expanduser().resolve() == target:
            pids.append(int(pid))
    for pid in pids:
        os.kill(pid, 15)
    deadline = time.time() + 30
    while time.time() < deadline and desktop_running(config, mirror):
        time.sleep(0.5)
    if desktop_running(config, mirror):
        fail("the Desktop did not quit within 30 s; quit it and retry")


def partition_of(name, entry, mirror):
    store = expand(entry["data_dir"]) / "claude-code-sessions"
    found = mirror.partitions(store) if store.is_dir() else []
    prefix = entry.get("partition")
    if prefix:
        found = [p for p in found if f"{p.parent.name}/{p.name}".startswith(prefix)]
        if not found:
            fail(f"account {name!r}: \"partition\" {prefix!r} matches nothing; see claude-session-mirror.py --data-dir <its data dir> --list")
    if len(found) == 1:
        return found[0]
    if not found:
        return None
    fail(f"account {name!r}: its data dir holds {len(found)} partitions; set \"partition\" in {CONFIG_FILE}")


def mirror_plan(config, mirror):
    """Partitions and copies for every account, resolved before anything changes."""
    chosen = [p for name, entry in config["accounts"].items() if (p := partition_of(name, entry, mirror))]
    if len(chosen) < 2:
        return chosen, []
    return chosen, mirror.plan(chosen, "newest")


def apply_mirror(mirror, chosen, copies):
    if not copies:
        return
    for store in {p.parent.parent for p in chosen}:
        mirror.backup(store)
    for source, target, _ in copies:
        mirror.copy(source, target)
    print(f"mirrored {len(copies)} session record(s)")


def open_desktop(config):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
    if config.get("desktop_config_dir"):
        env["CLAUDE_CONFIG_DIR"] = str(expand(config["desktop_config_dir"]))
    command = ["open", "-n", "-a", "Claude"]
    link = link_path(config)
    if link != DEFAULT_DATA_DIR:
        command += ["--args", f"--user-data-dir={link}"]
    subprocess.run(command, check=True, env=env)


def cmd_status(config, mirror, args):
    desktop, cli = active_desktop(config), active_cli(config)
    link = link_path(config)
    if args.json:
        print(json.dumps({
            "desktop": desktop, "cli": cli, "running": desktop_running(config, mirror),
            "accounts": list(config["accounts"]),
            "labels": {name: entry.get("label", name) for name, entry in config["accounts"].items()},
        }))
        return
    print(f"desktop link: {link} -> {link.resolve() if link.is_symlink() else '(not a symlink; run adopt)'}")
    print(f"desktop running: {'yes' if desktop_running(config, mirror) else 'no'}")
    for name, entry in config["accounts"].items():
        marks = [m for m, on in (("desktop", name == desktop), ("cli", name == cli)) if on]
        print(f"  {name:<14} {', '.join(marks) or '-':<13} data_dir={entry['data_dir']}  config_dir={entry['config_dir']}")


def cmd_use(config, mirror, args):
    entry = account(config, args.name)
    data_dir = expand(entry["data_dir"])
    link = link_path(config)
    if link.exists() and not link.is_symlink():
        fail(f"{link} is a real directory; run adopt first")
    mirroring = config.get("mirror", True) and not args.no_mirror
    if mirroring:
        mirror_plan(config, mirror)  # fail on ambiguous partitions before quitting anything
        linked = link.resolve()
        for name, entry in config["accounts"].items():
            other = expand(entry["data_dir"])
            if other.resolve() != linked and mirror.instance_running(other):
                fail(f"a Claude instance is open on {name!r}'s data dir; quit it and retry")
    if desktop_running(config, mirror):
        quit_desktop(config, mirror)
    if mirroring:
        for name, entry in config["accounts"].items():
            if mirror.instance_running(expand(entry["data_dir"])):
                fail(f"a Claude instance is open on {name!r}'s data dir; quit it and retry")
        apply_mirror(mirror, *mirror_plan(config, mirror))
    data_dir.mkdir(parents=True, exist_ok=True)
    temporary = link.with_name(link.name + ".switching")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(data_dir)
    os.replace(temporary, link)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(args.name + "\n")
    print(f"active account: {args.name}")
    if not args.no_open:
        open_desktop(config)


def cmd_adopt(config, mirror, args):
    entry = account(config, args.name)
    data_dir = expand(entry["data_dir"])
    link = link_path(config)
    if link.is_symlink():
        fail(f"{link} is already a symlink")
    if not link.is_dir():
        fail(f"{link} not found")
    if data_dir.exists():
        fail(f"{data_dir} already exists")
    if desktop_running(config, mirror):
        fail("quit the Desktop first")
    link.rename(data_dir)
    link.symlink_to(data_dir)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(args.name + "\n")
    print(f"moved {link} to {data_dir} and linked it back; active account: {args.name}")


def cmd_link_config(config, _mirror, args):
    entry = account(config, args.name)
    shared = expand(config.get("shared_config_dir")) or Path.home() / ".claude"
    target = expand(entry["config_dir"])
    if target.resolve() == shared.resolve():
        fail(f"{args.name!r} uses the shared config dir itself")
    target.mkdir(parents=True, exist_ok=True)
    for item in SHAREABLE:
        source, destination = shared / item, target / item
        if not source.exists():
            continue
        if destination.is_symlink():
            if destination.resolve() != source.resolve():
                print(f"skip {item}: links to {os.readlink(destination)}")
            continue
        if destination.exists():
            print(f"skip {item}: {destination} already exists; merge it by hand")
            continue
        destination.symlink_to(source)
        print(f"linked {item}")
    print(f"sign in once with: CLAUDE_CONFIG_DIR={target} claude   (then /login)")


def cmd_env(config, _mirror, args):
    name = args.name or active_cli(config)
    if not name:
        fail("no active account; run use first")
    print(f"export CLAUDE_CONFIG_DIR={expand(account(config, name)['config_dir'])}")


def cmd_exec(config, _mirror, args):
    name = args.account or active_cli(config)
    if not name:
        fail("no active account; run use first")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        fail("nothing to run; pass a command after --")
    os.environ["CLAUDE_CONFIG_DIR"] = str(expand(account(config, name)["config_dir"]))
    os.execvp(command[0], command)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command_name", required=True)
    commands.add_parser("status").add_argument("--json", action="store_true")
    use = commands.add_parser("use")
    use.add_argument("name")
    use.add_argument("--no-mirror", action="store_true")
    use.add_argument("--no-open", action="store_true")
    commands.add_parser("adopt").add_argument("name")
    commands.add_parser("link-config").add_argument("name")
    commands.add_parser("env").add_argument("name", nargs="?")
    run = commands.add_parser("exec")
    run.add_argument("--account")
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    handlers = {
        "status": cmd_status, "use": cmd_use, "adopt": cmd_adopt,
        "link-config": cmd_link_config, "env": cmd_env, "exec": cmd_exec,
    }
    handlers[args.command_name](load_config(), load_mirror(), args)


if __name__ == "__main__":
    main()
