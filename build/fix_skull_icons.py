"""Replace icons that draw a fossil instead of the animal.

Every taxon in the app is meant to read as the living animal in profile. A few
did not: Giganotosaurus, Dilophosaurus and Compsognathus each came back from
PhyloPic as a SKULL -- an anatomically superb one, with orbits and fenestrae,
and completely inconsistent beside 270 body outlines. Titanoboa had the same
problem in a different form: a whole animal, but coiled and seen from above,
which at 46 px reads as a face rather than a snake.

PhyloPic's search cannot say which of its images is a skull, so this enumerates
every licence-acceptable candidate for a taxon, converts each one, and writes a
review sheet to look at. Once a candidate is chosen, `--apply key=index` writes
it into life_icons.json and life_credits.json with its own attribution.

    python3 fix_skull_icons.py                       # review sheet
    python3 fix_skull_icons.py --apply t:dilophosaurus=2 ...

There is also a structural check, because the eye is the only thing that caught
this and the eye does not run on every build:

    python3 fix_skull_icons.py --audit

A skull silhouette is mostly holes -- orbit, naris, antorbital and mandibular
fenestrae, and the gaps between teeth -- while a body outline has almost none.
Counting enclosed subpaths separates the two cleanly, and anything over the
threshold is worth a human look before it ships.
"""
import json
import os
import re
import sys
import tempfile

import phylopic

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")
CREDITS = os.path.join(HERE, "life_credits.json")
# Developer-only review sheet. Written outside the repo on purpose -- anything
# dropped into web/ has to be remembered and deleted before a commit.
SHEET = os.path.join(os.environ.get("ICON_SHEET_DIR", tempfile.gettempdir()),
                     "icon_picks.html")

# key -> (search name, why it needs replacing)
TARGETS = {
    "t:giganotosaurus": ("Giganotosaurus", "skull, not the animal"),
    "t:dilophosaurus": ("Dilophosaurus", "skull, not the animal"),
    "t:compsognathus": ("Compsognathus", "skull, not the animal"),
    # PhyloPic has exactly one licence-acceptable Titanoboa and it is the coil,
    # so this one takes a stand-in from its own family (Boidae) rather than a
    # different view of the genus, which does not exist. The credit names the
    # species actually drawn, and the app shows that credit. Family-level
    # stand-ins are already how t:cetacea, t:sirenia and t:mosasauridae work.
    "t:titanoboa": ("Boa constrictor", "coiled, seen from above"),
    "t:titanoboa-cerrejonensis": ("Boa constrictor", "coiled, seen from above"),
}


def subpaths(markup):
    """Split an icon's path data into subpaths (each starts with M/m)."""
    d = ""
    for m in re.finditer(r'\bd="([^"]*)"', markup):
        d += " " + m.group(1)
    return [s for s in re.split(r"(?=[Mm])", d) if s.strip()]


def _pts(sub):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sub)]


def _signed_area(sub):
    v = _pts(sub)
    xs, ys = v[0::2], v[1::2]
    n = min(len(xs), len(ys))
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += xs[i] * ys[j] - xs[j] * ys[i]
    return a / 2.0


def hole_count(markup):
    """Enclosed subpaths -- the fenestrae that make a skull a skull.

    Winding is what distinguishes a hole from a body in an even-odd/nonzero
    fill, and potrace emits holes with the opposite orientation to the outline
    they sit in. So: take the sign of the largest subpath as "solid" and count
    everything wound the other way.
    """
    subs = subpaths(markup)
    if len(subs) < 2:
        return 0
    areas = [_signed_area(s) for s in subs]
    outer = max(areas, key=abs)
    if outer == 0:
        return 0
    sign = 1.0 if outer > 0 else -1.0
    return sum(1 for a in areas if a != 0 and (a > 0) != (sign > 0))


def hole_ratio(markup):
    """Area of the biggest enclosed hole, as a fraction of the outline.

    Hole COUNT alone does not separate a skull from a coral: Halysites has 36
    holes and is drawn perfectly correctly, because a chain coral is holes. What
    distinguishes a skull is hole SIZE -- an orbit or an antorbital fenestra is
    a large fraction of the head, while venation, pores and corallites are each
    a fraction of a percent. Big holes in something that should be one solid
    body is the signal worth looking at.
    """
    subs = subpaths(markup)
    if len(subs) < 2:
        return 0.0
    areas = [_signed_area(s) for s in subs]
    outer = max(areas, key=abs)
    if not outer:
        return 0.0
    holes = [abs(a) for a in areas if a and (a > 0) != (outer > 0)]
    return (max(holes) / abs(outer)) if holes else 0.0


def audit(thresh=0.035):
    icons = json.load(open(ICONS))
    rows = sorted(((hole_ratio(v), hole_count(v), k) for k, v in icons.items()),
                  reverse=True)
    flagged = [r for r in rows if r[0] >= thresh]
    print(f"{'big hole':>8} {'holes':>5}  icon")
    for r, n, k in rows[:18]:
        mark = "  <-- is this drawing the fossil, not the animal?" if r >= thresh else ""
        print(f"{r*100:7.1f}% {n:5d}  {k}{mark}")
    print(f"\n{len(flagged)} icons have a hole worth {thresh*100:.0f}%+ of the "
          f"outline. Holes are correct for corals, foliage and anything porous "
          f"-- the ones to look at are ANIMALS that should be a solid body.")
    return flagged


def review():
    build = phylopic.build_number()
    icons = json.load(open(ICONS))
    blocks = []
    for key, (name, why) in TARGETS.items():
        cands = phylopic.search(name, build, limit=12)
        cur = icons.get(key, "")
        cells = [f'<div class="c cur"><svg viewBox="0 0 64 40">{cur}</svg>'
                 f'<div class=n>CURRENT</div>'
                 f'<div class=t>{hole_count(cur)} holes &middot; {why}</div></div>']
        for i, c in enumerate(cands):
            try:
                svg = phylopic.fetch_vector(c)
                path, err = phylopic.convert(svg, tol=0.22)
            except Exception as e:
                path, err = None, str(e)
            if not path:
                cells.append(f'<div class=c><div class=n>#{i} failed</div>'
                             f'<div class=t>{err}</div></div>')
                continue
            cells.append(
                f'<div class=c><svg viewBox="0 0 64 40">{path}</svg>'
                f'<div class=n>#{i}</div><div class=t>{hole_count(path)} holes '
                f'&middot; {c["licence"]}<br>{c["attribution"]}<br>{c["taxon"]}</div></div>')
        blocks.append(f'<h2>{key} &mdash; searched "{name}"</h2>'
                      f'<div class=g>{"".join(cells)}</div>')
    open(SHEET, "w").write(
        '<!doctype html><meta charset=utf-8><title>icon picks</title><style>'
        'body{margin:0;background:#101820;color:#cfd9e6;font:12px/1.4 system-ui;padding:14px}'
        'h2{font-size:13px;color:#eaf1f8;margin:18px 0 8px;letter-spacing:.03em}'
        '.g{display:grid;grid-template-columns:repeat(6,220px);gap:10px}'
        '.c{--ko:#101820;background:rgba(255,255,255,.05);border:1px solid #2a3644;'
        'border-radius:8px;padding:8px;text-align:center}'
        '.c.cur{border-color:#c1553a}'
        '.c svg{width:202px;height:126px;display:block;fill:currentColor;color:#dbe6f2;'
        'stroke-linecap:round;stroke-linejoin:round}'
        '.n{font-weight:700;color:#eaf1f8;margin-top:5px}'
        '.t{color:#7d8b9c;font-size:9.5px;font-style:italic}'
        '</style>' + "".join(blocks))
    print(f"wrote {os.path.relpath(SHEET, HERE)}")


def apply(picks):
    build = phylopic.build_number()
    icons = json.load(open(ICONS))
    credits = json.load(open(CREDITS))
    for key, idx in picks.items():
        name = TARGETS[key][0]
        cands = phylopic.search(name, build, limit=12)
        c = cands[idx]
        svg = phylopic.fetch_vector(c)
        path = None
        for t in (0.22, 0.35, 0.5, 0.7, 1.0):
            path, err = phylopic.convert(svg, tol=t)
            if path and len(path) <= phylopic.BUDGET:
                break
        if not path:
            raise SystemExit(f"convert failed for {key}: {err}")
        icons[key] = path
        credits[key] = {"attribution": c["attribution"], "licence": c["licence"],
                        "licence_url": c["licence_url"], "taxon": c["taxon"],
                        "uuid": c["uuid"]}
        print(f"{key:32s} <- #{idx} {c['licence']:9s} {c['attribution']}  "
              f"({len(path)} chars, {hole_count(path)} holes)")
    json.dump(icons, open(ICONS, "w"), indent=1, sort_keys=True)
    json.dump(credits, open(CREDITS, "w"), indent=1, sort_keys=True)
    print(f"wrote life_icons.json ({len(icons)}) and life_credits.json "
          f"({len(credits)})")


if __name__ == "__main__":
    if "--audit" in sys.argv:
        audit()
    elif "--apply" in sys.argv:
        picks = {}
        for a in sys.argv[sys.argv.index("--apply") + 1:]:
            k, _, v = a.partition("=")
            picks[k] = int(v)
        apply(picks)
    else:
        review()
