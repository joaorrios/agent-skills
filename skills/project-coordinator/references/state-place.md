# Where the state lives

The state is always read and written at `.agents/coordinator/` in the
project root.

## Find or create it

- When `.agents/coordinator` exists, use it as it is: a folder, or a link
  to a folder somewhere else. Someone set it up on purpose, maybe an earlier
  coordinator or the user. Never move, replace, or unlink it.
- When it does not exist, create it as a plain folder in the project.

## Commit where it really lives

What `.agents/coordinator` is decides where the commit goes:

| `.agents/coordinator` | Commit |
|---|---|
| A folder the project tracks or can track | In the project |
| A folder the project ignores (`git check-ignore` says so) | None: the state stays local |
| A link to a folder inside another git repository | In that repository, only that folder |
| A link to a folder in no git repository | None |

```sh
dir=$(cd .agents/coordinator && pwd -P)          # the real folder, through a link
repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)
project=$(git rev-parse --show-toplevel)
if [ -z "$repo" ]; then
  :                                              # no repository: nothing to commit
elif [ "$repo" = "$project" ]; then
  git check-ignore -q .agents/coordinator || {
    git add -- .agents/coordinator
    git commit -m "chore(coordinator): <what changed>" -- .agents/coordinator
  }
else
  git -C "$repo" add -- "$dir"
  git -C "$repo" commit -m "chore(coordinator): <what changed>" -- "$dir"
fi
```

- In the project, `git add` through a link fails ("beyond a symbolic
  link"); that is the guard, not an error to work around.
- Never `git add -f` an ignored state into the project.
- Commit every file in the state's folder, not only `state.md` and
  `archive.md`.
- Never push the state's repository unless the user asks.
- Moving an existing state is the user's call: copy the folder, run
  `git rm -r --cached .agents/coordinator` in the project and commit that
  alone, link the new place, and ignore the link in `.git/info/exclude` as
  `/.agents/coordinator` (no trailing slash: git does not treat a link as a
  folder).
