"""Bake the BELT-TYPE channel into `_t`'s alpha: how much of an ARC this belt is (WP-10, item 2).

WHY. `_t` carries shortening and strike, and the atlas draws fold-belt ridges
wherever they say "belt". That is right for the Zagros and the Himalaya and
wrong for a magmatic arc: the Western Cordillera of the Andes is a chain of
volcanoes on an ignimbrite plateau, not ridge-and-valley, and the round-2
renders drew arc-parallel folds across it (register, 2026-09-02). The
difference is not an amplitude, it is a belt TYPE, and the plate model knows
it: an arc stands 150-300 km behind a trench, on the overriding plate, above
a slab of OCEANIC crust. Everything needed is already shipped --

    plates_time.json   the trench segments of every keyframe
    _e                 where the land is
    _o                 where there is real ocean crust (a spreading vector)

so the channel needs no source data: for each land cell, the great-circle
distance to the nearest trench point gives a band, and the point FAR_KM
beyond the trench along that direction says what is subducting. Continental
collision (the Himalaya, the Zagros -- both drawn as 'trench' in the
boundary set, since SUB/OCB/CCB are all one class there) has LAND, or an
epeiric sea with no crustal age (the Persian Gulf reads age 1.0 and a zero
spreading vector, the same as Kansas), on the far side and is not an arc.
The Nazca plate, the Pacific off Japan, the Indian Ocean off Sumatra all
carry a spreading vector, and those margins are.

ENCODING. Alpha = 1 + 254*(1 - arc), so a `_t` written before this channel
existed (alpha 255 by default) decodes as arc 0 and nothing changes; and the
alpha is never 0, so the lossless encoder cannot zero the RGB under it. The
shader reads gArc = 1 - T.a and takes the fold amplitude down by 0.9*gArc,
letting the dissection patches carry the arc's upland instead (a cone
patch for the volcanoes themselves is the next model).

    python3 build_arc.py            # every keyframe with a _t: alpha rewritten in place
    python3 build_arc.py 0 300      # just these ages
    python3 build_arc.py --stats 0  # what gets flagged, by region

build_tectonic.bake() calls attach() so a rebake of `_t` carries the channel.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
PLATES = os.path.join(HERE, "..", "web", "plates_time.json")
R_KM = 6371.0
BAND_IN = (80.0, 160.0)      # km behind the trench where the volcanic front begins
BAND_OUT = (300.0, 430.0)    # and where the back-arc has taken over
FAR_KM = 400.0               # the test point beyond the trench: past any gulf, onto the plate that subducts
DENSIFY_KM = 20.0
_plates = None


def _sm(a, lo, hi):
    t = np.clip((a - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.sin(la), np.cos(la) * np.sin(lo)], -1)


def trench_points(age):
    global _plates
    if _plates is None:
        _plates = json.load(open(PLATES))
    fr = _plates.get(str(int(age)))
    if not fr:
        return np.zeros((0, 3))
    pts = []
    for b in fr["b"]:
        if b.get("c") != "trench":
            continue
        p = np.asarray(b["p"], np.float64)
        if len(p) < 2:
            pts.append(_unit(p[:, 0], p[:, 1])); continue
        u = _unit(p[:, 0], p[:, 1])
        for a, c in zip(u[:-1], u[1:]):
            ang = np.arccos(np.clip(np.dot(a, c), -1.0, 1.0))
            n = max(1, int(ang * R_KM / DENSIFY_KM))
            for k in range(n):
                t = k / float(n)
                v = a * (1 - t) + c * t
                pts.append(v / np.linalg.norm(v))
        pts.append(u[-1])
    if not pts:
        return np.zeros((0, 3))
    return np.asarray(pts)


def _frame(age):
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    return next((f for f in manifest if f["age"] == age), None)


def land_mask(fr, w, h):
    e = np.asarray(Image.open(os.path.join(FIELDS, fr["e"])).convert("RGB").resize((w, h), Image.BOX))[..., 0] / 255.0
    d = e * 2.0 - 1.0
    z = np.sign(d) * d * d * 8000.0
    return z > float(fr.get("sealevel", 0.0))


def ocean_mask(fr):
    """Real ocean crust: the `_o` spreading vector is non-zero there. No-data
    (land, epeiric seas) ships as age 1.0 with a zero vector."""
    base = fr["e"][:fr["e"].rfind("_e")]
    p = os.path.join(FIELDS, base + "_o.webp")
    if not os.path.exists(p):
        return None
    o = np.asarray(Image.open(p).convert("RGB")).astype(np.float64) / 255.0
    spr = np.hypot(o[..., 1] * 2 - 1, o[..., 2] * 2 - 1)
    return spr > 0.10


def arc(age, w=512, h=256):
    fr = _frame(age)
    if fr is None:
        return None
    pts = trench_points(age)
    if len(pts) == 0:
        return np.zeros((h, w))
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    cells = _unit(LON.ravel(), LAT.ravel())
    chord, idx = cKDTree(pts).query(cells)
    ang = 2.0 * np.arcsin(np.clip(chord / 2.0, 0.0, 1.0))
    dkm = (ang * R_KM).reshape(h, w)
    band = _sm(dkm, *BAND_IN) * (1.0 - _sm(dkm, *BAND_OUT))
    # the point FAR_KM beyond the nearest trench point, along the great circle from the cell
    tp = pts[idx]
    tdir = tp - cells * np.sum(tp * cells, -1, keepdims=True)
    tn = np.linalg.norm(tdir, axis=-1, keepdims=True)
    tdir = np.where(tn > 1e-9, tdir / np.maximum(tn, 1e-9), 0.0)
    a2 = ang + FAR_KM / R_KM
    far = cells * np.cos(a2)[:, None] + tdir * np.sin(a2)[:, None]
    flon = np.degrees(np.arctan2(far[:, 2], far[:, 0]))
    flat = np.degrees(np.arcsin(np.clip(far[:, 1], -1, 1)))
    oc = ocean_mask(fr)
    if oc is None:
        return np.zeros((h, w))
    oh, ow = oc.shape
    fi = np.clip(((90.0 - flat) / 180.0 * oh).astype(int), 0, oh - 1)
    fj = (((flon + 180.0) / 360.0 * ow).astype(int)) % ow
    far_ocean = oc[fi, fj].reshape(h, w).astype(np.float64)
    far_ocean = gaussian_filter(far_ocean, 1.5, mode=("nearest", "wrap"))   # a cell's neighbours vote too
    land = land_mask(fr, w, h)
    out = band * _sm(far_ocean, 0.25, 0.6) * land
    return gaussian_filter(out, 1.0, mode=("nearest", "wrap"))


def attach(rgb, age):
    """RGB uint8 (h, w, 3) of a `_t` bake -> RGBA with the belt-type alpha."""
    a = arc(age, rgb.shape[1], rgb.shape[0])
    if a is None:
        a = np.zeros(rgb.shape[:2])
    alpha = np.round(1.0 + 254.0 * (1.0 - np.clip(a, 0, 1))).astype(np.uint8)
    return np.dstack([rgb, alpha])


def bake(age, quiet=False):
    fr = _frame(age)
    if fr is None:
        return None
    base = fr["e"][:fr["e"].rfind("_e")]
    path = os.path.join(FIELDS, base + "_t.webp")
    if not os.path.exists(path):
        return None
    rgb = np.asarray(Image.open(path).convert("RGB"))
    out = attach(rgb, age)
    Image.fromarray(out, "RGBA").save(path, "WEBP", lossless=True, quality=100, method=4, exact=True)
    a = 1.0 - (out[..., 3].astype(np.float64) - 1.0) / 254.0
    if not quiet:
        print("  %5d  arc > 0.5 on %.2f%% of cells  -> %s (%.0f kB)" % (
            age, 100 * (a > 0.5).mean(), os.path.basename(path), os.path.getsize(path) / 1024.0))
    return path


REGIONS = {"Andes W Cordillera": (-71, -67, -24, -16), "Andes E Cordillera": (-66, -63, -20, -16),
           "Cascades": (-123, -120, 41, 49), "Japan": (135, 142, 34, 40), "Sumatra": (98, 104, -4, 2),
           "Himalaya": (80, 90, 27, 30), "Zagros": (46, 54, 29, 35), "Alps": (6, 12, 45, 48),
           "Tibet": (84, 92, 32, 36), "Central America": (-92, -84, 12, 16), "Kamchatka": (156, 162, 52, 58)}


def stats(age):
    a = arc(age)
    h, w = a.shape
    for n, (lo0, lo1, la0, la1) in REGIONS.items():
        j0, j1 = int((lo0 + 180) / 360 * w), int((lo1 + 180) / 360 * w)
        i0, i1 = int((90 - la1) / 180 * h), int((90 - la0) / 180 * h)
        b = a[i0:i1, j0:j1]
        print("  %-20s arc mean %.2f   > 0.5 on %3.0f%%" % (n, b.mean(), 100 * (b > 0.5).mean()))


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]   # a future age is negative
    if "--stats" in sys.argv:
        stats(int(args[0]) if args else 0)
        return
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    ages = [int(x) for x in args] or [f["age"] for f in manifest]
    done = [p for p in (bake(a, quiet=len(ages) > 4) for a in ages) if p]
    print("belt type: %d keyframes" % len(done))


if __name__ == "__main__":
    main()
