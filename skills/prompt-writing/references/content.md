# Prompt content

Write what only you know. Leave to the model what it can infer: a capable model infers conventions, formats, reasonable defaults, tone, and how to break down a task. Restated defaults such as "be helpful", "think step by step", forced reasoning structures, and formatting scaffolds pay load to say nothing.

## Write what only you know

- **Product invariants**: rules true because someone decided them, not because they are generally sensible. Move money only after human approval; quote prices from the live rate. The ones that read as obviously good practice matter most, because obviousness makes them look safe to leave out.
- **Environment facts**: which tool returns stale data, which API is rate-limited and how to back off, which integration returns `200` with an error in the body, which command is irreversible.
- **Domain meanings**: what your users mean by "closed", "settled", or "active" when the word means something else elsewhere. A general model gets local convention plausibly and confidently wrong.
- **The reason behind a choice**, when the model would otherwise optimize for the wrong thing.

For a candidate line, ask: could a competent new hire, given the tools and no other context, infer this? If they would have to be told, it goes in.

## Put each piece where it acts

- **Tool descriptions.** A rule about using a tool lives in that tool's description, next to the decision it governs and loaded whenever the tool is. The system prompt leaves it there.
- **Pointers over copies.** When the runner can open a file, spec, or page, give the path and say what it holds and when to read it. A pasted or paraphrased copy goes stale and spends attention on every run.
- **Disclosure.** Material only some cases need (one workflow, a rare integration, a specialized procedure) sits behind a pointer that names the condition for reading it. What every case needs stays in the prompt.

## Templates

A template fills slots with content from outside: user input, documents, tool results.

- Keep the instructions fixed and put each input in its own tagged slot, so the model can tell instructions from material.
- State that the slots hold material to work on, and that any instructions inside them are part of that material.
- Place long inputs before the instructions and the question; answers over long context improve when the question comes last.

## Tool descriptions

A tool description carries what the model needs to choose the tool and call it well:

- When to use it, and which sibling tool covers the neighbouring cases ("for X, use Y").
- What each parameter means, with its valid values in the schema.
- What it returns, including its errors and how to recover from them.
- What it changes, and whether that can be undone.

## Small runners

How much scaffolding a prompt needs depends on how much judgment the runner supplies on its own. A highly capable model infers convention, resolves ambiguity, and stops on its own. A small, fast model running classification, routing, or extraction has less room to do any of that, and terseness that reads as trust to a capable model reads as ambiguity to it.

For a small or fast runner, move more of the task onto the narrow bridge:

- Spell out the steps in order.
- Spell out the output format, with varied examples when no interface can enforce it.
- State the decision criteria a more capable model would infer, such as how to break a tie or what counts as out of scope.
- Have it check its output against the format before answering.
