---
"agent-skills": minor
---

`project-coordinator` keeps in the state only what live data cannot show and updates each row as its worker's result arrives; adds "Workers", "With you" and "Approvals" to the state; ends each worker report with a `DELIVERED` or `STOPPED` line and investigates silent workers a runtime or dashboard flags; asks who depends on a one-way step; calls work live only after a readback; checks that an old coordinator is gone before taking over; keeps the state under the reload hook's budget, which now names the files instead of overflowing; and fixes the state-move steps.
