"""Segment each era into plates, then derive boundaries from the tessellation.

Earlier attempts drew boundaries by thresholding a strain field and thinning
it, which can only ever yield fragments: a threshold crossing is a patch, and
thinning a patch gives a broken crest. Plate boundaries in the real world are
not features in their own right — they are the *edges between plates*. So this
segments the surface into plates first and takes the borders afterwards, which
makes them continuous and closed by construction, exactly like the present-day
PB2002 network.

  1. Strain rate from the derived motion field. Plate interiors deform very
     little; margins concentrate all of it.
  2. Low-strain cells become seeds, connected components become plates, then
     the remaining cells are flooded to the nearest plate so the whole sphere
     is tiled with no gaps.
  3. Borders are traced from the label mosaic, chained into polylines and
     smoothed, so they draw as continuous curves.
  4. Each border is classified by the relative motion of the two plates across
     it: pulling apart is a ridge, closing is a trench, sliding is a transform.
  5. Plates are tracked between keyframes by overlap so identities — and
     therefore names — persist for as long as the plate does.
"""
import numpy as np
from collections import deque

GRID_W, GRID_H = 128, 64
MIN_PLATE_CELLS = 44          # below this a region is absorbed by its neighbour
TARGET_PLATES = (7, 14)       # acceptable plate count; the threshold adapts


# ------------------------------------------------------------ segmentation --
def strain_rate(vx, vy):
    def dx(a): return (np.roll(a, -1, axis=1) - np.roll(a, 1, axis=1)) * 0.5
    def dy(a): return (np.roll(a, -1, axis=0) - np.roll(a, 1, axis=0)) * 0.5
    dudx, dudy = dx(vx), dy(vx)
    dvdx, dvdy = dx(vy), dy(vy)
    div = dudx + dvdy
    shear = np.sqrt((dudy + dvdx) ** 2 + (dudx - dvdy) ** 2)
    return np.sqrt(div ** 2 + shear ** 2), div, shear


def _components(mask):
    """Label connected True cells (4-connected, wrapping in longitude)."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    cur = 0
    for r0 in range(H):
        for c0 in range(W):
            if not mask[r0, c0] or lab[r0, c0]:
                continue
            cur += 1
            q = deque([(r0, c0)])
            lab[r0, c0] = cur
            while q:
                r, c = q.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    rr, cc = r + dr, (c + dc) % W
                    if 0 <= rr < H and mask[rr, cc] and not lab[rr, cc]:
                        lab[rr, cc] = cur
                        q.append((rr, cc))
    return lab, cur


def _flood_fill_rest(lab):
    """Grow labelled regions outward until every cell belongs to one."""
    H, W = lab.shape
    out = lab.copy()
    q = deque()
    for r in range(H):
        for c in range(W):
            if out[r, c]:
                q.append((r, c))
    while q:
        r, c = q.popleft()
        v = out[r, c]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, (c + dc) % W
            if 0 <= rr < H and out[rr, cc] == 0:
                out[rr, cc] = v
                q.append((rr, cc))
    return out


def _absorb_small(lab):
    """Merge undersized regions into whichever neighbour they touch most."""
    H, W = lab.shape
    while True:
        ids, counts = np.unique(lab, return_counts=True)
        small = [i for i, n in zip(ids, counts) if i > 0 and n < MIN_PLATE_CELLS]
        if not small:
            return lab
        tgt = small[0]
        cells = np.argwhere(lab == tgt)
        tally = {}
        for r, c in cells:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, (c + dc) % W
                if 0 <= rr < H:
                    o = lab[rr, cc]
                    if o != tgt:
                        tally[o] = tally.get(o, 0) + 1
        lab[lab == tgt] = max(tally, key=tally.get) if tally else tgt
        if not tally:
            return lab


def segment(vx, vy, conf):
    """Tile the sphere with plates. Returns an int label grid (1..n)."""
    E, div, shear = strain_rate(vx, vy)
    E = E * np.clip(conf * 1.4, 0.15, 1.0)
    lab = None
    # Adapt the interior threshold until the plate count is sensible: too tight
    # and the world is one plate, too loose and it shatters into confetti.
    for pct in (28, 36, 44, 52, 60, 68):
        seeds = E < np.percentile(E, pct)
        l0, n = _components(seeds)
        if n == 0:
            continue
        l1 = _absorb_small(_flood_fill_rest(l0))
        k = len([i for i in np.unique(l1) if i > 0])
        lab = l1
        if TARGET_PLATES[0] <= k <= TARGET_PLATES[1]:
            break
    if lab is None:
        lab = np.ones((GRID_H, GRID_W), np.int32)
    # renumber 1..n
    ids = [i for i in np.unique(lab) if i > 0]
    remap = {v: i + 1 for i, v in enumerate(ids)}
    out = np.zeros_like(lab)
    for v, i in remap.items():
        out[lab == v] = i
    return out


# -------------------------------------------------------------- boundaries --
def _cell_ll(r, c):
    return ((c + 0.5) / GRID_W * 360 - 180, 90 - (r + 0.5) / GRID_H * 180)


def _node_ll(r, c):
    """Grid-corner position (corner r,c is the top-left of cell r,c)."""
    return (c / GRID_W * 360 - 180, 90 - r / GRID_H * 180)


def _chaikin(pts, iters=2, closed=False):
    for _ in range(iters):
        if len(pts) < 3:
            break
        out = []
        n = len(pts)
        rng = range(n) if closed else range(n - 1)
        if not closed:
            out.append(pts[0])
        for i in rng:
            a = pts[i]; b = pts[(i + 1) % n]
            out.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            out.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def trace_boundaries(lab, vx, vy):
    """Chain the borders of the label mosaic into smooth classified polylines."""
    H, W = lab.shape
    # mean velocity per plate, used to classify relative motion across a border
    vel = {}
    for i in [v for v in np.unique(lab) if v > 0]:
        m = lab == i
        vel[i] = (float(vx[m].mean()), float(vy[m].mean()))

    # collect border edges as graph edges between grid corners
    edges = {}          # (nodeA,nodeB) -> (labelL, labelR, orientation)
    adj = {}
    def add(n1, n2, la, lb, horiz):
        key = (n1, n2) if n1 < n2 else (n2, n1)
        if key in edges:
            return
        edges[key] = (la, lb, horiz)
        adj.setdefault(n1, []).append(n2)
        adj.setdefault(n2, []).append(n1)

    for r in range(H):
        for c in range(W):
            a = lab[r, c]
            # vertical edge between (r,c) and (r,c+1): separates left/right
            cc = (c + 1) % W
            if lab[r, cc] != a:
                add((r, cc), (r + 1, cc), a, lab[r, cc], False)
            # horizontal edge between (r,c) and (r+1,c)
            if r + 1 < H and lab[r + 1, c] != a:
                add((r + 1, c), (r + 1, c + 1), a, lab[r + 1, c], True)

    # walk chains: start at junctions (degree != 2), then any leftover loops
    visited = set()
    polylines = []

    def walk(start, nxt):
        chain = [start, nxt]
        prev, cur = start, nxt
        while True:
            key = (prev, cur) if prev < cur else (cur, prev)
            visited.add(key)
            nbrs = [n for n in adj.get(cur, []) if n != prev]
            if len(nbrs) != 1:
                break
            nxt2 = nbrs[0]
            k2 = (cur, nxt2) if cur < nxt2 else (nxt2, cur)
            if k2 in visited:
                break
            chain.append(nxt2)
            prev, cur = cur, nxt2
        return chain

    nodes = list(adj.keys())
    for n in nodes:
        if len(adj[n]) == 2:
            continue
        for m in adj[n]:
            key = (n, m) if n < m else (m, n)
            if key not in visited:
                polylines.append(walk(n, m))
    for key in list(edges.keys()):
        if key in visited:
            continue
        polylines.append(walk(key[0], key[1]))

    out = []
    for chain in polylines:
        if len(chain) < 3:
            continue
        # classify by the relative motion of the plates this chain separates
        das = []
        for i in range(len(chain) - 1):
            k = (chain[i], chain[i + 1]) if chain[i] < chain[i + 1] else (chain[i + 1], chain[i])
            if k in edges:
                das.append(edges[k])
        if not das:
            continue
        la = max(set(d[0] for d in das), key=[d[0] for d in das].count)
        lb = max(set(d[1] for d in das), key=[d[1] for d in das].count)
        if la == lb or la not in vel or lb not in vel:
            continue
        dvx = vel[la][0] - vel[lb][0]
        dvy = vel[la][1] - vel[lb][1]
        # chain direction, then the component of relative motion across it
        p0 = _node_ll(*chain[0]); p1 = _node_ll(*chain[-1])
        tx, ty = p1[0] - p0[0], p1[1] - p0[1]
        tl = np.hypot(tx, ty) + 1e-9
        nx, ny = -ty / tl, tx / tl          # unit normal to the boundary
        opening = dvx * nx + dvy * ny
        sliding = abs(dvx * (tx / tl) + dvy * (ty / tl))
        speed = np.hypot(dvx, dvy)
        if speed < 3:
            continue
        if abs(opening) > sliding * 0.8:
            cls = "ridge" if opening > 0 else "trench"
        else:
            cls = "transform"

        pts = _chaikin([_node_ll(r, c) for (r, c) in chain], 2)
        # Smoothing quadruples the point count; thin it back out again — the
        # curve is what matters, not the sample density.
        thin = [pts[0]]
        for q in pts[1:]:
            px, py = thin[-1]
            if abs(q[0] - px) + abs(q[1] - py) >= 0.9:
                thin.append(q)
        if thin[-1] != pts[-1]:
            thin.append(pts[-1])
        if len(thin) < 3:
            continue
        out.append({"c": cls, "r": round(float(speed), 1),
                    "p": [[round(x, 1), round(y, 1)] for x, y in thin]})
    return out


def plate_info(lab, vx, vy):
    """Centroid, size and mean motion for each plate."""
    H, W = lab.shape
    lon = (np.arange(W) + 0.5) / W * 360 - 180
    lat = 90 - (np.arange(H) + 0.5) / H * 180
    LON, LAT = np.meshgrid(lon, lat)
    w = np.cos(np.radians(LAT))
    info = {}
    for i in [v for v in np.unique(lab) if v > 0]:
        m = lab == i
        ww = w[m]
        # centroid on the sphere, so a plate spanning the seam averages sanely
        la = np.radians(LAT[m]); lo = np.radians(LON[m])
        x = (np.cos(la) * np.cos(lo) * ww).sum(); y = (np.cos(la) * np.sin(lo) * ww).sum()
        z = (np.sin(la) * ww).sum()
        n = np.sqrt(x * x + y * y + z * z) + 1e-9
        info[int(i)] = {
            "lon": float(np.degrees(np.arctan2(y / n, x / n))),
            "lat": float(np.degrees(np.arcsin(np.clip(z / n, -1, 1)))),
            "area": float(ww.sum()),
            "vx": float(vx[m].mean()), "vy": float(vy[m].mean()),
        }
    return info
