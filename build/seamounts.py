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

WHERE THE PLUMES ARE (2026-07-26). They used to be HASHED -- `_h(seed, p, 11)`
for the latitude, 34 of them, re-rolled nowhere and located nowhere. The
mechanism was right and every location was invented, so the most organised
feature of a real ocean was the one thing the map put in the wrong place. They
now come from `hotspots_cat`, which is the 53-plume catalogue in
`Deep Research/modeling/hotspots.py`: Hawaii, Louisville, Reunion, Kerguelen,
Tristan, Galapagos, Iceland, Yellowstone and the rest, at their real coordinates,
each drawn only back to the oldest dated edifice on its own trail.

Three things then fall out of the catalogue rather than needing new machinery:

  ISLANDS, ATOLLS AND GUYOTS. `hotspots_cat.summit_depth(A)` puts an edifice's
  summit at an ABSOLUTE depth set by its own age -- above water for the first
  ~16 Myr, a shallow bank to ~30, a flat-topped guyot for ever after. Height
  above the floor is then just the difference, which is why a young Hawaiian
  volcano on 90 Myr crust comes out 7 km tall and an Emperor guyot on the same
  crust comes out 3.5 km tall with its top 2 km down. One line, no new noise.

  ASEISMIC RIDGES. Ninetyeast, Walvis, Rio Grande, Chagos-Laccadive, Cocos,
  Carnegie, Emperor, Nazca, Greenland-Iceland-Faroe and the rest are not a
  texture problem, they are the same plume trails stamped densely enough to
  merge into a continuous high. `hotspots_cat.ridge_limbs` says which limbs are
  ridges and over what age span, because the difference between a ridge and a
  line of separate cones is plume flux against plate speed -- we have the
  observation and not the model, so use the observation.

  DEEP TIME STAYS MODELLED, AND SAYS SO. The oldest dated trail is ~135 Ma.
  Earth had plumes at 300 Ma and we do not know where, so the hashed population
  survives as the top-up beyond the catalogue's reach: real plumes where the
  record has them, a modelled population where it does not.
"""
import math

import numpy as np

import hotspots_cat

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

# An edifice built on old, already-deep crust has to be tall to reach the
# surface -- Mauna Loa is about 9 km from the abyssal floor to the summit -- but
# a runaway value would punch a mountain through the map, so cap the height a
# single stamp may claim at a shade more than that.
H_CHAIN_MAX = 9500.0
# Along a limb the catalogue calls an aseismic RIDGE, stamp this fraction of a
# basal radius apart. Below ~0.7 consecutive edifices overlap and the running
# maximum welds them into one continuous crest, which is what Ninetyeast is.
RIDGE_OVERLAP = 0.55
# An aseismic ridge never breaks the surface in this system: the word means a
# submarine ridge, and where one of them IS emergent -- Iceland, Trindade, the
# Galapagos, the Maldives -- the PaleoDEM already draws the island.
RIDGE_MIN_DEPTH = 250.0


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


def _stamp(out, ys, xs, h, w, dpc, plon, plat, hgt, elong, azi_deg, seed,
           cap=None, cap_val=None):
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
    if cap is not None and cap_val is not None:
        # The summit's ABSOLUTE elevation, recorded so a cone stamped for the
        # floor depth under its own centre cannot ride up a slope and stand
        # taller than its age allows. Without it a Ninetyeast edifice sized for
        # a 4.7 km floor came out as an island where the ridge flank is 3.7 km
        # down -- a chain of Indian Ocean islands that do not exist.
        cap[r0:r1, :] = np.where(prof > 0.0,
                                 np.maximum(cap[r0:r1, :], cap_val),
                                 cap[r0:r1, :])


_REC = None


def _tracker(age_of):
    """fn(lon, lat, max_age, step) -> [track, ...] in the PALEOMAP frame, or None.

    Returns a LIST of tracks, because a plume sitting on a spreading axis feeds
    both flanks and writes a mirror pair of trails. Falls back to crustage
    (Merdith topologies) if paleo_tracks cannot run, so a bare environment still
    gets chains -- but PALEOMAP is preferred, because a chain has to land in the
    ocean the TERRAIN draws, and the terrain is Scotese.
    """
    global _REC
    if age_of is None:
        return None
    try:
        import paleo_tracks
        if paleo_tracks.available():
            if _REC is None:
                _REC = paleo_tracks.Reconstructor()
            rc = _REC

            def _pm(lo, la, ma, st):
                return [rc.plume_track(lo, la, age_of, max_age=ma, step=st, pid=p)
                        for p in rc.plume_plates(lo, la)]
            return _pm
    except Exception:                                      # noqa: BLE001
        pass
    try:
        import crustage
        return lambda lo, la, ma, st: [crustage.plume_track(lo, la, age_of,
                                                            max_age=ma, step=st)]
    except Exception:                                      # noqa: BLE001
        return None


def _at_age(lon, lat, age):
    """Where a present-day point sat at `age`, or None. Same track the labels use."""
    if _REC is None or age is None:
        return (lon, lat)
    try:
        tr, _ = _REC.track(float(lon), float(lat), max(5, int(age)),
                           step=max(5, int(age)))
    except Exception:                                      # noqa: BLE001
        return None
    return (tr[-1][1], tr[-1][2]) if tr else None


def _densify(tr, dpc):
    """Insert points along a track so consecutive edifices overlap into a ridge.

    An aseismic ridge IS a chain whose volcanoes ran together; the only thing
    separating Ninetyeast from Louisville in this construction is the spacing.
    Interpolating the age too keeps the summit-depth law running smoothly along
    the crest, which is what makes a ridge shoal toward its young end.
    """
    if len(tr) < 2:
        return tr
    out = [tr[0]]
    for (lo0, la0, a0), (lo1, la1, a1) in zip(tr, tr[1:]):
        d0 = summit_h(a0)
        step = max(RIDGE_OVERLAP * max(d0 * RADIUS_PER_M, dpc * 1.3), dpc)
        dlon = ((lo1 - lo0 + 180.0) % 360.0) - 180.0
        gap = math.hypot(dlon * math.cos(math.radians(0.5 * (la0 + la1))), la1 - la0)
        n = int(gap / step)
        for i in range(1, n + 1):
            f = i / (n + 1.0)
            out.append((lo0 + dlon * f, la0 + (la1 - la0) * f, a0 + (a1 - a0) * f))
        out.append((lo1, la1, a1))
    return out


def summit_h(edifice_age):
    """Nominal edifice height above a ridge-crest floor, for sizing only."""
    return max(hotspots_cat.INITIAL_H - hotspots_cat.SUBSIDENCE
               * math.sqrt(max(0.0, edifice_age)), 0.0)


def field(age_myr, sea, lat1d, deg_per_cell, u=None, v=None, seed=7, age_of=None,
          floor=None, hotspot=None):
    """Seamount relief in metres, as (background, chains).

    `u`,`v` are the plate-motion direction (the age gradient). `floor` is the
    sea-floor depth in metres (negative down) that the edifices stand on: an
    edifice's SUMMIT sits at an absolute depth set by its own age, so its height
    is the distance from that summit down to whatever floor is actually there.
    Without it a Hawaiian volcano on 90 Myr crust would be as short as one on
    fresh crust and would never break the surface.

    `hotspot` overrides the catalogue (a list of objects with .lon/.lat/.name/
    .started); the default is the real one. Passing [] gives the old
    all-modelled behaviour.

    TWO ARRAYS COME BACK, and the split matters. The background population is
    procedural and must stay under the anti-breach cap in seafloor.py -- noise
    that reaches the surface paints turquoise flecks across the open abyss. The
    catalogued chains are named volcanoes at real coordinates, and their young
    ends are SUPPOSED to be islands.
    """
    h, w = age_myr.shape
    out = np.zeros((h, w), np.float32)
    chain = np.zeros((h, w), np.float32)
    cap = np.full((h, w), -1e9, np.float32)
    ys, xs = np.mgrid[0:h, 0:w]
    dpc = deg_per_cell

    def ok(la, lo):
        r = int((90.0 - la) / 180.0 * h)
        c = int((lo + 180.0) / 360.0 * w) % w
        if r < 0 or r >= h:
            return None
        return (r, c) if sea[r, c] else None

    # --- 1. hotspot chains, carried on the plate ---------------------------
    # Each volcano is reconstructed from the time it was born AT THE STATIONARY
    # PLUME forward to the target age. The chain therefore MOVES: scrub the
    # timeline and every cone tracks its plate while new ones appear at the
    # plume. Walking outward along the motion field, as this once did, looks
    # similar in a single frame and is quite wrong across time -- the volcanoes
    # stayed pinned to the map while the plate slid underneath them.
    track_fn = _tracker(age_of)
    plumes = []          # (tag, lon, lat, vigour, max_age, ridge_spans)
    if track_fn is not None:
        cat = ([] if (age_of is not None and age_of < 0) else
               hotspots_cat.active(age_of) if hotspot is None else list(hotspot))
        for i, hs in enumerate(cat):
            if ok(hs.lat, hs.lon) is None:
                continue                     # the plume is under a continent now
            span = CHAIN_LEN * 5
            if hs.started is not None:
                span = min(span, max(5.0, hs.started - age_of))
            limbs = hotspots_cat.ridge_limbs(hs.name)
            plumes.append((f"c{i}", hs.lon, hs.lat, 1.0, span, limbs))
        # Top up to a plausible worldwide count with MODELLED plumes wherever
        # the catalogue has run out -- which past ~135 Ma is everywhere.
        need = max(0, N_PLUMES - len(plumes))
        n = 0
        for p in range(N_PLUMES * 4):
            if n >= need:
                break
            plat = math.degrees(math.asin(_h(seed, p, 11) * 2.0 - 1.0))
            plon = _h(seed, p, 13) * 360.0 - 180.0
            if ok(plat, plon) is None:
                continue
            n += 1
            plumes.append((f"m{p}", plon, plat, 0.35 + 0.9 * _h(seed, p, 17),
                           CHAIN_LEN * 5, []))

    # --- 1a. named aseismic ridges, from their surveyed trace --------------
    # A ridge whose present-day position is known is entered where the survey
    # puts it and carried back on its own plate, rather than re-derived from the
    # plume -- because several of them were written on a plate the plume no
    # longer touches, and no reconstruction from the plume's present position can
    # reach them. See hotspots_cat.RIDGE_TRACE.
    # THE FUTURE IS NOT EXTRAPOLATED, and this is the one place it nearly was.
    # A plume track to a negative time asks pyGPlates for a rotation past the end
    # of the model, and the trace path is worse: every trace point passes the
    # `f >= age_of` test at a negative age, `_at_age` clamps the reconstruction
    # to 5 Ma, and the age arithmetic turns a 0 Ma ridge point into a 100 Myr
    # edifice -- so the whole catalogue would have been stamped at its
    # near-present position, two kilometres down, on a map where the plates have
    # since moved. Measured before it shipped: 2,602 cells at +100 Myr.
    # Past 0 Ma the modelled population carries the ocean alone, which is exactly
    # what the old hashed code did here and what oceanage does for crustal age.
    future = age_of is not None and age_of < 0
    if track_fn is not None and hotspot is None and not future:
        for name, tr0 in ((n, hotspots_cat.ridge_trace(n))
                          for n in hotspots_cat.RIDGE_TRACE):
            live = [(lo, la, f - age_of) for lo, la, f in tr0 if f >= age_of]
            if len(live) < 2:
                continue                     # none of it had formed yet
            here = []
            for lo, la, A in live:
                p = _at_age(lo, la, age_of)
                if p is not None:
                    here.append((p[0], p[1], A))
            for lo, la, A in _densify(here, dpc):
                at = ok(la, lo)
                if at is None:
                    continue
                r, c = at
                # An ASEISMIC RIDGE is submarine by definition -- that is what
                # the word means. Where one of these does break the surface
                # (Iceland, Trindade, the Galapagos, the Maldives) the PaleoDEM
                # already carries the island, so the survey has already answered
                # and the law must not overrule it with a second one.
                summit = max(hotspots_cat.summit_depth(A), RIDGE_MIN_DEPTH)
                hgt = summit_h(A) if floor is None else -summit - float(floor[r, c])
                hgt = min(hgt, H_CHAIN_MAX)
                if hgt <= 250.0:
                    continue
                sd = (abs(hash(name)) % 100000) + int(A)
                _stamp(chain, ys, xs, h, w, dpc, lo, la, hgt,
                       1.1 + 0.5 * _h(sd, 29), 0.0, sd, cap, -summit)

    traced = set(hotspots_cat.RIDGE_TRACE)
    for tag, plon, plat, vigour, span, limbs in plumes:
        try:
            trails = track_fn(plon, plat, int(span), 5) or []
        except Exception:                                  # noqa: BLE001
            continue
        modelled = tag[0] == "m"
        # Age spans already drawn from a survey must not be drawn a second time
        # from the model: Hawaii's plume track and the Emperor trace disagree by
        # 16 degrees at the old end, and drawing both gives two Emperor chains.
        done = [(old, young) for nm, old, young in limbs if nm in traced]
        segs = []
        for ti, tr in enumerate(trails):
            if not tr:
                continue
            # A limb the catalogue calls an aseismic ridge but has no trace for
            # is stamped densely enough to merge; everything else stays a line of
            # separate cones. Limb age windows apply to every trail this plume
            # writes: a mirror pair such as Walvis / Rio Grande shares one plume
            # and one start, and the catalogue does not say which flank each span
            # is on, so the union slightly over-draws the shorter limb rather
            # than dropping it.
            for nm, old, young in limbs:
                if nm in traced:
                    continue
                seg = [q for q in tr if young <= q[2] + age_of <= old]
                if len(seg) > 1:
                    segs.append((_densify(seg, dpc), True, ti))
            rest = [q for q in tr
                    if not any(y <= q[2] + age_of <= o for o, y in done)]
            if rest:
                segs.append((rest, False, ti))
        for pts, dense, ti in segs:
            for k, (lo, la, A) in enumerate(pts):
                at = ok(la, lo)
                if at is None:
                    continue
                r, c = at
                if modelled:
                    # No catalogue entry: keep the old height model, which is a
                    # plume that fades as its volcano leaves it.
                    hgt = (H_MIN + (H_MAX - H_MIN) * vigour * math.exp(-A / 42.0)
                           * (0.55 + 0.5 * _h(seed, k, 23)))
                    if hgt <= H_MIN:
                        continue
                else:
                    # Catalogued: the summit's depth is set by the edifice's own
                    # age, so the height is however far that is above the floor.
                    summit = hotspots_cat.summit_depth(A)
                    if floor is None:
                        hgt = summit_h(A)
                    else:
                        hgt = -summit - float(floor[r, c])
                    hgt = min(hgt, H_CHAIN_MAX)
                    if hgt <= 250.0:
                        continue
                # Elongate along the CHAIN, which is where the rift zones lie.
                if k + 1 < len(pts):
                    dlo = ((pts[k + 1][0] - lo + 180.0) % 360.0) - 180.0
                    dla = pts[k + 1][1] - la
                elif k:
                    dlo = ((lo - pts[k - 1][0] + 180.0) % 360.0) - 180.0
                    dla = la - pts[k - 1][1]
                else:
                    dlo = 0.0 if u is None else float(u[r, c])
                    dla = 0.0 if v is None else float(v[r, c])
                azi = math.degrees(math.atan2(dla, dlo)) if (dlo or dla) else 0.0
                sd = (abs(hash(tag)) % 100000) + ti * 7919 + k
                _stamp(chain if not modelled else out, ys, xs, h, w, dpc, lo, la,
                       hgt, (0.9 if dense else 0.55) + 0.7 * _h(sd, 29), azi, sd,
                       None if modelled else cap,
                       None if modelled else -summit)

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

    # Hold every catalogued summit at the elevation its own age says, on any
    # slope. The stamp is sized from the floor under its centre, so on a ridge
    # flank the same cone would otherwise stand hundreds of metres higher on the
    # shallow side -- which is how a submarine ridge grows islands.
    if floor is not None:
        known = cap > -1e8
        chain = np.where(known,
                         np.minimum(chain, np.maximum(cap - floor, 0.0)),
                         chain).astype(np.float32)
    return out, chain
