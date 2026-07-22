"""Add the land half of the fossil record: trees, fungi, and the regional floras
and faunas that were missing.

Before this the data held 428 taxa and not one fungus, on a timeline that runs
from a billion years ago. Plants were 17 entries, nearly all of them Paleozoic,
so the cycad, palm, ginkgo and flower drawings were never once used. Land is
also where the regional record is thinnest: Australia began at 45 Ma with no
Ediacara, Africa at 150 Ma, Eurasia at 56 Ma.

Two merges:
  GLOBAL   - per geological interval, inserted at index 1 rather than appended,
             because the panels show only the first four to six taxa of the
             realm you clicked and an appended plant is an invisible plant.
  REGIONAL - per landmass per interval, added to the span that already covers
             those ages where one exists, otherwise as a new span.

Duplicate names are skipped, so this is idempotent.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "life_data.json")

# interval name -> [(name, rank, realm, note), ...]
GLOBAL = {
 "Tonian": [
  ("Ourasphaira giraldae", "species", "fresh",
   "Branching filaments with chitin-like walls from Arctic Canada, dated near a "
   "billion years. If the identification holds it is the oldest fungus known, "
   "which puts fungi on Earth long before animals.")],
 "Early Ordovician": [
  ("Tortotubus protuberans", "species", "land",
   "The oldest fossil of a land organism with cord-forming mycelium. Fungi were "
   "rotting and binding the first soils before there were plant roots to put "
   "in them.")],
 "Middle Ordovician": [
  ("Glomeromycota", "phylum", "land",
   "Arbuscular mycorrhizal fungi, found inside the earliest land plants. Those "
   "plants had no roots, so the fungus was the root; the partnership still runs "
   "about eighty percent of plant species today.")],
 "Silurian": [
  ("Prototaxites", "genus", "land",
   "Tapering trunks up to eight metres tall standing over a landscape where "
   "nothing else reached the knee. Carbon isotopes point to a fungus rather "
   "than a plant, making it the largest organism on land for 40 million "
   "years.")],
 "Early Devonian": [
  ("Aglaophyton majus", "species", "land",
   "A rootless Rhynie plant with arbuscular fungi preserved alive inside its "
   "stems, the oldest direct fossil of the symbiosis that got plants onto "
   "land.")],
 "Middle Devonian": [
  ("Calamophyton", "genus", "land",
   "A cladoxylopsid tree from the oldest forest floors known. It shed whole "
   "branches rather than leaves, and its roots began cracking rock into soil "
   "and drawing CO2 out of the air.")],
 "Late Devonian": [
  ("Attercopus fimbriunguis", "species", "land",
   "An early arachnid that made silk from spigots set in plates rather than "
   "spinnerets: silk long before webs.")],
 "Mississippian": [
  ("Archaeocalamites", "genus", "land",
   "An early horsetail of the Mississippian wetlands, ancestral to the giant "
   "Calamites that would build the coal swamps.")],
 "Pennsylvanian": [
  ("Cordaites", "genus", "land",
   "Strap-leaved coniferophytes up to thirty metres tall on the drier ground "
   "beyond the mires: the first vegetation that would read as forest rather "
   "than swamp."),
  ("Psaronius", "genus", "land",
   "A tree fern whose trunk was a mantle of adventitious roots rather than "
   "wood. It took over the mires as the giant lycopsids faltered.")],
 "Early Permian": [
  ("Agaricomycetes", "class", "land",
   "Molecular clocks put the origin of lignin-digesting white-rot fungi near "
   "here. Before them dead wood simply piled up, which is most of the reason "
   "almost all the world's coal is older than this.")],
 "Late Permian": [
  ("Reduviasporonites", "genus", "land",
   "A worldwide fungal spike of filaments and spores at the extinction horizon "
   "itself, usually read as the rot of a collapsing land flora, though some "
   "workers argue the fossils are algae.")],
 "Middle Triassic": [
  ("Voltziales", "order", "land",
   "Conifers spreading through the dry Triassic interior: the first forests "
   "built by plants that could survive a real dry season.")],
 "Late Triassic": [
  ("Bennettitales", "order", "land",
   "Cycad-like plants with tight, flower-like cones that were probably insect "
   "pollinated. An independent Mesozoic run at the flower that left no "
   "descendants.")],
 "Early Jurassic": [
  ("Ginkgoales", "order", "land",
   "The ginkgo lineage at its widest, in mid-latitude forests on nearly every "
   "continent. One species, Ginkgo biloba, is still alive.")],
 "Middle Jurassic": [
  ("Castorocauda lutrasimilis", "species", "fresh",
   "A furred, beaver-tailed, web-footed mammaliaform that swam and ate fish. "
   "Mammal ecology was already varied a hundred million years before the "
   "dinosaurs left.")],
 "Early Cretaceous": [
  ("Archaefructus", "genus", "land",
   "Among the earliest flowering plants known from whole fossils: an aquatic "
   "herb from the Yixian lake beds, with no petals at all.")],
 "Late Cretaceous": [
  ("Magnoliopsida", "class", "land",
   "Flowering plants go from rare to dominant inside forty million years, "
   "pulling pollinating insects, fruit-eating birds and the modern structure "
   "of forests along with them."),
  ("Palaeoagaracites antiquus", "species", "land",
   "The oldest gilled mushroom known, in 99-million-year-old Burmese amber and "
   "already entirely modern in form.")],
 "Paleocene": [
  ("Metasequoia", "genus", "land",
   "Dawn-redwood swamp forest grew inside the Arctic Circle in the Paleocene "
   "warmth: a conifer that dropped its needles to sit out months of polar "
   "darkness.")],
 "Eocene": [
  ("Azolla", "genus", "fresh",
   "A floating fern that bloomed across a fresh-water-capped Arctic Ocean for "
   "roughly 800,000 years. The carbon it buried helped tip the planet out of "
   "its greenhouse."),
  ("Nypa", "genus", "land",
   "A mangrove palm whose pollen turns up in Eocene England and Belgium. For a "
   "while the tropics reached far enough north to put mangroves in the North "
   "Sea.")],
 "Oligocene": [
  ("Poaceae (C3 grasslands)", "family", "land",
   "Open grassy country spreads as the world cools and dries after the Eocene, "
   "and grazing mammals begin evolving the tall, cement-filled teeth that "
   "silica-rich grass demands.")],
 "Quaternary": [
  ("Armillaria ostoyae", "species", "land",
   "A single honey-fungus clone threads through nine square kilometres of "
   "Oregon forest soil. By area it is the largest organism known to be alive."),
  ("Sequoiadendron giganteum", "species", "land",
   "The giant sequoia, the largest tree on Earth by trunk volume, is a relict "
   "of a conifer flora that once ringed the northern hemisphere.")],
}

# region -> [(a0, a1, [(name, rank, realm, note), ...]), ...]
REGIONAL = {
 "Rodinia": [(720, 1000, [
  ("Ourasphaira giraldae", "species", "fresh",
   "Chitin-walled branching microfossils from the Arctic shelf of Rodinia, "
   "arguably the oldest fungus and older than any animal.")])],
 "Baltica": [(430, 458, [
  ("Tortotubus protuberans", "species", "land",
   "From Gotland: cord-forming fungal filaments binding soil on bare Silurian "
   "ground, before plants had roots.")])],
 "Laurentia": [(430, 443, [
  ("Pneumodesmus newmani", "species", "land",
   "A millipede from Stonehaven in Scotland with open spiracles, among the "
   "earliest animals known to have breathed air.")])],
 "Laurussia (Euramerica)": [
  (393, 419, [
   ("Prototaxites", "genus", "land",
    "Eight-metre tapering trunks standing over a knee-high Old Red Sandstone "
    "flora. The largest thing alive on land, and a fungus.")]),
  (383, 393, [
   ("Archaeopteris", "genus", "land",
    "The first modern-looking tree: a real woody trunk, flat leaves and deep "
    "roots. Its forests made the first deep soils and pulled down CO2.")])],
 "Pangaea": [
  (299, 320, [
   ("Cordaites", "genus", "land",
    "Strap-leaved coniferophytes thirty metres tall on the drier ground above "
    "the coal mires.")]),
  (273, 299, [
   ("Callipteris (Autunia)", "genus", "land",
    "The seed fern that marks the Permian red beds across Euramerica: the "
    "flora of a continent that had lost its swamps.")])],
 "Gondwana": [
  (299, 359, [
   ("Botrychiopsis", "genus", "land",
    "A cold-climate seed plant of the floras that recolonised bare ground as "
    "the Karoo ice sheets melted.")]),
  (252, 299, [
   ("Vertebraria", "genus", "land",
    "The segmented root of the Glossopteris trees, preserved in Antarctic peat "
    "and Indian coal: the plumbing of a forest that grew in polar light.")]),
  (150, 201, [
   ("Cheirolepidiaceae", "family", "land",
    "A drought-tolerant conifer family whose pollen swamps Jurassic Gondwanan "
    "lowlands. This was the canopy the sauropods fed in.")])],
 "Antarctica": [(252, 299, [
  ("Glossopteris", "genus", "land",
   "Permian coal and permineralised stumps in the Transantarctic Mountains: "
   "forests that grew through six months of polar darkness."),
  ("Vertebraria", "genus", "land",
   "Segmented Glossopteris roots preserved in Antarctic peat, many still "
   "standing in growth position.")])],
 "North China": [(120, 135, [
  ("Archaefructus", "genus", "land",
   "One of the earliest flowering plants known from complete fossils, an "
   "aquatic herb in the Yixian lake beds alongside the feathered dinosaurs.")])],
 "Africa": [
  (66, 100, [
   ("Weichselia", "genus", "land",
    "A fire- and drought-tolerant tree fern that carpeted the Cretaceous North "
    "African floodplains where Spinosaurus and Paralititan lived.")]),
  (30, 56, [
   ("Nypa", "genus", "land",
    "Mangrove-palm swamp fringed the Tethyan coast of Africa. The Fayum "
    "primates lived in forest right at the water's edge.")]),
  (5, 23, [
   ("Poaceae (C4 grasses)", "family", "land",
    "C4 grasses spread across Africa after about eight million years ago, "
    "turning closed woodland into open savanna: the habitat shift that frames "
    "human origins.")]),
  (-40, 2.6, [
   ("Termitomyces", "genus", "land",
    "Fungus farmed in gardens inside African termite mounds, an agriculture "
    "tens of millions of years older than our own.")])],
 "South America": [
  (56, 66, [
   ("Cerrejon rainforest", "flora", "land",
    "The oldest neotropical rainforest known: palms, legumes and aroids in a "
    "structurally modern canopy only a few million years after the asteroid, "
    "and hot enough to support Titanoboa.")]),
  (5, 23, [
   ("Mauritia", "genus", "land",
    "Palm-dominated swamp across the Miocene Pebas mega-wetland that filled "
    "western Amazonia, the cradle of its modern diversity.")])],
 "India": [(34, 56, [
  ("Cambay amber flora (Dipterocarpaceae)", "flora", "land",
   "Fifty-million-year-old amber from Gujarat holds a dipterocarp rainforest, "
   "and insects with Asian relatives: India was already trading life across a "
   "narrowing sea.")])],
 "Australia": [
  (550, 565, [
   ("Dickinsonia", "genus", "sea",
    "The Ediacara Hills type locality: quilted soft bodies up to a metre "
    "across, with cholesterol biomarkers that make Dickinsonia an animal."),
   ("Spriggina", "genus", "sea",
    "A segmented Ediacaran form with a shield-like head end, argued over for "
    "decades as a possible early arthropod relative."),
   ("Charnia", "genus", "sea",
    "Frond-shaped rangeomorphs anchored to the sea floor, feeding without a "
    "mouth or a gut.")]),
  (23, 45, [
   ("Nothofagus", "genus", "land",
    "Cool-temperate southern beech rainforest covered Australia before it "
    "dried. Its pollen dominates Eocene cores from the coast to the "
    "interior.")]),
  (5, 23, [
   ("Eucalyptus", "genus", "land",
    "Eucalypts and charcoal rise together through the Miocene record: fire and "
    "increasing aridity remaking a rainforest continent.")])],
 "Eurasia": [(34, 56, [
  ("Arecaceae (palms)", "family", "land",
   "Palm fronds and crocodiles at fifty degrees north. Messel preserves a "
   "paratropical forest in what is now Germany.")])],
 "North America": [
  (34, 56, [
   ("Metasequoia", "genus", "land",
    "Dawn-redwood swamp forest ran across the warm Eocene interior and up onto "
    "Ellesmere Island, inside the Arctic Circle.")]),
  (5, 23, [
   ("Poaceae (prairie)", "family", "land",
    "The Great Plains grassland spreads through the Miocene, which is why its "
    "horses evolve tall, ever-growing teeth.")])],
}

# Three intervals carried no marine taxon at all, so clicking any ocean in the
# Pennsylvanian, Pliocene or Quaternary printed "a gap in this app, not in the
# ocean". It was a gap in the app. These close it.
GLOBAL.update({
 "Pennsylvanian": GLOBAL["Pennsylvanian"] + [
  ("Fusulinida", "order", "sea",
   "Rice-grain foraminifera, abundant and fast-evolving enough to date the "
   "Carboniferous limestones they largely consist of."),
  ("Productida", "order", "sea",
   "Spiny, thick-shelled brachiopods resting on soft carbonate mud, the "
   "dominant shellfish of the late Paleozoic sea floor."),
  ("Crinoidea", "class", "sea",
   "Crinoid meadows dense enough that their broken stems make entire "
   "limestone formations.")],
 "Pliocene": [
  ("Otodus megalodon", "species", "sea",
   "A shark of perhaps eighteen metres that hunted whales. It disappears near "
   "the end of the Pliocene as the oceans cool and its prey moves poleward."),
  ("Mysticeti", "infraorder", "sea",
   "Baleen whales reach modern size as intensified coastal upwelling "
   "concentrates their food into dense patches."),
  ("Discoaster", "genus", "sea",
   "Star-shaped calcareous nannoplankton whose extinction near 1.9 million "
   "years ago is used to close out the warm Pliocene ocean.")],
 "Quaternary": GLOBAL["Quaternary"] + [
  ("Balaenoptera musculus", "species", "sea",
   "The blue whale, the largest animal that has ever lived, reaching that size "
   "only in the productive oceans of the ice ages."),
  ("Scleractinia", "order", "sea",
   "Reef corals drowned and re-established over and over as sea level swings "
   "through 120 metres with each glacial cycle."),
  ("Notothenioidei", "suborder", "sea",
   "Antarctic icefish carrying antifreeze glycoproteins in their blood, a "
   "radiation that tracks the freezing of the Southern Ocean.")],
})

GLOBAL_AT = 1  # insert position; see module docstring


def _names(taxa):
    return {(t[0] if isinstance(t, (list, tuple)) else t["name"]).lower()
            for t in taxa}


def merge_global(data):
    by_name = {e["interval"]: e for e in data["life"]}
    added = skipped = 0
    for interval, rows in GLOBAL.items():
        e = by_name.get(interval)
        if e is None:
            print(f"  WARNING no interval named {interval!r}")
            continue
        have = _names(e["taxa"])
        new = [{"name": n, "rank": r, "realm": rm, "note": note}
               for n, r, rm, note in rows if n.lower() not in have]
        skipped += len(rows) - len(new)
        e["taxa"][GLOBAL_AT:GLOBAL_AT] = new
        added += len(new)
    return added, skipped


def merge_regional(data):
    rt = data.setdefault("region_taxa", {})
    added = skipped = spans = 0
    for region, rows in REGIONAL.items():
        cur = rt.setdefault(region, [])
        for a0, a1, taxa in rows:
            lo, hi = min(a0, a1), max(a0, a1)
            span = next((s for s in cur
                         if abs(min(s["a0"], s["a1"]) - lo) < 0.01
                         and abs(max(s["a0"], s["a1"]) - hi) < 0.01), None)
            if span is None:
                span = {"a0": a0, "a1": a1, "taxa": []}
                cur.append(span)
                spans += 1
            have = _names(span["taxa"])
            new = [list(t) for t in taxa if t[0].lower() not in have]
            skipped += len(taxa) - len(new)
            span["taxa"].extend(new)
            added += len(new)
        cur.sort(key=lambda s: -max(s["a0"], s["a1"]))
    return added, skipped, spans


def main():
    data = json.load(open(DATA))
    g_add, g_skip = merge_global(data)
    r_add, r_skip, r_spans = merge_regional(data)
    json.dump(data, open(DATA, "w"), separators=(",", ":"))
    total = sum(len(e["taxa"]) for e in data["life"])
    total += sum(len(s["taxa"]) for v in data["region_taxa"].values() for s in v)
    print(f"global:   +{g_add} taxa ({g_skip} already present)")
    print(f"regional: +{r_add} taxa in {r_spans} new spans "
          f"({r_skip} already present)")
    print(f"life_data.json now holds {total} taxa entries")


if __name__ == "__main__":
    main()
