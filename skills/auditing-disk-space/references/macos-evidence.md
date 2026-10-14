# Conditional checks

## APFS and VM

For divergent allocation and free-space figures, compare timestamps, units and
scopes. Investigate hardlinks, APFS clones, snapshots, open deleted files and
concurrent writes. Collect snapshot and open-deleted-file evidence with errors
and coverage limits. Scope snapshot checks to the relevant volumes; distinguish
Finder's purgeable availability from `df`.

A cloned tree's allocation can exceed disk capacity. Quantify uniquely held
physical blocks only where measurements support that attribution. Keep an
unexplained discrepancy when sharing or concurrent activity cannot be isolated.

When free space falls despite smaller Data trees, compare physical usage across
APFS volume roles, including VM, at timestamped checkpoints. Record swap
separately and obtain memory-pressure evidence before claiming current pressure.
Active swap files remain system-managed. Treat a restart as a separate operation
requiring saved/closed work and explicit authorization; measure its outcome after
restart.

For protected-directory gaps, list the users, backups or metadata outside
coverage. Attribute bytes after obtaining sufficient measurement access. Compare
older inventories only within their recorded timing, methods and coverage.

## Repository lifecycle

Resolve Git and common directories, list dependent worktrees, and identify
application/workspace ownership. Classify independent clone, actual Git
worktree, CI checkout or retained laboratory from those records.

Check tracked and untracked changes, local-only commits, and confirmed backup or
remote reachability. Treat local remote-tracking refs as a cached observation.
Check agent/chat references, archive status in the owning application, active
process provenance and handles across the applications referencing the checkout.

For dependency-only cleanup, preserve source, Git history, dependent worktrees,
preferences and evidence. For laboratory retirement, identify retained
reproduction state and rebuilding costs; preserve the agreed reports, deliveries
and pinned references. Verify preservation archives through member lists and
hashes. Retire managed worktrees through the owning application's lifecycle.
Finish with an exact disposal boundary and verified preservation of everything
outside it.

## Git consolidation

Inspect pack counts, unique object counts and maintenance settings read-only.
Treat duplicated occurrences as a consolidation candidate; preserve the object
store rather than treating it as a disposable directory.

For an authorized consolidation:

1. Establish checkout and runner ownership, idle state and absence of writers.
   Check dependent worktrees, workers and Git processes. Temporary runner control
   must belong to the approved scope and target a verified process identity.
   Arrange resumption in a `finally` or equivalent cleanup path.
2. Record installed Git capabilities, repository layout, shallow/partial status
   and alternates. Inventory **all original local objects**, packed and loose,
   reachable and unreachable; retain sorted IDs, counts and a digest. Snapshot
   HEAD, refs, config, shallow metadata, working-tree/index state and relevant
   source hashes; record a `git fsck --full` baseline. Resolve external object
   dependencies in the preservation plan before preparing storage.
3. Budget temporary headroom and prepare storage with originals retained. Verify
   new pack integrity and coverage of every original object by verified new
   packs or retained readable loose objects. Require full inventory coverage,
   including objects outside reachable history and shallow boundaries.
4. Retain originals on any coverage or integrity failure. Once coverage is
   complete, remove only proven redundant storage through supported Git
   mechanisms, preserving unique loose objects.
5. Verify equality of full before/after object inventories and unchanged
   HEAD/refs/source/index/config/shallow state. Require successful
   `git fsck --full`, interpreting dangling objects against the baseline, and
   verify auxiliary indexes. Resume any temporarily controlled runner and
   verify its identity and resumed state, including on failure paths.

Finish with verified object and repository preservation, restored runner state,
and either completed consolidation or retained originals with the failed gate
identified. Return allocation and free-space comparisons to the main procedure.

## Installation artifacts

Compare downloaded archives or expanded preparation against installed versions
and contents. Establish active updater/process ownership and pending versions.
Preserve artifacts participating in an unfinished update.

Separate extension archives from installed extensions and record the download
cost of replacing archives. Record loss of offline reinstall capability when
removing installers. For system/boot preparation, distinguish redundant
installer contents from installed runtime, EFI, root patches, recovery material
and unique verification evidence.

Finish with comparison coverage, exact removable artifacts, replacement costs
and the installed/recovery state to preserve.
