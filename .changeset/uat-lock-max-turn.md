---
"agent-skills": minor
---

`uat-lock` limits a turn to `UAT_LOCK_MAX_TURN` minutes (default 90): past that, the head of the queue stops the holder, even one whose session is alive but hung, and the holder closes its Electron as it ends. `uat-lock status` shows each turn's age against the limit.
