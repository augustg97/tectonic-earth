"""Assemble compact vector + timeline data for the web app:
  - timeline.json : merged frame manifest (age -> file, epoch, period, sealevel,
                    climate) across future/present/deep-time, sorted young->old
  - boundaries.json : present-day PB2002 boundary segments classified as
                      ridge / transform / trench (decimated, rounded)
  - plates.json : simplified present-day plate polygons + MORVEL motion
  - hotspots.json : major volcanic hotspots
  - labels.json : era-correct continent / ocean / feature labels (paleo-coords)
"""
import json, re, glob, os
import numpy as np
from PIL import Image
from climate import climate_at
import features
import eras
import life

DATA = "../data"
WEB = "../web"
os.makedirs(WEB, exist_ok=True)

def r(x, n=2):
    return round(float(x), n)

# ---------- timeline (merge manifests) ----------
def build_timeline():
    """The field manifest IS the timeline now — it already carries the per
    keyframe scalars (temp, veg, ice thresholds) the shader needs."""
    all_ = json.load(open("../web/fields/manifest.json"))
    all_.sort(key=lambda m: m["age"])
    json.dump(all_, open(f"{WEB}/timeline.json", "w"), separators=(",", ":"))
    print("timeline:", len(all_), "keyframes")
    return all_

# ---------- boundaries ----------
CLASSMAP = {"OSR": "ridge", "OTF": "transform", "CTF": "transform",
            "SUB": "trench", "OCB": "trench", "CCB": "trench", "CRB": "trench"}
def build_boundaries():
    d = json.load(open(f"{DATA}/PB2002_steps.json"))
    segs = {"ridge": [], "transform": [], "trench": []}
    for i, f in enumerate(d["features"]):
        if i % 2:  # decimate by 2
            continue
        p = f["properties"]
        cls = CLASSMAP.get(p.get("STEPCLASS"), None)
        if not cls:
            continue
        a = (r(p["STARTLONG"]), r(p["STARTLAT"]))
        b = (r(p["FINALLONG"]), r(p["FINALLAT"]))
        segs[cls].append([a[0], a[1], b[0], b[1]])
    json.dump(segs, open(f"{WEB}/boundaries.json", "w"), separators=(",", ":"))
    for k, v in segs.items():
        print("  boundary", k, len(v))
    sz = os.path.getsize(f"{WEB}/boundaries.json")//1024
    print("boundaries:", sz, "KB")

# ---------- plates (simplified polygons) + MORVEL motion ----------
def simplify(ring, tol=0.8):
    """Decimate a lon/lat ring by min point spacing (deg)."""
    if len(ring) < 6:
        return ring
    out = [ring[0]]
    for p in ring[1:]:
        q = out[-1]
        if abs(p[0]-q[0]) + abs(p[1]-q[1]) >= tol:
            out.append(p)
    if out[-1] != ring[-1]:
        out.append(ring[-1])
    return out

def build_plates():
    d = json.load(open(f"{DATA}/PB2002_plates.json"))
    mv = json.load(open(f"{DATA}/nnr_morvel56.json"))["plates"]
    # map plate name -> morvel by loose name match
    out = []
    for f in d["features"]:
        name = f["properties"]["PlateName"]
        code = f["properties"]["Code"]
        geom = f["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            rings = [geom["coordinates"][0]]
        else:
            rings = [c[0] for c in geom["coordinates"]]
        for ring in rings:
            rr = [[r(x, 2), r(y, 2)] for x, y in ring]
            rr = simplify(rr, 0.7)
            if len(rr) >= 4:
                polys.append(rr)
        motion = mv.get(name)
        out.append({"name": name, "code": code, "rings": polys,
                    "motion": motion})
    json.dump(out, open(f"{WEB}/plates.json", "w"), separators=(",", ":"))
    print("plates:", len(out), "-", os.path.getsize(f"{WEB}/plates.json")//1024, "KB")

# ---------- back-advection of feature positions ----------
def _motion_fields():
    """Per-age (vx, vy) on the motion grid, for tracing points back in time."""
    man = json.load(open(f"{WEB}/fields/manifest.json"))
    out = {}
    for rec in man:
        p = os.path.join(WEB, "fields", rec["m"])
        if not os.path.exists(p):
            continue
        a = np.asarray(Image.open(p).convert("RGB")).astype(float) / 255
        out[rec["age"]] = ((a[..., 0] * 2 - 1) * 160, (a[..., 1] * 2 - 1) * 160,
                           a[..., 2])
    return out


# How far back the correction is trusted. Checked against known
# paleogeography, it holds up through the Mesozoic -- Chicxulub lands in the
# Gulf, Popigai in Siberia, Manicouagan in the Pangaean interior -- and then
# degrades. Past roughly 250 Ma a systematic poleward bias takes over: the
# motion field is block-matched on an equirectangular grid, whose cells
# converge at the poles, so a point that drifts to high latitude accumulates
# spurious meridional motion and keeps going. Unclamped, Acraman ended up at
# 88 S and Suordakh at 89 N, which is visibly nonsense.
#
# So: correct where the correction is trustworthy, and leave older features at
# their catalogued coordinates -- an approximation the module docstring
# already declares -- rather than replacing it with a confident-looking wrong
# answer.
ADVECT_LIMIT = 250.0
MAX_ABS_LAT = 78.0


def paleo_position(lon, lat, age, mot, step=5.0):
    """Carry a present-day point back to where that crust sat at `age`.

    Volcanic provinces and impact craters are catalogued at the coordinates
    where we find them today, but the crust they sit on has travelled. Marking
    the Siberian Traps or Chicxulub at modern coordinates on a 250 Ma map puts
    them in the wrong ocean. Stepping the point back along the measured motion
    field puts each event roughly where it actually happened.

    Stepping is done as a rotation on the sphere rather than by adding degrees
    of latitude and longitude. The naive version divides the longitude step by
    cos(lat), which blows up near the poles: a point that wandered to high
    latitude got flung around the globe and then stuck there, which is how
    Suordakh ended up at 88 N and Acraman at 87 S.

    Even done properly this recovers direction better than magnitude -- the
    motion field is smoothed and confidence-gated, so fast plates come out
    short. It is a correction, not a rotation model.
    """
    if age <= 0 or not mot:
        return lon, lat
    ages = sorted(a for a in mot if a >= 0)
    H, W = next(iter(mot.values()))[0].shape
    la, lo = np.radians(lat), np.radians(lon)
    p = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    n = int(age / step)
    for i in range(n):
        a = min(ages, key=lambda x: abs(x - i * step))
        vx, vy, cf = mot[a]
        lat_i = np.degrees(np.arcsin(np.clip(p[2], -1, 1)))
        lon_i = np.degrees(np.arctan2(p[1], p[0]))
        c = int((lon_i + 180) / 360 * W) % W
        r = int(np.clip((90 - lat_i) / 180 * H, 0, H - 1))
        if cf[r, c] < 0.2:
            continue
        # local east/north frame, then step backwards along the motion
        north = np.array([0.0, 0.0, 1.0])
        east = np.cross(north, p)
        ne = np.linalg.norm(east)
        if ne < 1e-8:                      # exactly at a pole: no defined east
            continue
        east /= ne
        north = np.cross(p, east)
        d = -(vx[r, c] * step) * east - (vy[r, c] * step) * north   # km
        dist = np.linalg.norm(d)
        if dist < 1e-9:
            continue
        axis = np.cross(p, d / dist)
        na = np.linalg.norm(axis)
        if na < 1e-9:
            continue
        axis /= na
        th = dist / 6371.0                 # arc angle on the sphere
        q = (p * np.cos(th) + np.cross(axis, p) * np.sin(th)
             + axis * np.dot(axis, p) * (1 - np.cos(th)))
        q /= np.linalg.norm(q)
        # backstop: refuse a step into the polar zone where the field is least
        # trustworthy, rather than letting the point run away to the pole
        if abs(np.degrees(np.arcsin(np.clip(q[2], -1, 1)))) > MAX_ABS_LAT:
            break
        p = q
    return (round(float(np.degrees(np.arctan2(p[1], p[0]))), 1),
            round(float(np.degrees(np.arcsin(np.clip(p[2], -1, 1)))), 1))


# ---------- hotspots + impacts (time-aware, paleo-positioned) ----------
def build_hotspots():
    mot = _motion_fields()
    out = features.hotspots()
    vis = features.visible_until()
    moved = 0
    # A plume has to be active on the frame its own province erupts. The two
    # are catalogued independently, so nothing enforces that but this.
    for problem in features.coupling_problems():
        print("  WARNING plume/province:", problem)
    for h in out:
        # The Neoproterozoic entries are authored directly onto the synthetic
        # Precambrian map, i.e. they are ALREADY in the frame of their era.
        # Advecting those would move them away from where they belong -- the
        # correction only applies to features catalogued at modern coordinates.
        if min(h["a0"], h["a1"]) >= 540:
            continue
        # A PROVINCE erupts at one place and then rides away on the plate, so it
        # has to be carried back to the crust it actually sat on. A PLUME does
        # not: it is anchored in the mantle while the plate slides over it, so
        # its present-day coordinate already is (approximately) where it has
        # always been. Only LIPs carry a 'peak', so only LIPs advect -- that
        # asymmetry is deliberate, not an oversight.
        ref = h.get("peak")
        if ref and 20 < ref <= ADVECT_LIMIT:
            h["lon"], h["lat"] = paleo_position(h["lon"], h["lat"], ref, mot)
            moved += 1

        # A flood basalt is a landform for far longer than it is an eruption.
        # Keep the eruption window for the "erupting now" flag, and widen the
        # window the marker is DRAWN in to however long the province stayed a
        # visible feature. Without this the Deccan appears for two frames and
        # then vanishes, when in fact it still holds up the Western Ghats.
        h["e0"], h["e1"] = h["a0"], h["a1"]
        vu = vis.get(h["n"])
        if vu is not None and h["k"] == "lip":
            h["vu"] = vu[0]
            h["vw"] = vu[1]
            h["a0"] = min(h["a0"], vu[0])

    imp = features.impacts()
    for m in imp:
        if 20 < m["age"] <= ADVECT_LIMIT:
            m["lon"], m["lat"] = paleo_position(m["lon"], m["lat"], m["age"], mot)
        # a crater is a lasting scar: visible from the impact onward
        m["a0"], m["a1"] = 0, m["age"]
        m["e0"], m["e1"] = m["age"], m["age"]
        m["peak"] = m["age"]
    out += imp
    notes = features.event_notes()
    for e in out:
        d = notes.get(e["n"])
        if not d:
            if e["k"] == "impact":
                d = (f"A confirmed impact structure roughly {e['d']} km across, "
                     f"formed about {e['peak']} million years ago.")
            elif e["k"] == "lip":
                d = ("A large igneous province: flood basalts erupted over a "
                     "geologically brief interval, on a scale with no modern "
                     "equivalent.")
            else:
                d = ("A long-lived mantle plume. The plate slides over it, so "
                     "the volcanoes it builds form a track rather than a "
                     "single centre.")
        e["d1"] = d
    json.dump(out, open(f"{WEB}/hotspots.json", "w"), separators=(",", ":"))
    print(f"volcanism + impacts: {len(out)} features "
          f"({len(imp)} craters, {moved} plume/LIP positions back-advected)")

# ---------- era labels (time-aware, full timeline) ----------
def build_labels():
    out = features.labels()
    desc = features.descriptions()
    ph = features.phases()
    for l in out:
        if l["n"] in desc:
            l["d"] = desc[l["n"]]
        # Long-lived features carry a description per phase of their life; the
        # app picks whichever contains the displayed age and falls back to "d".
        # A phase outside the label's own window can never be reached, and the
        # failure is silent -- the label just keeps showing its generic text --
        # so check it here rather than discovering it by scrubbing the timeline.
        if l["n"] in ph:
            l["ph"] = [{"a0": a0, "a1": a1, "d": t} for (a0, a1, t) in ph[l["n"]]]
            lo, hi = min(l["a0"], l["a1"]), max(l["a0"], l["a1"])
            for p in l["ph"]:
                if min(p["a0"], p["a1"]) < lo - 1 or max(p["a0"], p["a1"]) > hi + 1:
                    print(f"  WARNING unreachable phase: {l['n']} "
                          f"{p['a0']}-{p['a1']} outside label window {lo}-{hi}")
    json.dump(out, open(f"{WEB}/labels.json", "w"), separators=(",", ":"))
    have = sum(1 for l in out if "d" in l)
    phased = sum(1 for l in out if "ph" in l)
    print(f"labels: {len(out)} ({have} with descriptions, {phased} phased)")


# ---------- browsable intervals + supercontinents ----------
def build_eras():
    out = {"intervals": eras.intervals(),
           "supercontinents": eras.supercontinents()}
    json.dump(out, open(f"{WEB}/eras.json", "w"), separators=(",", ":"))
    print(f"eras: {len(out['intervals'])} intervals, "
          f"{len(out['supercontinents'])} supercontinents")


# ---------- biomes, life through time, regional fossil record ----------
def build_life():
    out = {"biomes": life.biomes(), "life": life.life(),
           "regional": life.regional(), "icons": life.icons()}
    json.dump(out, open(f"{WEB}/life.json", "w"), separators=(",", ":"))
    print(f"life: {len(out['biomes'])} biome samples, {len(out['life'])} intervals, "
          f"{len(out['regional'])} regions, {len(out['icons'])} illustrations")


if __name__ == "__main__":
    build_timeline()
    build_boundaries()
    build_plates()
    build_hotspots()
    build_labels()
    build_eras()
    build_life()
