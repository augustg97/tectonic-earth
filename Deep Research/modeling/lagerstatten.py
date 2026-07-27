"""B7 — Konservat-Lagerstätten as point features with present-day coordinates.

A Lagerstätte is where the fossil record stops being a catalogue of shells and
starts showing animals. Almost everything we know about soft-bodied life comes
from a few dozen sites, and they are POINTS on specific continents - so they ride
their block's plate track exactly as craters and LIPs already do in the app.

Two reasons they belong on the map rather than in a card:

  1. They explain the biota panel. When a card at 508 Ma lists Anomalocaris and
     Opabinia, the honest footnote is "because the Burgess Shale is 40 km away".
  2. They are the canonical EXCEPTIONS under the B1 design (model decides,
     curated is a flagged exception). A Lagerstätte's whole point is that it is
     not the generic assemblage - not because the animals were unusual, but
     because the PRESERVATION was.

Coordinates are PRESENT-DAY, on land today, which is the rule the build's
`coord_is_present_day()` applies and the one 18 terranes broke. Each entry names
the block it sits on so `paleo_tracks` can carry it.

`kind`: conservat (soft tissue) | concentration (mass accumulation) |
        both

Dependency-free (stdlib only).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["Lagerstatte", "SITES", "at", "by_block", "by_name"]


@dataclass(frozen=True)
class Lagerstatte:
    name: str
    lon: float
    lat: float                 # present-day, on land today
    block: str                 # paleogeography.py block, for the plate track
    base: float                # Ma, older bound
    top: float                 # Ma, younger bound
    kind: str
    realm: str                 # sea | land | fresh | mixed
    setting: str               # the depositional environment
    why: str                   # what it shows that nothing else does
    taxa: tuple = ()
    confidence: str = "good"


SITES = [
    # ---- Ediacaran -------------------------------------------------------
    Lagerstatte("Mistaken Point", -53.18, 46.63, "Avalonia", 575, 565,
                "conservat", "sea", "deep-water volcanic ash falls",
                "The Avalon assemblage, smothered in situ by ash below the photic "
                "zone - the oldest large complex organisms on Earth, preserved where "
                "they stood.",
                ("Fractofusus", "Charnia", "Bradgatia")),
    Lagerstatte("Ediacara Hills", 138.6, -31.3, "Australia", 560, 550,
                "conservat", "sea", "shallow sandy shelf, microbial mats",
                "The White Sea assemblage and the type locality of the whole biota.",
                ("Dickinsonia", "Spriggina", "Tribrachidium")),
    Lagerstatte("Nama Group", 16.4, -25.6, "Kalahari Craton", 550, 538,
                "conservat", "sea", "sandy shelf, three-dimensional preservation",
                "The first mineralised skeletons - and Cloudina tubes with predatory "
                "boreholes, the earliest direct evidence of predation.",
                ("Cloudina", "Namacalathus", "Pteridinium")),
    Lagerstatte("Doushantuo", 111.0, 30.9, "South China", 600, 551,
                "conservat", "sea", "phosphatised shelf sediments",
                "Phosphate preservation down to individual CELLS, including embryos - "
                "the highest-resolution window in the whole Precambrian.",
                ("Megasphaera", "acanthomorph acritarchs"), "moderate"),

    # ---- Cambrian --------------------------------------------------------
    Lagerstatte("Chengjiang", 102.6, 24.7, "South China", 520, 515,
                "conservat", "sea", "storm-buried shelf muds",
                "The earliest of the great Cambrian windows, and the one with the best "
                "early chordates. Over 250 species.",
                ("Haikouichthys", "Myllokunmingia", "Fuxianhuia")),
    Lagerstatte("Sirius Passet", -35.0, 82.8, "Laurentia", 518, 516,
                "conservat", "sea", "deep shelf below a carbonate platform margin",
                "The North Greenland window - a different community from Chengjiang at "
                "almost the same age, which is how we know Cambrian faunas were "
                "provincial.",
                ("Halkieria", "Kerygmachela", "Pambdelurion")),
    Lagerstatte("Emu Bay Shale", 137.5, -35.6, "Australia", 514, 512,
                "conservat", "sea", "restricted marine basin, rapid burial",
                "The only Cambrian Lagerstätte on Gondwana with preserved EYES - "
                "Anomalocaris eyes with 16,000 lenses each, which settles what it was "
                "for.",
                ("Anomalocaris", "Isoxys", "Redlichia")),
    Lagerstatte("Burgess Shale", -116.5, 51.4, "Laurentia", 508, 505,
                "conservat", "sea", "muds swept off a carbonate escarpment",
                "The type example, and still the richest. Its reinterpretation in the "
                "1970s-80s is what made 'disparity' a word palaeontologists argue about.",
                ("Marrella", "Opabinia", "Hallucigenia", "Wiwaxia", "Pikaia")),
    Lagerstatte("Qingjiang", 110.8, 30.2, "South China", 518, 518,
                "conservat", "sea", "deltaic muds, rapid burial",
                "Found in 2019: over 20,000 specimens with muscles, gills and guts "
                "visible, and a community only ~8% overlapping Chengjiang's.",
                ("cnidarians", "kinorhynchs", "ctenophores")),
    Lagerstatte("Orsten", 16.6, 56.9, "Baltica", 500, 492,
                "conservat", "sea", "anoxic limestone nodules",
                "Phosphatised microfossils under 2 mm, preserved in three dimensions "
                "with limbs and setae intact - larval crustaceans you can put under an "
                "SEM.",
                ("Rehbachiella", "Agnostus larvae")),

    # ---- Ordovician to Devonian -----------------------------------------
    Lagerstatte("Fezouata", -6.9, 30.4, "West African Craton", 480, 472,
                "conservat", "sea", "storm-influenced shelf off high-latitude Gondwana",
                "Proves the Cambrian body plans did NOT all die at the boundary - "
                "radiodonts and other 'Cambrian' animals survive well into the "
                "Ordovician, they just stop being preserved.",
                ("Aegirocassis", "marrellomorphs", "horseshoe crabs")),
    Lagerstatte("Soom Shale", 21.0, -32.0, "Kalahari Craton", 445, 443,
                "conservat", "sea", "cold quiet basin beneath the Hirnantian ice",
                "Deposited under a melting ice sheet: preserves muscle tissue, and the "
                "only conodont animals complete enough to show what the teeth belonged "
                "to.",
                ("Promissum", "Soomaspis")),
    Lagerstatte("Rhynie Chert", -2.84, 57.32, "Laurentia", 411, 407,
                "conservat", "land", "hot-spring silica flooding a wetland",
                "A whole terrestrial ecosystem silicified where it grew - plants with "
                "cell walls intact, the first mycorrhizal fungi, and the first "
                "land arthropods, all in place.",
                ("Rhynia", "Aglaophyton", "Rhyniognatha", "Palaeocharinus")),
    Lagerstatte("Hunsrück Slate", 7.6, 50.0, "Avalonia", 409, 405,
                "conservat", "sea", "rapid burial then pyritisation",
                "Pyritised soft tissue, so it can be X-rayed - the only way to see "
                "inside an articulated Devonian crinoid or asteroid.",
                ("Chotecops", "Mimetaster", "Palaeoisopus")),
    Lagerstatte("Gogo Formation", 126.1, -18.3, "Australia", 384, 380,
                "conservat", "sea", "carbonate reef inter-reef basins, limestone nodules",
                "Three-dimensional uncrushed fish, including Materpiscis with an "
                "umbilical cord - the oldest known live birth in a vertebrate.",
                ("Materpiscis", "Eastmanosteus", "Gogonasus")),

    # ---- Carboniferous to Permian ---------------------------------------
    Lagerstatte("East Kirkton", -3.5, 55.9, "Laurentia", 336, 331,
                "conservat", "land", "hot-spring lake in a volcanic setting",
                "'Lizzie' - the earliest reptiliomorph amniote-grade tetrapod, from the "
                "middle of Romer's Gap.",
                ("Westlothiana", "Balanerpeton")),
    Lagerstatte("Mazon Creek", -88.2, 41.3, "Laurentia", 309, 307,
                "both", "mixed", "siderite concretions in a delta",
                "A delta captures marine, brackish and terrestrial communities side by "
                "side - including the Tully Monster, which has resisted classification "
                "for sixty years.",
                ("Tullimonstrum", "Essexella", "Mazonomys")),
    Lagerstatte("Bear Gulch", -108.9, 47.0, "Laurentia", 324, 322,
                "conservat", "sea", "stratified tropical bay, seasonal laminae",
                "Fish with colour patterns and body outlines preserved, laid down in "
                "countable annual layers.",
                ("Falcatus", "Belantsea", "Harpagofututor")),

    # ---- Mesozoic --------------------------------------------------------
    Lagerstatte("Grès à Voltzia", 7.4, 48.6, "Armorica", 245, 243,
                "conservat", "mixed", "deltaic sandstone and mud lenses",
                "The best Early-Middle Triassic window: the recovery from the "
                "end-Permian, caught mid-rebuild.",
                ("Voltzia", "Antrimpos", "Triadobatrachus"), "moderate"),
    Lagerstatte("Monte San Giorgio", 8.92, 45.9, "Adria / Apulia", 242, 239,
                "conservat", "sea", "stagnant anoxic intraplatform basin",
                "Marine reptiles articulated and complete, some with embryos - the "
                "reference section for the Middle Triassic sea.",
                ("Ticinosuchus", "Ceresiosaurus", "Askeptosaurus")),
    Lagerstatte("Holzmaden (Posidonia Shale)", 9.5, 48.6, "Armorica", 183, 180,
                "conservat", "sea", "anoxic epicontinental sea floor, T-OAE",
                "Ichthyosaurs with SKIN OUTLINES and one caught giving birth. Deposited "
                "during the Toarcian oceanic anoxic event, which is what made the bottom "
                "water lethal enough to preserve them.",
                ("Stenopterygius", "Steneosaurus", "Seirocrinus")),
    Lagerstatte("Solnhofen", 11.0, 48.9, "Armorica", 151, 149,
                "conservat", "mixed", "hypersaline lagoons behind sponge reefs",
                "Archaeopteryx, with feathers. A lagoon so salty nothing lived on its "
                "floor, so nothing disturbed what fell in - which is also why its fauna "
                "is NOT a normal Tethyan assemblage and must never be replaced by one.",
                ("Archaeopteryx", "Compsognathus", "Pterodactylus", "Rhamphorhynchus")),
    Lagerstatte("Morrison Formation", -108.5, 39.7, "Laurentia", 157, 145,
                "concentration", "land", "seasonal floodplain and channel bone beds",
                "Not soft-tissue, but the densest sauropod record anywhere - the "
                "Late Jurassic terrestrial standard.",
                ("Allosaurus", "Stegosaurus", "Diplodocus", "Apatosaurus")),
    Lagerstatte("Yixian (Jehol Biota)", 121.1, 41.6, "North China", 125, 121,
                "conservat", "mixed", "volcanic ash falls into rift lakes",
                "Feathered dinosaurs, and enough of them to settle the bird question. "
                "Also melanosomes, so some of the colours are known.",
                ("Sinosauropteryx", "Microraptor", "Confuciusornis", "Repenomamus")),
    Lagerstatte("Santana / Crato", -39.5, -7.2, "Sao Francisco", 113, 108,
                "conservat", "mixed", "carbonate concretions in a restricted basin",
                "Three-dimensional pterosaurs with soft-tissue crests, and insects with "
                "colour preserved.",
                ("Tapejara", "Tupandactylus", "Dastilbe")),

    # ---- Cenozoic --------------------------------------------------------
    Lagerstatte("Fur Formation (Mo-clay)", 9.0, 56.8, "Baltica", 56, 54,
                "conservat", "mixed", "diatomite with ash layers",
                "Insects and birds either side of the PETM.",
                ("Lithornis", "fossil insects"), "moderate"),
    Lagerstatte("Green River Formation", -109.5, 41.5, "Laurentia", 53, 48,
                "both", "fresh", "long-lived stratified lakes, varved",
                "Millions of fish in countable annual laminae - the reference for lake "
                "deposition and for Eocene freshwater ecosystems.",
                ("Knightia", "Priscacara", "Icaronycteris")),
    Lagerstatte("Messel Pit", 8.75, 49.92, "Armorica", 48, 47,
                "conservat", "mixed", "anoxic maar lake in a volcanic crater",
                "Gut contents, stomach contents and fur - including Darwinius and a "
                "pregnant horse. A maar lake is a near-perfect trap: deep, stagnant and "
                "surrounded by forest.",
                ("Darwinius", "Propalaeotherium", "Eurotamandua")),
    Lagerstatte("Riversleigh", 138.7, -19.1, "Australia", 25, 0.05,
                "concentration", "land", "cave and pool limestones",
                "The whole Australian mammal radiation in one karst system, spanning "
                "25 Myr of an isolated continent.",
                ("Nimbadon", "Thylacoleo", "Obdurodon")),
    Lagerstatte("La Brea Tar Pits", -118.36, 34.06, "Laurentia", 0.05, 0.011,
                "concentration", "land", "asphalt seeps",
                "A predator trap, so the ratios are inverted - dire wolves and "
                "Smilodon vastly outnumber the herbivores that lured them in.",
                ("Smilodon", "Aenocyon dirus", "Panthera atrox")),
]

_BY_NAME = {s.name: s for s in SITES}


def by_name(name):
    return _BY_NAME.get(name)


def at(age, slack=0.0):
    """Sites whose window contains `age` Ma."""
    return [s for s in SITES if s.top - slack <= age <= s.base + slack]


def by_block(block):
    return [s for s in SITES if s.block == block]


def _selftest():
    import paleogeography as pg
    names = set()
    for s in SITES:
        assert s.name not in names, f"duplicate {s.name}"
        names.add(s.name)
        assert -180 <= s.lon <= 180 and -90 <= s.lat <= 90, f"{s.name} bad coord"
        assert s.base >= s.top, f"{s.name} base<top"
        assert s.kind in ("conservat", "concentration", "both"), s.name
        assert s.realm in ("sea", "land", "fresh", "mixed"), s.name
        # a track is carried by a CRATON, never by an assembly - naming
        # "Laurussia" here would have no plate to ride
        assert s.block in pg.BLOCKS, f"{s.name} names unknown block {s.block!r}"
        assert s.block not in pg.ASSEMBLIES, \
            f"{s.name} names the ASSEMBLY {s.block!r}; name the craton it sits on"
        # the block must exist when the site formed
        assert pg.exists(s.block, s.base), \
            f"{s.name}: {s.block} does not exist at {s.base} Ma"
    eras = {}
    for s in SITES:
        k = ("Precambrian" if s.base > 538.8 else "Palaeozoic" if s.base > 251.9
             else "Mesozoic" if s.base > 66 else "Cenozoic")
        eras[k] = eras.get(k, 0) + 1
    print(f"lagerstatten selftest OK: {len(SITES)} sites "
          + ", ".join(f"{v} {k}" for k, v in eras.items()))


if __name__ == "__main__":
    _selftest()
    print("\nsites through time:")
    for s in sorted(SITES, key=lambda s: -s.base):
        print(f"  {s.base:>6.1f}-{s.top:<6.1f} Ma  {s.name:<28} {s.block:<20} {s.realm}")
