"""Bake `*_v.webp` -- how far the crust under each pixel moves to the next keyframe.

WHAT IT IS FOR. The app interpolates terrain with
`mix(decElev(elevA), decElev(elevB), mixf)`, a cross-fade between two stationary
images. Measured (Deep Research/modeling/audit_terrain_motion.py), crust moves a
median of 14-42 texels of the 4096 grid per 5 Myr step and up to 65, so that
cross-fade is a double exposure: every mountain front, coastline and trench
splits into two half-amplitude copies mid-interval and snaps at the keyframe.
Continents do not slide, they dissolve from one place to another.

With this field the shader can carry each keyframe toward the other so the same
piece of crust lines up in both taps before they are blended:

    z = mix(elevA at uv - mixf*D,  elevB at uv + (1-mixf)*D,  mixf)

At mixf 0 and 1 that is exactly today's behaviour, so the keyframes themselves
cannot move -- which is also the gate on the whole change.

D IS STORED IN A LOCAL TANGENT FRAME, NOT AS A uv OFFSET, and that is the one
design decision here worth defending. A uv offset is what the shader wants, so
storing one is the obvious move; it is also unusable. Measured over nine ages,
`dlon` reaches 180 degrees and the 99th percentile poleward of 75 degrees is
148-163 -- not because anything moves that far, but because near a pole a small
motion spans many degrees of longitude. In the tangent frame the same field is
tame: max 6.11 deg per 5 Myr, or 680 km, or 13.6 cm/yr, which is India at its
fastest and a sane ceiling for a plate. So east/north components are stored and
the shader divides by cos(lat) to get its uv offset -- moving the singularity to
where it is meaningful and correct instead of clipping it out of the data.

CHANNELS (RGB, no alpha -- see the note on premultiplication at _encode):
    R  east  displacement, degrees of great circle, linear over +/-V_RANGE
    G  north displacement, same
    B  tear: divergence of the displacement field, centred at 128.
       ABOVE 128 the crust is separating -- a spreading ridge, and the gap the
       warp opens there is real new ocean floor. BELOW 128 it is converging, and
       THAT IS THE SHORTENING SIGNAL H4 needs: the overlap is the collision.
       WP-07 found the same quantity in the future branch, where 12.8 Mkm2 of
       land-on-land overlap is computed and then deleted by an np.maximum.

COVERAGE. PALEOMAP's polygons are present-day crust, so at earlier ages they
cover only 29-36% of the globe -- but 89-96% of land and 83-90% of relief, the
hole being subducted ocean. `plate_field` documents the measurement and the
Laplace fill that closes it. Uncovered cells are solved, not guessed: covered
cells are Dirichlet boundaries and the interior relaxes, which is a fair model
of a spreading basin whose velocity really does grade between its two margins.

RANGE: ages 0..995, which is every past keyframe. The future series (negative
ages) is not built from PALEOMAP rotations at all -- it is a rigid warp of the
present DEM by plate GROUP -- so its displacement has to come from
`build_fields._packed_targets` instead. Not done here; the app falls back to a
plain cross-fade across those intervals, exactly as today.

    ../venv/bin/python build_displacement.py            # all past keyframes
    ../venv/bin/python build_displacement.py 200 300    # just these
    ../venv/bin/python build_displacement.py --selftest
"""
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter

import paleo_tracks as PT
import plate_field as PF

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "fields")

# 1024x512. Halving it looks defensible on the average -- p50 error 0.2 km, p99
# 1.9 -- and is not, because the MAX goes to 42.6 km. The displacement field is
# smooth inside a plate and DISCONTINUOUS across a boundary, so downsampling
# averages across the discontinuity and puts its whole error exactly where the
# collisions are. Four texels of error at a suture is the artefact this is
# meant to remove.
VW, VH = 1024, 512
STEP = 5.0

# Degrees of great circle per 5 Myr at full scale. SCANNED, not guessed: the
# maximum over all 200 past keyframes is 10.27 deg -- 1,143 km, 22.9 cm/yr, at
# 85 Ma, which is the Cretaceous Pacific. A nine-age sample had suggested 6.11
# and an 8.0 ceiling built on it would have clipped the fastest crust in the
# model without saying so. 12.0 leaves real headroom, and _bake counts clipped
# cells so the next surprise cannot be silent either.
V_RANGE = 12.0

# 8-bit over +/-12 deg is 0.094 deg a level, about 10.5 km -- almost exactly one
# elevation texel (9.8 km). That is the residual after removing a 140-410 km
# ghost, it is at the resolution of the grid being warped, and because the
# texture is sampled with LinearFilter the quantisation appears as a continuous
# piecewise-linear ramp rather than as bands. 16-bit would need a packed
# high/low pair, and a packed pair CANNOT be linearly filtered -- interpolating
# a low byte across its wraparound gives garbage -- so it would have to be
# NearestFilter, which trades 10 km of smooth error for hard blocky seams. That
# is the wrong trade.
#
# LOSSLESS, and that was measured too. WebP q98 is a quarter of the size and its
# MAX displacement error is 102 km, ten texels, concentrated exactly where the
# field is discontinuous -- i.e. at plate boundaries, i.e. at the collisions
# this whole exercise exists to draw. p99 21.7 km, also worse than the quantum.
# Lossless costs 48 kB a keyframe against the 508 kB of field textures already
# loaded per keyframe, a 9% increase on something that loads two frames at a
# time, so there is nothing to buy here.

TEAR_RANGE = 6.0        # deg of displacement divergence per deg of arc, full scale


def _tangent_basis(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    e = np.stack([-np.sin(lo), np.cos(lo), np.zeros_like(lo)], -1)
    n = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
    return e, n


def displacement(age, w=VW, h=VH, rot=None):
    """(dE, dN, covered) in degrees of great circle, from `age` to `age+STEP`.

    Sign convention: the app's keyframe A is the YOUNGER of the interpolated
    pair and B the older, with mixf running 0 at A to 1 at B. So the useful
    quantity on keyframe A is where its crust sits at A+5, which is B.
    """
    import pygplates as pg
    if rot is None:
        rot = pg.RotationModel(PT.ROT)
    LON, LAT = PF._grid(w, h)
    flon, flat = LON.ravel(), LAT.ravel()
    V0 = PF.unit(flon, flat)
    ids, cov = PF.plate_raster(age, w, h)

    V1 = V0.copy()
    cflat = cov.ravel()
    for pid in np.unique(ids[cov]):
        m = (ids == pid).ravel() & cflat
        ax, ang = PF.euler(rot, int(pid), age + STEP, age)
        if ax is None:
            continue
        V1[m] = PF.rodrigues(V0[m], ax, ang)

    dot = np.clip((V0 * V1).sum(-1), -1.0, 1.0)
    gc = np.degrees(np.arccos(dot))                 # true angular displacement
    tang = V1 - dot[:, None] * V0                   # tangential component at V0
    dirn = tang / np.maximum(np.linalg.norm(tang, axis=-1, keepdims=True), 1e-15)
    e, n = _tangent_basis(flon, flat)
    dE = (gc * (dirn * e).sum(-1)).reshape(LON.shape)
    dN = (gc * (dirn * n).sum(-1)).reshape(LON.shape)
    dE[~cov] = 0.0
    dN[~cov] = 0.0
    return dE, dN, cov


def _smooth_wrap(a, size):
    """Box filter that WRAPS in longitude and clamps at the poles.

    Longitude is periodic and this pipeline has forgotten that in three separate
    places already (README on the duplicated meridian, render._smooth padding
    both axes 'edge', future_grid's non-integer harmonic). Latitude must NOT
    wrap -- the poles are real boundaries, not a seam.
    """
    a = uniform_filter(a, size=(1, size), mode="wrap")
    return uniform_filter(a, size=(size, 1), mode="nearest")


def laplace_fill(a, covered, iters=96, size=3, coarsest=32):
    """Relax `a` into ~covered, holding covered cells fixed. Cascadic multigrid.

    Converges to the Laplace solution on the hole, which for a basin between two
    diverging margins is a linear grade between their velocities -- what the
    crust there actually did. A nearest-neighbour fill would be a Voronoi
    tessellation instead, and WP-06 is the record of what Voronoi facets look
    like once a depth law renders them.

    IT MUST BE MULTIGRID, and this was measured rather than assumed. Plain
    Jacobi relaxation on the full grid does not converge here: the holes are
    subducted ocean basins spanning hundreds of cells, diffusion crosses only
    ~sqrt(iters) cells a pass, and at 1024x512 even 480 iterations sat 79 km
    from the converged answer (240 iterations, 160 km; 40, 318 km). Solving
    coarse-to-fine fixes it because at 32x16 the same basin is a few cells wide.
    Each level starts from its parent's answer and only has to add detail.
    """
    out = a.copy()
    if covered.all() or not covered.any():
        return out

    h, w = a.shape
    levels = []
    ch, cw = h, w
    while cw > coarsest:
        ch, cw = ch // 2, cw // 2
        levels.append((ch, cw))
    levels.reverse()                       # coarsest first

    def down(x, m, hh, ww):
        """Area-average to (hh, ww), weighting by the mask so a mostly-empty
        coarse cell is not dragged toward whatever little data it contains."""
        xm = (x * m).reshape(hh, x.shape[0] // hh, ww, x.shape[1] // ww).sum((1, 3))
        mm = m.reshape(hh, m.shape[0] // hh, ww, m.shape[1] // ww).sum((1, 3))
        return np.where(mm > 0, xm / np.maximum(mm, 1e-9), 0.0), mm > 0

    guess = None
    for (hh, ww) in levels + [(h, w)]:
        if (hh, ww) == (h, w):
            cur, curm = a, covered
        else:
            cur, curm = down(a, covered.astype(float), hh, ww)
        if guess is None:
            cur_out = np.where(curm, cur, float(a[covered].mean()))
        else:
            # nearest-neighbour upsample of the parent solution
            fy, fx = hh // guess.shape[0], ww // guess.shape[1]
            cur_out = np.repeat(np.repeat(guess, fy, 0), fx, 1)
            cur_out = np.where(curm, cur, cur_out)
        for _ in range(iters):
            cur_out = _smooth_wrap(cur_out, size)
            cur_out[curm] = cur[curm]
        guess = cur_out
    return guess


def tear(dE, dN, w, h):
    """Divergence of the displacement field, per degree of arc.

    Positive = separating (a ridge, and the gap the warp opens is new crust),
    negative = converging (a collision, and the overlap is the shortening).
    Longitude spacing shrinks as cos(lat), so the east derivative is scaled by
    1/cos(lat) -- without that the whole polar region reads as convergent.
    """
    _LON, LAT = PF._grid(w, h)
    dlon = 360.0 / w
    dlat = 180.0 / h
    coslat = np.maximum(np.cos(np.radians(LAT)), 0.08)
    dEdx = np.gradient(dE, axis=1) / (dlon * coslat)
    dNdy = -np.gradient(dN, axis=0) / dlat        # row 0 is north, so flip
    return dEdx + dNdy


def _encode(dE, dN, tr):
    """RGB uint8. No alpha deliberately.

    A fourth channel would be somewhere to put the coverage mask, and it is not
    worth the risk: a WebP with alpha can be decoded premultiplied, which would
    multiply the displacement in RGB by the coverage in A and destroy the data
    wherever the fill applies -- silently, and only in some browsers. Coverage
    stays a build-time diagnostic. If the shader ever needs it, give it its own
    channel in another texture rather than an alpha here.
    """
    r = np.clip(dE / V_RANGE, -1, 1) * 0.5 + 0.5
    g = np.clip(dN / V_RANGE, -1, 1) * 0.5 + 0.5
    b = np.clip(tr / TEAR_RANGE, -1, 1) * 0.5 + 0.5
    return np.stack([np.round(x * 255.0).astype(np.uint8) for x in (r, g, b)], -1)


def _bake(age, rot, quiet=False):
    t0 = time.time()
    dE, dN, cov = displacement(age, VW, VH, rot)
    clip = int(((np.abs(dE) > V_RANGE) | (np.abs(dN) > V_RANGE)).sum())
    dEf = laplace_fill(dE, cov)
    dNf = laplace_fill(dN, cov)
    tr = tear(dEf, dNf, VW, VH)
    arr = _encode(dEf, dNf, tr)
    name = "phan_%04d_v.webp" % age if age <= 540 else "pre_%04d_v.webp" % age
    path = os.path.join(OUT, name)
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
    kb = os.path.getsize(path) / 1024.0
    if not quiet:
        mx = float(np.hypot(dEf, dNf).max())
        print("  %-22s %5.1f kB  cover %4.1f%%  max %.2f deg (%.0f km)  clip %d  %.1fs"
              % (name, kb, 100 * cov.mean(), mx, mx * 111.32, clip, time.time() - t0))
    return kb, clip


# --------------------------------------------------------------------------

def _selftest():
    import pygplates as pg
    ok = True
    rot = pg.RotationModel(PT.ROT)

    # A zero-length interval must give exactly zero displacement. If it does
    # not, every field carries a DC offset and the warp drifts at mixf=0.
    LON, LAT = PF._grid(64, 32)
    V0 = PF.unit(LON.ravel(), LAT.ravel())
    ax, ang = PF.euler(rot, 101, 100.0, 100.0)
    V1 = PF.rodrigues(V0, ax, ang)
    if float(np.abs(V1 - V0).max()) > 1e-12:
        print("  FAIL zero interval is not the identity")
        ok = False

    # The tangent decomposition must reproduce the great-circle distance it was
    # built from -- otherwise east and north are not orthogonal and the shader
    # will warp along the wrong bearing.
    dE, dN, cov = displacement(200, 128, 64, rot)
    ids, _c = PF.plate_raster(200, 128, 64)
    LON2, LAT2 = PF._grid(128, 64)
    V0 = PF.unit(LON2.ravel(), LAT2.ravel())
    V1 = V0.copy()
    for pid in np.unique(ids[_c]):
        m = (ids == pid).ravel() & _c.ravel()
        a2, an2 = PF.euler(rot, int(pid), 205.0, 200.0)
        if a2 is not None:
            V1[m] = PF.rodrigues(V0[m], a2, an2)
    gc = np.degrees(np.arccos(np.clip((V0 * V1).sum(-1), -1, 1))).reshape(LAT2.shape)
    err = float(np.abs(np.hypot(dE, dN) - gc)[_c].max())
    if err > 1e-6:
        print("  FAIL tangent components do not reproduce the arc: %.3g deg" % err)
        ok = False
    else:
        print("  tangent decomposition vs great-circle: max %.2e deg" % err)

    # The fill must not touch covered cells. Silently overwriting the measured
    # data with the model would be undetectable downstream.
    a = np.random.RandomState(0).rand(64, 128)
    covm = np.random.RandomState(1).rand(64, 128) > 0.5
    f = laplace_fill(a, covm, iters=30)
    if float(np.abs(f[covm] - a[covm]).max()) > 1e-12:
        print("  FAIL laplace_fill modified covered cells")
        ok = False

    # ... and it must actually fill. A no-op that leaves zeros would read as
    # "this crust does not move", which is a plausible-looking wrong answer.
    if not np.isfinite(f).all() or float(np.abs(f[~covm]).max()) < 1e-9:
        print("  FAIL laplace_fill left the hole empty")
        ok = False

    # The smoother must wrap in longitude. A seam here puts a ridge of false
    # divergence down the antimeridian at every age.
    s = np.zeros((8, 16))
    s[4, 0] = 1.0
    sm = _smooth_wrap(s, 3)
    if sm[4, -1] <= 0:
        print("  FAIL _smooth_wrap does not wrap in longitude")
        ok = False

    # ... and must NOT wrap in latitude, or the north pole leaks into the south.
    s2 = np.zeros((8, 16))
    s2[0, 8] = 1.0
    if _smooth_wrap(s2, 3)[-1, 8] > 1e-12:
        print("  FAIL _smooth_wrap wraps in latitude")
        ok = False

    # Encode must round-trip through the byte and keep sign. An inverted sign
    # warps every plate backwards, which looks plausible in a still.
    for v in (-7.5, -1.0, 0.0, 2.5, 7.5):
        z = np.zeros((2, 2))
        px = _encode(np.full((2, 2), v), z, z)[0, 0, 0]
        back = (px / 255.0 * 2.0 - 1.0) * V_RANGE
        if abs(back - v) > V_RANGE / 255.0:
            print("  FAIL encode round-trip %.2f -> %.2f" % (v, back))
            ok = False

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    import pygplates as pg
    rot = pg.RotationModel(PT.ROT)
    ages = [int(a) for a in args] if args else list(range(0, 1000, int(STEP)))
    print("baking %d displacement fields at %dx%d" % (len(ages), VW, VH))
    t0 = time.time()
    tot = clips = 0
    for age in ages:
        kb, c = _bake(age, rot)
        tot += kb
        clips += c
    print("\n  %d fields, %.1f MB total, %.1f min, %d clipped cells"
          % (len(ages), tot / 1024.0, (time.time() - t0) / 60.0, clips))
    if clips:
        print("  RAISE V_RANGE -- displacement is being silently truncated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
