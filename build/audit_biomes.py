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

# (lon, lat, name, class, REAL annual precipitation in mm). The millimetres are
# what makes this a gate rather than a vibe: class ordering alone passed a field
# in which the Kazakh steppe (300 mm) scored 0.014 while the north Caspian
# steppe (280 mm) scored 0.234 -- less rain, seventeen times the value -- because
# both are "grass" and the check only asked whether the classes were ordered.
# Sites are chosen unambiguous and away from class boundaries and coasts.
#
# TWO of these were wrong when written, and both passed unnoticed. 30E/49N was
# labelled "Pontic steppe" and is Kyiv forest-steppe at ~620 mm; -77/1 was
# labelled "Choco" and lands at 2160 m ON THE ANDEAN CREST, spanning 511 to
# 3772 m, when the Choco is a coastal lowland at ~50 m. A reference list is
# data too, so terrain_sanity() below audits it on every run.
SITES = [
    (-62.0, -3.0, "Amazon basin", "wet", 2300),
    (20.0, 0.0, "Congo basin", "wet", 1700),
    (113.0, 1.0, "Borneo", "wet", 3200),
    (-76.6, 5.7, "Choco", "wet", 6000),
    (-49.0, -15.0, "Cerrado", "seasonal", 1500),
    (78.0, 21.0, "Deccan", "seasonal", 900),
    (32.0, -13.0, "Miombo", "seasonal", 1000),
    (105.0, 15.0, "Indochina", "seasonal", 1500),
    (-98.0, 39.0, "Great Plains", "grass", 500),
    (45.0, 47.0, "Don steppe", "grass", 350),
    (-63.0, -35.0, "Pampas", "grass", 900),
    (70.0, 48.0, "Kazakh steppe", "grass", 300),
    (25.0, 25.0, "Sahara", "desert", 15),
    (50.0, 21.0, "Rub al Khali", "desert", 40),
    (-69.0, -24.0, "Atacama", "desert", 5),
    (103.0, 43.0, "Gobi", "desert", 130),
    (135.0, -25.0, "Australian interior", "desert", 200),
    (-113.0, 39.0, "Great Basin", "desert", 230),
]
ORDER = ["wet", "seasonal", "grass", "desert"]

# The ratchet. Raise these when a change earns it, in the same commit.
BASE_OVERLAPS = 2
BASE_SPEARMAN = 0.862


def solve(age):
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    z = read_dem(idx[float(avail[np.argmin(np.abs(avail - max(age, 0)))])])
    zc = EP.carve(resample_dem(z, BF.ELEV_H, BF.ELEV_W), age, rec)[::-1]
    return (compute_fields(zc, age, BF.CLIM_H, BF.CLIM_W)[2],
            resample_dem(zc, BF.CLIM_H, BF.CLIM_W))


def main():
    age = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    Rf, Z = solve(age)
    H, W = Rf.shape
    rows = []
    for lon, lat, name, cls, mm in SITES:
        r = int((90 - lat) / 180 * H)
        c = int((lon + 180) / 360 * W)
        # A small box, because one texel is 26 km and a single sample lands
        # wherever the reconstruction happens to put a pixel.
        v = float(np.median(Rf[max(r - 2, 0):r + 3, max(c - 2, 0):c + 3]))
        rows.append((cls, v, name, mm))

    # THE LIST AUDITS ITSELF. Two sites were wrong before this existed, and both
    # produced "defects" that were chased into the model before anyone checked
    # where the sample actually landed.
    if age == 0:
        bad = []
        for lon, lat, name, cls, mm in SITES:
            r = int((90 - lat) / 180 * H)
            c = int((lon + 180) / 360 * W)
            b = Z[max(r - 2, 0):r + 3, max(c - 2, 0):c + 3]
            if b.max() <= 0:
                bad.append("%s is in the sea" % name)
            elif float(np.median(b)) > 1600 and cls in ("wet", "seasonal"):
                bad.append("%s sits at %.0f m, too high for a lowland biome"
                           % (name, float(np.median(b))))
        if bad:
            print("  SITE LIST SUSPECT: " + "; ".join(bad))
        else:
            print("  site list: all 18 land on terrain consistent with their class")

    print("  reference sites at %s Ma, by class (wet -> dry):" % age)
    for cls in ORDER:
        vs = [(v, n) for c, v, n, _ in rows if c == cls]
        vs.sort(reverse=True)
        print("    %-9s %s" % (cls, "  ".join("%s %.3f" % (n, v) for v, n in vs)))

    fails = 0
    print("  separation between adjacent classes:")
    for a, b in zip(ORDER, ORDER[1:]):
        lo_a = min(v for c, v, _, _ in rows if c == a)      # driest of the wetter class
        hi_b = max(v for c, v, _, _ in rows if c == b)      # wettest of the drier class
        margin = lo_a - hi_b
        bad = margin <= 0
        fails += bad
        print("    %-9s driest %.3f  vs  %-9s wettest %.3f   margin %+.3f%s"
              % (a, lo_a, b, hi_b, margin, "   <-- OVERLAP" if bad else ""))
    span = max(v for _, v, _, _ in rows) - min(v for _, v, _, _ in rows)
    print("  full span %.3f across %d sites, %d overlapping boundaries"
          % (span, len(rows), fails))

    # RANK AGREEMENT WITH REALITY. The class check only asks whether four groups
    # are ordered; this asks whether the field agrees with the actual rainfall
    # site by site, which is the question. Spearman, because the model's units
    # are companded and only the ordering is meaningful.
    mv = np.array([v for _, v, _, _ in rows])
    rv = np.array([float(mm) for _, _, _, mm in rows])
    rm = np.argsort(np.argsort(mv)).astype(float)
    rr = np.argsort(np.argsort(rv)).astype(float)
    rho = float(np.corrcoef(rm, rr)[0, 1])
        # WITHIN-CLASS AMPLIFICATION -- the statistic that located the close-zoom
    # colour defect. Spearman and the class margins both measure ORDER and
    # SEPARATION between classes; neither notices that two sites with the SAME
    # rainfall can land far apart. Measured: Cerrado and Indochina both get
    # 1500 mm and our field puts them 4.9x apart, and Don steppe (350 mm) scores
    # 4.3x the Great Plains (500 mm). Per class, the ratio of our spread to the
    # real one:
    #
    #     wet       real 3.5x   ours 1.5x   0.4x  (compressed)
    #     seasonal  real 1.7x   ours 5.8x   3.5x  <-- over-contrasted
    #     grass     real 3.0x   ours 4.8x   1.6x  <-- over-contrasted
    #     desert    real 46x    ours 10x    0.2x  (compressed)
    #
    # Compressive at both ends and over-contrasted in the middle, which is
    # exactly where the Great Plains and the Alps sit -- and is why their
    # rendered colour spreads 3-4x the reference at close zoom.
    print("  within-class amplification (our spread / the real spread):")
    _by = {}
    for _c, _v, _n, _m in rows:
        _by.setdefault(_c, []).append((float(_m), _v))
    for _c, _rs in _by.items():
        _mm = np.array([x[0] for x in _rs]); _vv = np.array([x[1] for x in _rs])
        _rr = _mm.max() / max(_mm.min(), 1e-9)
        _vr = _vv.max() / max(_vv.min(), 1e-9)
        print("    %-9s real %5.1fx   ours %5.1fx   %.1fx%s"
              % (_c, _rr, _vr, _vr / max(_rr, 1e-9),
                 "   <-- over-contrasted" if _vr / max(_rr, 1e-9) > 1.4 else ""))
    print("  Spearman rank correlation with real annual precipitation: %+.3f" % rho)
    worst = sorted(zip(np.abs(rm - rr), [n for _, _, n, _ in rows], mv, rv),
                   reverse=True)[:4]
    print("  worst rank inversions (rank gap, site, model, real mm):")
    for g, n, m, r in worst:
        print("    %2d  %-22s %.3f   %4.0f mm" % (int(g), n, m, r))

    # A RATCHET, NOT A PASS MARK. Two boundaries have overlapped since this file
    # was written and the field has never separated all four classes; failing on
    # that would block every deploy and teach everyone to set SKIP_AUDIT. What
    # must not happen is going BACKWARDS, so the gate holds the best state
    # reached and complains only below it. Move these two numbers in the same
    # commit as the change that earns them, and say why.
    if age != 0:
        return 0                      # the baseline is calibrated on present day
    bad = []
    if fails > BASE_OVERLAPS:
        bad.append("class overlaps %d, baseline %d" % (fails, BASE_OVERLAPS))
    if rho < BASE_SPEARMAN - 0.004:   # tolerance for solver noise
        bad.append("Spearman %+.3f, baseline %+.3f" % (rho, BASE_SPEARMAN))
    if bad:
        print("  MOVED BACKWARDS: " + "; ".join(bad))
        return 1
    print("  at or better than baseline (%d overlaps, Spearman %+.3f)"
          % (BASE_OVERLAPS, BASE_SPEARMAN))
    return 0


if __name__ == "__main__":
    sys.exit(main())
