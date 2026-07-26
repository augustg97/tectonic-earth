"""Seamounts, in the patterns they actually occur in.

The first version of this seeded one uniform population across the whole ocean
and stamped each as a radially symmetric cone. Both halves of that are wrong, and
together they gave the abyss a warty stipple of several thousand identical
mountains -- the opposite of a real chart, where the seamounts are the most
ORGANISED thing on the sea floor.

Real ones come in three populations with quite different behaviour:

  HOTSPOT CHAINS. A plume sits still in the mantle and the plate slides over it,
  so the volcanoes come out as a LINE, ageing away from the plume: an active
  island at one end, then a string of extinct cones subsiding as the crust they
  ride cools, then guyots planed flat by waves, then drowned banks. Hawaii-
  Emperor, Louisville, the Cook-Australs, the Tuamotus, Walvis, Ninetyeast.
  These are the large, conspicuous ones, and they are what makes a real chart
  look organised rather than sprinkled.

  NEAR-RIDGE SEAMOUNTS. Built at or beside the axis by the same volcanism that
  makes the crust, so they crowd onto young sea floor and thin out with age.
  Individually small.

  BACKGROUND. Genuinely sparse. Large tracts of old abyssal plain have nothing.

And none of them is a circle. A seamount is fed along rift zones -- typically two
or three arms radiating from the summit -- so the plan view is lobate and often
strongly elongated, and the flanks carry collapse scars. A perfect circle is the
one outline no volcano has.

WHAT GETS BAKED. The grid cell is 20 km and a 1 km seamount is 14 km across, so
the small population is sub-pixel and stamping it would alias rather than
resolve; ridge-flank bumpiness is the shader's fault-block fabric, not this. What
this field carries is the part the grid can hold: the chains, and the larger
near-ridge cones.
"""
import math

import numpy as np

# --- populations -----------------------------------------------------------
N_PLUMES = 34             # active plumes worldwide; the real count is 40-50
CHAIN_STEP = 1.6          # deg between volcanoes along a track
CHAIN_LEN = 26            # steps: a track a few thousand km long
NEAR_RIDGE_DENS = 0.040   # per square degree on brand-new crust
BACKGROUND_DENS = 0.0022   # per square degree on old abyssal plain

H_MIN = 1150.0            # m: the smallest this grid can resolve
H_MAX = 4300.0
POWER = 1.25              # power-law slope: many small, few large
RADIUS_PER_M = 0.00013    # deg of basal radius per metre (~1:14 flanks)


def _h(*ints):
    """Deterministic 0..1 from integers -- a seamount must be the same mountain
    at every keyframe, not a fresh roll that shimmers as you scrub."""
    x = 0x9E3779B9
    for v in ints:
        x = (x ^ (int(v) * 2654435761)) & 0xFFFFFFFF
        x ^= x >> 15
        x = (x * 2246822519) & 0xFFFFFFFF
    x ^= x >> 13
    return x / 4294967295.0


def _stamp(out, ys, xs, h, w, dpc, plon, plat, hgt, elong, azi_deg, seed):
    """One volcano: lobate, elongated along its rift zones, not a cone.

    Three angular harmonics do most of the work -- a two-armed rift gives the
    strong elongation seen on most large seamounts, and the higher terms break
    the outline up. The whole shape is stretched along `azi_deg`, which for a
    chain volcano is the direction of the chain, because rift zones tend to
    align with the stress field that the plate motion sets up.
    """
    rad = max(hgt * RADIUS_PER_M, dpc * 1.3)
    reach = rad * (1.0 + elong) * 1.5
    coslat = max(math.cos(math.radians(plat)), 0.05)
    row = int((90.0 - plat) / 180.0 * h)
    rr = int(np.ceil(reach / dpc)) + 1
    r0, r1 = max(0, row - rr), min(h, row + rr + 1)
    if r1 <= r0:
        return
    dy = (90.0 - (ys[r0:r1, :1] + 0.5) * dpc) - plat
    dlon = (((xs[r0:r1, :] + 0.5) * dpc - 180.0) - plon + 180.0) % 360.0 - 180.0
    dx = dlon * coslat
    # rotate into the volcano's own frame so the elongation follows its rift
    a = math.radians(azi_deg)
    ca, sa = math.cos(a), math.sin(a)
    ex = dx * ca + dy * sa
    ey = -dx * sa + dy * ca
    ex = ex / (1.0 + elong)                      # stretch along the rift
    d = np.hypot(ex, ey)
    th = np.arctan2(ey, ex)
    p1 = _h(seed, 1) * 6.2831
    p2 = _h(seed, 2) * 6.2831
    p3 = _h(seed, 3) * 6.2831
    warp = (1.0
            + 0.26 * np.cos(2.0 * th + p1)
            + 0.15 * np.cos(3.0 * th + p2)
            + 0.09 * np.cos(5.0 * th + p3))
    cone = np.clip(1.0 - d / np.maximum(rad * warp, 1e-6), 0.0, 1.0)
    if not cone.any():
        return
    prof = cone ** 1.45
    # A flank-collapse scar: one sector of the cone slumped away. Common on big
    # ocean volcanoes and part of why none of them is symmetric.
    if _h(seed, 4) > 0.55:
        sc = math.radians(_h(seed, 5) * 360.0)
        bite = np.cos(th - sc) > (0.55 + 0.3 * _h(seed, 6))
        prof = np.where(bite, prof * 0.45, prof)
    out[r0:r1, :] = np.maximum(out[r0:r1, :], (prof * hgt).astype(np.float32))


def field(age_myr, sea, lat1d, deg_per_cell, u=None, v=None, seed=7, age_of=None):
    """Seamount relief in metres.

    `u`,`v` are the plate-motion direction (the age gradient), which is what
    lets a plume trail a CHAIN rather than a dot: walking that field from a
    fixed plume traces the path the crust took over it.
    """
    h, w = age_myr.shape
    out = np.zeros((h, w), np.float32)
    ys, xs = np.mgrid[0:h, 0:w]
    dpc = deg_per_cell

    def ok(la, lo):
        r = int((90.0 - la) / 180.0 * h)
        c = int((lo + 180.0) / 360.0 * w) % w
        if r < 0 or r >= h:
            return None
        return (r, c) if sea[r, c] else None

    # --- 1. hotspot chains, carried on the plate ---------------------------
    # Positions come from crustage.plume_track, which reconstructs each volcano
    # from the time it was born at the stationary plume to the present target
    # time. The chain therefore MOVES: scrub the timeline and every cone tracks
    # its plate while new ones appear at the plume. Walking outward along the
    # motion field, as this used to, looks similar in a single frame and is
    # quite wrong across time -- the volcanoes stayed pinned to the map while
    # the plate slid underneath them.
    tracks = []
    if age_of is not None:
        try:
            import crustage
            n = 0
            for p in range(N_PLUMES * 4):
                if n >= N_PLUMES:
                    break
                plat = math.degrees(math.asin(_h(seed, p, 11) * 2.0 - 1.0))
                plon = _h(seed, p, 13) * 360.0 - 180.0
                if ok(plat, plon) is None:
                    continue
                n += 1
                tracks.append((p, 0.35 + 0.9 * _h(seed, p, 17),
                               crustage.plume_track(plon, plat, age_of,
                                                    max_age=CHAIN_LEN * 5, step=5)))
        except Exception:
            tracks = []
    for p, vigour, tr in tracks:
        for k, (lo, la, A) in enumerate(tr):
            at = ok(la, lo)
            if at is None:
                continue
            r, c = at
            # The volcano stops being fed the moment it leaves the plume, then
            # subsides with the cooling plate it rides.
            fade = math.exp(-A / 42.0)
            hgt = H_MIN + (H_MAX - H_MIN) * vigour * fade * (0.55 + 0.5 * _h(seed, p, k, 23))
            if hgt <= H_MIN:
                continue
            du = 0.0 if u is None else float(u[r, c])
            dv = 0.0 if v is None else float(v[r, c])
            azi = math.degrees(math.atan2(dv, du)) if (du or dv) else 0.0
            _stamp(out, ys, xs, h, w, dpc, lo, la, hgt,
                   0.55 + 0.7 * _h(seed, p, k, 29), azi, seed * 1000 + p * 50 + k)

    # --- 2. near-ridge and background -------------------------------------
    cell = 1.0
    for j in range(int(180 / cell)):
        la = 90.0 - (j + 0.5) * cell
        coslat = max(math.cos(math.radians(la)), 0.05)
        step = max(1, int(round(1.0 / coslat)))
        for i in range(0, int(360 / cell), step):
            lo = -180.0 + (i + 0.5) * cell
            at = ok(la, lo)
            if at is None:
                continue
            r, c = at
            a = float(age_myr[r, c])
            dens = BACKGROUND_DENS + NEAR_RIDGE_DENS * math.exp(-a / 14.0)
            if _h(seed, i, j, 31) > dens * cell * cell * coslat:
                continue
            uq = _h(seed, i, j, 37)
            hgt = min(H_MIN * (1.0 - uq) ** (-1.0 / POWER), H_MAX)
            _stamp(out, ys, xs, h, w, dpc,
                   lo + (_h(seed, i, j, 41) - 0.5) * cell,
                   la + (_h(seed, i, j, 43) - 0.5) * cell,
                   hgt, 0.15 + 0.55 * _h(seed, i, j, 47),
                   _h(seed, i, j, 53) * 360.0, seed * 7919 + i * 181 + j)
    return out
