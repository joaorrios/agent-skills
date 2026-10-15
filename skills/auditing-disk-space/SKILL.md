---
name: auditing-disk-space
description: Disk space audit and cleanup for macOS. Finds where space went with measured evidence, then removes only the paths the user explicitly authorizes. Use when a Mac is low on space or warns that its disk is full, or when free space keeps shrinking after a cleanup that could not explain it.
license: MIT
compatibility: macOS. Full Disk Access for the app or terminal that runs the agent; without it, protected folders go unmeasured.
---

# Auditing Disk Space

The audit is **read-only**: it ends with a numbered list of **candidates** and
stops. Removal is the final step and covers only the paths the user names,
directly or by number. A number names the paths listed under it in the report
and nothing else. Approving a category, stating a goal ("free up space"), or calling something a
cache names no path.

Every figure you report is **measured** (a command you ran in this audit) or
**inferred**. Label which.

The audit is done when the measured figures **reconcile** with the used space
`df` reports, or when you state the remaining gap as unexplained.

## 1. Measure the current state

```bash
df -h / /System/Volumes/Data
diskutil info /System/Volumes/Data | grep -Ei "free|purgeable|capacity|container"
tmutil listlocalsnapshots /
```

Start from these numbers, not from one someone reported. Free space moves while
you work, and Finder's "available" includes purgeable space that `df` does not.

## 2. Map the home, dot-directories included

```bash
for d in "$HOME"/* "$HOME"/.[!.]*; do
  /usr/bin/du -sxh "$d" 2>>"$TMPDIR/du-errors.txt"
done | sort -rh | head -25
grep -c "not permitted" "$TMPDIR/du-errors.txt"
```

- `.[!.]*` reaches dot-directories, where agent tooling keeps worktrees and
  models (`.claude`, `.codex`, `.ollama`) and where `.Trash` lives.
- One `du` per tree. Several large trees in one command get killed (exit 137)
  and return nothing; in the loop, a killed run loses only its own line.
- `-x` stays on one filesystem, so network mounts do not stall the scan.
- `/usr/bin/du` bypasses shell wrappers that truncate output. Truncated output
  reads exactly like complete output.
- Permission errors mean undersized figures. Without Full Disk Access,
  protected folders under `~/Library` come out small, and the missing space
  shows up later as an unexplained gap.

Reconcile the total with `df`. Find the rest (`/opt`, `/private/var`, other
users, snapshots) before proposing anything.

## 3. Follow the biggest branch down

Descend one level at a time into the largest entry, one tree per command, until
the cause names itself as a single file or a known class. Known classes, most
frequent first:

| Place | What it is |
|---|---|
| `~/.<agent-tool>/worktrees/**/node_modules` | Agent worktrees, each with its own dependencies. Tens of GB; usually the answer. |
| `~/Library/Application Support/*/vm_bundles` | Claude Desktop VM disk, about 10 GB each. `rootfs.img` is redownloaded, not rebuilt from the `.zst` beside it. |
| `~/Library/Group Containers/*whatsapp*/Message/Media` | Received photos and video. |
| `/private/var/folders/*/*/X/*code_sign_clone` | One browser copy per update, never collected. |
| `~/.ollama/models` | Local LLM weights, several GB per model. |
| `~/Library/pnpm`, `~/.npm`, `~/.cache` | Package stores. Removing them slows every later install. |
| `/opt/homebrew` | `brew cleanup` reclaims part of it. |
| App logs | Nothing rotates them. |
| `~/Library/Caches` | Live state of running apps, not a cause. |

## 4. Measure what removal would free

Separate `du` runs count shared files once per run. A single run counts each
hardlink once, so measure a set of directories in one call:

```bash
find "<root>" -maxdepth 3 -type d -name node_modules -prune -print0 \
  | xargs -0 /usr/bin/du -sxch | tail -1
```

When the list exceeds the argument limit, `xargs` splits it into several runs
and the total overcounts; measure the common parent instead.

That figure is still an upper bound. Files also held by a store outside the set
free nothing while the store keeps them. A link count above 1 (`ls -li`) shows
a hardlink. pnpm on APFS clones files from its store (`pnpm store path`)
instead, so the link count stays 1 and `du` counts every clone in full. Report
the figure as an upper bound whenever a store is involved.

## 5. Test every candidate

A path becomes a candidate only after it passes all four tests.

**Is a process using it?**

```bash
lsof 2>/dev/null | grep -F "<path>" | head
lsof -a -d cwd 2>/dev/null | grep -F "<path>"
```

Timestamps do not answer this. In one audit the Chrome clone in use was six
hours older than the newest one; removing by date would have killed the running
browser. `lsof +D` walks the whole tree and takes minutes on `node_modules`.

**Is it tracked by git?**

```bash
git -C "<repo>" ls-files --error-unmatch <paths>
git -C "<worktree>" status --porcelain | wc -l
```

A `.log` extension does not make a log. Evidence documents named `*.log.md`
live inside repositories and are tracked.

**Is it a log or a transcript?**

Logs record what a program did to itself. Transcripts record conversations, and
session resume depends on them. Open the file and look:

```bash
sqlite3 <file>.sqlite ".schema" | head -20
```

Fields like `module_path`, `file`, `line`, `level` mean diagnostics. Transcripts
stay out of the list. Known locations:

| Tool | Path |
|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` |
| Codex | `~/.codex/sessions/**/rollout-*.jsonl` |
| Cursor chats | `~/Library/Application Support/Cursor/User/globalStorage` |

**Is the app running?** Match on the process, not the bundle path. Another app
often launches helpers that live in `Foo.app/Contents/Helpers/`, so grepping the
bundle path counts a closed app as open.

```bash
osascript -e 'tell application "System Events" to get name of every application process whose background only is false'
```

## 6. Report and stop

Group the candidates: zero-consequence items first, then the ones that cost
time or data. Rank by size within each group. Number them with one sequence
that runs through both groups (if the first group ends at 4, the second starts
at 5), so each number identifies one item in the whole report.

For each, give the number, the exact paths, the measured size (marked as an
upper bound where step 4 says so), what it is, what breaks if it goes, and
whether it regenerates. Take regeneration from the program's documentation or
observed behaviour, not from the names of neighbouring files.

Close with the reconciliation: how much of the used space the report explains,
and the gap you could not explain. An admitted gap beats a plausible story,
because the user acts on the story.

End by asking which numbers to remove, then wait for the answer.

## 7. Remove what the user names

For each item the user names, by number or by path:

1. Map a number to the exact paths listed under it in the report. Rerun the
   step 5 tests on those paths. State changes between the report and the approval.
2. Record the free space from `df`.
3. Remove it with the owning tool's command when one exists: `git worktree
   remove`, `pnpm store prune`, `brew cleanup`, `ollama rm`, `tmutil
   deletelocalsnapshots`. Removing their files directly leaves the tool's
   records pointing at missing paths. Moving to Trash frees nothing until the
   Trash is emptied.
4. Record the free space again and compare the gain with the size you reported.
   Report any difference and its measured cause, or say it is unexplained.

## 8. Verify regeneration

For each removed item you said would regenerate, check the prediction once the
program has rebuilt it. A `foo.img` next to a `foo.img.zst`, written hours
later, reads like local decompression. In the audit behind the `vm_bundles`
row, it was a download: the `.zst` access time did not move during the rebuild,
and the 1.1 GB kept to avoid a download bought nothing.

```bash
ls -lTu <suspected-source>    # access time, not modification time
```

If the access time did not move across the rebuild, that file was not the
source. The test proves nothing on a volume mounted with `noatime` (check
`mount`). Tell the user which predictions failed and what each one costs them.
