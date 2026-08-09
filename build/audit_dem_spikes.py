"""Is there a mountain in the trench? Check the source DEMs and the shipped field.

FOUND ON SCREEN, not by a metric: a tan desert island in the middle of the
Mariana Trench at 143E 12N, where Google Earth shows the deepest water on the
planet. The 6-minute PaleoDEM stores the Challenger Deep axis as **+10500 m** --
the magnitude of the depth with the sign lost -- flanked by -9000 on both sides,
and the pipeline carried it through to a shipped +3349 m of dry land.

2,219 such cells across 21 of the 109 source ages. It had survived every check
in the suite because nothing ever asked "is any cell absurdly higher than its own
neighbourhood" -- the elevation gates are all about ranges and distributions,
and a 10 km spike sits comfortably inside a range that has to admit Everest.

TWO SIDES, BOTH CHECKED, because a build-side repair with no render-side check
is how the last one nearly shipped doing nothing:

  1. the SOURCE, after repair_spikes: no cell may stand 5 km above the median of
     its own 9-cell neighbourhood. At 10 km per cell nothing on Earth does.
  2. the SHIPPED FIELD: no cell may STEP 5 km from the one next to it. This is
     the one that catches a repair that silently stopped running, because it
     reads what the app actually loads. It is a step rather than an excursion
     for a reason -- see check_shipped.

Check 1 deliberately does NOT use an absolute ceiling. There are two different
things above 9,000 m in this data and only one is a defect: the fill (+10500 on
a -8000 rim, an 18.5 km step) and the real 30 Ma Himalaya (9,300-9,600 m on a
9,000 m rim, continuous with its surroundings). A ceiling flattens both.

    ../venv/bin/python audit_dem_spikes.py [--source]
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
Z_RANGE = 8000.0
JUMP = 5000.0


def dec(e):
    d = e * 2.0 - 1.0
    return np.sign(d) * d * d * Z_RANGE


def check_source():
    """Slow (109 DEMs x up to 8 repair passes) and opt-in; not part of the gate.

    Uses build_frames' OWN threshold, so the check and the repair can never
    drift apart -- a validator with its own copy of a constant is a validator
    that eventually tests something else.

    KNOWN RESIDUE, measured rather than hidden: below 8,000 m the repair leaves
    fill it cannot distinguish from terrain. At 100 Ma the big south-Pacific
    patch keeps an alternating +2,160 / -5,880 core (7,800 m, just under the
    line); 220 Ma keeps a row of +8,400 along the north pole; 160 Ma the same at
    the south. Lowering the threshold to reach them starts flattening real
    island-arc margins, which cost more than they fix. They are reported here so
    the next attempt starts from a number.
    """
    from scipy.ndimage import median_filter
    from build_frames import index_dems, read_dem, SPIKE_JUMP
    idx = index_dems()
    worst, bad_ages = 0.0, 0
    for a in sorted(idx):
        z = read_dem(idx[a])
        bg = median_filter(z, size=9, mode="nearest")
        d = np.abs(z - bg)
        # The median cannot wrap in longitude, so a coastline on the
        # antimeridian reads as an excursion of the TEST, not of the data.
        d[:, :5] = 0
        d[:, -5:] = 0
        m = float(d.max())
        if m > SPIKE_JUMP:
            bad_ages += 1
            print("    %6.1f Ma  a cell stands %.0f m off its neighbourhood" % (a, m))
        worst = max(worst, m)
    print("  source DEMs: worst excursion %.0f m over %d ages (limit %.0f)"
          % (worst, len(idx), SPIKE_JUMP))
    return bad_ages


def check_shipped():
    """The same jump test, on the field the app actually loads.

    THE STEP BETWEEN ADJACENT CELLS, and it took three tries to get the
    discriminator right:

      * "land surrounded by abyssal water" flagged Hawaii, which is exactly that
        and entirely real. Every oceanic island is land in deep water.
      * "5 km above a 15-cell median, on a stride-4 grid" flagged Hawaii too:
        at 39 km pitch an island IS a jump.
      * the step between NEIGHBOURING full-resolution cells separates them
        cleanly, because the two things differ in slope by 30x. Hawaii climbs
        4.2 km over 150 km of flank -- about 590 m per 9.8 km cell. The Mariana
        fill steps from -8,000 to the +8,000 clamp in ONE cell.

    It is also O(n) with no filter, which matters: this runs over 251 frames of
    4096x2048 on every build.
    """
    files = sorted(glob.glob(os.path.join(FIELDS, "*_e.avif")))
    if not files:
        print("  audit_dem_spikes: no shipped elevation fields to check")
        return 1
    hits, checked, worst = [], 0, 0.0
    for f in files:
        z = dec(np.asarray(Image.open(f).convert("L")).astype(float) / 255.0)
        checked += 1
        # Raw metres between adjacent cells, both axes, no latitude weighting.
        # Converting to a slope would divide the east-west term by cos(lat) and
        # make ordinary polar relief look near-vertical; the quantity that
        # identifies a fill is how far the VALUE jumps, not how steep the ground
        # is, and 5 km between neighbours is anomalous at every latitude.
        d = np.zeros_like(z)
        d[1:, :] = np.abs(z[1:, :] - z[:-1, :])
        d[:, 1:] = np.maximum(d[:, 1:], np.abs(z[:, 1:] - z[:, :-1]))
        worst = max(worst, float(d.max()))
        rogue = d > JUMP
        if rogue.any():
            r, c = np.argwhere(rogue)[np.argmax(d[rogue])]
            hits.append((os.path.basename(f), int(rogue.sum()),
                         (c + 0.5) / z.shape[1] * 360 - 180,
                         90 - (r + 0.5) / z.shape[0] * 180, float(d[r, c])))
    print("  shipped fields: %d checked, worst single-cell excursion %.0f m "
          "(limit %.0f)" % (checked, worst, JUMP))
    for name, n, lo, la, v in hits[:8]:
        print("    %-22s %d cells, worst %+.0f m step between adjacent cells at "
              "lon %.1f lat %.1f" % (name, n, v, lo, la))
    if hits:
        print("  %d frames carry a cell that steps more than %.0f m in one "
              "10 km cell" % (len(hits), JUMP))
        return 1
    print("  no frame steps more than %.0f m in one cell -- no fill survived"
          % JUMP)
    return 0


def main():
    fails = 0
    if "--source" in sys.argv:
        fails += check_source()
    fails += check_shipped()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
