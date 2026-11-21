# uat-lock

One queue per machine for local UAT and Electron test runs. Every holder waits its turn on a kernel `flock` in `~/.local/state/uat-lock/run.lock`, so a killed holder releases its turn and never leaves a stale lock. The queue is the only lock: harnesses keep none of their own.

## Install

Once per machine, with Python 3 on macOS or Linux and `~/.local/bin` on `PATH`:

```bash
install -d ~/.local/bin
install -m 755 tools/uat-lock/uat-lock ~/.local/bin/uat-lock
```

Repeat the copy to upgrade. Queue state lives in `~/.local/state/uat-lock/`, one per machine.

## Use

- **A command:** `uat-lock run --label <ticket> -- <test command>`.
- **A harness that opens and closes Electron itself** (Node, Playwright): spawn `uat-lock hold --label <ticket>` with a stdin pipe, launch Electron after it prints `READY`, and close its stdin when the session ends. A crash releases the turn too.
- **Calls nested inside a turn** pass through: commands under `run` inherit the turn; under `hold`, export `UAT_LOCK_HELD=1 UAT_LOCK_HOLDER_PID=<hold pid>` to them.

The turn starts once the 1-minute load is below 8, no GitHub Actions `Runner.Worker` job is running, and no Electron test runs outside the queue. While you wait, `uat-lock status` names the owner of each blocker; its owner or the user ends it. `uat-lock --help` lists the options and environment variables.

## Test

```bash
python3 -m unittest discover -s tools/uat-lock -p 'test_*.py'
```

Each test uses its own temporary state directory and leaves the machine's queue untouched.
