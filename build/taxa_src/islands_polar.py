"""Ocean islands and the poles: the places "cosmopolitan" does not reach.

biota.at_home stops a land taxon with a world-wide range at the edge of the
continents, and stops everything unnamed at the Antarctic ice. What is left to
show on Kerguelen, Mauritius, the Seychelles, Jan Mayen and post-Eocene
Antarctica is only what somebody has said lives there -- this file.

Ocean-island land life is ranged on its OCEAN's code ("ind", "sou", "arc"),
the only address a mid-ocean island has, and boxed to its archipelago.
"""
from _lib import E, T, write

KERGUELEN = [[37, 78, -54.5, -46]]          # Prince Edward, Crozet, Kerguelen, Heard
SUBANTARCTIC = [[-180, 180, -56, -45]]
MASCARENES = [[55, 64, -22, -19]]
MAURITIUS = [[57.2, 57.9, -20.6, -19.9]]
SEYCHELLES = [[55, 56.5, -5.5, -3.5]]
SEY_ALDABRA = [[46, 56.5, -10, -3.5]]

# ------------------------------------------------------------------ Kerguelen
E("Pringlea antiscorbutica", "species", "land", "flower", 5, 0, ["sou", "ind"],
  "Kerguelen cabbage, a wind-pollinated crucifer of the subantarctic islands; whalers ate it against scurvy.",
  hab=["island", "coast", "tundra"], box=KERGUELEN, w=3, cls=("Magnoliopsida", "Brassicales", "Brassicaceae"))
E("Azorella selago", "species", "land", "shrub", 5, 0, ["sou", "ind", "sa-s"],
  "A cushion plant that builds hard green mounds a metre across on windswept subantarctic fellfield.",
  hab=["island", "tundra", "alpine", "coast"], box=SUBANTARCTIC + [[-76, -64, -56, -40]],
  cls=("Magnoliopsida", "Apiales", "Apiaceae"))
E("Acaena magellanica", "species", "land", "flower", 5, 0, ["sou", "ind", "sa-s"],
  "The greater burnet of the far south, carpeting sheltered slopes from Patagonia to Kerguelen.",
  hab=["island", "tundra", "grassland", "coast"], box=SUBANTARCTIC + [[-76, -64, -56, -40]],
  cls=("Magnoliopsida", "Rosales", "Rosaceae"))
E("Poa cookii", "species", "land", "grass", 3, 0, ["sou", "ind"],
  "A tussock grass of Kerguelen, Heard and Marion Islands, thickest where seals and penguins manure the ground.",
  hab=["island", "coast", "tundra", "grassland"], box=KERGUELEN + [[158, 160, -55, -54]],
  cls=("Liliopsida", "Poales", "Poaceae"))
E("Anas eatoni", "species", "air", "waterfowl", 1, 0, ["sou", "ind"],
  "Eaton's pintail, a small duck found only on Kerguelen and the Crozet Islands.",
  hab=["island", "coast", "wetland"], box=[[50, 71, -50.5, -45.5]], realms=["air", "land"],
  cls=("Aves", "Anseriformes", "Anatidae"))
E("Cupressaceae", "family", "land", "conifer", 200, 0, ["cosmo", {"t": [34, 5], "in": ["sou"]}],
  "Cypresses, junipers, redwoods and their kin; their fossil wood lies in the Miocene lavas of Kerguelen, now a treeless island.",
  hab=["forest", "alpine", "island"], cls=("Pinopsida", "Pinales", "Cupressaceae"))

# ---------------------------------------------------------------- Mascarenes
E("Raphus cucullatus", "species", "land", "gamebird", 8, 0.0003, ["ind"],
  "The dodo, a giant flightless pigeon of Mauritius, extinct within a century of the first ships.",
  hab=["island", "forest", "coast"], box=MAURITIUS, w=3, cls=("Aves", "Columbiformes", "Columbidae"))
E("Cylindraspis", "genus", "land", "tortoise", 8, 0.0002, ["ind"],
  "The giant tortoises of Mauritius, Reunion and Rodrigues, five species grazing in herds of thousands until the 1700s.",
  hab=["island", "grassland", "forest", "coast"], box=MASCARENES, w=2, cls=("Reptilia", "Testudines", "Testudinidae"))
E("Pteropus niger", "species", "air", "bat", 2, 0, ["ind"],
  "The Mauritian flying fox, the island's last native mammal and the pollinator of its forest trees.",
  hab=["island", "forest"], box=MASCARENES, realms=["air", "land"], cls=("Mammalia", "Chiroptera", "Pteropodidae"))
E("Falco punctatus", "species", "air", "raptor", 2, 0, ["ind"],
  "The Mauritius kestrel, reduced to four wild birds in 1974 and brought back by captive breeding.",
  hab=["island", "forest"], box=MAURITIUS, realms=["air", "land"], cls=("Aves", "Falconiformes", "Falconidae"))
E("Phelsuma", "genus", "land", "lizard", 20, 0, ["ind", "mg"],
  "Day geckos, bright green nectar-feeders that spread from Madagascar to every island group of the western Indian Ocean.",
  hab=["island", "forest", "coast"], box=[[43, 64, -26, -3.5]], cls=("Reptilia", "Squamata", "Gekkonidae"))
E("Diospyros tessellaria", "species", "land", "broadleaf", 5, 0, ["ind"],
  "Mauritius ebony, the black-hearted timber the Dutch cut the island's forests for.",
  hab=["island", "forest"], box=MAURITIUS, cls=("Magnoliopsida", "Ericales", "Ebenaceae"))
E("Sideroxylon grandiflorum", "species", "land", "broadleaf", 5, 0, ["ind"],
  "The tambalacoque, long and wrongly said to need the dodo's gut to germinate; a slow canopy tree of Mauritius.",
  hab=["island", "forest"], box=MAURITIUS, cls=("Magnoliopsida", "Ericales", "Sapotaceae"))
E("Latania", "genus", "land", "palm", 8, 0, ["ind"],
  "Latan palms, a fan-palm genus confined to the Mascarenes, one species to each island.",
  hab=["island", "coast", "forest"], box=MASCARENES, cls=("Liliopsida", "Arecales", "Arecaceae"))

# ----------------------------------------------------------------- Seychelles
E("Sooglossidae", "family", "land", "frog", 63, 0, ["ind"],
  "Seychelles frogs, thumbnail-sized, whose nearest relative lives in India: they have ridden these granite islands since the two parted.",
  hab=["island", "forest"], box=SEYCHELLES, w=3, cls=("Amphibia", "Anura", ""), pic="Sooglossus")
E("Aldabrachelys gigantea", "species", "land", "tortoise", 2, 0, ["ind"],
  "The Aldabra giant tortoise, last of the Indian Ocean's giant tortoises, a hundred thousand strong on one atoll.",
  hab=["island", "grassland", "coast"], box=SEY_ALDABRA, w=3, cls=("Reptilia", "Testudines", "Testudinidae"))
E("Lodoicea maldivica", "species", "land", "palm", 20, 0, ["ind"],
  "The coco de mer of Praslin, bearing the largest seed of any plant, up to twenty-five kilograms.",
  hab=["island", "forest"], box=SEYCHELLES, w=3, cls=("Liliopsida", "Arecales", "Arecaceae"))
E("Pteropus seychellensis", "species", "air", "bat", 2, 0, ["ind"],
  "The Seychelles fruit bat, roosting by the hundred in the islands' takamaka and breadfruit trees.",
  hab=["island", "forest"], box=SEY_ALDABRA, realms=["air", "land"], cls=("Mammalia", "Chiroptera", "Pteropodidae"))
E("Coracopsis barklyi", "species", "air", "parrot", 2, 0, ["ind"],
  "The Seychelles black parrot, a few hundred birds in the palm forest of Praslin.",
  hab=["island", "forest"], box=SEYCHELLES, realms=["air", "land"], cls=("Aves", "Psittaciformes", "Psittacidae"))
E("Nepenthes pervillei", "species", "land", "pitcherplant", 20, 0, ["ind"],
  "The Seychelles pitcher plant, on bare granite summits; an early offshoot of a genus otherwise centred on Borneo.",
  hab=["island", "alpine", "forest"], box=SEYCHELLES, cls=("Magnoliopsida", "Caryophyllales", "Nepenthaceae"))
E("Medusagyne oppositifolia", "species", "land", "broadleaf", 50, 0, ["ind"],
  "The jellyfish tree of Mahe, sole member of its lineage, thought extinct until a few dozen were found in the 1970s.",
  hab=["island", "forest"], box=SEYCHELLES, cls=("Magnoliopsida", "Malpighiales", ""))

# ------------------------------------------------------------------ Jan Mayen
E("Salix herbacea", "species", "land", "shrub", 3, 0, ["arc", "eu", "gl", "na-n", "na-e"],
  "The dwarf willow, a tree a few centimetres tall, creeping through Arctic and alpine snowbeds.",
  hab=["tundra", "alpine", "island"], lat=[42, 84], cls=("Magnoliopsida", "Malpighiales", "Salicaceae"))
E("Racomitrium lanuginosum", "species", "land", "moss", 5, 0, ["arc", "eu", "gl", "na-n", "as-n", "sou", "sa-s", "nz"],
  "Woolly fringe-moss, the grey carpet over the lava fields of Iceland and Jan Mayen.",
  hab=["tundra", "alpine", "island", "coast"], lat=[40, 84], cls=("Bryopsida", "", ""))
E("Oxyria digyna", "species", "land", "flower", 3, 0, ["arc", "eu", "gl", "na-n", "na-w", "as-n", "as-c"],
  "Mountain sorrel, circling the Arctic and climbing every northern range, a first coloniser of raw ground.",
  hab=["tundra", "alpine", "island"], lat=[36, 84], cls=("Magnoliopsida", "Caryophyllales", "Polygonaceae"))

# ------------------------------------------------ Antarctica after the ice came
E("Listroderini", "tribe", "land", "beetle", 40, 0, [T(40, 14, "an", "sa-s"), T(14, 0, "sa-s", "sou")],
  "Weevils of southern South America whose fossils lie in the Meyer Desert beds, 500 km from the Pole: tundra insects that outlasted the first ice sheets.",
  hab=["tundra", "grassland", "alpine"], cls=("Insecta", "Coleoptera", "Curculionidae"))
E("Bryophyta", "division", "land", "moss", 330, 0, ["cosmo", "an"],
  "Mosses. They are most of Antarctica's land vegetation today, and beds of them lie freeze-dried in its Miocene tundra deposits.",
  hab=["tundra", "forest", "wetland", "alpine", "coast", "ice", "island"], cls=("Bryopsida", "", ""))
E("Tardigrada", "phylum", "land", "lobopod", 530, 0, ["cosmo", "an"],
  "Water bears, surviving freezing and drying alike; with nematodes and rotifers they are the permanent land animals of the ice-free Antarctic.",
  hab=["tundra", "ice", "forest", "wetland", "alpine"], cls=("", "", ""), pic="Hypsibius")
E("Prasiola crispa", "species", "land", "seaweed", 5, 0, ["an", "sou", "sa-s", "arc", "eu"],
  "A green alga that thrives on the guano-soaked ground of penguin rookeries, the most conspicuous plant life on the Antarctic coast.",
  hab=["coast", "ice", "tundra", "island"], lat=[50, 90], cls=("Trebouxiophyceae", "", ""))

# -------------------------------------------------- the tropical giants' twins
E("Eremotherium", "genus", "land", "groundsloth", 5, 0.011, [T(5, 2.7, "sa-n"), T(2.7, 0.011, "sa-n", "ca", "na-e")],
  "The tropical giant ground sloth, as big as Megatherium, ranging from Brazil through Panama to Florida.",
  hab=["rainforest", "forest", "grassland", "wetland"], lat=[0, 36], w=2, cls=("Mammalia", "Pilosa", "Megatheriidae"))
E("Mixotoxodon", "genus", "land", "notoungulate", 1.8, 0.011, ["sa-n", "ca", "na-e"],
  "The one notoungulate to leave South America, a rhino-sized grazer that reached Texas in the Great American Interchange.",
  hab=["grassland", "forest", "rainforest"], lat=[0, 32], cls=("Mammalia", "Notoungulata", "Toxodontidae"))

write("x-islands-polar.json")
