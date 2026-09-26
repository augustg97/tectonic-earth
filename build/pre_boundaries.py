"""THE PRECAMBRIAN PLATE OVERLAY FROM THE PRECAMBRIAN'S OWN MODEL (3.17).

From 545 to 1000 Ma the terrain is the authored craton poses
(build_synthetic.PRE_KEYS, drawn by precambrian.py), while plates_time.json
carried Merdith et al. (2021)'s boundaries -- a different Rodinia, in a
different frame. No smooth map takes one configuration to the other (a
rubber sheet fitted on the cratons doubled the boundary vertices lying deep
inside them), so the overlay drew subduction zones across cratons and left
the oceans between them without boundaries. The future had the same problem
and the same cure: its overlay comes from its own engine.

HERE THE PLATES ARE THE CRATONS. Each ocean cell joins the craton nearest it;
cratons in contact that move together (relative rotation under MERGE_DEG per
5 Myr) are one plate; the boundaries are the edges of that partition, traced
with marching squares; and each stretch is classed by the relative motion of
the two sides from the same poses that move the terrain (build_preframe
displacement's rotations): closing faster than it slides is a trench,
opening a ridge, the rest transforms. Plate names are the cratons' (a merged
plate takes its largest member's). Every keyframe is independent, like
Merdith's: the overlay steps with the nearest keyframe, as elsewhere.

    ../venv/bin/python pre_boundaries.py            # 545..1000 Ma into plates_time.json
    ../venv/bin/python pre_boundaries.py --show 750 # a PNG of the partition and classes
"""
import json
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree
from skimage import measure

import build_preframe as BP
import precambrian as PRE

HERE = os.path.dirname(os.path.abspath(__file__))
PT_JSON = os.path.join(HERE, "..", "web", "plates_time.json")
W, H = 720, 360
MERGE_DEG = 0.25          # relative rotation per 5 Myr under which touching cratons are one plate
MIN_RUN = 4               # vertices: shorter runs of one class are absorbed by their neighbours
PAD = 12
NAMES = {"EAntarctica": "East Antarctica", "NChina": "North China", "SChina": "South China",
         "WestAfrica": "West Africa", "Kazakh": "Kazakhstania"}
R_KM = 6371.0


def _grid():
    lon = (np.arange(W) + 0.5) / W * 360.0 - 180.0
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    lo, la = np.radians(LON), np.radians(LAT)
    X = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    return LON, LAT, X


def _rot_angle(M):
    return np.degrees(np.arccos(np.clip((np.trace(M) - 1.0) / 2.0, -1.0, 1.0)))


def partition(age):
    """(plate label per cell, {label: craton index list}, per-craton 5 Myr rotation)."""
    own = PRE.craton_owner(age, W, H)
    LON, LAT, X = _grid()
    names = PRE.CRATON_NAMES
    Pa = BP._poses(age)
    other = age + BP.STEP if age + BP.STEP <= 1000 else age - BP.STEP
    Pb = BP._poses(other)
    sgn = 1.0 if other > age else -1.0
    motion = {}
    for k, n in enumerate(names):
        if n in Pa and n in Pb:
            M = Pb[n] @ Pa[n].T
            motion[k] = M if sgn > 0 else M.T
    # every cell joins its nearest craton (on the sphere)
    land = own >= 0
    pts = X[land]
    lab = own[land]
    step = max(1, len(pts) // 60000)
    tree = cKDTree(pts[::step])
    _d, idx = tree.query(X.reshape(-1, 3))
    part = lab[::step][idx].reshape(H, W)
    part[land] = own[land]
    # cratons in contact that move together are one plate (union-find)
    parent = list(range(len(names)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    right = np.roll(part, -1, 1)
    down = np.vstack([part[1:], part[-1:]])
    contact = set()
    for A, B, both in ((part, right, land & np.roll(land, -1, 1)), (part, down, land & np.vstack([land[1:], land[-1:]]))):
        m = both & (A != B)
        for i, j in set(zip(A[m].ravel().tolist(), B[m].ravel().tolist())):
            contact.add((min(i, j), max(i, j)))
    for i, j in contact:
        if i in motion and j in motion and _rot_angle(motion[i].T @ motion[j]) < MERGE_DEG:
            parent[find(i)] = find(j)
    plate = np.vectorize(find)(part)
    return plate, motion, own


def _classify(x, n_out, Mi, Mj):
    """Class of a boundary point x (unit vector) with outward normal n_out (from
    plate i toward j), from the two plates' 5 Myr rotations."""
    vi = (Mi @ x) - x
    vj = (Mj @ x) - x
    rel = vj - vi
    rel -= (rel @ x) * x
    sp = np.linalg.norm(rel)
    if sp * R_KM < 2.0:                                   # < 0.4 mm/yr: not a boundary worth a class
        return "transform"
    nrm = rel @ n_out
    if abs(nrm) < 0.5 * sp:
        return "transform"
    return "ridge" if nrm > 0 else "trench"


def _smooth_classes(cls):
    """Absorb runs shorter than MIN_RUN into the class around them."""
    cls = list(cls)
    i = 0
    while i < len(cls):
        j = i
        while j < len(cls) and cls[j] == cls[i]:
            j += 1
        if j - i < MIN_RUN and (i > 0 or j < len(cls)):
            fill = cls[i - 1] if i > 0 else cls[j]
            for k in range(i, j):
                cls[k] = fill
        i = j
    return cls


def boundaries(age):
    plate, motion, own = partition(age)
    labels = sorted(set(plate.ravel().tolist()))
    wrap = np.concatenate([plate[:, -PAD:], plate, plate[:, :PAD]], 1)
    runs = []
    for i in labels:
        mask = (wrap == i).astype(float)
        for c in measure.find_contours(mask, 0.5):
            ys, xs = c[:, 0], c[:, 1] - PAD
            keep = (xs >= 0) & (xs < W)
            if keep.sum() < 3:
                continue
            ys, xs = ys[keep], xs[keep]
            lon = (xs + 0.5) / W * 360.0 - 180.0
            lat = 90.0 - (ys + 0.5) / H * 180.0
            lo, la = np.radians(lon), np.radians(lat)
            V = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
            T = np.gradient(V, axis=0)
            T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
            N = np.cross(V, T)
            N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
            # the side of the contour that is NOT plate i
            th = 1.5 / W * 2 * np.pi
            probe = np.cos(th) * V + np.sin(th) * N
            plo = np.degrees(np.arctan2(probe[:, 1], probe[:, 0]))
            pla = np.degrees(np.arcsin(np.clip(probe[:, 2], -1, 1)))
            px = np.clip(((plo + 180.0) / 360.0 * W).astype(int), 0, W - 1)
            py = np.clip(((90.0 - pla) / 180.0 * H).astype(int), 0, H - 1)
            nb = plate[py, px]
            flip = nb == i
            N[flip] *= -1.0
            probe = np.cos(th) * V + np.sin(th) * N
            plo = np.degrees(np.arctan2(probe[:, 1], probe[:, 0]))
            pla = np.degrees(np.arcsin(np.clip(probe[:, 2], -1, 1)))
            px = np.clip(((plo + 180.0) / 360.0 * W).astype(int), 0, W - 1)
            py = np.clip(((90.0 - pla) / 180.0 * H).astype(int), 0, H - 1)
            nb = plate[py, px]
            cls = []
            for k in range(len(V)):
                j = int(nb[k])
                if j == i or i not in motion or j not in motion:
                    cls.append(None)
                else:
                    cls.append((j, _classify(V[k], N[k], motion[i], motion[j])))
            # one boundary is traced from both sides: keep the lower plate's copy
            cur, pts = None, []
            flat = [c if c is None else c[1] for c in cls]
            flat = _smooth_classes([f or "none" for f in flat])
            for k in range(len(V)):
                key = None if cls[k] is None or cls[k][0] < i else flat[k]
                if key != cur and pts:
                    if cur not in (None, "none") and len(pts) > 1:
                        runs.append({"c": cur, "p": pts})
                    pts = []
                cur = key
                if key not in (None, "none"):
                    pts.append([round(float(lon[k]), 2), round(float(lat[k]), 2)])
            if cur not in (None, "none") and len(pts) > 1:
                runs.append({"c": cur, "p": pts})
    # A SUPERCONTINENT MOVING AS ONE PLATE has no internal boundary, and the
    # model has no oceanic plates to meet it -- but its periphery is where its
    # subduction was (Rodinia's Tonian margins facing Mirovoi, as Pangaea's
    # faced Panthalassa). With a single plate, the continental margin offset
    # ~200 km seaward is drawn as that ring of trenches.
    if len(labels) == 1:
        from scipy.ndimage import binary_dilation
        land = own >= 0
        ring = binary_dilation(np.concatenate([land[:, -PAD:], land, land[:, :PAD]], 1), iterations=4)
        for c in measure.find_contours(ring.astype(float), 0.5):
            ys, xs = c[:, 0], c[:, 1] - PAD
            keep = (xs >= 0) & (xs < W)
            pts = [[round(float((x + 0.5) / W * 360.0 - 180.0), 2), round(float(90.0 - (y + 0.5) / H * 180.0), 2)]
                   for y, x in zip(ys[keep], xs[keep])]
            if len(pts) > 20:
                runs.append({"c": "trench", "p": pts})
    # split at the dateline, thin the vertices
    out = []
    for r in runs:
        seg = [r["p"][0]]
        for p in r["p"][1:]:
            if abs(p[0] - seg[-1][0]) > 180:
                if len(seg) > 1:
                    out.append({"c": r["c"], "p": seg})
                seg = []
            seg.append(p)
        if len(seg) > 1:
            out.append({"c": r["c"], "p": seg})
    for r in out:
        p = r["p"]
        if len(p) > 3:
            r["p"] = [p[0]] + p[1:-1:2] + [p[-1]]
    # plate names: the largest member craton's
    LON, LAT, X = _grid()
    area = np.cos(np.radians(LAT))
    plates = []
    for lab in labels:
        m = plate == lab
        members = [k for k in range(len(PRE.CRATON_NAMES)) if ((own == k) & m).any()]
        if not members:
            continue
        big = max(members, key=lambda k: float(area[own == k].sum()))
        cm = (own >= 0) & m
        v = (X[cm] * area[cm][:, None]).sum(0)
        v /= max(np.linalg.norm(v), 1e-12)
        n = NAMES.get(PRE.CRATON_NAMES[big], PRE.CRATON_NAMES[big])
        if len(members) >= 5:                              # an assembled supercontinent is named as one
            n = "Rodinia" if age > 650 else "Gondwana"
        plates.append({"n": n, "lon": round(float(np.degrees(np.arctan2(v[1], v[0]))), 1),
                       "lat": round(float(np.degrees(np.arcsin(v[2]))), 1),
                       "a": round(float(area[m].sum()) * (4 * np.pi * R_KM ** 2 / area.sum()) / 1e6, 1), "s": 0})
    plates.sort(key=lambda p: -p["a"])
    return out, plates[:7]


def show(age, out):
    from PIL import Image
    plate, _m, own = partition(age)
    rng = np.random.default_rng(1)
    pal = rng.integers(40, 200, (32, 3))
    img = pal[plate % 32].astype(np.uint8)
    img[own >= 0] = np.minimum(255, img[own >= 0].astype(int) + 55).astype(np.uint8)
    runs, _p = boundaries(age)
    col = {"trench": (255, 60, 60), "ridge": (60, 220, 255), "transform": (255, 255, 90)}
    for r in runs:
        for lo, la in r["p"]:
            x = int((lo + 180) / 360 * W) % W
            y = min(H - 1, max(0, int((90 - la) / 180 * H)))
            img[y, x] = col[r["c"]]
    Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save(out)


def main(argv):
    if argv and argv[0] == "--show":
        a = int(argv[1])
        out = argv[2] if len(argv) > 2 else "pre_bounds_%d.png" % a
        show(a, out)
        print(out)
        return 0
    t0 = time.time()
    d = json.load(open(PT_JSON))
    n = 0
    for age in range(545, 1001, 5):
        runs, plates = boundaries(age)
        d[str(age)] = {"b": runs, "p": plates}
        n += 1
    with open(PT_JSON, "w") as fh:
        json.dump(d, fh, separators=(",", ":"))
    print("plates_time.json: %d Precambrian keyframes from the craton model, %.1f min" % (n, (time.time() - t0) / 60))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
