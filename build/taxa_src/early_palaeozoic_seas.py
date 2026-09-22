"""The Tonian cratons, the Ediacaran assemblages at genus level, and the
Cambrian-Silurian seas by block.

Measured on the shipped life.json before this batch: the most generic marine
slot-ages of the early Palaeozoic were Dasycladales, Chlorophyta, Rhodophyta,
Orthida, Graptolithina, hyoliths, Hexactinellida and Trilobita, nearly all on
the Gondwanan shelves (the Sahara, Amazonia, the Congo, Antarctica) and the
ocean cards; of the Precambrian, Chlorophyta / Rhodophyta / Porifera on the
West African, Congo, Kalahari and Sao Francisco cratons, which had no named
assemblage of their own. This batch gives those cards the record's own names:
the Atar and Mbuji-Mayi microfossils, the Rasthof cap-carbonate mats, the
White Sea and Nama genera not yet registered, the Moroccan and Bohemian
Cambrian trilobites, the Tremadocian olenids of Argentina and Oaxaca, the
Mediterranean-province trilobites of the Ordovician, the zone graptolites and
conodonts, and the tabulates, bryozoans, brachiopods and calcareous algae of
the Ordovician-Silurian shelves.
"""
from _lib import E, T, write

# ------------------------------------------------------- the Tonian cratons
E("Atar Group microfossils", "informal", "sea", "cyano", 1100, 950, ["af-n", "af-w"],
  "The cherts and shales of the Atar and El Mreiti groups of the Taoudeni basin of Mauritania, about 1.1 billion years old: cyanobacterial mats, colonial cells and the cysts of early eukaryotes, on a shallow sea over the West African craton.",
  hab=["coast", "shelf"], rep="Siphonophycus", assemblage=True)
E("Rasthof microbialites", "informal", "sea", "stromatolite", 662, 650, ["af-s"],
  "The cap carbonate laid over the Sturtian glacial deposits of the Otavi Group of Namibia: roll-up microbial mats metres thick, the first life of the sea floor after the snowball ice withdrew.",
  hab=["coast", "shelf"], rep="Stromatolites", assemblage=True)
E("Chuaria", "genus", "sea", "acritarch", 1100, 560, ["cosmo"],
  "A carbonaceous disc a few millimetres across, among the commonest large fossils of the Proterozoic, from the Grand Canyon to the Vindhyan of India: the compressed remains of a large-celled eukaryote or a colony.",
  hab=["shelf", "pelagic"], cls=("", "", ""))
E("Tawuia", "genus", "sea", "acritarch", 1000, 560, ["cosmo"],
  "A sausage-shaped carbonaceous compression a centimetre long, found with Chuaria in Tonian and Ediacaran shales worldwide; read as a macroalga or a coenocytic organism.",
  hab=["shelf"], cls=("", "", ""))
E("Ourasphaira giraldae", "species", "sea", "hyphae", 1010, 890, ["na-n"],
  "Branching filaments with chitin in their walls, from the Grassy Bay Formation of Arctic Canada: the oldest fossil that can be argued to be a fungus, a billion years old.",
  hab=["coast", "shelf"], cls=("", "", ""))

# ------------------------------------------------------- the Ediacaran, more
E("Vendia", "genus", "sea", "quilt", 558, 550, ["eu-n"],
  "A small segmented Ediacaran of the White Sea, a centimetre long, with the offset left-right quilting of Dickinsonia's kin; the genus that named the Vendian.",
  hab=["shelf"], cls=("", "Proarticulata", ""))
E("Cyclomedusa", "genus", "sea", "jellyfish", 570, 545, ["cosmo"],
  "Concentric discs pressed into Ediacaran sandstones on every continent, named as a jellyfish and now read as the holdfasts of fronds and the marks of microbial colonies.",
  hab=["shelf"], cls=("", "", ""))
E("Aspidella", "genus", "sea", "jellyfish", 575, 541, ["na-av", "eu-n", "au-e", "as-n"],
  "The holdfast disc of Newfoundland's Fermeuse Formation, the first Ediacaran fossil ever named (1872) and dismissed for a century; thousands cover some bedding planes.",
  hab=["shelf", "deep"], cls=("", "", ""))
E("Eoandromeda", "genus", "sea", "jellyfish", 560, 550, ["as-s", "au-e"],
  "An eight-armed spiral a few centimetres across, in the Doushantuo shales of South China and the Ediacara sandstones of the Flinders Ranges: the same animal on two continents, and a candidate ctenophore.",
  hab=["shelf"], cls=("", "", ""))
E("Inaria", "genus", "sea", "jellyfish", 560, 550, ["au-e"],
  "A sac-like Ediacaran body with a lobed base, from the Flinders Ranges, read as a sea-anemone-like animal buried in life position.",
  hab=["shelf"], cls=("", "", ""))
E("Palaeopascichnus", "genus", "sea", "strata", 570, 541, ["cosmo"],
  "Chains of repeating chambers on Ediacaran bedding planes, once taken for a trail and now for the body of a giant protist growing chamber by chamber, worldwide.",
  hab=["shelf", "deep"], cls=("", "", ""))
E("Namapoikia", "genus", "sea", "sponge", 549, 543, ["af-s"],
  "An encrusting skeletal organism up to a metre across that lined fissures in the Nama Group reefs of Namibia: the largest of the first animals with mineral skeletons.",
  hab=["reef", "shelf"], cls=("", "", ""))
E("Nasepia", "genus", "sea", "frond", 548, 541, ["af-s"],
  "An erniettomorph of the Nama Group, a bag of tubular segments that lived half-buried in the shifting sand of the last Ediacaran shelves.",
  hab=["shelf", "coast"], cls=("", "Erniettomorpha", ""))
E("Shaanxilithes", "genus", "sea", "worm", 551, 539, ["as-ne", "as-s", "in", "as-n"],
  "A ribbon-shaped fossil with fine transverse rings, from the last Ediacaran of Shaanxi and India to the first Cambrian: an animal or a colony, and a marker of the boundary interval.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Beothukis", "genus", "sea", "frond", 575, 560, ["na-av"],
  "A spindle-shaped rangeomorph of Mistaken Point, its self-similar branches all on one face, that lay flat on the deep-sea mud in the dark.",
  hab=["deep"], cls=("", "Rangeomorpha", ""))
E("Trepassia", "genus", "sea", "frond", 575, 565, ["na-av"],
  "A rangeomorph frond of the Drook Formation of Newfoundland, among the oldest large animals known at about 574 million years.",
  hab=["deep"], cls=("", "Rangeomorpha", ""))
E("Pectinifrons", "genus", "sea", "frond", 570, 560, ["na-av"],
  "A comb-shaped rangeomorph of Mistaken Point, a row of branches rising from a basal stolon, thousands preserved by volcanic ash on one surface.",
  hab=["deep"], cls=("", "Rangeomorpha", ""))
E("Haootia quadriformis", "species", "sea", "jellyfish", 560, 555, ["na-av"],
  "A four-fold body with bundled fibres from the Fermeuse Formation of Newfoundland, read as the oldest animal with muscles: a stalked cnidarian.",
  hab=["deep", "shelf"], cls=("", "", ""))
E("Tanarium", "genus", "sea", "acritarch", 635, 575, ["cosmo"],
  "A large acritarch with long branching processes, a signature of the early Ediacaran plankton after the Marinoan ice, from South China to central Australia and Siberia.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Appendisphaera", "genus", "sea", "acritarch", 635, 575, ["cosmo"],
  "A spiny acritarch of the early Ediacaran seas, one of the zone fossils of the Doushantuo-Pertatataka palynoflora; possibly the resting cysts of early animals.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Megasphaera", "genus", "sea", "microbe", 609, 580, ["as-s"],
  "Phosphatised spheres of dividing cells from the Doushantuo Formation of Guizhou, argued for twenty years to be animal embryos and by others to be giant bacteria or algae.",
  hab=["shelf"], cls=("", "", ""))
E("Miaohe biota", "informal", "sea", "seaweed", 551, 543, ["as-s"],
  "The black shales at the top of the Doushantuo Formation: carbonaceous seaweeds by the dozen, the spiral Eoandromeda, tubes and worm-like forms, a quiet late Ediacaran sea floor in South China.",
  hab=["shelf", "deep"], rep="Eoandromeda", assemblage=True)

# ------------------------------------------------------------- the Cambrian
E("Protospongia", "genus", "sea", "sponge", 520, 470, ["cosmo"],
  "A thin-walled glass sponge whose cross-shaped spicules lie in rows, in Cambrian and Ordovician shales from the Burgess Shale to Wales and China.",
  hab=["shelf", "deep"], cls=("Hexactinellida", "Reticulosa", "Protospongiidae"))
E("Hyolithes", "genus", "sea", "hyolith", 530, 252, ["cosmo"],
  "The type hyolith: a cone-shaped shell with a lid, and a pair of curved struts it steered with, on sea floors from the Cambrian to the Permian.",
  hab=["shelf"], cls=("Hyolitha", "Hyolithida", "Hyolithidae"))
E("Lingulella", "genus", "sea", "lingulid", 520, 445, ["cosmo"],
  "A small tongue-shaped phosphatic brachiopod of Cambrian and Ordovician shelves, burrowing like its living cousin Lingula.",
  hab=["shelf", "coast"], cls=("Lingulata", "Lingulida", "Obolidae"))
E("Billingsella", "genus", "sea", "brachiopod", 515, 480, ["cosmo"],
  "An early hinged brachiopod of the late Cambrian, found on every continent's shelf, from a family near the root of the orthides.",
  hab=["shelf"], cls=("Strophomenata", "Billingsellida", "Billingsellidae"))
E("Nisusia", "genus", "sea", "brachiopod", 515, 500, ["laurentia", "as-n", "au-e"],
  "A kutorginid brachiopod of the Burgess Shale and the Laurentian shelf, sometimes preserved with its spines still attached.",
  hab=["shelf"], cls=("Kutorginata", "Kutorginida", "Nisusiidae"))
E("Hupetina", "genus", "sea", "trilobite", 521, 515, ["af-n"],
  "One of the first trilobites of Morocco's Anti-Atlas, a fallotaspidoid of the Issafen Formation, near the base of the trilobite record on the Gondwanan shelf.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Fallotaspididae"))
E("Cambropallas", "genus", "sea", "trilobite", 515, 508, ["af-n"],
  "A trilobite a hand-span long from the Cambrian of Morocco, the commonest large fossil of the Jbel Wawrmast beds and of the fossil trade.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Holmiidae"))
E("Ellipsocephalus", "genus", "sea", "trilobite", 510, 500, ["eu-s", "eu-n"],
  "A smooth-shelled trilobite of the Jince beds of Bohemia and the Cambrian of Scandinavia, the first trilobite described from Bohemia (1825).",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Ellipsocephalidae"))
E("Conocoryphe", "genus", "sea", "trilobite", 510, 500, ["eu-s", "eu-n", "af-n", "as-c", "as-n"],
  "A blind trilobite of the Cambrian mud floors of Bohemia, the Montagne Noire, Spain, Wales and Morocco: eyes were of no use in the dark water it lived in.",
  hab=["shelf", "deep"], cls=("Trilobita", "Ptychopariida", "Conocoryphidae"))
E("Eccaparadoxides", "genus", "sea", "trilobite", 510, 500, ["eu-s", "eu-n", "af-n", "na-av", "as-n"],
  "A paradoxidid of the Cambrian of Bohemia, Spain, Morocco and Scandinavia, with a long spiny pygidium; a zone fossil of the middle Cambrian across the Gondwanan and Baltic shelves.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Paradoxididae"))
E("Parabolina", "genus", "sea", "trilobite", 497, 485, ["eu-n", "na-av", "sa-s", "ca", "as-n"],
  "An olenid trilobite of the Furongian black shales -- the Alum Shale of Scandinavia, Wales, Argentina and Oaxaca -- living at the edge of oxygen on the sea floor.",
  hab=["shelf", "deep"], cls=("Trilobita", "Ptychopariida", "Olenidae"))
E("Jujuyaspis", "genus", "sea", "trilobite", 486, 480, ["sa-s", "ca", "na-w", "as-c", "as-n", "eu-n"],
  "The olenid that marks the base of the Ordovician in Argentina and Bolivia, Oaxaca, Nevada, Kazakhstan and Norway: a wide-ranging trilobite of the outer shelf.",
  hab=["shelf", "deep"], cls=("Trilobita", "Ptychopariida", "Olenidae"))
E("Kainella", "genus", "sea", "trilobite", 486, 478, ["sa-s", "ca", "na-w", "na-e"],
  "A Tremadocian trilobite with a broad spiny pygidium, of the Argentine Cordillera Oriental, the Tinu Formation of Oaxaca and the Laurentian shelf.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Remopleurididae"))
E("Cordylodus", "genus", "sea", "conodont", 490, 476, ["cosmo"],
  "The conodont of the Cambrian-Ordovician boundary: its species define the last Cambrian and the first Ordovician zones on every continent.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "", ""))
E("Iapetognathus fluctivagus", "species", "sea", "conodont", 486.5, 484, ["cosmo"],
  "The conodont whose first appearance at Green Point, Newfoundland, defines the base of the Ordovician.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "", ""))

# ------------------------------------------------------ the zone graptolites
E("Rhabdinopora", "genus", "sea", "graptolite", 486, 478, ["cosmo"],
  "The first graptolite to leave the sea floor: a conical net of branches hanging from a float, drifting over every Tremadocian sea.",
  hab=["pelagic"], cls=("Graptolithina", "Dendroidea", "Anisograptidae"))
E("Tetragraptus", "genus", "sea", "graptolite", 478, 468, ["cosmo"],
  "Four stipes from one point, a Floian graptolite of the open ocean whose species date the early Ordovician worldwide.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Dichograptidae"))
E("Isograptus", "genus", "sea", "graptolite", 471, 466, ["cosmo"],
  "Two stipes folded back on themselves: the graptolite of the Dapingian, the Isograptus victoriae zones named from Victoria and found from Newfoundland to China.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Isograptidae"))
E("Nemagraptus gracilis", "species", "sea", "graptolite", 458.4, 455, ["cosmo"],
  "A slender S-shaped graptolite whose first appearance defines the base of the Sandbian; found on every Late Ordovician shelf and ocean floor.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Nemagraptidae"))
E("Dicellograptus", "genus", "sea", "graptolite", 460, 445, ["cosmo"],
  "Two stipes curving up like horns, the Late Ordovician graptolite of the black shales from Scotland to Kazakhstan and Australia.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Dicranograptidae"))
E("Normalograptus", "genus", "sea", "graptolite", 447, 440, ["cosmo"],
  "The plain single-stiped graptolite that outlived the Hirnantian ice: Normalograptus persculptus names the last Ordovician zone and its kin the first of the Silurian.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Normalograptidae"))
E("Cyrtograptus", "genus", "sea", "graptolite", 433.4, 427, ["cosmo"],
  "A spiral graptolite throwing off side branches, the zone fossil of the Wenlock in Britain, Bohemia, Baltica and Arctic Canada.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Cyrtograptidae"))
E("Saetograptus", "genus", "sea", "graptolite", 427, 423, ["cosmo"],
  "A Ludlow monograptid with paired spines on each cup, the zone fossil of the late Silurian shales of Wales, Bohemia and the Baltic.",
  hab=["pelagic"], cls=("Graptolithina", "Graptoloidea", "Monograptidae"))

# --------------------------------- the Ordovician trilobites, by province
E("Asaphellus", "genus", "sea", "trilobite", 485, 470, ["sa-s", "af-n", "eu-s", "eu-n", "as-c", "na-w"],
  "A smooth Tremadocian asaphid of the cool Gondwanan shelves -- Argentina, Bolivia, Morocco, Bohemia, Wales -- and of Kazakhstan.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Asaphidae"))
E("Hoekaspis", "genus", "sea", "trilobite", 470, 458, ["sa-s"],
  "A large asaphid of the Darriwilian shelf of Bolivia and northern Argentina, the commonest trilobite of the Andean Ordovician.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Asaphidae"))
E("Selenopeltis", "genus", "sea", "trilobite", 478, 445, ["eu-s", "eu-n", "af-n", "as-w"],
  "A spiny odontopleurid whose long pleural spines swept back the length of its body: the emblem of the Ordovician Mediterranean province, from Bohemia and Morocco to Wales and Turkey.",
  hab=["shelf"], cls=("Trilobita", "Odontopleurida", "Odontopleuridae"))
E("Placoparia", "genus", "sea", "trilobite", 478, 455, ["eu-s", "af-n", "eu-n"],
  "A blind cheirurid with a broad gently rounded shield, of the muddy cold-water shelves of Bohemia, Iberia, Morocco and Wales on the Gondwanan side of the Rheic Ocean.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Pliomeridae"))
E("Colpocoryphe", "genus", "sea", "trilobite", 478, 445, ["eu-s", "af-n", "eu-n"],
  "A calymenid of the Armorican, Iberian, Bohemian and Moroccan Ordovician, found rolled up by the hundred in the quartzites of Brittany.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Calymenidae"))
E("Ectillaenus", "genus", "sea", "trilobite", 478, 458, ["eu-s", "af-n", "eu-n"],
  "A smooth illaenid of the Mediterranean province, tucked into the sediment with only its convex head showing, in Bohemia, Portugal, Morocco and Wales.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Illaenidae"))
E("Onnia", "genus", "sea", "trilobite", 458, 445, ["eu-n", "af-n", "eu-s"],
  "A trinucleid with a wide pitted fringe, named for the Onny valley of Shropshire and sold by the thousand from the Ordovician of Morocco.",
  hab=["shelf", "deep"], cls=("Trilobita", "Asaphida", "Trinucleidae"))
E("Trinucleus", "genus", "sea", "trilobite", 460, 452, ["eu-n"],
  "The fringed trilobite of the Welsh Ordovician, blind, its pitted brim thought to sense currents in the mud it ploughed.",
  hab=["shelf", "deep"], cls=("Trilobita", "Asaphida", "Trinucleidae"))
E("Ogygiocaris", "genus", "sea", "trilobite", 470, 458, ["eu-n", "sa-s"],
  "A flat, wide asaphid of the Ogygiocaris shale of the Oslo region, the trilobite of the Baltic Darriwilian mud floors.",
  hab=["shelf", "deep"], cls=("Trilobita", "Asaphida", "Asaphidae"))
E("Dalmanitina", "genus", "sea", "trilobite", 460, 443, ["eu-s", "af-n", "sa-s", "eu-n", "as-n"],
  "A phacopid with a pointed tail that lived through the Hirnantian glaciation: the trilobite of the cold-water Hirnantia fauna from Bohemia and Wales to Morocco and Bolivia.",
  hab=["shelf"], cls=("Trilobita", "Phacopida", "Dalmanitidae"))

# --------------------------------------- the Silurian shelves and their fish
E("Encrinurus", "genus", "sea", "trilobite", 445, 419, ["cosmo"],
  "The strawberry-headed trilobite of Silurian reef flanks, its head covered in tubercles, from Dudley and Gotland to Laurentia, Siberia and Australia.",
  hab=["shelf", "reef"], cls=("Trilobita", "Phacopida", "Encrinuridae"))
E("Bumastus", "genus", "sea", "trilobite", 440, 419, ["laurentia", "eu-n"],
  "A smooth illaenid of the Wenlock reefs of Dudley and Gotland and the Silurian of Laurentia, its head and tail nearly featureless domes.",
  hab=["reef", "shelf"], lat=[0, 40], cls=("Trilobita", "Corynexochida", "Styginidae"))
E("Arctinurus", "genus", "sea", "trilobite", 435, 425, ["na-e"],
  "A lichid the size of a dinner plate from the Rochester Shale of New York, one of the largest Silurian trilobites.",
  hab=["shelf"], cls=("Trilobita", "Lichida", "Lichidae"))
E("Mixopterus", "genus", "sea", "eurypterid", 425, 419, ["eu-n", "na-e"],
  "A eurypterid with a scorpion-like curled tail and spined forelimbs, from the Ringerike sandstones of Norway; it walked as much as it swam.",
  hab=["coast", "shelf"], cls=("Eurypterida", "Eurypterida", "Mixopteridae"))
E("Thelodus", "genus", "sea", "ostracoderm", 435, 415, ["eu-n", "na-n", "as-n", "as-c"],
  "A jawless fish covered in tiny tooth-like scales, known mostly from those scales, which pave Silurian sandstones from the Baltic to Arctic Canada and Siberia.",
  hab=["coast", "shelf"], cls=("Thelodonti", "", ""))
E("Loganellia", "genus", "sea", "ostracoderm", 435, 425, ["eu-n", "as-c"],
  "A thelodont preserved whole in the Silurian of Scotland: a flattened jawless fish with a forked tail and, unexpectedly, gill-pouch denticles.",
  hab=["coast", "shelf"], cls=("Thelodonti", "", ""))
E("Birkenia", "genus", "sea", "ostracoderm", 435, 425, ["eu-n"],
  "A small anaspid of the Silurian of Lesmahagow and Norway, deep-bodied and scaled, with a tail that bent downward: an early jawless fish that swam in open water.",
  hab=["coast", "shelf"], cls=("Anaspida", "", ""))
E("Jamoytius", "genus", "sea", "ostracoderm", 435, 430, ["eu-n"],
  "A naked, eel-like jawless fish of the Lesmahagow Silurian of Scotland, with a ring of cartilage round its mouth: a lamprey's kin or something older.",
  hab=["coast", "shelf"], cls=("", "", ""))
E("Andreolepis", "genus", "sea", "fish", 425, 419, ["eu-n", "as-n"],
  "Scales and teeth from the late Silurian of Gotland and Russia that belong near the root of all bony fishes, four hundred and twenty-five million years old.",
  hab=["shelf", "coast"], cls=("Osteichthyes", "", ""))
E("Guiyu oneiros", "species", "sea", "lobefin", 425, 419, ["as-s"],
  "The oldest articulated bony fish, from the late Silurian Kuanti Formation of Yunnan: a lobe-finned fish with a mosaic of features the ray-fins and lobe-fins would later divide between them.",
  hab=["shelf", "coast"], cls=("Sarcopterygii", "", ""))
E("Entelognathus primordialis", "species", "sea", "placoderm", 423, 419, ["as-s"],
  "A placoderm from the Kuanti Formation of Yunnan with a bony jaw of the pattern all bony fishes and land vertebrates inherit; it moved the origin of the jaws we have into the armoured fishes.",
  hab=["shelf", "coast"], cls=("Placodermi", "", ""))
E("Climatius", "genus", "sea", "acanthodian", 420, 400, ["eu-n", "na-n"],
  "A spiny 'shark' of the Old Red Sandstone of Scotland, a hand long, with paired rows of fin spines under its belly.",
  hab=["coast", "river"], cls=("Acanthodii", "Climatiiformes", "Climatiidae"))
E("Heterorthella", "genus", "sea", "brachiopod", 433, 393, ["sa-s", "sa-n", "af-s"],
  "An orthide brachiopod of the cold Malvinokaffric seas of Silurian and Devonian Gondwana: Bolivia, Brazil, the Falklands and South Africa.",
  hab=["shelf"], cls=("Rhynchonellata", "Orthida", "Dalmanellidae"))

# ------------------------------ corals, bryozoans, brachiopods, algae
E("Lichenaria", "genus", "sea", "tabulate", 480, 458, ["laurentia", "as-n", "as-c"],
  "The first tabulate coral: small colonies of prismatic tubes in Early Ordovician limestones of Laurentia and Siberia, before reefs had corals.",
  hab=["shelf", "reef"], lat=[0, 40], cls=("Anthozoa", "Tabulata", "Lichenariidae"))
E("Catenipora", "genus", "sea", "tabulate", 450, 419, ["cosmo"],
  "A chain coral: tubes joined side by side into ranks that wander across the rock like chain-link, on Late Ordovician and Silurian shelves everywhere.",
  hab=["reef", "shelf"], lat=[0, 42], cls=("Anthozoa", "Tabulata", "Halysitidae"))
E("Syringopora", "genus", "sea", "tabulate", 445, 252, ["cosmo"],
  "The organ-pipe coral: loose bundles of tubes joined by cross-bars, from the Silurian to the Permian on every continent, common in Carboniferous reefs.",
  hab=["reef", "shelf"], lat=[0, 42], cls=("Anthozoa", "Tabulata", "Syringoporidae"))
E("Prasopora", "genus", "sea", "bryozoan", 460, 445, ["laurentia", "eu-n", "as-n"],
  "A gumdrop-shaped trepostome bryozoan of the Trenton and Cincinnatian limestones, and of Baltica: the bryozoan that built the Late Ordovician sea floor's small mounds.",
  hab=["shelf"], cls=("Stenolaemata", "Trepostomata", "Monticuliporidae"))
E("Hallopora", "genus", "sea", "bryozoan", 460, 420, ["laurentia", "eu-n"],
  "A branching trepostome bryozoan of Ordovician and Silurian shelves, its twigs the commonest bryozoan debris of the Cincinnatian.",
  hab=["shelf"], cls=("Stenolaemata", "Trepostomata", "Halloporidae"))
E("Orthis", "genus", "sea", "brachiopod", 485, 458, ["cosmo"],
  "The orthide that named its order: a ribbed, straight-hinged brachiopod of Ordovician shelves from Baltica and Laurentia to the Gondwanan margin.",
  hab=["shelf"], cls=("Rhynchonellata", "Orthida", "Orthidae"))
E("Sowerbyella", "genus", "sea", "brachiopod", 470, 420, ["cosmo"],
  "A small, finely ribbed strophomenide lying flat on Ordovician and Silurian mud floors worldwide, often in shell beds by the thousand.",
  hab=["shelf"], cls=("Strophomenata", "Strophomenida", "Sowerbyellidae"))
E("Strophomena", "genus", "sea", "brachiopod", 470, 420, ["cosmo"],
  "A wide, gently curved strophomenide with a straight hinge, resting on the sediment on its convex valve, on every Ordovician and Silurian shelf.",
  hab=["shelf"], cls=("Strophomenata", "Strophomenida", "Strophomenidae"))
E("Eospirifer", "genus", "sea", "brachiopod", 445, 400, ["cosmo"],
  "The first spiriferide: a brachiopod with a coiled internal support for its feeding organ, from the last Ordovician to the Early Devonian, the start of a line that ran to the Jurassic.",
  hab=["shelf"], cls=("Rhynchonellata", "Spiriferida", "Eospiriferidae"))
E("Vermiporella", "genus", "sea", "seaweed", 470, 419, ["cosmo"],
  "A calcified dasyclad alga, a branching tube a few millimetres wide, that paved shallow Ordovician and Silurian carbonate floors on every continent.",
  hab=["shelf", "coast"], lat=[0, 45], cls=("Ulvophyceae", "Dasycladales", ""))
E("Cyclocrinites", "genus", "sea", "seaweed", 470, 419, ["laurentia", "eu-n", "as-n", "as-c"],
  "A golf-ball alga: a sphere of packed branch-tips a few centimetres across, calcified, in Ordovician and Silurian limestones of Laurentia and Baltica.",
  hab=["shelf"], lat=[0, 45], cls=("Ulvophyceae", "Dasycladales", "Cyclocrinaceae"))
E("Dimorphosiphon", "genus", "sea", "seaweed", 470, 445, ["eu-n", "laurentia", "as-n"],
  "A calcified green alga of the Ordovician of Baltica and Laurentia, close to the living Halimeda in build, and a rock-former in Norway's Oslo region.",
  hab=["shelf"], lat=[0, 45], cls=("Ulvophyceae", "Bryopsidales", ""))
E("Palaeoporella", "genus", "sea", "seaweed", 460, 419, ["cosmo"],
  "A calcified dasyclad of Late Ordovician and Silurian shelves, one of the algae that turned Silurian lagoons into limestone.",
  hab=["shelf", "coast"], lat=[0, 45], cls=("Ulvophyceae", "Dasycladales", ""))
E("Ozarkodina", "genus", "sea", "conodont", 440, 400, ["cosmo"],
  "The commonest conodont of Silurian seas, whose apparatus is known entire; its species date the Silurian on every shelf.",
  hab=["pelagic", "shelf"], cls=("Conodonta", "Ozarkodinida", ""))
E("Icriodus", "genus", "sea", "conodont", 419, 359, ["cosmo"],
  "A shallow-water conodont of the Devonian, its rows of nodes the standard zonation of the near-shore seas from the Lochkovian to the Famennian.",
  hab=["shelf"], cls=("Conodonta", "", ""))
write("x-early-palaeozoic-seas.json")
