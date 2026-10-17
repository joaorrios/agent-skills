# Agent Skills

Portable skills for coding agents.

## Skills

- **approach-review** — challenges a proposed technical approach before implementation.
- **auditing-disk-space**: finds where disk space went on a Mac with measured evidence, then removes only the paths the user explicitly authorizes.
- **claude-instance-topology** — maps and safely changes how Claude Desktop and CLI instances on macOS share accounts, configuration, and history, including switching between accounts.
- **codex-image** — creates and edits images through the official Codex plugin, on request or autonomously as part of ongoing work, with Claude-owned art direction, acceptance, and integration.
- **dev-handoff**: hands a design or prototype to developers, choosing between an HTML handoff page built from Figma, real screens captured from a running build into annotated Figma, or both, with every unsettled item in a drafts table.
- **implementation-review** — inspects the technical aspects of a completed implementation before acceptance or shipping.
- **project-coordinator** — keeps one persistent coordinator per project that delegates to workers, verifies their results, and survives session changes and context compaction.
- **prompt-writing**: writes one-off prompts that ask a subagent, another agent, or another model for a specific output.
- **unhobble** — updates and simplifies context engineering for new, stronger models.

Each skill is independently installable and self-contained within its folder.

## Install

Install with the open Agent Skills CLI:

```bash
npx skills add joaorrios/agent-skills
```

Choose the skills you want when prompted. The CLI handles each supported coding agent's skill location.

```text
skills/
  approach-review/
    SKILL.md
    agents/
      intent-extractor.md
      intent-reviewer.md
      reviewer.md
  auditing-disk-space/
    SKILL.md
  claude-instance-topology/
    SKILL.md
    references/
    scripts/
  codex-image/
    SKILL.md
  dev-handoff/
    SKILL.md
    references/
  implementation-review/
    SKILL.md
    agents/
      reviewer.md
  project-coordinator/
    SKILL.md
    agents/
      openai.yaml
    references/
    scripts/
  prompt-writing/
    SKILL.md
    references/
  unhobble/
    SKILL.md
```

The two technical-review skills dispatch a fresh isolated reviewer using their bundled `agents/reviewer.md`; `approach-review` can also run an intent check with its extractor and intent reviewer. They work best in runtimes that can spawn an isolated subagent and optionally enforce a read-only boundary.

`codex-image` requires Claude Code with Agent and visual inspection, the `openai/codex-plugin-cc` plugin, and authenticated Codex with `image_gen` and access to the same files.

`project-coordinator` is invoked by the user only. It runs in Claude Code or Codex inside a git repository, and its reload hook needs a POSIX shell. Workers that outlive the coordinator's session need a runtime such as Paseo. In Cursor, Cursor Projects covers the same need.

`dev-handoff` reads and writes Figma through the Figma MCP server and needs a place to publish an HTML page the team can open. When the `design:design-handoff` skill is installed, it offers that checklist as a complement.

`auditing-disk-space` targets macOS. It measures completely only when the app or terminal running the agent has Full Disk Access.

`unhobble` requires access to read and edit the target material and an independent reviewer.

`claude-instance-topology` targets macOS with Claude Desktop and/or the Claude Code CLI. Its scripts need Python 3; the icon script also needs Pillow, and the menu bar plugin needs SwiftBar. It changes only where configuration and history live: every login goes through Anthropic's own sign-in flows in the unmodified apps, and it never reads, copies, or alters the credentials the apps store, in line with Anthropic's [terms for credential use](https://code.claude.com/docs/en/legal-and-compliance#authentication-and-credential-use).

## Technical review independence

The reviewer receives the artifact and coordinates needed to investigate the real system, not the author's reasoning, defenses, suspected weaknesses, or expected conclusions.

Written requirements and prior technical decisions are evidence of intent, not authority over technical correctness. A review may identify a defect even when the artifact faithfully follows what was written.

## Versioning

Agent Skills follows Semantic Versioning for the collection as a whole. Changesets records the intended bump for future changes:

```bash
npm run changeset
npm run version
```

Release tags use `vMAJOR.MINOR.PATCH`. Versioning is independent from installation: `npx skills` installs and updates skills from the repository, while SemVer tags and releases identify published collection states.

## License

MIT
