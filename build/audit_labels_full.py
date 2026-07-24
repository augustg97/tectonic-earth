"""Systematic audit of EVERY label: date span, first-appearance placement, and
whether it keeps tracking the same feature across its whole lifespan.

Three independent checks, run at every 5-Myr step inside each label's own window,
against the shipped elevation field (the same data the app draws):

  TERRAIN   does the drawn position sit on the kind of ground the label names?
            A sea or ocean must be in water; everything else must be on land.
            Reported as the fraction of its lifespan spent on the wrong medium.
  DEBUT     is it correctly placed at the age it FIRST appears? A label that
            settles later but debuts in the wrong ocean still reads as a bug.
  DRIFT     the largest single-step jump in drawn position. A feature that
            hops hundreds of km between neighbouring keyframes is not tracking
            one feature; it is being re-snapped to a different one.

Run:  ../venv/bin/python audit_labels_full.py [--csv]
"""
import json, math, os, sys

from audit_labels import elev_at, track_pos, SEA_TYPES, WEB


def great_circle(a, b):
    (lo1, la1), (lo2, la2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians((lo2 - lo1 + 180.0) % 360.0 - 180.0)
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return math.degrees(2 * math.asin(min(1.0, math.sqrt(x))))


# Types whose position the elevation field cannot judge: a lake sits in its own
# field, an ice sheet floats over either medium, and a "region" may name either.
SKIP_TYPES = {"lake", "ice", "region", "sea_ice"}

# Submarine by definition -- a drowned plateau or microcontinent SHOULD read as
# water, so the land test would flag every one of them as broken.
SUBMARINE = set()
try:
    import build_webdata as _bw
    SUBMARINE = set(getattr(_bw, "PLATEAU_LABEL", {}).keys())
except Exception:
    pass


def audit(tracked_only=True):
    labels = json.load(open(os.path.join(WEB, "labels.json")))
    if isinstance(labels, dict):
        labels = labels.get("labels", [])
    rows = []
    for l in labels:
        if l.get("t") in SKIP_TYPES or l.get("n") in SUBMARINE:
            continue
        # An UNtracked label is repositioned by the app's snapLabel terrain
        # search before it is drawn, so its stored coordinate is not what the
        # reader sees and testing it here means nothing. Only tracked labels are
        # drawn where this audit looks.
        if tracked_only and not l.get("tr"):
            continue
        a0, a1 = float(l.get("a0", 0)), float(l.get("a1", 0))
        lo, hi = min(a0, a1), max(a0, a1)
        t = l.get("t", "")
        want_sea = t in SEA_TYPES
        tr = l.get("tr")
        step = 5.0
        ages = [lo + i * step for i in range(int((hi - lo) / step) + 1)] or [lo]
        bad = tested = 0
        prev = None
        maxjump = 0.0
        jump_at = None
        debut_ok = None
        for a in ages:
            plon, plat = track_pos(tr, l.get("lon", 0), l.get("lat", 0), a)
            # Judge a small neighbourhood, not a single cell. The app's snapLabel
            # already nudges a tracked label onto matching ground within a few
            # degrees, and a narrow coastal range (the Andes, the Apennines) is
            # only ever a cell or two from water -- scoring that as "in the
            # ocean" buries the real failures under false alarms.
            zs = [elev_at(a, plon + dx, plat + dy)
                  for dx, dy in ((0, 0), (1.5, 0), (-1.5, 0), (0, 1.5), (0, -1.5))]
            zs = [z for z in zs if z is not None]
            if zs:
                tested += 1
                wrong = all((z >= 0) if want_sea else (z < 0) for z in zs)
                if wrong:
                    bad += 1
                # the debut is the OLDEST age in the window (labels run old->young)
                if debut_ok is None:
                    debut_ok = not wrong
            if prev is not None:
                d = great_circle(prev, (plon, plat))
                if d > maxjump:
                    maxjump, jump_at = d, a
            prev = (plon, plat)
        if not tested:
            continue
        rows.append({
            "n": l.get("n"), "t": t, "lo": lo, "hi": hi,
            "tracked": bool(tr), "wrong": bad / tested, "tested": tested,
            "debut_ok": debut_ok, "maxjump": maxjump, "jump_at": jump_at,
        })
    return rows


def main():
    rows = audit()
    # severity: wrong-medium dominates, then a bad debut, then drift
    def sev(r):
        return (r["wrong"] * 100 + (0 if r["debut_ok"] else 25)
                + min(r["maxjump"], 60) * 0.4)
    rows.sort(key=sev, reverse=True)

    if "--csv" in sys.argv:
        print("name,type,from,to,tracked,wrong_frac,debut_ok,max_jump_deg")
        for r in rows:
            print("%s,%s,%g,%g,%s,%.2f,%s,%.1f" % (
                r["n"], r["t"], r["hi"], r["lo"], r["tracked"],
                r["wrong"], r["debut_ok"], r["maxjump"]))
        return

    n_bad = sum(1 for r in rows if r["wrong"] > 0.34)
    n_debut = sum(1 for r in rows if not r["debut_ok"])
    n_jump = sum(1 for r in rows if r["maxjump"] > 25)
    print("labels audited: %d" % len(rows))
    print("  wrong medium for >1/3 of lifespan : %d" % n_bad)
    print("  mis-placed at first appearance    : %d" % n_debut)
    print("  jumps >25 deg between keyframes   : %d" % n_jump)
    print()
    print("%-38s %-10s %11s %6s %6s %7s %s" %
          ("LABEL", "TYPE", "WINDOW(Ma)", "WRONG", "DEBUT", "JUMP", "TRACKED"))
    for r in rows[:34]:
        if sev(r) < 12:
            break
        print("%-38s %-10s %5g-%-5g %5.0f%% %6s %6.0f %s" % (
            r["n"][:38], r["t"], r["hi"], r["lo"], r["wrong"] * 100,
            "ok" if r["debut_ok"] else "BAD", r["maxjump"],
            "yes" if r["tracked"] else "no"))


if __name__ == "__main__":
    main()
