---
"agent-skills": patch
---

`full-auto` UAT splits findings into objective failures and decisions. The orchestrator fixes objective failures (a crash, an unhandled runtime or console error, a promised output that failed or holds wrong data, a promised action that plainly did not work) in a closed loop of at most 3 rounds of fix, push, and retest of the failed cases on the new head, and escalates any still reproducing. Subjective UX and product decisions stay unfixed and go to the user. The UAT report summarizes each failure the loop resolved, and testers record crashes and console errors verbatim.
