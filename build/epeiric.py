"""Flood the epicontinental seas the global paleo-DEM cannot resolve.

The PaleoDEMs are a 20 km global grid built for topography, and they lose
shallow seas that flooded continental interiors: the Trans-Saharan Seaway does
not appear at any age, so its label had nothing to sit on and the map silently
contradicted its own description. The same is true of the Cannonball Sea, the
last marine incursion into the middle of North America.

This is the same deliberate exception the Great Lakes get in bake_lakes: where
the record is clear and the grid simply cannot resolve the feature, seed it
rather than pretend it was not there. Everything here is a named sea with real
stratigraphic control, not a general licence to invent water.

Footprints are given in PRESENT-DAY coordinates -- the modern outcrop of the
basin's marine deposits -- and back-advected along the same PALEOMAP rotations
that carry the labels, which are the frame the terrain itself is drawn in, so
the sea lands on the crust it actually flooded. Depth follows an authored curve
so each sea waxes and wanes instead of switching on and off.

Only low ground floods: anything already above FLOOD_CEILING is left alone, so
seeding a seaway cannot drown a mountain range.
"""
import math

import numpy as np

FLOOD_CEILING = 900.0        # m: ground higher than this is never flooded


def _curve(age, points):
    """Linear interpolation over (age, value) points, 0 outside the range."""
    pts = sorted(points, key=lambda p: p[0])
    if age <= pts[0][0] or age >= pts[-1][0]:
        return 0.0
    for i in range(len(pts) - 1):
        a0, v0 = pts[i]
        a1, v1 = pts[i + 1]
        if a0 <= age <= a1:
            t = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return v0 + (v1 - v0) * t
    return 0.0


SEAS = {
    # The Trans-Saharan Seaway flooded the Iullemmeden, Malian and Taoudeni
    # basins, joining Tethys to the Gulf of Guinea and cutting West Africa into
    # islands. Two high-stands -- the Cenomanian-Turonian and again in the
    # Paleocene -- with final withdrawal in the Eocene as the basins filled and
    # the region rose. Footprint anchors are the modern basins.
    "Trans-Saharan Sea": {
        "anchors": [(-3.0, 17.5, 550), (2.0, 20.0, 500), (7.5, 16.0, 500),
                    (6.5, 12.0, 420), (1.0, 14.0, 450), (10.0, 20.0, 400)],
        "depth": [(50, 0), (55, 55), (60, 110), (66, 130), (75, 95),
                  (85, 120), (94, 165), (100, 90), (105, 0)],
    },
    # The Cannonball Formation: a brief Paleocene arm of the Boreal sea reaching
    # down into the Dakotas, the last time salt water crossed the continent.
    "Cannonball Sea": {
        "anchors": [(-100.5, 47.0, 380), (-99.0, 45.5, 320), (-101.5, 48.5, 300)],
        "depth": [(56, 0), (58, 70), (60, 105), (62, 70), (64, 0)],
    },
    # ---------------- the Triassic-Jurassic, added 2026-07-27 ----------------
    # This module reached 50-105 Ma and 56-64 Ma and nothing else, so the
    # interval where the reconstruction is WORST for shelf sea had no seeded
    # water at all. Measured against Deep Time Maps on 31 ages: at 240 Ma we drew
    # 1.8% shallow sea against Blakey's 8.0%, and 93% of everything he draws as
    # shelf sea was dry land in ours (200 Ma: 3.1 vs 8.0, 83%; 180 Ma: 4.7 vs
    # 8.1, 77%). That is also the whole of the +5 to +9 pp land EXCESS at those
    # ages -- it was never extra continent, it was missing sea.
    #
    # Each of these is a named basin with stratigraphic control, not a general
    # licence to invent water, and each depth curve is its own transgression.
    #
    # The Germanic Basin: the type Triassic epicontinental sea, a shallow arm of
    # Tethys reaching into central Europe through the Silesian and Carpathian
    # gates. The Muschelkalk is its marine middle -- limestone between the
    # continental red beds of the Buntsandstein below and the Keuper above.
    "Muschelkalk Sea": {
        "anchors": [(9.0, 51.0, 420), (13.0, 52.5, 380), (6.0, 49.0, 340),
                    (16.0, 50.0, 320), (10.5, 47.5, 300)],
        "depth": [(228, 0), (232, 45), (237, 95), (243, 130), (247, 90),
                  (250, 0)],
    },
    # The Zechstein: a hypersaline inland sea over northern Europe, flooded from
    # the Boreal ocean through a narrow gap and evaporated down repeatedly. Its
    # salt is why the North Sea has domes and gas fields.
    "Zechstein Sea": {
        "anchors": [(8.0, 53.0, 460), (2.0, 54.5, 400), (14.0, 52.0, 340),
                    (-1.0, 54.0, 280)],
        "depth": [(250, 0), (252, 70), (256, 120), (259, 105), (262, 0)],
    },
    # The Sverdrup Basin: a long-lived marine trough in the Canadian Arctic
    # islands, filled with Triassic and Jurassic shelf mudstone and sandstone.
    "Sverdrup Sea": {
        "anchors": [(-95.0, 78.5, 460), (-85.0, 77.0, 400), (-105.0, 79.5, 380),
                    (-75.0, 76.0, 320)],
        "depth": [(140, 0), (155, 70), (180, 120), (215, 130), (245, 95),
                  (255, 0)],
    },
    # The West Siberian Basin: repeatedly flooded from the Arctic through the
    # Mesozoic, and the largest single epicontinental sea of the Jurassic.
    "West Siberian Sea (Jurassic)": {
        "anchors": [(72.0, 62.0, 620), (78.0, 66.0, 520), (68.0, 58.0, 460),
                    (84.0, 63.0, 420), (75.0, 70.0, 400)],
        "depth": [(140, 0), (150, 80), (165, 135), (180, 150), (200, 110),
                  (215, 0)],
    },
    # The Sundance Sea: a Middle-Late Jurassic arm of the Boreal ocean reaching
    # south down western North America, the predecessor of the Cretaceous
    # Western Interior Seaway and the sea the Morrison Formation replaced.
    "Sundance Sea": {
        "anchors": [(-108.0, 44.0, 420), (-110.0, 47.0, 380), (-106.0, 41.0, 330),
                    (-112.0, 50.0, 320)],
        "depth": [(148, 0), (155, 75), (165, 130), (172, 120), (180, 60),
                  (185, 0)],
    },
    # The Russian Platform: the Moscow Basin and its neighbours, flooded from the
    # north in the Late Jurassic -- the black shales of the Volga are its record.
    "Russian Platform Sea": {
        "anchors": [(40.0, 56.0, 520), (48.0, 52.0, 440), (34.0, 59.0, 400),
                    (52.0, 58.0, 380)],
        "depth": [(140, 0), (148, 70), (158, 120), (168, 105), (180, 0)],
    },
    # NOTE, and it is the reason two entries were removed again the same day:
    # what belongs in this table is an epicontinental SEA -- water standing on
    # continental interior, which a 20 km grid loses because it is shallow. A
    # continental SHELF is a different object, it is a margin not an interior,
    # and the shelf mechanism below now supplies it to a measured target. An
    # Arabian carbonate platform and an Australian northwest shelf were entered
    # here first and did both jobs at once: at 220 Ma the named seas alone took
    # the shelf fraction from 6.3% to 11.3% against a 7.3% target, which is the
    # double count showing up as an over-flooded frame.
    # The Neuquen Basin: a back-arc embayment on the Pacific margin of southern
    # Gondwana, marine through most of the Jurassic.
    "Neuquen Sea": {
        "anchors": [(-70.0, -37.0, 380), (-68.0, -34.0, 320), (-71.5, -40.0, 300)],
        "depth": [(130, 0), (145, 70), (165, 115), (185, 100), (200, 0)],
    },
    # The Northern Calcareous Alps and the Dolomites: the Tethyan carbonate
    # platforms of the Triassic, and the reefs the Dachstein fauna built.
    "Tethyan Platform (Alpine)": {
        "anchors": [(12.0, 46.5, 340), (16.0, 47.5, 300), (9.0, 45.5, 280)],
        "depth": [(195, 0), (205, 80), (220, 130), (235, 125), (250, 0)],
    },
}

# ------------------------------------------------------------------ shelf ---
# The named basins above are the seas a reader can point at. They are not the
# whole deficit: at 240 Ma the gap is 6.2 points of the GLOBE, about 31 million
# square kilometres, and every named epicontinental sea of that age put together
# is a third of it. The rest is a CONTINENTAL SHELF that our terrain does not
# have.
#
# Rendered side by side the difference is not subtle -- Blakey's Triassic Pangaea
# carries a wide bright shelf all the way round its margin, and ours is a solid
# mass with a fringe one or two pixels wide. That is a resolution artefact with a
# specific cause: a 20 km grid samples the shelf break, which is 130-200 m deep
# and tens to a couple of hundred kilometres offshore, in one or two cells, so
# the shelf falls between samples and the coastline lands on the slope.
#
# So flood the outermost band of low continental ground during the highstand.
# This is the same deliberate exception the named seas and the Great Lakes get:
# where the record is clear and the grid cannot resolve the feature, seed it.
# What it must NOT do is drown continental interiors, so it is gated on distance
# from the coast as well as on elevation.
SHELF_WINDOW = [(115, 0.0), (130, 1.0), (250, 1.0), (262, 0.0)]
# Half-width of the neighbourhood a frame is judged against. Swept, and the
# sweep is worth recording because the number is not arbitrary and the check is
# independent of the thing being fitted. The target is a median of OUR OWN source
# grids over this window; Deep Time Maps is then used only to SCORE it, never to
# set it. Mean absolute error of the target against Blakey over 150-250 Ma:
#
#     +/-30 Myr   1.56 pp     the anomaly's own neighbourhood is depressed too
#     +/-50 Myr   1.35 pp
#     +/-70 Myr   0.68 pp     <- here
#     +/-90 Myr   0.69 pp     no better, and it starts lifting the 0 Ma control
#
# 70 Myr is about the length of a period, which is the timescale over which
# continental configuration and eustatic sea level actually change shelf area.
SHELF_SMOOTH_MYR = 70.0
SHELF_BAND = -1305.0       # m: the depth band that counts as shelf when measuring
# Swept against Deep Time Maps on seven ages. Mean absolute error over that set,
# land and shelf-sea fraction of the globe, for four (ceiling, reach, sigma):
#     700 / 0.55 / 3.2    land 1.72 pp   shelf 1.02 pp   <- here
#     700 / 0.75 / 4.5    land 1.88      shelf 0.97
#     900 / 0.75 / 4.5    land 1.83      shelf 0.96
#    1200 / 0.90 / 5.5    land 1.93      shelf 0.94
# The wider settings buy 0.06 pp of shelf accuracy for 0.2 pp of land, which is
# the wrong trade: land area is the better-constrained of the two measurements
# and the one an over-eager shelf would damage first.
SHELF_CEILING = 700.0      # m: ground above this is never shelf, whatever the age
SHELF_DEPTH = 110.0        # m: what a flooded shelf cell is set to
SHELF_REACH = 0.55         # how much ocean in the neighbourhood counts as "coastal"
SHELF_SIGMA_DEG = 3.2      # the neighbourhood radius, degrees (~355 km)


def _blob(LON, LAT, plon, plat, radius_km):
    """Smooth 0..1 falloff around a point, on the sphere."""
    r = math.degrees(radius_km / 6371.0)
    dlon = ((LON - plon + 180.0) % 360.0) - 180.0
    d = np.sqrt((dlon * np.cos(np.radians(LAT))) ** 2 + (LAT - plat) ** 2)
    # 1 inside, tapering to 0 at the rim
    return np.clip(1.0 - (d / r) ** 2, 0.0, 1.0)


_SHELF_TABLE = None


def _shelf_profile():
    """Raw shelf fraction of the globe at every Phanerozoic keyframe, and a
    time-smoothed version of it. Computed once, at coarse resolution.

    WHY THE TARGET COMES FROM THE FRAME'S OWN NEIGHBOURS. A fixed-strength shelf
    over-floods any frame that already has one, and measured on the raw
    PaleoDEMs that is most of them -- the shelf fraction jumps 8.6% -> 4.5% ->
    3.0% -> 6.3% -> 1.6% -> 8.2% -> 13.8% across 170, 180, 200, 220, 240, 250 and
    260 Ma while eustatic sea level slides smoothly from 83 m down to 0. Shelf
    area does not do that. Sea level moves slowly, coastlines move slowly, and a
    seven-point swing between two adjacent 10 Myr frames is how the source grids
    were authored rather than anything that happened.

    So the target is the frame's own neighbourhood, and the mechanism supplies
    only the DEFICIT against it. A frame that already carries a shelf gets
    nothing; a frame that is anomalously bare against the 30 Myr either side of
    it gets brought up to them. Nothing here consults an external
    reconstruction -- the erraticism is visible in our own source data, and it is
    self-correcting at ages nobody has checked.
    """
    global _SHELF_TABLE
    if _SHELF_TABLE is not None:
        return _SHELF_TABLE
    try:
        from build_frames import index_dems, read_dem
        from render import resample_dem
    except Exception:                                      # noqa: BLE001
        _SHELF_TABLE = ([], [])
        return _SHELF_TABLE
    h, w = 256, 512
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    aw = np.cos(np.radians(lat))[:, None] * np.ones((1, w))
    aw = aw / aw.sum()
    idx = index_dems()
    ages = sorted(a for a in idx if 0 <= a <= 541)
    raw = []
    for a in ages:
        z = resample_dem(read_dem(idx[a]), h, w)
        raw.append(float((aw * ((z < 0) & (z > SHELF_BAND))).sum()))
    ages = np.array(ages, float)
    raw = np.array(raw, float)
    # Median, not mean: one anomalously bare frame should not drag its own
    # target down, which is exactly what it would do in an average.
    smooth = np.array([float(np.median(raw[np.abs(ages - a) <= SHELF_SMOOTH_MYR]))
                       for a in ages])
    _SHELF_TABLE = (ages, np.maximum(smooth, raw))
    return _SHELF_TABLE


def shelf_target(age):
    """Shelf fraction of the globe this frame ought to carry, from its own
    neighbourhood. Zero if the profile could not be built."""
    ages, target = _shelf_profile()
    if not len(ages):
        return 0.0
    return float(np.interp(abs(age), ages, target))


def _coastal(land, deg_per_cell):
    """0..1 weight: how close a land cell is to open sea.

    A smoothed land fraction rather than a distance transform. It is far cheaper
    at 2048x4096, it is smooth by construction -- so the flooded shelf has a soft
    landward edge instead of a contour -- and it says the right thing: a cell
    whose neighbourhood is half ocean is on a margin, and a cell surrounded by
    land is an interior whatever its elevation.
    """
    from scipy.ndimage import gaussian_filter
    sigma = max(1.0, SHELF_SIGMA_DEG / max(deg_per_cell, 1e-6))
    frac = gaussian_filter(land.astype(np.float32), sigma, mode="nearest")
    # How much OCEAN is in this cell's neighbourhood, normalised. A cell right on
    # the coast sees about half ocean and scores 1; a continental interior sees
    # none and scores 0. (Written the other way round first -- 1 - frac/REACH --
    # which is 0 at the coastline itself, so almost nothing flooded.)
    return np.clip((1.0 - frac) / max(SHELF_REACH, 1e-6), 0.0, 1.0)


def carve(z, age, reconstructor=None, verbose=False):
    """Flood the seeded seas into an elevation grid for one age.

    z is (H, W), row 0 = north, spanning the globe. Returns a new grid.
    """
    total = sum(_curve(age, s["depth"]) for s in SEAS.values())
    shelfw = _curve(age, SHELF_WINDOW)
    if total <= 0 and shelfw <= 0:
        return z
    h, w = z.shape
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    out = z
    for name, spec in SEAS.items():
        depth = _curve(age, spec["depth"])
        if depth <= 0:
            continue
        mask = np.zeros_like(z)
        for alon, alat, radius in spec["anchors"]:
            plon, plat = alon, alat
            if reconstructor is not None:
                try:
                    tr, _ = reconstructor.track(float(alon), float(alat),
                                                min(540, max(age, 5)))
                    if tr:
                        # last point at or before the age
                        best = min(tr, key=lambda r: abs(r[0] - age))
                        plon, plat = best[1], best[2]
                except Exception:
                    pass
            mask = np.maximum(mask, _blob(LON, LAT, plon, plat, radius))
        if not mask.any():
            continue
        # only low ground floods, and the fade at the rim is a shoreline
        floodable = np.clip((FLOOD_CEILING - out) / FLOOD_CEILING, 0.0, 1.0)
        m = mask * floodable
        # NEVER raise: blending toward a shallow target would lift the abyssal
        # floor of a neighbouring ocean up to shelf depth wherever the footprint
        # overlapped it. Flooding can only ever lower ground.
        out = np.minimum(out, out * (1.0 - m) + (-depth) * m)
        if verbose:
            print(f"    {name}: {depth:.0f} m over "
                  f"{100.0 * (m > 0.05).mean():.2f}% of the grid")

    # The Pangaean shelf. Applied AFTER the named seas so a basin already
    # flooded to 150 m is not pulled back up to shelf depth by it.
    if shelfw > 0:
        land = out >= 0.0
        near = _coastal(land, 180.0 / h)
        # Only low ground, and only near the coast, and never a raise -- the same
        # three guards the named seas use.
        base = near * land
        lat_ = 90.0 - (np.arange(h) + 0.5) / h * 180.0
        aw = np.cos(np.radians(lat_))[:, None] * np.ones((1, w))
        aw = aw / aw.sum()

        def flood(k):
            """The weight sets WHICH ground floods, not how deep.

            Blending toward a shelf depth in proportion to a weight looks like
            the natural thing and is not: at weight 0.02 it shaves two metres off
            everything near the coast, and any land already within two metres of
            sea level becomes "shelf". Measured at 220 Ma that took the shelf
            fraction from 6.3% to 11.1% in one step, so the response was a
            staircase and the solver below could not land on a target at all.

            A rising sea floods higher ground. So the weight is an ELEVATION
            CEILING, and the area it covers grows smoothly with it -- which is
            both the physical statement and the monotone function the solver
            needs. The 60 m ramp keeps the landward edge soft instead of drawing
            a contour line along it.
            """
            ceil = np.clip(k, 0.0, 1.0) * SHELF_CEILING
            m = base * np.clip((ceil - out) / 60.0, 0.0, 1.0)
            return np.minimum(out, out * (1.0 - m) + (-SHELF_DEPTH) * m)

        def shelf_frac(g):
            return float((aw * ((g < 0) & (g > SHELF_BAND))).sum())

        target = shelf_target(age)
        have = shelf_frac(out)
        # ACCEPT ONLY IF IT HELPS. On some frames the smallest flood the grid can
        # express already overshoots: the 220 Ma PaleoDEM carries about 5% of the
        # globe as coastal land within FOURTEEN METRES of sea level, so a ceiling
        # of 14 m converts all of it at once and the shelf fraction steps 6.3% ->
        # 11.2% with nothing in between. A solver cannot land on a target that
        # the function jumps over, and pretending otherwise is how the previous
        # attempt over-flooded that frame by 3.3 points.
        #
        # So the test is not "is there a deficit" but "does flooding get closer
        # to the target than leaving it alone". Where the answer is no, the frame
        # keeps what it has -- which is the right answer anyway, because land
        # sitting within a few metres of sea level is the grid being vague about
        # a coastline, not a shelf waiting to be revealed.
        if target > have + 1e-5:
            # SOLVE for the weight rather than scaling by the fractional
            # shortfall. The response is not proportional -- the weight sets how
            # DEEP the flooding goes, and shelf area is a threshold crossing of
            # that -- so scaling by (target-have)/target lands well short. Six
            # bisection steps on a monotone function is exact enough and costs
            # six passes over a mask that is already computed.
            lo_k, hi_k = 0.0, shelfw
            if shelf_frac(flood(hi_k)) > target:
                for _ in range(6):
                    mid = 0.5 * (lo_k + hi_k)
                    if shelf_frac(flood(mid)) < target:
                        lo_k = mid
                    else:
                        hi_k = mid
            shelfw = hi_k
            cand = flood(shelfw)
            if abs(shelf_frac(cand) - target) < abs(have - target):
                out = cand
            else:
                shelfw = 0.0
            if verbose and shelfw == 0.0:
                print(f"    Pangaean shelf: declined -- the smallest flood this "
                      f"grid can express overshoots ({100 * shelf_frac(cand):.1f}% "
                      f"against a {100 * target:.1f}% target, from {100 * have:.1f}%)")
            elif verbose:
                print(f"    Pangaean shelf: weight {shelfw:.2f}, shelf "
                      f"{100 * have:.1f}% -> {100 * shelf_frac(out):.1f}% "
                      f"(target {100 * target:.1f}%)")
        elif verbose:
            print(f"    Pangaean shelf: none needed "
                  f"({100 * have:.1f}% already, target {100 * target:.1f}%)")
    return out
