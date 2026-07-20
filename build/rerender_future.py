"""Re-render the future keyframes in place after a future climate-table edit.

The future series (ages 0 -> -250) is built by warping the present DEM by
plate-group rotation; its rainfall textures come from the wind solve, which is
driven by climate.py's veg and temp. When the future climate changed (solar
brightening + biosphere collapse: veg 1.0 -> 0.48, hotter, drier), the barren
OVERLAY updated for free from the manifest, but the shipped rainfall textures
still encoded the old lush vegetation. This regenerates just the future
elevation + rainfall WebPs so the terrain itself reads as the drier, more
desert future -- rerender_ages.py only knows the phan/pre paths, not 'fut'.

Elevation is a deterministic warp and comes out identical, so the derived `_m`
motion fields stay valid and are left untouched. Run refresh_manifest.py after
this to re-add the solar-luminosity field and keep every record consistent.

    python rerender_future.py
"""
import json
import os

import numpy as np

from build_fields import (export, future_grid, rasterise_groups,
                          ELEV_H, ELEV_W, CLIM_H, CLIM_W, STEP, OUT)
from build_frames import index_dems, read_dem, sealevel_for
from render import resample_dem

MAN = os.path.join(OUT, "manifest.json")


def main():
    man = json.load(open(MAN))
    by_age = {m["age"]: i for i, m in enumerate(man)}

    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    z0 = read_dem(idx[float(avail[np.argmin(np.abs(avail - 0))])])
    Zsrc = resample_dem(z0, 900, 1800)      # north-up source for the warp
    gid = rasterise_groups()

    done = 0
    for age in range(-STEP, -251, -STEP):
        if age not in by_age:
            continue
        frac = abs(age) / 250.0
        gh = future_grid(frac, gid, Zsrc, ELEV_H, ELEV_W)
        gl = future_grid(frac, gid, Zsrc, CLIM_H, CLIM_W)
        # future terrain is referenced to today's sea level, so apply the era's
        # eustatic level by hand (same correction as the original build)
        sl = sealevel_for(age)
        gh = gh - sl
        gl = gl - sl
        rec, _ = export(age, gh, gl[::-1], "fut")
        man[by_age[age]] = rec
        done += 1
        print(f"  +{-age:>3} Myr  re-rendered  veg {rec['veg']:.2f}  "
              f"temp {rec['temp']:+.2f}  gmst {rec['gmst']:.1f}C")

    json.dump(man, open(MAN, "w"), separators=(",", ":"))
    print(f"future re-rendered: {done} keyframes. "
          f"Now run refresh_manifest.py to re-add 'sol' and finalise metadata.")


if __name__ == "__main__":
    main()
