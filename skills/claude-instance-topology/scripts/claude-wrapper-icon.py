#!/usr/bin/env python3
"""Recolor a Claude wrapper .app icon so Finder, Spotlight, and Launchpad tell wrappers apart.

Samples the two-tone palette from the live /Applications/Claude.app artwork on
every run, so an upstream art change carries through instead of being remapped
onto a stale palette. Recolors the largest rendition and downscales every size
from it.

    claude-wrapper-icon.py --app "/Applications/Claude Personal.app" --variant graphite
    claude-wrapper-icon.py --app "/Applications/Claude Personal.app" --undo

Applying a variant needs Pillow.
"""

# Only the standard library is needed to import this module, so the pure
# mapping stays testable without Pillow.

import argparse
import plistlib
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

SOURCE_APP = Path("/Applications/Claude.app")
LSREGISTER = Path(
    "/System/Library/Frameworks/CoreServices.framework/Frameworks"
    "/LaunchServices.framework/Support/lsregister"
)

VARIANTS = {
    "graphite": ((46, 50, 58), (250, 246, 242)),
    "inverted": ((250, 246, 242), (198, 92, 56)),
    "indigo": ((72, 92, 148), (250, 246, 242)),
}

ICON_SIZES = (16, 32, 128, 256, 512)

# Coarse enough that grain and gradient collapse into one bucket, fine enough
# that background and glyph never share one.
PALETTE_BUCKET = 8
# Well under the ~216 separating the shipped two tones, well over anything grain
# alone can produce. Below it the artwork is no longer two-tone and the
# projection would silently invent colors.
MIN_PALETTE_DISTANCE = 60.0
PALETTE_SAMPLE_LIMIT = 250_000


def fail(message):
    sys.exit(f"error: {message}")


def run(*command):
    try:
        subprocess.run(command, check=True, capture_output=True)
    except FileNotFoundError:
        fail(f"{command[0]} not found")
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace").strip() or f"exit {error.returncode}"
        fail(f"{Path(command[0]).name} failed: {detail}")


def distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right)) ** 0.5


def modal_color(pixels):
    """Center of the most populated color bucket, at full precision."""
    key = lambda rgb: tuple(channel // PALETTE_BUCKET for channel in rgb)
    bucket = Counter(key(rgb) for rgb in pixels).most_common(1)[0][0]
    members = [rgb for rgb in pixels if key(rgb) == bucket]
    return tuple(sum(channel) / len(members) for channel in zip(*members))


def sample_palette(pixels):
    """Background and glyph tones of a two-tone icon.

    Background is the modal color because it covers the most area; glyph is the
    modal color among the decile furthest from it, which finds a glyph whether
    it is lighter or darker than its background.
    """
    if not pixels:
        fail("source artwork has no opaque pixels")
    background = modal_color(pixels)
    ranked = sorted(pixels, key=lambda rgb: distance(rgb, background), reverse=True)
    glyph = modal_color(ranked[: max(1, len(ranked) // 10)])
    if distance(background, glyph) < MIN_PALETTE_DISTANCE:
        fail(
            "source artwork is no longer two-tone "
            f"(tones differ by {distance(background, glyph):.0f}, "
            f"expected at least {MIN_PALETTE_DISTANCE:.0f}) — refusing to guess a palette"
        )
    return background, glyph


class Recolorer:
    """Maps a sampled two-tone palette onto a new one, preserving grain.

    Each pixel is projected onto the source background-to-glyph axis, the new
    palette is interpolated at that position, and the pixel's deviation from the
    ideal source tone is added back. That residual is the grain and gradient.
    """

    def __init__(self, palette, new_background, new_glyph):
        self.background, self.glyph = palette
        self.new_background = new_background
        self.new_glyph = new_glyph
        self.axis = tuple(g - b for g, b in zip(self.glyph, self.background))
        self.axis_squared = sum(a * a for a in self.axis) or 1.0

    def tone(self, rgb):
        position = (
            sum(
                (channel - origin) * axis
                for channel, origin, axis in zip(rgb, self.background, self.axis)
            )
            / self.axis_squared
        )
        return min(1.0, max(0.0, position))

    def pixel(self, rgb):
        position = self.tone(rgb)
        remapped = []
        for index, channel in enumerate(rgb):
            ideal = self.background[index] + self.axis[index] * position
            target = self.new_background[index] + (
                self.new_glyph[index] - self.new_background[index]
            ) * position
            remapped.append(min(255, max(0, round(target + (channel - ideal)))))
        return tuple(remapped)

    def image(self, image):
        from PIL import Image

        out = Image.new("RGBA", image.size)
        source, destination = image.load(), out.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                red, green, blue, alpha = source[x, y]
                if alpha == 0:
                    destination[x, y] = (0, 0, 0, 0)
                    continue
                destination[x, y] = self.pixel((red, green, blue)) + (alpha,)
        return out


def icon_path(app):
    """The icon file a bundle's Info.plist actually points at."""
    info = app / "Contents/Info.plist"
    if not info.is_file():
        fail(f"{info} not found")
    with info.open("rb") as handle:
        name = plistlib.load(handle).get("CFBundleIconFile", "AppIcon")
    if not name.endswith(".icns"):
        name += ".icns"
    return app / "Contents/Resources" / name


def is_source_bundle(app, target, source_app, source_icon):
    """True when --app resolves to the bundle the artwork is read from."""
    return (
        app.resolve() == source_app.resolve()
        or target.resolve() == source_icon.resolve()
    )


def renditions_by_edge(icns, workdir):
    """Every rendition inside an icns, keyed by its pixel edge."""
    from PIL import Image

    iconset = workdir / "source.iconset"
    run("iconutil", "-c", "iconset", str(icns), "-o", str(iconset))
    renditions = {}
    for png in iconset.glob("*.png"):
        with Image.open(png) as rendition:
            renditions[rendition.size[0]] = png
    if not renditions:
        fail(f"{icns} contains no renditions")
    return renditions


def opaque_pixels(png, limit=PALETTE_SAMPLE_LIMIT):
    from PIL import Image

    with Image.open(png) as image:
        raw = image.convert("RGBA").tobytes()
    stride = max(1, len(raw) // 4 // limit)
    return [
        (raw[offset], raw[offset + 1], raw[offset + 2])
        for offset in range(0, len(raw), 4 * stride)
        if raw[offset + 3] == 255
    ]


def build_icns(renditions, recolorer, workdir):
    """Recolor the largest rendition and derive every size from it.

    The hand-tuned 16 and 32px renditions are deliberately not used as their own
    sources: their edge is a warm semi-transparent bevel that sits off the
    background-to-glyph axis, so the remap preserves it as a bright fringe
    against the new palette. The largest rendition ends in a neutral shadow that
    survives recoloring, and downscaling from it stays clean.
    """
    from PIL import Image

    iconset = workdir / "AppIcon.iconset"
    iconset.mkdir()
    with Image.open(renditions[max(renditions)]) as largest:
        art = recolorer.image(largest.convert("RGBA"))

    for base in ICON_SIZES:
        for scale, suffix in ((1, ""), (2, "@2x")):
            edge = base * scale
            rendition = art if art.size[0] == edge else art.resize((edge, edge), Image.LANCZOS)
            rendition.save(iconset / f"icon_{base}x{base}{suffix}.png")

    icns = workdir / "AppIcon.icns"
    run("iconutil", "-c", "icns", str(iconset), "-o", str(icns))
    return icns


def refresh(app):
    run("touch", str(app))
    if LSREGISTER.is_file():
        run(str(LSREGISTER), "-f", str(app))
    subprocess.run(["killall", "Dock"], check=False, capture_output=True)


def undo(app, target, backup, marker):
    if backup.is_file():
        shutil.copy2(backup, target)
        marker.unlink(missing_ok=True)
    elif marker.is_file():
        target.unlink(missing_ok=True)
        marker.unlink()
    else:
        fail(f"no backup at {backup}")
    refresh(app)
    print(f"restored {app.name} to its original icon")


def apply(app, target, backup, marker, variant):
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        fail("Pillow is required: python3 -m pip install --user Pillow")

    source_icns = icon_path(SOURCE_APP)
    if not source_icns.is_file():
        fail(f"{source_icns} not found")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        renditions = renditions_by_edge(source_icns, workdir)
        palette = sample_palette(opaque_pixels(renditions[max(renditions)]))
        recolorer = Recolorer(palette, *VARIANTS[variant])
        icns = build_icns(renditions, recolorer, workdir)

        if target.is_file():
            if not backup.is_file():
                shutil.copy2(target, backup)
        elif not backup.is_file():
            marker.touch()
        shutil.copy2(icns, target)

    refresh(app)
    print(f"applied '{variant}' to {app.name}; undo with --undo")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True, type=Path)
    parser.add_argument("--variant", choices=sorted(VARIANTS))
    parser.add_argument("--undo", action="store_true")
    args = parser.parse_args()

    app = args.app.expanduser()
    if not app.is_dir():
        fail(f"{app} not found")
    target = icon_path(app)
    if SOURCE_APP.is_dir() and is_source_bundle(
        app, target, SOURCE_APP, icon_path(SOURCE_APP)
    ):
        fail(
            f"{app.name} is the shared bundle every wrapper launches — recoloring it "
            "would invalidate its signature and make every later run derive from the "
            "recolored art; pass a wrapper .app instead"
        )
    backup = target.with_suffix(".icns.orig-backup")
    marker = target.with_suffix(".icns.no-original")

    if args.undo:
        undo(app, target, backup, marker)
        return
    if not args.variant:
        fail("--variant is required unless --undo is passed")
    apply(app, target, backup, marker, args.variant)


if __name__ == "__main__":
    main()
