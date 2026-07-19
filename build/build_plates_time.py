"""Export per-era plate tessellations: continuous boundaries and named plates.

Reads the derived motion textures, segments each keyframe into plates, traces
the borders as continuous polylines, and — the part that makes the layer
readable — tracks plate identity across keyframes so names persist for as long
as a plate does.

Naming works outward from the present, where the answer is known: each region
at 0 Ma is matched to the PB2002 plate it overlaps most, so it inherits a real
name (Pacific, Nazca, Eurasia...). Walking back through time, each frame's
regions are matched to the previous frame's by overlap and inherit the name.
A plate that appears with no ancestor is named for the landmass it carries,
falling back to its ocean basin.
"""
import os, json
import numpy as np
from PIL import Image

import plates_time as PT
import features

OUT = "../web/fields"
WEB = "../web"
W, H = PT.GRID_W, PT.GRID_H


def load_motion(rec):
    a = np.asarray(Image.open(os.path.join(OUT, rec["m"])).convert("RGB")).astype(float) / 255
    return (a[..., 0] * 2 - 1) * 160, (a[..., 1] * 2 - 1) * 160, a[..., 2]


def rasterise_pb2002():
    """Present-day plate names on the motion grid, for seeding the chain."""
    plates = json.load(open(f"{WEB}/plates.json"))
    lon = (np.arange(W) + 0.5) / W * 360 - 180
    lat = 90 - (np.arange(H) + 0.5) / H * 180
    LON, LAT = np.meshgrid(lon, lat)
    names = np.empty((H, W), object); names[:] = None
    for p in plates:
        inside = np.zeros((H, W), bool)
        for ring in p["rings"]:
            ring = np.asarray(ring, float)
            x, y = ring[:, 0], ring[:, 1]
            acc = np.zeros((H, W), bool)
            for i in range(len(ring)):
                j = (i - 1) % len(ring)
                acc ^= (((y[i] > LAT) != (y[j] > LAT)) &
                        (LON < (x[j] - x[i]) * (LAT - y[i]) / (y[j] - y[i] + 1e-12) + x[i]))
            inside |= acc
        names[inside & (names == None)] = p["name"]      # noqa: E711
    return names


def dominant(counter):
    return max(counter, key=counter.get) if counter else None


# Only landmasses and ocean basins make sense as plate names. A mountain belt
# or an epeiric sea is a feature ON a plate, not a plate.
PRIORITY = {"continent": 0, "ocean": 1}


def name_from_geography(lab, pid, age, labels, cen=None):
    """Name a plate for what it actually carries in THIS world.

    Names are far more meaningful when read off the era's own geography than
    when propagated across a hundred million years of splitting and merging,
    which smears one name across unrelated fragments. A label sitting inside
    the plate wins; failing that, the nearest one within reach.
    """
    m = lab == pid
    active = [l for l in labels
              if l["t"] in PRIORITY
              and min(l["a0"], l["a1"]) - 6 <= age <= max(l["a0"], l["a1"]) + 6]
    best, bp = None, 99
    for l in active:
        c = int((l["lon"] + 180) / 360 * W) % W
        r = int(np.clip((90 - l["lat"]) / 180 * H, 0, H - 1))
        if m[r, c]:
            p = PRIORITY.get(l["t"], 4)
            if p < bp:
                bp, best = p, l["n"]
    if best or cen is None:
        return best
    # nothing inside: take the nearest feature, if it is close enough to mean
    # anything at all
    bd = 1e9
    for l in active:
        dlon = abs(((l["lon"] - cen[0] + 540) % 360) - 180)
        d = np.hypot(dlon * np.cos(np.radians(cen[1])), l["lat"] - cen[1])
        if d < bd:
            bd, best = d, l["n"]
    return best if bd < 42 else None


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    man.sort(key=lambda m: m["age"])
    by_age = {m["age"]: m for m in man}
    ages = sorted(by_age)
    labels = features.labels()

    seg, info, bounds = {}, {}, {}
    for a in ages:
        vx, vy, cf = load_motion(by_age[a])
        lab = PT.segment(vx, vy, cf)
        seg[a] = lab
        info[a] = PT.plate_info(lab, vx, vy)
        bounds[a] = PT.trace_boundaries(lab, vx, vy)
    print(f"segmented {len(ages)} keyframes")

    # ---- seed names at the present, then propagate along the chain ----
    pb = rasterise_pb2002()
    names = {a: {} for a in ages}
    a0 = min(ages, key=lambda x: abs(x))
    for pid in info[a0]:
        m = seg[a0] == pid
        tally = {}
        for n in pb[m]:
            if n:
                tally[n] = tally.get(n, 0) + 1
        cen0 = (info[a0][pid]["lon"], info[a0][pid]["lat"])
        names[a0][pid] = dominant(tally) or name_from_geography(seg[a0], pid, a0, labels, cen0)

    def propagate(order):
        prev = None
        for a in order:
            if prev is None:
                prev = a; continue
            lp, lc = seg[prev], seg[a]
            for pid in info[a]:
                m = lc == pid
                tally = {}
                for q in lp[m]:
                    if q:
                        tally[int(q)] = tally.get(int(q), 0) + 1
                src = dominant(tally)
                inherited = names[prev].get(src) if src else None
                cen = (info[a][pid]["lon"], info[a][pid]["lat"])
                geo = name_from_geography(lc, pid, a, labels, cen)
                if abs(a) <= 25 and src and tally[src] / max(1, m.sum()) > 0.5 and inherited:
                    # near the present the surveyed plate names are the truth
                    names[a][pid] = inherited
                else:
                    names[a][pid] = geo or inherited or "Plate"
            prev = a

    propagate([a for a in ages if a >= a0])                 # into the past
    propagate([a for a in ages if a <= a0][::-1])           # into the future

    # ---- export ----
    out = {}
    total_pts = 0
    for a in ages:
        plates = []
        used = {}
        # largest region keeps the plain name; splinters are named for what
        # they carry, so we don't end up with "Australia 2, 3, 4"
        for pid, d in sorted(info[a].items(), key=lambda kv: -kv[1]["area"]):
            if d["area"] < 4.0:
                continue
            nm = names[a].get(pid) or "Plate"
            # Segmentation can split one named plate into two regions. Qualify
            # the smaller one rather than dropping it — a missing plate is far
            # more misleading than an approximate name.
            if nm in used:
                alt = name_from_geography(seg[a], pid, a, labels, (d["lon"], d["lat"]))
                alt = alt if alt else None
                if alt and alt not in used:
                    nm = alt
                else:
                    base, ref = nm, used[nm]
                    ns = "N" if d["lat"] > ref[1] else "S"
                    ew = "E" if ((d["lon"] - ref[0] + 540) % 360 - 180) > 0 else "W"
                    nm = f"{base} ({ns}{ew})"
                    k = 2
                    while nm in used:
                        nm = f"{base} {k}"; k += 1
            used[nm] = (d["lon"], d["lat"])
            sp = float(np.hypot(d["vx"], d["vy"]))
            plates.append({"n": nm, "lon": round(d["lon"], 1), "lat": round(d["lat"], 1),
                           "a": round(d["area"], 1), "s": round(sp, 0),
                           "vx": round(d["vx"], 1), "vy": round(d["vy"], 1)})
        # Cap the label count: a dozen plate names on top of the era labels is
        # unreadable, and the small ones are the least certain anyway.
        plates = [q for q in plates if not q["n"].startswith("Plate")][:6]
        total_pts += sum(len(b["p"]) for b in bounds[a])
        out[str(a)] = {"b": bounds[a], "p": plates}

    path = f"{WEB}/plates_time.json"
    json.dump(out, open(path, "w"), separators=(",", ":"))
    npl = np.mean([len(v["p"]) for v in out.values()])
    print(f"plates_time.json: {os.path.getsize(path)/1e6:.2f} MB, "
          f"{total_pts} boundary points, {npl:.1f} plates per era")
    sample = out[str(a0)]["p"][:8]
    print("present-day plate names:", ", ".join(p["n"] for p in sample))


if __name__ == "__main__":
    main()
