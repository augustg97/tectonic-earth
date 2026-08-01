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
    path = os.path.join(BF.OUT, "fut_%04d_t.webp" % abs(age))
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
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
        n += 1
        land = float((gh > 0).sum()) / gh.size * 100.0
        print(f"  {age:+5d} Myr  land {land:5.2f}%  max {gh.max():6.0f} m  "
              f"fabric {act if act is not None else -1:.1f}%  "
              f"[{time.time()-ts:.0f}s]  ({n}/50)", flush=True)

    print(f"future: {n} keyframes rebuilt in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
