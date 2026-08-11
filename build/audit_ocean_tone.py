"""Ocean tone against Blue Marble: depth contrast AND broad tonal variation.

Two quantities, and the whole history of this palette is that tuning either one
alone moves the other the wrong way:

  DEPTH SPAN     how much darker the abyss is than the rise. Measured on the
                 rendered frame, binned by the shipped elevation field, in the
                 same sRGB pixel values on both sides.
  BROAD SHARE    the fraction of the ocean's spatial variance at wavelengths
                 longer than 250 km. This is the quantity G3 used to narrow the
                 ramp -- it found ours carrying 20-47% against the reference's
                 13-16% -- and it existed only as a note until now.

BLUE MARBLE'S OCEAN IS A VALID REFERENCE HERE, which iteration 128 had to check
before trusting: its ocean luminance correlates +0.823 with the source DEM's
depth, running 9.0 at -5,500 m to 56.2 at -1,500 m. NASA composited a
bathymetric ocean into it. That is not true of its LAND luminance, which carries
no hillshade (iteration 82) -- the two halves of the same image have to be
trusted separately.

MATCHED RESOLUTION IS A PRECONDITION. Our shot is about 1 km/px and Blue Marble
is 7.4; comparing them raw reads our 1-7 km detail against a band the reference
cannot carry, which is the error that cost iterations 96-98. Ours is
box-downsampled to the reference pitch before either number is computed.

AND BOTH SIDES IN ONE COLOUR SPACE. The palette's constants are LINEAR and the
framebuffer is sRGB; iteration 129 compared a linear ramp figure against an sRGB
measurement and concluded the ramp was inert when it was doing exactly what it
specified. Everything here is sRGB pixel values, on both sides.

Measured at the time of writing, equatorial Atlantic:

    quantity                    ours    Blue Marble
    depth span -5,500..-2,500   0.94x        3.79x
    broad share (>250 km)         see the run -- G3's 20-47% vs 13-16%

    ../venv/bin/python audit_ocean_tone.py
"""
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
BM_PATH = os.path.join(HERE, "..", "data", "bluemarble.jpg")
FIELD = os.path.join(HERE, "..", "web", "fields", "phan_0000_e.avif")
VERIFY = os.path.join(HERE, "verify")
SHOT = "oc_atl2"
# DERIVED, not assumed. The first value here was a guess at what zoom 2.2 covers
# and it was half the true width, so every depth bin paired pixels with the wrong
# depth -- pixels labelled -3,500 m were really shelf, where the river plume is
# active, which is why the residual came out plume-coloured. Fitted by matching
# the shot's own land mask row-profile against the field over a range of
# half-widths: best at 12.5 degrees, error 0.00034, against 6.5 assumed.
#
# Re-derive this whenever the framing changes. A framing taken on faith is the
# same failure as a reference taken on faith.
BOX = (-42.5, -17.5, -12.5, 12.5)   # oc_atl2 at zoom 2.2, middle 60%, derived
Z_RANGE = 8000.0
BROAD_KM = 250.0
# ABSOLUTE LUMINANCE BY DEPTH, and it is here because its absence shipped a
# defect the user reported before any gate did: "our ocean floor is far too
# dark". Span and broad-share are both RATIOS, and a ratio is improved by
# darkening the deep end -- which is what iteration 131-134 did taking the span
# from 1.35 to 2.83. Nothing in this file constrained the level, so the palette
# was free to walk down until the whole sea read as abyss, and it did: measured,
# the deepest water came out 1.52x the reference's while everything above -4000 m
# came out 0.73-0.87x.
#
# Blue Marble's ocean luminance is a valid reference for this (+0.823 with the
# source DEM's depth, and it is a composited bathymetric ocean), at matched
# resolution and in the same colour space -- the two preconditions this file
# already enforces for the span.
LEVEL_BANDS = [(-6000, -5000), (-5000, -4000), (-4000, -3000),
               (-3000, -2000), (-2000, -1000), (-1000, -200)]
# BLUE MARBLE GOVERNS THE SHAPE, NOT THE LEVEL, and this file learned that the
# expensive way. Fitting the absolute level to Blue Marble was achieved -- RMS
# 2.21 across the bands above -- and the mid-Pacific still rendered black,
# because Blue Marble is a PHOTOGRAPH of water that returns almost no light from
# 5 km down. The brief is Google-Earth-equivalent, and a bathymetric
# visualisation stays legibly blue at every depth because its job is to show the
# sea floor.
#
# So the level is checked against what the app is FOR, in two directions:
#
#   ABYSS_MIN   the deepest water must remain readable. Below this the sea floor
#               stops being visible at all, which is the defect the user
#               reported ("our ocean floor is far too dark") while every ratio
#               in this file was passing. The originally shipped ramp sat at 10.
#   CLIP_MAX    and the shallow end must not blow out paying for it. The chosen
#               ramp clips 4.9% of shelf water in one channel, against 0.14%
#               before and 23.4% for a ramp one step brighter; what clips is the
#               sunlit carbonate banks, which really are near-white.
ABYSS_MIN = 18.0
CLIP_MAX = 9.0


def dec(e):
    d = e * 2.0 - 1.0
    return np.sign(d) * d * d * Z_RANGE


def broad_share(lum, mask, kmpx):
    """Fraction of the ocean's variance at wavelengths longer than BROAD_KM.

    Computed as a variance ratio rather than an FFT, because the mask is
    irregular (land, cloud and ice are excluded) and a windowed FFT of a masked
    field mostly measures the mask. Smoothing to 250 km and comparing variances
    answers the same question and cannot be fooled by hole shape.
    """
    v = np.where(mask, lum, np.nan)
    n = max(int(round(BROAD_KM / kmpx)), 2)
    small = (max(lum.shape[1] // n, 2), max(lum.shape[0] // n, 2))
    filled = np.where(mask, lum, np.nanmean(v))
    lo = np.array(Image.fromarray(filled.astype(np.float32)).resize(small, Image.BILINEAR)
                  .resize((lum.shape[1], lum.shape[0]), Image.BILINEAR))
    tot = np.nanvar(v)
    broad = np.nanvar(np.where(mask, lo, np.nan))
    return float(broad / tot) if tot > 1e-9 else float("nan")


def main():
    shot = os.path.join(VERIFY, SHOT + ".png")
    if not os.path.exists(shot):
        print("  audit_ocean_tone: shoot %s,-30,0,0,2.2 first" % SHOT)
        return 1
    BM = np.asarray(Image.open(BM_PATH).convert("RGB")).astype(float)
    H, W, _ = BM.shape
    bm_kmpx = 40075.0 / W
    lo0, lo1, la0, la1 = BOX

    E = dec(np.asarray(Image.open(FIELD).convert("L")).astype(float) / 255.0)
    eh, ew = E.shape
    sub = E[int((90 - la1) / 180 * eh):int((90 - la0) / 180 * eh),
            int((lo0 + 180) / 360 * ew):int((lo1 + 180) / 360 * ew)]

    im = np.asarray(Image.open(shot).convert("RGB")).astype(float)
    im = im[im.shape[0] // 5:4 * im.shape[0] // 5, im.shape[1] // 5:4 * im.shape[1] // 5]
    # MATCHED RESOLUTION: ours down to Blue Marble's pitch, by BOX so it averages
    km_ours = (lo1 - lo0) * 111.0 * np.cos(np.radians((la0 + la1) / 2)) / im.shape[1]
    k = max(int(round(bm_kmpx / km_ours)), 1)
    small = (max(im.shape[1] // k, 8), max(im.shape[0] // k, 8))
    ours = np.asarray(Image.fromarray(im.astype(np.uint8)).resize(small, Image.BOX)).astype(float)

    r0, r1 = int((90 - la1) / 180 * H), int((90 - la0) / 180 * H)
    c0, c1 = int((lo0 + 180) / 360 * W), int((lo1 + 180) / 360 * W)
    ref = BM[r0:r1, c0:c1]
    D = np.array(Image.fromarray(sub.astype(np.float32)).resize(
        (ours.shape[1], ours.shape[0]), Image.BILINEAR))
    Dref = np.array(Image.fromarray(sub.astype(np.float32)).resize(
        (ref.shape[1], ref.shape[0]), Image.BILINEAR))

    print("  ours downsampled %dx to %.1f km/px, matching Blue Marble" % (k, bm_kmpx))
    print("  %-28s %10s %14s" % ("quantity", "ours", "Blue Marble"))
    out = {}
    for lab, im_, d_ in (("ours", ours, D), ("bm", ref, Dref)):
        lum = im_.mean(axis=2)
        # The blue test is for Blue Marble, whose land is brown; our render's
        # deep water can be dark enough that B-G falls under 4, so gate on the
        # DEPTH FIELD as the primary and use colour only to drop ice and cloud.
        water = (d_ < -1000) & (lum > 3) & (im_[:, :, 2] >= im_[:, :, 1])

        def band(a):
            s = water & (d_ >= a) & (d_ < a + 1000)
            return float(lum[s].mean()) if s.sum() > 10 else float("nan")
        deep, mid = band(-5500), band(-2500)
        out[lab] = (mid / deep if deep == deep and deep > 0 else float("nan"),
                    broad_share(lum, water, bm_kmpx))
    # Labelled without digits in the label: a caller parsing this line with a
    # regex for the first number would otherwise capture the "500" of "-5,500".
    print("  %-28s %10.2f %14.2f" % ("depth span deep..mid",
                                     out["ours"][0], out["bm"][0]))
    print("  %-28s %10.2f %14.2f" % ("broad share (>250 km)",
                                     out["ours"][1], out["bm"][1]))
    print("  the two must move together: G3 narrowed the ramp on the second and")
    print("  cost the first, because nothing separated depth from everything else.")

    # ...AND NEITHER OF THEM IS A LEVEL. Both numbers above are ratios and both
    # can be satisfied by a sea that is uniformly too dark to look at.
    print("  %-28s %10s %14s" % ("absolute level by depth", "ours", "Blue Marble"))
    errs = []
    for a, b in LEVEL_BANDS:
        def lvl(im_, d_):
            lum_ = im_.mean(axis=2)
            s = (d_ >= a) & (d_ < b) & (lum_ > 1) & (im_[:, :, 2] >= im_[:, :, 1])
            return float(lum_[s].mean()) if s.sum() > 8 else float("nan")
        o, r = lvl(ours, D), lvl(ref, Dref)
        if o == o and r == r:
            errs.append(o - r)
        print("    %5d..%-6d m %20.1f %14.1f" % (a, b, o, r))
    if not errs:
        print("  no depth band had enough water to measure -- NOT TESTED")
        return 1
    lum = ours.mean(axis=2)
    deep = (D < -4500) & (lum > 1)
    abyss = float(np.median(lum[deep])) if deep.sum() > 40 else float("nan")
    wet = (D < -50) & (lum > 2)
    clip = 100.0 * float((ours[wet].max(axis=1) >= 250).mean()) if wet.sum() > 40 \
        else float("nan")
    print("  abyss median %.1f (floor %.1f)   channel-clipped water %.2f%% "
          "(ceiling %.1f%%)" % (abyss, ABYSS_MIN, clip, CLIP_MAX))
    bad = 0
    if not (abyss >= ABYSS_MIN):
        print("  THE SEA FLOOR IS TOO DARK TO READ, whatever its contrast is.")
        bad = 1
    if not (clip <= CLIP_MAX):
        print("  the shallow end is blowing out paying for the deep end.")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
