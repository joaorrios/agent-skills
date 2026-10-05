#!/usr/bin/env bash
# Deterministic behavior witness for scripts/claude-wrapper-icon.py.
#
# The palette mapping, palette sampling, icon path resolution and shared-bundle
# guard are pure and run everywhere. The Pillow-backed image pass runs only
# where Pillow is installed, and reports as skipped rather than passed.
#
# Run from the skill root: bash scripts/tests/claude-wrapper-icon.test.sh
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SCRIPT="$ROOT/scripts/claude-wrapper-icon.py"

python3 - "$SCRIPT" <<'PY'
import sys

# Loading the script by path would otherwise leave a scripts/__pycache__ behind.
sys.dont_write_bytecode = True

import importlib.util
import plistlib
import tempfile
from pathlib import Path

script_path = Path(sys.argv[1])
if not script_path.is_file():
    sys.exit(f"FAIL missing script — {script_path}")

spec = importlib.util.spec_from_file_location("claude_wrapper_icon", script_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

failures = []


def ok(label):
    print(f"ok   {label}")


def fail(label, detail):
    failures.append((label, detail))
    print(f"FAIL {label} — {detail}")


def require(label, condition, detail=""):
    ok(label) if condition else fail(label, detail or "condition false")


def equals(label, actual, expected):
    require(label, actual == expected, f"got {actual!r}, expected {expected!r}")


def exits(label, call):
    try:
        call()
    except SystemExit:
        ok(label)
    else:
        fail(label, "expected SystemExit, none raised")


# --- import surface -------------------------------------------------------
# Pillow is imported inside the functions that need it so the mapping stays
# testable where it is absent. A module-level import would break that.
require(
    "importing the module does not pull in Pillow",
    "PIL" not in sys.modules,
    "PIL was imported at module level",
)

# --- palette mapping ------------------------------------------------------
PALETTE = ((100, 100, 100), (200, 200, 200))
recolorer = module.Recolorer(PALETTE, (50, 50, 50), (200, 220, 240))

equals("tone of the background is 0", recolorer.tone((100, 100, 100)), 0.0)
equals("tone of the glyph is 1", recolorer.tone((200, 200, 200)), 1.0)
equals("tone of the midpoint is 0.5", recolorer.tone((150, 150, 150)), 0.5)
equals("tone clamps above the glyph", recolorer.tone((250, 250, 250)), 1.0)
equals("tone clamps below the background", recolorer.tone((50, 50, 50)), 0.0)

equals("background maps to the new background", recolorer.pixel((100, 100, 100)), (50, 50, 50))
equals("glyph maps to the new glyph", recolorer.pixel((200, 200, 200)), (200, 220, 240))
equals("midpoint interpolates the new palette", recolorer.pixel((150, 150, 150)), (125, 135, 145))
# (10, -10, 0) is orthogonal to the source axis, so it is pure grain: it must
# survive the remap untouched rather than being folded into the tone.
equals("grain survives the remap", recolorer.pixel((110, 90, 100)), (60, 40, 50))
equals("channels clamp at 255", recolorer.pixel((250, 250, 250)), (250, 255, 255))

# --- palette sampling -----------------------------------------------------
two_tone = [(100, 100, 100)] * 900 + [(200, 200, 200)] * 100
background, glyph = module.sample_palette(two_tone)
equals("samples the background from the dominant area", background, (100.0, 100.0, 100.0))
equals("samples the glyph from the furthest decile", glyph, (200.0, 200.0, 200.0))

inverted = [(200, 200, 200)] * 900 + [(100, 100, 100)] * 100
background, glyph = module.sample_palette(inverted)
equals("samples a glyph darker than its background", (background, glyph), ((200.0,) * 3, (100.0,) * 3))

exits(
    "refuses artwork that is not two-tone",
    lambda: module.sample_palette([(100, 100, 100)] * 900 + [(120, 120, 120)] * 100),
)
exits("refuses artwork with no opaque pixels", lambda: module.sample_palette([]))

# --- bundle introspection and guard ---------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    def bundle(name, info):
        app = root / name
        (app / "Contents").mkdir(parents=True)
        with (app / "Contents/Info.plist").open("wb") as handle:
            plistlib.dump(info, handle)
        return app

    named = bundle("Named.app", {"CFBundleIconFile": "AppIcon"})
    suffixed = bundle("Suffixed.app", {"CFBundleIconFile": "electron.icns"})
    bare = bundle("Bare.app", {})
    equals("resolves the declared icon name", module.icon_path(named).name, "AppIcon.icns")
    equals("does not double the .icns suffix", module.icon_path(suffixed).name, "electron.icns")
    equals("falls back to AppIcon when undeclared", module.icon_path(bare).name, "AppIcon.icns")
    exits("refuses a bundle with no Info.plist", lambda: module.icon_path(root / "Absent.app"))

    source_icon = module.icon_path(suffixed)
    require(
        "guards the source bundle itself",
        module.is_source_bundle(suffixed, source_icon, suffixed, source_icon),
    )
    require(
        "guards a wrapper pointing at the source icon",
        module.is_source_bundle(named, source_icon, suffixed, source_icon),
    )
    require(
        "allows an ordinary wrapper",
        not module.is_source_bundle(named, module.icon_path(named), suffixed, source_icon),
    )

# --- image pass (Pillow only) ---------------------------------------------
try:
    from PIL import Image
except ImportError:
    print("skip Pillow absent — image pass not exercised")
else:
    image = Image.new("RGBA", (2, 2))
    image.putpixel((0, 0), (100, 100, 100, 255))
    image.putpixel((1, 0), (200, 200, 200, 255))
    image.putpixel((0, 1), (110, 90, 100, 255))
    image.putpixel((1, 1), (0, 0, 0, 0))
    out = module.Recolorer(PALETTE, (50, 50, 50), (200, 220, 240)).image(image)
    equals("image keeps the background mapping", out.getpixel((0, 0)), (50, 50, 50, 255))
    equals("image keeps the glyph mapping", out.getpixel((1, 0)), (200, 220, 240, 255))
    equals("image keeps grain", out.getpixel((0, 1)), (60, 40, 50, 255))
    equals("image leaves transparent pixels untouched", out.getpixel((1, 1)), (0, 0, 0, 0))

print()
if failures:
    print(f"{len(failures)} failing assertion(s)")
    sys.exit(1)
print("all assertions passed")
PY
