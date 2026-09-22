"""Open ocean and deep sea: what lives over and on the ridges, rises, plateaus and
abyssal plains. Written when the submerged labels (Ontong Java, Shatsky, Walvis...)
became sea cards and showed how little of the pelagic realm the registry held --
every one of them read "coelacanth, vent clam, vent mussel".

Basin codes only, with `hab` doing the real work: pelagic (the water column),
deep (bathyal and abyssal floor), vent, reef, shelf, coast. `box` keeps a regional
animal off the far side of its own ocean: "pac" is both the Coral Triangle and
the Gulf of California.
"""
from _lib import E, T, write

OCEANS = ["pac", "atl", "ind", "sou"]
WARM = ["pac", "atl", "ind"]
EPAC = [-135, -70, -45, 45]            # eastern Pacific
IWP = [[30, 180, -35, 35], [-180, -140, -30, 30]]   # Indo-West Pacific

# ------------------------------------------------------------ whales and seals
E("Physeter macrocephalus", "species", "sea", "whale", 2.6, 0, OCEANS + ["med"],
  "The sperm whale, the largest toothed predator alive, diving past two kilometres to hunt squid in the dark.",
  hab=["pelagic", "deep"], w=3, cls=("Mammalia", "Cetacea", "Physeteridae"))
E("Physeteroidea", "superfamily", "sea", "whale", 25, 2.6, OCEANS + ["med", "tet"],
  "Sperm whales in their Miocene variety, from dwarf forms to Livyatan, a raptorial hunter of other whales.",
  hab=["pelagic", "deep"], cls=("Mammalia", "Cetacea", "Physeteridae"), rep="Physeter macrocephalus")
E("Ziphiidae", "family", "sea", "dolphin", 20, 0, OCEANS,
  "Beaked whales, the deepest-diving mammals: Cuvier's beaked whale has been logged at nearly three kilometres.",
  hab=["pelagic", "deep"], cls=("Mammalia", "Cetacea", "Ziphiidae"), pic="Mesoplodon")
E("Delphinidae", "family", "sea", "dolphin", 11, 0, OCEANS + ["med", "arc"],
  "Oceanic dolphins, from spinners to orcas; a late-Miocene radiation that now fills every sea.",
  hab=["pelagic", "shelf", "coast"], cls=("Mammalia", "Cetacea", "Delphinidae"), pic="Tursiops")
E("Phocidae", "family", "sea", "seal", 20, 0, ["atl", "arc", "pac", "sou", "med", "an"],
  "True seals, which arose in the North Atlantic and reached the Antarctic pack ice by the late Miocene.",
  hab=["coast", "ice", "shelf", "island"], realms=["sea", "land"], cls=("Mammalia", "Carnivora", "Phocidae"))
E("Otariidae", "family", "sea", "seal", 12, 0, ["pac", "sou", "sa-s", "af-s", "au", "nz", "na-w"],
  "Sea lions and fur seals, a North Pacific family that crossed the equator about six million years ago.",
  hab=["coast", "island", "shelf"], realms=["sea", "land"], cls=("Mammalia", "Carnivora", "Otariidae"))
E("Mirounga leonina", "species", "sea", "seal", 2.6, 0, ["sou", "sa-s", "an"],
  "The southern elephant seal, bulls of four tonnes hauling out on subantarctic beaches to fight and breed.",
  hab=["coast", "island", "ice"], realms=["sea", "land"], w=3, cls=("Mammalia", "Carnivora", "Phocidae"))
E("Zalophus californianus", "species", "sea", "seal", 1, 0, ["pac", "na-w", "ca"],
  "The California sea lion, breeding on the desert islands of the Gulf of California and the Pacific coast.",
  hab=["coast", "island", "shelf"], realms=["sea", "land"], box=[-126, -105, 18, 50],
  cls=("Mammalia", "Carnivora", "Otariidae"))
E("Phocoena sinus", "species", "sea", "dolphin", 2, 0, ["pac"],
  "The vaquita, the smallest and rarest cetacean, confined to the turbid head of the Gulf of California.",
  hab=["coast", "shelf"], box=[-115.5, -113.0, 29.5, 32.0], w=3, cls=("Mammalia", "Cetacea", "Phocoenidae"))
E("Dugong dugon", "species", "sea", "sirenian", 2, 0, ["ind", "pac"],
  "The dugong, the one strictly marine sea cow left, grazing seagrass from the Red Sea to the Coral Sea.",
  hab=["coast", "shelf", "reef"], lat=[0, 30], box=IWP, w=3, cls=("Mammalia", "Sirenia", "Dugongidae"))

# ------------------------------------------------------------- fishes and sharks
E("Myctophidae", "family", "sea", "cod", 55, 0, OCEANS + ["med", "arc", "tet"],
  "Lanternfishes, perhaps the most abundant vertebrates on Earth, rising hundreds of metres to the surface every night.",
  hab=["pelagic", "deep"], w=2, cls=("Actinopterygii", "Myctophiformes", "Myctophidae"), pic="Myctophum")
E("Ceratioidei", "suborder", "sea", "fish", 23, 0, OCEANS,
  "Deep-sea anglerfishes, luring prey with a glowing bait; in some, the dwarf male fuses to the female for life.",
  hab=["deep"], cls=("Actinopterygii", "Lophiiformes", ""), pic="Melanocetus")
E("Macrouridae", "family", "sea", "cod", 40, 0, OCEANS + ["arc"],
  "Grenadiers or rattails, the commonest fishes of the continental slope and the abyssal plain.",
  hab=["deep"], cls=("Actinopterygii", "Gadiformes", "Macrouridae"), pic="Coryphaenoides")
E("Thunnus", "genus", "sea", "bigfish", 30, 0, WARM + ["med"],
  "Tunas: warm-blooded, ocean-crossing predators built for sustained speed.",
  hab=["pelagic"], lat=[0, 60], w=2, cls=("Actinopterygii", "Scombriformes", "Scombridae"))
E("Istiophoridae", "family", "sea", "bigfish", 15, 0, WARM,
  "Marlins and sailfish, the fastest fishes of the open tropical ocean.",
  hab=["pelagic"], lat=[0, 45], cls=("Actinopterygii", "Istiophoriformes", "Xiphiidae"), pic="Xiphias")
E("Exocoetidae", "family", "sea", "fish", 40, 0, WARM,
  "Flying fishes, gliding tens of metres on enlarged fins to escape tuna and dolphinfish.",
  hab=["pelagic"], lat=[0, 40], cls=("Actinopterygii", "Beloniformes", ""), pic="Cheilopogon")
E("Totoaba macdonaldi", "species", "sea", "bigfish", 2, 0, ["pac"],
  "The totoaba, a two-metre drum found only in the Gulf of California, spawning at the Colorado River's mouth.",
  hab=["coast", "shelf"], box=[-115.5, -109.0, 24.0, 32.0], cls=("Actinopterygii", "", "Sciaenidae"))
E("Carcharodon carcharias", "species", "sea", "shark", 6, 0, OCEANS + ["med"],
  "The great white shark, descended from broad-toothed makos about six million years ago.",
  hab=["pelagic", "shelf", "coast"], lat=[15, 60], cls=("Chondrichthyes", "Lamniformes", "Lamnidae"))
E("Isurus", "genus", "sea", "shark", 30, 0, OCEANS + ["med", "tet"],
  "Mako sharks, the fastest of all sharks and ocean-wide hunters of tuna and swordfish.",
  hab=["pelagic"], cls=("Chondrichthyes", "Lamniformes", "Lamnidae"))
E("Hexanchus", "genus", "sea", "shark", 100, 0, OCEANS + ["med", "tet"],
  "Sixgill sharks, a lineage little changed since the Jurassic, cruising the dark continental slopes.",
  hab=["deep"], cls=("Chondrichthyes", "Hexanchiformes", "Hexanchidae"))
E("Somniosus microcephalus", "species", "sea", "shark", 2.6, 0, ["arc", "atl"],
  "The Greenland shark, the longest-lived vertebrate known; individuals are thought to reach four centuries.",
  hab=["deep", "pelagic", "ice"], lat=[50, 90], w=3, cls=("Chondrichthyes", "Squaliformes", "Squalidae"))
E("Rhincodon typus", "species", "sea", "shark", 28, 0, WARM,
  "The whale shark, the largest fish alive, filtering plankton at the surface of warm seas.",
  hab=["pelagic", "reef"], lat=[0, 35], cls=("Chondrichthyes", "Orectolobiformes", ""))
E("Mobula", "genus", "sea", "ray", 28, 0, WARM,
  "Manta and devil rays, filter-feeders that leap clear of the water in schools of thousands.",
  hab=["pelagic", "reef"], lat=[0, 40], cls=("Chondrichthyes", "Myliobatiformes", "Mobulidae"))
E("Chaetodontidae", "family", "sea", "reeffish", 30, 0, [T(30, 14, "tet", "ind", "pac", "atl"), T(14, 0, "ind", "pac", "atl")],
  "Butterflyfishes, coral-pickers whose numbers rise and fall with the reef itself.",
  hab=["reef"], lat=[0, 32], cls=("Actinopterygii", "Perciformes", "Chaetodontidae"))

# ------------------------------------------------------------ reptiles and birds
E("Cheloniidae", "family", "sea", "seaturtle", 70, 0, WARM + ["med", "tet"],
  "Hard-shelled sea turtles: green, hawksbill, loggerhead and their Cretaceous forerunners.",
  hab=["pelagic", "shelf", "reef", "coast"], lat=[0, 50], cls=("Reptilia", "Testudines", "Cheloniidae"), pic="Chelonia")
E("Dermochelys coriacea", "species", "sea", "seaturtle", 2.6, 0, OCEANS + ["med"],
  "The leatherback, a half-tonne turtle that follows jellyfish from the tropics to subpolar water.",
  hab=["pelagic"], lat=[0, 65], cls=("Reptilia", "Testudines", "Dermochelyidae"))
E("Diomedeidae", "family", "air", "seabird", 30, 0, ["sou", "pac", "atl", "ind"],
  "Albatrosses, gliding the wind belts for years between landfalls on remote islands.",
  hab=["pelagic", "island"], lat=[20, 70], realms=["air", "sea"], w=2,
  cls=("Aves", "Procellariiformes", "Diomedeidae"), rep="Diomedea exulans")
E("Diomedea exulans", "species", "air", "seabird", 2, 0, ["sou", "ind", "atl", "pac"],
  "The wandering albatross, with the widest wingspan of any living bird, circling the Southern Ocean between breeding seasons.",
  hab=["pelagic", "island"], lat=[28, 68], realms=["air", "sea", "land"], w=3,
  cls=("Aves", "Procellariiformes", "Diomedeidae"))
E("Procellariiformes", "order", "air", "seabird", 45, 0, OCEANS + ["arc", "med"],
  "Petrels, shearwaters and storm-petrels: tube-nosed seabirds that come ashore only to breed.",
  hab=["pelagic", "island", "coast"], realms=["air", "sea", "land"], cls=("Aves", "Procellariiformes", ""), pic="Puffinus")
E("Spheniscidae", "family", "land", "penguin", 62, 0,
  [T(62, 34, "nz", "an", "sa-s", "au"), T(34, 0, "nz", "an", "sa-s", "au", "af-s", "sou")],
  "Penguins, flightless divers since the Paleocene; several Eocene and Oligocene species stood as tall as a person.",
  hab=["coast", "island", "ice", "shelf", "pelagic"], realms=["land", "sea"], cls=("Aves", "Sphenisciformes", "Spheniscidae"))
E("Aptenodytes patagonicus", "species", "land", "penguin", 2, 0, ["sou", "sa-s"],
  "The king penguin, breeding in colonies of hundreds of thousands on the subantarctic islands.",
  hab=["coast", "island"], lat=[44, 62], realms=["land", "sea"], w=3, cls=("Aves", "Sphenisciformes", "Spheniscidae"))
E("Alle alle", "species", "air", "seabird", 2, 0, ["arc", "atl"],
  "The little auk, nesting by the million in High Arctic scree and wintering on the open North Atlantic.",
  hab=["coast", "island", "ice", "pelagic", "tundra"], lat=[50, 85], realms=["air", "sea", "land"],
  cls=("Aves", "Charadriiformes", "Alcidae"))
E("Fulmarus glacialis", "species", "air", "seabird", 2, 0, ["arc", "atl", "pac"],
  "The northern fulmar, a cold-water petrel that nests on sea cliffs from Brittany to the High Arctic.",
  hab=["coast", "island", "pelagic", "tundra"], lat=[45, 85], realms=["air", "sea", "land"],
  cls=("Aves", "Procellariiformes", ""))
E("Phaethon", "genus", "air", "seabird", 5, 0, WARM,
  "Tropicbirds, plunge-divers of the warm open ocean that nest on the remotest islands.",
  hab=["pelagic", "island"], lat=[0, 32], realms=["air", "sea", "land"], cls=("Aves", "Charadriiformes", ""))
E("Onychoprion fuscatus", "species", "air", "seabird", 2, 0, WARM,
  "The sooty tern, which stays on the wing for years at sea and breeds in vast colonies on tropical islets.",
  hab=["pelagic", "island"], lat=[0, 30], realms=["air", "sea", "land"], cls=("Aves", "Charadriiformes", "Laridae"))

# ---------------------------------------------------------------- invertebrates
E("Architeuthis", "genus", "sea", "squid", 5, 0, OCEANS,
  "The giant squid, reaching twelve metres and known for most of history only from carcasses and sperm-whale scars.",
  hab=["deep", "pelagic"], w=3, cls=("Cephalopoda", "Teuthida", "Architeuthidae"))
E("Vampyroteuthis infernalis", "species", "sea", "squid", 23, 0, WARM,
  "The vampire squid, last of an order older than the dinosaurs, drifting in the oxygen-minimum zone on marine snow.",
  hab=["deep"], lat=[0, 45], cls=("Cephalopoda", "Vampyromorpha", ""))
E("Dosidicus gigas", "species", "sea", "squid", 2, 0, ["pac"],
  "The Humboldt or jumbo squid, hunting in shoals of thousands along the eastern Pacific.",
  hab=["pelagic", "deep"], box=EPAC, cls=("Cephalopoda", "Teuthida", ""))
E("Octocorallia", "subclass", "sea", "coral", 480, 0, OCEANS + ["med", "arc", "tet", "pan", "iap", "rhe"],
  "Soft corals, sea fans and bamboo corals; on seamounts they form forests that can be thousands of years old.",
  hab=["deep", "reef", "shelf"], cls=("Anthozoa", "Alcyonacea", ""), pic="Gorgonia")
E("Lophelia pertusa", "species", "sea", "coral", 5, 0, ["atl", "med", "pac", "ind"],
  "A cold-water coral building reefs in the dark, hundreds of metres down, along continental slopes and seamounts.",
  hab=["deep"], cls=("Anthozoa", "Scleractinia", "Caryophylliidae"))
E("Stylophora pistillata", "species", "sea", "coral", 5, 0, ["ind", "pac"],
  "A branching reef coral of the Indo-Pacific; its Red Sea populations tolerate unusually hot water.",
  hab=["reef"], lat=[0, 32], box=IWP, cls=("Anthozoa", "Scleractinia", "Pocilloporidae"))
E("Osedax", "genus", "sea", "worm", 100, 0, OCEANS + ["med", "tet"],
  "Bone-eating worms that bore into whale skeletons on the sea floor; their traces go back to plesiosaur bones.",
  hab=["deep"], cls=("Polychaeta", "Sabellida", ""))
E("Xenophyophorea", "class", "sea", "foram", 66, 0, OCEANS,
  "Giant single-celled organisms of the abyssal plain, some the size of a fist, building shells from sediment.",
  hab=["deep"], cls=("Monothalamea", "", ""))
E("Pyrosoma", "genus", "sea", "jellyfish", 23, 0, WARM,
  "Pyrosomes: glowing colonial tunicates, hollow tubes that can grow longer than a whale.",
  hab=["pelagic"], lat=[0, 45], cls=("Thaliacea", "", ""))
E("Physalia physalis", "species", "sea", "jellyfish", 5, 0, WARM,
  "The Portuguese man o' war, a colony of specialised animals sailing under a gas-filled float.",
  hab=["pelagic"], lat=[0, 45], cls=("Hydrozoa", "Siphonophorae", ""))

# --------------------------------------------------- sea plants, algae, plankton
E("Sargassum natans", "species", "sea", "seaweed", 5, 0, ["atl"],
  "Free-floating sargassum, the golden weed of the Sargasso Sea, carrying its own community of fish, crabs and turtles.",
  hab=["pelagic"], lat=[0, 42], w=3, cls=("Phaeophyceae", "Fucales", "Sargassaceae"))
E("Sargassum", "genus", "sea", "seaweed", 20, 0, WARM + ["med"],
  "Sargassum weeds, attached on warm rocky shores and, in two Atlantic species, drifting free in mid-ocean.",
  hab=["coast", "reef", "shelf"], lat=[0, 42], cls=("Phaeophyceae", "Fucales", "Sargassaceae"))
E("Zostera marina", "species", "sea", "seagrass", 5, 0, ["atl", "pac", "arc", "med"],
  "Eelgrass, the seagrass of cool northern shores, nursery to cod, scallops and brent geese.",
  hab=["coast", "shelf"], lat=[26, 72], cls=("Liliopsida", "Alismatales", "Zosteraceae"))
E("Thalassia testudinum", "species", "sea", "seagrass", 10, 0, ["atl"],
  "Turtle grass, forming the great seagrass meadows of the Caribbean and the Gulf of Mexico.",
  hab=["coast", "shelf", "reef"], lat=[8, 32], box=[-98, -58, 8, 32], cls=("Liliopsida", "Alismatales", "Hydrocharitaceae"))
E("Halophila stipulacea", "species", "sea", "seagrass", 5, 0, ["ind"],
  "A small seagrass of the Red Sea and western Indian Ocean, growing from the shallows to fifty metres down.",
  hab=["coast", "shelf", "reef"], lat=[0, 32], box=[30, 80, -30, 32], cls=("Liliopsida", "Alismatales", "Hydrocharitaceae"))
E("Thalassodendron ciliatum", "species", "sea", "seagrass", 5, 0, ["ind"],
  "The seagrass of Saya de Malha, a drowned bank in mid-ocean carrying the largest seagrass meadow on Earth.",
  hab=["shelf", "reef", "coast"], lat=[0, 30], box=[32, 75, -30, 28], cls=("Liliopsida", "Alismatales", "Cymodoceaceae"))
E("Avicennia marina", "species", "land", "mangrove", 5, 0,
  ["ind", "pac", "af-e", "af-s", "ar", "in", "as-se", "as-e", "au", "ng", "nz", "mg"],
  "The grey mangrove, the most salt- and cold-tolerant of all, fringing desert coasts from the Red Sea to New Zealand.",
  hab=["coast", "wetland"], lat=[0, 39], realms=["land", "sea"], box=IWP, cls=("Magnoliopsida", "Lamiales", "Acanthaceae"))
E("Trichodesmium erythraeum", "species", "sea", "cyano", 66, 0, WARM,
  "'Sea sawdust', a nitrogen-fixing cyanobacterium whose rust-coloured blooms are the likely source of the Red Sea's name.",
  hab=["pelagic"], lat=[0, 35], cls=("Cyanophyceae", "Oscillatoriales", ""))
E("Prochlorococcus", "genus", "sea", "cyano", 150, 0, WARM + ["med", "tet", "pan"],
  "The smallest and most numerous photosynthesiser known, making a large share of the oxygen produced by the open ocean.",
  hab=["pelagic"], lat=[0, 45], cls=("Cyanophyceae", "Synechococcales", ""))
write("x-open-ocean.json")
