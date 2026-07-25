"""Build and cache the isochron crustal-age grid for every keyframe.

Runs crustage.build() over the whole 0-1000 Ma range in ONE process, which is
the only way it is affordable: the ridge geometry at a given time t is needed by
41 different target times, so resolving topologies once per t and rotating the
cached geometry afterwards turns ten thousand topology resolutions into two
hundred. Cold start is ~50 s; every keyframe after that is under four seconds.

The future (negative ages) is not covered by any published rotation model, so it
is not built here -- those keyframes carry the present-day grid aged forward,
which is consistent with how the future terrain is already made.
"""
import os
import sys
import time

import numpy as np

import crustage

H, W = 512, 1024


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    ages = list(range(lo, hi + 1, crustage.STEP))
    os.makedirs(crustage.CACHE, exist_ok=True)
    t0 = time.time()
    done = 0
    for T in ages:
        f = os.path.join(crustage.CACHE, f"age_{T:05d}_{H}x{W}.npz")
        if os.path.exists(f):
            done += 1
            continue
        age, arc, dst, pid = crustage.build(float(T), H, W)
        np.savez_compressed(f, age=age, arc=arc, dst=dst, pid=pid)
        done += 1
        if done % 10 == 0 or done == len(ages):
            el = time.time() - t0
            ok = np.isfinite(age)
            print(f"  {T:4d} Ma  [{done}/{len(ages)}]  {el/60:.1f} min  "
                  f"dated {100*ok.mean():.0f}%  "
                  f"median gap {np.nanmedian(dst):.1f} deg  "
                  f"{len(np.unique(arc[ok]))} arcs", flush=True)
    print(f"done: {done} keyframes in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
