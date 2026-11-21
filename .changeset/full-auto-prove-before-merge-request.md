---
"agent-skills": patch
---

`full-auto` full stop now ends with the PR open for the user to request the merge, and every step the repo lets the agent take before that request done and proven. For a required check that runs only once a merge is requested, the agent runs its workflow's commands locally; the check itself stays pending until the merge is requested. Full send requests the merge, watches the merge-time validation until the PR is merged, and withdraws the request before pushing any correction. Screenshots and video of a user-facing change are uploaded so they render in the PR body, in the section the repo's PR template names for them, with one source for the `gh --attach` guidance.
