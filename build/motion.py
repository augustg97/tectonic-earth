"""Derive plate motion for every era directly from the reconstruction.

The present-day layers (MORVEL vectors, PB2002 boundaries) only describe today.
Rather than invent boundary geometry for deep time, this recovers motion from
the data already in hand: two elevation keyframes ARE the same crust some
millions of years apart, so block-matching one against the other measures how
far each patch of surface travelled.

From that single displacement field both overlays follow, and they agree with
each other by construction:
  * motion vectors  -- the field itself, in mm/yr
  * boundaries      -- its divergence. Crust pulling apart is a spreading
                       ridge; crust converging is a trench or collision.

Matching uses a wide baseline (+/- BASE_MYR). Over a single 5 Myr step a plate
moves well under one grid cell, which integer block-matching cannot resolve at
all; over ~30 Myr it moves several cells and the measurement becomes real.

Exported as one small RGB image per keyframe (R = east, G = north,
B = confidence), which the page samples for arrows and the shader reads to
draw boundaries.
"""
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view

GRID_W, GRID_H = 128, 64
SEARCH = 6            # max shift searched, in cells
PATCH = 3             # half-width of the correlation patch
BASE_MYR = 15.0       # half-baseline; frames BASE before and after are compared
V_RANGE = 160.0       # mm/yr encoded across the 0..1 range
DEG_PER_CELL = 360.0 / GRID_W


def coarsen(Z):
    """Reduce an elevation grid to the motion grid. Callers cache this per
    keyframe so the wide matching baseline costs no extra generation."""
    im = Image.fromarray(np.clip((Z + 8000) / 16000 * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.resize((GRID_W, GRID_H), Image.BOX)).astype(np.float32)


def _highpass(x, k=4):
    pad = np.pad(x, ((k, k), (k, k)), mode="wrap")
    low = sliding_window_view(pad, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))
    return x - low


def displacement(C0, C1, dt_myr):
    """Match C1 (younger) against C0 (older); both already coarsened. Returns
    vx, vy in mm/yr and a confidence 0..1. +vx is east, +vy is north."""
    A = _highpass(C0)
    B = _highpass(C1)

    P = 2 * PATCH + 1
    Apad = np.pad(A, ((PATCH, PATCH), (PATCH, PATCH)), mode="wrap")
    Awin = sliding_window_view(Apad, (P, P))

    best = np.full((GRID_H, GRID_W), 1e9, np.float32)
    second = np.full((GRID_H, GRID_W), 1e9, np.float32)
    bx = np.zeros((GRID_H, GRID_W), np.float32)
    by = np.zeros((GRID_H, GRID_W), np.float32)
    costs = {}
    for dy in range(-SEARCH, SEARCH + 1):
        for dx in range(-SEARCH, SEARCH + 1):
            Bsh = np.roll(np.roll(B, -dy, axis=0), -dx, axis=1)
            Bpad = np.pad(Bsh, ((PATCH, PATCH), (PATCH, PATCH)), mode="wrap")
            cost = np.abs(Awin - sliding_window_view(Bpad, (P, P))).mean(axis=(-1, -2))
            costs[(dx, dy)] = cost
            upd = cost < best
            second = np.where(upd, best, np.minimum(second, cost))
            bx = np.where(upd, dx, bx)
            by = np.where(upd, dy, by)
            best = np.where(upd, cost, best)

    # Sub-cell refinement: fit a parabola through the winning cost and its two
    # neighbours on each axis, so vectors vary smoothly instead of snapping to
    # whole cells.
    def refine(axis):
        out = np.zeros((GRID_H, GRID_W), np.float32)
        for dy in range(-SEARCH, SEARCH + 1):
            for dx in range(-SEARCH, SEARCH + 1):
                m = (bx == dx) & (by == dy)
                if not m.any():
                    continue
                lo = costs.get((dx - 1, dy) if axis == 0 else (dx, dy - 1))
                hi = costs.get((dx + 1, dy) if axis == 0 else (dx, dy + 1))
                if lo is None or hi is None:
                    continue
                den = (lo - 2 * best + hi)
                shift = np.where(np.abs(den) > 1e-6, 0.5 * (lo - hi) / np.where(den == 0, 1, den), 0)
                out = np.where(m, np.clip(shift, -0.5, 0.5), out)
        return out
    bx = bx + refine(0)
    by = by + refine(1)

    # Confidence: matching is only meaningful where there is structure to match.
    # Abyssal plain is featureless and would otherwise report confident nonsense.
    P2 = 2 * PATCH + 1
    var = sliding_window_view(np.pad(np.abs(A), ((PATCH, PATCH), (PATCH, PATCH)), mode="wrap"),
                              (P2, P2)).mean(axis=(-1, -2))
    conf = np.clip(var / (np.percentile(var, 55) + 1e-6), 0, 1)
    uniq = np.clip((second - best) / (best + 1e-3) * 3.0, 0, 1)
    conf *= (0.45 + 0.55 * uniq)

    # cells -> degrees -> mm/yr (111 km per degree; east shrinks with latitude)
    lat = 90 - (np.arange(GRID_H) + 0.5) / GRID_H * 180
    coslat = np.cos(np.radians(lat))[:, None]
    vx = bx * DEG_PER_CELL * coslat * 111.0 / dt_myr
    vy = -by * DEG_PER_CELL * 111.0 / dt_myr        # row + is south

    # Plates move as rigid sheets, so spread the confident measurements over
    # their neighbourhoods. This both de-noises the field and fills the quiet
    # interior of a plate from its well-textured margins.
    def wblur(a, w, k=2):
        pa = np.pad(a * w, ((k, k), (k, k)), mode="wrap")
        pw = np.pad(w, ((k, k), (k, k)), mode="wrap")
        num = sliding_window_view(pa, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))
        den = sliding_window_view(pw, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))
        return num / (den + 1e-6)
    for _ in range(2):
        vx = wblur(vx, conf); vy = wblur(vy, conf)
    return vx.astype(np.float32), vy.astype(np.float32), conf.astype(np.float32)


def encode(vx, vy, conf):
    r = np.clip(vx / V_RANGE * 0.5 + 0.5, 0, 1)
    g = np.clip(vy / V_RANGE * 0.5 + 0.5, 0, 1)
    b = np.clip(conf, 0, 1)
    return Image.fromarray((np.stack([r, g, b], -1) * 255 + 0.5).astype(np.uint8))


def remove_net_rotation(vx, vy, conf):
    """Subtract the confidence-weighted global mean motion.

    Paleomagnetic reconstructions do not constrain paleolongitude, so
    successive frames can share an arbitrary global drift. Left in, that drift
    swamps the real signal and makes every plate appear to march the same way.
    Removing it puts the field in something close to a no-net-rotation frame,
    which is also the convention MORVEL uses for present-day motions.
    """
    w = conf.sum() + 1e-6
    return vx - (vx * conf).sum() / w, vy - (vy * conf).sum() / w


def classify(vx, vy, conf):
    """Ridge / trench / transform strength from the motion field.

    Divergence separates spreading from converging; the shear (off-diagonal
    strain) picks out where plates slide past each other instead. Doing this
    offline rather than in the shader means the field can be smoothed and
    thresholded properly, so boundaries come out as continuous belts rather
    than a speckle of pixels crossing a threshold.
    """
    def dx(a):
        return (np.roll(a, -1, axis=1) - np.roll(a, 1, axis=1)) * 0.5
    def dy(a):
        return (np.roll(a, -1, axis=0) - np.roll(a, 1, axis=0)) * 0.5

    dudx, dudy = dx(vx), dy(vx)
    dvdx, dvdy = dx(vy), dy(vy)
    div = dudx + dvdy                      # >0 spreading, <0 converging
    shear = np.sqrt((dudy + dvdx) ** 2 + (dudx - dvdy) ** 2)

    def smooth(a, k=1):
        pad = np.pad(a, ((k, k), (k, k)), mode="wrap")
        return sliding_window_view(pad, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))

    div = smooth(div); shear = smooth(shear)
    c = np.clip(conf * 1.5, 0, 1)
    # Boundaries are narrow features on a coarse grid, so thresholds are set
    # high and the fields are NOT smoothed afterwards -- blurring the result
    # turns a plate margin into a broad stain rather than a line.
    scale = np.percentile(np.abs(div)[conf > 0.25], 94) + 1e-6
    ridge = np.clip(div / scale - 0.80, 0, 1) * c
    trench = np.clip(-div / scale - 0.80, 0, 1) * c
    # transform: strong shear that is NOT mostly opening or closing
    tscale = np.percentile(shear[conf > 0.25], 96) + 1e-6
    trans = np.clip(shear / tscale - 0.85, 0, 1) * c
    trans *= np.clip(1.0 - (ridge + trench) * 2.0, 0, 1)
    return np.clip(ridge, 0, 1), np.clip(trench, 0, 1), np.clip(trans, 0, 1)


def encode_bounds(ridge, trench, trans):
    return Image.fromarray(
        (np.stack([ridge, trench, trans], -1) * 255 + 0.5).astype(np.uint8))


def _bilerp(F, y, x):
    h, w = F.shape
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    x0 %= w; x1 = (x0 + 1) % w
    y0 = np.clip(y0, 0, h - 1); y1 = np.clip(y0 + 1, 0, h - 1)
    return (F[y0, x0] * (1 - fx) * (1 - fy) + F[y0, x1] * fx * (1 - fy) +
            F[y1, x0] * (1 - fx) * fy + F[y1, x1] * fx * fy)


def _skeleton(S, thresh):
    """Non-maximum suppression: keep only the crest of each ridge in S.

    Thresholding a smooth field leaves a blob several cells wide, which is why
    the boundaries rendered as stains. Suppressing everything that is not a
    local maximum along the gradient reduces each belt to a one-cell line.
    """
    h, w = S.shape
    gy, gx = np.gradient(S)
    mag = np.hypot(gx, gy) + 1e-9
    ux, uy = gx / mag, gy / mag
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    a = _bilerp(S, yy + uy, xx + ux)
    b = _bilerp(S, yy - uy, xx - ux)
    return (S >= a) & (S >= b) & (S > thresh)


def boundary_lines(vx, vy, conf, up=2):
    """Trace derived plate boundaries as line segments.

    Returns {'ridge': [...], 'trench': [...], 'transform': [...]} where each
    entry is [lon1, lat1, lon2, lat2]. Segments are what the present-day PB2002
    layer draws, so deep-time boundaries render in exactly the same style
    instead of as a coloured field.
    """
    def smooth(a, k=1):
        pad = np.pad(a, ((k, k), (k, k)), mode="wrap")
        return sliding_window_view(pad, (2 * k + 1, 2 * k + 1)).mean(axis=(-1, -2))

    def dx(a): return (np.roll(a, -1, axis=1) - np.roll(a, 1, axis=1)) * 0.5
    def dy(a): return (np.roll(a, -1, axis=0) - np.roll(a, 1, axis=0)) * 0.5

    dudx, dudy = dx(vx), dy(vx)
    dvdx, dvdy = dx(vy), dy(vy)
    div = smooth(dudx + dvdy)
    shear = smooth(np.sqrt((dudy + dvdx) ** 2 + (dudx - dvdy) ** 2))
    c = np.clip(conf * 1.5, 0, 1)

    # upsample so the traced line has finer than one-cell placement
    H, W = GRID_H * up, GRID_W * up
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    ys, xs = yy / up, xx / up
    divU = _bilerp(div, ys, xs); shU = _bilerp(shear, ys, xs); cU = _bilerp(c, ys, xs)

    ok = conf > 0.25
    dscale = np.percentile(np.abs(div)[ok], 90) + 1e-6
    sscale = np.percentile(shear[ok], 93) + 1e-6

    masks = {
        "ridge":     _skeleton(divU / dscale, 0.75) & (cU > 0.30),
        "trench":    _skeleton(-divU / dscale, 0.75) & (cU > 0.30),
        "transform": _skeleton(shU / sscale, 0.95) & (cU > 0.35),
    }
    # shear is high wherever plates interact; keep transforms only where the
    # motion is not mostly opening or closing
    masks["transform"] &= (np.abs(divU) / dscale < 0.55)

    out = {}
    for name, M in masks.items():
        segs = []
        idx = np.argwhere(M)
        Mset = set(map(tuple, idx))
        for (r, cc) in idx:
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                nb = ((r + dr) % H, (cc + dc) % W)
                if nb in Mset:
                    lon1 = (cc + 0.5) / W * 360 - 180
                    lat1 = 90 - (r + 0.5) / H * 180
                    lon2 = (nb[1] + 0.5) / W * 360 - 180
                    lat2 = 90 - (nb[0] + 0.5) / H * 180
                    if abs(lon2 - lon1) > 180:      # skip the wrap seam
                        continue
                    segs.append([round(lon1, 1), round(lat1, 1),
                                 round(lon2, 1), round(lat2, 1)])
        out[name] = segs
    return out
