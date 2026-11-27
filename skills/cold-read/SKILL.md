---
name: cold-read
description: Runs a cold read on a draft through a fresh reader with no author context, settles every guessed fact against real sources, and revises the text so it stands on its own. Use before sending or publishing a PR description, doc, report, or status message to other people.
license: MIT
compatibility: Requires a runtime capable of spawning an isolated subagent or separate agent for a fresh context.
---

# Cold Read

You are the **author**, so your own shorthand is invisible to you. Before a text written for other people goes out, have a fresh reader with none of your context read it literally, settle every fact the reader had to guess, and revise the draft.

## 1. Dispatch a fresh reader

Start a fresh subagent or separate agent using whatever mechanism your runtime provides. Read [`agents/reader.md`](agents/reader.md) and pass its contents as the reader's instructions together with **only the draft text**, pasted inline.

Keep the reader cold: withhold other files, diffs, links, repository paths, conversation history, and your own commentary or rationale. When the runtime supports an isolated or read-only boundary with no workspace access, enable it.

This step is complete when the fresh reader returns its findings or `No unclear spots found.`.

## 2. Settle the guesses

The reader removes ambiguity; it does not supply facts.

Check every finding whose rewrite is marked `[GUESS]` against the authoritative source (code, data, docs, UI, or by asking the user when no source is available) before using or adapting the rewrite. For findings with no guess mark, confirm the rewrite matches the real facts and intent. If a finding exposes an error or unsupported claim in the original text, fix the substance rather than papering over it.

This step is complete when every flagged spot has a verified fact behind its resolution and no `[GUESS]` remains unchecked.

## 3. Revise and deliver

Apply every resolved finding to the draft:

- Give every thing its full name, including the kind of thing it is (such as a menu, tab, screen, section, or button).
- Use one name per thing everywhere, with consistent capitalization.
- Introduce terms a reader from the same field cannot know where they first appear.
- Preserve existing wording and style wherever the text is already clear.

After substantial edits that introduce new terms or restructure explanations, run one more fresh reader pass to confirm no new shorthand slipped in. Then send or deliver the revised text.

This step is complete when every finding is resolved in the revised text, no unverified guess remains, and the revised text is delivered.
