"""C1 / C3 / C4 / C10 — audit build/climate.py's SYSTEM table against the literature.

READ-ONLY. Four independent checks, each of which can fail on its own:

  C1  GMST against PhanDA (Judd et al. 2024, Science 385, eadk3705), the current
      standard: range 11-36 C over 485-0 Ma, global maximum in the Turonian
      (93.9-89.39 Ma), five named climate states.
  C3  O2 against GEOCARBSULF and Krause et al. (2022): a broad Permo-Carboniferous
      maximum near 30% (NOT 35%), below present until the end of the Devonian.
  C4  Internal consistency of GMST against CO2. PhanDA reports an APPARENT
      Earth-system sensitivity of ~8 C per CO2 doubling across the Phanerozoic -
      much larger than the ~3 C equilibrium sensitivity because a deep-time
      average folds in ice sheets, vegetation and weathering. If our CO2 doubles
      between two ages and our GMST barely moves, one of the columns is wrong.
  C10 The faint young Sun. Solar luminosity is -8% at 1000 Ma, so a Tonian frame
      must be held up by CO2 or it will be spuriously cold. Check that the table
      compensates rather than simply running cold.

    ../../venv/bin/python climate_audit.py
    ../../venv/bin/python climate_audit.py --md out.md
"""

from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, HERE)
sys.path.insert(0, BUILD)

import deeptime as dt                                    # noqa: E402

# --- PhanDA published anchors -------------------------------------------------
# The full time series is in the paper's supplementary data. These are the values
# stated in the paper and its coverage, and they are enough to catch a table that
# is wrong in KIND rather than in detail.
PHANDA = {
    "coverage": (485.0, 0.0),
    "gmst_range": (11.0, 36.0),
    "max_interval": ("Turonian", 93.9, 89.39, 36.0),
    "min_note": "Late Pleistocene glacial maxima, ~11 C",
    "sensitivity_C_per_doubling": 8.0,
    "states": [("icehouse", None, 18.0), ("cool greenhouse", 18.0, 24.0),
               ("warm greenhouse", 24.0, 30.0), ("hothouse", 30.0, None)],
    "cite": "Judd, Tierney et al. 2024, Science 385, eadk3705",
}

# --- O2 reference shape -------------------------------------------------------
O2_REF = {
    "peak_pct": 30.0, "peak_window": (320, 260),
    "note": "Krause et al. 2022 Annu. Rev.; ~30% is current, 35% is the high end "
            "of older GEOCARBSULF runs",
    "below_present_until": 360.0,
}


class F:
    def __init__(self, check, sev, detail, evidence, fix=""):
        self.check, self.sev, self.detail = check, sev, detail
        self.evidence, self.fix = evidence, fix


def table():
    """[(age, gmst, co2, o2, sol), ...] from climate.system_at(), past only."""
    import climate
    ages = sorted({abs(r[0]) for r in climate.SYSTEM} | {abs(r[0]) for r in climate.CLIMATE})
    out = []
    for a in ages:
        if a > 1000:
            continue
        try:
            s = climate.system_at(a)
        except Exception:                                  # noqa: BLE001
            continue
        out.append((a, s.get("gmst"), s.get("co2"), s.get("o2"), s.get("sol")))
    return out


def run():
    rows = table()
    if not rows:
        return rows, [F("SETUP", "HIGH", "could not read climate.system_at()", "")]
    out = []

    phan = [r for r in rows if 0 <= r[0] <= 485 and r[1] is not None]

    # ---- C1: range ----------------------------------------------------------
    lo, hi = PHANDA["gmst_range"]
    ours_lo = min(r[1] for r in phan)
    ours_hi = max(r[1] for r in phan)
    hot_age = max(phan, key=lambda r: r[1])[0]
    if ours_hi < 30.0:
        out.append(F("C1-RANGE", "HIGH",
                     f"our Phanerozoic GMST maximum is {ours_hi:.1f} C at {hot_age:g} Ma; "
                     f"PhanDA's is {hi:.0f} C. We never reach the hothouse state at all.",
                     PHANDA["cite"],
                     "raise the Cretaceous and Early Eocene rows"))
    elif ours_hi < hi - 3:
        out.append(F("C1-RANGE", "MED",
                     f"our maximum {ours_hi:.1f} C at {hot_age:g} Ma vs PhanDA {hi:.0f} C "
                     f"(short by {hi-ours_hi:.1f} C)", PHANDA["cite"], ""))
    if ours_lo > lo + 3:
        out.append(F("C1-RANGE", "MED",
                     f"our Phanerozoic minimum is {ours_lo:.1f} C; PhanDA reaches "
                     f"{lo:.0f} C ({PHANDA['min_note']})", PHANDA["cite"], ""))

    # ---- C1: is the maximum in the right place? -----------------------------
    name, mb, mt, mv = PHANDA["max_interval"]
    near = [r for r in phan if mt - 12 <= r[0] <= mb + 12]
    if near:
        best_near = max(near, key=lambda r: r[1])[1]
        if best_near < ours_hi - 1.5:
            out.append(F("C1-PEAK", "MED",
                         f"our global maximum sits at {hot_age:g} Ma, but PhanDA's is the "
                         f"{name} ({mb}-{mt} Ma) where we have only {best_near:.1f} C",
                         PHANDA["cite"],
                         f"the {name} should be the single warmest frame"))

    # ---- C1: climate states -------------------------------------------------
    counts = {}
    for a, g, *_ in phan:
        counts[dt.climate_state(g).name] = counts.get(dt.climate_state(g).name, 0) + 1
    if not counts.get("hothouse"):
        out.append(F("C1-STATE", "MED",
                     "no keyframe in 485-0 Ma reaches the hothouse state (>30 C). PhanDA "
                     "finds Earth spent MORE of the Phanerozoic warm than cold.",
                     PHANDA["cite"], "check the Cretaceous and Early Eocene"))

    # ---- C3: oxygen ---------------------------------------------------------
    o2 = [(a, v) for a, _, _, v, _ in rows if v is not None and a <= 1000]
    if o2:
        pk_age, pk = max(((a, v) for a, v in o2), key=lambda t: t[1])
        w0, w1 = O2_REF["peak_window"]
        if pk > 32:
            out.append(F("C3-O2", "MED",
                         f"our O2 peak is {pk:.1f}% at {pk_age:g} Ma; the current review "
                         f"puts it near {O2_REF['peak_pct']:.0f}%", O2_REF["note"],
                         "lower the Permo-Carboniferous peak toward 30%"))
        if not (w1 - 25 <= pk_age <= w0 + 25):
            out.append(F("C3-O2", "MED",
                         f"our O2 peak sits at {pk_age:g} Ma; it should fall in the "
                         f"Pennsylvanian-early Permian ({w0}-{w1} Ma)", O2_REF["note"], ""))
        dev = [v for a, v in o2 if 420 <= a <= 360]
        if dev and min(dev) > 21:
            out.append(F("C3-O2", "LOW",
                         "O2 does not drop below present at any point in the Devonian; "
                         "the models put it below present until near the end of it",
                         O2_REF["note"], ""))

    # ---- C4: GMST vs CO2 consistency ----------------------------------------
    pairs = [(a, g, c) for a, g, c, _o, _s in rows
             if g is not None and c and 0 <= a <= 485]
    pairs.sort()
    worst = []
    for (a0, g0, c0), (a1, g1, c1) in zip(pairs, pairs[1:]):
        if not c0 or not c1 or c0 <= 0 or c1 <= 0:
            continue
        doub = math.log2(c1 / c0)
        if abs(doub) < 0.5:                                # need a real CO2 change
            continue
        implied = doub * PHANDA["sensitivity_C_per_doubling"]
        actual = g1 - g0
        # allow generous slack: palaeogeography and solar also move GMST
        if abs(actual) < abs(implied) * 0.25:
            worst.append((abs(implied - actual), a0, a1, c0, c1, g0, g1, implied, actual))
    worst.sort(reverse=True)
    for _d, a0, a1, c0, c1, g0, g1, implied, actual in worst[:4]:
        out.append(F("C4-SENS", "LOW",
                     f"{a0:g}->{a1:g} Ma: CO2 {c0:.0f}->{c1:.0f} ppm implies about "
                     f"{implied:+.1f} C at PhanDA's ~8 C/doubling, but GMST moves "
                     f"{actual:+.1f} C ({g0:.1f}->{g1:.1f})",
                     "apparent Earth-system sensitivity, " + PHANDA["cite"],
                     "not necessarily an error - palaeogeography moves GMST too - but "
                     "worth a look"))

    # ---- C10: faint young Sun -----------------------------------------------
    ton = [r for r in rows if 720 <= r[0] <= 1000 and r[1] is not None]
    mod = [r for r in rows if r[0] <= 5 and r[1] is not None]
    if ton and mod:
        tmean = sum(r[1] for r in ton) / len(ton)
        now = mod[0][1]
        sol = [r[4] for r in ton if r[4] is not None]
        if sol:
            out.append(F("C10-SUN", "INFO",
                         f"Tonian mean GMST {tmean:.1f} C against {now:.1f} C today, with "
                         f"solar luminosity {sum(sol)/len(sol):+.1f}%. "
                         + ("Warmer despite a dimmer Sun - CO2 is compensating, which is "
                            "the expected resolution of the faint-young-Sun paradox."
                            if tmean > now else
                            "COLDER than today AND a dimmer Sun: check that the CO2 column "
                            "is high enough to hold a Tonian world above freezing."),
                         "Gough (1981); faint young Sun paradox", ""))
    return rows, out


def main():
    rows, findings = run()
    print(f"climate.py SYSTEM table: {len(rows)} ages sampled, "
          f"{len([r for r in rows if 0 <= r[0] <= 485])} inside PhanDA coverage\n")
    order = {"HIGH": 0, "MED": 1, "LOW": 2, "INFO": 3}
    for f in sorted(findings, key=lambda f: (order.get(f.sev, 9), f.check)):
        print(f"[{f.sev:4s}] {f.check}")
        print(f"        {f.detail}")
        if f.fix:
            print(f"        -> {f.fix}")
    if not findings:
        print("no findings")
    print(f"\n{len(findings)} findings")

    print("\n--- our curve at the ages that matter ---")
    print(f"{'age':>6} {'GMST':>7} {'state':>17} {'CO2':>7} {'O2':>6} {'sol%':>6}")
    for a in (0, 20, 50, 66, 90, 100, 145, 200, 250, 300, 360, 445, 485, 540, 720, 1000):
        r = min(rows, key=lambda r: abs(r[0] - a)) if rows else None
        if not r or abs(r[0] - a) > 12:
            continue
        st = dt.climate_state(r[1]).name if r[1] is not None else "?"
        print(f"{r[0]:>6.0f} {r[1] if r[1] is not None else float('nan'):>7.1f} {st:>17} "
              f"{r[2] if r[2] else 0:>7.0f} {r[3] if r[3] else 0:>6.1f} "
              f"{r[4] if r[4] is not None else 0:>6.2f}")


if __name__ == "__main__":
    main()
