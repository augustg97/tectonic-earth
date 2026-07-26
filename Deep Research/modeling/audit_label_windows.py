"""A2 — does every crustal label draw only when the thing it names existed?

READ-ONLY. `features.LABELS` rows are `(type, name, lon, lat, a0, a1)` and the
window is authored by hand. Nothing in the pipeline checks it against the history
of the entity named, so a label can be drawn at an age when its continent had not
assembled or had already dispersed. That is a class of error the build cannot
currently see, and it is invisible on screen because a wrongly-timed label still
lands on *some* terrain.

This audits the window against `paleogeography.py`:

  EXISTS      the block's own life span (`Block.first` .. `Block.last`)
  ASSEMBLY    an assembly label (Gondwana, Pangaea, Rodinia, Laurussia, ...) must
              not draw outside that assembly's window
  RIFT        a terrane label should not draw before the terrane rifted from its
              parent if the name only means something afterwards
  ANCHOR      a label the build will back-advect must be authored at PRESENT-DAY
              coordinates on land TODAY - the rule the build's
              coord_is_present_day() applies, and the one 18 terranes broke

    ../../venv/bin/python audit_label_windows.py
    ../../venv/bin/python audit_label_windows.py --md out.md
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, HERE)
sys.path.insert(0, BUILD)

import paleogeography as pg                               # noqa: E402

# features.LABELS names -> paleogeography block names, where they differ.
ALIAS = {
    "Laurussia (Euramerica)": "Laurussia", "Euramerica": "Laurussia",
    "Sino-Korea": "North China", "Yangtze": "South China",
    "Kaapvaal Craton": "Kalahari Craton", "Zimbabwe Craton": "Kalahari Craton",
    "Sao Francisco Craton": "Sao Francisco", "Rio de la Plata Craton": "Rio de la Plata",
    "West Africa": "West African Craton", "Congo": "Congo Craton",
    "Kalahari": "Kalahari Craton", "Amazonia Craton": "Amazonia",
    "Precordillera": "Cuyania / Precordillera", "Cuyania": "Cuyania / Precordillera",
    "Malvinas": "Falkland / Malvinas", "Falklands": "Falkland / Malvinas",
    "Apulia": "Adria / Apulia", "Adria": "Adria / Apulia",
    "Timanide Belt": "Timan-Pechora", "Timania": "Timan-Pechora",
    "Shan-Thai": "Sibumasu", "Mongolia": "Amuria / Mongolia",
    "Amuria": "Amuria / Mongolia", "East Antarctic Craton": "East Antarctica",
}
SLACK = 30.0     # Ma. A label may reasonably lead or trail its entity a little.


class F:
    def __init__(self, check, sev, name, detail, fix=""):
        self.check, self.sev, self.name, self.detail, self.fix = check, sev, name, detail, fix


def resolve(name):
    n = ALIAS.get(name, name)
    if n in pg.BLOCKS:
        return n, "block"
    if n in pg.ASSEMBLIES:
        return n, "assembly"
    # try a loose match on the block list
    low = n.lower()
    for b in pg.BLOCKS:
        if b.lower() == low or low.startswith(b.lower()) or b.lower().startswith(low):
            return b, "block"
    return None, None


def run():
    import features as Fx
    out, checked = [], 0
    present = None
    try:
        import build_webdata as BW
        present = getattr(BW, "_present_elevation", None)
    except Exception:                                      # noqa: BLE001
        pass

    CRUSTAL = {"continent", "craton", "terrane", "orogen", "region"}
    for row in Fx.LABELS:
        if len(row) < 6:
            continue
        typ, name, lon, lat, a0, a1 = row[0], row[1], row[2], row[3], row[4], row[5]
        base, top = max(a0, a1), min(a0, a1)
        key, kind = resolve(name)
        if key is None:
            continue
        checked += 1

        if kind == "block":
            b = pg.BLOCKS[key]
            if base > b.first + SLACK:
                out.append(F("EXISTS", "MED" if base - b.first < 200 else "HIGH", name,
                             f"drawn back to {base:g} Ma but {key} is only identifiable "
                             f"from ~{b.first:g} Ma ({base-b.first:.0f} Myr too early)",
                             f"set a0 no older than {b.first:g}"))
            if top < b.last - SLACK:
                out.append(F("EXISTS", "MED", name,
                             f"drawn to {top:g} Ma but {key} ends at {b.last:g} Ma", ""))
            # a terrane's name usually means something only after it rifted
            rifts = [e for e in pg.rift_events(key)]
            if rifts and b.kind == "terrane":
                oldest_rift = max(r[1] for r in rifts)
                if base > oldest_rift + 120:
                    out.append(F("RIFT", "LOW", name,
                                 f"drawn back to {base:g} Ma; {key} rifts from its parent "
                                 f"at ~{oldest_rift:g} Ma, so the name is anachronistic "
                                 f"before that", ""))
        else:
            a = pg.ASSEMBLIES[key]
            # "Gondwana (assembling)" is a legitimate name before assembly completes.
            assembling = "assembl" in name.lower()
            if base > a["base"] + SLACK and not assembling:
                out.append(F("ASSEMBLY", "MED", name,
                             f"drawn back to {base:g} Ma but {key} only assembles by "
                             f"{a['base']:g} Ma", f"set a0 to {a['base']:g}"))
            # Compare against when the mass stops being RECOGNISABLE, not when
            # rifting starts - Pangaea rifts from ~175 Ma and is still one
            # continent for another 75 Myr.
            gone = pg.recognisable_until(key)
            if top < gone - SLACK:
                out.append(F("ASSEMBLY", "MED", name,
                             f"drawn to {top:g} Ma but {key} is no longer recognisable "
                             f"after ~{gone:g} Ma", f"set a1 to {gone:g}"))

        # anchor check: will the build track this label, and is the coord valid?
        if typ in CRUSTAL and present is not None and base < 540:
            try:
                z = present(lon, lat)
                if z is not None and z < 0:
                    out.append(F("ANCHOR", "MED", name,
                                 f"authored at ({lon:g}, {lat:g}), which is under water "
                                 f"today ({z:.0f} m), so the build cannot back-advect it "
                                 f"and it falls to snapLabel's wide terrain search",
                                 "re-anchor on the ground the entity BECAME"))
            except Exception:                              # noqa: BLE001
                pass
    return checked, out


def main():
    checked, findings = run()
    order = {"HIGH": 0, "MED": 1, "LOW": 2}
    findings.sort(key=lambda f: (order.get(f.sev, 9), f.check, f.name))
    print(f"{checked} labels matched to a known block or assembly; "
          f"{len(findings)} findings\n")
    for f in findings:
        print(f"[{f.sev:4s}] {f.check:9s} {f.name}")
        print(f"         {f.detail}")
        if f.fix:
            print(f"         -> {f.fix}")
    if not findings:
        print("every matched label draws only while the entity it names existed.")
    if "--md" in sys.argv:
        path = sys.argv[sys.argv.index("--md") + 1]
        with open(path, "w") as fh:
            fh.write("# Label window audit\n\n"
                     f"`modeling/audit_label_windows.py` over **{checked} matched "
                     f"labels** — {len(findings)} findings.\n\n"
                     "| sev | check | label | finding | fix |\n|---|---|---|---|---|\n")
            for f in findings:
                fh.write(f"| {f.sev} | {f.check} | **{f.name}** | {f.detail} | "
                         f"{f.fix} |\n")
        print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
