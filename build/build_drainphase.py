"""Bake `*_x.webp` -- DRAINAGE COORDINATES for the plains (WP-10, plan B5, second form).

The first form of B5 lays the atlas's dissected plateau and lowland patches on
the crust from a lattice, isotropically: a valley network with no downstream.
Real plains drain somewhere -- the Great Plains east, the Deccan east, West
Siberia north -- and their tributaries point the way. This bakes, per
keyframe, the same kind of coordinates the belts have in `_q`: omega along the
regional drainage (increasing UPSTREAM, so the tilted atlas patches, which
drain toward their own row 0, are sampled with patch-y = omega) and chi
across it, one unit per 256 km, fitted by the same preconditioned solve as
the fold coordinates.

The direction is the downhill direction of the PaleoDEM smoothed to ~120 km:
that is what a D8 receiver field averaged over a patch would give (rivers on
a plain run down the regional slope), without running the surface build.
Confidence is the regional slope itself, 0.2-1.0 m/km, times the plains gate
(shortening below 0.30, on land), so a belt or a truly flat basin (the Amazon
at 0.05 m/km) leaves the coordinates unconstrained and the shader falls back
to the isotropic first form there.

CHANNELS (RGBA, lossless WebP, exact): R,G = chi and B,A = omega, 16-bit each
over +-Q_RANGE units, as in `_q`.

    python3 build_drainphase.py            # all keyframes with an _e field
    python3 build_drainphase.py 0 300      # just these ages
    python3 build_drainphase.py -j         # three processes
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_foldphase as FP

FIELDS = FP.FIELDS
LAMBDA = FP.LAMBDA
Z_RANGE = 8000.0
W, H = 512, 256
SMOOTH_PX = 1.5              # ~120 km at the equator on the 512-wide grid
SLOPE_LO, SLOPE_HI = 0.2, 1.0  # m/km: confidence ramp of the regional slope


def _elev(path):
    im = Image.open(path).convert("L").resize((W, H), Image.BOX)
    s = 2.0 * np.asarray(im, np.float64) / 255.0 - 1.0
    return np.sign(s) * s * s * Z_RANGE


def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def bake(age, quiet=False):
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    fr = next((f for f in manifest if f["age"] == age), None)
    if fr is None:
        return None
    base = fr["e"][:fr["e"].rfind("_e")]
    epath = os.path.join(FIELDS, base + "_e.avif")
    tpath = os.path.join(FIELDS, base + "_t.webp")
    if not (os.path.exists(epath) and os.path.exists(tpath)):
        return None
    z = _elev(epath)
    t = np.asarray(Image.open(tpath).convert("RGB").resize((W, H), Image.BILINEAR)).astype(np.float64) / 255.0
    short = t[..., 0]
    lat = np.radians(90.0 - (np.arange(H) + 0.5) / H * 180.0)[:, None] * np.ones((1, W))
    cl = np.maximum(np.cos(lat), 0.15)
    # smooth on the sphere's grid (wrap in longitude), then the gradient per radian of arc
    zs = gaussian_filter(z, SMOOTH_PX, mode=("nearest", "wrap"))
    dlon = 2 * np.pi / W
    dlat = np.pi / H
    gx = (np.roll(zs, -1, axis=1) - np.roll(zs, 1, axis=1)) / (2 * dlon) / cl      # east, m per radian
    gy = -(np.roll(zs, -1, axis=0) - np.roll(zs, 1, axis=0)) / (2 * dlat)           # north (rows run south)
    gy[0] = gy[1]; gy[-1] = gy[-2]
    mag = np.hypot(gx, gy)
    mkm = mag / 6371.0                                                              # m per km
    dx, dy = -gx / (mag + 1e-9), -gy / (mag + 1e-9)                                 # downhill, unit
    w = (z > 0) * (1.0 - _ss(0.08, 0.30, short)) * _ss(SLOPE_LO, SLOPE_HI, mkm)
    # omega increases upstream: target is the UPHILL unit vector, sign physical
    omega = FP._solve(-dx / LAMBDA, -dy / LAMBDA, w, lat)
    # chi across the flow; its sign is arbitrary, so it is grown consistent like phi
    ax, ay = -dy, dx
    sg = FP._consistent_sign(ax, ay, w)
    chi = FP._solve(sg * ax / LAMBDA, sg * ay / LAMBDA, w, lat)
    out = FP._encode(chi, omega)
    name = base + "_x.webp"
    Image.fromarray(out, "RGBA").save(os.path.join(FIELDS, name), "WEBP",
                                      lossless=True, quality=100, method=4, exact=True)
    if not quiet:
        m = w > 0.3
        span = lambda a: float(np.percentile(a[m], 99) - np.percentile(a[m], 1)) if m.any() else 0.0
        print("  %s  gated %.1f%% of land  chi span %.1f  omega span %.1f  -> %s" % (
            age, 100 * m.sum() / max(1, (z > 0).sum()), span(chi), span(omega), name))
    return name


def main():
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    ages = [int(x) for x in args] or [f["age"] for f in manifest]
    procs = 3 if "-j" in sys.argv else 1
    if procs > 1:
        from multiprocessing import Pool
        with Pool(procs) as pool:
            done = [r for r in pool.map(bake, ages) if r]
    else:
        done = [r for r in (bake(a) for a in ages) if r]
    print("drainage coordinates: %d keyframes -> %s" % (len(done), FIELDS))


if __name__ == "__main__":
    main()
