"""Replace the class-level names in the curated spans with the registry's genera.

    ../venv/bin/python upgrade_curated.py            # report only
    ../venv/bin/python upgrade_curated.py --apply    # rewrite life_data.json

The curated record (`build/life_data.json`, `region_taxa`) was written before
the registry had genera for most seas, so many of its spans say "Ammonoidea",
"Fusulinida", "Foraminifera" -- names that are true of every sea there has ever
been. A curated name has authority over place on its card and keeps its slot,
so a class-level curated name is a class-level card. Where the registry now
holds two or more genera of that group, alive across the span and at home on
the label (the same at_home / in_reach / latitude / habitat rules the composer
applies to everything else -- curated names skip them, so they are applied
here), the class-level entry is replaced by up to three of them. Where it
holds one, the genus is added beside the name; where none, the name stays,
because it is what there is. Spans marked `exception` are left alone.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import biota                                                 # noqa: E402
import features                                              # noqa: E402

LIFE = os.path.join(BUILD, "life_data.json")
LABELS = os.path.join(BUILD, "..", "web", "labels.json")

GENERIC = {"class", "subclass", "order", "suborder", "phylum", "kingdom", "domain",
           "clade", "superorder", "superfamily", "infraorder", "division", "subphylum"}

#: curated name -> tokens that a registry entry's classification or form may carry
GROUPS = {
    "Ammonoidea": {"Ammonoidea", "Goniatitida", "Ceratitida", "Ammonitida", "Prolecanitida",
                   "Agoniatitida", "Anarcestida", "Clymeniida", "Phylloceratida",
                   "Lytoceratida", "Ancyloceratida", "form:ammonite", "form:heteromorph"},
    "Goniatitida": {"Goniatitida"}, "Ceratitida": {"Ceratitida"},
    "Foraminifera": {"Foraminifera", "Fusulinida", "Globigerinida", "Globigerinina",
                     "Rotaliida", "Miliolida", "Textulariida", "Nummulitidae",
                     "form:foram", "form:largeforam"},
    "Fusulinida": {"Fusulinida", "Fusulinidae", "Schwagerinidae", "Verbeekinidae",
                   "Neoschwagerinidae", "Fusulinata"},
    "Globigerinina": {"Globigerinida", "Globigerinina", "Globigerinidae", "Globorotaliidae"},
    "Belemnitida": {"Belemnitida", "form:belemnite"},
    "Conodonta": {"Conodonta", "form:conodont"},
    "Cyanobacteria": {"Cyanophyceae", "Cyanobacteria", "Oscillatoriales", "Chroococcales",
                      "Nostocales", "form:cyano"},
    "Radiolaria": {"Radiolaria", "Radiozoa", "Polycystina", "form:radiolarian"},
    "Graptolithina": {"Graptolithina", "Graptoloidea", "Dendroidea", "form:graptolite"},
    "Brachiopoda": {"Brachiopoda", "Rhynchonellata", "Strophomenata", "Lingulata",
                    "form:brachiopod", "form:lingulid"},
    "Productida": {"Productida", "Productidae", "Productoidea", "Productellidae",
                   "Linoproductidae", "Marginiferidae"},
    "Scleractinia": {"Scleractinia", "form:coral"},
    "Ichthyosauria": {"Ichthyosauria", "form:ichthyosaur"},
    "Rudistes": {"Hippuritida", "Rudistes", "form:rudist"},
    "Bivalvia": {"Bivalvia", "form:bivalve", "form:clam", "form:mussel", "form:oyster",
                 "form:giantclam", "form:rudist"},
    "Acritarcha": {"Acritarcha", "form:acritarch"},
    "Stromatoporoidea": {"Stromatoporoidea", "form:stromatoporoid"},
    "Crinoidea": {"Crinoidea"},
    "Bacillariophyta": {"Bacillariophyceae", "Bacillariophyta", "Diatomea", "form:diatom"},
    "Diatomea": {"Bacillariophyceae", "Bacillariophyta", "Diatomea", "form:diatom"},
    "Selachii": {"Chondrichthyes", "Elasmobranchii", "Selachii", "form:shark", "form:ray"},
    "Chondrichthyes": {"Chondrichthyes", "Elasmobranchii", "Holocephali", "form:shark",
                       "form:ray"},
    "Osteostraci": {"Osteostraci"},
    "Placodermi": {"Placodermi", "form:placoderm", "form:antiarch"},
    "Notoungulata": {"Notoungulata", "form:notoungulate"},
    "Tabulata": {"Tabulata", "form:tabulate"}, "Rugosa": {"Rugosa", "form:horncoral"},
    "Plesiosauria": {"Plesiosauria", "form:plesiosaur", "form:pliosaur"},
    "Mysticeti": {"Mysticeti"}, "Cetacea": {"Cetacea", "form:whale", "form:dolphin"},
    "Archaeoceti": {"Archaeoceti", "form:archaeocete"},
    "Sirenia": {"Sirenia", "form:sirenian"},
    "Actinopterygii": {"Actinopterygii", "form:fish", "form:bigfish", "form:reeffish",
                       "form:cod", "form:eel", "form:flatfish"},
    "Bryozoa": {"Bryozoa", "Stenolaemata", "Trepostomata", "Fenestrata", "Cryptostomata",
                "form:bryozoan"},
    "Fenestrata": {"Fenestrata", "Fenestellidae"},
    "Trigonotarbida": {"Trigonotarbida"},
    "Gorgonopsia": {"Gorgonopsia", "form:gorgonopsian"},
    "Pareiasauria": {"Pareiasauria", "Pareiasauridae", "form:pareiasaur"},
    "Phytosauria": {"Phytosauria", "Phytosauridae"},
    "Aetosauria": {"Aetosauria", "Stagonolepididae"},
    "Sparassodonta": {"Sparassodonta", "form:sparassodont"},
    "Litopterna": {"Litopterna", "form:litoptern"},
    "Ginkgoales": {"Ginkgoales", "form:ginkgo"},
    "Calpionellida": {"Calpionellida"},
    "Rhodophyta": {"Rhodophyta", "Florideophyceae", "Bangiophyceae", "Corallinales",
                   "Solenoporaceae"},
    "Coccolithophyceae": {"Prymnesiophyceae", "Coccolithophyceae", "form:coccolith"},
    "Euphausiacea": {"Euphausiacea"}, "Notothenioidei": {"Notothenioidei", "Nototheniidae"},
    "Placodontia": {"Placodontia", "form:placodont"},
    "Rangeomorpha": {"Rangeomorpha"},
    "Procellariiformes": {"Procellariiformes"},
    "Bryophyta": {"Bryophyta", "Bryopsida", "form:moss"},
    "Polypodiopsida": {"Polypodiopsida", "Polypodiales", "Osmundales", "Cyatheales",
                       "form:fern", "form:treefern"},
    "Dinoflagellata": {"Dinoflagellata", "Dinophyceae", "form:dinoflagellate"},
    "Crocodylia": {"Crocodylia", "Crocodylidae", "Alligatoridae", "Gavialidae",
                   "form:crocodile", "form:gharial"},
}


#: (label, curated name) pairs left alone: the registry's genera would be a
#: worse answer than the class-level note. Each with its reason.
KEEP = {
    ("Arctic Ocean", "Bivalvia"): "the registry's Cenozoic bivalves are temperate; the note says hardy Arctic shelf communities",
}


#: forms that a group's tokens reach but a reader would not call by the name
EXCLUDE_FORMS = {"Brachiopoda": {"sclerite"}, "Conodonta": set()}


def tokens(e):
    out = {"form:" + e.get("form", "")}
    for v in (e.get("cls") or {}).values():
        if v:
            out.add(v)
    p = e.get("pbdb") or {}
    for k in ("phylum", "class", "order", "family"):
        if p.get(k):
            out.add(p[k])
    return out


def labels_by_name():
    with open(LABELS) as f:
        labs = json.load(f)
    by = {}
    for lab in labs:
        by.setdefault(lab["n"], []).append(lab)
    return by


def label_for(cands, age):
    for lab in cands:
        lo, hi = min(lab["a0"], lab["a1"]), max(lab["a0"], lab["a1"])
        if lo - 1 <= age <= hi + 1:
            return lab
    return cands[0]


def candidates(reg, name, curated_realm, lab, a0, a1, taken):
    want = GROUPS.get(name)
    if not want:
        return []
    span = max(1.0, a1 - a0)
    ages = [a0 + 0.1 * span, (a0 + a1) / 2.0, a1 - 0.1 * span]
    marine = biota.is_marine(lab, ages[1])
    out = []
    for n, e in reg.items():
        if n in taken or e.get("assemblage") or e.get("rank") not in ("genus", "species", "subspecies"):
            continue
        realms = set(e.get("realms") or [e["realm"]])
        if curated_realm not in realms:
            continue
        if not (tokens(e) & want) or e.get("form") in EXCLUDE_FORMS.get(name, ()):
            continue
        ov = min(e["fad"], a1) - max(e["lad"], a0)
        if ov < 0.4 * span and ov < 0.9 * max(1.0, e["fad"] - e["lad"]):
            continue
        # the place rules are asked only at ages the taxon is alive: a slice
        # that has not begun is not "away", it is absent
        lo, hi = max(a0, e["lad"]), min(a1, e["fad"])
        live = [a for a in ages if lo <= a <= hi] or [(lo + hi) / 2.0]
        ok = True
        for a in live:
            home = biota.label_home(lab, features, a)
            plat = biota.lat_at(lab, a)
            habs = biota.label_habitats(lab, a, plat)
            if home is None or not biota.at_home(e, home, a, sea_card=marine):
                ok = False
                break
            if not biota.in_reach(e, lab, a) or not biota.lat_ok(e, plat, a):
                ok = False
                break
            if not biota.hab_ok(e, habs, biota.is_polar(lab, a, plat)):
                ok = False
                break
        if not ok:
            continue
        b = biota.breadth(e, ages[1]) or 99
        out.append((b, -ov, n))
    out.sort()
    return [n for _b, _o, n in out]


def main(argv):
    apply = "--apply" in argv
    reg = biota.load()["taxa"]
    labs = labels_by_name()
    with open(LIFE) as f:
        life = json.load(f)
    R = life["region_taxa"]
    replaced = added = kept = 0
    for name, spans in R.items():
        if name not in labs:
            continue
        for sp in spans:
            if sp.get("exception"):
                continue
            a0, a1 = min(sp["a0"], sp["a1"]), max(sp["a0"], sp["a1"])
            lab = label_for(labs[name], (a0 + a1) / 2.0)
            taken = {t[0] for t in sp["taxa"]}
            new = []
            for t in sp["taxa"]:
                tname, rank, realm = t[0], t[1], t[2]
                if rank not in GENERIC or tname not in GROUPS or (name, tname) in KEEP:
                    new.append(t)
                    continue
                found = candidates(reg, tname, realm, lab, a0, a1, taken)[:3]
                if len(found) >= 2:
                    print(f"  {name} {a0}-{a1}: {tname} -> {', '.join(found)}")
                    replaced += 1
                elif len(found) == 1:
                    print(f"  {name} {a0}-{a1}: {tname} + {found[0]}")
                    new.append(t)
                    added += 1
                else:
                    kept += 1
                    new.append(t)
                for i, g in enumerate(found):
                    e = reg[g]
                    # the curated prose is about the PLACE ("rudists built the
                    # Golden Lane banks round the young Gulf"): it goes with the
                    # first genus that replaces the name, as its label-local note
                    note = t[3] if (i == 0 and len(found) >= 2 and t[3]) else e.get("note", "")
                    # a genus of two realms is written in the realm the span
                    # asked for: a fish of rivers and shelves is "sea" on a sea
                    new.append([g, e.get("rank", "genus"), realm, note])
                    taken.add(g)
            sp["taxa"] = new
    print(f"{replaced} class-level names replaced, {added} kept with one genus beside them, "
          f"{kept} kept as they were")
    if apply:
        with open(LIFE, "w") as f:
            json.dump(life, f, indent=1, ensure_ascii=False)
        print("life_data.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
