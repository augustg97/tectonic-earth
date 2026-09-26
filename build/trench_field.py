"""THE TRENCH AS A DISTANCE (3.17): the alpha channel of every `_f` field.

WHY. A subduction zone is the sharpest thing on a sea floor seen from space: a
trench 60-100 km wide and two to four kilometres below the abyssal plain,
hugging the Pacific rim, with the low outer rise seaward of it where the plate
bends before it goes down. The present-day DEM carries the trenches (smoothed:
Peru-Chile about -5,000 m against -4,400 m of floor), but the PaleoDEMs from
5-10 Ma back carry none -- the Andean margin at 22 S is a smooth ramp from
-4,300 m to the coast -- so every past and future ocean met its active margins
with no sign that crust was being consumed there.

WHY NOT CARVE IT INTO `_e`. Every crust-bound field is carried between
keyframes by the displacement warp, and on the ocean side of a trench that is
the SUBDUCTING plate, moving 250-500 km per 5 Myr step. A trench carved into
the elevation would ride that plate: it would slide under the margin and
vanish at the start of each interval while the next keyframe's copy swept in
from hundreds of km out -- two half-depth trenches and a jump at every
crossing, the flutter this release removed elsewhere. A trench belongs to the
plate BOUNDARY, not to either plate.

WHAT. So it ships as a signed distance to the trench AXIS, in km, positive
seaward, on the 1024x512 `_f` grid (whose alpha was free), and the shader
reads it UNWARPED and blends the two keyframes' DISTANCES rather than their
troughs: the linear mix of two signed distance fields of a line in two places
is the distance field of the line in between, so the trench slides smoothly
from one keyframe's position to the next with no ghost. The profile (trough,
steep landward wall, outer rise) is drawn in the shader from the distance and
the local depth, so it costs no texture of its own.

WHERE THE AXIS GOES. The plate model's trench lines (plates_time.json) say
which margins subduct and which way, not where the axis lies to the kilometre:
at 0 Ma they sit 20-60 km from the real trenches. For each point of a line the
profile across it is read from the shipped `_e`: the ocean side is the deeper
one; its far-field depth is the median 150-280 km out; and the axis is placed
just beyond the FOOT of the margin slope, where the floor first reaches the
far-field depth -- which is where real trenches are. A point with no deep
ocean on either side (a continental collision, drawn as 'trench' in the
boundary set) or no step up on the landward side (a line in open water with
no margin or arc) makes no trench. The Precambrian keyframes are skipped:
their boundaries come from a different model from the craton terrain.

ENCODING. Alpha 1 = no trench here; 2..255 = s over +/-S_KM (2 km a level).
Never 0, so the lossless encoder cannot zero the RGB under it (as `_t`), and
a `_f` written before this channel (alpha 255) decodes as s = +S_KM: far
seaward, where the profile is zero -- nothing changes.

    ../venv/bin/python trench_field.py              # every Phanerozoic and future `_f`, alpha rewritten
    ../venv/bin/python trench_field.py 0 100 -150   # some ages
    ../venv/bin/python trench_field.py --show 100   # a PNG of the axis and field over the elevation
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.spatial import cKDTree

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
PLATES = os.path.join(HERE, "..", "web", "plates_time.json")
R_KM = 6371.0
W, H = 1024, 512            # the _f grid
S_KM = 250.0                # encoded +/- range
LAND_KM = 70.0              # how far landward the distance is kept at a margin (the inner wall)
LAND_ARC_KM = 240.0         # ... and behind an intra-oceanic trench, where the shader raises the arc
LAT_KM = 110.0              # beyond a line's end: the cap closes within ~2 trench widths
MIN_LEN_KM = 400.0          # shorter lines are slivers of the topology
END_KM = 150.0              # no arc this close to a line's end
STEP_KM = 12.0              # densification along a line
SNAP_KM = 450.0             # how far seaward a carried line may be moved to its margin
PRE_FROM = 545              # Precambrian boundaries are another model's: no trenches
_plates = None


def _unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def _lonlat(v):
    return np.degrees(np.arctan2(v[..., 1], v[..., 0])), np.degrees(np.arcsin(np.clip(v[..., 2], -1, 1)))


def elevation(age, w=2048, h=1024):
    man = json.load(open(os.path.join(FIELDS, "manifest.json")))
    fr = next(f for f in man if f["age"] == age)
    e = np.asarray(Image.open(os.path.join(FIELDS, fr["e"])).convert("RGB").resize((w, h), Image.BOX))[..., 0]
    d = e.astype(np.float32) / 255.0 * 2.0 - 1.0
    return np.sign(d) * d * d * 8000.0


def _sample(Z, v):
    h, w = Z.shape
    lon, lat = _lonlat(v)
    x = ((lon + 180.0) / 360.0 * w - 0.5)
    y = np.clip((90.0 - lat) / 180.0 * h - 0.5, 0, h - 1.001)
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    x0 %= w
    x1 = (x0 + 1) % w
    y1 = np.minimum(y0 + 1, h - 1)
    return ((Z[y0, x0] * (1 - fx) + Z[y0, x1] * fx) * (1 - fy)
            + (Z[y1, x0] * (1 - fx) + Z[y1, x1] * fx) * fy)


# ------------------------------------------------ the lines, in the TERRAIN's frame
# plates_time.json is Merdith et al. (2021) in Merdith's own reference frame;
# the terrain is PALEOMAP's. They agree at 0 Ma and part fast -- the share of
# trench vertices that fall on dry land goes 19% at 0 Ma, 26% at 5, 33% at 20,
# 41% at 150 -- so the Farallon trench at 100 Ma lies nowhere near the
# PALEOMAP Cordillera. Each subduction sub-segment is therefore carried to the
# present on its OVERRIDING plate by Merdith's rotations, and back out to the
# keyframe by PALEOMAP's rotation of whatever plate holds that ground today
# (the app's own slot raster and platerot.json). It arrives with its polarity:
# the overriding side is known, not guessed from depth.
MERDITH = os.path.join(HERE, "..", "data", "merdith2021", "SM2_X")
ROTJSON = os.path.join(HERE, "..", "web", "platerot.json")
CACHE = os.path.join(HERE, "cache", "trench")
_rot = _slot0 = _prot = None


def _rotmat(ax, ang):
    ax = np.asarray(ax, np.float64)
    n = np.linalg.norm(ax)
    if n < 1e-12 or abs(ang) < 1e-12:
        return np.eye(3)
    k = ax / n
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def _merdith_segments(age):
    """[(points (n,3) in Merdith's frame at `age`, overriding plate id, overriding polygon)]."""
    import pygplates
    global _rot
    if _rot is None:
        _rot = pygplates.RotationModel(os.path.join(MERDITH, "1000_0_rotfile_Merdith_et_al.rot"))
    topo = [os.path.join(MERDITH, f) for f in (
        "1000-410-Topologies_Merdith_et_al.gpml", "1000-410-Convergence_Merdith_et_al.gpml",
        "1000-410-Divergence_Merdith_et_al.gpml", "1000-410-Transforms_Merdith_et_al.gpml",
        "410-250_plate_boundaries_Merdith_et_al.gpml", "250-0_plate_boundaries_Merdith_et_al.gpml",
        "TopologyBuildingBlocks_Merdith_et_al.gpml")]
    resolved, shared = [], []
    pygplates.resolve_topologies(topo, _rot, resolved, float(age), shared)
    out = []
    for sec in shared:
        ft = sec.get_feature().get_feature_type().to_qualified_string().split(":")[-1]
        if ft != "SubductionZone":
            continue
        for sub in sec.get_shared_sub_segments():
            try:
                r = sub.get_overriding_and_subducting_plates()
            except Exception:                                   # noqa: BLE001
                r = None
            if not r:
                continue
            over = r[0]
            pid = over.get_feature().get_reconstruction_plate_id()
            xyz = np.asarray(sub.get_resolved_geometry().to_xyz_list(), np.float64)
            if len(xyz) >= 2:
                out.append((xyz, pid, over.get_resolved_boundary()))
    return out


def terrain_lines(age):
    """[(points (n,3), overriding-side unit normals (n,3))] in the terrain's frame."""
    import pygplates
    global _slot0, _prot
    os.makedirs(CACHE, exist_ok=True)
    cf = os.path.join(CACHE, "t_%04d.npz" % age if age >= 0 else "t_m%04d.npz" % -age)
    if os.path.exists(cf):
        z = np.load(cf, allow_pickle=True)
        return list(zip(z["P"], z["O"]))
    import plate_field as PF
    import paleo_tracks as PT
    if _slot0 is None:
        # PALEOMAP's own plate ids at 0 Ma and its rotation model -- NOT the
        # app's slot raster, whose slots are re-ranked by area in every keyframe
        # (slot 3 at 0 Ma is not slot 3 at 30 Ma)
        _slot0 = PF.plate_raster(0.0)
        _prot = pygplates.RotationModel(PT.ROT)
    ids0, cov0 = _slot0
    sh, sw = ids0.shape
    out = []
    for xyz, pid, poly in _merdith_segments(age):
        pts = _densify(xyz)
        tan = np.gradient(pts, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-12)
        nor = np.cross(pts, tan)
        nor /= np.maximum(np.linalg.norm(nor, axis=1, keepdims=True), 1e-12)
        # which side is the overriding plate: probe 80 km each way
        th = 80.0 / R_KM
        pr_p = np.cos(th) * pts + np.sin(th) * nor
        pr_m = np.cos(th) * pts - np.sin(th) * nor
        mid = len(pts) // 2
        inside_p = sum(poly.is_point_in_polygon(pygplates.PointOnSphere(*pr_p[i])) for i in (0, mid, len(pts) - 1))
        inside_m = sum(poly.is_point_in_polygon(pygplates.PointOnSphere(*pr_m[i])) for i in (0, mid, len(pts) - 1))
        over_dir = 1.0 if inside_p >= inside_m else -1.0
        probe = pr_p if over_dir > 0 else pr_m
        # the PALEOMAP plate is looked up well inside the overriding plate: 80 km
        # from the Andean trench is still offshore, in the Nazca slot, and Nazca's
        # rotation threw the 30 Ma trench 1,100 km out into the Pacific
        th2 = 250.0 / R_KM
        deep_probe = np.cos(th2) * pts + np.sin(th2) * nor * over_dir
        # to the present on the overriding plate (Merdith) ...
        pole, ang = _rot.get_rotation(0.0, pid, float(age)).get_euler_pole_and_angle()
        R0 = _rotmat(pole.to_xyz(), ang)
        pts0, probe0 = pts @ R0.T, probe @ R0.T
        # ... and out to the keyframe on whatever PALEOMAP plate holds that ground today
        lon, lat = _lonlat(deep_probe @ R0.T)
        xi = np.clip(((lon + 180.0) / 360.0 * sw).astype(int), 0, sw - 1)
        yi = np.clip(((90.0 - lat) / 180.0 * sh).astype(int), 0, sh - 1)
        cv = cov0[yi, xi]
        if not cv.any():
            continue
        vals, cnt = np.unique(ids0[yi, xi][cv], return_counts=True)
        pm = int(vals[np.argmax(cnt)])                     # one plate per sub-segment: no tearing
        ax, an = PF.euler(_prot, pm, float(age), 0.0)      # present -> keyframe, PALEOMAP
        P = PF.rodrigues(pts0, ax, an)
        Pr = PF.rodrigues(probe0, ax, an)
        P /= np.linalg.norm(P, axis=1, keepdims=True)
        t2 = np.gradient(P, axis=0)
        t2 /= np.maximum(np.linalg.norm(t2, axis=1, keepdims=True), 1e-12)
        n2 = np.cross(P, t2)
        n2 /= np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-12)
        sgn = np.sign(((Pr - P) * n2).sum(1))
        sgn[sgn == 0] = 1.0
        out.append((P, n2 * sgn[:, None]))
    np.savez(cf, P=np.array([o[0] for o in out], dtype=object), O=np.array([o[1] for o in out], dtype=object))
    return out


def _densify(u):
    pts = [u[0]]
    for a, c in zip(u[:-1], u[1:]):
        ang = np.arccos(np.clip(np.dot(a, c), -1.0, 1.0))
        n = max(1, int(ang * R_KM / STEP_KM))
        for k in range(1, n + 1):
            t = k / float(n)
            v = (np.sin((1 - t) * ang) * a + np.sin(t * ang) * c) / np.sin(ang) if ang > 1e-9 else c
            pts.append(v / np.linalg.norm(v))
    return np.asarray(pts)


def _lines(age):
    global _plates
    if _plates is None:
        _plates = json.load(open(PLATES))
    fr = _plates.get(str(int(age)))
    out = []
    for b in (fr or {}).get("b", ()):
        if b.get("c") != "trench" or len(b["p"]) < 2:
            continue
        u = _unit(*np.asarray(b["p"], np.float64).T)
        pts = [u[0]]
        for a, c in zip(u[:-1], u[1:]):
            ang = np.arccos(np.clip(np.dot(a, c), -1.0, 1.0))
            n = max(1, int(ang * R_KM / STEP_KM))
            for k in range(1, n + 1):
                t = k / float(n)
                # slerp, so a long segment stays on the sphere
                if ang > 1e-9:
                    v = (np.sin((1 - t) * ang) * a + np.sin(t * ang) * c) / np.sin(ang)
                else:
                    v = c
                pts.append(v / np.linalg.norm(v))
        if len(pts) >= 3:
            out.append(np.asarray(pts))
    return out


def axis(age, Z=None):
    """(axis points, seaward normals, tangents) as unit vectors: the subduction
    lines of this age in the terrain's frame, the axis moved to the foot of the
    margin slope."""
    if age >= PRE_FROM:
        return np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 3)), np.zeros(0)
    if Z is None:
        Z = elevation(age)
    if age >= 0:
        segs = [(P, -O) for P, O in terrain_lines(age)]      # polarity known: seaward = away from the overriding plate
    else:
        segs = [(P, None) for P in _lines(age)]             # the future engine's own lines: side from depth
    X = np.arange(-300.0, 700.1, 5.0)                       # km across the line
    A, N, T, L = [], [], [], []
    for P, sea in segs:
        if len(P) < 3:
            continue
        tan = np.gradient(P, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-12)
        nor = np.cross(P, tan)
        nor /= np.maximum(np.linalg.norm(nor, axis=1, keepdims=True), 1e-12)
        th = X / R_KM
        prof = _sample(Z, np.cos(th)[None, :, None] * P[:, None, :] + np.sin(th)[None, :, None] * nor[:, None, :])
        if sea is None:
            near_p = prof[:, (X >= 30) & (X <= 200)].mean(1)
            near_m = prof[:, (X <= -30) & (X >= -200)].mean(1)
            sgn = np.where(near_p <= near_m, 1.0, -1.0)     # the deeper side is the one going down
        else:
            sgn = np.where((sea * nor).sum(1) >= 0, 1.0, -1.0)
        # re-sample so + is seaward (X is not symmetric, so flip by sampling -X)
        prof_o = np.where(sgn[:, None] > 0, prof, _sample(
            Z, np.cos(th)[None, :, None] * P[:, None, :] - np.sin(th)[None, :, None] * nor[:, None, :]))
        # THE SEAWARD SNAP. Merdith's overriding margins include terranes that
        # PALEOMAP accretes later, so a carried line can sit inland of the
        # keyframe's coast. Walk seaward to the first deep water (up to
        # SNAP_KM), take the far-field depth beyond it, and put the axis at the
        # foot of the slope that leads down to it -- where real trenches are.
        # A margin or arc behind (a real step up from the abyss) says it is a
        # continental or arc margin; open ocean on both sides is an
        # intra-oceanic zone, whose arc the PaleoDEMs do not draw, and the
        # line itself is then the best estimate.
        xa = np.full(len(P), np.nan)
        arcless = np.zeros(len(P), bool)
        for i in range(len(P)):
            deep = np.nonzero((X >= -150) & (X <= SNAP_KM) & (prof_o[i] < -2500.0))[0]
            if not len(deep):
                continue
            xd = X[deep[0]]
            fw = (X >= xd + 80.0) & (X <= xd + 250.0)
            far = np.median(prof_o[i, fw])
            if not far < -2500.0:
                continue
            behind = (X >= xd - 300.0) & (X <= xd - 20.0)
            margin = behind.any() and prof_o[i, behind].max() > far + 1500.0
            if margin:
                thr = far + 0.12 * abs(far)
                ft = np.nonzero((X >= xd - 150.0) & (prof_o[i] <= thr))[0]
                if len(ft):
                    xa[i] = min(X[ft[0]] + 12.0, SNAP_KM)
            elif xd <= 0.0:
                xa[i] = 0.0
                arcless[i] = True
        good = np.isfinite(xa)
        if good.sum() < 3:
            continue
        # the axis runs along the line smoothly: fill the gaps, median then mean
        xi = np.interp(np.arange(len(P)), np.nonzero(good)[0], xa[good])
        xi = uniform_filter1d(median_filter(xi, size=9, mode="nearest"), 7, mode="nearest")
        seaward = nor * sgn[:, None]
        keep = good
        if sea is None:
            # a guessed side that flips along the line would fold the field over itself
            maj = 1.0 if (sgn[good] > 0).mean() >= 0.5 else -1.0
            keep = good & (sgn == maj)
        th = xi / R_KM
        ax = np.cos(th)[:, None] * P + np.sin(th)[:, None] * seaward
        ax /= np.linalg.norm(ax, axis=1, keepdims=True)
        # distance along the line from its nearer end: a line shorter than
        # MIN_LEN_KM is a sliver of the topology and makes no trench (it drew as
        # an embossed rectangle), and no arc is raised within END_KM of an end,
        # where it would stop square
        seg = np.r_[0.0, np.cumsum(np.arccos(np.clip((P[1:] * P[:-1]).sum(1), -1, 1)) * R_KM)]
        if seg[-1] < MIN_LEN_KM:
            continue
        d_end = np.minimum(seg, seg[-1] - seg)
        # an arc-less (intra-oceanic) stretch keeps its distance 240 km landward, so
        # the shader can raise the arc there; a margin stops at 70 (the inner wall)
        arcy = (uniform_filter1d(arcless.astype(float), 9, mode="nearest") > 0.5) & (d_end > END_KM)
        land = np.where(arcy, LAND_ARC_KM, LAND_KM)
        A.append(ax[keep]); N.append(seaward[keep]); T.append(tan[keep]); L.append(land[keep])
    if not A:
        return np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 3)), np.zeros(0)
    return np.concatenate(A), np.concatenate(N), np.concatenate(T), np.concatenate(L)


def signed_km(age, Z=None):
    """(H, W) signed distance to the trench axis in km (+ seaward), NaN where none."""
    A, N, T, Lk = axis(age, Z)
    s = np.full((H, W), np.nan, np.float32)
    if len(A) == 0:
        return s
    lon = (np.arange(W) + 0.5) / W * 360.0 - 180.0
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    G = _unit(LON.ravel(), LAT.ravel())
    chord = 2.0 * np.sin(S_KM / R_KM / 2.0)
    dist, idx = cKDTree(A).query(G, distance_upper_bound=chord * 1.05)
    hit = np.isfinite(dist)
    d = G[hit] - A[idx[hit]]
    sv = (d * N[idx[hit]]).sum(1) * R_KM
    lv = np.abs((d * T[idx[hit]]).sum(1)) * R_KM
    # past a line's end the nearest axis point is its endpoint and lv > 0: fold
    # that into the distance, so the trough closes in a round cap instead of a
    # square cut (the arc never reaches an end: see END_KM)
    se = np.sign(sv) * np.sqrt(sv * sv + lv * lv)
    good = (se <= S_KM) & (se >= -Lk[idx[hit]]) & (lv <= LAT_KM)
    flat = s.ravel()
    hi = np.nonzero(hit)[0]
    flat[hi[good]] = se[good]
    return flat.reshape(H, W)


def alpha(age, Z=None):
    s = signed_km(age, Z)
    a = np.ones((H, W), np.uint8)
    v = np.isfinite(s)
    a[v] = np.clip(np.round(2.0 + (s[v] + S_KM) / (2.0 * S_KM) * 253.0), 2, 255).astype(np.uint8)
    return a


def _stem(age):
    if age < 0:
        return "fut_%04d" % (-age)
    return ("pre_%04d" if age > 540 else "phan_%04d") % age


def write(age, quiet=False):
    t0 = time.time()
    path = os.path.join(FIELDS, _stem(age) + "_f.webp")
    rgb = np.asarray(Image.open(path).convert("RGB"))
    assert rgb.shape[:2] == (H, W), (path, rgb.shape)
    a = alpha(age)
    Image.fromarray(np.dstack([rgb, a])).save(path, "WEBP", lossless=True, exact=True, method=6)
    back = np.asarray(Image.open(path))
    assert back.shape[-1] == 4 and np.array_equal(back[..., :3], rgb), "RGB under the alpha changed: " + path
    if not quiet:
        cov = 100.0 * float((a > 1).mean())
        print("  %-18s trench field on %4.1f%% of the grid  %.1fs" % (_stem(age) + "_f", cov, time.time() - t0),
              flush=True)


def show(age, out):
    Z = elevation(age, W, H)
    s = signed_km(age)
    img = np.zeros((H, W, 3), np.float32)
    land = Z > 0
    img[..., 2] = np.clip(0.25 + Z / -8000.0, 0, 1) * (~land)
    img[..., 1] = np.where(land, 0.45, 0.1)
    v = np.isfinite(s)
    prof = np.where(v, np.exp(-(np.nan_to_num(s) / np.where(np.nan_to_num(s) < 0, 16.0, 30.0)) ** 2), 0)
    img[..., 0] = np.maximum(img[..., 0], prof)
    img[v & (np.abs(np.nan_to_num(s)) < 3)] = (1, 1, 0)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out)


def main(argv):
    if argv and argv[0] == "--show":
        age = int(argv[1])
        out = argv[2] if len(argv) > 2 else "trench_%d.png" % age
        show(age, out)
        print(out)
        return 0
    man = json.load(open(os.path.join(FIELDS, "manifest.json")))
    ages = [int(a) for a in argv] or sorted(f["age"] for f in man if f["age"] < PRE_FROM)
    print("trench field -> _f alpha: %d keyframes" % len(ages), flush=True)
    for a in ages:
        write(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
