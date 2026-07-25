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

# --- age-depth (half-space cooling, Parsons & Sclater style) ---------------
RIDGE_DEPTH = 2600.0        # m: crest of a mid-ocean ridge
DEPTH_PER_SQRT_MYR = 350.0  # m per sqrt(Myr): how fast it deepens with age
MAX_ABYSS = 6000.0
# Half-spreading rate. Real ridges run 10-80 mm/yr; 30 mm/yr (= 30 km/Myr) is a
# fair global mean and puts the oldest surviving crust near 180 Myr, which is
# what the ocean basins actually show.
SPREAD_KM_PER_MYR = 30.0
MAX_CRUST_AGE = 190.0       # Myr: older than this and it has been subducted

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


def _ridge_network(polys, seg_deg=1.35, jog_deg=0.62, seed=17):
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
      2. resample each chain into segments of about `seg_deg`;
      3. jog alternate segments sideways, perpendicular to the local axis, to
         build the transform staircase.
    The jog is drawn from a stable hash of the segment index, so a given age
    always produces the same network and it does not shimmer between frames.

    Returns polylines plus one id PER SEGMENT. That id is what finally makes
    fracture zones work: with hundreds of segments instead of thirteen, the
    boundaries of the nearest-segment partition stop being continent-length
    Voronoi walls and become exactly what they should be -- a dense family of
    flowline-parallel traces, one running out from every transform.
    """
    import random as _r
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

    # --- 2 & 3. resample into segments and jog them into a staircase -----
    rng = _r.Random(seed)
    out, sid = [], 0
    for chain in chains:
        # walk the chain accumulating arc length, emitting a vertex every seg_deg
        pts, acc, prev = [chain[0]], 0.0, chain[0]
        for q in chain[1:]:
            dlon = (q[0] - prev[0] + 180.0) % 360.0 - 180.0
            step = math.hypot(dlon * math.cos(math.radians((q[1] + prev[1]) * 0.5)), q[1] - prev[1])
            acc += step
            if acc >= seg_deg:
                pts.append(q); acc = 0.0
            prev = q
        if pts[-1] != chain[-1]:
            pts.append(chain[-1])
        if len(pts) < 2:
            continue
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            dlon = (b[0] - a[0] + 180.0) % 360.0 - 180.0
            clat = max(math.cos(math.radians((a[1] + b[1]) * 0.5)), 0.05)
            L = math.hypot(dlon * clat, b[1] - a[1]) + 1e-9
            # unit normal to the segment, on the sphere's local tangent plane
            nx, ny = -(b[1] - a[1]) / L, (dlon * clat) / L
            j = (rng.random() - 0.5) * 2.0 * jog_deg
            out.append([[a[0] + nx * j / clat, a[1] + ny * j],
                        [b[0] + nx * j / clat, b[1] + ny * j]])
            sid += 1
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

    tdist = None
    txyz, tids = _densify(trench)
    if txyz is not None and len(txyz) >= 8:
        tdist, _ = _sphere_distance(txyz, tids, h, w)

    out = {"ridge": (rdist, rid, len(rxyz) >= 200), "trench": tdist}
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
    r = math.degrees(radius_km / 6371.0)
    dlon = ((LON - plon + 180.0) % 360.0) - 180.0
    d = np.sqrt((dlon * np.cos(np.radians(LAT))) ** 2 + (LAT - plat) ** 2)
    return np.clip(1.0 - (d / r) ** 2, 0.0, 1.0)


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
        "anchors": [(69.0, -49.0, 620), (75.0, -53.0, 520), (64.0, -46.0, 400)],
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
            age_myr = np.clip(dist_deg * 111.19 / SPREAD_KM_PER_MYR, 0.0, MAX_CRUST_AGE)
            model_depth = -(RIDGE_DEPTH + DEPTH_PER_SQRT_MYR * np.sqrt(age_myr))
            model_depth = np.clip(model_depth, -MAX_ABYSS, -RIDGE_DEPTH)

            # Blend over deep ocean only, leaving shelves and any real surveyed
            # bathymetry (the present day) largely alone.
            deep = np.clip((-out - 2200.0) / 2200.0, 0.0, 1.0) * sea * polefade
            wgt = deep * (0.72 if ridge_ok else 0.35)
            out = out * (1.0 - wgt) + model_depth * wgt

            # SPREADING DIRECTION = the gradient of the ridge-distance field. It
            # points straight away from the ridge that made this crust, which is
            # the direction the plate travelled, so the shader's abyssal-hill
            # fabric lies at right angles to it -- parallel to the ridge axis, as
            # real abyssal hills do.
            sm = _nd.gaussian_filter(dist_deg, 2.0)
            gy, gx = np.gradient(sm)
            coslat = np.clip(np.cos(np.radians(lat1d)), 0.08, 1.0)[:, None]
            east = gx / coslat
            north = -gy                                # row index increases south
            mag = np.hypot(east, north) + 1e-9
            u, v = east / mag, north / mag
            conf = np.clip(mag / (0.35 * np.median(mag[sea]) + 1e-6), 0.0, 1.0) * polefade

            relief = np.zeros_like(out)
            deg_per_cell = 180.0 / h

            # AXIAL VALLEY. A slow ridge carries a rift valley a few tens of km
            # wide down its crest; the broad swell either side is already there,
            # because it IS the age-depth curve above.
            relief -= np.exp(-(dist_deg / 0.55) ** 2) * 900.0

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
            fzd = _edt_wrap(~edge) * deg_per_cell
            # A trace is only a fracture zone where it runs along the flowline.
            # Cell boundaries between distant or oddly-oriented segments cut
            # across the grain and must be dropped, or they draw a lattice.
            fgy, fgx = np.gradient(_nd.gaussian_filter(fzd, 1.0))
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
            rng = np.random.default_rng(11)
            smt = _nd.gaussian_filter(rng.random(out.shape).astype(np.float32), 2.2)
            smt = np.clip((smt - 0.74) / 0.26, 0.0, 1.0) ** 2
            chain = smt.copy()
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            step_cells = 2.0
            for k in range(1, 8):
                sy = yy + v * (k * step_cells)          # +v is north; rows go south
                sx = xx - (u / coslat) * (k * step_cells)
                back = _nd.map_coordinates(smt, [np.clip(sy, 0, h - 1), sx % w],
                                           order=1, mode="grid-wrap")
                chain = np.maximum(chain, back * (1.0 - k / 9.0))
            relief += _nd.gaussian_filter(chain, 0.9) * 780.0 * np.clip(
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
            dland = _nd.gaussian_filter(_edt_wrap(out < 0) * deg_per_cell, 6.0)
            sed = np.exp(-(dland / 5.0) ** 2)
            relief *= (1.0 - 0.72 * sed)                 # hills and scarps drown in it

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
            ofield[..., 0] = np.where(sea, np.clip(dist_deg / 75.0, 0.0, 1.0), 1.0)
            ofield[..., 1] = np.where(sea, np.clip(0.5 + 0.5 * u * conf, 0.0, 1.0), 0.5)
            ofield[..., 2] = np.where(sea, np.clip(0.5 + 0.5 * v * conf, 0.0, 1.0), 0.5)
        else:
            # ---- fallback: no resolved topology for this age ----------------
            # Regional depth gradient as a stand-in for the spreading direction.
            seaf = sea.astype(np.float32)
            dep = np.where(sea, out, 0.0).astype(np.float32)
            reg = _nd.gaussian_filter(dep, 9.0) / np.maximum(_nd.gaussian_filter(seaf, 9.0), 1e-3)
            gy, gx = np.gradient(reg)
            coslat = np.clip(np.cos(np.radians(lat1d)), 0.08, 1.0)[:, None]
            east, north = gx / coslat, -gy
            slope = np.hypot(east, north)
            conf = np.clip(slope / 11.0, 0.0, 1.0) * polefade
            inv = 1.0 / (slope + 1e-6)
            age01 = np.clip((-out - RIDGE_DEPTH) / (MAX_ABYSS - RIDGE_DEPTH), 0.0, 1.0)
            ofield[..., 0] = np.where(sea, age01, 1.0)
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
