"""The REAL sea-floor age grid, carried backwards through the rotation model.

Why this exists alongside crustage.py. The isochron model reconstructs age from
the Merdith topologies, and measured against the published present-day age grid
it correlates only 0.41, with a median error of 33 Myr. That is not a bug to be
tuned out: Merdith et al. is a deep-time model built to get CONTINENTS right
across a billion years, and its Cenozoic ocean-basin detail is coarser than a
model built for the purpose. So where real data exists, use real data.

Muller et al. (2019) publish the age of every surviving piece of ocean floor at
0.1 degrees. A cell whose age today is A0 existed at time T if and only if
A0 > T, and its age then was A0 - T; where it was then follows from rotating it
back on its own plate. That gives a genuine, surveyed age grid for as far back
as ocean crust survives -- and nothing beyond, because beyond that the crust was
subducted and there is no record to reconstruct.

The crossover is not a matter of taste. Coverage falls away as the crust that
survives today gets younger than the target time, and the isochron model takes
over where the data runs out. Between them:

    0 Ma           surveyed, complete
    0-80 Ma        surveyed, near-complete -- most sea floor is younger than this
    80-180 Ma      surveyed but thinning as older crust is subducted
    >180 Ma        modelled: essentially no crust of that age survives anywhere
"""
import os
import math

import numpy as np
import pygplates

import crustage

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "..", "data", "Muller2019_PresentDay_AgeGrid.nc")
STATIC = os.path.join(crustage.MODEL, "shapes_static_polygons_Merdith_et_al.gpml")
CACHE = os.path.join(HERE, "cache", "realage")

_PRESENT = None      # (age0[H,W], pid[H,W]) at working resolution


def present(h=512, w=1024):
    """Present-day age and plate id, on the working grid."""
    global _PRESENT
    if _PRESENT is not None and _PRESENT[0].shape == (h, w):
        return _PRESENT
    import scipy.ndimage as ndi
    from scipy.io import netcdf_file
    f = netcdf_file(GRID, "r", mmap=False)
    z = np.array(f.variables["z"].data, np.float32)
    lat = np.array(f.variables["lat"].data)
    if lat[0] < lat[-1]:
        z = z[::-1]                      # row 0 = north, as everywhere else here
    z = z[:, :-1]                        # the +180 column duplicates -180
    zi = ndi.zoom(np.nan_to_num(z, nan=-1.0), (h / z.shape[0], w / z.shape[1]), order=0)
    age0 = np.where(zi < 0, np.nan, zi).astype(np.float32)

    # Plate id per cell, from the model's own static polygons, so the rotation
    # that carries a cell back is the one its plate actually took.
    feats = pygplates.FeatureCollection(STATIC)
    polys = []
    pygplates.reconstruct(feats, crustage.rotmodel(), polys, 0.0)
    pp = pygplates.PlatePartitioner([p for p in polys], crustage.rotmodel())
    ch, cw = 180, 360
    la = 90.0 - (np.arange(ch) + 0.5) / ch * 180.0
    lo = (np.arange(cw) + 0.5) / cw * 360.0 - 180.0
    small = np.full((ch, cw), -1, np.int32)
    for j in range(ch):
        for i in range(cw):
            pl = pp.partition_point(pygplates.PointOnSphere(float(la[j]), float(lo[i])))
            if pl is not None:
                small[j, i] = pl.get_feature().get_reconstruction_plate_id()
    jj = (np.arange(h) * ch // h).clip(0, ch - 1)
    ii = (np.arange(w) * cw // w).clip(0, cw - 1)
    pid = small[jj[:, None], ii[None, :]]
    _PRESENT = (age0, pid)
    return _PRESENT


def at(T, h=512, w=1024):
    """(age_myr, valid) at time T, from surveyed crust carried back.

    Scattered forward-style: every surviving cell is rotated back to where it
    was, then gathered onto the target grid by nearest neighbour. Rotating the
    GRID instead would need the inverse plate assignment at T, which is the
    thing we are trying to establish.
    """
    from scipy.spatial import cKDTree
    age0, pid = present(h, w)
    keep = np.isfinite(age0) & (age0 > T) & (pid >= 0)
    if keep.sum() < 64:
        return np.full((h, w), np.nan, np.float32), np.zeros((h, w), bool)

    lat1d = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon1d = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon1d, lat1d)
    rot = crustage.rotmodel()

    P, A = [], []
    for p in np.unique(pid[keep]):
        m = keep & (pid == p)
        if m.sum() == 0:
            continue
        try:
            fr = rot.get_rotation(float(T), int(p), 0.0)
        except Exception:
            continue
        if fr is None:
            continue
        xyz = crustage.xyz_of(LON[m], LAT[m])
        P.append(xyz @ crustage._rotmat(fr).T)
        A.append(age0[m] - T)
    if not P:
        return np.full((h, w), np.nan, np.float32), np.zeros((h, w), bool)
    P = np.concatenate(P); A = np.concatenate(A).astype(np.float32)

    G = crustage.xyz_of(LON, LAT).reshape(-1, 3)
    d, i = cKDTree(P).query(G, k=1)
    ang = np.degrees(2.0 * np.arcsin(np.clip(d * 0.5, 0.0, 1.0)))
    # Only claim a cell if a reconstructed parcel actually lands near it. Past
    # about a degree the nearest surviving parcel is not evidence about this
    # cell, it is the edge of a hole where the crust was subducted.
    ok = (ang <= 1.2).reshape(h, w)
    out = np.where(ok, A[i].reshape(h, w), np.nan).astype(np.float32)
    return out, ok


def cached(T, h=512, w=1024):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"real_{int(round(T)):05d}_{h}x{w}.npz")
    if os.path.exists(f):
        z = np.load(f)
        return z["age"], z["ok"]
    a, ok = at(T, h, w)
    np.savez_compressed(f, age=a, ok=ok)
    return a, ok


if __name__ == "__main__":
    import sys, time
    print(" T (Ma)   surveyed cells   % of globe   mean age")
    for T in (0, 20, 40, 60, 80, 100, 120, 150, 180, 200):
        t0 = time.time()
        a, ok = at(float(T))
        print(f"  {T:4d}      {ok.sum():8d}       {100*ok.mean():5.1f}%     "
              f"{np.nanmean(a) if ok.any() else float('nan'):6.1f} Myr   [{time.time()-t0:.1f}s]")
