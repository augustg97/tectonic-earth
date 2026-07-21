"""Bake a per-keyframe LAKE field from the shipped elevation textures.

Lakes are not authored here -- they are DERIVED from the reconstructed terrain,
the same way coastlines and rivers are. For each keyframe we depression-fill the
elevation grid (priority-flood / morphological reconstruction) with the OCEAN as
the base level: water pools in every closed basin up to the lowest lip over which
it would spill to the sea. The lake DEPTH (filled - terrain) is written as a new
grayscale `_w` texture the shader samples and interpolates exactly like `_e`.

Because it is computed from each frame's own terrain, the lake system EVOLVES:
Baikal's rift only holds water once the rift exists, endorheic basins fill and
dry as the topography changes, and unnamed basins appear wherever the landscape
actually encloses one -- no stamped discs, no fixed positions.

    ../venv/bin/python bake_lakes.py            # all keyframes
    ../venv/bin/python bake_lakes.py phan_0000  # one, with stats

Fast (morphological reconstruction is C); ~a few minutes for 251 frames, and it
reads/writes only the small elevation textures -- NOT the 35-min field rebuild.
"""
import os, sys, glob
import numpy as np
from PIL import Image
from skimage.morphology import reconstruction, remove_small_objects
from scipy.ndimage import gaussian_filter

from fieldpack import dec_elev, Z_RANGE, RF_MAX

FIELDS = os.path.join(os.path.dirname(__file__), "..", "web", "fields")
ELEV_W, ELEV_H = 2048, 1024

DMAX = 2600.0   # depth (m) that encodes to full white; sqrt curve concentrates
                # precision at the shore, where the eye reads the waterline
DMIN = 10.0     # shallower than this is DEM noise or a damp flat, not a lake
MIN_AREA = 5    # drop lake blobs smaller than this many cells (speckle)
# Topographic fill assumes every basin is brim-full, which is only true where
# inflow >= evaporation. In arid basins water sits far below the spill point or
# dries to a salt pan, so a shallow arid flood is not open water. Require extra
# depth as the climate dries: deep basins (Caspian) survive everywhere, thin
# sheet-floods over deserts drop out.
ARID_RAIN = 0.30     # rainfall (0..1 of RF_MAX) below which aridity kicks in
ARID_BOOST = 150.0   # extra depth (m) a hyper-arid basin must reach to count


def enc_depth(d):
    return np.clip(np.sqrt(np.clip(d / DMAX, 0.0, 1.0)), 0.0, 1.0)


def fill_depressions(Z, sea=0.0):
    """Water surface after every closed land basin fills to its spill point.
    The ocean (Z<=sea) and the grid border are the outlets water drains to."""
    Z = Z.astype(np.float32)
    seed = np.full_like(Z, Z.max())
    outlet = Z <= sea
    outlet[0, :] = outlet[-1, :] = outlet[:, 0] = outlet[:, -1] = True
    seed[outlet] = Z[outlet]
    # reconstruction by erosion lowers `seed` toward `Z` but never below it,
    # so interior pits rise only to the lowest path out -- the spill level.
    filled = reconstruction(seed, Z, method="erosion")
    return filled


def load_rain(epath):
    """Rainfall (0..1 of RF_MAX) resampled to the elevation grid, or None."""
    rpath = epath.replace("_e.webp", "_r.webp")
    if not os.path.exists(rpath):
        return None
    r = Image.open(rpath).convert("L").resize((ELEV_W, ELEV_H), Image.BILINEAR)
    return np.asarray(r, np.float32) / 255.0


def lake_depth(Z, rain01=None):
    # The paleo-DEMs are 8-bit and coarse, so their terrain comes in flat
    # terraces; depression-filling those raw gives blocky, staircased lake
    # outlines. A light gaussian rounds the terraces into natural basins before
    # the fill (the shipped elevation texture is untouched -- this smoothing only
    # feeds the lake computation), and the shoreline noise in the shader carries
    # the rest of the fine detail.
    Zs = gaussian_filter(Z, sigma=1.0, mode="nearest")
    filled = fill_depressions(Zs)
    depth = np.maximum(0.0, filled - Zs)
    depth[Z < 0.0] = 0.0                 # the sea (real coastline) is not a lake
    dmin = np.full_like(depth, DMIN)
    if rain01 is not None:
        arid = np.clip((ARID_RAIN - rain01) / ARID_RAIN, 0.0, 1.0)
        dmin = DMIN + arid * ARID_BOOST
    mask = depth >= dmin
    mask = remove_small_objects(mask, min_size=MIN_AREA)
    depth[~mask] = 0.0
    return depth


def bake_one(epath, stats=False):
    wpath = epath.replace("_e.webp", "_w.webp")
    e = np.asarray(Image.open(epath).convert("RGB"))[..., 0].astype(np.float32) / 255.0
    Z = dec_elev(e)
    depth = lake_depth(Z, load_rain(epath))
    enc = (enc_depth(depth) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(enc, "L").save(wpath, "WEBP", lossless=True, method=6)
    if stats:
        wet = depth > 0
        frac = 100.0 * wet.mean()
        print(f"{os.path.basename(epath)}: lake cover {frac:.3f}%  "
              f"max depth {depth.max():.0f} m  cells {wet.sum()}  -> {os.path.basename(wpath)}")
    return wpath


def main():
    args = sys.argv[1:]
    if args:
        for a in args:
            p = a if a.endswith("_e.webp") else os.path.join(FIELDS, a + "_e.webp")
            bake_one(p, stats=True)
        return
    files = sorted(glob.glob(os.path.join(FIELDS, "*_e.webp")))
    print(f"baking {len(files)} lake fields...")
    for i, p in enumerate(files):
        bake_one(p)
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(files)}")
    print("done")


if __name__ == "__main__":
    main()
