"""Bake fut_XXXX_v.webp for the 50 future keyframes, in place.

WHY THIS IS SEPARATE. The future elevations are already correct on disk;
only the displacement field was missing, and it needs nothing from the
elevation pipeline except which group owns each cell. Recomputing the
ownership test alone takes seconds per frame instead of the 85 s a full
future_grid costs, so the whole series bakes in a couple of minutes.

The physics is exact rather than matched: every group turns about ONE axis
by an angle proportional to frac, so the rotation carrying its crust from
one keyframe to the next is a rotation about that same axis by the angle
difference -- no differencing of rasters, no fitting. Convention follows
build_displacement exactly (apply the interval rotation to this grid's own
directions; store east/north in the local tangent frame), so the shader
needs no new code.
"""
import os
import sys
import time

import numpy as np
from PIL import Image

import build_fields as BF
import build_displacement as BD

VW, VH = BD.VW, BD.VH
STEP = BF.STEP


def bake(age, gid=None, Zsrc=None, quiet=False):
    """fut_XXXX_v.webp from future_tectonics (3.16): each cell's crust moves by
    its owning plate's rotation from this keyframe to the next one ahead,
    R_g(t + STEP) R_g(t)^T -- the plates' own smooth kinematics, no raster
    differencing. New ocean between plates is filled by the Laplace solve."""
    import future_tectonics as FT
    t0 = time.time()
    myr = abs(age)
    _z, own, _src, _E, _cw = FT.render(myr, VH, VW, fray=False)
    owner = own.ravel()
    lon = (np.arange(VW) + 0.5) / VW * 360 - 180
    lat = 90 - (np.arange(VH) + 0.5) / VH * 180
    LON, LAT = np.meshgrid(lon, lat)
    V0 = BF.BS.unit(LON.ravel(), LAT.ravel())
    V1 = V0.copy()
    for i, p in enumerate(FT.PLATES):
        m = owner == i
        if not m.any():
            continue
        Rint = FT.rot(p, myr + STEP) @ FT.rot(p, myr).T
        V1[:, m] = Rint @ V0[:, m]
    dot = np.clip((V0 * V1).sum(0), -1.0, 1.0)
    gc = np.degrees(np.arccos(dot))
    tang = V1 - dot * V0
    dirn = tang / np.maximum(np.linalg.norm(tang, axis=0), 1e-15)
    e, n = BD._tangent_basis(LON.ravel(), LAT.ravel())
    dE = (gc * (dirn.T * e).sum(-1)).reshape(VH, VW)
    dN = (gc * (dirn.T * n).sum(-1)).reshape(VH, VW)
    # Unclaimed cells are new ocean opened between the drifting plates: filled
    # from the covered values by the same Laplace solve the Phanerozoic path
    # uses, so the new floor moves with the plates that opened it.
    cov = (owner >= 0).reshape(VH, VW)
    dE = BD.laplace_fill(dE, cov)
    dN = BD.laplace_fill(dN, cov)
    arr = BD._encode(dE, dN, np.zeros_like(dE))
    path = os.path.join(BF.OUT, "fut_%04d_v.webp" % myr)
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
    if not quiet:
        print("  %+5d Myr  max %.2f deg  covered %5.1f%%  %5.1f kB  [%.0fs]"
              % (-myr, float(np.abs(np.stack([dE, dN])).max()),
                 100.0 * float((owner >= 0).mean()),
                 os.path.getsize(path) / 1024.0, time.time() - t0), flush=True)
    return float(np.abs(np.stack([dE, dN])).max())


def main():
    t0 = time.time()
    for age in range(-STEP, -251, -STEP):
        bake(age)
    print("DONE future displacement fields in %.1f min" % ((time.time() - t0) / 60.0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
