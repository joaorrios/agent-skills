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
        "comments": {"totalCount": 0, "nodes": []}, "reviews": {"totalCount": 0, "nodes": []},
        "reviewThreads": {"totalCount": 0, "nodes": []},
    }
    for field in ("comments", "reviews"):
        if field in kw and "totalCount" not in kw[field]:
            kw[field]["totalCount"] = len(kw[field]["nodes"])
    pr.update(kw)
    return pr

def codex_summary(sha, status, security_sha=None, security_status=None):
    state = {"code_review": {"commit_sha": sha, "status": status},
             "security_review": {"commit_sha": security_sha, "status": security_status}}
    body = "<!-- codex-review-state:v1 %s --> `%s`" % (json.dumps(state), (sha or HEAD)[:7])
    return {"id": "s1", "url": "u-summary", "body": body, "author": {"login": "chatgpt-codex-connector", "__typename": "Bot"}}

class Fake:
    def __init__(self, pr, checks=(), heads=None, thread_pages=None, pages=None):
        self.pr, self.checks = pr, list(checks)
        self.heads = heads  # sequence of heads returned by `pr view headRefOid`
        self.thread_pages = thread_pages or []
        self.pages = pages or {}  # connection field -> list of full pages
    def __call__(self, args, allow=(0,)):
        out = ""
        if args[:2] == ["api", "graphql"]:
            q = next(a for a in args if a.startswith("query="))
            if "pageInfo" in q:
                after = next((a.split("=", 1)[1] for a in args if a.startswith("after=")), None)
                idx = 0 if after is None else int(after)
                field = next(f for f in ("reviewThreads", "comments", "reviews") if f + "(first" in q)
                pages = self.thread_pages if field == "reviewThreads" else self.pages[field]
                out = json.dumps({"data": {"repository": {"pullRequest": {field: pages[idx]}}}})
            else:
                out = json.dumps({"data": {"viewer": {"login": "me"}, "repository": {"pullRequest": self.pr}}})
        elif args[:2] == ["pr", "checks"]:
            if not self.checks:
                return subprocess.CompletedProcess(args, 1, "", "no checks reported on the 'x' branch")
            out = json.dumps(self.checks)
        elif args[:2] == ["pr", "view"]:
            out = (self.heads.pop(0) if self.heads else self.pr["headRefOid"]) + "\n"
        elif args[0] == "api" and ("rules/branches" in args[1] or "protection" in args[1]):
            raise m.GhError("gh: Not Found (HTTP 404)", False)
        elif args[0] == "api" and "compare" in args[1]:
            out = "0"
        return subprocess.CompletedProcess(args, 0, out, "")

def age(w, i):
    for k in w.head_seen: w.head_seen[k] -= m.NO_CHECKS_GRACE + 1

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
    print(("PASS" if cond else "FAIL"), name, "|", detail.strip().splitlines()[-1] if detail.strip() else "")

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

# 4. no CI checks: wait within the grace period, then green and ready
code, out = run(Fake(pr_json(), []), until="green")
check("no CI checks, within grace -> waits", code is None, out or "(no exit)")
code, out = run(Fake(pr_json(), []), until="green", between=age)
check("no CI checks, past grace -> green", code == 0 and "green on" in out, out)
code, out = run(Fake(pr_json(), []), between=age)
check("no CI checks, past grace -> ready", code == 0 and "ready on" in out, out)
# 4b. only an advisory bot check -> still no CI, green after grace
code, out = run(Fake(pr_json(), [{"name": "CodeRabbit", "bucket": "pass", "link": "l", "description": "Review completed"}]), until="green", between=age)
check("only coderabbit check, past grace -> green", code == 0 and "green on" in out, out)

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

# 8. changes requested outside the last 100 reviews still blocks ready
def review(i, state, login="bot-ish", typename="User"):
    return {"id": f"r{i}", "url": f"u-r{i}", "state": state, "body": "x", "commit": {"oid": HEAD}, "author": {"login": login, "__typename": typename}}
old_cr = review(0, "CHANGES_REQUESTED", "human")
later = [review(i, "COMMENTED", "other") for i in range(1, 101)]
pr = pr_json(reviews={"totalCount": 101, "nodes": later})
pages = {"reviews": [{"pageInfo": {"hasNextPage": True, "endCursor": "1"}, "nodes": [old_cr] + later[:99]},
                     {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": later[99:]}]}
code, out = run(Fake(pr, CI, pages=pages))
check("changes requested beyond last 100 reviews -> exit 1", code == 1 and "changes requested by human" in out, out)

# 9. running Codex summary outside the last 100 comments keeps waiting
summary = codex_summary(HEAD, "in_progress")
chatter = [{"id": f"c{i}", "url": "u", "body": "hi", "author": {"login": "other", "__typename": "User"}} for i in range(100)]
codex_old_review = review(200, "COMMENTED", "chatgpt-codex-connector", "Bot")
pr = pr_json(comments={"totalCount": 101, "nodes": chatter}, reviews={"nodes": [codex_old_review]})
pages = {"comments": [{"pageInfo": {"hasNextPage": True, "endCursor": "1"}, "nodes": [summary] + chatter[:99]},
                      {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": chatter[99:]}]}
code, out = run(Fake(pr, CI, pages=pages), bots=["chatgpt-codex-connector"])
check("codex running beyond last 100 comments -> waits", code is None, out or "(no exit)")

# 10. Codex security review states
for status, want in (("in_progress", None), ("failed", 1), ("completed", 0)):
    pr = pr_json(comments={"nodes": [codex_summary(HEAD, "completed", HEAD, status)]})
    code, out = run(Fake(pr, CI), bots=["chatgpt-codex-connector"])
    check(f"code completed + security {status} -> {want}", code == want, out or "(no exit)")
pr = pr_json(comments={"nodes": [codex_summary(None, None, HEAD, "completed")]})
code, out = run(Fake(pr, CI), bots=["chatgpt-codex-connector"])
check("security-only completed -> ready", code == 0 and "ready on" in out, out)

print(f"{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
