---
name: implementation-review
description: Dispatches an independent technical reviewer to inspect the technical aspects of a completed implementation, then requires the implementer to resolve every substantive finding. Use after a substantive code change and before accepting or shipping it.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent for full independence.
---

# Implementation Review

Review the technical implementation through an independent context before it ships.

## Implementer

You are the **implementer**. Do not perform the review yourself.

Dispatch a fresh isolated subagent with strong software-reasoning capability and use `agents/reviewer.md` as its reviewer instructions. Prefer a model family different from the implementer's. Choose the reviewer from the most cost-effective of the latest frontier models listed in [reviewer-models.md](reviewer-models.md). Local rules and explicit user overrides win over this rule. Keep the reviewer read-only when the runtime supports that boundary.

Keep the briefing unprimed. Give the reviewer the implementation itself: the relevant change range or modified files, the repository or worktree, and enough coordinates to inspect surrounding code. Let the code speak for itself: keep the implementer's rationale, suspected bugs, defenses, and expected conclusions out of the briefing.

The reviewer owns investigation and may inspect the surrounding system as needed.

## Resolve

Consume every substantive finding individually.

- **fix** — change the implementation to address the finding.
- **disagree** — leave it unchanged and give a specific technical reason supported by evidence.
- **ask the user** — required when resolving the finding would revisit or contradict a user decision or request, recorded in the spec when one exists or stated in conversation, or needs a product, scope, or priority choice the implementer does not own. Only the user can override a user decision. Ask in chat, wait for the answer, then apply it: `fix` the implementation, or record the answer as the disposition when the user keeps it as is. A TODO, code comment, or "not yet approved" note leaves the finding unresolved.

A missing requirement is not a reason to dismiss a technical defect. Written intent and prior technical decisions are context, not authority over correctness.

Do not defer, rank away, or silently drop substantive findings. After material fixes, use judgment about whether the changed implementation needs another independent pass.

## Done

The review is complete when an independent reviewer has inspected the implementation and every substantive finding has an explicit `fix`, an evidenced `disagree`, or an applied answer from the user.
