"""Does the rainfall field SEPARATE the world's biomes at all?

The lesson this exists to enforce (MODEL-GAPS Q iteration 39): when the classes
OVERLAP in the input, no threshold placed anywhere can separate them, and every
round spent moving the canopy curve is moving a boundary through a region where
the field carries no information. The tell is cheap -- sort the reference sites
by the index and look for inversions -- and it was the measurement that ended
months of palette tuning. It has never been a script, so every climate change
since has been checked by hand or not at all.

Run it before and after ANY change to render.py's solve:

    ../venv/bin/python audit_biomes.py            # present day
    ../venv/bin/python audit_biomes.py 280        # any age

Reports the separation margin between the driest wet-class site and the wettest
dry-class site. A NEGATIVE margin means the field cannot support the biome map
however the shader is tuned. It prints the whole table every run, pass or fail:
a validator that shows its number only when it fails is unreadable exactly when
it passes, and you cannot see a margin narrowing until it has already gone.
"""
import sys

import numpy as np

sys.path.insert(0, ".")
import build_fields as BF
import epeiric as EP
import paleo_tracks
from build_frames import index_dems, read_dem
from render import compute_fields, resample_dem

# (lon, lat, name, class). Classes are ordered wet -> dry; the field has to keep
# them in this order. Sites are chosen to be unambiguous and far from coasts and
# class boundaries, so a failure here is the field's and not the sampling's.
SITES = [
    (-62.0, -3.0, "Amazon basin", "wet"),
    (20.0, 0.0, "Congo basin", "wet"),
    (113.0, 1.0, "Borneo", "wet"),
    (-77.0, 1.0, "Choco", "wet"),
    (-49.0, -15.0, "Cerrado", "seasonal"),
    (78.0, 21.0, "Deccan", "seasonal"),
    (32.0, -13.0, "Miombo", "seasonal"),
    (105.0, 15.0, "Indochina", "seasonal"),
    (-98.0, 39.0, "Great Plains", "grass"),
    (30.0, 49.0, "Pontic steppe", "grass"),
    (-63.0, -35.0, "Pampas", "grass"),
    (70.0, 48.0, "Kazakh steppe", "grass"),
    (25.0, 25.0, "Sahara", "desert"),
    (50.0, 21.0, "Rub al Khali", "desert"),
    (-69.0, -24.0, "Atacama", "desert"),
    (103.0, 43.0, "Gobi", "desert"),
    (135.0, -25.0, "Australian interior", "desert"),
    (-113.0, 39.0, "Great Basin", "desert"),
]
ORDER = ["wet", "seasonal", "grass", "desert"]


def solve(age):
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    z = read_dem(idx[float(avail[np.argmin(np.abs(avail - max(age, 0)))])])
    zc = EP.carve(resample_dem(z, BF.ELEV_H, BF.ELEV_W), age, rec)[::-1]
    return compute_fields(zc, age, BF.CLIM_H, BF.CLIM_W)[2]


def main():
    age = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    Rf = solve(age)
    H, W = Rf.shape
    rows = []
    for lon, lat, name, cls in SITES:
        r = int((90 - lat) / 180 * H)
        c = int((lon + 180) / 360 * W)
        # A small box, because one texel is 26 km and a single sample lands
        # wherever the reconstruction happens to put a pixel.
        v = float(np.median(Rf[max(r - 2, 0):r + 3, max(c - 2, 0):c + 3]))
        rows.append((cls, v, name))

    print("  reference sites at %s Ma, by class (wet -> dry):" % age)
    for cls in ORDER:
        vs = [(v, n) for c, v, n in rows if c == cls]
        vs.sort(reverse=True)
        print("    %-9s %s" % (cls, "  ".join("%s %.3f" % (n, v) for v, n in vs)))

    fails = 0
    print("  separation between adjacent classes:")
    for a, b in zip(ORDER, ORDER[1:]):
        lo_a = min(v for c, v, _ in rows if c == a)      # driest of the wetter class
        hi_b = max(v for c, v, _ in rows if c == b)      # wettest of the drier class
        margin = lo_a - hi_b
        bad = margin <= 0
        fails += bad
        print("    %-9s driest %.3f  vs  %-9s wettest %.3f   margin %+.3f%s"
              % (a, lo_a, b, hi_b, margin, "   <-- OVERLAP" if bad else ""))
    span = max(v for _, v, _ in rows) - min(v for _, v, _ in rows)
    print("  full span %.3f across %d sites, %d overlapping boundaries"
          % (span, len(rows), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
