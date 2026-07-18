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

# ---------- hotspots ----------
HOTSPOTS = [
    ("Hawaii", -155.3, 19.4), ("Iceland", -17.0, 64.8), ("Yellowstone", -110.7, 44.4),
    ("Galápagos", -91.5, -0.4), ("Réunion", 55.7, -21.2), ("Afar", 40.0, 11.5),
    ("Tahiti / Society", -149.0, -17.6), ("Samoa", -172.0, -14.3), ("Louisville", -141.0, -51.0),
    ("Kerguelen", 69.0, -49.6), ("Tristan da Cunha", -12.3, -37.1), ("Azores", -25.7, 37.9),
    ("Canary", -17.9, 28.3), ("Cape Verde", -24.0, 15.0), ("St. Helena", -9.9, -16.5),
    ("Ascension", -14.4, -7.9), ("Bouvet", 3.4, -54.4), ("Marion", 37.8, -46.9),
    ("Crozet", 51.0, -46.4), ("Amsterdam", 77.5, -37.8), ("Balleny", 164.0, -67.0),
    ("Erebus", 167.2, -77.5), ("Marquesas", -139.0, -9.0), ("Pitcairn", -130.1, -25.4),
    ("Easter", -109.3, -27.1), ("San Felix", -80.1, -26.3), ("Juan Fernández", -78.8, -33.7),
    ("Caroline", 164.0, 5.0), ("Cameroon", 9.2, 4.2), ("Hoggar", 6.0, 23.0),
    ("Tibesti", 17.5, 21.0), ("Darfur", 24.0, 13.0), ("Comoros", 43.3, -11.6),
    ("Fernando", -33.8, -3.9), ("Trindade", -29.3, -20.5), ("Bowie", -135.6, 53.0),
    ("Cobb / Axial", -130.0, 46.0), ("Guadalupe", -113.2, 29.1), ("Socorro", -111.0, 18.7),
    ("Raton", -104.0, 37.0), ("Bermuda", -64.8, 32.6), ("New England", -60.0, 40.0),
    ("Jan Mayen", -8.2, 71.0), ("Eifel", 6.8, 50.2), ("Hainan", 110.0, 20.0),
    ("Changbai", 128.0, 42.0), ("Vesuvius / Campania", 14.4, 40.8), ("Etna", 15.0, 37.7),
]
def build_hotspots():
    out = [{"name": n, "lon": lo, "lat": la} for n, lo, la in HOTSPOTS]
    json.dump(out, open(f"{WEB}/hotspots.json", "w"), separators=(",", ":"))
    print("hotspots:", len(out))

# ---------- era-correct labels (paleo-coordinates, time windows) ----------
# type: continent | ocean | sea | orogen ; a0/a1 = age window (Ma; future<0)
LABELS = [
    # present-ish continents (valid roughly 0..-120 & 0..80)
    {"t":"continent","n":"North America","lon":-100,"lat":45,"a0":-30,"a1":80},
    {"t":"continent","n":"South America","lon":-60,"lat":-15,"a0":-30,"a1":110},
    {"t":"continent","n":"Africa","lon":20,"lat":5,"a0":-40,"a1":150},
    {"t":"continent","n":"Eurasia","lon":90,"lat":55,"a0":-20,"a1":60},
    {"t":"continent","n":"Australia","lon":135,"lat":-25,"a0":-20,"a1":45},
    {"t":"continent","n":"Antarctica","lon":135,"lat":-82,"a0":-40,"a1":160},
    {"t":"continent","n":"India","lon":78,"lat":22,"a0":0,"a1":45},
    {"t":"ocean","n":"Pacific Ocean","lon":-150,"lat":0,"a0":-10,"a1":160},
    {"t":"ocean","n":"Atlantic Ocean","lon":-30,"lat":10,"a0":0,"a1":140},
    {"t":"ocean","n":"Indian Ocean","lon":75,"lat":-30,"a0":0,"a1":120},
    # Mesozoic / breakup
    {"t":"continent","n":"Laurasia","lon":40,"lat":50,"a0":150,"a1":250},
    {"t":"continent","n":"Gondwana","lon":30,"lat":-40,"a0":150,"a1":540},
    {"t":"ocean","n":"Tethys Ocean","lon":90,"lat":5,"a0":120,"a1":260},
    {"t":"ocean","n":"Panthalassa","lon":-150,"lat":0,"a0":160,"a1":320},
    # Pangaea
    {"t":"continent","n":"Pangaea","lon":10,"lat":5,"a0":250,"a1":320},
    {"t":"ocean","n":"Paleo-Tethys","lon":100,"lat":0,"a0":300,"a1":420},
    # Paleozoic
    {"t":"continent","n":"Laurussia (Euramerica)","lon":-20,"lat":10,"a0":340,"a1":420},
    {"t":"continent","n":"Laurentia","lon":-60,"lat":5,"a0":430,"a1":600},
    {"t":"continent","n":"Baltica","lon":10,"lat":30,"a0":430,"a1":540},
    {"t":"continent","n":"Siberia","lon":90,"lat":45,"a0":430,"a1":600},
    {"t":"ocean","n":"Iapetus Ocean","lon":-30,"lat":20,"a0":440,"a1":540},
    {"t":"ocean","n":"Rheic Ocean","lon":-10,"lat":-20,"a0":360,"a1":440},
    # Precambrian / authored
    {"t":"continent","n":"Gondwana (assembling)","lon":25,"lat":-45,"a0":540,"a1":600},
    {"t":"continent","n":"Pannotia","lon":10,"lat":-40,"a0":580,"a1":620},
    {"t":"continent","n":"Rodinia","lon":-10,"lat":0,"a0":700,"a1":1000},
    {"t":"ocean","n":"Mirovia","lon":-140,"lat":0,"a0":720,"a1":1000},
    # Future
    {"t":"continent","n":"Pangaea Proxima","lon":30,"lat":5,"a0":-250,"a1":-120},
    {"t":"ocean","n":"Neo-Panthalassa","lon":-150,"lat":0,"a0":-250,"a1":-60},
    {"t":"sea","n":"Mediterranean (closing)","lon":18,"lat":36,"a0":-90,"a1":-20},
]
def build_labels():
    json.dump(LABELS, open(f"{WEB}/labels.json", "w"), separators=(",", ":"))
    print("labels:", len(LABELS))

if __name__ == "__main__":
    build_timeline()
    build_boundaries()
    build_plates()
    build_hotspots()
    build_labels()
