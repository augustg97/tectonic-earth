"""The relief of mountain belts the source drew as envelopes (the mountain round,
second pass, 2026-09). Baked into the elevation field.

WHY. The Palaeozoic and Precambrian belts are smooth symmetric envelopes, and
the future's collision belts are the smooth uplift they were built as. The
first pass grew dissection per pixel on top of them; it could not reshape
them, so the belts still read as symmetric tents and the future's as clumps,
and the per-pixel pattern re-formed as the envelope changed. This replaces the
envelope's own form below ~160 km with an eroded landscape:

  1. THE WEDGE. Each belt's crest moves toward its foreland (the side
     build_foreland.polarity finds: lower, and not ocean), the shift largest at
     the crest and zero at the belt's foot. The footprint and the height stay;
     the foreland flank steepens and the hinterland flank lengthens, which is
     the critical-taper shape of real orogens (a steep thrust front, a long
     gentle back or a plateau). A symmetric tent is an authoring artefact.
  2. THE DRAINAGE. The belt at erosional steady state under uplift (lem.steady:
     stream power, the keyframe's own rainfall, a threshold slope): the uplift
     is the belt's regional height, broad rather than tent-shaped, varied along
     the belt (massifs, saddles) and skewed toward the front; the erodibility
     varies with lithology and with rock bands parallel to the belt
     (strike_bands). This decides where the valleys, divides, spurs and
     basins go -- the ORGANISATION.
  3. THE AMPLITUDE. The eroded surface is split into three bands (wavelengths
     up to ~250 km, the inside of a belt), and each band's amplitude AND
     distribution are matched to what real mountain belts of the same regional
     height carry in the PaleoDEMs built on modern topography (0-30 Ma;
     REAL_BANDS, REAL_Q; --calib re-measures). A steady-state network on a 10 km
     grid makes steep pyramids between broad low valleys, near-Gaussian where
     real relief is heavy-tailed; so the model is trusted for the pattern and
     the Earth for the amplitude. Coarser than a belt's inside, the source's.

DETERMINISTIC, AND KEYED TO THE CRUST. Every perturbation -- the seed roughness
the network grows from, the massif uplift, the lithology -- is a noise of the
crust's own 0 Ma position (the plate slot raster _p and platerot.json), so the
same rock grows the same valleys at every keyframe without a chain, and any
rebuild path (build_fields.export, reskin_seafloor.save_eo) reproduces it
exactly for one keyframe alone.

WHERE. In the past, every upland older than 55-70 Ma (see weight(): age, not a
local test); in the future, where the relief deficit (relief_deficit.py) says
the belt was built smooth.

    python3 relief.py --calib           # re-measure REAL_BANDS on 0-30 Ma
    import relief; Z = relief.apply(Z, age, tag, rain=None)
"""
import json
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, maximum_filter, zoom

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
WEB = os.path.join(HERE, "..", "web")
R_EARTH_KM = 6371.0
RF_MAX = 1.3

# ---- where ----
AGE_ON = (55.0, 70.0)   # ramp: younger PaleoDEMs carry modern topography's own valleys
W_LO, W_HI = 0.20, 0.50  # the relief deficit that turns the bake on

# ---- the wedge ----
WEDGE_PX = 8.0          # crest shift toward the foreland, pixels (~80 km)

# ---- the amplitude and its distribution: real belts, per band ----
# Measured on the PaleoDEMs built on modern topography (0, 10, 20, 30 Ma), land
# equatorward of 62 deg, by relief.calib(). Bands are differences of gaussians
# at REAL_SIG pixels; a band between sigmas s1 and s2 peaks near a WAVELENGTH of
# 2 pi sqrt(s1 s2) pixels -- the scale convention the shader's own notes warn
# about -- so the three bands reach ~250 km, the inside of a belt. Coarser than
# that is the belt itself, the reconstruction's statement, and stays the
# source's (wedged).
#
# REAL_BANDS: the median LOCAL rms of each band over a ~400 km window (sigma 40
# px), binned by regional elevation (a 10 px gaussian). The window is wide on
# purpose: normalised over 60 km the relief came out one amplitude everywhere,
# and real terrain is patchy -- rough stretches and smooth ones at the same
# height -- which is half of why a first synthesis read as blobs against the
# real ranges it was tested on (the control: today's belts blurred to an
# envelope and re-grown).
REAL_SIG = (0.0, 1.0, 2.0, 4.0)
REAL_NORM = 40.0
# The pooled band rms the synthesis reaches against real belts, on the control
# (today's belts blurred to an envelope and re-grown): 87/78/83 m against
# 114/95/128 -- mapping to a heavy-tailed shape moves variance into the rare
# extremes, and the median-based table undercounts them. Corrected per band.
REAL_GAIN = np.array([1.30, 1.22, 1.50])
REAL_E = np.array([450, 750, 1050, 1400, 1800, 2250, 2750, 3500, 5000], float)
# CONDITIONED ON SLOPE AS WELL AS HEIGHT. At one regional height a plateau and
# a belt's flank carry very different relief (the finest band at 1 km: 44 m on
# ground whose ~60 km-smoothed surface slopes under 0.2%, 92 m where it slopes
# 0.5-1%), and a table by height alone gave the Sahara's plateaus a belt's
# ruggedness in the control. The slope is of the 60 km-smoothed surface, which
# an ancient envelope and today's terrain both have (medians 0.0039 and 0.0040
# over belts), so the two are comparable. Classes REAL_S (edges), rows below.
REAL_S = np.array([0.0, 0.002, 0.005, 0.010, 1.0])
REAL_SC = np.array([0.0012, 0.0033, 0.0072, 0.015])     # class centres, for interpolation
REAL_BANDS = np.array([
    [  # band 0-1 px (~20-60 km)
        [22, 37, 44, 50, 94, 95, 73, 109, 126],
        [61, 61, 67, 77, 91, 100, 94, 121, 129],
        [82, 91, 92, 104, 106, 107, 118, 137, 145],
        [82, 120, 121, 125, 120, 120, 140, 140, 123],
    ],
    [  # band 1-2 px (~60-120 km)
        [22, 33, 40, 44, 71, 79, 70, 87, 103],
        [53, 55, 59, 68, 76, 91, 82, 95, 104],
        [73, 76, 76, 89, 96, 95, 95, 109, 110],
        [73, 106, 106, 109, 109, 111, 116, 114, 108],
    ],
    [  # band 2-4 px (~120-250 km)
        [32, 44, 54, 58, 95, 99, 117, 127, 148],
        [75, 74, 84, 86, 97, 122, 122, 127, 147],
        [109, 111, 106, 123, 129, 139, 134, 148, 159],
        [109, 160, 160, 157, 159, 167, 176, 177, 176],
    ],
], float)
# ...and the SHAPE of each band's distribution, standardised by that local rms:
# its quantiles at REAL_P percent, over belts (regional height > 900 m), out to
# the 0.01st and 99.99th, because that is where the character is: real relief
# is heavy-tailed -- a few deep gorges and high crests carry much of it; the
# finest band's kurtosis is 18 and its 99.99th percentile +11 sd -- where a
# steady-state network scaled to the right rms is near-Gaussian (kurtosis 3.4).
# A first table stopped at the 0.5th/99.5th percentiles and clipped beyond
# them, which capped the synthesis at kurtosis 4 whatever else was done. The
# synthesis maps its own quantiles onto these.
REAL_P = np.array([0.01, 0.03, 0.1, 0.3, 1, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50, 52.5, 55, 57.5, 60, 62.5, 65, 67.5, 70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5, 90, 92.5, 95, 97.5, 99, 99.7, 99.9, 99.97, 99.99])
REAL_Q = np.array([
    [-8.498, -6.857, -5.169, -3.878, -2.758, -2.047, -1.511, -1.221, -1.022, -0.876, -0.760, -0.665, -0.584, -0.513, -0.449, -0.392, -0.339, -0.291, -0.245, -0.203, -0.161, -0.123, -0.088, -0.053, -0.021, -0.000, 0.023, 0.058, 0.100, 0.142, 0.187, 0.235, 0.287, 0.345, 0.409, 0.481, 0.564, 0.658, 0.770, 0.908, 1.089, 1.337, 1.704, 2.370, 3.344, 4.802, 6.238, 8.248, 11.319],
    [-5.705, -4.989, -4.120, -3.363, -2.560, -2.000, -1.558, -1.286, -1.092, -0.945, -0.826, -0.723, -0.636, -0.559, -0.491, -0.431, -0.375, -0.324, -0.275, -0.228, -0.185, -0.144, -0.104, -0.067, -0.032, -0.000, 0.035, 0.077, 0.124, 0.173, 0.224, 0.280, 0.340, 0.408, 0.484, 0.569, 0.664, 0.774, 0.904, 1.059, 1.252, 1.508, 1.863, 2.479, 3.354, 4.491, 5.622, 7.208, 9.643],
    [-4.276, -3.885, -3.388, -2.887, -2.335, -1.876, -1.498, -1.258, -1.081, -0.940, -0.825, -0.723, -0.637, -0.561, -0.491, -0.428, -0.370, -0.317, -0.266, -0.218, -0.172, -0.125, -0.078, -0.035, 0.007, 0.053, 0.101, 0.152, 0.207, 0.264, 0.325, 0.390, 0.460, 0.536, 0.620, 0.711, 0.812, 0.926, 1.055, 1.205, 1.386, 1.623, 1.950, 2.482, 3.176, 4.048, 4.918, 6.445, 7.863]
])

def _g(a, s):
    return gaussian_filter(a, s, mode=("nearest", "wrap"))


def stem(age):
    if age < 0:
        return "fut_%04d" % abs(age)
    return ("phan_%04d" if age <= 540 else "pre_%04d") % age


def _grid(H, W):
    lon = (np.arange(W) + 0.5) / W * 360.0 - 180.0
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    return lon, lat


def rain_for(age, H, W):
    p = os.path.join(FIELDS, stem(age) + "_r.webp")
    if not os.path.exists(p):
        return np.full((H, W), 0.5, np.float32)
    a = np.asarray(Image.open(p).convert("L").resize((W, H), Image.BILINEAR), np.float32)
    return a / 255.0 * RF_MAX


_PLATEROT = None


def material(age, H, W):
    """(3, H, W) unit vectors: where each pixel's crust sat at 0 Ma, z-up.

    Plate slot from _p (nearest), rotation from platerot.json, then each
    component smoothed over ~1 degree so the frames of two plates blend across
    their boundary instead of stepping -- belts ARE plate boundaries."""
    global _PLATEROT
    if _PLATEROT is None:
        _PLATEROT = json.load(open(os.path.join(WEB, "platerot.json")))
    lon, lat = _grid(H, W)
    LO, LA = np.radians(lon)[None, :], np.radians(lat)[:, None]
    v = np.stack([np.cos(LA) * np.cos(LO) * np.ones((H, W)),
                  np.cos(LA) * np.sin(LO) * np.ones((H, W)),
                  np.sin(LA) * np.ones((H, W))]).astype(np.float32)
    p = os.path.join(FIELDS, stem(age) + "_p.webp")
    rot = _PLATEROT["rot"].get(str(int(age)))
    if not os.path.exists(p) or rot is None:
        return v
    slot = np.asarray(Image.open(p).convert("L"))
    sh, sw = slot.shape
    ry = np.clip(((np.arange(H) + 0.5) / H * sh).astype(int), 0, sh - 1)
    rx = np.clip(((np.arange(W) + 0.5) / W * sw).astype(int), 0, sw - 1)
    S = slot[ry][:, rx]
    out = v.copy()
    for k in np.unique(S):
        q = rot[int(k)] if int(k) < len(rot) else [0.0, 0.0, 1.0, 0.0]
        ax = np.array(q[:3], np.float32); ang = float(q[3])
        n = np.linalg.norm(ax)
        if n < 1e-9 or abs(ang) < 1e-12:
            continue
        ax /= n
        m = S == k
        vv = v[:, m]
        c, s = np.cos(ang), np.sin(ang)
        cr = np.cross(ax[None, :], vv.T).T
        dt = (ax[:, None] * vv).sum(0)
        out[:, m] = vv * c + cr * s + ax[:, None] * (dt * (1.0 - c))[None, :]
    sig = max(1.0, 1.0 / (180.0 / H))
    out = np.stack([_g(out[i], sig) for i in range(3)])
    out /= np.maximum(np.linalg.norm(out, axis=0, keepdims=True), 1e-6)
    return out.astype(np.float32)


def crust_noise(mat, scale_km, seed, octaves=3):
    """Zero-mean, unit-ish noise of the crust's 0 Ma position, cells ~scale_km."""
    import precambrian as PRE
    H, W = mat.shape[1:]
    n = PRE.fbm3(mat.reshape(3, -1).astype(np.float64) * (R_EARTH_KM / scale_km), seed,
                 octaves=octaves).reshape(H, W)
    n = n - n.mean()
    return (n / max(n.std(), 1e-6)).astype(np.float32)


def _hash2(ix, iy, seed):
    """Two uniform [0,1) numbers per integer cell, vectorised."""
    h = (ix.astype(np.int64) * 73856093) ^ (iy.astype(np.int64) * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    a = (h & 0xFFFF).astype(np.float32) / 65536.0
    b = ((h >> 16) & 0xFFFF).astype(np.float32) / 65536.0
    return a, b


def stripes(mat, across, wavelength_km, seed, mask):
    """Stripes RUNNING ALONG STRIKE, keyed to the crust: -1..1.

    Phasor noise (the construction the shader's erosion relief uses): every
    jittered pivot of a grid in the crust's 0 Ma frame emits a cosine across
    strike, at its own frequency (0.8-1.25x), and the pivots are blended as a
    phase vector, so the stripes are parallel to the belt, irregular in
    spacing and continuous. `across` is the across-strike direction already in
    the material frame (3, H, W). Evaluated on the three axis planes of the
    material direction and blended by a steep power of it (triplanar)."""
    H, W = mat.shape[1:]
    out = np.zeros((H, W), np.float32)
    idx = np.nonzero(mask.ravel())[0]
    if idx.size == 0:
        return out
    m = mat.reshape(3, -1)[:, idx].astype(np.float64)
    a = across.reshape(3, -1)[:, idx].astype(np.float64)
    k = R_EARTH_KM / wavelength_km
    wts = np.abs(m) ** 12
    wts /= np.maximum(wts.sum(0, keepdims=True), 1e-12)
    acc_c = np.zeros(idx.size); acc_s = np.zeros(idx.size); acc_w = np.zeros(idx.size)
    for ax in range(3):
        b, c = [(1, 2), (2, 0), (0, 1)][ax]
        pw = wts[ax]
        sel = pw > 0.02
        if not sel.any():
            continue
        qx = m[b, sel] * k; qy = m[c, sel] * k
        nx, ny = a[b, sel], a[c, sel]
        nn = np.maximum(np.hypot(nx, ny), 1e-9); nx /= nn; ny /= nn
        cx, cy = np.floor(qx), np.floor(qy)
        fx, fy = qx - cx, qy - cy
        pc = np.zeros(sel.sum()); ps = np.zeros(sel.sum()); pwt = np.zeros(sel.sum())
        for oy in (-1, 0, 1):
            for ox in (-1, 0, 1):
                h1, h2 = _hash2(cx + ox, cy + oy, seed + 7 * ax)
                h3, h4 = _hash2(cx + ox + 101, cy + oy + 37, seed + 7 * ax + 3)
                dx = fx - ox - (0.25 + 0.5 * h1)
                dy = fy - oy - (0.25 + 0.5 * h2)
                wgt = np.maximum(1.0 - (dx * dx + dy * dy) * 0.69444, 0.0) ** 3 * (0.35 + 0.65 * h3)
                ph = 2.0 * np.pi * (0.8 + 0.45 * h4) * (dx * nx + dy * ny)
                pc += wgt * np.cos(ph); ps += wgt * np.sin(ph); pwt += wgt
        acc_c[sel] += pw[sel] * pc; acc_s[sel] += pw[sel] * ps; acc_w[sel] += pw[sel] * pwt
    l = np.maximum(np.hypot(acc_c, acc_s), 1e-9)
    conf = np.clip(l / np.maximum(acc_w, 1e-9) / 0.22, 0.0, 1.0)
    flat = out.ravel()
    flat[idx] = (acc_c / l * conf).astype(np.float32)
    return flat.reshape(H, W)


def across_material(mat, env, sig=8.0):
    """The across-strike (downhill) direction of the smoothed envelope, carried
    into the material frame by differencing the material field along it."""
    H, W = env.shape
    e = _g(env, sig)
    gy, gx = np.gradient(e)                        # per pixel; rows run south
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    cl = np.maximum(np.cos(np.radians(lat)), 0.1)[:, None]
    # downhill direction in PIXEL space, corrected for the east-west cell width
    ux, uy = -gx / cl, -gy                        # uphill -> downhill, x stretched by 1/cos
    n = np.maximum(np.hypot(ux * cl, uy), 1e-12)
    ux, uy = ux / n, uy / n
    dmx = np.stack([np.gradient(mat[i], axis=1) for i in range(3)])
    dmy = np.stack([np.gradient(mat[i], axis=0) for i in range(3)])
    v = dmx * ux[None] + dmy * uy[None]
    v /= np.maximum(np.linalg.norm(v, axis=0, keepdims=True), 1e-12)
    return v.astype(np.float32)


STRIKE_BANDS = 0.9      # erodibility contrast of the strike-parallel rock bands (0 off)
STRIKE_N = 3.0          # bands from a belt's foot to its crest


def strike_bands(Zw, mat):
    """Hard and soft rock in bands PARALLEL TO THE BELT: -1..1.

    Thrust sheets and folded strata put alternating resistant and weak rock
    along strike, and erosion turns them into longitudinal ridges and valleys
    (the Valley and Ridge, the Zagros, the Jura, the Lesser Himalaya's strike
    valleys). Keyed to the contours of the belt's own smoothed envelope --
    each band a level of normalised height within the belt -- so the bands run
    where the belt runs and bend with it, continuous by construction; a phase
    drifting along the belt (a crust noise at ~400 km) keeps them from reading
    as contour lines. Noise stripes were tried first and drew worms."""
    env = _g(np.maximum(Zw, 0.0), 6)
    low = (env > 50) & (env < 600)
    base = float(np.percentile(env[low], 50)) if low.any() else 200.0
    crest = _g(maximum_filter(env, size=41, mode=("nearest", "wrap")), 8)
    B = np.clip((env - base) / np.maximum(crest - base, 300.0), 0.0, 1.0)
    ph = 1.2 * crust_noise(mat, 400.0, 131, 2)
    return np.cos(2.0 * np.pi * STRIKE_N * B + ph).astype(np.float32)


def polarity(Z):
    """(fe, fn): the unit direction toward each belt's foreland, spread across
    the belt and upsampled; zero where no side qualifies."""
    import build_foreland as BFL
    import plate_field as PF
    H, W = Z.shape
    fw, fh = BFL.FW, BFL.FH
    z1 = Z.reshape(fh, H // fh, fw, W // fw).mean(axis=(1, 3))
    LON, LAT = PF._grid(fw, fh)
    zero = np.zeros_like(z1)
    fe, fn, live = BFL.polarity(z1, zero, zero, zero, LON, LAT)
    wt = _g(live.astype(np.float32), 5)
    fe = _g(fe.astype(np.float32), 5) / np.maximum(wt, 1e-3)
    fn = _g(fn.astype(np.float32), 5) / np.maximum(wt, 1e-3)
    nrm = np.maximum(np.hypot(fe, fn), 1e-6)
    conf = np.clip(wt * 3.0, 0.0, 1.0)
    fe, fn = fe / nrm * conf, fn / nrm * conf
    fe = zoom(fe, (H / fh, W / fw), order=1)
    fn = zoom(fn, (H / fh, W / fw), order=1)
    return fe.astype(np.float32), fn.astype(np.float32)


def wedge(Z, fe, fn, shift_px=WEDGE_PX):
    """Move each belt's crest toward its foreland, footprint fixed (see 1.)."""
    H, W = Z.shape
    env = _g(np.maximum(Z, 0.0), 4)
    low = (env > 50) & (env < 600)
    base = float(np.percentile(env[low], 50)) if low.any() else 200.0
    crest = _g(maximum_filter(env, size=31, mode=("nearest", "wrap")), 6)
    B = np.clip((env - base) / np.maximum(crest - base, 300.0), 0.0, 1.0)
    B = _g(B, 4)
    ux = shift_px * B * fe
    uy = -shift_px * B * fn                       # rows run north to south
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    out = map_coordinates(Z, [np.clip(yy - uy, 0, H - 1), (xx - ux) % W], order=1, mode="nearest")
    return np.where(Z > 0, np.maximum(out, 1.0), Z).astype(np.float32)


def _smooth01(x):
    t = np.clip(x, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def weight(Z, age):
    """How much of the baked relief replaces the source, 0..1.

    THE PAST IS DECIDED BY AGE, NOT BY A LOCAL TEST. Before ~65 Ma no valley in
    a PaleoDEM is a statement about its time -- only the envelope is -- and a
    local roughness test was fooled twice: by the narrow band of noise Scotese
    ran along each crest (+-100 m, read as real relief, so every crest was left
    a prism), and by frame-to-frame authoring noise, which would switch a belt's
    relief between the bake's and the source's from one keyframe to the next.
    So every upland older than AGE_ON is baked (regional height 350 -> 800 m),
    ramping in across AGE_ON from the modern-topography Cenozoic, and the
    amplitude is still set by the real-belt calibration. THE FUTURE carries the
    present day's real ranges, so there the relief deficit decides, with its
    holes closed so a crest between two deficient flanks is baked too."""
    import relief_deficit as RD
    E = _g(np.maximum(Z, 0.0), 10)
    upland = _smooth01((E - 350.0) / 450.0) * (Z > 0)
    if age >= 0:
        a0, a1 = AGE_ON
        r = float(np.clip((age - a0) / (a1 - a0), 0.0, 1.0))
        return (upland * r).astype(np.float32)
    D = RD.deficit(Z)
    w = _smooth01((D - W_LO) / (W_HI - W_LO))
    w = np.maximum(w, _g(maximum_filter(w, size=9, mode=("nearest", "wrap")), 3) * upland)
    return (w * (Z > 0)).astype(np.float32)


def regional_slope(z):
    """RMS slope (m/m) of the ~60 km-smoothed surface, over ~40 km."""
    H, W = z.shape
    sm = _g(np.maximum(z, 0.0), 6)
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    dy = np.pi * R_EARTH_KM * 1000.0 / H
    dx = 2.0 * np.pi * R_EARTH_KM * 1000.0 / W * np.maximum(np.cos(np.radians(lat)), 0.05)
    gy = np.gradient(sm, axis=0) / dy
    gx = (np.roll(sm, -1, 1) - np.roll(sm, 1, 1)) * 0.5 / dx[:, None]
    return np.sqrt(_g(gx * gx + gy * gy, 4)).astype(np.float32)


def _table(E, S, tab):
    """Bilinear in (regional height, log slope) over a (4 slope, 9 height) table."""
    ls = np.log(np.clip(S, REAL_SC[0], REAL_SC[-1]))
    lc = np.log(REAL_SC)
    j = np.clip(np.searchsorted(lc, ls) - 1, 0, len(lc) - 2)
    t = np.clip((ls - lc[j]) / (lc[j + 1] - lc[j]), 0.0, 1.0)
    lo = np.stack([np.interp(E, REAL_E, tab[c]) for c in range(len(lc))])
    a = np.take_along_axis(lo, j[None], 0)[0]
    b = np.take_along_axis(lo, (j + 1)[None], 0)[0]
    return (a * (1.0 - t) + b * t).astype(np.float32)


def spectral(h, Zw, dom):
    """Z's envelope above REAL_SIG[-1], plus h's bands matched to real belts:
    each band standardised by its own ~400 km local rms, its distribution
    mapped onto the real one (REAL_Q), and rescaled to the real local rms at
    this regional height (REAL_BANDS). The model decides where each valley and
    divide is; the Earth decides how the relief is distributed."""
    land = (Zw > 0).astype(np.float32)
    E = _g(np.maximum(Zw, 0.0), 10)
    S = regional_slope(Zw)
    new = _g(Zw, REAL_SIG[-1])
    L = [h] + [_g(h, s) for s in REAL_SIG[1:]]
    den = np.maximum(_g(land, REAL_NORM), 1e-3)
    # the mapping is fitted where the real tables were measured -- belts,
    # regional height over 900 m -- and applied everywhere: fitted over every
    # upland, the synthesis put its extremes in the low hills and stayed
    # near-Gaussian in the belts (kurtosis 5 against 12 over belts alone)
    m = dom & (Zw > 0) & (E > 900.0)
    if m.sum() < 2000:
        m = dom & (Zw > 0)
    for i in range(len(REAL_SIG) - 1):
        b = L[i] - L[i + 1]
        loc = np.sqrt(_g(b * b * land, REAL_NORM) / den)
        u = b / np.maximum(loc, 1.0)
        if m.sum() > 200:
            qs = np.percentile(u[m], REAL_P)
            qs = np.maximum.accumulate(qs + np.arange(qs.size) * 1e-6)
            u = np.interp(u, qs, REAL_Q[i], left=REAL_Q[i][0], right=REAL_Q[i][-1])
        tgt = _table(E, S, REAL_BANDS[i]) * REAL_GAIN[i]
        new += (u * tgt).astype(np.float32)
    return new.astype(np.float32)


def _fill(z):
    """Depressions filled to their spill level (morphological reconstruction)."""
    from skimage.morphology import reconstruction
    seed = z.copy()
    seed[1:-1, :] = z.max()
    return reconstruction(seed, z, method="erosion").astype(np.float32)


def _lake_view(z):
    """The elevation as bake_lakes.py sees it: sqrt-encoded to 8 bits, resized to
    2048 x 1024 with PIL's bilinear filter, decoded."""
    from fieldpack import enc_elev, dec_elev
    e = (np.clip(enc_elev(z), 0, 1) * 255.0 + 0.5).astype(np.uint8)
    H, W = z.shape
    e2 = np.asarray(Image.fromarray(e).resize((W // 2, H // 2), Image.BILINEAR), np.float32) / 255.0
    return dec_elev(e2).astype(np.float32)


def fill_new_pits_coarse(out, Z, w, rounds=3):
    """The same, at the resolution and encoding the lake bake reads: halving the
    grid by averaging dams the narrow outlets of the new valleys, and the water
    balance then fills the dammed reaches with lakes that change from one
    keyframe to the next (measured: 0.19% -> 1.02% of the 400 Ma belts under
    water, the source's own basins kept). Each round raises the full-resolution
    floor of every new coarse hollow to its spill level -- a valley floor
    sedimented to its outlet -- and re-checks, because the raise is seen through
    the same averaging."""
    land = Z > 0
    H, W = Z.shape
    lo = np.float32(-50.0)
    b2 = _lake_view(np.where(land, Z, lo))
    src_pit = (_fill(b2) - b2) > 0.5
    w2 = np.asarray(Image.fromarray(w.astype(np.float32)).resize((W // 2, H // 2), Image.BILINEAR))
    for _r in range(rounds):
        a2 = _lake_view(np.where(land, out, lo))
        d2 = _fill(a2) - a2
        new = (d2 > 0.5) & ~src_pit & (w2 > 0.02) & (a2 > 0)
        if not new.any():
            break
        up = np.asarray(Image.fromarray(np.where(new, d2, 0.0).astype(np.float32)).resize((W, H), Image.BILINEAR))
        grow = np.asarray(Image.fromarray(new.astype(np.float32)).resize((W, H), Image.NEAREST)) > 0.5
        out = np.where(grow & land, out + up * 1.05 + 1.0, out).astype(np.float32)
    return out


def fill_new_pits(out, Z, w):
    """Fill the closed hollows the synthesis made, and only those.

    The steady-state network drains everywhere by construction; the band
    recombination does not, and its heavy tail cuts the odd deep pit -- which
    the water-balance lake bake would fill with a lake. A hollow the SOURCE has
    (the Tarim, the Qaidam, a rift) is a real closed basin and is kept."""
    land = Z > 0
    if not (land & (w > 0.02)).any():
        return out
    lo = np.float32(-50.0)
    a = np.where(land, out, lo).astype(np.float32)
    b = np.where(land, Z, lo).astype(np.float32)
    fa, fb = _fill(a), _fill(b)
    new_pit = (fa - a > 0.5) & (fb - b < 0.5) & (w > 0.02) & land
    return np.where(new_pit, fa, out).astype(np.float32)


def apply(Z, age, tag=None, rain=None, verbose=False):
    """The keyframe's elevation with the belts' relief baked in (land only)."""
    import lem
    Z = np.asarray(Z, np.float32)
    H, W = Z.shape
    w = weight(Z, age)
    if float(w.max()) < 0.03:
        if verbose:
            print("  relief %s: no envelope belts" % stem(age))
        return Z
    if rain is None:
        rain = rain_for(age, H, W)
    elif rain.shape != Z.shape:
        rain = np.asarray(Image.fromarray(np.asarray(rain, np.float32)).resize((W, H), Image.BILINEAR))
    fe, fn = polarity(Z)
    Zw = wedge(Z, fe, fn)
    mat = material(age, H, W)
    seed = (15.0 * crust_noise(mat, 12.0, 101, 2) + 40.0 * crust_noise(mat, 35.0, 103, 2)
            + 80.0 * crust_noise(mat, 90.0, 107, 2))
    env = _g(Zw, 6)
    gy, gx = np.gradient(env)
    gN, gE = -gy, gx                              # uphill, east/north
    gm = np.maximum(np.hypot(gE, gN), 1e-6)
    skew = np.clip(-(gE * fe + gN * fn) / gm, -1.0, 1.0)
    skew *= np.clip(gm / (np.percentile(gm[w > 0.5], 50) + 1e-6), 0.0, 1.0) if (w > 0.5).any() else 0.0
    # NO STRIKE STRIPES. Stripes along strike (phasor noise in the uplift and
    # the erodibility, keyed to the crust) raised the synthesis' elongation to
    # today's, and drew a maze of wormy ridges doing it -- snow-capped worms
    # across a synthetic Himalaya in the control. stripes() and
    # across_material() are kept for the next attempt at thrust sheets.
    dom = (w > 0.02)
    un = crust_noise(mat, 150.0, 109, 2)
    kn = crust_noise(mat, 50.0, 113, 2)
    if STRIKE_BANDS > 0.0:
        kn = kn + STRIKE_BANDS * strike_bands(Zw, mat)
    _out, h = lem.steady(Zw, w, rain, seed_noise=seed, sweeps=20, cycles=5, skew=skew,
                         u_noise=un, k_noise=kn, un_amp=0.5, kn_amp=0.6, diff_steps=0,
                         verbose=verbose)
    new = spectral(h, Zw, dom)
    if os.environ.get("RELIEF_DEBUG"):
        np.save(os.environ["RELIEF_DEBUG"] + "_h.npy", h); np.save(os.environ["RELIEF_DEBUG"] + "_zw.npy", Zw)
        np.save(os.environ["RELIEF_DEBUG"] + "_w.npy", w)
    # A SOFT CEILING. Averaged over a 10 km cell no ground on today's Earth
    # stands much above 6.7 km (the present field's own maximum), and the
    # heavy-tailed calibration puts rare crests well past a belt's envelope --
    # 8.9 km on the future's highest range before this. Above 6 km, compressed
    # toward 7.2 km.
    over = np.maximum(new - 6000.0, 0.0)
    new = np.where(over > 0, 6000.0 + 1200.0 * np.tanh(over / 1200.0), new)
    out = np.where(Z > 0, Z + w * (new - Z), Z)
    out = np.where(Z > 0, np.maximum(out, 1.0), Z).astype(np.float32)
    out = fill_new_pits(out, Z, w)
    out = fill_new_pits_coarse(out, Z, w)
    if verbose:
        m = w > 0.5
        print("  relief %s: %.2f%% of the globe weighted >0.5; >3 km %d -> %d cells, max %.0f -> %.0f"
              % (stem(age), 100.0 * float(m.mean()), int((Z > 3000).sum()), int((out > 3000).sum()),
                 float(Z.max()), float(out.max())))
    return out


def calib(ages=(0, 10, 20, 30)):
    import relief_deficit as RD
    edges = [300, 600, 900, 1200, 1600, 2000, 2500, 3000, 4000, 6000]
    acc = []
    for a in ages:
        z = RD.elevation(a).astype(np.float32)
        Hh = z.shape[0]
        lat = np.abs(90 - (np.arange(Hh) + 0.5) / Hh * 180)[:, None]
        land = (z > 0) & (lat < 62)
        lf = land.astype(np.float32)
        E = _g(np.maximum(z, 0), 10)
        L = [z] + [_g(z, s) for s in REAL_SIG[1:]]
        rows = []
        for i in range(len(REAL_SIG) - 1):
            b = L[i] - L[i + 1]
            rms = np.sqrt(_g(b * b * lf, 6) / np.maximum(_g(lf, 6), 1e-3))
            rows.append([float(np.median(rms[land & (E >= p) & (E < q)])) if (land & (E >= p) & (E < q)).sum() > 300
                         else np.nan for p, q in zip(edges[:-1], edges[1:])])
        acc.append(rows)
    m = np.nanmedian(np.array(acc), axis=0)
    print("E centres", [(p + q) // 2 for p, q in zip(edges[:-1], edges[1:])])
    for i, row in enumerate(m):
        print("band %d:" % i, " ".join("%4.0f" % v for v in row), "   table:",
              " ".join("%4.0f" % v for v in REAL_BANDS[i]))


if __name__ == "__main__":
    import sys
    if "--calib" in sys.argv:
        calib()
