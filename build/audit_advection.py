"""Does advecting the keyframes actually remove the ghost? Measure, don't assume.

Replicates the shader's `baseElev` on the CPU, both ways, and scores the two
against each other across one keyframe interval. Same idea as `shadersim.py`:
validate the arithmetic without touching GLSL or needing a browser to composite.

THE CLAIM UNDER TEST. A cross-fade between two keyframes whose crust has moved
14-42 texels is a double exposure: at mid-interval every ridge appears twice at
half amplitude, so RELIEF SAGS and then snaps back at the next keyframe.
Advecting each frame toward the other should hold relief flat across the
interval instead. That is a number, so this measures it: p95 of the elevation
gradient over land, at mixf 0, 0.25, 0.5, 0.75, 1.

TWO GATES, and the first is the one that protects the data:
  1. At mixf 0 and 1 the warped result must be EXACTLY the old one. The offsets
     carry a zero mix weight there, so this is true algebraically; it is checked
     anyway, because "exactly at the keyframes" is the promise section H makes
     to the PaleoDEMs and an off-by-one in the sign of mixf would break it while
     still looking plausible mid-interval.
  2. Mid-interval relief must not sag.

    ../venv/bin/python audit_advection.py
    ../venv/bin/python audit_advection.py --selftest
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")

Z_RANGE = 8000.0        # fieldpack.Z_RANGE
V_DEG = 12.0            # build_displacement.V_RANGE / the shader's V_DEG
COS_FLOOR = 0.15        # the shader's max(cos(lat), 0.15)

# Intervals to score. Each is a real event whose crust is moving fast enough
# that the ghost should be visible, plus a slow one as a control.
INTERVALS = [
    (45, 50, "India closing on Asia"),
    (85, 90, "the fastest crust in the model"),
    (200, 205, "Pangaea, slow interior"),
    (400, 405, "Palaeozoic, worst median displacement"),
]


def _load(age, kind):
    tag = "phan" if age <= 540 else "pre"
    for ext in ("avif", "webp"):
        p = os.path.join(FIELDS, "%s_%04d_%s.%s" % (tag, age, kind, ext))
        if os.path.exists(p):
            return np.asarray(Image.open(p).convert("RGB" if kind == "v" else "L"))
    return None


def _dec(e):
    d = e.astype(np.float32) / 255.0 * 2.0 - 1.0
    return np.sign(d) * d * d * Z_RANGE


def _sample(img, u, v):
    """Bilinear sample of an equirectangular field at uv, wrapping in longitude.

    Longitude wraps and latitude clamps -- the poles are real boundaries, not a
    seam. Getting that backwards is the recurring bug in this pipeline.
    """
    h, w = img.shape
    x = (u % 1.0) * w - 0.5
    y = np.clip(v, 0.0, 1.0) * h - 0.5
    return map_coordinates(img, [y, x], order=1, mode="grid-wrap")


def warp_field(age, h, w):
    """The shader's warpAt(), on a grid. Returns (du, dv) in IMAGE uv units.

    IMAGE SPACE, NOT GPU SPACE, and the distinction cost an hour. On the GPU
    every texture is flipped on upload, so uv.y = 1 is north for all of them
    and the shader's dv is +dN/180. Here nothing is flipped, so row 0 is north
    for all of them and dv is -dN/180. Either convention is fine as long as it
    is applied to EVERY field; the bug was flipping `_v` alone to imitate the
    GPU while leaving elevation in image space, which does not merely invert the
    north-south sign -- it applies the north pole's displacement at the south
    pole. Two of these tests reported "MISALIGNS" before this was found, which
    is a warp being blamed for a mistake in its own instrument.
    """
    v = _load(age, "v")
    if v is None:
        return None, None
    vv = v.astype(np.float32) / 255.0
    dE = (vv[..., 0] * 2.0 - 1.0) * V_DEG
    dN = (vv[..., 1] * 2.0 - 1.0) * V_DEG
    # resample the 1024x512 field onto the elevation grid
    yy, xx = np.mgrid[0:h, 0:w]
    uy = (yy + 0.5) / h * vv.shape[0] - 0.5
    ux = (xx + 0.5) / w * vv.shape[1] - 0.5
    dE = map_coordinates(dE, [uy, ux], order=1, mode="grid-wrap")
    dN = map_coordinates(dN, [uy, ux], order=1, mode="grid-wrap")
    lat = 90.0 - (yy + 0.5) / h * 180.0             # image space: row 0 is north
    cl = np.maximum(np.cos(np.radians(lat)), COS_FLOOR)
    return dE / (cl * 360.0), -dN / 180.0


def base_elev(zA, zB, t, du, dv, warped):
    h, w = zA.shape
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5) / w
    v = (yy + 0.5) / h
    if not warped:
        return zA * (1 - t) + zB * t
    a = _sample(zA, u - t * du, v - t * dv)
    b = _sample(zB, u + (1 - t) * du, v + (1 - t) * dv)
    return a * (1 - t) + b * t


def relief(z):
    """p95 of the gradient magnitude over land -- how sharp the terrain is."""
    gy, gx = np.gradient(z)
    g = np.hypot(gx, gy)
    land = z > 0
    return float(np.percentile(g[land], 95)) if land.any() else 0.0


def run():
    print("Relief across one keyframe interval: p95 |grad z| over land, metres/texel")
    print("A cross-fade double-exposes and SAGS in the middle; advection should not.\n")
    worst_gate1 = 0.0
    rows = []
    for a, b, why in INTERVALS:
        zA, zB = _load(a, "e"), _load(b, "e")
        if zA is None or zB is None:
            print("  %d-%d Ma: fields missing, skipped" % (a, b))
            continue
        zA, zB = _dec(zA), _dec(zB)
        du, dv = warp_field(a, *zA.shape)
        if du is None:
            print("  %d-%d Ma: no _v yet, skipped" % (a, b))
            continue
        old = [relief(base_elev(zA, zB, t, du, dv, False)) for t in (0, .25, .5, .75, 1)]
        new = [relief(base_elev(zA, zB, t, du, dv, True)) for t in (0, .25, .5, .75, 1)]

        # gate 1: the keyframes themselves must not move
        e0 = np.abs(base_elev(zA, zB, 0.0, du, dv, True) - zA).max()
        e1 = np.abs(base_elev(zA, zB, 1.0, du, dv, True) - zB).max()
        worst_gate1 = max(worst_gate1, float(e0), float(e1))

        ends = (old[0] + old[4]) / 2.0
        sag_old = 100.0 * (1.0 - old[2] / ends)
        sag_new = 100.0 * (1.0 - new[2] / ends)
        rows.append((a, b, why, sag_old, sag_new))
        print("  %3d-%-3d Ma  %s" % (a, b, why))
        print("     cross-fade  " + "  ".join("%6.1f" % x for x in old)
              + "   sag at mid-interval %5.1f%%" % sag_old)
        print("     advected    " + "  ".join("%6.1f" % x for x in new)
              + "   sag at mid-interval %5.1f%%" % sag_new)
        print()

    print("GATE 1 -- the keyframes must be untouched (mixf 0 and 1)")
    print("   worst deviation across all intervals: %.3g m  %s"
          % (worst_gate1, "PASS" if worst_gate1 < 1e-3 else "FAIL"))
    print()
    print("GATE 2 -- mid-interval relief must not sag")
    ok = True
    for a, b, why, so, sn in rows:
        verdict = "better" if sn < so - 0.5 else ("no change" if abs(sn - so) <= 0.5 else "WORSE")
        if sn > so + 0.5:
            ok = False
        print("   %3d-%-3d Ma  cross-fade %5.1f%% -> advected %5.1f%%   %s"
              % (a, b, so, sn, verdict))
    if rows:
        print("\n   mean sag  %.1f%% -> %.1f%%"
              % (np.mean([r[3] for r in rows]), np.mean([r[4] for r in rows])))
    return 0 if (ok and worst_gate1 < 1e-3) else 1


def _selftest():
    ok = True
    # A zero warp must reproduce the plain cross-fade exactly, or the sampler
    # itself is introducing error and every comparison below is against a
    # moving baseline rather than against the old behaviour.
    rs = np.random.RandomState(0)
    zA, zB = rs.rand(64, 128) * 3000, rs.rand(64, 128) * 3000
    z = np.zeros((64, 128))
    for t in (0.0, 0.3, 1.0):
        d = np.abs(base_elev(zA, zB, t, z, z, True) - base_elev(zA, zB, t, z, z, False)).max()
        if d > 1e-6:
            print("  FAIL zero warp is not a no-op at t=%.1f: %.3g" % (t, d))
            ok = False
    # The sampler must wrap in longitude, not clamp.
    img = np.zeros((8, 16)); img[4, 0] = 1.0
    if _sample(img, np.array([-0.01]), np.array([4.5 / 8]))[0] <= 0:
        print("  FAIL _sample does not wrap in longitude")
        ok = False
    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(0 if _selftest() else 1)
    raise SystemExit(run())
