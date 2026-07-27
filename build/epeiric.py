"""Flood the epicontinental seas the global paleo-DEM cannot resolve.

The PaleoDEMs are a 20 km global grid built for topography, and they lose
shallow seas that flooded continental interiors: the Trans-Saharan Seaway does
not appear at any age, so its label had nothing to sit on and the map silently
contradicted its own description. The same is true of the Cannonball Sea, the
last marine incursion into the middle of North America.

This is the same deliberate exception the Great Lakes get in bake_lakes: where
the record is clear and the grid simply cannot resolve the feature, seed it
rather than pretend it was not there. Everything here is a named sea with real
stratigraphic control, not a general licence to invent water.

Footprints are given in PRESENT-DAY coordinates -- the modern outcrop of the
basin's marine deposits -- and back-advected along the same PALEOMAP rotations
that carry the labels, which are the frame the terrain itself is drawn in, so
the sea lands on the crust it actually flooded. Depth follows an authored curve
so each sea waxes and wanes instead of switching on and off.

Only low ground floods: anything already above FLOOD_CEILING is left alone, so
seeding a seaway cannot drown a mountain range.
"""
import math

import numpy as np

FLOOD_CEILING = 900.0        # m: ground higher than this is never flooded


def _curve(age, points):
    """Linear interpolation over (age, value) points, 0 outside the range."""
    pts = sorted(points, key=lambda p: p[0])
    if age <= pts[0][0] or age >= pts[-1][0]:
        return 0.0
    for i in range(len(pts) - 1):
        a0, v0 = pts[i]
        a1, v1 = pts[i + 1]
        if a0 <= age <= a1:
            t = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return v0 + (v1 - v0) * t
    return 0.0


SEAS = {
    # The Trans-Saharan Seaway flooded the Iullemmeden, Malian and Taoudeni
    # basins, joining Tethys to the Gulf of Guinea and cutting West Africa into
    # islands. Two high-stands -- the Cenomanian-Turonian and again in the
    # Paleocene -- with final withdrawal in the Eocene as the basins filled and
    # the region rose. Footprint anchors are the modern basins.
    "Trans-Saharan Sea": {
        "anchors": [(-3.0, 17.5, 550), (2.0, 20.0, 500), (7.5, 16.0, 500),
                    (6.5, 12.0, 420), (1.0, 14.0, 450), (10.0, 20.0, 400)],
        "depth": [(50, 0), (55, 55), (60, 110), (66, 130), (75, 95),
                  (85, 120), (94, 165), (100, 90), (105, 0)],
    },
    # The Cannonball Formation: a brief Paleocene arm of the Boreal sea reaching
    # down into the Dakotas, the last time salt water crossed the continent.
    "Cannonball Sea": {
        "anchors": [(-100.5, 47.0, 380), (-99.0, 45.5, 320), (-101.5, 48.5, 300)],
        "depth": [(56, 0), (58, 70), (60, 105), (62, 70), (64, 0)],
    },
}


def _blob(LON, LAT, plon, plat, radius_km):
    """Smooth 0..1 falloff around a point, on the sphere."""
    r = math.degrees(radius_km / 6371.0)
    dlon = ((LON - plon + 180.0) % 360.0) - 180.0
    d = np.sqrt((dlon * np.cos(np.radians(LAT))) ** 2 + (LAT - plat) ** 2)
    # 1 inside, tapering to 0 at the rim
    return np.clip(1.0 - (d / r) ** 2, 0.0, 1.0)


def carve(z, age, reconstructor=None, verbose=False):
    """Flood the seeded seas into an elevation grid for one age.

    z is (H, W), row 0 = north, spanning the globe. Returns a new grid.
    """
    total = sum(_curve(age, s["depth"]) for s in SEAS.values())
    if total <= 0:
        return z
    h, w = z.shape
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    out = z
    for name, spec in SEAS.items():
        depth = _curve(age, spec["depth"])
        if depth <= 0:
            continue
        mask = np.zeros_like(z)
        for alon, alat, radius in spec["anchors"]:
            plon, plat = alon, alat
            if reconstructor is not None:
                try:
                    tr, _ = reconstructor.track(float(alon), float(alat),
                                                min(540, max(age, 5)))
                    if tr:
                        # last point at or before the age
                        best = min(tr, key=lambda r: abs(r[0] - age))
                        plon, plat = best[1], best[2]
                except Exception:
                    pass
            mask = np.maximum(mask, _blob(LON, LAT, plon, plat, radius))
        if not mask.any():
            continue
        # only low ground floods, and the fade at the rim is a shoreline
        floodable = np.clip((FLOOD_CEILING - out) / FLOOD_CEILING, 0.0, 1.0)
        m = mask * floodable
        # NEVER raise: blending toward a shallow target would lift the abyssal
        # floor of a neighbouring ocean up to shelf depth wherever the footprint
        # overlapped it. Flooding can only ever lower ground.
        out = np.minimum(out, out * (1.0 - m) + (-depth) * m)
        if verbose:
            print(f"    {name}: {depth:.0f} m over "
                  f"{100.0 * (m > 0.05).mean():.2f}% of the grid")
    return out
