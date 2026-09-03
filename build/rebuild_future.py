"""Rebuild ONLY the 50 future keyframes, in place.

S1-S5 (WP-07) all live in future_grid, so the Phanerozoic and Precambrian frames
are bit-identical to what is already on disk and re-rendering them would cost
hours for no change. This mirrors main()'s future block exactly -- same eustatic
correction, same export tags, same motion coarsening -- and then the manifest is
refreshed from the files on disk by refresh_manifest.py.

Run it, do not background it without a log: a backgrounded build that dies is a
trap this project has already fallen into twice (README 7.11).
"""
import os, sys, time
import numpy as np

from build_frames import index_dems, read_dem, sealevel_for
from render import resample_dem
import build_fields as BF
import motion as MO
import build_tectonic as BT

STEP = BF.STEP
TW, TH = BT.TW, BT.TH


def bake_future_disp(age, frac, gid, Zsrc):
    """Write fut_XXXX_v.webp: how far the crust moves to the next keyframe.

    The future frames shipped no displacement field, so the app cross-faded
    them -- the very double-exposure H1 was built to end, still happening in
    the future era. It is derivable exactly: every group turns about ONE axis
    by an angle proportional to frac, so the rotation carrying the crust from
    one keyframe to the next is a rotation about that same axis by the angle
    difference. Same convention as build_displacement (apply the interval
    rotation to this grid's own directions, store east/north in the tangent
    frame), so the shader needs no new code. B is the tear channel, which
    only the tectonic bake consumes; it stays neutral here because the
    future fabric is derived from the belt instead.
    """
    import numpy as np
    from PIL import Image
    import build_displacement as BD
    owner = BF.LAST_BELT.get("owner")
    if owner is None:
        return None
    VW, VH = BD.VW, BD.VH
    # this grid's own directions
    lon = (np.arange(VW) + 0.5) / VW * 360 - 180
    lat = 90 - (np.arange(VH) + 0.5) / VH * 180
    LON, LAT = np.meshgrid(lon, lat)
    V0 = BF.BS.unit(LON.ravel(), LAT.ravel())
    # owner map came back at the last future_grid resolution; sample it here
    oh, ow = owner.shape
    oy = np.clip(((90 - LAT) / 180 * oh).astype(int), 0, oh - 1)
    ox = (((LON + 180) / 360 * ow).astype(int)) % ow
    own = owner[oy, ox].ravel()
    packed = BF._packed_targets(gid, Zsrc)
    gh, gw = gid.shape
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    dfrac = float(STEP) / 250.0
    V1 = V0.copy()
    for i, g in enumerate(BF.GROUPS):
        m = own == i
        if not m.any():
            continue
        gm = gid == i
        if not gm.any():
            continue
        s = BF.BS.unit(GLON[gm], GLAT[gm]).mean(axis=1); s /= np.linalg.norm(s)
        tl, tb, spin = packed[g]
        t = BF.BS.unit(tl, tb)
        Rfull = BF.BS.rodrigues(t, spin) @ BF.BS.rot_from_to(s, t)
        # axis and total angle of the group's whole journey
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
    nrm = np.maximum(np.linalg.norm(tang, axis=0), 1e-15)
    dirn = tang / nrm
    e, n = BD._tangent_basis(LON.ravel(), LAT.ravel())
    dE = (gc * (dirn.T * e).sum(-1)).reshape(VH, VW)
    dN = (gc * (dirn.T * n).sum(-1)).reshape(VH, VW)
    arr = BD._encode(dE, dN, np.zeros_like(dE))
    Image.fromarray(arr).save(
        os.path.join(BF.OUT, "fut_%04d_v.webp" % abs(age)), "WEBP",
        lossless=True, method=6)
    return float(np.abs(np.stack([dE, dN])).max())


def bake_future_fabric(age, frac):
    """Write fut_XXXX_t.webp: the fold fabric of the future's own orogens.

    The future frames shipped NO tectonic field, so every collisional belt
    reached the shader as isotropic noise -- round hummocks where a real
    orogen is a set of parallel ridges, which is what "the mountains look
    weird" meant. The belt raster future_grid just built IS the orogen:
    its strength is the shortening, and its ISO-CONTOUR TANGENT is the
    strike, exactly as a fold axis runs along a belt rather than across it.
    Encoded identically to build_tectonic (R sqrt-companded shortening,
    G,B the double angle), so the shader needs no new code.
    """
    import numpy as np
    from scipy.ndimage import gaussian_filter, zoom as ndzoom
    from PIL import Image
    belt = BF.LAST_BELT.get("belt")
    if belt is None:
        return None
    h, w = belt.shape
    b = ndzoom(belt, (TH / h, TW / w), order=1)
    b = np.clip(gaussian_filter(b, 1.0, mode=("nearest", "wrap")), 0.0, 1.0)
    # gradient in (east, north); rows run north->south, hence the sign
    gy, gx = np.gradient(b)
    gN, gE = -gy, gx
    mag = np.sqrt(gE * gE + gN * gN) + 1e-9
    # strike = tangent to the contour = perpendicular to the gradient
    tE, tN = -gN / mag, gE / mag
    c2, s2 = tE * tE - tN * tN, 2.0 * tE * tN
    sh = b * 0.35                       # clears the shader's 0.30 fabric gate
    fade = np.clip(sh / (0.10 * BT.SHORT_REF), 0.0, 1.0)
    arr = BT._encode(sh, c2 * fade, s2 * fade)
    import build_arc                    # the belt-type alpha, as build_tectonic.bake ships it
    arr = build_arc.attach(arr, age)
    path = os.path.join(BF.OUT, "fut_%04d_t.webp" % abs(age))
    Image.fromarray(arr, "RGBA").save(path, "WEBP", lossless=True, method=6, exact=True)
    return float((sh > 0.045).mean()) * 100.0


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
        act = bake_future_fabric(age, frac)
        dmax = bake_future_disp(age, frac, gid, Zsrc)
        n += 1
        land = float((gh > 0).sum()) / gh.size * 100.0
        print(f"  {age:+5d} Myr  land {land:5.2f}%  max {gh.max():6.0f} m  "
              f"fabric {act if act is not None else -1:.1f}%  "
              f"disp {dmax if dmax is not None else -1:.2f}deg  "
              f"[{time.time()-ts:.0f}s]  ({n}/50)", flush=True)

    print(f"future: {n} keyframes rebuilt in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
