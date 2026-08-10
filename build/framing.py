"""What ground does a shot at a given zoom actually cover?

Every measurement that compares the render against anything -- a reference
image, a field, another shot -- needs this, and until now every one of them
guessed. The guesses have been expensive: an assumed half-width cost the ocean
audit nine rounds of pairing pixels with the wrong depths, and an assumed
`45/zoom` cost a whole close-zoom round that turned out to have been shot at
the widest view in the app.

MEASURED, not derived. One framing that straddles a real coastline (head of the
Adriatic, 13.5E 45.5N) shot at five zooms, each fitted by matching the rendered
land mask's row profile against the shipped elevation field:

    zoom   half-height   fit err   km across   km/px at 760
    1.40      6.30 deg   0.00070        1399         1.84
    2.00     17.40 deg   0.01878        3863         5.08
    2.80     24.90 deg   0.03141        5528         7.27
    3.80     80.30 deg   0.02308       17827        23.46
    5.00     88.80 deg   0.04072       19714        25.94

TWO THINGS THIS TABLE SAYS, and the second is the important one.

1. Zoom is a camera DISTANCE, clamped by the app to [1.35, 5], and SMALLER IS
   CLOSER. 5.0 is the whole globe -- 53% of the frame is empty space around the
   limb -- and 1.4 is as close as the app goes, about 1.84 km/px. shoot.py
   refuses anything outside the range rather than silently clamping.

2. IT IS ONLY TRUSTWORTHY AT THE CLOSE END. The fit error rises 30-60x from
   zoom 1.4 to the wide end, because past about zoom 2 the frame stops being a
   lat/lon box: it is a curved cap of a sphere, and no single half-width
   describes it. At 5.0 the fitted 88.8 degrees is most of a hemisphere and the
   flat-box model behind that number has stopped meaning anything.

   So: a matched-resolution comparison against an external reference is VALID at
   zoom 1.4-2.0 and NOT valid at the wide end without a real spherical
   reprojection. Wide-zoom framings are for looking at, and for statistics that
   do not need to know where a pixel is.

`km_per_px` returns (km_per_px, fit_error, trustworthy) and callers are expected
to branch on the third value rather than quietly using a number the fit does not
support.
"""
import bisect

# zoom -> (half-height degrees, fit error). See the table above.
TABLE = [(1.40, 6.30, 0.00070),
         (2.00, 17.40, 0.01878),
         (2.80, 24.90, 0.03141),
         (3.80, 80.30, 0.02308),
         (5.00, 88.80, 0.04072)]
# Above this fit error the flat lat/lon-box model is not describing the frame.
# 0.02 sits between zoom 1.4's 0.0007 and zoom 2.8's 0.031, and admits zoom 2.0
# at 0.0188 -- the widest framing where a pixel's ground position is meaningful.
TRUST_ERR = 0.02
ZOOM_MIN, ZOOM_MAX = 1.35, 5.0


def half_degrees(zoom):
    """Angular half-height at this zoom, linearly interpolated in the table."""
    if zoom <= TABLE[0][0]:
        return TABLE[0][1], TABLE[0][2]
    if zoom >= TABLE[-1][0]:
        return TABLE[-1][1], TABLE[-1][2]
    i = bisect.bisect_left([t[0] for t in TABLE], zoom)
    z0, h0, e0 = TABLE[i - 1]
    z1, h1, e1 = TABLE[i]
    f = (zoom - z0) / (z1 - z0)
    return h0 + f * (h1 - h0), max(e0, e1)


def km_per_px(zoom, px=760):
    """(km_per_px, fit_error, trustworthy) for a square shot `px` across.

    Vertical scale, in degrees of LATITUDE, so there is no cos(lat) term -- the
    fit is on the row profile. An earlier version multiplied by cos(lat) and
    was wrong by 30% at 45 degrees for exactly that reason.
    """
    if not (ZOOM_MIN <= zoom <= ZOOM_MAX):
        raise ValueError(
            "zoom %r is outside the app's [%g, %g]; it would clamp, and the "
            "framing would not be the one asked for" % (zoom, ZOOM_MIN, ZOOM_MAX))
    half, err = half_degrees(zoom)
    return (2.0 * half * 111.0) / px, err, err <= TRUST_ERR


def selftest():
    ok = True
    for z, h, _ in TABLE:
        got, _, _ = km_per_px(z)
        want = 2.0 * h * 111.0 / 760.0
        if abs(got - want) > 1e-6:
            print("    zoom %.2f: %.4f != %.4f" % (z, got, want))
            ok = False
    _, _, near = km_per_px(1.4)
    _, _, far = km_per_px(5.0)
    if not near or far:
        print("    trust flags wrong: close should be trusted, wide should not")
        ok = False
    try:
        km_per_px(16.0)
        print("    an out-of-range zoom did not raise")
        ok = False
    except ValueError:
        pass
    print("  framing selftest: %s" % ("ok" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    print("  zoom -> ground scale for a 760 px shot")
    print("    %6s %11s %10s %11s" % ("zoom", "km/px", "fit err", "trustworthy"))
    for z in (1.4, 1.7, 2.0, 2.4, 2.8, 3.8, 5.0):
        k, e, t = km_per_px(z)
        print("    %6.2f %11.2f %10.5f %11s" % (z, k, e, "yes" if t else "NO"))
    sys.exit(selftest())
