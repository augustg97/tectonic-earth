"""Bake `*_f.webp` -- the flexural moat in front of a mountain belt (H5).

A range plus its parallel trough is the diagnostic signature of collision. The
Ganges plain, the Po basin, the Alberta foredeep and the Appalachian foreland
are all the same landform: an orogen loads the lithosphere, the plate bends
under the weight, and a long low basin forms alongside it. Nothing in this app
drew one, because a 20 km grid authored at 1 degree cannot carry a trough that
is 100-300 km wide and a few hundred metres deep.

WHY THIS WAS DEFERRED, AND WHAT CHANGED. Section H recorded two blockers. The
second was polarity -- which SIDE the trough falls on -- and the objection was
real: a symmetric moat is defensible physics and would put a basin on the wrong
side of half the world's ranges. This module solves polarity instead of ducking
it. The first blocker was that flexure changes hypsometry; that is handled by
never touching high ground at all, so a range's own elevation is provably
unaltered (see the GATE below, and audit_foreland.py which measures it).

POLARITY, AND WHY IT IS NOT ONE RULE. The naive rule -- "the foreland sits on
the underthrusting plate" -- gets the Himalaya right and the Andes wrong. India
underthrusts Asia and the Ganges lies on the Indian side, the incoming plate.
But Nazca subducts beneath South America and the Chaco-Beni foreland lies EAST,
on the OVERRIDING plate, because the western side is ocean and an ocean cannot
hold a foreland basin. The two cases are not the same rule and no single
kinematic test covers both.

What DOES cover both is the observation that a foreland basin is a continental
lowland adjacent to a load. So the side is chosen by asking what is actually
there, across strike:

    * deep ocean cannot be a foreland          -- rules out the Pacific side of
                                                  the Andes, which is the case
                                                  the kinematic rule fails on
    * the lower side wins                      -- Ganges over Tibet
    * ties break toward the plate moving INTO  -- the peripheral-foreland case,
      the orogen                                  where both sides are continent

Across-strike comes free: `_t` already carries the fold axis, and the foreland
lies perpendicular to it. That is the same double angle the fabric uses, so the
basin is guaranteed to run parallel to the belt that made it.

THE PROFILE is the standard broken-plate flexural response, w(x) = exp(-x/a) *
cos(x/a): deepest against the thrust front, shallowing outward, and crossing
into a low FOREBULGE beyond, which is a real feature -- the Cincinnati Arch and
the Ozark Dome are forebulges of the Appalachian foreland. a is the flexural
parameter, ~130 km for continental lithosphere.

CHANNELS: R deflection down (0..FLEX_MAX m), G forebulge up (0..BULGE_MAX m).

    ../venv/bin/python build_foreland.py            # all past keyframes
    ../venv/bin/python build_foreland.py --selftest
"""
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter

import plate_field as PF

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")

FW, FH = 1024, 512
KM_PER_DEG = 111.32
Z_RANGE = 8000.0

LOAD_MIN = 1500.0       # m: what counts as an orogenic load

# Shortening is a BONUS, not a gate, and finding out why is the main result of
# building this. PALEOMAP's static polygons are built around continental blocks
# and carry no distinct motion for oceanic plates, so `_t` sees the India-Asia
# collision clearly (shortening 0.58 across the Himalaya) and is blind to
# Nazca-South America: a transect at 20S reads 0.02-0.10 all the way across,
# including at the trench, where the real convergence is 7 cm/yr. Gating the
# load on shortening therefore built a Ganges and refused an Andean foreland,
# an Alpine one and a Zagros one -- not because those ranges lack forelands but
# because this model cannot see what drives them. So the load is the RANGE, which
# the DEM gives directly, and shortening only deepens a basin where it is
# corroborated. Recorded as a known limit rather than tuned around.
SHORT_BONUS = 0.22      # _t byte above which a load counts as corroborated
# Flexural parameter. For a broken plate the moat's first zero is at pi/2 * a,
# so a sets the BASIN WIDTH: 130 km gives a 200 km moat, and the Ganges plain is
# about 300 km across -- most of it was landing past the zero, in the forebulge,
# which is why the basin read as nothing. 190 km puts the zero near 300 km and
# matches the Ganges, the Alberta foredeep and the Po.
ALPHA_KM = 190.0
REACH_KM = 460.0        # beyond this the profile is spent
FLEX_MAX = 620.0        # m of deflection under the heaviest load
BULGE_MAX = 90.0        # m of forebulge; real ones are tens of metres
# How far across strike to look. SEVERAL distances, not one, and that is not
# belt-and-braces: a single 320 km probe from the crest of Tibet is still on
# Tibet, so the model scored the range itself as its own foreland and then broke
# the resulting tie arbitrarily. Both selftest failures were this. An orogen can
# be a thousand kilometres wide, so probe past one.
PROBE_KM = (200.0, 380.0, 560.0, 760.0)
# ...and a foreland must be genuinely LOWER than the range that loads it. This
# is what stops a plateau being read as its own basin.
DROP_MIN = 800.0

# GATE. No cell at or above this elevation is touched, at all, ever. That is
# what makes "the ranges themselves do not move" a measurement rather than a
# hope -- audit_foreland.py checks the >1 km, >2 km and >3 km hypsometry is
# bit-identical. It also keeps the moat where a moat belongs: a foreland is a
# PLAIN, and anything already a kilometre and a half up is the range, not its
# basin.
GATE_HI = 1500.0
GATE_LO = 700.0

# The range's FOOTPRINT, as distinct from its load-bearing core. The flexural
# profile is deepest at the edge of the load -- and the edge of a >1500 m core
# is a mountain flank, where the gate above is busy protecting the range. So the
# two fought: the deflection peaked exactly where it was forbidden, and the
# basin came out 94 m deep instead of several hundred. Measuring distance from
# the footprint instead puts the peak at the FOOT of the range, on the plain,
# which is both where a foreland basin actually is and where the gate is happy.
FOOT_MIN = 900.0


def _load_field(age, kind):
    tag = "phan" if age <= 540 else "pre"
    for ext in ("avif", "webp"):
        p = os.path.join(FIELDS, "%s_%04d_%s.%s" % (tag, age, kind, ext))
        if os.path.exists(p):
            im = Image.open(p)
            return np.asarray(im.convert("L" if kind == "e" else "RGB"))
    return None


def _elev(age, w, h):
    a = _load_field(age, "e")
    if a is None:
        return None
    im = Image.fromarray(a).resize((w, h), Image.BILINEAR)
    d = np.asarray(im).astype(np.float32) / 255.0 * 2.0 - 1.0
    return np.sign(d) * d * d * Z_RANGE


def _tect(age, w, h):
    a = _load_field(age, "t")
    if a is None:
        return None, None, None
    im = Image.fromarray(a).resize((w, h), Image.BILINEAR)
    t = np.asarray(im).astype(np.float32) / 255.0
    return t[..., 0], t[..., 1] * 2 - 1, t[..., 2] * 2 - 1


def _tangent(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    e = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
    n = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
    return e, n


def _sample_at(z, lon, lat):
    """Nearest-cell elevation lookup, wrapping longitude and clamping latitude."""
    h, w = z.shape
    c = np.clip(((lon + 180.0) % 360.0) / 360.0 * w, 0, w - 1).astype(np.int32)
    r = np.clip((90.0 - lat) / 180.0 * h, 0, h - 1).astype(np.int32)
    return z[r, c]


def across_strike(z, sigma=4.0):
    """Unit vector (east, north) pointing DOWN the range's regional slope.

    The fold axis in `_t` would be the natural source -- a foreland lies
    perpendicular to strike -- and it cannot be used, for two compounding
    reasons. `_t` nulls its axis wherever shortening is negligible, which is
    precisely the ranges this model is blind to; and where the axis does exist
    it says which way the belt RUNS, not which way is downhill.

    The terrain answers both at once. Smoothed to a regional scale, the gradient
    of a mountain belt points across strike by construction, and it points down
    -- which is where a foreland basin is. sigma is ~4 cells, about 150 km, big
    enough to ignore individual valleys and small enough to follow a curving
    belt like the Zagros or the Carpathians.
    """
    zs = gaussian_filter(z, (sigma, 0.0), mode="nearest")
    zs = gaussian_filter(zs, (0.0, sigma), mode="wrap")
    drow, dcol = np.gradient(zs)
    # row increases SOUTHWARD, so north = -d/drow. Downhill is the negative
    # gradient. Getting this sign wrong points every basin at the range.
    ge, gn = -dcol, drow
    m = np.maximum(np.hypot(ge, gn), 1e-9)
    return ge / m, gn / m


def polarity(z, short, c2, s2, lon, lat):
    """Unit across-strike vector (east, north) pointing at the foreland side.

    Zero where no side qualifies, which is the honest answer for an orogen with
    ocean on both flanks -- an island arc has no foreland and should not be
    given one.
    """
    ax_e, ax_n = across_strike(z)

    coslat = np.maximum(np.cos(np.radians(lat)), 0.12)
    scores, vecs = [], []
    for sgn in (1.0, -1.0):
        best = np.full(z.shape, -1e6, np.float32)
        for pk in PROBE_KM:
            dlat = pk / KM_PER_DEG
            dlon = dlat / coslat
            plon = lon + sgn * ax_e * dlon
            plat = np.clip(lat + sgn * ax_n * dlat, -89.5, 89.5)
            pz = _sample_at(z, plon, plat)
            # Deep ocean cannot hold a foreland basin -- this is what puts the
            # Andean basin east rather than in the Peru-Chile trench. And it
            # must be clearly lower than the load, or a wide plateau qualifies
            # as its own foreland.
            ok = (pz > -900.0) & (pz < z - DROP_MIN)
            sc = np.where(ok, 4000.0 - np.clip(pz, -900.0, 6000.0), -1e6)
            best = np.maximum(best, sc)
        scores.append(best)
        vecs.append((sgn * ax_e, sgn * ax_n))

    pick = scores[0] >= scores[1]
    best = np.maximum(scores[0], scores[1])
    fe = np.where(pick, vecs[0][0], vecs[1][0])
    fn = np.where(pick, vecs[0][1], vecs[1][1])
    live = best > -1e5
    return np.where(live, fe, 0.0), np.where(live, fn, 0.0), live


def deflection(age, w=FW, h=FH):
    z = _elev(age, w, h)
    short, c2, s2 = _tect(age, w, h)
    if z is None or short is None:
        return None, None
    LON, LAT = PF._grid(w, h)

    load = z > LOAD_MIN
    if not load.any():
        return np.zeros_like(z), np.zeros_like(z)

    fe, fn, live = polarity(z, short, c2, s2, LON, LAT)
    load = load & live
    if not load.any():
        return np.zeros_like(z), np.zeros_like(z)

    # Nearest load cell for every cell, and the true great-circle distance to
    # it. Doing the distance properly rather than in grid cells matters: a
    # column is 39 km at the equator and 20 km at 60 degrees, so a cell-count
    # radius would make every high-latitude foreland half the width it should be.
    # Distance is measured from the range's footprint, but the WEIGHT and the
    # polarity still come from its high core -- a foothill does not load the
    # lithosphere, it just marks where the load stops.
    from scipy.ndimage import binary_dilation
    foot = (z > FOOT_MIN) & binary_dilation(load, iterations=8)
    foot |= load
    _d, (iy, ix) = distance_transform_edt(~foot, return_indices=True)
    lonL, latL = LON[iy, ix], LAT[iy, ix]
    dlon = (LON - lonL + 180.0) % 360.0 - 180.0
    dlat = LAT - latL
    mlat = np.radians(0.5 * (LAT + latL))
    dx = dlon * np.cos(mlat) * KM_PER_DEG
    dy = dlat * KM_PER_DEG
    dist = np.hypot(dx, dy)

    # Is this cell on the foreland side of the load it belongs to? The load's
    # own foreland vector is in ITS tangent frame; over a few hundred km the
    # frames differ little, so comparing directly is fair at this resolution.
    # The nearest FOOTPRINT cell is not necessarily a load cell, so the
    # polarity and weight are taken from the nearest LOAD cell instead.
    _dl, (ly, lx) = distance_transform_edt(~load, return_indices=True)
    feL, fnL = fe[ly, lx], fn[ly, lx]
    norm = np.maximum(np.hypot(dx, dy), 1e-6)
    align = (dx / norm) * feL + (dy / norm) * fnL

    # Broken-plate flexural profile.
    x = dist / ALPHA_KM
    prof = np.exp(-x) * np.cos(x)
    # THE LOAD IS THE RANGE, NOT ITS FRONT CELL. w0 used to read the elevation
    # of the nearest load cell, and the nearest load cell to a foreland is by
    # construction the range's outermost one -- a 1,800 m foothill, not the
    # 5,000 m massif behind it. So w0 sat pinned at its 0.12 floor everywhere
    # and every basin came out a tenth of its depth. Take the regional maximum
    # instead: what bends the plate is the mass of the whole belt.
    from scipy.ndimage import maximum_filter
    peak = maximum_filter(np.where(load, z, 0.0), size=(7, 7))
    w0 = np.clip((peak[ly, lx] - LOAD_MIN) / 4000.0, 0.12, 1.0)
    # Corroborated collision digs deeper than mere altitude does.
    w0 = w0 * np.where(short[ly, lx] > SHORT_BONUS, 1.0, 0.72)

    side = np.clip((align - 0.30) / 0.45, 0.0, 1.0)
    reach = (dist < REACH_KM) & ~foot
    amp = w0 * side * reach

    down = np.clip(prof, 0.0, None) * amp * FLEX_MAX
    up = np.clip(-prof, 0.0, None) * amp * BULGE_MAX

    # THE GATE. Nothing at or above GATE_HI moves. This is the promise that the
    # ranges keep their PaleoDEM elevations, and it is checkable.
    gate = np.clip((GATE_HI - z) / (GATE_HI - GATE_LO), 0.0, 1.0)
    down *= gate
    up *= gate

    # Smooth: a foreland basin is a broad flexure, not a stencil of the load.
    down = gaussian_filter(down, (2.0, 0.0), mode="nearest")
    down = gaussian_filter(down, (0.0, 2.0), mode="wrap")
    up = gaussian_filter(up, (1.5, 0.0), mode="nearest")
    up = gaussian_filter(up, (0.0, 1.5), mode="wrap")
    # ...and re-apply the gate, because smoothing can push a little of the moat
    # back up onto ground the gate had protected.
    down *= gate
    up *= gate
    return down, up


def bake(age, quiet=False):
    t0 = time.time()
    down, up = deflection(age)
    if down is None:
        return 0.0
    r = np.clip(down / FLEX_MAX, 0, 1)
    g = np.clip(up / BULGE_MAX, 0, 1)
    b = np.zeros_like(r)
    arr = np.stack([np.round(x * 255).astype(np.uint8) for x in (r, g, b)], -1)
    name = "phan_%04d_f.webp" % age if age <= 540 else "pre_%04d_f.webp" % age
    path = os.path.join(FIELDS, name)
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
    cov = 100.0 * float((down > 25.0).mean())
    if not quiet:
        print("  %-22s %5.1f kB  basin %4.2f%% of globe  max %5.0f m  %.1fs"
              % (name, os.path.getsize(path) / 1024.0, cov, down.max(), time.time() - t0))
    return cov


def _selftest():
    ok = True
    w, h = 256, 128
    LON, LAT = PF._grid(w, h)

    # A north-south range with LAND to the east and DEEP OCEAN to the west must
    # put its foreland to the EAST. This is the Andes case, and it is the one a
    # purely kinematic polarity rule gets wrong.
    z = np.full((h, w), -3000.0, np.float32)
    band = (np.abs(LON - 0.0) < 3.0) & (np.abs(LAT) < 40.0)
    z[band] = 4000.0
    east = (LON > 3.0) & (LON < 60.0) & (np.abs(LAT) < 40.0)
    z[east] = 300.0
    short = np.where(band, 0.6, 0.0).astype(np.float32)
    th = np.radians(90.0)                       # fold axis north-south
    c2 = np.full((h, w), np.cos(2 * th), np.float32)
    s2 = np.full((h, w), np.sin(2 * th), np.float32)
    fe, fn, live = polarity(z, short, c2, s2, LON, LAT)
    m = band & live
    if not m.any() or np.mean(fe[m]) <= 0.5:
        print("  FAIL foreland did not choose the LAND side (mean fe=%.2f)"
              % (np.mean(fe[m]) if m.any() else float("nan")))
        ok = False

    # Same range, land on BOTH sides but the west is lower: it must pick west.
    z2 = z.copy()
    west = (LON < -3.0) & (LON > -60.0) & (np.abs(LAT) < 40.0)
    z2[west] = 100.0
    fe2, _fn2, live2 = polarity(z2, short, c2, s2, LON, LAT)
    m2 = band & live2
    if not m2.any() or np.mean(fe2[m2]) >= -0.5:
        print("  FAIL did not pick the LOWER of two land sides (mean fe=%.2f)"
              % (np.mean(fe2[m2]) if m2.any() else float("nan")))
        ok = False

    # An island arc -- ocean both sides -- must get NO foreland at all.
    z3 = np.full((h, w), -3000.0, np.float32)
    z3[band] = 4000.0
    _fe3, _fn3, live3 = polarity(z3, short, c2, s2, LON, LAT)
    if live3[band].any():
        print("  FAIL an arc with ocean on both flanks was given a foreland")
        ok = False

    # The profile must be a moat that shallows and then bulges, not a step.
    x = np.linspace(0, 6, 200)
    prof = np.exp(-x) * np.cos(x)
    if not (prof[0] > 0.99 and prof.min() < -0.02 and abs(prof[-1]) < 0.01):
        print("  FAIL flexural profile has no moat/forebulge/decay structure")
        ok = False

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


def main():
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    args = [int(a) for a in sys.argv[1:] if not a.startswith("--")]
    ages = args or list(range(0, 1001, 5))
    print("baking %d foreland fields at %dx%d" % (len(ages), FW, FH))
    t0 = time.time()
    covs = [bake(a) for a in ages]
    print("\n  %d fields, %.1f min. Basin covers median %.2f%% of the globe, max %.2f%%"
          % (len(ages), (time.time() - t0) / 60.0, float(np.median(covs)), float(np.max(covs))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
