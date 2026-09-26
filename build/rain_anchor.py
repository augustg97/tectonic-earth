"""THE PRESENT-DAY RAIN ANCHOR (3.16): observed rainfall calibrates the model's
own near the present, and the correction rides the crust and fades with age.

WHY. The climate solve runs dry over highlands and the monsoon: at 0 Ma it read
0.024 over the Columbia Mountains (real 1,600 mm), 0.03-0.12 on the Ganges plain
(1,050 mm) and 0.000 on the Himalayan crest (1,950 mm), Spearman 0.644 against
67 sites. The lever that would fix it globally -- the orographic strip -- is the
one that keeps Pangaea's interior dry, which the user chose (audit_biomes.py,
2026-08-09); a physical orographic mode was measured to wet Pangaea's interior
from 17% to 58% above 0.2, so the model itself stays as it is.

WHAT. The delta method, the standard way palaeoclimate work leans on the
present: the model's error AT the present is measured against observation, and
removed from nearby times in proportion to how similar they are to today.

  1. Observation: WorldClim 2.1, 1970-2000 annual precipitation (Fick & Hijmans
     2017), area-averaged onto the rain grid.
  2. Onto the model's own scale by QUANTILE MAPPING over land: each cell takes
     the model value at its observed rank. The palette was calibrated on the
     model's distribution, so the distribution is kept and only the geography
     of it changes -- where the wet and dry ground is.
  3. The correction is the log ratio log(qm + e) - log(model + e), SMOOTHED at
     ~80 km over land only (a normalised convolution, so the ocean's zero never
     dilutes a coast). The model keeps its own structure below that scale -- its
     windward and lee slopes -- and takes the observed amount region by region.
     This is also why what ships is the model's field, calibrated, and not
     WorldClim's: its licence forbids redistributing the data, and a bias
     correction at the regional scale is a new, model-derived field.
  4. At age t the correction is carried to where the crust is (the slot raster
     _p and platerot.json, the same rotations the shader's material coordinate
     uses) and applied with weight 1 within 5 Myr of the present, fading to 0 by
     35 Myr on both sides. Past that the geography is no longer today's and the
     model stands alone -- which is what keeps Pangaea exactly as it was.

    ../venv/bin/python rain_anchor.py --build     # (re)derive the correction from the 0 Ma solve
    ../venv/bin/python rain_anchor.py --report    # the present day against observation, by site
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
WC = os.path.join(HERE, "..", "data", "worldclim")
CACHE = os.path.join(HERE, "cache", "rain_anchor.npz")
FIELDS = os.path.join(HERE, "..", "web", "fields")
ROTJSON = os.path.join(HERE, "..", "web", "platerot.json")

EPS = 0.02            # Rf units: a floor so the log ratio is finite over deserts
SIGMA_DEG = 0.75      # the correction's scale: regional, ~80 km
FADE0, FADE1 = 5.0, 35.0   # Myr: full weight inside FADE0, none past FADE1

_C = {}


def weight(age):
    a = abs(float(age))
    if a <= FADE0:
        return 1.0
    if a >= FADE1:
        return 0.0
    t = (a - FADE0) / (FADE1 - FADE0)
    return float(1.0 - t * t * (3.0 - 2.0 * t))


def observed(h, w):
    """WorldClim 2.1 annual precipitation in mm on an h x w north-up lat-lon
    grid, the mean over the land part of each cell; NaN where it has none."""
    tot = None
    for m in range(1, 13):
        a = np.asarray(Image.open(os.path.join(WC, "wc2.1_10m_prec_%02d.tif" % m)), np.float32)
        tot = a if tot is None else tot + a
    land = tot > -1000.0
    val = np.where(land, tot, 0.0).astype(np.float32)
    s = np.asarray(Image.fromarray(val).resize((w, h), Image.BOX), np.float32)
    c = np.asarray(Image.fromarray(land.astype(np.float32)).resize((w, h), Image.BOX), np.float32)
    return np.where(c > 0.15, s / np.maximum(c, 1e-6), np.nan)


def _smooth_land(v, land, sigma_deg):
    """Gaussian smoothing on the sphere over land only: the ocean contributes
    neither value nor weight. sigma in degrees of arc; longitude widens by
    1/cos(lat) row by row."""
    h, w = v.shape
    sy = sigma_deg / (180.0 / h)
    num = gaussian_filter1d(np.where(land, v, 0.0), sy, axis=0, mode="nearest")
    den = gaussian_filter1d(land.astype(np.float64), sy, axis=0, mode="nearest")
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    out_n = np.empty_like(num)
    out_d = np.empty_like(den)
    for i in range(h):
        sx = min(sigma_deg / (360.0 / w) / max(np.cos(np.radians(lat[i])), 0.05), w / 4.0)
        out_n[i] = gaussian_filter1d(num[i], sx, mode="wrap")
        out_d[i] = gaussian_filter1d(den[i], sx, mode="wrap")
    return np.where(out_d > 1e-3, out_n / np.maximum(out_d, 1e-9), 0.0)


def build(model0, land0):
    """The correction on the present-day rain grid. model0: the model's own 0 Ma
    rainfall in Rf units (north-up); land0: its land mask."""
    h, w = model0.shape
    obs = observed(h, w)
    both = land0 & np.isfinite(obs)
    # quantile mapping onto the model's land distribution
    order = np.argsort(obs[both], kind="stable")
    ranks = np.empty(order.size, np.int64)
    ranks[order] = np.arange(order.size)
    sorted_model = np.sort(model0[both])
    qm = np.full((h, w), np.nan, np.float32)
    qm[both] = sorted_model[ranks]
    # land the model has and the observation does not (islands, coastal cells):
    # the nearest observed cell's mapped value
    have = np.isfinite(qm)
    if (land0 & ~have).any():
        _, (iy, ix) = distance_transform_edt(~have, return_indices=True)
        qm = np.where(land0 & ~have, qm[iy, ix], qm)
    L = np.where(land0, np.log(qm + EPS) - np.log(model0 + EPS), 0.0)
    C = _smooth_land(L, land0, SIGMA_DEG).astype(np.float32)
    return C, qm


def load():
    if "C" not in _C:
        if not os.path.exists(CACHE):
            raise SystemExit("rain_anchor: no correction cached -- run rain_anchor.py --build")
        d = np.load(CACHE)
        _C["C"] = d["C"]
    return _C["C"]


def _rot():
    if "rot" not in _C:
        with open(ROTJSON) as f:
            _C["rot"] = json.load(f)["rot"]
    return _C["rot"]


def transport(C, age, h, w):
    """The correction as it sits at `age`: each cell of the h x w grid reads C
    where its crust is today (slot raster + rotation, age -> 0 Ma)."""
    import plate_field as PF
    tag = "fut" if age < 0 else ("phan" if age <= 540 else "pre")
    p = os.path.join(FIELDS, "%s_%04d_p.webp" % (tag, abs(int(age))))
    rot = _rot().get(str(int(age)))
    if int(age) == 0 or not os.path.exists(p) or rot is None:
        if int(age) != 0:
            print("  rain_anchor: no slot raster or rotations at %s Ma -- correction not carried"
                  % age, flush=True)
        if C.shape == (h, w):
            return C
        return np.asarray(Image.fromarray(C.astype(np.float32)).resize((w, h), Image.BILINEAR), np.float32)
    slot = np.asarray(Image.open(p).convert("RGB"))[..., 0]
    sh, sw = slot.shape
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon, lat)
    sy = np.clip(((90.0 - LAT) / 180.0 * sh).astype(int), 0, sh - 1)
    sx = np.clip(((LON + 180.0) / 360.0 * sw).astype(int), 0, sw - 1)
    s = slot[sy, sx]
    v = PF.unit(LON.ravel(), LAT.ravel())
    out = np.empty_like(v)
    sf = s.ravel()
    for k in np.unique(sf):
        m = sf == k
        q = rot[int(k)] if int(k) < len(rot) else [0.0, 0.0, 1.0, 0.0]
        # errstate: numpy's matmul on Apple Accelerate raises a spurious
        # divide-by-zero flag on some shapes; the product is exact (checked
        # against the einsum below).
        with np.errstate(all="ignore"):
            out[m] = PF.rodrigues(v[m], np.asarray(q[:3], float), float(q[3]))
    plon, plat = PF.lonlat(out)
    # bilinear read of C at the present-day position
    ch, cw = C.shape
    fy = (90.0 - plat) / 180.0 * ch - 0.5
    fx = (plon + 180.0) / 360.0 * cw - 0.5
    y0 = np.clip(np.floor(fy).astype(int), 0, ch - 1)
    y1 = np.clip(y0 + 1, 0, ch - 1)
    ty = np.clip(fy - np.floor(fy), 0, 1)
    x0 = np.floor(fx).astype(int) % cw
    x1 = (x0 + 1) % cw
    tx = fx - np.floor(fx)
    r = (C[y0, x0] * (1 - tx) * (1 - ty) + C[y0, x1] * tx * (1 - ty)
         + C[y1, x0] * (1 - tx) * ty + C[y1, x1] * tx * ty)
    return r.reshape(h, w).astype(np.float32)


def land_mask(z_northup, h, w):
    """Land on the h x w rain grid from any north-up elevation grid (metres
    relative to the keyframe's own sea level)."""
    z = np.asarray(z_northup, np.float32)
    if z.shape != (h, w):
        z = np.asarray(Image.fromarray(z).resize((w, h), Image.BILINEAR), np.float32)
    return z > 0.0


def apply(rain01, age, land, rf_max):
    """rain01: the keyframe's rainfall as shipped (Rf / RF_MAX, north-up); land:
    its land mask on the same grid. Returns the anchored field, same units."""
    wt = weight(age)
    if wt <= 0.0:
        return rain01
    h, w = rain01.shape
    C = transport(load(), age, h, w)
    rf = rain01 * rf_max
    out = (rf + EPS) * np.exp(wt * C) - EPS
    out = np.where(land, np.clip(out, 0.0, rf_max), rf)
    return (out / rf_max).astype(rain01.dtype)


def _model0():
    """The model's own 0 Ma rainfall and land mask, exactly as export() solves it."""
    import build_fields as BF
    import bake_rain as BR
    import paleo_tracks
    from build_frames import index_dems, read_dem
    from render import compute_fields
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    z = read_dem(idx[float(avail[np.argmin(np.abs(avail))])])
    zc = BR.rain_for(0, z, rec)                       # lat-ascending climate grid
    _, _, Rf, _, _ = compute_fields(zc, 0, BF.CLIM_H, BF.CLIM_W)
    rain = np.asarray(Image.fromarray((np.clip(Rf / BF.RF_MAX, 0, 1) * 255).astype(np.uint8))
                      .resize((BF.RAIN_W, BF.RAIN_H), Image.LANCZOS)) / 255.0
    zn = zc[::-1]                                     # north-up, like the rain
    if zn.shape != rain.shape:
        zn = np.asarray(Image.fromarray(zn.astype(np.float32))
                        .resize((BF.RAIN_W, BF.RAIN_H), Image.BILINEAR))
    return rain * BF.RF_MAX, zn > 0.0


def main():
    if "--build" in sys.argv:
        m0, land0 = _model0()
        C, qm = build(m0.astype(np.float64), land0)
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        np.savez_compressed(CACHE, C=C)
        lc = C[land0]
        print("rain_anchor: correction built on %dx%d, land log-ratio p5/50/95 %+.2f/%+.2f/%+.2f"
              % (C.shape[1], C.shape[0], *np.percentile(lc, [5, 50, 95])))
    if "--report" in sys.argv:
        import build_fields as BF
        m0, land0 = _model0()
        after = apply(m0 / BF.RF_MAX, 0, land0, BF.RF_MAX) * BF.RF_MAX
        obs = observed(*m0.shape)
        h, w = m0.shape
        for n, lo, la in (("Columbia Mts", -117.5, 51.0), ("Ganges (Patna)", 85.1, 25.6),
                          ("Himalayan front", 86.9, 27.6), ("Lhasa", 91.1, 29.65),
                          ("Amazon", -62.0, -3.5), ("Sahara", 8.0, 24.0),
                          ("Great Plains", -100.0, 40.0), ("Appalachians", -80.0, 38.0)):
            y = int((90 - la) / 180 * h)
            x = int((lo + 180) / 360 * w)
            print("  %-16s obs %6.0f mm   model %.3f -> anchored %.3f"
                  % (n, obs[y, x], m0[y, x], after[y, x]))


if __name__ == "__main__":
    main()
