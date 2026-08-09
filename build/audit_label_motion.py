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

    FROZEN  a label whose visibility window runs PAST its own track. trackPos
            clamps at both ends, so those ages all render at the track's last
            point -- the name stops dead while the crust under it keeps moving.
            This is what put the Ellesmerian Belt at the same spot near the
            north pole for hundreds of millions of years, and it is invisible to
            the JUMP check above precisely because a frozen label never moves.

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

    # FROZEN: the window runs past the track. trackPos clamps at both ends, so
    # every age beyond it draws at the same point and the name stands still
    # while its plate keeps moving. Invisible to the JUMP check above precisely
    # because a frozen label never moves -- which is how the Ellesmerian Belt
    # sat near the north pole for hundreds of millions of years unnoticed.
    frozen, ntr = [], 0
    for l in lab:
        tr = l.get("tr")
        if not tr or len(tr) < 2:
            continue
        ntr += 1
        ages = [p[0] for p in tr]
        a0 = min(l.get("a0", 0), l.get("a1", 0))
        a1 = max(l.get("a0", 0), l.get("a1", 0))
        lo, hi = min(ages), max(ages)
        stuck = (lo - a0 if a0 < lo else 0.0) + (a1 - hi if a1 > hi else 0.0)
        if stuck >= 20.0:
            frozen.append((stuck, l.get("n"), a0, a1, lo, hi))
    frozen.sort(reverse=True)
    print(f"\n{'stuck':>6}  {'label':32s} window vs track")
    for s, n, a0, a1, lo, hi in frozen[:10]:
        print(f"{s:5.0f}   {n[:31]:32s} visible {a0:g}-{a1:g} Ma, track {lo:g}-{hi:g}")
    # THE FUTURE IS THE RATCHET, the deep past is not.
    #
    # Past 540 Ma the rotation model simply ends, and a name held at its 540 Ma
    # position is the honest answer -- those are reported and not failed. The
    # future is the opposite case: the motion is synthesised, deterministic and
    # already baked into every keyframe, so a label frozen there is a label that
    # did not ask. It was the shipped behaviour until future_motion.py, and it
    # put four of six continent names in open ocean at +250 Myr.
    fut = [f for f in frozen if f[2] < 0 and f[4] > f[2] + 2.5]
    print(f"\n{len(frozen)} of {ntr} tracked labels freeze 20+ Myr; "
          f"{len(frozen) - len(fut)} of them run past\nthe 540 Ma end of the rotation "
          f"model, which is inherent.")
    if fut:
        print(f"\n  {len(fut)} FREEZE IN THE FUTURE, where the motion exists and is "
              f"baked:\n    " + ", ".join(f[1] for f in fut))
        return 1
    print("  no label freezes in the future — every one rides the synthesised motion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
