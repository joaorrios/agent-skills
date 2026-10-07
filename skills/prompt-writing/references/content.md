# What goes in a prompt

Write what only you know. Leave to the model what it can infer. A capable model infers conventions, formats, reasonable defaults, tone, and how to break down a task. It cannot infer facts about your product, your environment, or your domain that exist nowhere in its training data or its tools.

## Write what only you know

- **Product invariants**: rules true because someone decided them, not because they are generally sensible. Never move money without human approval; never quote a price without checking the live rate. The ones that read as obviously good practice matter most, because obviousness makes them look safe to leave out.
- **Environment facts**: which tool returns stale data, which API is rate-limited and how to back off, which integration returns `200` with an error in the body, which command is irreversible.
- **Domain meanings**: what your users mean by "closed", "settled", or "active" when the word means something else elsewhere. A general model gets local convention plausibly and confidently wrong.
- **The reason behind a choice**, when the model would otherwise optimize for the wrong thing.

For a candidate line, ask: could a competent new hire, given the tools and no other context, infer this? If they would have to be told, it goes in. When unsure, keep it: an extra line costs tokens, a missing invariant costs an incident.

## Leave to the model

- **Restated defaults.** "Be helpful", "think step by step", forced reasoning structures, and formatting scaffolds pay load to say nothing on a capable model.
- **Caps for behaviour the runner does not show.** A rule like "never write multi-paragraph docstrings, one short line max" existed because a weaker model wrote too many comments. For a model that reads the surrounding code, "match the comment density, naming, and idiom of the surrounding code" says more and handles more.
- **Examples of how to act or where to look.** They pull the model toward the cases shown and away from the ones you missed. Give the goal, the full scope, and the completion criterion instead.
- **Drafts as input.** A draft, mockup, or sample in context becomes the template, however the prompt frames it. When the model should invent, pass the facts and constraints the draft holds, not the draft.
- **Taste carried by examples.** Rules describe the generic average: "short, accurate, no clickbait" returns "A Guide to Remote Team Productivity". State the bar in words first ("specific, with a hook a reader would click: a concrete moment or a surprising claim"). Add a contrasting weak and strong pair only when words fail to convey the bar, and vary it so no single example becomes the template.

## Put each piece where it acts

- **Tool descriptions.** A rule about using a tool lives in that tool's description, next to the decision it governs and loaded whenever the tool is. Leave it out of the system prompt.
- **Pointers over copies.** When the runner can open a file, spec, or page, give the path and say what it holds and when to read it. A pasted or paraphrased copy goes stale and spends attention on every run.
- **Disclosure.** Material only some cases need (one workflow, a rare integration, a specialized procedure) sits behind a pointer that names the condition for reading it. What every case needs stays in the prompt.

## Density tracks the runner

How much scaffolding a prompt needs depends on how much judgment the runner can supply on its own. A flagship model infers convention, resolves ambiguity, and stops on its own. A small, fast model running classification, routing, or extraction has less room to do any of that, and terseness that reads as trust to a flagship reads as ambiguity to it.

For a small or fast runner, move more of the task onto the narrow bridge:

- Spell out the steps in order.
- Give a strict output template, plus three to five varied format examples when no schema can enforce the shape.
- State the decision criteria that a flagship would infer, such as how to break a tie or what counts as out of scope.
- Have it check its output against the template before answering.

Treat the prompt and its model as a pair. A prompt written for one tier or generation fits another only after you refit its density, in either direction.
