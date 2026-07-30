"""Rebuild ONE Precambrian keyframe. Usage: rebuild_pre_age.py 545

Mirrors main()'s Precambrian block for a single age -- authored craton grid,
blended onto the real 540 Ma DEM across the handoff, then the normal export.
Written because killing a long reskin mid-write truncates whatever file it was
holding open, and a truncated AVIF is a frame the app cannot load at all.
"""
import sys, time
import numpy as np

from build_frames import index_dems, read_dem
from render import resample_dem
import build_fields as BF
import precambrian as PRE


def main(argv):
    age = int(argv[1]) if len(argv) > 1 else 545
    t0 = time.time()
    idx = index_dems(); avail = np.array(sorted(idx.keys()))
    z540 = read_dem(idx[float(avail[np.argmin(np.abs(avail - 540))])])
    A_hi = resample_dem(z540, BF.ELEV_H, BF.ELEV_W)
    A_lo = resample_dem(z540, BF.CLIM_H, BF.CLIM_W)
    hi = PRE.precambrian_grid(age, tw=BF.ELEV_W, th=BF.ELEV_H, flood=140.0)
    lo = PRE.precambrian_grid(age, tw=BF.CLIM_W, th=BF.CLIM_H, flood=140.0)
    wq = float(np.clip((age - 540.0) / 20.0, 0, 1))
    wl = float(np.clip((age - 540.0) / 110.0, 0, 1))
    hi = BF.handoff_blend(A_hi, hi, wq, wl)
    lo = BF.handoff_blend(A_lo, lo, wq)
    BF.export(age, hi, lo[::-1], "pre")
    print(f"pre {age} Ma rebuilt: land {(hi>0).mean()*100:.3f}%  [{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
