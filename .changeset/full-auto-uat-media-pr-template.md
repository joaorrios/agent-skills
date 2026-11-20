---
"agent-skills": patch
---

`full-auto` leaves UAT media to the repo's PR template: the skill says once, under the product validation gate, that the media in the PR follow that template, and `references/uat.md` points there instead of restating upload steps and `gh --attach` flags. `references/uat.md` also points to "Result" for what happens to findings and to "Later runs" for when a retest happens, keeping only how to classify findings and how a retest runs.
