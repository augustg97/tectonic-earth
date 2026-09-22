"""The Tonian and Cryogenian, block by block.

Seventeen Precambrian land labels shared one identical list -- amoebae, sponges,
two algal phyla and cyanobacteria -- because the registry's Precambrian entries
were global. The record is not: each craton's cover carries its own named
microfossil assemblage, and the eukaryotes of the Tonian have names.
"""
from _lib import E, T, write

# ------------------------------------------------------- the named eukaryotes
E("Trachyhystrichosphaera", "genus", "sea", "acritarch", 1000, 720, ["cosmo"],
  "A large spiny acritarch, the cyst of a Tonian eukaryote, found in shales from Siberia to Svalbard and Australia: the plankton of the world before the snowball.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Cerebrosphaera", "genus", "sea", "acritarch", 780, 740, ["cosmo"],
  "A wrinkled, brain-textured acritarch of the late Tonian, the zone fossil of the last thirty million years before the Sturtian ice.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Valeria", "genus", "sea", "acritarch", 1600, 700, ["cosmo"],
  "A large acritarch with concentric striations, one of the longest-lived Proterozoic eukaryotes, in shales for nine hundred million years.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Proterocladus", "genus", "sea", "seaweed", 1000, 800, ["as-e", "na-n", "eu"],
  "A branching green alga a few millimetres tall, from the Tonian of North China and Spitsbergen: the oldest known green seaweed, and green plants' first anchor to the sea floor.",
  hab=["shelf", "coast"], cls=("Ulvophyceae", "Cladophorales", ""))
E("Palaeovaucheria", "genus", "sea", "seaweed", 1030, 1000, ["as-n"],
  "A filamentous yellow-green alga of the Lakhanda Group of Siberia, close to the living Vaucheria; one of the first algae that can be placed in a modern group.",
  hab=["shelf", "coast"], cls=("Xanthophyceae", "", ""))
E("Longfengshania", "genus", "sea", "seaweed", 900, 800, ["as-e"],
  "A stalked, bulb-headed macroalga of the Tonian of North China, a few centimetres tall, held to the sea floor by a disc.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Tappania", "genus", "sea", "hyphae", 1600, 800, ["cosmo"],
  "A branching, budding microfossil of the Mesoproterozoic and Tonian, read by some as an early fungus, by others as an alga; either way, a complex cell a billion years before animals.",
  hab=["shelf"], cls=("", "", ""))
E("Melanocyrillium", "genus", "sea", "testate", 780, 740, ["na-w", "na-e", "au", "eu", "as-n"],
  "A vase-shaped microfossil of the Chuar Group of the Grand Canyon: the shell of a testate amoeba, and among the oldest fossils that can be tied to a living eukaryote group.",
  hab=["shelf"], cls=("", "Arcellinida", ""))
E("Siphonophycus", "genus", "sea", "cyano", 2000, 500, ["cosmo"],
  "Sheaths of a filamentous cyanobacterium, the mat-builder of Proterozoic tidal flats, preserved in chert on every craton.",
  hab=["coast", "shelf"], cls=("Cyanophyceae", "Oscillatoriales", ""))
E("Eoentophysalis", "genus", "sea", "cyano", 2000, 600, ["cosmo"],
  "A colonial coccoid cyanobacterium of Proterozoic cherts, all but identical to the living Entophysalis of tropical tidal flats.",
  hab=["coast", "shelf"], cls=("Cyanophyceae", "Chroococcales", ""))

# --------------------------------------------------------- block assemblages
E("Bitter Springs microbiota", "informal", "sea", "cyano", 830, 800, ["au"],
  "The chert microfossils of the Bitter Springs Formation of central Australia: cyanobacterial mats, colonial cells and eukaryotic algae preserved cell by cell, the standard picture of a Tonian shallow sea.",
  hab=["coast", "shelf"], rep="Siphonophycus", assemblage=True)
E("Chuar Group biota", "informal", "sea", "testate", 780, 740, ["na-w", "na-e"],
  "The late Tonian shales of the Grand Canyon: vase-shaped amoebae, spiny acritarchs and the first sign of predation on eukaryotes, in a sea over Laurentia thirty million years before the ice.",
  hab=["shelf"], rep="Melanocyrillium", assemblage=True)
E("Svanbergfjellet biota", "informal", "sea", "seaweed", 810, 750, ["eu", "gl"],
  "The Svanbergfjellet Formation of Spitsbergen: Proterocladus and other green algae, acritarchs and cyanobacterial mats on the Tonian margin of Baltica.",
  hab=["shelf", "coast"], rep="Proterocladus", assemblage=True)
E("Lakhanda biota", "informal", "sea", "seaweed", 1030, 1000, ["as-n"],
  "The Lakhanda Group of the Siberian platform, about a billion years old: filamentous algae, acritarchs and the sheaths of cyanobacteria in a shallow, quiet sea.",
  hab=["shelf", "coast"], rep="Palaeovaucheria", assemblage=True)
E("Liulaobei biota", "informal", "sea", "seaweed", 900, 800, ["as-e"],
  "Macroscopic algae of the Tonian of North China -- Longfengshania and its kin -- among the oldest seaweeds visible to the naked eye.",
  hab=["shelf", "coast"], rep="Longfengshania", assemblage=True)
E("Lantian biota", "informal", "sea", "seaweed", 602, 580, ["as-e"],
  "The Lantian Formation of Anhui: macroalgae and enigmatic soft-bodied forms in black shale just after the Marinoan ice, among the oldest large complex organisms.",
  hab=["shelf", "deep"], rep="Longfengshania", assemblage=True)
E("Vindhyan microfossils", "informal", "sea", "cyano", 1100, 950, ["in"],
  "Cherts and shales of the Vindhyan basin of central India: cyanobacterial mats, acritarchs and stromatolites, on a craton that would drift from the equator to the pole and back before anything walked on it.",
  hab=["coast", "shelf"], rep="Siphonophycus", assemblage=True)
E("Vazante stromatolites", "informal", "sea", "stromatolite", 1000, 900, ["sa-n", "sa-s"],
  "Stromatolite reefs of the Vazante Group on the Sao Francisco craton, columns and domes of a Tonian carbonate platform.",
  hab=["coast", "shelf"], rep="Stromatolites", assemblage=True)

# ------------------------------------------ the first Cambrian shelves (541-521)
# Before the trilobites every continent's card read "hyoliths, Bivalvia,
# Ostracoda, Hexactinellida". This is what the first ten million years of the
# Cambrian actually leave: small shelly fossils and traces.
E("Anabarites", "genus", "sea", "tubeworm", 541, 525, ["cosmo"],
  "A three-lobed tube a few millimetres long, among the first mineralised skeletons of the Cambrian and a zone fossil of its opening stage on every continent.",
  hab=["shelf", "coast"], cls=("", "Anabaritida", "Anabaritidae"))
E("Aldanella", "genus", "sea", "seasnail", 537, 521, ["cosmo"],
  "A tiny coiled shell of the earliest Cambrian, snail-like or a mollusc's cousin, found from Siberia to Newfoundland and marking the base of the Tommotian.",
  hab=["shelf", "coast"], cls=("", "", "Aldanellidae"))
E("Treptichnus pedum", "species", "sea", "strata", 541, 480, ["cosmo"],
  "The zigzag burrow that defines the base of the Cambrian: an animal probing the sediment from below, worldwide, at a level no body fossil can match.",
  hab=["shelf", "coast"])
E("Chancelloria", "genus", "sea", "sponge", 525, 500, ["cosmo"],
  "A bag-shaped animal armoured with star-shaped spicules, sessile on Cambrian sea floors, whose isolated stars are among the commonest small shelly fossils.",
  hab=["shelf"], cls=("", "", "Chancelloriidae"))
E("Microdictyon", "genus", "sea", "lobopod", 525, 505, ["cosmo"],
  "A lobopodian whose net-patterned armour plates were known as small shelly fossils for decades before the Chengjiang animal that wore them turned up.",
  hab=["shelf"], cls=("Lobopodia", "", ""))
write("x-precambrian-blocks.json")
