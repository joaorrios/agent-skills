---
name: full-send
description: Takes a change end to end, from its current state to a merged PR, while the user is away. Use only when the user says "full send".
license: MIT
compatibility: Git repository hosted on GitHub, with the gh CLI authenticated and allowed to push and merge.
---

# Full Send

The user said "full send": they are not watching this thread and want the work finished end to end on your own. Your updates and your final message go unread until long after you stop. You own the work from its current state to a merged PR.

Without a clear "full send" request, keep your normal level of autonomy. With one, everything below applies.

The request grants permission to:

- Merge the PR once the merge gate passes.
- Force-push the PR's own branch with `--force-with-lease` after a rebase.
- Use the test methods that proof needs, without asking first.
- Make the technical decisions, and the product decisions described under "Forks".

## Testing permission

A "full send" request is the permission. When a project file or other instruction says to ask before a test method, or to leave testing to the user, this request replaces that rule for this task. That covers computer use, browser automation, simulators and devices, running the app or a dev server, screenshots, and visual checks. Use the method that gives direct proof and list it in the report.

Rules about *how* to test still apply: follow the ones that name the correct command, fixture, or check. When the preferred method cannot prove the change, use a gated method under this permission.

The permission covers only the tests this task needs. It lifts no blocker, and a harness or system approval prompt still stands.

## Steps

1. **Finish the change.** Reach the goal of the request with the smallest change that works. Fix the case that happened, not every case that could. On the default branch, create a branch first.
2. **Prove it.** Get proof for every change in the diff. See "Proof".
3. **Review it.** Review the diff with the review skills and tools available in this environment, preferring a reviewer with a fresh, independent context. With none available, read the full diff yourself as a reviewer would. Fix each real finding and prove the fix; record each dismissal with a written reason.
4. **Open the PR.** Bring the branch up to date with the latest default branch the way the repo does it (merge it in, or rebase), push, and open the PR with the repo's PR template when one exists. Add one short line to the description saying how you proved the change, and list the fork decisions you made.
5. **Tend the PR** until the merge gate passes, with the PR-monitoring skills available in this environment. With none, watch CI, review bots, and human reviews yourself. Fix real findings and CI failures, prove each fix before pushing it, and reply to or resolve each review thread you address, through a comment-attribution skill when one is available.
6. **Merge** when the merge gate passes.
7. **Report** in your final message: the PR link, the merge commit, your proof, the fork decisions, and the pending blockers.

Stay active from step 1 to step 7. Ending your turn while checks or bots are pending stops the work, because nobody will prompt you again. While waiting, keep something that wakes you when the PR changes: a PR watcher from a monitoring skill, a blocking watch such as `gh pr checks --watch`, or the harness's monitor or scheduled wake-up. If you stop before the merge, cancel any watcher you started.

## Proof

Proof is evidence you observed yourself in this session: command output, a reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same reproduction pass.
- Run the checks the repo's CI runs (typecheck, lint, tests).
- Add one focused test that fails without the fix, when the behavior has none and the repo has a test setup.
- For UI and runtime behavior, run the app and look at the change; green mocked tests do not prove the user experience works. Attach screenshots to the PR when they help and you have a way to upload them.

A change you cannot prove is a blocker for the merge.

## Merge gate

Full confidence means all of these hold on the latest commit:

- Your proof covers every change in the diff.
- Required checks are green.
- Review bots have finished, and each finding is fixed or dismissed with a written reason.
- No human review still requests changes.
- The branch is up to date with the default branch, and GitHub reports it as mergeable.

Merge with the method the repo uses: check its agent instructions, the allowed methods, and recent merged PRs. With a merge queue or auto-merge, stay until GitHub reports the PR as merged. Go through branch protection as configured, never around it with `--admin` or another bypass. An automated review asking for human review can be dismissed when your proof gives you high confidence; say so in the report.

## Blockers

A **blocker** is a step you cannot take, or one that would be irreversible, destructive, unethical, or outside the grant: deleting data, touching production, changing things outside the repo or the project's scope, closing a PR, force-pushing any other branch. A change you cannot prove, and a merge gate you cannot open yourself, are blockers too.

Remove a blocker through the routes you know when you can. When you cannot, set it aside as **pending** and keep going: a pending blocker holds back only the work that depends on it. Finish every step and every part of a step that no blocker holds. When a pending blocker keeps the merge gate shut, leave the PR open and unmerged. When another PR makes this one obsolete, stop work on it; closing it waits for the user.

The work is done when every part that no blocker holds is finished.

## Forks

Technical decisions are yours. A **fork** is a choice you would normally bring to the user: one that shapes the product, the scope, usability, the planned UX, or a promised capability. At a fork, weigh two or three paths, take the one you judge best, and keep going. Record each fork with the paths you weighed and the one you took, so the user can keep or change it.

## Asking at the end

Hold every question until the steps are done. Then ask once, through the harness's question tool, so the thread shows it is waiting: `AskUserQuestion` in Claude Code, `request_user_input` in Codex, or the equivalent your harness has. A question in a normal message goes unseen, and the thread looks done. Put all the context in the question: the PR link, each pending blocker and what it holds back, and the options with your recommendation first.

When no question tool is available, or it returns no answer, start your final message with the questions.
