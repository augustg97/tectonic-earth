"""CRUSTAL AGE FROM ISOCHRONS -- the structural replacement for distance-to-ridge.

Everything the sea floor does used to be derived from one question: how far is
this point from the nearest spreading ridge RIGHT NOW. Nature asks nothing of
the sort. Every parcel of ocean crust was created at a ridge at a particular
moment and has been carried away ever since, and what it carries is a frozen
record of the ridge AS IT WAS -- not a function of where the ridge is today.

Three things followed from getting that wrong, and all three were visible:

  * FABRIC ORIENTATION was wrong away from the axis. Abyssal hills lie parallel
    to the ISOCHRON -- the shape the ridge had when that crust formed. Keyed to
    the present ridge they sweep round it in arcs, where a real chart shows dead
    straight parallel combing.

  * FRACTURE ZONES could not persist. The long scars that cross a whole basin on
    a real chart are MATERIAL lines: one transform's entire history, frozen into
    the plate and carried with it. Ours were the Voronoi boundaries of the
    PRESENT segmentation, rebuilt from nothing every keyframe, so they could
    never be older than the frame they were drawn in.

  * THE COORDINATE'S GRADIENT COLLAPSED with range, which is what marbled the
    far field into contour loops and then left it featureless once that was
    capped. Real abyssal hills stay about 5 km apart from the axis all the way
    to the trench, because they are cut at a roughly steady spreading rate; only
    their AMPLITUDE decays, as sediment buries them. Distance-to-ridge conflates
    spacing with amplitude. Age does not: its gradient is 1/(spreading rate),
    which does not decay at all.

THE CONSTRUCTION. Crust at time T with age A sat on a ridge at time T+A. So take
the ridge geometry at T+A and carry it forward to T on each flank's own plate:
that reconstructed line IS the isochron of age A. Do it for every A and the age
grid falls out, and with it the isochron tangent (which is the fabric direction)
and the fracture zones (which are the offsets between neighbouring isochron
segments, carried in the crust exactly as the real ones are).

Crust belongs to a plate, and only the isochrons of THAT plate can have made it,
so the match is done per plate -- a nearest-isochron search over the whole globe
puts a 180 Myr line next to a 20 Myr one and tears the field.

COVERAGE, measured against the Merdith model:

    target      isochron arcs   within 5 deg   within 15 deg
       0 Ma             4370            99%           100%
     150 Ma             1638            93%           100%
     300 Ma             1803            86%           100%
     500 Ma             2329            81%            99%

which is the number that decides whether this is possible at all in deep time.
It is: the model carries enough ridge history to date most of the ocean at every
era. What it cannot do is make deep-time sea floor TRUE -- that crust was
subducted and there is no record of it. It makes it structurally correct, which
is a different and achievable claim.
"""
import os
import math

import numpy as np
import pygplates

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "data", "merdith2021", "SM2_X")
ROT = os.path.join(MODEL, "1000_0_rotfile_Merdith_et_al.rot")
TOPO = [os.path.join(MODEL, f) for f in (
    "1000-410-Topologies_Merdith_et_al.gpml",
    "1000-410-Convergence_Merdith_et_al.gpml",
    "1000-410-Divergence_Merdith_et_al.gpml",
    "1000-410-Transforms_Merdith_et_al.gpml",
    "410-250_plate_boundaries_Merdith_et_al.gpml",
    "250-0_plate_boundaries_Merdith_et_al.gpml",
    "TopologyBuildingBlocks_Merdith_et_al.gpml",
)]
CACHE = os.path.join(HERE, "cache", "age")

# A spreading centre in the model's own vocabulary. ContinentalRift and
# ExtendedContinentalCrust are included because a young ocean basin opens as a
# rift and the model keeps calling it one for a while -- excluding them loses
# the first 20-30 Myr of every basin, which is exactly the crust nearest the
# axis and the most legible on a chart.
RIDGE_TYPES = {"MidOceanRidge", "ContinentalRift", "ExtendedContinentalCrust"}

STEP = 5                 # Myr between isochrons, and between keyframes
MAX_AGE = 200            # Myr; older ocean crust essentially does not survive
SEG_DEG = 0.35           # isochron resampling

_ROTM = None
_RIDGE_CACHE = {}        # t -> [(pid, lon[], lat[], arc_id), ...]
_next_arc = [0]


def rotmodel():
    global _ROTM
    if _ROTM is None:
        _ROTM = pygplates.RotationModel(ROT)
    return _ROTM


def xyz_of(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.sin(la), np.cos(la) * np.sin(lo)], -1)


def _densify(lon, lat, step_deg=SEG_DEG):
    """Resample a lon/lat polyline so nearest-VERTEX distance stands in for
    nearest-SEGMENT distance."""
    lo_out, la_out = [lon[0]], [lat[0]]
    for i in range(1, len(lon)):
        dlon = (lon[i] - lon[i - 1] + 180.0) % 360.0 - 180.0
        d = math.hypot(dlon * math.cos(math.radians((lat[i] + lat[i - 1]) * 0.5)),
                       lat[i] - lat[i - 1])
        n = max(1, min(400, int(d / step_deg)))
        for k in range(1, n + 1):
            f = k / n
            lo_out.append(lon[i - 1] + dlon * f)
            la_out.append(lat[i - 1] + (lat[i] - lat[i - 1]) * f)
    return np.asarray(lo_out), np.asarray(la_out)


def ridges_at(t):
    """Spreading centres at time t, densified, with the plate id of each flank.

    Cached, and that caching is what makes the whole model affordable. Resolving
    topologies costs about a second; a target time needs 41 of them, and there
    are 251 targets, which is ten thousand resolutions and three hours. But the
    SAME time t is needed by 41 different targets, so resolving once per t and
    rotating the cached geometry afterwards turns it into 251 resolutions.
    """
    key = int(round(t))
    if key in _RIDGE_CACHE:
        return _RIDGE_CACHE[key]
    resolved, shared = [], []
    pygplates.resolve_topologies(TOPO, rotmodel(), resolved, float(key), shared)
    out = []
    for s in shared:
        ft = s.get_feature().get_feature_type().to_qualified_string().split(":")[-1]
        if ft not in RIDGE_TYPES:
            continue
        for sub in s.get_shared_sub_segments():
            ll = np.asarray(sub.get_resolved_geometry().to_lat_lon_list(), np.float64)
            if len(ll) < 2:
                continue
            lo, la = _densify(ll[:, 1], ll[:, 0])
            pids = set()
            try:
                for tp in sub.get_sharing_resolved_topologies() or []:
                    pids.add(int(tp.get_feature().get_reconstruction_plate_id()))
            except Exception:
                pass
            if not pids:
                continue
            # One arc id per SUB-SEGMENT: the arcs are what a transform offsets
            # from one another, so a change of arc id across the grain is a
            # fracture zone -- and because the id travels with the crust, that
            # trace persists for as long as the crust does.
            aid = _next_arc[0]; _next_arc[0] += 1
            for pid in pids:
                out.append((pid, lo, la, aid))
    _RIDGE_CACHE[key] = out
    return out


def _rotmat(finite):
    """FiniteRotation -> 3x3, so a whole isochron rotates in one numpy call."""
    pole, ang = finite.get_euler_pole_and_angle()
    x, y, z = pole.to_xyz()
    c, s, C = math.cos(ang), math.sin(ang), 1.0 - math.cos(ang)
    return np.array([
        [x * x * C + c,     x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, y * y * C + c,     y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, z * z * C + c],
    ])


def isochrons_at(T, max_age=MAX_AGE, step=STEP):
    """{plate_id: (xyz[N,3], age[N], arcid[N])} -- every isochron, carried to T."""
    rot = rotmodel()
    per = {}
    for A in range(0, max_age + 1, step):
        t = int(T) + A
        if t > 1000:
            break
        for pid, lo, la, aid in ridges_at(t):
            if A == 0:
                p = xyz_of(lo, la)
            else:
                try:
                    fr = rot.get_rotation(float(T), int(pid), float(t))
                except Exception:
                    continue
                if fr is None:
                    continue
                # pygplates uses (x=lon0/lat0 axis) ordering matching to_xyz
                p = xyz_of(lo, la) @ _rotmat(fr).T
            b = per.setdefault(pid, [[], [], []])
            b[0].append(p)
            b[1].append(np.full(len(lo), float(A), np.float32))
            b[2].append(np.full(len(lo), aid, np.int64))
    return {p: (np.concatenate(v[0]), np.concatenate(v[1]), np.concatenate(v[2]))
            for p, v in per.items() if v[0]}


def plate_ids(T, h, w):
    """Which plate each cell is on at time T. Resolved coarse and upsampled --
    plate polygons are thousands of km across, so nothing is lost, and the
    point-in-polygon test is the one genuinely slow step here."""
    ch, cw = 180, 360
    resolved, shared = [], []
    pygplates.resolve_topologies(TOPO, rotmodel(), resolved, float(T), shared)
    polys = [r for r in resolved if r.get_resolved_boundary() is not None]
    if not polys:
        return np.full((h, w), -1, np.int32)
    pp = pygplates.PlatePartitioner(polys, rotmodel())
    lat = 90.0 - (np.arange(ch) + 0.5) / ch * 180.0
    lon = (np.arange(cw) + 0.5) / cw * 360.0 - 180.0
    small = np.full((ch, cw), -1, np.int32)
    for j in range(ch):
        for i in range(cw):
            pl = pp.partition_point(pygplates.PointOnSphere(float(lat[j]), float(lon[i])))
            if pl is not None:
                small[j, i] = pl.get_feature().get_reconstruction_plate_id()
    jj = (np.arange(h) * ch // h).clip(0, ch - 1)
    ii = (np.arange(w) * cw // w).clip(0, cw - 1)
    return small[jj[:, None], ii[None, :]]


_PART_CACHE = {}


def partitioner(t):
    """Plate partitioner at time t, cached -- plume tracks need one per birth
    time and the same times recur across every target."""
    key = int(round(t))
    if key not in _PART_CACHE:
        resolved, shared = [], []
        pygplates.resolve_topologies(TOPO, rotmodel(), resolved, float(key), shared)
        polys = [r for r in resolved if r.get_resolved_boundary() is not None]
        _PART_CACHE[key] = pygplates.PlatePartitioner(polys, rotmodel()) if polys else None
    return _PART_CACHE[key]


def plume_track(plon, plat, T, max_age=110, step=5):
    """Where a fixed plume's volcanoes have got to by time T.

    THE POINT OF A HOTSPOT is that it does not move with the plate. The plume
    sits in the mantle; the plate slides over it; the volcano built last is
    carried away while a new one grows in its place. That is what makes a chain,
    and it is what the previous version got backwards -- it drew a line outward
    from the plume in the plate-motion direction, which looks similar in one
    frame and is quite wrong across time: the volcanoes stayed put on the map
    while the plate slid under them, so nothing was ever carried anywhere.

    Done properly the chain is not a line drawn from the plume at all. It is the
    set of volcanoes BORN AT the plume at times T+A for every A, each carried
    forward to T on whatever plate happened to be over the plume when it formed.
    Scrub the timeline and every cone now tracks its plate while fresh ones
    appear at the stationary plume, which is the behaviour the Hawaiian-Emperor
    chain is the textbook illustration of.

    Returns [(lon, lat, age_Myr), ...], youngest first.
    """
    rot = rotmodel()
    pt = pygplates.PointOnSphere(float(plat), float(plon))
    out = []
    for A in range(0, max_age + 1, step):
        tb = int(round(T)) + A
        if tb > 1000 or tb < 0:
            break
        pp = partitioner(tb)
        if pp is None:
            break
        pl = pp.partition_point(pt)
        if pl is None:
            continue
        pid = int(pl.get_feature().get_reconstruction_plate_id())
        if A == 0:
            out.append((float(plon), float(plat), 0.0))
            continue
        try:
            fr = rot.get_rotation(float(T), pid, float(tb))
        except Exception:
            continue
        if fr is None:
            continue
        v = xyz_of(np.array([plon]), np.array([plat])) @ _rotmat(fr).T
        v = v[0] / (np.linalg.norm(v[0]) + 1e-12)
        la = math.degrees(math.asin(max(-1.0, min(1.0, float(v[1])))))
        lo = math.degrees(math.atan2(float(v[2]), float(v[0])))
        out.append((lo, la, float(A)))
    return out


def build(T, h=512, w=1024):
    """(age_myr, azimuth_deg, arc_id, dist_deg) for time T. NaN where undatable."""
    from scipy.spatial import cKDTree
    per = isochrons_at(T)
    pid = plate_ids(T, h, w)

    lat1d = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon1d = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon1d, lat1d)
    G = xyz_of(LON, LAT).reshape(-1, 3)

    age = np.full(h * w, np.nan, np.float32)
    arc = np.full(h * w, -1, np.int64)
    dst = np.full(h * w, np.nan, np.float32)
    flat = pid.ravel()
    for p, (xyz, ag, aid) in per.items():
        sel = np.flatnonzero(flat == p)
        if sel.size == 0 or len(xyz) < 4:
            continue
        d, i = cKDTree(xyz).query(G[sel], k=1)
        age[sel] = ag[i]
        arc[sel] = aid[i]
        dst[sel] = np.degrees(2.0 * np.arcsin(np.clip(d * 0.5, 0.0, 1.0)))
    return (age.reshape(h, w), arc.reshape(h, w), dst.reshape(h, w), pid)


def cached(T, h=512, w=1024):
    """build(), memoised to disk -- the expensive part runs once per keyframe."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"age_{int(round(T)):05d}_{h}x{w}.npz")
    if os.path.exists(f):
        z = np.load(f)
        return z["age"], z["arc"], z["dst"], z["pid"]
    a, r, d, p = build(T, h, w)
    np.savez_compressed(f, age=a, arc=r, dst=d, pid=p)
    return a, r, d, p


if __name__ == "__main__":
    import sys, time
    T = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    t0 = time.time()
    age, arc, dst, pid = build(T)
    ok = np.isfinite(age)
    print(f"T={T:.0f} Ma  {time.time()-t0:.1f}s")
    print(f"  dated {100*ok.mean():.0f}% of the globe   "
          f"age {np.nanmin(age):.0f}..{np.nanmax(age):.0f} mean {np.nanmean(age):.0f} Myr")
    print(f"  {len(np.unique(arc[ok]))} distinct isochron arcs represented")
    print(f"  nearest-isochron distance: median {np.nanmedian(dst):.2f} deg, "
          f"p90 {np.nanpercentile(dst,90):.2f} deg")
