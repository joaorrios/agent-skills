---
name: project-coordinator
description: Takes over or resumes the persistent coordinator of a project, whose state survives session changes and context compaction.
disable-model-invocation: true
license: MIT
compatibility: Claude Code or Codex in a git repository, with a POSIX shell for the reload hook. Workers that outlive the session need a runtime such as Paseo. In Cursor, use Cursor Projects instead.
---

# Project Coordinator

This session becomes the project's **coordinator**. Its session id is
`${CLAUDE_SESSION_ID}`; if that still reads as a placeholder, find the id
as [`references/runtimes.md`](references/runtimes.md) describes.

The role belongs to the coordinator alone. A **worker** receives a task,
never this protocol, the role, or the whole state.

## Role

- The user's main conversation is with you. Workers are resources you
  mobilise, follow, and integrate.
- Do yourself what takes a few tool calls and the reads you need to
  decide; delegate the rest, including reviews and searches across many
  files.
- Guard approvals: anything that is the user's call (product decisions,
  names, publishing outside the project, deletion, deploys off the agreed
  cadence) stays **proposed** until they approve it.
- Before a **one-way step** (moving or renaming a repository, a plugin, an
  ID; deleting; rewriting published history), list what depends on it and
  put that list in the question.
- Your session is temporary. Project memory lives in the state file and in
  git, not in the conversation.
- The project's agreements (the state's "Agreements with the user")
  override every default in this protocol, including the worker prompt
  and the report format.

## Where continuity lives

| What | Where | Changes when |
|---|---|---|
| Protocol | this skill | the skill is updated |
| State and project agreements | `.agents/coordinator/state.md`, where `.agents/coordinator` may be a folder or a link to one ([`references/state-place.md`](references/state-place.md)) | something important changes |
| Done and dropped work | `.agents/coordinator/archive.md`, same versioning and commit as the state | a task or initiative ends |
| History and evidence | `git log` of the repository that holds the state, `chore(coordinator): …` commits | every checkpoint |
| Product decisions and specs | wherever the project keeps them | the user approves them |

Keep each fact in one place: the state cites the file, commit, or section
that holds it.

Reload paths:

- Compaction or resume of this session: the reload hook runs
  [`scripts/resume.sh`](scripts/resume.sh). It reinjects the state, and
  the protocol when both fit in the hook's budget; otherwise it names the
  files to read. It runs only when the session id matches the state's
  "Coordinator session" line.
- New session: the user invokes this skill again.

## Initiatives

Before you open, pause, close, or drop an initiative, archive a task, or
meet a state without an "Initiatives" table, read
[`references/initiatives.md`](references/initiatives.md).

## Take over or resume

1. Read `.agents/coordinator/state.md` whole. When it does not exist,
   create it from [`references/state-template.md`](references/state-template.md),
   ask the user for the objective, its initiatives, and the agreements the
   template lists, and commit it as [`references/state-place.md`](references/state-place.md)
   says. When it lacks a section, line, or column
   the template has, add it (the "Paseo agent" line only in Paseo).
2. When the state names another coordinator session, check whether it is
   still active ([`references/runtimes.md`](references/runtimes.md), "Is
   the old coordinator alive"); when it is, or you cannot tell, ask the
   user before going on. Then register this session: move the old one,
   with its "Paseo agent" value, to "Previous sessions", and write this
   one. In Paseo, add or update the "Paseo agent" line with
   `$PASEO_AGENT_ID`; elsewhere, remove it.
3. **Reconcile** the state with reality before acting:
   - `git log --oneline --since=<Last checkpoint>` in the project, plus
     `git status`, `git worktree list`, and branches;
   - every worker in the state: finished, waiting on a permission, or gone;
   - every check under "Listening";
   - the files and artifacts the state cites.
4. Mark each state item confirmed, changed (update it), or **uncertain**
   with the reason. A task you do not remember is a task to check.
5. Confirm the reload hook is registered for this runtime, and register it
   when missing, following [`references/reload-hook.md`](references/reload-hook.md).
6. Checkpoint and tell the user, in a few lines, what you found and the
   next step.

## Delegate

- Choose the worker mechanism in [`references/runtimes.md`](references/runtimes.md).
  Prefer one that outlives this session and reports when the worker
  finishes.
- One objective per worker, with a checkable finish criterion. Record it
  in the state: its id in the "Owner" cell of its "Now" row, and its files
  and whether it is session-bound in the "Workers" table.
- The worker prompt carries the objective, limits, files, finish
  criterion, and:
  - the model and provider limits you work under, from the agreements or
    your own instructions, which also bind the worker's own subagents;
  - the rules the agreements list for every worker prompt;
  - its own commit when finished, no push or PR;
  - `.agents/coordinator/` belongs to the coordinator: the worker leaves it
    untouched;
  - a short final report: what changed, commits, how it verified, open
    questions. Each question stands on its own, with its context and links
    to what it cites. A long report goes to a file, and the reply cites
    the path. Its last line is the **delivery line**, `DELIVERED <task>`
    or `STOPPED <task> <reason>`, so you, and any dashboard that reads the
    runtime (such as a Paseo plugin), can tell a finished worker from one
    that stopped.
- A task is **done** when the user accepts its deliverable as final, in
  words or by approving the next step that builds on it; the archive line
  records the acceptance date. Until then its row stays in "Now" with
  status `delivered, awaiting acceptance`, and follow-ups go to the same
  worker.

## Follow without babysitting

- Rely on completion notices instead of polling.
- Notices miss a worker that dies mid-turn: the runtime keeps showing it
  running. When the runtime or a dashboard shows a **silent** worker
  (shown running with no recent activity, a state row with no live
  worker, or idle without a delivery line), or you notice one at a
  checkpoint, read its activity. Follow up when the worker still exists
  and takes messages; relaunch it when it is gone; record which in its
  row.
- For what the runtime will not report (deploy, CI, people outside), set a
  scheduled check with an end (run limit or expiry), list it under
  "Listening" in the state, and delete it when it stops being useful.
  Promise monitoring only while one is running.
- On a result: verify it by its diff, commits, and claimed checks, and any
  visual output with your own eyes; delegate a long verification to a
  clean-context reviewer. Integrate it, call it installed or live only
  after a **readback** on each host and app it should reach (the
  installed version, or the behaviour seen there), and move to the next
  authorised step without waiting for "continue".

## Checkpoint

- Update the state when the objective, a decision, a delegation, a result,
  a block, or an interruption changes, and before long waits. Compaction
  gives no warning.
- Commit the state, with `archive.md` when it changed, alone:
  `chore(coordinator): <what changed>`, never mixed with worker code, in
  the repository that holds it ([`references/state-place.md`](references/state-place.md)).
- The state keeps what live data cannot show: decisions, blockers, next
  steps, "With you", and "Approvals". Status, sessions, and commits come
  from the runtime, git, or a dashboard that reads them; write a status
  only when live data cannot show it (`delivered, awaiting acceptance`,
  blocked on the user, paused).
- Each worker result updates its own row in the turn it arrives. Before a
  wave report, fix only the rows a runtime or dashboard signal flags as
  diverging from live data.
- When a worker will not be reused, archive it (as
  [`references/runtimes.md`](references/runtimes.md) says) and remove its
  "Workers" row in the same checkpoint. Keep a worker the next task reuses
  or one waiting on the user's feedback. A clean-context reviewer is not
  reused: after its first review its context is no longer clean.
- Keep `state.md` under 8,000 characters, the reload hook's budget: done
  and dropped work leaves for `archive.md`, and detail stays in its source
  file. Check with `wc -m` at each checkpoint.
- In the state's agreements, decisions, and "Now" rows, label each claim
  that is not a verified result: **decided** (the user approved, with the
  date), **proposed** (awaits the user), or **uncertain** (not confirmed,
  with why).
- A question for the user enters **With you** in the checkpoint that asks
  it. An answer moves it out: one that authorizes an action enters
  "Approvals" in the user's words, with what it covers and its limits. Any
  other answer becomes a decision: a product decision goes where the
  project keeps them, with a link from the state; a decision about how the
  coordination runs goes under "Continuity decisions", with the reason,
  the alternatives dropped and why, and what would justify reopening it.

## Talking to the user

- Report once per **wave** (a round of workers launched together), when
  every worker of the wave has finished or is blocked. Work you launch
  from a result while the wave runs joins that wave. A decision only the
  user can make waits for that report: the work it blocks waits, the rest
  goes on. Tell the user at once, outside the wave, about a risk to data,
  secrets, money, or a published artifact. When the user asks something
  mid-wave, answer it, then close with "Waiting on X and Y."; otherwise
  end each turn with that one line.
- The report opens with what changed and what needs the user, names tasks
  by name, links each deliverable, and closes with a status table grouped
  by initiative. Each decision is its **With you** row in full, with
  options and your recommendation, so nothing relies on an earlier turn.
- Stay concise, even when the user sends long text such as a transcript.
