"""The seas at genus level, Cambrian to Cretaceous.

Before this the Palaeozoic open-ocean cards were 80 per cent class- and
order-level entries ("Brachiopoda, Crinoidea, Bryozoa") and the Mesozoic ones
63 per cent. The PBDB menus in pbdb_menus/ (top genera by collections per region
and era) chose most of these; the rest are the animals a museum would lead with.

Basins carry the pelagic and nektonic forms; rim crust codes carry the shelf
faunas, because a Sloss sea's card is composed from the crust it flooded.
"""
from _lib import E, T, write

LAUR = ["na-w", "na-e", "na-n", "gl", "iap"]                  # Laurentian shelves
BALT = ["eu", "iap", "rhe", "ura"]                            # Baltica and its margins
EURAM = ["na-w", "na-e", "na-n", "gl", "eu", "rhe", "iap"]
GOND = ["af-n", "af-w", "af-s", "af-e", "sa-n", "sa-s", "au", "an", "in", "ar", "rhe", "iap"]
PZ_ALL = ["cosmo"]
TETH = ["tet", "eu", "af-n", "as-w", "ar", "as-c", "as-e", "as-se", "in", "med"]
PANTH = ["pan", "na-w", "as-e", "as-n", "au", "nz", "sa-s", "an", "pac"]
WIS = ["na-w", "na-e", "arc"]                                 # the Western Interior Seaway
NATL = ["atl", "eu", "na-e", "af-n", "ca"]

# ------------------------------------------------------------------ Cambrian
E("Marrella", "genus", "sea", "cambrianarthropod", 508, 505, ["na-w", "na-n"],
  "The commonest animal of the Burgess Shale, a thumbnail-sized arthropod with sweeping head spines; thousands of specimens, no close living relative.",
  hab=["shelf", "deep"], cls=("", "Marrellomorpha", "Marrellidae"))
E("Opabinia", "genus", "sea", "radiodont", 508, 505, ["na-w", "na-n"],
  "Five eyes and a hose-like proboscis ending in a claw; the Burgess Shale animal that drew laughter when first described.",
  hab=["shelf", "deep"], cls=("Dinocaridida", "", "Opabiniidae"))
E("Pikaia", "genus", "sea", "fish", 508, 505, ["na-w", "na-n"],
  "A lancelet-like swimmer from the Burgess Shale with a notochord and V-shaped muscles: one of the oldest chordates.",
  hab=["shelf"], cls=("", "", "Pikaiidae"))
E("Ottoia", "genus", "sea", "worm", 508, 505, ["na-w", "na-n"],
  "A burrowing priapulid worm, the commonest predator of the Burgess Shale sea floor, found with hyoliths in its gut.",
  hab=["shelf"], cls=("Priapulida", "", "Ottoiidae"))
E("Elrathia", "genus", "sea", "trilobite", 507, 500, ["na-w", "na-e"],
  "The trilobite everyone has held: Elrathia kingii from Utah's Wheeler Shale, quarried by the million from a low-oxygen shelf it had almost to itself.",
  hab=["shelf"], w=2, cls=("Trilobita", "Ptychopariida", "Alokistocaridae"))
E("Ptychagnostus", "genus", "sea", "agnostid", 510, 497, ["cosmo"],
  "A tiny blind agnostid trilobite that drifted worldwide, which is what makes it the middle Cambrian's best time-marker.",
  hab=["pelagic", "shelf"], cls=("Trilobita", "Agnostida", "Ptychagnostidae"))
E("Olenus", "genus", "sea", "trilobite", 497, 485, ["eu", "iap", "na-e", "as-c", "as-e"],
  "The late Cambrian trilobite of the Baltic alum shales, living in black oxygen-poor mud that preserved it in its thousands.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Olenidae"))
E("Archaeocyathus", "genus", "sea", "archaeocyath", 525, 510, ["au", "sa-s", "na-w", "as-n", "af-n", "an"],
  "A cup-shaped reef builder of the early Cambrian, sponge-grade animals that made the first animal reefs and were gone by the middle of the period.",
  hab=["reef"], cls=("Archaeocyatha", "", ""))

# ---------------------------------------------------------------- Ordovician
E("Flexicalymene", "genus", "sea", "trilobite", 470, 443, LAUR + ["eu", "af-n"],
  "The enrolled trilobite of the Cincinnati hills, found curled into a ball by the thousand; the commonest trilobite of Late Ordovician North America.",
  hab=["shelf"], w=2, cls=("Trilobita", "Phacopida", "Calymenidae"))
E("Rafinesquina", "genus", "sea", "brachiopod", 470, 440, LAUR + ["eu"],
  "A wide, flat strophomenid brachiopod that lay on the mud like a dropped coin, the most abundant shell in the Ordovician limestones of the American Midwest.",
  hab=["shelf"], cls=("Strophomenata", "Strophomenida", "Rafinesquinidae"))
E("Platystrophia", "genus", "sea", "brachiopod", 470, 430, LAUR + ["eu"],
  "A strongly ribbed brachiopod with a sharp fold, so common in Cincinnatian rocks that it is Ohio's state fossil in all but name.",
  hab=["shelf"], cls=("Rhynchonellata", "Orthida", "Platystrophiidae"))
E("Cryptolithus", "genus", "sea", "trilobite", 465, 445, LAUR + ["eu"],
  "The lace-collar trilobite: blind, with a pitted fringe around the head that filtered the mud it ploughed through.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Trinucleidae"))
E("Orthoceras", "genus", "sea", "orthocone", 470, 440, ["eu", "iap", "ura", "af-n", "as-c", "na-e", "na-w"],
  "The straight-shelled nautiloid of the Baltic 'Orthoceras limestone', a metre-long swimmer whose chambered shells pave the floors of Swedish churches.",
  hab=["shelf", "pelagic"], w=2, cls=("Cephalopoda", "Orthocerida", "Orthoceratidae"))
E("Didymograptus", "genus", "sea", "graptolite", 480, 460, ["cosmo"],
  "The tuning-fork graptolite, two branches hanging from a float; a colonial drifter whose fossils zone the Early Ordovician worldwide.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Dichograptidae"))
E("Climacograptus", "genus", "sea", "graptolite", 468, 435, ["cosmo"],
  "A single-stemmed graptolite with square-cut cups, the drifting plankton of Late Ordovician black shales on every continent.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Diplograptidae"))
E("Streptelasma", "genus", "sea", "horncoral", 470, 425, LAUR + ["eu"],
  "A solitary horn coral, the simplest of the rugose corals, standing on its tip in the Ordovician mud.",
  hab=["shelf"], cls=("Anthozoa", "Rugosa", "Streptelasmatidae"))
E("Constellaria", "genus", "sea", "bryozoan", 460, 445, LAUR,
  "A branching bryozoan whose colonies are dotted with star-shaped mounds; in the Cincinnatian it is a rock-forming fossil.",
  hab=["shelf"], cls=("Stenolaemata", "Cystoporata", "Constellariidae"))
E("Isorophus", "genus", "sea", "crinoid", 460, 445, LAUR,
  "An edrioasteroid, a disc of an echinoderm that cemented itself to shells and fed with five curved arms; a group with no living relatives.",
  hab=["shelf"], cls=("Edrioasteroidea", "Isorophida", ""))
E("Sacabambaspis", "genus", "sea", "ostracoderm", 465, 455, ["sa-s", "sa-n", "au"],
  "A jawless armoured fish of Ordovician Gondwana, tadpole-shaped with a bony head shield, in shoals along the Bolivian shore.",
  hab=["coast", "shelf"], cls=("Pteraspidomorphi", "Arandaspida", "Arandaspididae"))
E("Astraspis", "genus", "sea", "ostracoderm", 460, 450, ["na-w", "na-e"],
  "One of the oldest vertebrates with a skeleton, a jawless fish clad in mosaic bony plates, from the Ordovician of Colorado.",
  hab=["coast", "shelf"], cls=("Pteraspidomorphi", "", "Astraspididae"))

# ------------------------------------------------------------------ Silurian
E("Atrypa", "genus", "sea", "brachiopod", 435, 370, ["cosmo"],
  "A round, finely ribbed brachiopod with a spiral feeding organ inside, in nearly every Silurian and Devonian shelf sea in the world.",
  hab=["shelf", "reef"], w=2, cls=("Rhynchonellata", "Atrypida", "Atrypidae"))
E("Leptaena", "genus", "sea", "brachiopod", 445, 360, ["cosmo"],
  "A wrinkled, flat-lying brachiopod with a sharp bend at the edge, one of the longest-lived shell genera of the Palaeozoic.",
  hab=["shelf"], cls=("Strophomenata", "Strophomenida", "Rafinesquinidae"))
E("Calymene", "genus", "sea", "trilobite", 436, 415, ["eu", "na-e", "af-n", "iap"],
  "The 'Dudley bug', a trilobite so abundant in the Silurian limestone of the English Midlands that the town put it on its coat of arms.",
  hab=["shelf", "reef"], w=2, cls=("Trilobita", "Phacopida", "Calymenidae"))
E("Dalmanites", "genus", "sea", "trilobite", 435, 410, ["eu", "na-e", "iap", "af-n", "sa-s"],
  "A trilobite with a long tail spine and large crescent eyes, a swimmer or fast crawler of the Silurian shelf.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Dalmanitidae"))
E("Eurypterus", "genus", "sea", "eurypterid", 432, 418, ["na-e", "eu", "iap"],
  "The sea scorpion of New York's Bertie waterlime, found by the thousand in a salty lagoon; the type of its whole group.",
  hab=["coast", "shelf"], w=2, cls=("Merostomata", "Eurypterida", "Eurypteridae"))
E("Kockelella", "genus", "sea", "conodont", 433, 425, ["cosmo"],
  "A Silurian conodont, known from tooth-like elements a millimetre long that zone the Wenlock and Ludlow worldwide.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Kockelellidae"))
E("Panderodus", "genus", "sea", "conodont", 470, 400, ["cosmo"],
  "A long-lived conodont whose cone-shaped elements are in almost every Ordovician and Silurian limestone; the animal itself was a small eel-like swimmer.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Panderodontida", "Panderodontidae"))
E("Heliolites", "genus", "sea", "tabulate", 440, 385, ["cosmo"],
  "A 'sun coral', a tabulate whose tubes stand in a honeycomb of finer ones, building Silurian and Devonian reefs with Favosites and Halysites.",
  hab=["reef"], cls=("Anthozoa", "Heliolitida", "Heliolitidae"))

# ------------------------------------------------------------------ Devonian
E("Phacops", "genus", "sea", "trilobite", 410, 372, ["eu", "af-n", "na-e", "rhe"],
  "The trilobite with the compound eyes of stacked calcite lenses, each one visible to the naked eye; a Devonian reef-dweller found enrolled by the hundred.",
  hab=["shelf", "reef"], w=2, cls=("Trilobita", "Phacopida", "Phacopidae"))
E("Eldredgeops", "genus", "sea", "trilobite", 393, 380, ["na-e"],
  "The Devonian trilobite of New York and Ohio, once called Phacops rana, whose eye lenses were read for the evolution of vision.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Phacopidae"))
E("Hexagonaria", "genus", "sea", "horncoral", 393, 372, ["na-e", "na-w", "eu", "af-n", "as-c"],
  "The Petoskey stone: a colonial rugose coral of Devonian reefs whose six-sided corallites turn up as pebbles on Lake Michigan beaches.",
  hab=["reef", "shelf"], cls=("Anthozoa", "Rugosa", "Disphyllidae"))
E("Manticoceras", "genus", "sea", "ammonite", 382, 372, ["cosmo"],
  "A Late Devonian goniatite whose disappearance marks the Frasnian-Famennian extinction, one of the five great ones.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Gephuroceratidae"))
E("Tentaculites", "genus", "sea", "hyolith", 420, 375, ["cosmo"],
  "Ringed, tapering shells a centimetre long, in such numbers that they pave Devonian bedding planes; what the animal was is still argued.",
  hab=["shelf"], cls=("", "Tentaculitida", "Tentaculitidae"))
E("Cladoselache", "genus", "sea", "shark", 385, 360, ["na-e"],
  "An early shark from the Cleveland Shale, preserved with skin and muscle: a fast open-water hunter with the terminal mouth of a fish rather than a shark's underslung one.",
  hab=["pelagic", "shelf"], cls=("Chondrichthyes", "Cladoselachiformes", "Cladoselachidae"))
E("Titanichthys", "genus", "sea", "placoderm", 372, 359, ["na-e", "af-n"],
  "A placoderm as long as Dunkleosteus but with no teeth: a filter-feeder, the first giant to make a living straining the sea.",
  hab=["pelagic", "shelf"], cls=("Placodermi", "Arthrodira", "Titanichthyidae"))
E("Coccosteus", "genus", "sea", "placoderm", 395, 380, ["eu", "gl", "na-e"],
  "A half-metre arthrodire of the Old Red Sandstone lakes and seas of Scotland, armoured over the head and trunk and naked behind.",
  hab=["shelf", "lake"], realms=["sea", "fresh"], cls=("Placodermi", "Arthrodira", "Coccosteidae"))
E("Cheirolepis", "genus", "sea", "fish", 395, 380, ["eu", "gl", "na-e"],
  "One of the earliest ray-finned fishes, a fast predator of the Devonian lakes of Scotland and Quebec, ancestral in form to half the vertebrates alive.",
  hab=["lake", "river", "coast"], realms=["fresh", "sea"], cls=("Actinopterygii", "Cheirolepiformes", "Cheirolepididae"))

# ------------------------------------------------------------- Carboniferous
E("Composita", "genus", "sea", "brachiopod", 345, 252, ["cosmo"],
  "A smooth, rounded brachiopod, the single most abundant shell of Carboniferous and Permian limestones in North America.",
  hab=["shelf"], cls=("Rhynchonellata", "Athyridida", "Athyrididae"))
E("Archimedes", "genus", "sea", "bryozoan", 345, 300, ["na-e", "na-w", "eu", "as-n"],
  "A bryozoan built as a corkscrew: a lacy fan wound round a spiral axis, named for the screw, and a rock-former in Mississippian limestones.",
  hab=["shelf"], w=2, cls=("Stenolaemata", "Fenestrata", "Fenestellidae"))
E("Pentremites", "genus", "sea", "blastoid", 340, 305, ["na-e", "na-w"],
  "A blastoid: a bud-shaped echinoderm on a stalk, with five feeding grooves, so abundant in the Mississippian of the Mississippi valley that they are sold by the jar.",
  hab=["shelf"], w=2, cls=("Blastoidea", "Spiraculata", "Pentremitidae"))
E("Platycrinites", "genus", "sea", "crinoid", 345, 300, ["na-e", "na-w", "eu"],
  "A crinoid with a twisted stem and a low cup, from the Mississippian crinoid gardens of Indiana and Iowa where sea lilies grew in meadows.",
  hab=["shelf"], cls=("Crinoidea", "Camerata", "Platycrinitidae"))
E("Aviculopecten", "genus", "sea", "bivalve", 360, 252, ["cosmo"],
  "A scallop-like bivalve of the late Palaeozoic, in every shelf sea from the Mississippian to the end of the Permian.",
  hab=["shelf"], cls=("Bivalvia", "Pectinida", "Aviculopectinidae"))
E("Bellerophon", "genus", "sea", "seasnail", 360, 252, ["cosmo"],
  "A planispiral snail-like mollusc, coiled in one plane like a tiny nautilus, grazing Carboniferous and Permian sea floors.",
  hab=["shelf"], cls=("Gastropoda", "Bellerophontida", "Bellerophontidae"))
E("Goniatites", "genus", "sea", "ammonite", 335, 326, ["cosmo"],
  "The goniatite that names its group: a globular ammonoid with zigzag sutures, a swimmer of Mississippian seas on every continent.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Goniatitidae"))
E("Edestus", "genus", "sea", "shark", 315, 305, ["na-e", "eu", "as-n"],
  "The 'scissor-tooth shark', with a single blade of teeth in each jaw that never shed; a Pennsylvanian predator the size of a great white.",
  hab=["pelagic", "shelf"], cls=("Chondrichthyes", "Eugeneodontida", "Edestidae"))
E("Stethacanthus", "genus", "sea", "shark", 380, 320, ["na-e", "na-w", "eu", "as-n", "au"],
  "A shark whose males carried an anvil-shaped fin on the back topped with a brush of tooth-like scales: display, most likely.",
  hab=["shelf", "pelagic"], cls=("Chondrichthyes", "Symmoriiformes", "Stethacanthidae"))
E("Lophophyllidium", "genus", "sea", "horncoral", 320, 252, ["na-e", "na-w", "eu", "as-e"],
  "A small solitary horn coral of Pennsylvanian and Permian shelves, standing alone in the mud between the brachiopod beds.",
  hab=["shelf"], cls=("Anthozoa", "Rugosa", "Lophophyllidiidae"))
E("Neospirifer", "genus", "sea", "brachiopod", 320, 252, ["cosmo"],
  "A winged, strongly ribbed spiriferid brachiopod, common enough in the Permian to have been used as a guide fossil across Pangaea's shelves.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferida", "Trigonotretidae"))

# ------------------------------------------------------------------- Permian
E("Waagenoconcha", "genus", "sea", "brachiopod", 295, 252, ["cosmo"],
  "A spiny productid brachiopod that anchored itself in soft mud with hair-fine spines, a Permian shell of cool and warm seas alike.",
  hab=["shelf"], cls=("Strophomenata", "Productida", "Productidae"))
E("Leptodus", "genus", "sea", "brachiopod", 275, 252, TETH + ["na-w"],
  "A brachiopod so modified for reef life it looks like an oyster: cemented, with a comb of internal ridges; one of the odd forms of the Permian reefs of Texas and the Tethys.",
  hab=["reef"], cls=("Strophomenata", "Productida", "Lyttoniidae"))
E("Girtyocoelia", "genus", "sea", "sponge", 300, 252, ["na-w", "na-e", "tet", "eu"],
  "A sphinctozoan sponge, a string of beads with a canal through them, one of the builders of the Permian Reef of Texas.",
  hab=["reef"], cls=("Demospongiae", "", "Sebargasiidae"))
E("Xenacanthus", "genus", "sea", "shark", 360, 252, ["euramerica", "as-e", "in", "au", "sa-s"],
  "A freshwater shark with an eel's body and a long spine at the back of the head, hunting the coal-swamp rivers and lakes for a hundred million years.",
  hab=["river", "lake", "wetland"], realms=["fresh"], cls=("Chondrichthyes", "Xenacanthiformes", "Xenacanthidae"))
E("Timorites", "genus", "sea", "ammonite", 260, 252, ["tet", "as-se", "au", "as-w", "na-w"],
  "A Late Permian ammonoid with complex sutures on the road to the ammonites proper, from the Tethyan reefs of Timor.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Cyclolobidae"))

# ------------------------------------------------------------------ Triassic
E("Monotis", "genus", "sea", "bivalve", 215, 205, ["cosmo"],
  "A thin-shelled bivalve that drifted or lay in shoals over the whole Late Triassic ocean; its beds date Norian rocks from Alaska to New Zealand.",
  hab=["pelagic", "shelf"], cls=("Bivalvia", "Pectinida", "Monotidae"))
E("Mixosaurus", "genus", "sea", "ichthyosaur", 247, 237, ["tet", "eu", "as-e", "pan", "na-w", "as-se"],
  "A metre-long early ichthyosaur with a fish's tail only half formed, from the Middle Triassic of the Alps, China and Nevada.",
  hab=["pelagic", "shelf"], cls=("Reptilia", "Ichthyosauria", "Mixosauridae"))
E("Cymbospondylus", "genus", "sea", "ichthyosaur", 247, 237, ["na-w", "pan", "eu", "tet"],
  "An early ichthyosaur up to seventeen metres long with an eel-like body and no dorsal fin, from Nevada's Middle Triassic sea.",
  hab=["pelagic"], cls=("Reptilia", "Ichthyosauria", "Cymbospondylidae"))
E("Thalattosauria", "order", "sea", "nothosaur", 247, 205, ["pan", "na-w", "as-e", "eu", "tet"],
  "Thalattosaurs, long-tailed marine reptiles of the Triassic with pointed down-turned snouts, from the shores of Panthalassa and the Tethys.",
  hab=["coast", "shelf"], cls=("Reptilia", "Thalattosauria", ""))
E("Trachyceras", "genus", "sea", "ammonite", 237, 227, ["tet", "eu", "as-e", "pan", "na-w"],
  "A knobbly ceratitid ammonoid of the Carnian, in the Alps and the Tethys; its extinction near the Carnian Pluvial Episode.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Trachyceratidae"))
E("Tropites", "genus", "sea", "ammonite", 232, 227, ["tet", "eu", "as-e", "pan", "na-w"],
  "A globular Carnian ammonoid, the zone fossil of the late Carnian on both sides of Pangaea.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Tropitidae"))
E("Rhaetavicula", "genus", "sea", "mussel", 208, 201, ["eu", "tet", "na-e", "atl"],
  "The 'Rhaetic bone bed' bivalve, small and asymmetric, crowding the last sea floors of the Triassic in Europe.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Pterioida", "Bakevelliidae"))
E("Saurichthys", "genus", "sea", "bigfish", 250, 201, ["cosmo"],
  "A pike-shaped ray-finned fish with a long toothed snout, an ambush predator of Triassic seas and lakes worldwide.",
  hab=["shelf", "pelagic", "lake"], realms=["sea", "fresh"], cls=("Actinopterygii", "Saurichthyiformes", "Saurichthyidae"))

# ------------------------------------------------------------------ Jurassic
E("Dactylioceras", "genus", "sea", "ammonite", 183, 178, ["eu", "tet", "atl", "na-w", "sa-s", "as-e"],
  "The Whitby ammonite, ribbed and evolute, once carved with snakes' heads and sold as the serpents St Hilda turned to stone.",
  hab=["pelagic", "shelf"], w=2, cls=("Cephalopoda", "Ammonitida", "Dactylioceratidae"))
E("Perisphinctes", "genus", "sea", "ammonite", 163, 155, ["cosmo"],
  "A large evolute ammonite with forked ribs, common enough in the Oxfordian to be found in Europe, East Africa, Cuba and Japan.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Perisphinctidae"))
E("Leedsichthys", "genus", "sea", "bigfish", 165, 152, ["eu", "tet", "atl", "sa-s"],
  "The largest ray-finned fish that has ever lived, sixteen metres of filter-feeder from the Oxford Clay, straining the Jurassic sea like a whale shark.",
  hab=["pelagic"], w=3, cls=("Actinopterygii", "Pachycormiformes", "Pachycormidae"))
E("Ophthalmosaurus", "genus", "sea", "ichthyosaur", 165, 155, ["eu", "atl", "na-w", "sa-s"],
  "An ichthyosaur with eyes the size of dinner plates, the largest of any vertebrate relative to its body, for hunting squid in the dark.",
  hab=["pelagic"], cls=("Reptilia", "Ichthyosauria", "Ophthalmosauridae"))
E("Metriorhynchus", "genus", "sea", "seacroc", 165, 155, ["eu", "atl", "tet", "sa-s"],
  "A crocodile rebuilt for the open sea: flippers, a tail fin, no armour, hunting fish and ammonites in the Oxford Clay.",
  hab=["pelagic", "shelf"], cls=("Reptilia", "Thalattosuchia", "Metriorhynchidae"))
E("Rhomaleosaurus", "genus", "sea", "pliosaur", 183, 176, ["eu", "atl"],
  "A seven-metre pliosaur of the Early Jurassic, with nostrils built to smell under water, from the same Yorkshire and Somerset shales as Dactylioceras.",
  hab=["shelf", "pelagic"], cls=("Reptilia", "Plesiosauria", "Rhomaleosauridae"))
E("Cryptoclidus", "genus", "sea", "plesiosaur", 165, 160, ["eu", "atl"],
  "A long-necked plesiosaur of the Oxford Clay with a hundred needle teeth, netting small fish and squid.",
  hab=["shelf", "pelagic"], cls=("Reptilia", "Plesiosauria", "Cryptoclididae"))
E("Trigonia", "genus", "sea", "bivalve", 200, 66, ["cosmo"],
  "A thick, ornamented triangular clam that burrowed Jurassic and Cretaceous sands worldwide; a lone survivor, Neotrigonia, still lives off Australia.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Trigoniida", "Trigoniidae"))
E("Lithiotis", "genus", "sea", "oyster", 190, 180, ["tet", "eu", "af-n", "as-w", "na-w", "as-se"],
  "A tall, wafer-thin bivalve that grew in dense upright thickets, the reef-builder of the Early Jurassic Tethys when corals were scarce.",
  hab=["reef", "coast"], cls=("Bivalvia", "Ostreida", "Lithiotidae"))
E("Pleurotomaria", "genus", "sea", "seasnail", 200, 100, ["cosmo"],
  "A slit-shelled sea snail of Jurassic and Cretaceous shelves; its relatives survive today only in deep water.",
  hab=["shelf"], cls=("Gastropoda", "Pleurotomariida", "Pleurotomariidae"))
E("Hybodus", "genus", "sea", "shark", 250, 100, ["cosmo"],
  "A hybodont shark with a spine before each dorsal fin and two kinds of teeth, for fish and for shellfish; the commonest shark of Mesozoic seas and rivers.",
  hab=["shelf", "coast", "river"], realms=["sea", "fresh"], cls=("Chondrichthyes", "Hybodontiformes", "Hybodontidae"))
E("Ichthyornis", "genus", "air", "earlybird", 95, 83, WIS,
  "A tern-sized seabird with teeth, skimming the Western Interior Seaway; among the closest known relatives of modern birds.",
  hab=["pelagic", "coast", "shelf"], realms=["air", "sea"], cls=("Aves", "Ichthyornithiformes", "Ichthyornithidae"))

# ---------------------------------------------------------------- Cretaceous
E("Exogyra", "genus", "sea", "oyster", 160, 66, ["cosmo"],
  "A thick, coiled oyster with a spiral beak, cemented to the Cretaceous sea floor in beds you can walk on in Texas and Alabama.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Ostreida", "Gryphaeidae"))
E("Durania", "genus", "sea", "rudist", 100, 66, TETH + ["ca", "atl", "na-e"],
  "A barrel-shaped rudist, one of the strange bivalves that grew in thickets and built the reefs of the Late Cretaceous tropics in place of corals.",
  hab=["reef"], cls=("Bivalvia", "Hippuritida", "Radiolitidae"))
E("Ptychodus", "genus", "sea", "shark", 100, 84, ["cosmo"],
  "A shark with pavement teeth for crushing clams, ten metres long, a Cretaceous durophage whose teeth litter the chalk seas of two hemispheres.",
  hab=["shelf"], cls=("Chondrichthyes", "Ptychodontiformes", "Ptychodontidae"))
E("Cretoxyrhina", "genus", "sea", "shark", 107, 73, ["cosmo"],
  "The 'Ginsu shark', seven metres long, whose bite marks are on the bones of mosasaurs and plesiosaurs from Kansas to Europe.",
  hab=["pelagic", "shelf"], cls=("Chondrichthyes", "Lamniformes", "Cretoxyrhinidae"))
E("Squalicorax", "genus", "sea", "shark", 105, 66, ["cosmo"],
  "The crow shark, a scavenger of the Cretaceous seas whose serrated teeth are found lodged in dinosaur bones washed out to sea.",
  hab=["shelf", "coast"], cls=("Chondrichthyes", "Lamniformes", "Anacoracidae"))
E("Elasmosaurus", "genus", "sea", "plesiosaur", 81, 80, WIS,
  "A plesiosaur with seventy-two neck vertebrae and a neck seven metres long, from the Kansas chalk; its first describer put the head on the tail.",
  hab=["pelagic", "shelf"], w=2, cls=("Reptilia", "Plesiosauria", "Elasmosauridae"))
E("Protostega", "genus", "sea", "seaturtle", 85, 80, WIS,
  "A three-metre sea turtle of the Western Interior Seaway, ancestor in form to Archelon, with a shell reduced to struts.",
  hab=["pelagic", "shelf"], cls=("Reptilia", "Testudines", "Protostegidae"))
E("Pachydiscus", "genus", "sea", "ammonite", 84, 66, ["cosmo"],
  "A late ammonite that grew shells a metre across, among the last of its kind, in the seas of the final Cretaceous stages worldwide.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ammonitida", "Pachydiscidae"))
E("Hoploscaphites", "genus", "sea", "heteromorph", 75, 66, WIS + ["eu", "atl"],
  "A hook-shaped scaphitid ammonite of the Pierre Shale and the Maastrichtian chalk, one of the very last ammonites before the impact.",
  hab=["shelf"], cls=("Cephalopoda", "Ammonitida", "Scaphitidae"))
E("Toxochelys", "genus", "sea", "seaturtle", 86, 72, WIS,
  "A metre-long sea turtle of the Niobrara chalk, close to the stem of the living sea turtles.",
  hab=["shelf", "coast"], cls=("Reptilia", "Testudines", "Toxochelyidae"))
E("Platecarpus", "genus", "sea", "mosasaur", 84, 81, WIS + ["eu", "af-n", "atl"],
  "A mid-sized mosasaur, the commonest in the Kansas chalk, preserved with skin, a forked tail fin and the contents of its gut.",
  hab=["pelagic", "shelf"], cls=("Reptilia", "Squamata", "Mosasauridae"))
E("Clidastes", "genus", "sea", "mosasaur", 85, 72, WIS + ["eu", "atl"],
  "A slender, fast mosasaur of shallow water, the smallest of the Kansas chalk mosasaurs at two to four metres.",
  hab=["shelf", "coast"], cls=("Reptilia", "Squamata", "Mosasauridae"))
E("Uintacrinus", "genus", "sea", "crinoid", 86, 84, WIS + ["eu"],
  "A stalkless crinoid that drifted in colonies of hundreds and sank together, leaving slabs of the Kansas chalk covered in its arms.",
  hab=["pelagic"], cls=("Crinoidea", "Articulata", "Uintacrinidae"))
E("Bananogmius", "genus", "sea", "fish", 90, 84, WIS,
  "A deep-bodied plethodid fish of the Niobrara sea with a fan-like dorsal fin the length of its back.",
  hab=["pelagic", "shelf"], cls=("Actinopterygii", "Tselfatiiformes", "Plethodidae"))
E("Pteranodon", "genus", "air", "pterosaur", 86, 84, WIS,
  "A pterosaur with a seven-metre wingspan and a blade of a crest, fishing far out over the Western Interior Seaway.",
  hab=["pelagic", "coast"], realms=["air", "sea"], w=3, cls=("Reptilia", "Pterosauria", "Pteranodontidae"))
E("Nyctosaurus", "genus", "air", "pterosaur", 85, 84, WIS,
  "A small pterosaur of the Kansas chalk with an antler-like crest half again as long as its skull.",
  hab=["pelagic", "coast"], realms=["air", "sea"], cls=("Reptilia", "Pterosauria", "Nyctosauridae"))
E("Globotruncana", "genus", "sea", "foram", 90, 66, ["cosmo"],
  "A planktonic foraminifer with a double keel, the zone fossil of the Late Cretaceous ocean; the K-Pg boundary clay is full of its broken shells.",
  hab=["pelagic"], cls=("Globothalamea", "Rotaliida", "Globotruncanidae"))
E("Thalassinoides", "informal", "sea", "strata", 500, 0, ["cosmo"],
  "Thalassinoides: the branching burrow systems of shrimps and their forebears, a trace fossil that turns Cretaceous chalk and Jurassic limestone into a network of tunnels.",
  hab=["shelf"], fill=None)
E("Micraster", "genus", "sea", "seaurchin", 90, 66, ["eu", "atl", "af-n", "as-w", "na-e", "ca"],
  "The heart urchin of the English chalk, whose changing shape up through the cliffs was one of the first fossil lineages read as evolution.",
  hab=["shelf"], cls=("Echinoidea", "Spatangoida", "Micrasteridae"))
E("Belemnitella", "genus", "sea", "belemnite", 84, 66, ["eu", "atl", "na-e", "arc"],
  "A Late Cretaceous belemnite whose bullet-shaped guards fill the Maastricht chalk; its oxygen isotopes were among the first used to read past sea temperatures.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Belemnitida", "Belemnitellidae"))
E("Nautilus", "genus", "sea", "nautilus", 35, 0, ["ind", "pac"],
  "The living Nautilus, a survivor of the once-vast shelled-cephalopod dynasties, still hauls its chambered shell up Indo-Pacific reef slopes at night.",
  hab=["deep", "reef"], lat=[0, 35], box=[[90, 180, -30, 20]], w=2,
  cls=("Cephalopoda", "Nautilida", "Nautilidae"))
write("x-marine-depth.json")
