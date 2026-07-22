"""Fetch real organism silhouettes from PhyloPic and fit them to the icon box.

The hand-drawn icons were assembled from ellipses and wedges, which is why they
stayed blocky no matter how much anatomy was added -- a Tyrannosaurus built from
six primitives is a diagram of a Tyrannosaurus, not its outline. PhyloPic
(phylopic.org) is a library of free silhouettes traced by paleoartists from
skeletal reconstructions and life restorations, which is the research base this
needs, and it publishes per-image licence and attribution metadata.

The vectors are potrace output: 1536px-wide cubic paths, ~20 kB and 30 subpaths
each, most of them tracing speckle. Rendered at 46x31 CSS pixels that detail is
invisible and the payload is not. So each silhouette is:

  parsed -> transformed out of potrace's flipped coordinate space -> flattened
  to polylines -> speckle subpaths dropped -> Douglas-Peucker simplified ->
  normalised into the 64x40 icon box -> re-emitted at 1 decimal place.

Tolerance is set in icon-box units. The icon is 64 units wide and renders 46 px
wide, so 1 unit is 0.72 px: a 0.25-unit tolerance is a fifth of a pixel, far
below anything visible, and it takes a 20 kB trace to under 1 kB.

LICENSING. PhyloPic images are individually licensed. This module accepts only
CC0, Public Domain Mark, and CC-BY, and REFUSES CC-BY-SA and CC-BY-NC: the
share-alike terms would reach the whole project and the non-commercial term is a
usage restriction the site cannot honour. Attribution is recorded for every
image regardless of licence and written to life_credits.json for display.
"""
import json
import math
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "phylopic")
API = "https://api.phylopic.org"
UA = ("TectonicEarth/1.0 (deep-time paleogeography viewer; "
      "https://augustg97.github.io/tectonic-earth/)")

# Icon box. Height 40 with the drawing inset so nothing touches the edge.
BOX_W, BOX_H = 64.0, 40.0
PAD = 1.5

# Licences we may use. Anything else is skipped with a note.
OK_LICENCES = {
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0",
    "https://creativecommons.org/publicdomain/mark/1.0/": "PDM",
    "https://creativecommons.org/licenses/by/3.0/": "CC BY 3.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
}
# Ranked best-first: a public-domain silhouette costs the project nothing.
LICENCE_RANK = {"CC0": 0, "PDM": 1, "CC BY 4.0": 2, "CC BY 3.0": 3}


# ----------------------------------------------------------------- fetching --
def _get(url, binary=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": ("image/svg+xml" if binary
                   else "application/vnd.phylopic.v2+json")})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    return raw if binary else json.loads(raw)


def _cache_path(*parts):
    p = os.path.join(CACHE, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def build_number():
    """The API refuses paged queries without the current build number."""
    try:
        return _get(f"{API}/images?filter_name=aves")["build"]
    except Exception:
        d = _get(f"{API}/")
        return d["build"]


def search(name, build, limit=8):
    """Candidate silhouettes for a taxon name, best licence first."""
    cp = _cache_path("search", re.sub(r"[^a-z0-9]+", "_", name.lower()) + ".json")
    if os.path.exists(cp):
        with open(cp) as f:
            return json.load(f)
    url = (f"{API}/images?filter_name={urllib.request.quote(name.lower())}"
           f"&build={build}&page=0&embed_items=true")
    try:
        d = _get(url)
        time.sleep(0.25)
    except Exception as e:
        if "404" in str(e):          # no match; cache the miss
            with open(cp, "w") as f:
                json.dump([], f)
        else:
            print(f"    ! search failed for {name!r}: {e}")
        return []
    want = name.lower().split()
    out = []
    for it in d.get("_embedded", {}).get("items", [])[:limit]:
        links = it.get("_links", {})
        lic = (links.get("license") or {}).get("href", "")
        vec = (links.get("vectorFile") or {}).get("href")
        if not vec or lic not in OK_LICENCES:
            continue
        spec = ((links.get("specificNode") or {}).get("title", "")).lower()
        gen = ((links.get("generalNode") or {}).get("title", "")).lower()
        # The silhouette must actually depict what was asked for. Matching the
        # SPECIFIC node catches "Glossopteris" -> "Glossopteris browniana";
        # matching the GENERAL node catches the higher-rank case, where asking
        # for "Odonata" correctly answers with a damselfly. Without this the set
        # quietly fills with wrong animals -- Macropus returned a bushbaby.
        got = spec + " | " + gen
        if not any(w in got for w in want if len(w) > 3):
            continue
        out.append({
            "uuid": it["uuid"],
            "attribution": it.get("attribution") or "(unattributed)",
            "licence": OK_LICENCES[lic],
            "licence_url": lic,
            "vector": vec,
            "taxon": (links.get("specificNode") or {}).get("title", name),
            "clade": (links.get("generalNode") or {}).get("title", ""),
        })
    out.sort(key=lambda c: LICENCE_RANK.get(c["licence"], 9))
    with open(cp, "w") as f:
        json.dump(out, f)
    return out


def fetch_vector(cand):
    p = _cache_path("vectors", cand["uuid"] + ".svg")
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(_get(cand["vector"], binary=True))
        time.sleep(0.35)          # be a good citizen against a free API
    with open(p) as f:
        return f.read()


# ------------------------------------------------------------ path handling --
_TOKEN = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def _tokens(d):
    for m in _TOKEN.finditer(d):
        yield m.group(1) if m.group(1) else float(m.group(2))


def _bezier(p0, p1, p2, p3, steps):
    for i in range(1, steps + 1):
        t = i / steps
        u = 1 - t
        yield (u * u * u * p0[0] + 3 * u * u * t * p1[0]
               + 3 * u * t * t * p2[0] + t * t * t * p3[0],
               u * u * u * p0[1] + 3 * u * u * t * p1[1]
               + 3 * u * t * t * p2[1] + t * t * t * p3[1])


def flatten(d, steps=10):
    """SVG path data -> list of closed polylines. potrace emits M/c/l/z only."""
    subs, cur, start, pos, prev_c2 = [], [], None, (0.0, 0.0), None
    cmd, args = None, []
    it = list(_tokens(d))
    i = 0
    while i < len(it):
        t = it[i]
        if isinstance(t, str):
            cmd = t
            i += 1
            if cmd in "Zz":
                if len(cur) > 2:
                    subs.append(cur)
                cur = []
                if start:
                    pos = start
                continue
        n = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4,
             "Q": 4, "T": 2, "A": 7}[cmd.upper()]
        args = it[i:i + n]
        if len(args) < n or any(isinstance(a, str) for a in args):
            break
        i += n
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            pos = (args[0] + (pos[0] if rel else 0),
                   args[1] + (pos[1] if rel else 0))
            if len(cur) > 2:
                subs.append(cur)
            cur, start = [pos], pos
            cmd = "l" if rel else "L"      # implicit lineto after moveto
        elif c in "LT":
            pos = (args[0] + (pos[0] if rel else 0),
                   args[1] + (pos[1] if rel else 0))
            cur.append(pos)
        elif c == "H":
            pos = (args[0] + (pos[0] if rel else 0), pos[1])
            cur.append(pos)
        elif c == "V":
            pos = (pos[0], args[0] + (pos[1] if rel else 0))
            cur.append(pos)
        elif c in "CS":
            if c == "C":
                p1 = (args[0] + (pos[0] if rel else 0),
                      args[1] + (pos[1] if rel else 0))
                p2 = (args[2] + (pos[0] if rel else 0),
                      args[3] + (pos[1] if rel else 0))
                p3 = (args[4] + (pos[0] if rel else 0),
                      args[5] + (pos[1] if rel else 0))
            else:
                p1 = (2 * pos[0] - prev_c2[0], 2 * pos[1] - prev_c2[1]) \
                    if prev_c2 else pos
                p2 = (args[0] + (pos[0] if rel else 0),
                      args[1] + (pos[1] if rel else 0))
                p3 = (args[2] + (pos[0] if rel else 0),
                      args[3] + (pos[1] if rel else 0))
            cur.extend(_bezier(pos, p1, p2, p3, steps))
            prev_c2, pos = p2, p3
            continue
        elif c == "Q":
            q1 = (args[0] + (pos[0] if rel else 0),
                  args[1] + (pos[1] if rel else 0))
            q2 = (args[2] + (pos[0] if rel else 0),
                  args[3] + (pos[1] if rel else 0))
            p1 = (pos[0] + 2 / 3 * (q1[0] - pos[0]),
                  pos[1] + 2 / 3 * (q1[1] - pos[1]))
            p2 = (q2[0] + 2 / 3 * (q1[0] - q2[0]),
                  q2[1] + 2 / 3 * (q1[1] - q2[1]))
            cur.extend(_bezier(pos, p1, p2, q2, steps))
            pos = q2
        elif c == "A":
            pos = (args[5] + (pos[0] if rel else 0),
                   args[6] + (pos[1] if rel else 0))
            cur.append(pos)
        prev_c2 = None
    if len(cur) > 2:
        subs.append(cur)
    return subs


def _rdp(pts, eps):
    """Douglas-Peucker. The silhouettes are traced from raster, so they carry
    far more vertices than a 46-pixel-wide icon can show."""
    if len(pts) < 3:
        return pts
    ax, ay = pts[0]
    bx, by = pts[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy)
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = (abs(dy * px - dx * py + bx * ay - by * ax) / n if n
             else math.hypot(px - ax, py - ay))
        if d > best:
            best, bi = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return _rdp(pts[:bi + 1], eps)[:-1] + _rdp(pts[bi:], eps)


def _area(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def convert(svg, tol=0.25, speck=0.0016, flip=False):
    """PhyloPic SVG -> one path string in the 64x40 icon box.

    speck is a fraction of the largest subpath's area; potrace traces dust
    specks and stray marks as their own subpaths and at icon size they are
    indistinguishable from noise.
    """
    m = re.search(r'viewBox="([\d.\-\s]+)"', svg)
    if not m:
        return None, "no viewBox"
    vb = [float(x) for x in m.group(1).split()]
    tm = re.search(r"translate\(([-\d.]+),\s*([-\d.]+)\)\s*scale\("
                   r"([-\d.]+),\s*([-\d.]+)\)", svg)
    tx, ty, sx, sy = ((float(tm.group(1)), float(tm.group(2)),
                       float(tm.group(3)), float(tm.group(4)))
                      if tm else (0.0, 0.0, 1.0, 1.0))
    polys = []
    for d in re.findall(r'\sd="([^"]+)"', svg):
        for poly in flatten(d):
            polys.append([(x * sx + tx, y * sy + ty) for x, y in poly])
    if not polys:
        return None, "no paths"
    biggest = max(abs(_area(p)) for p in polys)
    polys = [p for p in polys if abs(_area(p)) >= biggest * speck]

    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if w <= 0 or h <= 0:
        return None, "degenerate"
    s = min((BOX_W - 2 * PAD) / w, (BOX_H - 2 * PAD) / h)
    ox = (BOX_W - w * s) / 2 - min(xs) * s
    oy = (BOX_H - h * s) / 2 - min(ys) * s

    out = []
    for poly in polys:
        q = [((x * s + ox) if not flip else BOX_W - (x * s + ox),
              y * s + oy) for x, y in poly]
        q = _rdp(q, tol)
        if len(q) < 3:
            continue
        out.append("M" + " ".join(f"{x:.1f} {y:.1f}" for x, y in q) + "Z")
    if not out:
        return None, "simplified away"
    return '<path d="%s"/>' % "".join(out), None


BUDGET = 1500   # chars of markup per icon


def silhouette(name, build, tol=0.22, flip=False, pick=0, budget=BUDGET):
    """Best available silhouette for a taxon name, as (markup, credit).

    Simplification is adaptive: a leaf with fine venation needs a coarser
    tolerance than a dinosaur outline to land in the same byte budget, and at
    46 px neither loses anything a viewer could see.
    """
    cands = search(name, build)
    if not cands:
        return None, None
    cand = cands[min(pick, len(cands) - 1)]
    try:
        svg = fetch_vector(cand)
    except Exception as e:
        print(f"    ! vector fetch failed for {name!r}: {e}")
        return None, None
    path = None
    for t in (tol, 0.35, 0.5, 0.7, 1.0, 1.4):
        path, err = convert(svg, tol=t, flip=flip)
        if not path:
            print(f"    ! convert failed for {name!r}: {err}")
            return None, None
        if len(path) <= budget:
            break
    return path, cand


if __name__ == "__main__":
    b = build_number()
    print("build", b)
    for n in ("Tyrannosaurus", "Stegosaurus", "Anomalocaris", "Glossopteris"):
        p, c = silhouette(n, b)
        if p:
            print(f"{n:16s} {len(p):5d} chars  {c['licence']:9s} {c['attribution']}")
