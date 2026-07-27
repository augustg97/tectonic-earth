"""A5 / F1 -- the shipped reconstruction against two published series.

The app's palaeogeography has never been checked against anything outside its own
pipeline. Three reference series exist on disk:

    Deep Time Maps(TM)   32 global Mollweide maps, Present -> 525 Ma   (c) CPGS
    Scotese PALEOMAP     16 numbered maps, 0 -> 650 Ma                 (c) C R Scotese
    Scotese Future World +50 / +150 / +250 Myr                         (c) C R Scotese

They are COPYRIGHTED. This script measures against them and never reproduces
them: nothing it writes contains reference pixels.

The two series are not the same kind of witness, and the report must not
pretend otherwise:

  * Deep Time Maps is Ron Blakey's reconstruction (Colorado Plateau Geosystems).
    It is INDEPENDENT of ours -- different author, different plate model,
    different palaeogeographic judgement. Disagreement is a real result.
  * Our terrain comes from the Scotese & Wright PaleoDEMs, so the Scotese series
    is a SELF-CONSISTENCY check. It should agree; if it does not, our pipeline
    broke something on the way in.

WHAT IS MEASURED, in the handoff's value order

  1. land fraction        the cheapest and most diagnostic number
  2. shelf-sea extent     does our 20 km DEM under-resolve epeiric seas
  3. ice extent           the spatial pattern, which an area check cannot see
  4. continental position where a coastline sits, fitted as a rigid longitude
                          offset -- palaeomagnetism fixes latitude and never
                          longitude, so that is the axis a frame error lives on

METHOD

  The reference maps are Mollweide; our fields are equirectangular. Every
  reference pixel is inverted to (lon, lat) and our field is sampled there, so
  the comparison happens on the reference's own grid. Mollweide is EQUAL-AREA,
  so a pixel count on that grid is already an area integral -- no cos(lat)
  weighting, and none of the polar exaggeration that makes the eye the worst
  available instrument for this.

  The projection is validated on the present-day map before anything else is
  believed: 0 Ma is the one age where both sides are the real Earth, so any
  disagreement there is the reprojection, not the model.

  Class colours are learned from the present-day map at known localities rather
  than guessed, and the shallow-water cut in OUR field is calibrated so that the
  two agree at 0 Ma -- then frozen and applied unchanged at every other age.

DECODING THE FIELD -- a correction

  build/fieldpack.py uses Z_RANGE = 8000.0, and so does every other consumer in
  build/. `modeling/frame_experiment.py:_decode()` uses 11000.0, which is wrong;
  the handoff prompt inherited the error. It does not move that experiment's
  headline (its land/abyss split is scored with one threshold across all three
  frames, so the ranking is untouched) but its "shelf" boundary is really -364 m,
  not -500 m. This script uses 8000.0.

    ../../venv/bin/python audit_reconstruction.py             # everything
    ../../venv/bin/python audit_reconstruction.py --validate  # 0 Ma check only
    ../../venv/bin/python audit_reconstruction.py --dtm
    ../../venv/bin/python audit_reconstruction.py --scotese
    ../../venv/bin/python audit_reconstruction.py --future
    ../../venv/bin/python audit_reconstruction.py --selftest

READ-ONLY. It writes nothing and imports build/ only to reuse the app's own
ice arithmetic.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
FIELDS = os.path.join(ROOT, "web", "fields")
REFDIR = os.path.join(ROOT, "Deep Time Maps and Resources")
PALEOMAP_DIR = os.path.join(ROOT, "data", "paleomap_gpm",
                            "Scotese PaleoAtlas_v3", "PALEOMAP Global Plate Model")
PALEOMAP_ROT = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlateModel.rot")
PALEOMAP_POLY = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlatePolygons.gpml")

Z_RANGE = 8000.0            # build/fieldpack.py -- NOT frame_experiment's 11000
EARTH_KM2 = 5.101e8
R_EARTH_KM = 6371.0


# --------------------------------------------------------------- projection --
def moll_inverse(h, w, lon0=0.0):
    """(lon, lat, inside) for the centre of every pixel of an h x w Mollweide.

    The ellipse is taken to be inscribed in the image, which is the framing the
    Deep Time Maps series uses -- verified: their 1200x600 maps have non-black
    pixels reaching x=0 and x=1199 on the centre row and y=0/y=599 on the centre
    column, so semi-axes are exactly w/2 and h/2.
    """
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5 - w / 2.0) / (w / 2.0)          # -1 .. +1
    Y = -(yy + 0.5 - h / 2.0) / (h / 2.0)         # +1 at the top
    inside = X * X + Y * Y <= 1.0
    th = np.arcsin(np.clip(Y, -1.0, 1.0))
    lat = np.degrees(np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1)))
    with np.errstate(divide="ignore", invalid="ignore"):
        lon = lon0 + 180.0 * X / np.cos(th)
    inside &= np.abs(lon - lon0) <= 180.0 + 1e-9
    lon = ((lon + 180.0) % 360.0) - 180.0
    return lon, lat, inside


def moll_forward(lon, lat, h, w, lon0=0.0):
    """(px, py) of one (lon, lat). Only used by the selftest."""
    la = math.radians(lat)
    th = la
    for _ in range(60):                            # Newton on 2t + sin2t = pi sin(lat)
        f = 2 * th + math.sin(2 * th) - math.pi * math.sin(la)
        d = 2 + 2 * math.cos(2 * th)
        if abs(d) < 1e-12:
            break
        th -= f / d
    X = (((lon - lon0 + 180.0) % 360.0) - 180.0) / 180.0 * math.cos(th)
    return w / 2.0 + X * (w / 2.0) - 0.5, h / 2.0 - math.sin(th) * (h / 2.0) - 0.5


# ---------------------------------------------------- reference classification --
# Learned from 00-Ma-PresentMOLL-tn.jpg at localities whose class is not in
# question. Median RGB of a 3x3 patch:
#
#   Sahara (12E,22N)      231,200,135     Amazon (60W,5S)       41, 67, 29
#   Kalahari (22E,24S)    203,173,122     Congo  (22E,2S)       58, 82, 32
#   Greenland (42W,72N)   255,255,255     Antarctica (0,85S)   231,230,236
#   North Sea (3E,56N)     23,167,206     Hudson (85W,60N)       6,154,198
#   Yellow Sea (123E,35N)  20,160,201     Patagonian shelf      14,155,199
#   Central Pacific        2, 71,112      Central Atlantic       1, 52, 87
#   Indian Ocean           2, 95,136      Gulf of Mexico deep    0, 91,125
#
# Three separations fall straight out and none of them is a close call:
#   ocean   B exceeds R by a wide margin        (land never does, ice never does)
#   ice     bright AND NEUTRAL                   (see below)
#   shallow the green channel                   (150-180 inshore, 50-100 abyssal)
#
# "Neutral" rather than "unsaturated", and the difference was found the hard
# way. A saturation cut of 28 read 1.1% of the 420 Ma map as ice, all of it at
# |lat| < 30 in a world with no ice sheets: the culprit is a pale green-grey
# Silurian lowland, median RGB (217,228,212). Real ice in this series is
# genuinely neutral -- (250,250,251) at the present pole, (246,246,247) on the
# Gondwanan sheet at 300 Ma, (231,231,228) at the LGM -- so requiring
# |R-G| and |G-B| to be small separates them, where one saturation number
# cannot. Measured cost of the tighter rule: it reads 13.0 Mkm2 of present-day
# ice against the real 15.7, and 30.5 at the LGM against ~37, i.e. it runs
# about 17% low at both ends because shaded ice margins are neither bright nor
# neutral. That bias is consistent, so ratios between ages survive it.
UNKNOWN, LAND, SHALLOW, DEEP, ICE = 0, 1, 2, 3, 4
CLASS_NAMES = {UNKNOWN: "unknown", LAND: "land", SHALLOW: "shallow",
               DEEP: "deep", ICE: "ice"}

G_SHALLOW = 135      # the trough between the two ocean modes; see _selftest


def classify_ref(im, g_shallow=G_SHALLOW):
    """Class per pixel of an RGB reference map."""
    R = im[..., 0].astype(np.int16)
    G = im[..., 1].astype(np.int16)
    B = im[..., 2].astype(np.int16)
    mx = im.max(axis=2).astype(np.int16)
    mn = im.min(axis=2).astype(np.int16)
    cls = np.zeros(im.shape[:2], np.int8)
    ocean = (B > R + 30) & (B >= G - 10)
    ice = (~ocean) & (mn >= 150) & (np.abs(R - G) <= 8) & (np.abs(G - B) <= 14)
    land = (~ocean) & (~ice) & (mx >= 30)
    cls[land] = LAND
    cls[ocean & (G >= g_shallow)] = SHALLOW
    cls[ocean & (G < g_shallow)] = DEEP
    cls[ice] = ICE
    return cls


def caption_mask(im, inside):
    """Rectangle covering the "<age> / (c) CPGS" caption burnt into every map.

    Found, not assumed: bright pixels that lie WELL outside the map ellipse can
    only be caption, so their bounding box locates it, and the box is then
    extended to the image edge to catch the glyph rows that do fall inside.
    Masked identically on both sides of every comparison, so it costs coverage
    and never biases a difference.
    """
    h, w = inside.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r2 = ((xx + 0.5 - w / 2.0) / (w / 2.0)) ** 2 + ((yy + 0.5 - h / 2.0) / (h / 2.0)) ** 2
    outer = (im.max(axis=2) > 60) & (r2 > 1.05)
    m = np.zeros((h, w), bool)
    if not outer.any():
        return m
    ys, xs = np.nonzero(outer)
    m[max(0, ys.min() - 6):ys.max() + 7, 0:min(w, xs.max() + 11)] = True
    return m


def ref_grid(path, lon0=0.0, g_shallow=G_SHALLOW):
    """-> (cls, valid, lon, lat) on the reference's own equal-area pixel grid."""
    im = np.asarray(Image.open(path).convert("RGB"))
    h, w, _ = im.shape
    lon, lat, inside = moll_inverse(h, w, lon0)
    yy, xx = np.mgrid[0:h, 0:w]
    r2 = ((xx + 0.5 - w / 2.0) / (w / 2.0)) ** 2 + ((yy + 0.5 - h / 2.0) / (h / 2.0)) ** 2
    valid = inside & (r2 <= 0.985) & (im.max(axis=2) >= 30) & ~caption_mask(im, inside)
    return classify_ref(im, g_shallow), valid, lon, lat


# ------------------------------------------------------------------ our side --
def decode_elev(img_u8):
    t = img_u8.astype(np.float32) / 255.0 * 2.0 - 1.0
    return np.sign(t) * (t * t) * Z_RANGE


def keyframe_base(age):
    """The shipped basename nearest `age` (negative = future), and the age used."""
    a = 5 * int(round(age / 5.0))
    if a < 0:
        return "fut_%04d" % abs(a), a
    return ("pre_%04d" % a) if a > 540 else ("phan_%04d" % a), a


def load_elev(age):
    base, used = keyframe_base(age)
    p = os.path.join(FIELDS, base + "_e.webp")
    if not os.path.exists(p):
        return None, None
    return decode_elev(np.asarray(Image.open(p).convert("L"))), used


def sample_ours(Z, lon, lat, dlon=0.0):
    """Nearest-neighbour sample of an equirectangular field at (lon+dlon, lat)."""
    H, W = Z.shape
    yi = np.clip(((90.0 - lat) / 180.0 * H).astype(np.int32), 0, H - 1)
    xi = (((lon + dlon + 180.0) / 360.0 * W).astype(np.int32)) % W
    return Z[yi, xi]


def sample_ours_ss(Z, lon, lat, inside, h, w, lon0=0.0, n=3):
    """Land fraction within each Mollweide pixel, by n x n subpixel sampling.

    The reference is a thumbnail (1200x600 ~ 0.3 deg) and our field is 4096x2048
    (~0.09 deg), so a single nearest-neighbour sample throws away most of ours at
    every coastline. Averaging the binary land indicator over the pixel footprint
    is what a cartographer drawing at the reference's resolution would do.
    """
    H, W = Z.shape
    acc = np.zeros((h, w), np.float32)
    cnt = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    for iy in range(n):
        for ix in range(n):
            X = (xx + (ix + 0.5) / n - w / 2.0) / (w / 2.0)
            Y = -(yy + (iy + 0.5) / n - h / 2.0) / (h / 2.0)
            ok = X * X + Y * Y <= 1.0
            th = np.arcsin(np.clip(Y, -1, 1))
            la = np.degrees(np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1)))
            with np.errstate(divide="ignore", invalid="ignore"):
                lo = lon0 + 180.0 * X / np.cos(th)
            ok &= np.abs(lo - lon0) <= 180.0
            lo = ((lo + 180.0) % 360.0) - 180.0
            yi = np.clip(((90.0 - la) / 180.0 * H).astype(np.int32), 0, H - 1)
            xi = (((lo + 180.0) / 360.0 * W).astype(np.int32)) % W
            acc += np.where(ok, (Z[yi, xi] >= 0.0), 0.0)
            cnt += ok
    return np.divide(acc, np.maximum(cnt, 1), where=cnt > 0) * inside


def our_ice(age, H=512, W=1024):
    """The app's own ice arithmetic, from build/ice_audit.py, at `age`.

    Imported rather than reimplemented so that this audit and the app's ice
    audit cannot drift apart.
    """
    if BUILD not in sys.path:
        sys.path.insert(0, BUILD)
    try:
        import ice_audit
    except Exception:                                        # noqa: BLE001
        return None
    base, used = keyframe_base(age)
    try:
        man = json.load(open(os.path.join(FIELDS, "manifest.json")))
    except Exception:                                        # noqa: BLE001
        return None
    rec = next((m for m in man if m["age"] == used), None)
    if rec is None:
        return None
    z, rf = ice_audit.fields(base, H, W)
    if z is None:
        return None
    land, li, si, gl, sn, T = ice_audit.ice_masks(z, rf, used, rec["iceT"], rec["seaT"])
    return np.maximum(li, np.maximum(gl, si * 0.0))          # sheet + mountain ice


# ------------------------------------------------------------------- metrics --
def unit_vectors(lon, lat):
    la, lo = np.radians(lat), np.radians(lon)
    c = np.cos(la)
    return np.stack([c * np.cos(lo), c * np.sin(lo), np.sin(la)], axis=-1)


def displacement_km(lon_a, lat_a, lon_b, lat_b, cap=200000):
    """Mean/median/p90 great-circle distance from each A point to the nearest B."""
    from scipy.spatial import cKDTree
    if len(lon_a) == 0 or len(lon_b) == 0:
        return None
    if len(lon_a) > cap:
        idx = np.linspace(0, len(lon_a) - 1, cap).astype(int)
        lon_a, lat_a = lon_a[idx], lat_a[idx]
    if len(lon_b) > cap:
        idx = np.linspace(0, len(lon_b) - 1, cap).astype(int)
        lon_b, lat_b = lon_b[idx], lat_b[idx]
    tree = cKDTree(unit_vectors(lon_b, lat_b))
    d, _ = tree.query(unit_vectors(lon_a, lat_a))
    gc = 2.0 * np.arcsin(np.clip(d / 2.0, 0, 1)) * R_EARTH_KM
    return float(gc.mean()), float(np.median(gc)), float(np.percentile(gc, 90))


def lat_profile(mask, lat, valid, step=10.0):
    """Fraction of each latitude band that is `mask`. Bands are equal-area free:
    Mollweide pixels all carry the same area, so this is a plain count."""
    edges = np.arange(-90, 90 + step, step)
    out = []
    for i in range(len(edges) - 1):
        b = valid & (lat >= edges[i]) & (lat < edges[i + 1])
        out.append(float(mask[b].mean()) if b.sum() > 200 else np.nan)
    return np.array(out), edges


def kappa(a, b):
    """Cohen's kappa for two boolean masks.

    Agreement % is a trap here and the trap gets worse with age: at 450 Ma the
    reference is 85% ocean, so a map that predicted "ocean everywhere" would
    score 85% agreement. Kappa is agreement above what chance would give at the
    same base rates -- 0 means no skill, 1 means perfect.
    """
    n = a.size
    if n == 0:
        return float("nan")
    po = float((a == b).mean())
    pa, pb = float(a.mean()), float(b.mean())
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if abs(1 - pe) > 1e-9 else float("nan")


# ------------------------------------------- the frame, from the rotations ---
# A third witness, and the one that settles who is out of step with whom.
# Our Phanerozoic terrain is the Scotese & Wright PaleoDEM read straight through
# (build/build_frames.py:read_dem does periodicity repair and nothing else), so
# it should sit in the PALEOMAP frame by construction. Advecting present-day land
# with PALEOMAP_PlateModel.rot and scoring the result against our own field
# tests that claim directly -- and the same advected mask can then be scored
# against each published map, which localises any offset to a specific witness
# instead of leaving it hanging between three.
def paleomap_available():
    return os.path.exists(PALEOMAP_ROT) and os.path.exists(PALEOMAP_POLY)


_PID_CACHE = {}


def _plate_ids(step=2.0):
    """Plate id per cell of a `step`-degree grid, partitioned at t=0."""
    if step in _PID_CACHE:
        return _PID_CACHE[step]
    import pygplates
    rot = pygplates.RotationModel(PALEOMAP_ROT)
    polys = pygplates.FeatureCollection(PALEOMAP_POLY)
    part = pygplates.PlatePartitioner(polys, rot, reconstruction_time=0)
    lats = np.arange(90 - step / 2, -90, -step)
    lons = np.arange(-180 + step / 2, 180, step)
    pid = np.full((len(lats), len(lons)), -1, np.int32)
    for i, la in enumerate(lats):
        for j, lo in enumerate(lons):
            f = part.partition_point(pygplates.PointOnSphere(float(la), float(lo)))
            if f is not None:
                pid[i, j] = f.get_feature().get_reconstruction_plate_id()
    _PID_CACHE[step] = (pid, rot)
    return _PID_CACHE[step]


def paleomap_land(age, out_h=180, out_w=360, src=None):
    """Present-day land advected to `age` by the PALEOMAP rotations.

    Negative `age` is the future. Returns a boolean (out_h, out_w) mask on an
    equirectangular grid, or None if the model is not on disk.

    The source grid must be FINER than the output or the scatter leaves holes
    that look like missing continent: sampled at 1 deg onto a 0.5 deg output
    this returned 7.3% land at age 0, where the answer is 29%. Three source
    samples per output cell per axis fills it.
    """
    if not paleomap_available():
        return None
    if src is None:
        src = 180.0 / out_h / 3.0
    import pygplates
    pid_grid, rot = _plate_ids()
    ph, pw = pid_grid.shape
    Z0, _ = load_elev(0)
    if Z0 is None:
        return None
    lats = np.arange(90 - src / 2, -90, -src)
    lons = np.arange(-180 + src / 2, 180, src)
    LON, LAT = np.meshgrid(lons, lats)
    H0, W0 = Z0.shape
    yi = np.clip(((90.0 - LAT) / 180.0 * H0).astype(int), 0, H0 - 1)
    xi = (((LON + 180.0) / 360.0 * W0).astype(int)) % W0
    land = Z0[yi, xi] >= 0.0
    gy = np.clip(((90.0 - LAT) / 180.0 * ph).astype(int), 0, ph - 1)
    gx = (((LON + 180.0) / 360.0 * pw).astype(int)) % pw
    pids = pid_grid[gy, gx]
    out = np.zeros((out_h, out_w), bool)
    V = unit_vectors(LON[land], LAT[land])
    P = pids[land]
    for p in np.unique(P):
        if p < 0:
            continue
        try:
            fr = rot.get_rotation(float(age), int(p))
        except Exception:                                    # noqa: BLE001
            continue
        pole, ang = fr.get_euler_pole_and_angle()
        pl, po = pole.to_lat_lon()
        M = _rodrigues(_unit(po, pl), math.degrees(ang))
        W = (M @ V[P == p].T).T
        la = np.degrees(np.arcsin(np.clip(W[:, 2], -1, 1)))
        lo = np.degrees(np.arctan2(W[:, 1], W[:, 0]))
        ry = np.clip(((90.0 - la) / 180.0 * out_h).astype(int), 0, out_h - 1)
        rx = (((lo + 180.0) / 360.0 * out_w).astype(int)) % out_w
        out[ry, rx] = True
    return out


def best_dlon_masks(a_land, b_land, lat_grid, coarse=5.0):
    """Rigid longitude offset aligning `b` onto `a` on a shared equirect grid.

    Positive = `a` sits that many degrees EAST of `b`. Scored with cos(lat)
    weights, and reported alongside kappa because plain agreement is inflated by
    the ocean fraction.
    """
    w = np.cos(np.radians(lat_grid))
    W = a_land.shape[1]
    best = (-2.0, 0.0)
    for d in np.arange(-180.0, 180.0, coarse):
        k = int(round(d / 360.0 * W))
        s = float((w * (np.roll(b_land, k, axis=1) == a_land)).sum() / w.sum())
        if s > best[0]:
            best = (s, d)
    d0 = best[1]
    for d in np.arange(d0 - coarse, d0 + coarse + 0.5, 1.0):
        k = int(round(d / 360.0 * W))
        s = float((w * (np.roll(b_land, k, axis=1) == a_land)).sum() / w.sum())
        if s > best[0]:
            best = (s, d)
    d = ((best[1] + 180.0) % 360.0) - 180.0
    k = int(round(d / 360.0 * W))
    return d, best[0], kappa(a_land.ravel(), np.roll(b_land, k, axis=1).ravel())


def best_dlon(Z, ref_land, valid, lon, lat, coarse=5.0):
    """Rigid longitude offset that best aligns our land with the reference's.

    Longitude is the axis a reconstruction frame is free on -- palaeomagnetism
    gives palaeolatitude and never palaeolongitude -- so a large fitted offset is
    the signature of a frame difference and a large residual after it is a
    genuine disagreement about geography.
    """
    def score(d):
        ours = sample_ours(Z, lon, lat, d) >= 0.0
        return float((ours[valid] == ref_land[valid]).mean())
    cand = np.arange(-180.0, 180.0, coarse)
    s = [score(d) for d in cand]
    d0 = cand[int(np.argmax(s))]
    fine = np.arange(d0 - coarse, d0 + coarse + 0.5, 1.0)
    sf = [score(d) for d in fine]
    dbest = float(fine[int(np.argmax(sf))])
    # sampling OUR field at lon+d to match the reference at lon means our
    # feature sits d degrees EAST of theirs, so the reference-minus-ours
    # convention used everywhere else in this file is the negation.
    return -(((dbest + 180.0) % 360.0) - 180.0), float(max(sf)), score(0.0)


# --------------------------------------------------------- the DTM series ----
# age in Ma per file. 021-Ka is the Last Glacial Maximum, 21 ka: our nearest
# keyframe is 0 Ma, which is the modern world and not the LGM, so it is reported
# separately and excluded from the summary rather than silently matched.
DTM_LGM = "021-Ka-Pleistocene_GMaxMOLL-tn.jpg"


def dtm_files():
    out = []
    for p in sorted(glob.glob(os.path.join(REFDIR, "*.jpg"))):
        b = os.path.basename(p)
        if "moll" not in b.lower():
            continue
        head = b.split("-")[0]
        if b == DTM_LGM:
            out.append((0.021, p, True))
            continue
        try:
            age = float(head)
        except ValueError:
            continue
        out.append((age, p, False))
    return sorted(out)


def ref_land_equirect(path, out_h=180, out_w=360, lon0=0.0, scotese=False):
    """A reference map's land mask, rasterised onto an equirectangular grid.

    Majority vote over the reference pixels falling in each cell. Cells that
    receive no sample (the caption patch) come back False and are reported.
    """
    if scotese:
        cls, valid, lon, lat = scotese_grid(path)
        ref = (cls == LAND) & valid
    else:
        cls, valid, lon, lat = ref_grid(path, lon0)
        ref = ((cls == LAND) | (cls == ICE)) & valid
    yi = np.clip(((90.0 - lat) / 180.0 * out_h).astype(int), 0, out_h - 1)
    xi = (((lon + 180.0) / 360.0 * out_w).astype(int)) % out_w
    tot = np.zeros((out_h, out_w), np.int32)
    hit = np.zeros((out_h, out_w), np.int32)
    np.add.at(tot, (yi[valid], xi[valid]), 1)
    np.add.at(hit, (yi[ref], xi[ref]), 1)
    cov = tot > 0
    return (hit > tot / 2) & cov, cov


def run_frames(ages=(50, 90, 150, 200, 250, 300, 350, 400, 450, 500)):
    """Who is out of step with whom.

    Three land masks per age -- ours, PALEOMAP's rotations applied to today's
    land, and each published map -- pairwise, as a rigid longitude offset. Our
    terrain should sit at ~0 against PALEOMAP because it IS the PaleoDEM; the
    interesting question is where the published maps sit.
    """
    if not paleomap_available():
        print("PALEOMAP model not on disk; frame triangulation skipped")
        return []
    out_h, out_w = 180, 360
    lat_grid = np.repeat((90 - (np.arange(out_h) + 0.5) / out_h * 180)[:, None], out_w, 1)
    dtm = {int(a): p for a, p, lgm in dtm_files() if not lgm}
    sco = {v: os.path.join(REFDIR, k) for k, v in SCOTESE.items()}
    print("FRAME TRIANGULATION -- rigid longitude offset between each pair")
    print("PALEOMAP = present-day land advected by PALEOMAP_PlateModel.rot.")
    print("Our terrain is that model's own PaleoDEM, so ours-vs-PALEOMAP is the")
    print("control: it should be near zero, and anything else is a pipeline bug.\n")
    hdr = (f"{'age':>6} {'ours vs PALEOMAP':>17} {'DTM vs PALEOMAP':>17} "
           f"{'DTM vs ours':>13} {'Scotese vs ours':>16}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for age in ages:
        pl = paleomap_land(age, out_h, out_w)
        Z, _ = load_elev(age)
        if pl is None or Z is None:
            continue
        H, W = Z.shape
        yi = np.clip(((90.0 - lat_grid) / 180.0 * H).astype(int), 0, H - 1)
        lon_grid = np.tile((np.arange(out_w) + 0.5) / out_w * 360 - 180, (out_h, 1))
        xi = (((lon_grid + 180.0) / 360.0 * W).astype(int)) % W
        ours = Z[yi, xi] >= 0.0
        d_op, s_op, k_op = best_dlon_masks(ours, pl, lat_grid)
        r = {"age": age, "ours_vs_paleomap": d_op}
        cells = [f"{d_op:+7.0f} (k {k_op:.2f})"]
        near = min(dtm, key=lambda a: abs(a - age)) if dtm else None
        if near is not None and abs(near - age) <= 12:
            dl, _cov = ref_land_equirect(dtm[near], out_h, out_w)
            d1, s1, k1 = best_dlon_masks(dl, pl, lat_grid)
            d2, s2, k2 = best_dlon_masks(dl, ours, lat_grid)
            r["dtm_vs_paleomap"], r["dtm_vs_ours"] = d1, d2
            cells.append(f"{d1:+7.0f} (k {k1:.2f})")
            cells.append(f"{d2:+6.0f}")
        else:
            cells += ["", ""]
        nears = min(sco, key=lambda a: abs(a - age)) if sco else None
        if nears is not None and abs(nears - age) <= 16:
            sl, _cov = ref_land_equirect(sco[nears], out_h, out_w, scotese=True)
            d3, s3, k3 = best_dlon_masks(sl, ours, lat_grid)
            r["scotese_vs_ours"] = d3
            cells.append(f"{d3:+8.0f}")
        print(f"{age:6d} {cells[0]:>17} {cells[1]:>17} {cells[2]:>13} "
              f"{(cells[3] if len(cells) > 3 else ''):>16}")
        rows.append(r)
    print()
    return rows


def scotese_grid(path):
    """(cls, valid, lon, lat) for one annotated Scotese plate. Land/ocean only."""
    im = np.asarray(Image.open(path).convert("RGB"))
    e = scotese_ellipse(im)
    if e is None:
        return None, None, None, None
    cx, cy, a, b = e
    h, w, _ = im.shape
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5 - cx) / a
    Y = -(yy + 0.5 - cy) / b
    inside = X * X + Y * Y <= 0.985
    th = np.arcsin(np.clip(Y, -1, 1))
    lat = np.degrees(np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1)))
    with np.errstate(divide="ignore", invalid="ignore"):
        lon = 180.0 * X / np.cos(th)
    inside &= np.abs(lon) <= 180.0
    lon = ((lon + 180.0) % 360.0) - 180.0
    R = im[..., 0].astype(np.int16)
    G = im[..., 1].astype(np.int16)
    B = im[..., 2].astype(np.int16)
    mx = im.max(axis=2).astype(np.int16)
    mn = im.min(axis=2).astype(np.int16)
    ocean = (B > R + 25) & (B >= G - 10)
    anno = ((mn >= 145) & ((mx - mn) <= 40)) | \
           ((R > 150) & (G > 60) & (G < 175) & (B < 90))
    valid = inside & ~anno & (mx >= 30)
    cls = np.where(ocean, DEEP, LAND).astype(np.int8)
    return cls, valid, lon, lat


def calibrate_shallow_cut(lon0=0.0):
    """The depth in OUR field whose area matches the reference's shallow tint at 0 Ma.

    The tint is a cartographic class, not a depth contour, so it has to be
    calibrated rather than assumed -- and 0 Ma is the only age where both sides
    are the same planet. Returns (cut_m, ref_frac, our_frac).
    """
    p = os.path.join(REFDIR, "00-Ma-PresentMOLL-tn.jpg")
    cls, valid, lon, lat = ref_grid(p, lon0)
    Z, _ = load_elev(0)
    z = sample_ours(Z, lon, lat)
    target = float((cls[valid] == SHALLOW).mean())
    lo, hi = 50.0, 6000.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        f = float((((z < 0) & (z > -mid))[valid]).mean())
        if f < target:
            lo = mid
        else:
            hi = mid
    cut = 0.5 * (lo + hi)
    return cut, target, float((((z < 0) & (z > -cut))[valid]).mean())


def audit_age(path, age, cut, lon0=0.0, want_dlon=True, want_disp=True):
    cls, valid, lon, lat = ref_grid(path, lon0)
    h, w = cls.shape
    Z, used = load_elev(age)
    if Z is None:
        return None
    inside = valid
    ref_land = (cls == LAND) | (cls == ICE)
    landfrac = sample_ours_ss(Z, lon, lat, inside, h, w, lon0)
    our_land = landfrac >= 0.5
    z = sample_ours(Z, lon, lat)
    our_shallow = (z < 0) & (z > -cut) & ~our_land
    ref_shallow = cls == SHALLOW

    V = float(valid.sum())
    r = {
        "age": age, "used": used, "file": os.path.basename(path),
        "valid_frac": V / float((cls >= 0).size),
        "ref_land": float(ref_land[valid].mean()),
        "our_land": float(our_land[valid].mean()),
        "ref_ice": float((cls == ICE)[valid].mean()),
        "ref_shallow": float(ref_shallow[valid].mean()),
        "our_shallow": float(our_shallow[valid].mean()),
        "agree": float((ref_land[valid] == our_land[valid]).mean()),
        "iou": float((ref_land & our_land & valid).sum() /
                     max(1, ((ref_land | our_land) & valid).sum())),
        "kappa": kappa(ref_land[valid], our_land[valid]),
    }
    # where the reference's shelf sea goes in ours
    m = ref_shallow & valid
    if m.sum():
        r["refshelf_is_our_land"] = float(our_land[m].mean())
        r["refshelf_is_our_shallow"] = float(our_shallow[m].mean())
        r["refshelf_is_our_deep"] = float(((~our_land) & (~our_shallow))[m].mean())
    # latitude structure: agreement here is a palaeomagnetic check and should
    # survive even when longitude does not
    pa, _ = lat_profile(ref_land, lat, valid)
    pb, _ = lat_profile(our_land, lat, valid)
    ok = ~(np.isnan(pa) | np.isnan(pb))
    r["lat_rms"] = float(np.sqrt(((pa[ok] - pb[ok]) ** 2).mean())) if ok.sum() > 3 else None
    r["lat_r"] = float(np.corrcoef(pa[ok], pb[ok])[0, 1]) if ok.sum() > 3 else None
    if want_dlon:
        d, sd, s0 = best_dlon(Z, ref_land, valid, lon, lat)
        r["dlon"], r["agree_dlon"], r["agree_0"] = d, sd, s0
        # IoU and kappa AFTER the rigid rotation: this is the part of the
        # disagreement that a frame difference cannot explain
        rot_land = sample_ours(Z, lon, lat, -d) >= 0.0
        r["iou_dlon"] = float((ref_land & rot_land & valid).sum() /
                              max(1, ((ref_land | rot_land) & valid).sum()))
        r["kappa_dlon"] = kappa(ref_land[valid], rot_land[valid])
        # the shelf question, asked only where BOTH models put continental
        # crust -- otherwise it answers a placement question instead
        rot_z = sample_ours(Z, lon, lat, -d)
        rot_shal = (rot_z < 0) & (rot_z > -cut) & ~rot_land
        both = valid & (ref_shallow | (cls == LAND)) & (rot_land | rot_shal)
        if both.sum() > 500:
            r["shared_cont"] = float(both[valid].mean())
            sh = both & ref_shallow
            r["shared_refshelf_our_land"] = float(rot_land[sh].mean()) if sh.sum() else None
            ld = both & (cls == LAND)
            r["shared_refland_our_shelf"] = float(rot_shal[ld].mean()) if ld.sum() else None
    if want_disp:
        a = valid & ref_land
        b = valid & our_land
        r["disp_ref_to_our"] = displacement_km(lon[a], lat[a], lon[b], lat[b])
        r["disp_our_to_ref"] = displacement_km(lon[b], lat[b], lon[a], lat[a])
    ice = our_ice(age)
    if ice is not None:
        H, W = ice.shape
        yi = np.clip(((90.0 - lat) / 180.0 * H).astype(np.int32), 0, H - 1)
        xi = (((lon + 180.0) / 360.0 * W).astype(np.int32)) % W
        oi = ice[yi, xi] >= 0.5
        r["our_ice"] = float(oi[valid].mean())
        ri = (cls == ICE)
        r["ice_iou"] = float((ri & oi & valid).sum() / max(1, ((ri | oi) & valid).sum()))
        for tag, sel in (("polar", np.abs(lat) >= 55), ("low", np.abs(lat) < 55)):
            r["ref_ice_" + tag] = float((ri & sel)[valid].mean())
            r["our_ice_" + tag] = float((oi & sel)[valid].mean())
    return r


def run_dtm(lon0=0.0):
    cut, rf, of = calibrate_shallow_cut(lon0)
    print("SHALLOW-WATER CALIBRATION (0 Ma, the one age both sides are the real Earth)")
    print(f"  reference shallow tint {rf*100:.2f}% of surface")
    print(f"  matched by our field at z > {-cut:.0f} m  -> {of*100:.2f}%")
    print("  the tint is a cartographic class, not a depth contour; this cut is")
    print("  frozen here and applied unchanged at every other age.\n")

    rows = []
    for age, path, is_lgm in dtm_files():
        r = audit_age(path, 0 if is_lgm else age, cut, lon0)
        if r is None:
            continue
        r["lgm"] = is_lgm
        rows.append(r)

    print("LAND AREA  (Mollweide pixels are equal-area, so % is area)")
    hdr = (f"{'age':>6} {'DTM land':>9} {'ours':>7} {'delta':>7} "
           f"{'lat r':>6} {'latRMS':>7}   how the land is spread in latitude")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r["lgm"]:
            continue
        print(f"{r['age']:6.0f} {r['ref_land']*100:8.1f}% {r['our_land']*100:6.1f}% "
              f"{(r['our_land']-r['ref_land'])*100:+6.1f}% "
              f"{r['lat_r']:6.2f} {r['lat_rms']*100:6.1f}%")
    lgm = [r for r in rows if r["lgm"]]
    if lgm:
        r = lgm[0]
        print(f"{'21 ka':>6} {r['ref_land']*100:8.1f}% {r['our_land']*100:6.1f}% "
              f"{(r['our_land']-r['ref_land'])*100:+6.1f}%   (LGM: our nearest "
              f"keyframe is 0 Ma, the modern world -- excluded from the summary)")

    print("\nPOSITION  (kappa, not agreement: at 450 Ma the reference is 85% ocean,")
    print("so 'ocean everywhere' would already score 85% agreement. kappa 0 = no skill.)")
    hdr = (f"{'age':>6} {'IoU':>6} {'kappa':>6} {'d.lon':>6} {'IoU@d':>6} {'kappa@d':>8} "
           f"{'gain':>6} {'DTM->ours km':>14} {'ours->DTM km':>14}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r["lgm"] or "dlon" not in r:
            continue
        d1, d2 = r["disp_ref_to_our"], r["disp_our_to_ref"]
        print(f"{r['age']:6.0f} {r['iou']:6.3f} {r['kappa']:6.3f} {r['dlon']:+6.0f} "
              f"{r['iou_dlon']:6.3f} {r['kappa_dlon']:8.3f} "
              f"{r['kappa_dlon']-r['kappa']:+6.3f} "
              f"{d1[0]:9.0f}/{d1[1]:4.0f} {d2[0]:9.0f}/{d2[1]:4.0f}")
    if lgm:
        r = lgm[0]
        print(f"{'21 ka':>6} {r['iou']:6.3f} {r['kappa']:6.3f}")

    print("\nSHELF SEA  (reference tint vs our z > %.0f m)" % -cut)
    print("The last two columns are asked only where BOTH models put continental")
    print("crust, AFTER the rigid longitude fit -- otherwise the answer is about")
    print("placement, not about flooding.")
    hdr2 = (f"{'age':>6} {'DTM shelf':>10} {'ours':>7} {'delta':>7} "
            f"{'shared crust':>13} {'their shelf=our land':>21} {'their land=our shelf':>21}")
    print(hdr2)
    print("-" * len(hdr2))
    for r in rows:
        if r["lgm"] or "refshelf_is_our_land" not in r:
            continue
        a = r.get("shared_refshelf_our_land")
        b = r.get("shared_refland_our_shelf")
        sc = r.get("shared_cont")
        print(f"{r['age']:6.0f} {r['ref_shallow']*100:9.1f}% {r['our_shallow']*100:6.1f}% "
              f"{(r['our_shallow']-r['ref_shallow'])*100:+6.1f}% "
              f"{(sc*100 if sc else float('nan')):12.1f}% "
              f"{(a*100 if a is not None else float('nan')):20.0f}% "
              f"{(b*100 if b is not None else float('nan')):20.0f}%")

    print("\nICE  (% of the whole surface; 'polar' is |lat| >= 55)")
    hdr3 = (f"{'age':>6} {'DTM ice':>8} {'ours':>7} {'IoU':>6} "
            f"{'DTM polar':>10} {'our polar':>10} {'DTM low':>8} {'our low':>8}")
    print(hdr3)
    print("-" * len(hdr3))
    for r in rows:
        if "our_ice" not in r:
            continue
        tag = "21 ka" if r["lgm"] else f"{r['age']:.0f}"
        print(f"{tag:>6} {r['ref_ice']*100:7.2f}% {r['our_ice']*100:6.2f}% {r['ice_iou']:6.3f} "
              f"{r['ref_ice_polar']*100:9.2f}% {r['our_ice_polar']*100:9.2f}% "
              f"{r['ref_ice_low']*100:7.2f}% {r['our_ice_low']*100:7.2f}%")

    body = [r for r in rows if not r["lgm"]]
    print(f"\n{len(body)} matched ages. Means: IoU "
          f"{np.mean([r['iou'] for r in body]):.3f} -> {np.mean([r['iou_dlon'] for r in body]):.3f} "
          f"after the longitude fit, kappa "
          f"{np.mean([r['kappa'] for r in body]):.3f} -> "
          f"{np.mean([r['kappa_dlon'] for r in body]):.3f}, |d.lon| "
          f"{np.mean([abs(r['dlon']) for r in body]):.0f} deg, land bias "
          f"{np.mean([r['our_land']-r['ref_land'] for r in body])*100:+.1f}%")
    for lo, hi, tag in ((0, 100, "0-100 Ma  "), (100, 260, "100-260 Ma"),
                        (260, 600, "260-525 Ma")):
        g = [r for r in body if lo <= r["age"] < hi]
        if not g:
            continue
        print(f"  {tag}  n={len(g):2d}  IoU {np.mean([r['iou'] for r in g]):.3f} -> "
              f"{np.mean([r['iou_dlon'] for r in g]):.3f}   kappa "
              f"{np.mean([r['kappa'] for r in g]):.3f} -> "
              f"{np.mean([r['kappa_dlon'] for r in g]):.3f}   |d.lon| "
              f"{np.mean([abs(r['dlon']) for r in g]):3.0f} deg   land bias "
              f"{np.mean([r['our_land']-r['ref_land'] for r in g])*100:+.1f}%")
    return rows


# ---------------------------------------------- the Scotese numbered series --
# These are annotated plates: continent and ocean names, subduction ticks, white
# modern-coastline overlays, a legend box and an equator line all sit on top of
# the map. Land/ocean survives that; ice and shelf do not, so only land is
# scored and the numbers carry more noise than the DTM ones. Recorded rather
# than dropped, because it is the second witness and it is Scotese's own frame.
SCOTESE = {"000.jpg": 0, "014.jpg": 14, "050.jpg": 50, "066.jpg": 66, "094.jpg": 94,
           "152.jpg": 152, "195.jpg": 195, "237.jpg": 237, "255.jpg": 255,
           "306.jpg": 306, "342.jpg": 342, "390.jpg": 390, "425.jpg": 425,
           "458.jpg": 458, "514.jpg": 514}


def scotese_ellipse(im):
    """Locate the inset map ellipse. These plates have margins, a title and a
    legend, so the ellipse is not inscribed in the image the way the DTM ones are.

    Taken from the largest connected component of strongly-coloured pixels --
    the map body. Titles and legend text are white on black and fail the colour
    test; where a label does touch the body, using the component's bounding box
    for the minor axis stretches it (measured: a/b came out 1.89-2.01 across the
    series). A Mollweide is exactly 2:1, so the minor axis is taken as a/2 and
    only the widest row -- the equator -- is trusted.
    """
    from scipy import ndimage
    G = im[..., 1].astype(np.int16)
    B = im[..., 2].astype(np.int16)
    body = ndimage.binary_closing((B > 55) | (G > 55), np.ones((5, 5)))
    lab, n = ndimage.label(body)
    if n == 0:
        return None
    sizes = ndimage.sum(body, lab, range(1, n + 1))
    comp = lab == int(np.argmax(sizes)) + 1
    rows = comp.sum(axis=1)
    y_eq = int(np.argmax(rows))
    r = np.nonzero(comp[y_eq])[0]
    if len(r) < 50:
        return None
    a = 0.5 * (r.max() - r.min())
    return 0.5 * (r.min() + r.max()), float(y_eq), a, a / 2.0


def run_scotese():
    print("SCOTESE PALEOMAP numbered series -- land only.")
    print("These plates carry names, arrows, white modern-coastline overlays and a")
    print("legend on top of the map. Land/ocean survives that; ice and shelf do not.")
    print("Our terrain IS the Scotese & Wright PaleoDEMs, so this is a")
    print("SELF-CONSISTENCY check, not an independent one.\n")
    hdr = (f"{'age':>6} {'S land':>7} {'ours':>7} {'delta':>7} {'agree':>7} {'IoU':>6} "
           f"{'d.lon':>6} {'agree@d':>8}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for fn, age in sorted(SCOTESE.items(), key=lambda kv: kv[1]):
        p = os.path.join(REFDIR, fn)
        if not os.path.exists(p):
            continue
        im = np.asarray(Image.open(p).convert("RGB"))
        e = scotese_ellipse(im)
        if e is None:
            continue
        cx, cy, a, b = e
        h, w, _ = im.shape
        yy, xx = np.mgrid[0:h, 0:w]
        X = (xx + 0.5 - cx) / a
        Y = -(yy + 0.5 - cy) / b
        inside = X * X + Y * Y <= 0.985
        th = np.arcsin(np.clip(Y, -1, 1))
        lat = np.degrees(np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1)))
        with np.errstate(divide="ignore", invalid="ignore"):
            lon = 180.0 * X / np.cos(th)
        inside &= np.abs(lon) <= 180.0
        lon = ((lon + 180.0) % 360.0) - 180.0
        R = im[..., 0].astype(np.int16)
        G = im[..., 1].astype(np.int16)
        B = im[..., 2].astype(np.int16)
        mx = im.max(axis=2).astype(np.int16)
        mn = im.min(axis=2).astype(np.int16)
        ocean = (B > R + 25) & (B >= G - 10)
        # annotation: near-white glyphs and outlines, and the orange subduction ticks
        anno = ((mn >= 145) & ((mx - mn) <= 40)) | ((R > 150) & (G > 60) & (G < 175) & (B < 90))
        valid = inside & ~anno & (mx >= 30)
        ref_land = (~ocean) & valid
        Z, _ = load_elev(age)
        if Z is None:
            continue
        our_land = sample_ours(Z, lon, lat) >= 0.0
        d, sd, s0 = best_dlon(Z, ref_land, valid, lon, lat)
        row = {"age": age, "ref_land": float(ref_land[valid].mean()),
               "our_land": float(our_land[valid].mean()),
               "agree": float(s0), "dlon": d, "agree_dlon": float(sd),
               "iou": float((ref_land & our_land & valid).sum() /
                            max(1, ((ref_land | our_land) & valid).sum()))}
        rows.append(row)
        print(f"{age:6d} {row['ref_land']*100:6.1f}% {row['our_land']*100:6.1f}% "
              f"{(row['our_land']-row['ref_land'])*100:+6.1f}% {row['agree']*100:6.1f}% "
              f"{row['iou']:6.3f} {row['dlon']:+6.0f} {row['agree_dlon']*100:7.1f}%")
    if rows:
        print(f"\n{len(rows)} ages. Mean agreement {np.mean([r['agree'] for r in rows])*100:.1f}%, "
              f"mean IoU {np.mean([r['iou'] for r in rows]):.3f}, mean |d.lon| "
              f"{np.mean([abs(r['dlon']) for r in rows]):.0f} deg")
    return rows


# --------------------------------------------------------------- F1: future --
# The six claims the handoff reads off 20F250v4.jpg (c) 2000 C R Scotese.
FUTURE_CLAIMS = [
    "Africa at the centre of the assembled mass",
    "North America to its west-northwest, South America SSW, Eurasia east",
    "a Mediterranean Mts collisional belt running NE from Africa into Eurasia",
    "Antarctica + Australia a SEPARATE southern mass on a narrow neck",
    "an interior sea surviving between North America and Africa/Eurasia",
    "the Pacific occupying essentially the whole opposite hemisphere",
]

# One anchor per continent, on stable interior crust, present-day coordinates.
ANCHORS = {
    "N America":  (-100.0, 40.0, "NORTH_AMERICA"),
    "S America":  (-55.0, -12.0, "SOUTH_AMERICA"),
    "Africa":     (20.0, 5.0, "AFRICA"),
    "NW Africa":  (0.0, 22.0, "AFRICA"),
    "S Africa":   (25.0, -26.0, "AFRICA"),
    "Europe":     (20.0, 52.0, "EURASIA"),
    "Siberia":    (100.0, 62.0, "EURASIA"),
    "China":      (110.0, 34.0, "EURASIA"),
    "India":      (78.0, 22.0, "INDIA"),
    "Arabia":     (45.0, 24.0, "ARABIA"),
    "Australia":  (133.0, -25.0, "AUSTRALIA"),
    "Antarctica": (0.0, -84.0, "ANTARCTICA"),
    "E Antarct.": (90.0, -75.0, "ANTARCTICA"),
    "Somalia":    (45.0, 3.0, "SOMALIA"),
}


def _rodrigues(axis, deg):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * (K @ K)


def _unit(lon, lat):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def _rot_from_to(s, t):
    v = np.cross(s, t)
    n = np.linalg.norm(v)
    if n < 1e-12:
        return np.eye(3)
    return _rodrigues(v / n, math.degrees(math.atan2(n, float(np.dot(s, t)))))


def our_future_rotations():
    """Reproduce build/build_fields.py's per-group rotation at +250 Myr exactly.

    Not re-derived from the table -- imported, so that a change to GROUP_TARGET
    or PLATE_GROUP shows up here instead of leaving this audit describing a
    version of the future the app no longer builds. build/ modules use relative
    paths and load data at import time, so this has to run from build/.
    """
    if BUILD not in sys.path:
        sys.path.insert(0, BUILD)
    cwd = os.getcwd()
    try:
        os.chdir(BUILD)
        import build_fields as BF
        gid = BF.rasterise_groups()
        # THE PACKED TARGETS, not the authored ones. future_grid relaxes
        # GROUP_TARGET so the groups stop interpenetrating (they were deleting
        # 35% of Earth's land), and reading the raw table here would have left
        # this audit describing a future the app no longer builds -- which is the
        # exact failure the docstring above says it exists to avoid. Same lesson
        # as regression_gate.py: an audit that reconstructs the pipeline instead
        # of calling it silently stops tracking it.
        idx = BF.index_dems()
        Zsrc = BF.resample_dem(BF.read_dem(idx[min(idx, key=lambda k: abs(k))]),
                               900, 1800)
        targets = BF._packed_targets(gid, Zsrc)
    finally:
        os.chdir(cwd)
    gh, gw = gid.shape
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    out = {}
    for i, g in enumerate(BF.GROUPS):
        m = gid == i
        if not m.any():
            continue
        v = _unit(GLON[m], GLAT[m]).mean(axis=1)
        v /= np.linalg.norm(v)
        tl, tb, spin = targets[g]
        t = _unit(tl, tb)
        out[g] = (_rodrigues(t, spin) @ _rot_from_to(v, t), v)
    return out


def paleomap_future(points, age=-250.0):
    """PALEOMAP position of present-day points at `age` (negative = future)."""
    import pygplates
    rot = pygplates.RotationModel(PALEOMAP_ROT)
    polys = pygplates.FeatureCollection(PALEOMAP_POLY)
    part = pygplates.PlatePartitioner(polys, rot, reconstruction_time=0)
    out = {}
    for name, (lon, lat) in points.items():
        pt = pygplates.PointOnSphere(float(lat), float(lon))
        found = part.partition_point(pt)
        if found is None:
            out[name] = (None, None, None)
            continue
        pid = found.get_feature().get_reconstruction_plate_id()
        try:
            p = rot.get_rotation(float(age), pid) * pt
        except Exception:                                    # noqa: BLE001
            out[name] = (None, None, pid)
            continue
        la, lo = p.to_lat_lon()
        out[name] = (lo, la, pid)
    return out


def gc_km(lon1, lat1, lon2, lat2):
    p, q = _unit(lon1, lat1), _unit(lon2, lat2)
    return float(np.arccos(np.clip(np.dot(p, q), -1, 1)) * R_EARTH_KM)


def run_future():
    print("F1 -- the future series, against PALEOMAP's own future rotations")
    print("PALEOMAP_PlateModel.rot carries rotations to -250 Ma. That makes the")
    print("comparison quantitative instead of a look at a JPEG.\n")

    rots = our_future_rotations()
    pts = {k: (v[0], v[1]) for k, v in ANCHORS.items()}
    pm = paleomap_future(pts, -250.0)

    hdr = (f"{'anchor':>11} {'present':>16} {'ours +250':>16} {'PALEOMAP +250':>16} "
           f"{'sep km':>7} {'d.lat':>6} {'d.lon':>6}")
    print(hdr)
    print("-" * len(hdr))
    seps, rel = [], {}
    for name, (lon, lat, grp) in ANCHORS.items():
        R = rots.get(grp)
        if R is None:
            continue
        v = R[0] @ _unit(lon, lat)
        olat = math.degrees(math.asin(max(-1, min(1, v[2]))))
        olon = math.degrees(math.atan2(v[1], v[0]))
        plon, plat, _pid = pm[name]
        if plon is None:
            print(f"{name:>11} ({lon:7.1f},{lat:6.1f}) ({olon:7.1f},{olat:6.1f}) "
                  f"{'no plate':>16}")
            continue
        d = gc_km(olon, olat, plon, plat)
        dlon = ((olon - plon + 180) % 360) - 180
        seps.append(d)
        rel[name] = ((olon, olat), (plon, plat))
        print(f"{name:>11} ({lon:7.1f},{lat:6.1f}) ({olon:7.1f},{olat:6.1f}) "
              f"({plon:7.1f},{plat:6.1f}) {d:7.0f} {olat-plat:+6.1f} {dlon:+6.1f}")
    if seps:
        print(f"\nmean separation {np.mean(seps):.0f} km, median {np.median(seps):.0f} km, "
              f"max {np.max(seps):.0f} km")
        print("Absolute separation is NOT the test. Both models are free in absolute")
        print("longitude, and ours additionally chooses its own orientation. What has")
        print("to agree is the RELATIVE arrangement -- who is next to whom, and on")
        print("which side.\n")

    # relative arrangement, in each model's own frame, measured from Africa
    print("RELATIVE ARRANGEMENT  (bearing and distance FROM Africa, each model in")
    print("its own frame -- this is the part that carries meaning)")
    hdr2 = f"{'anchor':>11} {'ours: km / bearing':>22} {'PALEOMAP: km / bearing':>24} {'d.km':>7} {'d.brg':>7}"
    print(hdr2)
    print("-" * len(hdr2))
    if "Africa" in rel:
        (oal, oab), (pal, pab) = rel["Africa"]
        for name in ANCHORS:
            if name not in rel or name == "Africa":
                continue
            (ol, ob), (pl, pb) = rel[name]
            dk_o, br_o = _range_bearing(oal, oab, ol, ob)
            dk_p, br_p = _range_bearing(pal, pab, pl, pb)
            db = ((br_o - br_p + 180) % 360) - 180
            print(f"{name:>11} {dk_o:12.0f} km {br_o:7.0f} {dk_p:14.0f} km {br_p:7.0f} "
                  f"{dk_o-dk_p:+7.0f} {db:+7.0f}")
    print()
    return rel


def _range_bearing(lon1, lat1, lon2, lat2):
    p1, l1 = math.radians(lat1), math.radians(lon1)
    p2, l2 = math.radians(lat2), math.radians(lon2)
    dl = l2 - l1
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    brg = (math.degrees(math.atan2(y, x)) + 360) % 360
    d = math.acos(max(-1, min(1, math.sin(p1) * math.sin(p2) +
                              math.cos(p1) * math.cos(p2) * math.cos(dl)))) * R_EARTH_KM
    return d, brg


def _spread(mask, cw, V):
    """(land fraction, r50, r90, emptiest hemisphere) for a land mask.

    r50/r90 are the angular radii holding 50% and 90% of the land about its own
    centroid -- how tightly assembled the world is, independent of where it sits.
    """
    a = float((cw * mask).sum() / cw.sum())
    if not mask.any():
        return a, float("nan"), float("nan"), 0.0
    v = (V[mask] * cw[mask][:, None]).sum(axis=0)
    v /= np.linalg.norm(v)
    d = np.degrees(np.arccos(np.clip(V[mask] @ v, -1, 1)))
    wt = cw[mask]
    o = np.argsort(d)
    c = np.cumsum(wt[o]) / wt.sum()
    r50 = float(d[o][np.searchsorted(c, 0.5)])
    r90 = float(d[o][np.searchsorted(c, 0.9)])
    best = 1.0
    for pl in np.arange(-85, 86, 5.0):
        for po in np.arange(-180, 180, 5.0):
            hemi = (V @ _unit(po, pl)) > 0
            best = min(best, float((cw * (mask & hemi)).sum() /
                                   max(1e-9, (cw * hemi).sum())))
    return a, r50, r90, best


def future_series(h=360, w=720):
    """The future series against PALEOMAP, age by age.

    The single most diagnostic number is land AREA. Continental crust is
    conserved over 250 Myr -- a rigid rotation cannot create or destroy it -- so
    any trend here is an artefact of how the reconstruction is built, in either
    model, and it is measurable without settling any question of where the
    continents should go.
    """
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon, lat)
    cw = np.cos(np.radians(LAT))
    V = unit_vectors(LON, LAT)
    print("THE SERIES, ours against PALEOMAP's own rotations")
    print("r50/r90 = angular radius holding 50%/90% of the land about its centroid:")
    print("how tightly the world is assembled. 'empty hemi' = least land any")
    print("hemisphere holds, which is the Pacific-hemisphere claim as a number.")
    hdr = (f"{'+Myr':>6} | {'ours land':>10} {'Mkm2':>7} {'r50':>5} {'r90':>5} "
           f"{'empty':>6} | {'PM land':>8} {'Mkm2':>7} {'r50':>5} {'r90':>5} {'empty':>6}")
    print(hdr)
    print("-" * len(hdr))
    for age in (0, -25, -50, -75, -100, -150, -200, -250):
        Z, _ = load_elev(age)
        if Z is None:
            continue
        H, W = Z.shape
        z = Z[np.clip(((90 - LAT) / 180 * H).astype(int), 0, H - 1),
              (((LON + 180) / 360 * W).astype(int)) % W]
        oa, o50, o90, oe = _spread(z >= 0, cw, V)
        pm = paleomap_land(age, h, w)
        if pm is not None:
            pa, p50, p90, pe = _spread(pm, cw, V)
            print(f"{-age:6d} | {oa*100:9.1f}% {oa*EARTH_KM2/1e6:7.1f} {o50:5.1f} "
                  f"{o90:5.1f} {oe*100:5.1f}% | {pa*100:7.1f}% {pa*EARTH_KM2/1e6:7.1f} "
                  f"{p50:5.1f} {p90:5.1f} {pe*100:5.1f}%")
        else:
            print(f"{-age:6d} | {oa*100:9.1f}% {oa*EARTH_KM2/1e6:7.1f} {o50:5.1f} "
                  f"{o90:5.1f} {oe*100:5.1f}% |")
    print("\nPALEOMAP's mask is present-day land advected rigidly, rasterised and")
    print("closed, so it carries about +2 points of its own bias (31.1% at age 0")
    print("against Earth's 29.2%). It is flat in age, which is the point.")

    # relief: a collision belt would show up as new high ground
    print()
    hdr = f"{'+Myr':>6} {'land >1 km':>11} {'land >2 km':>11} {'mean land z':>12}"
    print(hdr)
    print("-" * len(hdr))
    for age in (0, -50, -100, -150, -200, -250):
        Z, _ = load_elev(age)
        if Z is None:
            continue
        H, W = Z.shape
        la = np.repeat((90 - (np.arange(H) + 0.5) / H * 180)[:, None], W, 1)
        c = np.cos(np.radians(la))
        t = c.sum()
        land = Z >= 0
        print(f"{-age:6d} {float((c*(Z>1000)).sum()/t)*EARTH_KM2/1e6:8.1f} Mkm2 "
              f"{float((c*(Z>2000)).sum()/t)*EARTH_KM2/1e6:8.1f} Mkm2 "
              f"{float((Z[land]*c[land]).sum()/(c*land).sum()):9.0f} m")


def future_group_map(h=360, w=720):
    """Which plate group each patch of land belongs to in our +250 Myr frame.

    Needed because the six claims are about WHO is next to whom, and the shipped
    field is just elevation -- it does not say which blob is North America.
    Present-day land is split by PLATE_GROUP, each group carried forward by the
    same rotation build_fields.future_grid uses, and scattered onto the output.
    """
    from scipy import ndimage
    if BUILD not in sys.path:
        sys.path.insert(0, BUILD)
    cwd = os.getcwd()
    try:
        os.chdir(BUILD)
        import build_fields as BF
        gid = BF.rasterise_groups()
        groups = list(BF.GROUPS)
    finally:
        os.chdir(cwd)
    rots = our_future_rotations()
    Z0, _ = load_elev(0)
    gh, gw = gid.shape
    src = 0.5
    lats = np.arange(90 - src / 2, -90, -src)
    lons = np.arange(-180 + src / 2, 180, src)
    LON, LAT = np.meshgrid(lons, lats)
    H0, W0 = Z0.shape
    land = Z0[np.clip(((90 - LAT) / 180 * H0).astype(int), 0, H0 - 1),
              (((LON + 180) / 360 * W0).astype(int)) % W0] >= 0
    g = gid[np.clip(((90 - LAT) / 180 * gh).astype(int), 0, gh - 1),
            (((LON + 180) / 360 * gw).astype(int)) % gw]
    out = np.full((h, w), -1, np.int16)
    for i, name in enumerate(groups):
        R = rots.get(name)
        if R is None:
            continue
        m = land & (g == i)
        if not m.any():
            continue
        V = (R[0] @ unit_vectors(LON[m], LAT[m]).T).T
        la = np.degrees(np.arcsin(np.clip(V[:, 2], -1, 1)))
        lo = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
        ry = np.clip(((90 - la) / 180 * h).astype(int), 0, h - 1)
        rx = (((lo + 180) / 360 * w).astype(int)) % w
        blob = np.zeros((h, w), bool)
        blob[ry, rx] = True
        blob = ndimage.binary_closing(blob, np.ones((3, 3)))
        out[blob & (out < 0)] = i
    return out, groups


def future_claims(h=360, w=720):
    """The six claims from 20F250v4.jpg, each answered from our own field."""
    from scipy import ndimage
    Z, _ = load_elev(-250)
    if Z is None:
        return
    gmap, groups = future_group_map(h, w)
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon, lat)
    H, W = Z.shape
    z = Z[np.clip(((90 - LAT) / 180 * H).astype(int), 0, H - 1),
          (((LON + 180) / 360 * W).astype(int)) % W]
    land = z >= 0
    cw = np.cos(np.radians(LAT))

    def cen(m):
        if not m.any():
            return None
        v = (unit_vectors(LON[m], LAT[m]) * cw[m][:, None]).sum(axis=0)
        v /= np.linalg.norm(v)
        return (math.degrees(math.atan2(v[1], v[0])),
                math.degrees(math.asin(max(-1, min(1, v[2])))))

    all_c = cen(land)
    print("\nTHE SIX CLAIMS, from our own +250 Myr field")
    print(f"  centroid of all land ({all_c[0]:.0f},{all_c[1]:.0f})")
    print(f"  {'group':>14} {'centroid':>16} {'km from land centroid':>22} "
          f"{'bearing from AFRICA':>20}")
    afr = cen(land & (gmap == groups.index("AFRICA")))
    for i, name in enumerate(groups):
        c = cen(land & (gmap == i))
        if c is None:
            continue
        d0 = gc_km(c[0], c[1], all_c[0], all_c[1])
        dk, br = _range_bearing(afr[0], afr[1], c[0], c[1])
        print(f"  {name:>14} ({c[0]:7.1f},{c[1]:6.1f}) {d0:16.0f} km "
              f"{('-' if name == 'AFRICA' else f'{br:.0f} deg, {dk:.0f} km'):>20}")

    lab, n = ndimage.label(land, np.ones((3, 3)))
    sizes = np.array(ndimage.sum(land * cw, lab, range(1, n + 1)))
    order = np.argsort(sizes)[::-1]
    tot = float((cw * land).sum())
    print(f"\n  connected landmasses larger than 1% of the land:")
    for k in order[:6]:
        if sizes[k] < 0.01 * tot:
            break
        m = lab == k + 1
        mem = [groups[i] for i in np.unique(gmap[m]) if i >= 0 and
               (cw * (m & (gmap == i))).sum() > 0.02 * sizes[k]]
        print(f"    {sizes[k]/tot*100:5.1f}% of land   {', '.join(mem)}")

    big = lab == order[0] + 1
    filled = ndimage.binary_fill_holes(big)
    hole = filled & ~big
    hl, hn = ndimage.label(hole)
    if hn:
        hs = np.array(ndimage.sum(hole * cw, hl, range(1, hn + 1)))
        k = int(np.argmax(hs)) + 1
        sea = hl == k
        rim = ndimage.binary_dilation(sea, np.ones((5, 5))) & big
        mem = [(groups[i], float((cw * (rim & (gmap == i))).sum() /
                                 max(1e-9, (cw * rim).sum())))
               for i in np.unique(gmap[rim]) if i >= 0]
        mem.sort(key=lambda t: -t[1])
        print(f"\n  largest enclosed sea {hs.max()/tot*100:.1f}% of land area "
              f"({hs.max()/cw.sum()*EARTH_KM2/1e6:.1f} Mkm2); its shore is")
        for name, f in mem[:5]:
            print(f"    {f*100:4.0f}%  {name}")


def future_geometry(age=-250, h=360, w=720):
    """What our own +250 Myr field actually contains -- the six claims, measured."""
    Z, used = load_elev(age)
    if Z is None:
        print("no future field for age %s" % age)
        return None
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    LON, LAT = np.meshgrid(lon, lat)
    H, W = Z.shape
    yi = np.clip(((90.0 - LAT) / 180.0 * H).astype(int), 0, H - 1)
    xi = (((LON + 180.0) / 360.0 * W).astype(int)) % W
    z = Z[yi, xi]
    cw = np.cos(np.radians(LAT))
    land = z >= 0
    tot = cw.sum()
    print(f"OUR {-age:+d} Myr FIELD, measured")
    print(f"  land                    {100*(land*cw).sum()/tot:.1f}% of surface")
    print(f"  shelf sea (0 to -500 m) {100*(((z<0)&(z>-500))*cw).sum()/tot:.1f}%")

    # The emptiest hemisphere: rotate a pole over the sphere and find the
    # hemisphere holding the least land. Scotese's Pangaea Ultima puts the
    # Pacific over essentially a whole hemisphere, so this number is the claim.
    V = unit_vectors(LON, LAT)
    best = None
    for plat in np.arange(-85, 86, 5.0):
        for plon in np.arange(-180, 180, 5.0):
            c = _unit(plon, plat)
            hemi = (V @ c) > 0
            f = float((land & hemi)[hemi].astype(float).mean()) if hemi.any() else 1.0
            f = float((cw * (land & hemi)).sum() / max(1e-9, (cw * hemi).sum()))
            if best is None or f < best[0]:
                best = (f, plon, plat)
    f, plon, plat = best
    c = _unit(plon, plat)
    anti = (V @ c) <= 0
    fa = float((cw * (land & anti)).sum() / (cw * anti).sum())
    print(f"  emptiest hemisphere     {f*100:.1f}% land, centred ({plon:.0f},{plat:.0f})")
    print(f"  its antipode            {fa*100:.1f}% land")

    # Is the assembled mass solid, or is there an interior sea? Take the largest
    # connected landmass, fill its holes, and ask how much of the filled area is
    # water. A solid disc scores ~0.
    from scipy import ndimage
    lab, n = ndimage.label(land, np.ones((3, 3)))
    if n:
        sizes = ndimage.sum(land, lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        big = lab == k
        filled = ndimage.binary_fill_holes(big)
        hole = filled & ~big
        print(f"  largest landmass        {100*(cw*big).sum()/tot:.1f}% of surface, "
              f"{100*(cw*big).sum()/max(1e-9,(cw*land).sum()):.0f}% of all land")
        print(f"  enclosed sea inside it  {100*(cw*hole).sum()/max(1e-9,(cw*filled).sum()):.1f}% "
              f"of its outline ({(cw*hole).sum()/tot*EARTH_KM2/1e6:.1f} Mkm2)")
        print(f"  separate landmasses     {n} in total, "
              f"{int((sizes > sizes.max()*0.02).sum())} larger than 2% of the biggest")
    return best


# ------------------------------------------------------------------ selftest --
def _selftest():
    ok = True

    # 1. Mollweide round-trip
    for lon, lat in [(0, 0), (120, 45), (-170, -80), (37, 71), (-95, -12)]:
        px, py = moll_forward(lon, lat, 600, 1200)
        L, A, ins = moll_inverse(600, 1200)
        i, j = int(round(py)), int(round(px))
        if not ins[i, j] or abs(A[i, j] - lat) > 0.5 or \
           abs(((L[i, j] - lon + 180) % 360) - 180) > 1.0:
            print(f"FAIL round-trip ({lon},{lat}) -> ({L[i,j]:.2f},{A[i,j]:.2f})")
            ok = False

    # 2. Mollweide is equal-area: the ellipse must cover the whole sphere, and
    #    a latitude band must hold its true share of pixels
    L, A, ins = moll_inverse(600, 1200)
    n = ins.sum()
    if abs(n / (math.pi * 300 * 600) - 1.0) > 0.01:
        print(f"FAIL ellipse area {n} vs {math.pi*300*600:.0f}")
        ok = False
    band = ins & (np.abs(A) <= 30.0)
    if abs(band.sum() / n - 0.5) > 0.01:            # sin(30) = 0.5 of the sphere
        print(f"FAIL equal-area: |lat|<=30 holds {band.sum()/n:.3f}, want 0.500")
        ok = False

    # 3. the class rule on the learned palette
    cases = [((231, 200, 135), LAND), ((41, 67, 29), LAND), ((203, 173, 122), LAND),
             ((255, 255, 255), ICE), ((231, 230, 236), ICE),
             ((23, 167, 206), SHALLOW), ((6, 154, 198), SHALLOW),
             ((2, 71, 112), DEEP), ((1, 52, 87), DEEP), ((0, 91, 125), DEEP)]
    for rgb, want in cases:
        got = int(classify_ref(np.array([[rgb]], np.uint8))[0, 0])
        if got != want:
            print(f"FAIL classify {rgb} -> {CLASS_NAMES[got]}, want {CLASS_NAMES[want]}")
            ok = False

    # 4. the decode matches build/fieldpack.py rather than frame_experiment.py
    if BUILD not in sys.path:
        sys.path.insert(0, BUILD)
    try:
        import fieldpack
        if abs(fieldpack.Z_RANGE - Z_RANGE) > 1e-9:
            print(f"FAIL Z_RANGE {Z_RANGE} vs build/fieldpack {fieldpack.Z_RANGE}")
            ok = False
        for z in (-6000.0, -500.0, 0.0, 3000.0):
            enc = np.clip(np.round(fieldpack.enc_elev(np.array([z])) * 255), 0, 255)
            back = decode_elev(enc)[0]
            if abs(back - z) > max(60.0, abs(z) * 0.02):
                print(f"FAIL decode {z} -> {back:.0f}")
                ok = False
    except ImportError:
        print("note: build/fieldpack.py not importable, decode check skipped")

    # 5. the reprojection, on the one age where both sides are the real Earth
    p = os.path.join(REFDIR, "00-Ma-PresentMOLL-tn.jpg")
    if os.path.exists(p) and os.path.exists(os.path.join(FIELDS, "phan_0000_e.webp")):
        cls, valid, lon, lat = ref_grid(p)
        Z, _ = load_elev(0)
        h, w = cls.shape
        lf = sample_ours_ss(Z, lon, lat, valid, h, w)
        ours = lf >= 0.5
        ref = (cls == LAND) | (cls == ICE)
        agree = float((ours[valid] == ref[valid]).mean())
        refl = float(ref[valid].mean())
        ice = float((cls == ICE)[valid].mean())
        if agree < 0.95:
            print(f"FAIL present-day land/sea agreement {agree:.3f} -- the "
                  f"reprojection is wrong, not the model")
            ok = False
        if abs(refl - 0.292) > 0.02:
            print(f"FAIL reference land+ice at 0 Ma {refl:.3f}, Earth is 0.292")
            ok = False
        if not 11.0 <= ice * EARTH_KM2 / 1e6 <= 17.0:
            print(f"FAIL reference ice at 0 Ma {ice*EARTH_KM2/1e6:.1f} Mkm2, "
                  f"Antarctica+Greenland is 15.7 and the rule runs ~17% low")
            ok = False
        # and an ice-free world must read ice-free: the ice rule's failure mode
        # is pale LAND, and it shows up in hothouses, not in glacials
        for fn, cap in (("90-Ma-U-CretaceousMOLL-tn.jpg", 0.5),
                        ("50-MaPaleogene-Eocene-MOLL-tn.jpg", 0.5),
                        ("420-Ma-U-Silurian-MOLL-tn.jpg", 1.5)):
            q = os.path.join(REFDIR, fn)
            if not os.path.exists(q):
                continue
            c2, v2, _lo, la2 = ref_grid(q)
            pol = float(((c2 == ICE) & v2 & (np.abs(la2) >= 55)).mean()) * EARTH_KM2 / 1e6
            tot = float(((c2 == ICE) & v2).mean()) * EARTH_KM2 / 1e6
            if pol > 0.5 or tot > cap:
                print(f"FAIL {fn}: ice {tot:.1f} Mkm2 ({pol:.1f} polar) in a "
                      f"world with no ice sheets -- the class is catching pale land")
                ok = False
        print(f"present-day check: land/sea agreement {agree*100:.1f}%, "
              f"reference land+ice {refl*100:.1f}% (Earth 29.2%), reference ice "
              f"{ice*EARTH_KM2/1e6:.1f} Mkm2 (Antarctica+Greenland 15.7)")
    else:
        print("note: reference or field missing, present-day check skipped")

    print("selftest OK" if ok else "SELFTEST FAILED")
    return ok


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        _selftest()
        return
    if "--validate" in a:
        _selftest()
        return
    did = False
    if "--dtm" in a or not a:
        print("=" * 100)
        print("A5 -- DEEP TIME MAPS (c) CPGS, an INDEPENDENT reconstruction")
        print("=" * 100)
        run_dtm()
        did = True
    if "--frames" in a or not a:
        print("\n" + "=" * 100)
        print("A5 -- WHICH RECONSTRUCTION IS OUT OF STEP")
        print("=" * 100)
        run_frames()
        did = True
    if "--scotese" in a or not a:
        print("\n" + "=" * 100)
        print("A5 -- SCOTESE PALEOMAP (c) C R Scotese, our terrain's OWN source")
        print("=" * 100)
        run_scotese()
        did = True
    if "--future" in a or not a:
        print("\n" + "=" * 100)
        print("F1 -- THE FUTURE SERIES")
        print("=" * 100)
        run_future()
        future_series()
        future_geometry()
        future_claims()
        did = True
    if not did:
        print(__doc__)


if __name__ == "__main__":
    main()
