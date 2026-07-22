"""Replicate the app's label placement offline, so it can be reasoned about.

snapLabel is the only thing that decides where a name is drawn, and it depends
on a detail that is easy to miss: frameAt() returns the FIRST keyframe interval
containing the age, so AT an exact keyframe age X the app is reading the field
of X-5, and one million years older it reads X. Untracked labels do a 90-degree
terrain search against that field, so a label can jump to a different continent
as the age crosses a keyframe boundary -- which is what the Gondwana name does
between 421 and 420 Ma.

Usage:  python3 probe_labels.py Gondwana 430 425 421 420 415
        python3 probe_labels.py --cambrian
"""
import json
import math
import os
import sys

import audit_labels as A

FIELDS = A.FIELDS
STEP = 5


def frame_index_age(age):
    """The keyframe whose field the app actually samples at this age."""
    # ages ascend; frameAt returns the first interval [A[k], A[k+1]] containing age
    k = math.floor(age / STEP) * STEP
    if abs(age - k) < 1e-9:          # exactly on a keyframe -> the interval below
        k -= STEP
    return k


def solid(age_key, lo, la, want_land):
    hit = n = 0
    for dy in (-4, 0, 4):
        for dx in (-6, 0, 6):
            z = A.elev_at(age_key, ((lo + dx + 540) % 360) - 180,
                          max(-88, min(88, la + dy)))
            if z is None:
                continue
            n += 1
            hit += (z > 0) == want_land
    return bool(n) and hit / n >= 0.65


def snap(label, age, tracked_radius=14):
    """Where the app draws this label at this age."""
    key = frame_index_age(age)
    tr = label.get("tr")
    base = (A.track_pos(tr, label["lon"], label["lat"], age) if tr
            else (label["lon"], label["lat"]))
    want_land = label["t"] not in ("sea", "ocean")
    if solid(key, base[0], base[1], want_land):
        return base[0], base[1], 0.0, key
    maxrad = tracked_radius if tr else 90
    astep = 15 if tr else 10
    for rad in range(4, maxrad + 1, 4):
        for a in range(0, 360, astep):
            dlon = rad * math.cos(math.radians(a)) / max(0.25, math.cos(math.radians(base[1])))
            lo = ((base[0] + dlon + 540) % 360) - 180
            la = max(-86, min(86, base[1] + rad * math.sin(math.radians(a))))
            if solid(key, lo, la, want_land):
                return lo, la, float(rad), key
    return (base[0], base[1], -1.0, key) if tr else (None, None, -1.0, key)


def load():
    p = os.path.join(A.HERE, "..", "web", "labels.json")
    d = json.load(open(p))
    return d if isinstance(d, list) else d.get("labels", [])


def visible(l, age):
    t = min(0.8, abs(l["a1"] - l["a0"]) * 0.5)
    return min(l["a0"], l["a1"]) - t <= age <= max(l["a0"], l["a1"]) + t


def report(names, ages):
    labels = {l["n"]: l for l in load()}
    for n in names:
        l = labels.get(n)
        if not l:
            print(f"{n}: NOT FOUND")
            continue
        tag = "tracked" if l.get("tr") else "untracked"
        print(f"=== {n} ({l['t']}, {tag}, window {max(l['a0'],l['a1']):g}"
              f"-{min(l['a0'],l['a1']):g}, coord {l['lon']},{l['lat']})")
        prev = None
        for age in ages:
            if not visible(l, age):
                print(f"   {age:6.1f} Ma  hidden")
                continue
            lo, la, rad, key = snap(l, age)
            if lo is None:
                print(f"   {age:6.1f} Ma  DROPPED   (field {key} Ma)")
                prev = None
                continue
            jump = ""
            if prev is not None:
                # spherical, or a step across the antimeridian reads as 180 deg
                def _u(x, y):
                    a, b = math.radians(y), math.radians(x)
                    return (math.cos(a)*math.cos(b), math.cos(a)*math.sin(b), math.sin(a))
                u1, u2 = _u(lo, la), _u(prev[0], prev[1])
                d = math.degrees(math.acos(max(-1, min(1, sum(p*q for p, q in zip(u1, u2))))))
                if d > 15:
                    jump = f"   <-- JUMPED {d:.0f} deg"
            print(f"   {age:6.1f} Ma  ({lo:7.1f},{la:6.1f})  moved {rad:4.0f} deg"
                  f"  (field {key} Ma){jump}")
            prev = (lo, la)


if __name__ == "__main__":
    _o = A.field
    A.field = lambda age: _o(int(round(age / 5.0)) * 5)
    args = sys.argv[1:]
    if args and args[0] == "--cambrian":
        report(["Gondwana", "Laurentia", "Baltica", "Siberia", "Avalonia"],
               [540, 530, 520, 510, 500, 490])
    elif args and args[0] == "--devonian":
        report(["Gondwana", "Laurussia", "Laurentia", "Baltica", "Siberia"],
               [430, 425, 421, 420, 419, 415, 410])
    elif args and args[0] == "--ediacaran":
        report(["Siberia", "Laurentia", "Pannotia", "Gondwana"],
               [600, 590, 580, 570, 560, 550, 545, 541, 540, 535, 530])
    else:
        names = [a for a in args if not a.replace(".", "").isdigit()]
        ages = [float(a) for a in args if a.replace(".", "").isdigit()]
        report(names, ages or [500])
