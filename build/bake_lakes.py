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

from fieldpack import dec_elev, RF_MAX, Z_RANGE
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
# ...but only where there is water to keep them: the floor is scaled by the
# catchment's humidity index, full above this. A hyper-arid basin holds what its
# water budget supports and no more -- without this a flat desert basin 130 m
# deep was flooded to a tenth of its depth across 670,000 km2 at 150 Ma, and a
# 500 m plateau hole in the +250 Myr belt, under 0.01 of rainfall, was a lake.
HUM_DEEP = 0.30
# AN OVERFLOWING BASIN IS BREACHED. Where the water budget tops the spill, the
# outflow cuts down its outlet, and a keyframe is millions of years: a shallow
# basin that overflows drains, and only a deep tectonic core keeps standing
# water (Tanganyika, Baikal). Filling every such basin to its lip put the
# wettest lowlands of every era under giant shallow lakes -- 845,000 km2 in the
# Congo and 419,000 km2 in the Amazon at 5 Ma (median depth 21-36 m), 1.7
# million km2 at 150 Ma -- exactly where the real rivers are strongest. The
# present day ships real lake outlines and is unaffected.
#
# The breach is set by the DISCHARGE, not by overflowing alone: an outlet cuts
# down in proportion to what flows through it, so a basin draining a continental
# river incises fast while a rift lake's modest overflow does not. Measured as
# the lake area the budget could support (inflow over evaporation, in cells of
# ~380 km2): the Congo and Amazon basins at 5 Ma ~2,950, the +250 Myr lowland
# lakes 1,340-3,710, against Tanganyika 160 and the East African soda lakes 265
# (overflow ratio alone does not separate them: Amazon 2.2, the rift 1.6).
BREACH_OVERFLOW = True
BREACH_Q = 600.0

# THE RECORD NAMES SOME BASINS AS LAKES, AND THERE IT OUTRANKS THE MODEL'S SKY.
# The two rules above read the catchment's humidity from the climate solve, and
# that solve runs dry over interiors (it is the same lever that keeps Pangaea a
# desert, a trade the user chose). Where the geological record itself names a
# lake -- a "lake" label, inside its own window, at its plate-tracked position
# -- the basin under it is not asked whether the model thinks it is wet enough:
# its deep floor is not scaled down and it is not breached. Measured when the
# two rules landed, water under the record's own lake labels fell from 29
# label-keyframes to 25 (Songliao at 110 and 135 Ma, the Jehol lakes at 130
# and 135, Uinta at 50, Baikal at 30, Tanganyika at 10), every one of them a
# basin the model called too dry to keep. This authors no lake: a basin the DEM
# does not have still holds nothing. Reads the tracks from web/labels.json, so
# the labels must be built before the lakes (build_webdata, then this).
RECORD_R_DEG = 1.2
_RECORD = None


def _record_lakes():
    global _RECORD
    if _RECORD is None:
        import json
        _RECORD = []
        p = os.path.join(os.path.dirname(__file__), "..", "web", "labels.json")
        if os.path.exists(p):
            for it in json.load(open(p)):
                if it.get("t") == "lake":
                    tr = it.get("tr") or [[0, it["lon"], it["lat"]]]
                    _RECORD.append((min(it["a0"], it["a1"]), max(it["a0"], it["a1"]),
                                    [(float(a), float(lo), float(la)) for a, lo, la in tr]))
    return _RECORD


def record_points(age):
    """(lon, lat) of every record-named lake whose window holds this age, at its
    tracked position then (tracks run from the present into the past)."""
    pts = []
    for a0, a1, tr in _record_lakes():
        if not (a0 - 2.5 <= age <= a1 + 2.5):
            continue
        ages = [t[0] for t in tr]
        if age <= ages[0]:
            pts.append((tr[0][1], tr[0][2])); continue
        for i in range(1, len(tr)):
            if tr[i][0] >= age:
                f = (age - tr[i - 1][0]) / max(tr[i][0] - tr[i - 1][0], 1e-6)
                dl = ((tr[i][1] - tr[i - 1][1] + 540.0) % 360.0) - 180.0
                pts.append((((tr[i - 1][1] + f * dl + 540.0) % 360.0) - 180.0,
                            tr[i - 1][2] + f * (tr[i][2] - tr[i - 1][2])))
                break
        else:
            pts.append((tr[-1][1], tr[-1][2]))
    return pts

# A few notable lakes sit in basins too shallow for the 20 km global DEM to
# resolve (glacially scoured lows, chiefly), so they never emerge from the fill.
# We seed only the BASIN -- a gentle hollow carved into the fill DEM (never the
# shipped elevation) at the lake's present position, within its own age window --
# and let the SAME water balance decide whether and how much it holds. Not an
# authored lake: a hint that a depression exists, filled by the same physics as
# every other basin. Each lobe: (dlon, dlat, semiMajorDeg, semiMinorDeg, azDeg).
# (Empty: the present frame now uses REAL lake outlines via bake_present_lakes.py,
# so the Great Lakes no longer need seeding here. Other notable DEM-missed lakes
# could be listed for paleo/future frames if ever needed.)
SEED_LAKES = []


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


def drop_unresolved(Zs, filled, k=1.0):
    """Keep only the closed basins the shipped elevation can actually resolve.

    The lakes are read from the 8-bit sqrt-encoded AVIF, and one code of that
    encoding is (4/255)*sqrt(8000 z): 20 m at 200 m, 63 m at 2 km, 89 m at
    4 km. A basin shallower than one code at its own water level cannot be told
    from quantisation -- and the codec's own error is of that order (33 m rms,
    up to 150 m, over the mountain belts at 400 Ma, where rugged relief costs
    the encoder most). Read literally, that noise pocked every range with
    small lakes: on one keyframe the codec alone doubled the belt lake cover.
    So a flooded region survives only if its deepest point lies at least one
    code below its spill level. Unlike an h-minima transform this leaves the
    basins that do survive their full depth. September 2026."""
    dep = filled - Zs
    lbl, n = cclabel(dep > 1e-3)
    if not n:
        return filled
    ids = np.arange(1, n + 1)
    dmax = nd_max(dep, lbl, ids)
    lvl = nd_max(filled, lbl, ids)
    step = (4.0 / 255.0) * np.sqrt(Z_RANGE * np.maximum(lvl, 0.0))
    keep = np.concatenate([[True], dmax >= k * step])
    return np.where(keep[lbl], filled, Zs).astype(np.float32)


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
    filled = drop_unresolved(Zs, fill_depressions(Zs))

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
    hum_b = np.zeros(nb + 2, np.float32)                 # the catchment's humidity index
    hum_b[1:nb + 1] = nd_mean(hum, catch, labels)
    # basins the record names as lakes at this age (see RECORD_R_DEG above)
    recorded = set()
    rr = max(1, int(round(RECORD_R_DEG / 180.0 * h)))
    for lon, lat in record_points(age):
        y = int(np.clip((90.0 - lat) / 180.0 * h, 0, h - 1))
        x = int(((lon + 180.0) / 360.0 * w)) % w
        if T[y, x] < -10.0:        # a subglacial lake (Vostok) is under ice, not open water
            continue
        cols = np.arange(x - rr, x + rr + 1) % w
        win = markers[max(0, y - rr):y + rr + 1][:, cols]
        recorded.update(int(v) for v in np.unique(win) if 1 <= v <= nb)
        if 1 <= catch[y, x] <= nb:
            recorded.add(int(catch[y, x]))

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
        if b not in recorded:
            deep_frac *= float(np.clip(hum_b[b] / HUM_DEEP, 0.0, 1.0))
        lvl_deep = floor + deep_frac * depth_basin
        # water-budget level: raise until submerged area == supported area
        lvl_bal = floor
        cum = np.cumsum(ac)
        if target[b] > 0.0:
            k = min(int(np.searchsorted(cum, min(target[b], cum[-1]))), len(zc) - 1)
            lvl_bal = zc[k]
        below_spill = float(cum[min(int(np.searchsorted(zc, sp, side="right")), len(zc)) - 1]) if len(zc) else 0.0
        if BREACH_OVERFLOW and b not in recorded and target[b] >= below_spill and target[b] >= BREACH_Q:
            level[b] = min(lvl_deep, sp)          # overflowing: the outlet is cut, the deep core stays
        else:
            level[b] = min(max(lvl_bal, lvl_deep), sp)

    Lcell = level[flat].reshape(h, w)
    # Depth against the SMOOTHED surface, not the 8-bit one: a lake floor is a
    # few flat terraces a code apart (26 m at 350 m), and depth measured on them
    # jumped a whole code at every terrace edge, so the shoreline was the terrace
    # outline -- rectangular protrusions and stair-steps along the grid on every
    # lowland lake. Against Zs the depth tapers across the edge and the shore
    # follows a contour.
    depth = np.maximum(0.0, Lcell - Zs)
    depth[Z < 0.0] = 0.0
    # keep a lake body if it is large enough OR deep enough
    lbl, nlab = cclabel(depth >= DMIN)
    if nlab:
        ids = np.arange(1, nlab + 1)
        area = nd_sum(np.ones_like(depth), lbl, ids)
        dmax = nd_max(depth, lbl, ids)
        keep = np.concatenate([[False], (area >= MIN_AREA) | (dmax >= KEEP_DEEP)])
        # ...or if the record names it: the size rule clears the DEM's speckle,
        # and a lake the record names is not speckle at any size (Uinta at 50 Ma
        # was 3 cells, Baikal at 30 Ma one: the lake's first, small stages)
        if recorded:
            on_rec = np.isin(catch, np.fromiter(recorded, np.int64)) & (lbl > 0)
            keep[np.unique(lbl[on_rec])] = True
        depth[~keep[lbl]] = 0.0
    # notable lakes the global DEM can't resolve, added at their known basins
    depth = np.maximum(depth, seed_depth(Z, age))
    return depth


def load_rain(epath):
    rpath = epath.replace("_e.avif", "_r.webp")
    if not os.path.exists(rpath):
        return None
    r = Image.open(rpath).convert("L").resize((ELEV_W, ELEV_H), Image.BILINEAR)
    return np.asarray(r, np.float32) / 255.0 * RF_MAX


def bake_one(epath, stats=False):
    base = os.path.splitext(os.path.basename(epath))[0].replace("_e", "")
    wpath = epath.replace("_e.avif", "_w.webp")
    # Resized to THIS module's working grid. The lake field ships at 2048x1024
    # and the elevation is 4096x2048, and nothing reconciled them: load_rain
    # resizes to the small grid while the elevation was read at native size,
    # so lake_depth got a (1024,2048) rainfall against a (2048,4096) terrain
    # and refused to broadcast. Latent until something rebaked every frame.
    _im = Image.open(epath).convert("RGB").resize((ELEV_W, ELEV_H), Image.BILINEAR)
    e = np.asarray(_im)[..., 0].astype(np.float32) / 255.0
    Z = dec_elev(e)
    Rf = load_rain(epath)
    age = parse_age(base)
    if Rf is None:
        depth = np.zeros_like(Z)
    else:
        depth = lake_depth(Z, Rf, temperature(Z, age), age)
    enc = (enc_depth(depth) * 255.0 + 0.5).astype(np.uint8)
    # RGB, NOT grayscale any more. R is the lake depth this file has always
    # carried; G is the DRY-BASIN mask, which tells the shader that ground below
    # sea level here is exposed rather than submerged. It has to live in a
    # second channel of an existing per-frame texture rather than a new file:
    # the shader must know before it decides land or sea, and a grayscale image
    # has no room to say it. (G == R on a grayscale decode, so every frame has
    # to be rebaked with this in place, or old files would read their own lake
    # depth as a dry mask and drain every lake on Earth.)
    import epeiric as _EP
    # Z, not just the shape: the basin outline IS the bathymetry now, so the
    # mask cannot be built without it. Omitting it returns an empty mask and
    # the feature silently does not ship.
    dry = _EP.messinian_mask(depth.shape, float(age), Z)
    gch = (np.clip(dry, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    rgb = np.dstack([enc, gch, np.zeros_like(enc)])
    Image.fromarray(rgb, "RGB").save(wpath, "WEBP", lossless=True, method=6)
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
            p = a if a.endswith("_e.avif") else os.path.join(FIELDS, a + "_e.avif")
            bake_one(p, stats=True)
        return
    files = sorted(glob.glob(os.path.join(FIELDS, "*_e.avif")))
    print(f"baking {len(files)} lake fields...")
    for i, p in enumerate(files):
        bake_one(p)
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(files)}")
    print("done")


if __name__ == "__main__":
    main()
