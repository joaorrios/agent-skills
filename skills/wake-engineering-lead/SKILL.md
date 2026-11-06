---
name: wake-engineering-lead
description: Reports to João's Engineering Lead (Grok Bot) at done, blocked, or needs-joao, on the GitHub PR the Lead follows or is handed, else by one webhook wake. Use when a brief identifies the requester as the Engineering Lead, hands you over to the Lead, or enables Lead wake.
license: MIT
compatibility: A shell with curl and jq, and gh for PR comments. Agent id and title come from Paseo when the agent runs there.
---

# Wake Engineering Lead

The **Engineering Lead** is the Grok Bot that coordinates João's personal Limnar and Paseo work and hands tasks to agents like you. It acts when something wakes it, so reach it once your task reaches a terminal state, through one channel: the GitHub pull request it follows when there is one, otherwise a webhook **wake**.

Reaching the Lead is on when the brief comes from the Lead, with no opt-in phrase needed, when a parent agent hands you over to it ("from here you deal with the Engineering Lead"), or when the brief enables it; a brief that turns it off wins.

## 1. Choose the channel

Choose at the start of the task, so you know where your result will go before you have one:

- **PR the Lead follows.** The Lead follows a PR when its own brief handed you that PR, or when it has already commented on it. Report on that PR (step 3).
- **PR the Lead does not follow yet.** The work has an open PR, or will end in one you open, and the Lead has not taken it: every PR you open, and every PR a parent agent or another requester named. Hand it over on the PR (step 3), with one wake so the Lead learns of it.
- **No PR.** The work has no PR and will not produce one. Report with a webhook wake (step 4).

A PR URL in a brief from anyone but the Lead is a coordinate for the work: it says where the code is, not whether the Lead follows it, and it never means the Lead can be left out.

This step is complete when you know which of the three applies. When the work later gains a PR, choose again.

## 2. Reach a terminal state

Report only when the task ends in one of these states; progress, partial results, and questions you can answer yourself stay in your normal replies. When several apply, report the one the Lead must act on first, `needs-joao` before `blocked` before `done`, and name the others in the summary.

| `state` | Meaning |
|---|---|
| `done` | The result is ready for the Lead: a PR ready for review, a report, a change applied. |
| `blocked` | You cannot go on without something the Lead can supply: access, missing information, a technical call you and your reviewers could not settle, a fix outside your scope. |
| `needs-joao` | Going on needs a product decision, which only João takes. |

**When João decides.** João takes product decisions: how the product is used, its design, its strategy, and its marketing, including what a feature does, how usable it is, and which product direction to follow between alternatives. Technical decisions, such as the framework, caching, or an implementation tradeoff, are not his: make them yourself, ask a technical reviewer or advisor agent, or report `blocked` so the Lead unblocks you.

Merging, spending money, and contacting people stay outside your task: when the work needs one, say so in your report, as `done` when it is the next step after finished work and `blocked` when you cannot finish without it, and the Lead takes it from there.

Write a **summary** of up to three sentences the Lead can act on without opening your transcript: what is ready, what blocks you and what would unblock it, or what João must decide.

## 3. Report on the PR

Comment on the PR, opening with the Lead and the state so the Lead finds its part of the thread:

```markdown
**Engineering Lead** · `blocked`

<summary>
```

- **PR the Lead follows:** the comment is the whole report.
- **Handing the PR over:** add a line saying you are handing this PR to the Lead and what stays open on it, then send one wake (step 4) with the PR's URL so the Lead starts following it. From then on, the PR is the channel.

This step is complete when the comment is posted and, for a handover, the wake is sent.

## 4. Webhook wake

### Find the destination

Resolve the webhook URL and key from the first source that yields both, so a brief needs to carry neither once the host is set up:

1. **Secret store.** When the runtime documents a secret store holding them (an OS keychain, a Paseo credential helper, or equivalent), read them through the store's own read command.
2. **Well-known file.** `~/.config/agent-wake/webhook.env`, defining `WEBHOOK_URL` and `WEBHOOK_KEY` unless the brief renames them. When it is missing, go on to the next source; create nothing.
3. **Brief.** The file path or variable names the brief gives.

Load the values straight into shell variables and use them only there: `set -a; . "$file"; set +a` for a file, the store's read command inside `$( )` for a store. They are credentials, and the transcript is visible to others: printing the file or a value (`cat`, `echo`, `printf`) puts them in it, and so does pasting a value into the reply, a commit, or a PR body.

This step is complete when both variables are set. When no source yields both, skip the POST and say in your final reply that the Lead was not woken because no webhook is configured. Another webhook env file on the host belongs to a different consumer, so it stays out of the search.

### POST

Send this JSON body, every field present:

| Field | Value |
|---|---|
| `source` | `"paseo-agent"`, so the Lead's single webhook can tell this from its other senders. |
| `agent_id` | `$PASEO_AGENT_ID`, or the runtime's session id outside Paseo (`$CLAUDE_CODE_SESSION_ID` in Claude Code). |
| `agent_title` | The agent's Paseo name (add `--host` to `paseo inspect` when the brief gives one), or the title the brief gave you. |
| `state` | `done`, `blocked`, or `needs-joao`. |
| `summary` | The summary from step 2. |
| `pr_url` | The URL of the PR you are handing over, or `null` when there is none. |

```sh
set -a; . ~/.config/agent-wake/webhook.env; set +a  # or whichever source the destination resolved to
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
