"""Which plate owns each pixel, at any age -- the raster H1 and H2 both need.

H1 warps each keyframe toward its neighbour so that crust SLIDES instead of
cross-fading, and H2 samples the terrain noise in the crust's own frame so the
texture rides with the plate rather than staying pinned to the globe. Both need
the same thing first: a per-pixel plate id, in the frame the terrain is drawn in.

WHY PALEOMAP AND NOT MERDITH. The terrain is Scotese & Wright's PaleoDEMs and
`paleo_tracks` already tracks every feature on Scotese's own rotations, because
mixing frames places names on one Earth and draws them on another. A displacement
field is if anything more sensitive: it is differenced over 5 Myr, and the gap
between two published frames drifts by about a degree over that interval against
plate motions of two to four, so borrowing Merdith's rotations here would inject
a 25-50% error into the very quantity being measured.

THE COVERAGE LIMIT, MEASURED. PALEOMAP's static polygons are PRESENT-DAY crust,
so reconstructed to an earlier age they cover only the crust that still exists.
Measured on a 1-degree grid against our own shipped elevation field:

    age      globe    land    relief      uncovered land
      0      99.9%   100.0%   100.0%           0.0 Mkm2
     50      36.3     92.7     90.1          10.1
    100      35.2     92.5     87.2          10.5
    200      33.1     88.7     83.1          18.5
    300      30.1     91.3     84.9           9.8
    400      30.2     95.8     89.8           3.5
    500      29.3     94.5     89.7           4.8

The global figure looks alarming and is not the one that matters. The hole is
subducted ocean -- abyssal plain, which is where the warp matters least, is
nearly featureless, and is synthesised procedurally by `seafloor.py` anyway.
Where there is relief to smear, we have 83-90% of it.

WHAT FILLS THE HOLE, AND WHY IT IS NOT A HACK. Uncovered cells are overwhelmingly
open ocean between two diverging continents. That crust was spreading, so its
velocity really is intermediate between the two bounding plates and really does
grade across the basin -- which is what a distance-weighted fill from the covered
margins produces. It is a fair model of a mid-ocean basin, not a smoothing
convenience. Where it is wrong is beside a subduction zone, where it takes the
overriding plate's motion for floor that is about to be consumed; that floor is
abyssal plain within a few keyframes of vanishing, so the error has nowhere to
show. `covered` is returned alongside the ids so a caller can always tell modelled
cells from measured ones.
"""
import os

import numpy as np

import paleo_tracks as PT

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "plate_rasters")

# 0.35 deg. The displacement inside a plate is a rigid rotation and so is very
# smooth; all the structure is at the boundaries, and those are 4 elevation
# texels wide at this resolution, which is finer than the boundaries themselves
# are known. Going finer costs partition time for no signal.
PW, PH = 1024, 512


def _grid(w, h):
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    return np.meshgrid(lon, lat)


_PART = {}


def _partitioner(age):
    """PlatePartitioner at an age. Cached -- building one is most of the cost."""
    key = round(float(age), 3)
    hit = _PART.get(key)
    if hit is None:
        import pygplates as pg
        rot = pg.RotationModel(PT.ROT)
        hit = pg.PlatePartitioner(pg.FeatureCollection(PT.STATIC), rot,
                                  reconstruction_time=float(age))
        if len(_PART) > 4:
            _PART.clear()
        _PART[key] = hit
    return hit


def plate_raster(age, w=PW, h=PH, use_cache=True):
    """(ids, covered) for one age. ids is int32, 0 where no polygon owns the cell.

    Plate id 0 is PALEOMAP's anchor and never moves, so it is indistinguishable
    from "no data" by value alone -- which is exactly the trap `paleo_tracks`
    records ("a point that falls outside every polygon silently stays put instead
    of failing"). Hence the separate `covered` mask; do not infer coverage from
    ids != 0.
    """
    path = os.path.join(CACHE, "pr_%s_%dx%d.npz" % (
        str(int(round(float(age) * 10))).replace("-", "m"), w, h))
    if use_cache and os.path.exists(path):
        d = np.load(path)
        return d["ids"], d["covered"]

    import pygplates as pg
    LON, LAT = _grid(w, h)
    part = _partitioner(age)
    ids = np.zeros(LON.size, np.int32)
    cov = np.zeros(LON.size, bool)
    flon, flat = LON.ravel(), LAT.ravel()
    for i in range(flon.size):
        poly = part.partition_point(pg.PointOnSphere(float(flat[i]), float(flon[i])))
        if poly is not None:
            cov[i] = True
            ids[i] = poly.get_feature().get_reconstruction_plate_id() or 0
    ids = ids.reshape(LON.shape)
    cov = cov.reshape(LON.shape)

    if use_cache:
        os.makedirs(CACHE, exist_ok=True)
        np.savez_compressed(path, ids=ids, covered=cov)
    return ids, cov


def euler(rot, pid, to_age, from_age):
    """(axis unit vector, angle) taking plate `pid` from from_age to to_age.

    Returned as a numpy axis/angle rather than a pygplates FiniteRotation so the
    caller can rotate a whole plate's worth of pixels with one Rodrigues
    evaluation. Rotating 500k points through pygplates one at a time is minutes
    per keyframe; vectorised it is milliseconds.
    """
    fr = rot.get_rotation(float(to_age), int(pid), float(from_age))
    if fr is None:
        return None, 0.0
    try:
        pole, ang = fr.get_euler_pole_and_angle()
    except Exception:
        return None, 0.0
    la, lo = pole.to_lat_lon()
    la, lo = np.radians(la), np.radians(lo)
    axis = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return axis, float(ang)


def rodrigues(v, axis, ang):
    """Rotate unit vectors v (..., 3) about `axis` by `ang`. Vectorised."""
    if axis is None or abs(ang) < 1e-12:
        return v
    c, s = np.cos(ang), np.sin(ang)
    kv = np.cross(axis, v)
    kdv = v @ axis
    return v * c + kv * s + axis[None, :] * (kdv * (1.0 - c))[:, None]


def unit(lon, lat):
    la, lo = np.radians(lat), np.radians(lon)
    cl = np.cos(la)
    return np.stack([cl * np.cos(lo), cl * np.sin(lo), np.sin(la)], -1)


def lonlat(v):
    n = v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)
    return np.degrees(np.arctan2(n[..., 1], n[..., 0])), np.degrees(np.arcsin(np.clip(n[..., 2], -1, 1)))


# --------------------------------------------------------------------------

def _selftest():
    """Adversarial: a check that cannot fail is not a check."""
    ok = True
    import pygplates as pg

    # unit/lonlat must round-trip, including at the antimeridian and the poles.
    for lo, la in ((0, 0), (179.9, 0), (-179.9, 0), (45, 89.9), (-120, -89.9)):
        blo, bla = lonlat(unit(np.array([lo]), np.array([la])))
        dlon = (blo[0] - lo + 180) % 360 - 180
        if abs(dlon) > 1e-6 or abs(bla[0] - la) > 1e-6:
            print("  FAIL round-trip at (%s, %s) -> (%.6f, %.6f)" % (lo, la, blo[0], bla[0]))
            ok = False

    # Rodrigues must agree with pygplates itself, or every displacement is wrong.
    rot = pg.RotationModel(PT.ROT)
    worst = 0.0
    for pid in (101, 201, 301, 701, 801):
        ax, ang = euler(rot, pid, 100.0, 0.0)
        if ax is None:
            continue
        fr = rot.get_rotation(100.0, int(pid), 0.0)
        for lo, la in ((-75, 40), (10, -30), (140, 60), (-160, -55)):
            mine = lonlat(rodrigues(unit(np.array([lo]), np.array([la])), ax, ang))
            p = fr * pg.PointOnSphere(float(la), float(lo))
            tla, tlo = p.to_lat_lon()
            d = abs((mine[0][0] - tlo + 180) % 360 - 180) + abs(mine[1][0] - tla)
            worst = max(worst, d)
    if worst > 1e-6:
        print("  FAIL Rodrigues disagrees with pygplates by %.3g deg" % worst)
        ok = False
    else:
        print("  Rodrigues vs pygplates: max %.2e deg over 20 point-plate pairs" % worst)

    # A zero-length interval must be the identity, or the field has a DC offset.
    ax, ang = euler(rot, 101, 50.0, 50.0)
    if ax is not None and abs(ang) > 1e-9:
        print("  FAIL zero interval is not identity (angle %.3g)" % ang)
        ok = False

    # Coverage must be near-total at 0 Ma. If it is not, the model files are
    # wrong and every downstream number would be quietly built on a hole.
    ids, cov = plate_raster(0, 180, 90, use_cache=False)
    frac = float(cov.mean())
    if frac < 0.98:
        print("  FAIL coverage at 0 Ma is only %.1f%%" % (100 * frac))
        ok = False
    else:
        print("  coverage at 0 Ma: %.1f%%, %d distinct plates" % (100 * frac, len(np.unique(ids[cov]))))

    print("  selftest: %s" % ("pass" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if _selftest() else 1)
