---
"agent-skills": minor
---

Add `wake-engineering-lead`, which lets an agent working for João's Engineering Lead wake it with one webhook POST (`source`, `agent_id`, `agent_title`, `state`, `summary`, `pr_url`) when the task ends `done`, `blocked`, or `needs-joao`, with the URL and key resolved from a documented host secret store, `~/.config/agent-wake/webhook.env`, or a path the brief names, and the PR comment kept as the wake when the task already has a PR.
