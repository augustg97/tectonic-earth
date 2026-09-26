"""The plate boundaries and plate names of the FUTURE keyframes, from the future
engine itself (future_tectonics, 3.16).

Until 3.16 the negative ages of plates_time.json were whatever the retired
build_plates_time.py had left there in July: the present PB2002 network
advected along an optical-flow motion field of the OLD future terrain. The
terrain has since been rebuilt twice; the boundaries were never rebuilt, so the
overlay drew plates the map no longer had. Here they come from the same plate
ownership and the same rotations that built the terrain, so the two cannot
disagree:

  * a boundary is an edge between two plates' crust in FT.render's owner map
    (cells no plate claims -- new ocean -- go to the nearer plate, so a
    spreading gap puts its boundary on its medial line, where a ridge is);
  * its class is the plates' RELATIVE MOTION across it: opening -> ridge,
    closing -> trench, sliding -> transform;
  * an edge across which the two plates no longer move (a suture: India
    against Asia after the storyline welds them) is not a plate boundary and
    is not drawn, and plates that move as one are named as one;
  * Scotese's subduction zones (future_tectonics.ACTIVE_MARGINS: the Ring of
    Fire kept round the Pacific and the new Atlantic arcs) are drawn as
    trenches just offshore of the margin, and a closing edge between two
    plates' OCEAN floor where one of them has such a margin facing it is
    dropped: that ocean is being consumed at the margin, not in mid-ocean.

    ../venv/bin/python build_plates_future.py            # rewrite the future entries
    ../venv/bin/python build_plates_future.py --maps DIR # plus a debug map per 50 Myr
"""
import json
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
H, W = 360, 720                       # 0.5 degree: the overlay is a line drawing
STEP = 5
V_ACTIVE = 5.0                        # km/Myr (0.5 cm/yr): slower than this is a suture
CLASS_COS = 0.42                      # |normal share| above this opens or closes (~65 deg)
MARGIN_OFF_KM = 90.0                  # a trench sits this far off its arc's coast
SUPPRESS_KM = 1500.0                  # closing ocean-ocean edges this near a facing margin are its ocean
MIN_SPECK = 120                       # cells (~360,000 km2): smaller oceanic ownership islands are absorbed

NAMES = {"AFRICA": "Africa", "ARABIA": "Arabia", "EURASIA": "Eurasia", "INDIA": "India",
         "AUSTRALIA": "Australia", "ANTARCTICA_E": "East Antarctica",
         "ANTARCTICA_W": "West Antarctica", "NORTH_AMERICA": "North America",
         "SOUTH_AMERICA": "South America", "PACIFIC": "Pacific", "BAJA": "Baja"}


def _ft():
    import future_tectonics as FT
    FT.storyline()
    return FT


def _grid():
    lat = 90.0 - (np.arange(H) + 0.5) * 180.0 / H
    lon = -180.0 + (np.arange(W) + 0.5) * 360.0 / W
    LON, LAT = np.meshgrid(lon, lat)
    return LON, LAT


def _unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def _tangent(lon, lat):
    """East and north unit vectors at (lon, lat)."""
    lo, la = np.radians(lon), np.radians(lat)
    e = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
    n = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
    return e, n


def owner_at(FT, t):
    """Owner map with every cell assigned (new ocean to the nearer plate), the
    material point each cell came from, and whether it is continental.

    Where an ocean closes, two plates' carried floors overlap and the higher
    value wins cell by cell, so the owner map there is a speckle of both --
    harmless to the terrain (it is all deep floor), but every speck would be
    a little closed plate boundary. Oceanic specks smaller than MIN_SPECK
    cells go to the plate that surrounds them."""
    _, owner, src, _, cont = FT.render(t, H, W, fray=False)
    owner = owner.astype(np.int16)

    def fill(owner, miss):
        o3 = np.concatenate([owner, owner, owner], 1)
        m3 = np.concatenate([miss, miss, miss], 1)
        _, ind = ndimage.distance_transform_edt(m3, return_indices=True)
        return np.where(miss, o3[ind[0], ind[1]][:, W:2 * W], owner)
    if (owner < 0).any():
        owner = fill(owner, owner < 0)
    for _ in range(3):
        speck = np.zeros((H, W), bool)
        for i in np.unique(owner):
            lab, n = ndimage.label(owner == i)
            if n <= 1:
                continue
            sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
            ccont = ndimage.sum(cont, lab, index=np.arange(1, n + 1))
            small = 1 + np.nonzero((sizes < MIN_SPECK) & (ccont < 0.5 * sizes)
                                   | (sizes < MIN_SPECK // 6))[0]
            speck |= np.isin(lab, small)
        if not speck.any():
            break
        owner = fill(owner, speck)
    return owner, src, cont


def _groups(FT, t, owner):
    """Plates that move as one: adjacent and with a relative rotation slower
    than V_ACTIVE at every point they share. Union-find over the edges."""
    parent = list(range(len(FT.PLATES)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    LON, LAT = _grid()
    X = _unit(LON, LAT)
    pairs = set()
    for a, b in ((owner, np.roll(owner, -1, 1)), (owner[:-1], owner[1:])):
        m = a != b
        pairs |= set(zip(a[m].tolist(), b[m].tolist()))
    for i, j in pairs:
        if i < 0 or j < 0 or i == j:
            continue
        pi, pj = FT.PLATES[i], FT.PLATES[j]
        # the largest relative speed along their shared edge
        m = ((owner == i) & ((np.roll(owner, -1, 1) == j) | (np.roll(owner, 1, 1) == j)))
        if not m.any():
            m = (owner == i) & ((np.roll(owner, -1, 0) == j) | (np.roll(owner, 1, 0) == j))
        v = FT.velocity(pj, t, X[m]) - FT.velocity(pi, t, X[m])
        if np.linalg.norm(v, axis=-1).max() < V_ACTIVE:
            parent[find(i)] = find(j)
    return [find(i) for i in range(len(FT.PLATES))]


def _margin_lines(FT, t, owner, src, cont):
    """Trenches of Scotese's active margins at t, off the SAME coast the
    terrain raises its arcs from (FT._active_km: the coast in each margin's
    box that faces the ocean going down beneath it, carried by material
    point so it rides the crust through its deformation), pushed offshore.
    Returns the trench mask and, per margin plate, the ocean it faces (for
    suppressing mid-ocean duplicates)."""
    km_per_cell = 180.0 / H * 111.2
    P = np.moveaxis(src, 0, -1)
    trench = np.zeros((H, W), bool)
    facing = {}
    shore = ndimage.binary_dilation(~cont, iterations=1)
    for i, (p, lo0, lo1, la0, la1, t0, t1, _amp, kind, _f, _h) in enumerate(FT.ACTIVE_MARGINS):
        if not (t0 <= t <= t1):
            continue
        pi = FT.PI[p]
        mine = (owner == pi) & cont
        if mine.sum() < 3:
            continue
        Dg, Wg = FT._active_km(i)
        D = FT.sample(Dg, P)
        wb = FT.sample(Wg, P)
        coast = mine & shore & (D < 1.5 * km_per_cell) & (wb > 0.5)
        if coast.sum() < 3:
            continue
        d = ndimage.distance_transform_edt(~coast) * km_per_cell
        trench |= ~cont & (np.abs(d - MARGIN_OFF_KM) < km_per_cell * 0.75)
        facing[pi] = facing.get(pi, np.zeros((H, W), bool)) | (~cont & (d < SUPPRESS_KM))
    return trench, facing


def _trace(mask):
    """Polylines through a boolean mask, as lists of (row, col): thinned to a
    one-cell 8-connected skeleton first (a rasterised edge is a staircase,
    and every stair was a branch), then walked greedily from endpoints; loops
    are cut anywhere."""
    from collections import defaultdict
    from skimage.morphology import skeletonize
    # thin on a copy tiled across the dateline so a line crossing it stays whole
    wide = np.concatenate([mask[:, -8:], mask, mask[:, :8]], 1)
    mask = skeletonize(ndimage.binary_closing(wide, iterations=1))[:, 8:-8]
    pts = set(zip(*np.nonzero(mask)))
    nb = defaultdict(list)
    for r, c in pts:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    q = (r + dr, (c + dc) % W)
                    if q in pts:
                        nb[(r, c)].append(q)
    seen = set()
    runs = []
    order = sorted(pts, key=lambda p: len(nb[p]))          # endpoints first
    for s in order:
        if s in seen:
            continue
        run = [s]
        seen.add(s)
        cur = s
        while True:
            nxt = [q for q in nb[cur] if q not in seen]
            if not nxt:
                break
            # prefer the 4-neighbour: fewer diagonal zig-zags
            nxt.sort(key=lambda q: abs(q[0] - cur[0]) + min(abs(q[1] - cur[1]), W - abs(q[1] - cur[1])))
            cur = nxt[0]
            seen.add(cur)
            run.append(cur)
        if len(run) >= 3:
            runs.append(run)
    return runs


def _to_ll(run):
    out = []
    for r, c in run:
        lon = -180.0 + (c + 0.5) * 360.0 / W
        lat = 90.0 - (r + 0.5) * 180.0 / H
        out.append([round(lon, 1), round(lat, 1)])
    return out


def _decimate(pts, tol=1.6):
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        q = out[-1]
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) >= tol:
            out.append(p)
    out.append(pts[-1])
    return out


def boundaries(FT, t):
    owner, src, cont = owner_at(FT, t)
    grp = _groups(FT, t, owner)
    LON, LAT = _grid()
    X = _unit(LON, LAT)
    E, N = _tangent(LON, LAT)
    trench, facing = _margin_lines(FT, t, owner, src, cont)

    # edge cells: this cell's plate differs from the one east or south of it
    east = np.roll(owner, -1, 1)
    south = np.concatenate([owner[1:], owner[-1:]], 0)
    other = np.where(east != owner, east, np.where(south != owner, south, -1))
    edge = other >= 0
    g = np.array(grp)
    edge &= g[np.clip(owner, 0, None)] != g[np.clip(other, 0, None)]
    cls = np.full((H, W), -1, np.int8)             # 0 ridge, 1 trench, 2 transform
    rr, cc = np.nonzero(edge)
    if rr.size:
        a = owner[rr, cc]
        b = other[rr, cc]
        x = X[rr, cc]
        v = np.zeros_like(x)
        for i, p in enumerate(FT.PLATES):
            m = b == i
            if m.any():
                v[m] += FT.velocity(p, t, x[m])
            m = a == i
            if m.any():
                v[m] -= FT.velocity(p, t, x[m])
        # the edge normal, from a toward b: the gradient of "is b" smoothed
        ind = np.zeros((H, W), np.float32)
        nrm = np.zeros((rr.size, 2), np.float32)
        for j in np.unique(b):
            ind[:] = (owner == j)
            sm = ndimage.gaussian_filter(ind, 2.0, mode=("nearest", "wrap"))
            gy, gx = np.gradient(sm)
            m = b == j
            coslat = np.cos(np.radians(LAT[rr[m], cc[m]]))
            nrm[m, 0] = gx[rr[m], cc[m]] / np.maximum(coslat, 0.2)   # east
            nrm[m, 1] = -gy[rr[m], cc[m]]                             # north (rows run south)
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
        ve = np.einsum("ij,ij->i", v, E[rr, cc])
        vn = np.einsum("ij,ij->i", v, N[rr, cc])
        # the normal (opening +) and tangential components of the relative
        # motion, averaged ALONG the boundary (~220 km): the normal from a
        # rasterised edge turns every cell, and the class flickered with it
        vN = ve * nrm[:, 0] + vn * nrm[:, 1]
        vT = np.abs(-ve * nrm[:, 1] + vn * nrm[:, 0])
        acc = np.zeros((3, H, W), np.float32)
        acc[0, rr, cc] = vN
        acc[1, rr, cc] = vT
        acc[2, rr, cc] = 1.0
        for k in range(3):
            acc[k] = ndimage.gaussian_filter(acc[k], 4.0, mode=("nearest", "wrap"))
        vN = acc[0, rr, cc] / np.maximum(acc[2, rr, cc], 1e-6)
        vT = acc[1, rr, cc] / np.maximum(acc[2, rr, cc], 1e-6)
        spd = np.hypot(vN, vT)
        along = vN / np.maximum(spd, 1e-9)
        # b moving TOWARD a (against the a->b normal) closes the edge
        c = np.where(along < -CLASS_COS, 1, np.where(along > CLASS_COS, 0, 2)).astype(np.int8)
        c[spd < V_ACTIVE] = -1
        # a closing edge between two plates' OCEAN floor, facing an active
        # margin of either: that ocean goes down at the margin, not here
        ocean = ~cont[rr, cc]
        sup = np.zeros(rr.size, bool)
        for pi, fm in facing.items():
            sup |= fm[rr, cc] & ((a == pi) | (b == pi))
        c[(c == 1) & ocean & sup] = -1
        cls[rr, cc] = c

    runs = []
    for k, name in ((0, "ridge"), (1, "trench"), (2, "transform")):
        m = cls == k
        # a class flickering along one edge: drop runs shorter than ~450 km
        lab, n = ndimage.label(m, structure=np.ones((3, 3)))
        if n:
            sizes = ndimage.sum(m, lab, index=np.arange(1, n + 1))
            m &= np.isin(lab, 1 + np.nonzero(sizes >= 8)[0])
        for run in _trace(m):
            runs.append({"c": name, "p": _decimate(_to_ll(run))})
    for run in _trace(trench & ~ndimage.binary_dilation(cls == 1, iterations=2)):
        runs.append({"c": "trench", "p": _decimate(_to_ll(run))})

    # named plates: one per group, named after its largest member
    cell_km2 = (np.radians(180.0 / H) * 6371.0) * (np.radians(360.0 / W) * 6371.0) * np.cos(np.radians(LAT))
    plates = []
    for root in sorted(set(grp)):
        members = [i for i in range(len(FT.PLATES)) if grp[i] == root]
        m = np.isin(owner, members)
        if not m.any():
            continue
        area = float(cell_km2[m].sum()) / 1e6
        if area < 3.0:
            continue
        # named after the member with the most CONTINENT (the Pangaea Proxima
        # core is Eurasia's plate, not Australia's, whose ocean is larger),
        # with a tenth of the total area to break it for an ocean plate: the
        # Pacific, not the Baja sliver riding it
        big = max(members, key=lambda i: cell_km2[(owner == i) & cont].sum()
                  + 0.1 * cell_km2[owner == i].sum())
        c = (X[m] * cell_km2[m][:, None]).sum(0)
        c /= np.linalg.norm(c)
        lon = float(np.degrees(np.arctan2(c[1], c[0])))
        lat = float(np.degrees(np.arcsin(np.clip(c[2], -1, 1))))
        # a centroid that falls off the plate (a ring-shaped plate) moves to
        # the plate's cell nearest it
        r = int(np.clip((90 - lat) / 180 * H, 0, H - 1))
        cidx = int(((lon + 180) / 360 * W)) % W
        if not m[r, cidx]:
            d = np.einsum("ijk,k->ij", X, c)
            d[~m] = -2
            r, cidx = np.unravel_index(int(np.argmax(d)), d.shape)
            lon = float(LON[r, cidx]); lat = float(LAT[r, cidx])
        plates.append({"n": NAMES[FT.PLATES[big]], "lon": round(lon, 1), "lat": round(lat, 1),
                       "a": round(area, 1), "s": 0,
                       "m": [NAMES[FT.PLATES[i]] for i in members]})
    plates.sort(key=lambda p: -p["a"])
    return runs, plates[:7], owner, cls, trench


def debug_map(FT, t, path, owner, cls, trench):
    from PIL import Image
    rgb = np.zeros((H, W, 3), np.uint8)
    for i, p in enumerate(FT.PLATES):
        rgb[owner == i] = FT.COLOURS[p]
    _, _, _, _, cont = FT.render(t, H, W, fray=False)
    rgb = (rgb * np.where(cont, 1.0, 0.55)[..., None]).astype(np.uint8)
    rgb[cls == 0] = (232, 83, 78)
    rgb[cls == 1] = (89, 176, 214)
    rgb[cls == 2] = (224, 178, 58)
    rgb[trench] = (40, 120, 255)
    Image.fromarray(rgb).resize((W * 2, H * 2), Image.NEAREST).save(path)


def main():
    FT = _ft()
    maps = None
    if "--maps" in sys.argv:
        maps = sys.argv[sys.argv.index("--maps") + 1]
        os.makedirs(maps, exist_ok=True)
    path = os.path.join(WEB, "plates_time.json")
    out = json.load(open(path))
    # the past (Merdith 2021, build_plates_gplates) is kept; every future entry is rewritten
    out = {k: v for k, v in out.items() if int(float(k)) >= 0}
    for t in range(STEP, 251, STEP):
        runs, plates, owner, cls, trench = boundaries(FT, float(t))
        out[str(-t)] = {"b": runs, "p": plates}
        kinds = {}
        for r in runs:
            kinds[r["c"]] = kinds.get(r["c"], 0) + 1
        print("  +%3d Myr  %3d runs %s  plates: %s" % (
            t, len(runs), kinds, ", ".join("%s%s" % (p["n"], "+%d" % (len(p["m"]) - 1) if len(p["m"]) > 1 else "")
                                           for p in plates)), flush=True)
        if maps and t % 50 == 0:
            debug_map(FT, float(t), os.path.join(maps, "plates_%03d.png" % t), owner, cls, trench)
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("plates_time.json: future entries rebuilt from the future engine (%d)" % 50)


if __name__ == "__main__":
    main()
