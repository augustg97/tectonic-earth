"""A deep-time taxon database with ATTRIBUTES and REGIONS.

The app's life_data.json carries names, ranks, realms and a short note. What it
does not carry is the attributes a card actually wants - how big, how it lived,
what it ate, where it lived and when precisely - and without those the biota
panels cannot say anything specific and cannot be checked.

This is that layer. Each entry is:

    Taxon(name, rank, clade, realm, first, last, size_m, habit, diet,
          provinces, biome, note, confidence)

`provinces` uses the vocabulary of paleobiogeography.py, so a taxon can be looked
up by province and an age, which is what turns per-label curation into a query:

    >>> [t.name for t in at(280, province='Gondwanan Province')][:3]
    ['Glossopteris', 'Gangamopteris', 'Vertebraria']

Sizes are typical adult maxima in METRES (length for animals, height for plants);
they are order-of-magnitude values chosen so a card can say "about the size of X"
without being wrong. `first`/`last` are Ma.

Run this file to validate and to write taxa.json next to it.
Dependency-free (stdlib only).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

__all__ = ["Taxon", "TAXA", "at", "by_name", "by_province", "by_realm", "stats"]

REALMS = ("sea", "land", "air", "fresh")
RANKS = ("species", "genus", "tribe", "family", "order", "subclass", "class",
         "phylum", "clade", "informal", "assemblage")


@dataclass(frozen=True)
class Taxon:
    name: str
    rank: str
    clade: str            # the group a reader would recognise: "seed fern", "sauropod"
    realm: str
    first: float          # Ma, first appearance
    last: float           # Ma, last appearance (0 = extant)
    size_m: float         # typical adult maximum, metres
    habit: str            # how it lived
    diet: str             # what it ate / how it fed
    provinces: tuple      # paleobiogeography province names, or ('cosmopolitan',)
    biome: str = ""       # biome_model zone or name, where meaningful
    note: str = ""
    confidence: str = "good"

    @property
    def extant(self) -> bool:
        return self.last <= 0.0

    def alive_at(self, age: float) -> bool:
        return self.last <= age <= self.first


# ---------------------------------------------------------------------------
# The database. Grouped by interval so gaps are visible.
# (name, rank, clade, realm, first, last, size_m, habit, diet, provinces, biome, note)
# ---------------------------------------------------------------------------

_ROWS = [
    # ================= Tonian - Cryogenian (1000-635 Ma) =================
    ("Stromatolite", "informal", "cyanobacterial buildup", "sea", 3500, 0, 3.0,
     "laminated microbial buildup on warm shelves", "photosynthesis",
     ("cosmopolitan",), "", "The dominant reef of the first three billion years. Declines "
     "sharply in the Cambrian as grazing and burrowing begin; survives today only in "
     "refugia like Hamelin Pool."),
    ("Bangiomorpha", "genus", "red alga", "sea", 1050, 720, 0.002,
     "filamentous, attached to shallow substrate", "photosynthesis",
     ("cosmopolitan",), "", "Among the oldest fossils showing sexual reproduction and "
     "complex multicellularity."),
    ("Acritarchs", "informal", "organic-walled microfossils", "sea", 1800, 0, 0.0002,
     "planktonic", "photosynthesis / heterotrophy", ("cosmopolitan",), "",
     "Mostly the cysts of algae; the workhorse biostratigraphic fossil of the "
     "Proterozoic and early Palaeozoic."),
    ("Cryoconite communities", "assemblage", "microbial", "fresh", 720, 635, 0.0001,
     "meltponds on the surface of snowball ice", "photosynthesis",
     ("cosmopolitan",), "ice sheet",
     "The best candidate refugium for photosynthetic life through the Sturtian and "
     "Marinoan glaciations.", "moderate"),

    # ================= Ediacaran (635-538.8 Ma) =================
    ("Charnia", "genus", "rangeomorph", "sea", 575, 550, 1.0,
     "sessile frond anchored by a holdfast, in the deep sea below the photic zone",
     "osmotrophy or suspension feeding", ("Avalon assemblage",), "",
     "The first complex macrofossil recognised from rocks then thought to be Precambrian."),
    ("Fractofusus", "genus", "rangeomorph", "sea", 575, 560, 0.4,
     "reclining on the sea floor, deep water", "osmotrophy",
     ("Avalon assemblage",), "", "Shows evidence of reproduction by stolons."),
    ("Dickinsonia", "genus", "dickinsoniomorph", "sea", 560, 550, 1.4,
     "flat on a microbial mat, possibly mobile", "external digestion of the mat beneath it",
     ("White Sea assemblage",), "",
     "Cholesteroid biomarkers argue it was an animal. Up to 1.4 m and a few mm thick."),
    ("Kimberella", "genus", "kimberellomorph", "sea", 555, 550, 0.05,
     "mobile bottom-dweller", "grazing with a radula-like apparatus",
     ("White Sea assemblage",), "",
     "The strongest Ediacaran candidate for a bilaterian, possibly mollusc-like; leaves "
     "scratch traces beside its body fossils."),
    ("Yorgia", "genus", "proarticulatan", "sea", 558, 550, 0.25,
     "mobile grazer on microbial mats", "ciliary feeding",
     ("White Sea assemblage",), "", "Found with a trail of its own feeding impressions."),
    ("Tribrachidium", "genus", "trilobozoan", "sea", 555, 550, 0.04,
     "sessile, three-rayed symmetry", "suspension feeding",
     ("White Sea assemblage",), "", "A body plan with no counterpart in any living phylum."),
    ("Ernietta", "genus", "erniettomorph", "sea", 548, 539, 0.1,
     "partly buried, sack-like, in shifting sand", "suspension feeding",
     ("Nama assemblage",), "", ""),
    ("Cloudina", "genus", "tubular biomineraliser", "sea", 550, 539, 0.04,
     "gregarious tube-dweller, reef-forming", "suspension feeding",
     ("Nama assemblage",), "",
     "One of the FIRST mineralised skeletons, and it carries the first evidence of "
     "predation: drill holes made by something that hunted it."),
    ("Namacalathus", "genus", "goblet-shaped biomineraliser", "sea", 548, 539, 0.03,
     "stalked, attached to microbial reefs", "suspension feeding",
     ("Nama assemblage",), "", ""),

    # ================= Cambrian (538.8-485.4 Ma) =================
    ("Anomalocaris", "genus", "radiodont", "sea", 520, 500, 1.0,
     "active nektonic swimmer with lateral flaps", "predator",
     ("Olenellid Province", "Redlichiid Province"), "",
     "The largest Cambrian animal; compound eyes with tens of thousands of lenses."),
    ("Opabinia", "genus", "stem-arthropod", "sea", 508, 505, 0.07,
     "nektobenthic", "predator, using a single frontal grasping proboscis",
     ("Olenellid Province",), "", "Five eyes. Burgess Shale."),
    ("Hallucigenia", "genus", "lobopodian", "sea", 518, 505, 0.035,
     "benthic walker", "possibly scavenging on sponges",
     ("Olenellid Province", "Redlichiid Province"), "",
     "Reconstructed upside-down and back-to-front for decades."),
    ("Wiwaxia", "genus", "stem-mollusc / annelid", "sea", 518, 505, 0.05,
     "benthic, armoured with sclerites and spines", "grazing",
     ("Olenellid Province", "Redlichiid Province"), "", ""),
    ("Marrella", "genus", "marrellomorph arthropod", "sea", 515, 505, 0.02,
     "swimming and crawling near the bottom", "deposit feeding",
     ("Olenellid Province",), "", "The most abundant animal in the Burgess Shale."),
    ("Olenellus", "genus", "olenellid trilobite", "sea", 521, 509, 0.1,
     "benthic", "deposit feeding / predation",
     ("Olenellid Province",), "", "Index fossil of Laurentia, Baltica and Siberia."),
    ("Redlichia", "genus", "redlichiid trilobite", "sea", 521, 509, 0.25,
     "benthic", "deposit feeding / predation",
     ("Redlichiid Province",), "", "Index fossil of Gondwana and its margins."),
    ("Myllokunmingia", "genus", "stem-vertebrate", "sea", 518, 515, 0.028,
     "nektonic", "filter feeding", ("Redlichiid Province",), "",
     "Among the earliest known craniates, from Chengjiang."),
    ("Pikaia", "genus", "cephalochordate-grade chordate", "sea", 508, 505, 0.04,
     "swimming", "filter feeding", ("Olenellid Province",), "", ""),
    ("Archaeocyaths", "class", "sponge-grade reef builder", "sea", 525, 510, 0.15,
     "sessile, cup-shaped, reef-forming on tropical shelves", "suspension feeding",
     ("Olenellid Province", "Redlichiid Province"), "",
     "The FIRST animal reef builders. Extinct by the mid-Cambrian, leaving reef building "
     "to microbes again until the Ordovician."),
    ("Small shelly fauna", "assemblage", "mixed early biomineralisers", "sea", 541, 521,
     0.002, "benthic, mostly millimetric", "various",
     ("cosmopolitan",), "", "Spines, plates, tubes and caps 1-2 mm long; the bridge "
     "between the Ediacaran and the Lagerstatten."),

    # ================= Ordovician (485.4-443.8 Ma) =================
    ("Cameroceras", "genus", "nautiloid cephalopod", "sea", 470, 440, 6.0,
     "nektonic, with a long straight conical shell", "apex predator",
     ("Laurentian (North American) Province", "Baltic Province"), "",
     "Among the largest animals of the early Palaeozoic; the classic figure of ~9 m is "
     "probably an overestimate.", "moderate"),
    ("Isotelus", "genus", "asaphid trilobite", "sea", 460, 445, 0.7,
     "benthic burrower", "predation and deposit feeding",
     ("Laurentian (North American) Province",), "", "One of the largest trilobites."),
    ("Didymograptus", "genus", "graptolite", "sea", 478, 458, 0.05,
     "planktonic colony", "suspension feeding", ("cosmopolitan",), "",
     "Graptolites are the definitive Ordovician-Silurian biostratigraphic tool because "
     "they were planktonic and therefore near-global."),
    ("Halysites", "genus", "tabulate coral", "sea", 460, 419, 0.3,
     "colonial reef builder, chain-like", "suspension feeding",
     ("Laurentian (North American) Province",), "",
     "Part of the stromatoporoid-tabulate-rugose reef that replaces the Cambrian "
     "archaeocyath and microbial mound."),
    ("Receptaculites", "genus", "uncertain (alga or sponge)", "sea", 470, 360, 0.3,
     "sessile on carbonate shelves", "unknown",
     ("Laurentian (North American) Province",), "", ""),
    ("Conodonts", "class", "early vertebrate", "sea", 520, 201, 0.04,
     "nektonic, eel-like", "predation with phosphatic tooth elements",
     ("cosmopolitan",), "", "Known for a century from their teeth alone; the animal was "
     "found only in 1983."),

    # ================= Silurian - Devonian (443.8-358.9 Ma) =================
    ("Cooksonia", "genus", "early vascular plant", "land", 433, 393, 0.06,
     "tiny dichotomising axes in damp lowlands", "photosynthesis",
     ("Early vascular flora",), "wetland",
     "Among the first vascular plants; a few centimetres tall, with terminal sporangia."),
    ("Baragwanathia", "genus", "lycopsid", "land", 425, 393, 0.3,
     "creeping and upright shoots with true microphylls", "photosynthesis",
     ("Early vascular flora",), "wetland", ""),
    ("Aglaophyton", "genus", "rhyniophyte-grade plant", "land", 411, 407, 0.18,
     "rootless, in a hot-spring wetland", "photosynthesis",
     ("Early vascular flora",), "wetland",
     "From the Rhynie chert, and the earliest clear evidence of arbuscular mycorrhizal "
     "symbiosis - land plants have always been partly fungal."),
    ("Prototaxites", "genus", "probable fungus", "land", 420, 370, 8.0,
     "free-standing column, the tallest organism of its day", "saprotrophy / decay",
     ("Archaeopteris forest flora",), "", "No modern analogue. For 130 Myr the largest "
     "organism on land was probably a fungus."),
    ("Archaeopteris", "genus", "progymnosperm tree", "land", 385, 359, 30.0,
     "the first true forest tree: real wood, roots to ~1 m, a spreading crown",
     "photosynthesis", ("Archaeopteris forest flora",), "temperate forest",
     "Deep rooting and canopy shade begin the silicate-weathering and organic-burial "
     "drawdown of CO2 that ends in the Late Palaeozoic Ice Age."),
    ("Wattieza", "genus", "cladoxylopsid tree", "land", 390, 380, 8.0,
     "palm-like crown of frond-like branches", "photosynthesis",
     ("Archaeopteris forest flora",), "", "Earliest known tree-form, from Gilboa."),
    ("Elkinsia", "genus", "seed fern", "land", 372, 359, 1.0,
     "small woody plant", "photosynthesis", ("Archaeopteris forest flora",), "",
     "Among the earliest seed plants - the innovation that frees reproduction from "
     "standing water."),
    ("Dunkleosteus", "genus", "arthrodire placoderm", "sea", 382, 358, 4.0,
     "nektonic apex predator with bladed jaw plates instead of teeth", "apex predator",
     ("Eastern Americas Realm", "Old World Realm"), "",
     "One of the highest bite forces measured for any fish."),
    ("Tiktaalik", "genus", "elpistostegalian stem-tetrapod", "fresh", 383, 375, 2.7,
     "shallow-water predator with a mobile neck and weight-bearing fins", "predator",
     ("Eastern Americas Realm",), "wetland",
     "Found by predicting the ROCK first: Devonian, shallow-marine to freshwater, "
     "then searching Ellesmere Island."),
    ("Ichthyostega", "genus", "early tetrapod", "fresh", 374, 359, 1.5,
     "amphibious, with limbs but a fish-like tail", "predator",
     ("Old World Realm",), "wetland", "Seven toes."),
    ("Eurypterids", "order", "sea scorpion", "sea", 467, 252, 2.5,
     "nektobenthic, some in brackish and fresh water", "predator",
     ("cosmopolitan",), "", "Jaekelopterus at ~2.5 m is the largest arthropod that "
     "ever lived, rivalled only by Arthropleura."),
    ("Stringocephalus", "genus", "terebratulid brachiopod", "sea", 390, 383, 0.1,
     "benthic, attached", "suspension feeding", ("Old World Realm",), "",
     "A Middle Devonian index fossil of the Old World Realm."),
    ("Australocoelia", "genus", "brachiopod", "sea", 419, 393, 0.02,
     "benthic, cold-water shelf", "suspension feeding",
     ("Malvinokaffric Realm",), "", "Diagnostic of the cold high-latitude Gondwanan realm."),

    # ================= Carboniferous (358.9-298.9 Ma) =================
    ("Lepidodendron", "genus", "arborescent lycopsid", "land", 359, 299, 50.0,
     "unbranched pole with a crown, DETERMINATE growth - grew, reproduced once, died",
     "photosynthesis", ("Euramerican Province",), "wetland",
     ">50 m tall and 2 m across at the base, with a shallow stigmarian rooting system. "
     "This is the coal."),
    ("Sigillaria", "genus", "arborescent lycopsid", "land", 383, 254, 30.0,
     "tall, usually unbranched, in coal swamps", "photosynthesis",
     ("Euramerican Province",), "wetland", ""),
    ("Calamites", "genus", "arborescent horsetail", "land", 359, 299, 12.0,
     "clonal thickets on levees and channel margins", "photosynthesis",
     ("Euramerican Province",), "wetland",
     ">10 m tall, with a unifacial vascular cambium - it made wood in a way no living "
     "plant does."),
    ("Medullosa", "genus", "medullosalean seed fern", "land", 359, 299, 10.0,
     "scrambling or self-supporting, with very large fronds", "photosynthesis",
     ("Euramerican Province",), "", "Produced the largest pollen grains known."),
    ("Psaronius", "genus", "marattialean tree fern", "land", 323, 252, 10.0,
     "tree fern with a mantle of adventitious roots", "photosynthesis",
     ("Euramerican Province", "Cathaysian Province"), "",
     "Takes over the tropical wetlands after the ~305 Ma rainforest collapse."),
    ("Cordaites", "genus", "cordaitalean gymnosperm", "land", 359, 252, 30.0,
     "tree with strap-shaped leaves; coastal and upland", "photosynthesis",
     ("Euramerican Province", "Angaran Province"), "temperate forest",
     "The dominant tree of the cool Angaran province, and a relative of conifers."),
    ("Arthropleura", "genus", "giant myriapod", "land", 346, 290, 2.6,
     "ground-dwelling", "detritivore / herbivore",
     ("Euramerican Province",), "",
     "The largest known land arthropod. Traditionally tied to high O2 and the coal "
     "forest, but recent work finds it after the collapse and probably "
     "forest-independent.", "moderate"),
    ("Meganeura", "genus", "griffinfly", "air", 315, 299, 0.7,
     "aerial predator, ~70 cm wingspan", "predator on other insects",
     ("Euramerican Province",), "", "Same caveat as Arthropleura on the oxygen story."),
    ("Hylonomus", "genus", "early reptile", "land", 318, 315, 0.25,
     "insectivore living in hollow lycopsid stumps", "insectivore",
     ("Euramerican Province",), "",
     "Among the earliest amniotes - the group that could reproduce away from water and "
     "so inherited the drying world."),
    ("Eurydesma", "genus", "bivalve", "sea", 299, 272, 0.12,
     "cold-water shelf, often in glacial dropstone facies", "suspension feeding",
     ("Gondwanan (Austral) Realm",), "",
     "The diagnostic cold-water fauna of the Late Palaeozoic Ice Age in Gondwana."),
    ("Fusulinids", "family", "large benthic foraminifera", "sea", 340, 252, 0.06,
     "benthic on warm carbonate shelves", "symbiont-bearing heterotrophy",
     ("Tethyan Realm",), "",
     "Grain-of-wheat shaped and up to 6 cm. Their PRESENCE marks the warm Tethyan realm "
     "and their ABSENCE marks the cool Gondwanan and Boreal ones."),

    # ================= Permian (298.9-251.9 Ma) =================
    ("Glossopteris", "genus", "glossopterid seed fern", "land", 299, 252, 30.0,
     "woody tree in very wet soils, like a modern bald cypress; conical, widely spaced "
     "crowns to exploit low-angle polar light", "photosynthesis",
     ("Gondwanan Province",), "wetland",
     "Trunk to 80 cm, tongue-shaped leaves 2-30 cm with reticulate venation. Antarctic "
     "wood shows broad growth rings and an abrupt autumn shutdown taking as little as a "
     "month. Its distribution across five now-separated continents was Suess's evidence "
     "for Gondwana. Died out BEFORE 252.3 Ma, ~350 kyr ahead of the marine extinction."),
    ("Gangamopteris", "genus", "glossopterid seed fern", "land", 299, 260, 15.0,
     "as Glossopteris but with non-midribbed leaves", "photosynthesis",
     ("Gondwanan Province",), "wetland", ""),
    ("Vertebraria", "genus", "glossopterid root", "land", 299, 252, 0.0,
     "septate, air-filled roots in waterlogged soil", "-",
     ("Gondwanan Province",), "wetland",
     "The root of Glossopteris, named separately before the connection was known; its "
     "internal air channels are a waterlogging adaptation."),
    ("Gigantopteris", "genus", "gigantopterid seed plant", "land", 280, 252, 3.0,
     "climbing or scrambling, with large net-veined leaves", "photosynthesis",
     ("Cathaysian Province",), "tropical rainforest",
     "The marker of the everwet Cathaysian province, whose rainforest survives the "
     "Euramerican collapse and persists to the end-Permian."),
    ("Rufloria", "genus", "cordaitalean leaf", "land", 299, 252, 25.0,
     "deciduous tree with strong growth rings", "photosynthesis",
     ("Angaran Province",), "boreal forest",
     "The characteristic Angaran leaf - cool temperate, seasonal, deciduous."),
    ("Dimetrodon", "genus", "sphenacodontid synapsid", "land", 295, 272, 4.6,
     "terrestrial apex predator with a tall neural-spine sail", "carnivore",
     ("Euramerican Province",), "",
     "Not a dinosaur, and closer to us than to any reptile."),
    ("Inostrancevia", "genus", "gorgonopsian therapsid", "land", 260, 252, 3.5,
     "terrestrial apex predator with sabre canines", "carnivore",
     ("Angaran Province",), "", ""),
    ("Lystrosaurus", "genus", "dicynodont therapsid", "land", 255, 247, 1.0,
     "burrowing herbivore", "herbivore",
     ("cosmopolitan",), "",
     "The type case of post-extinction cosmopolitanism: after the end-Permian it was "
     "briefly a large fraction of all land vertebrates, on every continent."),
    ("Helicoprion", "genus", "eugeneodont chondrichthyan", "sea", 290, 250, 4.0,
     "nektonic, with a spiral tooth whorl in the lower jaw", "predator on soft prey",
     ("Tethyan Realm", "Boreal Realm"), "", ""),

    # ================= Triassic (251.9-201.4 Ma) =================
    ("Dicroidium", "genus", "corystosperm seed fern", "land", 252, 201, 10.0,
     "forked-frond tree and shrub", "photosynthesis",
     ("Dicroidium Flora",), "temperate forest",
     "Replaces Glossopteris across Gondwana after the end-Permian."),
    ("Pleuromeia", "genus", "lycopsid", "land", 252, 240, 2.0,
     "unbranched, in disturbed coastal ground", "photosynthesis",
     ("Dicroidium Flora", "Northern Triassic conifer flora"), "",
     "A disaster taxon: it carpets the early Triassic when the forests are gone."),
    ("Cynognathus", "genus", "cynodont therapsid", "land", 247, 237, 1.2,
     "terrestrial predator", "carnivore", ("cosmopolitan",), "",
     "Its Gondwana-wide distribution was classic evidence for continental drift."),
    ("Shonisaurus", "genus", "ichthyosaur", "sea", 237, 210, 15.0,
     "pelagic", "predator on cephalopods and fish", ("Tethyan Realm",), "", ""),
    ("Eoraptor", "genus", "early dinosaur", "land", 231, 228, 1.5,
     "bipedal, cursorial", "omnivore", ("cosmopolitan",), "",
     "From the Ischigualasto Formation, Argentina - near the base of the dinosaur radiation."),
    ("Coelophysis", "genus", "coelophysoid theropod", "land", 215, 196, 3.0,
     "gracile bipedal predator, gregarious", "carnivore", ("cosmopolitan",), "", ""),
    ("Placerias", "genus", "dicynodont", "land", 221, 205, 3.5,
     "heavy-bodied browser", "herbivore", ("cosmopolitan",), "", ""),

    # ================= Jurassic (201.4-143.1 Ma) =================
    ("Araucaria", "genus", "araucarian conifer", "land", 200, 0, 60.0,
     "emergent canopy tree", "photosynthesis",
     ("Cosmopolitan Jurassic gymnosperm flora",), "temperate rainforest",
     "Still living - monkey puzzle and Norfolk Island pine are the same genus that "
     "dominated Jurassic forests."),
    ("Williamsonia", "genus", "bennettitalean", "land", 200, 90, 3.0,
     "stout trunk with a crown of pinnate leaves and flower-like cones", "photosynthesis",
     ("Cosmopolitan Jurassic gymnosperm flora",), "",
     "Bennettitales look like cycads and are not; their bisexual cones long confused the "
     "search for the origin of flowers."),
    ("Ginkgo", "genus", "ginkgoalean", "land", 200, 0, 35.0,
     "deciduous tree", "photosynthesis",
     ("Cosmopolitan Jurassic gymnosperm flora",), "temperate forest",
     "One species survives; the genus was near-global in the Jurassic and Cretaceous."),
    ("Brachiosaurus", "genus", "sauropod dinosaur", "land", 154, 150, 22.0,
     "high browser with forelimbs longer than hindlimbs", "herbivore",
     ("cosmopolitan",), "seasonal tropical forest", ""),
    ("Diplodocus", "genus", "diplodocid sauropod", "land", 154, 150, 26.0,
     "low-to-mid browser with a whip tail", "herbivore", ("cosmopolitan",), "", ""),
    ("Allosaurus", "genus", "allosauroid theropod", "land", 155, 145, 9.0,
     "terrestrial apex predator", "carnivore", ("cosmopolitan",), "", ""),
    ("Stegosaurus", "genus", "thyreophoran dinosaur", "land", 155, 145, 9.0,
     "low browser with dorsal plates and a spiked tail", "herbivore",
     ("cosmopolitan",), "", ""),
    ("Archaeopteryx", "genus", "avialan dinosaur", "air", 150, 148, 0.5,
     "arboreal or short-flight glider", "carnivore / insectivore",
     ("Solnhofen Lagoon",), "",
     "From the Solnhofen lagoon, a hypersaline lagoonal Lagerstatte whose fauna is a "
     "mixture of marine, terrestrial and aerial - which is why it should not be "
     "realm-locked in a biota panel."),
    ("Liopleurodon", "genus", "pliosaurid plesiosaur", "sea", 166, 155, 7.0,
     "pelagic pursuit predator", "apex predator", ("Boreal Realm", "Tethyan Realm"), "", ""),
    ("Buchia", "genus", "bivalve", "sea", 160, 130, 0.08,
     "cool-water shelf, gregarious", "suspension feeding",
     ("Boreal Realm",), "", "A diagnostic Boreal-realm marker."),

    # ================= Cretaceous (143.1-66 Ma) =================
    ("Archaefructus", "genus", "early angiosperm", "fresh", 125, 122, 0.5,
     "aquatic herb", "photosynthesis", ("Early angiosperm flora",), "wetland",
     "Among the oldest flowering plants with preserved reproductive structures, from the "
     "Yixian Formation."),
    ("Rudists", "order", "reef-building bivalve", "sea", 155, 66, 1.0,
     "sessile, conical, gregarious - a bivalve behaving like a coral",
     "suspension feeding", ("Tethyan Realm",), "",
     "They displace corals as the main tropical reef builder for much of the Cretaceous, "
     "and die at the K-Pg."),
    ("Tyrannosaurus", "genus", "tyrannosaurid theropod", "land", 68, 66, 12.0,
     "terrestrial apex predator", "carnivore", ("Nearctic",), "", ""),
    ("Triceratops", "genus", "ceratopsid dinosaur", "land", 68, 66, 9.0,
     "low browser with a frill and three horns", "herbivore", ("Nearctic",), "", ""),
    ("Quetzalcoatlus", "genus", "azhdarchid pterosaur", "air", 68, 66, 11.0,
     "terrestrial stalker and soaring flier, ~11 m wingspan", "carnivore",
     ("Nearctic",), "", "Among the largest flying animals that ever lived."),
    ("Mosasaurus", "genus", "mosasaur", "sea", 82, 66, 13.0,
     "pelagic and shelf predator", "apex predator",
     ("Boreal Realm", "Tethyan Realm", "Western Interior Seaway"), "", ""),
    ("Hesperornis", "genus", "hesperornithean bird", "sea", 83, 78, 1.8,
     "flightless foot-propelled diver, toothed", "piscivore",
     ("Western Interior Seaway", "Hudson Seaway"), "",
     "A bird, so it is realm 'air' by clade and 'sea' by ecology - a case where a strict "
     "realm lock produces the wrong answer."),
    ("Ammonites", "subclass", "ammonoid cephalopod", "sea", 409, 66, 0.6,
     "nektonic, coiled external shell", "predator / scavenger",
     ("cosmopolitan",), "",
     "The single most useful Mesozoic biostratigraphic group; gone at the K-Pg while "
     "nautiloids survived."),
    ("Coccolithophores", "class", "calcareous nannoplankton", "sea", 220, 0, 0.00002,
     "photic-zone plankton with calcite plates", "photosynthesis",
     ("cosmopolitan",), "",
     "From ~201 Ma they rain carbonate onto the DEEP sea floor for the first time, "
     "moving the carbonate factory off the shelf and giving the modern ocean its clear "
     "blue colour."),

    # ================= Paleogene (66-23 Ma) =================
    ("Metasequoia", "genus", "deciduous conifer", "land", 90, 0, 45.0,
     "deciduous canopy tree, forming high-latitude forests", "photosynthesis",
     ("Nearctic", "Palearctic"), "boreal forest",
     "Polar broadleaf-deciduous forest grew inside the Arctic Circle in the Eocene; "
     "Metasequoia is its signature. Described as a fossil in 1941 and found alive in 1944."),
    ("Nothofagus", "genus", "southern beech", "land", 80, 0, 40.0,
     "canopy tree of cool temperate rainforest", "photosynthesis",
     ("Neotropical", "Australasian", "Antarctic"), "temperate rainforest",
     "Its distribution across South America, New Zealand, Australia and (fossil) "
     "Antarctica is a Gondwanan vicariance pattern."),
    ("Titanoboa", "genus", "boid snake", "land", 60, 58, 13.0,
     "semi-aquatic ambush predator", "carnivore", ("Neotropical",), "wetland",
     "Its size implies a mean annual temperature above ~30 C in Palaeocene Colombia."),
    ("Basilosaurus", "genus", "archaeocete whale", "sea", 41, 34, 18.0,
     "fully aquatic, serpentine, with vestigial hindlimbs", "apex predator",
     ("Tropical",), "", "A whale still carrying the legs of its land ancestry."),
    ("Uintatherium", "genus", "dinoceratan", "land", 45, 37, 4.0,
     "heavy browser with six blunt horns", "herbivore", ("Nearctic", "Palearctic"), "", ""),
    ("Nummulites", "genus", "larger benthic foraminifera", "sea", 56, 34, 0.1,
     "benthic on warm carbonate shelves", "symbiont-bearing heterotrophy",
     ("Tropical",), "", "Coin-sized single cells; the limestone of the Egyptian pyramids "
     "is largely made of them."),

    # ================= Neogene - Quaternary (23-0 Ma) =================
    ("Andropogoneae", "tribe", "C4 grasses", "land", 25, 0, 3.0,
     "fire-adapted tussock and sward grasses", "photosynthesis (C4)",
     ("Afrotropical", "Neotropical", "Australasian"), "savanna",
     "C4 grasslands expand in the late Miocene (~8 Ma) under low CO2 and seasonal "
     "aridity - the biome that makes the modern savanna fauna possible."),
    ("Otodus megalodon", "species", "otodontid shark", "sea", 20, 3.6, 16.0,
     "pelagic macropredator", "apex predator on marine mammals",
     ("Tropical", "North temperate"), "", ""),
    ("Proconsul", "genus", "early ape", "land", 23, 17, 1.0,
     "arboreal quadruped", "frugivore", ("Afrotropical",), "seasonal tropical forest",
     "ENDEMIC TO AFRICA. Its appearance on an Australian-sector card was the bug that "
     "exposed the endemism filter not reaching submerged and island labels."),
    ("Megatherium", "genus", "ground sloth", "land", 2.0, 0.011, 6.0,
     "terrestrial browser, able to rear on its hindlimbs", "herbivore",
     ("Neotropical", "Nearctic"), "",
     "A South American native that invaded North America during the Great American "
     "Interchange, in one of at least eight ground-sloth lineages to do so."),
    ("Phorusrhacids", "family", "terror bird", "land", 27, 1.8, 3.0,
     "flightless cursorial predator", "carnivore", ("Neotropical",), "temperate grassland",
     "Apex predators of isolated South America; possibly island-hopped north by ~5 Ma."),
    ("Toxodon", "genus", "notoungulate", "land", 3.0, 0.012, 2.7,
     "heavy grazer, rhinoceros-like in build but unrelated", "herbivore",
     ("Neotropical",), "temperate grassland",
     "One of the endemic South American ungulate orders that the interchange extinguished."),
    ("Mammuthus primigenius", "species", "woolly mammoth", "land", 0.4, 0.004, 3.4,
     "cold-adapted grazer of the mammoth steppe", "grazer",
     ("Palearctic", "Nearctic"), "temperate grassland",
     "The mammoth steppe - cold, dry, productive grassland - is a biome with no modern "
     "equivalent, and it vanished with the ice."),
    ("Homo sapiens", "species", "hominin", "land", 0.3, 0, 1.7,
     "generalist, tool-using, globally dispersed", "omnivore",
     ("cosmopolitan",), "", "Cited as pivotal in the late Pleistocene megafaunal "
     "extinctions on every continent it reached."),
    ("Rhizophora", "genus", "mangrove", "land", 60, 0, 30.0,
     "intertidal tree on stilt roots, salt-excluding", "photosynthesis",
     ("Tropical",), "wetland",
     "Mangrove is the one forest that shows up as coastline rather than as interior "
     "vegetation, and it is a Cenozoic feature."),
    ("Diatoms", "class", "siliceous phytoplankton", "sea", 190, 0, 0.0002,
     "photic-zone plankton with silica frustules", "photosynthesis",
     ("cosmopolitan",), "",
     "Radiate strongly from the Cretaceous and dominate high-latitude and upwelling "
     "productivity in the Cenozoic; they draw silica down and are why sponges and "
     "radiolarians build thinner skeletons than they used to."),
]


TAXA = tuple(
    Taxon(name=r[0], rank=r[1], clade=r[2], realm=r[3], first=float(r[4]),
          last=float(r[5]), size_m=float(r[6]), habit=r[7], diet=r[8],
          provinces=tuple(r[9]), biome=r[10], note=r[11],
          confidence=(r[12] if len(r) > 12 else "good"))
    for r in _ROWS
)


# ---------------------------------------------------------------------------
# queries
# ---------------------------------------------------------------------------

def at(age: float, realm: Optional[str] = None,
       province: Optional[str] = None) -> list:
    """Taxa alive at `age` Ma, optionally filtered by realm and/or province.

    A taxon tagged 'cosmopolitan' matches any province."""
    out = [t for t in TAXA if t.alive_at(age)]
    if realm:
        out = [t for t in out if t.realm == realm]
    if province:
        out = [t for t in out
               if province in t.provinces or "cosmopolitan" in t.provinces]
    return sorted(out, key=lambda t: -t.size_m)


def by_name(name: str) -> Optional[Taxon]:
    for t in TAXA:
        if t.name.lower() == name.lower():
            return t
    return None


def by_province(province: str) -> list:
    return [t for t in TAXA if province in t.provinces]


def by_realm(realm: str) -> list:
    return [t for t in TAXA if t.realm == realm]


def stats() -> dict:
    realms = {}
    for t in TAXA:
        realms[t.realm] = realms.get(t.realm, 0) + 1
    provs = set()
    for t in TAXA:
        provs.update(t.provinces)
    return dict(n=len(TAXA), realms=realms, provinces=len(provs),
                oldest=max(t.first for t in TAXA),
                extant=sum(1 for t in TAXA if t.extant))


def to_json(path: Optional[str] = None) -> str:
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "taxa.json")
    rows = [asdict(t) for t in TAXA]
    for r in rows:
        r["provinces"] = list(r["provinces"])
    with open(path, "w") as fh:
        json.dump({"schema": 1,
                   "note": "Deep Research taxon database. Sizes are typical adult "
                           "maxima in metres; ages in Ma.",
                   "taxa": rows}, fh, indent=1)
    return path


# ---------------------------------------------------------------------------

def _selftest() -> None:
    names = set()
    for t in TAXA:
        assert t.realm in REALMS, f"{t.name}: bad realm {t.realm}"
        assert t.rank in RANKS, f"{t.name}: bad rank {t.rank}"
        assert t.first > t.last, f"{t.name}: first <= last"
        assert t.first <= 4000, f"{t.name}: impossible first appearance"
        assert t.size_m >= 0, t.name
        assert t.provinces, f"{t.name}: no provinces"
        assert t.name not in names, f"duplicate {t.name}"
        names.add(t.name)
        assert t.habit and t.diet, f"{t.name}: missing habit/diet"
    # no land taxon before land plants except the deliberate microbial ones
    for t in TAXA:
        if t.realm == "land" and t.first > 470:
            raise AssertionError(f"{t.name} is on land at {t.first} Ma, before land plants")
    # queries behave
    g = by_name("Glossopteris")
    assert g and g.alive_at(280) and not g.alive_at(300)
    gond = [t.name for t in at(280, realm="land", province="Gondwanan Province")]
    assert "Glossopteris" in gond and "Gigantopteris" not in gond
    cath = [t.name for t in at(280, realm="land", province="Cathaysian Province")]
    assert "Gigantopteris" in cath and "Glossopteris" not in cath
    assert at(1000), "nothing alive at 1000 Ma"
    s = stats()
    print(f"taxa_db selftest OK: {s['n']} taxa, realms {s['realms']}, "
          f"{s['provinces']} distinct province tags, {s['extant']} extant")


if __name__ == "__main__":
    _selftest()
    p = to_json()
    print("wrote", p)
    print()
    for age in (560, 500, 380, 305, 270, 150, 66, 10):
        rows = at(age)
        big = rows[0] if rows else None
        print(f"{age:>4} Ma  {len(rows):>3} taxa in the database"
              + (f"; largest {big.name} ({big.size_m:g} m, {big.clade})" if big else ""))
