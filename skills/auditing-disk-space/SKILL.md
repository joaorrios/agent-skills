---
name: auditing-disk-space
description: Audit macOS disk usage and propose cleanup when space is low or keeps shrinking after cleanup. Execute concrete paths and operations only within the user's approved scope.
license: MIT
compatibility: macOS. Protected folders require Full Disk Access for the executing app or terminal; otherwise report partial coverage.
---

# Auditing Disk Space

## 1. Establish the baseline

Create an audit directory for command output. Record timestamps, units, exit
status and stderr; show compact summaries and retain inventories in artifacts.
Send brief progress updates during lengthy scans or operations.

```bash
df -k / /System/Volumes/Data
diskutil apfs list
tmutil listlocalsnapshots /
sysctl vm.swapusage
```

Keep file-tree allocation (`du`), available space (`df`), APFS container free
space, per-volume use, snapshots and swap as separate measurements. Label
inferences and coverage limits; use fresh measurements for the baseline.
Finish with a timestamped baseline and the scopes each measurement covers.

## 2. Locate the consumption

```bash
/usr/bin/du -x -k -d 1 "$HOME" > "<audit-dir>/home.tsv" 2> "<audit-dir>/home.errors"
```

Descend one tree at a time through the largest entries, including hidden
folders. Account for other branches such as `/opt`, `/private/var`, other users
and backups. Record inaccessible or interrupted scans as partial coverage.

Measure candidate sets without overlapping parents and children. Prefer one
`du` invocation or a common parent to avoid recounting hardlinks across separate
runs or `xargs` batches. Treat allocation as an upper bound on recovery; shared
APFS blocks remain unresolved by `du`.

For allocation above capacity, unexplained free-space changes or large VM/swap,
read [APFS and VM](references/macos-evidence.md#apfs-and-vm).
Finish with owners and purposes for the large measured entries, and an explicit
unexplained remainder where coverage or physical attribution is incomplete.

## 3. Qualify candidates

Establish each candidate's exact path, owner, purpose and proposed operation.
Complete all applicable checks:

- **Use:** capture open-file and cwd listings, process identity and errors;
  filter path boundaries. Inspect useful output even with a nonzero exit.
  Report only the use observed within that coverage. Use bounded listings for
  large trees instead of recursive `lsof +D`. Identify owning app and helpers
  from process provenance rather than bundle-path matches alone.
- **Retention:** identify conversations, evidence, unique data and dependencies
  to preserve. For repository content, read
  [Repository lifecycle](references/macos-evidence.md#repository-lifecycle).
- **Purpose:** inspect content rather than extensions or directory names.
  Distinguish diagnostic logs from conversations needed for session resume.
  Inspect SQLite with `sqlite3 -readonly -init /dev/null "<file>" ".schema"`.
- **Effects:** establish what removal or consolidation changes, the owning
  tool's lifecycle operation, and recreation or download costs. Support
  regeneration claims with documentation or observed normal use.

For large Git object stores, read
[Git consolidation](references/macos-evidence.md#git-consolidation).
For updates, installers or system preparation, read
[Installation artifacts](references/macos-evidence.md#installation-artifacts).
Finish with evidence for every applicable check; keep unresolved items out of
the executable candidate list.

## 4. Present the scope for approval

Rank candidates by measured allocation. Each row needs an ID, exact path,
operation, allocation upper bound, owner, use and retention evidence, effects
and regeneration cost. Close with coverage, the unexplained remainder and
hypotheses clearly distinguished from measurements.

The audit ends here unless the concrete scope is already authorized. An
unambiguous approval of numbered rows or a presented plan covers their paths,
operations and effects; carry that approval forward. A general goal or an
unspecified category supplies no concrete scope. Obtain approval for additions
or changed effects before including them in execution.

## 5. Execute and verify

For each authorized operation:

1. Recheck use, ownership and retention. Resolve changed state against the
   approved scope before proceeding.
2. Capture timestamped `df` and relevant allocation/volume baselines.
3. Execute through the owning tool's lifecycle operation where available.
   Consolidate Git stores using the reference's preservation gates.
4. Verify absence for removals or preservation and integrity for consolidation.
   Report failures and retained originals.
5. Remeasure `df` and relevant APFS/VM figures. Report observed net gain
   separately from allocation reduction. Concurrent activity affects the gain;
   attribute differences only to measured causes, leaving the rest unexplained.

Finish with a result for every approved operation and a before/after comparison.
Moving to Trash retains allocation until it is emptied.

## 6. Observe regeneration

Check predictions when normal use recreates an item. Mark unobserved predictions
pending; leave downloads, installs and tests to normal use rather than triggering
them to refill removed paths. Reassess active or regenerating caches before any
further cleanup. Finish with each prediction marked observed, contradicted or
pending, and its download or installation cost recorded.
