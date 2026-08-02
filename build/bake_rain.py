"""Re-bake ONLY the rainfall field (`*_r.webp`) for every keyframe.

WHY SURGICAL. The climate solve changed (render._rainfall gained meridional
moisture transport), and rainfall is written by build_fields.export alongside
elevation and ocean structure -- so the obvious route, re-running the whole
build, would re-render 251 keyframes and cost hours to change one channel that
takes a second to compute. Elevation and ocean structure did not change and
must not be touched: re-encoding them would churn every AVIF for nothing.

WHAT DEPENDS ON THIS. `_d` (drainage, whose flow accumulation is driven by
rainfall) and `_w` (lakes, whose water balance is) both derive from it, so both
are rebuilt afterwards -- see the chain in the round's commit. Ice does not:
its thresholds are temperature, not rain.

Mirrors export()'s encoding exactly: CLIM-resolution solve, /RF_MAX, LANCZOS to
RAIN_W x RAIN_H, polar_lowpass, then _gray + _save at RAIN_Q.
"""
import os
import sys
import time

import numpy as np
from PIL import Image

import build_fields as BF
from build_frames import index_dems, read_dem, sealevel_for
from render import compute_fields, resample_dem
from build_fields import polar_lowpass
import epeiric as EP
import paleo_tracks
import precambrian as PRE


def rain_for(age, z, rec):
    """The climate grid this age's rainfall must be solved on.

    Each era builds its own: the Phanerozoic carves epeiric seas into the
    shipped grid first, the future warps the present DEM and applies its own
    eustatic correction, and the Precambrian blends into the authored map. Using
    the raw DEM for all three would solve the climate over terrain the app never
    draws -- the mistake export()'s own comment records.
    """
    if age < 0:
        gl = BF.future_grid(abs(age) / 250.0, rain_for.gid, rain_for.Zsrc,
                            BF.CLIM_H, BF.CLIM_W) - sealevel_for(age)
        return gl[::-1]
    if age <= 540:
        Zhi = EP.carve(resample_dem(z, BF.ELEV_H, BF.ELEV_W), age, rec)
        return Zhi[::-1]
    lo = PRE.precambrian_grid(age, tw=BF.CLIM_W, th=BF.CLIM_H, flood=140.0)
    A_lo = resample_dem(read_dem(rain_for.idx[rain_for.near540]), BF.CLIM_H, BF.CLIM_W)
    wq = float(np.clip((age - 540.0) / 20.0, 0, 1))
    return BF.handoff_blend(A_lo, lo, wq)[::-1]


def main():
    t0 = time.time()
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    rain_for.idx = idx
    rain_for.near540 = float(avail[np.argmin(np.abs(avail - 540))])
    rain_for.gid = BF.rasterise_groups()
    rain_for.Zsrc = resample_dem(read_dem(idx[float(avail[np.argmin(np.abs(avail))])]),
                                 900, 1800)
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None

    ages = ([a for a in range(0, 541, BF.STEP)]
            + [a for a in range(-BF.STEP, -251, -BF.STEP)]
            + [a for a in range(540 + BF.STEP, 1001, BF.STEP)])
    tags = {}
    for a in ages:
        tags[a] = "fut" if a < 0 else ("phan" if a <= 540 else "pre")
    n = 0
    for age in ages:
        z = read_dem(idx[float(avail[np.argmin(np.abs(avail - max(age, 0)))])])
        zc = rain_for(age, z, rec)
        _, _, Rf, _, _ = compute_fields(zc, age, BF.CLIM_H, BF.CLIM_W)
        rain = np.asarray(Image.fromarray(
            (np.clip(Rf / BF.RF_MAX, 0, 1) * 255).astype(np.uint8)).resize(
            (BF.RAIN_W, BF.RAIN_H), Image.LANCZOS)) / 255.0
        r = BF._gray(polar_lowpass(rain))
        path = os.path.join(BF.OUT, "%s_%04d_r.webp" % (tags[age], abs(age)))
        BF._save(r, path, BF.RAIN_Q)
        n += 1
        if n % 25 == 0:
            print("  %d/%d  (%.1f min)" % (n, len(ages), (time.time() - t0) / 60),
                  flush=True)
    print("DONE %d rainfall fields in %.1f min" % (n, (time.time() - t0) / 60), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
