"""Bake `*_q.webp` -- FOLD COORDINATES for the mountain belts (WP-10, plan B3b).

WHY A POTENTIAL. The atlas patches carry real eroded ridge-and-valley, but
laying a striped patch over a belt by rotating it to the local strike fails
in the way every rotated-texture-bomb does: a patch rotated about its cell's
centre cannot follow a belt that bends (a strike change of 20 degrees 250 km
from the centre moves the stripes by six spacings), and neighbouring cells
with different rotations meet as a quilt. The sea floor never had this
problem, because its fabric is keyed to a baked SCALAR -- the companded age --
whose gradient IS the direction, so every periodic term is continuous by
construction. This bakes the land equivalent: two potentials per keyframe,

    phi   across strike, one unit per PATCH_KM of ground
    psi   along strike, one unit per PATCH_KM of ground

fitted by least squares so that grad(phi) follows the unit vector across the
fold axis and grad(psi) the axis itself, weighted by the shortening gate, on
the equirect grid of the `_t` field with the cos(lat) metric. Sampling the
belt patch at (phi, psi) then puts its ridges along strike everywhere, bends
them with the belt, and needs no cells, no rotation and no seams. Where the
strike field is not integrable (a belt that curls) the fit spreads the error
as a mild stretch, which is what real folds do at a bend.

THE SIGN. A fold axis is a line, so the across vector is defined up to sign,
and a potential needs one sign field. It is chosen by region growing from the
most shortened cell of each belt, each cell taking the sign that agrees with
the neighbour it was reached from; a belt with a genuine 180-degree twist gets
a fold in phi along one line, which the patch's own variation hides.

CHANNELS (RGBA, lossless WebP -- a sawtooth would seam and a lossy codec would
terrace): R,G = phi and B,A = psi, each 16-bit over +-Q_RANGE units.

    python3 build_foldphase.py            # all keyframes with a _t field
    python3 build_foldphase.py 0 300      # just these ages
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
PATCH_KM = 256.0                 # must match ATLAS_KM in the shader
LAMBDA = PATCH_KM / 6371.0       # one unit of phi per this many radians
Q_RANGE = 64.0                   # units; +-64 patches is 16,000 km, and 16 bits still resolve half a kilometre
GATE_LO, GATE_HI = 0.10, 0.40    # the shader's atlasGate on the shortening byte


def _gate(r):
    t = np.clip((r - GATE_LO) / (GATE_HI - GATE_LO), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _consistent_sign(vx, vy, w):
    """Flip vectors so that neighbours agree, growing from the strongest cell
    of every connected gated region. Returns the sign array (+-1)."""
    h, wd = vx.shape
    sign = np.zeros((h, wd), np.int8)
    active = w > 0.02
    from collections import deque
    order = np.argsort(-w, axis=None)
    for flat in order:
        i, j = divmod(int(flat), wd)
        if not active[i, j] or sign[i, j] != 0:
            continue
        sign[i, j] = 1
        dq = deque([(i, j)])
        while dq:
            ci, cj = dq.popleft()
            s0 = sign[ci, cj]
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = ci + di, (cj + dj) % wd
                if ni < 0 or ni >= h or not active[ni, nj] or sign[ni, nj] != 0:
                    continue
                d = vx[ci, cj] * vx[ni, nj] + vy[ci, cj] * vy[ni, nj]
                sign[ni, nj] = s0 if d >= 0 else -s0
                dq.append((ni, nj))
    sign[sign == 0] = 1
    return sign.astype(np.float64)


def _solve(gx, gy, w, lat):
    """Weighted least squares grad(f) = (gx, gy) [per radian, east/north] on an
    equirect grid, periodic in longitude, Neumann in latitude. Minimises
    sum over edges of  w_e * (df_e - g_e)^2  with w_e the gate on the edge plus
    a small floor, and returns f.

    THE SOLVE. lsqr on this system hit its 3000-iteration cap at 75 s a
    keyframe -- the discrete Poisson problem at 512x256 is far too
    ill-conditioned for an unpreconditioned Krylov method. Dropping the weights
    from the operator and masking only the target (a plain Laplacian, solved
    exactly by FFT) is fast but WRONG: a gated strip with an along-strike target
    has curl all along its two sides, and the projection onto gradient fields
    throws most of that amplitude away -- psi over the Zagros came out at a
    quarter of its length, i.e. the atlas ridges stretched four times.
    So: conjugate gradients on the weighted normal equations, preconditioned
    by that same exact FFT solve of the unit-weight Laplacian. The weights lie
    in [EPS, 1+EPS], so the preconditioned condition number is about 1/EPS and
    CG converges in a few dozen iterations of a few milliseconds each."""
    from scipy.fft import dct, idct
    from scipy.sparse.linalg import LinearOperator, cg
    h, wd = gx.shape
    n = h * wd
    dlon = 2 * np.pi / wd
    dlat = np.pi / h
    cl = np.maximum(np.cos(lat), 0.15)
    EPS = 0.02
    # east edges (i, j) -> (i, j+1), periodic; north edges (i, j) -> (i+1, j)
    te = gx * cl * dlon                                   # target f[i,j+1] - f[i,j]
    we = 0.5 * (w + np.roll(w, -1, axis=1)) + EPS
    tn = -gy[:-1] * dlat                                  # row index grows SOUTH
    wn = 0.5 * (w[:-1] + w[1:]) + EPS

    def A_T(de, dn):
        out = np.roll(de, 1, axis=1) - de
        out[1:] += dn
        out[:-1] -= dn
        return out

    def op(f):
        f = f.reshape(h, wd)
        de = (np.roll(f, -1, axis=1) - f) * we
        dn = (f[1:] - f[:-1]) * wn
        return A_T(de, dn).ravel()

    kx = 2.0 - 2.0 * np.cos(2.0 * np.pi * np.arange(wd) / wd)
    ky = 2.0 - 2.0 * np.cos(np.pi * np.arange(h) / h)
    lam = ky[:, None] + kx[None, :]
    lam[0, 0] = 1.0

    def prec(d):
        D = np.fft.fft(dct(d.reshape(h, wd), type=2, axis=0, norm="ortho"), axis=1)
        F = D / lam
        F[0, 0] = 0.0
        return idct(np.real(np.fft.ifft(F, axis=1)), type=2, axis=0, norm="ortho").ravel()

    rhs = A_T(we * te, wn * tn).ravel()
    rhs -= rhs.mean()                                     # range of A^T is mean-free
    f, info = cg(LinearOperator((n, n), matvec=op, dtype=np.float64), rhs,
                 M=LinearOperator((n, n), matvec=prec, dtype=np.float64),
                 rtol=1e-6, maxiter=400)
    if info != 0:
        print("  warning: cg did not converge (info=%d)" % info)
    f = f.reshape(h, wd)
    f -= np.average(f.ravel(), weights=w.ravel() + 1e-6)
    return f


def bake(age, quiet=False):
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    fr = next((f for f in manifest if f["age"] == age), None)
    if fr is None:
        return None
    base = fr["e"][:fr["e"].rfind("_e")]
    tpath = os.path.join(FIELDS, base + "_t.webp")
    if not os.path.exists(tpath):
        return None
    t = np.asarray(Image.open(tpath).convert("RGB")).astype(np.float64) / 255.0
    h, wd = t.shape[:2]
    lat = np.radians(90.0 - (np.arange(h) + 0.5) / h * 180.0)[:, None] * np.ones((1, wd))
    w = _gate(t[..., 0])
    c2, s2 = t[..., 1] * 2 - 1, t[..., 2] * 2 - 1
    th = 0.5 * np.arctan2(s2, c2)                 # fold axis angle from east
    # blur the axis a little (in the double-angle domain, which has no wrap)
    from scipy.ndimage import gaussian_filter
    c2b = gaussian_filter(np.cos(2 * th) * w, 1.0, mode=("nearest", "wrap"))
    s2b = gaussian_filter(np.sin(2 * th) * w, 1.0, mode=("nearest", "wrap"))
    th = 0.5 * np.arctan2(s2b, c2b)
    sx, sy = np.cos(th), np.sin(th)               # along strike (east, north)
    ax, ay = -sy, sx                              # across strike
    sg = _consistent_sign(ax, ay, w)
    phi = _solve(sg * ax / LAMBDA, sg * ay / LAMBDA, w, lat)
    sg2 = _consistent_sign(sx, sy, w)
    psi = _solve(sg2 * sx / LAMBDA, sg2 * sy / LAMBDA, w, lat)
    out = _encode(phi, psi)
    name = base + "_q.webp"
    # Lossless WebP is 31% smaller than an optimised PNG of the same bytes
    # (214 KB against 311 KB at the present day). `exact` matters: the low byte
    # of psi rides in alpha, and without it the encoder is free to zero the RGB
    # of any pixel whose alpha happens to be 0 -- which corrupts phi there.
    Image.fromarray(out, "RGBA").save(os.path.join(FIELDS, name), "WEBP",
                                      lossless=True, quality=100, method=6, exact=True)
    if not quiet:
        span = lambda a: float(np.percentile(a[w > 0.3], 99) - np.percentile(a[w > 0.3], 1)) if (w > 0.3).any() else 0.0
        print("  %s  gated %.1f%%  phi span %.1f  psi span %.1f  -> %s" % (
            age, 100 * (w > 0.3).mean(), span(phi), span(psi), name))
    return name


def _encode(phi, psi):
    def q16(a):
        v = np.clip((a + Q_RANGE) / (2 * Q_RANGE), 0, 1) * 65535.0
        v = np.round(v).astype(np.uint32)
        return (v >> 8).astype(np.uint8), (v & 255).astype(np.uint8)
    r, g = q16(phi); b, a = q16(psi)
    return np.stack([r, g, b, a], -1)


def main():
    manifest = json.load(open(os.path.join(FIELDS, "manifest.json")))
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    ages = [int(x) for x in args] or [f["age"] for f in manifest]
    procs = 3 if "-j" in sys.argv else 1
    if procs > 1:
        from multiprocessing import Pool
        with Pool(procs) as pool:
            done = [r for r in pool.map(bake, ages) if r]
    else:
        done = [r for r in (bake(a) for a in ages) if r]
    print("fold coordinates: %d keyframes -> %s" % (len(done), FIELDS))


if __name__ == "__main__":
    main()
