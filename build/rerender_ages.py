"""Re-render a few Phanerozoic keyframes in place after a climate-table edit.

Vegetation feeds the moisture-recycling floor in the rainfall solve, so
changing it changes the `_r` textures as well as the manifest. A full rebuild
takes ~35 minutes to redo 251 keyframes when only a handful actually moved,
so this re-exports just the ages given on the command line and patches their
manifest records. Elevation is deterministic and comes out identical, which
is what makes this safe: the `_m` motion fields derived from it stay valid.

    python rerender_ages.py 225 230 235 240 245 250 255 260
"""
import json, os, sys
import numpy as np

from build_fields import (export, handoff_blend,
                          ELEV_H, ELEV_W, CLIM_H, CLIM_W, OUT)
from build_frames import index_dems, read_dem
from render import resample_dem
import precambrian as PRE
import epeiric as EP
import paleo_tracks

MAN = os.path.join(OUT, "manifest.json")
_IDX = index_dems()
_AVAIL = np.array(sorted(_IDX.keys()))


def dem_for_age(age):
    near = float(_AVAIL[np.argmin(np.abs(_AVAIL - age))])
    return read_dem(_IDX[near])


def _pre_grids(age, a_hi, a_lo):
    """Authored Precambrian terrain, ramped onto the real 540 Ma map."""
    hi = PRE.precambrian_grid(age, tw=ELEV_W, th=ELEV_H, flood=140.0)
    lo = PRE.precambrian_grid(age, tw=CLIM_W, th=CLIM_H, flood=140.0)
    wq = float(np.clip((age - 540.0) / 60.0, 0, 1))
    # the SAME land-preserving handoff build_fields uses; a straight blend of
    # metres here would quietly put the drowned-continent artefact back
    return handoff_blend(a_hi, hi, wq), handoff_blend(a_lo, lo, wq)


def main(ages):
    man = json.load(open(MAN))
    by_age = {m["age"]: i for i, m in enumerate(man)}
    a_hi = a_lo = None
    for age in ages:
        if age not in by_age:
            print(f"  {age:>5} Ma  not a keyframe, skipped")
            continue
        if age <= 540:
            z = dem_for_age(age)
            Zhi = resample_dem(z, ELEV_H, ELEV_W)
            # same seeded seas build_fields applies, or a per-frame re-render
            # would quietly drain them again
            global _REC
            try:
                _REC
            except NameError:
                _REC = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
            Zhi = EP.carve(Zhi, age, _REC)
            rec, _ = export(age, Zhi, z, "phan")
        else:
            if a_hi is None:                      # anchor, loaded once
                z540 = dem_for_age(540)
                a_hi = resample_dem(z540, ELEV_H, ELEV_W)
                a_lo = resample_dem(z540, CLIM_H, CLIM_W)
            hi, lo = _pre_grids(age, a_hi, a_lo)
            rec, _ = export(age, hi, lo[::-1], "pre")
        man[by_age[age]] = rec
        print(f"  {age:>5} Ma  re-rendered  veg {rec['veg']:.2f}  "
              f"temp {rec['temp']:+.2f}  ice<{rec['iceT']:.0f}C")
    json.dump(man, open(MAN, "w"), separators=(",", ":"))
    print(f"manifest patched ({len(ages)} ages)")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]])
