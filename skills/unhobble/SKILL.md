---
name: unhobble
description: Updates and simplifies context engineering for new, stronger models. Removes bloat, excessive constraints, repetitive exposition, instruction conflicts, and attention hogs.
argument-hint: "[path or artifacts]"
license: MIT
compatibility: Requires file access and a separate reviewer who has not taken part in the rewrite.
---

# Unhobble

To **unhobble** a model is to remove the constraints that prevent it from making full use of its capabilities. In this skill, that means revising instructions and context that unnecessarily limit its judgment or burden its attention, often inherited from workarounds for weaker models. Preserve the user's intent and the facts and constraints the model still needs to do the work.

Rewrite the instructions to express what the user wants clearly and let the model use its judgment. Preserve the facts and constraints it needs to do the work.

## 1. Recover the current intent

Identify what the user wants the instructions to achieve, and what facts and constraints the model needs to act on that intent.

Read each target in full. Check related documents and authoritative sources for current facts and requirements. Treat the existing text as evidence; some of it may be out of date. Use the user's current direction to resolve conflicts with older instructions.

Present your understanding to the user, with the sources that support it and any questions that affect the rewrite.

This step is complete when the user agrees with that understanding and those questions are resolved.

## 2. Assess the existing material

Use the agreed intent and necessary context to decide what to do with the material. Assess it at the level where a change is needed, from a single rule to multiple documents.

Auditable decisions:

- **Keep** — the content is needed and already expresses the intent or context clearly.
- **Cut** — the content is no longer needed or leads the model away from what the user wants.
- **Reshape** — the content is needed, but its wording, form, or location should change.
- **Add** — needed guidance or context is missing from the available sources.
- **Clarify** — more information is needed to decide what to do with the content.

Principles:

- **Judgment** — Trust capable models to use good judgment. Trying to control every decision can make their reasoning worse. Give them clear goals, relevant context, and real constraints, then let them decide how to act.
- **Attention** — What you include, repeat, or explain at length directs the model’s attention. Keep Chekhov’s gun effect in mind when choosing what to include and emphasize. Remove explanations of things the model already knows and details that give a concern or solution more weight than the user’s intent calls for.
- **Exploration** — Examples that teach the model how to act, or list possible places to look, can draw its attention away from cases that were not shown. Replace them with a clear goal, the full scope, and a clear condition for completion. Let the model work out which cases matter.
- **Useful guidance** — ask whether the model would already do what the user wants without the instruction. If so, remove it. If you are unsure and the answer would change your decision, try the same task with and without it and compare the results.
- **Interface** — Make tools clear through their names, inputs, affordances and constraints, so the model can work out how to use them without enumerating use cases.
- **Disclosure** — keep shared guidance in the main document. Put details needed only in certain cases behind a link that says what they cover and when to read them.
- **Single source** — state each rule or fact in one place. Link to it from other places where the model needs it.
- **Right place** — Remove prose that repeats what the artifacts already make clear. Use prose for what they cannot express well on their own.

Give a reason for each decision. Resolve questions that affect the rewrite. Confirm changes to the agreed intent with the user.

This step is complete when every part of the material has been assessed, each decision has a reason, each **Clarify** has been resolved, and missing guidance or context has been identified.

## 3. Rewrite the material

Rewrite the material to express that intent clearly. Apply the decisions from step 2 and make the needed context available where the model will use it.

**Write the current state** — State the current rules and facts directly. Cut narration of changes or negations about what came before. If nothing in a document is still needed, remove it.

This step is complete when every **Keep**, **Cut**, **Reshape**, and **Add** decision has been applied.

## 4. Update related material

Find everything affected by the changes. Update or remove the affected parts so they agree with the rewritten material. Historical and archived records may keep their outdated mentions.

This step is complete when all affected material still in use reflects the current instructions, and links to moved or added content work and state when to read it.

## 5. Review the result

Use a separate reviewer who has not taken part in the rewrite. Give them the user's agreed goals, preferences, facts, and constraints; the relevant sources; and the material before and after the changes. Let them reach their own conclusions.

Ask the reviewer to check whether step 1 missed anything and whether the result does what the user wants. All needed facts and constraints must be available to the model through the instructions, tools, or other sources. Keep your own analysis, preferred solution, and unrelated workspace material out of that context.

Check for failure modes:

- **Under-cut** — unnecessary rules, repetition, or unintended framing remain.
- **Over-cut** — a removal loses guidance or context the model still needs.
- **Wrong shape** — needed content is misleading, hard to find, or in the wrong place or form.
- **Missing** — a goal, preference, fact, or constraint was overlooked or is still unsupported.

Judge by what the model needs now. Earlier presence alone is no reason to restore a passage.

After the reviewer's first assessment, compare the findings with the reasons recorded in step 2. Address each finding or explain why you disagree. Confirm changes to the agreed intent with the user. After edits, update related material and have the reviewer check the changes again.

The pass is complete when all four failure modes are absent, each finding has been addressed or rejected with a reason, and the reviewer has checked any resulting changes.
