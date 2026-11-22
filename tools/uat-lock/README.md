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

The turn starts once the 1-minute load is below 8, no GitHub Actions `Runner.Worker` job is running, and no Electron test runs outside the queue. While you wait, `uat-lock status` names the owner of each blocker. A turn lasts at most 90 minutes of wall-clock time, sleep included (`UAT_LOCK_MAX_TURN`, in minutes; raise it for a long exploratory hold, or set `inf` for none). Past that, the head stops the holder even when its session is alive but hung: first the holder itself, which closes its apps as it ends, then, if the turn is still held, every process with `run.lock` open and the Electron test processes its session started or left orphaned during the turn. The limit is the holder's own, so a holder that raised it keeps it. When a `run` command ends, processes it left with `run.lock` open are stopped too. The head of the queue closes orphaned Electron test processes on its own; one with a live launcher waits for its owner or the user.

When a turn ends, by exit, stdin EOF, a stop signal or an error, it closes the Electron test processes its session started during the turn, and any left with no live launcher, before the next turn begins. An app another session or the user started meanwhile stays open. A holder killed with SIGKILL leaves its apps as orphans, which the next head closes. `uat-lock --help` lists the options and environment variables.

## Test

```bash
python3 -m unittest discover -s tools/uat-lock -p 'test_*.py'
```

Each test uses its own temporary state directory and leaves the machine's queue untouched. Tests that start real processes count only the Electron copies they place under their own temporary directory, so they never close another run's app.
