"""Assemble compact vector + timeline data for the web app:
  - timeline.json : merged frame manifest (age -> file, epoch, period, sealevel,
                    climate) across future/present/deep-time, sorted young->old
  - boundaries.json : present-day PB2002 boundary segments classified as
                      ridge / transform / trench (decimated, rounded)
  - plates.json : simplified present-day plate polygons + MORVEL motion
  - hotspots.json : major volcanic hotspots
  - labels.json : era-correct continent / ocean / feature labels (paleo-coords)
"""
import json
import math, re, glob, os
import numpy as np
from PIL import Image
from climate import climate_at
import climate
import features
import eras
import life
import paleo_tracks

DATA = "../data"
WEB = "../web"
os.makedirs(WEB, exist_ok=True)

def r(x, n=2):
    return round(float(x), n)

# ---------- timeline (merge manifests) ----------
def build_timeline():
    """The field manifest IS the timeline now — it already carries the per
    keyframe scalars (temp, veg, ice thresholds) the shader needs. Sea colour
    is layered on here rather than baked into the fields, because it is a
    display choice (how the water reads) not part of the elevation/rainfall
    physics, so it can be retuned without a 35-minute field rebuild."""
    all_ = json.load(open("../web/fields/manifest.json"))
    for m in all_:
        m.update(climate.sea_colour_at(m["age"]))
    all_.sort(key=lambda m: m["age"])
    json.dump(all_, open(f"{WEB}/timeline.json", "w"), separators=(",", ":"))
    print("timeline:", len(all_), "keyframes (with sea-colour palette)")
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
    out = features.hotspots()
    vis = features.visible_until()
    # A real rotation model (Merdith 2021 via pyGPlates) carries each feature
    # along its plate's finite rotation, giving a continuous track that is
    # correct on ocean floor as well as continent -- so a crater rides the plate
    # instead of freezing. Fall back to the old block-matched advection only if
    # pyGPlates or the model files are missing.
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    mot = None if rec else _motion_fields()
    tracked = 0

    # A plume has to be active on the frame its own province erupts. The two
    # are catalogued independently, so nothing enforces that but this.
    for problem in features.coupling_problems():
        print("  WARNING plume/province:", problem)
    for h in out:
        # The Neoproterozoic entries are authored directly onto the synthetic
        # Precambrian map, i.e. they are ALREADY in the frame of their era.
        # Advecting those would move them away from where they belong -- the
        # correction only applies to features catalogued at modern coordinates.
        neo = min(h["a0"], h["a1"]) >= 540

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

        if neo:
            continue
        # A PROVINCE erupts at one place then rides away on the plate, so it gets
        # a track back to the crust it erupted through. A PLUME is anchored in
        # the mantle while the plate slides over it, so it stays put -- no track.
        # Only LIPs carry a 'peak', which is what distinguishes the two.
        if h.get("peak") and h["k"] == "lip":
            span = max(h["a0"], h["a1"])
            if rec:
                tr, _ = rec.track(h["lon"], h["lat"], span)
                if len(tr) > 1:
                    h["tr"] = tr
                    tracked += 1
            elif 20 < h["peak"] <= ADVECT_LIMIT:
                h["lon"], h["lat"] = paleo_position(h["lon"], h["lat"], h["peak"], mot)

    imp = features.impacts()
    scar = features.scar_life()
    glob = features.global_effect()
    conf = features.impact_confidence()
    for m in imp:
        # A crater rides the plate from the moment it forms. Track it from the
        # present back to the impact -- on ocean floor this is the whole point:
        # a Pacific crater moves ~45 deg in 80 Myr, it does not sit still.
        if rec:
            tr, _ = rec.track(m["lon"], m["lat"], m["age"])
            if len(tr) > 1:
                m["tr"] = tr
                tracked += 1
        elif 20 < m["age"] <= ADVECT_LIMIT:
            m["lon"], m["lat"] = paleo_position(m["lon"], m["lat"], m["age"], mot)
        # How long a crater stays a crater varies by two orders of magnitude,
        # so the old flat 90 Myr fade was wrong at both ends: Chicxulub was
        # buried within about two million years, while Manicouagan is 215 Myr
        # old and still the most recognisable impact structure on the planet.
        life = scar.get(m["n"], (90, ""))[0]
        m["sl"] = life
        m["slw"] = scar.get(m["n"], (90, ""))[1]
        if m["n"] in glob:
            m["ge"] = glob[m["n"]]
        if m["n"] in conf:
            m["cf"], m["cfu"] = conf[m["n"]]
        # Visible from the impact until the scar is gone -- and structures whose
        # mark on the world outlasted their own topography (an ejecta layer, an
        # extinction, a climate excursion) stay flagged all the way to the
        # present, because that is the sense in which they are still there.
        m["a0"] = 0 if m["n"] in glob else max(0.0, m["age"] - life)
        m["a1"] = m["age"]
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
    src = "Merdith 2021 rotation tracks" if rec else "block-matched advection"
    print(f"volcanism + impacts: {len(out)} features "
          f"({len(imp)} craters, {tracked} given plate-motion tracks; {src})")

# ---------- era labels (time-aware, full timeline) ----------
_DEM_CACHE = {}


def _present_elevation():
    """The shipped present-day elevation raster, for sanity-checking coords."""
    if "p" in _DEM_CACHE:
        return _DEM_CACHE["p"]
    path = os.path.join(WEB, "fields", "phan_0000_e.webp")
    try:
        from PIL import Image
        im = Image.open(path).convert("L")
        _DEM_CACHE["p"] = (im.load(), im.width, im.height)
    except Exception as e:
        print(f"  note: present-day DEM unavailable ({e}); "
              f"skipping label coordinate check")
        _DEM_CACHE["p"] = None
    return _DEM_CACHE["p"]


def _elev_lookup(dem, lon, lat):
    px, w, h = dem
    x = int((lon + 180.0) / 360.0 * w) % w
    y = max(0, min(h - 1, int((90.0 - lat) / 180.0 * (h - 1))))
    e = px[x, y] / 255.0
    sgn = 2.0 * e - 1.0
    return (1 if sgn >= 0 else -1) * sgn * sgn * 8000.0



def _unit(lon, lat):
    import math
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def _centroid(points):
    """Spherical centroid. A mean of longitudes tears apart across 180."""
    import math
    if not points:
        return None
    x = y = z = 0.0
    for lon, lat in points:
        a, b, c = _unit(lon, lat)
        x += a; y += b; z += c
    n = math.sqrt(x * x + y * y + z * z)
    if n < 1e-9:
        return None
    x, y, z = x / n, y / n, z / n
    return (math.degrees(math.atan2(y, x)), math.degrees(math.asin(max(-1, min(1, z)))))


def smooth_track(tr, win=5):
    """Take the teleports out of a resolved composite track.

    A composite name is placed by choosing, per keyframe, which landmass it
    belongs to. When two candidates are close the choice can flip, and the name
    crosses an ocean between one frame and the next -- Siberia moved 60 degrees
    between 565 and 570 Ma, Laurussia 57 between 350 and 355. The choice is
    usually defensible at BOTH frames; what is indefensible is arriving there
    instantly.

    So smooth the result: a short rolling mean over the track turns a step into
    a ramp across a few keyframes, which reads as a continent drifting rather
    than a caption jumping. Real motion survives it -- plates move slowly enough
    that a five-frame window barely touches them.

    Longitude is averaged as a unit vector, or a track crossing the
    antimeridian would be smeared right across the map on its way through.
    """
    if len(tr) < 3:
        return tr
    ages = [int(a) for a, _, _ in tr]
    xs = [math.cos(math.radians(lo)) for _, lo, _ in tr]
    ys = [math.sin(math.radians(lo)) for _, lo, _ in tr]
    la = [v for _, _, v in tr]
    n = len(tr)
    h = win // 2
    out = []
    for i in range(n):
        j0, j1 = max(0, i - h), min(n, i + h + 1)
        k = j1 - j0
        cx = sum(xs[j0:j1]) / k
        cy = sum(ys[j0:j1]) / k
        lon = math.degrees(math.atan2(cy, cx)) if (cx or cy) else tr[i][1]
        out.append([ages[i], round(((lon + 180.0) % 360.0) - 180.0, 1),
                    round(sum(la[j0:j1]) / k, 1)])
    return out


#: Rough continent boxes on PRESENT-DAY coordinates. Crude on purpose: the only
#: job is to say which continent a label's modern anchor sits on, so the biota
#: fallback can stop listing an African ape under the Amazon. Overlaps are kept
#: rather than resolved -- a point in the eastern Mediterranean is genuinely
#: both European and Asian, and a label there should filter loosely, not wrongly.
REGION_BOXES = [
    ("na", -170, -52, 8, 85), ("na", -180, -168, 50, 72),
    ("sa", -85, -33, -57, 14),
    ("eu", -25, 62, 35, 72),
    ("af", -20, 52, -36, 38),
    ("as", 25, 180, 5, 80), ("as", -180, -168, 60, 72),
    ("au", 108, 180, -50, -8),
    ("an", -180, 180, -90, -60),
]


def region_tags(lon, lat):
    """Continent tags for a present-day coordinate, or None if it matches none."""
    out = set()
    for tag, lo0, lo1, la0, la1 in REGION_BOXES:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            out.add(tag)
    return sorted(out) or None


def composite_track(spec, a_old, rec, step=5):
    """Per-age position of a paleocontinent, from where its fragments were.

    Modern anchors ride the Merdith rotations (frame-corrected to the PaleoDEM).
    Past 540 Ma the map is the authored Precambrian composite instead of a real
    DEM, so the position comes from that composite's own craton placement, and
    the two are blended across exactly the 540-600 handoff the terrain uses --
    otherwise the name would drift off the landmass while the landmass morphs.
    """
    modern = spec.get("modern") or []
    cratons = spec.get("cratons") or []
    tracks = []
    for lon, lat in modern:
        try:
            tr, _ = rec.track(float(lon), float(lat), min(540, max(a_old, 5)), step=step)
        except Exception:
            continue
        if len(tr) > 1:
            tracks.append({int(round(a)): (x, y) for a, x, y in tr})
    pre = None
    if cratons:
        try:
            import build_synthetic as BS
            pre = BS.pre_placement
        except Exception:
            pre = None
    # The craton centroid has to be taken over a CONSTANT set. build_synthetic's
    # placement does not return every craton at every age, and a name whose
    # centroid is averaged over eight blocks at one keyframe and five at the
    # next lurches by tens of degrees for no reason on the map -- Siberia moved
    # 60 degrees between 565 and 570 Ma this way. Carry a missing block forward
    # from where it last was instead of dropping it out of the average.
    carried = {}
    out = []
    for age in range(0, int(math.ceil(a_old)) + step, step):
        m = None
        if tracks:
            pts = [t[min(age, 540)] for t in tracks if min(age, 540) in t]
            m = _centroid(pts)
        c = None
        if pre is not None and age > 540:
            place = {n: (lo, la) for n, lo, la, _sp in pre(age)}
            for n in cratons:
                if n in place:
                    carried[n] = place[n]
            pts = [carried[n] for n in cratons if n in carried]
            c = _centroid(pts)
        if m is None and c is None:
            continue
        wq = max(0.0, min(1.0, (age - 540.0) / 60.0)) if c is not None else 0.0
        if m is None:
            lon, lat = c
        elif c is None or wq <= 0:
            lon, lat = m
        else:
            # interpolate on the sphere, shortest way round
            d = ((c[0] - m[0] + 180.0) % 360.0) - 180.0
            lon = m[0] + d * wq
            lat = m[1] + (c[1] - m[1]) * wq
        out.append([age, round(((lon + 180.0) % 360.0) - 180.0, 1), round(lat, 1)])
    return out



_LANDMASS_CACHE = {}


def landmasses(age, nx=720, ny=360, min_area=40.0):
    """Connected landmasses in the shipped DEM at this age, with centroids.

    Longitude wraps, so a continent straddling 180 is ONE landmass and not two.
    Areas are cos(lat)-weighted; centroids are spherical.
    """
    key = int(round(age / 5.0)) * 5
    if key in _LANDMASS_CACHE:
        return _LANDMASS_CACHE[key]
    import numpy as np
    from PIL import Image
    try:
        from scipy import ndimage
    except Exception as e:
        # Silently returning [] here disables continent snapping for the WHOLE
        # build and the only symptom is labels quietly drifting back into the
        # sea. Say so once, loudly.
        if not _LANDMASS_CACHE.get("_warned"):
            print(f"  WARNING: scipy unavailable ({e}) -- paleocontinent labels "
                  f"will NOT be snapped to landmasses. Run with the venv python.")
            _LANDMASS_CACHE["_warned"] = True
        _LANDMASS_CACHE[key] = []
        return []
    name = (f"pre_{key:04d}_e.webp" if key > 540 else
            (f"fut_{abs(key):04d}_e.webp" if key < 0 else f"phan_{key:04d}_e.webp"))
    path = os.path.join(WEB, "fields", name)
    if not os.path.exists(path):
        _LANDMASS_CACHE[key] = []
        return []
    a = np.asarray(Image.open(path).convert("L").resize((nx, ny)), np.float32) / 255.0
    sg = 2 * a - 1
    z = np.sign(sg) * sg * sg * 8000.0
    land = z > 0
    lab, _ = ndimage.label(land)
    for y in range(ny):                      # weld components across 180
        if land[y, 0] and land[y, nx - 1]:
            u, v = lab[y, 0], lab[y, nx - 1]
            if u != v:
                lab[lab == v] = u
    wlat = np.cos(np.radians(90 - (np.arange(ny) + 0.5) / ny * 180))[:, None]
    out = []
    for i in np.unique(lab):
        if i == 0:
            continue
        m = lab == i
        area = float((m * wlat).sum())
        if area < min_area:
            continue
        ys, xs = np.nonzero(m)
        lon = (xs + 0.5) / nx * 360 - 180
        lat = 90 - (ys + 0.5) / ny * 180
        cl, sl = np.cos(np.radians(lat)), np.sin(np.radians(lat))
        vx = (cl * np.cos(np.radians(lon))).mean()
        vy = (cl * np.sin(np.radians(lon))).mean()
        vz = sl.mean()
        n = math.sqrt(vx * vx + vy * vy + vz * vz)
        if n < 1e-9:
            continue
        clon = math.degrees(math.atan2(vy / n, vx / n))
        clat = math.degrees(math.asin(max(-1, min(1, vz / n))))
        # keep a sample of the landmass itself. A name should sit on the part of
        # the continent its own crust occupies, not at the middle of the whole
        # thing: while Gondwana is welded into Pangaea, its centroid is up in
        # Laurasia, and the label wandered 60 degrees as fragments came and went.
        step = max(1, len(lon) // 1500)
        cells = np.stack([lon[::step], lat[::step]])
        out.append((area, clon, clat, cells))
    out.sort(key=lambda r: -r[0])
    _LANDMASS_CACHE[key] = out
    return out


def _nearest_cell(cells, lon, lat):
    """Closest point of a landmass to a position, and its angular distance."""
    import numpy as np
    clo, cla = cells
    a = np.radians(lat); b = np.radians(lon)
    u = np.array([math.cos(a) * math.cos(b), math.cos(a) * math.sin(b), math.sin(a)])
    la, lo = np.radians(cla), np.radians(clo)
    v = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    dot = np.clip(u @ v, -1.0, 1.0)
    k = int(np.argmax(dot))
    return float(clo[k]), float(cla[k]), math.degrees(math.acos(dot[k]))


def _arc(lon0, lat0, lon1, lat1):
    a0, b0, c0 = _unit(lon0, lat0)
    a1, b1, c1 = _unit(lon1, lat1)
    d = max(-1.0, min(1.0, a0 * a1 + b0 * b1 + c0 * c1))
    return math.degrees(math.acos(d))


# generous: the uniqueness rule already stops a name taking the wrong
# continent, and a tight cap just leaves deep-time names floating instead
MAX_SNAP_DEG = 75.0



_GRID_CACHE = {}


def elev_grid(age, nx=720, ny=360):
    """Low-res elevation for an age, for water snapping."""
    key = int(round(age / 5.0)) * 5
    if key in _GRID_CACHE:
        return _GRID_CACHE[key]
    import numpy as np
    from PIL import Image
    name = (f"pre_{key:04d}_e.webp" if key > 540 else
            (f"fut_{abs(key):04d}_e.webp" if key < 0 else f"phan_{key:04d}_e.webp"))
    path = os.path.join(WEB, "fields", name)
    if not os.path.exists(path):
        _GRID_CACHE[key] = None
        return None
    a = np.asarray(Image.open(path).convert("L").resize((nx, ny)), np.float32) / 255.0
    sg = 2 * a - 1
    _GRID_CACHE[key] = np.sign(sg) * sg * sg * 8000.0
    return _GRID_CACHE[key]


def nearest_water(age, lon, lat, avoid=(), avoid_deg=14.0, max_deg=60.0,
                  min_depth=40.0, prefer=None):
    """Closest sea cell to a position, keeping clear of already-placed names.

    Ocean labels used to be static present-day coordinates evaluated in a
    reconstruction frame, so they drifted over continents; and the Precambrian
    pair (Adamastor, Mozambique) ended up sitting on top of each other. Snapping
    to real water with a separation rule fixes both.
    """
    import numpy as np
    z = elev_grid(age)
    if z is None:
        return None
    ny, nx = z.shape
    la = np.radians(90 - (np.arange(ny) + 0.5) / ny * 180)[:, None]
    lo = np.radians((np.arange(nx) + 0.5) / nx * 360 - 180)[None, :]
    a, b = math.radians(lat), math.radians(lon)
    dot = (np.cos(la) * np.cos(lo) * math.cos(a) * math.cos(b)
           + np.cos(la) * np.sin(lo) * math.cos(a) * math.sin(b)
           + np.sin(la) * math.sin(a))
    # Require water, not the waterline: a low-res cell can read as sea while the
    # full-resolution texture there is a few metres above it, which is how these
    # labels ended up on their own coastline. Keep the floor SHALLOW though --
    # an epicontinental seaway is only 100-150 m deep, and a 200 m floor sent
    # the Trans-Saharan label out into the Atlantic instead.
    ok = z < -min_depth
    if not ok.any():
        ok = z < 0
    for (alon, alat) in avoid:
        aa, bb = math.radians(alat), math.radians(alon)
        d2 = (np.cos(la) * np.cos(lo) * math.cos(aa) * math.cos(bb)
              + np.cos(la) * np.sin(lo) * math.cos(aa) * math.sin(bb)
              + np.sin(la) * math.sin(aa))
        ok &= d2 < math.cos(math.radians(avoid_deg))
    if not ok.any():
        return None
    # continuity: a basin name should stay in the basin it was in, or it flips
    # between neighbouring seas as the coastline shifts frame to frame
    if prefer is not None:
        pa, pb = math.radians(prefer[1]), math.radians(prefer[0])
        dp = (np.cos(la) * np.cos(lo) * math.cos(pa) * math.cos(pb)
              + np.cos(la) * np.sin(lo) * math.cos(pa) * math.sin(pb)
              + np.sin(la) * math.sin(pa))
        dot = dot + 0.6 * dp
    # OPENNESS: prefer the wide part of a basin, not merely a wet cell.
    #
    # A cell can be under water and still be a bad place for a name, because
    # the water there is a strait two pixels across and the TEXT covers the
    # land either side. That is what "the Ural Ocean hovers over land" actually
    # was: at low resolution its position was correctly wet, and at the
    # resolution the globe draws, the last 25 Myr of the basin is a thread.
    #
    # Every ocean in the set showed this at the YOUNGEST end of its window --
    # Ural 255-280 Ma, Rheic 320-360, Palaeo-Tethys 200-225 -- because that is
    # when a closing ocean stops being a place and becomes a seam. Scoring by
    # how much of a ~5-degree neighbourhood is water pushes the name into
    # whatever open sea is left, and when there is none it at least finds the
    # widest remaining part.
    water = (z < 0).astype(np.float32)
    k = max(2, int(round(5.0 / (180.0 / z.shape[0]))))
    pad = np.pad(water, ((k, k), (0, 0)), mode="edge")
    pad = np.pad(pad, ((0, 0), (k, k)), mode="wrap")
    csum = pad.cumsum(0).cumsum(1)
    n = 2 * k + 1
    box = (csum[n - 1:, n - 1:] - csum[:-n + 1 or None, n - 1:]
           - csum[n - 1:, :-n + 1 or None] + csum[:-n + 1 or None, :-n + 1 or None])
    openness = box[:z.shape[0], :z.shape[1]] / float(n * n)
    dot = dot + 0.45 * openness
    d = np.where(ok, dot, -4.0)
    k = int(np.argmax(d))
    y, x = divmod(k, nx)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.clip(dot.flat[k], -1, 1))))))
    if prefer is None and ang > max_deg:
        return None
    return (float((x + 0.5) / nx * 360 - 180), float(90 - (y + 0.5) / ny * 180))


def resolve_to_landmasses(tracks, windows, order):
    """Put each paleocontinent ON a landmass, and never two on the same one.

    The rotation model and the PaleoDEM do not agree plate by plate -- the global
    frame correction is rigid, the real disagreement is regional -- so a centroid
    derived from modern fragments can land in open ocean. Siberia did, at every
    Cambrian age. Snapping to the nearest real landmass fixes that; enforcing one
    landmass per name is what stops two continents sharing a label, which is the
    confusing failure the search version produced.

    Names are matched biggest-first, so Gondwana claims the supercontinent before
    a smaller name can take it.
    """
    resolved = {n: [] for n in tracks}
    last = {}
    ages = sorted({a for tr in tracks.values() for a, _lo, _la in tr})
    for age in ages:
        here = [n for n in order
                if n in tracks and windows[n][0] <= age <= windows[n][1]]
        if not here:
            continue
        masses = landmasses(age)
        used = set()
        # Score every (name, landmass) pair and take the most confident matches
        # first, rather than letting a fixed priority order decide. A fixed order
        # made the big names claim landmasses that a small one was sitting
        # directly on: Avalonia went from always on land to on land less than
        # half the time. Ties still fall to the priority order, so a
        # supercontinent wins a genuine draw.
        pairs = []
        for rank, n in enumerate(here):
            pt = next(((lo, la) for a, lo, la in tracks[n] if a == age), None)
            if pt is None:
                continue
            prev = last.get(n)
            for k, (area, clon, clat, cells) in enumerate(masses):
                plon, plat, d = _nearest_cell(cells, pt[0], pt[1])
                # Distance to where the crust actually is leads; continuity is a
                # tie-break, not the driver. Weighted the other way round, one
                # bad frame becomes permanent -- Laurussia latched onto a
                # 43-cell islet and continuity then kept re-picking it for
                # 50 Myr, 40 degrees from the continent it names.
                # Continuity weight rises with age: the deep-time DEM
                # (authored Precambrian composite, high Ediacaran sea level)
                # makes landmasses appear, flood and fragment between keyframes,
                # and without a strong pull toward where the label just was it
                # hops island to island -- which is the Ediacaran "jump". In the
                # Phanerozoic the terrain is real and distance can lead.
                cw = 0.55 if age < 540 else 1.6
                score = d if prev is None else d + cw * _nearest_cell(
                    cells, prev[0], prev[1])[2]
                # and a continent does not belong on a speck
                score += 10.0 * max(0.0, 1.0 - area / 500.0)
                pairs.append((score, rank, n, k, plon, plat))
        pairs.sort()
        placed = {}
        for score, _rank, n, k, plon, plat in pairs:
            if n in placed or k in used or score > MAX_SNAP_DEG:
                continue
            used.add(k)
            placed[n] = (plon, plat)
            last[n] = (plon, plat)
            resolved[n].append([age, round(plon, 1), round(plat, 1)])
        # Second pass: continents that genuinely MERGED may share a landmass.
        # One-name-per-landmass is right while they are separate -- it is what
        # stops two names on one continent -- but once Gondwana and Laurussia
        # weld into Pangaea both names belong on it, at their own ends. Without
        # this, whichever lost the tie was flung to another landmass entirely,
        # 69 degrees away. Sharing is allowed only when the two placements stay
        # well apart, so they still read as two labels on one supercontinent.
        for score, _rank, n, k, plon, plat in pairs:
            if n in placed or score > MAX_SNAP_DEG:
                continue
            if any(_arc(plon, plat, q[0], q[1]) < 18.0 for q in placed.values()):
                continue
            placed[n] = (plon, plat)
            last[n] = (plon, plat)
            resolved[n].append([age, round(plon, 1), round(plat, 1)])
        # The biggest landmass must not go nameless. During assembly the
        # composite centroids sit out on the fragments -- Gondwana on Australia,
        # Pannotia on Laurentia -- and the great welded core of the
        # supercontinent, the largest single mass on the map, could end up with
        # no label within 25 degrees of it. That is the "huge unlabelled island"
        # in the Ediacaran. If the largest mass is unclaimed, hand it to the
        # most senior in-window composite (the priority order leads with the
        # supercontinent of the age), MOVING that name there rather than adding
        # a second copy.
        if masses:
            biggest = max(masses, key=lambda m: m[0])
            barea, bclon, bclat, bcells = biggest
            claimed_near = any(
                _arc(p[0], p[1], bclon, bclat) < 22.0 for p in placed.values())
            if barea > 4000 and not claimed_near:
                for n in here:                       # here is in priority order
                    plon, plat, d = _nearest_cell(bcells, *(
                        placed.get(n) or last.get(n) or (bclon, bclat)))
                    if resolved[n] and resolved[n][-1][0] == age:
                        resolved[n][-1] = [age, round(plon, 1), round(plat, 1)]
                    else:
                        resolved[n].append([age, round(plon, 1), round(plat, 1)])
                    placed[n] = (plon, plat)
                    last[n] = (plon, plat)
                    break
        for n in here:
            if n in placed:
                continue
            pt = next(((lo, la) for a, lo, la in tracks[n] if a == age), None)
            if pt is not None:
                resolved[n].append([age, round(pt[0], 1), round(pt[1], 1)])
    return resolved



# Labels for the oceanic plateaus and microcontinents that seafloor.py seeds
# into the elevation field. Both must use the SAME back-advected anchors, or
# the name floats off the bank it is meant to sit on -- so the track is built
# here from seafloor's own anchor list rather than from a static coordinate,
# and the window covers the whole time the plateau is visible, emergent or
# submerged (which is what "label the submerged form too" needs).
PLATEAU_LABEL = {
    "Kerguelen Microcontinent": ("Kerguelen", 120, 0),
    "Mauritia": ("Mauritia", 85, 0),
    "Jan Mayen Microcontinent": ("JanMayen", 55, 0),
    "Seychelles Microcontinent": ("Seychelles", 90, 0),
    "Zealandia": ("Zealandia", 85, 0),
    "Argoland": ("Argoland", 165, 0),
    "Broken Ridge": ("BrokenRidge", 100, 0),
    "East Tasman Plateau": ("EastTasman", 80, 0),
    "Ontong Java Plateau": ("OntongJava", 126, 0),
    "Manihiki Plateau": ("Manihiki", 125, 0),
    "Shatsky Rise": ("Shatsky", 147, 0),
    "Agulhas Plateau": ("Agulhas", 100, 0),
    "Mascarene Plateau": ("MascarenePlateau", 45, 0),
    "Rio Grande Rise": ("RioGrandeRise", 85, 0),
    "Walvis Ridge": ("WalvisRidge", 120, 0),
}


def _plateau_track(key, a_old, rec, step=5):
    """Centroid of a plateau's back-advected anchors, per age -- the same
    positions seafloor.py seeds, so the label lands on the seeded bank."""
    import seafloor
    spec = seafloor.PLATEAUS.get(key)
    if not spec:
        return []
    out = []
    for age in range(0, int(a_old) + step, step):
        pts = []
        for alon, alat, _r in spec["anchors"]:
            plon, plat = alon, alat
            if rec is not None and age > 0:
                try:
                    tr, _ = rec.track(float(alon), float(alat), min(540, max(age, 5)))
                    if tr:
                        b = min(tr, key=lambda r: abs(r[0] - age))
                        plon, plat = b[1], b[2]
                except Exception:
                    pass
            pts.append((plon, plat))
        c = _centroid(pts)
        if c:
            out.append([age, round(c[0], 1), round(c[1], 1)])
    return out


def build_labels():
    out = features.labels()
    desc = features.descriptions()
    ph = features.phases()
    # Carry each label along its plate's REAL rotation (Merdith 2021), the same
    # track craters and LIPs use, so a name follows its feature across the whole
    # timeline instead of being yanked to the nearest matching terrain by
    # snapLabel -- which put the Western Interior Seaway and Gulf of Mexico out
    # in the Pacific at 98 Ma. Cap at 540 Ma: the deep-Precambrian frame is
    # authored, not Merdith-derived, and Scotese/Merdith only agree within the
    # Phanerozoic. Labels authored entirely in the Precambrian era-frame
    # (>=540 Ma, e.g. Timanian Belt) are left to snapLabel with their paleo coord.
    rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    tracked = 0
    untracked_bad_coord = []
    # A track back-advects a PRESENT-DAY coordinate. Many labels here are not
    # authored that way: paleo-entities (Gondwana, Baltica, Avalonia, Cimmeria,
    # the Glossopteris flora) carry the position they occupied in their own era's
    # reconstruction, and back-advecting one of those is meaningless -- it moves
    # a point that was never at that place today. The give-away is that the coord
    # sits on the wrong side of TODAY's coastline for the kind of feature it is:
    # the Appalachians are a real mountain range, so their coordinate had better
    # be on land today, and (-75, 30) is 4400 m of open Atlantic.
    # Those labels are left untracked and keep snapLabel's wide terrain search,
    # which is how they were placed before tracking existed.
    present_dem = _present_elevation()

    def coord_is_present_day(l):
        """Is this coordinate a real present-day position on trackable crust?

        The test is LAND today, whatever the feature was. A track follows crust,
        and only crust that still exists can be followed — an epicontinental sea
        like the Western Interior Seaway sat on continental crust that is now dry
        South Dakota, so it tracks perfectly well. A coordinate out on today's
        abyssal plain is either authored in its own era's reconstruction frame
        (Gondwana at 30E 40S, Avalonia in the South Atlantic) or sits on ocean
        floor that has since been subducted. Neither can be back-advected, so
        both keep snapLabel's terrain search instead.
        """
        if present_dem is None:
            return True
        return _elev_lookup(present_dem, l["lon"], l["lat"]) > 0

    composites = dict(getattr(features, "COMPOSITE_LABELS", {}))
    water_specs = dict(getattr(features, "COMPOSITE_WATER", {}))
    composites.update(getattr(features, "COMPOSITE_BELTS", {}))
    n_comp = 0
    raw_comp, comp_window, comp_label = {}, {}, {}
    water_placed, n_water = {}, 0
    for l in out:
        if l["n"] in desc:
            l["d"] = desc[l["n"]]
        # Region tag, for the biota fallback. Derived from the label's own
        # present-day anchor rather than hand-listed: there are 103 labels that
        # show a biota panel and hand-tagging them was never going to stay
        # current. Composites use the centroid of their modern fragments.
        spec_r = (getattr(features, "COMPOSITE_LABELS", {}).get(l["n"]) or {})
        mods = spec_r.get("modern")
        if mods:
            rg = set()
            for mlon, mlat in mods:
                for t in (region_tags(mlon, mlat) or []):
                    rg.add(t)
            if rg:
                l["rg"] = sorted(rg)
        else:
            # Region tag for the biota filter, from the label's own coordinate.
            # Use region_tags DIRECTLY rather than gating on coord_is_present_day
            # (which requires land TODAY) -- a submerged fragment like the East
            # Tasman Plateau or Kerguelen has a real present-day position but is
            # underwater, so the land gate skipped it and its card then showed
            # Proconsul, an African ape, off Australia. The continent boxes
            # return None over open ocean and for a paleo-frame coordinate that
            # lands in no box, so this is safe to apply broadly; restrict to
            # post-Pangaean windows, where a present-day coordinate is
            # meaningful, so a deep-time craton authored in its own era's frame
            # is not mis-tagged.
            if max(l["a0"], l["a1"]) <= 320:
                rg = region_tags(l["lon"], l["lat"])
                if rg:
                    l["rg"] = rg
        # Attach the per-label extras FIRST. Each tracking branch below ends in
        # `continue`, so anything after them is skipped for the labels that take
        # one -- which silently cost six seas their phase descriptions when the
        # water branch was added.
        #
        # lakes carry a rendered radius (deg) plus real morphology (oriented,
        # multi-lobe ellipses) so the app can draw them as their actual shapes
        if l["t"] == "lake":
            l["r"] = features.lake_radius(l["n"])
            l["shape"] = features.lake_shape(l["n"])
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
        # Not oceans: an ocean basin is a body of water, not a patch of crust, so
        # carrying a present-day ocean point back on its plate follows the wrong
        # thing (Tethys would ride the Indian plate south, away from the Tethyan
        # seaway). Broad ocean names keep snapLabel. Seas (epicontinental, ON
        # continental crust) DO ride the plate correctly and are the ones that
        # were mislaid — that is the fix.
        plspec = PLATEAU_LABEL.get(l["n"])
        if rec is not None and plspec is not None:
            key, a1w, a0w = plspec
            l["a1"], l["a0"] = a1w, a0w
            tr = _plateau_track(key, max(a1w, a0w), rec)
            if len(tr) > 1:
                l["tr"] = tr
                tracked += 1
            continue
        wspec = water_specs.get(l["n"])
        if rec and wspec is not None:
            tr = composite_track(wspec, max(l["a0"], l["a1"]), rec)
            out_tr = []
            avoid_at = {}
            for a, lo_, la_ in tr:
                if not (min(l["a0"], l["a1"]) - 5 <= a <= max(l["a0"], l["a1"]) + 5):
                    continue
                w = nearest_water(a, lo_, la_, avoid=water_placed.get(a, ()),
                                  prefer=avoid_at.get("prev"))
                if w is not None:
                    avoid_at["prev"] = w
                if w is None:
                    out_tr.append([a, lo_, la_])
                else:
                    out_tr.append([a, round(w[0], 1), round(w[1], 1)])
                    water_placed.setdefault(a, []).append(w)
            if len(out_tr) > 1:
                # NOT smoothed, unlike the composites. nearest_water picks a
                # specific water cell per keyframe, and a rolling mean walks the
                # result off it -- smoothing these put ten sea labels back onto
                # land. A basin name that hops 20 degrees between frames is a
                # smaller error than one standing on a beach.
                l["tr"] = out_tr
                tracked += 1
                n_water += 1
            continue
        # Every OTHER sea and ocean gets snapped to water too.
        #
        # COMPOSITE_WATER hand-defines the 16 basins whose position genuinely
        # needs two margins to pin down. The rest were left to the app's
        # snapLabel, and an audit against the shipped terrain found eleven of
        # them standing on dry land for a third or more of their window --
        # Mid-Atlantic Ridge on Africa at 100 Ma, the Boreal Sea 692 m up. Same
        # cause as the sixteen, so the same cure: sample the label's own
        # position per keyframe and move it to the nearest real water.
        #
        # A SEA rides the crust it floods, so its base position comes from the
        # plate track. An OCEAN does not -- a basin is water, and carrying a
        # present-day point back on its plate follows the wrong thing (Tethys
        # would ride India south) -- so an ocean's base stays its authored coord
        # and only the water snap moves it.
        if l["t"] in ("sea", "ocean"):
            lo_w, hi_w = min(l["a0"], l["a1"]), max(l["a0"], l["a1"])
            base = {}
            if (rec and l["t"] == "sea" and lo_w < 540
                    and coord_is_present_day(l)):
                span = min(540, max(5, hi_w))
                try:
                    btr, _ = rec.track(l["lon"], l["lat"], span)
                    for a_, x_, y_ in btr:
                        base[int(round(a_ / 5.0)) * 5] = (x_, y_)
                except Exception:
                    base = {}
            a_ = math.floor(lo_w / 5.0) * 5.0
            out_tr, prev_w = [], None
            while a_ <= math.ceil(hi_w / 5.0) * 5.0 + 0.01:
                key = int(round(a_ / 5.0)) * 5
                if base:
                    near = min(base, key=lambda k: abs(k - key))
                    bx, by = base[near]
                else:
                    bx, by = l["lon"], l["lat"]
                w = nearest_water(key, bx, by, avoid=water_placed.get(key, ()),
                                  prefer=prev_w)
                if w is None:
                    out_tr.append([key, round(bx, 1), round(by, 1)])
                else:
                    prev_w = w
                    out_tr.append([key, round(w[0], 1), round(w[1], 1)])
                    water_placed.setdefault(key, []).append(w)
                a_ += 5.0
            if len(out_tr) > 1:
                # NOT smoothed, unlike the composites. nearest_water picks a
                # specific water cell per keyframe, and a rolling mean walks the
                # result off it -- smoothing these put ten sea labels back onto
                # land. A basin name that hops 20 degrees between frames is a
                # smaller error than one standing on a beach.
                l["tr"] = out_tr
                tracked += 1
                n_water += 1
            continue
        spec = composites.get(l["n"])
        if rec and spec is not None:
            tr = composite_track(spec, max(l["a0"], l["a1"]), rec)
            if len(tr) > 1:
                raw_comp[l["n"]] = tr
                comp_window[l["n"]] = (min(l["a0"], l["a1"]), max(l["a0"], l["a1"]))
                comp_label[l["n"]] = l
            continue
        if rec and l["t"] != "ocean" and min(l["a0"], l["a1"]) < 540:
            span = min(540, max(l["a0"], l["a1"]))
            if span >= 5 and coord_is_present_day(l):
                tr, _ = rec.track(l["lon"], l["lat"], span)
                if len(tr) > 1:
                    l["tr"] = tr
                    tracked += 1
            elif span >= 5:
                untracked_bad_coord.append(l["n"])
    if raw_comp:
        order = getattr(features, "COMPOSITE_ORDER", None) or list(composites)
        order = [n for n in order if n in raw_comp] + \
                [n for n in raw_comp if n not in order]
        fixed = resolve_to_landmasses(raw_comp, comp_window, order)
        for name, tr in fixed.items():
            if len(tr) > 1:
                deep = (min(a for a, lo, la in tr) >= 500
                        or max(a for a, lo, la in tr) >= 560)
                comp_label[name]["tr"] = smooth_track(tr, win=11 if deep else 5)
                tracked += 1
                n_comp += 1
    if n_comp:
        print(f"  {n_comp} paleocontinents positioned from their modern fragments")
    if n_water:
        print(f"  {n_water} seas and oceans positioned from their margins")
    if untracked_bad_coord:
        print(f"  {len(untracked_bad_coord)} labels left untracked — their coord is "
              f"not a present-day position: "
              f"{', '.join(sorted(untracked_bad_coord)[:8])}"
              + (" ..." if len(untracked_bad_coord) > 8 else ""))
    json.dump(out, open(f"{WEB}/labels.json", "w"), separators=(",", ":"))
    have = sum(1 for l in out if "d" in l)
    phased = sum(1 for l in out if "ph" in l)
    print(f"labels: {len(out)} ({have} with descriptions, {phased} phased, {tracked} plate-tracked)")


# ---------- browsable intervals + supercontinents ----------
def build_eras():
    out = {"intervals": eras.intervals(),
           "supercontinents": eras.supercontinents(),
           "glaciations": eras.glaciations()}
    json.dump(out, open(f"{WEB}/eras.json", "w"), separators=(",", ":"))
    print(f"eras: {len(out['intervals'])} intervals, "
          f"{len(out['supercontinents'])} supercontinents, "
          f"{len(out['glaciations'])} glaciations")


# ---------- biomes, life through time, regional fossil record ----------
def build_life():
    # Tag the global list with what was NOT global, so the app's fallback can
    # stop listing an African ape under North America.
    gl = life.life()
    tagged = 0
    for e in gl:
        for t in e.get("taxa", []):
            en = life.endemic(t.get("n") or t.get("name", ""))
            if en:
                t["en"] = en
                tagged += 1
    print(f"  {tagged} global taxa tagged with a region restriction")
    out = {"biomes": life.biomes(), "life": gl,
           "regional": life.regional(), "icons": life.icons(),
           "regionTaxa": life.region_taxa(), "sparse": life.sparse(),
           "labelRegion": {k: sorted(v) for k, v in life.LABEL_REGION.items()},
           "credits": life.credits()}
    json.dump(out, open(f"{WEB}/life.json", "w"), separators=(",", ":"))
    spans = sum(len(v) for v in out["regionTaxa"].values())
    print(f"life: {len(out['biomes'])} biome samples, {len(out['life'])} intervals, "
          f"{len(out['regional'])} regions, {len(out['icons'])} illustrations, "
          f"{len(out['regionTaxa'])} regions x {spans} spans of local biota, "
          f"{len(out['credits'])} credited")
    # The global list is thin on marine taxa in the Cenozoic, which is exactly
    # where the old code used to cross realms. Surface that as a build warning
    # so it is visible rather than only showing up as land animals in an ocean.
    for e in out["life"]:
        for realm, label in (("sea", "marine"), ("land", "terrestrial")):
            n = sum(1 for t in e["taxa"] if (t["realm"] == "sea") == (realm == "sea"))
            if n == 0:
                print(f"  note: {e['interval']} has no {label} taxa in the global list")


if __name__ == "__main__":
    build_timeline()
    build_boundaries()
    build_plates()
    build_hotspots()
    build_labels()
    build_eras()
    build_life()
