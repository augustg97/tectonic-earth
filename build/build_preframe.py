"""The Precambrian crust's own motion: `pre_*_v.webp`, `pre_*_p.webp` and the
Precambrian rows of `platerot.json`, from the SAME craton poses that draw the
terrain (3.17).

THE DEFECT. From 545 to 1000 Ma the terrain is generated (precambrian.py): each
craton is a fractal block placed by the authored poses in
build_synthetic.PRE_KEYS. But the warp that carries a keyframe toward its
neighbour (`_v`, build_displacement) and the frame crust-bound textures ride
(`_p` + platerot, build_platefield) were baked from PALEOMAP's rotations of
present-day plate polygons -- a different description of the same world.
Measured at 900 Ma: the warp moved crust 0.5-1.0 degrees a keyframe while the
blocks the terrain draws moved 0.07-0.14, and at 600 Ma it said 1.6 where the
blocks moved 5.4. So in every interval the continents slid the warp's way and
snapped back at the next keyframe, and the texture coordinate jumped at every
crossing -- 18x the change just before it at 900 Ma, 9x at 750, against 1.3x
at 405 Ma where warp and terrain are one model. In a time lapse through the
Tonian that is a flutter every 5 Myr.

THE FIX. For each keyframe a and craton k with pose P_k(a) (world <- local):
    warp      x -> P_k(a+5) P_k(a)^T x        where the crust sits at the next
                                               older keyframe (the app's B)
    frame     M_k(a) = Q_k P_k(540) P_k(a)^T  this crust's position today
Q_k is PALEOMAP's own 540 -> 0 Ma rotation for the plate under the craton's
540 Ma footprint, so the Precambrian frame hands off to the Phanerozoic one
without a jump; before 540 the texture rides the block the terrain draws. Cells
no craton owns (ocean) take the Laplace fill of the warp and the nearest
craton's slot, as build_displacement and build_platefield do for crust PALEOMAP
does not cover. The terrain itself is not touched.

    ../venv/bin/python build_preframe.py              # 545..1000 Ma
    ../venv/bin/python build_preframe.py 895 900      # some ages
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation

import build_displacement as BD
import build_platefield as BPF
import build_synthetic as BS
import precambrian as PRE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "fields")
ROTJSON = os.path.join(HERE, "..", "web", "platerot.json")
W, H = BD.VW, BD.VH                     # 1024 x 512, the grid both fields ship at
assert (W, H) == (BPF.PW, BPF.PH)
STEP = 5
AGES = list(range(545, 1001, STEP))
HANDOFF = 540


def _poses(age):
    return {name: PRE.craton_pose(lon, lat, spin) for name, lon, lat, spin in BS.pre_placement(age)}


def _grid_units():
    lon = (np.arange(W) + 0.5) / W * 360.0 - 180.0
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    lo, la = np.radians(LON), np.radians(LAT)
    X = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    return LON, LAT, X


def _handoff_frames():
    """Q_k: PALEOMAP's 540 -> 0 Ma rotation for each craton, read from the
    shipped 540 Ma slot raster and its row of platerot.json, taking the slot
    that covers most of the craton's 540 Ma footprint."""
    table = json.load(open(ROTJSON))["rot"][str(HANDOFF)]
    slot540 = np.asarray(Image.open(os.path.join(OUT, "phan_%04d_p.webp" % HANDOFF)))[..., 0]
    owner = PRE.craton_owner(HANDOFF, W, H)
    Q = {}
    for k, name in enumerate(PRE.CRATON_NAMES):
        m = owner == k
        if not m.any():
            Q[name] = np.eye(3)
            continue
        s = int(np.bincount(slot540[m].ravel()).argmax())
        ax, ang = np.array(table[s][:3], float), float(table[s][3])
        Q[name] = Rotation.from_rotvec(ax / max(np.linalg.norm(ax), 1e-12) * ang).as_matrix() \
            if abs(ang) > 1e-12 else np.eye(3)
    return Q


def displacement(age, w=W, h=H):
    """(dE, dN, covered) in degrees of great circle, from `age` to `age+STEP`,
    by the craton poses -- the Precambrian twin of build_displacement.
    displacement, same conventions, for build_tectonic's fabric as well."""
    owner = PRE.craton_owner(age, w, h)
    Pa, Pb = _poses(age), _poses(age + STEP)
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    lo, la = np.radians(LON.ravel()), np.radians(LAT.ravel())
    flat = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    V1 = flat.copy()
    own = owner.ravel()
    for k, name in enumerate(PRE.CRATON_NAMES):
        m = own == k
        if not m.any() or name not in Pa:
            continue
        Mv = Pb.get(name, Pa[name]) @ Pa[name].T
        with np.errstate(all="ignore"):
            V1[m] = flat[m] @ Mv.T
    dot = np.clip((flat * V1).sum(-1), -1.0, 1.0)
    gc = np.degrees(np.arccos(dot))
    tang = V1 - dot[:, None] * flat
    dirn = tang / np.maximum(np.linalg.norm(tang, axis=-1, keepdims=True), 1e-15)
    e, n = BD._tangent_basis(LON.ravel(), LAT.ravel())
    dE = (gc * (dirn * e).sum(-1)).reshape(h, w)
    dN = (gc * (dirn * n).sum(-1)).reshape(h, w)
    cov = owner >= 0
    dE[~cov] = 0.0
    dN[~cov] = 0.0
    return dE, dN, cov, owner


def bake(age, Q, P540, X, quiet=False):
    t0 = time.time()
    dE, dN, cov, owner = displacement(age, W, H)
    Pa = _poses(age)
    clip = int(((np.abs(dE) > BD.V_RANGE) | (np.abs(dN) > BD.V_RANGE)).sum())
    dEf = BD.laplace_fill(dE, cov)
    dNf = BD.laplace_fill(dN, cov)
    tr = BD.tear(dEf, dNf, W, H)
    Image.fromarray(BD._encode(dEf, dNf, tr)).save(
        os.path.join(OUT, "pre_%04d_v.webp" % age), "WEBP", lossless=True, method=6)
    # ---- the frame: craton slots, and each craton's rotation to today
    slot = np.where(cov, owner, 0).astype(np.uint8)
    if not cov.all():
        slot = BPF._nearest_fill(slot, cov)
    Image.fromarray(np.dstack([slot, slot, slot])).save(
        os.path.join(OUT, "pre_%04d_p.webp" % age), "WEBP", lossless=True, method=6)
    quats = []
    for name in PRE.CRATON_NAMES:
        if name not in Pa:
            quats.append([0.0, 0.0, 1.0, 0.0])
            continue
        M = Q[name] @ P540[name] @ Pa[name].T
        rv = Rotation.from_matrix(M).as_rotvec()
        ang = float(np.linalg.norm(rv))
        ax = rv / ang if ang > 1e-12 else np.array([0.0, 0.0, 1.0])
        quats.append([round(float(ax[0]), 6), round(float(ax[1]), 6), round(float(ax[2]), 6),
                      round(ang, 6)])
    while len(quats) < BPF.SLOTS:
        quats.append([0.0, 0.0, 1.0, 0.0])
    if not quiet:
        mx = float(np.hypot(dEf, dNf).max())
        print("  pre_%04d  crust owned %4.1f%%  warp max %.2f deg (%.0f km)  clip %d  %.1fs"
              % (age, 100 * cov.mean(), mx, mx * 111.32, clip, time.time() - t0), flush=True)
    return quats


def main():
    ages = [int(a) for a in sys.argv[1:]] or AGES
    t0 = time.time()
    _L, _A, X = _grid_units()
    Q = _handoff_frames()
    P540 = _poses(HANDOFF)
    print("Precambrian crust frame from the craton poses: %d keyframes" % len(ages), flush=True)
    d = json.load(open(ROTJSON))
    for a in ages:
        d["rot"][str(a)] = bake(a, Q, P540, X)
    with open(ROTJSON, "w") as fh:
        json.dump(d, fh, separators=(",", ":"))
    print("  platerot.json: %d Precambrian rows rewritten, %.1f min" % (len(ages), (time.time() - t0) / 60.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
