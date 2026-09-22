"""The Triassic and Early Cretaceous shelves, and the polar seas of the Cenozoic.

After the first marine batch the Mesozoic sea cards were still 51 per cent class-
and order-level names, and most of that was the Triassic (Claraia, Ceratitida,
Halobia and little else) and the Early Cretaceous (Buchia and the belemnites).
The Cenozoic's 37 per cent was the Southern Ocean, the Arctic and the Paratethys.
These are the genera the PBDB menus rank highest there, with the animals a
museum would show.
"""
from _lib import E, T, write

TETH = ["tet", "eu", "af-n", "as-w", "ar", "as-c", "as-e", "as-se", "in", "med"]
PANTH = ["pan", "na-w", "as-e", "as-n", "au", "nz", "sa-s", "an", "pac"]
BOREAL = ["arc", "eu", "as-n", "na-n", "na-w", "gl"]
SOUTH = ["sou", "an", "nz", "au", "sa-s", "af-s"]
PARA = ["tet", "eu", "as-w", "as-c"]

# ------------------------------------------------------------------ Triassic
E("Eumorphotis", "genus", "sea", "bivalve", 252, 240, ["cosmo"],
  "A ribbed scallop-like bivalve that crowded the sea floors of the earliest Triassic with Claraia, one of the few shells that thrived in the aftermath of the extinction.",
  hab=["shelf"], cls=("Bivalvia", "Pectinida", "Aviculopectinidae"))
E("Unionites", "genus", "sea", "clam", 252, 201, ["cosmo"],
  "A small, plain clam of low-oxygen Triassic muds, tolerant enough to be almost the only shell in some Early Triassic beds.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Cardiida", "Anthracosiidae"))
E("Bakevellia", "genus", "sea", "mussel", 260, 100, ["cosmo"],
  "A wing-shelled bivalve of lagoons and shallow shelves, in the Permian, Triassic and Jurassic of every continent.",
  hab=["coast", "shelf"], cls=("Bivalvia", "Ostreida", "Bakevelliidae"))
E("Neoschizodus", "genus", "sea", "bivalve", 252, 201, ["cosmo"],
  "A trigoniid clam, ribbed and triangular, that burrowed the Triassic sands of the Tethys and the Muschelkalk sea.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Trigoniida", "Myophoriidae"))
E("Gondolella", "genus", "sea", "conodont", 300, 200, ["cosmo"],
  "A conodont whose platform elements zone the Permian and Triassic worldwide; the last of the conodonts went with its family at the end of the Triassic.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Gondolellidae"))
E("Neospathodus", "genus", "sea", "conodont", 252, 245, ["cosmo"],
  "An Early Triassic conodont whose elements date the recovery from the end-Permian extinction, stage by stage, in Pakistan, China and Nevada alike.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Gondolellidae"))
E("Flexoptychites", "genus", "sea", "ammonite", 247, 237, TETH + ["pan", "na-w"],
  "A smooth, globular ceratitid ammonoid of the Middle Triassic Tethys, in the Alpine limestones by the thousand.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Ptychitidae"))
E("Gymnotoceras", "genus", "sea", "ammonite", 245, 237, ["na-w", "pan", "as-n", "as-e"],
  "The Anisian ammonoid of Nevada's Fossil Hill and of Arctic Siberia, a ceratitid of the open Panthalassan and Boreal seas.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Ceratitidae"))
E("Cladiscites", "genus", "sea", "ammonite", 237, 208, TETH + ["au", "pan"],
  "A smooth, involute Late Triassic ammonoid of the Tethys and Timor, with fine spiral lines and sutures like lace.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Cladiscitidae"))
E("Cassianella", "genus", "sea", "oyster", 242, 227, ["tet", "eu", "as-e", "as-se"],
  "A small pearl-oyster relative of the Cassian beds of the Dolomites, where a whole Triassic reef community is preserved shell by shell.",
  hab=["reef", "shelf"], cls=("Bivalvia", "Ostreida", "Cassianellidae"))
E("Coelostylina", "genus", "sea", "seasnail", 252, 201, ["cosmo"],
  "A tall-spired sea snail of Triassic shelves, common enough in the Cassian and Muschelkalk faunas to be the Triassic's ordinary snail.",
  hab=["shelf", "reef"], cls=("Gastropoda", "", "Coelostylinidae"))
E("Spondylospira", "genus", "sea", "brachiopod", 237, 201, ["pan", "sa-s", "na-w", "tet"],
  "A Late Triassic spiriferinid brachiopod of the Panthalassan shelves, from Nevada to Peru.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferinida", "Spondylospiridae"))
E("Cyrtina", "genus", "sea", "brachiopod", 420, 201, ["cosmo"],
  "A small spiriferide brachiopod with a high flat beak, from the Silurian to the last Triassic sea floors.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferida", "Cyrtinidae"))
E("Encrinus liliiformis", "species", "sea", "crinoid", 245, 237, ["eu", "tet", "as-e"],
  "The sea lily of the Muschelkalk, whose stem ossicles make whole beds of the German Middle Triassic; the crinoid gardens of a shallow inland sea.",
  hab=["shelf"], w=2, cls=("Crinoidea", "Encrinida", "Encrinidae"))
E("Nothosauridae", "family", "sea", "nothosaur", 247, 227, ["tet", "eu", "as-e", "as-w", "af-n", "as-se", "pan", "na-w"],
  "Nothosaurs: long-necked, paddle-limbed reptiles of Triassic shores, seal-like in habit, from the Muschelkalk to Guizhou.",
  hab=["coast", "shelf"], cls=("Reptilia", "Sauropterygia", "Nothosauridae"))
E("Tanystropheus", "genus", "sea", "protorosaur", 247, 227, ["tet", "eu", "as-e", "as-w", "af-n"],
  "A reptile whose neck was longer than the rest of it, with a dozen elongated vertebrae, fishing from the Tethyan shore.",
  hab=["coast", "shelf"], realms=["sea", "land"], w=2, cls=("Reptilia", "Protorosauria", "Tanystropheidae"))
E("Placodus", "genus", "sea", "placodont", 247, 237, ["tet", "eu", "as-e", "as-w"],
  "A placodont with peg teeth in front and flat crushing plates behind, browsing shellfish on the Muschelkalk sea floor.",
  hab=["shelf", "coast"], cls=("Reptilia", "Placodontia", "Placodontidae"))
E("Henodus", "genus", "sea", "placodont", 237, 227, ["eu", "tet"],
  "A placodont with a turtle-like shell wider than long and a toothless beak, in a brackish lagoon of Late Triassic Germany.",
  hab=["coast"], cls=("Reptilia", "Placodontia", "Henodontidae"))
E("Ichthyosaurus", "genus", "sea", "ichthyosaur", 201, 190, ["eu", "atl", "tet", "na-w"],
  "The ichthyosaur of Lyme Regis, dolphin-shaped, that Mary Anning dug from the Blue Lias.",
  hab=["pelagic", "shelf"], w=2, cls=("Reptilia", "Ichthyosauria", "Ichthyosauridae"))
E("Psiloceras", "genus", "sea", "ammonite", 201.4, 199, ["cosmo"],
  "The smooth ammonite whose first appearance defines the base of the Jurassic, in the first seas after the end-Triassic extinction.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Psiloceratidae"))

# ---------------------------------------------------------- Early Cretaceous
E("Neocomites", "genus", "sea", "ammonite", 140, 130, TETH + ["atl", "sa-s", "sa-n", "ca", "pac"],
  "A ribbed Valanginian ammonite of the Tethys and the young Atlantic, the standard fossil of the Neocomian.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Neocomitidae"))
E("Olcostephanus", "genus", "sea", "ammonite", 137, 130, ["cosmo"],
  "A globular, strongly ribbed ammonite of the Valanginian, known from Europe to Argentina, Mexico and South Africa.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Olcostephanidae"))
E("Crioceratites", "genus", "sea", "heteromorph", 133, 125, TETH + ["atl", "sa-s", "na-w", "pac"],
  "An open-coiled ammonite, whorls not touching, ribbed and spined, of the Hauterivian seas of the Tethys and Neuquen.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Crioceratitidae"))
E("Deshayesites", "genus", "sea", "ammonite", 125, 121, TETH + ["atl", "eu", "arc", "sa-n"],
  "The ammonite that defines the base of the Aptian, in the seas that widened as the Atlantic opened south.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Deshayesitidae"))
E("Douvilleiceras", "genus", "sea", "ammonite", 113, 106, ["cosmo"],
  "A knobbed, thick-ribbed Albian ammonite found on every continent, in the Western Interior Seaway and the Tethys alike.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Douvilleiceratidae"))
E("Mortoniceras", "genus", "sea", "ammonite", 106, 100, ["cosmo"],
  "A large keeled Albian ammonite of the Tethys, Africa and the Americas, the last zone fossil of the Early Cretaceous.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Brancoceratidae"))
E("Oxytropidoceras", "genus", "sea", "ammonite", 110, 100, ["cosmo"],
  "A sharp-keeled Albian ammonite of the Gulf Coast, Peru, Venezuela and Africa: the fauna of a tropical Atlantic that had just been made.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Mojsisovicsiidae"))
E("Polyptychites", "genus", "sea", "ammonite", 137, 133, BOREAL + ["atl"],
  "A Boreal Valanginian ammonite of the northern seas, from England to Siberia and Canada, marking the province the Tethyan forms did not reach.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Polyptychitidae"))
E("Tropaeum", "genus", "sea", "heteromorph", 121, 113, ["au", "eu", "arc", "na-n", "sa-s"],
  "A giant open-coiled Aptian ammonite, over a metre across in the Eromanga sea of Australia, whose shell was a slow spiral of separate whorls.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Ancyloceratidae"))
E("Steinmanella", "genus", "sea", "bivalve", 140, 92, ["sa-s", "sa-n", "pac", "as-e", "af-s"],
  "A large, heavily ribbed trigoniid clam, the shell that paves the Early Cretaceous shores of Argentina, and known too from Japan and South Africa.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Trigoniida", "Steinmanellidae"))
E("Pterotrigonia", "genus", "sea", "bivalve", 140, 66, ["as-e", "na-e", "na-w", "pac", "atl", "eu", "in", "au"],
  "A winged trigoniid clam of Cretaceous shores, common in Japan and the American Gulf Coast.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Trigoniida", "Megatrigoniidae"))
E("Neithea", "genus", "sea", "bivalve", 145, 66, ["cosmo"],
  "A ribbed, unequal-valved scallop of Cretaceous shelves, one of the commonest bivalves of the chalk seas.",
  hab=["shelf"], cls=("Bivalvia", "Pectinida", "Neitheidae"))
E("Glyphea", "genus", "sea", "lobster", 200, 100, ["cosmo"],
  "A burrowing lobster of Jurassic and Cretaceous sea floors, whose Thalassinoides-type burrows outnumber its bodies by millions.",
  hab=["shelf", "coast"], cls=("Malacostraca", "Decapoda", "Glypheidae"))
E("Ptyktoptychion", "genus", "sea", "shark", 118, 100, ["au", "pan"],
  "A chimaera of the Eromanga sea, known from its tooth plates in the opal fields of South Australia.",
  hab=["shelf"], cls=("Chondrichthyes", "Chimaeriformes", "Callorhinchidae"))
E("Umoonasaurus", "genus", "sea", "plesiosaur", 118, 113, ["au"],
  "A small plesiosaur of the cold Eromanga sea, found in the opal mines of Coober Pedy with crests on its skull.",
  hab=["shelf", "coast"], cls=("Reptilia", "Plesiosauria", "Leptocleididae"))
E("Orbitolina", "genus", "sea", "largeforam", 125, 90, TETH + ["ca", "atl", "sa-n", "pac"],
  "A cone-shaped larger foraminifer of the Urgonian reefs and platforms, the rock-former of the Aptian-Albian Tethys.",
  hab=["reef", "shelf"], lat=[0, 40], cls=("Globothalamea", "Loftusiida", "Orbitolinidae"))
E("Toxaster", "genus", "sea", "seaurchin", 140, 100, TETH + ["atl", "sa-s", "sa-n", "ca"],
  "A heart urchin of Early Cretaceous shelf marls, the ancestor of Micraster's line, burrowing in the Tethyan mud.",
  hab=["shelf"], cls=("Echinoidea", "Spatangoida", "Toxasteridae"))
E("Hypsocormus", "genus", "sea", "bigfish", 170, 145, ["eu", "tet", "atl"],
  "A tuna-shaped pachycormid fish of the Jurassic sea, a fast predator of the same family as the giant filter-feeder Leedsichthys.",
  hab=["pelagic"], cls=("Actinopterygii", "Pachycormiformes", "Pachycormidae"))

# ------------------------------------------------------- the polar Cenozoic seas
E("Panopea", "genus", "sea", "clam", 145, 0, ["cosmo"],
  "The geoduck, a deep-burrowing clam with a siphon longer than its shell, in cool shelf sands from the Cretaceous to the present; the commonest fossil shell of Antarctica's Miocene.",
  hab=["shelf", "coast"], lat=[25, 80], cls=("Bivalvia", "Adapedonta", "Hiatellidae"))
E("Lahillia", "genus", "sea", "clam", 70, 34, ["an", "sa-s", "sou", "nz"],
  "A thick-shelled clam of Seymour Island, in the Antarctic shelf sands from the last Cretaceous stage through the Eocene, before the ice.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Cardiida", "Lahilliidae"))
E("Antarctodarwinella", "genus", "sea", "seasnail", 55, 34, ["an", "sou"],
  "A struthiolariid sea snail of Eocene Antarctica, a lineage that survives in New Zealand's ostrich-foot shells.",
  hab=["shelf", "coast"], cls=("Gastropoda", "Sorbeoconcha", "Struthiolariidae"))
E("Austrochlamys", "genus", "sea", "bivalve", 12, 0, ["an", "sou", "sa-s"],
  "A cold-water scallop of the Antarctic shelf since the Miocene; its relative Adamussium colbecki grows under the sea ice today.",
  hab=["shelf", "ice"], cls=("Bivalvia", "Pectinida", "Pectinidae"))
E("Limopsis", "genus", "sea", "bivalve", 145, 0, ["cosmo"],
  "A small, hairy-shelled clam of cool and deep water, one of the commonest bivalves of the Antarctic and subantarctic shelves.",
  hab=["shelf", "deep"], lat=[30, 80], cls=("Bivalvia", "Arcida", "Limopsidae"))
E("Cellaria", "genus", "sea", "bryozoan", 66, 0, ["cosmo"],
  "A jointed, bushy bryozoan of cool shelf seas; in the Southern Ocean bryozoans build the sea-floor thickets that a reef's corals build in the tropics.",
  hab=["shelf"], lat=[30, 80], cls=("Gymnolaemata", "Cheilostomata", "Cellariidae"))
E("Notosaria", "genus", "sea", "brachiopod", 23, 0, ["nz", "sou", "an", "au"],
  "A rhynchonellid brachiopod of New Zealand and the Southern Ocean, a lamp-shell lineage still common where the water is cold.",
  hab=["shelf", "coast"], cls=("Rhynchonellata", "Rhynchonellida", "Notosariidae"))
E("Magasella", "genus", "sea", "brachiopod", 23, 0, ["nz", "sou", "au"],
  "A terebratulid brachiopod of New Zealand's shelves, where lamp-shells are still abundant in the cool south.",
  hab=["shelf", "coast"], cls=("Rhynchonellata", "Terebratulida", "Terebratellidae"))
E("Diaphus", "genus", "sea", "cod", 23, 0, ["cosmo"],
  "A lanternfish genus of a hundred living species, whose otoliths are the commonest fish fossils of Neogene deep-water sediments from New Zealand to Italy.",
  hab=["pelagic", "deep"], cls=("Actinopterygii", "Myctophiformes", "Myctophidae"))
E("Coelorinchus", "genus", "sea", "cod", 23, 0, ["cosmo"],
  "A grenadier of the continental slope, its otoliths in New Zealand's Miocene mudstones by the hundred.",
  hab=["deep"], cls=("Actinopterygii", "Gadiformes", "Macrouridae"))
E("Eurhomalea", "genus", "sea", "clam", 60, 0, ["an", "sou", "sa-s", "nz", "au"],
  "A venus clam of the cold southern shelves, in Antarctic sediments from the Palaeocene onward and on Patagonian shores today.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Venerida", "Veneridae"))
E("Cucullaea", "genus", "sea", "clam", 183, 0, ["cosmo"],
  "A thick, boxy ark clam of cool shelf sands; the commonest shell of Seymour Island's Palaeocene, and still living off Australia.",
  hab=["shelf"], cls=("Bivalvia", "Arcida", "Cucullaeidae"))
E("Balaenoptera", "genus", "sea", "whale", 11, 0, ["cosmo"],
  "The rorquals -- blue, fin, minke and humpback's kin -- lunge-feeders on krill and shoaling fish since the late Miocene.",
  hab=["pelagic"], cls=("Mammalia", "Cetacea", "Balaenopteridae"))
E("Megaptera", "genus", "sea", "whale", 5.3, 0, ["cosmo"],
  "The humpback whale, with flippers a third of its length, migrating between polar feeding grounds and tropical calving waters.",
  hab=["pelagic", "coast"], cls=("Mammalia", "Cetacea", "Balaenopteridae"))
E("Orcinus", "genus", "sea", "dolphin", 5.3, 0, ["cosmo"],
  "The orca, the ocean's top predator, hunting from the pack ice to the tropics in family pods that pass their hunting techniques down the generations.",
  hab=["pelagic", "coast", "ice"], w=2, cls=("Mammalia", "Cetacea", "Delphinidae"))
E("Lobodon carcinophaga", "species", "sea", "seal", 2.6, 0, ["an", "sou"],
  "The crabeater seal, the most numerous large mammal on Earth after us, sieving krill through lobed teeth on the Antarctic pack ice.",
  hab=["ice", "pelagic", "coast"], realms=["sea", "land"], cls=("Mammalia", "Carnivora", "Phocidae"))
E("Pagophilus groenlandicus", "species", "sea", "seal", 2.6, 0, ["arc", "atl"],
  "The harp seal, whelping on the pack ice of the North Atlantic and following the ice edge through the year.",
  hab=["ice", "pelagic", "coast"], realms=["sea", "land"], cls=("Mammalia", "Carnivora", "Phocidae"))
E("Mallotus villosus", "species", "sea", "fish", 5, 0, ["arc", "atl", "pac"],
  "The capelin, the small silver fish that cod, whales and seabirds of the North Atlantic and Arctic all depend on.",
  hab=["pelagic", "coast"], lat=[45, 85], cls=("Actinopterygii", "Osmeriformes", "Osmeridae"))
E("Gadus morhua", "species", "sea", "cod", 3.6, 0, ["arc", "atl"],
  "The Atlantic cod, the fish that fed and built the North Atlantic's coasts, from the Grand Banks to Lofoten.",
  hab=["shelf", "pelagic"], lat=[40, 82], w=2, cls=("Actinopterygii", "Gadiformes", "Gadidae"))
E("Dissostichus mawsoni", "species", "sea", "cod", 2.6, 0, ["sou", "an"],
  "The Antarctic toothfish, a two-metre notothenioid with antifreeze in its blood, top fish predator under the Ross Sea ice.",
  hab=["deep", "shelf", "ice"], cls=("Actinopterygii", "Perciformes", "Nototheniidae"))
E("Pleuragramma antarctica", "species", "sea", "cod", 2.6, 0, ["sou", "an"],
  "The Antarctic silverfish, the herring of the Southern Ocean, the link between the krill and the penguins, seals and whales.",
  hab=["pelagic", "ice", "shelf"], cls=("Actinopterygii", "Perciformes", "Nototheniidae"))
E("Euphausia superba", "species", "sea", "shrimp", 5, 0, ["sou", "an"],
  "Antarctic krill: swarms of hundreds of millions of tonnes on which the whole Southern Ocean food web rests.",
  hab=["pelagic", "ice"], w=3, cls=("Malacostraca", "Euphausiacea", "Euphausiidae"))
E("Limacina helicina", "species", "sea", "seasnail", 5, 0, ["arc", "sou", "an", "atl", "pac"],
  "The sea butterfly, a swimming snail a few millimetres across that feeds Arctic cod and whales, and whose thin shell dissolves first as the ocean acidifies.",
  hab=["pelagic", "ice"], lat=[45, 90], cls=("Gastropoda", "Pteropoda", "Limacinidae"))
E("Clione limacina", "species", "sea", "seasnail", 5, 0, ["arc", "sou", "an", "atl", "pac"],
  "The sea angel, a shell-less swimming snail of the polar oceans that hunts sea butterflies with hooked tentacles.",
  hab=["pelagic", "ice"], lat=[45, 90], cls=("Gastropoda", "Gymnosomata", "Clionidae"))
E("Congeria", "genus", "fresh", "mussel", 23, 0, ["eu", "as-w"],
  "A dreissenid mussel of the Paratethys, whose beds fill the brackish Pannonian lake sediments in their millions.",
  hab=["lake"], cls=("Bivalvia", "Myida", "Dreissenidae"))
E("Cerithium", "genus", "sea", "seasnail", 66, 0, ["cosmo"],
  "A tall-spired horn snail of warm shallow water, in vast numbers in the brackish Sarmatian sea of the Paratethys.",
  hab=["coast", "shelf"], lat=[0, 50], cls=("Gastropoda", "Caenogastropoda", "Cerithiidae"))
E("Mactra", "genus", "sea", "clam", 66, 0, ["cosmo"],
  "Trough shells, burrowing clams of sandy shores; the Paratethys of the late Miocene was so full of them that its beds are called the Mactra limestones.",
  hab=["coast", "shelf"], cls=("Bivalvia", "Venerida", "Mactridae"))
E("Cerastoderma", "genus", "sea", "clam", 23, 0, ["eu", "as-w", "af-n", "med", "atl", "arc"],
  "The cockle, a shallow-burrowing clam of estuaries and brackish lagoons; the Paratethys's low salinity suited it, and its species there ran riot.",
  hab=["coast"], cls=("Bivalvia", "Cardiida", "Cardiidae"))
E("Sarmatian fauna", "informal", "sea", "clam", 12.7, 11.6, PARA,
  "The brackish Sarmatian sea of the Paratethys: no corals, no sea urchins, no ammonite kin, but cockles, trough shells and horn snails in beds a hundred metres thick.",
  hab=["coast", "shelf"], rep="Cerastoderma", assemblage=True)
write("x-mesozoic-polar-seas.json")
