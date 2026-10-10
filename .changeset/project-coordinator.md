---
"agent-skills": minor
---

Add `project-coordinator`, a user-invoked skill that keeps one persistent coordinator per project: it delegates to workers, verifies and integrates their results, checkpoints its state in the repo, and reloads after compaction through a session-filtered hook for Claude Code and Codex.
