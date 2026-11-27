# Coordinator state

Protocol: the `project-coordinator` skill. Workers leave this file
untouched.

- Coordinator session: `<id>` (since YYYY-MM-DD; runtime: <runtime>)
- Paseo agent: `<id>` (only in Paseo: the value of `$PASEO_AGENT_ID`)
- Previous sessions: none
- Last checkpoint: YYYY-MM-DD

## Objective

<What the user wants delivered, and where its source list or spec lives.>

## Initiatives

Each initiative serves the objective. Status: active, or paused with the
reason.

| Initiative | Goal | Done when | Status | Reference |
|---|---|---|---|---|

## Now

<Current wave, what runs, last publication.>

Status only when live data cannot show it. Next step and blocker are
concrete enough to act on without asking.

| Item | Initiative | Owner | Status | Next step | Blocker | Reference |
|---|---|---|---|---|---|---|

## Workers

| Worker id | Files | Session-bound |
|---|---|---|

## With you

Questions waiting on the user, each answerable cold.

| Key | Question | Context and links | Options, recommended first | Blocks | Since |
|---|---|---|---|---|---|

## Approvals

What the user authorized, in their exact words.

| Key | User's words | Covers | Target and limits | When |
|---|---|---|---|---|

## Listening

Every scheduled check or watch running for the coordinator.

| Watches | Mechanism and id | Ends | Remove with |
|---|---|---|---|

## Agreements with the user

Each line dated and labelled **decided** or **proposed**. Leave out what
the repo's agent instructions already settle and point to them instead.

- Models and providers workers may use, their own subagents included.
- Rules every worker prompt carries (for example: with a browser, close
  everything it opened in `finally` and leave the tabs it found open).
- Commit convention for workers.
- Publish or deploy cadence (per wave, per item, on request).
- Where product decisions and specs live.
- Report format, when it differs from the protocol's default.

## Continuity decisions

<Numbered. Each with reason, alternatives dropped, and what would reopen
it. Start with where this file and `archive.md` live: versioned in the
repo (history through `chore(coordinator)` commits; name who can read the
remote it is pushed to, since a pushed commit stays in that history) or
kept out of git.>

## Open (not delegated)

Work the coordinator does itself or has not assigned yet, one line each,
with its initiative.

## Environment

<Branch, dev servers and where they run, deploy notes.>
