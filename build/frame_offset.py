"""Measure the longitude offset between the Merdith rotation model and the
Scotese paleo-DEMs, per age.

Paleomagnetism fixes latitude and orientation but says NOTHING about absolute
longitude — a reconstruction can slide every continent east or west together and
fit the same data. Different published models therefore choose different
absolute frames, and this project uses two of them at once: terrain comes from
Scotese & Wright's PaleoDEMs, while plate tracks for labels, craters and LIPs
come from Merdith et al. (2021) via pyGPlates.

At 90 Ma the two disagree by about 18 degrees. That is why the Western Interior
Seaway label sat over the Appalachians and the Appalachians label sat in the
Atlantic: the names were being placed on Merdith's Earth and drawn on Scotese's.

The fix is to measure the offset rather than guess it. For each age:

  1. sample present-day land points,
  2. back-advect them with Merdith to that age -> a predicted land cloud in the
     MERDITH frame,
  3. find the longitude shift that best lands that cloud on the DEM's actual
     land at the same age.

Latitude is left alone: paleomagnetism does constrain it, the two models agree
on it closely, and fitting it would let real disagreement leak into a fudge.

Writes frame_offset.json: {age: delta_lon}. paleo_tracks applies it so every
track comes out in the frame the terrain is actually drawn in.
"""
import json
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
OUT = os.path.join(HERE, "frame_offset.json")
Z_RANGE = 8000.0
STEP = 5                      # keyframe spacing
MAX_AGE = 540                 # Merdith topologies + Phanerozoic DEMs
SHIFTS = np.arange(-60, 60.5, 1.0)


def land_mask(age, nx=720, ny=360):
    name = f"phan_{int(age):04d}_e.webp"
    p = os.path.join(FIELDS, name)
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("L").resize((nx, ny), Image.NEAREST)
    a = np.asarray(im, np.float32) / 255.0
    s = 2.0 * a - 1.0
    z = np.sign(s) * s * s * Z_RANGE
    return z > 0


def sample_points(mask, nx=720, ny=360, stride=6):
    ys, xs = np.nonzero(mask[::stride, ::stride])
    lon = (xs * stride) / nx * 360.0 - 180.0
    lat = 90.0 - (ys * stride) / ny * 180.0
    return lon, lat


def score(mask, lon, lat, nx=720, ny=360):
    """Fraction of the predicted cloud that lands on real DEM land."""
    x = ((lon + 180.0) / 360.0 * nx).astype(int) % nx
    y = np.clip(((90.0 - lat) / 180.0 * ny).astype(int), 0, ny - 1)
    return mask[y, x].mean()


def smooth_offsets(raw, med_win=7, mean_win=5):
    """Smooth the per-age fit.

    The difference between two reconstructions' absolute frames is a property of
    the models, not of any single keyframe: it has to vary smoothly with age. The
    per-age fit does not, because the objective is shallow -- especially in the
    Palaeozoic, where correcting the shift only moves the on-land score a few
    points, so noise picks the winner. Raw, this series stepped 41 degrees
    between 360 and 365 Ma, which yanked every tracked feature sideways and then
    back: the Laurussia label latched onto an islet 40 degrees from its
    continent and stayed there for 50 Myr.

    Rolling median first (kills the outliers), then a short rolling mean (takes
    the corners off), then re-anchor the present at zero, where the two models
    agree by construction.
    """
    ages = sorted(int(k) for k in raw)
    v = [float(raw[str(a)]) for a in ages]
    n = len(v)

    def roll(vals, win, fn):
        h = win // 2
        return [fn(vals[max(0, i - h):min(n, i + h + 1)]) for i in range(n)]

    def median(xs):
        xs = sorted(xs)
        m = len(xs) // 2
        return xs[m] if len(xs) % 2 else 0.5 * (xs[m - 1] + xs[m])

    v = roll(v, med_win, median)
    v = roll(v, mean_win, lambda xs: sum(xs) / len(xs))
    base = v[ages.index(0)] if 0 in ages else 0.0
    return {str(a): round(v[i] - base * (1.0 if a == 0 else 0.0), 1)
            for i, a in enumerate(ages)}


def main():
    import paleo_tracks
    if not paleo_tracks.available():
        raise SystemExit("pyGPlates / Merdith files unavailable")
    rec = paleo_tracks.Reconstructor()

    m0 = land_mask(0)
    lon0, lat0 = sample_points(m0)
    print(f"{len(lon0)} present-day land sample points")

    # Back-advect every sample once, keeping the whole track, so each age is a
    # lookup rather than another reconstruction pass.
    tracks = []
    for i, (lo, la) in enumerate(zip(lon0, lat0)):
        try:
            tr, _ = rec.track(float(lo), float(la), MAX_AGE, step=STEP)
        except Exception:
            continue
        if len(tr) > 1:
            tracks.append({int(round(a)): (x, y) for a, x, y in tr})
        if (i + 1) % 250 == 0:
            print(f"  advected {i+1}/{len(lon0)}")
    print(f"{len(tracks)} usable tracks")

    out = {}
    for age in range(0, MAX_AGE + 1, STEP):
        mask = land_mask(age)
        if mask is None:
            continue
        pts = [t[age] for t in tracks if age in t]
        if len(pts) < 200:
            continue
        lon = np.array([p[0] for p in pts])
        lat = np.array([p[1] for p in pts])
        best, best_s = 0.0, -1.0
        for d in SHIFTS:
            s = score(mask, ((lon + d + 180.0) % 360.0) - 180.0, lat)
            if s > best_s:
                best_s, best = s, float(d)
        base = score(mask, lon, lat)
        out[str(age)] = round(best, 1)
        print(f"  {age:4d} Ma  shift {best:+6.1f} deg   on-land {base*100:4.0f}% "
              f"-> {best_s*100:4.0f}%")

    out = smooth_offsets(out)
    json.dump(out, open(OUT, "w"), indent=0, sort_keys=True)
    print(f"\nwrote {OUT} ({len(out)} ages, smoothed)")


if __name__ == "__main__":
    main()
