"""Does close-zoom land grain track how rugged the ground actually is?

WHY THIS FILE STARTS WITH A SELF-TEST. The first version of this measurement
band-passed at RELATIVE scales -- a half-size and a sixth-size resample of
whatever image it was handed. On any roughly self-similar spectrum that ratio is
nearly constant, so it returned ~0.09 for the Alps, ~0.09 for the West Siberian
Lowland, ~0.09 with all procedural elevation detail switched OFF, ~0.09 with the
land normal octaves switched off, and the same to within 0.07% across a 1.66x
change in render scale. Four sites, four shader variants, two capture sizes, one
number. It was measuring its own construction.

So the metric here works in ABSOLUTE KILOMETRES -- a difference-of-Gaussians
whose sigmas are computed from each shot's own km/px -- and it refuses to report
anything until it has separated two pairs whose answer is known in advance:

    detail ON vs detail OFF   the same framing with `det` forced to zero. If a
                              metric cannot see the removal of the only relief a
                              plain has, it cannot see relief.
    rugged vs flat            the Alps against the West Siberian Lowland, which
                              differ 23x in the shipped field (133.5 vs 5.8 m
                              between adjacent 10 km cells).

THE QUESTION IT ASKS. Past about zoom 4 every bit of ground texture is
synthesised: `_e` is 4096x2048, about 9.8 km per cell, and there is nothing
finer to interpolate. Synthesis is free to be uniform, and uniform is wrong --
real 1 km roughness spans orders of magnitude between an alpine valley wall and
a sedimentary basin. This measures whether the render keeps that distinction
where no data survives to enforce it.

NO EXTERNAL REFERENCE IS VALID FOR THIS BAND and no number here pretends
otherwise. Blue Marble is 7.4 km/px, so it cannot carry 1-5 km detail, and its
land luminance carries no hillshade at any scale (iteration 82). The comparison
is between our own sites, ranked by the shipped field's own ruggedness.

    ../venv/bin/python shoot.py --nolabels gl_alpsC,8,46.5,0,1.4 \\
        gl_wsibC,68,60,0,1.4 gl_amazC,-60,-3,0,1.4 gl_sahfC,10,22,0,1.4
    ../venv/bin/python audit_land_grain.py
"""
import os
import sys

import numpy as np
from PIL import Image

import framing

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify")
FIELD = os.path.join(HERE, "..", "web", "fields", "phan_0000_e.avif")
Z_RANGE = 8000.0
# The band to look in, kilometres. This was 1.5-5.0 km, chosen for a "zoom 16"
# that does not exist: the app stops at 1.84 km/px, so a 1.5 km wavelength is
# 0.8 px -- under Nyquist, unmeasurable, and not on screen for any user either.
# 6-20 km is the finest band the closest view can actually resolve, and it
# straddles the shipped field's own 9.8 km cell, which is the interesting place:
# below it the shader is inventing, above it the data is speaking.
BAND_KM = (6.0, 20.0)
# Wavelength per unit sigma, CALIBRATED against the filter's measured response
# rather than derived. At the textbook sigma = lambda/2 this difference-of-
# Gaussians peaked at 6.8 km while claiming a 1.5-5 km band -- a label that
# does not match the instrument is how a measurement ends up answering a
# different question than the one written above it.
SIG_K = 5.0
# The app's zoom is a camera DISTANCE clamped to [1.35, 5] and SMALLER IS
# CLOSER. 1.4 is as close as the app goes; 5.0 shows the whole globe with 53%
# of the frame empty. Asking for 16 renders at 5 -- shoot.py now refuses it.
ZOOM = 1.4
# km/px at ZOOM, DERIVED by fitting the land-mask row profile of a framing that
# straddles a real coastline (head of the Adriatic, 13.5E 45.5N): half-height
# 6.30 degrees of latitude, fit error 0.00070. The same fit on a frame that is
# 78% land rails at the search floor and returns nonsense, which is why the
# calibration site has a coastline in it and the sites being measured need not.
KMPX = 2.0 * 6.30 * 111.0 / 760.0
# (name, shot, lon, lat). Ruggedness is READ FROM THE FIELD at run time, never
# hard-coded, so the ranking cannot go stale against a re-bake.
SITES = [("Alps", "gl_alpsC", 8.0, 46.5),
         ("W Siberia", "gl_wsibC", 68.0, 60.0),
         ("Amazon", "gl_amazC", -60.0, -3.0),
         ("Sahara flat", "gl_sahfC", 10.0, 22.0)]
# The render must keep at least this much of the field's own spread. The field
# spans 23x; demanding 23x back would be wrong -- hillshade compresses, and a
# plain should not be pure flat -- but collapsing to 1.2x is the defect.
MIN_SPREAD = 2.0


def gauss(x, sigma):
    """Separable Gaussian blur, sigma in pixels, REFLECT-padded.

    numpy's mode="same" zero-pads. On a render whose land sits around
    luminance 120 that is a 120-level cliff around all four borders, and the
    difference-of-Gaussians turns it into a bright frame that dominates the
    statistic: with it in place this filter answered 0.27 to a 1 km signal and
    0.27 to an 80 km one, which is no band-pass at all. Reflecting instead
    matches the analytic transfer function to three decimals.
    """
    if sigma < 0.5:
        return x.copy()
    r = max(int(4 * sigma), 1)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    out = np.pad(x, ((r, r), (0, 0)), mode="reflect")
    out = np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 0, out)
    out = np.pad(out, ((0, 0), (r, r)), mode="reflect")
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 1, out)


def land_mask(im):
    return ~((im[:, :, 2] > im[:, :, 1] + 4) & (im[:, :, 2] > im[:, :, 0] + 10))


def grain(path, kmpx, band=BAND_KM):
    """RMS of the ABSOLUTE-kilometre band, relative to local mean luminance."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(float)
    lum = im.mean(axis=2)
    m = land_mask(im) & (lum > 6)
    if m.sum() < 2000:
        return float("nan")
    s_lo, s_hi = band[0] / kmpx / SIG_K, band[1] / kmpx / SIG_K
    dog = gauss(lum, s_lo) - gauss(lum, s_hi)
    return float(dog[m].std() / max(lum[m].mean(), 1e-6))


def km_per_px(path, lat, lon=None):
    """DERIVE the scale from the shot's own land mask. Never assume it.

    This began as (45/zoom) degrees of half-width, which is a guess about what
    the camera covers, and a guess is how the ocean audit spent nine rounds
    pairing pixels with the wrong depths. It also had a specific tell: with the
    assumed scale the 1.5-5 km band read 0.099 on West Siberian LAND and 0.103
    on the sea in the same frame, and 0.097 / 0.120 for the Alps. A band that
    cannot tell land from ocean is not measuring the band it claims to.

    Fitted by matching the rendered land mask's row profile against the shipped
    field over a range of half-widths, the same construction audit_ocean_tone
    uses. Returns (km_per_px, half_degrees) so callers can report what was
    actually fitted rather than what was hoped for.
    """
    im = np.asarray(Image.open(path).convert("RGB")).astype(float)
    prof = land_mask(im).mean(axis=1)
    e = np.asarray(Image.open(FIELD).convert("L")).astype(float) / 255.0
    d = e * 2.0 - 1.0
    z = np.sign(d) * d * d * Z_RANGE
    eh, ew = z.shape
    best = None
    for half in np.arange(0.6, 24.01, 0.2):
        r0 = int((90 - (lat + half)) / 180 * eh)
        r1 = int((90 - (lat - half)) / 180 * eh)
        c0 = int((lon - half + 180) / 360 * ew)
        c1 = int((lon + half + 180) / 360 * ew)
        if r1 - r0 < 3 or c1 - c0 < 3:
            continue
        lm = (z[r0:r1, c0:c1] > 0).astype(np.float32)
        p = np.array(Image.fromarray(lm).resize((1, len(prof)), Image.BILINEAR)).ravel()
        err = float(np.mean((p - prof) ** 2))
        if best is None or err < best[0]:
            best = (err, half)
    half = best[1]
    return (2.0 * half * 111.0 * np.cos(np.radians(lat))) / im.shape[1], half


def field_rugged(lon, lat, half=3.0):
    e = np.asarray(Image.open(FIELD).convert("L")).astype(float) / 255.0
    d = e * 2.0 - 1.0
    z = np.sign(d) * d * d * Z_RANGE
    eh, ew = z.shape
    s = z[int((90 - (lat + half)) / 180 * eh):int((90 - (lat - half)) / 180 * eh),
          int((lon - half + 180) / 360 * ew):int((lon + half + 180) / 360 * ew)]
    s = np.where(s > 0, s, np.nan)
    return float(np.nanmean(np.concatenate(
        [np.abs(np.diff(s, axis=0)).ravel(), np.abs(np.diff(s, axis=1)).ravel()])))


def selftest():
    """Refuse to report until the metric has separated two known pairs.

    Returns (ok, lines). The detail-on/off pair is only available when the
    A/B shots exist; when they do not, that half is reported as untested
    rather than quietly passing -- a validator that prints "ok" for a check it
    skipped is the failure mode audit_island_biomes was rebuilt around.
    """
    lines, ok, hard = [], True, True
    synth_ok = None
    n = 512
    y, x = np.indices((n, n)).astype(float)
    # Two synthetic fields with the SAME mean and total contrast, differing only
    # in which band carries it: one at 11 km (in band), one at 150 km (out).
    fine = (120 + 18 * np.sin(2 * np.pi * x * KMPX / 11.0)
            * np.sin(2 * np.pi * y * KMPX / 11.0))
    coarse = (120 + 18 * np.sin(2 * np.pi * x * KMPX / 150.0)
              * np.sin(2 * np.pi * y * KMPX / 150.0))
    m = np.ones((n, n), bool)

    def g(a):
        s_lo, s_hi = BAND_KM[0] / KMPX / SIG_K, BAND_KM[1] / KMPX / SIG_K
        d = gauss(a, s_lo) - gauss(a, s_hi)
        return float(d[m].std() / a[m].mean())
    gf, gc = g(fine), g(coarse)
    synth_ok = gf > 6 * gc
    lines.append("    in-band 11 km %.4f vs out-of-band 150 km %.4f  (%.0fx)  %s"
                 % (gf, gc, gf / max(gc, 1e-9), "ok" if synth_ok else "FAILS"))
    ok = ok and synth_ok

    pair = [("CB_gl_wsibC", "detail ON"), ("CD_gl_wsibC", "detail OFF")]
    have = all(os.path.exists(os.path.join(VERIFY, p + ".png")) for p, _ in pair)
    if not have:
        # The synthetic half proves the FILTER and needs nothing on disk, so it
        # blocks. This half proves end-to-end sensitivity to a real shader lever
        # and needs A/B artefacts that only exist in a round that made them --
        # so it reports UNTESTED loudly and does not block a routine build. The
        # distinction matters: never confuse "did not run" with "passed", and
        # never make a build depend on a screenshot from a previous experiment.
        lines.append("    detail on/off pair NOT PRESENT -- that half is "
                     "UNTESTED (does not block; the synthetic half still does)")
    else:
        vals = [grain(os.path.join(VERIFY, p + ".png"), KMPX)
                for p, _ in pair]
        sep = abs(vals[0] - vals[1]) / max(vals[0], 1e-9)
        # 10%, and the number this bar exists to beat is ZERO: the relative-
        # scale metric this replaced moved 0.0% when the same lever was pulled.
        # Measured at the time of writing, 14%. Set the bar BELOW that on
        # purpose and record both, because a threshold quietly nudged under
        # whatever today's build happens to produce is not a test.
        good = sep > 0.10
        lines.append("    detail ON %.4f vs OFF %.4f  (%.0f%% apart)  %s"
                     % (vals[0], vals[1], 100 * sep, "ok" if good else "FAILS"))
        ok = ok and good
        hard = hard and good
    return ok, lines


def main():
    print("  land grain in an ABSOLUTE %.1f-%.1f km band, zoom %.0f"
          % (BAND_KM[0], BAND_KM[1], ZOOM))
    print("  self-test (the metric must separate known pairs before it reports):")
    ok, lines = selftest()
    for ln in lines:
        print(ln)
    if not ok:
        print("  audit_land_grain: SELF-TEST FAILED -- reporting no site numbers.")
        print("  The previous metric passed everything because it separated")
        print("  nothing; a number from an unvalidated instrument is worse than")
        print("  no number.")
        return 1

    rows, missing = [], []
    present = [x for x in SITES
               if os.path.exists(os.path.join(VERIFY, x[1] + ".png"))]
    if not present:
        print("  no close-zoom shots present -- nothing measured, not blocking.")
        print("  See the usage in the docstring; the round that changes land")
        print("  detail is the round that owes this fresh ones.")
        return 0
    print("    %-12s %13s %11s" % ("site", "field m/cell", "grain"))
    for name, shot, lon, lat in SITES:
        p = os.path.join(VERIFY, shot + ".png")
        if not os.path.exists(p):
            missing.append(name)
            continue
        g = grain(p, KMPX)
        r = field_rugged(lon, lat)
        rows.append((name, r, g))
        print("    %-12s %13.1f %11.4f" % (name, r, g))
    if missing:
        print("  %d site(s) have no shot and were NOT tested: %s"
              % (len(missing), ", ".join(missing)))
        return 1
    a = np.array([[r, g] for _, r, g in rows])
    fs = a[:, 0].max() / max(a[:, 0].min(), 1e-9)
    gs = a[:, 1].max() / max(a[:, 1].min(), 1e-9)
    print("    field spread %.1fx    rendered spread %.2fx    (floor %.1fx)"
          % (fs, gs, MIN_SPREAD))
    if gs < MIN_SPREAD:
        print("  close-zoom grain is relief-BLIND: every landscape draws the same")
        print("  crumple where no data survives to say otherwise.")
        return 1
    print("  close-zoom grain still tracks the ground it is standing on")
    return 0


if __name__ == "__main__":
    sys.exit(main())
