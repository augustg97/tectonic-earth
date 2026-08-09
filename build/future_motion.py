"""Where a present-day point ends up on the future map.

THE DEFECT. The app synthesises 250 Myr of future plate motion -- build_fields
inverse-warps today's DEM by a per-group rotation, groups pack until their land
stops interpenetrating, and sutures rise where they meet -- and the LABELS do
not ride any of it. Every track is built by paleo_tracks, which only runs
backwards, so a track spans 0..N Ma and `trackPos` clamps at both ends. Anything
visible in the future renders at its age-0 position for the whole future era.
Measured on the shipped build: Antarctica and Africa frozen 40 Myr, North and
South America 30, Eurasia and Australia 20 -- six continent names standing still
while the continents under them cross tens of degrees.

This is not a case of missing information. The motion is authored, deterministic
and already baked into every future keyframe; the labels simply never asked for
it.

WHY IT MUST BE THE SAME ROTATION, not an approximation of it. The label has to
stay on its own crust, and the crust's position comes from `_packed_targets`,
whose relaxation depends on each group's land radius -- which depends on the
present DEM. Recomputing the packing on a coarser grid, or without the DEM,
gives targets a degree or two off, and a degree of target error at the far end
of a 250 Myr rotation is a name standing offshore. So this calls the same
`rasterise_groups()` and the same `_packed_targets(gid, Zsrc)` on the same
900x1800 present DEM that build_fields.main uses, and caches the result keyed to
the things that would change it.

    R_full(g) = rodrigues(t, spin) @ rot_from_to(cent[g], t)     # 0 -> +250 Myr
    p(myr)    = axis_angle_scale(R_full, myr/250) @ p(0)

future_grid applies the INVERSE of that per pixel (it asks "where did this cell
come from"); a label is a point being carried forward, so it uses the forward
form. Getting that backwards moves every name the wrong way round the globe,
which is a silent and very confident-looking failure -- so `selftest` below
checks the advanced position against the baked future elevation rather than
against another calculation.
"""
import hashlib
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "future_motion.json")
SPAN_MYR = 250.0          # build_fields: frac = abs(age) / 250.0


def _fingerprint():
    """Everything that would change the answer, so a stale cache cannot survive."""
    import build_fields as BF
    plates = os.path.join(HERE, "..", "web", "plates.json")
    h = hashlib.sha256()
    h.update(repr(sorted(BF.GROUP_TARGET.items())).encode())
    h.update(repr(sorted(BF.PLATE_GROUP.items())).encode())
    h.update(repr(BF.PACK).encode())
    h.update(repr(os.path.getmtime(plates)).encode())
    h.update(repr(os.path.getsize(plates)).encode())
    return h.hexdigest()[:16]


def _compute():
    import build_fields as BF
    import build_synthetic as BS
    from build_frames import index_dems, read_dem
    from render import resample_dem

    gid = BF.rasterise_groups()
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    z0 = read_dem(idx[float(avail[np.argmin(np.abs(avail - 0))])])
    Zsrc = resample_dem(z0, 900, 1800)
    packed = BF._packed_targets(gid, Zsrc)

    gh, gw = gid.shape
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)

    out = {}
    for i, g in enumerate(BF.GROUPS):
        m = gid == i
        if not m.any() or g not in packed:
            continue
        c = BS.unit(GLON[m], GLAT[m]).mean(axis=1)
        c /= np.linalg.norm(c)
        tl, tb, spin = packed[g]
        t = BS.unit(tl, tb)
        Rfull = BS.rodrigues(t, spin) @ BS.rot_from_to(c, t)
        out[g] = Rfull.tolist()
    return out, gid


def _load():
    """Per-group 0 -> +250 Myr rotation, cached; recomputed when inputs change."""
    fp = _fingerprint()
    if os.path.exists(CACHE):
        try:
            d = json.load(open(CACHE))
            if d.get("fingerprint") == fp:
                return {k: np.array(v, float) for k, v in d["rot"].items()}
        except (ValueError, KeyError):
            pass
    rot, gid = _compute()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump({"fingerprint": fp, "rot": rot}, open(CACHE, "w"))
    _save_group_mask(gid)
    return {k: np.array(v, float) for k, v in rot.items()}


MASK = os.path.join(HERE, "cache", "future_groups.npy")


def _save_group_mask(gid):
    """A coarse group id grid, so `group_at` needs no polygon work at call time.

    Coarsened 8x to 0.5 degrees. This one CAN be coarse: it answers "which plate
    group is this label on", and a label within half a degree of a plate boundary
    has no well-defined answer anyway. It is only the PACKING that needs the fine
    grid, and that is computed above at full resolution.
    """
    g = np.asarray(gid)[::8, ::8]
    np.save(MASK, g.astype(np.int16))


_ROT = None
_MASK = None
_NAMES = None


def _ready():
    global _ROT, _MASK, _NAMES
    if _ROT is None:
        import build_fields as BF
        _NAMES = BF.GROUPS
        _ROT = _load()
        if not os.path.exists(MASK):
            _save_group_mask(BF.rasterise_groups())
        _MASK = np.load(MASK)
    return _ROT is not None


def group_at(lon, lat, search_deg=6.0):
    """Which plate group owns this point, searching outward if it is offshore.

    A continent label sits at a landmass centroid, which is reliably inside its
    own plate; a sea or a coastal name can fall in the -1 gap between digitised
    plate rings, and returning None there would silently leave that label frozen
    -- the exact failure this file exists to remove. So widen until something is
    found, out to a few degrees.
    """
    _ready()
    h, w = _MASK.shape
    r = int(round((90.0 - lat) / 180.0 * h))
    c = int(round((lon + 180.0) / 360.0 * w))
    r = max(0, min(h - 1, r))
    step = max(1, int(round(180.0 / h)))
    for rad in range(0, int(search_deg / (180.0 / h)) + 1, step):
        r0, r1 = max(0, r - rad), min(h, r + rad + 1)
        sl = _MASK[r0:r1]
        cols = [(c + d) % w for d in range(-rad, rad + 1)]
        vals = sl[:, cols]
        vals = vals[vals >= 0]
        if vals.size:
            return _NAMES[int(np.bincount(vals).argmax())]
    return None


def advance(lon, lat, myr, group=None):
    """Carry a present-day point forward `myr` million years. myr >= 0."""
    import build_fields as BF
    _ready()
    g = group or group_at(lon, lat)
    if g is None or g not in _ROT:
        return None
    Rm = BF.axis_angle_scale(_ROT[g], min(1.0, max(0.0, myr / SPAN_MYR)))
    import build_synthetic as BS
    p = BS.unit(lon, lat).reshape(3)
    q = Rm @ p
    return (float(np.degrees(np.arctan2(q[1], q[0]))),
            float(np.degrees(np.arcsin(np.clip(q[2], -1, 1)))))


def selftest():
    """Check the advanced position against the BAKED future terrain.

    The direction of a rotation is the one thing here that no amount of reading
    can settle -- both directions produce a smooth, plausible-looking track. So
    the test is empirical: take a continent's present centroid, advance it, and
    ask the shipped future elevation texture whether that place is land.

    AND IT REPORTS THE TWO CONTROLS, because "6/6 on land" proves nothing by
    itself -- Africa barely leaves its own outline. The controls are the reverse
    rotation and no rotation at all (what shipped before this file existed).
    Measured at +250 Myr: forward 6/6, reversed 2/6, frozen 2/6. That spread is
    the evidence; without it the check could pass while doing nothing.
    """
    import glob
    import io
    from PIL import Image
    try:
        import pillow_avif  # noqa: F401
    except ImportError:
        pass
    sites = [("Africa", 20.0, 2.0), ("Australia", 134.0, -25.0),
             ("South America", -60.0, -10.0), ("Eurasia", 90.0, 55.0),
             ("North America", -100.0, 45.0), ("Antarctica", 20.0, -80.0)]
    fails = 0
    print("  future label motion -- is the advanced point still on its continent?")
    for myr in (50, 150, 250):
        f = glob.glob(os.path.join(HERE, "..", "web", "fields",
                                   "fut_%04d_e.*" % myr))
        if not f:
            print("    +%3d Myr  no baked frame fut_%04d_e.* to check against"
                  % (myr, myr))
            continue
        im = np.asarray(Image.open(f[0]).convert("L")).astype(float)
        h, w = im.shape
        # sqrt-companded elevation: sea level is the encoded zero point, read
        # from the frame's own ocean rather than assumed.
        sea = float(np.percentile(im, 40))

        def onland(p):
            if p is None:
                return False
            r = int((90 - p[1]) / 180 * h) % h
            c = int((p[0] + 180) / 360 * w) % w
            return float(im[max(0, min(h - 1, r)), c]) > sea + 6

        fwd, rev, froz, bad, travel = 0, 0, 0, [], []
        for name, lo, la in sites:
            g = group_at(lo, la)
            if g is None or g not in _ROT:
                bad.append(name)
                continue
            import build_fields as BF
            import build_synthetic as BS
            Rm = BF.axis_angle_scale(_ROT[g], myr / SPAN_MYR)
            p = BS.unit(lo, la).reshape(3)

            def ll(q):
                return (float(np.degrees(np.arctan2(q[1], q[0]))),
                        float(np.degrees(np.arcsin(np.clip(q[2], -1, 1)))))
            hit = onland(ll(Rm @ p))
            fwd += hit
            rev += onland(ll(Rm.T @ p))
            froz += onland((lo, la))
            travel.append(float(np.degrees(np.arccos(np.clip((Rm @ p) @ p, -1, 1)))))
            if not hit:
                bad.append(name)
        fails += len(bad)
        print("    +%3d Myr  forward %d/%d   [controls: reversed %d, frozen %d]"
              "   travel %4.1f deg%s"
              % (myr, fwd, len(sites), rev, froz,
                 float(np.mean(travel)) if travel else 0.0,
                 "   OFF: " + ", ".join(bad) if bad else ""))
    print("  %d misses (a reversed or frozen label misses most of them)" % fails)
    return fails


if __name__ == "__main__":
    import sys
    sys.exit(1 if selftest() > 4 else 0)
