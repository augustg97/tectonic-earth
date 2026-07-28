"""Rebuild ONE Phanerozoic keyframe in place. Usage: rebuild_phan_age.py 5

Mirrors main()'s Phanerozoic block exactly -- same DEM pick, same epeiric carve,
same export tag and the same lat-ascending flip for the climate solve -- so a
single frame can be re-rendered without re-running the other 250.
"""
import sys, time
import numpy as np

from build_frames import index_dems, read_dem
from render import resample_dem
import build_fields as BF
import epeiric as EP
import paleo_tracks


def main(argv):
    age = int(argv[1]) if len(argv) > 1 else 5
    t0 = time.time()
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    z = read_dem(idx[float(avail[np.argmin(np.abs(avail - age))])])
    Zhi = resample_dem(z, BF.ELEV_H, BF.ELEV_W)
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    before = float((Zhi > 0).sum()) / Zhi.size * 100.0
    Zhi = EP.carve(Zhi, age, rec, verbose=True)
    after = float((Zhi > 0).sum()) / Zhi.size * 100.0
    BF.export(age, Zhi, Zhi[::-1], "phan")
    print(f"phan {age} Ma rebuilt: land {before:.3f}% -> {after:.3f}%  "
          f"[{time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
