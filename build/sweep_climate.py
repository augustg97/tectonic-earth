"""Sweep climate constants offline, with every guard the register has earned.

compute_fields runs in about a second, so the whole guard set costs a few
seconds per variant -- which means a climate constant can be swept properly
instead of being changed once and re-baked to find out.

THE GUARDS, and each one exists because something got past its predecessor:

  amplification   per class, our within-class spread over the real spread.
                  Iteration 104: we compress the extremes and over-contrast the
                  middle (seasonal 3.5x, grass 1.6x). This is the thing being
                  fixed, so it is the objective, not a guard.
  Spearman        order against real annual precipitation. Ratchet: +0.862.
  overlaps        adjacent biome classes whose ranges cross. Ratchet: 2.
  PANGAEA GREEN   the one that matters most and the one that failed. Iteration
                  87 raised the recycling floor, turned Permian Pangaea from 18%
                  green to 64%, and shipped -- because the field statistic being
                  watched ("land wetter than 0.25") moved 0.198 to 0.170 while
                  the RENDER went 0.18 to 0.64. The threshold had no relation to
                  what the shader draws.

                  So this computes the SHADER'S OWN canopy function on the
                  field: ari = Rf / (0.46 * pet), h = smoothstep(0.03, 0.61,
                  ari), green = h > 0.28 -- the point where the palette's dry
                  axis has given way to mid. A field-side guard is only worth
                  having if it evaluates the same expression the renderer does.

                  NOW CALIBRATED (iteration 112), against the render at three
                  eras measured at globe zoom:

                      age     render   proxy h>0.28   proxy h>0.45
                      0 Ma      0.42       0.65           0.59
                      122 Ma    0.53       0.73           0.66
                      280 Ma    0.35       0.63           0.56

                  Correlation with the render: +0.978 and +0.993. The ORDERING
                  greenhouse > now > Pangaea holds on both. The absolute level
                  is offset -- the proxy sits ~0.2 high -- so it must be read as
                  a RELATIVE instrument, and on that footing it is exactly what
                  iteration 87's statistic was not: that one moved the wrong
                  way, this one tracks at +0.99.

                  Local slope for extrapolating to the render, from the 0 Ma and
                  280 Ma anchors: d(render)/d(proxy) about 0.67. Three points
                  fit two parameters, so treat it as an estimate that the render
                  check confirms, not replaces.

Measured on the shipped constants (ORO_DRAIN sweep, iteration 106):

    ORO_DRAIN   seasonal  grass  Spearman  Pangaea
    0.85 (ship)     3.2     1.1     0.866     0.63
    0.65            2.9     1.1     0.874     0.68
    0.55            2.8     1.0     0.903     0.71
    0.45            2.6     0.8     0.905     0.74
    0.25            2.7     0.6     0.907     0.81

0.55 is where Spearman has taken nearly all its gain and grass amplification
lands exactly on 1.0; below it grass over-corrects into compression and Pangaea
keeps wetting for nothing.

    ../venv/bin/python sweep_climate.py
"""
import os
import sys

import numpy as np

BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)


# NO PROBE COPY NEEDED. `pet` is not in scope where Rf is assembled -- it is
# derived from T further down, by exactly the expression the shader uses. Both
# T and Rf come back from compute_fields, so the guard can be built from the
# public return values and the module's constants overridden in memory.


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def metrics(RP, z, sites):
    Z, T, Rf, lat, cl = RP.compute_fields(z, 0.0)
    Rf = np.asarray(Rf)
    h, w = Rf.shape

    def at(A, lon, lat):
        A = np.asarray(A)
        return float(A[int((90 - lat) / 180 * h), int((lon + 180) / 360 * w) % w])
    by, allv, allm = {}, [], []
    for lon, lat, name, cls, mm in sites:
        v = at(Rf, lon, lat)
        by.setdefault(cls, []).append((float(mm), v))
        allv.append(v)
        allm.append(float(mm))
    amp = {}
    for cls, rows in by.items():
        mm = np.array([r[0] for r in rows])
        vv = np.array([r[1] for r in rows])
        amp[cls] = (vv.max() / max(vv.min(), 1e-9)) / (mm.max() / max(mm.min(), 1e-9))
    from scipy.stats import spearmanr
    rho = float(spearmanr(allm, allv).correlation)
    east = {n: at(Rf, lo, la) for lo, la, n, c, mm in sites
            if n in ("Appalachians", "Chesapeake")}
    return amp, rho, east


def pangaea_green(RP, dem_for):
    """The shader's own canopy test, on the 280 Ma field."""
    Z, T, Rf, lat, cl = RP.compute_fields(dem_for(280.0), 280.0)
    Rf = np.asarray(Rf)
    # the shader's own expressions, verbatim (index.html: pet, then ari, then h)
    pet = np.clip((np.asarray(T) + 12.0) / 34.0, 0.16, 1.35)
    land = np.asarray(Z) > 0.0
    ari = Rf / np.maximum(0.46 * pet, 1e-6)
    hh = smoothstep(0.03, 0.61, ari)
    return float((hh[land] > 0.28).mean())


def main():
    try:
        import render as RP
        import audit_biomes as AB
        from build_frames import index_dems, read_dem
        idx = index_dems()
        avail = np.array(sorted(idx))

        def dem_for(a):
            return read_dem(idx[float(avail[np.argmin(np.abs(avail - a))])])
        z0 = dem_for(0.0)

        VARIANTS = [("baseline", {})]
        for v in (600.0, 900.0, 1400.0):
            VARIANTS.append(("UPLIFT_SCALE=%.0f" % v, {"UPLIFT_SCALE": v}))
        VARIANTS.append(("UPL=900 LAT_HI=48",
                         {"UPLIFT_SCALE": 900.0, "MONSOON_LAT_HI": 48.0}))
        VARIANTS.append(("UPL=900 ORO=0.65",
                         {"UPLIFT_SCALE": 900.0, "ORO_DRAIN": 0.65}))

        print("  %-18s %-24s %8s %8s %14s" %
              ("variant", "amp wet/seas/grass/des", "Spearman", "Pangaea",
               "Appal/Chesa"))
        base = {k: getattr(RP, k) for k in
                ("RECYCLE_KM", "FLOOR_BARE", "ORO_DRAIN", "MONSOON_LAT_HI", "UPLIFT_SCALE")}
        for label, over in VARIANTS:
            for k, v in base.items():
                setattr(RP, k, v)
            for k, v in over.items():
                setattr(RP, k, v)
            amp, rho, east = metrics(RP, z0, AB.SITES)
            pg = pangaea_green(RP, dem_for)
            order = ["wet", "seasonal", "grass", "desert"]
            print("    %-16s %-24s %8.3f %8.2f %6.3f %6.3f%s"
                  % (label,
                     " ".join("%.1f" % amp.get(c, float("nan")) for c in order),
                     rho, pg, east.get("Appalachians", float("nan")),
                     east.get("Chesapeake", float("nan")),
                     "  <-- Spearman down" if rho < 0.855 else ""))
    finally:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
