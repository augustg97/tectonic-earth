"""A seamount POPULATION, rather than a few smeared chains.

There are roughly 24,000 seamounts over a kilometre high on the present ocean
floor -- about one every one and a half degrees of ocean -- and on a real chart
they are a large part of what makes the abyss look busy rather than blank. We had
generic streaks smeared along the plate-motion direction, which reads as a smudge
because that is what it is: no individual mountain, no summit, no shadow.

The population is not random. Three things about it are well established and all
three are modelled here:

  HEIGHT follows a power law -- very many small ones, very few large. So the
  height is drawn from an inverse-power transform of a uniform variate rather
  than from a Gaussian, which would give a typical seamount and almost no
  outliers, exactly backwards.

  BIRTH happens at the ridge, where most seamounts are built by the same
  volcanism that makes the crust, and at hotspots, where a plume builds a chain
  as the plate slides over it. So the density is highest on young crust and along
  the tracks, not uniform.

  SUBSIDENCE. A seamount rides its plate and sinks with it as the crust cools, so
  an old seamount stands the same height above ITS OWN crust but sits far deeper.
  Some grew fast enough to reach the surface and are then planed flat by waves
  and drowned as guyots -- which is why flat-topped seamounts are common on old
  crust and absent on young.

Placement is a stable hash of position, so a given seamount is the same mountain
at every keyframe rather than re-rolling and shimmering.
"""
import numpy as np

DENSITY = 0.55            # seamounts per square degree of ocean, at the ridge
# Lower cut. NOT the smallest real seamount -- the smallest this grid can carry.
# A cell is 20 km, and a 1 km seamount is only 14 km across its base, so the
# whole population below about 1.2 km is sub-pixel here and stamping it would
# alias rather than resolve. Same division as the abyssal hills: the field
# carries what the grid can hold and the shader synthesises the rest per pixel.
# Above this cut the model produces of order ten thousand mountains, which is
# the right order for the resolvable part of a population that runs to ~24,000
# above a kilometre.
H_MIN = 1200.0
H_MAX = 4200.0            # m: the largest, which reach the surface
POWER = 1.15              # power-law slope for the height distribution
# Basal radius per metre of height. A seamount's flanks stand at roughly 1:14,
# so a 1 km cone is about 14 km across the base -- 0.13 deg. Getting this wrong
# by the factor of thirty it was wrong by gave a 4 km seamount a basal radius of
# 1,950 km and covered 84% of the ocean in one merged shield.
RADIUS_PER_M = 0.00013


def _hash2(i, j, salt):
    """Deterministic 0..1 from a pair of integers. Stable across keyframes, so a
    seamount stays the same mountain instead of shimmering."""
    x = (i * 73856093) ^ (j * 19349663) ^ (salt * 83492791)
    x &= 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0xFFFFFFFF
    x ^= x >> 16
    return x / 4294967295.0


def field(age_myr, sea, lat1d, deg_per_cell, hotspot=None, seed=7):
    """Seamount relief in metres, on the model grid.

    Seeded on a coarse lattice so the cost is set by the number of MOUNTAINS,
    not by the number of cells -- each one is then stamped as a cone over the
    handful of cells it actually covers.
    """
    h, w = age_myr.shape
    out = np.zeros((h, w), np.float32)
    cell = 1.0                                   # deg between candidate sites
    nlat = int(180 / cell)
    nlon = int(360 / cell)

    ys, xs = np.mgrid[0:h, 0:w]
    for j in range(nlat):
        lat = 90.0 - (j + 0.5) * cell
        coslat = max(np.cos(np.radians(lat)), 0.05)
        # equal-area sampling: fewer candidate sites per degree of longitude
        # near the poles, or the caps would sprout a dense fringe of volcanoes
        step = max(1, int(round(1.0 / coslat)))
        for i in range(0, nlon, step):
            lon = -180.0 + (i + 0.5) * cell
            r = _hash2(i, j, seed)
            row = int((90.0 - lat) / 180.0 * h)
            col = int((lon + 180.0) / 360.0 * w)
            if row < 0 or row >= h or col < 0 or col >= w or not sea[row, col]:
                continue
            a = float(age_myr[row, col])
            # Born at the ridge and on hotspots: density falls with crustal age
            # because most seamounts are built at or near the axis.
            dens = DENSITY * (0.35 + 0.85 * np.exp(-a / 28.0))
            if hotspot is not None:
                dens *= (1.0 + 5.0 * float(hotspot[row, col]))
            if r > dens * cell * cell * coslat:
                continue
            u = _hash2(i, j, seed + 101)
            hgt = H_MIN * (1.0 - u) ** (-1.0 / POWER)
            if hgt > H_MAX:
                hgt = H_MAX
            rad = max(hgt * RADIUS_PER_M, deg_per_cell * 1.2)
            # jitter off the lattice, or the population lines up on a grid
            plon = lon + (_hash2(i, j, seed + 211) - 0.5) * cell
            plat = lat + (_hash2(i, j, seed + 307) - 0.5) * cell
            rr = int(np.ceil(rad / deg_per_cell)) + 1
            r0, r1 = max(0, row - rr), min(h, row + rr + 1)
            if r1 <= r0:
                continue
            dy = (90.0 - (ys[r0:r1, :1] + 0.5) * deg_per_cell) - plat
            dlon = (((xs[r0:r1, :] + 0.5) * deg_per_cell - 180.0) - plon + 180.0) % 360.0 - 180.0
            d = np.hypot(dlon * coslat, dy)
            cone = np.clip(1.0 - d / rad, 0.0, 1.0)
            if not cone.any():
                continue
            # A cone with a rounded shoulder, not a spike. Tall ones on old crust
            # reached the surface and were planed flat -- a guyot -- so their
            # summit is a plateau rather than a peak.
            prof = cone ** 1.35
            if hgt > 2400.0 and a > 35.0:
                prof = np.minimum(prof, 0.78) / 0.78 * 0.92
            out[r0:r1, :] = np.maximum(out[r0:r1, :], (prof * hgt).astype(np.float32))
    return out
