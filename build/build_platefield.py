"""Bake `*_p.webp` + `platerot.json` -- the crust's OWN coordinate frame (H2).

THE DEFECT. Every ridge, crest and valley finer than the 9.8 km grid comes from
`detail3`, evaluated at `dirFromUv(uv)` -- a pure function of position on the
globe, with no age term anywhere in it. So the fine structure of a mountain
range is a property of the PLACE, not of the ROCK: as a continent drifts, it
slides out from under its own texture and the ridges stay behind. Only the
amplitude travels with the plate, because that comes from the interpolated
field. It is the same defect the sea floor was rebuilt to remove -- abyssal
fabric keyed to the present ridge instead of to the isochron -- and the land
side never got the fix.

THE FIX. Give the shader a MATERIAL COORDINATE: for each pixel, the direction on
the sphere that this piece of crust occupied at 0 Ma. Sample the noise there and
the pattern is welded to the rock, so a range keeps its own ridges wherever the
plate carries it.

WHY A SLOT RASTER AND AN ARRAY OF ROTATIONS, rather than shipping the coordinate
itself. Eight bits over 360 degrees is 1.4 degrees, about 156 km, against noise
whose finest octave resolves 1.3 km -- so a stored coordinate would not merely
be imprecise, it would quantise the whole texture into 156 km blocks. The
rotation is exact and costs one byte a pixel plus 48 vec4 uniforms, and inside a
plate it is perfectly smooth because it IS a rigid rotation.

48 SLOTS, AND WHAT HAPPENS TO THE TAIL. PALEOMAP has 223 plates at 0 Ma and 56
by 900 Ma, but the distribution is very uneven: the top 48 carry 88% of covered
cells at 0 Ma and 93-99.8% before 200 Ma. The rest are microplates. Leaving them
unrotated would leave visible patches where the texture does not ride, so every
cell outside the top 48 -- and every cell PALEOMAP does not cover at all -- is
assigned the slot of its nearest top-48 neighbour. Adjacent crust moves
similarly, so that is a fair approximation and, more to the point, a continuous
one; identity would have been a discontinuity.

THE TEXTURE IS SAMPLED THROUGH wA(), like every other crust-bound field, and
that is what keeps the material coordinate continuous across a keyframe
boundary. Looking up the plate at the WARPED position asks "which plate owns the
crust that is actually here", so at the end of one interval and the start of the
next the same rock resolves to the same plate and therefore to the same
coordinate. Sampling at the unwarped uv instead would make the noise pattern pop
at every keyframe.

    ../venv/bin/python build_platefield.py            # all past keyframes
    ../venv/bin/python build_platefield.py --selftest
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

import paleo_tracks as PT
import plate_field as PF

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "fields")
ROTJSON = os.path.join(HERE, "..", "web", "platerot.json")

PW, PH = 1024, 512
SLOTS = 48          # must equal the shader's PLATE_SLOTS and uPlateQ length
STEP = 5


def _nearest_fill(slot, known):
    """Give every unknown cell its nearest known cell's slot. Wraps in longitude.

    distance_transform_edt does not wrap, and longitude does; a non-wrapping
    fill puts a seam of wrong slots down the antimeridian, which would show as a
    strip of land whose texture does not ride with it. Tiling three times and
    taking the middle is the cheap correct answer at this resolution.
    """
    h, w = slot.shape
    k3 = np.concatenate([known, known, known], axis=1)
    s3 = np.concatenate([slot, slot, slot], axis=1)
    _d, (iy, ix) = distance_transform_edt(~k3, return_indices=True)
    filled = s3[iy, ix]
    return filled[:, w:2 * w]


def bake(age, rot, quiet=False):
    t0 = time.time()
    ids, cov = PF.plate_raster(age, PW, PH)

    # Rank by area. Ties are broken by plate id so a rebuild is deterministic --
    # otherwise the slot table could reshuffle between runs and every cached
    # texture would silently disagree with the shipped rotation array.
    vals, counts = np.unique(ids[cov], return_counts=True)
    order = sorted(zip(counts, vals), key=lambda t: (-t[0], int(t[1])))
    top = [int(v) for _c, v in order[:SLOTS]]

    slot = np.zeros((PH, PW), np.uint8)
    known = np.zeros((PH, PW), bool)
    for s, pid in enumerate(top):
        m = cov & (ids == pid)
        slot[m] = s
        known |= m
    if not known.all():
        slot = _nearest_fill(slot, known)

    quats = []
    for pid in top:
        # age -> 0 Ma: where this crust sits in the reference frame.
        ax, ang = PF.euler(rot, pid, 0.0, float(age))
        if ax is None:
            ax, ang = np.array([0.0, 0.0, 1.0]), 0.0
        quats.append([round(float(ax[0]), 6), round(float(ax[1]), 6),
                      round(float(ax[2]), 6), round(float(ang), 6)])
    while len(quats) < SLOTS:
        quats.append([0.0, 0.0, 1.0, 0.0])

    name = "phan_%04d_p.webp" % age if age <= 540 else "pre_%04d_p.webp" % age
    path = os.path.join(OUT, name)
    Image.fromarray(np.dstack([slot, slot, slot])).save(
        path, "WEBP", lossless=True, method=6)
    if not quiet:
        print("  %-22s %5.1f kB  %3d plates -> %2d slots, %4.1f%% of cells filled  %.1fs"
              % (name, os.path.getsize(path) / 1024.0, len(vals), len(top),
                 100 * float((~known).mean()), time.time() - t0))
    return quats


def _selftest():
    import pygplates as pg
    ok = True
    rot = pg.RotationModel(PT.ROT)

    # The fill must wrap. A seam of wrong slots down the antimeridian would show
    # as a strip whose texture does not ride with its continent.
    slot = np.zeros((8, 16), np.uint8)
    known = np.zeros((8, 16), bool)
    slot[4, 0] = 7
    known[4, 0] = True
    f = _nearest_fill(slot, known)
    if f[4, 15] != 7:
        print("  FAIL _nearest_fill does not wrap in longitude")
        ok = False
    if not (f == 7).all():
        print("  FAIL _nearest_fill left cells unassigned")
        ok = False

    # At age 0 the rotation must be the identity, or the present day -- the one
    # frame we can check by eye against a real map -- would have its texture
    # rotated off the crust it belongs to.
    q = bake(0, rot, quiet=True)
    if max(abs(r[3]) for r in q) > 1e-9:
        print("  FAIL age 0 rotations are not identity")
        ok = False

    # Rotating a point by its own slot's rotation must land where pygplates puts
    # it. This is the whole contract; if it drifts, the texture rides the wrong
    # crust and nothing downstream would say so.
    ids, cov = PF.plate_raster(200, PW, PH)
    vals, counts = np.unique(ids[cov], return_counts=True)
    order = sorted(zip(counts, vals), key=lambda t: (-t[0], int(t[1])))
    worst = 0.0
    for _c, pid in order[:6]:
        ax, ang = PF.euler(rot, int(pid), 0.0, 200.0)
        fr = rot.get_rotation(0.0, int(pid), 200.0)
        for lon, lat in ((10, 20), (-70, -30), (120, 45)):
            mine = PF.lonlat(PF.rodrigues(PF.unit(np.array([lon]), np.array([lat])), ax, ang))
            p = fr * pg.PointOnSphere(float(lat), float(lon))
            tla, tlo = p.to_lat_lon()
            worst = max(worst, abs((mine[0][0] - tlo + 180) % 360 - 180) + abs(mine[1][0] - tla))
    if worst > 1e-6:
        print("  FAIL slot rotation disagrees with pygplates by %.3g deg" % worst)
        ok = False
    else:
        print("  slot rotation vs pygplates: max %.2e deg" % worst)

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


def main():
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    import pygplates as pg
    rot = pg.RotationModel(PT.ROT)
    args = [int(a) for a in sys.argv[1:] if not a.startswith("--")]
    ages = args or list(range(0, 1001, STEP))
    print("baking %d plate-slot fields at %dx%d, %d slots" % (len(ages), PW, PH, SLOTS))
    t0 = time.time()
    table = {}
    for age in ages:
        table[str(age)] = bake(age, rot)
    if not args and os.path.exists(ROTJSON):
        table = {**json.load(open(ROTJSON)), **table}
    with open(ROTJSON, "w") as fh:
        json.dump({"slots": SLOTS, "rot": table}, fh, separators=(",", ":"))
    print("\n  %d fields, platerot.json %.0f kB, %.1f min"
          % (len(ages), os.path.getsize(ROTJSON) / 1024.0, (time.time() - t0) / 60.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
