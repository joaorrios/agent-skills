---
"agent-skills": patch
---

`full-auto`'s `uat-lock` is the one queue for every local UAT and Electron test run: the new `uat-lock hold` holds the turn for an exact Electron session (released on stdin EOF, SIGTERM, or a crash), nested calls inside a turn pass through, the turn also waits for active GitHub Actions `Runner.Worker` jobs and out-of-queue Electron test processes, and `uat-lock status` shows the CI runner and each Electron test process with its owner.
