"""Tests for uat-lock. Run: python3 -m unittest test_uat_lock (from this folder).

Every test uses its own temporary UAT_LOCK_DIR, a fake load file, and a fake
process list unless it needs the real process tree, so it never touches the
machine's queue.
"""
import contextlib
import errno
import fcntl
import importlib.machinery
import importlib.util
import io
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uat-lock")
NM_ELECTRON = "/w/app/node_modules/.pnpm/electron@41/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron"


class UatLockTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="uat-lock-test-")
        self.dir = os.path.join(self.tmp, "state")
        self.load_file = os.path.join(self.tmp, "load")
        self.ps_file = os.path.join(self.tmp, "ps")
        self.set_load(0.5)
        self.set_ps([])
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith("UAT_LOCK_") and k != "GITHUB_ACTIONS"}
        self.env.update(UAT_LOCK_DIR=self.dir, UAT_LOCK_POLL="0.05",
                        UAT_LOCK_LOAD_FILE=self.load_file, UAT_LOCK_PS_FILE=self.ps_file)
        self.procs = []
        self.errs = {}

    def tearDown(self):
        for p in self.procs:
            if p.poll() is None:
                p.kill()
            p.wait()
            for f in (p.stdin, p.stdout, p.stderr):
                if f:
                    f.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers
    def set_load(self, value):
        with open(self.load_file, "w") as f:
            f.write(str(value))

    def set_ps(self, rows):
        """Rows are (pid, ppid, etime, command) or (pid, ppid, etime, argv0, args)
        when argv[0] has spaces, as ps reports it apart from the command line."""
        with open(self.ps_file, "w") as f:
            for row in rows:
                pid, ppid, etime, cmd = row[:4]
                if len(row) == 5:
                    cmd = "%s\t%s" % (cmd, row[4])
                f.write("%d %d %s %s\n" % (pid, ppid, etime, cmd))

    def start(self, *args, env=None, stdin=subprocess.PIPE):
        p = subprocess.Popen([sys.executable, SCRIPT] + list(args), env=env or self.env,
                             stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.procs.append(p)
        return p

    def run_cmd(self, *args, env=None, timeout=30):
        return subprocess.run([sys.executable, SCRIPT] + list(args), env=env or self.env,
                              stdin=subprocess.DEVNULL, capture_output=True,
                              universal_newlines=True, timeout=timeout)

    def read_err(self, p, timeout):
        ready, _, _ = select.select([p.stderr], [], [], timeout)
        if not ready:
            return False
        chunk = os.read(p.stderr.fileno(), 65536).decode()
        self.errs[p.pid] = self.errs.get(p.pid, "") + chunk
        return bool(chunk)

    def wait_err(self, p, text, timeout=20):
        """Wait until p printed text on stderr, then check it is still waiting."""
        end = time.time() + timeout
        while text not in self.errs.get(p.pid, ""):
            if time.time() > end or not self.read_err(p, end - time.time()):
                self.fail("never printed %r; got %r" % (text, self.errs.get(p.pid, "")))
        self.assertIsNone(p.poll(), "process should still be waiting")

    def wait_ready(self, p, timeout=20):
        ready, _, _ = select.select([p.stdout], [], [], timeout)
        self.assertTrue(ready, "no READY within %ss" % timeout)
        self.assertEqual(p.stdout.readline().decode().strip(), "READY")

    def release(self, p):
        p.stdin.close()
        p.stdin = None

    def finish(self, p, timeout=20):
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out.decode(), self.errs.get(p.pid, "") + err.decode()

    def run_lock_free(self):
        path = os.path.join(self.dir, "run.lock")
        fd = os.open(path, os.O_RDWR | os.O_CREAT)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False
        finally:
            os.close(fd)

    def status(self):
        r = self.run_cmd("status")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    # run
    def test_run_returns_exit_code_and_releases(self):
        r = self.run_cmd("run", "--", "sh", "-c", "echo hi; exit 3")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout, "hi\n")
        self.assertTrue(self.run_lock_free())
        out = self.status()
        self.assertIn("running: none", out)
        self.assertIn("queue: empty", out)

    def test_run_exports_holder_to_command(self):
        r = self.run_cmd("run", "--", "sh", "-c", 'echo "$UAT_LOCK_HELD $UAT_LOCK_HOLDER_PID $PPID"')
        held, holder, ppid = r.stdout.split()
        self.assertEqual(held, "1")
        self.assertEqual(holder, ppid)

    def test_runs_are_serialized_in_order(self):
        a = self.start("hold", "--label", "A")
        self.wait_ready(a)
        b = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(b, "waiting for the running holder")
        out = self.status()
        self.assertIn("label=A", out.split("running: ")[1].splitlines()[0])
        self.assertIn("queue 1: ticket 1 pid=%d" % b.pid, out)
        self.release(a)
        self.assertEqual(self.finish(b)[0], 0)

    # hold
    def test_hold_releases_on_stdin_eof(self):
        p = self.start("hold", "--label", "electron qa")
        self.wait_ready(p)
        self.assertFalse(self.run_lock_free())
        self.assertIn("label=electron qa", self.status())
        self.release(p)
        self.assertEqual(self.finish(p)[0], 0)
        self.assertTrue(self.run_lock_free())

    def test_hold_releases_on_sigkill(self):
        p = self.start("hold")
        self.wait_ready(p)
        p.kill()
        p.wait()
        self.assertTrue(self.run_lock_free())
        self.assertIn("running: none", self.status())
        r = self.run_cmd("run", "--", "true")
        self.assertEqual(r.returncode, 0)

    def test_hold_releases_on_sigterm(self):
        p = self.start("hold")
        self.wait_ready(p)
        p.send_signal(signal.SIGTERM)
        p.wait(timeout=5)
        self.assertTrue(self.run_lock_free())

    # re-entrancy (needs the real process tree)
    def real_env(self):
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1")
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        return env

    def test_nested_run_and_hold_pass_through(self):
        nested = "%s %s run -- echo nested-run && %s %s hold </dev/null" % (
            sys.executable, SCRIPT, sys.executable, SCRIPT)
        r = self.run_cmd("run", "--", "sh", "-c", nested, env=self.real_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split(), ["nested-run", "READY"])
        self.assertIn("passing through", r.stderr)

    def test_nested_under_hold_passes_through_with_exported_pid(self):
        env = self.real_env()
        h = self.start("hold", env=env)
        self.wait_ready(h)
        nested = dict(env, UAT_LOCK_HELD="1", UAT_LOCK_HOLDER_PID=str(h.pid))
        # Started by this test process, which is the hold's owner.
        r = self.run_cmd("run", "--", "echo", "inside", env=nested)
        self.assertEqual(r.stdout, "inside\n", r.stderr)
        self.release(h)
        self.finish(h)

    def test_spoofed_holder_queues_instead(self):
        env = self.real_env()
        h = self.start("hold", env=env)
        self.wait_ready(h)
        spoof = dict(env, UAT_LOCK_HELD="1", UAT_LOCK_HOLDER_PID=str(os.getpid()))
        b = self.start("run", "--", "true", env=spoof, stdin=subprocess.DEVNULL)
        self.wait_err(b, "waiting for the running holder")
        self.release(h)
        rc, _, err = self.finish(b)
        self.assertEqual(rc, 0)
        self.assertIn("does not hold run.lock", err)

    # stale tickets
    def test_stale_tickets_are_removed(self):
        a = self.start("hold")
        self.wait_ready(a)
        dead = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(dead, "ticket 1:")
        dead.kill()
        dead.wait()
        orphan = os.path.join(self.dir, "tickets", "000000000099.lock")
        open(orphan, "w").close()
        tickets = os.path.join(self.dir, "tickets")
        self.assertEqual(len(os.listdir(tickets)), 2)
        self.assertIn("queue: empty", self.status())
        self.assertEqual(os.listdir(tickets), [])
        self.release(a)

    # gates
    def test_waits_for_load(self):
        self.set_load(9.5)
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(p, "load 9.50 to drop below 8")
        self.set_load(1)
        rc, _, err = self.finish(p)
        self.assertEqual(rc, 0)
        self.assertIn("load 9.50 to drop below 8", err)

    def test_waits_for_active_runner_worker(self):
        self.set_ps([(700, 1, "10-00:00:00", "/Users/x/bin/Runner.Listener run"),
                     (701, 700, "14:01", "/Users/x/bin.2.3/Runner.Worker spawnclient 1 2")])
        p = self.start("hold")
        self.wait_err(p, "CI job to finish (Runner.Worker pid 701, running 14:01)")
        self.set_ps([(700, 1, "10-00:00:00", "/Users/x/bin/Runner.Listener run")])
        self.wait_ready(p)
        self.release(p)
        _, _, err = self.finish(p)
        self.assertIn("CI job to finish (Runner.Worker pid 701, running 14:01)", err)

    def test_runner_gate_skipped_by_env(self):
        self.set_ps([(701, 1, "01:00", "/x/Runner.Worker spawnclient 1 2")])
        for extra in ({"UAT_LOCK_IGNORE_RUNNER": "1"}, {"GITHUB_ACTIONS": "true"}):
            r = self.run_cmd("run", "--", "true", env=dict(self.env, **extra))
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_waits_for_out_of_queue_electron(self):
        self.set_ps([(800, 1, "05:00", "node /w/app/node_modules/.bin/electron-vite dev"),
                     (801, 800, "04:59", NM_ELECTRON + " ."),
                     (802, 801, "04:58", NM_ELECTRON.replace("MacOS/Electron", "Frameworks/Electron Helper.app/Contents/MacOS/Electron Helper") + " --type=gpu-process")])
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(p, "out-of-queue Electron pid 801 (worktree /w/app, running 04:59) to exit")
        self.set_ps([])
        rc, _, err = self.finish(p)
        self.assertEqual(rc, 0)
        self.assertIn("out-of-queue Electron pid 801 (worktree /w/app, running 04:59) to exit", err)

    def test_ignores_desktop_apps_and_honours_ignore_env(self):
        self.set_ps([(900, 1, "1-00:00:00", "/Applications/Slack.app/Contents/MacOS/Slack"),
                     (901, 1, "1-00:00:00", "/Applications/Claude.app/Contents/Frameworks/Electron Framework.framework/Helpers/chrome_crashpad_handler"),
                     (902, 1, "1-00:00:00", "/Applications/Foo.app/Contents/MacOS/Electron out/main/index.js")])
        self.assertEqual(self.run_cmd("run", "--", "true").returncode, 0)
        self.set_ps([(903, 1, "00:10", NM_ELECTRON + " -r /w/node_modules/playwright-core/lib/server/electron/loader.js")])
        r = self.run_cmd("run", "--", "true", env=dict(self.env, UAT_LOCK_IGNORE_ELECTRON="1"))
        self.assertEqual(r.returncode, 0)

    def test_detects_out_main_and_playwright_loader(self):
        self.set_ps([(950, 1, "00:10", "/w/b/node_modules/electron/dist/electron /w/b/out/main/index.js"),
                     (951, 1, "00:10", "node -r /w/c/node_modules/playwright-core/lib/server/electron/loader.js /w/c")])
        out = self.status()
        self.assertIn("electron: pid 950", out)
        self.assertIn("electron: pid 951", out)

    # closing leftover Electron processes
    def fake_electron(self):
        path = os.path.join(self.tmp, "app", "node_modules", "electron", "dist", "electron")
        os.makedirs(os.path.dirname(path))
        shutil.copy(shutil.which("sleep"), path)
        return path

    def spawn_orphan(self, path):
        """Start path detached through a double fork, as a session that died leaves it."""
        r = subprocess.run(["/bin/sh", "-c", '"$0" 60 >/dev/null 2>&1 & echo $!', path],
                           capture_output=True, universal_newlines=True, check=True)
        return int(r.stdout.strip())

    @staticmethod
    def kill_quietly(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def gone(self, pid, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    return True
            try:
                with open("/proc/%d/stat" % pid) as f:
                    if f.read().split(") ", 1)[1].startswith("Z"):
                        return True
            except OSError:
                pass
            time.sleep(0.05)
        return False

    def test_ended_turn_closes_the_electron_it_started(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_KILL_GRACE="2")
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        earlier = self.spawn_orphan(electron)
        self.addCleanup(self.kill_quietly, earlier)
        p = self.start("hold", env=dict(env, UAT_LOCK_IGNORE_ELECTRON="1"))
        self.wait_ready(p)
        started = self.spawn_orphan(electron)
        self.release(p)
        rc, _, err = self.finish(p)
        self.assertEqual(rc, 0)
        self.assertTrue(self.gone(started), err)
        self.assertIn("closing Electron pid %d" % started, err)
        self.assertFalse(self.gone(earlier, 0), "an Electron from before the turn was closed")

    def test_ended_run_closes_the_electron_its_command_left(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_KILL_GRACE="2")
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        pidfile = os.path.join(self.tmp, "pid")
        r = self.run_cmd("run", "--", "/bin/sh", "-c",
                         '"$0" 60 >/dev/null 2>&1 & echo $! > "$1"; exit 4', electron, pidfile, env=env)
        self.assertEqual(r.returncode, 4)
        with open(pidfile) as f:
            pid = int(f.read())
        self.assertTrue(self.gone(pid), r.stderr)

    def test_head_closes_orphaned_electron_and_spares_owned_ones(self):
        kill_log = os.path.join(self.tmp, "kills")
        self.set_ps([(700, 1, "10:00", "/usr/local/bin/claude"),
                     (701, 700, "05:00", NM_ELECTRON + " ."),
                     (702, 1, "04:00", NM_ELECTRON + " .")])
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL,
                       env=dict(self.env, UAT_LOCK_KILL_LOG=kill_log))
        self.wait_err(p, "closing Electron pid 702")
        self.set_ps([])
        rc, _, err = self.finish(p)
        self.assertEqual(rc, 0)
        with open(kill_log) as f:
            kills = {int(line.split()[0]) for line in f}
        self.assertEqual(kills, {702})
        self.assertIn("out-of-queue Electron pid 701", err)

    def test_stop_signal_during_cleanup_still_kills_a_stuck_electron(self):
        electron = os.path.join(self.tmp, "app", "node_modules", "electron", "dist", "electron")
        os.makedirs(os.path.dirname(electron))
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1",
                   UAT_LOCK_KILL_GRACE="3", UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp)
        env.pop("UAT_LOCK_PS_FILE")
        p = self.start("hold", env=env)
        self.wait_ready(p)
        # An app that ignores SIGTERM, with argv[0] at an Electron path.
        r = subprocess.run(["bash", "-c", '(exec -a "$0" "$1" -c "import signal, time; '
                            'signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)") '
                            '>/dev/null 2>&1 & echo $!', electron, sys.executable],
                           capture_output=True, universal_newlines=True, check=True)
        stuck = int(r.stdout)
        self.addCleanup(self.kill_quietly, stuck)
        time.sleep(0.5)
        self.release(p)
        self.wait_err(p, "closing Electron pid %d" % stuck)
        p.send_signal(signal.SIGTERM)
        self.finish(p)
        self.assertTrue(self.gone(stuck), self.errs.get(p.pid, ""))

    def test_orphan_holding_run_lock_after_its_holder_died_is_closed(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp)
        env.pop("UAT_LOCK_PS_FILE")
        first = self.start("run", "--", "sh", "-c", '"$0" 60 >/dev/null 2>&1 & sleep 2', electron,
                           env=env, stdin=subprocess.DEVNULL)
        self.wait_err(first, "your turn")
        time.sleep(0.5)
        first.kill()
        first.wait()
        r = self.run_cmd("run", "--", "echo", "ADMITTED", env=env, timeout=30)
        self.assertEqual(r.stdout.strip(), "ADMITTED", r.stderr)
        self.assertIn("holding run.lock after its holder died", r.stderr)

    def test_head_ends_a_turn_held_past_the_limit(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp,
                   UAT_LOCK_MAX_TURN="0.02")
        env.pop("UAT_LOCK_PS_FILE")
        # A holder whose session hangs: it never closes stdin.
        hung = self.start("hold", env=env)
        self.wait_ready(hung)
        app = self.spawn_orphan(electron)
        self.addCleanup(self.kill_quietly, app)
        r = self.run_cmd("run", "--", "echo", "ADMITTED", env=env, timeout=30)
        self.assertEqual(r.stdout.strip(), "ADMITTED", r.stderr)
        self.assertIn("exceeded", r.stderr)
        hung.wait(timeout=10)
        self.assertTrue(self.gone(app))

    def test_ended_run_stops_what_its_command_left_holding_run_lock(self):
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1",
                   UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp, UAT_LOCK_KILL_GRACE="0.5")
        env.pop("UAT_LOCK_PS_FILE")
        pidfile = os.path.join(self.tmp, "pid")
        r = self.run_cmd("run", "--", "sh", "-c", 'sleep 60 & echo $! > "$0"', pidfile, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(pidfile) as f:
            left = int(f.read())
        self.assertTrue(self.gone(left), r.stderr)
        self.assertIn("left by the command with run.lock open", r.stderr)
        r = self.run_cmd("run", "--", "echo", "ADMITTED", env=env, timeout=15)
        self.assertEqual(r.stdout.strip(), "ADMITTED", r.stderr)

    def test_expired_turn_of_a_stuck_holder_closes_its_live_session_app(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp,
                   UAT_LOCK_MAX_TURN="0.02", UAT_LOCK_KILL_GRACE="0.3")
        env.pop("UAT_LOCK_PS_FILE")
        stuck = self.start("hold", env=env)
        self.wait_ready(stuck)
        # Launched by this test process, which stays alive like a hung session.
        app = subprocess.Popen([electron, "60"])
        self.procs.append(app)
        stuck.send_signal(signal.SIGSTOP)
        self.addCleanup(lambda: stuck.poll() is None and stuck.send_signal(signal.SIGCONT))
        r = self.run_cmd("run", "--", "echo", "ADMITTED", env=env, timeout=40)
        self.assertEqual(r.stdout.strip(), "ADMITTED", r.stderr)
        self.assertIn("still held", r.stderr)
        app.wait(timeout=10)
        stuck.wait(timeout=10)

    def test_holder_limit_rules_its_turn(self):
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1",
                   UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp)
        env.pop("UAT_LOCK_PS_FILE")
        holder = self.start("hold", env=dict(env, UAT_LOCK_MAX_TURN="100"))
        self.wait_ready(holder)
        waiter = self.start("run", "--", "true", env=dict(env, UAT_LOCK_MAX_TURN="0.01"),
                            stdin=subprocess.DEVNULL)
        self.wait_err(waiter, "waiting for the running holder")
        time.sleep(2)
        self.assertIsNone(holder.poll())
        self.assertIn("of 100m max", self.status())
        self.release(holder)
        self.assertEqual(self.finish(waiter)[0], 0)

    def test_expired_sweep_spares_another_session_electron(self):
        electron = self.fake_electron()
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp,
                   UAT_LOCK_MAX_TURN="0.02", UAT_LOCK_KILL_GRACE="0.3")
        env.pop("UAT_LOCK_PS_FILE")
        stuck = self.start("hold", env=env)
        self.wait_ready(stuck)
        orphan = self.spawn_orphan(electron)
        self.addCleanup(self.kill_quietly, orphan)
        # Another live session, a process that is not a launch wrapper, starts its own app.
        other = subprocess.Popen([sys.executable, "-c", "import subprocess, sys, time; "
                                  "p = subprocess.Popen([sys.argv[1], '60']); print(p.pid, flush=True); "
                                  "time.sleep(60)", electron], stdout=subprocess.PIPE)
        self.procs.append(other)
        theirs = int(other.stdout.readline())
        self.addCleanup(self.kill_quietly, theirs)
        stuck.send_signal(signal.SIGSTOP)
        self.addCleanup(lambda: stuck.poll() is None and stuck.send_signal(signal.SIGCONT))
        # The waiter then waits on the other session's Electron at its own gate.
        waiter = self.start("run", "--", "true", env=env, stdin=subprocess.DEVNULL)
        self.wait_err(waiter, "out-of-queue Electron pid %d" % theirs, timeout=30)
        err = self.errs.get(waiter.pid, "")
        self.assertIn("still held", err)
        self.assertTrue(self.gone(orphan), err)
        self.assertFalse(self.gone(theirs, 0), "another session's Electron was closed")

    def test_infinite_limit_means_no_limit(self):
        r = self.run_cmd("run", "--", "echo", "OK", env=dict(self.env, UAT_LOCK_MAX_TURN="inf"))
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "OK"), r.stderr)

    def test_nested_call_left_by_a_run_never_waits_on_itself(self):
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1",
                   UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp, UAT_LOCK_KILL_GRACE="0.5")
        env.pop("UAT_LOCK_PS_FILE")
        # The command starts a nested hold in the background and exits at once,
        # so the nested call cannot verify its holder and queues with the
        # inherited run.lock fd.
        fifo = os.path.join(self.tmp, "fifo")
        os.mkfifo(fifo)
        r = self.run_cmd("run", "--", "sh", "-c", '"$0" "$1" hold <> "$2" > /dev/null 2>&1 & sleep 0.2',
                         sys.executable, SCRIPT, fifo, env=env)
        self.addCleanup(subprocess.run, ["pkill", "-f", fifo])
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_cmd("run", "--", "echo", "ADMITTED", env=env, timeout=20)
        self.assertEqual(r.stdout.strip(), "ADMITTED", r.stderr)

    def test_turn_within_the_limit_is_left_alone(self):
        env = dict(self.env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1",
                   UAT_LOCK_TEST_ELECTRON_UNDER=self.tmp)
        env.pop("UAT_LOCK_PS_FILE")
        holder = self.start("hold", env=env)
        self.wait_ready(holder)
        waiter = self.start("run", "--", "true", env=env, stdin=subprocess.DEVNULL)
        self.wait_err(waiter, "waiting for the running holder")
        time.sleep(1)
        self.assertIsNone(holder.poll())
        self.release(holder)
        self.assertEqual(self.finish(waiter)[0], 0)

    def test_ended_turn_spares_electron_another_session_started(self):
        kill_log = os.path.join(self.tmp, "kills")
        p = self.start("hold", env=dict(self.env, UAT_LOCK_KILL_LOG=kill_log))
        self.wait_ready(p)
        self.set_ps([(700, 1, "10:00", "/usr/local/bin/claude"),
                     (701, 700, "00:05", NM_ELECTRON + " ."),
                     (702, 1, "00:04", NM_ELECTRON + " ."),
                     (703, 702, "00:04", NM_ELECTRON.replace("MacOS/Electron", "Frameworks/Electron Helper.app/Contents/MacOS/Electron Helper") + " --type=gpu-process")])
        self.release(p)
        rc, _, err = self.finish(p)
        self.assertEqual(rc, 0)
        with open(kill_log) as f:
            kills = [tuple(map(int, line.split())) for line in f]
        self.assertEqual(kills, [(702, signal.SIGTERM), (703, signal.SIGTERM)], err)

    # status
    def test_status_reports_runner_holder_electron_and_queue(self):
        run_lock = os.path.join(self.dir, "tickets")
        os.makedirs(run_lock)
        fd = os.open(os.path.join(self.dir, "run.lock"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            with open(os.path.join(self.dir, "run.lock.info"), "w") as f:
                f.write("ticket=4 pid=5000 owner=4990 child=0 mode=hold since=2026-11-20 10:00:00 label=t18\n")
            self.set_ps([
                (701, 1, "02:00", "/x/Runner.Worker spawnclient 1 2"),
                (4990, 4000, "09:00", "node /w/t18/harness.js"),
                (4000, 1, "1:00:00", "claude --session t18"),
                (5000, 4990, "08:00", "/usr/bin/python3 uat-lock hold --label t18"),
                (5001, 4990, "07:00", NM_ELECTRON.replace("/w/app", "/w/t18") + " ."),
                (6000, 1, "2:00:00", "codex exec"),
                (6001, 6000, "06:00", "/bin/zsh -c pnpm test:e2e"),
                (6002, 6001, "05:00", "/w/other/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron /w/other/out/main/index.js"),
            ])
            out = self.status()
        finally:
            os.close(fd)
        self.assertIn("load (1 min): 0.50, limit 8", out)
        self.assertIn("ci runner: active Runner.Worker pid 701, elapsed 02:00", out)
        self.assertIn("running: ticket=4 pid=5000", out)
        self.assertRegex(out, r"electron: pid 5001, elapsed 07:00, in-queue, worktree /w/t18, "
                              r"parent 4990 node /w/t18/harness.js, launcher 4000 claude --session t18")
        self.assertRegex(out, r"electron: pid 6002, elapsed 05:00, OUT-OF-QUEUE, worktree /w/other, "
                              r"parent 6001 /bin/zsh -c pnpm test:e2e, launcher 6000 codex exec")
        self.assertIn("queue: empty", out)

    def test_status_idle(self):
        out = self.status()
        for line in ("ci runner: idle", "running: none", "electron: none", "queue: empty"):
            self.assertIn(line, out)


    # review regressions
    def test_info_is_never_partial_during_post_spawn_update(self):
        gate = os.path.join(self.tmp, "gate")
        env = dict(self.real_env(), UAT_LOCK_TEST_INFO_GATE=gate)
        info = os.path.join(self.dir, "run.lock.info")
        p = self.start("run", "--", "sh", "-c", "sleep 1; touch %s; sleep 1" % gate,
                       env=env, stdin=subprocess.DEVNULL)
        end, seen = time.time() + 60, 0
        while time.time() < end and p.poll() is None:
            try:
                with open(info) as f:
                    text = f.read()
            except OSError:
                time.sleep(0.01)
                continue
            seen += 1
            self.assertRegex(text, r"^ticket=\d+ pid=%d .*\n$" % p.pid)
        self.assertGreater(seen, 0)
        self.assertEqual(self.finish(p)[0], 0)

    def test_nested_call_during_post_spawn_update_passes_through(self):
        # The holder publishes its post-spawn update only after the nested call
        # has run, so the nested call always reads during that update.
        gate = os.path.join(self.tmp, "gate")
        env = dict(self.real_env(), UAT_LOCK_TEST_INFO_GATE=gate)
        nested = "%s %s run -- echo nested-now && touch %s" % (sys.executable, SCRIPT, gate)
        r = self.run_cmd("run", "--", "sh", "-c", nested, env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "nested-now\n")
        self.assertIn("passing through", r.stderr)

    def test_linux_electron_is_gated_and_listed(self):
        self.set_ps([(810, 1, "03:00", "/w/app/node_modules/electron/dist/electron ."),
                     (811, 810, "02:59", "/w/app/node_modules/electron/dist/electron --type=zygote")])
        self.assertIn("electron: pid 810, elapsed 03:00, OUT-OF-QUEUE, worktree /w/app,", self.status())
        self.assertNotIn("pid 811", self.status())
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(p, "out-of-queue Electron pid 810 (worktree /w/app, running 03:00)")
        self.set_ps([])
        self.assertEqual(self.finish(p)[0], 0)

    def test_paths_with_spaces(self):
        self.set_ps([
            (820, 1, "01:00", "/Users/x/My Project/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron", "."),
            (821, 1, "01:00", "/Users/x/Linux Box/node_modules/electron/dist/electron", "--no-sandbox ."),
            (822, 1, "01:00", "node /Users/x/Other Repo/out/main/index.js"),
            (830, 1, "04:00", "/Users/x/CI Runner/bin/Runner.Worker", "spawnclient 1 2"),
        ])
        out = self.status()
        self.assertIn("ci runner: active Runner.Worker pid 830, elapsed 04:00", out)
        self.assertIn("electron: pid 820, elapsed 01:00, OUT-OF-QUEUE, worktree /Users/x/My Project,", out)
        self.assertIn("electron: pid 821, elapsed 01:00, OUT-OF-QUEUE, worktree /Users/x/Linux Box,", out)
        self.assertIn("electron: pid 822, elapsed 01:00, OUT-OF-QUEUE, worktree /Users/x/Other Repo,", out)
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(p, "Runner.Worker pid 830")
        self.wait_err(p, "out-of-queue Electron pid 820 (worktree /Users/x/My Project,")
        self.set_ps([])
        self.assertEqual(self.finish(p)[0], 0)

    def assert_cancelled(self, p):
        rc, out, err = self.finish(p)
        self.assertEqual(rc, 1, err)
        self.assertNotIn("READY", out)
        self.assertIn("stdin closed before the turn started", err)

    def test_hold_cancels_on_eof_behind_another_holder(self):
        a = self.start("hold")
        self.wait_ready(a)
        b = self.start("hold")
        self.wait_err(b, "waiting for the running holder")
        self.release(b)
        self.assert_cancelled(b)
        self.assertIn("queue: empty", self.status())
        self.release(a)
        self.finish(a)
        self.assertTrue(self.run_lock_free())

    def test_hold_cancels_on_eof_behind_closed_gate(self):
        self.set_load(9.5)
        p = self.start("hold")
        self.wait_err(p, "load 9.50 to drop below 8")
        self.assertFalse(self.run_lock_free())
        self.release(p)
        self.assert_cancelled(p)
        self.assertTrue(self.run_lock_free())
        out = self.status()
        self.assertIn("running: none", out)
        self.assertIn("queue: empty", out)

    def test_unreadable_process_list_keeps_gates_closed(self):
        os.unlink(self.ps_file)
        p = self.start("run", "--", "true", stdin=subprocess.DEVNULL)
        self.wait_err(p, "process inspection to work (cannot read UAT_LOCK_PS_FILE")
        self.set_ps([])
        self.assertEqual(self.finish(p)[0], 0)

    def test_status_reports_unavailable_inspection(self):
        os.unlink(self.ps_file)
        r = self.run_cmd("status")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ci runner: unknown (process inspection unavailable:", r.stdout)
        self.assertIn("electron: unknown (process inspection unavailable:", r.stdout)

    def test_failing_ps_command(self):
        bin_dir = os.path.join(self.tmp, "bin")
        os.mkdir(bin_dir)
        with open(os.path.join(bin_dir, "ps"), "w") as f:
            f.write("#!/bin/sh\nexit 1\n")
        os.chmod(os.path.join(bin_dir, "ps"), 0o755)
        env = dict(self.env, PATH=bin_dir + os.pathsep + os.environ.get("PATH", ""))
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        r = self.run_cmd("status", env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ci runner: unknown (process inspection unavailable: ps failed", r.stdout)
        p = self.start("run", "--", "true", env=env, stdin=subprocess.DEVNULL)
        self.wait_err(p, "process inspection to work (ps failed")
        p.kill()
        ok = dict(env, UAT_LOCK_IGNORE_RUNNER="1", UAT_LOCK_IGNORE_ELECTRON="1")
        self.assertEqual(self.run_cmd("run", "--", "true", env=ok).returncode, 0)

    def test_nested_call_without_inspection_exits(self):
        h = self.start("hold", env=self.real_env())
        self.wait_ready(h)
        env = dict(self.env, UAT_LOCK_HELD="1", UAT_LOCK_HOLDER_PID=str(h.pid),
                   UAT_LOCK_PS_FILE=os.path.join(self.tmp, "missing"))
        r = self.run_cmd("run", "--", "echo", "never", env=env)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("cannot be verified", r.stderr)
        self.release(h)
        self.finish(h)

    def test_paths_with_space_hyphen(self):
        self.set_ps([
            (840, 1, "01:00", "/w/My - Project/node_modules/electron/dist/electron", "."),
            (841, 1, "01:00", "/w/Mac - Project/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron", "--inspect ."),
            (850, 1, "02:00", "/w/CI - Runner/bin/Runner.Worker", "spawnclient 1 2"),
        ])
        out = self.status()
        self.assertIn("ci runner: active Runner.Worker pid 850, elapsed 02:00", out)
        self.assertIn("electron: pid 840, elapsed 01:00, OUT-OF-QUEUE, worktree /w/My - Project,", out)
        self.assertIn("electron: pid 841, elapsed 01:00, OUT-OF-QUEUE, worktree /w/Mac - Project,", out)
        p = self.start("run", "--", "echo", "ADMITTED", stdin=subprocess.DEVNULL)
        self.wait_err(p, "Runner.Worker pid 850")
        self.wait_err(p, "out-of-queue Electron pid 840 (worktree /w/My - Project,")
        self.wait_err(p, "out-of-queue Electron pid 841 (worktree /w/Mac - Project,")
        self.set_ps([])
        rc, out, _ = self.finish(p)
        self.assertEqual((rc, out), (0, "ADMITTED\n"))

    def test_known_paths_as_launcher_arguments_are_not_misread(self):
        self.set_ps([
            (860, 1, "01:00", "/bin/sh -c /w/CI - Runner/bin/Runner.Worker spawnclient"),
            (861, 1, "01:00", "/usr/bin/env /w/My - Project/node_modules/electron/dist/electron ."),
        ])
        out = self.status()
        self.assertIn("ci runner: idle", out)
        self.assertIn("electron: none", out)

    def test_queued_hold_cancels_when_eof_lands_while_blocked_on_queue(self):
        a = self.start("hold")
        self.wait_ready(a)
        b = self.start("hold")
        self.wait_err(b, "waiting for the running holder")
        guard = os.open(os.path.join(self.dir, "queue.lock"), os.O_RDWR)
        try:
            fcntl.flock(guard, fcntl.LOCK_EX)
            time.sleep(1)  # b finishes its poll and blocks on queue.lock
            self.release(b)
            self.release(a)
            self.assertEqual(self.finish(a)[0], 0)
        finally:
            fcntl.flock(guard, fcntl.LOCK_UN)
            os.close(guard)
        self.assert_cancelled(b)
        self.assertTrue(self.run_lock_free())

    def test_spaced_paths_whose_first_word_is_a_launcher_name(self):
        self.set_ps([
            (870, 1, "01:00", "/w/node Project/node_modules/electron/dist/electron", "."),
            (871, 1, "02:00", "/w/ci/npm Runner/bin/Runner.Worker", "spawnclient 1 2"),
        ])
        out = self.status()
        self.assertIn("ci runner: active Runner.Worker pid 871, elapsed 02:00", out)
        self.assertIn("electron: pid 870, elapsed 01:00, OUT-OF-QUEUE, worktree /w/node Project,", out)
        p = self.start("run", "--", "echo", "ADMITTED", stdin=subprocess.DEVNULL)
        self.wait_err(p, "Runner.Worker pid 871")
        self.wait_err(p, "out-of-queue Electron pid 870 (worktree /w/node Project,")
        self.set_ps([])
        rc, out, _ = self.finish(p)
        self.assertEqual((rc, out), (0, "ADMITTED\n"))

    def test_known_paths_in_option_values_are_not_executables(self):
        self.set_ps([
            (880, 1, "01:00", "/usr/bin/grep --exclude=/w/app/node_modules/electron/dist/electron needle file"),
            (881, 1, "01:00", "/usr/bin/grep --exclude=/w/app/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron needle file"),
            (882, 1, "01:00", "/usr/bin/grep --exclude=/w/ci/bin/Runner.Worker needle file"),
        ])
        out = self.status()
        self.assertIn("ci runner: idle", out)
        self.assertIn("electron: none", out)
        r = self.run_cmd("run", "--", "echo", "ADMITTED")
        self.assertEqual((r.returncode, r.stdout), (0, "ADMITTED\n"), r.stderr)

    def test_real_processes_are_classified_by_argv0(self):
        # Copies of sleep stand in for Electron and Runner.Worker under spaced
        # paths; a shell carries the same paths only as arguments.
        electron = os.path.join(self.tmp, "node Project", "node_modules", "electron", "dist", "electron")
        runner = os.path.join(self.tmp, "ci", "npm Runner", "bin", "Runner.Worker")
        for path in (electron, runner):
            os.makedirs(os.path.dirname(path))
            shutil.copy(shutil.which("sleep"), path)
        procs = [subprocess.Popen([electron, "30"]), subprocess.Popen([runner, "30"]),
                 subprocess.Popen(["/bin/sh", "-c", "sleep 30", "--exclude=" + electron, runner])]
        self.procs.extend(procs)
        env = dict(self.env)
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        deadline = time.time() + 20
        while True:
            out = self.run_cmd("status", env=env).stdout
            if "pid %d," % procs[0].pid in out or time.time() > deadline:
                break
        self.assertIn("ci runner: active Runner.Worker pid %d," % procs[1].pid, out)
        self.assertIn("electron: pid %d, " % procs[0].pid, out)
        self.assertIn("worktree %s," % os.path.dirname(electron).split("/node_modules/")[0]
                      .replace(os.path.expanduser("~"), "~"), out)
        self.assertNotIn("pid %d," % procs[2].pid, out)

    @unittest.skipUnless(sys.platform == "darwin", "the second lookup is ps comm on macOS")
    def test_failing_executable_lookup_keeps_gates_closed(self):
        # The process listing works; only the separate argv[0] lookup fails.
        bin_dir = os.path.join(self.tmp, "bin")
        os.mkdir(bin_dir)
        with open(os.path.join(bin_dir, "ps"), "w") as f:
            f.write('#!/bin/sh\ncase "$*" in *comm=*) exit 1;; esac\nexec /bin/ps "$@"\n')
        os.chmod(os.path.join(bin_dir, "ps"), 0o755)
        electron = os.path.join(self.tmp, "node Project", "node_modules", "electron", "dist", "electron")
        runner = os.path.join(self.tmp, "ci", "npm Runner", "bin", "Runner.Worker")
        for path in (electron, runner):
            os.makedirs(os.path.dirname(path))
            shutil.copy(shutil.which("sleep"), path)
        self.procs.extend([subprocess.Popen([electron, "30"]), subprocess.Popen([runner, "30"])])
        env = dict(self.env, PATH=bin_dir + os.pathsep + os.environ.get("PATH", ""))
        env.pop("UAT_LOCK_PS_FILE")
        env["UAT_LOCK_TEST_ELECTRON_UNDER"] = self.tmp
        r = self.run_cmd("status", env=env)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ci runner: unknown (process inspection unavailable: executable lookup", r.stdout)
        self.assertIn("electron: unknown (process inspection unavailable: executable lookup", r.stdout)
        p = self.start("run", "--", "echo", "ADMITTED", env=env, stdin=subprocess.DEVNULL)
        self.wait_err(p, "process inspection to work (executable lookup (ps comm) failed")
        p.kill()

    def test_nested_call_passes_through_after_wrapper_sigkill(self):
        # The command outlives its killed wrapper and keeps run.lock; a nested
        # call from it must pass through instead of queueing behind itself.
        go, done, out = (os.path.join(self.tmp, n) for n in ("go", "done", "out"))
        script = ("while [ ! -f %s ]; do sleep 0.05; done; "
                  "%s %s run -- echo NESTED > %s 2>&1; touch %s; sleep 30") % (
                      go, sys.executable, SCRIPT, out, done)
        wrapper = subprocess.Popen([sys.executable, SCRIPT, "run", "--", "sh", "-c", script],
                                   env=self.real_env(), stdin=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)

        def kill_group():
            try:
                os.killpg(wrapper.pid, signal.SIGKILL)
            except OSError:
                pass
            wrapper.wait()
        self.addCleanup(kill_group)
        info = os.path.join(self.dir, "run.lock.info")
        deadline = time.time() + 30
        while " child=0 " in (open(info).read() if os.path.exists(info) else " child=0 "):
            self.assertLess(time.time(), deadline, "the wrapper never started its command")
            time.sleep(0.05)
        wrapper.kill()
        wrapper.wait()
        self.assertFalse(self.run_lock_free(), "the command should still hold run.lock")
        open(go, "w").close()
        deadline = time.time() + 30
        while not os.path.exists(done):
            self.assertLess(time.time(), deadline, "nested call queued behind its own lock")
            time.sleep(0.05)
        with open(out) as f:
            text = f.read()
        self.assertIn("NESTED", text)
        self.assertIn("passing through", text)

    def test_nested_call_passes_through_after_sigkill_in_publication_window(self):
        # The wrapper is held before it publishes child= itself and is killed
        # there; the child published its own pid before exec, so the nested
        # call still recognises its inherited turn.
        gate, started, go, done, out = (os.path.join(self.tmp, n)
                                        for n in ("gate", "started", "go", "done", "out"))
        script = ("echo $$ > %s; while [ ! -f %s ]; do sleep 0.05; done; "
                  "%s %s run -- echo NESTED > %s 2>&1; touch %s; sleep 30") % (
                      started, go, sys.executable, SCRIPT, out, done)
        env = dict(self.real_env(), UAT_LOCK_TEST_INFO_GATE=gate)
        wrapper = subprocess.Popen([sys.executable, SCRIPT, "run", "--", "sh", "-c", script],
                                   env=env, stdin=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)

        def kill_group():
            try:
                os.killpg(wrapper.pid, signal.SIGKILL)
            except OSError:
                pass
            wrapper.wait()
        self.addCleanup(kill_group)
        deadline = time.time() + 30
        while not (os.path.exists(started) and open(started).read().strip()):
            self.assertLess(time.time(), deadline, "the command never started")
            time.sleep(0.05)
        child = int(open(started).read())
        with open(os.path.join(self.dir, "run.lock.info")) as f:
            published = f.read()
        wrapper.kill()
        wrapper.wait()
        self.assertFalse(self.run_lock_free(), "the command should still hold run.lock")
        open(go, "w").close()
        deadline = time.time() + 30
        while not os.path.exists(done):
            self.assertLess(time.time(), deadline, "nested call queued behind its own lock")
            time.sleep(0.05)
        with open(out) as f:
            text = f.read()
        self.assertIn("NESTED", text)
        self.assertIn("passing through", text)
        self.assertIn("pid=%d owner=0 child=%d " % (wrapper.pid, child), published)

    def test_sigterm_between_spawn_and_registration_is_forwarded(self):
        # SIGTERM lands after the command started but before the wrapper
        # registered it: the wrapper must defer it, forward it to the command,
        # and keep run.lock.info until the command exits.
        spawn_gate, started, term, go, done, out = (
            os.path.join(self.tmp, n) for n in ("spawn-gate", "started", "term", "go", "done", "out"))
        script = ("trap 'echo got >> %s' TERM; echo $$ > %s; "
                  "while [ ! -f %s ]; do sleep 0.05; done; "
                  "%s %s run -- echo NESTED > %s 2>&1; touch %s") % (
                      term, started, go, sys.executable, SCRIPT, out, done)
        env = dict(self.real_env(), UAT_LOCK_TEST_SPAWN_GATE=spawn_gate)
        wrapper = subprocess.Popen([sys.executable, SCRIPT, "run", "--", "sh", "-c", script],
                                   env=env, stdin=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)

        def kill_group():
            try:
                os.killpg(wrapper.pid, signal.SIGKILL)
            except OSError:
                pass
            wrapper.wait()
        self.addCleanup(kill_group)
        info = os.path.join(self.dir, "run.lock.info")

        def wait_for(path, what, content=True):
            deadline = time.time() + 30
            while not os.path.exists(path) or (content and not read(path).strip()):
                self.assertLess(time.time(), deadline, what)
                time.sleep(0.05)

        def read(path):
            with open(path) as f:
                return f.read()

        wait_for(started, "the command never started")
        wrapper.send_signal(signal.SIGTERM)
        time.sleep(0.5)
        self.assertIsNone(wrapper.poll(), "SIGTERM during spawn killed the wrapper")
        self.assertTrue(os.path.exists(info))
        open(spawn_gate, "w").close()
        wait_for(term, "SIGTERM was not forwarded to the command")
        self.assertIsNone(wrapper.poll(), "the wrapper must wait for its command")
        self.assertTrue(os.path.exists(info), "metadata removed while the command runs")
        self.assertFalse(self.run_lock_free())
        open(go, "w").close()
        wait_for(done, "nested call queued behind its own lock", content=False)
        self.assertEqual(wrapper.wait(timeout=30), 0)
        text = read(out)
        self.assertIn("NESTED", text)
        self.assertIn("passing through", text)
        self.assertFalse(os.path.exists(info))
        self.assertTrue(self.run_lock_free())

    def test_runner_whose_job_waits_in_queue_does_not_block_the_head(self):
        # Local ticket 0 waits on the runner gate; the worker's own job then
        # queues as ticket 1. The worker never leaves the process list, so
        # without the exemption both tickets wait for each other forever.
        worker = (701, 1, "05:00", "/x/bin/Runner.Worker spawnclient 1 2")
        self.set_ps([worker])
        local = self.start("hold", "--label", "local")
        self.wait_err(local, "CI job to finish (Runner.Worker pid 701")
        ci_env = dict(self.env, GITHUB_ACTIONS="true")
        ci = self.start("run", "--", "echo", "CI", env=ci_env, stdin=subprocess.DEVNULL)
        self.wait_err(ci, "position 2 in queue")
        self.set_ps([worker, (ci.pid, 701, "00:05", "%s %s run -- echo CI" % (sys.executable, SCRIPT))])
        self.wait_ready(local)
        self.wait_err(ci, "waiting for the running holder")
        self.assertIn("ci runner: active Runner.Worker pid 701, elapsed 05:00, "
                      "its job waits in this queue (ticket 1)", self.status())
        self.release(local)
        self.assertEqual(self.finish(local)[0], 0)
        rc, out, _ = self.finish(ci)
        self.assertEqual((rc, out), (0, "CI\n"))

def load_script(lock_dir):
    """Import uat-lock as a module whose state lives in lock_dir."""
    loader = importlib.machinery.SourceFileLoader("uat_lock_under_test", SCRIPT)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(os.environ, {"UAT_LOCK_DIR": lock_dir}):
        loader.exec_module(module)
    return module


class LinuxExecutableLookupTest(unittest.TestCase):
    """ps works and this process's /proc entry is readable; others may fail."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="uat-lock-test-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.mod = load_script(os.path.join(self.tmp, "state"))
        me = os.getpid()
        self.listing = "".join("%d 1 %s %s\n" % row for row in [
            (me, "00:10", "python3 test"),
            (900, "01:00", "/w/node Project/node_modules/electron/dist/electron ."),
            (901, "02:00", "/w/ci/npm Runner/bin/Runner.Worker spawnclient 1 2"),
            (902, "00:01", "/bin/sleep 1"),
        ])
        self.cmdlines = {
            me: b"python3\0test\0",
            900: b"/w/node Project/node_modules/electron/dist/electron\0.\0",
            901: b"/w/ci/npm Runner/bin/Runner.Worker\0spawnclient\0001\0002\0",
        }

    @contextlib.contextmanager
    def linux(self, errors):
        real_open = open

        def fake_open(path, mode="r", *args, **kwargs):
            m = re.match(r"/proc/(\d+)/cmdline$", str(path))
            if not m:
                return real_open(path, mode, *args, **kwargs)
            pid = int(m.group(1))
            code = errors.get(pid, 0 if pid in self.cmdlines else errno.ENOENT)
            if code:
                raise OSError(code, os.strerror(code), path)
            return io.BytesIO(self.cmdlines[pid])

        env = {k: v for k, v in os.environ.items() if not k.startswith("UAT_LOCK_")}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(self.mod.sys, "platform", "linux"), \
                mock.patch.object(self.mod.subprocess, "check_output", return_value=self.listing), \
                mock.patch.object(self.mod, "open", fake_open, create=True):
            yield

    def test_permission_errors_fail_closed(self):
        for errors in ({900: errno.EACCES, 901: errno.EACCES}, {900: errno.EIO}, {901: errno.EPERM}):
            with self.subTest(errors=errors), self.linux(errors):
                with self.assertRaises(self.mod.InspectError):
                    self.mod.process_table()
                _, reasons = self.mod.gate_reasons(False, False)
                self.assertIn("inspect", [key for key, _ in reasons])
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = self.mod.cmd_status()
                self.assertEqual(rc, 1)
                self.assertIn("ci runner: unknown (process inspection unavailable: executable lookup",
                              out.getvalue())
                self.assertIn("electron: unknown (process inspection unavailable: executable lookup",
                              out.getvalue())

    def test_exited_processes_are_tolerated(self):
        # 902 has no /proc entry (ENOENT): it exited between the two reads.
        with self.linux({}):
            table = self.mod.process_table()
            _, reasons = self.mod.gate_reasons(False, False)
        self.assertEqual(table[900].kind, "electron")
        self.assertEqual(table[901].kind, "runner")
        self.assertEqual(table[902].exe, "/bin/sleep")
        keys = [key for key, _ in reasons]
        self.assertIn("runner 901", keys)
        self.assertIn("electron 900", keys)

if __name__ == "__main__":
    unittest.main()
