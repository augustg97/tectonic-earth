"""Does our sea floor carry the relief the real one does, band by band?

Queue item 2 asked whether the ocean floor reads like Google Earth's. The
premise being tested was that our synthetic abyssal fabric is far too strong --
that the "commas" covering the Hawaii framing are drowning the real bathymetry.

Measured against the source the app is built from (the 6-minute PaleoDEM at
0 Ma, which for the present day IS real bathymetry), the premise is largely
false. Median ratio 1.21 across four provinces and two bands:

    box                    band          source    ours   ratio
    equatorial Atlantic    110-440 km       371     282    0.76
                           39-110 km        128     126    0.99
    Hawaii plain           110-440 km       478     813    1.70
                           39-110 km        296     372    1.25
    Scotia / Drake         110-440 km       795     921    1.16
                           39-110 km        370     426    1.15
    central Pacific        110-440 km       175     235    1.34
                           39-110 km         91     141    1.55

WHY ONLY THESE TWO BANDS. Below about 13-39 km the source cannot be read: real
abyssal hills are 50-300 m at 5-10 km wavelength, which a 6-minute grid does not
resolve, so a ratio there measures the source's resolution and not our fidelity.
Above 440 km the box itself sets the scale. The two bands in between are
resolved by both sides and are the only ones that carry information.

The residual signal, such as it is: the equatorial Atlantic runs UNDER at the
large scale (0.76) while every Pacific box runs over. That is the fracture-zone
belt -- 100 km-scale linear troughs the source resolves fully -- being
under-drawn relative to synthetic fabric elsewhere. It is a 24% deficit, not the
missing feature it looked like by eye.

**THE ORIENTATION CHECK IS A PRECONDITION, NOT A COURTESY.** The first version
of this measurement reported our texture at 2.7-4.3x the real relief, with a
table, and it was entirely false: `read_dem` returns latitude ASCENDING (row 0
is the south pole) and `resample_dem` flips it, so indexing the source north-up
compares opposite hemispheres. Everest against the southern Indian Ocean. The
script refuses to report anything until four landmarks come back with the right
sign on both sides.

    ../venv/bin/python audit_ocean_relief.py
"""
import os
import sys

import numpy as np
from PIL import Image

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELD = os.path.join(HERE, "..", "web", "fields", "phan_0000_e.avif")
Z_RANGE = 8000.0

# (name, lon, lat, expected sign) -- the precondition
LANDMARKS = [("Everest", 86.9, 28.0, +1), ("Sahara", 10.0, 23.0, +1),
             ("Mariana Trench", 142.3, 11.4, -1), ("Hawaii", -155.5, 19.6, +1)]

BOXES = [("equatorial Atlantic", -35, -10, -5, 5),
         ("Hawaii plain", -170, -150, 15, 30),
         ("Scotia / Drake", -60, -35, -62, -52),
         ("central Pacific", -140, -120, -20, 0)]
BANDS = [(1.0, 4.0, "110-440 km"), (0.35, 1.0, "39-110 km")]

# Ratios seen when this was first measured correctly. A band drifting far from
# these means the sea floor changed; it does not by itself mean it got worse.
BASE_MEDIAN = 1.21
TOLERANCE = 0.35


def at(A, lon, lat):
    h, w = A.shape
    return float(A[int((90 - lat) / 180 * h), int((lon + 180) / 360 * w) % w])


def box(A, lo0, lo1, la0, la1):
    h, w = A.shape
    return A[int((90 - la1) / 180 * h):int((90 - la0) / 180 * h),
             int((lo0 + 180) / 360 * w):int((lo1 + 180) / 360 * w)]


def bandsd(a, deg_per_cell, lo_deg, hi_deg):
    """sd of the component between two angular wavelengths."""
    def blur(x, d):
        n = max(int(round(d / deg_per_cell)), 1)
        if n < 2:
            return x.copy()
        return np.array(Image.fromarray(x.astype(np.float32))
                        .resize((max(x.shape[1] // n, 2), max(x.shape[0] // n, 2)),
                                Image.BILINEAR)
                        .resize((x.shape[1], x.shape[0]), Image.BILINEAR))
    return float((blur(a, lo_deg) - blur(a, hi_deg)).std())


def main():
    if not os.path.exists(FIELD):
        print("  audit_ocean_relief: no shipped present-day field to check")
        return 1
    from build_frames import index_dems, read_dem
    from fieldpack import dec_elev
    src = read_dem(index_dems()[0.0])[::-1]          # -> north-up
    ours = dec_elev(np.asarray(Image.open(FIELD).convert("L")).astype(float) / 255.0)

    bad = [n for n, lo, la, sg in LANDMARKS
           if np.sign(at(src, lo, la)) != sg or np.sign(at(ours, lo, la)) != sg]
    if bad:
        print("  ORIENTATION CHECK FAILED at %s -- refusing to report ratios."
              % ", ".join(bad))
        print("  read_dem returns latitude ASCENDING; the source needs [::-1].")
        return 1
    print("  orientation verified on %d landmarks" % len(LANDMARKS))

    print("  abyssal relief by wavelength, sd in metres:")
    print("    %-22s %-12s %7s %7s %6s" % ("box", "band", "source", "ours", "ratio"))
    ratios = []
    for nm, a, b, c, d in BOXES:
        s, o = box(src, a, b, c, d), box(ours, a, b, c, d)
        for lo, hi, lab in BANDS:
            ss = bandsd(s, 180.0 / src.shape[0], lo, hi)
            oo = bandsd(o, 180.0 / ours.shape[0], lo, hi)
            ratios.append(oo / max(ss, 1e-9))
            print("    %-22s %-12s %7.0f %7.0f %6.2f"
                  % (nm if lo == 1.0 else "", lab, ss, oo, ratios[-1]))
    med = float(np.median(ratios))
    off = abs(med - BASE_MEDIAN)
    print("  median ratio %.2f  (was %.2f when first measured correctly)"
          % (med, BASE_MEDIAN))
    if off > TOLERANCE:
        print("  <-- the sea floor's relief moved %.2f from where it was; that is"
              " a change worth explaining, in either direction" % off)
        return 1
    print("  within %.2f of the recorded value -- the sea floor still carries"
          " roughly the relief the real one does" % TOLERANCE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
