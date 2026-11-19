---
"agent-skills": patch
---

`full-auto` UAT waits for its turn with the new `scripts/uat-lock` (one UAT at a time per machine, in arrival order, once the load average is below 8) and attaches its evidence to the PR with `gh --attach`: one video or one screenshot in the PR body, the full report, trace, and other media in a comment.
