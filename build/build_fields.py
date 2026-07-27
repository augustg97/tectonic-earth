"""Export the terrain + climate field textures the web build interpolates.

Per keyframe we ship two grayscale WebPs -- elevation (coastline-critical, so
high res) and rainfall (smooth, so low res) -- plus a few scalars in the
manifest. Temperature is NOT shipped: it is a closed form of latitude,
elevation and the era anomaly, so the shader recomputes it for free.

Three eras, three sources:
  * Phanerozoic 0-540 Ma -- Scotese & Wright paleoDEMs, straight through.
  * Future 0 -> +250 Myr -- the PRESENT DEM rigidly rotated by plate group.
    At age 0 every rotation is the identity, so the future series begins as an
    exact copy of the present frame and inherits its full detail; there is no
    seam and no drop in fidelity.
  * Precambrian 540-1000 Ma -- generated cratons (see precambrian.py), blended
    onto the real 540 Ma DEM across the youngest 60 Myr so the handoff into the
    Phanerozoic is continuous instead of popping.

A third texture per keyframe carries derived plate motion (see motion.py),
which drives both the motion-vector arrows and the plate boundaries at every
age rather than only near the present.
"""
import os, re, json, glob, io, math
import numpy as np
import netCDF4
from PIL import Image

import render as R
from render import compute_fields, resample_dem, smooth_bathymetry, glaciation
from climate import climate_at, system_at
from fieldpack import enc_elev, RF_MAX
from build_frames import period_for, sealevel_for, index_dems, read_dem
import build_synthetic as BS
import precambrian as PRE
import epeiric as EP
import seafloor as SF
import motion as MO
import paleo_tracks

OUT = "../web/fields"
os.makedirs(OUT, exist_ok=True)

# 2048x4096, doubled in July 2026. The source PaleoDEMs are 6 arc-minute --
# 0.1 degrees, 11.1 km at the equator -- and at 1024x2048 a texel was 19.5 km,
# so HALF the resolution that exists was being thrown away before anything else
# happened. Everything downstream inherited that: a continental slope drops
# 3 km across two texels and arrives as a staircase of near-vertical facets, a
# seamount is three texels across, and the shader has to reconstruct what the
# grid could not carry. 2048 rows puts a texel at 9.8 km, which is the source
# resolution and therefore the point at which more pixels stop buying anything.
#
# Cost, measured on the 0 Ma frame against a lossless encode: 439 kB at q=94
# against 198 kB at 1024x2048/q=96, and the same steep-ground error (0.71 levels
# mean, 3 at the 99th percentile). Across 251 keyframes that is about 51 MB
# against 25, so the elevation roughly doubles and the whole payload goes from
# 118 to ~144 MB. Quality drops 96 -> 94 because the finer grid needs less help:
# there is less real content per texel for the encoder to ring around.
ELEV_H, ELEV_W = 2048, 4096     # coastline resolution; matches the 6' source DEM
# Rainfall drives biome colour, the glacier equilibrium line AND the weighting
# on the drainage network, so it is the field that decides how varied a
# continent looks -- and at 768x384 it was the coarsest input in the pipeline,
# a quarter the linear resolution of the elevation it is painted over. That
# mismatch is most of why large landmasses came out in flat patches.
#
# CLIM is the resolution the wind solve actually RUNS at, and raising only the
# export would have bought nothing: the detail has to exist before it can be
# saved. Both go up together.
RAIN_H, RAIN_W = 768, 1536      # rainfall texture, 4x the pixels
CLIM_H, CLIM_W = 768, 1536      # the wind solve runs here too, or there is
                                # no new detail to export
# Ocean-structure field: crustal age + spreading direction. It is smooth (the
# fine abyssal-hill fabric is synthesised in the shader from it, not stored), so
# a quarter of the elevation resolution is ample and keeps the extra webp small.
# Deliberately NOT raised with the elevation: this field's limit is precision,
# not resolution -- see the companding note in seafloor.py -- and more pixels
# would cost real bytes to store a field that is already smooth between them.
OCEAN_H, OCEAN_W = 1024, 2048
# ELEV_Q is 94, and the reason is measurable rather than a matter of
# taste. WebP's lossy path rings around sharp edges, and the elevation field is
# encoded signed-sqrt so that one 8-bit level is 55 m at 1.5 km depth and 105 m
# at 5.5 km. Measured against a lossless encode of the same field, q=92 puts a
# mean error of 0.97 levels and a 99th percentile of FOUR on steep submarine
# ground (against 0.06 on flat abyss) -- i.e. a couple of hundred metres of
# invented relief, spatially organised as ringing, which the hillshade renders
# as the granular black speckle that covered every ridge flank and shelf edge.
# It is not visible on the abyssal plains because there is no edge there to ring
# around, which is exactly why it took so long to attribute.
#
# It buys the one thing the shader cannot: the shader's dequantisation shrinkage
# knows the size of a QUANTISATION step and can remove it exactly, but ringing is
# several steps and indistinguishable from real relief once it is in the file.
#
# 94 rather than 96 because the grid doubled at the same time. Measured on the
# 0 Ma frame, 2048x4096/q=94 lands at the same steep-ground error as
# 1024x2048/q=96 -- 0.71 levels mean, 3 at the 99th percentile -- for 439 kB
# against 198. Finer texels hold less real content each, so there is less for
# the encoder to ring around and the quality can come back down.
ELEV_Q, RAIN_Q, OCEAN_Q = 94, 90, 90
STEP = 5                         # Myr between keyframes, everywhere


def polar_lowpass(z, strength=1.0):
    """Band-limit the poleward rows of an equirectangular grid along longitude.

    THE ROOT CAUSE OF POLAR WARPING. An equirectangular grid stores the same
    number of longitude columns in every latitude row, so approaching a pole
    those columns crowd into a vanishing circle: at 89.9 degrees the 2048
    columns of a row span about 70 km of ground, a third of a kilometre each,
    while the rows stay ~20 km apart. Nothing in the source data resolves that,
    so the surplus is pure resampling noise -- and because it varies with
    longitude, a globe renders it as a radial starburst fanning out of the pole.
    Every downstream consumer inherits it: relief shading, ice, the depth ramp.

    Averaging each row over 1/cos(lat) columns removes exactly that surplus and
    nothing else. One column at the equator (a no-op), ~3 at 70 degrees, ~11 at
    85, most of the row inside the last tenth of a degree -- which is right,
    because there those columns really are all the same few kilometres of
    ground. Real geography survives: a coastline at 85 degrees still spans
    hundreds of columns.

    Doing it HERE rather than in the shader means it is fixed once, for every
    field and every consumer, at no per-pixel cost.
    """
    from scipy.ndimage import uniform_filter1d
    h, w = z.shape
    out = np.asarray(z, np.float32).copy()
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    al = np.abs(lat)
    coslat = np.maximum(np.cos(np.radians(lat)), 1e-6)
    # The window widens from one cell to three across the last 15 degrees. One
    # cell is the strict anti-alias criterion and is right through the
    # mid-latitudes, but it leaves the innermost rows merely SMOOTHED when they
    # need to CONVERGE: a pole is a single point, every meridian meets there, so
    # any residual variation around the last ring is drawn as a starburst no
    # matter how small it is. Ramping to three cells makes the final rows
    # average essentially the whole ring, which is what the geometry demands,
    # while 60-75 degrees is left almost untouched.
    t = np.clip((al - 75.0) / 15.0, 0.0, 1.0)
    k = strength * (1.0 + 2.0 * (t * t * (3.0 - 2.0 * t)))
    for i in range(h):
        win = int(round(k[i] / coslat[i]))
        if win > 1:
            # mode="wrap": longitude is periodic, so the average must be circular
            out[i] = uniform_filter1d(out[i], size=min(win, w), mode="wrap")
    # Final convergence. Inside the last two degrees the whole ring is one
    # ~200 km patch of ground, and every meridian of it is drawn meeting at a
    # single screen point -- so ANY variation left around that ring renders as a
    # starburst, however small and however real. Fade each of those rows into
    # its own mean, reaching full only exactly at the pole. This is a ring
    # average, but a legitimate one: it is bounded to two degrees and its weight
    # ramps smoothly to 1, unlike the earlier version that clamped a ring radius
    # and stamped a hard-edged disc across the whole cap.
    conv = np.clip((al - 88.0) / 2.0, 0.0, 1.0) ** 2
    for i in np.nonzero(conv > 0.001)[0]:
        out[i] = out[i] * (1.0 - conv[i]) + out[i].mean() * conv[i]
    return out


def _gray(a01):
    return Image.fromarray((np.clip(a01, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGB")


def _save(img, path, q):
    img.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)


_SF_REC = None


def _sf_reconstructor():
    """One reconstructor for the whole run, or None if pyGPlates is absent."""
    global _SF_REC
    if _SF_REC is None:
        try:
            _SF_REC = paleo_tracks.Reconstructor() if paleo_tracks.available() else False
        except Exception:
            _SF_REC = False
    return _SF_REC or None


def _load_motion(age, tag):
    """(vx, vy) for this age from the shipped _m field, or None if not built yet.

    seafloor needs the divergence of the plate-motion field to find spreading
    ridges. The _m texture is derived from the elevation keyframes by motion.py,
    so on a re-render it already exists; on a cold first build it does not, and
    seafloor falls back to seeding only the plateaus.
    """
    mf = os.path.join(OUT, f"{tag}_{abs(age):04d}_m.webp")
    if not os.path.exists(mf):
        return None
    a = np.asarray(Image.open(mf).convert("RGB"), np.float32) / 255.0
    vx = (a[..., 0] * 2 - 1) * 160.0
    vy = (a[..., 1] * 2 - 1) * 160.0
    return vx, vy


def export(age, Z_hi, z_for_climate, tag):
    """Z_hi: elevation at ELEV res, row 0 = north. z_for_climate: the raw
    lat-ascending DEM, kept as a fallback for callers that have no carved grid."""
    cl = climate_at(age)
    # THE CLIMATE SOLVE SEES THE TERRAIN THAT IS DRAWN, not the raw DEM.
    #
    # This ran on `z_for_climate` -- the source grid, before epeiric.carve -- so
    # every seeded sea changed the coastline and the map without making the air
    # over it any wetter. Harmless when the module seeded two named seas; not
    # harmless once it also supplies the continental shelf that ringed Pangaea,
    # which is several percent of the globe. Moisture recharges over water in
    # compute_fields, so a shelf sea upwind is exactly the thing that should be
    # feeding the Triassic megamonsoon's windward margins.
    #
    # ORIENTATION IS THE HAZARD HERE and it is the one that renders the whole
    # world upside down: read_dem returns latitude ASCENDING, resample_dem
    # returns row 0 = NORTH, epeiric.carve assumes north-first, and
    # compute_fields wants ascending again. Hence the flip -- verified by
    # measuring that rainfall still peaks at the equator and not at the poles.
    _, _, Rf, _, _ = compute_fields(z_for_climate, age, CLIM_H, CLIM_W)
    rain = np.asarray(Image.fromarray(
        (np.clip(Rf / RF_MAX, 0, 1) * 255).astype(np.uint8)).resize(
        (RAIN_W, RAIN_H), Image.LANCZOS)) / 255.0

    # Evolving sea-floor structure and the oceanic plateaus: age-graded abyss
    # from ridge distance, fracture zones, and Kerguelen / Ontong Java / the
    # Seychelles seeded so they drown and re-emerge on cue. See seafloor.py.
    mot = _load_motion(age, tag)
    Z_hi, ofield = SF.apply(Z_hi, age, reconstructor=_sf_reconstructor(), motion=mot)
    # Kill the polar longitude surplus BEFORE encoding, in true metres, so every
    # consumer of the elevation field is clean at the poles. See polar_lowpass.
    Z_hi = polar_lowpass(Z_hi)
    for _c in range(ofield.shape[2]):
        ofield[..., _c] = polar_lowpass(ofield[..., _c])
    e = _gray(enc_elev(smooth_bathymetry(Z_hi)))
    r = _gray(rain)
    # ocean-structure field: R = crustal age, G/B = spreading direction. The
    # shader grows the abyssal-hill fabric from it, so it need only be smooth.
    o = Image.fromarray((np.clip(ofield, 0, 1) * 255 + 0.5).astype(np.uint8)
                        ).resize((OCEAN_W, OCEAN_H), Image.BILINEAR)
    ef = f"{tag}_{abs(age):04d}_e.webp"
    rf = f"{tag}_{abs(age):04d}_r.webp"
    of = f"{tag}_{abs(age):04d}_o.webp"
    n = (_save(e, os.path.join(OUT, ef), ELEV_Q) + _save(r, os.path.join(OUT, rf), RAIN_Q)
         + _save(o, os.path.join(OUT, of), OCEAN_Q))
    ice_T, sea_T = glaciation(cl)
    ep, per = period_for(age)
    sysd = system_at(age)
    return {"age": age, "e": ef, "r": rf, "m": ef.replace("_e.webp", "_m.webp"),
            "epoch": ep, "period": per, "sealevel": sealevel_for(age),
            "temp": round(cl["temp"], 3), "veg": round(cl["veg"], 3),
            "iceT": round(ice_T, 2), "seaT": round(sea_T, 2),
            "snowball": round(R.snowball_at(cl), 3),
            "gmst": sysd["gmst"], "co2": sysd["co2"], "o2": sysd["o2"]}, n


# ---------------------------------------------------------------- future ----
# Where each group's centroid heads by +250 Myr, and its spin.
#
# RE-AIMED 2026-07-27 against the reconstruction this future is supposed to be.
# Measured as bearings from Africa at +250 Myr, against Scotese's Pangaea Ultima
# -- the geometry Farnsworth et al. (2024) modelled the climate on, which is why
# it is the one drawn here:
#
#                     was    now   published
#   North America     331    293      298 deg
#   South America     252    203      201
#   Eurasia            36     65       66
#   mean error         38      3
#
# And Australia now goes SOUTH with Antarctica instead of welding onto Africa's
# eastern flank: 6,321 km from Africa on bearing 152 and 3,933 km from
# Antarctica, where it was 2,969 km due east of Africa and inside the main mass.
# Land at +250 Myr goes UP as a side effect, 126.1 -> 128.5 Mkm2, because a
# better-spread arrangement stacks less.
#
# These are the AUTHORED targets. _packed_targets relaxes them so the groups stop
# interpenetrating, so what is written here is the intent and not the final
# position -- change these to move the reconstruction, and PACK to change how
# tightly it closes.
GROUP_TARGET = {
    "AFRICA":        (20, 2, 0),
    "EURASIA":       (74, 4, -16),
    "NORTH_AMERICA": (-8, -2, 52),
    "SOUTH_AMERICA": (0, -56, 34),
    "INDIA":         (44, 20, 14),
    "AUSTRALIA":     (70, -12, 118),
    "ANTARCTICA":    (25, -42, 26),
    "ARABIA":        (33, 18, 8),
    "PACIFIC":       (-150, 5, 0),
    # The Somali plate has to be its own group or the East African Rift cannot
    # open. It was lumped in with AFRICA, so it rotated identically with Africa
    # and no gap ever appeared -- while the labels promised an Afar Seaway from
    # +3 Myr, Somalia as an island from +15, and an East African Ocean from +25.
    # The map simply never showed the split the text described.
    # This target carries it east-northeast into the Indian Ocean, opening a
    # Red Sea-scale strait by +25 Myr and a true ocean basin by +60-130, and
    # eventually docking it against the India/Australia mass as Pangaea Proxima
    # assembles -- which is the "Madagascar-scale fragment drifting into the
    # Indian Ocean" the label describes.
    "SOMALIA":       (78, 4, 10),
}
PLATE_GROUP = {
    "Africa": "AFRICA", "Somalia": "SOMALIA", "Lwandle": "SOMALIA",
    "Eurasia": "EURASIA", "Amur": "EURASIA", "Okhotsk": "EURASIA",
    "Aegean Sea": "EURASIA", "Anatolia": "EURASIA", "Yangtze": "EURASIA",
    "Okinawa": "EURASIA", "Sunda": "EURASIA", "Burma": "EURASIA",
    "Philippine Sea": "EURASIA", "Timor": "AUSTRALIA", "Banda Sea": "EURASIA",
    "Molucca Sea": "EURASIA", "Mariana": "PACIFIC", "Caroline": "PACIFIC",
    "North America": "NORTH_AMERICA", "Juan de Fuca": "NORTH_AMERICA",
    "Rivera": "NORTH_AMERICA", "Cocos": "NORTH_AMERICA",
    "Caribbean": "NORTH_AMERICA", "Panama": "NORTH_AMERICA",
    "South America": "SOUTH_AMERICA", "Nazca": "SOUTH_AMERICA",
    "Altiplano": "SOUTH_AMERICA", "North Andes": "SOUTH_AMERICA",
    "Juan Fernandez": "SOUTH_AMERICA", "Easter": "SOUTH_AMERICA",
    "Galapagos": "SOUTH_AMERICA",
    "India": "INDIA", "Capricorn": "INDIA",
    "Australia": "AUSTRALIA", "Macquarie": "AUSTRALIA", "Birds Head": "AUSTRALIA",
    "Maoke": "AUSTRALIA", "Woodlark": "AUSTRALIA", "Solomon Sea": "AUSTRALIA",
    "New Hebrides": "AUSTRALIA", "Conway Reef": "AUSTRALIA",
    "Balmoral Reef": "AUSTRALIA", "Kermadec": "AUSTRALIA", "Tonga": "AUSTRALIA",
    "Niuafo'ou": "AUSTRALIA", "Futuna": "AUSTRALIA",
    "Antarctica": "ANTARCTICA", "Scotia": "ANTARCTICA", "Shetland": "ANTARCTICA",
    "Sandwich": "ANTARCTICA", "Sur": "ANTARCTICA",
    "Arabia": "ARABIA",
    "Pacific": "PACIFIC", "Manus": "PACIFIC", "North Bismarck": "PACIFIC",
    "South Bismarck": "PACIFIC",
}
GROUPS = sorted(set(GROUP_TARGET))


def rasterise_groups(h=360, w=720):
    """Group id per cell on the present-day sphere (-1 = unassigned ocean)."""
    plates = json.load(open("../web/plates.json"))
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    LON, LAT = np.meshgrid(lon, lat)
    gid = np.full((h, w), -1, np.int16)
    for p in plates:
        g = PLATE_GROUP.get(p["name"])
        if g is None:
            continue
        gi = GROUPS.index(g)
        inside = np.zeros((h, w), bool)
        for ring in p["rings"]:
            ring = np.asarray(ring, float)
            x, y = ring[:, 0], ring[:, 1]
            acc = np.zeros((h, w), bool)
            for i in range(len(ring)):
                j = (i - 1) % len(ring)
                cond = ((y[i] > LAT) != (y[j] > LAT)) & \
                       (LON < (x[j] - x[i]) * (LAT - y[i]) / (y[j] - y[i] + 1e-12) + x[i])
                acc ^= cond
            inside |= acc
        gid[inside & (gid < 0)] = gi
    return gid


def axis_angle_scale(Rm, frac):
    """Scale a rotation matrix's angle by frac (identity at frac=0)."""
    c = np.clip((np.trace(Rm) - 1.0) / 2.0, -1, 1)
    ang = np.arccos(c)
    if ang < 1e-8:
        return np.eye(3)
    ax = np.array([Rm[2, 1] - Rm[1, 2], Rm[0, 2] - Rm[2, 0], Rm[1, 0] - Rm[0, 1]])
    ax /= (2 * np.sin(ang))
    return BS.rodrigues(ax, np.degrees(ang) * frac)


# How close the packed targets may come, as a fraction of "the two land discs
# just touch". 1.0 is the physically clean statement AND the measured optimum,
# and the two agree for a reason: the radius is the 90th percentile of each
# group's land, so a tenth of every landmass still lies outside its disc and
# still collides at the margins. That residual collision is not a defect -- it is
# what a suture is, and a supercontinent that assembled without one would be
# wrong. Swept, raw land at +250 Myr against +0 (a rigid rotation conserves it
# exactly; rasterising costs about 5.5%):
#
#     PACK   land +250   loss    r90     emptiest hemisphere
#     0.00       97.1   35.5%   59.9 deg      0.10%      <- authored, the defect
#     0.75      114.7   23.8%   67.5 deg      0.11%
#     0.95      130.3   13.4%   74.6 deg      0.46%
#     1.00      133.1   11.6%   76.6 deg      0.55%      <- here
#     1.05      135.6   10.0%   78.4 deg      0.76%
#
# PALEOMAP's own rigid rotations give r90 76 deg, so 1.00 lands on the
# independent yardstick rather than near it, which is the reason to stop there
# rather than push the area figure lower.
PACK = 1.0
# Swept against what a collisional system actually adds. Today land above 2 km is
# 8.8 Mkm2; the Alpine-Himalayan belt is roughly 10,000 km long and 500 wide, so a
# Pangaea Ultima system should add of order 3-6 Mkm2 above 2 km, not tens. At
# +250 Myr these settings give:
#     land >1 km  29.9 -> 36.3 Mkm2      land >2 km  8.8 -> 13.8      >3 km  4.3 -> 5.5
#     mean land elevation 620 -> 781 m
# which is a Himalaya-scale addition rather than a world of mountains.
SUTURE_DEG = 3.0        # half-width of a collisional belt, degrees (~330 km)
SUTURE_UPLIFT = 3400.0  # m of crustal thickening at the contact by +250 Myr
SUTURE_POW = 3.0        # sharpens the belt; see the note where it is applied
SPRING = 0.55     # pull back toward the authored arrangement each pass
RELAX = 0.35      # step size; small enough that the two forces find a balance
_PACK_CACHE = {}


def _packed_targets(gid, Zsrc=None):
    """GROUP_TARGET, pushed apart until the groups no longer interpenetrate.

    THE DEFECT THIS FIXES. future_grid resolves two groups landing on the same
    ground with `out = np.maximum(out, z)`, so the lower of the two is deleted --
    and because the rule is "high ground wins", what it deletes is coastal plain,
    shelf and continental interior. Measured over the shipped series: land falls
    148.1 -> 92.6 Mkm2 across 250 Myr, a 37% loss, against 5.5% for a rigid
    rotation that conserves area by construction; ground below 1 km falls 45%
    while land above 2 km is flat; and mean land elevation RISES 667 -> 879 m.
    Instrumenting the claim masks pins it exactly: at +250 Myr, 53.3 Mkm2 of land
    is stacked on top of other land against a total deficit of 58.0, so 92% of
    the loss is groups interpenetrating and nothing else.

    THE FIX IS NOT A BETTER COLLISION RULE. Any rule that picks one of two
    stacked cells throws the other away; the land has nowhere to go because the
    destination is already full. The targets themselves are too close together
    for the size of the things being sent there -- everything collides with
    EURASIA, which is the largest group and is aimed into the middle of the pile.

    So treat each group as a disc of its own equal-area radius and relax the
    AUTHORED targets until they only touch. The arrangement is preserved --
    Africa still central, the Pacific still opposite, each group still heading
    where it was authored to head -- and only the packing changes. That also
    addresses the separate finding that the assembly ends too compact (r90 60
    degrees against PALEOMAP's 76) and closes about 100 Myr early, because both
    are the same over-tight targets seen from a different angle.
    """
    key = id(gid)
    if key in _PACK_CACHE:
        return _PACK_CACHE[key]
    gh, gw = gid.shape
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    cosw = np.cos(np.radians(GLAT))
    tot = cosw.sum()

    # LAND, not territory. A PB2002 plate group is mostly ocean -- the Pacific
    # group alone is a third of the globe -- and sizing the berths by territory
    # asked ten discs to tile the whole sphere, which is not a supercontinent but
    # a dispersal. What must not interpenetrate is the LAND each group carries,
    # because ocean stacked on ocean costs nothing and land stacked on land is
    # the entire defect.
    land = None
    if Zsrc is not None:
        zy = (np.arange(gh) * Zsrc.shape[0] // gh).clip(0, Zsrc.shape[0] - 1)
        zx = (np.arange(gw) * Zsrc.shape[1] // gw).clip(0, Zsrc.shape[1] - 1)
        land = Zsrc[np.ix_(zy, zx)] >= 0

    names, tgt, rad, mass = [], [], [], []
    for i, g in enumerate(GROUPS):
        m = gid == i
        if not m.any():
            continue
        tl, tb, _spin = GROUP_TARGET[g]
        names.append(g)
        tgt.append(BS.unit(tl, tb))
        lm = m & land if land is not None else m
        # The radius that holds this group's land about its own centroid. A
        # percentile rather than the maximum, so one stray island does not book
        # a berth for the whole group; and a real radius rather than an
        # equal-area disc, because what has to clear a neighbour is how far the
        # mass REACHES, not how much of it there is.
        if lm.any():
            c = BS.unit(GLON[m], GLAT[m]).mean(axis=1)
            c /= np.linalg.norm(c)
            v = BS.unit(GLON[lm], GLAT[lm])
            ang = np.arccos(np.clip(c @ v, -1.0, 1.0))
            wts = cosw[lm]
            order = np.argsort(ang)
            cw = np.cumsum(wts[order]) / max(wts.sum(), 1e-9)
            rad.append(float(ang[order][np.searchsorted(cw, 0.90)]))
            mass.append(float(wts.sum()))
        else:
            rad.append(0.0)          # an all-ocean group needs no berth
            mass.append(0.0)
    T = np.array(tgt, float)
    T0 = T.copy()                    # the authored arrangement, to spring back to
    mass = np.array(mass, float)
    mass = mass / max(mass.max(), 1e-9)

    # CONSTRAINED relaxation, and both constraints are needed.
    #
    # Mass-weighted, so a pair separates by moving the SMALL one. Pushing each
    # of a pair equally sent Eurasia -- which is the heaviest group and collides
    # with every other -- 67 degrees across the globe into the north Pacific,
    # because it accumulated a push from each neighbour and escaped. Continents
    # do not work that way: a small block docks against a large one.
    #
    # And sprung back to the authored arrangement, so the equilibrium is "as
    # close to what was authored as the geometry permits" rather than whatever
    # configuration the pushes happen to reach. The authored targets encode a
    # published reconstruction -- Scotese's Pangaea Ultima, which the app's
    # climate is calibrated on -- and the defect being fixed is that the groups
    # interpenetrate, not that the arrangement is wrong.
    for _ in range(400):
        step = np.zeros_like(T)
        for a in range(len(T)):
            for b in range(a + 1, len(T)):
                if rad[a] <= 0.0 or rad[b] <= 0.0:
                    continue
                d = math.acos(max(-1.0, min(1.0, float(np.dot(T[a], T[b])))))
                need = (rad[a] + rad[b]) * PACK
                if d >= need or d < 1e-6:
                    continue
                axis = np.cross(T[a], T[b])
                nrm = np.linalg.norm(axis)
                if nrm < 1e-9:
                    continue
                axis /= nrm
                over = need - d
                wa = mass[b] / max(mass[a] + mass[b], 1e-9)   # light one moves
                wb = mass[a] / max(mass[a] + mass[b], 1e-9)
                step[a] += -axis * over * wa
                step[b] += axis * over * wb
        # restoring spring toward the authored target
        for a in range(len(T)):
            ax = np.cross(T[a], T0[a])
            nrm = np.linalg.norm(ax)
            if nrm > 1e-9:
                dev = math.acos(max(-1.0, min(1.0, float(np.dot(T[a], T0[a])))))
                step[a] += (ax / nrm) * dev * SPRING
        moved = 0.0
        for a in range(len(T)):
            amp = np.linalg.norm(step[a])
            if amp < 1e-9:
                continue
            axis = step[a] / amp
            ang = min(amp, 0.05) * RELAX
            T[a] = BS.rodrigues(axis, math.degrees(ang)) @ T[a]
            T[a] /= np.linalg.norm(T[a])
            moved = max(moved, ang)
        if moved < 1e-5:
            break

    out = {}
    for k, g in enumerate(names):
        v = T[k]
        lat = math.degrees(math.asin(max(-1.0, min(1.0, float(v[2])))))
        lon = math.degrees(math.atan2(float(v[1]), float(v[0])))
        out[g] = (lon, lat, GROUP_TARGET[g][2])
    _PACK_CACHE[key] = out
    return out


def future_grid(frac, gid, Zsrc, h, w):
    """Inverse-warp the present DEM by per-group rotation. frac 0 -> identity.

    Seafloor that no group claims is new ocean opened behind the drifting
    plates. Filling it with one flat constant made those gaps read as blocky
    slabs of dead-level abyss with hard edges -- exactly the "oceans move as
    chunks" complaint. Instead the fill is a smooth field: shallower where new
    crust is young (near a spreading centre) grading to true abyssal depth, so
    the gaps look like ridge-and-basin ocean floor rather than a cut-out. It is
    still only a backdrop -- the shader adds the fine abyssal-hill texture on
    top -- but it removes the flat-slab appearance at the source.
    """
    gh, gw = gid.shape
    owner = np.full((h, w), -1, np.int16)     # which group won each cell
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    LON, LAT = np.meshgrid(lon, lat)
    T = BS.unit(LON.ravel(), LAT.ravel())
    # low-frequency ridge/basin backdrop for unclaimed ocean, centred near the
    # mid-ocean depth and never as shallow as a shelf
    # INTEGER harmonics only: sin(2.3*lon) does not repeat over 360 degrees, so
    # the backdrop itself carried a step at the antimeridian wherever unclaimed
    # new ocean showed through -- which is most of the Pacific in the future
    # frames, and the other half of the stationary north-south line.
    fx = np.sin(np.radians(LON) * 2.0 + 0.7) + 0.6 * np.sin(np.radians(LON) * 5.0 + 2.1)
    fy = np.sin(np.radians(LAT) * 3.1 + 1.3) + 0.5 * np.cos(np.radians(LAT) * 6.7)
    out = (-4300.0 + 700.0 * fx * fy).astype(float)

    # Rifted margins are not straight lines. The group masks are rasterised
    # PB2002 boundary POLYLINES, so when two groups pull apart the new coastline
    # inherits that surveyed geometry exactly -- which is why the far eastern tip
    # of Eurasia broke away along a ruler-straight edge from the first future
    # keyframe onward. Fray the boundary with fractal noise on the sphere: the
    # direction used for the CLAIM TEST is perturbed by a degree or two while the
    # elevation is still sampled at the true position, so margins gain headlands
    # and embayments and plate interiors are untouched. Evaluated in 3D, so it is
    # seamless across the antimeridian and the poles.
    Tc = T.copy()
    for scale, amp, seed in ((2.6, 0.026, 1301), (6.1, 0.013, 1607), (14.3, 0.006, 1913)):
        Tc = Tc + amp * np.stack([
            PRE.fbm3(T * scale, seed, octaves=2) - 0.5,
            PRE.fbm3(T * scale + 4.7, seed + 31, octaves=2) - 0.5,
            PRE.fbm3(T * scale + 9.1, seed + 61, octaves=2) - 0.5])
    Tc /= np.linalg.norm(Tc, axis=0)

    # present centroid of each group, on the sphere
    cent = {}
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    for i, g in enumerate(GROUPS):
        m = gid == i
        if not m.any():
            continue
        v = BS.unit(GLON[m], GLAT[m]).mean(axis=1)
        v /= np.linalg.norm(v)
        cent[g] = v

    packed = _packed_targets(gid, Zsrc)
    for i, g in enumerate(GROUPS):
        if g not in cent:
            continue
        tl, tb, spin = packed[g]
        s = cent[g]; t = BS.unit(tl, tb)
        Rfull = BS.rodrigues(t, spin) @ BS.rot_from_to(s, t)
        Rm = axis_angle_scale(Rfull, frac)
        S = Rm.T @ T
        slat = np.degrees(np.arcsin(np.clip(S[2], -1, 1)))
        slon = np.degrees(np.arctan2(S[1], S[0]))
        # claim test on the frayed direction; elevation from the true one
        Sc = Rm.T @ Tc
        clat = np.degrees(np.arcsin(np.clip(Sc[2], -1, 1)))
        clon = np.degrees(np.arctan2(Sc[1], Sc[0]))
        gy = np.clip(((90 - clat) / 180 * gh).astype(int), 0, gh - 1)
        # longitude is periodic -- clipping it instead of wrapping smears the
        # column at 180 across the whole height and is half of the stationary
        # north-south line that ran down the Pacific.
        gx = ((clon + 180) / 360 * gw).astype(int) % gw
        claims = gid[gy, gx] == i
        if not claims.any():
            continue
        sy = np.clip(((90 - slat) / 180 * Zsrc.shape[0]).astype(int), 0, Zsrc.shape[0] - 1)
        sx = ((slon + 180) / 360 * Zsrc.shape[1]).astype(int) % Zsrc.shape[1]
        z = np.where(claims, Zsrc[sy, sx], -9999.0).reshape(h, w)
        owner = np.where(z > out, i, owner)
        out = np.maximum(out, z)          # overlap -> collision keeps the high ground

    # COLLISIONAL UPLIFT ALONG THE SUTURES.
    #
    # Rigid rotation has no mechanism to raise a mountain, so land above 2 km was
    # flat across the whole series -- 8.7 to 8.6 Mkm2 from now to +250 Myr -- and
    # the collisional belt Scotese draws through the middle of Pangaea Ultima
    # could not appear anywhere. A supercontinent assembling without building a
    # single range is the one thing the reconstruction is most sure about.
    #
    # Now that the groups are packed to MEET rather than interpenetrate there is
    # a contact to work with: where two different groups' land abuts, crust
    # thickens. The belt is a smoothed indicator of "a different group is nearby",
    # so it is widest where two masses are broadly in contact and absent along a
    # free coast, and it grows with `frac` because an orogen rises over the whole
    # collision rather than appearing at the end.
    #
    # This is a supercontinent-scale statement, not a claim about any particular
    # range: the belts appear where these groups collide, which is where any
    # reconstruction would put them, and the app's card says so.
    if frac > 0.02:
        from scipy.ndimage import gaussian_filter, maximum_filter
        land = out >= 0.0
        own = np.where(land, owner, -1)
        diff = np.zeros((h, w), np.float32)
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            a = np.roll(np.roll(own, dy, 0), dx, 1)
            b = np.roll(np.roll(own, -dy, 0), -dx, 1)
            diff += ((own >= 0) & (a >= 0) & (a != own)).astype(np.float32)
            diff += ((own >= 0) & (b >= 0) & (b != own)).astype(np.float32)
        seed = np.clip(diff, 0.0, 1.0)
        # widen the seed to a belt a few hundred km across, then smooth its edge
        sigma = max(1.0, SUTURE_DEG / (180.0 / h))
        # NOT normalised by its own maximum. Dividing a smoothed 0..1 field by
        # its peak rescales the tails as well, so the belt became a broad plateau
        # of near-1 values and narrowing the kernel changed nothing -- land above
        # 2 km came out at 26 Mkm2 against today's 8.8, a world of mountains. A
        # gaussian of an indicator is already 0..1 and already peaks at 1 where
        # the contact is solid, which is exactly the shape wanted.
        # ...and raised to a power, because a gaussian is broad-shouldered and an
        # orogen is not. At SUTURE_POW = 1 a belt tall enough to make a Himalaya
        # also lifted ten million square kilometres past a kilometre; the power
        # concentrates the same uplift onto the contact and lets the flanks fall
        # away, which is both the right shape and the right area.
        belt = gaussian_filter(maximum_filter(seed, size=3), sigma) ** SUTURE_POW
        out = out + SUTURE_UPLIFT * frac * belt * land
    return out



def handoff_blend(A, B, wq):
    """Cross-fade the real 540 Ma DEM into the authored Precambrian composite.

    Blending elevations in METRES destroys land. Ocean floor is about -4000 m
    and a continental interior only a few hundred, so mixing in even 8 percent
    of "ocean" drowns most land: measured, the world went from 18.6 percent land
    at 540 Ma to 7.5 percent one keyframe later and bottomed out at 4.3 percent
    mid-handoff, before a whole southern continent reappeared out of it. That is
    the "continents flood then a new continent arises" the map showed between
    595 and 545 Ma, and it is an artefact of the cross-fade, not geology.

    Two corrections. Blend in the SIGNED-SQRT domain the shader already
    interpolates keyframes in, which compresses the abyss so a coastline
    survives a partial mix. Then re-level the result so its land fraction is the
    interpolation of the two endpoints' land fractions, instead of collapsing to
    wherever the two happen to agree. The handoff is still a morph between two
    reconstructions -- it cannot be anything else -- but land area now moves
    smoothly from one world to the other.
    """
    if wq <= 0:
        return A
    if wq >= 1:
        return B

    def enc(z):
        return 0.5 + 0.5 * np.sign(z) * np.sqrt(np.clip(np.abs(z) / 8000.0, 0, 1))

    def dec(e):
        s = 2 * e - 1
        return np.sign(s) * s * s * 8000.0

    h, w = A.shape
    wlat = np.cos(np.radians(90 - (np.arange(h) + 0.5) / h * 180))[:, None]
    denom = wlat.sum() * w

    def landfrac(z):
        return float(((z > 0) * wlat).sum() / denom)

    out = dec(enc(A) * (1 - wq) + enc(B) * wq)
    target = landfrac(A) * (1 - wq) + landfrac(B) * wq
    lo, hi = -3000.0, 3000.0
    for _ in range(40):                      # bisect the sea-level shim
        mid = (lo + hi) / 2
        if landfrac(out + mid) < target:
            lo = mid
        else:
            hi = mid
    return out + (lo + hi) / 2


# ------------------------------------------------------------------ main ----
def main():
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    manifest, total = [], 0
    coarse = {}          # age -> motion-grid elevation, for the matching pass

    def dem_for(age):
        near = float(avail[np.argmin(np.abs(avail - age))])
        return read_dem(idx[near])

    # ---- Phanerozoic ----
    _rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    for age in range(0, 541, STEP):
        z = dem_for(age)
        Zhi = resample_dem(z, ELEV_H, ELEV_W)
        # flood the epicontinental seas this grid cannot resolve (see epeiric.py)
        Zhi = EP.carve(Zhi, age, _rec)
        coarse[age] = MO.coarsen(Zhi)
        # Zhi[::-1], not z: the climate solve must see the terrain that is DRAWN.
        # resample_dem returns row 0 = north and compute_fields wants latitude
        # ascending, hence the flip. Only the Phanerozoic path does this -- the
        # future and Precambrian branches build their own climate-resolution
        # grids (gl, lo) with their own eustatic corrections already applied, and
        # substituting the high-res one there would quietly change what those
        # eras solve for.
        m, n = export(age, Zhi, Zhi[::-1], "phan")
        manifest.append(m); total += n
    print(f"Phanerozoic: {len(manifest)} keyframes")

    # ---- Future: plate-warped present DEM ----
    gid = rasterise_groups()
    z0 = dem_for(0)
    Zsrc = resample_dem(z0, 900, 1800)      # north-up source for warping
    nfut = 0
    for age in range(-STEP, -251, -STEP):
        frac = abs(age) / 250.0
        gh = future_grid(frac, gid, Zsrc, ELEV_H, ELEV_W)
        gl = future_grid(frac, gid, Zsrc, CLIM_H, CLIM_W)
        # The future series warps TODAY's terrain, which is referenced to
        # today's sea level, so the era's eustatic level has to be applied by
        # hand. Without this the coastline never moves and low ground such as
        # Florida, Bangladesh and the Netherlands stays dry through a hothouse
        # that has melted every ice sheet. (The Phanerozoic DEMs are already
        # relative to their own contemporaneous sea level; adjusting those too
        # would double-count.)
        sl = sealevel_for(age)
        gh = gh - sl
        gl = gl - sl
        coarse[age] = MO.coarsen(gh)
        m, n = export(age, gh, gl[::-1], "fut")   # export wants lat-ascending
        manifest.append(m); total += n; nfut += 1
    print(f"Future: {nfut} keyframes (plate-warped present DEM)")

    # ---- Precambrian: authored, anchored onto the real 540 Ma map ----
    z540 = dem_for(540)
    A_hi = resample_dem(z540, ELEV_H, ELEV_W)
    A_lo = resample_dem(z540, CLIM_H, CLIM_W)
    npre = 0
    for age in range(540 + STEP, 1001, STEP):
        hi = PRE.precambrian_grid(age, tw=ELEV_W, th=ELEV_H, flood=140.0)
        lo = PRE.precambrian_grid(age, tw=CLIM_W, th=CLIM_H, flood=140.0)
        # ramp from the real 540 Ma reconstruction into the authored one
        wq = float(np.clip((age - 540.0) / 60.0, 0, 1))
        hi = handoff_blend(A_hi, hi, wq)
        lo = handoff_blend(A_lo, lo, wq)
        coarse[age] = MO.coarsen(hi)
        m, n = export(age, hi, lo[::-1], "pre")
        manifest.append(m); total += n; npre += 1
    print(f"Precambrian: {npre} keyframes (anchored to 540 Ma)")

    # ---- motion: match each keyframe's neighbours across a wide baseline ----
    ages = sorted(coarse)
    for rec in manifest:
        a = rec["age"]
        older = min(ages, key=lambda x: abs(x - (a + MO.BASE_MYR)))
        younger = min(ages, key=lambda x: abs(x - (a - MO.BASE_MYR)))
        dt = max(5.0, older - younger)
        vx, vy, cf = MO.displacement(coarse[older], coarse[younger], dt)
        p = os.path.join(OUT, rec["m"])
        MO.encode(vx, vy, cf).save(p, "WEBP", quality=94, method=6)
        total += os.path.getsize(p)
    print(f"motion: {len(manifest)} fields derived")

    manifest.sort(key=lambda m: m["age"])
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"),
              separators=(",", ":"))
    print(f"TOTAL {len(manifest)} keyframes, {total/1e6:.2f} MB of field textures")


if __name__ == "__main__":
    main()
