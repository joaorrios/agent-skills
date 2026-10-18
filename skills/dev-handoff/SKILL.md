---
name: dev-handoff
description: Design handoff to developers, by any route: a Figma design into an HTML handoff page, a running build or prototype captured into annotated Figma, or both. Use when a design or prototype is ready for developers; start here before design:design-handoff, which this skill offers as a complement.
license: MIT
compatibility: Figma MCP server to read Figma and capture screens into it; a place to publish an HTML page the team can open.
---

# Dev Handoff

A **handoff** gives developers what they need to implement a delivery and shows plainly what is not settled. Everything in it is one of two things:

- **Spec**: what the **baseline** (the version chosen to ship, as Figma frames or a **build**, meaning running code or a prototype), the design system, and the decisions say. Developers implement it as written.
- **Draft**: everything else, such as prototype parameters, toggles, fallbacks, and workarounds, even at their baseline value, until the design system or a decision fixes them; sample data; generated or placeholder assets; copy no decision has approved. Each draft is a row in the **drafts table** (`What · Status · What's needed`), which every handoff carries, even when short.

A treatment the design system applies through a token (a corner shape, an elevation, a type style) is spec by reference: cite the token and leave its values to the design system.

## 1. Gather

- **Baseline**: the frames or build in scope, with a link to every screen and state (Figma node link, URL with route and state, or branch and commit).
- **Design system**: the tokens and components the baseline uses.
- **Decisions**: the brief in the team's task tracker (every requirement and every line of copy it supplies), meeting notes, and this conversation. Where a decision contradicts the baseline, or requires a state the baseline lacks, note it for step 3.

This step is complete when every screen and state in scope has a source link, and the design system and every decision source are named.

## 2. Choose the route

The route follows where the baseline lives and what it must convey:

- **Figma to page**: the baseline is finished Figma frames. Make an HTML handoff page from them: [`references/html-page.md`](references/html-page.md).
- **Build to Figma**: the baseline is a build. Capture its real screens into Figma and organize them into numbered, annotated sections: [`references/figma-capture.md`](references/figma-capture.md).
- **Both**: static states fit Figma, but motion, gestures, or interaction need a live demo. Static states go to Figma (existing frames, or captured), motion and interaction to an HTML page, and each links to the other. Read both references.

When the user named a route, take it. Otherwise state the route and its reason in one line with your step 3 questions, and proceed with it unless the answers change it. When the baseline itself is unclear (two prototype variants, or Figma and build disagree), which one is the baseline is the first question.

This step is complete when the route is named with its reason.

## 3. Ask what the sources leave open

Ask, in one round, only what the baseline, the design system, and the decisions leave unanswered. Whatever stays unanswered becomes a draft with what it needs; the handoff states only what a source says.

In the same round, offer the `design:design-handoff` checklist of states, edge cases, and accessibility as a complement. When the user takes it, run it on the same baseline and sort its output by the same rule: what a source answers becomes spec, the rest goes to the drafts table. When that skill is not installed, say so and continue.

This step is complete when every question has an answer or a row in the drafts table.

## 4. Make the handoff

Follow the route's reference, or both references on the both route. Write the handoff in the dev team's working language; product copy stays exactly as designed, in its own language.

This step is complete when every check in each reference you followed passes.

## 5. Check

- Every spec value traces to the baseline, the design system, or a decision, and token-applied treatments cite their token.
- Every kind of draft listed under Draft has a row in the drafts table, and only approved copy is called final.
- Every link opens the right node, route, or state.

This step is complete when every item holds.

## 6. Hand over

Write the comment for the dev task: what is ready and for which platforms, the handoff link (both links on the both route), the two or three behaviours to watch, and one line on what is still a draft. Post it once the user approves it, or hand the user the text when you cannot reach the tracker. Then remind the user to tell the developer through the team's usual channel.

This step is complete when the comment is posted or handed over, and the user has every link.
