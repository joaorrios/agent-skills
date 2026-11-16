---
name: approach-review
description: Dispatches an independent technical reviewer to challenge a proposed approach before implementation, then requires the approach author to resolve every substantive finding. Use once the approach to a substantive change is complete, before coding it.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent for full independence.
---

# Approach Review

Review the technical approach through an independent context before implementation.

## Author

You are the **approach author**. Do not perform the review yourself.

An approach states the decisions and interfaces a capable implementer builds from; detail below that belongs to the implementer. Before review, test each assumption the approach rests on that a quick throwaway probe or prototype can settle, and cite the result in the approach.

Review the approach once, when it is complete. When someone else already dispatches its review, leave the review to them.

Dispatch a fresh isolated subagent with strong software-reasoning capability and use `agents/reviewer.md` as its reviewer instructions. Prefer a model family different from the approach author's. Choose the reviewer from the most cost-effective of the latest frontier models listed in [reviewer-models.md](reviewer-models.md). Local rules and explicit user overrides win over this rule. Keep the reviewer read-only when the runtime supports that boundary.

Keep the briefing unprimed. Give the reviewer the proposed approach, its repository or worktree, and enough coordinates to inspect the real system. Let the artifact speak for itself: keep the author's rationale, suspected weaknesses, defenses, and expected conclusions out of the briefing.

The reviewer owns investigation and may inspect the surrounding system as needed.

## Intent check

Run it whenever the approach was shaped in conversations with the user, including the current session, and their transcripts can be passed as files or exports.

1. Dispatch a separate extractor subagent with `agents/intent-extractor.md` and only the transcripts. Keep the approach out of its briefing so its ledger stays independent of the artifact.
2. After the reviewer returns its technical findings, send it `agents/intent-reviewer.md` and the ledger as its final pass. When the runtime cannot continue that reviewer, dispatch a fresh one with `agents/intent-reviewer.md`, the approach, its coordinates, and the ledger. Send the ledger without commentary.

Resolve missing and contradicted entries with `change` or by asking the user; ask the user about unresolved entries. Keep out-of-scope entries with the approach so the stage they name receives them.

## Resolve

Consume every substantive finding individually, whatever severity label the reviewer gave it.

- **change** — revise the approach to address the finding.
- **disagree** — keep the approach and give a specific technical reason supported by evidence.
- **track** — only for a rare case whose fix is not easy. Follow the repository's policy for rare cases; without one, open an issue stating the scenario, what the user sees, and why it already behaves that way, or ask the user. Point the approach to where it is tracked.
- **ask the user** — required when resolving the finding would revisit or contradict a user decision or request, settle an open question, or needs a product, scope, or priority choice the author does not own. Only the user can override a user decision. Ask in chat, wait for the answer, then apply it: `change` the approach, or record the answer as the disposition when the user keeps it as is. An open question, TODO, or "not yet approved" note written into an artifact leaves the finding unresolved.

A finding is **blocking** when the defect would occur on the common path, lose user content or a newer edit, report false success, break an ordering or locking guarantee, violate the spec, or regress existing behavior. A **rare case** is a real defect off the common path that keeps today's behavior and has none of those effects. A rare case with an easy fix gets `change`.

A missing requirement is not a reason to dismiss a technical defect. If a finding exposes an omission in the written intent, update the affected artifact rather than using its silence as justification.

## Re-check

Before sending the approach back, reread it whole and re-check every earlier finding against it.

Send it back only when a `change` resolved a blocking finding, and at most once: to the same reviewer session, at the same reasoning effort, covering only what changed. When that pass still reports a blocking finding, stop revising and bring the open findings to whoever owns the decision: the user, or whoever assigned you the approach.

## Done

The review is complete when an independent reviewer has inspected the approach, every substantive finding has an explicit `change`, an evidenced `disagree`, a `track` that points to where it is tracked, or an applied answer from the user, and any owed re-check has returned or gone to the decision's owner. When the approach was shaped with the user, it also requires a completed ledger pass, or a stated reason the transcripts could not be passed.
