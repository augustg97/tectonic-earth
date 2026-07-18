"""Render a paleoDEM elevation grid into a paleogeographic map texture.

Climate is derived physically rather than from latitude stripes:

  * Prevailing winds by latitude — tropical easterlies (0-30), mid-latitude
    westerlies (30-60), polar easterlies (60-90).
  * Moisture is advected downwind: air recharges to saturation over ocean and
    dries as it crosses land, so continental interiors go arid on their own and
    a supercontinent (Pangaea, Gondwana) develops a genuine dry heart with wet,
    monsoonal windward margins.
  * Orographic rainfall — air forced up a slope rains out, leaving a rain
    shadow on the lee side (Andes/Atacama, Himalaya/Tibet, Sierra/Basin-Range).
  * Rain belts modulate the delivered moisture: wet ITCZ, dry subtropical
    highs, wet mid-latitude storm track, dry cold poles.

Biome colour then comes from temperature x rainfall, so the same map yields
rainforest, savanna, steppe, desert, taiga and tundra in the right places.

Terrane-scale texture comes from the DEM's own high-frequency relief, so the
detail is real topography and travels with the continents instead of being
random noise that re-rolls every frame (which read as flicker when scrubbing).

Output: RGB uint8 (H x W x 3), equirectangular, row 0 = +90 lat, col 0 = -180 lon.
"""
import numpy as np
from climate import climate_at

# ---- tunables -------------------------------------------------------------
FETCH_KM     = 3200.0  # e-folding distance for moisture drying inland
ORO_RAIN     = 1.9     # orographic rainfall gain per unit upslope
ORO_DRAIN    = 0.85    # moisture stripped by forced ascent
UPLIFT_SCALE = 300.0   # metres of rise (large-scale) that counts as full uplift
SEA_RECHARGE = 1.0
TEMP_REF     = -0.55   # climate.py's present-day `temp`; anomalies are relative
                       # to it so the modern frame reproduces the real profile


def _c(h):
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float) / 255.0


# ocean depth ramp
# Abyssal tone stays well clear of black: on the globe an unlit ocean
# hemisphere would otherwise vanish against the starfield.
OCEAN = [
    (-6500, _c("0a2340")), (-4000, _c("10365c")), (-2500, _c("16507a")),
    (-1000, _c("236f99")), (-350, _c("3893b6")), (-120, _c("74c3d6")),
    (-15, _c("aee3ea")), (0, _c("cdeef0")),
]

# biome anchors
ICE      = _c("eef4f8"); SNOW    = _c("f6f9fc")
TUNDRA   = _c("979c81"); BOREAL  = _c("415539")
TEMPF    = _c("4c7440"); RAINF   = _c("2b6531")
GRASS    = _c("909b52"); SAVANNA = _c("c0a865")
DESERT   = _c("cbb083"); DESERT_D= _c("b59a67")
ROCK     = _c("8b8073"); ROCK_D  = _c("6d6458")
BARREN   = _c("9c8f7b"); BARREN_D= _c("7e7263")


def _ramp(x, stops):
    xs = [s[0] for s in stops]
    out = np.empty(x.shape + (3,), float)
    x = np.clip(x, xs[0], xs[-1])
    for i in range(len(stops) - 1):
        a, ca = stops[i]; b, cb = stops[i + 1]
        m = (x >= a) & (x <= b)
        t = (x[m] - a) / (b - a + 1e-9)
        out[m] = ca[None, :] * (1 - t)[:, None] + cb[None, :] * t[:, None]
    out[x <= xs[0]] = stops[0][1]
    out[x >= xs[-1]] = stops[-1][1]
    return out


def _smooth(a, k=1):
    if k <= 0:
        return a
    pad = np.pad(a, ((k, k), (k, k)), mode="edge")
    from numpy.lib.stride_tricks import sliding_window_view
    return sliding_window_view(pad, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))


def _bilin_up(g, H, W):
    """Smooth bilinear upsample of grid g to (H,W), wrapping in x (lon)."""
    gh, gw = g.shape
    gy = np.linspace(0, gh, H, endpoint=False); gx = np.linspace(0, gw, W, endpoint=False)
    y0 = np.floor(gy).astype(int); fy = gy - y0
    x0 = np.floor(gx).astype(int); fx = gx - x0
    y1 = np.minimum(y0 + 1, gh - 1); x1 = (x0 + 1) % gw
    y0 = np.clip(y0, 0, gh - 1)
    top = g[y0][:, x0] * (1 - fx)[None, :] + g[y0][:, x1] * fx[None, :]
    bot = g[y1][:, x0] * (1 - fx)[None, :] + g[y1][:, x1] * fx[None, :]
    return top * (1 - fy)[:, None] + bot * fy[:, None]


def _fbm(shape, seed=7, octaves=4):
    """Constant-seed fractal noise. Seed must NOT vary with age: a noise field
    that re-rolls per frame reads as flicker when frames cross-fade."""
    rng = np.random.default_rng(seed)
    H, W = shape
    acc = np.zeros(shape); amp = 1.0; tot = 0.0
    for o in range(octaves):
        gh = max(3, int(5 * 1.9 ** o)); gw = max(6, int(10 * 1.9 ** o))
        acc += amp * _bilin_up(rng.standard_normal((gh, gw)), H, W)
        tot += amp; amp *= 0.55
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-9)


def _hillshade(z, out_h, out_w, az=315.0, alt=42.0):
    dy = np.gradient(z, axis=0) / (180.0 / out_h * 111000.0)
    dx = np.gradient(z, axis=1) / (360.0 / out_w * 111000.0)
    k = 4200.0                      # vertical exaggeration
    dx *= k; dy *= k
    slope = np.arctan(np.hypot(dx, dy))
    aspect = np.arctan2(-dx, dy)
    az_r = np.radians(360 - az + 90); alt_r = np.radians(alt)
    hs = (np.sin(alt_r) * np.cos(slope) +
          np.cos(alt_r) * np.sin(slope) * np.cos(az_r - aspect))
    return np.clip(hs, 0, 1)


def _band(x, lo, hi, feather=9.0):
    """~1 inside [lo,hi], feathered to 0 outside."""
    return np.clip((x - (lo - feather)) / feather, 0, 1) * \
           np.clip(((hi + feather) - x) / feather, 0, 1)


def _advect(elev, ocean, direction, decay, floor):
    """March moisture downwind across each row, returning delivered rainfall.

    direction +1: westerly wind, air travels west->east (increasing column)
    direction -1: easterly wind, air travels east->west (decreasing column)
    `decay` is per-column retention (varies with latitude, since columns are
    physically closer together near the poles) and `floor` is the moisture that
    evapotranspiration recycles back, which is why real continental interiors
    are semi-arid rather than absolutely dry.  Two wraps are run so the result
    does not depend on where the scan starts.
    """
    H, W = elev.shape
    m = np.full(H, 0.6)
    R = np.zeros((H, W))
    for step in range(2 * W):
        if direction > 0:
            c = step % W; pc = (c - 1) % W
        else:
            c = (W - 1 - (step % W)); pc = (c + 1) % W
        sea = ocean[:, c]
        uplift = np.clip(elev[:, c] - elev[:, pc], 0, None) / UPLIFT_SCALE
        # rainfall where moist air is forced to rise
        rain = m * (1.0 + ORO_RAIN * uplift)
        if step >= W:
            R[:, c] = np.where(sea, 0.0, rain)
        # moisture budget: saturate over sea; inland decay toward the recycling
        # floor, with extra loss where air is forced over high ground
        inland = floor + (m - floor) * decay
        inland = np.clip(inland - ORO_DRAIN * uplift * m, 0.0, 1.0)
        m = np.where(sea, SEA_RECHARGE, inland)
    return R


def _rainfall(Z, land, lat, cl):
    """Delivered rainfall field, 0..~1.3."""
    H, W = Z.shape
    elev = np.clip(Z, 0, None)
    ocean = ~land
    absl = np.abs(lat)

    # columns are physically narrower toward the poles, so a fixed e-folding
    # distance means a latitude-dependent per-column retention
    dx_km = (360.0 / W) * 111.0 * np.clip(np.cos(np.radians(lat[:, 0])), 0.02, 1)
    decay = np.exp(-dx_km / FETCH_KM)
    # Evapotranspiration recycles moisture back into passing air -- strongest in
    # the warm, densely vegetated tropics, which is how the Amazon stays wet
    # thousands of km from the Atlantic.
    floor = (0.08 + 0.16 * cl["veg"]) * (0.60 + 0.80 * np.cos(np.radians(lat[:, 0])))

    # Orographic lift must respond to real ranges, not pixel-scale DEM
    # roughness -- otherwise every column registers a small "climb" and the
    # multiplicative drain annihilates moisture before it reaches any interior.
    elev_s = _smooth(elev, 3)

    R_west = _advect(elev_s, ocean, +1, decay, floor)   # mid-latitude westerlies
    R_east = _advect(elev_s, ocean, -1, decay, floor)   # tropical & polar easterlies

    # Near the equator the ITCZ pulls air in from both hemispheres and the flow
    # reverses seasonally, so whichever ocean is closer supplies the basin.
    # Away from it, the prevailing trades/westerlies rule and a lee coast such
    # as the Atacama stays in the rain shadow.
    itcz = np.exp(-(lat ** 2) / (2 * 9.0 ** 2))
    R_trop = np.maximum(R_east, R_west) * itcz + R_east * (1 - itcz)
    # Westerlies dominate ~40-65 deg. Keeping them out of the subtropics matters:
    # it lets easterly maritime air reach subtropical EAST coasts (SE US, SE
    # China, SE Brazil) while west coasts at those latitudes stay in the lee.
    westerly = _band(absl, 40, 65, feather=8.0)
    R = np.clip(R_trop * (1 - westerly) + R_west * westerly, 0, 1.6)

    # Atmospheric rain belts. These MODULATE the delivered moisture rather than
    # gating it: the belt never clamps to zero, so whether a subtropical region
    # is desert or monsoon is decided by its geography (fetch, coasts, relief).
    arid = cl["arid"]
    B = (0.42
         + 0.52 * np.exp(-(lat ** 2) / (2 * 13.0 ** 2))
         - (0.26 + 0.20 * arid) * np.exp(-((absl - 24) ** 2) / (2 * 10.0 ** 2))
         + 0.24 * np.exp(-((absl - 50) ** 2) / (2 * 13.0 ** 2))
         - 0.34 * np.exp(-((absl - 88) ** 2) / (2 * 18.0 ** 2)))
    B = np.clip(B, 0.10, 1.15)

    # Monsoon: summer heating over a landmass draws in oceanic air. Added over
    # land in the tropics/subtropics, but still gated by R, so a coast with a
    # short sea fetch (India) floods while a deep interior (Sahara) does not.
    land_s = _smooth(land.astype(float), 2)
    monsoon = 0.62 * np.exp(-((absl - 18) ** 2) / (2 * 12.0 ** 2)) * land_s

    # a warmer world evaporates more; `arid` already shapes the belts above so
    # it is deliberately not applied twice here
    glob = np.clip(1.02 + 0.22 * cl["temp"], 0.78, 1.30)
    Rf = (B + monsoon) * R * glob
    # The advection runs along rows, so without meridional mixing the field
    # keeps row-to-row streaks that surface later as straight horizontal bands
    # of vegetation. Real atmosphere mixes across latitude; so does this.
    Rf = _smooth(Rf, 2)
    Rf = 0.5 * Rf + 0.25 * np.roll(Rf, 1, axis=0) + 0.25 * np.roll(Rf, -1, axis=0)
    Rf = _smooth(Rf, 1)
    return np.clip(Rf, 0, 1.3)


def _b3(col, H, W):
    return np.ones((H, W, 3)) * col


def _L3(a, b, t):
    return a * (1 - t)[..., None] + b * t[..., None]


def resample_dem(z, out_h, out_w):
    """Bilinear-resample a lat-ascending DEM to (out_h,out_w) with row 0 = north."""
    H0, W0 = z.shape
    yi = np.linspace(0, H0 - 1, out_h); xi = np.linspace(0, W0 - 1, out_w)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H0 - 1); fy = (yi - y0)[:, None]
    x0 = np.floor(xi).astype(int); x1 = np.minimum(x0 + 1, W0 - 1); fx = (xi - x0)[None, :]
    a = z.astype(float)
    top = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx
    bot = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
    return (top * (1 - fy) + bot * fy)[::-1]


def smooth_bathymetry(Z):
    """Flatten the abyssal plains. They hold no useful detail, their lossy
    compression artifacts show up as blocking in the ocean depth ramp, and
    smoothing them shrinks the shipped texture appreciably. Shelves and
    coastlines are untouched."""
    deep = np.clip((-Z - 600.0) / 1200.0, 0, 1)
    return Z * (1 - deep) + _smooth(Z, 3) * deep


def compute_fields(z, age, out_h=512, out_w=1024):
    """Resample a DEM and derive the climate fields for an era.

    Returns (Z, T, Rf, lat, cl): elevation (m), surface temperature (deg C),
    rainfall (0..1.3), the latitude grid, and the era's climate record.

    The web build ships these fields instead of finished colour images: the
    shader interpolates ELEVATION between keyframes, which makes a coastline
    migrate across the pixel grid rather than cross-fade against another
    coastline, and recomputes shading per pixel so relief stays crisp.
    """
    cl = climate_at(age)
    H0, W0 = z.shape
    yi = np.linspace(0, H0 - 1, out_h); xi = np.linspace(0, W0 - 1, out_w)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H0 - 1); fy = (yi - y0)[:, None]
    x0 = np.floor(xi).astype(int); x1 = np.minimum(x0 + 1, W0 - 1); fx = (xi - x0)[None, :]

    def samp(a):
        top = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx
        bot = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
        return top * (1 - fy) + bot * fy

    Z = samp(z.astype(float))[::-1]        # flip so row 0 = north
    lat = np.linspace(90, -90, out_h)[:, None] * np.ones((1, out_w))
    land = Z >= 0
    zpos = np.clip(Z, 0, None)
    s2 = np.sin(np.radians(lat)) ** 2
    T = (26.0 - 24.0 * s2 - 26.0 * s2 ** 3) \
        + (cl["temp"] - TEMP_REF) * (4.0 + 15.0 * s2) \
        - zpos * 0.0058
    Rf = _rainfall(Z, land, lat, cl)
    return Z, T, Rf, lat, cl


def glaciation(cl):
    """Per-era ice thresholds (deg C) for land ice and pack ice."""
    iceN, iceS = cl["iceN"], cl["iceS"]
    if iceN is None and iceS is None:
        glac = 0.0
    else:
        line = min(x for x in (iceN, iceS) if x is not None)
        glac = float(np.clip((90.0 - line) / 40.0, 0, 1))
    return -30.0 + 12.0 * glac, -14.0 + 5.0 * glac


def render(z, age, out_h=512, out_w=1024, hillshade=True):
    """z: (lat, lon) grid with latitude ASCENDING (row 0 = south pole)."""
    Z, T, Rf, lat, cl = compute_fields(z, age, out_h, out_w)
    absl = np.abs(lat)

    sea = Z < 0
    land = ~sea
    zpos = np.clip(Z, 0, None)

    img = np.empty((out_h, out_w, 3), float)
    img[sea] = _ramp(Z[sea], OCEAN)

    temp = cl["temp"]; veg = cl["veg"]

    # ---------------- biome colour ----------------
    w = np.clip((T + 6.0) / 30.0, 0, 1)          # warmth 0..1
    # Effective moisture is rainfall against evaporative demand (a Budyko-style
    # dryness index): cold Siberia supports taiga on rain that would leave a hot
    # subtropical plain a desert.
    pet = np.clip((T + 12.0) / 34.0, 0.16, 1.35)
    h = np.clip(Rf / (0.46 * pet), 0, 1)         # humidity 0..1

    dry = _L3(_b3(TUNDRA, out_h, out_w), _b3(DESERT, out_h, out_w), w)
    mid = _L3(_b3(GRASS, out_h, out_w), _b3(SAVANNA, out_h, out_w), w)
    cold_wet = _L3(_b3(BOREAL, out_h, out_w), _b3(TEMPF, out_h, out_w),
                   np.clip(w * 2, 0, 1))
    warm_wet = _L3(_b3(TEMPF, out_h, out_w), _b3(RAINF, out_h, out_w),
                   np.clip((w - 0.5) * 2, 0, 1))
    wet = np.where((w < 0.5)[..., None], cold_wet, warm_wet)

    t_lo = np.clip(h / 0.45, 0, 1)
    t_hi = np.clip((h - 0.45) / 0.55, 0, 1)
    base = np.where((h < 0.45)[..., None], _L3(dry, mid, t_lo), _L3(mid, wet, t_hi))

    # deepen the driest cores so great deserts read as sand seas
    core = np.clip((0.30 - h) / 0.30, 0, 1) * np.clip((w - 0.45) * 2.2, 0, 1)
    base = _L3(base, _b3(DESERT_D, out_h, out_w), core * 0.5)

    # ---------------- pre-vegetation land ----------------
    if veg < 0.999:
        barren = _L3(_b3(BARREN, out_h, out_w), _b3(BARREN_D, out_h, out_w),
                     np.clip(zpos / 2400.0, 0, 1))
        # Before vascular plants the land is essentially bare rock; as greening
        # spreads through the Devonian the last holdouts of bare ground are the
        # dry uplands, so strip those last.
        bf = (1 - veg) ** 0.5 * np.clip(0.92 + 0.08 * (1 - h) + zpos / 9000.0, 0, 1)
        base = _L3(base, barren, np.clip(bf, 0, 1))

    # ---------------- relief ----------------
    rock = np.clip((zpos - 1700) / 1500.0, 0, 1)
    base = _L3(base, _L3(_b3(ROCK, out_h, out_w), _b3(ROCK_D, out_h, out_w),
                         np.clip((zpos - 2600) / 1800.0, 0, 1)), rock * 0.85)

    snowline = 2600.0 + 190.0 * np.clip(T, -20, 30)
    snowf = np.clip((zpos - snowline) / 420.0, 0, 1)
    base = _L3(base, _b3(SNOW, out_h, out_w), snowf)

    img[land] = base[land]

    # ---------------- ice sheets ----------------
    # Ice is placed by temperature, not a latitude line, so it hugs real
    # geography: it climbs onto highlands (Greenland, Antarctica, Andes) and
    # spares cold-but-dry lowlands (Siberia, interior Alaska) the way Earth does.
    # Thresholds are calibrated so the present day glaciates Greenland and
    # Antarctica but leaves Siberia and interior Canada ice-free -- they are
    # cold, yet nowhere near cold enough to hold a permanent sheet.
    ice_T, sea_ice_T = glaciation(cl)
    # a little constant-seed noise keeps the margin lobed rather than a contour
    lobe = (_fbm((out_h, out_w), seed=17, octaves=5) - 0.5) * 3.4
    # Ice coverage is a continuous ramp, not a threshold test. A boolean mask
    # made whole ice sheets appear between one frame and the next -- the
    # Cryogenian onset lurched badly -- whereas a ramp lets glaciations
    # advance and retreat smoothly as the climate curve moves.
    ice_amt = np.clip((ice_T - (T + lobe)) / 4.5, 0, 1)
    # Pack ice has no coastline to hold its shape, so without a good deal of
    # noise its margin renders as a bare latitude contour.
    packn = _fbm((out_h, out_w), seed=53, octaves=5)
    sea_amt = np.clip((sea_ice_T - (T + lobe * 2.6 + (packn - 0.5) * 5.0)) / 3.5, 0, 1) \
        * np.clip((packn - 0.30) / 0.14, 0, 1)
    ice_col = _b3(ICE * 0.55 + SNOW * 0.45, out_h, out_w)
    pack_col = _b3(_c("cfe0e8"), out_h, out_w) * (0.94 + 0.10 * packn)[..., None]
    img = np.where(land[..., None], _L3(img, ice_col, ice_amt),
                                    _L3(img, pack_col, sea_amt))

    # ---------------- shading & terrane detail ----------------
    if hillshade:
        hs = _hillshade(Z, out_h, out_w)
        shade = 0.70 + 0.62 * hs
        # high-pass relief: real ridges/valleys, and it drifts with the plates
        detail = np.clip((Z - _smooth(Z, 2)) / 340.0, -1, 1)
        shade *= (1.0 + 0.20 * detail)
        hw = np.where(land, 1.0, 0.30)     # keep the seafloor calm
        img *= ((1 - hw) + hw * shade)[..., None]

    return np.clip(img, 0, 1) * 255.0, Z


def render_u8(z, age, **kw):
    img, Z = render(z, age, **kw)
    return img.astype(np.uint8), Z


if __name__ == "__main__":
    import netCDF4, glob
    from PIL import Image
    tests = {"0Ma": "Map01_*0Ma", "90Ma": "Map21_*90Ma", "195Ma": "Map42_*195Ma",
             "250Ma": "Map49_*250Ma", "300Ma": "Map57_*300Ma",
             "445Ma": "Map77_*445Ma", "540Ma": "Map88_*540Ma"}
    for tag, pat in tests.items():
        f = sorted(glob.glob(f"../data/paleodems_1deg/**/{pat}.nc", recursive=True))[0]
        age = float("".join(ch for ch in tag if ch.isdigit()))
        ds = netCDF4.Dataset(f)
        z = np.asarray(ds.variables["z"][:], float)
        la = np.asarray(ds.variables["lat"][:])
        if la[0] > la[-1]:
            z = z[::-1]
        img, _ = render_u8(z, age)
        Image.fromarray(img).save(f"test_{tag}.png")
        print("wrote test_%s.png" % tag)
