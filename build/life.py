"""Biomes, life through time, and the regional fossil record.

The app showed tectonics and climate and said nothing about what was living in
any of it, which for most of this timeline is the more interesting half. Three
layers land here:

  BIOMES    - what kinds of environment existed at a given age, in rough order
              of global extent, using terms that are not anachronistic. Before
              land plants the terrestrial "biomes" are microbial crust and bare
              regolith; grassland does not appear until the Cenozoic.
  LIFE      - per geological interval: a summary, a handful of representative
              taxa at whatever rank is actually informative for that time, and
              what first appeared or died out.
  REGIONAL  - what the fossil record of a particular landmass shows at a
              particular time, so clicking Gondwana in the Permian tells you
              about Glossopteris and Mesosaurus rather than repeating the
              global summary.

Bulk content lives in life_data.json; this module holds the illustration set
and the logic that binds a taxon name to a drawing.
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "life_data.json")) as _f:
    _DATA = json.load(_f)
with open(os.path.join(_HERE, "life_icons.json")) as _f:
    ICONS = json.load(_f)
# Attribution and licence for every traced silhouette. PhyloPic images are
# individually licensed and the CC-BY ones REQUIRE credit, so this ships to the
# app and is rendered in the About panel. Absent for hand-drawn icons.
_CREDITS_PATH = os.path.join(_HERE, "life_credits.json")
CREDITS = {}
if os.path.exists(_CREDITS_PATH):
    with open(_CREDITS_PATH) as _f:
        CREDITS = json.load(_f)


# WHICH DRAWING STANDS FOR WHICH TAXON.
#
# Until 2026-09 this was an ordered table of three hundred lowercase substrings
# matched against the taxon's NAME, with a per-realm fallback -- land: a monitor
# lizard, sea: a palaeoniscid fish -- for anything that matched nothing. Both
# halves failed structurally, and twice. A name is not a classification, so the
# table was only ever as complete as the last author's memory of the data: every
# batch of new names (province markers, present-day regional biota) arrived with
# no rules, and 124 of them drew the lizard, Acacia and Bison and Picea alike,
# while kelp, krill and reef corals drew the fish. And where a rule did match,
# the drawing was too coarse to be right: "carnivore" was a coyote, so Ursus was
# a coyote; "mammal" was an opossum, so Megatherium and the litopterns were too.
# A fallback that always succeeds makes every omission invisible.
#
# The table and the fallback are GONE, not deprecated. Every organism declares
# its body FORM in the registry (build/taxa/*.json), every form declares its one
# drawing (biota_forms.py), the classification cross-checks the form
# (biota.check_form), and a name that is not registered has NO drawing -- which
# build_life() refuses to ship and audit_biota.py reports.
def taxon_key(name):
    """The per-taxon icon key, if this taxon has a silhouette of its own."""
    return "t:" + re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


def icon_for(name, realm=None):
    """The illustration key for a taxon name, from the registry. '' if none.

    `realm` is accepted and ignored: it is what the old fallback keyed on.
    """
    import biota                                           # noqa: PLC0415
    ic, _how = biota.icon_for(name, ICONS)
    return ic or ""


def _section(name):
    """'fauna' | 'flora' | 'other' from the registry, so an interval card can
    list its animals and its plants under their own headings."""
    try:
        import biota                                       # noqa: PLC0415
        e = biota.get(name)
        return biota._section(e) if e else ""
    except Exception:                                      # noqa: BLE001
        return ""


def credits():
    """Only the credits actually referenced by an icon in the build."""
    return CREDITS


def biomes():
    return _DATA["biomes"]


def life():
    """Per-interval life, with an illustration bound to every taxon."""
    out = []
    for e in _DATA["life"]:
        taxa = []
        for t in e["taxa"]:
            win = None
            if isinstance(t, (list, tuple)):
                if len(t) >= 5:
                    name, rank, realm, note, win = t[0], t[1], t[2], t[3], t[4]
                else:
                    name, rank, realm, note = t
            else:
                name, rank, realm, note = (t["name"], t["rank"], t["realm"], t["note"])
                win = t.get("win")
            rec = {"n": name, "r": rank, "realm": realm, "note": note,
                   "ic": icon_for(name, realm), "k": _section(name)}
            # Optional per-taxon age window [appear, disappear], TIGHTER than the
            # interval -- so Homo sapiens can sit inside the 2.58-Myr Quaternary
            # but only show for its real last 0.3 Myr, and only where the record
            # puts it. The app hides the taxon outside this.
            if win:
                rec["w"] = [max(win), min(win)]
            taxa.append(rec)
        out.append({"interval": e["interval"], "a0": e["a0"], "a1": e["a1"],
                    "summary": e["summary"], "taxa": taxa,
                    "first": e.get("first_appearances", []),
                    "ext": e.get("extinctions", [])})
    return out


def regional():
    return _DATA.get("regional", {})


def region_taxa():
    """Per-place, per-interval characteristic biota, with icons bound.

    Clicking any two features at the same age used to show the same four
    organisms, because there was only ever one global list. This is what makes
    Permian Gondwana show Glossopteris and Mesosaurus while Permian Siberia
    does not. Realm is enforced on the way out: a marine region may only carry
    marine taxa, which is the defect this exists to fix.
    """
    out = {}
    for region, spans in _DATA.get("region_taxa", {}).items():
        marine = region in MARINE_REGIONS
        rows = []
        for s in spans:
            taxa = []
            for t in s.get("taxa", []):
                name, rank, realm, note = (
                    t if isinstance(t, (list, tuple))
                    else (t["name"], t["rank"], t["realm"], t["note"]))
                if marine and realm != "sea":
                    print(f"  WARNING dropped {realm} taxon {name!r} "
                          f"from marine region {region!r}")
                    continue
                taxa.append({"n": name, "r": rank, "realm": realm,
                             "note": note, "ic": icon_for(name, realm)})
            if taxa:
                # `exception` says this locality is atypical FOR ITS PROVINCE and
                # the province model must never speak over it -- Solnhofen, the
                # Zechstein, the Nama Sea, the Messinian salt basin, Lake Pannon,
                # the two ridge-vent faunas. Everything else is province-typical,
                # so the model owns the claim about WHICH province and the
                # curated list supplies the detail inside it.
                # modeling/audit_curated_biota.py classifies all 198 spans and is
                # the check that a new curated entry declares itself.
                rows.append({"a0": s["a0"], "a1": s["a1"], "taxa": taxa,
                             **({"shared": s["shared"]} if s.get("shared") else {}),
                             **({"exception": True} if s.get("exception") else {})})
        if rows:
            out[region] = rows
    return out


def sparse():
    return _DATA.get("sparse", {})


# Anything named here may only ever carry realm="sea" taxa. NOTE deliberately
# absent: Solnhofen Lagoon and Hudson Seaway (their key fossils are the birds /
# pterosaurs / dinosaurs they preserved), and Lake Pannon (brackish, endemic
# freshwater molluscs) — realm-locking those would strip exactly what makes them
# worth naming.
MARINE_REGIONS = {
    "Panthalassa", "Panthalassic Ocean", "Panthalassic (proto)", "Iapetus Ocean",
    "Rheic Ocean", "Tethys Ocean", "Palaeo-Tethys", "Mirovia", "Pacific Ocean",
    "Atlantic Ocean", "Indian Ocean", "Southern Ocean", "Arctic Ocean",
    "Mediterranean", "Mediterranean (closing)", "Western Interior Seaway",
    "Sauk Sea", "Zechstein Sea", "Turgai Strait", "Eromanga Sea", "Paratethys",
    "Mozambique Ocean", "Adamastor Ocean", "Ural Ocean", "Tornquist Sea",
    "Neo-Panthalassa", "Sundance Sea", "Trans-Saharan Sea",
    "Central American Sea", "East African Ocean",
    # marine features added 2026-07 to end the "every ocean shows the same fauna"
    "Muschelkalk Sea", "Mowry Sea", "Boreal Sea", "Bearpaw Sea", "Neotethys",
    "Nama Sea", "Tippecanoe Sea", "Kaskaskia Sea", "Absaroka Sea",
    "Messinian Salt Basin", "West Siberian Sea", "South China Sea", "Tasman Sea",
    "Gulf of Mexico", "Mid-Atlantic Ridge", "East Pacific Rise", "Cannonball Sea",
    "Viking Corridor", "Hispanic Corridor",
}


def icons():
    return ICONS


def biomes_at(age):
    """Biomes for the nearest sampled age."""
    if not _DATA["biomes"]:
        return []
    best = min(_DATA["biomes"], key=lambda b: abs(b["age"] - age))
    return best["biomes"]


if __name__ == "__main__":
    miss = sorted({t["n"] for e in life() for t in e["taxa"] if not t["ic"]})
    print("intervals:", len(life()), " biome samples:", len(biomes()),
          " regions:", len(regional()), " icons:", len(ICONS))
    print(f"  interval-list taxa with no drawing: {len(miss)}  {miss[:12]}")


# --------------------------------------------------------------- endemism --
#: Taxa in the GLOBAL per-interval list that were NOT global. The global list is
#: what the app falls back to when a clicked landmass has no biota of its own,
#: and without this it will happily list Proconsul -- an African ape -- under
#: North America, which is what it did. Tagging the clear cases lets the
#: fallback drop anything that plainly did not live there.
#:
#: Only unambiguous restrictions are listed. A taxon absent from here is treated
#: as unrestricted, which is the safe default: over-filtering would silently
#: hide real animals, and the fallback already announces itself as a global list.
ENDEMIC = {
    # Hominins and other post-Cretaceous land taxa that were NOT global.
    # Homo erectus is the one that was reported: it was being listed for a Lake
    # Titicaca card at 1 Ma, and it never reached the Americas -- no hominin did
    # until Homo sapiens, around 20,000 years ago. The taxon carried an age
    # window and no region, and an unrestricted entry is shown everywhere the
    # age matches, so "when" was right and "where" was unconstrained.
    "Homo erectus": {"af", "as", "eu"},
    "Paranthropus boisei": {"af"},
    "Armillaria ostoyae": {"na"},          # one clone, in Oregon
    # Homo sapiens reached everywhere, but not at once, and the entry's own note
    # already says the map should not show it before it arrived.
    "Homo sapiens": {"af", "as", "eu", "au", "na", "sa"},
    "Metasequoia": {"as", "na", "eu"},     # northern-hemisphere dawn redwood
    "Multituberculata": {"na", "eu", "as"},
    "Condylarthra": {"na", "eu", "as"},
    "Plesiadapiformes": {"na", "eu"},
    "Nypa": {"as", "au"},                  # mangrove palm, Indo-Pacific
    "Hipparion": {"na", "eu", "as", "af"},  # never South America or Australia
    # Africa
    "Proconsul": {"af"}, "Sahelanthropus tchadensis": {"af"},
    "Aegyptopithecus": {"af"}, "Australopithecus afarensis": {"af"},
    "Homo habilis": {"af"}, "Deinotherium": {"af", "eu", "as"},
    # South America
    "Megatherium": {"sa"}, "Glyptodon": {"sa"}, "Titanoboa cerrejonensis": {"sa"},
    "Platyrrhini": {"sa"}, "Titanis walleri": {"sa", "na"},
    "Phorusrhacos longissimus": {"sa"}, "Macrauchenia patachonica": {"sa"},
    "Pyrotherium": {"sa"}, "Doedicurus clavicaudatus": {"sa"},
    "Cladosictis patagonica": {"sa"}, "Toxodon": {"sa"},
    # North America
    "Megacerops": {"na"}, "Mesohippus": {"na"}, "Uintatherium": {"na"},
    "Smilodon": {"na", "sa"}, "Smilodon fatalis": {"na", "sa"},
    "Aepycamelus giraffinus": {"na"}, "Merychippus insignis": {"na"},
    "Teleoceras proterum": {"na"}, "Hyracotherium": {"na", "eu"},
    "Icaronycteris": {"na"}, "Carpolestes": {"na"},
    # Australia and New Guinea
    "Diprotodon": {"au"}, "Diprotodon optatum": {"au"},
    "Thylacoleo carnifex": {"au"}, "Obdurodon": {"au"},
    "Varanus priscus": {"au"}, "Genyornis newtoni": {"au"},
    "Procoptodon goliah": {"au"}, "Nimbadon lavarackorum": {"au"},
    "Macropus fuliginosus": {"au"},
    # Eurasia
    "Coelodonta antiquitatis": {"eu", "as"},
    "Mammuthus primigenius": {"na", "eu", "as"}, "Mammuthus": {"na", "eu", "as", "af"},
"Megaloceros giganteus": {"eu", "as"},
    "Ursus spelaeus": {"eu"}, "Panthera spelaea": {"na", "eu", "as"},
    "Gastornis": {"na", "eu"}, "Hyaenodon horridus": {"na"},
    "Basilosaurus isis": {"af"}, "Pakicetus attocki": {"as"},
    "Ambulocetus natans": {"as"}, "Aegyptopithecus": {"af"}, "Paraceratherium": {"as", "eu"},
    "Darwinius masillae": {"eu"}, "Homo neanderthalensis": {"eu", "as"},
    "Elephas maximus": {"as"}, "Mammut americanum": {"na"},
    # Southern-hemisphere plants
    "Nothofagus": {"sa", "au", "an"},
    "Sequoiadendron giganteum": {"na"},
}

#: Broad region tags for the LANDMASS labels the app can show a card for. Deep
#: time makes this fuzzy on purpose -- a Palaeozoic continent is not a modern
#: one -- so only names with an unambiguous modern descendant are mapped, and
#: anything unmapped skips the filter entirely.
LABEL_REGION = {
    "North America": {"na"}, "Laurentia": {"na"}, "Laurussia (Euramerica)": {"na", "eu"},
    "South America": {"sa"}, "Amazonia": {"sa"}, "Patagonia": {"sa"},
    "Africa": {"af"}, "Congo Craton": {"af"}, "Kalahari Craton": {"af"},
    "West Africa Craton": {"af"}, "Sao Francisco Craton": {"sa"},
    "Eurasia": {"eu", "as"}, "Europe": {"eu"}, "Baltica": {"eu"},
    "Siberia": {"as"}, "North China": {"as"}, "South China": {"as"},
    "India": {"as"}, "Greater India": {"as"},
    "Australia": {"au"}, "Sahul": {"au"}, "Zealandia": {"au"},
    "Antarctica": {"an"}, "Australia-East Antarctica": {"au", "an"},
}


def endemic(name):
    """Region tags a taxon is restricted to, or None if unrestricted."""
    return sorted(ENDEMIC.get(name, [])) or None


def label_region(name):
    return sorted(LABEL_REGION.get(name, [])) or None
