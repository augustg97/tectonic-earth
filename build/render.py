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
ORO_STRIP_MAX= 0.75    # ...but never more than this fraction of what the air holds
UPLIFT_SCALE = 300.0   # metres of rise (large-scale) that counts as full uplift
SEA_RECHARGE = 1.0
SEA_MIN      = 0.25    # what an ENCLOSED sea supplies, against open ocean's 1.0
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
    """Box smooth. Longitude WRAPS, latitude does not.

    This padded both axes with mode="edge", which quietly put a discontinuity
    down the antimeridian in every field derived through it. Columns either side
    of 180 were averaged against a replicated edge instead of against the data
    on the other side of the globe, so the map carried a stationary north-south
    line from the Bering Strait past New Zealand to Antarctica -- most visible in
    the deep Pacific, where smooth_bathymetry leans on this hardest and there is
    no real relief to hide it. Longitude is periodic; latitude is not (the poles
    are genuine edges), so the two axes are padded differently."""
    if k <= 0:
        return a
    pad = np.pad(a, ((k, k), (0, 0)), mode="edge")
    pad = np.pad(pad, ((0, 0), (k, k)), mode="wrap")
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


def _sea_recharge(ocean, W):
    """How much moisture a water body can actually hand to the air over it.

    Both marches saturated to SEA_RECHARGE over ANY water, so the Black Sea, the
    Caspian and the Mediterranean resupplied an air mass exactly as the open
    Atlantic does. Measured at present day, the meridional march arrived at the
    Pontic steppe carrying 0.547 against the Kazakh steppe's 0.013 at the same
    latitude -- and the difference is not continentality, it is that one column
    happened to cross an inland sea on the way and had its clock reset to full.
    The steppe came out at 0.411, wetter than the Congo, which is the largest
    class inversion audit_biomes.py reports.

    Evaporative supply scales with the fetch of open water upwind, so weight the
    recharge by how much water lies within a few hundred kilometres. An enclosed
    sea supplies a real but limited amount; an ocean supplies all of it.
    """
    k = max(int(round(W / 72.0)), 3)          # ~500 km at CLIM resolution
    openness = _smooth(ocean.astype(float), k)
    return SEA_RECHARGE * (SEA_MIN + (1.0 - SEA_MIN) * np.clip(openness / 0.55, 0.0, 1.0))


def _advect(elev, ocean, direction, decay, floor, regen=None, recharge=None, rec_km=None):
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
    # Distance since the air last crossed open water. The recycling floor is not
    # a constant: it is water that fell upstream and evaporated again, so three
    # thousand kilometres into a continent there is less of it to recycle. With
    # a flat floor, Kazakhstan and the Taklamakan came out as wet as temperate
    # forest (measured index 0.42 and 0.28 against a 0.20 canopy threshold) --
    # deep interiors were being fed moisture that had no upstream source.
    dist = np.zeros(H)
    dx_km = (360.0 / W) * 111.0 * np.cos(np.radians(np.linspace(90.0, -90.0, H)))
    for step in range(2 * W):
        if direction > 0:
            c = step % W; pc = (c - 1) % W
        else:
            c = (W - 1 - (step % W)); pc = (c + 1) % W
        sea = ocean[:, c]
        # WET LAND RESETS THE RECYCLING CLOCK. Crossing three thousand
        # kilometres of rainforest is not the same as crossing three thousand
        # kilometres of sand: what fell upstream evaporates again, and roughly a
        # third of the Amazon's rain is water that already fell in the basin. A
        # distance-only decay gave the Amazon a backwards west-drying profile --
        # measured 0.706 at the mouth against 0.141 under the Andes, when the
        # Andean foreland is in reality the wettest part of it. `regen` is the
        # previous pass's rainfall, so this is a fixed-point iteration and not a
        # circular definition; where it is dry the clock runs at full speed and
        # central Asia stays steppe.
        if regen is None:
            dist = np.where(sea, 0.0, dist + dx_km)
        else:
            g = RECYCLE_REGEN * np.clip(regen[:, c] / RECYCLE_REF, 0.0, 1.0)
            dist = np.where(sea, 0.0, np.maximum(dist + dx_km * (1.0 - g), 0.0))
        # ...AND GATED ON LOCAL VEGETATION, because cold alone cannot tell a
        # boreal forest from a mid-latitude desert. Cold-scaling by itself lifts
        # Siberia to 0.048 but raises the Gobi's floor 54% with it, and Spearman
        # falls to +0.853. Recycling needs something growing to do the
        # returning; `regen` is the previous pass's rainfall and the only local
        # proxy available inside the march. Cold AND wet gets the full floor;
        # cold and bare gets a quarter of it.
        locv = (1.0 if regen is None
                else FLOOR_BARE + (1.0 - FLOOR_BARE)
                * np.clip(regen[:, c] / RECYCLE_REF, 0.0, 1.0))
        fl = floor * locv * np.exp(-dist / (RECYCLE_KM if rec_km is None else rec_km))
        if regen is not None:
            # ...and wet ground does not merely slow the decay, it raises what
            # the air decays TOWARD. Evapotranspiration over closed canopy
            # returns a large fraction of what fell, which is why the Amazon's
            # profile is nearly flat from the mouth to the Andes instead of
            # halving across the basin.
            fl = np.maximum(fl, RECYCLE_FLOOR * SEA_RECHARGE
                            * np.clip(regen[:, c] / RECYCLE_REF, 0.0, 1.0))
        uplift = np.clip(elev[:, c] - elev[:, pc], 0, None) / UPLIFT_SCALE
        # rainfall where moist air is forced to rise
        rain = m * (1.0 + ORO_RAIN * uplift)
        if step >= W:
            R[:, c] = np.where(sea, 0.0, rain)
        # moisture budget: saturate over sea; inland decay toward the recycling
        # floor, with extra loss where air is forced over high ground
        inland = fl + (m - fl) * decay
        # AIR CANNOT LOSE MORE WATER THAN IT IS CARRYING. Unbounded, this term
        # is ORO_DRAIN * uplift * m with uplift measured in units of 300 m, so a
        # single column climbing the Himalayan front asks for roughly seventeen
        # times the moisture present, the result clips to zero, and every column
        # beyond it is dry for ever. Measured on the shipped field: land above
        # 2500 m came out at mean rainfall 0.0027 with 97.7% of it under 0.02,
        # against 0.1494 for land below 500 m -- every high range on Earth a
        # desert, including the monsoon-facing Himalayan front. That fed the
        # snow (capped at 30% wherever Rf is 0), the flow accumulation that
        # weights by rainfall, and every alpine biome.
        #
        # Capping the strip at a FRACTION of what the parcel holds keeps the
        # rain shadow -- three columns of climbing still leave under 2% -- while
        # letting the windward slope and the crest take the water on the way up,
        # which is where it actually falls.
        inland = np.clip(inland - np.minimum(ORO_DRAIN * uplift * m,
                                             ORO_STRIP_MAX * m), 0.0, 1.0)
        m = np.where(sea, SEA_RECHARGE if recharge is None else recharge[:, c], inland)
    return R


def _advect_ns(elev, ocean, toward_north, decay, floor, recharge=None, rec_km=None):
    """March moisture along COLUMNS, from the equator toward one pole.

    WHY THIS EXISTS. The zonal solve above carries moisture east-west only, so a
    continent's east coast can only be watered by air that has already crossed
    the whole landmass. Under westerlies that is fatal: eastern North America
    came out at 0.048 against the Sahara's 0.043 -- the Atlantic and the Gulf
    sit DOWNWIND of it and were never allowed to supply it at all.

    Real mid-latitude weather is not zonal. Extratropical cyclones pull
    subtropical-ocean air poleward along continental east coasts, and that
    meridional transport is what waters the eastern United States, eastern
    China and eastern Australia. One extra pass per hemisphere buys it.

    Row 0 is north, so travelling north means walking the row index DOWN.
    Latitude does not wrap -- a pole is a real boundary, not a seam -- so each
    column starts saturated at the equator and marches once.
    """
    H, W = elev.shape
    R = np.zeros((H, W))
    eq = H // 2
    rows = range(eq, -1, -1) if toward_north else range(eq, H)
    m = np.full(W, SEA_RECHARGE)
    prev = None
    dist = np.zeros(W)
    dy_km = (180.0 / H) * 111.0
    for r in rows:
        sea = ocean[r]
        dist = np.where(sea, 0.0, dist + dy_km)
        fl = floor[r] * np.exp(-dist / (RECYCLE_KM if rec_km is None else rec_km[r]))
        uplift = np.zeros(W) if prev is None else \
            np.clip(elev[r] - elev[prev], 0, None) / UPLIFT_SCALE
        rain = m * (1.0 + ORO_RAIN * uplift)
        R[r] = np.where(sea, 0.0, rain)
        inland = fl + (m - fl) * decay
        # AIR CANNOT LOSE MORE WATER THAN IT IS CARRYING. Unbounded, this term
        # is ORO_DRAIN * uplift * m with uplift measured in units of 300 m, so a
        # single column climbing the Himalayan front asks for roughly seventeen
        # times the moisture present, the result clips to zero, and every column
        # beyond it is dry for ever. Measured on the shipped field: land above
        # 2500 m came out at mean rainfall 0.0027 with 97.7% of it under 0.02,
        # against 0.1494 for land below 500 m -- every high range on Earth a
        # desert, including the monsoon-facing Himalayan front. That fed the
        # snow (capped at 30% wherever Rf is 0), the flow accumulation that
        # weights by rainfall, and every alpine biome.
        #
        # Capping the strip at a FRACTION of what the parcel holds keeps the
        # rain shadow -- three columns of climbing still leave under 2% -- while
        # letting the windward slope and the crest take the water on the way up,
        # which is where it actually falls.
        inland = np.clip(inland - np.minimum(ORO_DRAIN * uplift * m,
                                             ORO_STRIP_MAX * m), 0.0, 1.0)
        m = np.where(sea, SEA_RECHARGE if recharge is None else recharge[r], inland)
        # LATERAL MIXING INSIDE THE MARCH, not smoothing afterwards. Each column
        # is otherwise an isolated one-dimensional atmosphere, and isolated
        # neighbours drift apart row by row until the field carries vertical
        # stripes -- visible in the first build as light bands down the West
        # Siberian Basin. Blurring the finished field only hides that; mixing the
        # moisture as it travels stops the divergence accumulating, which is also
        # what eddies actually do. Longitude wraps, so np.roll is the right
        # neighbour operator here.
        m = 0.25 * np.roll(m, 1) + 0.5 * m + 0.25 * np.roll(m, -1)
        prev = r
    return R


def _rainfall(Z, land, lat, cl):
    """Delivered rainfall field, 0..~1.3."""
    H, W = Z.shape
    elev = np.clip(Z, 0, None)
    ocean = ~land
    absl = np.abs(lat)

    # HOW FAR RECYCLED MOISTURE PERSISTS IS A FUNCTION OF TEMPERATURE, and it
    # was a single global constant. RECYCLE_KM = 1800 means the evapotranspiration
    # floor is down to 2% after the 7000 km of land between the Atlantic and
    # central Siberia -- so the model gives Siberia 0.010, exactly what it gives
    # the Sahara, for 400 mm of real rainfall against 15. The same error runs
    # through central Europe (650 mm -> 0.076) and the west Siberian lowland
    # (500 mm -> 0.046).
    #
    # Recycling persists as long as what falls can evaporate again and stay in
    # the air, and cold air over boreal forest holds its water far better than
    # hot air over savanna: the e-folding distance scales with the inverse of
    # evaporative demand. Keyed to latitude here, which is the same proxy for
    # local temperature the floor and the decay already use two lines below.
    # This is why five separate threads this session -- the snow line, the
    # drainage network, the alpine biomes, the palette and now Siberia -- all
    # ended at "our high and cold ground is too dry".
    rec_km = RECYCLE_KM * (1.0 + RECYCLE_COLD
                           * np.clip(1.0 - np.cos(np.radians(lat[:, 0])), 0.0, 1.0))
    # columns are physically narrower toward the poles, so a fixed e-folding
    # distance means a latitude-dependent per-column retention
    dx_km = (360.0 / W) * 111.0 * np.clip(np.cos(np.radians(lat[:, 0])), 0.02, 1)
    decay = np.exp(-dx_km / FETCH_KM)
    # Evapotranspiration recycles moisture back into passing air -- strongest in
    # the warm, densely vegetated tropics, which is how the Amazon stays wet
    # thousands of km from the Atlantic.
    # THE FLOOR ITSELF SCALES WITH COLD, and this is the discriminator the last
    # attempt lacked. Iteration 87 raised the floor globally to water the world's
    # forested interiors; it worked for Siberia and turned Pangaea from 18% green
    # to 64%, because a global constant cannot tell a boreal forest from a hot
    # supercontinent interior. They differ in TEMPERATURE: what governs how much
    # moisture recycling sustains is the evaporative demand it works against, and
    # a cold interior loses far less of what it returns. Pangaea straddled the
    # equator, so a cold-keyed floor barely touches it -- at 20 N the factor is
    # 1.12 against 2.06 at Siberia's 62 N. Same latitude proxy as RECYCLE_COLD,
    # which is the reach; this is the amount.
    floor = ((0.08 + 0.16 * cl["veg"])
             * (0.60 + 0.80 * np.cos(np.radians(lat[:, 0])))
             * (1.0 + FLOOR_COLD * np.clip(1.0 - np.cos(np.radians(lat[:, 0])), 0.0, 1.0)))

    # Orographic lift must respond to real ranges, not pixel-scale DEM
    # roughness -- otherwise every column registers a small "climb" and the
    # multiplicative drain annihilates moisture before it reaches any interior.
    elev_s = _smooth(elev, 3)

    # Two passes: the first says where it rains, the second lets that rain feed
    # its own recycling. One iteration is enough -- the second pass moves the
    # Amazon and leaves the deserts alone, and a third would only sharpen an
    # already-converged field at twice the cost.
    rech = _sea_recharge(ocean, W)
    R_west = _advect(elev_s, ocean, +1, decay, floor, recharge=rech, rec_km=rec_km)   # mid-latitude westerlies
    R_east = _advect(elev_s, ocean, -1, decay, floor, recharge=rech, rec_km=rec_km)   # tropical & polar easterlies
    # SMOOTH THE SEED ACROSS LATITUDE BEFORE FEEDING IT BACK. The advection
    # marches along rows, so a recycling term read row-by-row makes wet rows
    # self-sustaining and dry rows self-limiting -- the feedback sharpens
    # row-to-row contrast faster than the latitude mixing at the end of this
    # function can smooth it out, and the western Amazon came back with a
    # dead-straight horizontal edge top and bottom. Real evapotranspiration
    # mixes across latitude before it rains again; so does this.
    # Smoothing this seed across latitude was tried, on the theory that a
    # row-by-row recycling term would make wet rows self-sustaining and dry rows
    # self-limiting. Measured over the western Amazon it moves row-banding from
    # 0.0464 to 0.0423 -- real but negligible, and not worth a re-bake of 251
    # frames. The straight forest edges visible there have a different cause: a
    # threshold applied to a field whose gradient is mostly latitudinal draws a
    # latitude line, which is the shader's jitter to fix, not this.
    R_seed = np.maximum(R_west, R_east)
    R_west = _advect(elev_s, ocean, +1, decay, floor, regen=R_seed, recharge=rech, rec_km=rec_km)
    R_east = _advect(elev_s, ocean, -1, decay, floor, regen=R_seed, recharge=rech, rec_km=rec_km)
    # ...and poleward transport by extratropical cyclones, which is the only way
    # a continental east coast can be watered under westerlies (see _advect_ns).
    dy_km = (180.0 / H) * 111.0
    decay_ns = np.exp(-dy_km / FETCH_KM)
    floor_col = floor[:, None] * np.ones((1, W))
    R_ns = _advect_ns(elev_s, ocean, True, decay_ns, floor_col, recharge=rech, rec_km=rec_km) \
         + _advect_ns(elev_s, ocean, False, decay_ns, floor_col, recharge=rech, rec_km=rec_km)
    # MIX ACROSS LONGITUDE. Every column in the meridional pass is an
    # independent one-dimensional march, so neighbouring columns diverge and the
    # result carries vertical streaks -- the exact mirror of the horizontal
    # streaks the zonal pass leaves, which the rows below already fix. Verified
    # in the render: the first build with meridional transport put light vertical
    # stripes down the West Siberian Basin and through the eastern US forest.
    # The real subsiding and ascending limbs are broad, so smoothing here costs
    # nothing physical. It is applied to R_ns ALONE: the zonal field must keep
    # its sharp east-west gradients (the hundredth-meridian dry line is one).
    R_ns = _smooth(R_ns, 2)

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
    # Moisture CONVERGES: a place is as wet as the wettest flow reaching it, not
    # as dry as the driest. The cyclone band runs 25-60 degrees, which is where
    # poleward transport actually dominates the moisture budget.
    cyc = _band(absl, 32, 62, feather=10.0)
    descend = np.exp(-((absl - 24.0) ** 2) / (2 * 11.0 ** 2))
    # ...AND THROUGH THE MONSOON, which is the other meridional flow and the one
    # that waters the subtropics. R_ns is the only south-north transport in the
    # solve and it was admitted through `cyc` alone -- the extratropical cyclone
    # band, 32 to 62 degrees -- so between the equator and the horse latitudes
    # nothing could move poleward at all. The Indian monsoon is exactly that
    # flow, and the Himalayan front is what it runs into.
    #
    # The existing `monsoon` term below cannot fix this: it enters as
    # `Rf = (B + monsoon) * R`, a MULTIPLIER on moisture already delivered, so
    # where R is zero for want of transport the bonus multiplies zero and stays
    # zero. A monsoon is a delivery mechanism, not a gain.
    #
    # Deliberately NOT gated by `descend`. The subtropical-high suppression is
    # what makes the deserts, and applying it here would cancel the monsoon at
    # precisely the latitudes it exists; the desert asymmetry is already carried
    # properly by the Rodwell-Hoskins `induced` term, which dries the ground
    # WEST of the monsoon source rather than the source itself.
    # The admission itself is applied further down, once the Rodwell-Hoskins
    # descent is known -- see MONSOON ADMISSION below. Delivering moisture here
    # and drying it there is the wrong order: it wet the Rub al Khali to 0.142,
    # which is the failure this solve has already been through once.
    R = np.clip(np.maximum(R, R_ns * cyc * 1.45 * (1.0 - 0.85 * descend)), 0, 1.6)

    # Atmospheric rain belts. These MODULATE the delivered moisture rather than
    # gating it: the belt never clamps to zero, so whether a subtropical region
    # is desert or monsoon is decided by its geography (fetch, coasts, relief).
    arid = cl["arid"]
    # The subtropical high is the strongest single control on where deserts are,
    # and it was too weak. Arabia came out as wet as the Amazon -- 0.294 against
    # 0.295 -- because it sits at 20 N with the Indian Ocean immediately upwind,
    # so it kept a short-fetch moisture supply AND took the full monsoon bonus.
    # The Sahara at the same latitude was correctly bone dry only because its
    # easterlies had already crossed a continent. Fetch alone cannot separate
    # them: the Rub al Khali is dry because air is DESCENDING over it, not
    # because moisture failed to arrive.
    B = (0.42
         + 0.52 * np.exp(-(lat ** 2) / (2 * 13.0 ** 2))
         - (0.30 + 0.22 * arid) * np.exp(-((absl - 24) ** 2) / (2 * 11.0 ** 2))
         + 0.24 * np.exp(-((absl - 50) ** 2) / (2 * 13.0 ** 2))
         - 0.34 * np.exp(-((absl - 88) ** 2) / (2 * 18.0 ** 2)))
    B = np.clip(B, 0.10, 1.15)

    # Monsoon: summer heating over a landmass draws in oceanic air. Added over
    # land in the tropics/subtropics, but still gated by R, so a coast with a
    # short sea fetch (India) floods while a deep interior (Sahara) does not.
    land_s = _smooth(land.astype(float), 2)
    monsoon = 0.60 * np.exp(-((absl - 17) ** 2) / (2 * 11.5 ** 2)) * land_s

    # MONSOON-INDUCED SUBSIDENCE (the Rodwell-Hoskins mechanism).
    #
    # Arabia came out as wet as the Amazon, and weakening the monsoon globally
    # to dry it also dried India and southeast Asia, which was the wrong trade.
    # The real asymmetry is not that Arabia gets less moisture -- the Indian
    # Ocean is right there -- it is that Arabia sits in air that is actively
    # DESCENDING, and what makes it descend is the Indian monsoon itself.
    #
    # Deep convection over a monsoon heat source drives a compensating
    # circulation that sinks to its WEST, and that descent is what maintains
    # the Arabian, Saharan and Middle Eastern deserts. Modelling it is simple:
    # take the monsoon field, smear it, shift it west, and subtract. The wet
    # source keeps its rain and dries the land behind it, which is exactly the
    # observed pattern -- Kerala green, the Rub al Khali the driest sand on
    # Earth, at the same latitude a couple of thousand kilometres apart.
    # NEGATIVE rolls. Column index increases eastward, so np.roll(+n) moves the
    # field EAST -- the opposite of what the paragraph above describes, and the
    # reason the shadow was landing on southeast Asia instead of Arabia.
    # Measured with the sign wrong: the Rub al Khali indexed 0.33 while monsoon
    # China indexed 0.20, i.e. the model had the two deserts and forests swapped.
    #
    # And a CONTINUOUS westward decay, not three discrete 40-degree lags. With
    # lags, the air over any given desert is sourced from exactly 40, 80 and 120
    # degrees east of it -- for Arabia that is the Bay of Bengal, which is ocean,
    # so `monsoon * land` there is zero and Arabia got no shadow at all. Descent
    # is not delivered in discrete jumps; it is a broad subsiding limb whose
    # strength falls off with distance from the heat source.
    # THE HEAT SOURCE IS WHERE IT ACTUALLY RAINS, not where the latitude band
    # says it might. `monsoon` is 0.60 * f(latitude) * land, so it hands the same
    # 0.565 to the Deccan and to the Rub al Khali -- a monsoon core and the
    # driest sand on Earth, at the same latitude with the same land fraction --
    # and the descent built from it then came out slightly STRONGER over the
    # Deccan (0.2096) than over Arabia (0.1983), which is backwards from the
    # mechanism it is modelling. Rodwell-Hoskins descent is forced by deep
    # CONVECTION, and convection needs moisture: weight the source by the rain
    # actually delivered there, which the solve has already worked out by this
    # point. India then drives Arabia's descent strongly, and Arabia -- having
    # no convection of its own -- drives almost nothing back.
    # NORMALISED TO UNIT MEAN over the monsoon band, because the point is to
    # REDISTRIBUTE the descent toward genuinely convecting sources, not to
    # reduce it. Applied raw, the weight is below 1 nearly everywhere, so the
    # total descent budget shrank and every desert got wetter with it -- the
    # Rub al Khali went 0.122 to 0.197 and the Sahara 0.009 to 0.035 while the
    # Deccan improved. Two margins better and one much worse is not a fix.
    wgt = np.clip(R / MONSOON_WET, 0.0, 1.0)
    src = monsoon > 0.20
    wgt = wgt / max(float(wgt[src].mean()) if src.any() else 1.0, 1e-3)
    ms = _smooth(monsoon * wgt, max(2, int(W / 90)))
    step = max(1, int(W / 120))            # sample every ~3 degrees
    induced = np.zeros_like(ms)
    wsum = 0.0
    d = step
    while d * 360.0 / W <= 96.0:           # out to ~96 degrees west of source
        w = np.exp(-(d * 360.0 / W) / SUBSID_LAMBDA)
        induced += np.roll(ms, -d, axis=1) * w
        wsum += w
        d += step
    # Weight the descent to the SUBTROPICAL RIDGE. One uniform gain cannot both
    # dry the Rub al Khali and spare the Sahel: they sit on the same belt, and
    # every gain strong enough to make Arabia sand turned the Sahel to sand too.
    # They differ in latitude, not in longitude -- the descending limb maximises
    # over the ridge near 26 degrees, while the Sahel and the Chaco lie on its
    # equatorward flank where the summer ITCZ still reaches them.
    ridge = np.exp(-((absl - 26.0) ** 2) / (2.0 * 9.5 ** 2))
    induced *= (SUBSID_GAIN / wsum) * ridge
    monsoon = np.clip(monsoon - induced, 0.0, None)

    # MONSOON ADMISSION. R_ns is the only south-north transport in the solve and
    # it was admitted through `cyc` alone -- the extratropical cyclone band, 32
    # to 62 degrees -- so nothing could move poleward anywhere between the
    # equator and the horse latitudes. The Indian monsoon is exactly that flow
    # and the Himalayan front is what it runs into, which is why land above
    # 2500 m came out at mean rainfall 0.0027 with 97.7% of it under 0.02.
    #
    # The `monsoon` term above cannot do this job: it enters as
    # `Rf = (B + monsoon) * R`, a MULTIPLIER on moisture already delivered, so
    # where R is zero for want of transport the bonus multiplies zero.
    # A monsoon is a delivery mechanism, not a gain.
    #
    # Admitted HERE, after `induced`, and suppressed by it -- the same descent
    # that dries Arabia in the multiplier has to dry it in the delivery, or the
    # Rub al Khali floods (measured at 0.142 with the admission applied before
    # this point, against 0.013 for the Sahara beside it).
    subs = np.clip(induced / max(float(induced.max()), 1e-6), 0.0, 1.0)
    mons_adm = (_band(absl, 5.0, 32.0, feather=9.0) * _smooth(land.astype(float), 2)
                * np.clip(1.0 - MONSOON_SUBS * subs, 0.0, 1.0))
    R = np.clip(np.maximum(R, R_ns * mons_adm * MONSOON_ADM), 0, 1.6)

    # a warmer world evaporates more; `arid` already shapes the belts above so
    # it is deliberately not applied twice here
    glob = np.clip(1.02 + 0.22 * cl["temp"], 0.78, 1.30)
    Rf = (B + monsoon) * R * glob
    # ...AND THE SAME DESCENT SUPPRESSES WHAT THE ZONAL FLOW DELIVERS.
    # Subtracting `induced` from the monsoon bonus alone cannot dry Arabia,
    # because Arabia's moisture is not a bonus: it is a peninsula with ocean on
    # three sides, so the advection arrives with a short fetch and full load.
    # Measured on the shipped field, that left the Rub al Khali at a humidity
    # index of 0.404 against the Congo rainforest's 0.321 -- the driest sand on
    # Earth reading wetter than a rainforest, which no biome threshold can
    # survive. Air that is sinking does not rain whatever reaches it, so the
    # descent has to scale the delivered field, not just one term of it.
    Rf *= np.clip(1.0 - SUBSID_DRY * induced, 0.12, 1.0)
    # The advection runs along rows, so without meridional mixing the field
    # keeps row-to-row streaks that surface later as straight horizontal bands
    # of vegetation. Real atmosphere mixes across latitude; so does this.
    Rf = _smooth(Rf, 2)
    Rf = 0.5 * Rf + 0.25 * np.roll(Rf, 1, axis=0) + 0.25 * np.roll(Rf, -1, axis=0)
    Rf = _smooth(Rf, 1)
    return np.clip(Rf, 0, 1.3)


RECYCLE_KM = 1800.0     # e-folding distance of land moisture recycling, at the equator
FLOOR_BARE   = 0.25     # share of the floor bare ground still gets
FLOOR_COLD   = 2.0      # recycling sustains more where evaporative demand is low
RECYCLE_COLD = 9.0      # ...times this much further where the air is cold and holds it
RECYCLE_REGEN = 0.90    # how far wet ground rewinds that clock
RECYCLE_REF = 0.25      # rainfall counted as 'fully recycling'
RECYCLE_FLOOR = 0.55    # fraction of saturation wet ground sustains
SUBSID_LAMBDA = 26.0    # e-folding distance of the subsiding limb, degrees lon
SUBSID_GAIN = 0.75      # how much of the source monsoon the descent cancels
MONSOON_ADM = 1.00      # admission of poleward transport through monsoon geometry
MONSOON_SUBS= 0.95      # how completely the induced descent closes that admission
MONSOON_WET = 0.35      # delivered rain at which a monsoon source convects at full strength
SUBSID_DRY = 2.6        # how hard that descent suppresses delivered rain


def _b3(col, H, W):
    return np.ones((H, W, 3)) * col


def _L3(a, b, t):
    return a * (1 - t)[..., None] + b * t[..., None]


def resample_dem(z, out_h, out_w):
    """Bilinear-resample a lat-ascending DEM to (out_h,out_w) with row 0 = north.

    Longitude is sampled as a PERIODIC axis: the output spans the full 360
    degrees and the column after the last input column is the first one again.
    Mapping onto 0..W0-1 and clamping instead (which is what this did) both
    stretches the map by one input column and breaks the wrap at 180."""
    H0, W0 = z.shape
    yi = np.linspace(0, H0 - 1, out_h)
    xi = np.linspace(0, W0, out_w, endpoint=False)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H0 - 1); fy = (yi - y0)[:, None]
    x0 = np.floor(xi).astype(int) % W0; x1 = (x0 + 1) % W0; fx = (xi - np.floor(xi))[None, :]
    a = z.astype(float)
    top = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx
    bot = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
    return (top * (1 - fy) + bot * fy)[::-1]


def smooth_bathymetry(Z):
    """Band-limit the sea floor to what a 20 km grid can actually carry.

    This began as "flatten the abyssal plains", and for the plains it worked.
    The band it did not reach is the one that mattered: ridges, rises, arcs and
    plateaus, between about 1.5 and 3 km. Measured on the shipped field, 29% of
    adjacent texels there differ by two or more encoding levels and the 95th
    percentile is five -- some 350 m between neighbours, on ground whose true
    slope over 20 km is a fraction of a degree. That is not relief, it is the
    source DEM aliased onto a grid too coarse to hold it, and the renderer has
    no way to tell the difference: every one of those steps becomes a hard
    facet, and together they are the granular black hatch that traced every
    mid-ocean ridge on the globe.

    So the criterion is the shelf break rather than the abyss. Below it, the
    fine structure of the sea floor is synthesised per pixel from the ocean-
    structure field and does not need to be -- cannot usefully be -- carried
    here. Above it, on the shelf and around the coast, the shipped field IS the
    best description available and is left alone.

    Two passes rather than one wide kernel: 5x5 across the whole sea floor below
    the break, and a 3x3 weighted into the deep, where there is genuinely nothing
    finer to keep. A single wider box would have the same reach but a boxier
    impulse response, and the sea floor is one of the few places a filter
    footprint would be visible.

    These radii are in CELLS and are deliberately NOT scaled with the grid --
    unlike every filter in seafloor.py, which encodes a width in degrees. This
    one encodes the raster's own Nyquist limit, so when the grid doubled to
    2048x4096 the footprint correctly halved in angle: 5 cells is 49 km at
    9.8 km cells against 137 km at 19.5, and the extra 90 km of bathymetry it
    now keeps is exactly what the finer grid was bought for."""
    below = np.clip((-Z - 250.0) / 650.0, 0, 1)      # 0 on the shelf, 1 past the break
    Zs = Z * (1 - below) + _smooth(Z, 2) * below
    deep = np.clip((-Z - 2200.0) / 1400.0, 0, 1)
    return Zs * (1 - deep) + _smooth(Zs, 1) * deep


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
    # longitude is periodic here too -- see resample_dem
    yi = np.linspace(0, H0 - 1, out_h); xi = np.linspace(0, W0, out_w, endpoint=False)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H0 - 1); fy = (yi - y0)[:, None]
    x0 = np.floor(xi).astype(int) % W0; x1 = (x0 + 1) % W0; fx = (xi - np.floor(xi))[None, :]

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


#: How much colder an ice-sheet MARGIN is than the latitude band it reaches.
#: The climate table's ice line is where ice gets TO, and a sheet's edge sits in
#: air a few degrees below the zonal mean for that latitude -- it is over ice,
#: which is bright and cold, and it is usually inland or upslope of the parallel
#: it touches. Six degrees is what the present day needs, and the same six
#: degrees independently lands the Late Palaeozoic Ice Age peak on its measured
#: extent, which is the check that makes it a constant rather than a fudge.
MARGIN_OFFSET = -5.0


def zonal_T(lat_deg, temp):
    """Sea-level mean annual temperature at a latitude, as the SHADER computes it.

    Duplicated from the GLSL on purpose. The threshold has to be expressed in
    the same temperature field it will be compared against, or the number means
    nothing; and the alternative -- shipping the curve as data -- would put a
    second copy in flight anyway. If the GLSL curve changes, change it here.
    """
    s2 = np.sin(np.radians(lat_deg)) ** 2
    return (26.0 - 24.0 * s2 - 26.0 * s2 ** 3) + (temp + 0.55) * (4.0 + 15.0 * s2)


def glaciation(cl):
    """Per-era ice thresholds (deg C) for land ice and sea ice.

    This used to map the ice line onto the threshold through a hand-fitted
    linear ramp, `-30 + 12*glac`, and it was wrong by about eleven degrees:
    land ice needed a mean annual temperature below -21 C, when a real ice
    sheet's margin sits nearer -10. Measured against the record the app was
    under-iced at EVERY ice-bearing keyframe and over-iced at none -- the
    present drew 4.0 Mkm2 of land ice against an actual 15.7. The ramp also
    saturated at an ice line of 50 degrees, so every Cryogenian snowball got
    an identical threshold no matter how far the ice actually reached.

    Now the threshold is simply the temperature at the ice line the table
    already states, less the margin offset. That makes the table's number mean
    what it says -- "land poleward of this carries ice" -- so when the drawn
    area disagrees with the literature the fix is to correct a latitude a
    reader can check, not a magic constant. See ice_audit.py.

    Sea ice is WARMER than land ice, not colder. An earlier version of this
    had it the other way round on the reasoning that land glaciates where ocean
    does not -- which is true of ICE SHEETS and false of what the sea actually
    grows. Pack ice is a thin skin that forms as soon as the surface freezes,
    and it reaches further from the pole than any sheet does: today it covers
    the Southern Ocean out past 60S every winter while the Antarctic sheet
    stops at the coast. Getting this backwards left a bare gap between the ice
    sheet's edge and the nearest sea ice, all the way round the continent.

    The real land/ocean asymmetry is elsewhere, and it is about thickness and
    what the ice rests on: a sheet is kilometres thick and grounds on rock, so
    where the water is shallow enough to ground on, the LAND threshold applies
    (see the shelf term in the shader). That is what makes Antarctica and the
    Arctic look so unalike, not the ocean resisting freezing.
    """
    lines = [x for x in (cl["iceN"], cl["iceS"]) if x is not None]
    if not lines:
        return -30.0, -14.0          # ice-free hothouse; nothing to place
    # The shader's temperature field is hemisphere-symmetric, so one threshold
    # serves both poles and the equatorward line has to win -- otherwise an era
    # with ice at one pole only would lose it.
    line = min(lines)
    sb = snowball_at(cl)
    # MARGIN_OFFSET calibrates an ORDINARY ice sheet, whose margin sits several
    # degrees colder than the nominal ice line. A snowball does not work that
    # way: the ice-albedo runaway carries the sheet past its own equilibrium
    # margin and freezes the ocean over completely. Keeping the offset left a
    # bare tropical belt ~12 degrees wide that the equatorial glacial deposits
    # rule out, so fade it out as the state goes global and add a little
    # headroom. The narrow refugia that DID exist are drawn in the shader.
    ice_T = float(zonal_T(line, cl["temp"])) + MARGIN_OFFSET * (1.0 - sb) + 2.0 * sb
    return ice_T, ice_T + 3.0


def snowball_at(cl):
    """How completely frozen this era is, 0..1, from the ice line alone.

    A snowball is not just a strong icehouse: the ice-albedo runaway carries the
    line into the tropics, and the interesting consequences -- narrow refugia of
    thin ice and open water, cryoconite meltwater ponds on the ablating
    equatorial ice -- only exist in that state. 1 when the line is at the
    equator, 0 by 25 degrees, which keeps every ordinary icehouse (the Hirnantian
    at 64, the Pleistocene at 72) firmly at zero.
    """
    lines = [x for x in (cl["iceN"], cl["iceS"]) if x is not None]
    if not lines:
        return 0.0
    line = min(lines)
    return float(max(0.0, min(1.0, (25.0 - line) / 20.0)))


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
