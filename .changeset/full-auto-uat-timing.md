---
"agent-skills": patch
---

`full-auto` runs UAT once at the end of a batch of work, when the PR is back to ready to merge, instead of after every push. It never reruns UAT for a small change, and after rework it asks the user whether to look directly or rerun UAT.
