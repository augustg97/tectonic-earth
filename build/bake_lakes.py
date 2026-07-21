"""Bake a per-keyframe LAKE field from a hydrological WATER BALANCE.

A basin holds a lake only if its water budget supports one. Pure topographic
depression-filling puts a lake in every hollow, which over-produces them and
ignores climate; this instead balances water in against water out:

  runoff  = max(0, rainfall - evaporative demand)      per cell, from the era's
            own climate fields, so it tracks how wet the world was at the time
  inflow  = sum of runoff over a basin's CATCHMENT      (a watershed segmentation,
            so rivers count -- a dry basin fed by wet uplands, like Lake Chad
            from the Sahel, still fills)
  outflow = lake-surface evaporation x lake area
  lake fills to the level where inflow == outflow, CAPPED at the spill point
            (a basin with more water than it can evaporate overflows and becomes
            a through-flowing lake at its spill level -- Baikal, the rift lakes)

So wet catchments make big lakes, arid basins with no river supply make none,
and the same basin waxes and wanes as the climate and terrain change through
time. Depth (surface - terrain) ships as the sqrt-encoded `_w` texture.

    ../venv/bin/python bake_lakes.py             # all keyframes
    ../venv/bin/python bake_lakes.py phan_0000   # one, with stats

Reads only the small elevation + rainfall textures; NOT the 35-min field rebuild.
"""
import os, sys, glob
import numpy as np
from PIL import Image
from scipy.ndimage import (gaussian_filter, label as cclabel, mean as nd_mean,
                           sum as nd_sum, maximum as nd_max)
from skimage.morphology import reconstruction
from skimage.segmentation import watershed

from fieldpack import dec_elev, RF_MAX
from climate import climate_at

FIELDS = os.path.join(os.path.dirname(__file__), "..", "web", "fields")
ELEV_W, ELEV_H = 2048, 1024
TEMP_REF = -0.55                 # matches render.py / the shader

DMAX = 2600.0    # depth (m) that encodes to full white (sqrt curve -> shore detail)
DMIN = 10.0      # ignore water shallower than this (sub-grid noise)
# Keep a lake body only if it is either sizeable OR genuinely deep: this drops
# the shallow speckle the coarse DEM throws off in wet lowlands (the Amazon
# drains to the sea, it should not pond) while sparing small but deep real lakes
# like Baikal, whose footprint is only a handful of 20 km cells.
MIN_AREA = 22    # cells
KEEP_DEEP = 140.0  # metres -- a body deeper than this survives regardless of area
# Runoff = rainfall x a coefficient that ramps up with the humidity index
# h = Rf/(0.46*pet) (the app's own dryness calibration): a desert sheds almost
# nothing, a rainforest sheds most of its rain. Positive wherever it is genuinely
# wet, so mountain and monsoon catchments feed their basins.
RUN_H0, RUN_H1 = 0.15, 0.85
EVAP_K = 0.65            # lake-surface evaporation as a multiple of pet
AREA_K = 0.55           # overall lake-size scale (tune abundance)
# Deep basins hold permanent water even under a semi-arid sky (huge volume and
# catchment buffer them -- Baikal, Tanganyika, Titicaca), so a basin fills to at
# least this fraction of its own depth once it is this deep, independent of the
# year's water budget. Shallow basins get NO floor and live or die by climate.
DEEP_LO, DEEP_HI, DEEP_MAX = 90.0, 320.0, 0.60

# A few notable lakes sit in basins too shallow for the 20 km global DEM to
# resolve (glacially scoured lows, chiefly), so they never emerge from the fill.
# We seed only the BASIN -- a gentle hollow carved into the fill DEM (never the
# shipped elevation) at the lake's present position, within its own age window --
# and let the SAME water balance decide whether and how much it holds. Not an
# authored lake: a hint that a depression exists, filled by the same physics as
# every other basin. Each lobe: (dlon, dlat, semiMajorDeg, semiMinorDeg, azDeg).
SEED_LAKES = [
    # The Great Lakes as five carved lobes at their real positions/orientations;
    # they are a Pleistocene feature, so only the last few Myr of frames.
    dict(lon=-84.0, lat=45.6, carve=150.0, max_age=3.0, lobes=[
        (-3.6, 2.3, 2.70, 1.13, 104), (-3.1, -1.5, 2.25, 0.79, 4),
        (1.9, -0.5, 1.35, 0.92, 150), (2.9, -3.3, 1.80, 0.41, 71),
        (6.3, -1.7, 1.44, 0.39, 80)]),
]


def enc_depth(d):
    return np.clip(np.sqrt(np.clip(d / DMAX, 0.0, 1.0)), 0.0, 1.0)


def fill_depressions(Z, sea=0.0):
    """Water surface after every closed basin fills to its spill point; the ocean
    (Z<=sea) and grid border are the outlets."""
    Z = Z.astype(np.float32)
    seed = np.full_like(Z, Z.max())
    outlet = Z <= sea
    outlet[0, :] = outlet[-1, :] = outlet[:, 0] = outlet[:, -1] = True
    seed[outlet] = Z[outlet]
    return reconstruction(seed, Z, method="erosion")


def parse_age(base):
    kind, num = base.split("_")
    a = int(num)
    return -a if kind == "fut" else a          # future frames carry negative age


def temperature(Z, age):
    lat = np.linspace(90, -90, Z.shape[0])[:, None] * np.ones((1, Z.shape[1]))
    s2 = np.sin(np.radians(lat)) ** 2
    cl = climate_at(age)
    zpos = np.clip(Z, 0.0, None)
    return (26.0 - 24.0 * s2 - 26.0 * s2 ** 3) \
        + (cl["temp"] - TEMP_REF) * (4.0 + 15.0 * s2) - zpos * 0.0058


def seed_depth(Z, age):
    """Depth field for the seeded lakes whose basins the global DEM can't resolve
    (land only, within each lake's age window). Deepest at each lobe's centre so
    it depth-shades like a real lake."""
    h, w = Z.shape
    out = np.zeros((h, w), np.float32)
    lat = np.linspace(90, -90, h)[:, None] * np.ones((1, w))
    lon = (np.arange(w) / w * 360.0 - 180.0)[None, :] * np.ones((h, 1))
    for sk in SEED_LAKES:
        if abs(age) > sk["max_age"]:
            continue
        bump = np.zeros((h, w), np.float32)
        for dlon, dlat, a, b, az in sk["lobes"]:
            clon, clat = sk["lon"] + dlon, sk["lat"] + dlat
            A = np.radians(az); sA, cA = np.sin(A), np.cos(A)
            dx = ((lon - clon + 540.0) % 360.0 - 180.0) * np.cos(np.radians(clat))
            dy = lat - clat
            al = dx * sA + dy * cA; ac = dx * cA - dy * sA
            er = np.sqrt((al / a) ** 2 + (ac / b) ** 2)
            bump = np.maximum(bump, np.clip(1.0 - er, 0.0, 1.0))   # union of lobes
        out = np.maximum(out, np.where(Z >= 0.0, sk["carve"] * bump, 0.0))
    return out


def lake_depth(Z, Rf, T, age=0.0):
    h, w = Z.shape
    coslat = np.clip(np.cos(np.radians(np.linspace(90, -90, h)))[:, None]
                     * np.ones((1, w)), 0.02, None)
    pet = np.clip((T + 12.0) / 34.0, 0.16, 1.35)
    hum = Rf / (0.46 * pet)                              # humidity index (0 desert .. 1+ wet)
    rcoef = np.clip((hum - RUN_H0) / (RUN_H1 - RUN_H0), 0.0, 1.0)
    runoff = Rf * rcoef                                  # streamflow leaving a cell
    evap = EVAP_K * pet                                 # loss per unit lake area

    # De-terrace the 8-bit paleo-DEM before the fill so basins are natural, not
    # staircased (the shipped elevation is untouched -- this feeds only the lakes).
    Zs = gaussian_filter(Z, sigma=1.0, mode="nearest")
    filled = fill_depressions(Zs)

    # Basin bottoms are the flooded hollows; use them (plus the ocean) as the
    # markers of a watershed segmentation, which assigns every land cell to the
    # basin it drains into -- that catchment is what collects the runoff.
    bottoms = (filled - Zs > 1.0) & (Z >= 0.0)
    markers, nb = cclabel(bottoms)
    if nb == 0:
        return np.zeros_like(Z)
    ocean_lbl = nb + 1
    markers[Z < 0.0] = ocean_lbl
    catch = watershed(Zs, markers=markers)

    flat = catch.ravel()
    inflow = np.bincount(flat, weights=(runoff * coslat).ravel(),
                         minlength=ocean_lbl + 1)
    # spill level and lake-surface evaporation, per basin, from its bottom cells
    labels = np.arange(1, nb + 1)
    spill = np.zeros(nb + 2, np.float32)
    evap_b = np.full(nb + 2, 1e-3, np.float32)
    spill[1:nb + 1] = nd_mean(filled, markers, labels)
    evap_b[1:nb + 1] = np.maximum(1e-3, nd_mean(evap, markers, labels))
    target = np.zeros(nb + 2)                            # lake area the budget supports
    target[1:nb + 1] = AREA_K * inflow[1:nb + 1] / evap_b[1:nb + 1]

    # Per basin, take the HIGHER of two water levels: the one the water budget
    # sustains against evaporation, and a deep-basin floor (permanent lakes) --
    # both capped at the spill. Cells are grouped by basin with one sort, then
    # each basin's own cells sorted by height to read off the level for an area.
    Zf = Z.ravel(); Af = coslat.ravel()
    land = (flat >= 1) & (flat <= nb)
    idx = np.flatnonzero(land)
    cb = flat[idx]
    o = np.argsort(cb, kind="stable")
    idx = idx[o]; cb = cb[o]
    bounds = np.searchsorted(cb, np.arange(1, nb + 2))
    level = np.zeros(nb + 2, np.float32)
    for b in range(1, nb + 1):
        s, e = bounds[b - 1], bounds[b]
        if e <= s:
            continue
        ci = idx[s:e]
        zc = Zf[ci]; ac = Af[ci]
        so = np.argsort(zc); zc = zc[so]; ac = ac[so]
        floor = zc[0]; sp = spill[b]
        depth_basin = sp - floor
        # deep-basin floor: fill at least this fraction of the basin's depth
        deep_frac = DEEP_MAX * np.clip((depth_basin - DEEP_LO) / (DEEP_HI - DEEP_LO), 0.0, 1.0)
        lvl_deep = floor + deep_frac * depth_basin
        # water-budget level: raise until submerged area == supported area
        lvl_bal = floor
        if target[b] > 0.0:
            cum = np.cumsum(ac)
            k = min(int(np.searchsorted(cum, min(target[b], cum[-1]))), len(zc) - 1)
            lvl_bal = zc[k]
        level[b] = min(max(lvl_bal, lvl_deep), sp)

    Lcell = level[flat].reshape(h, w)
    depth = np.maximum(0.0, Lcell - Z)
    depth[Z < 0.0] = 0.0
    # keep a lake body if it is large enough OR deep enough
    lbl, nlab = cclabel(depth >= DMIN)
    if nlab:
        ids = np.arange(1, nlab + 1)
        area = nd_sum(np.ones_like(depth), lbl, ids)
        dmax = nd_max(depth, lbl, ids)
        keep = np.concatenate([[False], (area >= MIN_AREA) | (dmax >= KEEP_DEEP)])
        depth[~keep[lbl]] = 0.0
    # notable lakes the global DEM can't resolve, added at their known basins
    depth = np.maximum(depth, seed_depth(Z, age))
    return depth


def load_rain(epath):
    rpath = epath.replace("_e.webp", "_r.webp")
    if not os.path.exists(rpath):
        return None
    r = Image.open(rpath).convert("L").resize((ELEV_W, ELEV_H), Image.BILINEAR)
    return np.asarray(r, np.float32) / 255.0 * RF_MAX


def bake_one(epath, stats=False):
    base = os.path.splitext(os.path.basename(epath))[0].replace("_e", "")
    wpath = epath.replace("_e.webp", "_w.webp")
    e = np.asarray(Image.open(epath).convert("RGB"))[..., 0].astype(np.float32) / 255.0
    Z = dec_elev(e)
    Rf = load_rain(epath)
    age = parse_age(base)
    if Rf is None:
        depth = np.zeros_like(Z)
    else:
        depth = lake_depth(Z, Rf, temperature(Z, age), age)
    enc = (enc_depth(depth) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(enc, "L").save(wpath, "WEBP", lossless=True, method=6)
    if stats:
        lake = depth > 0
        h, w = Z.shape
        cw = np.cos(np.radians(np.linspace(90, -90, h)))[:, None] * np.ones((1, w))
        land = Z >= 0
        cov = 100.0 * (cw * lake).sum() / (cw * land).sum()
        print(f"{base}: lake {cov:.2f}% of land  max {depth.max():.0f} m  "
              f"cells {lake.sum()}  -> {os.path.basename(wpath)}")
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
