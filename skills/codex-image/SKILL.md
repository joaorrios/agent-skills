---
name: codex-image
description: "Images via Codex. Use to create or edit requested images, or when generated images would benefit the work in progress, individually or as a set."
license: MIT
compatibility: "Claude Code with Agent, visual inspection, and the openai/codex-plugin-cc plugin; authenticated Codex with image_gen and file access in the same environment."
---

# Codex Image

Claude owns art direction, acceptance, and integration; Codex produces the images.

## Autonomy

Plan and produce the images needed for the current work, including sets and refinements, without per-call approval. User-defined limits and gates take precedence; changing providers, billing, or permissions requires authorization.

## 1. Brief

Transfer intent, not the entire conversation. Codex needs the intended visual result, the constraints that define it, and the destination of each image. Preserve the established direction; take ownership of creative choices that remain open.

Provide references as files accessible to Codex, with absolute paths and explicit roles: edit target, content, or art direction. Attachments in the Claude chat are not inherited automatically.

For sets, establish a shared direction and a distinct role for each image.

**Ready to produce:** each image has an actionable brief that requires no implicit context, and the visual intent is specific enough to guide selection among results that satisfy the same content requirements.

## 2. Production

In the main conversation, call `Agent` with `subagent_type: "codex:codex-rescue"`, in the foreground. Place `--fresh --wait` before the brief, without forwarding `--wait` to the internal `task` command. This target is a subagent, not a skill: calling `Skill(codex:rescue)` re-enters the command. Model and reasoning effort follow the Codex configuration unless the user explicitly chooses otherwise.

Forward the brief and this contract to **Codex** through the subagent:

> Use your `imagegen` skill with the native `image_gen` tool. Save each image in its own file in the workspace and record its associated final prompt. Limit changes to the images and that record; Claude owns integration. Return absolute paths and any blockers.

Group independent images into one delegation. If the direction is uncertain, produce one representative image first and take it through acceptance before expanding the set. For an edit, forward the selected file and the intended change; `--fresh` avoids relying on the latest thread from another task.

**Outputs received:** the returned files are available for Claude to inspect. A task still in progress or an empty response remains pending.

## 3. Acceptance and delivery

Claude owns acceptance, based on viewing the produced images — not on Codex's success report.

**Accepted when:** the image fulfills the request and supports the work's art direction. The composition must serve the visual intent, the finish must meet the standard set by the quality references, and the image must work for its intended use. Meeting content and format requirements does not compensate for a weak visual solution. Without references, Claude sets the editorial bar from the purpose and context.

Autonomously refine anything that fails acceptance, preserving what already works. Each new call must address an identified defect or explore a deliberate visual alternative. Mark the item as blocked when there is no plausible next intervention; preserve the best result and the unresolved issue without treating them as acceptance.

When the image is the deliverable, present the selected version. When it is an asset for another deliverable, incorporate it into the artifact in the requested format and assess acceptance in that application. The primary work remains the requested artifact, not an image representing it.

**Complete when:** all necessary images have passed aesthetic and functional acceptance, are available at their final destinations with their prompts recorded, and have been delivered individually or integrated. Blocked items make the delivery partial, with the unresolved issue stated explicitly.
