---
"agent-skills": minor
---

`uat-lock` closes every Electron test process started during a turn when the turn ends, however it ends, and the head of the queue closes orphaned Electron test processes instead of waiting on them forever.
