"""Find labels that move in ways no piece of crust ever could.

audit_labels.py already checks whether a name sits on the right KIND of ground.
This checks whether it sits in a plausible PLACE, frame to frame, which is a
different failure and the one a viewer actually notices: a name that jumps an
ocean between one keyframe and the next, or drifts steadily across a continent
it never belonged to.

Two things get reported.

    JUMP    the largest single-keyframe displacement over the label's window.
            Plates move at most ~200 mm/yr, which over a 5 Myr step is about
            1000 km, or 9 degrees. Anything past roughly 15 degrees in one step
            is the label being re-placed, not the crust moving.

    UNTRACKED  a long-lived landmass or region with no plate track at all.
            Those fall back to snapLabel's 90-degree search for matching
            terrain, which finds whatever is nearest rather than whatever is
            right. Cimmeria spent 46 Myr attached to Laurasia beside the Urals
            this way -- a continent it had not reached, and would collide with
            rather than join -- and then jumped the width of Palaeo-Tethys when
            the search found somewhere better.

    ../venv/bin/python audit_label_motion.py [--max-step 15] [--all]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(HERE, "..", "web", "labels.json")

#: A 5 Myr keyframe step at a very fast 200 mm/yr is about 9 degrees. Past this
#: the label is being re-placed rather than carried.
MAX_STEP_DEG = 15.0

#: Types where a missing track is a real problem: these are pieces of crust with
#: a history, not points that happen to sit somewhere. Oceans are excluded on
#: purpose -- a basin is water, and tracking it would follow the wrong plate.
CRUSTAL = {"continent", "region", "island", "orogen", "craton"}


def sep(a, b):
    """Great-circle separation in degrees."""
    lo1, la1 = math.radians(a[0]), math.radians(a[1])
    lo2, la2 = math.radians(b[0]), math.radians(b[1])
    d = math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(lo1 - lo2)
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def main():
    lab = json.load(open(LABELS))
    max_step = MAX_STEP_DEG
    if "--max-step" in sys.argv:
        max_step = float(sys.argv[sys.argv.index("--max-step") + 1])
    show_all = "--all" in sys.argv

    jumps, untracked = [], []
    for l in lab:
        span = abs(l["a1"] - l["a0"])
        tr = l.get("tr")
        if not tr:
            if l["t"] in CRUSTAL and span >= 40:
                untracked.append((span, l["n"], l["t"], l["a1"], l["a0"]))
            continue
        tr = sorted(tr, key=lambda r: r[0])
        worst, at = 0.0, None
        for i in range(1, len(tr)):
            if abs(tr[i][0] - tr[i - 1][0]) > 12:      # a gap, not a step
                continue
            d = sep(tr[i - 1][1:], tr[i][1:])
            if d > worst:
                worst, at = d, (tr[i - 1][0], tr[i][0])
        if worst > max_step or show_all:
            jumps.append((worst, l["n"], l["t"], at))

    jumps.sort(reverse=True)
    print(f"{'jump':>7}  {'label':32s} {'type':10s} between")
    for d, n, t, at in jumps:
        w = f"{at[0]:g}->{at[1]:g} Ma" if at else ""
        print(f"{d:6.1f}°  {n[:31]:32s} {t:10s} {w}")
    print(f"\n{len([j for j in jumps if j[0] > max_step])} labels move more than "
          f"{max_step:g}° in a single 5 Myr step")

    untracked.sort(reverse=True)
    print(f"\n{'span':>6}  {'label':32s} {'type':10s} window")
    for span, n, t, a1, a0 in untracked:
        print(f"{span:5.0f}   {n[:31]:32s} {t:10s} {a1:g}-{a0:g} Ma")
    print(f"\n{len(untracked)} crustal labels live 40+ Myr with no plate track "
          f"(they fall back to a 90° terrain search)")


if __name__ == "__main__":
    main()
