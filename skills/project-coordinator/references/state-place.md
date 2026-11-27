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
| A folder, or a link to a folder, that the project tracks or can track | In the project, the real folder |
| A folder, or a link to a folder, that the project ignores | None: the state stays local |
| A link to a folder inside another git repository | In that repository, only that folder |
| A link to a folder in no git repository | None |

Always commit the real folder the path resolves to, never the link itself:
committing a link saves the link, not the state behind it.

```sh
dir=$(cd .agents/coordinator && pwd -P)          # the real folder, through any link
repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)
if [ -n "$repo" ] && ! git -C "$repo" check-ignore -q "$dir"; then
  git -C "$repo" add -- "$dir"
  git -C "$repo" commit -m "chore(coordinator): <what changed>" -- "$dir"
fi                                               # otherwise: nothing to commit
```

- Never `git add -f` an ignored state into the project.
- Commit every file in the state's folder, not only `state.md` and
  `archive.md`.
- Never push the state's repository unless the user asks.
- Moving an existing state is the user's call: copy the folder to its new
  place and compare the two; run `git rm -r --cached .agents/coordinator`
  in the project and commit that alone; delete the local folder; create
  the link (`ln -s <new> .agents/coordinator`); add `/.agents/coordinator`
  to `.git/info/exclude` (no trailing slash: git does not treat a link as
  a folder); confirm with `ls -l .agents/` that it is a link.
