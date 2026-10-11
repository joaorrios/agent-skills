---
name: approach-review
description: Dispatches an independent technical reviewer to challenge a proposed approach before implementation, then requires the approach author to resolve every substantive finding. Use after choosing how to build a substantive change and before coding it.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent for full independence.
---

# Approach Review

Review the technical approach through an independent context before implementation.

## Author

You are the **approach author**. Do not perform the review yourself.

Dispatch a fresh isolated subagent with strong software-reasoning capability and use `agents/reviewer.md` as its reviewer instructions. Prefer a different model family from the author when a comparably capable one is available. Keep the reviewer read-only when the runtime supports that boundary.

Keep the briefing unprimed. Give the reviewer the proposed approach, its repository or worktree, and enough coordinates to inspect the real system. Let the artifact speak for itself: keep the author's rationale, suspected weaknesses, defenses, and expected conclusions out of the briefing.

The reviewer owns investigation and may inspect the surrounding system as needed.

## Intent check

Run it whenever the approach was shaped in conversations with the user, including the current session, and their transcripts can be passed as files or exports.

1. Dispatch a separate extractor subagent with `agents/intent-extractor.md` and only the transcripts. Keep the approach out of its briefing so its ledger stays independent of the artifact.
2. After the reviewer returns its technical findings, send it the ledger as its final pass. When the runtime cannot continue that reviewer, dispatch a fresh one with `agents/reviewer.md`, the approach, and the ledger for this pass alone. The ledger is evidence of user intent; send it without commentary.

Every ledger entry reported as anything other than honored or out of scope is a substantive finding. Confirm that a named owner exists for each handed-off entry.

## Resolve

Consume every substantive finding individually.

- **change** — revise the approach to address the finding.
- **disagree** — keep the approach and give a specific technical reason supported by evidence.
- **ask the user** — required when resolving the finding would revisit or contradict a user decision or request, or needs a product, scope, or priority choice the author does not own. Ask in chat, wait for the answer, then apply it. An open question, TODO, or "not yet approved" note written into an artifact leaves the finding unresolved.

A user decision is outside the author's `disagree`; a contradicted or missing intent entry is resolved by `change` or by asking the user.

A missing requirement is not a reason to dismiss a technical defect. If a finding exposes an omission in the written intent, update the affected artifact rather than using its silence as justification.

Do not defer, rank away, or silently drop substantive findings. After material revisions, use judgment about whether the changed approach needs another independent pass.

## Done

The review is complete when an independent reviewer has inspected the approach and every substantive finding has an explicit `change`, an evidenced `disagree`, or an applied answer from the user.
