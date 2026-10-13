---
name: prompt-writing
description: Writes prompts that drive a model, such as system prompts, subagent briefs, tool descriptions, and prompt templates. Use when writing one, or when one produces the wrong output.
license: MIT
---

# Prompt Writing

A prompt gives a capable model the goal, the context it lacks, and the real constraints, then leaves the rest to its judgment. Aim for the smallest set of high-signal tokens that gets the output you want.

Scale the steps to how long the prompt lives and what rides on it. A system prompt, template, or tool description runs many times: take each step in full. A one-off brief in the middle of a task takes the same steps in moments, from the intent you already hold. When a prompt produces the wrong output, go to [When the output is wrong](#when-the-output-is-wrong).

## 1. Recover the intent

Establish:

- **Goal**: what the output is for and who consumes it next (a person, a parser, a parent agent).
- **Runner**: the model that will run the prompt, its tier, its tools, and what it loads into context on its own.
- **What only you know**: facts the runner cannot infer from training or from its tools, such as product invariants, environment quirks, what common words mean in this domain, and the reason behind a choice.
- **Done**: what a finished output looks like, stated so the model can tell done from not done.

When the runner is a model generation you have not prompted before, read its provider's prompting guide for how it differs from earlier ones.

Ask the user for anything that would change the prompt and that neither you nor the material at hand holds.

This step is complete when you know the runner, can state the goal, what only you know, and done in a few lines, and no open question would change the prompt.

## 2. Zone the freedom

Decide how much latitude each part of the task gets, by how fragile it is:

- **Open field**: several outputs are valid and quality is a judgment call (grouping, generation, copywriting, research, rating). Give the goal, the bar, and the context; trust the model to find the route.
- **Narrow bridge**: one output is correct and a small error breaks it (schemas, data formats, migrations, API calls, irreversible actions). Give exact steps and a fixed output shape.

Carry a fixed shape in an **interface** whenever one exists: a JSON schema, an enum, a typed tool parameter, a script. `status: "pending" | "in_progress" | "completed"` teaches the values without one example and cannot drift from the code. When no interface can carry the shape, spell the format out in the prompt.

Most prompts mix both. An agent prompt leaves the approach open and locks the tool-call format; a generation task leaves the content open and locks the output schema. Zone each part rather than picking one mode for the whole prompt. Writing an open field in narrow-bridge language collapses the output to the generic average; writing a narrow bridge in open-field language invites improvisation where it breaks things.

Calibrate the zones to the runner: the less capable the model, the more of the task becomes narrow bridge. When the runner is a small or fast model, read [`references/content.md`](references/content.md#small-runners). The prompt and its runner are a pair: a new runner, stronger or weaker, means refitting the zones.

This step is complete when every part of the task is marked open field or narrow bridge and every narrow-bridge part has its interface or spelled-out format.

## 3. Draft

For a prompt that runs many times, decide what earns a place and where each piece lives with [`references/content.md`](references/content.md); it also covers what templates and tool descriptions must carry.

Write the open-field parts at the right **altitude**: specific enough to guide, general enough to leave the model strong heuristics. Too low hardcodes brittle logic ("if the title contains a colon, split on it and capitalize the second half"). Too high gives no signal ("write good titles"). Between them: "make titles specific and punchy over comprehensive." Write the narrow-bridge parts as exact steps with their interface or format.

- **Intent over enumeration.** State the principle once and let the model handle the cases. "Match the register to the situation" covers the fifth case that four if-clauses miss.
- **Reasons with constraints.** A constraint with its why generalizes to cases you did not list. "The response is read aloud by a text-to-speech engine, so write out symbols" beats "never use ellipses".
- **Chekhov's gun.** The model treats everything in the prompt as something it is meant to use: a mentioned edge case gets handled, a named tool gets called, a detail mentioned in passing becomes the focus, and parallel runs given the same detail converge on it. Include only what should fire, and cut details that give a concern more weight than the user's intent calls for. Emphasis works the same way: CRITICAL and MUST make capable models overtrigger, so state a real constraint plainly with its reason.
- **Positive targets.** Say what to do. A prohibition puts the banned behaviour on stage too. Keep one only as a hard guardrail you cannot phrase positively, and pair it with the target behaviour.
- **Examples.** The model leans toward the cases shown. In place of examples of how to act or where to look, give the goal, the full scope, and the completion criterion. For a quality bar, state it in words first, and add one contrasting weak and strong pair when the words do not move the output. For an output shape no interface can carry, give three to five varied examples.
- **Material as input.** A draft, mockup, or sample in context becomes a **mold** the output copies, however the prompt frames it. When the model should invent, pass the facts and constraints the material holds instead. When the task works on the material itself (review it, edit it, follow it), point to it.
- **Bounded demands.** Every superlative (best, all, every, until perfect) gets a stopping condition. The strongest completion criteria are both checkable and exhaustive: "every changed endpoint has a test" rather than "test thoroughly".
- **Explicit action and scope.** Capable models follow instructions literally: "suggest changes" gets suggestions. Say whether to act or advise, how far the work extends, and ask explicitly for work beyond the basics when you want it.
- **Current state.** Derive each rule from the current intent and the risks this task carries for this runner. A past mistake earns a line only if the same risk is live in this task.
- **Matching form.** The prompt's own format tends to come back in the output; write the prompt in the form you want back.

### Briefs

A **brief** is the prompt for a subagent or another agent you hand work to. It carries what the runner cannot see:

- The goal and why it matters, the coordinates to the real material (paths, URLs, ids, branches), the constraints, and what is already done.
- The rules the runner will not load on its own: instructions from the conversation, from skills you loaded, and confirmations given for this task. Instruction files the runner loads itself stay out.
- What to return and in what shape, since you consume the result.

When you want an independent judgment, keep the brief **unprimed**: give the artifact and the coordinates, and keep your conclusions, suspicions, and preferred answer out.

This step is complete when the goal, what only you know, and done each appear once in the draft, and every part is written as its zone calls for.

## 4. Check the draft

Read the draft line by line. Each line follows the step 3 rules and either changes behaviour against the runner's default or carries something only you know. Keep a line when unsure whether it carries something only you know; delete a whole sentence that fails rather than trimming words.

Then check how the draft reads without your context. For a prompt that runs many times or carries high stakes, dispatch a subagent, on the runner's model when you can, give it only the draft, unprimed, and ask how it understands the task and what it would do, without doing it. Compare that reading with the intent from step 1 and fix where they diverge. Trust the fresh reading over your own sense of ambiguity: the author tends to find ambiguity a fresh reader resolves. For a one-off brief, read the draft yourself as the runner would, with only this prompt and its tools.

This step is complete when every line passes, nothing only you know was cut, and a reading without your context matches the intent.

## When the output is wrong

Get a failing output in hand before changing anything. Most failures are a misfit you can read off the zones:

- **Generic average**: the output is the safe answer anyone would give. The prompt lacks the context and the bar that make it specific; rules alone describe the average ("short, accurate, no clickbait" returns "A Guide to Remote Team Productivity"). Add what only you know about this case, state the bar, and add a contrasting pair if the bar in words does not move the output.
- **Improvising where it must not**: a narrow bridge written as an open field. Add the interface or spell out the format, and have the model check its output against it.
- **Right direction, mediocre**: the model complies instead of trying. Rules turn the task into a checklist to satisfy, or material in context acts as a mold. Cut the rules down to the goal and the bar, and handle the material as **Material as input** describes.
- **Wrong focus**: the work centers on a minor part, converges where it should diverge, or does more than asked. A Chekhov's gun is firing: a mention that should not be there, or an emphatic instruction. Cut the mention, or state the instruction plainly with the condition for using it.

When a failure fits none of these, the intent or the facts were incomplete: return to step 1.

Fix the cause the entry names in the prompt's wording, rather than adding a clause for the failing input. The fix is done when the failing input gives the intended output and an input that used to work still does.
