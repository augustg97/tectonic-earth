"""THE FUTURE AS PLATE TECTONICS (3.16): kinematics, collisions, rendering.

WHAT IT REPLACES. Until 3.15 the future was ten plate groups, each turned about
ONE fixed axis from today to a packed target at +250 Myr, with overlaps settled
by keeping the higher ground. Nothing deformed: a continent that ran into
another slid underneath it with its outline intact (Australia at +250 was
today's Australia), and the packing -- groups treated as discs of their land
radius, pushed apart until they only touched -- left the Atlantic open,
because two concave coasts cannot close on a disc. The drawing did not match
the reconstruction it was aimed at.

WHAT THIS IS. Three parts, each a statement a reader can check:

1. KINEMATICS: each plate's rotation from today to time t, R_g(t), is a smooth
   (C1) curve through keyframe rotations. The first 25 Myr are TODAY'S MOTION,
   extrapolated -- the NNR-MORVEL56 Euler vectors (Argus, Gordon & DeMets 2011)
   -- which is the one part of any future that is measured. After that the
   keyframes follow Scotese's published scenario (Atlas of Future Plate
   Tectonic Reconstructions, 2018; Pangea Proxima), stage by stage: the Red
   Sea and the Mediterranean close by +50, Australia runs into SE Asia and
   closes the South China Sea by +75, West Antarctica rifts away while East
   Antarctica is drawn north into the tropics and collides with Sumatra and
   north-west Australia at +150, the Atlantic starts to close from +100 as
   its floor goes down beneath the Americas, and by +250 North America is
   against West Africa and South America wraps round southern Africa to meet
   East Antarctica, enclosing the remnant Indian Ocean (the Medi-Pangean Sea).
   Keyframe positions are authored as ANCHORS -- "this present-day point is
   against that one" -- and fitted as rigid rotations, so the scenario reads as
   geology rather than as numbers.

2. DEFORMATION: continents do not interpenetrate and do not pass through each
   other. Every Myr the rigid motion is applied, the new overlap between two
   plates' CONTINENTAL crust is measured, and it is taken up by shortening both
   margins: each plate's crust behind the contact is displaced back along the
   convergence, fully at the front and fading over ~700 km into its interior.
   The displacement accumulates in an inverse map per plate (which material
   point is now at each position of the plate's own frame), so outlines
   crumple, margins shorten and the leading edge of an indenter is flattened
   against what it hits. The area lost is crustal thickening (Airy isostasy,
   ~5.3 km of surface per unit of areal shortening), capped by gravitational
   collapse (the thickened crust spreads sideways past about double thickness,
   which is how a plateau widens) and worn down with time. Oceanic crust does
   not collide: continents override it, which is subduction.

3. RENDERING: at any keyframe, any present-day field (the DEM, the ocean-age
   grid) is carried to its future position through the same maps, so the
   terrain, the age of the sea floor, the plate slots, the labels and the
   displacement field all describe one motion.

    ../venv/bin/python future_tectonics.py --integrate     # run the 250 Myr integration, cache it
    ../venv/bin/python future_tectonics.py --maps          # debug maps at 25 Myr steps
    ../venv/bin/python future_tectonics.py --report        # speeds, contacts, shortening
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates
from scipy.ndimage import label as cclabel

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "future_tectonics")
WEB = os.path.join(HERE, "..", "web")
SPAN = 250.0            # Myr
STEP = 5                # keyframe spacing, Myr
DT = 1.0                # integration step, Myr
WH, WW = 360, 720       # the working grid (0.5 deg): masks, deformation, inverse maps
CH, CW = 720, 1440      # the continental-crust mask (0.25 deg)
PH, PW = 1440, 2880     # the present-day plate raster (0.125 deg)
RE = 6371.0             # km

# ------------------------------------------------------------------ geometry


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    cl = np.cos(la)
    return np.stack([cl * np.cos(lo), cl * np.sin(lo), np.sin(la)], -1)


def lonlat(v):
    n = v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-15)
    return (np.degrees(np.arctan2(n[..., 1], n[..., 0])),
            np.degrees(np.arcsin(np.clip(n[..., 2], -1.0, 1.0))))


def expm(r):
    r = np.asarray(r, float)
    th = float(np.linalg.norm(r))
    if th < 1e-14:
        return np.eye(3)
    k = r / th
    K = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    return np.eye(3) + math.sin(th) * K + (1.0 - math.cos(th)) * (K @ K)


def logm(R):
    c = float(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0))
    th = math.acos(c)
    if th < 1e-12:
        return np.zeros(3)
    if math.pi - th < 1e-6:
        # near pi: axis from the symmetric part
        B = (R + np.eye(3)) / 2.0
        k = np.sqrt(np.clip(np.diag(B), 0.0, None))
        i = int(np.argmax(k))
        k = B[:, i] / max(k[i], 1e-12)
        return k / np.linalg.norm(k) * th
    w = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2.0 * math.sin(th))
    return w * th


def fit_rotation(P, Q, w=None):
    """The rotation R minimising sum w_i |R p_i - q_i|^2 (Wahba's problem)."""
    P = np.atleast_2d(P); Q = np.atleast_2d(Q)
    w = np.ones(len(P)) if w is None else np.asarray(w, float)
    B = (Q * w[:, None]).T @ P
    U, _S, Vt = np.linalg.svd(B)
    M = np.diag([1.0, 1.0, np.linalg.det(U) * np.linalg.det(Vt)])
    return U @ M @ Vt


def tangent_basis(v):
    """East and north unit vectors at unit vectors v (...,3)."""
    x, y, z = v[..., 0], v[..., 1], v[..., 2]
    e = np.stack([-y, x, np.zeros_like(x)], -1)
    en = np.linalg.norm(e, axis=-1, keepdims=True)
    e = np.where(en > 1e-9, e / np.maximum(en, 1e-12), np.array([1.0, 0.0, 0.0]))
    n = np.cross(v, e)
    return e, n


def grid_dirs(h, w):
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    return unit(LON, LAT).astype(np.float64), LON, LAT


def sample(field, v, order=1, wrap=True):
    """Bilinear (order 1) or nearest (order 0) sample of a north-up
    equirectangular field (h, w) or (c, h, w) at unit vectors v (..., 3)."""
    lon, lat = lonlat(v)
    f = field if field.ndim == 3 else field[None]
    h, w = f.shape[1], f.shape[2]
    fy = np.clip((90.0 - lat) / 180.0 * h - 0.5, 0.0, h - 1.0)
    fx = (lon + 180.0) / 360.0 * w - 0.5
    if order == 0:
        iy = np.clip(np.round(fy).astype(np.int64), 0, h - 1)
        ix = np.round(fx).astype(np.int64) % w
        out = f[:, iy, ix]
    else:
        y0 = np.floor(fy).astype(np.int64); wy = fy - y0
        x0 = np.floor(fx).astype(np.int64); wx = fx - x0
        y1 = np.minimum(y0 + 1, h - 1)
        x0 %= w; x1 = (x0 + 1) % w
        out = (f[:, y0, x0] * (1 - wx) * (1 - wy) + f[:, y0, x1] * wx * (1 - wy)
               + f[:, y1, x0] * (1 - wx) * wy + f[:, y1, x1] * wx * wy)
    return out if field.ndim == 3 else out[0]


# -------------------------------------------------------------------- plates

PLATES = ["AFRICA", "ARABIA", "EURASIA", "INDIA", "AUSTRALIA", "ANTARCTICA_E",
          "ANTARCTICA_W", "NORTH_AMERICA", "SOUTH_AMERICA", "PACIFIC", "BAJA"]
PB = {
    "Africa": "AFRICA", "Somalia": "AFRICA",       # the East African Rift fails (Scotese 2018)
    "Arabia": "ARABIA",
    "Eurasia": "EURASIA", "Amur": "EURASIA", "Yangtze": "EURASIA", "Okhotsk": "EURASIA",
    "Okinawa": "EURASIA", "Sunda": "EURASIA", "Burma": "EURASIA", "Aegean Sea": "EURASIA",
    "Anatolia": "EURASIA", "Banda Sea": "EURASIA", "Molucca Sea": "EURASIA",
    "Philippine Sea": "EURASIA",
    "India": "INDIA",
    "Australia": "AUSTRALIA", "Birds Head": "AUSTRALIA", "Maoke": "AUSTRALIA",
    "Woodlark": "AUSTRALIA", "Solomon Sea": "AUSTRALIA", "New Hebrides": "AUSTRALIA",
    "Timor": "AUSTRALIA", "Kermadec": "AUSTRALIA", "Tonga": "AUSTRALIA",
    "Conway Reef": "AUSTRALIA", "Balmoral Reef": "AUSTRALIA", "Futuna": "AUSTRALIA",
    "Niuafo'ou": "AUSTRALIA",
    "Antarctica": "ANTARCTICA_E", "Shetland": "ANTARCTICA_W",
    "North America": "NORTH_AMERICA", "Juan de Fuca": "NORTH_AMERICA",
    "Rivera": "NORTH_AMERICA", "Cocos": "NORTH_AMERICA", "Caribbean": "NORTH_AMERICA",
    "Panama": "NORTH_AMERICA",
    "South America": "SOUTH_AMERICA", "Nazca": "SOUTH_AMERICA", "Altiplano": "SOUTH_AMERICA",
    "North Andes": "SOUTH_AMERICA", "Juan Fernandez": "SOUTH_AMERICA",
    "Easter": "SOUTH_AMERICA", "Galapagos": "SOUTH_AMERICA", "Scotia": "SOUTH_AMERICA",
    "Sandwich": "SOUTH_AMERICA",
    "Pacific": "PACIFIC", "Mariana": "PACIFIC", "Caroline": "PACIFIC", "Manus": "PACIFIC",
    "North Bismarck": "PACIFIC", "South Bismarck": "PACIFIC",
}
MORVEL_OF = {"AFRICA": "Africa", "ARABIA": "Arabia", "EURASIA": "Eurasia", "INDIA": "India",
             "AUSTRALIA": "Australia", "ANTARCTICA_E": "Antarctica",
             "ANTARCTICA_W": "Antarctica", "NORTH_AMERICA": "North America",
             "SOUTH_AMERICA": "South America", "PACIFIC": "Pacific", "BAJA": "Pacific"}
COLOURS = {"AFRICA": (214, 160, 80), "ARABIA": (190, 120, 90), "EURASIA": (120, 160, 90),
           "INDIA": (230, 200, 90), "AUSTRALIA": (230, 120, 70), "ANTARCTICA_E": (215, 215, 230),
           "ANTARCTICA_W": (160, 175, 215), "NORTH_AMERICA": (110, 140, 210),
           "SOUTH_AMERICA": (200, 110, 150), "PACIFIC": (120, 120, 120), "BAJA": (90, 200, 200)}
PI = {p: i for i, p in enumerate(PLATES)}


def _rasterise(h, w):
    """Plate index per cell of the present sphere, from PB2002's polygons."""
    plates = json.load(open(os.path.join(WEB, "plates.json")))
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    pid = np.full((h, w), -1, np.int16)
    for p in plates:
        g = PB.get(p["name"])
        if g is None:
            continue
        gi = PI[g]
        for ring in p["rings"]:
            ring = np.asarray(ring, float)
            x, y = ring[:, 0], ring[:, 1]
            r0 = max(0, int(np.floor((90 - y.max()) / 180 * h)) - 1)
            r1 = min(h, int(np.ceil((90 - y.min()) / 180 * h)) + 1)
            c0 = max(0, int(np.floor((x.min() + 180) / 360 * w)) - 1)
            c1 = min(w, int(np.ceil((x.max() + 180) / 360 * w)) + 1)
            if r1 <= r0 or c1 <= c0:
                continue
            LON, LAT = np.meshgrid(lon[c0:c1], lat[r0:r1])
            acc = np.zeros(LAT.shape, bool)
            for i in range(len(ring)):
                j = (i - 1) % len(ring)
                cond = ((y[i] > LAT) != (y[j] > LAT)) & \
                       (LON < (x[j] - x[i]) * (LAT - y[i]) / (y[j] - y[i] + 1e-12) + x[i])
                acc ^= cond
            sub = pid[r0:r1, c0:c1]
            sub[acc & (sub < 0)] = gi
    return pid


def present_dem():
    """Today's elevation, north-up, 900 x 1800 -- what the future is carried from."""
    if "dem" not in _S:
        from build_frames import index_dems, read_dem
        from render import resample_dem
        idx = index_dems()
        avail = np.array(sorted(idx.keys()))
        z0 = read_dem(idx[float(avail[np.argmin(np.abs(avail))])])
        _S["dem"] = resample_dem(z0, 900, 1800).astype(np.float32)
    return _S["dem"]


_S = {}


def present_plates():
    """(pid 0.125 deg, continental mask 0.25 deg) -- cached on disk."""
    if "pid" in _S:
        return _S["pid"], _S["cont"]
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "present_plates.npz")
    src = os.path.join(WEB, "plates.json")
    key = "%s-%s-%s" % (os.path.getmtime(src), hashlib.sha1(repr(sorted(PB.items())).encode()).hexdigest()[:8], "v6")
    if os.path.exists(p):
        d = np.load(p)
        if str(d["key"]) == key:
            _S["pid"], _S["cont"] = d["pid"], d["cont"]
            return _S["pid"], _S["cont"]
    pid = _rasterise(PH, PW)
    lon = (np.arange(PW) + 0.5) / PW * 360 - 180
    lat = 90 - (np.arange(PH) + 0.5) / PH * 180
    LON, LAT = np.meshgrid(lon, lat)
    # Unassigned polar caps belong to the continent there.
    pid[(pid < 0) & (LAT < -80.0)] = PI["ANTARCTICA_E"]
    pid[(pid < 0) & (LAT > 84.0)] = PI["NORTH_AMERICA"]
    # continental crust: no ocean age (Mueller 2019), and not a deep basin;
    # all of Antarctica's bedrock counts, since the DEM gives it without ice
    import realage
    age, _ = realage.present(CH, CW)
    dem = present_dem()
    z = np.asarray(_down(dem, CH, CW))
    wlat = 90 - (np.arange(CH) + 0.5) / CH * 180
    WLAT = np.repeat(wlat[:, None], CW, 1)
    cont = np.isnan(age) & ((z > -2200.0) | (WLAT < -62.0))
    contP = np.repeat(np.repeat(cont, 2, 0), 2, 1)
    _split_antarctica(pid, contP, LON, LAT)
    # Baja and California west of the San Andreas ride the Pacific plate:
    # carve them out as their own plate (they accrete to Alaska, Scotese +75-100)
    baja = (pid == PI["PACIFIC"]) & contP & (LON > -126.0) & (LON < -106.0) & (LAT > 20.0) & (LAT < 42.0)
    pid[baja] = PI["BAJA"]
    # Zealandia's Pacific-plate half stays with Australia (see README 9)
    zea = (pid == PI["PACIFIC"]) & contP & (LAT < -28.0) & ((LON > 155.0) | (LON < -170.0))
    pid[zea] = PI["AUSTRALIA"]
    # what remains of the Pacific plate is ocean floor (its "continental"
    # scraps are arc and plateau crust): it goes down beneath Asia, it does not
    # ram it for 250 Myr
    pac = np.repeat(np.repeat(pid == PI["PACIFIC"], 1, 0), 1, 1)
    pacC = pac[::2, ::2] if pac.shape != cont.shape else pac
    cont = cont & ~pacC
    np.savez_compressed(p, pid=pid, cont=cont, key=key)
    _S["pid"], _S["cont"] = pid, cont
    return pid, cont


# WEST ANTARCTICA (3.16). The continent splits along the Transantarctic
# Mountains' front -- the line Scotese's Trans-Antarctic rift opens along --
# from east of Cape Adare down the Victoria Land coast, along the Ross Ice
# Shelf's inner edge past the Queen Maud, Horlick and Thiel ranges to the
# Pensacolas and the Filchner's east side (lon, lat). Until 3.16 it was a
# lon/lat box (-179..-34, -86.5..-60), and a box opens as a box: the
# Trans-Antarctic Ocean came out as a band along a parallel and two meridians.
TAM_FRONT = [(172.5, -70.0), (166.0, -77.0), (175.0, -83.5), (-160.0, -85.5),
             (-120.0, -85.0), (-90.0, -84.0), (-60.0, -83.0), (-36.0, -78.5), (-30.0, -76.0)]


def _in_polygon(pts, poly):
    """Even-odd rule: which of pts (n, 2) lie inside the closed polygon (m, 2)."""
    x, y = pts[:, 0], pts[:, 1]
    inside = np.zeros(len(pts), bool)
    xj, yj = poly[-1]
    for xi, yi in poly:
        cross = (yi > y) != (yj > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (xj - xi) * (y - yi) / (yj - yi) + xi
        inside ^= cross & (x < xint)
        xj, yj = xi, yi
    return inside


def _split_antarctica(pid, contP, LON, LAT):
    """In place: Antarctic-plate continent on the Pacific side of TAM_FRONT
    goes to West Antarctica, and the plate's ocean floor to whichever of the
    two continents is nearer (a Voronoi split on the sphere), so the
    boundary between their floors is where a rift between them would open."""
    from scipy.spatial import cKDTree
    ant = pid == PI["ANTARCTICA_E"]
    if not ant.any():
        return
    # the polygon closes round the Pacific sector at 55 S; drawn in south
    # polar stereographic coordinates, so the dateline is not an edge
    ring = list(TAM_FRONT) + [(-30.0, -55.0)] + \
        [(lo, -55.0) for lo in np.arange(-35.0, -180.0, -5.0)] + \
        [(lo, -55.0) for lo in np.arange(180.0, 172.4, -2.5)]

    def st(lon, lat):
        r = 2.0 * np.tan(np.radians(90.0 + np.asarray(lat)) / 2.0)
        return np.stack([r * np.cos(np.radians(lon)), r * np.sin(np.radians(lon))], -1)
    poly = st([p[0] for p in ring], [p[1] for p in ring])
    ys, xs = np.nonzero(ant)
    inside = _in_polygon(st(LON[ys, xs], LAT[ys, xs]), poly)
    cc = contP[ys, xs]
    wa_c = inside & cc
    ea_c = (~inside) & cc
    X = unit(LON[ys, xs], LAT[ys, xs])
    ocean = ~cc
    wa = wa_c.copy()
    if wa_c.any() and ea_c.any() and ocean.any():
        dw, _ = cKDTree(X[wa_c][::3]).query(X[ocean])
        de, _ = cKDTree(X[ea_c][::3]).query(X[ocean])
        wa[np.nonzero(ocean)[0][dw < de]] = True
    pid[ys[wa], xs[wa]] = PI["ANTARCTICA_W"]


def _down(a, h, w):
    """Area-average resample of a north-up field to h x w."""
    from PIL import Image
    return np.asarray(Image.fromarray(np.asarray(a, np.float32)).resize((w, h), Image.BOX), np.float32)


# ---------------------------------------------------------------- kinematics

def morvel():
    if "mv" not in _S:
        d = json.load(open(os.path.join(HERE, "..", "data", "nnr_morvel56.json")))["plates"]
        _S["mv"] = d
    return _S["mv"]


def omega0(plate):
    """Today's angular velocity (rad/Myr, a vector) -- NNR-MORVEL56."""
    m = morvel()[MORVEL_OF[plate]]
    return unit(m["lon"], m["lat"]) * math.radians(m["w"])


def centroid(plate):
    pid, _ = present_plates()
    lon = (np.arange(PW) + 0.5) / PW * 360 - 180
    lat = 90 - (np.arange(PH) + 0.5) / PH * 180
    LON, LAT = np.meshgrid(lon, lat)
    m = pid == PI[plate]
    v = unit(LON[m], LAT[m]).mean(axis=0)
    return v / np.linalg.norm(v)


KEYS = {}        # plate -> [(t, R)], built by storyline()


def _spline(plate):
    """Keyframes -> (times, rotation vectors, tangents) for C1 Hermite interpolation."""
    ks = sorted(KEYS[plate], key=lambda k: k[0])
    ts = np.array([k[0] for k in ks], float)
    rs = np.array([logm(k[1]) for k in ks])
    # keep consecutive rotation vectors on the same sheet (no 2pi jumps)
    for i in range(1, len(rs)):
        th = np.linalg.norm(rs[i])
        if th > 1e-9:
            alt = rs[i] - rs[i] / th * 2 * math.pi
            if np.linalg.norm(alt - rs[i - 1]) < np.linalg.norm(rs[i] - rs[i - 1]):
                rs[i] = alt
    ms = np.zeros_like(rs)
    ms[0] = omega0(plate)
    for i in range(1, len(rs)):
        if i < len(rs) - 1:
            ms[i] = (rs[i + 1] - rs[i - 1]) / (ts[i + 1] - ts[i - 1])
        else:
            ms[i] = (rs[i] - rs[i - 1]) / (ts[i] - ts[i - 1])
    return ts, rs, ms


def rot(plate, t):
    """Total rotation of `plate` from today to t Myr ahead (3x3)."""
    key = ("spl", plate)
    if key not in _S:
        _S[key] = _spline(plate)
    ts, rs, ms = _S[key]
    t = float(np.clip(t, ts[0], ts[-1]))
    i = int(np.clip(np.searchsorted(ts, t, side="right") - 1, 0, len(ts) - 2))
    h = ts[i + 1] - ts[i]
    s = (t - ts[i]) / h
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1
    h10 = s ** 3 - 2 * s ** 2 + s
    h01 = -2 * s ** 3 + 3 * s ** 2
    h11 = s ** 3 - s ** 2
    r = h00 * rs[i] + h10 * h * ms[i] + h01 * rs[i + 1] + h11 * h * ms[i + 1]
    return expm(r)


def omega(plate, t, dt=0.25):
    """Angular velocity (rad/Myr, a vector) at time t."""
    a = rot(plate, max(t - dt, 0.0))
    b = rot(plate, t + dt)
    return logm(b @ a.T) / (t + dt - max(t - dt, 0.0))


def velocity(plate, t, v):
    """Surface velocity (km/Myr) of plate at unit vectors v (...,3)."""
    return np.cross(omega(plate, t), v) * RE


# ------------------------------------------------------ authoring helpers

def pt(lon, lat):
    return unit(lon, lat)


def at(plate, t, lon, lat):
    """Where today's point (lon, lat) on `plate` sits at t, rigidly."""
    return rot(plate, t) @ pt(lon, lat)


def present_motion(plate, t):
    return expm(omega0(plate) * t)


def follow(plate, other, t, t0):
    """`plate` locked to `other` since t0: R_p(t) = R_o(t) R_o(t0)^T R_p(t0)."""
    return rot(other, t) @ rot(other, t0).T @ rot(plate, t0)


def dock(plate, t, pairs, weights=None, spin_hint=None):
    """The rotation (today -> t) putting each present point p of `plate` at the
    target q: pairs = [((lon, lat) on plate, target unit vector), ...]."""
    P = np.array([pt(*a) for a, _ in pairs])
    Q = np.array([q / np.linalg.norm(q) for _, q in pairs])
    return fit_rotation(P, Q, weights)


def offset(q, toward, km):
    """Move unit vector q by `km` along the great circle toward `toward`."""
    q = q / np.linalg.norm(q)
    d = toward - q * np.dot(q, toward)
    n = np.linalg.norm(d)
    if n < 1e-12:
        return q
    d /= n
    a = km / RE
    return q * math.cos(a) + d * math.sin(a)


def add_key(plate, t, R):
    KEYS.setdefault(plate, [])
    KEYS[plate] = [k for k in KEYS[plate] if abs(k[0] - t) > 1e-9] + [(float(t), R)]
    _S.pop(("spl", plate), None)


def storyline():
    """Author every plate's keyframes. Imported from future_story.py so the
    scenario reads as its own document."""
    if KEYS:
        return
    import future_story
    future_story.author(sys.modules[__name__])


# --------------------------------------------------------------- deformation

W_DEF = 700.0          # km: how far behind a contact the shortening reaches
D_MAX = 1000.0         # km: the most any crust is displaced by shortening
H_ISO = 5300.0         # m of surface per unit areal shortening (Airy, 35 km crust, 2.8/3.3)
LOSS = 0.55            # share of the shortened area that goes down (underthrusting, escape), not up;
                       # India-Asia: about half of the convergence was never stacked in Tibet
E_COLLAPSE = 0.95      # excess thickness past which the crust spreads sideways
TAU_E = 160.0          # Myr: the new relief wears down (Scotese: Tibet under half by +125)
ALPHA = {              # share of a collision's shortening taken by the FIRST plate
    ("INDIA", "EURASIA"): 0.25, ("AUSTRALIA", "EURASIA"): 0.30, ("AFRICA", "EURASIA"): 0.35,
    ("ARABIA", "EURASIA"): 0.30, ("AFRICA", "ARABIA"): 0.50, ("ANTARCTICA_E", "EURASIA"): 0.25,
    ("ANTARCTICA_E", "AUSTRALIA"): 0.30, ("ANTARCTICA_W", "AUSTRALIA"): 0.35,
    ("BAJA", "NORTH_AMERICA"): 0.70, ("NORTH_AMERICA", "AFRICA"): 0.55,
    ("SOUTH_AMERICA", "AFRICA"): 0.55, ("SOUTH_AMERICA", "ANTARCTICA_E"): 0.60,
    ("ANTARCTICA_W", "ANTARCTICA_E"): 0.60,
}


def _alpha(a, b):
    if (a, b) in ALPHA:
        return ALPHA[(a, b)]
    if (b, a) in ALPHA:
        return 1.0 - ALPHA[(b, a)]
    return 0.5


class State:
    """Per-plate inverse maps W (material point at each position of the plate's
    own frame) and excess crustal thickness E, on the WH x WW grid."""

    def __init__(self):
        Q, _, _ = grid_dirs(WH, WW)
        self.Q = np.moveaxis(Q, -1, 0).astype(np.float32)          # (3, WH, WW)
        self.W = {p: self.Q.copy() for p in PLATES}
        self.E = {p: np.zeros((WH, WW), np.float32) for p in PLATES}
        self.t = 0.0

    def copy_arrays(self):
        return ({p: self.W[p] - self.Q for p in PLATES}, {p: self.E[p].copy() for p in PLATES})


def _world_masks(state, t, X, pid, cont):
    """Each plate's continental material, in the world frame at time t (WH x WW).
    The masks carry, as `.full`, each plate's material of either kind."""
    out = _Masks()
    for p in PLATES:
        R = rot(p, t)
        q = np.einsum("ij,jhw->ihw", R.T, X)                        # world -> plate frame
        m = sample(state.W[p], np.moveaxis(q, 0, -1))              # material point
        m = np.moveaxis(m, 0, -1)
        owner = sample(pid.astype(np.float32), m, order=0).astype(np.int16)
        c = sample(cont.astype(np.float32), m, order=0) > 0.5
        out.full[p] = owner == PI[p]
        out[p] = out.full[p] & c
    return out


class _Masks(dict):
    def __init__(self):
        super().__init__()
        self.full = {}


def _edt_km(mask, lat_c, dy_km):
    dx_km = dy_km * max(math.cos(math.radians(lat_c)), 0.15)
    return distance_transform_edt(mask, sampling=(dy_km, dx_km))


def _collide(state, t, masks, X, LAT):
    """Resolve the overlaps the last rigid step made. Returns per-plate world
    displacement fields (km, 3-vectors) for the plates that yield."""
    dy_km = math.radians(180.0 / WH) * RE
    disp = {}
    names = [p for p in PLATES if masks[p].any()]
    for ia in range(len(names)):
        for ib in range(ia + 1, len(names)):
            A, B = names[ia], names[ib]
            O = masks[A] & masks[B]
            if O.sum() < 3:
                continue
            lab, n = cclabel(O)
            for k in range(1, n + 1):
                comp = lab == k
                if comp.sum() < 2:
                    continue
                ys, xs = np.nonzero(comp)
                lat_c = float(LAT[ys, xs].mean())
                pad_y = int(1.6 * W_DEF / dy_km) + 2
                pad_x = int(pad_y / max(math.cos(math.radians(lat_c)), 0.2)) + 2
                y0, y1 = max(0, ys.min() - pad_y), min(WH, ys.max() + pad_y + 1)
                # longitude window may wrap: roll the component to the middle
                shift = WW // 2 - int(np.median(xs))
                xs_r = (xs + shift) % WW
                x0, x1 = max(0, xs_r.min() - pad_x), min(WW, xs_r.max() + pad_x + 1)
                sl = (slice(y0, y1), slice(x0, x1))
                roll = lambda a: np.roll(a, shift, axis=-1)[..., y0:y1, x0:x1]
                mA, mB, o = roll(masks[A]), roll(masks[B]), roll(comp)
                # WHAT YIELDS IS THE PLATE'S WHOLE LEADING EDGE, its marginal
                # seas with its continents. The overlap is between continents,
                # but pushing only the continental cells shoved each block back
                # while the sea floor of the same plate round it stayed, which
                # sheared every block's edge: across Indonesia, a hundred small
                # blocks, that combed Asia and Australia into each other in
                # long feathers of land and sea.
                fA, fB = roll(masks.full[A]), roll(masks.full[B])
                dA = _edt_km(mA, lat_c, dy_km)
                dB = _edt_km(mB, lat_c, dy_km)
                delta = np.where(o, dA + dB, 0.0)
                # the penetration, smoothed ALONG the front: per cell it is a
                # patchwork of distance-transform values, and a displacement
                # that jumps between neighbours has a divergence of order one
                # -- which read as a doubling of the crust in a single Myr
                sig = max(1.0, 120.0 / dy_km)
                num = gaussian_filter(delta, sig, mode="nearest")
                den = gaussian_filter(o.astype(np.float64), sig, mode="nearest")
                delta = np.where(o, num / np.maximum(den, 1e-6), 0.0)
                s, (iy, ix) = distance_transform_edt(~o, sampling=(dy_km, dy_km * max(math.cos(math.radians(lat_c)), 0.15)),
                                                     return_indices=True)
                dnear = delta[iy, ix]
                f = np.clip(1.0 - s / W_DEF, 0.0, 1.0) ** 2
                # THE PUSH IS ALONG THE CONTACT, NOT ALONG THE MOTION. Pushed back
                # along the relative velocity, an oblique or sliding contact was
                # never separated -- the push ran along the boundary -- and the
                # same material was shoved a little further every Myr, into
                # smears thousands of km long (North America's Chukotka ended up
                # 3,800 km inside Siberia). Each plate is pushed out of the
                # other down the gradient of its depth inside it, which always
                # separates them; head-on, that is the convergence direction.
                xc = X[:, ys, xs].mean(axis=1); xc /= np.linalg.norm(xc)
                ec, ncv = tangent_basis(xc)
                dx_km = dy_km * max(math.cos(math.radians(lat_c)), 0.15)
                gyA, gxA = np.gradient(dA)
                gyB, gxB = np.gradient(dB)
                # (east, north) gradients per km; rows run north -> south
                gA = np.array([gxA[o].mean() / dx_km, -gyA[o].mean() / dy_km])
                gB = np.array([gxB[o].mean() / dx_km, -gyB[o].mean() / dy_km])
                aA = _alpha(A, B)
                Xb = roll(X)
                # HOW MUCH TO PUSH: only what the plates' own motion drove in
                # this step. Resolving the whole standing overlap every Myr
                # re-pushed any overlap that could not be undone -- an island of
                # one plate engulfed by another, two plates welded after they
                # met -- a little further each step, for a hundred steps.
                vr = velocity(A, t, xc) - velocity(B, t, xc)
                vr = vr - xc * np.dot(vr, xc)
                for P, gvec, share, m, sgn in ((A, -gB, aA, fA, 1.0), (B, -gA, 1.0 - aA, fB, -1.0)):
                    gl = float(np.linalg.norm(gvec))
                    if gl < 0.25:
                        # an enclosed island or a symmetric overlap: the depth
                        # gradient has no direction; push back along the motion
                        v = -sgn * vr
                        vn = float(np.linalg.norm(v))
                        if vn < 1e-6:
                            continue
                        nvec = v / vn
                    else:
                        nvec = (gvec[0] * ec + gvec[1] * ncv) / gl
                    # convergence of this plate into the other, km per step
                    conv = max(0.0, float(np.dot(sgn * vr, -nvec))) * DT
                    if conv <= 0.0:
                        continue
                    nb = nvec[:, None, None] - Xb * np.einsum("i,ihw->hw", nvec, Xb)[None]
                    nb /= np.maximum(np.linalg.norm(nb, axis=0, keepdims=True), 1e-12)
                    sign = 1.0
                    mag = np.minimum(share * dnear, 1.5 * share * conv) * f * m
                    if not mag.any():
                        continue
                    blk = (sign * mag)[None] * nb
                    sg = max(1.0, 60.0 / dy_km)
                    blk = np.stack([gaussian_filter(c, sg, mode="nearest") for c in blk])
                    full = np.zeros((3, WH, WW), np.float32)
                    full[:, y0:y1, x0:x1] = blk
                    u = np.roll(full, -shift, axis=-1)
                    disp[P] = disp.get(P, 0.0) + u
    return disp


def _surface_div(u_t, Qlat):
    """Divergence (dimensionless) of a tangent displacement field u (km, 3-vec)
    on the lat-lon grid of the plate frame."""
    Qv = np.moveaxis(u_t[1], 0, -1)
    e, n = tangent_basis(np.moveaxis(u_t[0], 0, -1))
    ue = (Qv * e).sum(-1)
    un = (Qv * n).sum(-1)
    lat = np.radians(Qlat)
    cl = np.maximum(np.cos(lat), 0.05)
    dlon = math.radians(360.0 / WW)
    dlat = math.radians(180.0 / WH)
    due = (np.roll(ue, -1, 1) - np.roll(ue, 1, 1)) / (2 * dlon)
    uncl = un * cl
    dun = np.zeros_like(un)
    dun[1:-1] = (uncl[:-2] - uncl[2:]) / (2 * dlat)       # rows run north -> south
    return (due + dun) / (RE * cl)


def integrate(verbose=True):
    """Run 0 -> 250 Myr and save the state at every keyframe."""
    storyline()
    pid, cont = present_plates()
    X, _, LAT = grid_dirs(WH, WW)
    X = np.moveaxis(X, -1, 0).astype(np.float32)
    st = State()
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    _save(st, 0)
    nsteps = int(round(SPAN / DT))
    Qlat = LAT
    for k in range(1, nsteps + 1):
        t = k * DT
        masks = _world_masks(st, t, X, pid, cont)
        disp = _collide(st, t, masks, X, LAT)
        for P, u in disp.items():
            R = rot(P, t)
            # displacement into the plate's own frame, sampled at its grid
            xw = np.einsum("ij,jhw->ihw", R, st.Q)                  # plate grid -> world
            uw = sample(u, np.moveaxis(xw, 0, -1))                   # (3, WH, WW) km
            ur = np.einsum("ij,jhw->ihw", R.T, uw)                   # back into plate frame
            # past ~1,000 km of shortening a collision is taken up by
            # underthrusting and escape, not by more of the same crust piling up
            dnow = np.degrees(np.arccos(np.clip((st.W[P] * st.Q).sum(0), -1.0, 1.0))) * 111.2
            ur = ur * np.clip((D_MAX - dnow) / 250.0, 0.0, 1.0)[None]
            # semi-Lagrangian: the material at q now came from q - u
            back = st.Q - ur / RE
            back /= np.maximum(np.linalg.norm(back, axis=0, keepdims=True), 1e-12)
            bv = np.moveaxis(back, 0, -1)
            Wn = sample(st.W[P], bv)
            Wn /= np.maximum(np.linalg.norm(Wn, axis=0, keepdims=True), 1e-12)
            En = sample(st.E[P], bv)
            div = _surface_div((st.Q, ur), Qlat)
            st.W[P] = Wn.astype(np.float32)
            st.E[P] = (En + np.clip(-(1.0 - LOSS) * div, 0.0, 0.08)).astype(np.float32)
        for P in PLATES:
            E = st.E[P]
            if E.max() > E_COLLAPSE:
                ex = np.maximum(E - E_COLLAPSE, 0.0)
                sp = gaussian_filter(ex, (1.0, 1.0), mode=("nearest", "wrap"))
                E = E - 0.5 * ex + 0.5 * sp
            st.E[P] = (E * math.exp(-DT / TAU_E)).astype(np.float32)
        if k % int(STEP / DT) == 0:
            _save(st, t)
            if verbose:
                ov = sorted(((int((masks[a] & masks[b]).sum()), a, b) for ia, a in enumerate(PLATES)
                             for b in PLATES[ia + 1:]), reverse=True)[:3]
                print("      overlaps: " + ", ".join("%s-%s %d" % (a[:5], b[:5], n) for n, a, b in ov if n), flush=True)
                emax = max(float(st.E[p].max()) for p in PLATES)
                print("  +%3d Myr  yielding %-40s  E max %.2f  [%.0fs]"
                      % (t, ",".join(sorted(disp))[:40], emax, time.time() - t0), flush=True)
    return st


def _save(st, t):
    dW, E = st.copy_arrays()
    np.savez_compressed(os.path.join(CACHE, "state_%03d.npz" % int(round(t))),
                        fp=np.array(fingerprint()),
                        **{"dW_" + p: dW[p].astype(np.float16) for p in PLATES},
                        **{"E_" + p: E[p].astype(np.float16) for p in PLATES})


RIGID = False   # debug: render without the deformation (storyline iteration)


def load_state(t):
    t = int(round(abs(t)))
    key = ("state", t)
    if key in _S:
        return _S[key]
    if RIGID:
        Q, _, _ = grid_dirs(WH, WW)
        Q = np.moveaxis(Q, -1, 0).astype(np.float32)
        _S[key] = ({p: Q for p in PLATES}, {p: np.zeros((WH, WW), np.float32) for p in PLATES})
        return _S[key]
    path = os.path.join(CACHE, "state_%03d.npz" % t)
    if not os.path.exists(path):
        raise SystemExit("future_tectonics: no integrated state at +%d -- run --integrate" % t)
    d = np.load(path)
    # The deformation belongs to one storyline and one set of constants. A
    # state integrated before an edit to either still loads and still looks
    # plausible -- the plates simply carry the OLD collisions -- so it is
    # refused, not used: re-run --integrate.
    fp = str(d["fp"]) if "fp" in d.files else "none"
    if fp != fingerprint():
        raise SystemExit("future_tectonics: state at +%d was integrated for storyline %s, "
                         "the code now describes %s -- run --integrate" % (t, fp, fingerprint()))
    Q, _, _ = grid_dirs(WH, WW)
    Q = np.moveaxis(Q, -1, 0).astype(np.float32)
    W = {p: Q + d["dW_" + p].astype(np.float32) for p in PLATES}
    E = {p: d["E_" + p].astype(np.float32) for p in PLATES}
    _S[key] = (W, E)
    return W, E


# ---------------------------------------------------------- active margins
#
# Where ocean floor goes down beneath a continent, the continent's edge grows
# an Andean-type range: volcanoes and a thickened crust 100-250 km inland.
# Which margins are active, and when, follows Scotese's stages (the numbers in
# brackets are his maps): the Pacific "Ring of Fire" stays active throughout
# and becomes the "New Ring of Fire" round Pangea Proxima [11], so the Andes
# and the Cordillera are MAINTAINED rather than worn away; the Atlantic margins
# of the Americas turn active at +25 ("subduction begins along eastern South
# America ... eastern North America and eastern Greenland" [2]; "Boston, New
# York City and Washington D.C. are carried skyward by an erupting volcanic
# mountain chain"); southern Africa at +75 [4]; East Antarctica's trailing,
# southern edge at +150 [7]. Each ends when the ocean it consumes is gone.
#   (plate, lon0, lon1, lat0, lat1 in today's coordinates, t_on, t_off, peak m, kind,
#    facing azimuth deg, half-angle deg)
#
# THE BOX CHOOSES THE STRETCH OF COAST, THE FACING CHOOSES THE COAST. Until
# 3.16 the arc rose by distance from ANY coast inside a hard box, so the Gulf
# of Mexico raised the New England arc across Georgia and the box's own edge
# at 83 W stood in the terrain as a 1,000 km ruler-straight scarp, carried all
# the way to Pangaea Proxima. A margin is now measured from the coast in its
# box that faces the ocean going down beneath it (outward normal within the
# half-angle of the facing azimuth), and the box fades over its outer 3
# degrees, so an arc ends in a rounded tip where its trench does.
ACTIVE_MARGINS = [
    ("NORTH_AMERICA", -170, -104, 14, 72, 0, 250, 0, "keep", -125, 80),     # Cascadia..Aleutians: S, SW, W
    ("SOUTH_AMERICA", -82, -64, -57, 13, 0, 250, 0, "keep", -100, 70),      # the Andes' Pacific coast
    ("EURASIA", 125, 180, 28, 66, 0, 250, 0, "keep", 110, 80),              # Japan, Kurils, Kamchatka
    ("NORTH_AMERICA", -83, -52, 24, 52, 25, 235, 2800, "arc", 110, 75),     # the New England arc
    ("NORTH_AMERICA", -46, -17, 59, 83, 25, 235, 2200, "arc", 100, 75),     # east Greenland
    ("SOUTH_AMERICA", -61, -34, -42, 3, 25, 240, 2600, "arc", 90, 80),      # the Brazilian arc
    ("AFRICA", 14, 36, -36, -27, 75, 240, 2000, "arc", 180, 70),            # the Cape
    ("ANTARCTICA_E", 145, 180, -86, -66, 150, 250, 2200, "arc", 100, 80),   # Victoria Land, Ross side
    ("ANTARCTICA_E", -40, 0, -86, -68, 150, 250, 2200, "arc", -30, 80),     # Coats Land, Weddell side
]
ARC_RISE = 40.0          # Myr for an arc to build to its height
ARC_FALL = 60.0          # e-folding of its decay once its ocean has closed
BOX_FEATHER = 3.0        # degrees over which a margin's box fades at its edges


def _active_km(i):
    """(distance km inland from margin i's ACTIVE coast, box weight 0..1), on
    today's CH x CW grid. Cached per margin."""
    key = ("active", i)
    if key in _S:
        return _S[key]
    from scipy.ndimage import gaussian_filter, binary_dilation
    plate, lo0, lo1, la0, la1, _t0, _t1, _pk, _kind, face, half = ACTIVE_MARGINS[i]
    z = _down(present_dem(), CH, CW)
    land = z > 0.0
    lat = 90 - (np.arange(CH) + 0.5) / CH * 180
    lon = -180 + (np.arange(CW) + 0.5) / CW * 360
    LON, LAT = np.meshgrid(lon, lat)
    tl = np.clip(np.minimum(LON - lo0, lo1 - LON) / BOX_FEATHER, 0.0, 1.0)
    ta = np.clip(np.minimum(LAT - la0, la1 - LAT) / BOX_FEATHER, 0.0, 1.0)
    wbox = (tl * tl * (3 - 2 * tl)) * (ta * ta * (3 - 2 * ta))
    # outward (seaward) normal of the smoothed land indicator, as an azimuth
    lf = gaussian_filter(land.astype(np.float32), 2.0, mode=("nearest", "wrap"))
    gy, gx = np.gradient(lf)
    east = -gx / np.maximum(np.cos(np.radians(LAT)), 0.05)
    north = gy                       # rows run south
    az = np.degrees(np.arctan2(east, north))
    dif = np.abs((az - face + 180.0) % 360.0 - 180.0)
    coast = land & binary_dilation(~land) & (wbox > 0) & (dif <= half)
    dy = math.radians(180.0 / CH) * RE
    D = np.full((CH, CW), 1e9, np.float32)
    if coast.any():
        # row-wise longitude scaling, as _inland_km
        for b0 in range(0, CH, 60):
            b1 = min(CH, b0 + 60)
            lc = float(lat[(b0 + b1) // 2])
            pad = 40
            y0, y1 = max(0, b0 - pad), min(CH, b1 + pad)
            c3 = np.concatenate([coast[y0:y1]] * 3, 1)
            d = distance_transform_edt(~c3, sampling=(dy, dy * max(math.cos(math.radians(lc)), 0.05)))
            D[b0:b1] = d[b0 - y0:b1 - y0, CW:2 * CW]
    _S[key] = (np.where(land, D, 1e9).astype(np.float32), wbox.astype(np.float32))
    return _S[key]


def margin_fields(t, owner, src, contw):
    """(arc uplift m, keep 0..1) at t for cells with plate `owner` and material
    point `src` (3, h, w). `keep` shields a maintained margin from erosion."""
    h, w = owner.shape
    arc = np.zeros((h, w), np.float32)
    keep = np.zeros((h, w), np.float32)
    P = np.moveaxis(src, 0, -1)
    for i, (plate, lo0, lo1, la0, la1, ton, toff, peak, kind, _f, _h) in enumerate(ACTIVE_MARGINS):
        if t <= ton:
            continue
        mine = owner == PI[plate]
        if not mine.any():
            continue
        Dg, Wg = _active_km(i)
        D = sample(Dg, P)
        wb = sample(Wg, P) * mine * contw
        if not (wb > 0).any():
            continue
        if kind == "keep":
            keep = np.maximum(keep, np.clip(1.0 - D / 400.0, 0.0, 1.0) * wb)
            continue
        a = min((t - ton) / ARC_RISE, 1.0)
        if t > toff:
            a *= math.exp(-(t - toff) / ARC_FALL)
        a = a * a * (3.0 - 2.0 * a) if a < 1.0 else a
        prof = np.exp(-((D - 150.0) / 110.0) ** 2)
        arc = np.maximum(arc, peak * a * prof * wb)
    return arc, keep


# -------------------------------------------------------------------- render

def _frame_fields(t, p):
    """Per plate at t, on its own frame grid (WH x WW): how deep each cell is
    inside the crust the plate claims (grid cells to the nearest cell it does
    not), and how compressed the map is there (material distance per frame
    distance, the larger of the two grid directions). Cached."""
    key = ("frame", int(round(abs(t))), p)
    if key in _S:
        return _S[key]
    W, _ = load_state(t)
    pid, _ = present_plates()
    Wp = W[p]
    m = np.moveaxis(Wp, 0, -1)
    m = m / np.linalg.norm(m, axis=-1, keepdims=True)
    cl = sample(pid.astype(np.float32), m, order=0).astype(np.int16) == PI[p]
    pad = 40
    a = np.concatenate([cl[:, -pad:], cl, cl[:, :pad]], 1)
    depth = distance_transform_edt(a)[:, pad:-pad].astype(np.float32)
    Q, _, _ = grid_dirs(WH, WW)
    Q = np.moveaxis(Q, -1, 0)
    dq_r = np.linalg.norm(np.diff(Q, axis=1), axis=0)
    dq_c = np.linalg.norm(Q - np.roll(Q, 1, axis=2), axis=0)
    dw_r = np.linalg.norm(np.diff(Wp, axis=1), axis=0)
    dw_c = np.linalg.norm(Wp - np.roll(Wp, 1, axis=2), axis=0)
    # (a floor under the grid step: near the poles a meridian step is metres
    # and the float16 storage noise in W alone would read as compression)
    sr = dw_r / np.maximum(dq_r, 1e-9)
    sc = dw_c / np.maximum(dq_c, 0.25 * math.radians(180.0 / WH))
    sr = np.concatenate([sr, sr[-1:]], 0)
    comp = np.maximum(sr, sc).astype(np.float32)
    # DISTORTION: the 2x2 deformation gradient of the map in the local tangent
    # plane, and log(stretch ratio) + |log(area change)| from its singular
    # values -- 0 for a rigid plate, ~0.7 where crust has been squeezed or
    # sheared to half its width. Crust distorted this much has been reworked
    # by the collision; what it carried from today is no longer its surface.
    Wn = Wp / np.linalg.norm(Wp, axis=0, keepdims=True)
    lat = np.radians(90.0 - (np.arange(WH) + 0.5) * 180.0 / WH)
    cl = np.maximum(np.cos(lat), 0.05)[:, None]
    dlat = math.radians(180.0 / WH)
    dlon = math.radians(360.0 / WW)
    dWy = np.zeros_like(Wn)
    dWy[:, 1:-1] = (Wn[:, :-2] - Wn[:, 2:]) / (2 * dlat)       # northward (rows run south)
    dWy[:, 0] = dWy[:, 1]
    dWy[:, -1] = dWy[:, -2]
    dWx = (np.roll(Wn, -1, axis=2) - np.roll(Wn, 1, axis=2)) / (2 * dlon * cl)
    e, nv = tangent_basis(np.moveaxis(Wn, 0, -1))
    e = np.moveaxis(e, -1, 0)
    nv = np.moveaxis(nv, -1, 0)
    a = (dWx * e).sum(0)
    b = (dWy * e).sum(0)
    c = (dWx * nv).sum(0)
    d = (dWy * nv).sum(0)
    S = a * a + b * b + c * c + d * d
    det = np.abs(a * d - b * c)
    disc = np.sqrt(np.maximum(S * S - 4.0 * det * det, 0.0))
    s1 = np.sqrt(np.maximum((S + disc) * 0.5, 1e-12))
    s2 = np.sqrt(np.maximum((S - disc) * 0.5, 1e-12))
    dist = (np.log(s1 / s2) + np.abs(np.log(s1 * s2))).astype(np.float32)
    # the polar rows' longitude derivative is noise over a vanishing step
    dist[np.abs(90.0 - (np.arange(WH) + 0.5) * 180.0 / WH) > 88.0] = 0.0
    _S[key] = (depth, comp, dist)
    return depth, comp, dist


def _pyramid(src_field):
    """The source blurred at 1, 2, 4 and 8 of its own cells (level 0 is the
    source), wrapped in longitude. The last one is cached, keyed on the
    field's CONTENT (a strided checksum): an array's id() is reused once it is
    freed, and a stale pyramid would carry one field's terrain into another."""
    f = np.asarray(src_field, np.float32)
    key = (f.shape, float(np.nansum(f[::37, ::41], dtype=np.float64)),
           float(np.nansum(f[5::53, 3::59] ** 2, dtype=np.float64)))
    hit = _S.get("pyr")
    if hit is not None and hit[0] == key:
        return hit[1]
    lev = [f] + [gaussian_filter(f, s, mode=("nearest", "wrap")) for s in (1.0, 2.0, 4.0, 8.0)]
    _S["pyr"] = (key, lev)
    return lev


def render(t, h, w, source=None, fray=True, combine="max", strain=False):
    """Carry a present-day field to t Myr ahead on an h x w grid.

    Returns (out, owner, src, E_world, cont_world): the carried field (NaN where
    no plate claims the cell -- new ocean), the owning plate index, the material
    point (3, h, w) each cell came from, the excess thickness under it, and
    whether the crust there is continental.

    WHERE TWO PLATES CLAIM ONE CELL (3.16). Continental crust outranks oceanic;
    within a rank the cell goes to the plate it lies DEEPER inside, so an
    overlap the collision has not yet shortened away is split along its medial
    line -- a suture. It used to go to whichever plate carried the higher
    terrain there, and two continents meeting interfingered along every ridge
    of either: Australia and Asia came out combed into a hundred slivers.

    COMPRESSED CRUST IS LOW-PASSED BEFORE IT IS SAMPLED. Where the collision
    has squeezed 400 km of material into 100, each output cell is four source
    cells apart in the material and point-sampling it aliases -- ridges and
    valleys a few cells across become stripes and slivers of land and sea.
    The source is read from a pyramid level matched to the local compression
    (Gaussian sigma of half the material spacing), so a shortened belt comes
    out as the smoothed mass it now is, and the thickening (E) raises it.
    `combine` is kept for callers; claims are always resolved this way.
    strain=True adds a sixth output: the distortion of the crust under each
    cell (see _frame_fields).
    """
    storyline()
    pid, cont = present_plates()
    src_field = present_dem() if source is None else np.asarray(source, np.float32)
    # a field with holes (sea-floor ages: NaN where no crust dates them) is
    # sampled as before, holes and all, and not low-passed
    holes = bool(np.isnan(src_field).any())
    pyr = None if holes else _pyramid(src_field)
    sh = src_field.shape[0]
    W, E = load_state(t)
    X, _, _ = grid_dirs(h, w)
    Xf = X.reshape(-1, 3)
    if fray:
        import precambrian as PRE
        T = Xf.T
        Tc = T.copy()
        for scale, amp, seed in ((2.6, 0.026, 1301), (6.1, 0.013, 1607), (14.3, 0.006, 1913)):
            Tc = Tc + amp * np.stack([PRE.fbm3(T * scale, seed, octaves=2) - 0.5,
                                      PRE.fbm3(T * scale + 4.7, seed + 31, octaves=2) - 0.5,
                                      PRE.fbm3(T * scale + 9.1, seed + 61, octaves=2) - 0.5])
        Xc = (Tc / np.linalg.norm(Tc, axis=0)).T
    else:
        Xc = Xf
    n = Xf.shape[0]
    out = np.full(n, np.nan, np.float32)
    # 2 continental, 1 oceanic, 0 the PACIFIC's ocean floor, -1 unclaimed.
    # The Pacific goes down at every trench round it, today and in Scotese's
    # "New Ring of Fire" alike, so wherever its floor meets another plate's
    # the other plate's is on top. Carried rigidly north-west for 150 Myr,
    # it otherwise lies under all of East Asia and shows through every gap
    # the collision leaves in the continents' claims.
    rank = np.full(n, -1, np.int8)
    deep = np.full(n, -1.0, np.float32)       # how far inside its plate the winning claim is
    owner = np.full(n, -1, np.int16)
    src = np.zeros((n, 3), np.float32)
    Ew = np.zeros(n, np.float32)
    Dw = np.zeros(n, np.float32)
    # material spacing of one output cell, in source cells, at compression 1
    base = (180.0 / h) / (180.0 / sh)
    for p in PLATES:
        R = rot(p, abs(t))
        with np.errstate(all="ignore"):
            q = Xf @ R                        # R^T x, row-wise
        m = sample(W[p], q)
        m = np.moveaxis(m, 0, -1)
        m /= np.linalg.norm(m, axis=-1, keepdims=True)
        with np.errstate(all="ignore"):
            qc = Xc @ R
        mc = np.moveaxis(sample(W[p], qc), 0, -1)
        claims = sample(pid.astype(np.float32), mc, order=0).astype(np.int16) == PI[p]
        if not claims.any():
            continue
        dgrid, cgrid, xgrid = _frame_fields(t, p)
        dp = sample(dgrid, qc)                # frayed like the claim, so the suture is too
        cc = sample(cont.astype(np.float32), m) > 0.5
        r = np.where(cc, 2, 0 if p == "PACIFIC" else 1).astype(np.int8)
        better = claims & ((r > rank) | ((r == rank) & (dp > deep)))
        if not better.any():
            continue
        # the source value, from the pyramid level the compression asks for
        val = sample(src_field if holes else pyr[0], m)
        comp = sample(cgrid, q)
        sig = 0.5 * comp * base                 # wanted blur, source cells
        need = better & (sig > 0.6) & (not holes)
        if need.any():
            lv = np.log2(np.clip(sig[need], 1.0, 8.0))   # 0..3 -> levels 1..4
            i0 = np.floor(lv).astype(int)
            fr = (lv - i0).astype(np.float32)
            mm = m[need]
            acc = np.zeros(mm.shape[0], np.float32)
            for k in range(4):
                sel0 = i0 == k
                sel1 = (i0 + 1 == k) & (fr > 0)
                if sel0.any() or sel1.any():
                    sel = sel0 | sel1
                    v = sample(pyr[k + 1], mm[sel])
                    wgt = np.where(sel0[sel], 1.0 - fr[sel], fr[sel])
                    acc[sel] += wgt * v
            # below one source cell of blur, fade in from the unblurred value
            f0 = np.clip((sig[need] - 0.6) / 0.4, 0.0, 1.0)
            val[need] = (1.0 - f0) * val[need] + f0 * acc
        e = sample(E[p], q)
        if strain:
            Dw = np.where(better, sample(xgrid, q), Dw)
        out = np.where(better, val, out)
        rank = np.where(better, r, rank)
        deep = np.where(better, dp, deep)
        owner = np.where(better, PI[p], owner)
        src[better] = m[better]
        Ew = np.where(better, e, Ew)
    out, owner, src = out.reshape(h, w), owner.reshape(h, w), src.reshape(h, w, 3)
    Ew, rank, Dw = Ew.reshape(h, w), rank.reshape(h, w), Dw.reshape(h, w)
    _mend_tears(out, owner, src, Ew, rank, Dw)
    res = (out, owner, np.moveaxis(src, -1, 0), Ew, rank == 2)
    return res + (Dw,) if strain else res


TEAR_DEG = 0.75


def _mend_tears(out, owner, src, Ew, rank, Dw):
    """Cells inside other plates' crust that nothing but a hole or the
    Pacific's floor claims are tears, not ocean (in place).

    New ocean opens between two plates that move apart. Where the collision
    deformation has pushed a plate's frame over another plate's material, its
    claim test fails in slivers inside the collision zone itself, and the
    slivers took either the new-ocean backdrop or the Pacific floor carried
    beneath -- a ladder of abyssal cracks across Indonesia at +150 that no
    rule downstream could see, since such a cell has no strain of the plates
    round it. A cell whose claim is weak (none, or the Pacific's floor) and
    whose surroundings (~TEAR_DEG) are at least 80% strong claims takes their
    crust: height or age, continental or not by majority, thickening and
    strain by average, and the nearest strong cell's plate and material.
    A rift between two plates keeps its gap (half its surroundings are the
    gap itself); a sliver is mended."""
    h, w = owner.shape
    weak = rank <= 0
    if not weak.any():
        return
    strong = ~weak
    sig = max(1.0, TEAR_DEG / (180.0 / h))
    g = lambda a: gaussian_filter(a.astype(np.float32), sig, mode=("nearest", "wrap"))
    gs = g(strong)
    tear = weak & (gs > 0.8)
    if not tear.any():
        return
    valid = strong & ~np.isnan(out)
    den = g(valid)
    num = g(np.where(valid, out, 0.0))
    fillv = np.where(den > 0.25 * gs, num / np.maximum(den, 1e-6), np.nan)
    ds = np.maximum(gs, 1e-6)
    cfrac = g(rank == 2) / ds
    e_f = g(np.where(strong, Ew, 0.0)) / ds
    d_f = g(np.where(strong, Dw, 0.0)) / ds
    o3 = np.concatenate([weak] * 3, 1)
    _, (iy, ix) = distance_transform_edt(o3, return_indices=True)
    iy = iy[:, w:2 * w]
    ix = ix[:, w:2 * w] % w
    out[tear] = fillv[tear]
    owner[tear] = owner[iy[tear], ix[tear]]
    src[tear] = src[iy[tear], ix[tear]]
    rank[tear] = np.where(cfrac[tear] > 0.5, 2, 1)
    Ew[tear] = e_f[tear]
    Dw[tear] = d_f[tear]


def advance(lon, lat, myr, plate=None):
    """Where today's point sits `myr` ahead: its plate's rotation and the forward
    deformation (the inverse map inverted by fixed point). Returns (lon, lat)."""
    storyline()
    pid, _ = present_plates()
    p0 = pt(lon, lat)
    if plate is None:
        plate = PLATES[int(sample(pid.astype(np.float32), p0, order=0))] \
            if int(sample(pid.astype(np.float32), p0, order=0)) >= 0 else "PACIFIC"
    W, _ = load_state(int(round(myr / STEP)) * STEP)
    q = p0.copy()
    for _ in range(12):
        wq = sample(W[plate], q)
        wq = wq / np.linalg.norm(wq)
        q = q + (p0 - wq)
        q /= np.linalg.norm(q)
    x = rot(plate, myr) @ q
    return tuple(float(v) for v in lonlat(x))


def fingerprint():
    if "fp" in _S:
        return _S["fp"]
    storyline()
    h = hashlib.sha256()
    for p in PLATES:
        for t, R in sorted(KEYS[p], key=lambda k: k[0]):
            h.update(("%s %.3f %s" % (p, t, np.round(R, 7).tolist())).encode())
    h.update(repr((W_DEF, D_MAX, H_ISO, LOSS, E_COLLAPSE, TAU_E, sorted(ALPHA.items()), DT, WH)).encode())
    # ...and the integrator's own code: a change to how collisions push is as
    # much a new state as a change to where the plates go.
    import inspect
    for f in (_rasterise, present_plates, _spline, rot, _alpha, State, _world_masks,
              _edt_km, _collide, _surface_div, integrate):
        h.update(inspect.getsource(f).encode())
    _S["fp"] = h.hexdigest()[:16]
    return _S["fp"]


# --------------------------------------------------------------------- debug

def debug_map(t, path, h=720, w=1440, labels=True):
    """Plate-coloured relief map at t, with the continental outline."""
    from PIL import Image, ImageDraw
    z, owner, src, Ew, cw = render(t, h, w, fray=False)
    rgb = np.zeros((h, w, 3), np.float32)
    ocean = np.isnan(z) | (z < 0)
    rgb[:] = (40, 70, 130)
    for p in PLATES:
        m = (owner == PI[p]) & cw
        rgb[m] = COLOURS[p]
    zz = np.nan_to_num(z, nan=-4000.0) + H_ISO * Ew * cw
    shade = np.clip(0.75 + (np.roll(zz, 1, 1) - np.roll(zz, -1, 1)) / 4000.0, 0.45, 1.25)
    land = (zz > 0)
    rgb = rgb * np.where(land, 1.0, 0.55)[..., None] * shade[..., None]
    mt = np.clip((zz - 1500.0) / 3500.0, 0, 1)
    rgb = rgb * (1 - 0.5 * mt[..., None]) + 255 * 0.5 * mt[..., None]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.text((8, 6), "+%d Myr" % t, fill=(255, 255, 255))
    img.save(path)


def report():
    storyline()
    print("plate speeds (cm/yr at the plate centroid) by stage:")
    for p in PLATES:
        c = centroid(p)
        row = []
        for t in range(0, 250, 25):
            a = rot(p, t) @ c
            b = rot(p, t + 25) @ c
            d = math.degrees(math.acos(np.clip(np.dot(a, b), -1, 1))) * 111.2 * 1e5 / 25e6
            row.append("%4.1f" % d)
        print("  %-14s %s" % (p, " ".join(row)))


if __name__ == "__main__":
    if "--integrate" in sys.argv:
        integrate()
    if "--report" in sys.argv:
        report()
    if "--rigid" in sys.argv:
        globals()["RIGID"] = True
    if "--maps" in sys.argv:
        out = sys.argv[sys.argv.index("--maps") + 1] if len(sys.argv) > sys.argv.index("--maps") + 1 else "."
        for t in range(0, 251, 25):
            debug_map(t, os.path.join(out, "ft_%03d.png" % t))
