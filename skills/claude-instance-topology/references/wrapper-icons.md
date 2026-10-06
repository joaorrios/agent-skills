# Wrapper icons

A wrapper `.app` is a small bundle whose `Contents/MacOS/launcher` runs `open -n -a "Claude" --args …` and exits. The process that keeps running, and that the Dock draws a tile for, is the shared `/Applications/Claude.app`. A wrapper's icon therefore reaches Finder, Spotlight, Launchpad, and a parked Dock shortcut, but not the tile of a running instance.

## Recolor a wrapper icon

`scripts/claude-wrapper-icon.py` (relative to the skill root) recolors a wrapper's icon:

```bash
scripts/claude-wrapper-icon.py --app "/Applications/Claude Personal.app" --variant graphite
scripts/claude-wrapper-icon.py --app "/Applications/Claude Personal.app" --undo
```

Variants are the background and glyph color pairs in the script's `VARIANTS` table; `--help` lists them. Add or retune a pair there to pick other colors.

The icon is done when Finder and Spotlight show the new colors for the wrapper and `--undo` restores the original.

It samples the two-tone palette from the installed `Claude.app` artwork on every run, so it follows upstream art changes, and it stops with an error if that artwork is no longer two-tone. It backs up the original icon as `AppIcon.icns.orig-backup`, re-registers the bundle with `lsregister`, and restarts the Dock. It refuses `/Applications/Claude.app` itself: recoloring the shared bundle would invalidate its signature and make later runs sample already-recolored art.

The script recolors the largest rendition and downscales every size from it. The hand-tuned 16 and 32 px renditions end in a warm semi-transparent bevel that a two-tone remap turns into a bright fringe; the largest rendition ends in a neutral shadow that recolors cleanly. Keep that design when changing the script.

Run `bash scripts/tests/claude-wrapper-icon.test.sh` from the skill root after any change. The image checks run only where Pillow is installed and report as skipped otherwise.

## Distinguish the running tile

Only a separate real bundle changes the running tile. `cp -Rc /Applications/Claude.app` makes a free APFS clone, but the clone receives no app updates and must be re-cloned after each one. If changing its icon breaks launch, the ad-hoc re-sign that fixes it loses the notarized bundle's Keychain access, forcing a fresh login in that instance. Prefer the wrapper icon unless the Finder-level distinction proves insufficient.
