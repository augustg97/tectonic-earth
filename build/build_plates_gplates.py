"""Plate boundaries and named plates from a real rotation model.

This replaces the block-matched / advected approach (build_plates_time.py) for
all ages 0-1000 Ma. That approach DERIVED motion by image-matching the rendered
elevation frames, which is jittery, re-segments every frame (boundaries pop in
and out), and -- fatally -- goes to zero over featureless ocean, so oceanic
plates and the craters on them froze in place. The ocean floor is as active as
the continents; block-matching simply cannot see it.

Here every boundary comes from Merdith et al. (2021, Earth-Science Reviews 214,
103477; CC-BY 4.0), the published full-plate model whose span is exactly
0-1000 Ma. pyGPlates resolves the continuously-closing plate topologies at any
age: boundaries are shared closed polygons carried by finite Euler rotations,
so they move smoothly and continuously, keep stable identities, and are
classified by the model itself as ridge / subduction / transform. Ocean and
continent alike ride their plate at full speed.

The FUTURE (negative ages) is not covered by any published model, so those
keyframes keep the existing synthetic entries from plates_time.json.

Output is the same plates_time.json the app already consumes -- only the source
changes; the runtime page and shader are untouched.
"""
import json
import math
import os

import numpy as np
import pygplates

MODEL = "../data/merdith2021/SM2_X"
WEB = "../web"
STEP = 5

ROT = f"{MODEL}/1000_0_rotfile_Merdith_et_al.rot"
TOPO = [f"{MODEL}/{f}" for f in (
    "1000-410-Topologies_Merdith_et_al.gpml",
    "1000-410-Convergence_Merdith_et_al.gpml",
    "1000-410-Divergence_Merdith_et_al.gpml",
    "1000-410-Transforms_Merdith_et_al.gpml",
    "410-250_plate_boundaries_Merdith_et_al.gpml",
    "250-0_plate_boundaries_Merdith_et_al.gpml",
    "TopologyBuildingBlocks_Merdith_et_al.gpml",
)]

# The model classifies every boundary; fold its feature types into the three the
# app draws (ridge = spreading, trench = converging, transform = strike-slip).
CLASS = {
    "MidOceanRidge": "ridge", "ContinentalRift": "ridge",
    "ExtendedContinentalCrust": "ridge",
    "SubductionZone": "trench", "OrogenicBelt": "trench",
    "TerraneBoundary": "trench",
    "Transform": "transform", "Fault": "transform",
    "FractureZone": "transform", "InferredPaleoBoundary": "transform",
    "UnclassifiedFeature": "transform",
}

# Clean plate labels: the model names carry rotation-code suffixes
# ("Pacific PAC_099_088"), and some plates are bare ids we can name.
PID_NAME = {
    101: "North America", 201: "South America", 301: "Eurasia",
    304: "Iberia", 501: "India", 503: "Arabia", 701: "Africa",
    714: "Somalia", 801: "Australia", 802: "Antarctica", 901: "Pacific",
    902: "Farallon", 911: "Nazca", 926: "Cocos", 101000: "Greenland",
    1: "Africa", 2: "Kalahari", 3: "Congo", 4: "West Africa",
}
CODE = ("PAC", "EUR", "SAM", "NAM", "AFR", "ANT", "AUS", "IND", "NWA",
        "NEA", "COL", "SEA", "GRN", "ARB", "IBR", "BAL", "SIB", "LAU")


import re

_CODE_TAIL = re.compile(r"[_ ][A-Z]{2,4}[_ ]?\d{2,3}([_ ]\d{2,3})?$")
_UNDERSCORE_NUM = re.compile(r"_\d.*$")


def clean_name(feature, pid):
    n = (feature.get_name() or "").strip()
    if n:
        n = n.replace(" Plate", "").strip()
        # "Pacific PAC_099_088" -> "Pacific"; "Eurasia_1_0" -> "Eurasia"
        n = _CODE_TAIL.sub("", n).strip()
        n = _UNDERSCORE_NUM.sub("", n).strip()
        # a bare rotation code ("NAM_001_000") -> fall through to the pid map
        if n and not re.fullmatch(r"[A-Z]{2,4}", n) and not n.replace("_", "").isdigit():
            # ALL-CAPS single words read as shouting: "INDIA" -> "India"
            if n.isupper() and " " not in n and len(n) > 3:
                n = n.title()
            return n
    return PID_NAME.get(pid, "")


def split_dateline(pts):
    """Cut a lon/lat run wherever it wraps the antimeridian, so the app never
    streaks a segment across the whole map."""
    runs, cur = [], []
    for p in pts:
        if cur and abs(p[0] - cur[-1][0]) > 180:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    return runs


def decimate(pts, tol=0.35):
    """Thin a polyline by minimum point spacing (deg); the model gives dense
    geometry and the app does not need every vertex."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        q = out[-1]
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) >= tol:
            out.append(p)
    out.append(pts[-1])
    return out


def boundaries_at(rot, age):
    resolved, shared = [], []
    pygplates.resolve_topologies(TOPO, rot, resolved, age, shared)

    runs = []
    for s in shared:
        ft = s.get_feature().get_feature_type().to_qualified_string().split(":")[-1]
        cls = CLASS.get(ft, "transform")
        for sub in s.get_shared_sub_segments():
            latlon = sub.get_resolved_geometry().to_lat_lon_list()
            pts = [[round(lo, 2), round(la, 2)] for la, lo in latlon]
            for run in split_dateline(pts):
                run = decimate(run)
                if len(run) > 1:
                    runs.append({"c": cls, "p": run})

    plates = []
    for r in resolved:
        poly = r.get_resolved_boundary()
        if poly is None:
            continue
        pid = r.get_feature().get_reconstruction_plate_id()
        nm = clean_name(r.get_resolved_feature(), pid)
        if not nm:
            continue
        c = poly.get_boundary_centroid().to_lat_lon()
        area = poly.get_area() * 6371.0 * 6371.0 / 1e6      # million km^2
        plates.append({"n": nm, "lon": round(c[1], 1), "lat": round(c[0], 1),
                       "a": round(area, 1), "s": 0})
    plates.sort(key=lambda p: -p["a"])
    # de-duplicate names (keep the largest), cap to the app's 7
    seen, keep = set(), []
    for p in plates:
        if p["n"] in seen:
            continue
        seen.add(p["n"]); keep.append(p)
    return runs, keep[:7]


def main():
    rot = pygplates.RotationModel(ROT)
    path = f"{WEB}/plates_time.json"
    out = json.load(open(path)) if os.path.exists(path) else {}

    # keep the synthetic FUTURE entries (negative ages); the model stops at 0
    out = {k: v for k, v in out.items() if int(float(k)) < 0}

    total = 0
    for age in range(0, 1001, STEP):
        runs, plates = boundaries_at(rot, float(age))
        out[str(age)] = {"b": runs, "p": plates}
        total += sum(len(r["p"]) for r in runs)
    json.dump(out, open(path, "w"), separators=(",", ":"))

    sz = os.path.getsize(path) / 1e6
    nb = np.mean([len(out[str(a)]["b"]) for a in range(0, 1001, STEP)])
    npl = np.mean([len(out[str(a)]["p"]) for a in range(0, 1001, STEP)])
    print(f"plates_time.json: {sz:.2f} MB, {total} boundary points, "
          f"{nb:.0f} runs / {npl:.1f} named plates per era (Merdith 2021)")
    for a in (0, 100, 300, 540, 800, 1000):
        p = out[str(a)]
        print(f"  {a:>4} Ma: {len(p['b'])} runs, {len(p['p'])} named -",
              ", ".join(x["n"] for x in p["p"][:5]))


if __name__ == "__main__":
    main()
