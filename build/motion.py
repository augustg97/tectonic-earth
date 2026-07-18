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
