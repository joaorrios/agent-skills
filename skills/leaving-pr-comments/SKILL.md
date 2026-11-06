---
name: leaving-pr-comments
description: Formats GitHub comments an agent posts on the user's behalf, opening with a callout that names the agent, the user, and the agent's role. Use whenever leaving a comment on GitHub.
license: MIT
compatibility: An authenticated GitHub CLI (gh) to read the destination repository's visibility and to post.
---

# Leaving PR Comments

Every comment an agent posts on the user's behalf opens with an attribution **callout**, so people and other agents reading the thread can tell who is speaking and in what role.

## 1. Build the callout

```md
> [!NOTE]
> 🤖 **<identity> responding on behalf of <user> as <role>**

Actual comment starts here.
```

- **Identity**: the verified public name of the model that wrote the comment; when the harness exposes no model name, the harness name. When the host or your instructions give you an identity to speak under, such as a product or role name, use that instead of the model or provider. Use only names you can verify.
- **User**: the user's name or GitHub login.
- **Role**: what you do on this PR for the user, in a few words: implementer, reviewer, lead.

The role reports what you do; it does not take over the PR, grant authority, or change what your task allows. When you take responsibility for a PR, say so in the comment itself, such as "I'm taking over reporting on this PR as lead." When you read a thread, a user's clear instruction assigning a lead, or a lead's comment introducing itself and accepting the PR, is enough to know who is responsible; a generic bot comment or a bare link to the PR is not, and no stronger proof is needed.

This step is complete when every placeholder holds a verified value.

## 2. Add resume context on private repositories

Read the destination's visibility with `gh repo view <owner>/<repo> --json visibility -q .visibility`. Anything other than `PRIVATE`, including a failed check, gets the callout from step 1 as is.

On a `PRIVATE` repository, you may add one line inside the note naming the harness or environment and the agent or session id, so an authorized collaborator can resume the conversation:

```md
> [!NOTE]
> 🤖 **<identity> responding on behalf of <user> as <role>**
> <harness> · session `<id>`
```

Use only values the harness exposes, and add a resume command only when the harness documents one. Each value must be a reference that grants nothing by itself: leave out tokens, signed or access-granting URLs, credentials, local paths, and machine names.

This step is complete when the callout matches the destination's visibility.

## 3. Write the comment

Before posting, check the entire comment, including quoted text and attachments, for secrets and private details.

Keep the attribution inside the note and the actual reply outside it. The attribution line starts with the robot emoji. Do not add a horizontal rule, Setext underline, heading, signature footer, or a second attribution.

When the host requires comments posted under the user's name to begin with a prefix such as `Bot:`, put the prefix alone on the first line, then a blank line, then the callout, so the comment keeps the host's prefix and the callout still renders.

Apply this format to top-level PR comments, inline review comments, replies to bots or reviewers, and written explanations used before resolving or dismissing feedback. Do not add it to PR descriptions, commit messages, or text the user explicitly asked to post verbatim without attribution.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.

## 4. Post

Preview the final Markdown before posting so quoting and blank lines render as shown. After posting, verify that GitHub returned the comment or review URL. Resolve a review thread only after its response was posted successfully.

This step is complete when GitHub has returned the URL of the posted comment.
