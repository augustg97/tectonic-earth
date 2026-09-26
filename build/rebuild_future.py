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
    """fut_XXXX_v.webp: how far the crust moves to the next keyframe (3.16:
    the future engine's own plate kinematics; see bake_future_v.bake)."""
    import bake_future_v
    return bake_future_v.bake(age, quiet=True)


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


_G = {}


def _setup():
    """Per worker: the present-day source DEM, resampled once."""
    if not _G:
        idx = index_dems()
        avail = np.array(sorted(idx.keys()))
        z0 = read_dem(idx[float(avail[np.argmin(np.abs(avail - 0))])])
        _G["gid"] = BF.rasterise_groups()
        _G["Zsrc"] = resample_dem(z0, 900, 1800)
    return _G


def one(age):
    """Rebuild one future keyframe; returns its report line. Independent of
    every other keyframe (the engine's integrated state is read, not built),
    so the ages can run on separate workers."""
    G = _setup()
    gid, Zsrc = G["gid"], G["Zsrc"]
    ts = time.time()
    frac = abs(age) / 250.0
    gh = BF.future_grid(frac, gid, Zsrc, BF.ELEV_H, BF.ELEV_W)
    gl = BF.future_grid(frac, gid, Zsrc, BF.CLIM_H, BF.CLIM_W)
    sl = sealevel_for(age)
    gh = gh - sl
    gl = gl - sl
    BF.export(age, gh, gl[::-1], "fut")
    act = bake_future_fabric(age, frac)     # reads BF.LAST_BELT from the future_grid above
    dmax = bake_future_disp(age, frac, gid, Zsrc)
    land = float((gh > 0).sum()) / gh.size * 100.0
    return (f"  {age:+5d} Myr  land {land:5.2f}%  max {gh.max():6.0f} m  "
            f"fabric {act if act is not None else -1:.1f}%  "
            f"disp {dmax if dmax is not None else -1:.2f}deg  [{time.time()-ts:.0f}s]")


def main():
    """../venv/bin/python rebuild_future.py [--workers N] [ages...]"""
    t0 = time.time()
    args = sys.argv[1:]
    workers = 1
    if "--workers" in args:
        i = args.index("--workers")
        workers = int(args[i + 1])
        del args[i:i + 2]
    ages = [int(a) for a in args] or list(range(-STEP, -251, -STEP))
    # THE ELEVATION PASS BELOW ORDERS THE HIGH-RES GRID BEFORE THE CLIMATE ONE,
    # AND bake_future_fabric reads the belt the SECOND future_grid call left in
    # BF.LAST_BELT -- both within one worker, so the pairing holds per age.
    print(f"future rebuild: {len(ages)} keyframes on {workers} worker(s)", flush=True)
    n = 0
    if workers <= 1:
        for age in ages:
            n += 1
            print(one(age) + f"  ({n}/{len(ages)})", flush=True)
    else:
        from multiprocessing import Pool
        with Pool(workers) as pool:
            for line in pool.imap_unordered(one, ages):
                n += 1
                print(line + f"  ({n}/{len(ages)})", flush=True)
    print(f"future: {n} keyframes rebuilt in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0 if n == len(ages) else 1


if __name__ == "__main__":
    sys.exit(main())
