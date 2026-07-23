"""Derive a SURFACE-PROCESS field per keyframe: drainage, substrate, fetch.

The app knew where the ground was and how much rain fell on it, and nothing
about what the water then DID. So a continental interior came out as one flat
tone: no rivers, no floodplains, no distinction between a shield that has been
bare rock for a billion years and a basin filling with its debris. This adds the
three things that separate those, all derived from terrain the app already
ships rather than painted on.

    R  DRAINAGE   log flow accumulation. Depressions are filled, every cell is
       given a D8 steepest-descent receiver, and rain is routed downhill and
       summed. So a river appears where a large wet catchment converges, its
       size answers to the climate of the age, and it moves when the terrain
       does. This is what puts water in valleys instead of noise on slopes.

    G  SUBSTRATE  what the ground is made of, from what the terrain says about
       it. High relief at height is orogenic rock, freshly exposed and hard;
       low flat ground under a big catchment is a sediment basin, soft and
       deep; low flat ground with no catchment is old shield, planed down and
       hard. Erodibility follows, and so does what will grow.

    B  FETCH      how far the prevailing wind has travelled over land before it
       arrives, on the same latitude-banded easterlies and westerlies the
       rainfall solve uses. This is continentality -- the thing that makes the
       middle of a supercontinent different in kind from its margins, and the
       reason the Pangaean interior was a desert with monsoon coasts.

Written as one RGB webp per keyframe (`*_d.webp`), read alongside the elevation
and rainfall fields. Runs off the SHIPPED textures, so it needs no DEM and no
35-minute rebuild.

    ../venv/bin/python build_surface.py            # every keyframe
    ../venv/bin/python build_surface.py phan_0000  # one, with stats
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

from climate import climate_at

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
Z_RANGE = 8000.0
RF_MAX = 1.3
# Match the elevation field. At half its resolution a river channel was two
# pixels wide on a 2048-wide texture and vanished into the interpolation.
H, W = 1024, 2048


def _read(path, size=None):
    im = Image.open(path).convert("L")
    if size:
        im = im.resize(size, Image.BILINEAR)
    return np.asarray(im, np.float32) / 255.0


def elevation(base):
    p = os.path.join(FIELDS, base + "_e.webp")
    if not os.path.exists(p):
        return None
    s = 2.0 * _read(p, (W, H)) - 1.0
    return np.sign(s) * s * s * Z_RANGE


def rainfall(base):
    p = os.path.join(FIELDS, base + "_r.webp")
    if not os.path.exists(p):
        return np.full((H, W), 0.4, np.float32)
    return _read(p, (W, H)) * RF_MAX


# ---------------------------------------------------------------- drainage --
#: Eight neighbours as (drow, dcol). Longitude wraps; latitude does not.
D8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def fill_depressions(z, sea):
    """Raise every closed basin to its spill level (priority flood).

    Water cannot leave a hollow except over the lip, and a flow router that
    meets an unfilled hollow simply stops -- which on a real DEM means most of
    the continent drains nowhere. Filling first is what makes the routing give
    connected rivers rather than a scatter of fragments.

    Implemented as a flood from the coast inward with a heap, which is the
    standard priority-flood: pop the lowest cell on the frontier, and any
    neighbour lower than it gets raised to it.
    """
    import heapq
    filled = np.where(sea, z, np.inf).astype(np.float64)
    seen = sea.copy()
    heap = []
    ys, xs = np.nonzero(sea)
    for y, x in zip(ys.tolist(), xs.tolist()):
        for dy, dx in D8:
            ny, nx = y + dy, (x + dx) % W
            if 0 <= ny < H and not seen[ny, nx]:
                seen[ny, nx] = True
                filled[ny, nx] = z[ny, nx]
                heapq.heappush(heap, (float(z[ny, nx]), ny, nx))
    while heap:
        e, y, x = heapq.heappop(heap)
        for dy, dx in D8:
            ny, nx = y + dy, (x + dx) % W
            if not (0 <= ny < H) or seen[ny, nx]:
                continue
            seen[ny, nx] = True
            # Priority-flood-plus-EPSILON. A plain fill makes every drowned
            # basin exactly level, and D8 has no downhill neighbour on a flat,
            # so routing dies the moment it enters one and no river forms at
            # all. A micrometre of tilt away from the spill point costs nothing
            # visible and guarantees every cell has somewhere to send water.
            v = max(float(z[ny, nx]), e + 1e-3)
            filled[ny, nx] = v
            heapq.heappush(heap, (v, ny, nx))
    filled[sea] = z[sea]
    return filled.astype(np.float32)


def flow_accumulation(zf, rain, sea):
    """Route rain downhill and sum it.

    Cells are processed from high to low, which guarantees a cell's own total
    is complete before it hands on -- no iteration, one pass. The weight is
    rainfall, not cell count, so the same valley carries a great river in a wet
    age and a wadi in a dry one, which is most of the point of deriving this
    per keyframe instead of once.
    """
    n = H * W
    zflat = zf.ravel()
    # steepest-descent receiver for every cell
    best = np.full(n, -1, np.int64)
    drop = np.zeros(n, np.float32)
    for dy, dx in D8:
        # roll(-dy) puts the dy-neighbour at each cell. The row that wrapped
        # across the pole is not a neighbour of anything, so invalidate it --
        # and it is the row the shift came FROM, which is the opposite end from
        # the one it is tempting to blank. Getting this backwards silently
        # broke every north-south link and no river grew past a few cells.
        nz = np.roll(np.roll(zf, -dy, axis=0), -dx, axis=1)
        if dy < 0:
            nz[:1, :] = np.inf
        elif dy > 0:
            nz[H - 1:, :] = np.inf
        d = (zf - nz) / (1.4 if dy and dx else 1.0)
        # index of the neighbour, with longitude wrapped
        yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
        ny = np.clip(yy + dy, 0, H - 1)
        nx = (xx + dx) % W
        nidx = (ny * W + nx).ravel()
        dflat = d.ravel()
        take = dflat > drop
        best[take] = nidx[take]
        drop[take] = dflat[take]

    acc = np.maximum(rain.ravel(), 0.0).astype(np.float64) + 0.02
    order = np.argsort(-zflat, kind="stable")
    seaflat = sea.ravel()
    b = best
    a = acc
    for i in order:
        if seaflat[i]:
            continue
        j = b[i]
        if j >= 0 and not seaflat[j]:
            a[j] += a[i]
    return a.reshape(H, W).astype(np.float32)


# --------------------------------------------------------------- substrate --
def substrate(z, zf, acc, sea):
    """0 = soft sediment basin, 1 = hard shield / resistant orogen.

    Not a rock TYPE -- the record cannot give one globally through deep time --
    but the property that matters for how the surface behaves: whether the
    ground yields to water or resists it. Three settings the terrain can
    actually distinguish, and they behave differently in every respect that
    shows on a map.
    """
    zp = np.clip(z, 0, None)
    # local relief over a 3-cell window, as a proxy for tectonic youth
    rel = np.zeros_like(zp)
    for dy, dx in D8:
        rel = np.maximum(rel, np.abs(zp - np.roll(np.roll(zp, dy, 0), dx, 1)))
    orogen = np.clip((rel - 150.0) / 550.0, 0, 1) * np.clip(zp / 900.0, 0, 1)
    wet_low = np.clip(1.0 - zp / 700.0, 0, 1) * np.clip(np.log1p(acc) / 7.0, 0, 1)
    hard = np.clip(0.55 + 0.45 * orogen - 0.60 * wet_low, 0.0, 1.0)
    hard[sea] = 0.5
    return hard


# ------------------------------------------------------------------- fetch --
def fetch(z, sea, lat):
    """Distance the prevailing wind has run over land, 0 (coast) .. 1 (deep interior).

    Same wind bands as the rainfall solve -- tropical easterlies, mid-latitude
    westerlies, polar easterlies -- because a continentality that disagreed with
    the rainfall would put the dry heart in the wrong place.
    """
    # +1 = air travels toward increasing column (westerly), -1 = easterly.
    # One direction per ROW: the wind bands are zonal.
    a = np.abs(lat[:, 0])
    direction = np.where((a < 30) | (a >= 60), -1.0, 1.0)
    f = np.zeros((H, W), np.float32)
    for _ in range(2):                       # two wraps, so the start does not matter
        for step in range(W):
            for sgn in (-1.0, 1.0):
                rows = direction == sgn
                if not rows.any():
                    continue
                c = (step if sgn > 0 else W - 1 - step)
                pc = int((c - 1) % W) if sgn > 0 else int((c + 1) % W)
                prev = f[:, pc]
                grow = np.where(sea[:, c], 0.0, prev + 1.0)
                f[rows, c] = grow[rows]
    return np.clip(f / 90.0, 0, 1)


# ------------------------------------------------------------------ output --
def build_one(base, verbose=False):
    z = elevation(base)
    if z is None:
        return None
    rain = rainfall(base)
    sea = z < 0
    if sea.all():
        return None
    lat = np.linspace(90, -90, H)[:, None] * np.ones((1, W), np.float32)
    zf = fill_depressions(z, sea)
    acc = flow_accumulation(zf, rain, sea)
    hard = substrate(z, zf, acc, sea)
    fet = fetch(z, sea, lat)
    # Normalise PER FRAME, against this age's own distribution.
    #
    # A fixed divisor was tuned on the present day and was wrong everywhere
    # else: total accumulation depends on how much land there is, how wet it
    # is, and how much relief there is to concentrate flow, all of which move
    # by an order of magnitude across the timeline. At 60 Ma -- low relief,
    # a drowned interior -- the whole of North America peaked at 0.26 on a
    # scale where the shader does not draw a channel until 0.50, so the
    # continent had no rivers at all on it.
    #
    # Anchoring on a high percentile of the land distribution instead means
    # the top fraction of a percent of any age's land is always river, which
    # is what a drainage network actually looks like from orbit: a thin
    # dendritic minority of the surface, at every age.
    land = ~sea
    lo = float(np.percentile(acc[land], 90.0)) if land.any() else 1.0
    hi = float(np.percentile(acc[land], 99.85)) if land.any() else 10.0
    lo, hi = max(lo, 1e-3), max(hi, lo * 4.0)
    drain = np.clip((np.log1p(acc) - np.log1p(lo)) / (np.log1p(hi) - np.log1p(lo)), 0, 1)
    drain = drain * 0.55 + 0.30 * (drain > 0.001)      # channels land near 0.85
    drain = np.clip(drain, 0, 1)
    drain[sea] = 0.0
    rgb = np.stack([drain, hard, fet], -1)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    img.save(os.path.join(FIELDS, base + "_d.webp"), "WEBP", quality=92, method=4)
    if verbose:
        land = ~sea
        print(f"  {base}: river cells (drain>0.55) "
              f"{100.0*(drain[land] > 0.55).mean():.2f}% of land, "
              f"mean substrate {hard[land].mean():.2f}, "
              f"mean fetch {fet[land].mean():.2f}")
    return drain, hard, fet


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        build_one(sys.argv[1], verbose=True)
        return
    bases = sorted({os.path.basename(p)[:-len("_e.webp")]
                    for p in glob.glob(os.path.join(FIELDS, "*_e.webp"))})
    print(f"deriving surface fields for {len(bases)} keyframes...")
    for i, b in enumerate(bases):
        build_one(b, verbose=(i % 40 == 0))
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(bases)}")
    print("done")


if __name__ == "__main__":
    main()
