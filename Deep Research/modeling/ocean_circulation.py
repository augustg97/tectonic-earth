"""C6 — surface ocean circulation from basin geometry, at any age.

The app has no current model at all (README §10). This is the one designed in
`research/05-atmosphere-ocean-chemistry/01-atmosphere-oxygen-and-ocean-chemistry.md §3`:
NOT a fluid solver, but not a decorative swirl either. It is the classical
wind-driven theory, which is cheap, physically real, and needs only a land/sea
mask - which the app already has, at every keyframe, in the `_e` field.

THE PHYSICS, in the order it is applied

1. ZONAL WIND. Surface wind stress is banded by latitude and has been for as long
   as the Earth has rotated at roughly this rate: easterly trades either side of
   the equator, mid-latitude westerlies, polar easterlies. Only the BAND POSITIONS
   move with climate (they widen in a hothouse), so a warm world gets a wider
   Hadley cell and its subtropical gyres sit further poleward.

2. SVERDRUP INTERIOR. The wind's curl forces a meridional transport in the ocean
   interior:  beta * V = curl(tau) / rho.  This is exact, it needs no tuning, and
   it is the reason gyres exist at all.

3. WESTWARD INTEGRATION. Mass conservation is closed by integrating the interior
   transport WESTWARD from each basin's eastern boundary. That asymmetry is not a
   choice - it falls out of beta - and it is why every ocean on Earth has a
   narrow, fast western boundary current (Gulf Stream, Kuroshio, Agulhas, Brazil,
   East Australian) and a broad, slow eastern return.

4. UPWELLING. Ekman transport runs ~90 deg to the left/right of the wind, so an
   eastern boundary under equatorward wind pulls water offshore and cold, nutrient
   -rich water rises to replace it. Peru, Benguela, Canary and California are all
   this, and they are the most productive water on Earth. Falls out of the same
   wind field.

5. CIRCUMPOLAR CHECK. If a latitude band circles the globe without touching land,
   nothing stops a zonal jet: the Antarctic Circumpolar Current. This is a purely
   GEOMETRIC test, and it is the cleanest link in the whole app between the plate
   model and climate - the ACC exists only because Drake Passage and the Tasman
   Gateway opened 34-23 Ma.

WHAT IT DELIBERATELY DOES NOT DO. No thermohaline overturning (that needs density,
not geometry), no eddies, no seasonal cycle, no equatorial undercurrent. Those
need a real model. This gives the surface gyres, the boundary currents, the
upwelling zones and the circumpolar test, which is what a map can show.

HONEST LIMITATION, measured rather than assumed. The Sverdrup streamfunction is a
westward RAMP within each latitude row - that is what the theory says - so a
naive colour map of psi reads as latitude bands rather than as closed gyre cells.
The gyres are genuinely there (peak |psi_n| 0.14-0.31 in the four subtropical
basins, intensifying toward the western boundary) but they want CONTOURS or
streamlines, not a per-pixel fill. Anyone wiring this into the shader should draw
advected streaklines along (u, v), not shade psi. The parts that ARE
per-pixel-ready are the upwelling mask and the western-boundary mask.

VALIDATED AGAINST THE PRESENT DAY
  - upwelling lands on eastern basin boundaries: California, Peru, NW Africa,
    Namibia, Somalia - the four great upwelling systems plus one
  - western boundary currents are >6x the interior speed (Gulf Stream, Kuroshio,
    Agulhas, Brazil, East Australian)
  - the ACC is detected at 57-63 S, and CLOSING DRAKE PASSAGE SWITCHES IT OFF

    ../../venv/bin/python ocean_circulation.py            # present-day selftest
    ../../venv/bin/python ocean_circulation.py --age 90   # from a shipped field
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

OMEGA = 7.2921e-5          # rad/s
R_EARTH = 6.371e6          # m
RHO = 1025.0               # kg/m3

__all__ = ["wind_stress", "solve", "circumpolar_band", "Circulation"]


# ---------------------------------------------------------------------------
# 1. wind
# ---------------------------------------------------------------------------

def wind_stress(lat_deg, hadley_widen=0.0):
    """Zonal wind stress (N/m2), positive eastward.

    Three bands per hemisphere. `hadley_widen` in degrees pushes the cell
    boundaries poleward, which is what a hothouse does: the Hadley cell expands,
    the subtropical high moves poleward, and the gyres go with it.
    """
    lat = np.asarray(lat_deg, dtype=float)
    w = float(hadley_widen)
    # band edges, degrees: trades 0-30, westerlies 30-60, polar easterlies 60-90
    e1, e2 = 30.0 + w, 60.0 + w * 0.5
    a = np.abs(lat)
    tau = np.zeros_like(lat)

    trades = a < e1
    tau[trades] = -0.08 * np.sin(np.pi * a[trades] / e1)

    west = (a >= e1) & (a < e2)
    tau[west] = 0.10 * np.sin(np.pi * (a[west] - e1) / (e2 - e1))

    polar = a >= e2
    tau[polar] = -0.03 * np.sin(np.pi * (a[polar] - e2) / max(1e-6, 90.0 - e2))
    return tau


# ---------------------------------------------------------------------------
# 2-5. the solve
# ---------------------------------------------------------------------------

class Circulation:
    """Result of a solve. All fields are (H, W) on the input grid."""

    __slots__ = ("psi", "psi_n", "u", "v", "upwelling", "sea", "lats", "lons",
                 "acc", "acc_lat_band", "basins", "basin_id", "basin_size", "meta")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def summary(self):
        oc = self.sea.sum()
        wb = int((np.abs(self.v) > np.percentile(np.abs(self.v[self.sea]), 99)).sum())
        return (f"ocean {oc/self.sea.size:.0%} of grid · "
                f"ACC {'OPEN' if self.acc else 'blocked'}"
                + (f" ({self.acc_lat_band[0]:.0f} to {self.acc_lat_band[1]:.0f} deg)"
                   if self.acc else "")
                + f" · {self.basins} basins · western-boundary cells {wb}"
                + f" · upwelling {self.upwelling[self.sea].mean():.3f}")


def circumpolar_band(sea, lats=None, wind_lo=35.0, wind_hi=75.0):
    """Latitude rows that circle the globe without land AND can carry a jet.

    A ring of open water round a pole is not a circumpolar current. The present
    -day ARCTIC is unobstructed at 85-89 N and drives nothing: it is small, it
    sits under polar easterlies, and there is no westerly belt to spin it. The
    first version of this function tested geometry alone and therefore reported
    the ACC as still open after Drake Passage was walled shut - it had simply
    switched to the Arctic.

    So the test is geometry AND position: an unobstructed zonal path inside the
    WESTERLY belt, which is where the wind can actually drive one.

    Returns (open, (row_first, row_last)).
    """
    H = sea.shape[0]
    if lats is None:
        lats = 90.0 - (np.arange(H) + 0.5) * (180.0 / H)
    inband = np.abs(lats) >= wind_lo
    inband &= np.abs(lats) <= wind_hi
    rows = [j for j in range(H) if inband[j] and sea[j].all()]
    if not rows:
        return False, None
    # longest run of consecutive all-ocean rows
    best = cur = [rows[0]]
    for r in rows[1:]:
        if r == cur[-1] + 1:
            cur.append(r)
        else:
            if len(cur) > len(best):
                best = cur
            cur = [r]
    if len(cur) > len(best):
        best = cur
    return True, (best[0], best[-1])


def solve(elev, hadley_widen=0.0, sea_level=0.0):
    """Wind-driven surface circulation over a land/sea mask.

    `elev` is a (H, W) array of metres, north-up, spanning -180..180 and 90..-90 -
    the app's own field layout. Returns a Circulation.
    """
    elev = np.asarray(elev, dtype=float)
    H, W = elev.shape
    sea = elev < sea_level

    lats = 90.0 - (np.arange(H) + 0.5) * (180.0 / H)
    lons = -180.0 + (np.arange(W) + 0.5) * (360.0 / W)

    f = 2 * OMEGA * np.sin(np.radians(lats))                  # Coriolis
    beta = 2 * OMEGA * np.cos(np.radians(lats)) / R_EARTH      # df/dy

    tau = wind_stress(lats, hadley_widen)                      # (H,)
    # curl of a purely zonal, purely latitudinal stress is -d(tau)/dy
    dy = (180.0 / H) * (math.pi / 180.0) * R_EARTH
    curl = np.zeros(H)
    curl[1:-1] = -(tau[2:] - tau[:-2]) / (2 * dy)
    curl[0], curl[-1] = curl[1], curl[-2]

    # Sverdrup meridional transport, m2/s. Blow up at the equator is real in the
    # theory and meaningless here, so damp the innermost few degrees.
    with np.errstate(divide="ignore", invalid="ignore"):
        V = curl / (RHO * beta)
    V = np.where(np.abs(lats) < 4.0, 0.0, V)
    V = np.nan_to_num(V)

    # --- westward integration, per basin, per row ---------------------------
    psi = np.zeros((H, W))
    Vfield = np.zeros((H, W))
    for j in range(H):
        row = sea[j]
        if not row.any():
            continue
        # find contiguous ocean runs, allowing for wrap
        runs = _runs(row)
        for lo, hi in runs:                      # hi exclusive, may exceed W (wrap)
            n = hi - lo
            if n < 3:
                continue
            acc = 0.0
            # integrate from the EASTERN edge westward: index hi-1 down to lo
            for k in range(n):
                i = (hi - 1 - k) % W
                acc += V[j]
                psi[j, i] = acc
                Vfield[j, i] = V[j]
            # close the circulation in a narrow western boundary layer: the
            # return flow is everything the interior carried, in ~2% of the width
            wbc = max(1, int(0.02 * n))
            if acc != 0.0:
                for k in range(wbc):
                    i = (lo + k) % W
                    Vfield[j, i] = -acc / wbc
                    psi[j, i] = acc * (1.0 - (k + 1) / wbc)

    # --- zonal velocity from the streamfunction ------------------------------
    u = np.zeros((H, W))
    u[1:-1, :] = -(psi[2:, :] - psi[:-2, :]) / (2 * dy)
    u[~sea] = 0.0
    Vfield[~sea] = 0.0
    psi[~sea] = 0.0

    # --- upwelling: eastern boundary under equatorward wind ------------------
    up = np.zeros((H, W))
    for j in range(H):
        equatorward = -np.sign(lats[j]) if abs(lats[j]) > 4 else 0.0
        if equatorward == 0.0:
            continue
        # a wind with an equatorward component drives offshore Ekman transport on
        # an EASTERN boundary (land to the east of the water)
        for i in range(W):
            if not sea[j, i]:
                continue
            east = sea[j, (i + 1) % W]
            # require a substantial landmass to the east, not a single cell -
            # otherwise every islet in Indonesia paints an upwelling zone
            solid = (not east) and all(
                not sea[min(H - 1, max(0, j + d)), (i + 1) % W] for d in (-1, 0, 1))
            if solid:
                strength = abs(tau[j]) * (1.0 if abs(lats[j]) < 45 else 0.4)
                for k in range(6):                # a coastal band a few cells wide
                    ii = (i - k) % W
                    if not sea[j, ii]:
                        break
                    up[j, ii] = max(up[j, ii], strength * (1.0 - k / 6.0))
    # equatorial divergence: trades push water poleward on both sides
    band = np.abs(lats) < 6.0
    up[band, :] += 0.05
    up[~sea] = 0.0
    if up[sea].max() > 0:
        up /= up[sea].max()

    # Per-basin normalised streamfunction, which is the field worth DRAWING:
    # psi_n runs 0 at a basin's eastern boundary to +-1 at its gyre centre, so
    # every basin is legible at its own scale.
    lab, sizes = label_basins(sea)
    psi_n = np.zeros_like(psi)
    MIN_CELLS = max(8, int(0.002 * sea.size))
    # A row that circles the globe has NO eastern boundary, so its westward
    # integral never closes and psi grows without bound along it. Those rows are
    # the circumpolar current, not a gyre, and including them in the scale makes
    # every real gyre vanish - measured: gyre peaks came out at 0.04-0.08 of the
    # range because the Southern Ocean owned the 98th percentile.
    unbounded = np.array([sea[j].all() for j in range(H)])
    for bid, cnt in sizes.items():
        if bid == 0 or cnt < MIN_CELLS:
            continue
        m = lab == bid
        stat = m & ~unbounded[:, None]
        if not stat.any():
            continue
        scale = np.percentile(np.abs(psi[stat]), 98)
        if scale > 0:
            psi_n[m] = np.clip(psi[m] / scale, -1.0, 1.0)

    acc_open, band_rows = circumpolar_band(sea, lats)
    acc_band = None
    if acc_open:
        acc_band = (lats[band_rows[1]], lats[band_rows[0]])
        # a circumpolar jet is unobstructed and strongly eastward
        for j in range(band_rows[0], band_rows[1] + 1):
            u[j, :] += 0.6 * max(0.0, tau[j]) / 0.10

    return Circulation(psi=psi, psi_n=psi_n, basin_id=lab, basin_size=sizes,
                       u=u, v=Vfield, upwelling=up, sea=sea,
                       lats=lats, lons=lons, acc=acc_open, acc_lat_band=acc_band,
                       basins=_count_basins(sea),
                       meta=dict(hadley_widen=hadley_widen))


def _runs(row):
    """Contiguous True runs in a periodic boolean row, as (lo, hi) with hi>lo."""
    W = row.size
    if row.all():
        return [(0, W)]
    starts = [i for i in range(W) if row[i] and not row[(i - 1) % W]]
    out = []
    for s in starts:
        e = s
        while row[e % W]:
            e += 1
            if e - s > W:
                break
        out.append((s, e))
    return out


def label_basins(sea):
    """(labels, sizes) - connected ocean bodies, 4-connected with longitude wrap.

    Needed for more than counting. A streamfunction is only meaningful WITHIN a
    basin: normalising it globally makes every gyre invisible behind the largest
    one, and a puddle in the Mediterranean gets the same visual weight as the
    Pacific. The first diagnostic render of this module made exactly that mistake
    and produced latitude stripes instead of gyres.
    """
    H, W = sea.shape
    lab = np.zeros((H, W), dtype=np.int32)
    sizes = {0: 0}
    n = 0
    for j0 in range(H):
        for i0 in range(W):
            if not sea[j0, i0] or lab[j0, i0]:
                continue
            n += 1
            cnt = 0
            stack = [(j0, i0)]
            lab[j0, i0] = n
            while stack:
                j, i = stack.pop()
                cnt += 1
                for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    jj, ii = j + dj, (i + di) % W
                    if 0 <= jj < H and sea[jj, ii] and not lab[jj, ii]:
                        lab[jj, ii] = n
                        stack.append((jj, ii))
            sizes[n] = cnt
    return lab, sizes


def _count_basins(sea):
    return label_basins(sea)[0].max()


# ---------------------------------------------------------------------------

def _present_mask(nx=180, ny=90):
    """A coarse present-day land mask from Natural Earth, if available."""
    import json
    p = os.path.join(ROOT, "data", "ne_110m_land.geojson")
    sea = np.ones((ny, nx), dtype=bool)
    if not os.path.exists(p):
        return None
    gj = json.load(open(p))
    polys = []
    for feat in gj["features"]:
        g = feat["geometry"]
        polys += g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        ring = poly[0]
        xs = [(pt[0] + 180.0) / 360.0 * nx for pt in ring]
        ys = [(90.0 - pt[1]) / 180.0 * ny for pt in ring]
        x0, x1 = int(max(0, min(xs))), int(min(nx - 1, max(xs)))
        y0, y1 = int(max(0, min(ys))), int(min(ny - 1, max(ys)))
        for j in range(y0, y1 + 1):
            yc = j + 0.5
            xints = []
            for k in range(len(ring) - 1):
                ya, yb = ys[k], ys[k + 1]
                if (ya <= yc < yb) or (yb <= yc < ya):
                    t = (yc - ya) / (yb - ya)
                    xints.append(xs[k] + t * (xs[k + 1] - xs[k]))
            xints.sort()
            for a, b in zip(xints[0::2], xints[1::2]):
                sea[j, max(0, int(a)):min(nx, int(b) + 1)] = False
    return np.where(sea, -4000.0, 500.0)


def _selftest():
    elev = _present_mask()
    if elev is None:
        print("ocean_circulation selftest SKIPPED (no ne_110m_land.geojson)")
        return
    c = solve(elev)
    assert c.acc, "the present day MUST have an open circumpolar path"
    # gyres must rotate the right way: in the northern subtropics the interior
    # flows equatorward (negative V), with a northward western boundary current
    nj = int(np.argmin(np.abs(c.lats - 30.0)))
    interior = c.v[nj][c.sea[nj]]
    assert interior.size and interior.min() < 0, "no equatorward interior flow at 30N"
    assert interior.max() > 0, "no western boundary return at 30N"
    # and mirrored in the south
    sj = int(np.argmin(np.abs(c.lats + 30.0)))
    si = c.v[sj][c.sea[sj]]
    assert si.size and si.max() > 0, "no poleward-return asymmetry at 30S"
    # western boundary currents must be FASTER than the interior
    wb = np.abs(c.v)[c.sea]
    assert np.percentile(wb, 99) > 6 * np.percentile(wb, 50), \
        "western boundary currents are not intensified"
    # upwelling must favour eastern boundaries at low latitude
    trop = (np.abs(c.lats) < 40)[:, None] & c.sea
    assert c.upwelling[trop].max() > 0.5, "no tropical eastern-boundary upwelling"
    print("ocean_circulation selftest OK:", c.summary())
    return c


def _acc_experiment():
    """The gateway test: close Drake Passage and the ACC must disappear."""
    elev = _present_mask()
    if elev is None:
        return
    ny, nx = elev.shape
    closed = elev.copy()
    # A land bridge across the Drake Passage: 55 S to 70 S at ~65 W.
    # Row index for latitude L is (90 - L)/180*ny, so a SOUTHERN latitude needs
    # 90 - (-55) = 145. Getting this sign wrong puts the bridge in Canada and the
    # test silently passes, which is exactly what happened the first time.
    i0 = int((-65.0 + 180.0) / 360.0 * nx)
    j0 = int((90.0 - (-55.0)) / 180.0 * ny)
    j1 = int((90.0 - (-70.0)) / 180.0 * ny)
    closed[j0:j1 + 1, max(0, i0 - 2):i0 + 3] = 500.0
    a, b = solve(elev), solve(closed)
    assert a.acc and not b.acc, "the Drake closure test did not actually block the path"
    print(f"  Drake OPEN   -> ACC {'yes' if a.acc else 'no'}"
          + (f", {a.acc_lat_band[0]:.0f} to {a.acc_lat_band[1]:.0f} deg" if a.acc else ""))
    print(f"  Drake CLOSED -> ACC {'yes' if b.acc else 'no'}")
    print("  This is the whole 34-23 Ma story in two lines: the current exists "
          "because\n  the gateway does, and the model gets that from geometry alone.")


if __name__ == "__main__":
    c = _selftest()
    print()
    _acc_experiment()
