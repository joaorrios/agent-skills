# Coordinator state

Protocol: the `project-coordinator` skill. Workers leave this file
untouched.

- Coordinator session: `<id>` (since YYYY-MM-DD; runtime: <runtime>)
- Previous sessions: none
- Last checkpoint: YYYY-MM-DD

## Objective

<What the user wants delivered, and where its source list or spec lives.>

## Now

<Current wave, what runs, last publication.>

Status is a verified result, not an intent. Next step and blocker are
concrete enough to act on without asking.

| Item | Owner | Status | Next step | Blocker | Reference |
|---|---|---|---|---|---|

## Listening

Every scheduled check or watch running for the coordinator.

| Watches | Mechanism and id | Ends | Remove with |
|---|---|---|---|

## Agreements with the user

Each line dated and labelled **decided** or **proposed**. Ask about these
at the first takeover; leave out what the repo's agent instructions
already settle and point to them instead.

- Models and providers workers may use, their own subagents included.
- Commit convention for workers.
- Publish or deploy cadence (per wave, per item, on request).
- Where product decisions and specs live.
- Report format, when it differs from the protocol's default.

## Continuity decisions

<Numbered. Each with reason, alternatives dropped, and what would reopen
it. Start with where this file lives: versioned in the repo (history
through `chore(coordinator)` commits) or kept out of git.>

## Open (not delegated)

## Environment

<Branch, dev servers and where they run, deploy notes.>

## Next step
