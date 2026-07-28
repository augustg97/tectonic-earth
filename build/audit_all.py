"""Every read-only validator, run together, against a recorded baseline.

WHY A BASELINE AND NOT "ZERO FINDINGS". Some of these numbers cannot go to zero
and should not: `audit_label_windows` has two open findings that are genuine
disagreements about when Gondwana and Kazakhstania become identifiable, and
pretending otherwise would mean either falsifying a window or deleting a check.
What matters is that none of them moves BACKWARDS. So each check records what it
scored when it was adopted, and this fails when a number gets worse -- which is
the discipline the no-regression protocol asks for, applied to the audits
themselves rather than only to the frame switch.

  Deep Research/research reports/NO-REGRESSION-PROTOCOL.md section 5 is the
  source of these baselines. If a number legitimately improves, tighten the
  baseline here in the same commit, so the ratchet only ever turns one way.

    python3 audit_all.py            # all of them
    python3 audit_all.py --quick    # skip the two that need pyGPlates (~2 min)

Read-only throughout: nothing here writes to build/ or web/.
"""
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODELING = os.path.join(ROOT, "Deep Research", "modeling")
PY = sys.executable


class Check:
    """One validator, with what it must not do worse than."""

    def __init__(self, name, script, pattern, worse, baseline, why, slow=False):
        self.name, self.script, self.pattern = name, script, pattern
        self.worse, self.baseline, self.why, self.slow = worse, baseline, why, slow


def _n(txt, pattern):
    m = re.search(pattern, txt, re.M)
    return int(m.group(1)) if m else None


CHECKS = [
    Check("cards · HIGH", os.path.join(MODELING, "audit_cards.py"),
          r"=+ HIGH \((\d+)\)", "gt", 0,
          "a factual error in user-visible card text"),
    Check("cards · MED", os.path.join(MODELING, "audit_cards.py"),
          r"=+ MED \((\d+)\)", "gt", 0,
          "an unhedged contested claim, a date drift, or a coverage gap"),
    Check("label windows", os.path.join(MODELING, "audit_label_windows.py"),
          r"matched to a known block or assembly; (\d+) findings", "gt", 2,
          "a label drawn when the entity it names did not exist"),
    Check("curated biota · exceptions", os.path.join(MODELING, "audit_curated_biota.py"),
          r"EXCEPTION (\d+)", "ne", 10,
          "the ten localities the province model must never overwrite. A run that "
          "reclassifies Solnhofen as province-typical is a bug"),
    Check("curated biota · conflicts", os.path.join(MODELING, "audit_curated_biota.py"),
          r"CONFLICT (\d+)", "gt", 0,
          "a curated entry whose exception flag disagrees with what it looks like"),
    Check("climate table", os.path.join(MODELING, "climate_audit.py"),
          r"^(\d+) findings", "gt", 1,
          "the GMST/CO2/O2 table against PhanDA and Krause. One INFO finding is "
          "the faint-young-Sun check PASSING and is expected"),
    Check("ice extent", os.path.join(HERE, "ice_audit.py"),
          r"^(\d+) of \d+ checked keyframes fall outside", "gt", 1,
          "drawn ice area against the literature range, per keyframe. The one "
          "allowed finding is 570 Ma, and it is a KNOWN LIMIT of choosing one "
          "reference frame, not a defect: see README section 9"),
    Check("label plate vs text", os.path.join(HERE, "audit_label_plate.py"),
          r"^(\d+) findings", "gt", 0,
          "a label whose coordinate is a PALAEO position that happens to be land "
          "today, so it is silently tracked on whichever continent now sits "
          "there. Found eleven, including all four Sloss seas"),
    Check("frame gate · true regressions", os.path.join(MODELING, "regression_gate.py"),
          r"^  TRUE\s+(\d+)", "gt", 0,
          "features the frame switch made worse with no other explanation",
          slow=True),
]


def run_one(script, cwd):
    try:
        p = subprocess.run([PY, script], cwd=cwd, capture_output=True, text=True,
                           timeout=3600)
    except Exception as e:                                 # noqa: BLE001
        return f"FAILED TO RUN: {e}"
    return (p.stdout or "") + (p.stderr or "")


def main():
    quick = "--quick" in sys.argv
    outs, rows, bad = {}, [], 0
    for c in CHECKS:
        if quick and c.slow:
            rows.append((c.name, None, c.baseline, "skipped"))
            continue
        if c.script not in outs:
            cwd = MODELING if c.script.startswith(MODELING) else HERE
            print(f"  running {os.path.basename(c.script)} ...", flush=True)
            outs[c.script] = run_one(c.script, cwd)
        got = _n(outs[c.script], c.pattern)
        if got is None:
            # A check that cannot read its own script's output is a broken check,
            # and a broken check silently passing is the failure mode this whole
            # file exists to prevent (see README section 7.10).
            rows.append((c.name, None, c.baseline, "UNREADABLE"))
            bad += 1
            continue
        worse = (got > c.baseline) if c.worse == "gt" else (got != c.baseline)
        rows.append((c.name, got, c.baseline, "WORSE" if worse else "ok"))
        bad += bool(worse)

    w = max(len(r[0]) for r in rows)
    print()
    print(f"  {'check'.ljust(w)}   now   baseline   verdict")
    for name, got, base, verdict in rows:
        g = "  -" if got is None else f"{got:>3}"
        print(f"  {name.ljust(w)}   {g}   {base:>8}   {verdict}")
    print()
    if bad:
        print(f"{bad} check(s) moved backwards. Each one means:")
        for c in CHECKS:
            for name, _g, _b, v in rows:
                if name == c.name and v != "ok" and v != "skipped":
                    print(f"  - {c.name}: {c.why}")
        print("\nFix it, or move the baseline in audit_all.py IN THE SAME COMMIT "
              "and say why.")
        return 1
    print("all validators at or better than baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
