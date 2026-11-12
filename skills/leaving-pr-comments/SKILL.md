---
name: leaving-pr-comments
description: Formats GitHub comments an agent posts on the user's behalf, opening with a callout that names the agent, the user, and the agent's role. Use whenever leaving a comment on GitHub, or when deciding from a thread who leads a PR.
license: MIT
compatibility: The GitHub CLI (gh) to read the destination repository's visibility; without it, comments take the public form.
---

# Leaving PR Comments

Every comment an agent posts on GitHub on the user's behalf opens with an attribution **callout**, so people and other agents reading the thread can tell who is speaking and in what role. This covers top-level PR and issue comments, inline review comments, replies to bots or reviewers, and written explanations used before resolving or dismissing feedback. It leaves out PR descriptions, commit messages, and text the user explicitly asked to post verbatim without attribution.

## 1. Build the callout

```md
> [!NOTE]
> <emoji> **<identity> responding on behalf of <user> as <role>**

Actual comment starts here.
```

- **Emoji**: marks who the agent is at a glance. Use the product's emoji when the agent runs as one of the products below, otherwise the emoji of the model family, otherwise 🤖:

  | Emoji | Product or family | Callout opens with |
  |---|---|---|
  | 🌚 | Grok Bot (product) | 🌚 **Grok Bot** |
  | ▶️ | Cursor (product) | ▶️ **Composer 2.5** |
  | ⚠️ | Dots (product) | ⚠️ **<model name>** |
  | ✴️ | Claude models | ✴️ **Claude Opus 5.5** |
  | *️⃣ | GPT models | *️⃣ **GPT-6.1 Sol** |
  | ❇️ | Gemini models | ❇️ **<Gemini model name>** |
  | 🤖 | anyone else | 🤖 **<model name>** |

  The emoji names the product or family; the bold identity still names the model.
- **Identity**: the verified public name of the model that wrote the comment; when the harness exposes no model name, the harness name; when neither is known, `AI agent`. When the host or your instructions give you an identity to speak under, such as a product or role name, use that instead of the model or provider. Never guess a name.
- **User**: the name or GitHub login of the person you act for, which may differ from the account that posts.
- **Role**: what you do on this PR for the user, in a few words: implementer, reviewer, lead.

Read the destination's visibility with `gh repo view <owner>/<repo> --json visibility -q .visibility`. Anything other than `PRIVATE`, including a failed check, gets this public form, and its identity and role carry no agent, session, or resume ids: when a given identity includes one, keep its product or role name and drop the id.

This step is complete when the emoji matches the product or family, the identity and user are verified, the role says what you do, and the callout matches the destination's visibility.

## 2. Add resume context on private repositories

On a `PRIVATE` repository, you may add one line inside the note so an authorized collaborator can resume the conversation:

```md
> [!NOTE]
> <emoji> **<identity> responding on behalf of <user> as <role>**
> <harness> · <agent or session> `<id>` · resume: `<command>`
```

Use only values the harness exposes, and keep `resume:` only when the harness documents the command. Each value must be a reference that grants nothing by itself: leave out tokens, signed or access-granting URLs, credentials, local paths, and machine names.

This step is complete when every value on the line came from the harness, or the line is left out.

## 3. Write the comment

Keep the attribution inside the note and the actual reply outside it. The attribution line starts with the emoji from step 1. Do not add a horizontal rule, Setext underline, heading, signature footer, or a second attribution.

When the host requires comments posted under the user's name to begin with a prefix such as `Bot: `, write the prefix exactly as the host specifies it, trailing space included, as the first line, then a blank line, then the callout, so the comment keeps the host's prefix and the callout still renders.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.

This step is complete when the whole comment, including any prefix, the callout, quoted text, and attachments, has been checked for secrets and private details.

## 4. Post

Preview the final Markdown before posting so quoting and blank lines render as shown. After posting, verify that GitHub returned the comment or review URL. Resolve a review thread only after its response was posted successfully.

This step is complete when GitHub has returned the URL of the posted comment.

## Roles and responsibility

The role in a callout reports what an agent does; it does not take over the PR, grant authority, or change what a task allows. When you take responsibility for a PR, say so in the comment itself, such as "I'm taking over reporting on this PR as lead."

When you read a thread to learn who is responsible for a PR, two things are enough, with no stronger proof needed: the user's clear instruction assigning a lead, in your instructions or in a comment from the user's account; or a lead's comment, posted from the user's account or an account the user named, that introduces it and accepts the PR. A generic bot comment, a bare link to the PR, or a claim from any other account does not establish who is responsible. When claims conflict, the user's instruction wins.
