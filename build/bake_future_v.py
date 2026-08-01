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


def owner_map(frac, gid, Zsrc):
    """Which group's crust sits under each cell of the VWxVH grid."""
    lon = (np.arange(VW) + 0.5) / VW * 360 - 180
    lat = 90 - (np.arange(VH) + 0.5) / VH * 180
    LON, LAT = np.meshgrid(lon, lat)
    T = BF.BS.unit(LON.ravel(), LAT.ravel())
    gh, gw = gid.shape
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    packed = BF._packed_targets(gid, Zsrc)
    owner = np.full(T.shape[1], -1, np.int16)
    best = np.full(T.shape[1], -9999.0)
    rots = {}
    for i, g in enumerate(BF.GROUPS):
        m = gid == i
        if not m.any() or g not in packed:
            continue
        s = BF.BS.unit(GLON[m], GLAT[m]).mean(axis=1); s /= np.linalg.norm(s)
        tl, tb, spin = packed[g]
        t = BF.BS.unit(tl, tb)
        Rfull = BF.BS.rodrigues(t, spin) @ BF.BS.rot_from_to(s, t)
        Rm = BF.axis_angle_scale(Rfull, frac)
        S = Rm.T @ T
        slat = np.degrees(np.arcsin(np.clip(S[2], -1, 1)))
        slon = np.degrees(np.arctan2(S[1], S[0]))
        gy = np.clip(((90 - slat) / 180 * gh).astype(int), 0, gh - 1)
        gx = ((slon + 180) / 360 * gw).astype(int) % gw
        claims = gid[gy, gx] == i
        # highest ground wins the cell, exactly as future_grid resolves it
        z = np.where(claims, BF._bilerp(Zsrc, slat, slon), -9999.0)
        take = z > best
        owner[take] = i
        best[take] = z[take]
        rots[i] = Rfull
    return owner, rots


def bake(age, gid, Zsrc, quiet=False):
    t0 = time.time()
    frac = abs(age) / 250.0
    owner, rots = owner_map(frac, gid, Zsrc)
    lon = (np.arange(VW) + 0.5) / VW * 360 - 180
    lat = 90 - (np.arange(VH) + 0.5) / VH * 180
    LON, LAT = np.meshgrid(lon, lat)
    V0 = BF.BS.unit(LON.ravel(), LAT.ravel())
    V1 = V0.copy()
    dfrac = float(STEP) / 250.0
    for i, Rfull in rots.items():
        m = owner == i
        if not m.any():
            continue
        ang = float(np.arccos(np.clip((np.trace(Rfull) - 1.0) / 2.0, -1.0, 1.0)))
        if ang < 1e-9:
            continue
        ax = np.array([Rfull[2, 1] - Rfull[1, 2],
                       Rfull[0, 2] - Rfull[2, 0],
                       Rfull[1, 0] - Rfull[0, 1]]) / (2.0 * np.sin(ang))
        V1[:, m] = BD.PF.rodrigues(V0[:, m].T, ax, ang * dfrac).T
    dot = np.clip((V0 * V1).sum(0), -1.0, 1.0)
    gc = np.degrees(np.arccos(dot))
    tang = V1 - dot * V0
    dirn = tang / np.maximum(np.linalg.norm(tang, axis=0), 1e-15)
    e, n = BD._tangent_basis(LON.ravel(), LAT.ravel())
    dE = (gc * (dirn.T * e).sum(-1)).reshape(VH, VW)
    dN = (gc * (dirn.T * n).sum(-1)).reshape(VH, VW)
    # Unclaimed cells are new ocean opened between the drifting groups. A hard
    # zero there sits against 2 degrees of motion at the plate edge, and the
    # shader warps its samples by this field -- so the discontinuity would tear
    # the texture along every margin. Filled from the covered values by the
    # same Laplace solve the Phanerozoic path uses, which makes the new floor
    # move with the plates that opened it.
    cov = (owner >= 0).reshape(VH, VW)
    dE = BD.laplace_fill(dE, cov)
    dN = BD.laplace_fill(dN, cov)
    arr = BD._encode(dE, dN, np.zeros_like(dE))
    path = os.path.join(BF.OUT, "fut_%04d_v.webp" % abs(age))
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
    if not quiet:
        print("  %+5d Myr  max %.2f deg  covered %5.1f%%  %5.1f kB  [%.0fs]"
              % (age, float(np.abs(np.stack([dE, dN])).max()),
                 100.0 * float((owner >= 0).mean()),
                 os.path.getsize(path) / 1024.0, time.time() - t0), flush=True)
    return True


def main():
    t0 = time.time()
    gid = BF.rasterise_groups()
    idx = BF.index_dems()
    avail = np.array(sorted(idx.keys()))
    z0 = BF.read_dem(idx[float(avail[np.argmin(np.abs(avail - 0))])])
    Zsrc = BF.resample_dem(z0, 900, 1800)
    print("baking future displacement at %dx%d" % (VW, VH), flush=True)
    n = 0
    for age in range(-STEP, -251, -STEP):
        bake(age, gid, Zsrc)
        n += 1
    print("DONE %d fields in %.1f min" % (n, (time.time() - t0) / 60.0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
