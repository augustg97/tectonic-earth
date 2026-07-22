"""Check every map label against the terrain actually rendered underneath it.

A label carries an age window authored from the literature, and the globe draws
the elevation field. Those are two independent sources and they drift apart: the
Western Interior Seaway is labelled to 66 Ma, but the paleo-DEM has drained it by
about 72, so for the last few million years the name floats over dry land in the
southeast of the continent. That is the app contradicting itself on screen.

This samples the shipped elevation field at each label's own tracked position,
keyframe by keyframe across its window, and reports where the terrain disagrees
with what the label claims to be:

    sea / ocean labels  -> expect elevation below sea level
    everything else     -> expect land

It reports rather than edits. Some disagreements are the label being wrong, some
are a coarse 20 km DEM failing to resolve a narrow strait, and telling them apart
needs a judgement the script should not be making.

Usage:  python3 audit_labels.py [--type sea] [--min-bad 0.25]
"""
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
FIELDS = os.path.join(WEB, "fields")
Z_RANGE = 8000.0

_cache = {}


def field(age):
    """Elevation raster for the nearest shipped keyframe to this age."""
    key = round(age)
    if key in _cache:
        return _cache[key]
    # three naming schemes: future, Phanerozoic, and the authored Precambrian
    # above 540 Ma. Omitting "pre_" makes every deep-time probe silently report
    # "no data", which reads exactly like "the label is not on land".
    name = (f"fut_{abs(key):04d}_e.webp" if key < 0 else
            f"pre_{key:04d}_e.webp" if key > 540 else
            f"phan_{key:04d}_e.webp")
    p = os.path.join(FIELDS, name)
    if not os.path.exists(p):
        _cache[key] = None
        return None
    im = Image.open(p).convert("RGB")
    _cache[key] = (im.load(), im.width, im.height)
    return _cache[key]


def elev_at(age, lon, lat):
    f = field(age)
    if not f:
        return None
    px, w, h = f
    x = int((lon + 180.0) / 360.0 * w) % w
    y = int((90.0 - lat) / 180.0 * (h - 1))
    y = max(0, min(h - 1, y))
    e = px[x, y][0] / 255.0
    s = 2.0 * e - 1.0
    return math.copysign(s * s * Z_RANGE, s)


def track_pos(tr, lon, lat, age):
    """Where this label's crust sat at `age` (mirrors the app's trackPos)."""
    if not tr:
        return lon, lat
    if age <= tr[0][0]:
        return tr[0][1], tr[0][2]
    if age >= tr[-1][0]:
        return tr[-1][1], tr[-1][2]
    for i in range(len(tr) - 1):
        a0, x0, y0 = tr[i]
        a1, x1, y1 = tr[i + 1]
        if a0 <= age <= a1:
            f = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            dx = x1 - x0
            if dx > 180:
                dx -= 360
            if dx < -180:
                dx += 360
            return x0 + dx * f, y0 + (y1 - y0) * f
    return tr[-1][1], tr[-1][2]


SEA_TYPES = {"sea", "ocean"}


def main():
    only = None
    min_bad = 0.2
    for i, a in enumerate(sys.argv):
        if a == "--type" and i + 1 < len(sys.argv):
            only = sys.argv[i + 1]
        if a == "--min-bad" and i + 1 < len(sys.argv):
            min_bad = float(sys.argv[i + 1])

    labels = json.load(open(os.path.join(WEB, "labels.json")))
    if isinstance(labels, dict):
        labels = labels.get("labels", [])

    rows = []
    for l in labels:
        t = l.get("t", "")
        if only and t != only:
            continue
        a0, a1 = min(l["a0"], l["a1"]), max(l["a0"], l["a1"])
        if a1 > 540:                      # pre-Phanerozoic frames are authored
            continue
        wants_sea = t in SEA_TYPES
        ages = [a for a in range(int(math.floor(a0)), int(math.ceil(a1)) + 1, 5)]
        if not ages:
            ages = [round(a0)]
        checked, bad, worst = 0, [], None
        for age in ages:
            lon, lat = track_pos(l.get("tr"), l["lon"], l["lat"], age)
            z = elev_at(age, lon, lat)
            if z is None:
                continue
            checked += 1
            if (z < 0) != wants_sea:
                bad.append(age)
                if worst is None or abs(z) > abs(worst[1]):
                    worst = (age, z)
        if checked and len(bad) / checked >= min_bad:
            rows.append((len(bad) / checked, l["n"], t, a0, a1, bad, worst))

    rows.sort(reverse=True)
    print(f"{'label':34s} {'type':9s} window      mismatched ages")
    for frac, n, t, a0, a1, bad, worst in rows:
        span = f"{a1:g}-{a0:g}"
        b = ", ".join(str(x) for x in bad[:9]) + ("..." if len(bad) > 9 else "")
        print(f"{n[:33]:34s} {t:9s} {span:11s} {frac*100:3.0f}%  {b}")
        if worst:
            print(f"{'':34s} {'':9s} {'':11s}      worst {worst[0]} Ma: "
                  f"{worst[1]:+.0f} m")
    print(f"\n{len(rows)} labels disagree with the terrain for >={min_bad*100:.0f}%"
          f" of their window")


if __name__ == "__main__":
    main()
