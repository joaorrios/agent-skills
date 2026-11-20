---
name: approach-review
description: Dispatches an independent technical reviewer to challenge a proposed approach before implementation, then requires the approach author to resolve every substantive finding. Use after choosing how to build a substantive change and before coding it.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent for full independence.
---

# Approach Review

Review the technical approach through an independent context before implementation.

## Review inputs

When the approach continues earlier work or decisions, prepare an obligation ledger before dispatch. Give each applicable requirement or decision a stable id, its original source, current disposition, planned artifact location and observable proof. Include relevant dialogue, inherited PR/spec obligations, diagnostics and later amendments. Separate confirmed user decisions, technical proposals and unresolved evidence; identify the source revision. Preserve scope retained under another owner with its dependency and acceptance, rather than dropping it from the ledger.

The ledger maps inputs; original sources remain authority. Record source omissions or contradictions explicitly. It must not contain suggested findings, author defenses or an expected review verdict. For a self-contained approach, its requirements can supply this ledger.

## Author

You are the **approach author**. Do not perform the review yourself.

Dispatch a fresh isolated subagent with strong software-reasoning capability and use `agents/reviewer.md` as its reviewer instructions. Prefer a model family different from the approach author's. Choose the reviewer from the most cost-effective of the latest frontier models listed in [reviewer-models.md](reviewer-models.md). Local rules and explicit user overrides win over this rule. Keep the reviewer read-only when the runtime supports that boundary.

Keep the briefing unprimed. Give the reviewer every planning artifact, the obligation ledger and original-source coordinates, its repository or worktree, and enough coordinates to inspect the real system. Let the artifact speak for itself: keep the author's rationale, suspected weaknesses, defenses, and expected conclusions out of the briefing.

The reviewer owns investigation and may inspect the surrounding system as needed.

## Intent check

Run it whenever the approach was shaped in conversations with the user, including the current session, and their transcripts can be passed as files or exports.

1. Dispatch a separate extractor subagent with `agents/intent-extractor.md` and only the transcripts. Keep the approach and the obligation ledger out of its briefing so its intent ledger stays independent of the artifact.
2. After the reviewer returns its technical findings, send it `agents/intent-reviewer.md` and the intent ledger as its final pass. When the runtime cannot continue that reviewer, dispatch a fresh one with `agents/intent-reviewer.md`, the approach, its coordinates, and the intent ledger. Send the intent ledger without commentary.

Resolve missing and contradicted entries with `change` or by asking the user; ask the user about unresolved entries. Keep out-of-scope entries with the approach so the stage they name receives them.

## Resolve

Consume every substantive finding individually.

- **change** — revise the approach to address the finding.
- **disagree** — keep the approach and give a specific technical reason supported by evidence.
- **ask the user** — required when resolving the finding would revisit or contradict a user decision or request, settle an open question, or needs a product, scope, or priority choice the author does not own. Only the user can override a user decision. Ask in chat, wait for the answer, then apply it: `change` the approach, or record the answer as the disposition when the user keeps it as is. An open question, TODO, or "not yet approved" note written into an artifact leaves the finding unresolved.

A missing requirement is not a reason to dismiss a technical defect. If a finding exposes an omission in the written intent, update the affected artifact rather than using its silence as justification.

Do not defer, rank away, or silently drop substantive findings. Record findings, dispositions and supporting artifact locations in a review ledger. Keep that ledger distinct from the obligation and intent ledgers. Preserve the report and inspected artifact revisions so an earlier verdict cannot certify later changes.

After material revisions, obtain an independent follow-up over the changed approach and affected obligations. Reuse the reviewer for related corrections; a new broad pass is warranted when the approach materially changes beyond that scope.

## Done

The review is complete when an independent reviewer has inspected the approach against its applicable source obligations, ledger coverage is accounted for, and every substantive finding has an explicit `change`, an evidenced `disagree`, or an applied answer from the user. When the approach was shaped with the user, it also requires a completed intent ledger pass, or a stated reason the transcripts could not be passed. Report the inspected revisions, remaining limitations and planning-only evidence. Artifact existence or structural validation alone is not an accepted approach or implemented behavior.
