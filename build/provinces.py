"""Which biogeographic province each label sits in, at every age it is drawn.

THE PROBLEM THIS CLOSES. 336 labels show a biota panel and 101 of them have a
curated list, so **235 fell straight through to ONE GLOBAL LIST for the whole
interval**. A Verkhoyansk Belt card at 250 Ma showed "the world's Late Permian
biota" -- true of the world, and not an answer to what lived there. The heading
said so honestly, which made it a stated gap rather than an error, but it was
still the same list on two hundred different cards.

THE DECISION (2026-07-26). The MODEL decides; a curated list is a flagged
EXCEPTION. `Deep Research/modeling/paleobiogeography.py` returns a named province
for every cell in 0-1000 Ma -- 49 distinct ones, from the Sturtian snowball ocean
through the five named Ordovician shelf provinces to the Cathaysian coal flora --
so the panel can say WHICH province a place was in instead of listing the world.
Where the model still cannot place a point, the global list stays, under a
heading that says it is global.

WHAT THIS MODULE DOES. Walks every label across its own age window, takes its
palaeolatitude from the track the build already computes, asks the province model,
and emits RUNS -- [age_lo, age_hi, province_id] -- because a province changes on
the scale of a period while the timeline steps every 5 Myr, so 336 labels x 251
ages compresses to a few hundred runs. The app then looks up a province in
constant time with no biogeography ported into JavaScript.

The catalogue is imported, not copied: `paleobiogeography` is stdlib-only for
exactly this reason, and a second copy would drift from the one the audits check.
"""
import os
import sys

_MODELING = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "Deep Research", "modeling")

_PB = _PG = _TD = None

# The province model's markers are bare NAMES, and a card that prints a bullet
# list of bare names is not the same object as a card that shows an organism.
# The curated lists have an icon, a rank, a realm and a sentence about each
# animal or plant, and the province tier has to match them or it reads as a
# lesser thing on the same panel.
#
# `taxa_db` in the research folder covers 42 of the 96 markers. These are the
# other 54 -- the ones that are groups, sediments and floras rather than the
# single genera a taxon database collects. Rank and realm as well as the note,
# because the card prints all three.
MARKER_NOTES = {
    # --- Ediacaran and Precambrian ------------------------------------------
    "Rangea": ("genus", "sea", "The type rangeomorph: a frond built from one branching unit repeated at four scales, with no mouth, gut or limbs."),
    "Bradgatia": ("genus", "sea", "A bush-shaped rangeomorph, its fronds radiating from a common base rather than standing on a stalk."),
    "Pteridinium": ("genus", "sea", "A three-vaned erniettomorph that lived half-buried in sand, its body a set of quilted tubes."),
    "Spriggina": ("genus", "sea", "A segmented Ediacaran animal with a crescentic head shield -- one of the oldest bilaterally organised body plans known."),
    "stromatolites": ("informal", "sea", "Layered buildups made by microbial mats trapping and binding sediment. The dominant reef of the first three billion years."),
    "microbialites": ("informal", "sea", "Sediment bound by microbial mats. They come back in force after every mass extinction, when the grazers that normally crop them are gone."),
    "cyanobacteria": ("phylum", "sea", "Oxygenic photosynthetic bacteria: the organisms that put oxygen in the atmosphere, and the builders of stromatolites."),
    "banded iron formation": ("informal", "sea", "Alternating iron-rich and silica-rich layers precipitated from a ferruginous ocean. They largely stop forming by 1.85 Ga, once the deep sea holds oxygen."),
    "cap carbonates": ("informal", "sea", "Sheets of carbonate laid straight on top of glacial debris as a snowball Earth ended, under an atmosphere carrying hundreds of times today's CO2."),
    # --- Palaeozoic marine ---------------------------------------------------
    "Lingula": ("genus", "sea", "An inarticulate brachiopod that has burrowed in nearshore mud since the Cambrian -- among the most conservative animals known."),
    "Pentamerus": ("genus", "sea", "A large Silurian brachiopod that formed dense shell banks across carbonate shelves."),
    "Amphipora": ("genus", "sea", "A rod-shaped stromatoporoid sponge that grew in dense thickets in the lagoons behind Devonian reefs."),
    "Claraia": ("genus", "sea", "A thin-shelled bivalve that carpeted oxygen-poor sea floors after the end-Permian extinction: a disaster taxon, abundant because almost nothing else survived."),
    "Otoceras": ("genus", "sea", "The ammonoid whose first appearance defines the base of the Triassic."),
    "Verbeekina": ("genus", "sea", "A large spherical fusulinid foraminifer, up to a centimetre across, and an index fossil of the warm Permian Tethyan shelves."),
    "Waagenophyllum": ("genus", "sea", "A rugose coral of Permian Tethyan reefs, colonial and thickly walled."),
    "Deltopecten": ("genus", "sea", "A scallop-like bivalve of the cool Permian shelves of Gondwana, found with glacial dropstones in the same beds."),
    # --- Mesozoic and Cenozoic marine ---------------------------------------
    "Daonella": ("genus", "sea", "A flat, paper-thin bivalve of Triassic deep-shelf muds, often found in mass-mortality pavements."),
    "ceratitid ammonoids": ("order", "sea", "The ammonoid group that radiated through the Triassic from the handful of lineages that survived the end-Permian bottleneck."),
    "Dachstein reef fauna": ("informal", "sea", "The Late Triassic reef community of the Tethyan carbonate platforms -- scleractinian corals, calcareous sponges and encrusting problematica."),
    "belemnites": ("order", "sea", "Squid-like cephalopods with an internal bullet-shaped guard, abundant enough in Jurassic and Cretaceous seas to make rock."),
    "orbitolinids": ("group", "sea", "Large conical foraminifera of Cretaceous carbonate platforms, big enough to see without a lens."),
    "Discocyclina": ("genus", "sea", "A large disc-shaped foraminifer of Palaeogene tropical shelves, whose tests build limestone."),
    "Acropora": ("genus", "sea", "The fast-growing staghorn and table corals that build most of the framework of a modern reef."),
    "giant clams": ("genus", "sea", "Tridacna and its relatives, which farm symbiotic algae inside their own mantle tissue on shallow tropical reefs."),
    "reef fish radiation": ("informal", "sea", "The Cenozoic diversification of the fish families that live on and around coral -- wrasses, damselfish, butterflyfish."),
    "diatom ooze": ("informal", "sea", "Sea-floor sediment made of siliceous diatom skeletons, under the high-productivity belts of the Southern Ocean and the North Pacific."),
    "krill": ("order", "sea", "Swarming shrimp-like crustaceans. In the Southern Ocean they are the single link between diatoms and everything larger."),
    "notothenioid fish": ("group", "sea", "Antarctic fish carrying antifreeze glycoproteins in their blood, which radiated into an empty ocean as it froze."),
    # --- early land plants ---------------------------------------------------
    "Rhynia": ("genus", "land", "A leafless, rootless early vascular plant -- essentially a green stem with sporangia on top, preserved whole in the Rhynie chert."),
    "Asteroxylon": ("genus", "land", "An early lycophyte with leaf-like enations along a branching stem, and rooting structures that are not yet true roots."),
    "Zosterophyllum": ("genus", "land", "An early vascular plant carrying sporangia along the sides of its stems, on the line that leads to the lycophytes."),
    "lichens": ("informal", "land", "A fungus farming algae or cyanobacteria inside itself. Among the first things to colonise bare rock, and still the pioneer on newly exposed ground."),
    # --- Carboniferous-Permian floras ---------------------------------------
    "Cathaysiodendron": ("genus", "land", "A lycopsid tree of the Cathaysian coal forests of South China -- the rainforests that kept growing after the Euramerican ones collapsed."),
    "Lobatannularia": ("genus", "land", "A horsetail relative with whorls of broad leaves, characteristic of the Cathaysian flora."),
    "Noeggerathiopsis": ("genus", "land", "A strap-leaved cordaitalean of the Angaran flora: the cool-temperate Permian vegetation of Siberia."),
    "Vojnovskya": ("genus", "land", "A gymnosperm of the Angaran flora, from a Permian Siberia too cold for the coal swamps of the tropics."),
    # --- Triassic-Jurassic floras -------------------------------------------
    "Voltzia": ("genus", "land", "An early conifer of the Triassic, spreading across ground left empty when every peat-forming plant lineage died at the end of the Permian."),
    "Neocalamites": ("genus", "land", "A large Triassic and Jurassic horsetail, successor to the Calamites of the Carboniferous swamps."),
    "Umkomasia": ("genus", "land", "The seed-bearing organ of Dicroidium, the seed fern that dominated Triassic Gondwana."),
    "Ptilophyllum": ("genus", "land", "A bennettitalean with stiff fern-like fronds, common through Jurassic and Cretaceous floras."),
    # --- angiosperms and modern vegetation ----------------------------------
    "Nymphaeales": ("order", "land", "Water lilies -- one of the earliest-branching flowering plant lineages, and among the first angiosperms in the record."),
    "Platanaceae": ("family", "land", "The plane-tree family, among the first flowering plants to become common in Cretaceous floras."),
    "angiosperm canopy trees": ("group", "land", "Flowering trees closing a canopy overhead. That structure is what makes a rainforest a rainforest, and it does not exist before the Late Cretaceous."),
    "Poaceae": ("family", "land", "The grasses. Present from the Late Cretaceous, and ecologically almost invisible until about 40 Ma, when open grassland begins."),
    "C4 grasses": ("group", "land", "Grasses using the C4 photosynthetic pathway, which is efficient in warm, dry, low-CO2 air. They build tropical savanna from about 8 Ma."),
    "sedges": ("family", "land", "Cyperaceae: grass-like plants of wet ground, marsh and tundra, where true grasses do less well."),
    "Quercus": ("genus", "land", "Oak. With beech, the backbone of Northern Hemisphere temperate deciduous forest."),
    "Fagus": ("genus", "land", "Beech, a dominant temperate deciduous tree casting shade too deep for most competitors."),
    "Pinus": ("genus", "land", "Pine: the most widespread conifer genus, holding poor soils and fire-prone ground since the Cretaceous."),
    "Picea": ("genus", "land", "Spruce, a defining conifer of the boreal forest."),
    "Larix": ("genus", "land", "Larch -- the deciduous conifer, dropping its needles to survive the extreme continental winters of interior Siberia."),
    "dwarf birch": ("species", "land", "A low, ground-hugging birch of tundra and the ragged edge of the boreal forest."),
    "Acacia": ("genus", "land", "Thorny legume trees and shrubs of the seasonally dry tropics, and a defining element of savanna woodland."),
    "succulents": ("group", "land", "Water-storing plants of arid ground -- cacti in the Americas, euphorbias in Africa -- which spread as deserts do."),
    "epiphytes": ("group", "land", "Plants growing on other plants: orchids, bromeliads, ferns. They need a canopy to live in, so they date it."),
    "lianas": ("group", "land", "Woody climbers using trees as scaffolding to reach the light. Like epiphytes, they exist only where there is a canopy."),
}

# The province model is banded and block-aware, and `block` is what turns
# "tropical" into "Cathaysian Province". Only labels that ARE a named block can
# supply one; everything else gets the latitude band, which is what the model is
# built to fall back on.
MARINE_TYPES = {"ocean", "sea"}


def _load():
    global _PB, _PG, _TD
    if _PB is None:
        try:
            if _MODELING not in sys.path:
                sys.path.insert(0, _MODELING)
            import paleobiogeography                       # noqa: PLC0415
            import paleogeography                          # noqa: PLC0415
            _PB, _PG = paleobiogeography, paleogeography
        except Exception:                                  # noqa: BLE001
            _PB, _PG = False, False
    if _TD is None:
        try:
            import taxa_db                                 # noqa: PLC0415
            _TD = taxa_db
        except Exception:                                  # noqa: BLE001
            _TD = False
    return (_PB or None), (_PG or None)


def marker_taxon(name, realm):
    """A province marker as a full taxon record, or None if it cannot be one.

    Same shape the curated lists ship in -- {n, r, realm, note, ic} -- so the
    province tier of the biota panel renders through the SAME lifeHTML as
    everything else: an icon, a rank, a realm and a sentence. A card that lists
    bare names beside cards that show organisms reads as the poor relation, and
    it is also less useful: "Lepidodendron" tells a reader nothing they did not
    already know from not knowing it.

    Source order: taxa_db (42 of the 96 markers, with size, habit and diet
    behind them), then MARKER_NOTES above for the groups and sediments a taxon
    database does not collect. Anything in neither is dropped rather than shown
    bare -- that is the honest failure, and the selftest counts it so a new
    province marker cannot slip through undescribed.
    """
    default_realm = "sea" if realm == "marine" else "land"
    rec = _TD.by_name(name) if _TD else None
    if rec is not None:
        note = rec.note or (rec.habit or "").capitalize()
        if not note:
            return None
        return {"n": name, "r": rec.rank, "realm": rec.realm or default_realm,
                "note": note}
    hit = MARKER_NOTES.get(name)
    if hit is None:
        return None
    rank, rlm, note = hit
    return {"n": name, "r": rank, "realm": rlm, "note": note}


def _icon(name, realm):
    """The illustration id, from life.py's own ordered first-match table, so a
    province marker and a curated taxon of the same name get the same drawing."""
    try:
        import life                                        # noqa: PLC0415
        return life.icon_for(name, realm) or ""
    except Exception:                                      # noqa: BLE001
        return ""


def _lat_at(lab, age):
    """Palaeolatitude of a label at `age`, from its own track."""
    tr = lab.get("tr")
    if not tr:
        return lab.get("lat")
    if age <= tr[0][0]:
        return tr[0][2]
    if age >= tr[-1][0]:
        return tr[-1][2]
    for (a0, _x0, y0), (a1, _x1, y1) in zip(tr, tr[1:]):
        if a0 <= age <= a1:
            f = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return y0 + (y1 - y0) * f
    return tr[-1][2]


def build(labels, step=5):
    """({province_id: record}, {label_name: [[a_lo, a_hi, id], ...]}).

    Runs are inclusive at both ends and cover only the label's own window, so a
    name is never given a province at an age it is not drawn.
    """
    pb, pg = _load()
    if pb is None:
        return {}, {}
    blocks = set(getattr(pg, "BLOCKS", ()) or ())

    ids, recs = {}, {}
    out = {}
    for lab in labels:
        name = lab.get("n")
        a0, a1 = lab.get("a0", 0), lab.get("a1", 0)
        lo, hi = min(a0, a1), max(a0, a1)
        if hi <= 0 or lo > 1000:
            continue                       # future-only, or off the model's range
        lo = max(lo, 0)
        hi = min(hi, 1000)
        realm = "marine" if lab.get("t") in MARINE_TYPES else "terrestrial"
        block = name if name in blocks else None
        runs = []
        a = lo
        while a <= hi + 1e-9:
            lat = _lat_at(lab, a)
            if lat is None:
                a += step
                continue
            try:
                p = pb.province(float(a), float(lat), realm, block)
            except Exception:                              # noqa: BLE001
                a += step
                continue
            # A province with confidence 'none' is a climate band wearing a
            # province's clothes; say nothing rather than dress it up.
            if p is None or p.confidence == "none":
                a += step
                continue
            key = (p.name, p.realm)
            pid = ids.get(key)
            if pid is None:
                pid = ids[key] = len(ids)
                mk = []
                for m in list(p.markers)[:8]:
                    t = marker_taxon(m, p.realm)
                    if t is None:
                        continue
                    t["ic"] = _icon(t["n"], t["realm"])
                    mk.append(t)
                recs[pid] = {"n": p.name, "r": p.realm, "b": p.basis,
                             "c": p.confidence, "note": p.note, "mk": mk}
            if runs and runs[-1][2] == pid and abs(runs[-1][1] - (a - step)) < 1e-6:
                runs[-1][1] = a
            else:
                runs.append([a, a, pid])
            a += step
        if runs:
            out[name] = runs
    return recs, out


def _selftest():
    pb, _pg = _load()
    assert pb is not None, "Deep Research/modeling/paleobiogeography.py did not import"
    labs = [{"n": "Siberia", "t": "continent", "a0": 0, "a1": 540, "lon": 100, "lat": 65},
            {"n": "Tethys Ocean", "t": "ocean", "a0": 120, "a1": 260, "lon": 90, "lat": 5},
            {"n": "Verkhoyansk Belt", "t": "orogen", "a0": 0, "a1": 300,
             "lon": 130, "lat": 65}]
    recs, runs = build(labs)
    assert runs, "no runs produced"
    for lab in labs:
        assert lab["n"] in runs, f"{lab['n']} got no province at any age"
        for a_lo, a_hi, pid in runs[lab["n"]]:
            assert a_lo <= a_hi and pid in recs
    n = sum(len(v) for v in runs.values())
    print(f"provinces OK: {len(recs)} distinct provinces, {n} runs over "
          f"{len(runs)} labels")
    for name, rr in runs.items():
        print(f"  {name}: " + "; ".join(
            f"{a1:g}-{a0:g} Ma {recs[p]['n']}" for a0, a1, p in rr[:4]))
    # EVERY marker the model can emit must be describable, or the province tier
    # quietly shows fewer organisms than the province actually has. Walk the
    # whole model, not just the provinces these three test labels happen to hit.
    pb, _pg = _load()
    missing, total = set(), set()
    for realm in ("marine", "terrestrial"):
        for age in list(range(0, 1001, 10)):
            for lat in (-80, -55, -30, -10, 0, 10, 30, 55, 80):
                try:
                    p = pb.province(float(age), float(lat), realm)
                except Exception:                          # noqa: BLE001
                    continue
                for m in p.markers:
                    total.add(m)
                    if marker_taxon(m, p.realm) is None:
                        missing.add(m)
    print(f"  markers: {len(total)} distinct across the whole model, "
          f"{len(total) - len(missing)} describable")
    assert not missing, ("province markers with no icon/rank/description -- add "
                         f"them to MARKER_NOTES: {sorted(missing)}")


if __name__ == "__main__":
    _selftest()
