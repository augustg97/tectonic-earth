"""A landscape-evolution model for the schematic mountain belts (the mountain
round, 2026-09, second pass).

WHY A MODEL AND NOT MORE TEXTURE. The per-pixel erosion relief (FRAG
eroRelief) dissects a smooth envelope, but it cannot reshape it: the belt's
cross-section stays the symmetric tent Scotese drew, and the future's
collision zones stay the smooth uplift they were built as. Real ranges owe
their form -- drainage basins, asymmetric divides, spurs, massifs, deep
transverse valleys -- to fluvial erosion working against uplift, at every
scale. So this erodes the envelope itself:

    dh/dt = U - K (A * rain)^m S + kappa laplacian(h)

stream-power incision (n = 1, implicit down the receiver tree; lem.c), rain
from the keyframe's own `_r`, so the wet flank of a range is cut harder than
the dry one and the divide migrates -- asymmetry from climate, not from a
rule. U is not an uplift history (none is known): it NUDGES the belt's
low-pass (~50 km) back to the source envelope, so where a range stands, how
wide and how high is still the PaleoDEM's, and only the form below that scale
is erosion's.

WHERE. Only on ground the source drew schematically: the relief deficit
(relief_deficit.py) held high across the keyframe's neighbours in time, so a
Cenozoic frame whose neighbours carry real topography is left alone.

    import lem; out, state = lem.erode(Z, weight, rain, state=None)
"""
import ctypes
import hashlib
import os
import subprocess

import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "lem.c")
CACHE = os.path.join(HERE, "cache")

R_EARTH = 6.371e6

# ---- parameters (see the calibration notes in MODEL-GAPS, the mountain round) ----
M_EXP = 0.45            # stream-power area exponent (concavity m/n with n = 1)
K_ERODE = 0.35          # erodibility in the pseudo-time the loop runs in
KAPPA = 0.06            # hillslope diffusion per iteration, as kappa dt / dy^2
NUDGE_SIG_PX = 5.0      # the envelope scale the nudging holds (5 px ~ 50 km)
NUDGE_GAIN = 0.50       # fraction of the low-pass error restored per iteration
EPS = 1e-4              # flood epsilon, metres per metre
# The threshold slope, on a ~10 km grid: the steepest regional gradients of the
# real Himalaya and Andes at this sampling are ~5 km over 20 km, 0.25.
S_CRIT = 0.18
RAIN_FLOOR = 0.12       # a desert still drains


def _lib():
    os.makedirs(CACHE, exist_ok=True)
    tag = hashlib.sha1(open(SRC, "rb").read()).hexdigest()[:12]
    so = os.path.join(CACHE, "liblem_%s.dylib" % tag)
    if not os.path.exists(so):
        subprocess.check_call(["cc", "-O3", "-ffast-math", "-shared", "-fPIC", "-o", so, SRC])
    L = ctypes.CDLL(so)
    f32 = np.ctypeslib.ndpointer(np.float32, flags="C_CONTIGUOUS")
    i32 = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    u8 = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
    L.lem_route.argtypes = [ctypes.c_int, ctypes.c_int, f32, u8, f32, ctypes.c_float, ctypes.c_float,
                            f32, i32, i32, f32]
    L.lem_route.restype = ctypes.c_int
    L.lem_area.argtypes = [ctypes.c_int64, i32, i32, f32, f32]
    L.lem_incise.argtypes = [ctypes.c_int64, i32, i32, f32, f32, f32, ctypes.c_float, ctypes.c_float, f32, f32]
    L.lem_diffuse.argtypes = [ctypes.c_int, ctypes.c_int, u8, f32, ctypes.c_float, ctypes.c_float, f32, f32]
    L.lem_limit.argtypes = [ctypes.c_int64, i32, i32, f32, ctypes.c_float, f32]
    L.lem_steady.argtypes = [ctypes.c_int64, i32, i32, f32, f32, f32, ctypes.c_float, ctypes.c_float, f32]
    return L


_L = None


def lib():
    global _L
    if _L is None:
        _L = _lib()
    return _L


def geometry(H, W):
    """Per-row east-west cell width and the north-south one, metres."""
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    dy = np.float32(np.pi * R_EARTH / H)
    dx = (2.0 * np.pi * R_EARTH / W * np.maximum(np.cos(np.radians(lat)), 0.12)).astype(np.float32)
    return lat, dx, dy


def _g(a, s):
    return gaussian_filter(a, s, mode=("nearest", "wrap"))


def erode(Z, weight, rain, iters=600, state=None, seed_noise=None, K=None, verbose=False,
          lp_sig=25.0, u_gain=0.02, cycles=5, skew=None, u_noise=None, k_noise=None,
          skew_amp=0.45, un_amp=0.35, kn_amp=0.5):
    """Erode the belts of one keyframe toward a steady state under uplift.

    The uplift is not known, so it is solved for. It starts as the belt's
    REGIONAL height (the envelope low-passed over lp_sig pixels, ~250 km, so
    it is broad and flat-topped rather than the source's tent) over the belt's
    footprint, varied along the belt by u_noise (thrust sheets and massifs
    rise at different rates) and skewed across it by `skew` (+1 on the flank
    facing the foreland: rock uplift concentrates over the frontal ramps, so
    the divide moves toward the front and the belt becomes a wedge). The
    landscape is eroded under it toward steady state, and the uplift is then
    corrected multiplicatively wherever the eroded belt's regional mean sits
    off the source's -- so where a range stands, how wide and how high over a
    few hundred kilometres stays the source's, and its form is erosion's
    (Cordonnier et al. 2016 generate terrain the same way, from an uplift map
    under stream power). k_noise varies erodibility (lithology).

    Returns (Z_out, h_eroded).
    """
    L = lib()
    H, W = Z.shape
    lat, dx, dy = geometry(H, W)
    Z = np.ascontiguousarray(Z, np.float32)
    land = Z > 0.0
    want = (weight > 0.02) & land
    if not want.any():
        return Z.copy(), Z.copy()
    dom = binary_dilation(want, iterations=8) & land
    active = np.ascontiguousarray(dom.astype(np.uint8))
    target = _g(Z, lp_sig).astype(np.float32)
    ring = dom & ~want
    base = np.float32(np.percentile(Z[ring], 50) if ring.any() else 200.0)
    env = _g(Z, 3.0)
    foot = np.clip((env - base - 150.0) / 550.0, 0.0, 1.0)
    foot = foot * foot * (3.0 - 2.0 * foot)
    U = (np.maximum(target - base, 0.0) * foot).astype(np.float32)
    if u_noise is not None:
        U *= np.clip(1.0 + un_amp * u_noise, 0.2, 2.0)
    if skew is not None:
        U *= np.clip(1.0 + skew_amp * skew, 0.2, 2.0)
    U = (U * np.float32(u_gain) * want).astype(np.float32)
    if state is not None:
        h = np.where(dom, state, Z).astype(np.float32)
    else:
        h = Z.copy() if seed_noise is None else np.where(dom, Z + seed_noise, Z).astype(np.float32)
    h = np.ascontiguousarray(h)
    cellw = np.ascontiguousarray(((dx[:, None] * dy) * np.maximum(rain, RAIN_FLOOR)).astype(np.float32))
    K0 = K if K is not None else K_ERODE
    Kf = np.full((H, W), K0, np.float32)
    if k_noise is not None:
        Kf *= np.clip(1.0 + kn_amp * k_noise, 0.25, 2.5).astype(np.float32)
    Kf = np.ascontiguousarray(Kf)
    hf = np.empty_like(h); rec = np.empty((H, W), np.int32); order = np.empty(H * W, np.int32)
    dist = np.empty_like(h); A = np.zeros_like(h); tmp = np.empty_like(h)
    kdt = np.float32(KAPPA * float(dy) ** 2)
    per = max(1, iters // cycles)
    for it in range(iters):
        if it > 0 and it % per == 0:
            hl = _g(h, lp_sig)
            corr = np.clip((target - base) / np.maximum(hl - base, 50.0), 0.6, 1.6)
            U = np.ascontiguousarray((U * np.where(want, corr, 1.0)).astype(np.float32))
        no = L.lem_route(H, W, h, active, dx, dy, EPS, hf, rec, order, dist)
        if no < 0:
            raise MemoryError("lem_route")
        A.fill(0.0)
        L.lem_area(no, order, rec, cellw, A)
        L.lem_incise(no, order, rec, dist, A, Kf, M_EXP, 1.0, U, h)
        L.lem_limit(no, order, rec, dist, np.float32(S_CRIT), h)
        L.lem_diffuse(H, W, active, dx, dy, kdt, h, tmp)
        h, tmp = tmp, h
        if verbose and (it % 100 == 0 or it == iters - 1):
            m = want
            hp = h - _g(h, 2.5)
            print("    it %4d  hp rms %4.0f m  lp err %4.0f m  mean %4.0f (target %4.0f)  max %5.0f (src %5.0f)"
                  % (it, float(np.std(hp[m])), float(np.abs(target - _g(h, lp_sig))[m].mean()),
                     float(h[m].mean()), float(Z[m].mean()), float(h[m].max()), float(Z[m].max())), flush=True)
    w = np.clip(weight, 0.0, 1.0)
    out = (Z + w * (h - Z)).astype(np.float32)
    out = np.where(land, np.maximum(out, 1.0), Z)       # erosion never makes new sea
    return out, h


def steady(Z, weight, rain, state=None, seed_noise=None, sweeps=24, cycles=5, lp_sig=25.0,
           skew=None, u_noise=None, k_noise=None, skew_amp=0.45, un_amp=0.35, kn_amp=0.5,
           relax=0.5, diff_steps=2, verbose=False):
    """The belts of one keyframe at erosional steady state (see lem_steady).

    E = U/K, the uplift-to-erodibility ratio, is the only field: it is the
    belt's regional height (broad and flat-topped, not the source's tent) over
    its footprint, varied along the belt (u_noise: massifs and saddles; k_noise:
    lithology) and skewed toward the thrust front (skew, +1 on the flank facing
    the foreland). Each sweep routes the drainage on the current surface,
    solves the steady state on that network and relaxes toward it, so the
    network and the topography settle together; each cycle rescales E so the
    eroded belt's regional mean (lp_sig pixels) matches the source's.
    Returns (Z_out, h).
    """
    L = lib()
    H, W = Z.shape
    lat, dx, dy = geometry(H, W)
    Z = np.ascontiguousarray(Z, np.float32)
    land = Z > 0.0
    want = (weight > 0.02) & land
    if not want.any():
        return Z.copy(), Z.copy()
    dom = binary_dilation(want, iterations=8) & land
    active = np.ascontiguousarray(dom.astype(np.uint8))
    target = _g(Z, lp_sig).astype(np.float32)
    ring = dom & ~want
    base = np.float32(np.percentile(Z[ring], 50) if ring.any() else 200.0)
    env = _g(Z, 3.0)
    foot = np.clip((env - base - 150.0) / 550.0, 0.0, 1.0)
    foot = foot * foot * (3.0 - 2.0 * foot)
    E = (np.maximum(target - base, 0.0) * foot).astype(np.float32)
    if u_noise is not None:
        E *= np.clip(1.0 + un_amp * u_noise, 0.2, 2.0)
    if k_noise is not None:
        E /= np.clip(1.0 + kn_amp * k_noise, 0.25, 2.5)
    if skew is not None:
        E *= np.clip(1.0 + skew_amp * skew, 0.2, 2.0)
    E = (E * dom).astype(np.float32)
    E *= np.float32(0.4)                    # a first guess; the cycles set it
    E0 = E.copy(); Ecum = np.ones_like(E)
    from scipy.ndimage import label as _label
    comp, ncomp = _label(want)
    if state is not None:
        h = np.where(dom, state, Z).astype(np.float32)
    else:
        h = Z.copy() if seed_noise is None else np.where(dom, Z + seed_noise, Z).astype(np.float32)
    h = np.ascontiguousarray(h)
    cellw = np.ascontiguousarray(((dx[:, None] * dy) * np.maximum(rain, RAIN_FLOOR)).astype(np.float32))
    hf = np.empty_like(h); rec = np.empty((H, W), np.int32); order = np.empty(H * W, np.int32)
    dist = np.empty_like(h); A = np.zeros_like(h); tmp = np.empty_like(h)
    kdt = np.float32(KAPPA * float(dy) ** 2)
    for cyc in range(cycles):
        for sw in range(sweeps):
            no = L.lem_route(H, W, h, active, dx, dy, EPS, hf, rec, order, dist)
            A.fill(0.0)
            L.lem_area(no, order, rec, cellw, A)
            z = h.copy()
            L.lem_steady(no, order, rec, dist, A, np.ascontiguousarray(E), M_EXP, np.float32(S_CRIT), z)
            h = np.ascontiguousarray(np.where(dom, (1.0 - relax) * h + relax * z, Z).astype(np.float32))
            # hillslope diffusion rounds the crests; kept to the last sweep of a
            # cycle, because applied every sweep it smoothed over ~50 km and the
            # belts came out as blobs (the control against today's ranges)
            for _k in range(diff_steps if sw == sweeps - 1 else 0):
                L.lem_diffuse(H, W, active, dx, dy, kdt, h, tmp)
                h, tmp = tmp, h
        hl = _g(h, lp_sig)
        # ONE SCALAR PER BELT, not a factor per place: the steady state is linear
        # in E on a fixed network, so matching each connected belt's mean needs
        # one number, and a per-place factor compounded x16 wherever a big river
        # held the surface near base level (14.8 km summits on 1.2 km ground).
        corr = np.ones_like(h)
        for k in range(1, ncomp + 1):
            mk = comp == k
            num = float(Z[mk].mean()) - base
            den = max(float(h[mk].mean()) - base, 30.0)
            corr[mk] = np.clip(num / den, 0.5, 2.0)
        # ...and a mild local correction toward the regional envelope, bounded
        # in total so no place can run away
        loc = np.clip((target - base) / np.maximum(hl - base, 30.0), 0.8, 1.25)
        corr *= np.where(want, loc, 1.0)
        corr = _g(corr.astype(np.float32), 3.0)
        if verbose:
            m = want
            hp = h - _g(h, 2.5)
            print("    cycle %d  hp rms %4.0f m  lp err %4.0f m  mean %4.0f (target %4.0f)  max %5.0f (src %5.0f)"
                  % (cyc, float(np.std(hp[m])), float(np.abs(target - hl)[m].mean()),
                     float(h[m].mean()), float(Z[m].mean()), float(h[m].max()), float(Z[m].max())), flush=True)
        if cyc < cycles - 1:
            Ecum = np.clip(Ecum * corr, 0.25, 4.0)
            E = np.ascontiguousarray((E0 * Ecum).astype(np.float32))
    w = np.clip(weight, 0.0, 1.0)
    out = (Z + w * (h - Z)).astype(np.float32)
    out = np.where(land, np.maximum(out, 1.0), Z)
    return out, h
