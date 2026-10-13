---
name: prompt-writing
description: Writes one-off prompts that ask a subagent, another agent, or another model for a specific output. Use when writing one, or when one returned the wrong output.
license: MIT
---

# Prompt Writing

A **brief** is a one-off prompt that asks a model or agent for a specific output: a subagent dispatch, a task handed to another agent, a request to another model. It runs once, so its whole value is getting the right output without wasted runs: give the goal, the context the recipient lacks, and the real constraints in the fewest tokens that do it, then leave the rest to the recipient's judgment. When a brief returned the wrong output, go to [When the output is wrong](#when-the-output-is-wrong).

## 1. Gather what the brief carries

Know the **recipient** first: the model or agent that will run the brief, its tier, its tools, and what it loads into context on its own. Then gather what the brief carries:

- **Goal**: what the output is for, who consumes it (you, a person, a parser), and why it matters.
- **What only you know**: facts and constraints that reach the recipient only through you, because this session found them, the user said them in your conversation, or they sit in a doc you were told to use. That covers the rules of skills you loaded, confirmations given for this task, and what is already done, dead ends included. Files the recipient loads on its own, such as `AGENTS.md` or `CLAUDE.md`, already reach it.
- **Coordinates**: the paths, URLs, ids, and branches of the real material, each with what it holds. A pasted or paraphrased copy spends the recipient's attention and drifts from the source.
- **Done**: what a finished output looks like and what to return in what shape, stated so the recipient can tell done from not done.

This step is complete when you know the recipient and can state each item in a few lines.

## 2. Zone the freedom

Decide how much latitude each part of the task gets, by how fragile it is:

- **Open field**: several outputs are valid and quality is a judgment call (grouping, generation, copywriting, research, design). Give the goal, the bar, and the context; trust the recipient to find the route.
- **Narrow bridge**: one output is correct and a small error breaks it (schemas, data formats, migrations, API calls, irreversible actions). Give exact steps and a fixed output shape.

Use a schema when one exists. Otherwise spell the format out in the brief, with three to five varied examples.

Most briefs mix both. A brief to an agent leaves the approach open and locks the return format; a generation request leaves the content open and locks the output schema. Zone each part rather than picking one mode for the whole brief.

Calibrate the zones to the recipient: the less capable the model, the more of the task becomes narrow bridge. The more capable, including a recipient more capable than you, the more stays open field, with the method left to it, since the steps you would take cap a stronger model. When the recipient is a small or fast model, read [`references/small-models.md`](references/small-models.md).

This step is complete when every part is open field or narrow bridge, and each narrow bridge has its schema or format.

## 3. Draft

Write the open-field parts at the right **altitude**: specific enough to guide, general enough to leave the recipient strong heuristics. Too low hardcodes brittle logic ("if the title contains a colon, split on it and capitalize the second half"). Too high gives no signal ("write good titles"). Between them: "make titles specific and punchy over comprehensive." Write the narrow-bridge parts as exact steps with their schema or format.

- **Intent over enumeration.** State the principle once and let the recipient handle the cases. "Match the register to the situation" covers the fifth case that four if-clauses miss. Examples of how to act or where to look enumerate too: give the goal, the full scope, and the completion criterion instead.
- **Reasons with constraints.** A constraint with its why generalizes to cases you did not list. "The response is read aloud by a text-to-speech engine, so write out symbols" beats "never use ellipses".
- **Chekhov's gun.** The recipient treats everything in the brief as something it is meant to use: a mentioned edge case gets handled, a named tool gets called, a detail mentioned in passing becomes the focus, and parallel runs given the same detail converge on it. Include only what should fire, and cut details that give a concern more weight than the user's intent calls for. Emphasis works the same way: CRITICAL and MUST make capable models overtrigger, so state a real constraint plainly with its reason.
- **Positive targets.** Say what to do. A prohibition puts the banned behaviour on stage too. Keep one only as a hard guardrail you cannot phrase positively, and pair it with the target behaviour.
- **Material and references.** A draft, mockup, or sample in context, whether text, image, video, or motion, becomes a **mold** the output copies, however the brief frames it. Match what you pass to the aim:
  - **Copy**: pass the single sample.
  - **Quality bar**: name a body of work the recipient knows, such as a site, an author, a publication, a style, or a tool.
  - **Invention**: pass the principles the material holds, such as its structure, tone, or priorities, rather than the material itself.
  - **Work on the material** (review it, edit it, follow it): point to it.
- **Bounded demands.** Every superlative (best, all, every, until perfect) gets a stopping condition. The strongest completion criteria are both checkable and exhaustive: "every changed endpoint has a test" rather than "test thoroughly".
- **Literal reading.** Capable recipients do what the words say: "suggest changes" gets suggestions, "change it" gets changes. Choose the verb for the output you want. Name a method only when you need the work done exactly that way; otherwise the goal and done carry the request.
- **Current state.** Derive each rule from the current intent and the risks this task carries for this recipient. A past mistake earns a line only if the same risk is live in this task.
- **Matching form.** The brief's form shapes the answer's: a short, plain brief gets a short, plain answer, and a long brief full of jargon gets a long answer full of jargon.

When you want an independent judgment, keep the brief **unprimed**: give the artifact and the coordinates, and keep your conclusions, suspicions, and preferred answer out.

This step is complete when each item from step 1 appears once, written as its zone calls for.

## 4. Check the draft

Read the draft line by line. Each line follows the step 3 rules and either changes behaviour against the recipient's default or carries something only you know; restated defaults such as "be helpful" or "think step by step" say nothing. Keep a line when unsure whether it carries something only you know; delete a whole sentence that fails rather than trimming words.

Then check how the draft reads without your context. When a wrong start would waste real work, dispatch a subagent on the recipient's model, give it only the draft, unprimed, and ask how it understands the task and what it would do, without doing it. Compare that reading with the intent from step 1 and fix where they diverge. Trust the fresh reading over your own sense of ambiguity: the author tends to find ambiguity a fresh reader resolves. Otherwise, read the draft yourself as the recipient would, with only this brief and its tools.

This step is complete when every line passes and a reading without your context matches the intent.

## 5. Approve and send

Show the user the brief and send it once they approve it. When they change it, apply the change and show it again.

This step is complete when the user has approved the exact brief you send.

## When the output is wrong

Read the output against the zones. Most failures are one of these misfits:

- **Generic average**: the output is the safe answer anyone would give. The brief lacks the context and the bar that make it specific; rules alone describe the average ("short, accurate, no clickbait" returns "A Guide to Remote Team Productivity"). Add what only you know about this case, and name a reference that sets the bar.
- **Improvising where it must not**: a narrow bridge written as an open field. Add the schema or spell out the format, and have the recipient check its output against it.
- **Right direction, mediocre**: the recipient complies instead of trying. Rules turn the task into a checklist to satisfy, or material in context acts as a mold. Cut the rules down to the goal and the bar, and handle the material as **Material and references** describes.
- **Wrong focus**: the work centers on a minor part, converges where it should diverge, or does more than asked. A Chekhov's gun is firing: a mention that should not be there, or an emphatic instruction. Cut the mention, or state the instruction plainly with the condition for using it.

When a failure fits none of these, the intent or the facts were incomplete: return to step 1.

Fix the cause the entry names in the brief's wording, then take the revised brief through step 5. The fix is done when the output is what you needed.
