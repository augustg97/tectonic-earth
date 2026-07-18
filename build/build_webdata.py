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
from climate import climate_at
import features

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

# ---------- hotspots (time-aware: LIPs + long-lived plumes) ----------
def build_hotspots():
    out = features.hotspots()
    json.dump(out, open(f"{WEB}/hotspots.json", "w"), separators=(",", ":"))
    print("hotspots:", len(out), "(with age windows)")

# ---------- era labels (time-aware, full timeline) ----------
def build_labels():
    out = features.labels()
    json.dump(out, open(f"{WEB}/labels.json", "w"), separators=(",", ":"))
    print("labels:", len(out), "(with age windows)")

if __name__ == "__main__":
    build_timeline()
    build_boundaries()
    build_plates()
    build_hotspots()
    build_labels()
