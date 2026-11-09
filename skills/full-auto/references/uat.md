# UAT without the user

How to run the UAT that the full-auto UAT gate requires. You are the **orchestrator**: you built the change, write the script, run the two testers, and classify what they report. The testers use the running app as a user would; neither reads code to decide whether the app works.

| Tester | Knows | Does |
|---|---|---|
| **Promise tester** | Only what the PR promises the user: the list of what changes for the user in the PR description | Explores the app on its own to see whether each promise holds; consults the app's help only when stuck |
| **Script tester** | Your step-by-step script | Follows it in order and gives each step a verdict |

The script tester proves your acceptance cases; the promise tester catches your blind spots: a wrong path in the script, wrong help, wrong copy. Neither alone is enough. Both get [`../agents/uat-tester.md`](../agents/uat-tester.md) as their instructions, plus their role and inputs.

## 1. Prepare

- **The build:** the exact head you will close out with, as a dev or local build, with an isolated profile or user-data directory so it neither touches nor conflicts with an installed copy. Record the commit for every report.
- **The fixture:** a small test project or data set with one section per promise item, so every promise has something to act on. Give each tester its own copy, so one tester's edits cannot contaminate the other's evidence.
- **The input tool for each promise item**, by what the item touches:

  | The item touches | Drive it with |
  |---|---|
  | Behavior inside the page or window: what appears, what gets written | Playwright for web apps, Electron QA (Playwright or CDP into the renderer) for Electron apps |
  | An OS surface: the menu bar, a context menu, a system shortcut, the clipboard filled by another app, focus and activation | Computer use, in an interactive terminal session; headless sessions cannot use it |
  | Esc where computer use reserves it, held-key auto-repeat, IME composition and dictation, human typing cadence, multi-instance setups | A person: put it on the human checklist |

  Synthetic input proves in-app logic but never passes through the OS; computer use proves OS routing but types faster than a person (about 0 ms between actions). Neither is evidence for what the third row lists.
- **The human checklist:** the promise items that map to the third row, if any, written now as a short list for the user, never discovered as BLOCKED at the end. A change none of whose items needs a person has no checklist.
- **Pre-flight**, when a tester will use computer use: the host of the terminal has Accessibility and Screen Recording and was restarted after the grant; computer use is enabled for the tester's project directory; a test screenshot is not blank; the display stays awake (on macOS, `caffeinate -d -i -u` for the whole run); nobody else is using the machine; only one computer-use session is open. When the OS asks for a consent only a person can give, that is a blocker for the computer-use items.

This step is complete when the build runs from the recorded commit, every promise item has a fixture section and an input tool, and the pre-flight passed for any computer-use item.

## 2. Write the script

Write the script tester's script: numbered steps, each with the acceptance case it proves, the physical action a user takes, the expected result, and the evidence to save. Then:

- **Define timing.** Replace "immediately" with a delay a person would produce, such as 150–300 ms, and mark each timing-sensitive step to be repeated at least five times.
- **Check the script against the app.** A script tester follows the script's mistakes faithfully, such as reaching a screen through a mode that deliberately hides what the step expects. Have someone other than you review the script, or run the promise tester first and fix the script where it took a wrong path.

This step is complete when every acceptance case of the change has a step, every step has an action, an expected result, and its evidence, and someone other than you checked the script or the promise tester has run.

## 3. Run the testers

- **Order:** the promise tester first, then the script tester. Run them one after the other whenever they share the screen; only one session can drive it.
- **Sessions:** start each tester in a fresh session with its final brief; a brief changed after launch reaches a session that already read the old one. Give each: [`../agents/uat-tester.md`](../agents/uat-tester.md), its role, the build and how to launch it, its fixture copy, the input tool for each item with that tool's known limits, the outputs it may observe as evidence (such as a file diffed against the commit noted before each step, or a record read back), and where to write its report. The promise tester gets the PR's list of what changes for the user exactly as published; the script tester gets the script.
- **Watching:** keep a watcher on each tester that wakes you on permission prompts, questions, and the report appearing, and that reports only new events. Answer the approval prompts a tool asks on first use. Close a finished computer-use session before starting the next one, or it keeps the screen.

This step is complete when both testers have written their reports, or a tester's run is recorded as blocked with the reason.

## 4. Classify every finding

Testers often report intended behavior as a bug. Before anything reaches the user, read the code, the docs, and both reports, and put each finding in one class:

- **Real bug:** the app breaks a promise.
- **Tool limit:** the input tool could not perform or observe the action.
- **Script error:** your script led the tester astray.
- **Decision:** the behavior is intended or a product choice, possibly one nobody has made yet.

Make each finding judgeable:

- **Counts:** reproduce it and give counts, such as "2 of 5"; one failure is an anecdote.
- **A control case:** the same intent through another path, such as the keyboard shortcut next to a failing menu item.
- **A native baseline** when the failure could be platform behavior: the same action in a minimal native app, at several delays, with numbers. Use real input events for it; scripted menu clicks skip what the OS does between click and action.
- **Corroboration:** a finding both testers reached independently is the strongest evidence; one only the script tester hit may be a script error.

Classification orders the findings; it does not settle them. Every finding still goes to the user, and none is fixed before the user confirms it.

This step is complete when every finding has a class, counts, and the evidence behind it.

## 5. Report to the user

Post the UAT result in the PR and put it in your final report, a run with no findings included:

- **What was tested:** the commit, the environment, each tester's input tool, and that tool's limits, so the user knows what a PASS does not cover.
- **Per-item tables:** verdict, the physical action, what was observed, and the evidence files.
- **Ground-truth evidence:** when the promise is about what the app writes (a file, a record, a request), that output compared with its state before each step; screenshots alone do not prove it.
- **Each finding** with its class, counts, control case, and evidence, explained from zero, step by step, in plain language: what the user does, what happens, what was expected.
- **The help log** from the promise tester: each help page consulted and whether it solved the problem.
- **The human checklist** of what only the user can check, when the change has one.

This step is complete when the result is posted in the PR and every finding, every BLOCKED or INCONCLUSIVE item, and every human-checklist item is in the questions for the user.

## 6. Clean up

Close the app under test, the tester sessions, the watchers, and anything keeping the display awake.

This step is complete when nothing started for UAT is still running.

## Retesting confirmed fixes in a later run

The user answers after the run ends, so fixing confirmed findings is new work for a later run, which goes through the full-auto steps again. Its UAT retests the failed and fixed cases with the same kind of tester, on the fixed commit, repeating timing-sensitive cases at least five times, instead of a full two-tester run, unless the fix changes what the user sees or does beyond those cases. Unit tests, E2E, and probes passing do not make a fix done; the retest does. Keep any automated test that comes out of a finding at the lowest layer that proves it.
