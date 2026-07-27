"""The hotspot catalogue, and the one line of physics that turns it into
islands, atolls and guyots.

The catalogue itself lives in `Deep Research/modeling/hotspots.py` -- 53 plumes
with present-day coordinates, riding plate, chain, LIP root, start age, plume
flux where published, and a confidence grade, plus `ASEISMIC_RIDGES` mapping 15
named ridges to the plume that built each. That module is stdlib-only on purpose
so `build/` can import it rather than keep a second copy that drifts. This is the
two-line bridge plus the arithmetic the seeder needs.

WHY THIS MATTERS. `seamounts.field()` used to place its 34 plumes by HASHING a
seed -- literally `_h(seed, p, 11)` for the latitude. The chains it drew were
real in mechanism and imaginary in location, so a real ocean's most organised
feature was the one thing the map put in the wrong place. Hawaii, Louisville,
Ninetyeast, Walvis, the Emperor seamounts: all absent, and a scatter of invented
chains in their stead.

THE ONE LINE, from Deep Research WP-04 section 3:

    summit_depth = (ridge_depth - edifice_height) + 0.350 * sqrt(edifice age)

An edifice is built at the plume and then rides down as the plate under it cools
and contracts, on the same half-space law the sea floor already uses. With the
published constants it stands 1.4 km above the sea when new and drowns at about
16 Myr:

     0 Myr   -1.40 km   island
    10 Myr   -0.29 km   island
    20 Myr   +0.17 km   atoll / shallow bank
    40 Myr   +0.81 km   guyot
   100 Myr   +2.10 km   deep guyot

That single line gives islands at the young end, atolls in the middle and
flat-topped guyots at the old end WITHOUT a new noise function -- and it is
calibrated by the Hawaiian-Emperor chain rather than by eye: Midway at ~28 Ma is
an atoll, Meiji at ~85 Ma is a guyot about 2 km down.

WHERE THE CATALOGUE STOPS, THE MODEL CARRIES ON. The oldest dated plume trail is
about 135 Ma. Earth plainly had plumes at 300 Ma; we do not know where. So the
catalogue supplies the plumes it can date and a deterministic hashed population
tops the count up beyond that -- the standing rule, follow the record where there
is one and model the mechanism where there is not, with the difference stated
rather than blurred.
"""
import math
import os
import sys

_MODELING = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "Deep Research", "modeling")

_HS = None


def catalogue():
    """The hotspots module, or None if the research folder is not present."""
    global _HS
    if _HS is None:
        try:
            if _MODELING not in sys.path:
                sys.path.insert(0, _MODELING)
            import hotspots                                # noqa: PLC0415
            _HS = hotspots
        except Exception:                                  # noqa: BLE001
            _HS = False
    return _HS or None


# Half-space subsidence of an edifice, metres per sqrt(Myr). Same constant the
# sea floor's own depth-age law uses, which is the point: the mountain and the
# plain it stands on sink together.
SUBSIDENCE = 350.0
RIDGE_DEPTH = 2600.0        # m, axial depth where the edifice is built
INITIAL_H = 4000.0          # m, edifice height when it leaves the plume


def summit_depth(edifice_age):
    """Depth of the summit below sea level in metres. NEGATIVE is an island.

    THIS DELIBERATELY STAYS ON sqrt(t) WHILE THE SEA FLOOR MOVED TO GDH1.
    It looks like an inconsistency and is not, for two reasons.

    Physically, a hotspot edifice is built on the plume's SWELL -- Hawaii's is
    about a kilometre of dynamic uplift -- and subsides faster than plate cooling
    alone as it rides off the swell. 350 m per sqrt(Myr) is calibrated to the
    Hawaiian-Emperor chain we can see, and that calibration is what puts Midway
    at atoll depth and the Emperors at guyot depth. Coupling this to GDH1 pushes
    Midway to 515 m, over the atoll/guyot line: it would break the one part of
    this model that is checked directly against real bathymetry.

    Mechanically, there is no floating volcano either way. seamounts.field() sets
    an edifice's HEIGHT from the floor actually under it (`-summit - floor[r,c]`),
    not from an assumed axial depth, so a shallower GDH1 floor simply builds a
    shorter cone to reach the same summit.
    """
    a = max(0.0, float(edifice_age))
    return (RIDGE_DEPTH - INITIAL_H) + SUBSIDENCE * math.sqrt(a)


def kind(edifice_age):
    d = summit_depth(edifice_age)
    return "island" if d < 0 else ("atoll" if d < 500.0 else "guyot")


def active(age):
    """Catalogued plumes whose trail had already begun at `age` Ma.

    `started` is the oldest DATED edifice on the trail, so this is the honest
    window: outside it the plume may well have existed and we would be inventing
    its position.
    """
    hs = catalogue()
    if hs is None:
        return []
    return [h for h in hs.HOTSPOTS if h.started is not None and h.started >= age]


# ---------------------------------------------------------------------------
# Present-day traces of the named aseismic ridges, young end FIRST.
#
# WHY THESE ARE DATA AND NOT DERIVED. A plume track can only write on the plate
# that is over the plume TODAY, and several of these ridges are not: the
# Ninetyeast Ridge was cut into the Indian plate while India raced north over the
# Kerguelen plume, and India is now 5,000 km away, so no amount of reconstructing
# from Kerguelen's present position recovers it. Measured: every plate within 8
# degrees of Kerguelen shares Antarctica's rotation and every trail ends in the
# same place. Same for Chagos-Laccadive, which Reunion wrote on India.
#
# So the ridge is entered where the survey puts it and carried back on ITS OWN
# plate -- the identical machinery that carries every label. Formation age is
# interpolated along the trace between the limb's two ends, so the summit-depth
# law runs along the crest and each ridge shoals toward its young end by itself.
#
# The five ridges already carried by seafloor.PLATEAUS with authored emergence
# curves (Walvis, Rio Grande, Broken, Mascarene, Hawaiian) are deliberately NOT
# here: those curves record when each stood above water, which is knowledge the
# subsidence law does not have.
RIDGE_TRACE = {
    "Emperor Seamounts": [(172.0, 32.0), (170.3, 35.3), (170.4, 38.0),
                          (170.6, 41.1), (170.3, 44.6), (168.5, 48.0),
                          (167.5, 51.5), (165.0, 53.2)],
    "Ninetyeast Ridge": [(88.5, -31.0), (88.8, -24.0), (89.2, -17.0),
                         (89.8, -10.0), (90.2, -3.0), (90.0, 3.0),
                         (89.5, 8.0), (89.0, 10.0)],
    "Chagos-Laccadive Ridge": [(72.0, -6.5), (72.4, -1.0), (72.8, 4.0),
                               (73.2, 8.0), (73.4, 11.5), (73.0, 14.0)],
    "Cocos Ridge": [(-91.0, 1.5), (-89.0, 3.0), (-87.0, 4.5), (-85.5, 6.0),
                    (-84.5, 7.0)],
    "Carnegie Ridge": [(-91.0, -0.7), (-88.0, -1.0), (-85.0, -1.2),
                       (-82.0, -1.4), (-80.5, -1.5)],
    "Nazca Ridge": [(-84.0, -23.5), (-82.0, -21.5), (-80.0, -19.5),
                    (-78.5, -17.5), (-77.5, -15.5)],
    "Louisville Ridge": [(-139.0, -51.0), (-148.0, -48.5), (-157.0, -45.0),
                         (-165.0, -41.0), (-172.0, -37.0), (-178.0, -33.0),
                         (177.0, -29.0), (174.0, -26.0)],
    # Iceland's ridge is SYMMETRIC -- oldest at Greenland and at the Faroes,
    # youngest at Iceland in the middle -- and a trace carries one monotonic age
    # sequence, so only the Iceland-Faroe limb is entered. Drawing both limbs as
    # one polyline put a spurious ridge straight back across Iceland.
    "Greenland-Iceland-Faroe Ridge": [(-18.0, 64.9), (-15.0, 64.6),
                                      (-12.0, 64.2), (-9.0, 63.5),
                                      (-7.0, 62.5)],
    # Young end SE, at the Great Meteor end: the New England chain gets OLDER
    # toward the continental shelf (Bear ~103 Ma, Nashville ~83).
    "New England Seamounts": [(-56.5, 35.0), (-58.5, 36.2), (-61.5, 37.5),
                              (-64.5, 38.6), (-67.5, 39.8)],
    "Vitoria-Trindade Ridge": [(-29.3, -20.5), (-32.0, -20.5), (-35.0, -20.6),
                               (-38.0, -20.7), (-40.0, -20.8)],
}


def ridge_trace(name):
    """[(lon, lat, formation age Ma), ...] for a named ridge, or []."""
    hs = catalogue()
    pts = RIDGE_TRACE.get(name)
    if hs is None or not pts:
        return []
    spec = hs.ASEISMIC_RIDGES.get(name)
    if spec is None:
        return []
    _who, old, young = spec[0], spec[1], spec[2]
    n = len(pts) - 1
    return [(lo, la, young + (old - young) * (i / n if n else 0.0))
            for i, (lo, la) in enumerate(pts)]


def ridge_limbs(hotspot_name):
    """[(ridge name, oldest Ma, youngest Ma), ...] built by this plume.

    A limb listed here is an ASEISMIC RIDGE -- a continuous bathymetric high --
    rather than a string of separate cones, so the seeder stamps it densely
    enough that the edifices merge. Ninetyeast is 5,000 km of continuous ridge;
    Louisville is a line of discrete seamounts. The catalogue is what tells them
    apart, because the difference is plume flux against plate speed and we have
    the observation but not the model.
    """
    hs = catalogue()
    if hs is None:
        return []
    return [(name, old, young)
            for name, (who, old, young, _note) in hs.ASEISMIC_RIDGES.items()
            if who == hotspot_name]


def _selftest():
    hs = catalogue()
    assert hs is not None, "Deep Research/modeling/hotspots.py did not import"
    # our arithmetic must agree with the research module's, or the app and the
    # paper describe different mountains
    for a in (0, 5, 16, 20, 40, 80, 140):
        mine = summit_depth(a) / 1000.0
        theirs = hs.summit_depth(a)
        assert abs(mine - theirs) < 1e-9, f"{a} Myr: {mine} vs {theirs}"
    assert summit_depth(0) < 0, "a new edifice should be an island"
    assert summit_depth(80) > 500, "an 80 Myr edifice should be a guyot"
    cross = next(a for a in range(0, 60) if summit_depth(a) >= 0)
    assert 14 <= cross <= 18, f"islands should drown near 16 Myr, got {cross}"
    n = len(hs.HOTSPOTS)
    limbs = sum(len(ridge_limbs(h.name)) for h in hs.HOTSPOTS)
    assert limbs == len(hs.ASEISMIC_RIDGES), f"{limbs} limbs mapped of {len(hs.ASEISMIC_RIDGES)}"
    for name, pts in RIDGE_TRACE.items():
        assert name in hs.ASEISMIC_RIDGES, f"trace for unknown ridge {name}"
        assert len(pts) >= 2, f"{name}: a trace needs at least two points"
        for lo, la in pts:
            assert -180 <= lo <= 180 and -90 <= la <= 90, f"{name} {(lo, la)}"
        tr = ridge_trace(name)
        assert tr and tr[0][2] <= tr[-1][2], f"{name}: trace must run young end first"
    # a traced ridge must SHOAL toward its young end, or the subsidence law is
    # running backwards along the crest
    for name in RIDGE_TRACE:
        tr = ridge_trace(name)
        assert summit_depth(tr[0][2]) < summit_depth(tr[-1][2]), name
    print(f"hotspots_cat OK: {n} plumes, {limbs} aseismic-ridge limbs, "
          f"{len(RIDGE_TRACE)} of them with a surveyed trace, "
          f"islands drown at {cross} Myr")
    for a in (0, 10, 20, 40, 100):
        print(f"   {a:>4} Myr  summit {summit_depth(a):+8.0f} m  {kind(a)}")
    print(f"   active at   0 Ma: {len(active(0))} plumes")
    print(f"   active at  90 Ma: {len(active(90))} plumes")
    print(f"   active at 200 Ma: {len(active(200))} plumes")


if __name__ == "__main__":
    _selftest()
