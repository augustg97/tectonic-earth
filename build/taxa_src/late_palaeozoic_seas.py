"""The Devonian, Carboniferous and Permian seas beyond North America, and the
Ediacaran at genus level.

The first marine batch drew on the Laurentian shelf; the Rhenish and Cathaysian
shelves, the Ural Ocean, the Gondwanan cool-water seas and the Tethyan reefs of
Permian Asia were still "Brachiopoda, Rugosa, Fusulinida". The PBDB menus for
eu, as-e, au, af, sa and in rank these highest.

The Ediacaran's three assemblages -- Avalon, White Sea, Nama -- were curated by
name; their genera were not all in the registry.
"""
from _lib import E, T, write

RHENISH = ["eu", "af-n", "rhe", "ura"]
CATH = ["as-ne", "as-s", "as-ic", "tet"]
GONDW = ["au", "sa-s", "sa-n", "af-s", "in", "an", "as-sb"]

# ------------------------------------------------------------------ Devonian
E("Palmatolepis", "genus", "sea", "conodont", 385, 359, ["cosmo"],
  "The Late Devonian conodont whose platform elements zone the Frasnian and Famennian on every continent, and whose lineages thin out across the Kellwasser extinction.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Palmatolepidae"))
E("Polygnathus", "genus", "sea", "conodont", 410, 300, ["cosmo"],
  "A conodont genus of a hundred species that carries the Devonian time scale, from the Rhenish shelf to Guangxi.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Polygnathidae"))
E("Schizophoria", "genus", "sea", "brachiopod", 420, 300, ["cosmo"],
  "A rounded, finely ribbed orthid brachiopod, one of the commonest shells of Devonian and Carboniferous shelves from Germany to China and Australia.",
  hab=["shelf"], cls=("Rhynchonellata", "Orthida", "Schizophoriidae"))
E("Athyris", "genus", "sea", "brachiopod", 420, 350, ["cosmo"],
  "A smooth spiral-brachidium brachiopod with frilled growth lamellae, common in the Rhenish Devonian and the Ural Ocean's shelves.",
  hab=["shelf"], cls=("Rhynchonellata", "Athyridida", "Athyrididae"))
E("Reedops", "genus", "sea", "trilobite", 410, 385, ["af-n", "eu", "rhe"],
  "A phacopid trilobite of the Devonian of Morocco and Bohemia, one of the enrolled trilobites quarried from the Anti-Atlas by the thousand.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Phacopidae"))
E("Anarcestes", "genus", "sea", "ammonite", 405, 395, ["af-n", "eu", "rhe", "as-ne", "as-s"],
  "One of the first ammonoids, a small coiled goniatite of the Emsian seas of Morocco and the Rhenish shelf: the beginning of a lineage that lasted 340 million years.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Agoniatitida", "Anarcestidae"))
E("Cymaclymenia", "genus", "sea", "ammonite", 370, 359, ["af-n", "eu", "rhe", "as-ne", "as-s", "au"],
  "A clymeniid ammonoid, its siphuncle on the inside of the coil, of the last Devonian stage: the group appeared and vanished within the Famennian.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Clymeniida", "Cymaclymeniidae"))
E("Sporadoceras", "genus", "sea", "ammonite", 375, 359, ["cosmo"],
  "A globular Late Devonian goniatite of the open shelf, from the Canning Basin of Australia to the Rhenish Massif.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Sporadoceratidae"))
E("Gerastos", "genus", "sea", "trilobite", 410, 380, ["eu", "af-n", "rhe", "as-ne", "as-s", "na-e", "na-w"],
  "A small proetid trilobite of the Devonian of Morocco and the Rhenish shelf, the proetids being the family that would outlast every other trilobite.",
  hab=["shelf", "reef"], cls=("Trilobita", "Proetida", "Proetidae"))
E("Straparollus", "genus", "sea", "seasnail", 420, 252, ["cosmo"],
  "A wide, flat-coiled euomphalid sea snail of Devonian to Permian shelves, grazing the reef flats of the Rhenish Massif and the Urals.",
  hab=["shelf", "reef"], cls=("Gastropoda", "Euomphalina", "Euomphalidae"))
E("Canning Basin reef fauna", "informal", "sea", "stromatoporoid", 385, 359, ["au"],
  "The Devonian barrier reef of the Canning Basin, Western Australia, three hundred kilometres of stromatoporoid and coral reef preserved so completely that its fore-reef slopes still stand in the desert.",
  hab=["reef"], rep="Stromatoporoidea", assemblage=True)
E("Metacryphaeus", "genus", "sea", "trilobite", 410, 385, ["sa-s", "sa-n", "af-s", "an"],
  "A calmoniid trilobite of the Malvinokaffric Realm, the cold Devonian shelves of Brazil, Bolivia and the Falklands, with spines and a raised tail.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Calmoniidae"))
E("Orbiculoidea", "genus", "sea", "lingulid", 440, 252, ["cosmo"],
  "A disc-shaped phosphatic brachiopod that fastened to shells and driftwood, thriving in the oxygen-poor muds of the Gondwanan Devonian.",
  hab=["shelf", "coast"], cls=("Lingulata", "Lingulida", "Discinidae"))

# ------------------------------------------------------------- Carboniferous
E("Siphonodella", "genus", "sea", "conodont", 360, 345, ["cosmo"],
  "The conodont whose first appearance was chosen to mark the base of the Carboniferous, in the Tournaisian seas of China and Europe.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", "Polygnathidae"))
E("Siphonodendron", "genus", "sea", "horncoral", 345, 320, ["eu", "af-n", "as-ne", "as-s", "as-c", "na-e"],
  "A colonial rugose coral in bundles of narrow tubes, the reef-builder of Mississippian limestones from Britain to the Sahara and North China.",
  hab=["reef", "shelf"], cls=("Anthozoa", "Rugosa", "Lithostrotionidae"))
E("Caninia", "genus", "sea", "horncoral", 350, 300, ["cosmo"],
  "A large solitary horn coral of Carboniferous shelves, standing a hand's length high in the mud of the Ural Ocean and the European shelves.",
  hab=["shelf"], cls=("Anthozoa", "Rugosa", "Cyathopsidae"))
E("Elonichthys", "genus", "sea", "fish", 340, 300, ["eu", "na-e", "as-ne"],
  "A palaeoniscoid ray-finned fish with heavy rhombic scales, the commonest fish of Carboniferous lagoons and coal-swamp lakes in Europe.",
  hab=["coast", "lake", "river"], realms=["sea", "fresh"], cls=("Actinopterygii", "Palaeonisciformes", "Elonichthyidae"))
E("Eomarginifera", "genus", "sea", "brachiopod", 345, 310, ["eu", "as-c", "ura", "rhe"],
  "A small spiny productid brachiopod of the Carboniferous shelves of Europe and the Urals.",
  hab=["shelf"], cls=("Strophomenata", "Productida", "Productellidae"))
E("Dombarites", "genus", "sea", "ammonite", 330, 320, ["eu", "as-c", "ura"],
  "A Serpukhovian goniatite of the Ural Ocean, from the Dombar hills of Kazakhstan where the stage was named.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Delepinoceratidae"))
E("Fenestella", "genus", "sea", "bryozoan", 440, 252, ["cosmo"],
  "The lace bryozoan, a fan of branches joined by crossbars, on Carboniferous and Permian sea floors from Australia to the Urals.",
  hab=["shelf"], cls=("Stenolaemata", "Fenestrata", "Fenestellidae"))
E("Spirifer", "genus", "sea", "brachiopod", 360, 300, ["cosmo"],
  "The winged spiriferid brachiopod itself, broad and ribbed, of Carboniferous shelves the world over.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferida", "Spiriferidae"))
E("Levipustula", "genus", "sea", "brachiopod", 325, 305, ["au", "sa-s", "an", "as-sb"],
  "A productid brachiopod of the cold Carboniferous seas of eastern Australia and Argentina, in beds with dropstones from the Gondwanan ice.",
  hab=["shelf", "ice"], cls=("Strophomenata", "Productida", "Productellidae"))
E("Pericyclus", "genus", "sea", "ammonite", 350, 340, ["af-n", "eu", "as-c", "na-w", "as-ne"],
  "A ribbed goniatite of the Tournaisian, in the black shales of the Sahara and the Rhenish shelf.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Goniatitida", "Pericyclidae"))
E("Syringothyris", "genus", "sea", "brachiopod", 360, 320, ["cosmo"],
  "A large, high-beaked spiriferinid brachiopod of Mississippian shelves, from the Himalayan margin of India to Ireland.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferinida", "Syringothyrididae"))
E("Rhombopora", "genus", "sea", "bryozoan", 345, 252, ["cosmo"],
  "A twig-like bryozoan of late Palaeozoic shelves, its branches in every Permian limestone of Brazil and the Urals.",
  hab=["shelf"], cls=("Stenolaemata", "Rhabdomesida", "Rhomboporidae"))

# -------------------------------------------------------------------- Permian
E("Spinomarginifera", "genus", "sea", "brachiopod", 280, 252, CATH + ["eu", "as-w", "ar", "as-c"],
  "A spiny productid brachiopod, the commonest shell of the Permian Tethys from Transcaucasia to South China; its last species die at the boundary.",
  hab=["shelf"], cls=("Strophomenata", "Productida", ""))
E("Neochonetes", "genus", "sea", "brachiopod", 300, 252, ["cosmo"],
  "A small chonetid brachiopod with spines along the hinge, on Permian sea floors by the thousand, in South China above all.",
  hab=["shelf"], cls=("Strophomenata", "Productida", "Rugosochonetidae"))
E("Orthothetina", "genus", "sea", "brachiopod", 300, 252, ["cosmo"],
  "A flat, fan-shaped brachiopod of the Permian shelves of the Tethys and the Urals.",
  hab=["shelf"], cls=("Strophomenata", "Orthotetida", "Meekellidae"))
E("Permophricodothyris", "genus", "sea", "brachiopod", 290, 252, CATH + ["af-n", "as-w", "ar", "eu"],
  "A spiriferide brachiopod of the Permian Tethys, from the reefs of Tunisia to the Cathaysian shelves.",
  hab=["shelf", "reef"], cls=("Rhynchonellata", "Spiriferida", "Elythidae"))
E("Paratirolites", "genus", "sea", "ammonite", 254, 252, ["as-w", "eu", "tet", "as-c", "ar"],
  "The last ammonoid of the Permian in Transcaucasia and Iran, its beds ending at the extinction horizon.",
  hab=["pelagic", "shelf"], cls=("Cephalopoda", "Ceratitida", "Dzhulfitidae"))
E("Dielasma", "genus", "sea", "brachiopod", 300, 252, ["cosmo"],
  "A smooth terebratulid brachiopod of Permian reefs and shelves, on the Zechstein reef and in the Tethys.",
  hab=["reef", "shelf"], cls=("Rhynchonellata", "Terebratulida", "Dielasmatidae"))
E("Schizodus", "genus", "sea", "clam", 320, 252, ["cosmo"],
  "A smooth triangular clam of late Palaeozoic shelves, burrowing the Permian sands of the Zechstein and the Ural Ocean.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Trigoniida", "Schizodidae"))
E("Terrakea", "genus", "sea", "brachiopod", 290, 255, ["au", "an", "as-sb"],
  "A spiny productid brachiopod of the cool Permian seas of eastern Australia, the commonest fossil of the Sydney Basin marine beds.",
  hab=["shelf"], cls=("Strophomenata", "Productida", "Linoproductidae"))
E("Echinalosia", "genus", "sea", "brachiopod", 290, 255, ["au", "an", "nz", "in"],
  "A cool-water strophalosiid brachiopod of Permian eastern Australia, cemented to the sea floor by its spines.",
  hab=["shelf"], cls=("Strophomenata", "Productida", "Strophalosiidae"))
E("Ingelarella", "genus", "sea", "brachiopod", 290, 255, ["au", "an", "nz", "sa-s"],
  "A spiriferide brachiopod of the Gondwanan cool-water Permian, from Queensland to Antarctica.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferida", "Ingelarellidae"))
E("Spirigerella", "genus", "sea", "brachiopod", 290, 252, ["in", "as-c", "as-w", "tet", "as-sb"],
  "An athyridid brachiopod of the Permian of the Salt Range and the Himalayan margin, the commonest shell of the Tethyan shelf of India.",
  hab=["shelf"], cls=("Rhynchonellata", "Athyridida", "Athyrididae"))
E("Marginifera", "genus", "sea", "brachiopod", 300, 252, ["cosmo"],
  "A small productid brachiopod with a ridged margin, on Permian sea floors from the Salt Range to Texas.",
  hab=["shelf"], cls=("Strophomenata", "Productida", ""))
E("Stellispongiella", "genus", "sea", "sponge", 275, 252, ["af-n", "tet", "as-w", "eu"],
  "A calcified sponge of the Permian reefs of Tunisia, where sponges, not corals, built the reef.",
  hab=["reef"], cls=("Demospongiae", "Agelasida", "Stellispongiellidae"))
E("Enteletes", "genus", "sea", "brachiopod", 320, 252, ["cosmo"],
  "A globular, plicate orthid brachiopod of Permian shelves and reefs, from the Tethys to the Glass Mountains.",
  hab=["shelf", "reef"], cls=("Rhynchonellata", "Orthida", "Enteletidae"))
E("Pinzonella", "genus", "sea", "clam", 270, 252, ["sa-s", "sa-n"],
  "An endemic clam of the Permian Passa Dois seaway of Brazil, an inland sea of Gondwana that had its own molluscs and nothing else's.",
  hab=["shelf", "coast"], cls=("Bivalvia", "Carditida", "Astartidae"))
E("Hustedia", "genus", "sea", "brachiopod", 320, 252, ["cosmo"],
  "A small ribbed athyridid brachiopod of late Palaeozoic shelves, from the Brazilian Permian to the Glass Mountains of Texas.",
  hab=["shelf"], cls=("Rhynchonellata", "Athyridida", "Neoretziidae"))

# ------------------------------------------------------------------ Ediacaran
E("Fractofusus", "genus", "sea", "quilt", 575, 560, ["na-e", "eu", "iap"],
  "A spindle-shaped rangeomorph lying flat on the deep sea floor at Mistaken Point, its fractal branches repeating at four scales; the commonest fossil of the Avalon assemblage.",
  hab=["deep"], cls=("", "Rangeomorpha", ""))
E("Charniodiscus", "genus", "sea", "frond", 575, 555, ["na-e", "eu", "au", "iap"],
  "A frond on a stalk with a holdfast disc, standing in the current from Newfoundland to the Flinders Ranges; the disc was found first and named alone.",
  hab=["deep", "shelf"], cls=("", "Arboreomorpha", ""))
E("Thectardis", "genus", "sea", "sponge", 575, 565, ["na-e"],
  "A triangular, cone-shaped organism of the Avalon deep sea floor, read by some as the oldest sponge.",
  hab=["deep"], cls=("", "", ""))
E("Bradgatia", "genus", "sea", "quilt", 575, 560, ["na-e", "eu", "iap"],
  "A bush-shaped rangeomorph of the Avalon assemblage, its fronds radiating from the base like a lettuce.",
  hab=["deep"], cls=("", "Rangeomorpha", ""))
E("Andiva", "genus", "sea", "quilt", 558, 550, ["eu", "as-n"],
  "A bilaterally segmented, shield-shaped animal of the White Sea assemblage, one of the forms that made the Ediacaran seem an animal world.",
  hab=["shelf"], cls=("", "Proarticulata", ""))
E("Parvancorina", "genus", "sea", "cambrianarthropod", 558, 550, ["au", "eu", "as-n"],
  "A shield-shaped animal a centimetre long with an anchor-shaped ridge, from the Flinders Ranges and the White Sea, that could orient itself to the current.",
  hab=["shelf"], cls=("", "", ""))
E("Arkarua", "genus", "sea", "starfish", 558, 550, ["au"],
  "A disc with five-fold symmetry from the Flinders Ranges, the earliest candidate echinoderm.",
  hab=["shelf"], cls=("", "", ""))
E("Cloudina", "genus", "sea", "tubeworm", 550, 539, ["cosmo"],
  "The first animal to build a mineral skeleton: stacked cones of calcite in reefs on the Nama shelf, some of them bored by the first predator.",
  hab=["reef", "shelf"], w=2, cls=("", "", "Cloudinidae"))
E("Namacalathus", "genus", "sea", "goblet", 549, 539, ["af-s", "sa-s", "eu", "as-n", "ca"],
  "A stalked goblet of calcite with windows in its cup, standing beside Cloudina on the last Ediacaran reefs.",
  hab=["reef", "shelf"], cls=("", "", ""))
E("Swartpuntia", "genus", "sea", "frond", 545, 539, ["af-s", "na-w"],
  "A three-winged frond of the Nama assemblage, one of the last of the Ediacaran soft-bodied forms, surviving into the first million years of the Cambrian.",
  hab=["shelf"], cls=("", "Erniettomorpha", ""))
write("x-late-palaeozoic-seas.json")
