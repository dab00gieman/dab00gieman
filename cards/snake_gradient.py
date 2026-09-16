"""Post-process snk SVGs: paint the snake blue -> green along its journey.

snk's grid animation lights each cell briefly as the snake passes. The
flash colour is normally the contribution colour (light theme) or a flat
snake colour (dark theme). This rewrites every flash so the colour
interpolates from blue at the start of the run to the profile's terminal
green by the end — the snake literally turns green as it eats commits.
"""
import re
import sys

# flash keyframe: "<percent>%{fill:<value>}"
FLASH = re.compile(r"([\d.]+)%\{fill:([^}]+)\}")

# journey colours per theme: (start blue, end green)
PALETTES = {
    "light": ((9, 105, 218), (38, 174, 74)),    # GitHub blue -> GitHub green
    "dark": ((0, 198, 255), (0, 255, 65)),       # electric blue -> #00ff41
}


def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def journey_color(frac, theme="dark"):
    """Colour of the snake at 0..1 along its run."""
    start, end = PALETTES[theme]
    c = tuple(round(a + (b - a) * frac) for a, b in zip(start, end))
    return _hex(c)


def paint(svg, theme="dark"):
    """Rewrite every snake flash in an snk SVG's keyframes.

    Turn-on keyframes carry the flash colour (a literal or a var(--cN));
    turn-off keyframes always reference var(--ce) and stay untouched.
    """
    flashes = [m for m in FLASH.finditer(svg)
               if m.group(2).strip() != "var(--ce)"]
    if not flashes:
        return svg
    ts = [float(f.group(1)) for f in flashes]
    lo, hi = min(ts), max(ts)
    if hi - lo < 1e-9:
        lo, hi = 0.0, 1.0

    def repl(mo):
        if mo.group(2).strip() == "var(--ce)":
            return mo.group(0)            # turn-off keyframe: leave it
        t = float(mo.group(1))
        frac = (t - lo) / (hi - lo)
        return "{}%{{fill:{}}}".format(mo.group(1), journey_color(frac, theme))

    return FLASH.sub(repl, svg)


def main(argv):
    if len(argv) != 3 or argv[2] not in PALETTES:
        sys.exit("usage: snake_gradient.py <snk.svg> <light|dark>")
    path, theme = argv[1], argv[2]
    svg = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8").write(paint(svg, theme))
    print(f"painted {path} ({theme}) blue -> green")


if __name__ == "__main__":
    main(sys.argv)
