"""Generate Precambrian landmasses with organic coastlines.

The earlier version cut cratons out of the modern DEM with lon/lat bounding
boxes, which is why they read as rectangles — jittering the edge of a rectangle
still leaves a rectangle. Nothing about a 900 Ma coastline is known well enough
to trace, so these are *generated* rather than copied:

  * Coastline — each craton's radius is modulated by three octaves of 3D noise
    evaluated in the craton's own rotating frame, giving fractal shorelines with
    gulfs, peninsulas and a stable shape that turns with the block.
  * Erosion — Precambrian shields are ancient peneplains, worn low over
    hundreds of millions of years, so interiors are deliberately subdued: broad,
    low relief that floods easily into epeiric seas at high sea level.
  * Orogeny — where two cratons overlap they are colliding, so the suture is
    raised into a ridged mountain belt.
  * Volcanism — margins carry offshore island arcs, the accreting fringe that
    eventually welds onto the craton.

The result is speculative, but it is speculative in the right shape: fractal
coastlines and worn interiors rather than boxes or recycled modern outlines.
"""
import numpy as np
import build_synthetic as BS
from render import _smooth

# name -> (radius in degrees, noise seed). Radii scale with each craton's real
# extent; Laurentia and East Antarctica are the giants, the China blocks small.
CRATON_SHAPE = {
    "Laurentia":   (30.0,  3), "Baltica":    (17.0, 11), "Siberia":    (19.0, 17),
    "Amazonia":    (20.0, 23), "WestAfrica": (16.5, 31), "Congo":      (16.0, 41),
    "Kalahari":    (13.0, 47), "India":      (13.5, 53), "Australia":  (19.0, 61),
    "EAntarctica": (22.0, 67), "NChina":     (10.0, 71), "SChina":     (10.5, 79),
    "Kazakh":      (10.5, 83), "Arabia":     (11.0, 89),
}

ANCHOR = np.array([1.0, 0.0, 0.0])      # unit(lon=0, lat=0)


# ---------------------------------------------------------------- noise ----
def _h3(ix, iy, iz, seed):
    n = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 97).astype(np.int64)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xFFFFFF).astype(np.float64) / float(0xFFFFFF)


def vnoise3(P, seed):
    """Value noise over 3D points P (3,N)."""
    x, y, z = P
    ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64); iz = np.floor(z).astype(np.int64)
    fx = x - ix; fy = y - iy; fz = z - iz
    ux = fx * fx * (3 - 2 * fx); uy = fy * fy * (3 - 2 * fy); uz = fz * fz * (3 - 2 * fz)
    def c(dx, dy, dz): return _h3(ix + dx, iy + dy, iz + dz, seed)
    x00 = c(0,0,0)*(1-ux) + c(1,0,0)*ux
    x10 = c(0,1,0)*(1-ux) + c(1,1,0)*ux
    x01 = c(0,0,1)*(1-ux) + c(1,0,1)*ux
    x11 = c(0,1,1)*(1-ux) + c(1,1,1)*ux
    return (x00*(1-uy) + x10*uy)*(1-uz) + (x01*(1-uy) + x11*uy)*uz


def fbm3(P, seed, octaves=4, lac=2.07):
    s = np.zeros(P.shape[1]); a = 0.5; tot = 0.0; Q = P.copy()
    for i in range(octaves):
        s += a * vnoise3(Q, seed + i * 17)
        tot += a; a *= 0.5; Q = Q * lac
    return s / tot


# ------------------------------------------------------------ generation ----
def precambrian_grid(age, tw=1536, th=768, flood=140.0):
    """Elevation grid (th,tw), lat +90..-90 top->bottom, for a Precambrian age."""
    placements = BS.pre_placement(age)
    tlon = (np.arange(tw) + 0.5) / tw * 360 - 180
    tlat = 90 - (np.arange(th) + 0.5) / th * 180
    LON, LAT = np.meshgrid(tlon, tlat)
    T = BS.unit(LON.ravel(), LAT.ravel())           # (3,N)

    elev = np.full(T.shape[1], -5000.0)
    claims = np.zeros(T.shape[1], np.int16)
    belt = np.zeros(T.shape[1])

    for name, glon, glat, spin in placements:
        if name not in CRATON_SHAPE:
            continue
        R0, seed = CRATON_SHAPE[name]
        c = BS.unit(glon, glat)
        # only touch the cap this craton could possibly reach
        cosd = np.clip(c @ T, -1, 1)
        near = cosd > np.cos(np.radians(R0 * 1.9))
        if not near.any():
            continue
        idx = np.where(near)[0]
        Tn = T[:, idx]

        # craton-local frame: the shape (and its noise) rotates with the block
        Rloc = BS.rodrigues(c, spin) @ BS.rot_from_to(ANCHOR, c)
        L = Rloc.T @ Tn
        d = np.degrees(np.arccos(np.clip(L[0], -1, 1)))

        # Elongate the block: real cratons are not discs, and a circular base
        # shape shows through the noise as a suspiciously round outline.
        bearing = np.arctan2(L[2], L[1])
        axis = (seed % 7) * 0.4488                      # per-craton orientation
        d = d * (1.0 + 0.24 * np.cos(2.0 * (bearing - axis)))

        # fractal coastline: three scales of lobes, gulfs and crenulation
        rad = R0 * (1.0
                    + 0.42 * (fbm3(L * 2.2, seed, 3) - 0.5) * 2.0
                    + 0.17 * (fbm3(L * 5.8, seed + 5, 3) - 0.5) * 2.0
                    + 0.07 * (fbm3(L * 14.0, seed + 9, 2) - 0.5) * 2.0)

        inside = d < rad
        h = np.clip((rad - d) / (0.30 * R0), 0, 1)      # 0 at the shore, 1 inland

        # worn-down shield: low, broad relief that drowns easily
        shield = 120.0 + 430.0 * np.power(h, 0.85)
        undul = (fbm3(L * 5.5, seed + 13, 4) - 0.5) * 360.0
        # Ancient fold belts threaded through the shield. The noise domain is
        # squashed on one axis and stretched on another so the ridges come out
        # linear, like a worn orogen, instead of blotchy highland.
        Lb = L * np.array([[1.0], [0.55], [1.9]])
        ridged = 1.0 - np.abs(2.0 * fbm3(Lb * 3.4, seed + 29, 4) - 1.0)
        # Only a few tracts of the shield are orogen; elsewhere it is plain.
        gate = np.clip((fbm3(L * 1.8, seed + 37, 2) - 0.46) / 0.22, 0, 1)
        folds = np.power(ridged, 2.5) * 430.0 * gate * np.clip(h * 1.6, 0, 1)
        z = shield + undul + folds

        # Island arcs on the outboard fringe. Gated by a large-scale mask so
        # they cluster into chains along part of the margin rather than
        # speckling evenly all the way round.
        fringe = (~inside) & (d < rad + 0.22 * R0)
        arcn = fbm3(L * 18.0, seed + 21, 3)
        arcwhere = fbm3(L * 2.0, seed + 33, 2)
        isl = fringe & (arcn > 0.62) & (arcwhere > 0.48)
        zi = 40.0 + 300.0 * np.clip((arcn - 0.62) / 0.28, 0, 1)

        zt = np.where(inside, z, np.where(isl, zi, -9999.0))
        cur = elev[idx]
        elev[idx] = np.where(zt > cur, zt, cur)
        claims[idx] += inside.astype(np.int16)
        # ridged relief reserved for collisions, accumulated per craton
        ridged = 1.0 - np.abs(2.0 * fbm3(L * 5.0, seed + 29, 4) - 1.0)
        belt[idx] = np.maximum(belt[idx], np.where(inside, ridged ** 2, 0.0))

    elev = elev.reshape(th, tw)
    claims = claims.reshape(th, tw)
    belt = belt.reshape(th, tw)

    # Orogeny: where cratons overlap they are colliding, so raise a mountain
    # belt along the suture instead of letting one block simply overwrite the
    # other. Smoothed so the range has flanks rather than a hard seam.
    # Collision uplift is kept deliberately gentle. Overlapping discs intersect
    # along circular arcs, and a strong uplift there paints an obviously
    # geometric scar; the mountains that read as mountains are the fold belts
    # generated inside each craton above.
    suture = _smooth((claims >= 2).astype(float), 6)
    rough = fbm3(BS.unit(LON.ravel(), LAT.ravel()) * 7.0, 401, 3).reshape(th, tw)
    elev += np.clip(suture * 1.2, 0, 1) * (140.0 + 420.0 * belt) * (0.5 + 1.0 * rough)

    # continental shelf apron, then drop toward the era's sea level
    crust = (elev > -1500).astype(float)
    apron = crust
    for k in (2, 4, 7):
        apron = np.maximum(apron, _smooth(apron, k))
    elev = np.maximum(elev, -4800.0 + 4500.0 * np.clip(apron, 0, 1))
    land = elev > 0
    elev = np.where(land, elev - flood, elev)
    return elev
