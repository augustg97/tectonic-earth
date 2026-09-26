"""Palaeozoic life by place (3.17). The cards of 250-540 Ma repeated a handful of
names everywhere -- Leiosphaeridia on 93-100% of the cards at 375-475 Ma,
Collembola on 80-86% at 325-400, Hyolithes on all of them at 475 -- because the
registry held few genera tied to one palaeocontinent at one time. These are
the organisms that make Baltica, Avalonia, South China, Laurentia, the
Gondwanan shelf and the coal swamps look like themselves, each dated to its
formation and ranged on the crust its fossils lie in."""
from _lib import E, T, write
R, SY, AM = "Reptilia", "Synapsida", "Amphibia"

# ================================================= CARBONIFEROUS-PERMIAN FLORA
E("Neuropteris", "genus", "land", "seedfern", 323, 295, ["na-e", "na-w", "na-av", "eu", "af-n", "as-ne", "as-s"],
  "Tongue-shaped leaflets of the medullosan seed ferns, small trees whose fronds reached several metres; they are the commonest plant fossil in the ironstone nodules of the coal measures.",
  cls=("Pteridospermatopsida", "Medullosales", ""))
E("Alethopteris", "genus", "land", "seedfern", 325, 285, ["na", "eu", "af-n", "as-ne", "as-s"],
  "Leaflets joined at their bases in long, strap-like rows -- the foliage of Medullosa, a seed fern whose seeds could be as large as a hen's egg.",
  cls=("Pteridospermatopsida", "Medullosales", "Alethopteridaceae"))
E("Autunia", "genus", "land", "seedfern", 305, 265, ["eu", "na-w", "na-e", "af-n"],
  "A peltasperm seed fern whose leaf, long called Callipteris, is the classic sign of the base of the Permian in the red beds of Europe -- a plant of drier ground than the coal swamps.",
  aka=["Callipteris"], cls=("Pteridospermatopsida", "Peltaspermales", "Peltaspermaceae"))
E("Lepidophloios", "genus", "land", "lycopod", 330, 300, ["eu", "na-e", "na-w", "na-av"],
  "A scale tree of the coal swamps whose leaf cushions overlapped like the scales of a cone; it grew as one tall pole, branched once into a crown, shed its spores and died.",
  hab=["wetland", "forest"], cls=("Lycopsida", "Lepidodendrales", "Lepidodendraceae"))
E("Phyllotheca", "genus", "land", "horsetail", 290, 240, ["in", "au", "af-s", "an", "sa-s", "as-n"],
  "A sphenophyte of the Glossopteris swamps with whorls of long, narrow leaves joined at the base into a collar -- the southern counterpart of Calamites.",
  hab=["wetland", "river", "lake", "forest"], cls=("Equisetopsida", "Equisetales", "Phyllothecaceae"))
E("Phylladoderma", "genus", "land", "seedfern", 270, 252, ["eu-n", "as-n", "as-c"],
  "A peltasperm seed fern with long, tongue-shaped leaves, typical of the Late Permian floras of the Russian platform and Angara.",
  cls=("Pteridospermatopsida", "Peltaspermales", "Peltaspermaceae"))

# ================================================= CARBONIFEROUS-PERMIAN FAUNA
E("Meganeuropsis", "genus", "air", "dragonfly", 290, 279, ["na-w"],
  "The largest insect known: a griffinfly with wings spanning 71 centimetres, which hunted other insects over the Early Permian coastal plain of Kansas.",
  cls=("Insecta", "Meganisoptera", "Meganeuridae"))
E("Petrolacosaurus", "genus", "land", "lizard", 304, 300, ["na-w"],
  "A forty-centimetre, long-limbed reptile of the latest Carboniferous, one of the first diapsids -- the line that later gave lizards, crocodiles, dinosaurs and birds.",
  cls=(R, "Araeoscelidia", "Petrolacosauridae"))
E("Archaeothyris", "genus", "land", "pelycosaur", 308, 304, ["na-av"],
  "One of the oldest synapsids, the line leading to mammals: a fifty-centimetre, lizard-shaped insect-eater found inside a fossil tree stump in Nova Scotia.",
  cls=(SY, "Pelycosauria", "Ophiacodontidae"))
E("Ophiacodon", "genus", "land", "pelycosaur", 305, 280, ["na-w", "na-e", "eu"],
  "A two-to-three-metre synapsid with a long, deep skull -- probably a fish-eater of the Early Permian rivers and swamps.",
  cls=(SY, "Pelycosauria", "Ophiacodontidae"))
E("Varanops", "genus", "land", "pelycosaur", 280, 272, ["na-w"],
  "A lightly built, monitor-like synapsid predator a metre and a half long -- one of the last of the early branch of the mammal line.",
  cls=(SY, "Pelycosauria", "Varanopidae"))
E("Diadectes", "genus", "land", "reptiliomorph", 305, 275, ["na-w", "na-e", "eu"],
  "One of the first large plant-eaters on land: a three-metre, barrel-bodied tetrapod with broad cheek teeth, close to the ancestry of reptiles.",
  cls=(AM, "Diadectomorpha", "Diadectidae"))
E("Orobates", "genus", "land", "reptiliomorph", 296, 287, ["eu"],
  "A metre-long diadectid known from its skeleton and its own footprints -- enough to rebuild its gait as a robot, which showed it walked more upright than expected.",
  cls=(AM, "Diadectomorpha", "Diadectidae"))
E("Cacops", "genus", "land", "temnospondyl", 280, 272, ["na-w"],
  "A stocky, armour-backed amphibian with a large eardrum notch -- a land-going temnospondyl of the Early Permian, probably active at night.",
  cls=(AM, "Temnospondyli", "Dissorophidae"))
E("Lycaenops", "genus", "land", "gorgonopsian", 260, 254, ["af-s"],
  "A wolf-sized gorgonopsian with long sabre canines, the kind of predator that hunted dicynodonts across the Late Permian Karoo.",
  cls=(SY, "Gorgonopsia", "Gorgonopsidae"))
E("Titanophoneus", "genus", "land", "dinocephalian", 267, 262, ["eu-n"],
  "A carnivorous dinocephalian two and a half metres long, with long canines and a heavy skull -- a top predator of the Middle Permian before the gorgonopsians took over.",
  cls=(SY, "Dinocephalia", "Anteosauridae"))
E("Pareiasaurus", "genus", "land", "pareiasaur", 260, 255, ["af-s"],
  "A cow-sized, armour-studded plant-eater with leaf-shaped teeth -- one of the pareiasaurs, the largest herbivores of the Late Permian.",
  cls=(R, "Parareptilia", "Pareiasauridae"))
E("Coelurosauravus", "genus", "land", "lizard", 258, 252, ["mg", "eu"],
  "The first gliding reptile: a lizard-sized weigeltisaurid that spread wings of skin on rods of bone growing from its flanks.",
  cls=(R, "", "Weigeltisauridae"))
E("Youngina", "genus", "land", "lizard", 256, 252, ["af-s"],
  "A small, lizard-shaped diapsid of the latest Permian, close to the common ancestor of lizards and archosaurs; young were found huddled together in a burrow.",
  cls=(R, "Younginiformes", "Younginidae"))
E("Proterogyrinus", "genus", "fresh", "reptiliomorph", 335, 325, ["na-e", "eu-n"],
  "A two-metre anthracosaur of the Mississippian, a long-bodied predator of the swamps from West Virginia to Scotland.",
  realms=["fresh", "land"], cls=(AM, "Embolomeri", "Proterogyrinidae"))
E("Pederpes", "genus", "land", "stemtetrapod", 350, 346, ["eu-n"],
  "A metre-long tetrapod from Romer's Gap -- the stretch after the Devonian that had yielded almost no land vertebrates -- with feet that point forward, built for walking.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Whatcheeriidae"))
E("Crassigyrinus", "genus", "fresh", "stemtetrapod", 335, 325, ["eu-n", "na-e"],
  "A two-metre, big-mouthed stem tetrapod with tiny forelimbs -- back in the water, an ambush hunter of the Mississippian lakes.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Crassigyrinidae"))
E("Westlothiana", "genus", "land", "reptiliomorph", 340, 335, ["eu-n"],
  "A slender twenty-centimetre tetrapod from a Mississippian lake shore in Scotland, once hailed as the earliest reptile and now placed just outside the amniotes.",
  cls=(AM, "Reptiliomorpha", ""))
E("Balanerpeton", "genus", "land", "temnospondyl", 340, 335, ["eu-n"],
  "A small land-going temnospondyl with an eardrum -- among the first tetrapods that could hear sound travelling through air.",
  cls=(AM, "Temnospondyli", "Dendrerpetontidae"))
E("Greererpeton", "genus", "fresh", "stemtetrapod", 335, 325, ["na-e"],
  "A long-bodied colosteid with a flat skull and the lateral-line grooves of a fish -- an eel-like hunter that never really left the water.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Colosteidae"))
E("Hibbertopterus", "genus", "fresh", "eurypterid", 360, 300, ["eu-n", "na-w", "af-s"],
  "A giant sweep-feeding sea scorpion as long as a person, which raked lake and river beds with its spined limbs; one of its walking trackways runs six metres across a Scottish sandstone.",
  cls=("Merostomata", "Eurypterida", "Hibbertopteridae"))
E("Amphibamus", "genus", "fresh", "temnospondyl", 310, 307, ["na-e"],
  "A ten-centimetre, salamander-shaped dissorophoid of the Pennsylvanian coal swamps, close to the ancestry of frogs and salamanders.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Amphibamidae"))
E("Rhinesuchus", "genus", "fresh", "temnospondyl", 260, 255, ["af-s"],
  "A two-metre, flat-headed temnospondyl of the Late Permian rivers -- one of the big amphibians that the end-Permian extinction nearly ended.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Rhinesuchidae"))

# ===================================================== DEVONIAN LAND AND RIVER
E("Psilophyton", "genus", "land", "rhyniophyte", 408, 390, ["na-e", "na-av", "eu", "as-s"],
  "A trimerophyte of the Early Devonian: leafless stems that forked and forked again to a metre tall -- the stock from which ferns, horsetails and seed plants branched.",
  cls=("Trimerophytopsida", "Trimerophytales", ""))
E("Pertica", "genus", "land", "rhyniophyte", 400, 390, ["na-e", "na-av"],
  "A trimerophyte that grew a main stem with side branches in a spiral -- the first hint of the trunk-and-branch plan of trees.",
  cls=("Trimerophytopsida", "Trimerophytales", ""))
E("Rhacophyton", "genus", "land", "fern", 370, 359, ["na-e", "eu-n"],
  "A fern-like plant of the latest Devonian that grew in dense thickets on floodplains -- and burned: charcoal from its wildfires is common in its beds.",
  cls=("Polypodiopsida", "Stauropteridales", "Rhacophytaceae"))
E("Sawdonia", "genus", "land", "zosterophyll", 410, 390, ["na-e", "na-av", "eu"],
  "A spiny, leafless zosterophyll whose stems uncoiled like fern fiddleheads -- a cousin of the lycopods.",
  cls=("Zosterophyllopsida", "Sawdoniales", "Sawdoniaceae"))
E("Horneophyton", "genus", "land", "rhyniophyte", 411, 405, ["eu-n"],
  "A small plant of the Rhynie hot-spring marsh with a lumpy underground corm and a spore capsule with a central column like a moss's -- from before the vascular plants settled their plan.",
  cls=("Horneophytopsida", "Horneophytales", "Horneophytaceae"))
E("Leptophloeum", "genus", "land", "lycopod", 383, 359, ["as-s", "as-ne", "as-c", "au-e", "an", "sa-n", "af-s", "eu"],
  "A Late Devonian tree lycopsid with bark patterned in diamonds -- one of the few trees found across Gondwana and the northern continents alike.",
  cls=("Lycopsida", "", "Leptophloeaceae"))
E("Tiktaalik", "genus", "fresh", "lobefin", 377, 374, ["na-n"],
  "The 'fishapod': a three-metre lobe-finned fish with a neck, a flat head and fins with wrist bones, from Late Devonian river deposits now on Ellesmere Island.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Elpistostegidae"))
E("Ventastega", "genus", "fresh", "stemtetrapod", 373, 371, ["eu-n"],
  "A Late Devonian stem tetrapod from Latvia, between Tiktaalik and Acanthostega -- probably with limbs, still with a fish's tail fin.",
  cls=("Sarcopterygii", "Stegocephalia", ""))
E("Elginerpeton", "genus", "fresh", "stemtetrapod", 375, 368, ["eu-n"],
  "One of the earliest tetrapods, known from jaws and limb bones from the Late Devonian of Scotland -- a metre and a half long and still mostly in the water.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Elginerpetontidae"))
E("Panderichthys", "genus", "fresh", "lobefin", 385, 380, ["eu-n"],
  "A lobe-finned fish of the Middle Devonian lagoons with a flat head, no dorsal fins and the beginnings of fingers in its fin bones.",
  cls=("Sarcopterygii", "Tetrapodomorpha", "Panderichthyidae"))
E("Holoptychius", "genus", "fresh", "lobefin", 385, 359, ["eu-n", "na-e", "gl", "as-n", "an", "au-e"],
  "A porolepiform lobe-finned fish up to two and a half metres long, with big rounded scales and fangs -- one of the commonest large fishes of Late Devonian rivers.",
  cls=("Sarcopterygii", "Porolepiformes", "Holoptychiidae"))
E("Dipterus", "genus", "fresh", "lungfish", 390, 375, ["eu-n"],
  "An early lungfish of the Middle Devonian lake of northern Scotland, whose crushing tooth plates are almost those of a living lungfish.",
  cls=("Sarcopterygii", "Dipnoi", "Dipteridae"))
E("Pteraspis", "genus", "sea", "ostracoderm", 415, 400, ["eu-n"],
  "A jawless fish with a streamlined armoured head shield ending in a long snout, and wing-like spines behind its head that steadied it as it swam.",
  realms=["sea", "fresh"], cls=("Pteraspidomorphi", "Heterostraci", "Pteraspididae"))

# ================================================================ CAMBRIAN SEA
E("Fuxianhuia", "genus", "sea", "cambrianarthropod", 518, 515, ["as-s"],
  "An arthropod of the Chengjiang sea whose brain and nerves were fossilised -- evidence that complex arthropod brains already existed in the Early Cambrian.",
  cls=("Arthropoda", "Fuxianhuiida", "Fuxianhuiidae"))
E("Naraoia", "genus", "sea", "cambrianarthropod", 518, 505, ["as-s", "na-w"],
  "A soft-shelled, trilobite-like arthropod without eyes or a segmented back -- a naraoiid, common in both the Chengjiang and the Burgess seas.",
  cls=("Arthropoda", "Nektaspida", "Naraoiidae"))
E("Kunmingella", "genus", "sea", "cambrianarthropod", 520, 510, ["as-s"],
  "A millimetre-sized bivalved bradoriid, the most abundant animal of the Chengjiang sea, sometimes preserved with eggs under its shell.",
  cls=("Arthropoda", "Bradoriida", "Kunmingellidae"))
E("Amplectobelua", "genus", "sea", "radiodont", 518, 510, ["as-s"],
  "A radiodont with pincer-like grasping claws, one of the top predators of the Chengjiang sea.",
  cls=("Dinocaridida", "Radiodonta", "Amplectobeluidae"))
E("Leanchoilia", "genus", "sea", "cambrianarthropod", 515, 505, ["as-s", "na-w"],
  "A megacheiran arthropod with long, whip-tipped 'great appendages' in front, fossilised with its nervous system in the Chengjiang beds.",
  cls=("Arthropoda", "Megacheira", "Leanchoiliidae"))
E("Isoxys", "genus", "sea", "cambrianarthropod", 520, 505, ["as-s", "au-e", "na-w", "gl", "eu-s", "as-n"],
  "A bivalved Cambrian arthropod with big stalked eyes and spines fore and aft -- a swimming predator found in almost every Cambrian Lagerstätte.",
  cls=("Arthropoda", "Isoxyida", "Isoxyidae"))
E("Kerygmachela", "genus", "sea", "lobopod", 518, 515, ["gl"],
  "A gilled lobopodian of Sirius Passet with swimming flaps and two long, spined head limbs -- a snapshot of the step from lobopodians to arthropods.",
  cls=("Lobopodia", "", "Kerygmachelidae"))
E("Pambdelurion", "genus", "sea", "lobopod", 518, 515, ["gl"],
  "A half-metre gilled lobopodian of Sirius Passet, walking and swimming at once, with frontal claws -- a relative of the radiodonts.",
  cls=("Lobopodia", "", ""))
E("Buenellus", "genus", "sea", "trilobite", 518, 515, ["gl"],
  "An olenellid trilobite, the commonest in the Sirius Passet beds on the northern edge of Cambrian Laurentia.",
  cls=("Trilobita", "Redlichiida", "Olenellidae"))
E("Waptia", "genus", "sea", "cambrianarthropod", 508, 505, ["na-w"],
  "A shrimp-like Burgess Shale arthropod that brooded its eggs under its carapace -- the oldest direct evidence of parental care.",
  cls=("Arthropoda", "Hymenocarina", "Waptiidae"))
E("Canadaspis", "genus", "sea", "cambrianarthropod", 515, 505, ["na-w", "as-s"],
  "One of the commonest Burgess Shale arthropods: a bivalved, shrimp-like bottom-feeder that also lived in the Chengjiang sea.",
  cls=("Arthropoda", "Hymenocarina", "Canadaspididae"))
E("Sidneyia", "genus", "sea", "cambrianarthropod", 508, 505, ["na-w"],
  "A thirteen-centimetre Burgess Shale predator whose gut held crushed trilobites and hyoliths.",
  cls=("Arthropoda", "Artiopoda", "Sidneyiidae"))
E("Hurdia", "genus", "sea", "radiodont", 508, 500, ["na-w", "eu-s", "as-s"],
  "A radiodont with a long, hood-like carapace over its head -- first described piecemeal as several different animals.",
  cls=("Dinocaridida", "Radiodonta", "Hurdiidae"))
E("Aysheaia", "genus", "sea", "lobopod", 508, 505, ["na-w"],
  "A velvet-worm-like lobopodian of the Burgess Shale, often found among the sponges it may have fed on.",
  cls=("Lobopodia", "", "Aysheaiidae"))
E("Vauxia", "genus", "sea", "sponge", 508, 505, ["na-w"],
  "A branching Burgess Shale sponge with a fibrous skeleton -- one of the oldest demosponges.",
  cls=("Porifera", "Demospongiae", "Vauxiidae"))
E("Bailiella", "genus", "sea", "trilobite", 508, 497, ["as-ne", "eu-s", "eu-n", "na-av"],
  "An eyeless conocoryphid trilobite, of Middle Cambrian seas from North China to Avalonia and Bohemia.",
  cls=("Trilobita", "Ptychopariida", "Conocoryphidae"))
E("Damesella", "genus", "sea", "trilobite", 505, 500, ["as-ne"],
  "A spiny-tailed damesellid trilobite of the late Middle Cambrian of North China and Korea.",
  cls=("Trilobita", "Corynexochida", "Damesellidae"))
E("Blackwelderia", "genus", "sea", "trilobite", 500, 497, ["as-ne"],
  "A damesellid trilobite with long spines fanning from its tail, typical of the Guzhangian seas of North China.",
  cls=("Trilobita", "Corynexochida", "Damesellidae"))
E("Drepanura", "genus", "sea", "trilobite", 499, 496, ["as-ne"],
  "A trilobite whose broad, hooked tail shield is the 'swallow stone' of Shandong, collected as a curiosity in China for a thousand years.",
  cls=("Trilobita", "Corynexochida", "Damesellidae"))

# ============================================================== ORDOVICIAN SEA
E("Illaenus", "genus", "sea", "trilobite", 470, 445, ["eu-n", "as-n", "as-c", "na-e", "na-w"],
  "A smooth, rounded trilobite that lay half-buried in the sea floor with only its eyes showing -- common on the Ordovician shelves of Baltica.",
  cls=("Trilobita", "Corynexochida", "Illaenidae"))
E("Echinosphaerites", "genus", "sea", "crinoid", 465, 450, ["eu-n", "na-e"],
  "A cystoid echinoderm, a spiny ball on a short stalk, so abundant in the Middle Ordovician of Baltica that its skeletons form whole beds of limestone.",
  cls=("Echinodermata", "Rhombifera", "Echinosphaeritidae"))
E("Ceraurus", "genus", "sea", "trilobite", 460, 445, ["na-e", "na-w"],
  "A spiny cheirurid trilobite of the Trenton limestone seas, sometimes preserved with its legs.",
  cls=("Trilobita", "Phacopida", "Cheiruridae"))
E("Megalograptus", "genus", "sea", "eurypterid", 455, 445, ["na-e"],
  "One of the largest Ordovician sea scorpions, more than a metre long, with spiny grasping forelimbs.",
  cls=("Merostomata", "Eurypterida", "Megalograptidae"))
E("Hebertella", "genus", "sea", "brachiopod", 455, 445, ["na-e", "na-w"],
  "A ribbed orthid brachiopod, one of the commonest shells of the Late Ordovician seas of Laurentia.",
  cls=("Brachiopoda", "Orthida", "Plaesiomyidae"))
E("Tetradium", "genus", "sea", "tabulate", 465, 445, ["na", "as-n", "as-c", "au"],
  "A colonial coral (or perhaps an alga) of the Ordovician with tubes divided into four, forming mounds in the warm lagoons of Laurentia and Siberia.",
  cls=("Anthozoa", "Tabulata", "Tetradiidae"))
E("Maclurites", "genus", "sea", "seasnail", 470, 445, ["na-e", "na-w", "eu-n", "as-n"],
  "A big, flat-coiled gastropod with a heavy lid, lying on the Ordovician sea floor like a stone -- its shells stud limestones from Tennessee to Scotland.",
  cls=("Gastropoda", "", "Macluritidae"))
E("Ogygiocarella", "genus", "sea", "trilobite", 465, 455, ["eu-n", "sa-s", "af-n"],
  "A large, flat asaphid trilobite of Avalonia and the Gondwanan margin -- the 'Welsh trilobite', the first trilobite ever figured in print, in 1698.",
  cls=("Trilobita", "Asaphida", "Ogygiocarididae"))
E("Sinoceras", "genus", "sea", "orthocone", 460, 450, ["as-s"],
  "A long, straight-shelled nautiloid of the Late Ordovician of South China, whose sectioned shells make the 'pagoda stones' of Chinese decorative stone.",
  cls=("Cephalopoda", "Orthocerida", "Orthoceratidae"))
E("Nankinolithus", "genus", "sea", "trilobite", 455, 445, ["as-s", "eu"],
  "A trinucleid trilobite with a broad, pitted fringe around its head -- a sieve for filtering food from the Late Ordovician mud.",
  cls=("Trilobita", "Asaphida", "Trinucleidae"))
E("Armenoceras", "genus", "sea", "orthocone", 470, 450, ["as-ne", "na", "as-n"],
  "An actinocerid nautiloid whose chambers are threaded by a thick, beaded siphuncle -- common in the warm Middle Ordovician seas of North China and Laurentia.",
  cls=("Cephalopoda", "Actinocerida", "Armenoceratidae"))
E("Arandaspis", "genus", "sea", "ostracoderm", 480, 470, ["au-e"],
  "One of the oldest fishes with a bony skeleton: a jawless, finless, armoured swimmer of the Early Ordovician sea over central Australia.",
  cls=("Pteraspidomorphi", "Arandaspida", "Arandaspididae"))
E("Aegirocassis", "genus", "sea", "radiodont", 480, 476, ["af-n"],
  "A two-metre radiodont that filtered plankton with comb-like head limbs -- the gentle giant of the Early Ordovician Fezouata sea.",
  cls=("Dinocaridida", "Radiodonta", "Hurdiidae"))
E("Promissum", "genus", "sea", "conodont", 446, 443, ["af-s"],
  "The conodont animal preserved whole: forty centimetres long, eel-like, with big eyes and muscle blocks, from a shale laid down under the end-Ordovician ice.",
  cls=("Conodonta", "Prioniodontida", "Balognathidae"))
E("Gloeocapsomorpha prisca", "species", "sea", "cyano", 460, 450, ["eu-n", "na-e", "na-w", "as-c"],
  "A colonial microbe, probably a cyanobacterium, whose Ordovician blooms made the kukersite oil shale of Estonia -- which still fuels the country's power stations.",
  cls=("Cyanobacteria", "", ""))
E("Baltisphaeridium", "genus", "sea", "acritarch", 480, 445, ["eu-n", "as-c", "na-e", "ar"],
  "A spiny acritarch -- the resting cyst of an Ordovician plankter -- used to date the Ordovician rocks of Baltica.",
  hab=["pelagic", "shelf"], cls=("Acritarcha", "", ""))
E("Frankea", "genus", "sea", "acritarch", 470, 450, ["af-n", "eu-s", "sa-s", "ar", "as-w"],
  "A peri-Gondwanan acritarch with long branching spines, a marker of the cold high-latitude Ordovician seas off North Africa and Iberia.",
  hab=["pelagic", "shelf"], cls=("Acritarcha", "", ""))
E("Veryhachium", "genus", "sea", "acritarch", 480, 260, ["cosmo"],
  "A three-to-six-pointed star of an acritarch, the resting cyst of a Palaeozoic plankter, found in marine rocks from the Ordovician to the Permian.",
  hab=["pelagic", "shelf"], cls=("Acritarcha", "", ""))
E("Nuia", "genus", "sea", "seaweed", 485, 455, ["na", "as-n", "as-c", "sa-s"],
  "Tiny calcified rods, probably a green alga, that make up much of the Early Ordovician lime sands of Laurentia and Siberia.",
  cls=("Chlorophyta", "", ""))
E("Mastopora", "genus", "sea", "seaweed", 470, 445, ["na-e", "eu-n", "as-n", "as-c"],
  "A ball-shaped dasyclad green alga of the Ordovician, like a small calcified sea-grape, common on the carbonate shelves of Laurentia and Baltica.",
  cls=("Chlorophyta", "Dasycladales", ""))
E("Renalcis", "genus", "sea", "cyano", 530, 360, ["cosmo"],
  "A calcified microbe growing as clusters of tiny chambered lumps -- a builder of reefs beside the archaeocyath sponges in the Cambrian and the stromatoporoids in the Devonian.",
  lat=[0, 40], cls=("Cyanobacteria", "", ""))
E("Epiphyton", "genus", "sea", "cyano", 530, 360, ["cosmo"],
  "A shrub-like calcified microbe that framed reefs with the archaeocyaths in the Cambrian and again in the Late Devonian.",
  lat=[0, 40], cls=("Cyanobacteria", "", ""))
E("Rothpletzella", "genus", "sea", "cyano", 440, 370, ["cosmo"],
  "Fine calcified filaments that crusted over corals and stromatoporoids on the reefs of the Silurian and Devonian.",
  lat=[0, 40], cls=("Cyanobacteria", "", ""))

# ================================================================ SILURIAN SEA
E("Stricklandia", "genus", "sea", "brachiopod", 440, 430, ["eu-n", "na-e", "na-w", "as-n"],
  "A large pentamerid brachiopod of the Llandovery whose changing shape through time is used to date Silurian rocks.",
  cls=("Brachiopoda", "Pentamerida", "Stricklandiidae"))
E("Crotalocrinites", "genus", "sea", "crinoid", 430, 425, ["eu-n", "na-e", "as-n"],
  "A Silurian crinoid whose arms fused into a web, a filtering fan; it grew in meadows on Silurian reefs.",
  cls=("Crinoidea", "Monobathrida", "Crotalocrinitidae"))
E("Cardiola", "genus", "sea", "clam", 430, 420, ["eu-s", "af-n", "eu-n"],
  "A small, ribbed bivalve of the Silurian, abundant in the dark limestones of Bohemia and North Africa.",
  cls=("Bivalvia", "Praecardiida", "Cardiolidae"))
E("Scyphocrinites", "genus", "sea", "crinoid", 422, 415, ["eu-s", "af-n", "na-e", "as-s", "eu-n"],
  "A crinoid that floated from a gas-filled bulb instead of rooting on the sea floor; drifting colonies of it cover whole bedding planes at the Silurian-Devonian boundary.",
  cls=("Crinoidea", "Cladida", "Scyphocrinitidae"))
E("Deiphon", "genus", "sea", "trilobite", 430, 425, ["eu-s", "eu-n", "na-e"],
  "A cheirurid trilobite with a swollen, globe-shaped head and long spines -- perhaps a swimmer in open water.",
  cls=("Trilobita", "Phacopida", "Cheiruridae"))
E("Trimerus", "genus", "sea", "trilobite", 435, 380, ["na-e", "eu-n", "sa-s", "au-e"],
  "A large, smooth homalonotid trilobite with a triangular head, which ploughed through the Silurian and Devonian mud.",
  cls=("Trilobita", "Phacopida", "Homalonotidae"))
E("Slimonia", "genus", "sea", "eurypterid", 430, 420, ["eu-n"],
  "A metre-long Silurian sea scorpion with a broad body and a spiked tail, from the lagoons of southern Scotland.",
  cls=("Merostomata", "Eurypterida", "Slimonidae"))
E("Acutiramus", "genus", "sea", "eurypterid", 425, 415, ["na-e", "eu"],
  "A two-metre pterygotid sea scorpion with long pincers, among the largest arthropods of the Silurian.",
  cls=("Merostomata", "Eurypterida", "Pterygotidae"))
E("Jaekelopterus", "genus", "fresh", "eurypterid", 395, 390, ["eu-n", "na-w"],
  "The largest arthropod known: a sea scorpion some two and a half metres long, known from a 46-centimetre claw, hunting in Early Devonian estuaries.",
  realms=["fresh", "sea"], cls=("Merostomata", "Eurypterida", "Pterygotidae"))

# ================================================================ DEVONIAN SEA
E("Walliserops", "genus", "sea", "trilobite", 400, 395, ["af-n"],
  "A phacopid trilobite with a long three-pronged trident on its head, perhaps used by males in contests.",
  cls=("Trilobita", "Phacopida", "Acastidae"))
E("Dicranurus", "genus", "sea", "trilobite", 420, 395, ["af-n", "na-w", "na-e", "eu-s", "au-e"],
  "A spiny odontopleurid trilobite with two long horns curling back from its head like a ram's.",
  cls=("Trilobita", "Odontopleurida", "Odontopleuridae"))
E("Erbenochile", "genus", "sea", "trilobite", 400, 395, ["af-n"],
  "A trilobite with towering eyes crowned by a sunshade -- evidence that it lived in bright, shallow water.",
  cls=("Trilobita", "Phacopida", "Acastidae"))
E("Scutellum", "genus", "sea", "trilobite", 420, 380, ["eu-s", "af-n", "eu-n"],
  "A trilobite with a broad, fan-shaped, ribbed tail shield -- a characteristic dweller of Silurian and Devonian reefs.",
  cls=("Trilobita", "Corynexochida", "Scutelluidae"))
E("Harpes", "genus", "sea", "trilobite", 400, 375, ["eu-s", "af-n", "eu-n", "na-e"],
  "A trilobite with a broad, pitted horseshoe brim around its head -- probably a sieve for sifting food from the mud.",
  cls=("Trilobita", "Harpetida", "Harpetidae"))
E("Heliophyllum", "genus", "sea", "horncoral", 405, 375, ["na-e", "na-w", "eu", "as-c"],
  "A large solitary horn coral of the Middle Devonian whose fine growth ridges, counted as days, show about 400 days in a Devonian year.",
  lat=[0, 40], cls=("Anthozoa", "Rugosa", "Zaphrentidae"))
E("Pleurodictyum", "genus", "sea", "tabulate", 410, 380, ["eu", "af-n", "na-e", "sa", "au"],
  "A small, disc-shaped tabulate coral colony that often grew around a worm living in its base.",
  cls=("Anthozoa", "Tabulata", "Micheliniidae"))
E("Mcnamaraspis", "genus", "sea", "placoderm", 382, 378, ["au-w"],
  "A half-metre arthrodire placoderm of the Gogo reef, preserved in three dimensions in limestone nodules -- the state fossil of Western Australia.",
  cls=("Placodermi", "Arthrodira", "Camuropiscidae"))
E("Materpiscis", "genus", "sea", "placoderm", 382, 378, ["au-w"],
  "A 25-centimetre ptyctodont placoderm of the Gogo reef preserved with an embryo and its umbilical cord -- the oldest known live birth.",
  cls=("Placodermi", "Ptyctodontida", "Ptyctodontidae"))
E("Tornoceras", "genus", "sea", "ammonite", 390, 360, ["na-e", "na-w", "eu", "af-n", "as-s", "au-w"],
  "A small, smooth goniatite with a zigzag suture, one of the commonest ammonoids of the Middle and Late Devonian seas.",
  cls=("Cephalopoda", "Goniatitida", "Tornoceratidae"))
E("Clymenia", "genus", "sea", "ammonite", 368, 359, ["eu", "af-n", "au-w", "as-c"],
  "A clymeniid ammonoid, whose siphuncle ran along the inner side of the shell -- the reverse of every other ammonoid -- living only in the last ten million years of the Devonian.",
  cls=("Cephalopoda", "Clymeniida", "Clymeniidae"))

# ================================================== CARBONIFEROUS-PERMIAN SEA
E("Gigantoproductus", "genus", "sea", "brachiopod", 340, 325, ["eu", "af-n", "as-c", "as-s"],
  "The largest brachiopod ever: a productid up to thirty centimetres wide, lying in dense shell beds on the Mississippian sea floor.",
  cls=("Brachiopoda", "Productida", "Monticuliferidae"))
E("Lithostrotion", "genus", "sea", "horncoral", 345, 325, ["eu", "na", "af-n", "as", "au-e"],
  "A colonial rugose coral whose bundled columns built thickets on the warm Mississippian limestone shelves.",
  lat=[0, 40], cls=("Anthozoa", "Rugosa", "Lithostrotionidae"))
E("Falcatus", "genus", "sea", "shark", 326, 318, ["na-w"],
  "A thirty-centimetre shark of the Bear Gulch lagoon; males carried a spine curving forward over the head like a sickle, used, it seems, in courtship.",
  cls=("Chondrichthyes", "Symmoriiformes", "Falcatidae"))
E("Koninckopora", "genus", "sea", "seaweed", 345, 325, ["eu", "af-n", "as", "na-w", "au-e"],
  "A dasyclad green alga whose calcified branches make up part of many Mississippian limestones.",
  lat=[0, 40], cls=("Chlorophyta", "Dasycladales", ""))
E("Archaeolithophyllum", "genus", "sea", "seaweed", 315, 295, ["na-w", "na-e", "eu"],
  "A leafy calcareous red alga that grew in thickets on Pennsylvanian shelves, building the 'phylloid algal mounds' that now hold oil.",
  cls=("Rhodophyta", "", ""))
E("Parafusulina", "genus", "sea", "largeforam", 280, 265, ["na-w", "as", "eu-s"],
  "A large fusulinid: a single cell shaped like a grain of rice, up to a few centimetres long, so common that some Permian limestones are made of little else.",
  cls=("Foraminifera", "Fusulinida", "Schwagerinidae"))
E("Neoschwagerina", "genus", "sea", "largeforam", 270, 260, ["as-s", "as-sb", "as-ic", "as-w", "eu-s", "na-w"],
  "A spindle-shaped fusulinid with a maze of inner walls, the mark of the Middle Permian Tethys -- found in North America only in terranes rafted in from that ocean.",
  cls=("Foraminifera", "Fusulinida", "Neoschwagerinidae"))
E("Waagenoceras", "genus", "sea", "ammonite", 275, 265, ["na-w", "eu-s", "as-ic"],
  "A goniatite with an intricately frilled suture, from the Middle Permian reef seas of west Texas, Sicily and Timor.",
  cls=("Cephalopoda", "Goniatitida", "Cyclolobidae"))
E("Cyclolobus", "genus", "sea", "ammonite", 260, 252, ["in", "mg", "as-w"],
  "One of the last of the Palaeozoic ammonoids, a Late Permian form with a finely frilled suture, from the Salt Range and Madagascar.",
  cls=("Cephalopoda", "Goniatitida", "Cyclolobidae"))
E("Mizzia", "genus", "sea", "seaweed", 275, 255, ["na-w", "as-s", "eu-s", "as-ic", "as-w"],
  "A green alga built of chains of calcified beads, one of the main sediment-makers of the Permian reef lagoons, from the Capitan reef of Texas to the Tethys.",
  lat=[0, 35], cls=("Chlorophyta", "Dasycladales", ""))


# ============================== DEVONIAN-CARBONIFEROUS LAND ARTHROPODS AND PLANTS
# (springtails and mites stood on 76-85% of the land cards of 325-400 Ma)
E("Leverhulmia", "genus", "land", "myriapod", 411, 405, ["eu-n"],
  "A many-legged myriapod of the Rhynie hot-spring marsh, one of the first animals to walk on land among the first plants.",
  cls=("Myriapoda", "", ""))
E("Crussolum", "genus", "land", "myriapod", 410, 380, ["eu-n", "na-e"],
  "One of the oldest centipedes, known from its legs in the Rhynie chert and the Gilboa forest -- already a venomous hunter of the early undergrowth.",
  cls=("Myriapoda", "Scutigeromorpha", ""))
E("Gigantoscorpio", "genus", "land", "scorpion", 340, 330, ["eu-n"],
  "A Mississippian scorpion some 35 centimetres long from the lake shores of Scotland -- one of the first scorpions certainly built for land.",
  cls=("Arachnida", "Scorpiones", ""))
E("Delitzschala", "genus", "air", "dragonfly", 325, 320, ["eu"],
  "One of the oldest winged insects, a palaeodictyopteran from the Early Carboniferous -- flight had begun, 150 million years before any other animal flew.",
  cls=("Insecta", "Palaeodictyoptera", "Spilapteridae"))
E("Stenodictya", "genus", "air", "dragonfly", 310, 300, ["eu"],
  "A palaeodictyopteran with patterned, net-veined wings and a beak for sucking plant juices, from the coal forests of France.",
  cls=("Insecta", "Palaeodictyoptera", "Dictyoneuridae"))
E("Mazothairos", "genus", "air", "dragonfly", 310, 307, ["na-e"],
  "A palaeodictyopteran with a wingspan of up to half a metre and a sucking beak, from the coal-swamp nodules of Illinois.",
  cls=("Insecta", "Palaeodictyoptera", "Homoiopteridae"))
E("Euproops", "genus", "fresh", "horseshoecrab", 315, 295, ["na-e", "eu"],
  "A small horseshoe crab of the coal-swamp pools, with spined edges to its shield -- a freshwater cousin of the living Limulus.",
  cls=("Merostomata", "Xiphosurida", "Euproopidae"))
E("Acantherpestes", "genus", "land", "myriapod", 310, 300, ["na-e", "eu"],
  "A spiny millipede of the coal forests, up to thirty centimetres long -- smaller kin of the giant Arthropleura.",
  cls=("Myriapoda", "Diplopoda", "Euphoberiidae"))
E("Graeophonus", "genus", "land", "spider", 315, 300, ["na-e", "eu"],
  "A whip spider of the coal forests, with long raptorial forelegs -- the arachnid order has barely changed since.",
  cls=("Arachnida", "Amblypygi", "Graeophonidae"))
E("Sphenopteridium", "genus", "land", "seedfern", 355, 325, ["eu", "na", "af-n", "au-e", "as-s"],
  "A Mississippian seed fern with finely divided, wedge-lobed fronds, among the first seed plants to spread across the continents.",
  lat=[0, 50], cls=("Pteridospermatopsida", "Lyginopteridales", ""))
E("Lyginopteris", "genus", "land", "seedfern", 330, 310, ["eu", "na"],
  "A scrambling seed fern with glandular hairs on its stems, one of the first plants whose seed-bearing life was worked out from fossils.",
  lat=[0, 35], cls=("Pteridospermatopsida", "Lyginopteridales", "Lyginopteridaceae"))
E("Mariopteris", "genus", "land", "seedfern", 320, 300, ["eu", "na", "af-n", "as-ne", "as-s"],
  "A climbing seed fern that hung on tree ferns and scale trees by hooked frond tips -- the lianas of the coal forests.",
  lat=[0, 35], cls=("Pteridospermatopsida", "Callistophytales", "Mariopteridaceae"))

write("x-palaeozoic-regional.json")
