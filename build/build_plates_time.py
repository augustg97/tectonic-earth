"""Carry one plate model through time, rather than re-deriving it every frame.

Segmenting each keyframe independently made the boundaries jump: the derived
motion field wobbles a little between frames, the clustering reacts to that
wobble, and the whole tessellation reorganises. It also meant the present-day
frame was a derived guess sitting next to the surveyed PB2002 network, so the
two visibly disagreed.

Instead the plate model is advected. It starts as the *real* PB2002 plates at
age 0 and is then carried step by step along the measured motion field, so:

  * the present day IS PB2002 -- there is no seam to cross;
  * every frame is the previous frame moved slightly, so boundaries evolve
    continuously instead of reorganising;
  * boundaries follow the reconstruction's own motion by construction;
  * plates shrink, merge and vanish on their own as the crust they occupy
    converges, which is what the record should show;
  * names ride along with the label, so a plate keeps its identity for exactly
    as long as it exists.

Deep in the Precambrian the advected present-day network is necessarily a
fiction -- those plates did not exist -- but it is a *coherent* fiction driven
by the reconstruction, which reads far better than a mosaic that reshuffles
every step.
"""
import os, json
import numpy as np
from PIL import Image

import plates_time as PT

OUT = "../web/fields"
WEB = "../web"
W, H = PT.GRID_W, PT.GRID_H

LAT = 90 - (np.arange(H) + 0.5) / H * 180
LON = (np.arange(W) + 0.5) / W * 360 - 180
LONG, LATG = np.meshgrid(LON, LAT)
COSLAT = np.clip(np.cos(np.radians(LATG)), 0.15, 1.0)


def load_motion(rec):
    a = np.asarray(Image.open(os.path.join(OUT, rec["m"])).convert("RGB")).astype(float) / 255
    return (a[..., 0] * 2 - 1) * 160, (a[..., 1] * 2 - 1) * 160, a[..., 2]


def rasterise_pb2002():
    """PB2002 plates on the motion grid: an id raster plus id -> name."""
    plates = json.load(open(f"{WEB}/plates.json"))
    lab = np.zeros((H, W), np.int32)
    names = {}
    for i, p in enumerate(plates, start=1):
        inside = np.zeros((H, W), bool)
        for ring in p["rings"]:
            ring = np.asarray(ring, float)
            x, y = ring[:, 0], ring[:, 1]
            acc = np.zeros((H, W), bool)
            for k in range(len(ring)):
                j = (k - 1) % len(ring)
                acc ^= (((y[k] > LATG) != (y[j] > LATG)) &
                        (LONG < (x[j] - x[k]) * (LATG - y[k]) / (y[j] - y[k] + 1e-12) + x[k]))
            inside |= acc
        new = inside & (lab == 0)
        if new.any():
            lab[new] = i
            names[i] = p["name"]
    lab = PT._flood_fill_rest(lab)      # cells the polygons missed
    return lab, names


def majority(lab):
    """Light regularisation so advection noise does not fray the regions."""
    out = lab.copy()
    for r in range(H):
        rows = [max(0, r - 1), r, min(H - 1, r + 1)]
        for c in range(W):
            vals = [lab[rr, (c + dc) % W] for rr in rows for dc in (-1, 0, 1)]
            best, bn = lab[r, c], 0
            for v in set(vals):
                n = vals.count(v)
                if n > bn:
                    bn, best = n, v
            if bn >= 6:
                out[r, c] = best
    return out


def advect(lab, vx, vy, dt_myr, back=True):
    """Move the plate raster one step along the motion field.

    Semi-Lagrangian: the label at a grid point in the earlier frame is whatever
    label sits where that parcel has drifted to by the later frame. mm/yr over
    dt Myr works out as kilometres, which is a convenient accident of units.
    """
    sgn = 1.0 if back else -1.0
    dlon = (vx * dt_myr * sgn) / (111.0 * COSLAT)
    dlat = (vy * dt_myr * sgn) / 111.0
    src_lat = np.clip(LATG + dlat, -89.9, 89.9)
    c = np.mod(((LONG + dlon + 180) / 360 * W).astype(int), W)
    r = np.clip(((90 - src_lat) / 180 * H).astype(int), 0, H - 1)
    return lab[r, c]


def weld(lab, vx, vy, names, thresh=1.0):
    """Merge neighbouring plates that are no longer moving relative to
    each other.

    Advection alone preserves every plate for ever, which is wrong going back:
    the Atlantic closes, and North America and Africa should stop being two
    plates and become one. Two neighbours whose relative motion has fallen to
    nothing are a single plate, so they are welded and stay welded. Run over
    the whole march this makes plates progressively merge into the past and
    into the assembled future, and the boundary between them simply ceases to
    be drawn.
    """
    ids = [int(i) for i in np.unique(lab) if i > 0]
    if len(ids) < 2:
        return lab
    vel, area = {}, {}
    for i in ids:
        m = lab == i
        vel[i] = (float(vx[m].mean()), float(vy[m].mean()))
        area[i] = int(m.sum())
    # adjacency
    adj = set()
    right = np.roll(lab, -1, axis=1)
    down = np.roll(lab, -1, axis=0)[:-1]
    for a, b in zip(lab.ravel(), right.ravel()):
        if a != b and a > 0 and b > 0:
            adj.add((min(a, b), max(a, b)))
    for a, b in zip(lab[:-1].ravel(), down.ravel()):
        if a != b and a > 0 and b > 0:
            adj.add((min(a, b), max(a, b)))

    remap = {}
    for a, b in sorted(adj):
        a = remap.get(a, a); b = remap.get(b, b)
        if a == b:
            continue
        rel = np.hypot(vel[a][0] - vel[b][0], vel[a][1] - vel[b][1])
        if rel < thresh:
            keep, gone = (a, b) if area[a] >= area[b] else (b, a)
            remap[gone] = keep
            for k, v in list(remap.items()):
                if v == gone:
                    remap[k] = keep
    if remap:
        out = lab.copy()
        for gone, keep in remap.items():
            out[lab == gone] = keep
        return out
    return lab


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    man.sort(key=lambda m: m["age"])
    by_age = {m["age"]: m for m in man}
    ages = sorted(by_age)

    mot = {a: load_motion(by_age[a]) for a in ages}
    # Smooth the motion in TIME too: a single keyframe's field carries matching
    # noise, whereas neighbouring frames agree on the real signal.
    sm = {}
    for i, a in enumerate(ages):
        nb = [ages[j] for j in (i - 1, i, i + 1) if 0 <= j < len(ages)]
        sm[a] = (np.mean([mot[b][0] for b in nb], axis=0),
                 np.mean([mot[b][1] for b in nb], axis=0),
                 np.mean([mot[b][2] for b in nb], axis=0))

    lab0, names = rasterise_pb2002()
    a0 = min(ages, key=lambda x: abs(x))
    seg = {a0: lab0}

    def march(order, back):
        cur = lab0.copy()
        prev = None
        for a in order:
            if prev is None:
                prev = a
                continue
            vx, vy, cf = sm[prev]
            weak = cf < 0.22            # don't move crust on an unreliable match
            vx = np.where(weak, 0, vx)
            vy = np.where(weak, 0, vy)
            cur = advect(cur, vx, vy, abs(a - prev), back=back)
            cur = PT._flood_fill_rest(cur)
            cur = majority(cur)
            cur = PT._absorb_small(cur)
            cur = weld(cur, vx, vy, names)
            seg[a] = cur.copy()
            prev = a

    march([a for a in ages if a >= a0], back=True)           # into the past
    march([a for a in ages if a <= a0][::-1], back=False)     # into the future
    print(f"advected the plate model across {len(ages)} keyframes")

    out = {}
    total_pts = 0
    for a in ages:
        vx, vy, cf = sm[a]
        lab = seg[a]
        info = PT.plate_info(lab, vx, vy)
        bounds = PT.trace_boundaries(lab, vx, vy)
        plates = []
        for pid, d in sorted(info.items(), key=lambda kv: -kv[1]["area"]):
            nm = names.get(pid)
            if not nm or d["area"] < 6.0:
                continue
            plates.append({"n": nm, "lon": round(d["lon"], 1), "lat": round(d["lat"], 1),
                           "a": round(d["area"], 1),
                           "s": round(float(np.hypot(d["vx"], d["vy"])), 0)})
        total_pts += sum(len(b["p"]) for b in bounds)
        out[str(a)] = {"b": bounds, "p": plates[:7]}

    path = f"{WEB}/plates_time.json"
    json.dump(out, open(path, "w"), separators=(",", ":"))
    npl = np.mean([len(v["p"]) for v in out.values()])
    nb = np.mean([len(v["b"]) for v in out.values()])
    print(f"plates_time.json: {os.path.getsize(path)/1e6:.2f} MB, {total_pts} points, "
          f"{npl:.1f} plates and {nb:.1f} boundary runs per era")
    for probe in ("0", "90", "180", "250", "400", "540", "900", "-150"):
        if probe in out:
            n = len(out[probe]["p"])
            print(f"  {probe:>5} Ma: {n} named -", ", ".join(p["n"] for p in out[probe]["p"][:6]))


if __name__ == "__main__":
    main()
