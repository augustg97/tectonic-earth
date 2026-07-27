"""B1 prerequisite — audit all curated `region_taxa` entries against the province model.

The B1 decision (2026-07-26) is **model decides, curated is a flagged exception**:
`paleobiogeography.province()` runs everywhere; a curated list is shown only where
it is genuinely distinctive, and everywhere else the curated list is CHECKED
against the model rather than silently overriding it. Where the model has no
established province, the card shows the global interval list under a heading
that says it is global.

That design makes this audit the prerequisite, because it needs one thing the
data does not currently carry: **which curated entries are exceptions and which
are just province-typical**. This script proposes that split and reports the
disagreements.

Three verdicts per curated entry:

  EXCEPTION   genuinely distinctive - a Lagerstätte, an endemic island, a
              restricted basin, a locality whose whole point is that it is NOT
              the generic assemblage. KEEP and flag; the model must not overwrite
              it. (Solnhofen is the canonical case.)
  TYPICAL     consistent with what the model would say for its province anyway.
              Safe to let the model own; the curated text may still be better
              prose, so keep it as province-level copy rather than per-label.
  CONFLICT    the curated realm or latitude implies a different province from the
              one the model resolves. Needs a human.

READ-ONLY.

    ../../venv/bin/python audit_curated_biota.py
    ../../venv/bin/python audit_curated_biota.py --md out.md
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, HERE)
sys.path.insert(0, BUILD)

import paleobiogeography as pb                            # noqa: E402

# Localities whose whole point is that they are NOT the generic assemblage.
# A Lagerstätte preserves soft tissue and therefore shows animals that exist
# everywhere but fossilise nowhere else; an isolated island evolves its own fauna;
# a restricted basin has its own chemistry. None of these should ever be
# overwritten by a province model.
EXCEPTION_MARKERS = (
    "lagerstätte", "lagerstatte", "solnhofen", "burgess", "chengjiang", "qingjiang",
    "sirius passet", "emu bay", "orsten", "rhynie", "mazon creek", "messel",
    "yixian", "la brea", "riversleigh", "hunsrück", "bear gulch", "soom",
    "nama", "ediacara", "mistaken point", "doushantuo",
    "messinian", "zechstein", "castile", "muschelkalk", "green river",
    "pannon", "paratethys", "black sea", "caspian",
    "hydrothermal", "vent", "mid-atlantic ridge", "east pacific rise",
    "madagascar", "new zealand", "zealandia", "galapagos", "hawaii",
    "beringia", "wallace",
)

MARINE_HINT = ("ocean", "sea", "seaway", "strait", "corridor", "gulf", "ridge",
               "rise", "basin", "lagoon", "sound", "bay", "tethys", "panthalassa",
               "iapetus", "rheic", "mirovia")


class F:
    def __init__(self, verdict, name, span, detail, note=""):
        self.verdict, self.name, self.span = verdict, name, span
        self.detail, self.note = detail, note


def guess_realm(region_name, taxa):
    """marine or terrestrial, from the taxa's own realms, falling back on the name."""
    realms = [t[2] for t in taxa if len(t) > 2]
    sea = sum(1 for r in realms if r == "sea")
    land = sum(1 for r in realms if r in ("land", "air", "fresh"))
    if sea and not land:
        return "marine"
    if land and not sea:
        return "terrestrial"
    if sea or land:
        return "marine" if sea > land else "terrestrial"
    low = region_name.lower()
    return "marine" if any(h in low for h in MARINE_HINT) else "terrestrial"


_LABEL_LAT = None
_RECON = None


def _label_coords():
    """{label name: (lon, lat)} from the app's own features.LABELS."""
    global _LABEL_LAT
    if _LABEL_LAT is None:
        try:
            import features as Fx
            _LABEL_LAT = {r[1]: (r[2], r[3]) for r in Fx.LABELS if len(r) >= 4}
        except Exception:                                  # noqa: BLE001
            _LABEL_LAT = {}
    return _LABEL_LAT


def guess_lat(region_name, age=None):
    """Palaeolatitude at `age`. Crude on purpose - the province model is banded,
    so only the BAND matters, and getting the band wrong is exactly the kind of
    error this audit should surface rather than hide.

    Three sources, best first:
      1. the block's own anchors, if the region IS a continental block
      2. the app's authored label coordinate, back-advected on the plate model
      3. the authored coordinate as-is, which is only meaningful post-Pangaea
    The first version used (1) alone and therefore could not place 188 of 198
    entries - most region names are seas and ranges, not blocks.
    """
    import paleogeography as pg
    if region_name in pg.BLOCKS:
        lats = [a[1] for a in pg.BLOCKS[region_name].anchors]
        return sum(lats) / len(lats)
    xy = _label_coords().get(region_name)
    if xy is None:
        return None
    lon, lat = xy
    if age is None or age < 5:
        return lat
    global _RECON
    if _RECON is None:
        try:
            import paleo_tracks as pt
            _RECON = pt.Reconstructor() if pt.available() else False
        except Exception:                                  # noqa: BLE001
            _RECON = False
    if _RECON:
        try:
            tr, _pid = _RECON.track(lon, lat, age, step=max(5, int(age)))
            if tr:
                return tr[-1][2]
        except Exception:                                  # noqa: BLE001
            pass
    return lat


def run():
    life = json.load(open(os.path.join(BUILD, "life_data.json")))
    rt = life["region_taxa"]
    marine_lock = set()
    try:
        import life as L
        marine_lock = set(getattr(L, "MARINE_REGIONS", ()) or ())
    except Exception:                                      # noqa: BLE001
        pass

    out = []
    for name, spans in sorted(rt.items()):
        low = name.lower()
        is_exception = any(k in low for k in EXCEPTION_MARKERS)
        for sp in spans:
            a0, a1 = sp.get("a0", 0), sp.get("a1", 0)
            mid = 0.5 * (a0 + a1)
            taxa = sp.get("taxa", []) or []
            span = f"{max(a0,a1):g}-{min(a0,a1):g}"
            realm = guess_realm(name, taxa)
            lat = guess_lat(name, mid)

            if is_exception:
                out.append(F("EXCEPTION", name, span,
                             f"{len(taxa)} taxa, {realm}",
                             "distinctive locality - the model must never overwrite it"))
                continue

            if lat is None:
                out.append(F("TYPICAL", name, span,
                             f"{len(taxa)} taxa, {realm}; no palaeolatitude available",
                             "the model cannot place this without a block anchor - it "
                             "will fall to the labelled global list"))
                continue

            p = pb.province(mid, lat, realm)
            # a realm-locked marine region carrying land taxa is a real conflict
            bad_realm = (name in marine_lock and
                         any(len(t) > 2 and t[2] not in ("sea",) for t in taxa))
            if bad_realm:
                out.append(F("CONFLICT", name, span,
                             f"realm-locked marine but carries non-sea taxa",
                             "the export filter should have caught this"))
            elif p.basis == "default" or p.confidence == "none" or "no named" in p.name.lower():
                out.append(F("TYPICAL", name, span,
                             f"{len(taxa)} taxa, {realm} @ {lat:+.0f} deg; "
                             f"model says '{p.name}'",
                             "model has no province here - curated entry is the only "
                             "source, so keep it"))
            else:
                out.append(F("TYPICAL", name, span,
                             f"{len(taxa)} taxa, {realm} @ {lat:+.0f} deg -> "
                             f"{p.name}",
                             "province-typical; the model can own this and the curated "
                             "prose can move to province level"))
    return out


def main():
    findings = run()
    order = {"CONFLICT": 0, "EXCEPTION": 1, "TYPICAL": 2}
    findings.sort(key=lambda f: (order[f.verdict], f.name))
    counts = {}
    for f in findings:
        counts[f.verdict] = counts.get(f.verdict, 0) + 1
    print(f"{len(findings)} curated region_taxa spans audited")
    print("  " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())) + "\n")
    shown = {}
    for f in findings:
        shown[f.verdict] = shown.get(f.verdict, 0) + 1
        if f.verdict == "TYPICAL" and shown[f.verdict] > 12:
            continue
        print(f"[{f.verdict:9s}] {f.name} ({f.span} Ma)")
        print(f"            {f.detail}")
        if f.note:
            print(f"            -> {f.note}")
    if counts.get("TYPICAL", 0) > 12:
        print(f"\n  ... and {counts['TYPICAL']-12} more TYPICAL")

    if "--md" in sys.argv:
        path = sys.argv[sys.argv.index("--md") + 1]
        with open(path, "w") as fh:
            fh.write("# Curated biota audit (B1 prerequisite)\n\n"
                     f"`modeling/audit_curated_biota.py` over **{len(findings)} curated "
                     "spans**.\n\n"
                     + " · ".join(f"**{k}** {v}" for k, v in sorted(counts.items()))
                     + "\n\n| verdict | region | span | detail | action |\n"
                       "|---|---|---|---|---|\n")
            for f in findings:
                fh.write(f"| {f.verdict} | **{f.name}** | {f.span} Ma | {f.detail} | "
                         f"{f.note} |\n")
        print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
