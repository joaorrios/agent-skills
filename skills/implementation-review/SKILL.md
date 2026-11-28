---
name: implementation-review
description: Dispatches an independent technical reviewer to inspect the technical aspects of a completed implementation, then requires the implementer to resolve every substantive finding. Use once per integration unit, such as a PR, when its work is complete and rebased onto the base it lands on, before accepting or shipping it.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent for full independence.
---

# Implementation Review

Review the technical implementation through an independent context before it ships.

## Implementer

You are the **implementer**. Do not perform the review yourself.

Review once per integration unit, such as a PR, when its work is complete and after its final rebase onto the base it lands on. A later rebase that only resolves conflicts gets a check of those resolutions, not a new review. When someone else already dispatches the unit's review, leave the review to them.

Dispatch a fresh isolated subagent with strong software-reasoning capability and use `agents/reviewer.md` as its reviewer instructions. Prefer a model family different from the implementer's. Choose the reviewer from the most cost-effective of the latest frontier models listed in [reviewer-models.md](reviewer-models.md). Local rules and explicit user overrides win over this rule. Keep the reviewer read-only when the runtime supports that boundary.

Keep the briefing unprimed. Give the reviewer the implementation itself: the relevant change range or modified files, the repository or worktree, and enough coordinates to inspect surrounding code. Let the code speak for itself: keep the implementer's rationale, suspected bugs, defenses, and expected conclusions out of the briefing.

The reviewer owns investigation and may inspect the surrounding system as needed.

## Resolve

Consume every substantive finding individually, whatever severity label the reviewer gave it.

- **fix** — change the implementation to address the finding, with the smallest fix: delete or narrow before adding a lock, cache, helper, or option.
- **disagree** — leave it unchanged and give a specific technical reason supported by evidence.
- **track** — only for a rare case whose fix is not easy. Follow the repository's policy for rare cases; without one, open an issue stating the scenario, what the user sees, and why it already behaves that way, or ask the user. Point the change to where it is tracked.
- **ask the user** — required when resolving the finding would revisit or contradict a user decision or request, recorded in the spec when one exists or stated in conversation, or needs a product, scope, or priority choice the implementer does not own. Only the user can override a user decision. Ask in chat, wait for the answer, then apply it: `fix` the implementation, or record the answer as the disposition when the user keeps it as is. A TODO, code comment, or "not yet approved" note leaves the finding unresolved.

A finding is **blocking** when the defect occurs on the common path, loses user content or a newer edit, reports false success, breaks an ordering or locking guarantee, violates the spec, or regresses existing behavior. A **rare case** is a real defect off the common path that keeps today's behavior and has none of those effects. A rare case with an easy fix gets `fix`.

A missing requirement is not a reason to dismiss a technical defect. Written intent and prior technical decisions are context, not authority over correctness.

## Re-check

Before sending the implementation back, reread the whole change and re-check every earlier finding against it. If review grew the change, cut first. Agree with a finding because it is right, not to end the loop, and keep the scope to what the work asked for.

Send it back only when a `fix` resolved a blocking finding, and at most once: to the same reviewer session, at the same reasoning effort, covering only what changed. When that pass still reports a blocking finding, stop fixing and bring the open findings to whoever owns the decision: the user, or whoever assigned you the work.

## Done

The review is complete when an independent reviewer has inspected the implementation, every substantive finding has an explicit `fix`, an evidenced `disagree`, a `track` that points to where it is tracked, or an applied answer from the user, and any owed re-check has returned or gone to the decision's owner.
