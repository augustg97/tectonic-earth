"""THE COAST AS A DISTANCE (3.20): the green channel of every `_w` field.

WHY. The shader decided land or sea from the elevation field's own zero
contour, and on every low coast of the Phanerozoic that contour is a staircase.
Measured: the source draws its coastal lowlands at exactly 0 m, so the shipped
fields carry a terrace of code 128 (+0.12 m) tens of km wide (80,895 texels at
0 Ma, 25,189 at 100 Ma, 19,231 at 300 Ma), and between a texel at +0.12 m and a
neighbour at -10 m the bilinear field crosses zero a hundredth of the way
along: the waterline runs through the centres of the outermost terrace texels,
a polyline whose steps are the land mask's own -- one to two texels, 10-20 km.
3.17 hid the stairs under a noise added to the height (which flooded the
terrace into pools); three in-shader smoothings this round each left them,
because a kernel a texel wide cannot round a two-texel stair and one wide
enough costs fifty texture reads a pixel.

WHAT. Per keyframe, a signed distance in km to a SMOOTHED coastline, positive
on land. The land mask (Z >= 0 on the shipped `_e`) is blurred by a Gaussian of
SIGMA_KM on the ground (the longitude sigma widens with latitude), and across a
straight coast a blurred step is an error function, so the distance is its
inverse -- smooth, sub-texel, exact at the contour, no distance transform. It
interpolates as a distance, so the shader gets a waterline that is a smooth
curve at any zoom and slides between keyframes instead of cross-fading.

WHAT IS PROTECTED. A blur deletes whatever is narrower than itself: islands,
straits, inlets, spits. Wherever the smoothing would change what the mask says
by more than rounding a corner -- an island or an enclosed water lost, a strait
bridged, a neck cut, or any flipped texel further than PROTECT_FAR texels from
its own kind in the smoothed mask -- the field falls back toward the unsmoothed
mask, and its magnitude is multiplied up so the shader's trust band (it uses
the distance only within ~10 km of the smooth coast, the heights beyond) closes
there and the elevation field decides, as it always did.

ENCODING. 1..250 over +/-RANGE_KM about 126 (0.26 km a level); 0 is "no
field" (a file baked before this), 255 is the DRY-BASIN flag the channel has
always carried (the Messinian drawdown, one keyframe).

    python coast_edge.py                 # every `_w` in ../web/fields (lossless; R and B untouched)
    python coast_edge.py --ages 0,100    # some
    python coast_edge.py --show 0        # build/verify/coast_0.png: the mask's coast and the smooth one
    python coast_edge.py --stats         # census only, writes nothing
"""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import (binary_dilation, distance_transform_edt, gaussian_filter1d,
                           label)
from scipy.special import erfinv

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")

SIGMA_KM = 15.0         # the smoothing, on the ground
SIGMA_FINE = 0.55       # texels: the near-original blur protected features keep
PROTECT_FAR = 1.3       # texels: a flipped texel further than this from its own kind is a lost feature
RANGE_KM = 32.0
CENTRE, SPAN = 126.0, 124.0
DRY = 255
KM_PER_DEG = 111.2
Z_RANGE = 8000.0


def _blur(F, sig_km):
    """Gaussian of sig_km on the ground: rows by a fixed sigma, columns by a
    sigma that widens as the meridians converge (banded; longitude wraps)."""
    h, w = F.shape
    dy = 180.0 / h * KM_PER_DEG
    out = gaussian_filter1d(F, sig_km / dy, axis=0, mode="nearest")
    lat = 90.0 - (np.arange(h) + 0.5) * 180.0 / h
    res = np.empty_like(out)
    band = 32
    for b0 in range(0, h, band):
        b1 = min(h, b0 + band)
        c = max(np.cos(np.radians(float(lat[(b0 + b1) // 2]))), 0.03)
        sx = min(sig_km / (dy * c), w / 8.0)
        res[b0:b1] = gaussian_filter1d(out[b0:b1], sx, axis=1, mode="wrap")
    return res


def _blur_px(F, s):
    return gaussian_filter1d(gaussian_filter1d(F, s, axis=0, mode="nearest"), s, axis=1, mode="wrap")


def _lost(M, Ms):
    """Texels of class M the smoothing removed that are not just a rounded
    corner: whole components with no survivor, and anything further than
    PROTECT_FAR from the smoothed class."""
    gone = M & ~Ms
    if not gone.any():
        return gone
    far = gone & (distance_transform_edt(~Ms) > PROTECT_FAR)
    lab, n = label(M, structure=np.ones((3, 3), bool))
    if n:
        keep = np.zeros(n + 1, bool)
        keep[np.unique(lab[Ms & M])] = True
        far |= M & ~keep[lab]
    return far


def _bridges(M, Ms):
    """Components of what the smoothing ADDED to class M that join two
    components of M that were apart (a strait bridged, seen from the land; a
    neck cut, seen from the sea)."""
    add = Ms & ~M
    out = np.zeros_like(M)
    if not add.any():
        return out
    st = np.ones((3, 3), bool)
    lab, _ = label(M, structure=st)
    alab, n = label(add, structure=st)
    if not n:
        return out
    ring = binary_dilation(add, structure=st) & M
    ys, xs = np.nonzero(ring)
    # which added component each ring texel touches: look at its 8 neighbours
    h, w = M.shape
    touch = {}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            a = alab[np.clip(ys + dy, 0, h - 1), (xs + dx) % w]
            ok = a > 0
            for ai, li in zip(a[ok], lab[ys[ok], xs[ok]]):
                touch.setdefault(int(ai), set()).add(int(li))
    bad = [a for a, s in touch.items() if len(s) >= 2]
    if bad:
        m = np.zeros(n + 1, bool)
        m[bad] = True
        out = m[alab]
    return out


def sdf_km(Z):
    """Signed distance (km, + on land) to the smoothed coast of Z (h, w; row 0
    north), with the protected features' magnitude raised. Returns (sdf, wp)."""
    land = np.asarray(Z) >= 0.0
    F = land.astype(np.float32)
    B = _blur(F, SIGMA_KM)
    Ms = B > 0.5
    prot = _lost(land, Ms) | _lost(~land, ~Ms) | _bridges(land, Ms) | _bridges(~land, ~Ms)
    if prot.any():
        prot = binary_dilation(prot, structure=np.ones((3, 3), bool), iterations=2)
        wp = np.clip(_blur_px(prot.astype(np.float32), 1.2) * 1.6, 0.0, 1.0)
    else:
        wp = np.zeros_like(B)
    B1 = _blur_px(F, SIGMA_FINE)
    # The two are blended as distances, each from its own blur's inverse: the
    # smooth one in km, the fine one at its own (sub-texel) scale.
    h = Z.shape[0]
    dy = 180.0 / h * KM_PER_DEG
    d0 = SIGMA_KM * np.sqrt(2.0) * erfinv(np.clip(2.0 * B - 1.0, -0.9995, 0.9995))
    d1 = SIGMA_FINE * dy * np.sqrt(2.0) * erfinv(np.clip(2.0 * B1 - 1.0, -0.9995, 0.9995))
    d = (1.0 - wp) * d0 + wp * d1
    # ...and where protected, far: the shader trusts this only near its zero.
    d = d * (1.0 + 6.0 * wp)
    return np.clip(d, -RANGE_KM, RANGE_KM).astype(np.float32), wp


def channel(Z, dry=None, out_shape=None):
    """uint8 channel for `_w`.G from a full-resolution Z: 1..250 the coast
    distance, 255 the dry-basin flag where `dry` (in the output shape) is set."""
    s, _ = sdf_km(Z)
    if out_shape is not None and tuple(out_shape) != s.shape:
        fy, fx = s.shape[0] // out_shape[0], s.shape[1] // out_shape[1]
        assert fy >= 1 and fx >= 1 and s.shape[0] % out_shape[0] == 0, (s.shape, out_shape)
        s = s.reshape(out_shape[0], fy, out_shape[1], fx).mean(axis=(1, 3))
    g = np.clip(np.round(CENTRE + s * (SPAN / RANGE_KM)), 1, 250).astype(np.uint8)
    if dry is not None and np.asarray(dry).any():
        # ONE TEXEL WIDER THAN THE BASIN. The flag used to be 255 against 0 and
        # the shader cut it at a half: the bilinear edge fell half a texel
        # OUTSIDE the mask, over the shore. Against a neighbour of 126 or 250
        # the top code is reached only inside the mask, and the basin's rim --
        # sea by the heights, not dry by the flag -- drew as a blue thread
        # round the whole drained Mediterranean. Dilated here, from the
        # canonical mask every time, so re-running does not grow it.
        d = binary_dilation(np.asarray(dry) > 0.5, structure=np.ones((3, 3), bool))
        g = np.where(d, DRY, g).astype(np.uint8)
    return g


def read_Z(epath):
    e = np.asarray(Image.open(epath).convert("RGB"))[..., 0].astype(np.float32) / 255.0
    d = e * 2.0 - 1.0
    return np.sign(d) * d * d * Z_RANGE


def dry_mask(wpath, shape):
    """The dry-basin mask exactly as bake_lakes derives it (the canonical
    source: reading it back out of G would compound the dilation above)."""
    import epeiric as _EP
    import bake_lakes as _BL
    base = os.path.basename(wpath).replace("_wold.webp", "").replace("_w.webp", "")
    age = float(_BL.parse_age(base))
    if abs(age - _EP.MESSINIAN_AGE) > 0.01:
        return np.zeros(shape, bool)
    epath = wpath.replace("_wold.webp", "_e.avif").replace("_w.webp", "_e.avif")
    im = Image.open(epath).convert("RGB").resize((_BL.ELEV_W, _BL.ELEV_H), Image.BILINEAR)
    e = np.asarray(im)[..., 0].astype(np.float32) / 255.0
    d = e * 2.0 - 1.0
    m = _EP.messinian_mask((_BL.ELEV_H, _BL.ELEV_W), age, np.sign(d) * d * d * Z_RANGE)
    assert m.shape == tuple(shape), (m.shape, shape)
    return np.clip(m, 0.0, 1.0) > 0.5


def bake_file(wpath, write=True):
    epath = wpath.replace("_wold.webp", "_e.avif").replace("_w.webp", "_e.avif")
    if not os.path.exists(epath):
        return os.path.basename(wpath), None
    Z = read_Z(epath)
    a = np.asarray(Image.open(wpath).convert("RGB")).copy()
    dry = dry_mask(wpath, a.shape[:2])
    s, wp = sdf_km(Z)
    g = channel(Z, dry, a.shape[:2])
    land = Z >= 0
    sm = s > 0
    st = dict(flip=float((land != sm).mean() * 100.0), prot=float((wp > 0.5).mean() * 100.0),
              land=float(land.mean() * 100.0), land_s=float(sm.mean() * 100.0), dry=int(dry.sum()))
    if write:
        a[..., 1] = g
        Image.fromarray(a, "RGB").save(wpath, "WEBP", lossless=True, method=6)
    return os.path.basename(wpath), st


def _job(args):
    return bake_file(*args)


def show(age):
    name = ("phan_%04d" % age) if age >= 0 else ("fut_%04d" % -age)
    ep = os.path.join(FIELDS, name + "_e.avif")
    if not os.path.exists(ep):
        ep = os.path.join(FIELDS, "pre_%04d_e.avif" % age)
    Z = read_Z(ep)
    s, wp = sdf_km(Z)
    land = Z >= 0
    img = np.zeros(Z.shape + (3,), np.uint8)
    img[land] = (70, 110, 60)
    img[~land] = (30, 50, 110)
    img[(s > 0) & ~land] = (230, 200, 60)      # sea the smooth coast makes land
    img[(s <= 0) & land] = (60, 200, 230)      # land it makes sea
    img[wp > 0.5] = (img[wp > 0.5] * 0.5 + np.array([200, 40, 40]) * 0.5).astype(np.uint8)
    out = os.path.join(HERE, "verify", "coast_%d.png" % age)
    Image.fromarray(img).save(out)
    print("wrote", out)


def main():
    args = sys.argv[1:]
    if "--show" in args:
        show(int(args[args.index("--show") + 1]))
        return 0
    write = "--stats" not in args
    files = sorted(glob.glob(os.path.join(FIELDS, "*_w.webp")) + glob.glob(os.path.join(FIELDS, "*_wold.webp")))
    if "--ages" in args:
        want = set()
        for a in args[args.index("--ages") + 1].split(","):
            a = int(a)
            want.add(("phan_%04d" % a) if a >= 0 else ("fut_%04d" % -a))
            want.add("pre_%04d" % a)
        files = [f for f in files if os.path.basename(f).rsplit("_", 1)[0] in want]
    from multiprocessing import Pool
    workers = 8
    if "-j" in args:
        workers = int(args[args.index("-j") + 1])
    done = 0
    worst = (0.0, "")
    with Pool(workers) as pool:
        for name, st in pool.imap_unordered(_job, [(f, write) for f in files]):
            done += 1
            if st is None:
                print("  %-22s NO ELEVATION FILE -- skipped" % name, flush=True)
                continue
            if st["flip"] > worst[0]:
                worst = (st["flip"], name)
            if done % 25 == 0 or len(files) < 12:
                print("  %-22s land %5.2f -> %5.2f %%  flipped %4.2f %%  protected %4.2f %%  dry %d"
                      % (name, st["land"], st["land_s"], st["flip"], st["prot"], st["dry"]), flush=True)
    print("coast_edge: %d files %s; most texels flipped: %.2f %% (%s)  COAST-EDGE-DONE"
          % (done, "written" if write else "measured", worst[0], worst[1]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
