"""Why mountains do not appear to EMERGE: measure the keyframe transition.

The complaint this answers is that the app's mountain belts, seabeds and other
places where crust piles up are in the right place at the right height, but do
not look as though they got there by colliding. That is a claim about the
TRANSITION between keyframes, not about the keyframes, so this script measures
the transition.

WP-06's method rule applies and is the reason this file exists at all:
*measure the artefact's scale before matching it to a candidate.* Four fixes
were tried on the ocean staircase before anyone measured that the symptom was
tens of pixels across and the leading candidate was four. So here every
mechanism gets a number, and the numbers are in the units the fix will be
written in -- texels of the shipped 4096-wide elevation grid, and metres per
5 Myr keyframe step.

Read-only. Touches nothing in build/ or web/. Reads the SHIPPED fields, so it
measures what a viewer actually sees rather than what the source data says.

    ../../venv/bin/python audit_terrain_motion.py            # all three
    ../../venv/bin/python audit_terrain_motion.py --quick    # (a) only, no image reads

Needs pyGPlates and the PALEOMAP rotations for (a); degrades honestly without
them rather than reporting a smaller number.
"""
import os
import sys

BASELINE = {
    # Adopted 2026-07-29 as the state of the defect BEFORE any fix, so the
    # ratchet in build/audit_all.py can be pointed at this once H1 lands.
    # These must go DOWN. See NO-REGRESSION-PROTOCOL.md section 5.
    #
    # Recorded to the precision they were measured at. Rounding them UP would
    # make the very next run report an improvement that did not happen, which
    # is how a ratchet quietly stops ratcheting.
    "median_texel_displacement_400Ma": 41.95,
    "max_texel_displacement": 64.73,
    "largest_single_step_metres": 5889.67,
    "hypsometry_spike_pp": 2.80,
}

# Below this, a difference is re-measurement noise rather than a change. Without
# it every run prints "better" for the fourth decimal place.
TOL = 0.005

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
FIELDS = os.path.join(ROOT, "web", "fields")

sys.path.insert(0, BUILD)

import numpy as np  # noqa: E402

# The shipped elevation grid. A fix expressed in degrees or kilometres is not
# checkable against a screen; a fix expressed in texels of this grid is.
ELEV_W, ELEV_H = 4096, 2048
TEXEL_PER_DEG = ELEV_W / 360.0
KM_PER_DEG = 111.32
Z_RANGE = 8000.0          # build/fieldpack.py:13 -- keep in step
STEP = 5                  # Myr between keyframes, build_fields.py:98


# --------------------------------------------------------------------------
# field access
# --------------------------------------------------------------------------

def _pil():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    return Image


_CACHE = {}


def field(age, tag="phan"):
    """Decoded elevation in metres for one keyframe, or None if not shipped."""
    key = (tag, age)
    if key in _CACHE:
        return _CACHE[key]
    Image = _pil()
    z = None
    for ext in ("avif", "webp"):
        p = os.path.join(FIELDS, "%s_%04d_e.%s" % (tag, age, ext))
        if os.path.exists(p):
            a = np.asarray(Image.open(p).convert("L")).astype(np.float32) / 255.0
            d = a * 2.0 - 1.0
            z = np.sign(d) * d * d * Z_RANGE     # build/fieldpack.py:22-24
            break
    if len(_CACHE) > 6:
        _CACHE.clear()
    _CACHE[key] = z
    return z


def box(z, lon, lat, dlon, dlat):
    """Sub-array of an equirectangular grid around a centre, in degrees."""
    h, w = z.shape
    x0 = int((lon - dlon + 180) / 360 * w)
    x1 = int((lon + dlon + 180) / 360 * w)
    y0 = int((90 - (lat + dlat)) / 180 * h)
    y1 = int((90 - (lat - dlat)) / 180 * h)
    return z[max(0, y0):min(h, y1), max(0, x0):min(w, x1)]


def reconstructor():
    try:
        import paleo_tracks
        if not paleo_tracks.available():
            return None
        return paleo_tracks.Reconstructor()
    except Exception:
        return None


def tracked(rec, lon, lat, age):
    """Where the crust now at (lon, lat) sat at `age`, in the terrain's frame."""
    if rec is None or age <= 0:
        return lon, lat
    try:
        tr, _pid = rec.track(lon, lat, age, step=STEP)
    except Exception:
        return lon, lat
    return (tr[-1][1], tr[-1][2]) if tr else (lon, lat)


# --------------------------------------------------------------------------
# (a) how far does crust move between two adjacent keyframes?
# --------------------------------------------------------------------------

def measure_displacement(rec, verbose=True):
    """The scale of the cross-dissolve, in texels of the shipped grid.

    `baseElev` is mix(decElev(elevA), decElev(elevB), mixf) -- a cross-fade
    between two stationary images. That is only a motion if the crust barely
    moves between them. This measures whether it does.
    """
    if rec is None:
        print("  (a) SKIPPED -- pyGPlates or the PALEOMAP rotations are unavailable.")
        print("      Not reporting a smaller number in their absence; a missing")
        print("      dependency is not a measurement of zero.")
        return None

    pts = [(lon, lat) for lon in range(-170, 180, 20) for lat in range(-80, 81, 20)]
    rows = []
    for age in (10, 50, 100, 200, 300, 400, 500):
        km = []
        for lon, lat in pts:
            try:
                tr, _pid = rec.track(lon, lat, age, step=STEP)
            except Exception:
                continue
            if len(tr) < 2:
                continue
            (_a1, lo1, la1), (_a0, lo0, la0) = tr[-1], tr[-2]
            dlon = (lo1 - lo0 + 180) % 360 - 180
            mlat = np.radians((la0 + la1) / 2.0)
            km.append(np.hypot(dlon * np.cos(mlat), la1 - la0) * KM_PER_DEG)
        if not km:
            continue
        d = np.asarray(km)
        tex = d / KM_PER_DEG * TEXEL_PER_DEG
        rows.append((age, np.median(d), np.percentile(d, 90), d.max(),
                     np.median(tex), np.percentile(tex, 90), tex.max()))

    if verbose:
        print("  (a) CRUST DISPLACEMENT PER %d-Myr KEYFRAME INTERVAL" % STEP)
        print("      %d present-day points, tracked on the app's own rotations.\n" % len(pts))
        print("      age |      km per step       |   TEXELS per step (4096 grid)")
        print("          |   med    p90    max    |   med    p90    max")
        for r in rows:
            print("     %4d | %5.0f  %5.0f  %5.0f    | %5.1f  %5.1f  %5.1f" % r)

    med400 = next((r[4] for r in rows if r[0] == 400), 0.0)
    mx = max((r[6] for r in rows), default=0.0)
    if verbose:
        print()
        print("      A cross-dissolve spread over %.0f texels is a double exposure," % med400)
        print("      not a motion: relief ghosts into two half-amplitude copies")
        print("      mid-interval and snaps at the keyframe. One texel is ~9.8 km.")
    return {"median_texel_displacement_400Ma": float(med400),
            "max_texel_displacement": float(mx)}


# --------------------------------------------------------------------------
# (b) how much relief arrives in a single keyframe step?
# --------------------------------------------------------------------------

# Orogens whose growth or decay is well enough constrained to be a test case.
# Boxes are present-day; each is back-advected so it follows its own crust.
OROGENS = [
    ("Himalaya / Tibet", 85.0, 30.0, 12.0, 7.0, range(60, -1, -STEP)),
    ("Appalachians", -80.0, 38.0, 8.0, 6.0, range(340, 139, -20)),
    ("Caledonides", -5.0, 60.0, 9.0, 6.0, range(420, 199, -20)),
]


def measure_step(rec, verbose=True):
    """The vertical pop. Relief that arrives in one step cannot look tectonic."""
    worst = 0.0
    worst_where = ""
    for name, lon, lat, dlon, dlat, ages in OROGENS:
        if verbose:
            print("\n  (b) RELIEF PER KEYFRAME STEP -- %s" % name)
            print("      age  trkLon trkLat    p95(m)   step")
        prev = None
        for age in ages:
            z = field(age)
            if z is None:
                continue
            lo, la = tracked(rec, lon, lat, age)
            p95 = float(np.percentile(box(z, lo, la, dlon, dlat), 95))
            delta = "" if prev is None else "  %+7.0f m" % (p95 - prev)
            if prev is not None and abs(p95 - prev) > abs(worst):
                worst, worst_where = p95 - prev, "%s at %d Ma" % (name, age)
            if verbose:
                print("     %4d  %6.1f %6.1f   %7.0f%s" % (age, lo, la, p95, delta))
            prev = p95
    if verbose and worst_where:
        print()
        print("      Largest single-step change: %+.0f m (%s)." % (worst, worst_where))
        print("      Rendered as a linear ramp in mixf, a whole plateau inflates")
        print("      uniformly in place -- no propagation from the suture, no")
        print("      crumpling front, no foreland. That is the reported symptom.")
    return {"largest_single_step_metres": float(abs(worst))}


# --------------------------------------------------------------------------
# (c) is the source series itself temporally jumpy?
# --------------------------------------------------------------------------

def measure_jumpiness(lo=0, hi=120, verbose=True):
    """Authoring noise in RELIEF, the sibling of the one G1 found in shelf area.

    G1 recorded that the raw PaleoDEMs swing 8.6 -> 4.5 -> 3.0 -> 6.3 -> 1.6 ->
    8.2 -> 13.8% shallow sea across seven adjacent frames while sea level slides
    smoothly, "which is authoring and not geology". This asks the same question
    of land above 1 km, which no eustatic curve can move at all.
    """
    ser = []
    for age in range(lo, hi + 1, STEP):
        z = field(age)
        if z is None:
            continue
        ser.append((age, (z > 0).mean() * 100, (z > 1000).mean() * 100,
                    (z > 2000).mean() * 100))
    if verbose:
        print("\n  (c) FRAME-TO-FRAME HYPSOMETRY, %d-%d Ma" % (lo, hi))
        print("      Geology is smooth here; a spike that reverts on the next")
        print("      frame is the source series, not the Earth.\n")
        print("      age   land%   >1km%  >2km%  |  d(>1km)")
    spike = 0.0
    spike_at = None
    for i, (age, land, k1, k2) in enumerate(ser):
        d = "" if i == 0 else "  %+5.2f pp" % (k1 - ser[i - 1][2])
        if i and abs(k1 - ser[i - 1][2]) > spike:
            spike, spike_at = abs(k1 - ser[i - 1][2]), age
        if verbose:
            print("     %4d   %5.1f   %5.2f  %5.2f  |%s" % (age, land, k1, k2, d))
    if verbose and spike_at is not None:
        print()
        print("      Largest single-frame move in land above 1 km: %.2f pp at %d Ma."
              % (spike, spike_at))
        print("      For scale, 1 pp of the globe is ~1.5 Mkm2 -- a third of the")
        print("      Alpine-Himalayan belt appearing and vanishing in 5 Myr.")
    return {"hypsometry_spike_pp": float(spike)}


# --------------------------------------------------------------------------

def selftest():
    """Adversarial, per the rule that a check which cannot fail is not a check."""
    ok = True

    # The encoder round-trips. If this drifts, every metre in this file is wrong.
    for m in (-6000.0, -350.0, 0.0, 1500.0, 7900.0):
        e = 0.5 + 0.5 * np.sign(m) * np.sqrt(abs(m) / Z_RANGE)
        d = e * 2.0 - 1.0
        back = np.sign(d) * d * d * Z_RANGE
        if abs(back - m) > 1.0:
            print("  FAIL encoder round-trip: %.0f -> %.0f" % (m, back))
            ok = False

    # box() must not silently return an empty slice -- that reads as "no relief".
    z = np.zeros((ELEV_H, ELEV_W), np.float32)
    for lon, lat in ((0, 0), (179, 89), (-179, -89)):
        if box(z, lon, lat, 5.0, 5.0).size == 0:
            print("  FAIL box() empty at (%s, %s)" % (lon, lat))
            ok = False

    # A texel figure that does not match the grid the shader samples is useless.
    if abs(TEXEL_PER_DEG - ELEV_W / 360.0) > 1e-9:
        print("  FAIL texel scale does not match ELEV_W")
        ok = False

    # The fields must actually be present. Reporting "0 m of change" because
    # nothing loaded is exactly the failure mode audit_labels.field() had.
    if field(0) is None:
        print("  FAIL no shipped elevation field at 0 Ma -- results would be vacuous")
        ok = False

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


def main():
    quick = "--quick" in sys.argv
    print(__doc__.split("\n")[0])
    print("=" * 74)
    if not selftest():
        return 1
    print()
    rec = reconstructor()
    if rec is None:
        print("  note: reconstructor unavailable -- (a) will be skipped.\n")

    got = {}
    got.update(measure_displacement(rec) or {})
    if not quick:
        got.update(measure_step(rec) or {})
        got.update(measure_jumpiness() or {})

    print("\n" + "=" * 74)
    print("  AGAINST BASELINE (these must go DOWN as H1-H3 land)")
    for k, base in BASELINE.items():
        if k not in got:
            print("    %-38s  baseline %8.2f   not measured" % (k, base))
            continue
        now = got[k]
        slack = max(TOL, abs(base) * TOL)
        verdict = ("WORSE" if now > base + slack
                   else "better" if now < base - slack
                   else "at baseline")
        print("    %-38s  baseline %8.2f   now %8.2f   %s" % (k, base, now, verdict))
    print()
    print("  Section H of MODEL-GAPS.md is the plan these numbers justify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
