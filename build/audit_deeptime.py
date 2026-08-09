"""Does the deep-time map still do the thing it is known for?

Written after iteration 87 shipped a change that turned Pangaea's land from 18%
green to 64% -- an arid supercontinent rendered as a green one -- and was
verified past, because every metric in the suite was watching something else.
Spearman improved, the scatter improved, the banding peak improved 26%. Nobody
asked whether the desert was still a desert. **A metric suite answers the
questions it was built to ask, and Pangaea's aridity had no metric because it
had never failed.**

It has to be measured on the RENDER, not the field. Across the sweep that
produced the regression the field's "fraction of land wetter than 0.25" moved
0.198 to 0.170 -- almost nothing -- while the rendered green fraction went from
0.64 to 0.18. The biome canopy threshold sits far below 0.25, so the field
statistic carries no information about what the map looks like.

    ../venv/bin/python shoot.py --nolabels dt_280,2,-45,280,1.5
    ../venv/bin/python audit_deeptime.py

Expectations are stated as bounds with the reasoning, not as a fitted baseline:
the Permian interior is one of the best-attested arid regions in the record, and
the app's own copy promises "Pangaea grows a desert heart on its own".
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify")

# (shot, label, max green fraction, why)
CHECKS = [
    ("dt_280", "Pangaea 280 Ma interior", 0.32,
     "Permian Pangaea is the type example of a continental desert heart"),
    ("dt_122", "Cretaceous 122 Ma", 0.75,
     "a warm, high-sea-level greenhouse world -- green is expected, but not total"),
]

# WHOLE-GLOBE framings, because the zoomed ones cannot test what they claim to.
# dt_122 is centred on 90E 30N -- central Asia, which really was arid in the
# Early Cretaceous -- so it reads 0.04 against a cap of 0.75 and would pass with
# the entire planet rendered brown. At globe zoom the same era reads 0.53. A
# threshold is only a test if the framing can reach it.
GLOBE = [
    ("g280", "Pangaea 280 Ma, globe", 0.20, 0.50,
     "arid supercontinent -- but a planet with no vegetation at all is wrong too"),
    ("g0", "present day, globe", 0.28, 0.58, "the calibration point"),
    ("g122", "Cretaceous 122 Ma, globe", 0.35, 0.75,
     "a greenhouse world must not render as a desert"),
]

# The strongest statement in this file, and the only framing-robust one: an
# ORDERING. Absolute fractions drift with every palette change; the claim that
# the Cretaceous greenhouse is greener than today and today is greener than
# Permian Pangaea is a claim about the MODEL, and it survives any palette that
# is monotone. Measured when written: 0.53 > 0.42 > 0.35.
ORDER = ["g122", "g0", "g280"]


def green(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    lum = a.mean(axis=2)
    land = (~((a[:, :, 2] > a[:, :, 1] + 6) & (a[:, :, 2] > a[:, :, 0] + 18))) \
        & (lum > 28) & (lum < 235)
    if land.sum() < 500:
        return None, None
    c = (a[:, :, 1] - a[:, :, 0])[land]
    return float(c.mean()), float((c > 0).mean())


def main():
    fails = 0
    shot_any = False
    print("  deep-time character (measured on the RENDER, never on the field):")
    for name, label, cap, why in CHECKS:
        p = os.path.join(VERIFY, name + ".png")
        if not os.path.exists(p):
            print("    %-26s no shot -- run: shoot.py --nolabels %s,..." % (label, name))
            continue
        shot_any = True
        mean, frac = green(p)
        if frac is None:
            print("    %-26s too little land in frame" % label)
            continue
        bad = frac > cap
        fails += bad
        print("    %-26s greenness %+6.2f   green fraction %.2f  (cap %.2f)%s"
              % (label, mean, frac, cap, "   <-- TOO GREEN" if bad else ""))
        if bad:
            print("        %s" % why)
    # --- globe framings, with floors as well as caps ---
    for name, label, lo, hi, why in GLOBE:
        p = os.path.join(VERIFY, name + ".png")
        if not os.path.exists(p):
            print("    %-26s no shot -- run: shoot.py --nolabels %s,..."
                  % (label, name))
            continue
        shot_any = True
        mean, frac = green(p)
        if frac is None:
            continue
        bad = frac < lo or frac > hi
        fails += bad
        print("    %-26s greenness %+6.2f   green fraction %.2f  (%.2f..%.2f)%s"
              % (label, mean, frac, lo, hi,
                 "   <-- OUT OF RANGE" if bad else ""))
        if bad:
            print("        %s" % why)

    # --- the ordering ---
    fr = {}
    for name in ORDER:
        p = os.path.join(VERIFY, name + ".png")
        if os.path.exists(p):
            _m, f = green(p)
            if f is not None:
                fr[name] = f
    if len(fr) == len(ORDER):
        seq = [fr[n] for n in ORDER]
        ok = all(a > b for a, b in zip(seq, seq[1:]))
        fails += not ok
        print("    %-26s %s%s"
              % ("greenhouse > now > Pangaea",
                 " > ".join("%.2f" % v for v in seq),
                 "" if ok else "   <-- ORDER BROKEN"))
        if not ok:
            print("        the eras no longer sort by climate; a palette or "
                  "climate change has inverted them")

    if not shot_any:
        return 1
    print("  %d of %d deep-time checks failing" % (fails, len(CHECKS) + len(GLOBE) + 1))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
