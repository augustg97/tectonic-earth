"""Bake `*_t.webp` -- where crust is being shortened, and which way the folds run.

WHY THE APP CANNOT DRAW A COLLISION TODAY. Nothing tectonic reaches the shader.
`motA` is bound and never sampled, `motion.classify()` is dead code,
`build_plates_gplates.py` collapses Merdith's own OrogenicBelt into a generic
trench, and `plates_time.json` carries no velocity at any age >= 0. So the
fragment shader has no way to know that the ground under a pixel is being
squeezed, and `detail3` gives it ISOTROPIC ridged noise -- rough ground at every
orientation at once.

Real orogens are not isotropic. They are STRIPES: the Valley-and-Ridge
Appalachians, the Zagros, the Jura, the Verkhoyansk. Parallel ridges running
along strike are the single strongest visual cue that crust has been shortened,
and their absence is why a range in this app reads as bumpy ground however tall
it is. That is what this field exists to fix.

CHANNELS (RGB):
    R  shortening   the most compressive principal strain over this 5 Myr step,
                    0 where crust is extending or rigid, companded by SHORT_REF
    G,B fold axis   cos(2*theta), sin(2*theta), 0.5-centred

WHY A DOUBLE ANGLE. A fold axis is a LINE, not a direction -- 179 degrees and
1 degree are the same fabric. Storing theta directly puts a wrap discontinuity
in the middle of that identity, and bilinear filtering across it returns 90
degrees, which is exactly perpendicular to the truth. Storing (cos 2t, sin 2t)
has no discontinuity, interpolates correctly, and the shader recovers the axis
with one atan. This is the same trick the ocean-structure field uses for
spreading direction.

STRAIN, NOT DIVERGENCE. `_v`'s B channel already carries the divergence of the
displacement field, and divergence alone cannot orient anything -- it is a
scalar. The fabric needs the full 2-D strain tensor, whose eigenvectors give the
shortening direction and whose eigenvalues give its rate. Pure shear along a
transform has zero divergence and a perfectly well-defined fabric, which the
divergence channel would have reported as nothing happening.

Derived entirely from the shipped displacement field, so this costs no DEM and
no elevation rebuild -- about a second a keyframe.

    ../venv/bin/python build_tectonic.py            # all past keyframes
    ../venv/bin/python build_tectonic.py --selftest
"""
import os
import sys
import time

import numpy as np
from PIL import Image

import build_displacement as BD
import plate_field as PF

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "fields")

# 512x256. A deformation zone is 100-300 km and the fabric it orients is a
# broad-scale property, so 0.7 deg a cell resolves it with room to spare -- and
# unlike the displacement field there is no discontinuity here to be smeared,
# because the smoothing above has already turned every step into a gradient.
TW, TH = 512, 256
KM_PER_DEG = 111.32

# Full-scale shortening, in strain per 5 Myr. Measured across the series: the
# 99.9th percentile sits near 0.02 and collision zones reach a few times that.
# Companded with a square root so the common small values keep resolution.
# Set from the measured distribution, not guessed: p99.9 across the series runs
# 0.47-0.54 once the field is smoothed to a real deformation width. The first
# value tried was 0.06, which saturated the channel across a third of the globe.
SHORT_REF = 0.5

# Half-width of a deformation zone, in grid cells (~39 km each at 1024 wide).
# The displacement field is piecewise RIGID -- constant inside a plate, with a
# step across every boundary -- so differentiating it raw reports the step
# divided by one cell, which is a discretisation artefact, not a strain: it
# peaked at 9.6 where real convergence is a few tenths. Real deformation is
# distributed over an orogen, roughly 100-300 km, so the field is smoothed to
# that width BEFORE it is differentiated and the answer becomes a rate rather
# than a number about the grid.
ZONE_CELLS = 2.5


def strain(dE, dN, w, h):
    """(shortening, cos2t, sin2t) from the displacement field.

    dE/dN are degrees of great circle. Converting to strain needs PHYSICAL
    spacing, and on an equirectangular grid the east spacing shrinks as
    cos(lat) -- without that the whole polar region reports enormous strain
    purely because its columns are close together.
    """
    _LON, LAT = PF._grid(w, h)
    coslat = np.maximum(np.cos(np.radians(LAT)), 0.10)
    dx = (360.0 / w) * coslat * KM_PER_DEG          # km per column
    dy = (180.0 / h) * KM_PER_DEG                   # km per row
    from scipy.ndimage import gaussian_filter
    # Smooth to a real deformation-zone width first. Longitude wraps, latitude
    # does not.
    def sm(a):
        a = gaussian_filter(a, (0.0, ZONE_CELLS), mode="wrap")
        return gaussian_filter(a, (ZONE_CELLS, 0.0), mode="nearest")
    E = sm(dE) * KM_PER_DEG                         # displacement in km
    N = sm(dN) * KM_PER_DEG

    # np.gradient over axis 1 wraps by hand: longitude is periodic and this
    # pipeline has forgotten that in three separate places already.
    Ew = np.concatenate([E[:, -1:], E, E[:, :1]], axis=1)
    Nw = np.concatenate([N[:, -1:], N, N[:, :1]], axis=1)
    dEdx = (Ew[:, 2:] - Ew[:, :-2]) / (2.0 * dx)
    dNdx = (Nw[:, 2:] - Nw[:, :-2]) / (2.0 * dx)
    # row 0 is north, so a step DOWN a row is a step SOUTH -- negate for north.
    dEdy = -np.gradient(E, axis=0) / dy
    dNdy = -np.gradient(N, axis=0) / dy

    exx, eyy = dEdx, dNdy
    exy = 0.5 * (dEdy + dNdx)

    # Principal strains of [[exx,exy],[exy,eyy]].
    a = 0.5 * (exx + eyy)
    dxy = exx - eyy
    r = np.hypot(dxy, 2.0 * exy)                    # 2 * the deviatoric radius
    lam_min = a - 0.5 * r
    shortening = np.maximum(0.0, -lam_min)

    # The extension axis, which is what a fold axis runs along. (cos2t, sin2t)
    # falls straight out of the deviatoric components -- no atan2 needed here.
    denom = np.maximum(r, 1e-12)
    return shortening, dxy / denom, (2.0 * exy) / denom


TOPO_SHORT = 0.34   # shortening a full-height range claims from its own relief


def topo_fabric(age):
    """Strike from the range's OWN TOPOGRAPHY, for every orogen the plate
    reconstruction cannot see.

    Measured on the shipped field, the strain fabric is excellent where rigid
    plates collide head-on -- the Himalaya reads shortening 0.365 with an axis
    strength of 0.998 -- and absent everywhere else that matters: the Andes
    0.055, the Zagros 0.000, the Alps 0.090, against 0.082 over the open
    Pacific. Those are noise-level. The reason is honest: Andean-type shortening
    happens INSIDE the overriding plate, and a rigid-plate reconstruction has no
    way to express it, so no amount of differentiating the displacement field
    will find it.

    But a range states its own strike. A fold axis runs ALONG a belt, which is
    the tangent to its elevation contours -- the identical construction
    rebuild_future.py already uses on the belt raster, applied here to the
    topography itself. It costs no new data, works at every age including the
    Precambrian, and it cannot invent a range where there is no relief.
    """
    from scipy.ndimage import gaussian_filter, zoom as ndzoom
    from fieldpack import dec_elev
    name = ("phan_%04d_e.avif" if age <= 540 else "pre_%04d_e.avif") % age
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return None, None, None
    z = dec_elev(np.asarray(Image.open(p).convert("L")).astype(np.float32) / 255.0)
    h, w = z.shape
    zs = ndzoom(z, (float(TH) / h, float(TW) / w), order=1)
    zs = gaussian_filter(zs, 1.1, mode=("nearest", "wrap"))
    gy, gx = np.gradient(zs)
    gN, gE = -gy, gx
    mag = np.hypot(gE, gN) + 1e-9
    tE, tN = -gN / mag, gE / mag                 # contour tangent == strike
    c2, s2 = tE * tE - tN * tN, 2.0 * tE * tN
    # A belt is high AND has relief. Either alone is wrong: a plateau is high
    # and unstriped, a dissected lowland has relief and no strike worth drawing.
    relief = gaussian_filter(mag, 1.4, mode=("nearest", "wrap"))
    # HEIGHT RELATIVE TO THIS AGE'S OWN LAND, not an absolute 650 m. The fixed
    # threshold was calibrated on modern topography and silently switched the
    # fabric off in deep time: measured, phan_0300_t came out with a median
    # shortening of 0.000 against the present day's 0.141, because a 300 Ma
    # Pangaean belt in this DEM is a broad low swell and almost nothing cleared
    # the bar. An orogen is high RELATIVE TO THE CONTINENT IT SITS ON, at every
    # age, so the bar is now the land's own 70th and 97th percentiles.
    land = zs > 50.0
    if land.any():
        lo = float(np.percentile(zs[land], 70.0))
        hi = max(float(np.percentile(zs[land], 97.0)), lo + 350.0)
    else:
        lo, hi = 650.0, 2350.0
    ref = np.percentile(relief[zs > lo], 90) if (zs > lo).any() else 1.0
    st = (np.clip((zs - lo) / (hi - lo), 0.0, 1.0)
          * np.clip(relief / (ref + 1e-9), 0.0, 1.0))
    return st * TOPO_SHORT, c2, s2


def _encode(shortening, c2, s2):
    r = np.sqrt(np.clip(shortening / SHORT_REF, 0.0, 1.0))
    g = np.clip(c2, -1, 1) * 0.5 + 0.5
    b = np.clip(s2, -1, 1) * 0.5 + 0.5
    return np.stack([np.round(x * 255.0).astype(np.uint8) for x in (r, g, b)], -1)


def bake(age, rot, quiet=False):
    from scipy.ndimage import gaussian_filter
    t0 = time.time()
    dE, dN, cov = BD.displacement(age, TW, TH, rot)
    dE = BD.laplace_fill(dE, cov)
    dN = BD.laplace_fill(dN, cov)
    sh, c2, s2 = strain(dE, dN, TW, TH)
    # Weight by how much of this cell's displacement was MEASURED rather than
    # solved for. Inside a Laplace-filled basin the solution grades smoothly
    # between the two margins, and differentiating that grade reports a broad
    # sheet of distributed strain across ground where nothing is known -- which
    # is how 70-85% of the globe came out "active" on the first run. The
    # confidence is smoothed rather than binary so a real boundary sitting on
    # the edge of coverage, which is most subduction zones, keeps its signal.
    conf = gaussian_filter(cov.astype(np.float32), (0.0, 3.0), mode="wrap")
    conf = gaussian_filter(conf, (3.0, 0.0), mode="nearest")
    sh = sh * np.clip(conf, 0.0, 1.0)
    # NULL THE FABRIC WHERE THERE IS NO SHORTENING. The axis comes from
    # normalising the deviatoric strain, so as the strain goes to zero the
    # direction it reports goes to noise -- a random orientation at every cell
    # of every plate interior. That is wrong (an undeformed craton has no fold
    # fabric to draw) and it is also what made this texture 273 kB: random
    # high-frequency data does not compress. Fading the axis out with the
    # magnitude fixes both, and takes the file to a fraction of the size.
    # TOPOGRAPHIC FABRIC where the plate solution has nothing to say. Strain
    # wins wherever it is real; topography fills the rest, so the Himalaya keeps
    # its measured collision fabric and the Andes finally gets a strike at all.
    tst, tc2, ts2 = topo_fabric(age)
    if tst is not None:
        take = tst > sh
        c2 = np.where(take, tc2, c2)
        s2 = np.where(take, ts2, s2)
        sh = np.maximum(sh, tst)
    fade = np.clip(sh / (0.10 * SHORT_REF), 0.0, 1.0)
    c2 = c2 * fade
    s2 = s2 * fade
    arr = _encode(sh, c2, s2)
    # The belt-type channel rides in alpha (build_arc.py): arc 1 .. fold belt 0,
    # from the trenches and the land/ocean masks this keyframe already ships.
    # `exact` keeps the RGB under low alpha, which the lossless encoder may
    # otherwise zero (README 7, the fold-coordinate bake).
    import build_arc
    arr = build_arc.attach(arr, age)
    name = "phan_%04d_t.webp" % age if age <= 540 else "pre_%04d_t.webp" % age
    path = os.path.join(OUT, name)
    Image.fromarray(arr, "RGBA").save(path, "WEBP", lossless=True, method=6, exact=True)
    if not quiet:
        print("  %-22s %5.1f kB  shortening p99 %.4f max %.4f  active %.1f%%  %.1fs"
              % (name, os.path.getsize(path) / 1024.0, np.percentile(sh, 99),
                 sh.max(), 100 * float((sh > 0.004).mean()), time.time() - t0))
    return float(np.percentile(sh, 99.9))


def _selftest():
    import pygplates as pg
    ok = True

    # A pure east-west squeeze must report shortening, and its fold axis must
    # run NORTH-SOUTH. If this comes out perpendicular every range in the app
    # gets a fabric at right angles to itself, which would look deliberate.
    h, w = 64, 128
    _LON, LAT = PF._grid(w, h)
    xx = np.linspace(-1, 1, w)[None, :] * np.ones((h, 1))
    dE = -xx * 0.5           # converging toward lon 0
    dN = np.zeros_like(dE)
    sh, c2, s2 = strain(dE, dN, w, h)
    mid = (slice(h // 2 - 4, h // 2 + 4), slice(w // 2 - 4, w // 2 + 4))
    if sh[mid].mean() <= 0:
        print("  FAIL pure convergence reports no shortening")
        ok = False
    # extension axis (fold axis) should be north-south => 2t = 180 => c2 = -1
    if c2[mid].mean() > -0.9:
        print("  FAIL fold axis is not perpendicular to shortening (c2=%.2f)" % c2[mid].mean())
        ok = False

    # Pure extension must report ZERO shortening -- a ridge is not an orogen.
    sh2, _c, _s = strain(xx * 0.5, np.zeros_like(dE), w, h)
    if sh2[mid].mean() > 1e-9:
        print("  FAIL pure extension reports shortening")
        ok = False

    # A rigid translation must report no strain at all, or every plate interior
    # would grow a fabric it has no business having.
    sh3, _c, _s = strain(np.full((h, w), 0.7), np.full((h, w), -0.3), w, h)
    if sh3.max() > 1e-6:
        print("  FAIL rigid translation reports strain %.3g" % sh3.max())
        ok = False

    # The double angle must survive a round trip through the byte.
    for t in (0.0, 30.0, 89.0, 179.0):
        c, s = np.cos(np.radians(2 * t)), np.sin(np.radians(2 * t))
        px = _encode(np.zeros((2, 2)), np.full((2, 2), c), np.full((2, 2), s))[0, 0]
        back = 0.5 * np.degrees(np.arctan2(px[2] / 255.0 * 2 - 1, px[1] / 255.0 * 2 - 1)) % 180
        if min(abs(back - t), 180 - abs(back - t)) > 1.0:
            print("  FAIL fold axis round-trip %.0f -> %.1f" % (t, back))
            ok = False

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


def main():
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    import pygplates as pg
    import paleo_tracks as PT
    rot = pg.RotationModel(PT.ROT)
    args = [int(a) for a in sys.argv[1:] if not a.startswith("--")]
    ages = args or list(range(0, 1000, 5))
    print("baking %d tectonic fields at %dx%d" % (len(ages), TW, TH))
    t0 = time.time()
    peaks = [bake(age, rot) for age in ages]
    print("\n  %d fields, %.1f min. Shortening p99.9 across the series: "
          "median %.4f, max %.4f (SHORT_REF %.3f)"
          % (len(ages), (time.time() - t0) / 60.0,
             float(np.median(peaks)), float(np.max(peaks)), SHORT_REF))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
