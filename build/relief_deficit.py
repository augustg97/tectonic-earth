"""The RELIEF DEFICIT: how much of a mountain belt's ridge-and-valley relief the
source never drew. Baked into the BLUE channel of every `*_f.webp`.

WHY THIS EXISTS. The Palaeozoic and Precambrian ranges read as symmetric
triangular prisms, and the future's collision belts as smooth clumps. The
fields say why, and it is not the renderer. Inside mountain belts, the relief
finer than ~60-90 km -- the band a range is actually made of: spurs, transverse
valleys, peaks and saddles -- measures, as a local RMS at the same regional
elevation:

    0-35 Ma  (PaleoDEMs built on modern topography)   84 m at 1 km,  176 at 2.2 km
    100-200 Ma                                        ~40 m at 1 km, ~35 at 2 km
    300-400 Ma                                        16-19 m at 1 km, 26-44 at 2.2 km
    700 Ma   (generated cratons, precambrian.py)      11 m at 1 km
    +250 Myr (the synthesised suture belts)           ~23 m at every elevation

Scotese & Wright drew the older belts as smooth envelopes -- where a range stood
and how high -- and the future's belts are gaussians of a contact indicator, so
both carry the belt and none of its dissection. Nothing downstream can light
relief that is not there, and the hillshade stencil is blind in this band
anyway (MODEL-GAPS iteration 62). So the shader grows it per pixel (the erosion
relief in FRAG), and this field tells it HOW MUCH to grow at each place and age.

THE MEASURE IS DATA, NOT TASTE. The target is what real mountains of the same
regional elevation carry in the present-day PaleoDEM at this grid's resolution
(`R_MED`, measured by `--calib`). The deficit is the shortfall below the
real terrain's own lower quartile (`LO_FRAC` of the median), smoothed to a
regional quantity:

    D = clip((LO_FRAC * R(E) - rms) / (LO_FRAC * R(E)), 0, 1)

so ground that already carries real-looking relief gets D = 0 and is left to
its data -- the present day, and the Cenozoic frames whose PaleoDEMs are built
on modern topography -- while a schematic envelope gets most of a real belt's
dissection back. It also EVENS the source's own authoring noise: 5, 15 and 25
Ma carry about half the relief of 0, 10, 20 and 30 Ma, and a per-keyframe
deficit tops up exactly the thin ones.

What it is not: a claim about where any ancient valley was. The pattern is
grown from the belt's own slope and the crust's own coordinates; the particular
valley is invented, like the modelled rivers and the synthesised spreading
network (README section 9).

    ../venv/bin/python relief_deficit.py              # patch B of every _f in place
    ../venv/bin/python relief_deficit.py 300 -250     # some ages
    ../venv/bin/python relief_deficit.py --stats      # per-age table, no writes
    ../venv/bin/python relief_deficit.py --calib      # re-measure R(E) on 0 Ma
    ../venv/bin/python relief_deficit.py -j 4         # in parallel
"""
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
Z_RANGE = 8000.0
FW, FH = 1024, 512              # the _f grid

# The band: z minus a gaussian of 1.5 texels (14.7 km at 4096 wide) passes
# wavelengths below ~60-90 km (0.84 at 48 km, 0.35 at 100 km, 0.10 at 200 km).
# That is the band the shader's erosion octaves fill; the envelope of a belt
# lives above it, so a smooth prism scores low here however tall it is.
SIG_BAND = 1.5
SIG_LOCAL = 6.0                 # local rms over ~60 km
SIG_REGION = 10.0               # regional elevation E over ~100 km
SIG_RMS_REGION = 12.0           # the deficit is a REGIONAL quantity: see below
SIG_OUT = 3.0                   # final smoothing, ~30 km

# R(E): median local rms of the band against regional elevation, measured on
# the present-day field (phan_0000_e, land poleward of 62 deg excluded so the
# ice sheets' own smoothness is not taken for rock). --calib re-measures it:
#     E    400  600  800 1000 1250 1550 1850 2200 2600 3050 3650 4750
#     rms   25   37   70   84   91  134  152  176  254  246  196  143
# Smoothed to a monotone rise with the plateau fall-off real highlands show
# (Tibet's interior carries less relief than its rim).
R_E = np.array([0.0, 300.0, 400.0, 600.0, 800.0, 1000.0, 1250.0, 1550.0, 1850.0,
                2200.0, 2600.0, 3050.0, 3650.0, 4750.0, 9000.0])
R_MED = np.array([0.0, 18.0, 25.0, 40.0, 64.0, 82.0, 100.0, 128.0, 152.0,
                  180.0, 225.0, 240.0, 215.0, 175.0, 175.0])
# THE DEFICIT IS MEASURED IN L1, NOT RMS (the mountain round, second pass). A
# schematic belt is a tent, and a tent's crest is a sharp line: all of its band
# energy sits in a pixel or two, which an RMS over a ~120 km window reads as
# rough ground -- so the crests, the one part of a prism that most needs relief,
# were exactly where the deficit said none was missing (seen as holes along
# every crest in the bake's weight map). The mean ABSOLUTE band value discounts
# a sparse line: real terrain's L1 is a steady 0.68 of its RMS at every height,
# a lone crest line's a fraction of that. R_L1 is the median L1 over the same
# 12 px window on 0, 10, 20 and 30 Ma (land equatorward of 62 deg):
#     E     400  600  800 1000 1250 1550 1850 2200 2600 3050 3650 4750
#     L1     18   28   51   59   61   84  100  112  105  126  129  116
R_L1 = np.array([0.0, 14.0, 18.0, 28.0, 48.0, 58.0, 66.0, 84.0, 100.0,
                 110.0, 115.0, 122.0, 122.0, 116.0, 116.0])
# The real terrain's own lower quartile sits at 0.45-0.75 of the median in
# every elevation bin (measured, 0-35 Ma). Measuring the deficit below 0.55 of
# the median, rather than below the median itself, is what keeps real ground
# out of it: a smooth patch of genuine topography is not a schematic belt.
LO_FRAC = 0.55
# Relief only exists to dissect where the ground stands up. Below ~350 m the
# plains machinery (dissectRelief, the drainage carve) owns the texture.
E_ON0, E_ON1 = 350.0, 750.0
# NOT GATED ON SLOPE HERE, and that was measured rather than chosen. Height and
# smoothness alone cannot tell a schematic belt from a real TABLELAND -- the
# present-day map marks the Kalahari highveld, the High Plains, the Najd and the
# Ordos, which stand 1-1.5 km up and are smooth because they ARE smooth -- and
# the envelope slope does not separate them either: regional rms slope over
# ~50 km of the ~20 km surface reads 0.14-0.36% on those tablelands, 0.43% on
# the median 300 Ma belt, 0.31% on the +250 Myr belts, 0.09% on the Precambrian
# uplands, against 1.0-1.6% in the Zagros and the Alps. The distributions
# overlap. So this field says only how much relief is MISSING; how much of it a
# place can carry is the shader's decision, from the local relief (envelope
# slope times a drainage length), which is how dissection actually scales: a
# tableland far from its escarpment is barely cut, a belt's flank is cut deep.
# envelope_slope() stays for that measurement (--slopes).
SIG_SLOPE_SURF = 2.0            # the envelope, ~20 km
SIG_SLOPE_REG = 5.0             # regional rms of its slope, ~50 km
POLAR_DEG = 62.0                # present-day ice sheets are smooth for a reason


def stem(age):
    if age < 0:
        return "fut_%04d" % abs(age)
    return ("phan_%04d" if age <= 540 else "pre_%04d") % age


def elevation(age):
    """The SHIPPED elevation of a keyframe, decoded, full resolution."""
    p = os.path.join(FIELDS, stem(age) + "_e.avif")
    if not os.path.exists(p):
        return None
    s = 2.0 * np.asarray(Image.open(p).convert("L"), np.float32) / 255.0 - 1.0
    return np.sign(s) * s * s * Z_RANGE


def _g(a, s):
    # latitude clamps (the poles are real), longitude wraps (it is periodic)
    return gaussian_filter(a, s, mode=("nearest", "wrap"))


def fields(z, l1=False):
    """Regional elevation E, the band's regional rms (or L1), and the land mask."""
    H = z.shape[0]
    lat = np.abs(90.0 - (np.arange(H) + 0.5) / H * 180.0)[:, None]
    land = (z > 0.0)
    lf = land.astype(np.float32)
    band = z - _g(z, SIG_BAND)
    E = _g(np.maximum(z, 0.0), SIG_REGION)
    # over LAND only, so a coastline's own step is not counted as relief
    den = np.maximum(_g(lf, SIG_RMS_REGION), 1e-3)
    if l1:
        return E, _g(np.abs(band) * lf, SIG_RMS_REGION) / den, land, lat
    rms = np.sqrt(_g(band * band * lf, SIG_RMS_REGION) / den)
    return E, rms, land, lat


def _smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def envelope_slope(z):
    """Regional RMS slope (m/m) of the belt-scale surface."""
    H, W = z.shape
    s = _g(np.maximum(z, 0.0), SIG_SLOPE_SURF)
    lat = 90.0 - (np.arange(H) + 0.5) / H * 180.0
    dy = np.pi * 6.371e6 / H                                   # metres per row
    dx = 2.0 * np.pi * 6.371e6 / W * np.maximum(np.cos(np.radians(lat)), 0.05)
    gy = np.gradient(s, axis=0) / dy
    gx = (np.roll(s, -1, axis=1) - np.roll(s, 1, axis=1)) * 0.5 / dx[:, None]
    return np.sqrt(_g(gx * gx + gy * gy, SIG_SLOPE_REG))


def deficit(z):
    """D in [0, 1] at the full grid of z."""
    E, rms, land, lat = fields(z, l1=True)
    R = np.interp(E, R_E, R_L1)
    lo = np.maximum(LO_FRAC * R, 1.0)
    D = np.clip((lo - rms) / lo, 0.0, 1.0)
    D = D * _smoothstep(E_ON0, E_ON1, E) * land
    return np.clip(_g(D.astype(np.float32), SIG_OUT), 0.0, 1.0)


def to_f_grid(D):
    """Area-average the full-resolution field onto the 1024x512 _f grid."""
    h, w = D.shape
    fy, fx = h // FH, w // FW
    return D.reshape(FH, fy, FW, fx).mean(axis=(1, 3))


def deficit_f(age):
    """The deficit on the _f grid for one keyframe, or None without an _e."""
    z = elevation(age)
    if z is None:
        return None
    return to_f_grid(deficit(z))


def patch(age, quiet=False):
    """Write D into B of this keyframe's existing _f, leaving R and G alone."""
    t0 = time.time()
    p = os.path.join(FIELDS, stem(age) + "_f.webp")
    if not os.path.exists(p):
        if not quiet:
            print("  %-16s no _f (build_foreland.py bakes it, and calls this)" % stem(age))
        return None
    D = deficit_f(age)
    if D is None:
        return None
    arr = np.array(Image.open(p).convert("RGB"))
    if arr.shape[:2] != (FH, FW):
        raise SystemExit("unexpected _f size %s at %s" % (arr.shape, p))
    arr[..., 2] = np.round(np.clip(D, 0.0, 1.0) * 255.0).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(p, "WEBP", lossless=True, method=6, exact=True)
    back = np.asarray(Image.open(p).convert("RGB"))[..., 2]
    if not np.array_equal(back, arr[..., 2]):
        raise SystemExit("B channel did not round-trip at %s" % p)
    m = D > 0.02
    if not quiet:
        print("  %-16s D>0.02 on %5.2f%% of the globe, median there %.2f, max %.2f  %.1fs"
              % (stem(age), 100.0 * m.mean(), float(np.median(D[m])) if m.any() else 0.0,
                 float(D.max()), time.time() - t0))
    return float(D.max())


def stats(ages):
    """Per-age: how much mountain land carries a deficit, and how big."""
    print("  age    belt land(E>1km)%   D median   D p90   rms/R median")
    for a in ages:
        z = elevation(a)
        if z is None:
            continue
        E, rms, land, lat = fields(z)
        D = deficit(z)
        m = land & (E > 1000.0) & (lat < POLAR_DEG)
        if m.sum() < 100:
            print("  %5d   %5.2f   (no belt)" % (a, 100.0 * m.mean()))
            continue
        R = np.interp(E, R_E, R_MED)
        print("  %5d   %6.2f   %8.2f   %6.2f   %8.2f"
              % (a, 100.0 * m.mean(), float(np.median(D[m])), float(np.percentile(D[m], 90)),
                 float(np.median(rms[m] / np.maximum(R[m], 1.0)))))


def calib(age=0):
    """Re-measure R(E) on a real-topography keyframe; prints beside the table."""
    z = elevation(age)
    E, _rms, land, lat = fields(z)
    # the calibration is of the LOCAL rms, not the regional one the deficit uses
    lf = land.astype(np.float32)
    band = z - _g(z, SIG_BAND)
    rms = np.sqrt(_g(band * band * lf, SIG_LOCAL) / np.maximum(_g(lf, SIG_LOCAL), 1e-3))
    edges = [300, 500, 700, 900, 1100, 1400, 1700, 2000, 2400, 2800, 3300, 4000, 5500]
    print("  E bin centre   measured median   p25   table R(E)")
    for a, b in zip(edges[:-1], edges[1:]):
        m = land & (E >= a) & (E < b) & (lat < POLAR_DEG)
        if m.sum() < 300:
            continue
        c = 0.5 * (a + b)
        print("  %8.0f   %12.0f   %6.0f   %8.0f"
              % (c, float(np.median(rms[m])), float(np.percentile(rms[m], 25)),
                 float(np.interp(c, R_E, R_MED))))


def _one(a):
    return patch(a, quiet=False)


def main():
    argv = sys.argv[1:]
    if "--calib" in argv:
        calib()
        return 0
    jobs = 1
    if "-j" in argv:
        i = argv.index("-j")
        jobs = int(argv[i + 1])
        del argv[i:i + 2]
    ages = [int(a) for a in argv if not a.startswith("--")] or list(range(-250, 1001, 5))
    if "--stats" in argv:
        stats(ages)
        return 0
    t0 = time.time()
    print("relief deficit into B of %d _f fields" % len(ages), flush=True)
    if jobs > 1:
        from multiprocessing import Pool
        with Pool(jobs) as pool:
            res = pool.map(_one, ages, chunksize=1)
    else:
        res = [_one(a) for a in ages]
    done = sum(r is not None for r in res)
    print("RELIEF-DEFICIT-DONE %d/%d written in %.1f min" % (done, len(ages), (time.time() - t0) / 60.0))
    return 0 if done == len(ages) else 1


if __name__ == "__main__":
    raise SystemExit(main())
