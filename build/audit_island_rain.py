"""Is an island drier than the middle of a continent at the same latitude?

It cannot be. An island sits in saturated maritime air with unlimited fetch in
every direction; a continental interior at the same latitude has had its
moisture wrung out over thousands of kilometres. Whatever the belts and the
monsoon are doing at that latitude, they are doing it to both. So across a
latitude band, island rainfall must come out at least as high as mainland
rainfall -- and this needs no external data, no reference image, and no
literature value to check, which is why it is a gate rather than a table.

THE DEFECT IT EXISTS FOR. `_rainfall` ends with three box averages that remove
row-to-row banding from the zonal march. Rainfall is only defined on land -- the
march writes `where(sea, 0.0, rain)` -- so an unmasked box read the ocean's "no
value here" as "zero rain" and drained every coast toward the water. A
continental interior never noticed: its neighbours are land and equally wet. An
island smaller than the kernel was annihilated.

Measured at Kauai before the fix: the march delivered **1.0000**, the belts
scaled it to about 0.165, and the shipped field carried **0.0055** -- against
the Sahara's 0.0049. Every Hawaiian island drew as tan desert, in the shipped
build, at one of the framings this project uses as a standing reference. The
whole chain, Tahiti, Mauritius and Fiji with it.

WHY audit_island_biomes DID NOT CATCH IT. That one asks whether the RENDER
matches the FIELD on small land. Here the field itself said desert and the
render drew it faithfully, so it passed. Two validators, two questions: that one
guards the shader, this one guards the solve.

    ../venv/bin/python audit_island_rain.py
"""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
RF_MAX = 1.6
Z_RANGE = 8000.0
# A cell is "island" when its neighbourhood is mostly water, "mainland" when it
# is nearly all land. The gap between the two thresholds is deliberate: coastal
# cells belong to neither and are excluded, because a coast is genuinely
# intermediate and including it would blunt the comparison from both sides.
NEAR = 5
# SMALL vs LARGE ISLAND, not island vs mainland. The first version of this
# compared islands against continental interiors at the same latitude, and it
# PASSED on the broken field -- at 15-30 degrees the mainland median is the
# Sahara and Arabia, so anything maritime looks wet beside it. The defect is
# not "islands are dry", it is "SMALL islands are dry", because the leak scales
# with how much of the smoothing kernel is ocean. Comparing small islands
# against large ones holds latitude and maritime setting fixed and varies only
# the thing the mechanism depends on.
SMALL_MAX_LAND = 0.10
LARGE_MIN_LAND = 0.45
LARGE_MAX_LAND = 0.95
BANDS = [(0, 15), (15, 30), (30, 45), (45, 60)]
# A small island may be somewhat drier than a large one for real reasons -- a
# big island builds its own orography and its own convection. 0.60 allows a
# large real difference and still fails the defect by a wide margin: measured on
# the broken field the small-island median ran at 0.10-0.24 of the large-island
# median in the tropical and subtropical bands.
MIN_RATIO = 0.60
# Frames to check. All of them is 251 decodes of two fields; these span the
# eras and include the present, which is the one with real islands to test.
FRAMES = ["phan_0000", "phan_0040", "phan_0120", "phan_0280", "pre_0600"]


def load(tag):
    rp = os.path.join(FIELDS, tag + "_r.webp")
    ep = os.path.join(FIELDS, tag + "_e.avif")
    if not (os.path.exists(rp) and os.path.exists(ep)):
        return None, None
    R = np.asarray(Image.open(rp).convert("L")).astype(float) / 255.0 * RF_MAX
    e = np.asarray(Image.open(ep).convert("L")).astype(float) / 255.0
    d = e * 2.0 - 1.0
    Z = np.sign(d) * d * d * Z_RANGE
    Z = np.array(Image.fromarray(Z.astype(np.float32)).resize(
        (R.shape[1], R.shape[0]), Image.BILINEAR))
    return R, Z


def main():
    if not glob.glob(os.path.join(FIELDS, "*_r.webp")):
        print("  audit_island_rain: no rainfall fields present")
        return 1
    print("  does rainfall depend on how BIG an island is? (it must not)")
    print("    %-11s %7s %11s %11s %8s %7s"
          % ("frame", "band", "small isl", "large isl", "ratio", "n small"))
    fails, checked = [], 0
    for tag in FRAMES:
        R, Z = load(tag)
        if R is None:
            print("    %-11s no field -- NOT TESTED" % tag)
            fails.append(tag + " (missing)")
            continue
        H, W = R.shape
        land = Z > 0
        frac = ndimage.uniform_filter(land.astype(float), NEAR * 2 + 1)
        isl = land & (frac <= SMALL_MAX_LAND)
        main = land & (frac >= LARGE_MIN_LAND) & (frac <= LARGE_MAX_LAND)
        lat = np.abs(np.linspace(90, -90, H))[:, None] * np.ones((1, W))
        for lo, hi in BANDS:
            b = (lat >= lo) & (lat < hi)
            i, m = isl & b, main & b
            # Both populations need enough cells to have a median worth
            # comparing. Reported when they do not, never skipped in silence.
            if i.sum() < 40 or m.sum() < 100:
                print("    %-11s %3d-%-3d  too few cells (small %d, large %d)"
                      " -- NOT TESTED" % (tag, lo, hi, i.sum(), m.sum()))
                continue
            iv, mv = float(np.median(R[i])), float(np.median(R[m]))
            checked += 1
            ratio = iv / max(mv, 1e-6)
            bad = ratio < MIN_RATIO
            if bad:
                fails.append("%s %d-%d (%.2f)" % (tag, lo, hi, ratio))
            print("    %-11s %3d-%-3d %11.4f %11.4f %8.2f %7d %s"
                  % (tag, lo, hi, iv, mv, ratio, int(i.sum()),
                     "SMALL ISLANDS DRAINED" if bad else ""))
    if not checked:
        print("  audit_island_rain: nothing could be tested")
        return 1
    if fails:
        print("  %d band(s) have small islands drier than large ones at the "
              "same latitude: %s" % (len(fails), ", ".join(fails)))
        print("  That is not a climate, it is moisture leaking into the ocean.")
        return 1
    print("  islands hold their rain in all %d tested bands" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
