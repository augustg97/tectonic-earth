"""Rewrite ONLY the rainfall (_r) field for the Phanerozoic keyframes.

Rainfall is derived by the wind-and-moisture solve in render.compute_fields, and
until now that solve ran on the RAW paleo-DEM while everything else ran on the
carved one -- so every sea epeiric.py seeds changed the coastline and the map
without making the air over it any wetter. That was tolerable when the module
seeded two named seas. It is not once it also supplies the continental shelf that
ringed Pangaea, which is several percent of the globe and sits directly upwind of
the interior the megamonsoon is supposed to be drying.

Measured at 240 Ma, feeding the carved grid in:

    land that is still land   0.104 -> 0.122   (+17%)
    the deep interior         0.064 -> 0.070   (+11%)
    within 4 cells of a coast 0.307 -> 0.347   (+13%)

Global mean rainfall FALLS, and that is not a contradiction: 6% of the grid moved
from land, where this model reports rainfall, to sea, where it reports almost
none. Every square kilometre that is still land got wetter.

Only _r is rewritten. Elevation and ocean structure are unchanged by this (they
already use the carved grid), and the manifest's scalars come from climate_at()
which has not moved -- so nothing else is touched and the manifest is left alone.
That is deliberate: it has been clobbered twice before.

    ../venv/bin/python rerender_rain.py            # every Phanerozoic keyframe
    ../venv/bin/python rerender_rain.py 200 240    # just these
"""
import os
import sys

import numpy as np
from PIL import Image

import build_fields as bf
import epeiric as EP
import paleo_tracks
from fieldpack import RF_MAX
from render import compute_fields


def main(ages=None):
    idx = bf.index_dems()
    avail = np.array(sorted(idx.keys()))
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    if not ages:
        ages = list(range(0, 541, bf.STEP))
    n = 0
    for age in ages:
        near = float(avail[np.argmin(np.abs(avail - age))])
        z = bf.read_dem(idx[near])
        Zhi = EP.carve(bf.resample_dem(z, bf.ELEV_H, bf.ELEV_W), age, rec)
        # row 0 = north out of resample_dem/carve; compute_fields wants ascending
        _, _, Rf, _, _ = compute_fields(Zhi[::-1], age, bf.CLIM_H, bf.CLIM_W)
        rain = np.asarray(Image.fromarray(
            (np.clip(Rf / RF_MAX, 0, 1) * 255).astype(np.uint8)).resize(
            (bf.RAIN_W, bf.RAIN_H), Image.LANCZOS)) / 255.0
        out = os.path.join(bf.OUT, f"phan_{abs(age):04d}_r.webp")
        bf._save(bf._gray(rain), out, bf.RAIN_Q)
        n += 1
        print(f"  {age:>4} Ma  rain mean {float(Rf.mean()):.4f}", flush=True)
    print(f"rainfall: {n} keyframes rewritten")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]])
