"""Bake the OROGEN ATLAS (WP-10, plan B2): real eroded relief for the mountains.

WHY. Everything on land finer than the 9.8 km elevation grid used to be value
noise, and the register (iterations 51-77) measured that no per-pixel noise --
ridged, stretched, smeared or steered -- produces the ORGANISATION a mountain
range has: connected dendritic valleys, divides that run, ridges spaced 8-25
km along strike. Organisation is what erosion makes. So it is made here, once,
offline, by an erosion model, and the shader samples it like a texture instead
of inventing it per pixel.

WHAT. A small library of tileable relief patches, PATCH x PATCH texels at
DX metres each (default 512 at 500 m: 256 km across), each produced by the
standard stream-power / hillslope model

    dh/dt = U(x,y) - K A^m S^n + D lap(h)

run to a dynamic steady state on a periodic domain with a fixed base level
along a sparse network of outlet cells, so that drainage organises into
basins that fill the whole patch and every edge wraps. The uplift U carries
the tectonic style:

    belt      stripes of uplift along the y axis at a chosen spacing, wandering
              with a low noise -- a fold-and-thrust belt; the shader rotates the
              patch to the local fold axis, so y IS strike
    plateau   uniform uplift, low K -- a dissected upland, flat tops, deep
              incision only along the trunks
    lowland   low, gentle uplift with high D -- dissected rolling country

Several seeds of each. Output: build/atlas/*.png (RGBA: height hi/lo 16-bit
in R,G; normal x,y in B,A) plus web/atlas.png, a single 4x4 sheet of patches
the shader binds once, and web/atlas.json describing what each cell is.

    python3 build_orogen_atlas.py             # the full set (a few minutes)
    python3 build_orogen_atlas.py --quick     # 128 px, few steps, for a look

The solver is the implicit FastScape scheme (Braun & Willett 2013): receivers
by steepest descent, nodes ordered by their distance from an outlet, and the
implicit update h = (h + U dt + K dt A^m h_rcv / dx) / (1 + K dt A^m / dx)
applied one level of the tree at a time, vectorised over the level.
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "atlas")
WEB = os.path.join(HERE, "..", "web")

PATCH = 512          # texels per patch side
DX = 500.0           # metres per texel; the patch is 256 km across
M, N_EXP = 0.5, 1.0  # stream-power exponents
KM_PER_TEXEL = DX / 1000.0

# ---------------------------------------------------------------- noise
def _fbm(shape, seed, octaves=5, base=4):
    """Periodic value noise, so a patch tiles."""
    rng = np.random.default_rng(seed)
    h, w = shape
    out = np.zeros(shape, np.float64)
    amp, f = 1.0, base
    for _ in range(octaves):
        g = rng.random((f, f))
        # periodic bilinear upsample of an f x f lattice to h x w
        ys = (np.arange(h) / h) * f
        xs = (np.arange(w) / w) * f
        y0 = np.floor(ys).astype(int) % f; x0 = np.floor(xs).astype(int) % f
        y1 = (y0 + 1) % f; x1 = (x0 + 1) % f
        fy = (ys - np.floor(ys))[:, None]; fx = (xs - np.floor(xs))[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[np.ix_(y0, x0)] * (1 - fx) + g[np.ix_(y0, x1)] * fx
        b = g[np.ix_(y1, x0)] * (1 - fx) + g[np.ix_(y1, x1)] * fx
        out += amp * (a * (1 - fy) + b * fy)
        amp *= 0.5; f *= 2
    out -= out.min(); out /= (out.max() + 1e-12)
    return out


# ---------------------------------------------------------------- flow routing
def _receivers(h):
    """Steepest-descent receiver of every cell on a periodic grid (D8).
    Returns the flat receiver index and the slope to it; a cell with no lower
    neighbour is its own receiver (a pit or an outlet)."""
    n = h.shape[0]
    # A receiver must be strictly LOWER. Initialising the best slope at -1
    # let a cell pick an uphill neighbour, which made two-cell cycles, and a
    # breadth-first walk over a graph with cycles never ends.
    best = np.zeros(h.shape)
    rcv = np.arange(n * n).reshape(h.shape)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            nb = np.roll(np.roll(h, -dy, 0), -dx, 1)
            dist = DX * (np.hypot(dy, dx))
            s = (h - nb) / dist
            better = s > best
            best = np.where(better, s, best)
            idx = (np.roll(np.roll(rcv * 0 + np.arange(n * n).reshape(h.shape), -dy, 0), -dx, 1))
            rcv = np.where(better, idx, rcv)
    return rcv.ravel(), np.maximum(best, 0.0).ravel()


def _levels(rcv, outlet):
    """Order nodes by distance (in hops) from an outlet along the receiver
    tree: level 0 = outlets, level 1 = their donors, ... Pits that are not
    outlets never reach a level and are handled by the caller."""
    n = rcv.size
    level = np.full(n, -1, np.int32)
    level[outlet] = 0
    frontier = np.flatnonzero(outlet)
    donors_of = [[] for _ in range(n)]
    for i in range(n):
        if rcv[i] != i:
            donors_of[rcv[i]].append(i)
    # BFS from outlets over donors -- python loop over the tree, once per step,
    # vectorised where it matters (the solve).
    lv = 0
    order = [frontier]
    while frontier.size:
        nxt = []
        for f in frontier:
            for d in donors_of[f]:
                if level[d] < 0:          # visited guard: the tree is a DAG, but be safe
                    level[d] = lv + 1
                    nxt.append(d)
        lv += 1
        frontier = np.array(nxt, np.int64)
        if frontier.size:
            order.append(frontier)
    return order, level


def _fill_pits(h, outlet):
    """Fill every closed depression up to its spill level, so that every cell
    drains to an outlet. Morphological reconstruction by erosion (Vincent
    1993): the outlets keep their height, everything else starts at the
    maximum and is eroded down toward the surface, and what remains above the
    surface is exactly the water a pit would hold. C speed, one pass; the
    heap-based priority flood it replaces was a Python loop per cell per step.
    The grid wraps but the reconstruction does not; a pit that would drain
    across the wrap is filled to its interior spill instead, which only ever
    errs high, and the receivers below still route across the wrap."""
    from skimage.morphology import reconstruction
    seed = np.full(h.shape, h.max() + 1.0)
    seed[outlet] = h[outlet]
    # a tiny gradient toward the outlets so filled lakes are not perfectly flat
    filled = reconstruction(seed, np.maximum(h, np.where(outlet, h, -np.inf)), method="erosion")
    return np.maximum(filled, h)


def _resolve_flats(h, rcv, level, outlet):
    """Give every cell the pit filler left on a flat a receiver, by growing
    the drained set outward across the flat from where it already drains: a
    cell joins when a neighbour at most a hair higher already has a path. On
    a filled lake that walks in from the spill point, so the lake drains to
    it with no cycles. Returns the receiver array with every flat resolved."""
    n = h.shape[0]
    resolved = (level >= 0).reshape(h.shape)
    rc = rcv.reshape(h.shape).copy()
    ids = np.arange(n * n).reshape(h.shape)
    for _ in range(4 * n):
        todo = ~resolved & ~outlet
        if not todo.any():
            break
        changed = False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                nres = np.roll(np.roll(resolved, -dy, 0), -dx, 1)
                nh = np.roll(np.roll(h, -dy, 0), -dx, 1)
                nid = np.roll(np.roll(ids, -dy, 0), -dx, 1)
                take = todo & nres & (nh <= h + 1e-3)
                if take.any():
                    rc[take] = nid[take]; resolved[take] = True; todo &= ~take; changed = True
        if not changed:
            break
    return rc.ravel()


# ---------------------------------------------------------------- the model
def erode(uplift, K, D, outlet, steps, dt, seed, init=None, log=None):
    n = uplift.shape[0]
    rng = np.random.default_rng(seed)
    h = init if init is not None else rng.random(uplift.shape) * 5.0
    area_cell = DX * DX
    fill_every = 4
    for it in range(steps):
        h = h + uplift * dt
        # Pits are filled every few steps: the reconstruction is the one slow
        # call, and once drainage has organised a new closed pit is rare.
        hf = _fill_pits(h, outlet) if it % fill_every == 0 else h
        rcv, slope = _receivers(hf)
        order, level = _levels(rcv, outlet.ravel())
        if (level < 0).any():
            rcv = _resolve_flats(hf, rcv, level, outlet)
            order, level = _levels(rcv, outlet.ravel())
        hh = h.ravel()
        # drainage area: accumulate from the leaves down the tree
        A = np.full(n * n, area_cell)
        for lv in range(len(order) - 1, 0, -1):
            np.add.at(A, rcv[order[lv]], A[order[lv]])
        # implicit stream-power update, receivers first
        Kf = K.ravel() * dt * (A ** M) / DX
        for lv in range(1, len(order)):
            idx = order[lv]
            r = rcv[idx]
            hh[idx] = (hh[idx] + Kf[idx] * hh[r]) / (1.0 + Kf[idx])
        h = hh.reshape(n, n)
        # hillslope diffusion, explicit, periodic
        lap = (np.roll(h, 1, 0) + np.roll(h, -1, 0) + np.roll(h, 1, 1) + np.roll(h, -1, 1) - 4 * h) / (DX * DX)
        h = h + D * dt * lap
        h[outlet] = 0.0
        if log and (it % max(1, steps // 10) == 0 or it == steps - 1):
            log("    step %3d/%d  relief %6.0f m  mean %5.0f m" % (it + 1, steps, h.max() - h.min(), h.mean()))
    return h


def _normal(h, exag=1.0):
    gy, gx = np.gradient(h, DX)
    nx, ny = -gx * exag, -gy * exag
    return nx, ny


def make_patch(kind, seed, size, steps, log):
    n = size
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n]
    noise = _fbm((n, n), seed + 11, octaves=4, base=3)
    if kind == "belt":
        # fold-and-thrust stripes along y, spacing 9-18 km, wandering on the noise.
        # The stripes are not a ruled grating: their phase drifts on a low
        # noise that varies mostly ALONG strike (ridges step and plunge, the
        # en-echelon habit of real folds), their amplitude pinches and swells
        # along strike, and the whole belt is highest in the middle of the
        # patch and tapers to its margins.
        spacing_km = float(rng.uniform(9.0, 18.0))
        jit = _fbm((n, n), seed + 21, octaves=3, base=2)
        phase = 2 * np.pi * (x * KM_PER_TEXEL / spacing_km) + (noise - 0.5) * 4.0 + (jit - 0.5) * 7.0
        stripes = 0.5 + 0.5 * np.cos(phase)
        swell = 0.45 + 0.55 * _fbm((n, n), seed + 33, octaves=3, base=3)
        envelope = 0.35 + 0.65 * (0.5 - 0.5 * np.cos(2 * np.pi * x / n)) ** 0.8
        U = (0.0015 + 0.0030 * stripes ** 1.6 * swell) * envelope * (0.7 + 0.6 * noise)   # m/yr
        K = 2.5e-5 * (0.6 + 0.8 * _fbm((n, n), seed + 5, 3, 2))
        D = 0.03
    elif kind == "plateau":
        U = 0.0012 * (0.85 + 0.3 * noise)
        K = 1.2e-5 * (0.6 + 0.8 * _fbm((n, n), seed + 5, 3, 2))
        D = 0.02
    else:  # lowland
        U = 0.0004 * (0.7 + 0.6 * noise)
        K = 4e-5 * (0.6 + 0.8 * _fbm((n, n), seed + 5, 3, 2))
        D = 0.08
    # outlets: a sparse periodic set of base-level cells so the whole patch
    # drains and wraps. Two through-going valleys per axis, wandering.
    outlet = np.zeros((n, n), bool)
    for k in range(2):
        cx = int((k + 0.5) * n / 2 + (noise[0, :] .mean() - 0.5) * 20)
        wander = ((_fbm((n, n), seed + 31 + k, 3, 2)[:, 0] - 0.5) * n * 0.12).astype(int)
        for yy in range(n):
            outlet[yy, (cx + wander[yy]) % n] = True
        cy = int((k + 0.5) * n / 2)
        wander2 = ((_fbm((n, n), seed + 41 + k, 3, 2)[0, :] - 0.5) * n * 0.12).astype(int)
        for xx in range(n):
            outlet[(cy + wander2[xx]) % n, xx] = True
    if kind == "belt":
        # a belt's rivers leave ACROSS strike through two wandering transverse
        # trunks, plus one strike valley running between the ridges
        outlet[:] = False
        for k in range(2):
            cy = int((k + 0.5) * n / 2)
            wander2 = ((_fbm((n, n), seed + 41 + k, 3, 2)[0, :] - 0.5) * n * 0.18).astype(int)
            for xx in range(n):
                outlet[(cy + wander2[xx]) % n, xx] = True
        cx = int(rng.uniform(0.2, 0.8) * n)
        wander3 = ((_fbm((n, n), seed + 61, 3, 2)[:, 0] - 0.5) * n * 0.06).astype(int)
        for yy in range(n):
            outlet[yy, (cx + wander3[yy]) % n] = True
    dt = 20000.0  # years per step; a few hundred steps is a few Myr, enough for steady state at these K
    h = erode(U, K, D, outlet, steps, dt, seed, log=log)
    return h, {"kind": kind, "seed": seed, "spacing_km": (spacing_km if kind == "belt" else None),
               "relief_m": float(h.max() - h.min()), "mean_m": float(h.mean())}


def encode(h, out_png):
    from PIL import Image
    hn = (h - h.min()) / max(1e-6, (h.max() - h.min()))
    h16 = np.round(hn * 65535).astype(np.uint32)
    nx, ny = _normal(h)
    # normal components scaled: a 45-degree slope at 500 m/texel is 1.0
    nxq = np.clip(nx * 0.5 + 0.5, 0, 1); nyq = np.clip(ny * 0.5 + 0.5, 0, 1)
    rgba = np.stack([(h16 >> 8).astype(np.uint8), (h16 & 255).astype(np.uint8),
                     np.round(nxq * 255).astype(np.uint8), np.round(nyq * 255).astype(np.uint8)], -1)
    Image.fromarray(rgba, "RGBA").save(out_png, "PNG", optimize=True)
    return rgba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--size", type=int, default=PATCH)
    ap.add_argument("--steps", type=int, default=160)
    ap.add_argument("--only", default=None, help="kind:seed, e.g. belt:1")
    ap.add_argument("--assemble", action="store_true", help="just pack build/atlas/*.png into web/atlas.png")
    a = ap.parse_args()
    if a.assemble:
        assemble(json.load(open(os.path.join(OUT, "atlas.json")))["patch"]); return
    size = 128 if a.quick else a.size
    steps = 40 if a.quick else a.steps
    kinds = [("belt", 1), ("belt", 2), ("belt", 3), ("belt", 4), ("belt", 5), ("belt", 6),
             ("plateau", 1), ("plateau", 2), ("plateau", 3),
             ("lowland", 1), ("lowland", 2), ("lowland", 3)]
    if a.only:
        k, sd = a.only.split(":"); kinds = [(k, int(sd))]
    os.makedirs(OUT, exist_ok=True)
    meta = []
    for kind, seed in kinds:
        print("%s %d  (%d px, %d steps)" % (kind, seed, size, steps), flush=True)
        h, info = make_patch(kind, seed, size, steps, lambda m: print(m, flush=True))
        name = "%s_%02d.png" % (kind, seed)
        encode(h, os.path.join(OUT, name))
        np.save(os.path.join(OUT, name.replace(".png", ".npy")), h.astype(np.float32))
        info["file"] = name; meta.append(info)
        print("  -> %s  relief %.0f m" % (name, info["relief_m"]), flush=True)
    json.dump({"patch": size, "dx_m": DX, "patches": meta}, open(os.path.join(OUT, "atlas.json"), "w"), indent=1)
    print("atlas: %d patches in %s" % (len(meta), OUT))
    if not a.only:
        assemble(size)


def assemble(size):
    """Pack the patches into the 4x4 sheet the shader binds (web/atlas.png):
    cells 0-5 belts, 6-8 plateaus, 9-11 lowlands, in the order the shader's
    atlasTex() expects (cell = column + 4*row). PNG, lossless: the height is
    16-bit across two channels and any lossy codec would terrace it."""
    from PIL import Image
    meta = json.load(open(os.path.join(OUT, "atlas.json")))
    sheet = np.zeros((size * 4, size * 4, 4), np.uint8)
    cells = []
    for k, p in enumerate(meta["patches"][:16]):
        im = np.asarray(Image.open(os.path.join(OUT, p["file"])).convert("RGBA"))
        r, c = k // 4, k % 4
        sheet[r * size:(r + 1) * size, c * size:(c + 1) * size] = im
        cells.append({"cell": k, "kind": p["kind"], "seed": p["seed"], "relief_m": round(p["relief_m"])})
    out = os.path.join(WEB, "atlas.png")
    Image.fromarray(sheet, "RGBA").save(out, "PNG", optimize=True)
    json.dump({"patch": size, "dx_m": DX, "km_across": size * DX / 1000.0, "cells": cells},
              open(os.path.join(WEB, "atlas.json"), "w"), indent=1)
    print("atlas sheet: %s, %d cells, %.1f MB" % (out, len(cells), os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
