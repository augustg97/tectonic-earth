"""Rebuild ONLY the 50 future keyframes, in place.

S1-S5 (WP-07) all live in future_grid, so the Phanerozoic and Precambrian frames
are bit-identical to what is already on disk and re-rendering them would cost
hours for no change. This mirrors main()'s future block exactly -- same eustatic
correction, same export tags, same motion coarsening -- and then the manifest is
refreshed from the files on disk by refresh_manifest.py.

Run it, do not background it without a log: a backgrounded build that dies is a
trap this project has already fallen into twice (README 7.11).
"""
import sys, time
import numpy as np

from build_frames import index_dems, read_dem, sealevel_for
from render import resample_dem
import build_fields as BF
import motion as MO

STEP = BF.STEP


def main():
    t0 = time.time()
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    z0 = read_dem(idx[float(avail[np.argmin(np.abs(avail - 0))])])

    print("rasterising group mask at 0.125 deg ...", flush=True)
    gid = BF.rasterise_groups()
    Zsrc = resample_dem(z0, 900, 1800)
    print(f"mask {gid.shape}  source {Zsrc.shape}  [{time.time()-t0:.0f}s]", flush=True)

    n = 0
    for age in range(-STEP, -251, -STEP):
        ts = time.time()
        frac = abs(age) / 250.0
        gh = BF.future_grid(frac, gid, Zsrc, BF.ELEV_H, BF.ELEV_W)
        gl = BF.future_grid(frac, gid, Zsrc, BF.CLIM_H, BF.CLIM_W)
        sl = sealevel_for(age)
        gh = gh - sl
        gl = gl - sl
        BF.export(age, gh, gl[::-1], "fut")
        n += 1
        land = float((gh > 0).sum()) / gh.size * 100.0
        print(f"  {age:+5d} Myr  land {land:5.2f}%  max {gh.max():6.0f} m  "
              f"[{time.time()-ts:.0f}s]  ({n}/50)", flush=True)

    print(f"future: {n} keyframes rebuilt in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
