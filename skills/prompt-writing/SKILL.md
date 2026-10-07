---
name: prompt-writing
description: Writes prompts that drive a model, from system prompts and subagent briefs to task prompts, templates, and tool descriptions. Use when writing a prompt for a model or when a prompt you wrote produces the wrong output.
license: MIT
---

# Prompt Writing

A prompt gives a capable model the goal, the context it lacks, and the real constraints, then leaves the rest to its judgment. Aim for the smallest set of high-signal tokens that gets the output you want. Everything you write directs the model's attention, and every rule narrows its output to the range of cases you happened to think of.

## 1. Recover the intent

Establish:

- **Goal**: what the output is for and who consumes it next (a person, a parser, a parent agent).
- **Runner**: the model that will run the prompt, its tier, its tools, and what it already has in context. A subagent starts with nothing you have not written into its brief.
- **What only you know**: facts the model cannot infer from training or from its tools. [`references/content.md`](references/content.md#write-what-only-you-know) lists the kinds and the test for deciding.
- **Done**: what a finished output looks like, stated so the model can tell done from not done.

When the runner has its own prompting guide from its provider, read it for the behaviours that differ from its predecessors.

Ask the user for anything that would change the prompt and that you cannot find.

This step is complete when you can state all four in a few lines and no open question would change the prompt.

## 2. Zone the freedom

Decide how much latitude each part of the task gets, by how fragile it is:

- **Open field**: several outputs are valid and quality is a judgment call (grouping, generation, copywriting, research, rating). Give the goal, the bar, and the context; trust the model to find the route.
- **Narrow bridge**: one output is correct and a small error breaks it (schemas, data formats, migrations, API calls, irreversible actions). Give exact steps and a strict shape.

Carry a narrow bridge in an **interface** whenever one exists: a JSON schema, an enum, a typed tool parameter, a script. `status: "pending" | "in_progress" | "completed"` teaches the values without one example and cannot drift from the code; prose rules and format examples are the fallback when no interface can carry the shape.

Most prompts mix both. An agent prompt leaves the approach open and locks the tool-call format; a generation task leaves the content open and locks the output schema. Zone each part rather than picking one mode for the whole prompt. Writing an open field in narrow-bridge language collapses the output to the generic average; writing a narrow bridge in open-field language invites improvisation where it breaks things.

Calibrate the zones to the runner: the less capable the model, the more of the task becomes narrow bridge. See [`references/content.md`](references/content.md#density-tracks-the-runner) when the runner is a small or fast model.

This step is complete when every part of the task is marked open field or narrow bridge and every narrow-bridge part has its interface or template.

## 3. Draft

Decide what earns a place and where each piece lives with [`references/content.md`](references/content.md). Then write at the right **altitude**: specific enough to guide, general enough to leave the model strong heuristics. Too low hardcodes brittle logic ("if the title contains a colon, split on it and capitalize the second half"). Too high gives no signal ("write good titles"). Between them: "make titles specific and punchy over comprehensive."

- **Intent over enumeration.** State the principle once and let the model handle the cases. "Match the register to the situation" covers the fifth case that four if-clauses miss.
- **Reasons with constraints.** A constraint with its why generalizes to cases you did not list. "The response is read aloud by a text-to-speech engine, so write out symbols" beats "never use ellipses".
- **Chekhov's gun.** The model treats everything in the prompt as something it is meant to use: a mentioned edge case gets handled, a named tool gets called, a detail mentioned in passing becomes the focus, and parallel runs given the same detail converge on it. Include only what should fire, and cut details that give a concern more weight than the user's intent calls for. Emphasis works the same way: CRITICAL and MUST make capable models overtrigger, so state a real constraint plainly with its reason.
- **Positive targets.** Say what to do. A prohibition puts the banned behaviour on stage too. Keep one only as a hard guardrail you cannot phrase positively, and pair it with the target behaviour.
- **Bounded demands.** Every superlative (best, all, every, until perfect) gets a stopping condition. The strongest completion criteria are both checkable and exhaustive: "every changed endpoint has a test" rather than "test thoroughly".
- **Explicit action and scope.** Current models follow instructions literally: "suggest changes" gets suggestions. Say whether to act or advise, how far the work extends, and ask explicitly for work beyond the basics when you want it.
- **Current state.** Derive each rule from the current intent and the risks this task carries for this runner. A past mistake earns a line only if the same risk is live in this task.
- **Matching form.** The prompt's own format tends to come back in the output. When a prompt mixes instructions, context, examples, and inputs, wrap each kind in its own tag.

### Briefs

A **brief** is the prompt for a subagent or another agent you hand work to. It carries what the runner cannot see:

- The goal and why it matters, the coordinates to the real material (paths, URLs, ids, branches), the constraints, and what is already done.
- The standing rules from your own instructions that also bind the work, such as cleanup duties or actions that need confirmation. The runner does not see your instructions.
- What to return and in what shape, since you consume the result.

When you want an independent judgment, keep the brief **unprimed**: give the artifact and the coordinates, and keep your conclusions, suspicions, and preferred answer out.

This step is complete when every item from step 1 appears in the draft once, at the altitude its zone calls for.

## 4. Check the draft

Read the draft line by line. Each line must change behaviour against the runner's default or carry something only you know; delete a whole sentence that fails rather than trimming words.

Then check how the draft reads without your context. When you can dispatch a subagent, give it only the draft, unprimed, and ask how it understands the task and what it would do, without doing it. Compare that reading with the intent from step 1 and fix where they diverge. Trust the fresh reading over your own sense of ambiguity: the author tends to find ambiguity a fresh reader resolves. Without a subagent, read the draft as the runner would, with only this prompt and its tools.

This step is complete when every line passes, nothing only you know was cut, and a reading without your context matches the intent.

## When the output is wrong

Get a failing output in hand before changing anything. Most failures are a misfit you can read off the zones:

- **Generic average**: an open field strangled by rules or examples, or starved of the context that makes it specific. Delete rules, state the goal and the bar, and add what only you know about this case.
- **Improvising where it must not**: a narrow bridge written as an open field. Add the interface or template, and have the model check its output against it.
- **Right direction, mediocre**: the model complies instead of trying. Rules turn the task into a checklist to satisfy, and material in context (a draft, a sample, a reference) becomes the template, whatever the prompt says about using it only as input. Cut the rules down to the goal and the bar, and pass the facts the material holds rather than the material itself.
- **Wrong focus**: the work centers on a minor part, converges where it should diverge, or does more than asked. A Chekhov's gun is firing: a mention that should not be there, or an emphatic instruction. Cut the mention, or state the instruction plainly with the condition for using it.

Fix narrowly: change the one thing that handles the failing case. Re-run the failing input and one that used to work.
