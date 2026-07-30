"""Give the ocean floor real, evolving structure -- and put the plateaus back.

The ocean floor was a flat synthetic depth at every age but the present, so the
abyss read as a dead sheet however much procedural texture the shader laid over
it. That texture was static: it did not rift, spread or subduct with the rest
of the world. This bakes STRUCTURE into the elevation field itself, per
keyframe, so it travels and changes like the continents do.

Two things are added, both into the shipped `_e` elevation texture so they run
through the ordinary terrain shader and evolve because they are regenerated
every keyframe:

  1. AGE-GRADED ABYSS. Sea floor deepens as it ages away from a spreading
     ridge -- the half-space cooling law, depth ~ 2600 + 350*sqrt(age_Myr).
     There is no crustal-age grid for deep time, so age is inferred from the
     motion field's DIVERGENCE: a ridge is where crust pulls apart, so distance
     from the nearest divergent line is a proxy for age. Ridges come out
     shallow and banded, the abyssal plains deep and smooth, with ridge-parallel
     abyssal-hill fabric and transform-fault fracture zones cutting across.

  2. OCEANIC PLATEAUS AND MICROCONTINENTS. Kerguelen, Ontong Java, the
     Seychelles, Mauritia, Argoland and the rest are real crustal highs the
     20 km DEM does not resolve. Each is seeded from present-day anchors,
     back-advected on the plate rotations, with an elevation curve that carries
     it from emergent land, through a shallow drowned bank, to a deep old
     plateau -- so Kerguelen is an ISLAND in the Cretaceous and a pale plateau
     on the sea floor now, and you can watch it drown.

Everything is applied ONLY to ocean (z < 0) except where a plateau is authored
to stand above water, and a plateau can only ever RAISE the floor, never carve
a hole in a continent.

Wired into build_fields.py's export and rerender_ages.py, after epeiric.carve.
"""
import math

import numpy as np

# EVERY SPATIAL FILTER BELOW IS IN CELLS, and deg_per_cell = 180/h, so a radius
# written here means one thing at 1024 rows and half as much ground at 2048.
# When the elevation grid doubled in July 2026 all of them had to double with
# it, because each is a claim about the WORLD -- a fracture zone is 0.26 deg
# wide, a turbidite apron 5 deg, a continent more than 3 deg across -- and not a
# claim about the raster. The exception is render.smooth_bathymetry, whose whole
# job is to band-limit to what the grid can carry: that one is correctly a
# function of the raster and gets FINER as the raster does.
# --- AGE-DEPTH: GDH1, NOT PURE HALF-SPACE COOLING -------------------------
# Half-space cooling has the floor deepening as sqrt(age) for ever. It does not.
# Past ~80 Myr the observed sea floor FLATTENS, because a plate loses heat from
# below as well as from the top and settles towards a steady thickness.
#
# Pure sqrt reaches 6.9 km at 150 Myr -- deeper than almost anywhere real -- so
# the old code clipped it at MAX_ABYSS. A clip is not a flattening. It made every
# piece of crust older than 97 Myr EXACTLY 6000 m: measured on the present-day
# age grid, 34.2% of the sea floor, a third of the ocean rendered as a plateau
# with no depth gradient anywhere in it, across the whole old western Pacific and
# the old North Atlantic. Abyssal hills then had to carry relief that the
# large-scale field had flattened out.
#
# GDH1 (Stein & Stein 1992, Nature 359, 123) is the standard plate model and
# gives the flattening directly, in two branches that meet at 20 Myr:
#     t <  20 Myr   d = 2600 + 365*sqrt(t)
#     t >= 20 Myr   d = 5651 - 2473*exp(-0.0278*t)
# They agree to 0.4 m at the join. Old crust now settles onto a real asymptote of
# 5651 m instead of a clip, so 150 Myr crust comes up 387 m and, more to the
# point, 100 Myr and 180 Myr crust are no longer the same depth.
RIDGE_DEPTH = 2600.0        # m: crest of a mid-ocean ridge
DEPTH_PER_SQRT_MYR = 350.0  # m per sqrt(Myr): the old law, kept for reference
MAX_ABYSS = 6000.0          # a backstop now, not the shape of the old ocean
GDH1_A = 365.0              # m per sqrt(Myr) on the young branch
GDH1_D0 = 5651.0            # m: asymptotic plate depth
GDH1_DD = 2473.0            # m: the amplitude that decays away
GDH1_K = 0.0278             # per Myr
GDH1_T = 20.0               # Myr: where the two branches meet
# How far to smooth the crustal age BEFORE it sets depth. Chosen by
# measurement: 0 deg leaves 1,061 m cliffs at plate boundaries, 0.9 leaves
# 237, 1.9 leaves 130, and 3.3 brings it to ~90 m per 25 km cell, which is
# what a real abyssal plain does. Only the depth term uses it.
AGE_DEPTH_SMOOTH_DEG = 3.3


def depth_from_age(age_myr):
    """Depth below sea level in metres, POSITIVE DOWN, from crustal age. GDH1."""
    t = np.maximum(np.asarray(age_myr, dtype=np.float64), 0.0)
    young = RIDGE_DEPTH + GDH1_A * np.sqrt(t)
    old = GDH1_D0 - GDH1_DD * np.exp(-GDH1_K * t)
    return np.where(t < GDH1_T, young, old)
# Half-spreading rate. Real ridges run 10-80 mm/yr; 30 mm/yr (= 30 km/Myr) is a
# fair global mean and puts the oldest surviving crust near 180 Myr, which is
# what the ocean basins actually show.
SPREAD_KM_PER_MYR = 30.0
MAX_CRUST_AGE = 190.0       # Myr: older than this and it has been subducted

# --- ACROSS-RIDGE COORDINATE: COMPANDING ----------------------------------
# The across-ridge coordinate ships as ONE 8-bit channel, and the shader keys a
# periodic fault set to it -- so the quantisation step of that channel is the
# finest sea-floor fabric that can exist anywhere in the app. Stored linearly
# over 75 degrees the step is 0.29 deg, which is COARSER than the 0.176 deg
# texel: the field arrives as a staircase of flat terraces, and keying anything
# periodic to it draws the terrace contours instead of the fabric.
#
# A 16-bit channel is the textbook fix and it is not affordable here. Measured
# over the 251 keyframes: the extra byte is a sawtooth with a ~1.7-texel period,
# i.e. incompressible, so the field can no longer be stored lossily -- 224 MB
# for a long-period sawtooth encoding, 320 MB for a straight hi/lo split, and
# even a LOSSLESS three-channel field with no extra precision at all is 124 MB,
# against 23 MB today and 94 MB for every field in the app combined.
#
# Companding buys the precision for nothing. Store log(1 + d/D0) rather than d:
# the step becomes proportional to (D0 + d), so it is 0.033 deg at the axis --
# 8.7x finer than before, and five times finer than a texel -- widening to about
# a degree in the far field. That gradient is not a compromise, it is the
# physics: abyssal-hill fabric is cut at the axis and is progressively mantled
# by pelagic sediment as the crust ages away from it, so there is less and less
# fine structure out there to resolve. Precision is spent exactly where the sea
# floor keeps its detail.
CO_D0 = 2.5                 # deg: scale over which precision stays near-constant
# Full scale. This used to be 75 deg, which is how far the far side of
# Panthalassa sits from the nearest ridge the model resolves -- the right number
# when the coordinate was DISTANCE. It is the wrong number now that it is AGE:
# ocean crust does not survive past ~190 Myr, and 190 Myr at 30 km/Myr is 51.3
# deg of spreading, so a tenth of the coordinate's range could never occur and
# the precision spent on it was wasted. Must stay in step with CO_K in the
# shader; changing it changes the meaning of every shipped _o field.
CO_MAX = 52.0
CO_K = math.log(1.0 + CO_MAX / CO_D0)


def compand(dist_deg):
    """Degrees from the ridge axis -> the 0..1 coordinate that ships in R."""
    return np.log1p(np.clip(dist_deg, 0.0, CO_MAX) / CO_D0) / CO_K


_PLATES_CACHE = None
_GEOM_CACHE = {}


def _load_plates():
    """The resolved plate topologies, once. Boundaries are already classified
    into ridge / trench / transform by build_plates_gplates.py, straight from the
    Merdith model's own feature types -- so this is the reconstruction's opinion
    of where crust was being made and destroyed, not an inference."""
    global _PLATES_CACHE
    if _PLATES_CACHE is None:
        import json, os
        for p in ("../web/plates_time.json", "web/plates_time.json"):
            if os.path.exists(p):
                with open(p) as f:
                    _PLATES_CACHE = json.load(f)
                break
        else:
            _PLATES_CACHE = False
    return _PLATES_CACHE or None


def _chaikin(poly, rounds=2):
    """Round off a polyline's corners (Chaikin). The resolved topologies are
    stored as coarse polylines, so a trench drawn straight from them shows the
    model's own vertices as angular kinks -- and a trench with corners in it is
    the sort of ruled-with-a-straightedge feature that gives the whole sea floor
    away. Real arcs curve continuously. Cheap, and purely cosmetic."""
    if len(poly) < 3:
        return poly
    p = [list(q) for q in poly]
    for _ in range(rounds):
        out = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            dlon = (b[0] - a[0] + 180.0) % 360.0 - 180.0
            if abs(dlon) > 60.0:          # antimeridian jump: leave it alone
                out.append(b)
                continue
            out.append([a[0] + dlon * 0.25, a[1] * 0.75 + b[1] * 0.25])
            out.append([a[0] + dlon * 0.75, a[1] * 0.25 + b[1] * 0.75])
        out.append(p[-1])
        p = out
    return p


def _densify(polys, step_deg=0.35, smooth=True):
    """Polylines -> 3D unit vectors, resampled fine enough that nearest-VERTEX
    distance is a good stand-in for nearest-SEGMENT distance.

    `smooth` rounds the corners, which is right for a TRENCH (a real arc curves
    continuously and the model's own vertices should not show as kinks) and
    WRONG for a RIDGE: a spreading centre is a staircase of straight segments
    stepped by transform faults, and rounding that off is rounding off the very
    feature -- the ridge-transform geometry -- that makes a spreading system
    recognisable on a chart.
    """
    pts, ids = [], []
    if smooth:
        polys = [_chaikin(p) for p in polys]
    for i, poly in enumerate(polys):
        prev = None
        for lon, lat in poly:
            if prev is not None:
                dlon = (lon - prev[0] + 180.0) % 360.0 - 180.0
                d = math.hypot(dlon * math.cos(math.radians((lat + prev[1]) * 0.5)),
                               lat - prev[1])
                n = max(1, int(d / step_deg))
                for k in range(1, n):
                    t = k / n
                    pts.append((prev[0] + dlon * t, prev[1] + (lat - prev[1]) * t))
                    ids.append(i)
            pts.append((lon, lat)); ids.append(i)
            prev = (lon, lat)
    if not pts:
        return None, None
    a = np.radians(np.asarray(pts, np.float64))
    lo, la = a[:, 0], a[:, 1]
    xyz = np.stack([np.cos(la) * np.cos(lo), np.sin(la), np.cos(la) * np.sin(lo)], 1)
    return xyz, np.asarray(ids, np.int32)


def _sphere_distance(xyz, ids, h, w):
    """Great-circle distance (degrees) from every grid cell to the nearest of
    `xyz`, plus which polyline that was. Done as a 3D nearest-neighbour query on
    the unit sphere, so it is correct AT THE POLES -- a 2D distance transform on
    a lat/lon raster is not, because a degree of longitude is not a degree of
    ground."""
    from scipy.spatial import cKDTree
    lat = np.radians(90.0 - (np.arange(h) + 0.5) / h * 180.0)
    lon = np.radians((np.arange(w) + 0.5) / w * 360.0 - 180.0)
    clat = np.cos(lat)[:, None]
    gx = (clat * np.cos(lon)[None, :]).ravel()
    gy = np.repeat(np.sin(lat), w)
    gz = (clat * np.sin(lon)[None, :]).ravel()
    d, i = cKDTree(xyz).query(np.stack([gx, gy, gz], 1), k=1)
    ang = np.degrees(2.0 * np.arcsin(np.clip(d * 0.5, 0.0, 1.0)))
    return ang.reshape(h, w).astype(np.float32), ids[i].reshape(h, w)


def _hashf(i, salt):
    """Deterministic 0..1 from an integer cell index.

    Must not be `random`: the offsets have to depend only on WHERE along the
    axis a cell falls, not on the order arcs happened to be joined in, or a
    chain that gains a vertex at the next keyframe would re-roll its whole
    network and the fracture zones would shimmer between frames.
    """
    x = (int(i) * 2654435761 + int(salt) * 40503) & 0xFFFFFFFF
    x ^= x >> 15
    x = (x * 2246822519) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 3266489917) & 0xFFFFFFFF
    x ^= x >> 16
    return x / 4294967295.0


# ORDERS OF RIDGE SEGMENTATION. A spreading centre is not segmented at one
# scale, it is segmented at every scale, and that is precisely why a real chart
# shows a ridge as a complex fractal range rather than the broad straight line
# a single-scale model draws. Marine geology names the hierarchy:
#
#   first order   ridge-transform, 100s of km, offsets 10s-100s of km. These
#                 are the discontinuities whose wakes are the fracture zones.
#   second order  overlapping spreading centres, 30-100 km, smaller offsets.
#                 The main fracture-zone family comes off these.
#   third order   non-transform offsets and devals -- the axis bends rather
#                 than steps, so no fracture zone trails from them.
#   fourth order  axial crenulation at the scale of individual volcanoes.
#
# Amplitudes are held at a constant ~0.18 of segment length across all four,
# which is what makes the result self-similar -- a genuine fractal axis over
# 1.5 decades rather than a straight line with one wiggle imposed on it.
_ORDERS = (
    #  seg_deg  jog_deg  breaks (i.e. leaves a transform gap and a new segment id)
    (7.00,     1.250,   True),
    (2.00,     0.400,   True),
    (0.65,     0.115,   False),
    (0.22,     0.038,   False),
)


def _fractal_offset(s, salt):
    """Sideways offset of the axis, in degrees, at arc length s along a chain.

    Sums the four orders above. The two that break step (piecewise constant --
    a transform IS a discontinuity); the two that do not bend smoothly, because
    a third-order offset is a flexure of the axis, not a fault.
    """
    o = 0.0
    for li, (seg, jog, brk) in enumerate(_ORDERS):
        t = s / seg
        c = int(math.floor(t))
        a = (_hashf(c, salt + li * 977) - 0.5) * 2.0 * jog
        if brk:
            o += a
        else:
            f = t - c
            f = f * f * (3.0 - 2.0 * f)
            b = (_hashf(c + 1, salt + li * 977) - 0.5) * 2.0 * jog
            o += a + (b - a) * f
    return o


def _cell(s, li):
    return int(math.floor(s / _ORDERS[li][0]))


def _walk(chain, step_deg):
    """Resample a lon/lat chain at a fixed arc step, carrying arc length."""
    pts = [(chain[0][0], chain[0][1], 0.0)]
    s = 0.0
    for q in chain[1:]:
        p = pts[-1]
        dlon = (q[0] - p[0] + 180.0) % 360.0 - 180.0
        clat = max(math.cos(math.radians((q[1] + p[1]) * 0.5)), 0.05)
        d = math.hypot(dlon * clat, q[1] - p[1])
        if d < 1e-9:
            continue
        n = max(1, int(d / step_deg))
        for k in range(1, n + 1):
            f = k / float(n)
            pts.append((p[0] + dlon * f, p[1] + (q[1] - p[1]) * f, s + d * f))
        s += d
    return pts


def _ridge_network(polys, seed=17):
    """Turn the model's fragmentary ridge arcs into a CONNECTED, SEGMENTED
    spreading network -- the structural change that gives the sea floor crisp
    axial lines and real fracture zones.

    The reconstruction resolves only a dozen or so ridge arcs in deep time, and
    interpolating distance to that sparse set can only ever produce broad
    smooth swells: no axis you can trace, and no transforms. A real spreading
    system is one continuous network of SHORT segments -- 50-200 km each -- every
    one offset from its neighbour by a transform fault, marching across the
    basin in a staircase. That segmentation sits far below anything the plate
    model carries, but it IS the structure that makes a ridge legible, and every
    fracture zone in the ocean is the frozen wake of one of those offsets.

    So synthesise it, constrained by the real arcs rather than invented from
    nothing:
      1. join arcs whose endpoints nearly meet, so the system is continuous;
      2. walk each chain and displace it sideways by a FRACTAL offset summed
         over four orders of segmentation (see _ORDERS);
      3. cut the chain at the two orders that step, leaving the transform gap.

    Offsetting at four self-similar scales rather than one is what turns the
    axis from a broad straight line into a complex range: the first order rules
    the basin-wide staircase, and each finer order roughens the one above it in
    the same proportion, so the trace has structure at every scale you can zoom
    to. The offsets come from a positional hash, so a given age always produces
    the same network and it does not shimmer between frames.

    Returns polylines plus one id PER SEGMENT. That id is what finally makes
    fracture zones work: with hundreds of segments instead of thirteen, the
    boundaries of the nearest-segment partition stop being continent-length
    Voronoi walls and become exactly what they should be -- a dense family of
    flowline-parallel traces, one running out from every transform.
    """
    # --- 1. join arcs into chains ---------------------------------------
    arcs = [list(p) for p in polys if len(p) > 1]
    chains = []
    while arcs:
        cur = arcs.pop(0)
        joined = True
        while joined and arcs:
            joined = False
            for i, a in enumerate(arcs):
                for endA, endB, rev in ((cur[-1], a[0], False), (cur[-1], a[-1], True),
                                        (cur[0], a[-1], None), (cur[0], a[0], "revcur")):
                    dlon = (endB[0] - endA[0] + 180.0) % 360.0 - 180.0
                    dd = math.hypot(dlon * math.cos(math.radians(endA[1])), endB[1] - endA[1])
                    if dd < 6.0:
                        seg = a[::-1] if rev is True else a
                        if rev is None:
                            cur = a + cur
                        elif rev == "revcur":
                            cur = a[::-1] + cur
                        else:
                            cur = cur + seg
                        arcs.pop(i); joined = True; break
                if joined:
                    break
        chains.append(cur)

    # --- 2 & 3. displace by the fractal offset, cut at the transforms ----
    step = _ORDERS[-1][0]
    out = []
    for ci, chain in enumerate(chains):
        pts = _walk(chain, step)
        if len(pts) < 3:
            continue
        # The salt must depend on WHERE the chain is, not on its index in a list
        # whose order changes as arcs appear and vanish -- otherwise the whole
        # network re-rolls between keyframes. Quantised so it is stable under
        # the small drift of a chain that persists.
        salt = int((round(pts[0][0] / 8.0) * 131 + round(pts[0][1] / 8.0) * 17
                    + seed) & 0x7FFFFFFF)
        run = []
        prev_c = (_cell(pts[0][2], 0), _cell(pts[0][2], 1))
        for i, (lon, lat, s) in enumerate(pts):
            j = pts[min(i + 1, len(pts) - 1)]
            k = pts[max(i - 1, 0)]
            dlon = (j[0] - k[0] + 180.0) % 360.0 - 180.0
            clat = max(math.cos(math.radians(lat)), 0.05)
            L = math.hypot(dlon * clat, j[1] - k[1]) + 1e-9
            nx, ny = -(j[1] - k[1]) / L, (dlon * clat) / L   # unit normal, tangent plane
            o = _fractal_offset(s, salt)
            cur_c = (_cell(s, 0), _cell(s, 1))
            if cur_c != prev_c:                              # a transform: cut here
                if len(run) > 1:
                    out.append(run)
                run = []
                prev_c = cur_c
            run.append([lon + nx * o / clat, lat + ny * o])
        if len(run) > 1:
            out.append(run)
    return out


def _ridge_geometry(age, h=1024, w=2048):
    """Ridge-distance / segment-id / trench-distance fields for this age.

    Computed at half resolution and upsampled: these are smooth, basin-scale
    fields, so the detail costs nothing and the nearest-neighbour query stays
    fast enough to run over every keyframe.
    """
    key = round(float(age))
    if key in _GEOM_CACHE:
        return _GEOM_CACHE[key]
    d = _load_plates()
    if not d:
        _GEOM_CACHE[key] = None
        return None
    ages = sorted(int(k) for k in d.keys())
    near = min(ages, key=lambda a: abs(a - key))
    frame = d[str(near)]
    ridge = [b["p"] for b in frame.get("b", []) if b.get("c") == "ridge" and len(b.get("p", [])) > 1]
    trench = [b["p"] for b in frame.get("b", []) if b.get("c") == "trench" and len(b.get("p", [])) > 1]

    # Synthesise the connected, transform-offset spreading network from the
    # model's arcs, then measure distance to THAT. See _ridge_network.
    ridge = _ridge_network(ridge)
    rxyz, rids = _densify(ridge, step_deg=0.22, smooth=False)
    if rxyz is None or len(rxyz) < 8:
        _GEOM_CACHE[key] = None
        return None
    rdist, rid = _sphere_distance(rxyz, rids, h, w)

    # DISTANCE TO THE SEGMENT ENDS as well as to the axis. A spreading segment
    # is not uniform along its length: it is magmatically fat in the middle and
    # starved at the ends, so the axial valley shoals toward the segment centre
    # and drops into a NODAL BASIN a kilometre deeper at each end, against the
    # transform. Those basins and the bulges between them are the most legible
    # thing about a real ridge at chart scale, and with only an axis distance
    # the ridge could only ever be a uniform ribbon.
    ends = [p for run in ridge for p in (run[0], run[-1])]
    edist = None
    if len(ends) >= 4:
        exyz, eids = _densify([[p, p] for p in ends], step_deg=9.0, smooth=False)
        if exyz is not None and len(exyz) >= 4:
            edist, _ = _sphere_distance(exyz, eids, h, w)

    tdist = None
    txyz, tids = _densify(trench)
    if txyz is not None and len(txyz) >= 8:
        tdist, _ = _sphere_distance(txyz, tids, h, w)

    out = {"ridge": (rdist, rid, len(rxyz) >= 200), "trench": tdist, "ends": edist}
    _GEOM_CACHE[key] = out
    return out


def _upsample(a, h, w, order=1):
    from scipy.ndimage import zoom
    if a.shape == (h, w):
        return a
    return zoom(a, (h / a.shape[0], w / a.shape[1]), order=order)


def _edt_wrap(mask):
    """distance_transform_edt, but longitude is PERIODIC.

    The plain transform treats column 0 and column w-1 as maximally far apart,
    so any feature crossing the antimeridian gets cut in half and a false
    distance ridge runs down the join. Pad a quarter-width off each end, do the
    transform, crop back. (This pipeline has had to relearn that longitude wraps
    more than once -- see the seam notes in the project memory.)
    """
    from scipy.ndimage import distance_transform_edt
    w = mask.shape[1]
    pad = w // 4
    wide = np.concatenate([mask[:, -pad:], mask, mask[:, :pad]], axis=1)
    d = distance_transform_edt(wide)
    return d[:, pad:pad + w].astype(np.float32)


def _blob(LON, LAT, plon, plat, radius_km):
    """A LOBATE blob, not a disc.

    A perfect circle is the one outline no natural feature has, and an oceanic
    plateau is about as far from one as a shape gets: it is a flood-basalt pile,
    bounded by the rifted margins it split along, cut by fracture zones, and
    built from overlapping flow fronts. Drawn as a disc, Ontong Java and
    Kerguelen came out as machined coins sitting on the sea floor, which is the
    single most obviously artificial thing a chart can show.

    Three angular harmonics fix it for nothing. Their phases come from the
    blob's own position, so a given plateau keeps the same outline at every
    keyframe instead of writhing as you scrub.
    """
    r = math.degrees(radius_km / 6371.0)
    dlon = ((LON - plon + 180.0) % 360.0) - 180.0
    dx = dlon * np.cos(np.radians(LAT))
    dy = LAT - plat
    d = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    s = plon * 12.9898 + plat * 78.233
    warp = (1.0
            + 0.22 * np.cos(2.0 * th + math.sin(s) * math.pi)
            + 0.14 * np.cos(3.0 * th + math.sin(s * 2.3) * math.pi)
            + 0.08 * np.cos(5.0 * th + math.sin(s * 3.7) * math.pi))
    return np.clip(1.0 - (d / np.maximum(r * warp, 1e-6)) ** 2, 0.0, 1.0)


def _curve(age, points):
    """Elevation of a plateau at `age`, or None if it did not exist yet.

    The oldest point on a curve is the feature's BIRTH -- Ontong Java erupted at
    ~126 Ma, the Seychelles rifted at ~90, Rio Grande Rise at ~85. This used to
    clamp past that point and return the oldest value for all older ages, which
    quietly asserted that every one of them was a standing island throughout the
    Palaeozoic and the Precambrian: seven emergent plateaus were being drawn in
    the middle of Panthalassa at 300 Ma, as bright islands in open ocean. Return
    None instead and let the caller skip them. (The YOUNG end still clamps --
    a plateau that exists today goes on existing into the future.)
    """
    pts = sorted(points, key=lambda p: p[0])
    if age > pts[-1][0]:
        return None                      # not yet formed at this age
    if age <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        a0, v0 = pts[i]
        a1, v1 = pts[i + 1]
        if a0 <= age <= a1:
            t = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return v0 + (v1 - v0) * t
    return pts[-1][1]


# ---------------------------------------------------------------------------
# Oceanic plateaus and microcontinents. Present-day anchor(s) + radius(km), and
# an elevation curve (age_Ma, metres): positive is land, negative is submarine.
# Ages and settings from the oceanic-plateau / continental-fragment literature.
PLATEAUS = {
    # --- microcontinents that were once emergent -------------------------
    "Kerguelen": {
        # SOUTHERN plateau, not northern. All three anchors sat on the northern
        # Kerguelen Plateau, and that end shares its history with Broken Ridge:
        # it rifted north WITH India and the rotation model carries it that way,
        # so the bank -- and the label built from the same anchors -- tracked
        # India to 40 S at 100 Ma, nine degrees from the India label and reading
        # as attached to it. The southern plateau is the old part (~120 Ma) and
        # is Antarctic-plate crust that India tore away FROM, which is what the
        # card describes. Anchored there, the plateau stays where it belongs and
        # India leaves it behind.
        "anchors": [(74.0, -55.0, 600), (79.0, -58.5, 520), (70.0, -52.0, 430)],
        "elev": [(120, -1400), (110, 300), (95, 250), (85, -200), (60, -900),
                 (30, -1300), (0, -1400)]},
    "Seychelles": {
        "anchors": [(55.5, -5.0, 220)],
        "elev": [(90, 200), (66, 400), (60, 300), (40, 60), (0, 20)]},
    "Mauritia": {
        "anchors": [(59.0, -22.0, 300), (63.0, -27.0, 240)],
        "elev": [(85, 120), (75, 60), (65, -300), (40, -1200), (0, -1800)]},
    "JanMayen": {
        "anchors": [(-8.0, 70.5, 220), (-10.0, 68.0, 180)],
        "elev": [(55, 100), (40, -300), (30, -700), (25, -1100), (0, -1300)]},
    "Zealandia": {
        # Widest anchors and a genuinely emergent PEAK at ~80 Ma, when Zealandia
        # rifted from Gondwana as continental crust before it thinned and sank --
        # its greatest land extent, which is what the user asked to see.
        "anchors": [(170.0, -42.0, 750), (166.0, -33.0, 620),
                    (174.0, -47.0, 520), (159.0, -30.0, 460),
                    (163.0, -38.0, 520)],
        "elev": [(90, -300), (83, 500), (80, 550), (72, 200), (60, -300),
                 (45, -700), (23, -1000), (0, -1100)]},
    "Sahul": {
        # Australia + New Guinea + Tasmania on the exposed continental shelf.
        # The joined-up continent existed at the glacial low-stands; the 5-Myr
        # keyframes cannot resolve those, so the shelf is seeded to a shallow
        # bank -- just below the surface -- so its FULL extent reads as a
        # connected landmass edge through the Pleistocene even at an interglacial
        # keyframe. Marked shallow, not emergent, to stay honest about today.
        "anchors": [(141.0, -12.0, 380), (135.0, -10.0, 300),
                    (146.0, -40.0, 280), (140.0, -30.0, 420)],
        "elev": [(3, -120), (1, -60), (0.2, -30), (0, -60)]},
    "Argoland": {
        "anchors": [(112.0, -15.0, 340), (117.0, -18.0, 280)],
        "elev": [(165, 100), (155, 50), (130, -800), (100, -2500), (0, -4000)]},
    # --- large igneous province plateaus (submarine highs) ---------------
    "OntongJava": {
        "anchors": [(160.0, -3.0, 700), (165.0, 2.0, 520), (158.0, -8.0, 420)],
        "elev": [(126, 200), (120, -700), (100, -1300), (60, -1700), (0, -2000)]},
    "Manihiki": {
        "anchors": [(-161.0, -11.0, 380)],
        "elev": [(125, -500), (118, -1200), (60, -2000), (0, -2600)]},
    "Shatsky": {
        "anchors": [(159.0, 33.0, 420)],
        "elev": [(147, -1000), (140, -2200), (60, -3000), (0, -3400)]},
    "HessRise": {
        "anchors": [(178.0, 34.0, 360)],
        "elev": [(110, -1200), (99, -2400), (0, -3400)]},
    "Agulhas": {
        "anchors": [(26.0, -40.0, 320)],
        "elev": [(100, -1500), (90, -2200), (0, -2800)]},
    "BrokenRidge": {
        "anchors": [(96.0, -31.0, 300)],
        "elev": [(100, 100), (90, -400), (43, -1000), (0, -1600)]},
    "RioGrandeRise": {
        "anchors": [(-33.0, -31.0, 300)],
        "elev": [(85, 100), (80, -400), (45, -900), (0, -1400)]},
    "WalvisRidge": {
        "anchors": [(3.0, -25.0, 260), (8.0, -20.0, 220)],
        "elev": [(120, -500), (80, -1500), (0, -2400)]},
    "Naturaliste": {
        "anchors": [(110.0, -34.0, 240)],
        "elev": [(130, -600), (95, -1800), (0, -2500)]},
    "MascarenePlateau": {
        "anchors": [(60.0, -12.0, 380)],
        "elev": [(45, -100), (34, -800), (10, -1500), (0, -1800)]},
    # --- volcanic island chains, as shallow submarine ridges -------------
    "HawaiianRidge": {
        "anchors": [(-155.0, 20.0, 160), (-170.0, 26.0, 220),
                    (172.0, 31.0, 260)],
        "elev": [(80, -2500), (43, -1800), (20, -1200), (0, -800)]},
    "EastTasman": {
        "anchors": [(156.0, -44.0, 220)],
        "elev": [(80, -400), (55, -900), (0, -1500)]},
    "LineIslands": {
        "anchors": [(-160.0, 0.0, 400), (-162.0, 8.0, 300)],
        "elev": [(90, -700), (70, -1500), (0, -2200)]},
}


def emergent_names(age):
    """Plateaus standing above sea level at this age, for optional labelling."""
    out = []
    for n, sp in PLATEAUS.items():
        e = _curve(age, sp["elev"])
        if e is not None and e > 0:
            out.append(n)
    return out


def _plateau_field(shape, age, reconstructor):
    """Target elevation and mask for every seeded plateau at this age."""
    h, w = shape
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    target = np.full(shape, -1e9, np.float32)
    mask = np.zeros(shape, np.float32)
    for name, spec in PLATEAUS.items():
        elev = _curve(age, spec["elev"])
        if elev is None:
            continue                     # this plateau does not exist yet
        m = np.zeros(shape, np.float32)
        for alon, alat, radius in spec["anchors"]:
            plon, plat = alon, alat
            if reconstructor is not None and age > 0:
                try:
                    tr, _ = reconstructor.track(float(alon), float(alat),
                                                min(540, max(age, 5)))
                    if tr:
                        best = min(tr, key=lambda r: abs(r[0] - age))
                        plon, plat = best[1], best[2]
                except Exception:
                    pass
            m = np.maximum(m, _blob(LON, LAT, plon, plat, radius))
        # feather the rim so the plateau grades into the abyss
        here = m > 0.02
        target[here] = np.maximum(target[here], elev)
        mask = np.maximum(mask, m)
    return target, mask


def apply(z, age, reconstructor=None, motion=None, verbose=False):
    """Add evolving sea-floor structure and plateaus to an elevation grid.

    z is (H, W), row 0 = north. Returns (grid, ofield) where ofield is a HxWx3
    OCEAN-STRUCTURE field the shader grows the fine sea floor from:
      R  roughness age  0 rough young crust (shallow, near a ridge) .. 1 smooth
                        old crust (deep, sediment-buried), taken from depth.
      G,B spreading dir the regional-slope direction as (east, north), 0.5-centred
                        and scaled by CONFIDENCE (its length): full where the floor
                        has a clear regional tilt, ~0 on a flat abyssal plain.
    `motion` is accepted for compatibility but no longer needed.

    Nothing of the abyssal-hill FABRIC is baked into the ELEVATION: at 20 km per
    pixel a 2-5 km hill is sub-pixel, and baking it as fixed sine lines is exactly
    what made the old floor a grid of straight ridges. The shader grows it from
    ofield instead. Why the depth GRADIENT for the spreading direction: ocean
    crust deepens monotonically away from the ridge that made it (half-space
    cooling), so the large-scale slope points along the spreading direction,
    perpendicular to the ridge axis -- and unlike ridge-detection from the motion
    field (which is blank over open abyss and gave a Voronoi mesh of false
    ridges), it is smooth and defined wherever the floor tilts at all.
    """
    out = z.astype(np.float32).copy()
    h, w = out.shape
    sea = out < 0
    ofield = np.zeros((h, w, 3), np.float32)
    ofield[..., 0] = 1.0        # default (land / undefined): old, quiet crust
    ofield[..., 1] = 0.5        # default: no spreading direction, zero confidence
    ofield[..., 2] = 0.5

    from scipy import ndimage as _nd
    lat1d = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    # Poleward the equirectangular grid is badly squeezed; fade the fabric out.
    polefade = np.clip((74.0 - np.abs(lat1d)) / 14.0, 0.0, 1.0)[:, None]

    if sea.any():
        geom = _ridge_geometry(age)
        if geom is not None:
            # ---- REAL PLATE TECTONICS -------------------------------------
            # Crustal age from distance to the age's OWN resolved spreading
            # ridges (Merdith topologies via pyGPlates), not a proxy. Everything
            # below follows from it, so the floor genuinely opens at new rifts,
            # ages outward, and founders into the trenches -- and it all moves
            # because the ridge geometry is re-resolved at every keyframe.
            _rd, _rid, ridge_ok = geom["ridge"]
            dist_deg = _upsample(_rd, h, w, order=1)
            seg_id = _upsample(_rid.astype(np.float32), h, w, order=0)

            # ---- CRUSTAL AGE, from history rather than from present distance --
            # This is the substitution the whole sea floor now rests on. Age used
            # to be inferred as distance-to-the-nearest-present-ridge times a
            # spreading rate, which is wrong in three ways at once: the fabric it
            # implies is oriented to the ridge as it IS rather than as it WAS,
            # fracture zones cannot persist because nothing carries them, and the
            # coordinate's gradient decays with range so the far field loses its
            # fabric spacing along with its amplitude. Real age has none of those
            # problems -- its gradient is 1/(spreading rate) and does not decay.
            # See oceanage.py, crustage.py and realage.py.
            try:
                import oceanage
                # 768x1536, raised from 512x1024 in July 2026. This is the grid
                # the FRACTURE ZONES live or die on, and at 39 km cells they
                # died: rendering the fz field over the equatorial Atlantic at
                # both resolutions, the coarse one shows the ridge trace and
                # essentially nothing else, while the fine one shows the
                # Romanche-Chain-Vema family as the long continuous parallel
                # scars a real chart has. A fracture zone is a STEP in age a few
                # tens of km wide, so a cell that wide smooths it away before
                # anything downstream can see it -- and everything downstream
                # does depend on it: the baked troughs here, and the shader's
                # test for where the abyssal-hill fabric should break.
                #
                # Cheap, once the cold pyGPlates load is paid: 4.8 s a keyframe
                # against 54 s for the first call, so about 16 minutes across
                # the 201 ages, cached thereafter.
                _a, _az, _fz, _sv = oceanage.cached(round(float(age)), 768, 1536)
                age_myr = np.clip(_upsample(_a, h, w, order=1), 0.0, MAX_CRUST_AGE)
                fz_field = np.clip(_upsample(_fz, h, w, order=1), 0.0, 1.0)
                age_ok = True
            except Exception as _e:
                if verbose:
                    print(f"    crustal age unavailable ({_e}); falling back to distance")
                age_myr = np.clip(dist_deg * 111.19 / SPREAD_KM_PER_MYR, 0.0, MAX_CRUST_AGE)
                fz_field = None
                age_ok = False

            # DEPTH READS A SMOOTHED AGE; THE FABRIC READS THE RAW ONE.
            #
            # crustage assigns age per PLATE, from that plate's own isochrons, so
            # the field steps at every plate boundary -- and the boundaries are
            # long straight polygon edges. The depth-age law turns each step into
            # a wall: measured at 615 Ma, the 99.5th percentile change between
            # adjacent cells was 1,061 m over 25 km, against the 50-125 m a real
            # ocean does. That is the staircase, and its shape is the plate
            # geometry, which is why it reads as huge angular slabs rather than
            # anything oceanographic. It is worst in the Precambrian, where the
            # plate model has almost no isochrons to interpolate between.
            #
            # Depth is a REGIONAL quantity -- it varies over hundreds of km -- so
            # smoothing it over ~3 degrees costs nothing real and brings the
            # cell-to-cell step to about 90 m, inside the physical range. The
            # fabric, the fracture zones and the spreading direction keep the RAW
            # age, because those are fine-scale and a blur would erase them.
            _sg = AGE_DEPTH_SMOOTH_DEG * h / 180.0
            age_depth = _nd.gaussian_filter(age_myr, _sg, mode=("nearest", "wrap"))
            model_depth = -depth_from_age(age_depth)
            model_depth = np.clip(model_depth, -MAX_ABYSS, -RIDGE_DEPTH)

            # Blend over deep ocean only, leaving shelves and any real surveyed
            # bathymetry (the present day) largely alone.
            deep = np.clip((-out - 2200.0) / 2200.0, 0.0, 1.0) * sea * polefade
            wgt = deep * (0.72 if ridge_ok else 0.35)
            out = out * (1.0 - wgt) + model_depth * wgt

            # SPREADING DIRECTION = the gradient of the CRUSTAL AGE field. Age
            # increases along the flowline the crust travelled, so its gradient
            # is that flowline and the fabric lies at right angles to it --
            # parallel to the isochron, which is the ridge as it was when this
            # crust formed. That last clause is the whole point of the change:
            # taken from distance to the PRESENT ridge, the direction was right
            # only near the axis and swung wrong everywhere else, which is why
            # the fabric curved in arcs where a real chart combs dead straight.
            sm = _nd.gaussian_filter(age_myr if age_ok else dist_deg, 4.0)
            gy, gx = np.gradient(sm)
            coslat = np.clip(np.cos(np.radians(lat1d)), 0.08, 1.0)[:, None]
            east = gx / coslat
            north = -gy                                # row index increases south
            mag = np.hypot(east, north) + 1e-9
            u, v = east / mag, north / mag
            conf = np.clip(mag / (0.35 * np.median(mag[sea]) + 1e-6), 0.0, 1.0) * polefade

            relief = np.zeros_like(out)
            chain_relief = None      # catalogued plume edifices, exempt from the cap
            deg_per_cell = 180.0 / h

            # AXIAL VALLEY, VARYING ALONG STRIKE. A slow ridge carries a rift
            # valley a few tens of km wide down its crest; the broad swell
            # either side is already there, because it IS the age-depth curve
            # above. What was missing is that the valley is not a uniform
            # ribbon. Melt is delivered to the middle of a segment and starved
            # at its ends, so the crest shoals by several hundred metres toward
            # the segment centre and drops into a NODAL BASIN about a kilometre
            # deeper where it meets the transform. That alternation of bulge
            # and basin, repeating every segment down the whole system, is what
            # a real ridge looks like at chart scale -- and it is the direct
            # cause of the along-axis relief the straight-line version lacked.
            edist = geom.get("ends")
            nodal = (np.exp(-(_upsample(edist, h, w, order=1) / 1.15) ** 2)
                     if edist is not None else np.zeros_like(dist_deg))
            relief -= np.exp(-(dist_deg / 0.55) ** 2) * (620.0 + 780.0 * nodal)
            relief -= np.exp(-(dist_deg / 1.70) ** 2) * 300.0 * nodal
            relief += np.exp(-(dist_deg / 2.60) ** 2) * 340.0 * (1.0 - nodal)

            # FRACTURE ZONES, back where they belong -- traced from the ridge
            # network's own transform offsets.
            #
            # This was abandoned once because the partition was built on the
            # dozen arcs the plate model resolves, whose largest Voronoi cell
            # covered a quarter of the planet and whose boundaries were
            # continent-length straight walls. That was a resolution problem,
            # not a wrong idea: the boundary between crust that came off one
            # ridge segment and crust that came off the next IS the fracture
            # zone. With _ridge_network supplying a properly segmented spreading
            # system, there are hundreds of cells rather than thirteen, and the
            # same construction now yields what it always should have -- a dense
            # family of flowline-parallel traces, one running out from every
            # transform, curving with the plate as real ones do.
            sid_i = seg_id.astype(np.int32)
            edge = np.zeros(sid_i.shape, bool)
            dxb = sid_i != np.roll(sid_i, 1, axis=1)      # wraps at the antimeridian
            edge |= dxb
            edge |= np.roll(dxb, -1, axis=1)
            dyb = sid_i[:-1, :] != sid_i[1:, :]
            edge[:-1, :] |= dyb
            edge[1:, :] |= dyb
            # SMOOTH THE DISTANCE FIELD BEFORE ITS LEVEL SETS ARE USED AS
            # GEOMETRY. `edge` is a Voronoi boundary rasterised onto a lat/lon
            # grid, so it is a staircase of single cells: the exact boundary is
            # a smooth curve, and every right angle in it is an artefact of the
            # lattice, not a feature. Taking exp(-(fzd/0.24)^2) of the raw
            # transform therefore draws that staircase at full contrast, and
            # with the network now supplying four times as many segments as
            # before it covered the abyss in a right-angled circuit-board mesh.
            # Half a groove-width of blur costs nothing real -- the trough is
            # 0.24 deg wide and this is 0.26 -- and restores the smooth curve
            # the partition boundary always was. Same lesson as the sediment
            # field below: a distance transform is not a shape until it is
            # band-limited.
            fzd = _nd.gaussian_filter(_edt_wrap(~edge) * deg_per_cell, 3.0)
            # A trace is only a fracture zone where it runs along the flowline.
            # Cell boundaries between distant or oddly-oriented segments cut
            # across the grain and must be dropped, or they draw a lattice.
            fgy, fgx = np.gradient(_nd.gaussian_filter(fzd, 2.0))
            ge_, gn_ = fgx / coslat, -fgy
            gm_ = np.hypot(ge_, gn_) + 1e-6
            align = np.abs(ge_ / gm_ * u + gn_ / gm_ * v)   # 0 correct, 1 spurious
            keep = np.clip(1.0 - align * 1.8, 0.0, 1.0)
            # narrow trough with a flanking rise, and only out on real sea floor
            # ...and only on crust these segments plausibly made. Far out in the
            # basin the nearest segment is thousands of km away, the partition
            # boundary there is a straight wall between two distant cells rather
            # than a flowline, and drawing it puts a ruled line across empty
            # abyss. Fade the traces out past ~30 degrees of spreading.
            fz_ok = (keep * np.clip((-out - 2400.0) / 1500.0, 0.0, 1.0)
                     * (1.0 - np.clip((dist_deg - 16.0) / 14.0, 0.0, 1.0)))
            if age_ok and fz_field is not None:
                # AGE-DERIVED FRACTURE ZONES, replacing the Voronoi partition.
                # A fracture zone is two crusts of DIFFERENT AGE lying side by
                # side, so it is an age offset measured along the isochron --
                # which is exactly what oceanage.fz carries. The important
                # difference from the partition version is not accuracy, it is
                # PERSISTENCE: an age offset travels with the crust, so one
                # transform's wake stays in the plate for as long as the plate
                # lasts. That is why real fracture zones cross whole basins,
                # and why the old construction could never produce one -- it
                # was rebuilt from the present segmentation every keyframe and
                # so could never be older than the frame it was drawn in.
                fzw = (fz_field * np.clip((-out - 2400.0) / 1500.0, 0.0, 1.0)
                       * polefade)
                ring = np.clip(_nd.gaussian_filter(fzw, 5.2) - fzw * 0.80, 0.0, None)
                relief -= fzw * 430.0
                relief += ring * 260.0          # the flanking ridges either side
            else:
                relief -= np.exp(-(fzd / 0.24) ** 2) * 380.0 * fz_ok
                relief += np.exp(-((fzd - 0.62) / 0.45) ** 2) * 110.0 * fz_ok

            # TRENCHES. Where the model says crust is being consumed, cut the
            # deepest features on Earth -- narrow, arcuate, and only on the ocean
            # side. ~100 km wide is 5 cells here, so this is genuinely resolvable.
            tdist = geom["trench"]
            if tdist is not None:
                tdist = _upsample(tdist, h, w, order=1)
                trough = np.exp(-(tdist / 0.55) ** 2)
                deep_ok = np.clip((-out - 1500.0) / 2000.0, 0.0, 1.0)
                relief -= trough * deep_ok * 2300.0
                # OUTER RISE: the subducting plate flexes upward a few hundred
                # metres before it bends down, a low swell parallel to every
                # trench. Cheap, and it is visible on every real map.
                relief += np.exp(-((tdist - 2.2) / 1.1) ** 2) * deep_ok * 260.0

            # SEAMOUNTS, IN CHAINS. Volcanoes on ocean floor are built at fixed
            # hotspots while the plate slides over them, so they come out as
            # LINES -- Hawaii, Louisville, the Cook-Austral chain -- not as
            # scattered dots. Seed sparse cones, then smear each along the
            # direction the plate is travelling (which is the spreading
            # direction, u/v) taking a running maximum, so every seed is drawn
            # out into a track of progressively older, subsiding cones.
            if age_ok:
                # A POPULATION of individual mountains, not a smeared field.
                # The old construction seeded noise and dragged it along the
                # plate-motion direction taking a running maximum, which gives a
                # streak: no summit, no flank, no shadow, and nothing you could
                # point at and call a seamount. Real ones are discrete cones with
                # a power-law height distribution, built at the ridge and at
                # hotspots, subsiding with their plate and planed flat into
                # guyots if they ever reached the surface. See seamounts.py --
                # about six thousand of them above the 1.2 km this grid can
                # resolve, which is the right order for the resolvable part of a
                # population that runs to ~24,000 above a kilometre.
                import seamounts as _sm
                _bg, _chain = _sm.field(age_myr, sea, lat1d, deg_per_cell, u, v,
                                        age_of=float(age), floor=out)
                relief += _bg
                chain_relief = _chain
            else:
                rng = np.random.default_rng(11)
                smt = _nd.gaussian_filter(rng.random(out.shape).astype(np.float32), 4.4)
                smt = np.clip((smt - 0.74) / 0.26, 0.0, 1.0) ** 2
                chain = smt.copy()
                yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
                step_cells = 4.0
                for k in range(1, 8):
                    sy = yy + v * (k * step_cells)      # +v is north; rows go south
                    sx = xx - (u / coslat) * (k * step_cells)
                    back = _nd.map_coordinates(smt, [np.clip(sy, 0, h - 1), sx % w],
                                               order=1, mode="grid-wrap")
                    chain = np.maximum(chain, back * (1.0 - k / 9.0))
                relief += _nd.gaussian_filter(chain, 1.8) * 780.0 * np.clip(
                    1.1 - age_myr / 110.0, 0.15, 1.0)

            # SEDIMENT BLANKET. Abyssal plains next to a continent are the
            # flattest places on Earth -- turbidites pouring off the margin bury
            # the hills completely -- while mid-ocean floor keeps its full relief.
            # Without this every basin is uniformly rough to the coastline.
            # A distance transform returns stair-stepped level sets -- its
            # contours follow the pixel lattice -- so using it raw stamped the
            # sea floor with blocky right-angled zones where the fabric switched
            # off, which read as wide unnatural gaps with straight edges. Blur it
            # before use. Narrower than before (5 deg, not 7.5) and not quite to
            # zero, because a turbidite apron is a few hundred km wide, not a
            # thousand, and even it is not perfectly smooth.
            dland = _nd.gaussian_filter(_edt_wrap(out < 0) * deg_per_cell, 12.0)
            # ...and it is now a THICKNESS, competing against the relief it has
            # to bury, rather than a fade with distance from land. See
            # sediment.py: pelagic ooze accumulates at a rate set by latitude
            # times the crustal age, the turbidite wedge falls off from the
            # margin, and where the total exceeds the height of an abyssal hill
            # the floor is a plain. That threshold is why a real plain has a
            # sharp edge you can trace, which a distance fade can never produce.
            # It also needs a real age field to compute at all, which is a large
            # part of why the age model was worth building.
            if age_ok:
                import sediment as _sd
                # Distance to a SUBSTANTIAL landmass, not to any land at all.
                # A terrigenous wedge is built by a continent's rivers; a mid-
                # ocean island has no drainage basin behind it and builds
                # nothing. Measured against every scrap of land, the model put a
                # sediment apron around Hawaii and Iceland and buried 41% of the
                # ocean floor -- twice the real figure, and with plains in the
                # middle of the Pacific where the chart shows bare abyssal hills.
                # Eroding the mask first drops anything under about 3 degrees
                # across and leaves the continents.
                _big = _nd.binary_erosion(out >= 0, iterations=16)
                if not _big.any():
                    _big = out >= 0
                dbig = _nd.gaussian_filter(_edt_wrap(~_big) * deg_per_cell, 12.0)
                sed_m = _sd.thickness(age_myr, dbig, lat1d)
                sed = _sd.burial(sed_m)
                # A plain is a FILL TERRACE, not bare basalt: the pile stands the
                # floor up off the crust beneath it, which is why an abyssal
                # plain is measurably shallower than the ridge flank it grades
                # into. Added AFTER the burial multiply below, or the fill would
                # be scaled down by the very burial it represents.
                fill = np.minimum(sed_m, 3000.0) * _sd.FILL_FACTOR * sea
            else:
                sed = np.exp(-(dland / 5.0) ** 2)
                fill = 0.0
            relief *= (1.0 - 0.90 * sed)                 # hills and scarps drown in it
            relief = relief + fill

            relief *= polefade
            # NEVER let sea-floor relief break the surface. Seamount chains on
            # top of a ridge crest were raising 1,257 cells of open Panthalassa
            # above sea level at 300 Ma and drawing them as bright islands in the
            # middle of the ocean. Cap the rise so the floor can come up to, but
            # not past, 600 m depth -- real seamounts that DO breach are islands
            # the reconstruction places deliberately, not a by-product of noise.
            # Hold procedural relief well BELOW the depth at which the palette
            # starts lightening toward shelf turquoise (-850 m). At -600 every
            # seamount peak in mid-ocean lit up bright cyan, scattering
            # turquoise flecks in broad bands across the open abyss. Real
            # seamounts overwhelmingly stay deep -- the few that reach the
            # surface are guyots and atolls, and those come from the plateau
            # system deliberately, not from noise.
            headroom = np.maximum(-out - 1300.0, 0.0)
            relief = np.minimum(relief, headroom)
            # ...EXCEPT the catalogued plume chains, and this is the one place
            # the cap must not apply. Hawaii, Iceland, the Galapagos, Reunion,
            # the Azores, Cape Verde, Samoa, the Societies and the Marquesas are
            # volcanic ISLANDS, and a rule written to stop procedural noise
            # breaching was also holding every real one 1.3 km under water. The
            # split is not "how tall" but "do we know its name": a named
            # volcano's summit depth comes from its own age
            # (hotspots_cat.summit_depth), so the young end of a chain surfaces,
            # the middle is an atoll and the old end is a drowned guyot -- which
            # is the entire D4 prediction and it costs one comparison.
            if chain_relief is not None:
                relief = np.maximum(relief,
                                    chain_relief * (1.0 - 0.90 * sed) * polefade)
            out = out + np.where(sea & (out < -900.0), relief, 0.0)
            out = np.clip(out, -MAX_ABYSS, None)

            # R stays a PURE across-ridge coordinate (crustal age), because the
            # shader now uses it as exactly that -- to stretch the noise domain
            # for the abyssal grain and to run the fracture zones along the
            # flowline. Folding sediment into it, as an earlier version did,
            # breaks that coordinate near every margin.
            #
            # Sediment burial instead rides on the CONFIDENCE (the length of the
            # direction vector), which the shader already uses to fade the fabric
            # out: under a turbidite wedge there is no fabric to see.
            # Never all the way to zero: a dead-flat patch with a hard edge is
            # more obviously wrong than a faintly-textured one.
            conf = conf * (1.0 - 0.78 * sed)
            # R is NORMALISED DISTANCE FROM THE RIDGE, not age. The two differ
            # where it matters: age saturates at 190 Myr (crust older than that
            # has been subducted) which happens only ~51 degrees out, and in a
            # basin the size of Panthalassa most of the floor is further from the
            # few ridges this model resolves than that. A saturated R is a
            # CONSTANT, and the shader uses R as its across-ridge coordinate --
            # so the whole basin lost its grain and its fracture zones and went
            # glassy. Normalising over 75 degrees keeps the coordinate varying
            # right across the widest ocean; depth still uses the clamped age.
            # ...and it ships COMPANDED, log(1 + d/D0), not linear -- see the
            # note on CO_D0 at the top. The shader takes the exp back out, so
            # the quantity it works in is unchanged; what changes is that the
            # 256 available levels are now spent near the axis, where the
            # fabric actually is, instead of being spread evenly across a basin
            # whose far half is sediment-mantled and has nothing fine left to
            # resolve. This is the whole reason the fault set can be keyed to a
            # shipped 8-bit channel at all.
            # ...and what it compands is now AGE, not distance. Age is the
            # coordinate the fabric actually lives in: its gradient is one over
            # the spreading rate, which does not decay with range, so abyssal-
            # hill spacing stays uniform from the axis to the trench the way it
            # does in nature. Distance-to-the-present-ridge decayed, which is
            # what marbled the far field and then left it blank once that was
            # capped. Expressed in the same units as before -- degrees of
            # spreading -- so the shader's decode is unchanged and only the
            # meaning of the quantity improves.
            if age_ok:
                spread_deg = age_myr * SPREAD_KM_PER_MYR / 111.19
            else:
                spread_deg = dist_deg
            ofield[..., 0] = np.where(sea, compand(spread_deg), 1.0)
            ofield[..., 1] = np.where(sea, np.clip(0.5 + 0.5 * u * conf, 0.0, 1.0), 0.5)
            ofield[..., 2] = np.where(sea, np.clip(0.5 + 0.5 * v * conf, 0.0, 1.0), 0.5)
        else:
            # ---- fallback: no resolved topology for this age ----------------
            # Regional depth gradient as a stand-in for the spreading direction.
            seaf = sea.astype(np.float32)
            dep = np.where(sea, out, 0.0).astype(np.float32)
            reg = _nd.gaussian_filter(dep, 18.0) / np.maximum(_nd.gaussian_filter(seaf, 18.0), 1e-3)
            gy, gx = np.gradient(reg)
            coslat = np.clip(np.cos(np.radians(lat1d)), 0.08, 1.0)[:, None]
            east, north = gx / coslat, -gy
            slope = np.hypot(east, north)
            conf = np.clip(slope / 11.0, 0.0, 1.0) * polefade
            inv = 1.0 / (slope + 1e-6)
            age01 = np.clip((-out - RIDGE_DEPTH) / (MAX_ABYSS - RIDGE_DEPTH), 0.0, 1.0)
            # Companded like the main branch, so the shader has one decode.
            ofield[..., 0] = np.where(sea, compand(age01 * CO_MAX), 1.0)
            ofield[..., 1] = np.where(sea, np.clip(0.5 + 0.5 * east * inv * conf, 0.0, 1.0), 0.5)
            ofield[..., 2] = np.where(sea, np.clip(0.5 + 0.5 * north * inv * conf, 0.0, 1.0), 0.5)

    # plateaus and microcontinents ------------------------------------
    if PLATEAUS:
        target, pmask = _plateau_field(out.shape, age, reconstructor)
        valid = target > -1e8
        # raise the floor toward the plateau target where the blob is, but never
        # pull a continent DOWN: only apply where the target is higher than the
        # ground, or the ground is ocean
        raise_to = (valid & ((target > out) | sea))
        blend = np.clip(pmask, 0.0, 1.0) * raise_to
        out = np.where(raise_to, out * (1.0 - blend) + target * blend, out)
        # plateaus are their own crust: mark them as old/quiet so the shader does
        # not draw ridge-fabric across them
        ofield[..., 0] = np.where(pmask > 0.3, 1.0, ofield[..., 0])
        if verbose:
            em = emergent_names(age)
            print(f"    plateaus: {int((pmask > 0.05).sum())} cells seeded, "
                  f"emergent: {em or 'none'}")

    return out, ofield
