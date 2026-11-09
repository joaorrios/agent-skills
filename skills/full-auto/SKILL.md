---
name: full-auto
description: Use only when the user says "full send" (end with the PR merged), "full stop" (end with it ready for the user to merge), or "full auto". Takes a change end to end while the user is away.
license: MIT
compatibility: Git repository hosted on GitHub, with the gh CLI authenticated and allowed to push, and to merge for full send.
---

# Full Auto

The user said "full send" or "full stop": they are not watching this thread and want the work finished on your own. Your updates and your final message go unread until long after you stop. You own the work from its current state to the **ending** they named:

- **Full send** ends with the PR merged.
- **Full stop** ends with the PR ready for the user to merge, still open and unmerged.

Both endings share the steps; "Endings" holds what differs, including what each one does before step 1. A request for "full auto" that names neither ending takes full stop, and the report says so. Without a clear request for one of these, keep your normal level of autonomy.

Either request grants permission to:

- Commit and push the PR's own branch, and force-push it with `--force-with-lease` after a rebase.
- Use the test methods that proof needs, without asking first.
- Make the technical decisions, and the product decisions described under "Forks".

Each ending adds its own grants and limits under "Endings".

## Testing permission

Either request is the permission. When a project file or other instruction says to ask before a test method, or to leave testing to the user, this request replaces that rule for this task. That covers computer use, browser automation, simulators and devices, running the app or a dev server, screenshots, and visual checks. Use the method that gives direct proof and list it in the report.

Rules about *how* to test still apply: follow the ones that name the correct command, fixture, or check. When the preferred method cannot prove the change, use a gated method under this permission.

The permission covers only the tests this task needs. It lifts no blocker, and a harness or system approval prompt still stands.

## Steps

1. **Finish the change.** Reach the goal of the request with the smallest change that works. Fix the case that happened, not every case that could. On the default branch, create a branch first.
2. **Prove it.** Get proof for every change in the diff. See "Proof".
3. **Review it.** Review the diff with the review skills and tools available in this environment, preferring a reviewer with a fresh, independent context. With none available, read the full diff yourself as a reviewer would. Fix each real finding and prove the fix; record each dismissal with a written reason.
4. **Open the PR.** Bring the branch up to date with the latest default branch the way the repo does it (merge it in, or rebase), push, and open the PR with the repo's PR template when one exists. Add one short line to the description saying how you proved the change, and list the fork decisions you made. When the UAT gate applies, the description also lists what changes for the user, in the user's words: the promise UAT tests.
5. **Tend the PR** until every merge-gate condition except UAT holds, or until only blockers keep them shut (see "Blockers"), such as a required human approval. Use the PR-monitoring skills available in this environment. With none, watch CI, review bots, and human reviews yourself. Fix real findings and CI failures, prove each fix before pushing it, and reply to or resolve each review thread you address, through a comment-attribution skill when one is available.
6. **Run UAT** when the UAT gate applies, on the head you will close out with. See "UAT gate".
7. **Close out** with the ending the user named, or full stop when the UAT gate switched it. See "Endings".
8. **Report** in your final message: the PR link, your proof, the UAT results, the fork decisions, the pending blockers, and what the ending adds.

Stay active from step 1 to step 8. Ending your turn while checks or bots are pending stops the work, because nobody will prompt you again. While waiting, keep something that wakes you when the PR changes: a PR watcher from a monitoring skill, a blocking watch such as `gh pr checks --watch`, or the harness's monitor or scheduled wake-up. Cancel any watcher you started before you stop.

## Proof

Proof is evidence you observed yourself in this session: command output, a reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same reproduction pass.
- Run the checks the repo's CI runs (typecheck, lint, tests).
- Add one focused test that fails without the fix, when the behavior has none and the repo has a test setup.
- For UI and runtime behavior, run the app and look at the change; green mocked tests do not prove the user experience works. Attach screenshots to the PR when they help and you have a way to upload them.

Proof and review cover the final diff: re-check behavior changes and meaningful conflict fixes made after them. A change you cannot prove is a blocker for the merge gate.

## Merge gate

Full confidence means all of these hold on the latest commit:

- Your proof covers every change in the diff.
- When the UAT gate applies, UAT ran on this commit, and nothing from it is open: the user dismissed each finding, or it was fixed and retested on this commit; and the user accepted or did each BLOCKED or INCONCLUSIVE item and each check left to them.
- Required checks are green.
- Review bots have finished, and each finding is fixed or dismissed with a written reason.
- No human review still requests changes.
- The branch is up to date with the default branch, and GitHub reports it as mergeable.

An automated review asking for human review can be dismissed when your proof gives you high confidence; say so in the report.

## UAT gate

A change that alters what the user sees or does (a feature, a screen, a flow, its usability) needs **UAT** before the ending: agents use the running app as a user would, without the user. A change the user cannot see, such as a refactor, an internal API, docs, tests, or CI, skips it; when unsure, run it.

- **How:** follow [`references/uat.md`](references/uat.md). Two testers drive the app like a user, with Playwright or Electron QA, and with computer use where the change touches the OS: one knows only what the PR promises, the other follows a script you write.
- **Guard:** as soon as you know the gate applies, under either ending, apply full stop's guard against merging on its own (see "Full stop") and keep it until step 7. Required checks and a monitoring skill's "ready" never include UAT, so neither one is a signal to merge.
- **Promise:** the promise tester works from the PR description's list of what changes for the user. When the PR already exists without that list, add it to the description before UAT.
- **When:** on the head you close out with. A later commit that changes what the user sees or does needs a new run; a commit that only fixes findings the user confirmed needs a retest of those cases (see the reference).
- **Result:** every run goes to the user with its evidence, a run with no findings included, in the PR and in the report. A finding is a claim, not a confirmed bug: testers often report intended behavior as one. Leave each finding unfixed and ask the user to confirm it (see "Asking at the end"); fix only what the user confirms. Checks only a person can make, such as one that needs a real physical keyboard, go to the user as UAT left to them.
- **Ending:** under full send, switch to full stop whenever a finding, a BLOCKED or INCONCLUSIVE item, or a check left to the user awaits the user's answer; you may also switch when the user should see the change before it merges. Report the switch and its reason. Fixing confirmed findings is new work for a later run, which retests them.

## Endings

### Full send: merge

- **Grants:** merging the PR once the merge gate passes.
- **Close out:** merge with the method the repo uses: check its agent instructions, the allowed methods, and recent merged PRs. With a merge queue or auto-merge, stay until GitHub reports the PR as merged. Go through branch protection as configured, never around it with `--admin` or another bypass.
- **Report adds:** the merge commit.

### Full stop: hand off ready

- **Limits:** the PR stays unmerged. Merging, enabling auto-merge, entering a merge queue, pushing to the default branch, and asking another agent to do any of these all wait for the user.
- **Guard against merging on its own:** whenever the PR exists (before step 1 when it already does, right after opening it in step 4, and before each later push), disable auto-merge and take it out of any merge queue, and report what you changed. When you cannot, stop pushing and tending, and hand off at once with the **Blocked** verdict.
- **Close out:** fetch the default branch and check the live PR: head, base, checks, reviews, and mergeability; it is open, not a draft, and not set to merge on its own. When someone else merged it, report that instead. Then give one verdict:
  - **Ready to merge:** the merge gate passes.
  - **Waiting for the user's UAT answers:** only the user's answers on UAT findings, BLOCKED or INCONCLUSIVE items, or checks left to them remain, with or without a required approval.
  - **Waiting for approval:** only a required human approval remains, and you confirmed it is the actual blocker.
  - **Blocked:** what keeps the gate shut, what you tried, and what is needed.
- **Report adds:** the final head, the verdict, whether full send was switched here by the UAT gate, the reviewers' outcome, the remaining risks, and that the PR is still open and unmerged.

## Blockers

A **blocker** is a step you cannot take, or one that would be irreversible, destructive, unethical, or outside the grant: deleting data, touching production, changing things outside the repo or the project's scope, closing a PR, force-pushing any other branch. A change you cannot prove, and a merge gate you cannot open yourself, are blockers too.

Remove a blocker through the routes you know when you can. When you cannot, set it aside as **pending** and keep going: a pending blocker holds back only the work that depends on it. Finish every step and every part of a step that no blocker holds. When a pending blocker keeps the merge gate shut, leave the PR open and unmerged. When another PR makes this one obsolete, stop work on it; closing it waits for the user.

The work is done when every part that no blocker holds is finished.

## Forks

Technical decisions are yours. A **fork** is a choice you would normally bring to the user: one that shapes the product, the scope, usability, the planned UX, or a promised capability. At a fork, weigh two or three paths, take the one you judge best, and keep going. Record each fork with the paths you weighed and the one you took, so the user can keep or change it.

## Asking at the end

Hold every question until all steps or tasks are either done or blocked. Then ask once, through the harness's question tool, so the thread shows it is waiting: `AskUserQuestion` in Claude Code, `request_user_input` in Codex, or the equivalent your harness has. A question in a normal message goes unseen, and the thread looks done. Put all the context in the question: the PR link, each pending blocker and what it holds back, and the options with your recommendation first.

When no question tool is available, or it returns no answer, start your final message with the questions.
