---
name: council
description: Trigger this if the user says 'council'.
license: MIT
compatibility: Works best with a way to start agents on other model providers, such as a multi-agent orchestrator or provider CLIs; with only one reachable provider, it runs two delegates from it.
---

# Council

Before an audit, address outstanding PR comments, fix known issues, and run
relevant checks. Give council the updated implementation; do not defer known
fixes until reviews return. If the user wants to discard the implementation
and explore new ideas, skip fixes to code being replaced.

Bring in delegates to help with the user's request, usually for review or
feedback. Use strong models at high reasoning effort. When only one provider
is reachable, bring in two delegates from it. Otherwise use up to three
different providers, one delegate each, and when Claude is reachable include
it with two delegates. Claude gets two seats because it judges best, so its
judgment weighs more. If the user's instructions name council members, use
those; a named Claude model still gets two seats unless the user says
otherwise. Otherwise pick the latest flagship model from each provider, for
example Claude Opus, GPT Sol, and Gemini Pro. When two delegates share a
model, label them apart, for example Claude Opus A and Claude Opus B.

In T3 Code, use `orchestrator_capabilities` to resolve the models, then
`delegate_task` to start the delegates in parallel. Elsewhere, use the
harness's subagent tools, or any tool in the environment that starts or
messages agents on other providers or harnesses, such as a multi-agent
orchestrator or a provider's CLI. If a named member is unavailable, report it
instead of substituting. When the council has fewer than three providers, go
ahead, and say in the results which providers were unreachable.

Give each delegate the request and relevant context. For review or feedback,
keep their work read-only. Collect their responses and summarize the useful
findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description.
Put this section before the model and harness line at the end:

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| Claude Opus A | 7/10 | 9/10 |
| Claude Opus B | 8/10 | 9/10 |
| GPT Sol | 8/10 | 10/10 |
| Gemini Pro | 7/10 | 9/10 |
```

If a delegate gives no score, write `no score`. Do not invent one.
If the PR is open, edit the description. Do not post a comment for this.
If there is no PR, put the same results in the final reply only.

If you agree with their recommendations, make the changes and request a fresh
review after. Continue this process until all delegates are satisfied with the
outcome.

Do not let repeated reviews result in scope creep. It is your job to fight to
keep scope limited.
