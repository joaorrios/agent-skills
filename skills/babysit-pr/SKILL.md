---
name: babysit-pr
description: Monitors a pull request through CI and review bots, fixing real findings until it is ready to merge. Use when the user asks to monitor, watch, or babysit a PR.
license: MIT
compatibility: GitHub with the gh CLI authenticated; Python 3.9+ on a POSIX system for scripts/pr-wait. A monitor tool that streams a command's output, such as Claude Code's Monitor, gives the best wake-ups.
---

# Babysit PR

Review bots are helpful, even when they are not right.

## Waiting

Wait with `scripts/pr-wait` from this skill's folder (use its absolute path). Keep exactly one watcher per PR, and leave your own polling or `sleep` loops out: every watcher on a GitHub account shares one rate limit.

```bash
pr-wait <pr> [--repo owner/name] [--until ready|green|any-change] [--bot <login>]...
```

It prints one line per real event: a failed required check, all checks finished, a new comment, review, or thread, a review bot finishing on the head, base commits that touch this PR's files, a BEHIND or DIRTY branch, a merge or close. It exits 0 when the `--until` condition holds or the PR merges, 1 when it needs you (failed required check, conflicts, unresolved threads, BEHIND for `ready`, PR closed), and 2 on bad input or when another `pr-wait` already watches the PR.

- `ready` (default): required checks green, every review bot finished on the head, no unresolved threads, branch not BEHIND. Use this to babysit.
- `green`: required checks only.
- `any-change`: exit on the first event.

Pass `--bot` for each review bot the repo uses (check the bots on recent PRs), so `ready` waits for a bot that has not posted yet. Without `--bot`, `ready` counts only the bots already on the PR. CodeRabbit is advisory: reported, never waited for.

Some bots review only on demand. Codex (`chatgpt-codex-connector`) reviews when a PR opens or becomes ready, and again when someone comments `@codex review`. After pushing a fix, request a re-review from such a bot, or `ready` waits for a review that never comes.

Run `pr-wait` through the harness's monitor (in Claude Code, the Monitor tool with `timeout_ms: 3600000`), so each line wakes you. Without a monitor, run it as one long background command that notifies you when it exits.

Start it again after you push, after you handle an exit 1, and after a resume. It remembers what it already reported, so nothing that arrived in between is lost. When it says another pid already watches the PR, keep that one; kill it only when its events do not reach you.

Only the agent that owns the PR watches it. A delegated subagent or reviewer leaves the watching to its parent.

When an event needs no action, end your turn without a message. Stay quiet rather than posting "still waiting" or filler comments.

## GitHub rate limits

`gh pr create`, `gh pr view`, and `gh pr checks` use GraphQL. When GraphQL is used up (`gh api rate_limit --jq .resources.graphql`), the REST limit is separate and usually has room: read a PR with `gh api repos/<owner>/<repo>/pulls/<n>` and checks with `gh api repos/<owner>/<repo>/commits/<sha>/check-runs`. Wait for the reset with one background command before watching again.

## Reviews

Act only on checks and comments newer than the latest push. Verify every bot finding against the source before changing code. Fix real findings and CI failures, and tell repository failures apart from infrastructure flakes. When the repo documents rules for a review bot, read them before replying to its findings.

Reply to each finding you dismiss with a short, specific reason and resolve the thread. Replies go out under the user's name, so keep them factual: what changed, or why the finding does not apply. When a comment-attribution skill such as `leaving-pr-comments` is available, post every comment through it.

Keep the PR at the size the user's goal needs. Review loops grow a PR one cheap-looking fix at a time. Fix real bugs in the intended case; decline the rest with a written reason and list them as follow-ups: unneeded tests, guards for edge cases that do not matter, extra integration or compatibility, small performance costs. Prefer the fix that deletes or narrows code.

Screenshots and videos help reviewers too, when you have a way to upload them.

## Base branch and merging

Keep the branch current with the base, the way the repo does it (merging the base in, or rebasing). `pr-wait` reports when new base commits touch this PR's files and when the PR becomes BEHIND or DIRTY. When an overlapping PR makes this one obsolete, stop watching, report it, and ask before closing the PR unless closing was explicitly authorized.

Stop when `pr-wait --until ready` exits 0. Merge only when the user explicitly asked for it; otherwise report that the PR is ready. Right before a merge, run `git fetch` and check the PR again: a BEHIND or DIRTY branch, or base commits that landed after the last green run and touch this PR's files, mean update, push, and wait for green again. Merge with the method the repo uses.
