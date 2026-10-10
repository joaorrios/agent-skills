# Runtimes

As of 2026-10-08. These features move fast: check the runtime's current
docs when something here fails to match.

The coordinator needs workers that report when they finish and take
follow-ups, a way to learn its own session id, and, for what no worker
reports, a scheduled check. A worker or check that dies with the
coordinator's session is **session-bound**: record it as such, and on
takeover reconcile it from git instead of waiting for its notice.

## Paseo

Runs agents of any provider and keeps them, and its heartbeats, alive
across coordinator sessions; the user follows the whole team in the app.

- When the coordinator is itself a Paseo agent, the workers it creates
  join its workspace by default, so the user sees one workspace holding
  the coordinator and its team. Launch settings come from the user's
  profiles.
- Completion notices, follow-ups to the same agent, archiving, and
  heartbeats or schedules for checks all exist as tools; reconcile from
  its agent, permission, and schedule lists.

## Claude Code

- Session id: `${CLAUDE_SESSION_ID}` in the skill body, or
  `$CLAUDE_CODE_SESSION_ID` in the shell.
- Background subagents notify on finish and take follow-ups through
  `SendMessage`. They survive compaction and come back when the session is
  resumed, but one still running when the process ends stays unfinished.
- Agent teams (experimental, behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)
  add teammates that message each other and the lead. They end with the
  lead's session, and a resumed lead cannot reach them: spawn new ones.
- Durable workers: background sessions (`claude --bg`) run under a
  supervisor and survive the terminal closing; reach them through
  cross-session messaging, which can notify when the target goes idle.
- Scheduled checks: `/loop` and cron tasks are session-bound (restored on
  resume, expire after 7 days); routines through `/schedule` run in the
  cloud and outlive the session.

Docs: <https://code.claude.com/docs/en/sub-agents>,
<https://code.claude.com/docs/en/agent-teams>,
<https://code.claude.com/docs/en/agent-view>,
<https://code.claude.com/docs/en/cross-session-messaging>,
<https://code.claude.com/docs/en/scheduled-tasks>.

## Codex

- Session id: `$CODEX_SESSION_ID` in the shell, the root session's id;
  inside a subagent `$CODEX_THREAD_ID` names the subagent instead. Both
  come from the source, not the docs.
- Subagents start on request, and the parent waits for the results it
  asked for. An idle parent is not woken when a background subagent
  finishes ([openai/codex#15723](https://github.com/openai/codex/issues/15723),
  open), so collect the wave before ending the turn.
- Scheduled checks: scheduled tasks in the desktop app return to the same
  chat while the app runs; cloud tasks keep working with the computer
  asleep. The CLI has neither.

Docs: <https://learn.chatgpt.com/docs/agent-configuration/subagents>,
<https://learn.chatgpt.com/docs/automations>,
<https://learn.chatgpt.com/docs/cloud>.

## Cursor

Use Cursor Projects instead of this skill. A Project is a built-in
coordinator: it keeps context across chats, delegates to agents in
parallel, runs on a schedule or on events, and keeps running in the cloud
with the laptop closed (beta since 2026-09-10, paid plans).

Docs: <https://cursor.com/docs/agent/projects>.
