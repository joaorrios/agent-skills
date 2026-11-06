---
"agent-skills": minor
---

Add `wake-engineering-lead`, which lets an agent working for João's Engineering Lead report a terminal state (`done`, `blocked`, or `needs-joao` for product decisions only) on the GitHub PR the Lead follows, hand a PR over to the Lead with a comment and one wake, or, with no PR, wake the Lead with one webhook POST (`source`, `agent_id`, `agent_title`, `state`, `summary`, `pr_url`) whose URL and key come from a documented host secret store, `~/.config/agent-wake/webhook.env`, or a path the brief names.
