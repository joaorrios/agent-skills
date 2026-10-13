# Brief content

Write what only you know. Leave to the runner what it can infer: a capable model infers conventions, formats, reasonable defaults, tone, and how to break down a task. Restated defaults such as "be helpful", "think step by step", forced reasoning structures, and formatting scaffolds pay load to say nothing.

## Write what only you know

- **The user's intent**: what they asked for, why, and what they rejected along the way.
- **What the work established**: decisions already made, findings, and dead ends the runner would otherwise retrace.
- **Invariants**: rules true because someone decided them, not because they are generally sensible. Work only in this worktree; confirm before anything visible to others. The ones that read as obviously good practice matter most, because obviousness makes them look safe to leave out.
- **Environment facts**: which tool returns stale data, which API is rate-limited and how to back off, which integration returns `200` with an error in the body, which command is irreversible.
- **Domain meanings**: what the user means by "closed", "settled", or "active" when the word means something else elsewhere. A general model gets local convention plausibly and confidently wrong.

For a candidate line, ask: could a competent new hire, given the tools and no other context, infer this? If they would have to be told, it goes in.

## Small runners

How much scaffolding a brief needs depends on how much judgment the runner supplies on its own. A highly capable model infers convention, resolves ambiguity, and stops on its own. A small, fast model running classification, routing, or extraction has less room to do any of that, and terseness that reads as trust to a capable model reads as ambiguity to it.

For a small or fast runner, move more of the task onto the narrow bridge:

- Spell out the steps in order.
- Spell out the output format, with varied examples when no schema can enforce it.
- State the decision criteria a more capable model would infer, such as how to break a tie or what counts as out of scope.
- Have it check its output against the format before answering.
