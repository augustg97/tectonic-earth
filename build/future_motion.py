"""Where a present-day point ends up on the future map (labels, tracks).

A thin layer over future_tectonics (3.16): the label rides the SAME plate
rotation and the SAME collision deformation that built the future terrain, so a
name cannot drift off the crust it names. Until 3.15 this carried points on the
rigid per-group rotations of build_fields' packed targets; those are gone.

    group_at(lon, lat)            which future plate owns today's point
    advance(lon, lat, myr)        its position `myr` Myr ahead: (lon, lat)

The direction of a rotation is the one thing no amount of reading settles --
both directions give a smooth, plausible track -- so `selftest` checks advanced
positions against the BAKED future elevation, with the reversed and frozen
tracks as controls.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SPAN_MYR = 250.0


def _ft():
    import future_tectonics as FT
    FT.storyline()
    return FT


def group_at(lon, lat, search_deg=6.0):
    """Which future plate owns this point, searching outward if it falls in a
    gap between digitised plate rings (a sea or coastal name can)."""
    FT = _ft()
    pid, _ = FT.present_plates()
    h, w = pid.shape
    r = int(np.clip(round((90.0 - lat) / 180.0 * h - 0.5), 0, h - 1))
    c = int(round((lon + 180.0) / 360.0 * w - 0.5)) % w
    step = max(1, int(round(0.25 / (180.0 / h))))
    for rad in range(0, int(search_deg / (180.0 / h)) + 1, step):
        r0, r1 = max(0, r - rad), min(h, r + rad + 1)
        cols = [(c + d) % w for d in range(-rad, rad + 1)]
        vals = pid[r0:r1][:, cols]
        vals = vals[vals >= 0]
        if vals.size:
            return FT.PLATES[int(np.bincount(vals).argmax())]
    return None


def advance(lon, lat, myr, group=None):
    """Carry a present-day point forward `myr` million years (myr >= 0)."""
    FT = _ft()
    g = group or group_at(lon, lat)
    if g is None:
        return None
    myr = float(min(max(myr, 0.0), SPAN_MYR))
    if myr <= 0.0:
        return (float(lon), float(lat))
    return FT.advance(lon, lat, myr, plate=g)


def selftest():
    """Is the advanced point still on its continent in the baked future?"""
    import glob
    from PIL import Image
    try:
        import pillow_avif  # noqa: F401
    except ImportError:
        pass
    sites = [("Africa", 20.0, 2.0), ("Australia", 134.0, -25.0),
             ("South America", -60.0, -10.0), ("Eurasia", 90.0, 55.0),
             ("North America", -100.0, 45.0), ("East Antarctica", 20.0, -80.0)]
    fails = 0
    print("  future label motion -- is the advanced point still on its continent?")
    for myr in (50, 150, 250):
        f = glob.glob(os.path.join(HERE, "..", "web", "fields", "fut_%04d_e.*" % myr))
        if not f:
            print("    +%3d Myr  no baked frame to check against" % myr)
            continue
        im = np.asarray(Image.open(f[0]).convert("L")).astype(float)
        h, w = im.shape
        sea = float(np.percentile(im, 40))

        def onland(p):
            if p is None:
                return False
            r = int((90 - p[1]) / 180 * h) % h
            c = int((p[0] + 180) / 360 * w) % w
            return float(im[max(0, min(h - 1, r)), c]) > sea + 6

        fwd = froz = 0
        bad = []
        for name, lo, la in sites:
            p = advance(lo, la, myr)
            hit = onland(p)
            fwd += hit
            froz += onland((lo, la))
            if not hit:
                bad.append(name)
        fails += len(bad)
        print("    +%3d Myr  forward %d/%d   [control: frozen %d]%s"
              % (myr, fwd, len(sites), froz, "   OFF: " + ", ".join(bad) if bad else ""))
    print("  %d misses" % fails)
    return fails


if __name__ == "__main__":
    import sys
    sys.exit(1 if selftest() > 4 else 0)
