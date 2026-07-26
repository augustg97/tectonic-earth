"""A zonal energy-balance climate model for deep time.

Tectonic Earth's climate table hand-authors an ice line (`iceS`) for every
keyframe, and the ice audit then checks the DRAWN ice area against the literature.
That works, but it makes the ice line an input rather than a consequence: when the
drawn ice disagrees with the record there is no physics to appeal to.

This module is the physics. It is a one-dimensional diffusive energy-balance model
(Budyko-Sellers-North), which is the smallest model that reproduces the three
things we actually need:

    * a latitudinal temperature profile from solar forcing alone;
    * an ice line that emerges from the ice-albedo feedback rather than being set;
    * the SNOWBALL BIFURCATION - the reason a Cryogenian Earth freezes to the
      equator and then needs ~350x modern CO2 to escape.

It is deliberately not a GCM. It has no continents, no ocean heat transport that
knows where the ocean is, and no seasons. Use it to CHECK the table's ice line
against the table's own CO2 and solar luminosity, not to replace the shader.

    >>> r = solve(co2_ppm=280, age_ma=0)
    >>> round(r.gmst, 1), round(r.ice_line, 1)
    (13.4, 71.8)

KNOWN LIMITS - read before quoting a number from this
-----------------------------------------------------
* Calibrated on the present: 13.4 C and an ice line at 71.8 deg against a real
  14.0-15.0 C and a real margin near 70-75 deg. Good.
* It UNDERSTATES hothouses. At 1000 ppm and 90 Ma it gives 17 C where PhanDA gives
  ~30-36 C for the Turonian. A 1-D model with no clouds, no water-vapour
  amplification of the lapse rate and no continents cannot produce that; its
  effective sensitivity is ~2.5 C per doubling against PhanDA's ~8 C apparent
  Earth-system sensitivity, which folds in the slow feedbacks. Use the EBM for the
  SHAPE of the response and the position of the ice line, not for absolute GMST in
  a greenhouse.
* The snowball escape threshold it finds (~1400x preindustrial at 700 Ma) is high
  against the literature's ~350x, for the reason flagged under co2_forcing: the
  logarithmic law is wrong by a large factor at 10^5 ppm. The HYSTERESIS it
  demonstrates - a freeze-in threshold two to three orders of magnitude below the
  escape threshold - is the robust and interesting result.
* No seasons, no ocean heat transport that knows where the ocean is, no land/sea
  contrast, no orography.

Requires numpy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

__all__ = ["Result", "solve", "solar_luminosity", "co2_forcing", "sweep_co2",
           "snowball_thresholds"]


# ---------------------------------------------------------------------------
# physical constants and standard parameter values
# ---------------------------------------------------------------------------

S0_PRESENT = 1361.0        # W/m2, present total solar irradiance
A_OLR = 210.0              # W/m2, outgoing longwave intercept at 0 C  (Budyko)
B_OLR = 2.1                # W/m2/K, outgoing longwave slope
D_DIFF = 0.55              # W/m2/K, meridional diffusivity (North 1975 ~0.6)
ALBEDO_ICE = 0.62          # snow/ice surface
ALBEDO_OPEN = 0.30         # global mean ice-free planetary albedo
T_FREEZE = -10.0           # C, mean-annual temperature of the ice margin
S2 = -0.482                # 2nd Legendre coefficient of the insolation distribution
CO2_REF = 280.0            # ppm, preindustrial reference
F2X = 5.35                 # W/m2 per natural log of CO2 ratio (~3.7 W/m2 per doubling)


@dataclass
class Result:
    lat: np.ndarray            # degrees, cell centres
    temp: np.ndarray           # C, mean annual, zonal
    ice: np.ndarray            # bool, ice-covered
    gmst: float                # C, area-weighted
    ice_line: float            # degrees latitude of the ice margin (90 = ice free)
    ice_fraction: float        # fraction of planetary surface with ice
    co2_ppm: float
    solar: float               # S0 used, W/m2
    snowball: bool
    iterations: int
    converged: bool


# ---------------------------------------------------------------------------

def solar_luminosity(age_ma: float) -> float:
    """Gough (1981) standard solar model, as already used in build/climate.py.

    L/L0 = 1 / (1 + 0.4*(1 - t/t0)), t0 = 4570 Myr, t = 4570 - age.
    Works for negative ages (the future) too."""
    t0 = 4570.0
    t = t0 - age_ma
    return S0_PRESENT / (1.0 + 0.4 * (1.0 - t / t0))


def co2_forcing(co2_ppm: float, ref_ppm: float = CO2_REF) -> float:
    """Radiative forcing in W/m2 relative to `ref_ppm`.

    The logarithmic law is calibrated for the modern range and is known to
    understate forcing above ~1000 ppm and overstate it in the very high
    (snowball-escape) range, where band saturation and continuum absorption take
    over. Treat forcings beyond ~4000 ppm as indicative only."""
    return F2X * np.log(max(co2_ppm, 1e-6) / ref_ppm)


def _insolation_shape(x: np.ndarray) -> np.ndarray:
    """Normalised annual-mean insolation vs x = sin(latitude)."""
    p2 = 0.5 * (3.0 * x * x - 1.0)
    return 1.0 + S2 * p2


def _albedo(temp: np.ndarray, ice: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Planetary albedo: open-water/land value with a mild latitude increase for
    slant incidence, replaced by the ice value where the surface is frozen."""
    base = ALBEDO_OPEN + 0.08 * (0.5 * (3.0 * x * x - 1.0))
    return np.where(ice, ALBEDO_ICE, base)


def solve(co2_ppm: float = CO2_REF,
          age_ma: float = 0.0,
          n: int = 180,
          s0: Optional[float] = None,
          diffusivity: float = D_DIFF,
          max_iter: int = 400,
          relax: float = 0.35) -> Result:
    """Solve the EBM for a given CO2 and age (age sets solar luminosity).

    Returns a Result. `ice_line` is the latitude of the ice margin, 90 if ice-free
    and 0 if the planet is a hard snowball."""
    s0 = solar_luminosity(age_ma) if s0 is None else s0
    q = s0 / 4.0

    # grid in x = sin(lat), uniform in x so each cell has equal area
    xe = np.linspace(-1.0, 1.0, n + 1)
    x = 0.5 * (xe[:-1] + xe[1:])
    dx = xe[1] - xe[0]
    lat = np.degrees(np.arcsin(np.clip(x, -1, 1)))
    sfun = _insolation_shape(x)

    # diffusion operator: d/dx[ D (1-x^2) dT/dx ], flux-conservative
    # edge coefficients (interior edges only; no flux through the poles)
    ke = diffusivity * (1.0 - xe ** 2) / dx ** 2
    ke[0] = ke[-1] = 0.0

    # A + B T = q S (1 - alpha) + div( D (1-x^2) grad T )
    # =>  (B + k_left + k_right) T_i - k_left T_{i-1} - k_right T_{i+1}
    #      = q S_i (1-alpha_i) - A
    kl = ke[:-1]
    kr = ke[1:]
    main_base = B_OLR + kl + kr

    ftot = co2_forcing(co2_ppm)          # positive forcing lowers effective A
    a_eff = A_OLR - ftot

    temp = 15.0 + 30.0 * (1.0 - x ** 2) - 25.0   # a sensible warm start
    ice = temp < T_FREEZE
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        alb = _albedo(temp, ice, x)
        rhs = q * sfun * (1.0 - alb) - a_eff

        # tridiagonal solve (Thomas algorithm)
        a = -kl.copy()          # sub-diagonal
        b = main_base.copy()    # diagonal
        c = -kr.copy()          # super-diagonal
        d = rhs.copy()
        for i in range(1, n):
            m = a[i] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        new = np.empty(n)
        new[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            new[i] = (d[i] - c[i] * new[i + 1]) / b[i]

        temp_next = temp + relax * (new - temp)
        ice_next = temp_next < T_FREEZE
        done = np.max(np.abs(temp_next - temp)) < 1e-6 and np.array_equal(ice_next, ice)
        temp, ice = temp_next, ice_next
        if done:
            converged = True
            break

    gmst = float(np.mean(temp))          # equal-area cells, so a plain mean
    ice_fraction = float(np.mean(ice))
    if not ice.any():
        ice_line = 90.0
    elif ice.all():
        ice_line = 0.0
    else:
        # lowest |latitude| that is ice-covered
        ice_line = float(np.min(np.abs(lat[ice])))
    snowball = ice_fraction > 0.95

    return Result(lat=lat, temp=temp, ice=ice, gmst=gmst, ice_line=ice_line,
                  ice_fraction=ice_fraction, co2_ppm=co2_ppm, solar=s0,
                  snowball=snowball, iterations=it, converged=converged)


def sweep_co2(co2_values, age_ma: float = 0.0, **kw) -> list:
    return [solve(co2_ppm=c, age_ma=age_ma, **kw) for c in co2_values]


def snowball_thresholds(age_ma: float = 700.0, lo: float = 20.0, hi: float = 400000.0,
                        tol: float = 0.01) -> dict:
    """Find the two CO2 bifurcation points at a given age, by bisection.

    `entry` is the CO2 below which a warm start freezes over; `escape` is the CO2
    a frozen planet needs to deglaciate. They differ - that hysteresis IS the
    snowball problem, and it is why the Cryogenian terminations required a CO2
    spike of order 10^5 ppm rather than a gentle warming."""
    def frozen_from_warm(c):
        return solve(co2_ppm=c, age_ma=age_ma).snowball

    def frozen_from_cold(c):
        r = solve(co2_ppm=c, age_ma=age_ma, n=180)
        # restart from a fully glaciated state
        r2 = _solve_from(r, c, age_ma, start_temp=-40.0)
        return r2.snowball

    a, b = lo, hi
    for _ in range(60):
        m = np.sqrt(a * b)
        if frozen_from_warm(m):
            a = m
        else:
            b = m
        if b / a < 1 + tol:
            break
    entry = np.sqrt(a * b)

    a, b = lo, hi
    for _ in range(60):
        m = np.sqrt(a * b)
        if frozen_from_cold(m):
            a = m
        else:
            b = m
        if b / a < 1 + tol:
            break
    escape = np.sqrt(a * b)
    return dict(age_ma=age_ma, entry_ppm=float(entry), escape_ppm=float(escape),
                escape_x_modern=float(escape / CO2_REF))


def _solve_from(_r: Result, co2_ppm: float, age_ma: float, start_temp: float) -> Result:
    """Re-solve starting from a uniformly cold state, to find the cold branch."""
    n = 180
    s0 = solar_luminosity(age_ma)
    q = s0 / 4.0
    xe = np.linspace(-1.0, 1.0, n + 1)
    x = 0.5 * (xe[:-1] + xe[1:])
    dx = xe[1] - xe[0]
    lat = np.degrees(np.arcsin(np.clip(x, -1, 1)))
    sfun = _insolation_shape(x)
    ke = D_DIFF * (1.0 - xe ** 2) / dx ** 2
    ke[0] = ke[-1] = 0.0
    kl, kr = ke[:-1], ke[1:]
    main_base = B_OLR + kl + kr
    a_eff = A_OLR - co2_forcing(co2_ppm)

    temp = np.full(n, start_temp)
    ice = temp < T_FREEZE
    it = 0
    converged = False
    for it in range(1, 401):
        alb = _albedo(temp, ice, x)
        rhs = q * sfun * (1.0 - alb) - a_eff
        a = -kl.copy(); b = main_base.copy(); c = -kr.copy(); d = rhs.copy()
        for i in range(1, n):
            m = a[i] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        new = np.empty(n)
        new[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            new[i] = (d[i] - c[i] * new[i + 1]) / b[i]
        tn = temp + 0.35 * (new - temp)
        inew = tn < T_FREEZE
        done = np.max(np.abs(tn - temp)) < 1e-6 and np.array_equal(inew, ice)
        temp, ice = tn, inew
        if done:
            converged = True
            break
    frac = float(np.mean(ice))
    if not ice.any():
        il = 90.0
    elif ice.all():
        il = 0.0
    else:
        il = float(np.min(np.abs(lat[ice])))
    return Result(lat, temp, ice, float(np.mean(temp)), il, frac, co2_ppm, s0,
                  frac > 0.95, it, converged)


# ---------------------------------------------------------------------------

def _selftest() -> None:
    r = solve(co2_ppm=280, age_ma=0)
    assert r.converged, "present-day case did not converge"
    assert 10.0 < r.gmst < 18.0, f"present GMST out of range: {r.gmst:.1f}"
    assert 60.0 < r.ice_line < 80.0, f"present ice line implausible: {r.ice_line:.1f}"
    # warming with CO2, monotonically
    gm = [solve(co2_ppm=c, age_ma=0).gmst for c in (140, 280, 560, 1120, 2240)]
    assert all(b > a for a, b in zip(gm, gm[1:])), gm
    # sensitivity per doubling should be a few degrees, with slow feedbacks on
    per_doubling = (gm[-1] - gm[0]) / 4.0
    assert 1.0 < per_doubling < 12.0, per_doubling
    # a high-CO2 world is ice free
    assert solve(co2_ppm=4000, age_ma=90).ice_line == 90.0
    # a cold, faint-Sun world freezes
    assert solve(co2_ppm=60, age_ma=700).snowball
    print(f"climate_ebm selftest OK: present GMST {r.gmst:.1f} C, ice line "
          f"{r.ice_line:.1f} deg, ice fraction {r.ice_fraction:.3f}; "
          f"{per_doubling:.1f} C per CO2 doubling over 140-2240 ppm")


if __name__ == "__main__":
    _selftest()
    print()
    print("  age    CO2      S0     GMST   ice line  ice frac")
    for age, co2, label in [(0, 280, "preindustrial"),
                            (21, 190, "LGM"),
                            (90, 1000, "Turonian greenhouse"),
                            (300, 300, "Late Palaeozoic Ice Age"),
                            (445, 3000, "Hirnantian (high CO2, cold: the paradox)"),
                            (700, 300, "Cryogenian, faint Sun"),
                            (700, 100000, "Cryogenian snowball escape")]:
        r = solve(co2_ppm=co2, age_ma=age)
        print(f"{age:5.0f}  {co2:7.0f}  {r.solar:6.1f}  {r.gmst:6.1f}   "
              f"{r.ice_line:6.1f}   {r.ice_fraction:6.3f}   {label}")
    print()
    print("Snowball bifurcation at 700 Ma (faint Sun):")
    th = snowball_thresholds(700.0)
    print(f"   freeze-in below ~{th['entry_ppm']:.0f} ppm; "
          f"escape needs ~{th['escape_ppm']:.0f} ppm "
          f"(~{th['escape_x_modern']:.0f}x modern)")
