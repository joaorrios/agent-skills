"""Scenario tests for pr-wait against a fake gh. Run: python3 -I pr-wait.test.py"""
import contextlib, importlib.machinery, importlib.util, io, json, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "pr-wait"
loader = importlib.machinery.SourceFileLoader("pr_wait", str(SCRIPT))
spec = importlib.util.spec_from_loader("pr_wait", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

HEAD = "a" * 40
OLD = "b" * 40

def pr_json(**kw):
    pr = {
        "url": "https://github.com/o/r/pull/1", "state": "OPEN", "headRefOid": HEAD, "baseRefName": "main",
        "mergeStateStatus": "CLEAN", "author": {"login": "author"}, "baseRef": {"target": {"oid": "c" * 40}},
        "comments": {"nodes": []}, "reviews": {"nodes": []},
        "reviewThreads": {"totalCount": 0, "nodes": []},
    }
    pr.update(kw)
    return pr

def codex_summary(sha, status):
    body = ('<!-- codex-review-state:v1 {"code_review":{"commit_sha":"%s","status":"%s"},"security_review":{}} -->'
            ' `%s`' % (sha, status, sha[:7]))
    return {"id": "s1", "url": "u-summary", "body": body, "author": {"login": "chatgpt-codex-connector", "__typename": "Bot"}}

class Fake:
    def __init__(self, pr, checks=(), workflows=True, heads=None, thread_pages=None):
        self.pr, self.checks, self.workflows = pr, list(checks), workflows
        self.heads = heads  # sequence of heads returned by `pr view headRefOid`
        self.thread_pages = thread_pages or []
    def __call__(self, args, allow=(0,)):
        out = ""
        if args[:2] == ["api", "graphql"]:
            q = next(a for a in args if a.startswith("query="))
            if "pageInfo" in q:
                after = next((a.split("=", 1)[1] for a in args if a.startswith("after=")), None)
                idx = 0 if after is None else int(after)
                out = json.dumps({"data": {"repository": {"pullRequest": {"reviewThreads": self.thread_pages[idx]}}}})
            else:
                out = json.dumps({"data": {"viewer": {"login": "me"}, "repository": {"pullRequest": self.pr}}})
        elif args[:2] == ["pr", "checks"]:
            if not self.checks:
                return subprocess.CompletedProcess(args, 1, "", "no checks reported on the 'x' branch")
            out = json.dumps(self.checks)
        elif args[:2] == ["pr", "view"]:
            out = (self.heads.pop(0) if self.heads else self.pr["headRefOid"]) + "\n"
        elif args[0] == "api" and "workflows" in args[1]:
            if not self.workflows:
                raise m.GhError("gh: Not Found (HTTP 404)", False)
            out = "1"
        elif args[0] == "api" and ("rules/branches" in args[1] or "protection" in args[1]):
            raise m.GhError("gh: Not Found (HTTP 404)", False)
        elif args[0] == "api" and "compare" in args[1]:
            out = "0"
        return subprocess.CompletedProcess(args, 0, out, "")

def run(fake, until="ready", bots=(), polls=3, between=None):
    m.gh = fake
    m.STATE_DIR = Path(tempfile.mkdtemp())
    w = m.Watcher("o/r", 1, until, 5, list(bots))
    w.baseline = False
    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        for i in range(polls):
            try:
                w.poll()
            except SystemExit as e:
                code = e.code
                break
            if between:
                between(w, i)
    return code, buf.getvalue()

CI = [{"name": "ci", "bucket": "pass", "link": "l", "description": ""}]
results = []
def check(name, cond, detail):
    results.append(cond)
    print(("PASS" if cond else "FAIL"), name, "|", detail.strip().replace("\n", " / "))

# 1. human CHANGES_REQUESTED blocks ready
pr = pr_json(reviews={"nodes": [{"id": "r1", "url": "u-r1", "state": "CHANGES_REQUESTED", "body": "fix", "commit": {"oid": HEAD}, "author": {"login": "human", "__typename": "User"}}]})
code, out = run(Fake(pr, CI))
check("changes requested -> exit 1", code == 1 and "changes requested by human" in out, out)
# 1b. later approval by same human clears it
pr = pr_json(reviews={"nodes": [
    {"id": "r1", "url": "u-r1", "state": "CHANGES_REQUESTED", "body": "fix", "commit": {"oid": OLD}, "author": {"login": "human", "__typename": "User"}},
    {"id": "r2", "url": "u-r2", "state": "APPROVED", "body": "", "commit": {"oid": HEAD}, "author": {"login": "human", "__typename": "User"}}]})
code, out = run(Fake(pr, CI))
check("approval after changes requested -> ready", code == 0 and "ready on" in out, out)

# 2. earlier Codex review on head + running summary -> keeps waiting
pr = pr_json(comments={"nodes": [codex_summary(HEAD, "in_progress")]},
             reviews={"nodes": [{"id": "r3", "url": "u-r3", "state": "COMMENTED", "body": "x", "commit": {"oid": HEAD}, "author": {"login": "chatgpt-codex-connector", "__typename": "Bot"}}]})
code, out = run(Fake(pr, CI), bots=["chatgpt-codex-connector"])
check("codex running despite earlier review on head -> waits", code is None, out or "(no exit)")
# 2b. completed summary -> ready
pr = pr_json(comments={"nodes": [codex_summary(HEAD, "completed")]})
code, out = run(Fake(pr, CI), bots=["chatgpt-codex-connector"])
check("codex completed -> ready", code == 0 and "ready on" in out, out)

# 3. Codex failed -> exit 1 with request line
pr = pr_json(comments={"nodes": [codex_summary(HEAD, "failed")]})
code, out = run(Fake(pr, CI), bots=["chatgpt-codex-connector"])
check("codex failed -> exit 1", code == 1 and "review failed" in out, out)

# 4. no CI, no workflows -> green and ready
code, out = run(Fake(pr_json(), [], workflows=False), until="green")
check("no CI, no workflows -> green", code == 0 and "green on" in out, out)
code, out = run(Fake(pr_json(), [], workflows=False))
check("no CI, no workflows -> ready", code == 0 and "ready on" in out, out)
# 4b. workflows exist but no checks yet -> waits within grace, green after
code, out = run(Fake(pr_json(), [], workflows=True), until="green")
check("workflows, no checks, within grace -> waits", code is None, out or "(no exit)")
def age(w, i):
    for k in w.head_seen: w.head_seen[k] -= m.NO_CHECKS_GRACE + 1
code, out = run(Fake(pr_json(), [], workflows=True), until="green", between=age)
check("workflows, no checks, past grace -> green", code == 0 and "green on" in out, out)
# 4c. only an advisory bot check, no CI, no workflows -> green
code, out = run(Fake(pr_json(), [{"name": "CodeRabbit", "bucket": "pass", "link": "l", "description": "Review completed"}], workflows=False), until="green")
check("only coderabbit check, no workflows -> green", code == 0, out)

# 6. head moved before exit -> no ready on stale head
code, out = run(Fake(pr_json(), CI, heads=["d" * 40, "d" * 40, "d" * 40]))
check("head moved -> no exit", code is None, out or "(no exit)")
# 6b. new head is not stable on first poll
fake = Fake(pr_json(), CI)
m.gh = fake; m.STATE_DIR = Path(tempfile.mkdtemp())
w = m.Watcher("o/r", 1, "green", 5, []); w.baseline = False
w.poll()  # first poll on HEAD
fake.pr = pr_json(headRefOid="e" * 40)
buf = io.StringIO(); code = None
with contextlib.redirect_stdout(buf):
    try: w.poll()
    except SystemExit as e: code = e.code
check("new head not stable on first poll", code is None, buf.getvalue() or "(no exit)")

# 7. >100 threads -> unresolved found on another page
first_page = {"pageInfo": {"hasNextPage": True, "endCursor": "1"}, "nodes": [{"isResolved": True, "comments": {"nodes": [{"url": "t"}]}}] * 100}
second_page = {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"isResolved": False, "comments": {"nodes": [{"url": "u-old-thread"}]}}]}
threads_last = [{"isResolved": True, "path": "f", "line": 1, "comments": {"nodes": [{"id": f"c{i}", "url": "t", "body": "x", "author": {"login": "me", "__typename": "User"}}]}} for i in range(100)]
pr = pr_json(reviewThreads={"totalCount": 101, "nodes": threads_last})
code, out = run(Fake(pr, CI, thread_pages=[first_page, second_page]))
check("101 threads, old one unresolved -> exit 1", code == 1 and "u-old-thread" in out, out)

print(f"{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
