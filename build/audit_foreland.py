"""Does the foreland basin land on the right side, and do the ranges stay put?

Two questions, and the second is a promise rather than a preference: the brief
for H5 was to build a foreland WITHOUT altering the final elevations of mountain
ranges. That is checkable, so it is checked here rather than asserted.

    ../venv/bin/python audit_foreland.py
"""
import sys

import numpy as np

import build_foreland as BF
import plate_field as PF

# Present-day forelands, where the answer is not in doubt. Each is (name, what
# the world does, a box on the expected side, a box on the other side).
CASES = [
    ("Himalaya", "Ganges plain, S", (78, 88, 24, 27), (80, 88, 34, 39)),
    ("Andes", "Chaco-Beni, E", (-65, -61, -22, -16), (-73, -70.8, -22, -16)),
    ("Alps", "Po basin, S", (8, 12, 44, 45.4), (9, 13, 48, 50)),
    ("Zagros", "Mesopotamia, SW", (44, 48, 29.5, 32.5), (53, 57, 33, 36)),
    ("Rockies", "Great Plains, E", (-104, -99, 40, 48), (-121, -117, 40, 48)),
]

GATE_AGES = [0, 50, 100, 200, 300, 400, 500]


def run():
    LON, LAT = PF._grid(BF.FW, BF.FH)

    def box(a, lo0, lo1, la0, la1):
        m = (LON >= lo0) & (LON <= lo1) & (LAT >= la0) & (LAT <= la1)
        return a[m]

    print("POLARITY -- which side of the range does the basin fall on? (0 Ma)\n")
    down, _up = BF.deflection(0)
    right = wrong = 0
    for name, what, eb, ob in CASES:
        e, o = box(down, *eb), box(down, *ob)
        if e.mean() > o.mean() + 12:
            v, right = "CORRECT", right + 1
        elif o.mean() > e.mean() + 12:
            v, wrong = "WRONG SIDE", wrong + 1
        else:
            v = "weak"
        print("  %-9s %-17s expected %5.1f m | other %5.1f m   %s"
              % (name, what, e.mean(), o.mean(), v))
    print("\n  %d correct, %d weak, %d WRONG SIDE" % (right, len(CASES) - right - wrong, wrong))

    print("\nTHE PROMISE -- no mountain elevation may move.\n")
    print("  age | cells >=%.0f m altered | land%%      >1km%%      >2km%%      >3km%%"
          % BF.GATE_HI)
    bad = 0
    for age in GATE_AGES:
        z = BF._elev(age, BF.FW, BF.FH)
        if z is None:
            continue
        d, u = BF.deflection(age)
        zf = z - d + u
        moved = int((np.abs(zf - z)[z >= BF.GATE_HI] > 0.5).sum())
        bad += moved
        # THE SECOND PROMISE (WP-10, D1): a filled foreland is a plain, not a
        # hole, so the moat may never drown ground that is dry in the field.
        # Measured before the shader floor existed: the Gangetic plain went to
        # -54 m at Patna and 0.76% of present-day land fell below sea level.
        # `raw` is what the deflection alone would do; `drowned` is what the
        # shader draws, with its floor of 30 m above the water surface applied
        # exactly as elevDetail() applies it. The second must be zero.
        land = z >= 0.0
        raw = int((land & (zf < 0.0)).sum())
        zs = np.where(land & (d > 0.0), np.maximum(zf, np.minimum(z, 30.0)), zf)
        drowned = int((land & (zs < 0.0)).sum())
        bad += drowned
        print("       | dry ground the raw moat would drown: %6d cells (%.2f%% of "
              "land); after the shader floor: %d" % (raw, 100.0 * raw / max(1, land.sum()),
                                                    drowned))
        def f(a, t):
            return 100.0 * float((a > t).mean())
        print("  %4d | %19d | %5.2f→%5.2f  %5.3f→%5.3f  %5.3f→%5.3f  %5.3f→%5.3f"
              % (age, moved, f(z, 0), f(zf, 0), f(z, 1000), f(zf, 1000),
                 f(z, 2000), f(zf, 2000), f(z, 3000), f(zf, 3000)))
    print()
    if bad:
        print("  FAIL: %d high-ground cells were altered or dry cells drowned." % bad)
    else:
        print("  PASS: no cell at or above %.0f m moved, at any age tested."
              % BF.GATE_HI)
        print("  Land area falls slightly because a foreland basin IS low ground —")
        print("  that is the feature, and it is confined below the gate.")
    return 1 if (bad or wrong) else 0


if __name__ == "__main__":
    raise SystemExit(run())
