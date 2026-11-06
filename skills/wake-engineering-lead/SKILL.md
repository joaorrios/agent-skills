---
name: wake-engineering-lead
description: Wakes João's Engineering Lead (Grok Bot) with one webhook POST when the task reaches done, blocked, or needs-joao. Use when a brief identifies the requester as the Engineering Lead or enables Lead wake.
license: MIT
compatibility: A shell with curl and jq. Agent id and title come from Paseo when the agent runs there.
---

# Wake Engineering Lead

The **Engineering Lead** is the Grok Bot that coordinates João's personal Limnar and Paseo work and hands tasks to agents like you. It stays idle until something wakes it. A **wake** is one POST to the Lead's webhook, sent when your task reaches a terminal state, so the Lead can act without polling you.

The wake is on when the brief comes from the Lead, with no opt-in phrase needed, or when the brief enables it; a brief that turns it off wins. When the brief points to an existing GitHub pull request, put the terminal state and summary in a comment on that PR instead: the Lead follows its PRs, and a webhook POST would only duplicate the comment. The webhook covers work with no PR, a PR you opened as the result, and briefs that ask for the webhook explicitly.

## 1. Find the destination

Resolve the webhook URL and key from the first source that yields both, so a brief needs to carry neither once the host is set up:

1. **Secret store.** When the runtime documents a secret store holding them (an OS keychain, a Paseo credential helper, or equivalent), read them through the store's own read command.
2. **Well-known file.** `~/.config/agent-wake/webhook.env`, defining `WEBHOOK_URL` and `WEBHOOK_KEY` unless the brief renames them. When it is missing, go on to the next source; create nothing.
3. **Brief.** The file path or variable names the brief gives.

Load the values straight into shell variables and use them only there: `set -a; . "$file"; set +a` for a file, the store's read command inside `$( )` for a store. They are credentials, and the transcript is visible to others: printing the file or a value (`cat`, `echo`, `printf`) puts them in it, and so does pasting a value into the reply, a commit, or a PR body.

This step is complete when both variables are set. When no source yields both, skip the POST and say in your final reply that the Lead was not woken because no webhook is configured. Another webhook env file on the host belongs to a different consumer, so it stays out of the search.

## 2. Reach a terminal state

Post only when the task ends in one of these states:

| `state` | Meaning |
|---|---|
| `done` | The result is ready for the Lead: a PR opened, a report in the reply, a change applied. |
| `blocked` | You cannot go on without something the Lead can supply: access, missing information, a fix outside your scope. |
| `needs-joao` | Going on needs João himself: a decision, UAT, a merge, spending money, or contacting people. |

Progress, partial results, and questions you can answer from the brief stay in your normal replies. The POST is the only outward action this skill adds; merges, spending, and messages to people go to João through `needs-joao`.

## 3. POST

Send this JSON body, every field present:

| Field | Value |
|---|---|
| `source` | `"paseo-agent"`, so the Lead's single webhook can tell this from its other senders. |
| `agent_id` | `$PASEO_AGENT_ID`, or the runtime's session id outside Paseo (`$CLAUDE_CODE_SESSION_ID` in Claude Code). |
| `agent_title` | The agent's Paseo name (add `--host` to `paseo inspect` when the brief gives one), or the title the brief gave you. |
| `state` | `done`, `blocked`, or `needs-joao`. |
| `summary` | Up to three sentences the Lead can act on without opening your transcript: what is ready, what blocks you and what would unblock it, or what João must decide. |
| `pr_url` | The PR's URL, or `null` when there is none. |

```sh
set -a; . ~/.config/agent-wake/webhook.env; set +a  # or whichever source step 1 resolved
title=$(paseo inspect "$PASEO_AGENT_ID" --json | jq -r .Name)
jq -n --arg agent_id "$PASEO_AGENT_ID" --arg agent_title "$title" \
      --arg state "done" --arg summary "<summary>" --arg pr_url "<url or empty>" \
  '{source: "paseo-agent", agent_id: $agent_id, agent_title: $agent_title,
    state: $state, summary: $summary, pr_url: ($pr_url | if . == "" then null else . end)}' |
curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$WEBHOOK_URL" \
  -H "Authorization: Bearer $WEBHOOK_KEY" -H 'Content-Type: application/json' --data-binary @-
```

Post once per terminal state, after everything else in the task is finished, so the Lead wakes to the final result; a later follow-up that ends in a new terminal state posts again.

This step is complete when the POST returned a 2xx status and your final reply says the Lead was woken with that `state`. On any other status or a network error, retry once; if it still fails, give the status in your final reply.
