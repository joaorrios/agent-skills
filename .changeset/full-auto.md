---
"agent-skills": minor
---

Add `full-auto`, a skill that takes a change end to end while the user is away and forks at the end: "full send" merges the PR, "full stop" hands it off ready for the user to merge. Both share proof for every change, review and PR tending with the skills available, a merge gate, pending blockers that hold back only the work depending on them, recorded product forks, and one round of questions at the end. Adapted from tstack's `full-send` and `full-stop`. A UAT gate requires agent-run user acceptance testing for changes the user can see or use, reports every result to the user, leaves findings unfixed until the user confirms them, and switches full send to full stop when the user must look.
