"""The Cryogenian seas, the first ten million years of the Cambrian, and the
Cambrian by block from the first trilobites to the Furongian.

The Precambrian's generic remainder after 3.10 is the Cryogenian, whose cards
read "Chlorophyta, Rhodophyta, Porifera" because its record is thin -- but not
empty: the interglacial shales have Bavlinella and Leiosphaeridia, the Datangpo
Formation its microfossils, the Twitya Formation the first discs. The earliest
Cambrian (541-521 Ma) was one small-shelly list on every continent; the record
names the sclerites and tubes, and the first trilobites of each block have
names too: Fallotaspis in Morocco and Nevada, Profallotaspis in Siberia,
Callavia in Avalonia, Abadiella in Australia, Yunnanocephalus at Chengjiang.
The Miaolingian and Furongian of Laurentia, Gondwana and Cathaysia follow.
"""
from _lib import E, T, write

# ------------------------------------------------------------- the Cryogenian
E("Bavlinella faveolata", "species", "sea", "microbe", 720, 635, ["cosmo"],
  "Clusters of tiny cells packed into a mulberry-shaped colony, the commonest fossil of the Cryogenian interglacial shales on every continent; a cyanobacterium or a stressed eukaryote, either way the plankton of the seas between the snowballs.",
  hab=["pelagic", "shelf"], cls=("", "", ""))
E("Leiosphaeridia", "genus", "sea", "acritarch", 1800, 250, ["cosmo"],
  "Smooth-walled spheres without ornament, a form genus that holds the resting cysts of countless Proterozoic and Palaeozoic algae; in the Cryogenian, after the spiny acritarchs died back, they are most of what the seas left.",
  hab=["pelagic", "shelf"], cls=("", "Acritarcha", ""))
E("Datangpo microfossils", "informal", "sea", "acritarch", 663, 654, ["as-s"],
  "Organic-walled microfossils and Bavlinella colonies in the manganese-bearing black shales of the Datangpo Formation of South China: life in the ten-million-year interglacial between the Sturtian and Marinoan ice.",
  hab=["shelf", "pelagic"], rep="Bavlinella faveolata", assemblage=True)
E("Twitya discs", "informal", "sea", "jellyfish", 650, 640, ["na-n"],
  "Simple discs and rings a centimetre across in the Twitya Formation of the Mackenzie Mountains, laid down between the two Cryogenian glaciations: the oldest candidates for the Ediacaran kind of large body, ten million years before the Marinoan ice.",
  hab=["shelf", "deep"], rep="Cyclomedusa", assemblage=True)
E("Fifteenmile scale microfossils", "informal", "sea", "acritarch", 811, 740, ["na-n"],
  "Mineralised scales a few microns across, of a dozen shapes, from the Fifteenmile Group of the Yukon: the armour of Tonian eukaryotes, the first biomineralisation known, laid down in the shallow sea of Laurentia's western edge before the Sturtian ice.",
  hab=["shelf", "coast"], rep="Trachyhystrichosphaera", assemblage=True)

# ----------------------------------------------- the last Ediacaran tubes
E("Vendotaenia", "genus", "sea", "seaweed", 580, 541, ["cosmo"],
  "Ribbon-shaped carbonaceous compressions a millimetre wide and centimetres long, on Ediacaran bedding planes from the White Sea to South China: an alga or a sulphur bacterium, and among the commonest fossils of the age.",
  hab=["shelf", "deep"], cls=("", "", ""))
E("Sinotubulites", "genus", "sea", "tubeworm", 550, 539, ["as-s", "as-ne", "na-w", "sa-s"],
  "A tube of nested layers, a centimetre long, from the last Ediacaran of South China, Nevada and Brazil: one of the first animals with a mineral skeleton, beside Cloudina.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Corumbella werneri", "species", "sea", "tubeworm", 545, 541, ["sa-s", "sa-n", "na-w"],
  "A four-sided organic tube with a mineral coat from the Tamengo Formation of Brazil, also in Nevada: read as a stalked cnidarian, a scyphozoan polyp fixed to the last Ediacaran sea floor.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Gaojiashania", "genus", "sea", "worm", 551, 541, ["as-ne", "as-s", "na-w"],
  "A segmented ribbon of the Gaojiashan biota of Shaanxi, a few centimetres long, pyritised in three dimensions: an animal of the last Ediacaran sea floor whose kind is still argued.",
  hab=["shelf"], cls=("", "", ""))
E("Conotubus", "genus", "sea", "tubeworm", 551, 541, ["as-ne", "na-w"],
  "A tube of nested cones from the Gaojiashan biota of Shaanxi, pyritised and preserved whole: the organic-walled kin of Cloudina, and one of the first animals to build a tube to live in.",
  hab=["shelf"], cls=("", "", ""))

# ------------------------------------------- the earliest Cambrian (541-521)
E("Protohertzina", "genus", "sea", "conodont", 541, 530, ["cosmo"],
  "Curved phosphatic spines a millimetre long, the grasping teeth of an arrow-worm-like animal, and the first tooth-shaped fossils of the Cambrian: Protohertzina anabarica marks the Fortunian on every continent.",
  hab=["pelagic", "shelf"], cls=("", "", ""))
E("Watsonella crosbyi", "species", "sea", "bivalve", 535, 528, ["cosmo"],
  "A tiny laterally compressed shell, a mollusc near the root of the bivalves and rostroconchs, whose first appearance is the candidate marker for the second stage of the Cambrian from Siberia to Newfoundland and China.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Lapworthella", "genus", "sea", "sclerite", 530, 510, ["cosmo"],
  "Conical phosphatic sclerites with ribbed sides, the armour of a tommotiid, a lophophorate that wore a coat of them; among the commonest small shelly fossils of the early Cambrian.",
  hab=["shelf"], cls=("", "Tommotiida", ""))
E("Sunnaginia", "genus", "sea", "sclerite", 530, 521, ["as-n", "eu-n", "na-av"],
  "A tommotiid of the Tommotian of Siberia and the Avalonian shelves of England and Newfoundland, known from its sclerites; a zone fossil of the stage that first showed the Cambrian had begun before the trilobites.",
  hab=["shelf"], cls=("", "Tommotiida", ""))
E("Tommotia", "genus", "sea", "sclerite", 530, 521, ["cosmo"],
  "The tommotiid that named the Tommotian stage of Siberia: asymmetric phosphatic caps, paired left and right, that armoured a sessile animal on the earliest Cambrian sea floor.",
  hab=["shelf"], cls=("", "Tommotiida", ""))
E("Hyolithellus", "genus", "sea", "tubeworm", 535, 500, ["cosmo"],
  "A slender phosphatic tube a few millimetres long, once taken for a hyolith and now for the dwelling of a worm, on Cambrian shelves everywhere.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Coleoloides", "genus", "sea", "tubeworm", 535, 515, ["na-av", "eu-n", "as-n"],
  "Calcareous tubes standing in dense stands on the earliest Cambrian shelves of Avalonia -- the Bonavista Peninsula, Massachusetts, Shropshire -- and Siberia.",
  hab=["shelf", "coast"], cls=("", "", ""))
E("Rhombocorniculum", "genus", "sea", "sclerite", 525, 515, ["cosmo"],
  "Slender phosphatic spines with a rhombic cross-section, the sclerites of an unknown animal, whose first appearance marks Cambrian Stage 3 from Siberia and Avalonia to China and Australia.",
  hab=["shelf"], cls=("", "", ""))
E("Halkieria", "genus", "sea", "sclerite", 525, 510, ["gl", "eu-n", "as-n", "au-e", "as-s"],
  "A slug-shaped animal armoured with two thousand sclerites and a shell at each end, known whole from Sirius Passet in Greenland and from its scattered sclerites on most early Cambrian shelves.",
  hab=["shelf"], cls=("", "", "Halkieriidae"))
E("Shackleton Limestone reefs", "informal", "sea", "archaeocyath", 525, 510, ["an"],
  "Archaeocyath reefs of the Shackleton Limestone in the Transantarctic Mountains: the Cambrian sea over the edge of East Antarctica, at the equator, building the first animal reefs beside Australia's.",
  hab=["reef", "shelf"], rep="Archaeocyathus", assemblage=True)

# ------------------------------------------ the first trilobites, by block
E("Fallotaspis", "genus", "sea", "trilobite", 521, 517, ["af-n", "na-w"],
  "Among the first trilobites anywhere: a flat, wide-headed olenelloid of the Anti-Atlas of Morocco and the Fallotaspis zone of Nevada and California, at the base of the trilobite record.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Fallotaspididae"))
E("Profallotaspis", "genus", "sea", "trilobite", 521, 518, ["as-n"],
  "Siberia's first trilobite, from the lower Atdabanian of the Lena river: a fallotaspidoid at the very start of the Siberian trilobite record.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Fallotaspididae"))
E("Callavia", "genus", "sea", "trilobite", 517, 512, ["na-av", "eu-n"],
  "The large olenelloid of the Avalonian shelves -- the Brigus Formation of Newfoundland, the Comley limestones of Shropshire, the Braintree slates of Massachusetts -- Avalonia's own first trilobite.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Callaviidae"))
E("Serrodiscus", "genus", "sea", "agnostid", 518, 510, ["na-av", "eu-n", "eu-s", "as-n", "na-w"],
  "A tiny eodiscid a few millimetres long with a serrated tail, of the early Cambrian of Avalonia, Siberia, Spain and Laurentia: small, blind and everywhere.",
  hab=["shelf"], cls=("Trilobita", "Agnostida", "Eodiscidae"))
E("Bergeroniellus", "genus", "sea", "trilobite", 518, 512, ["as-n"],
  "A Siberian trilobite of the Botomian stage, the zone fossil of the Lena and Aldan shelves in the middle of the early Cambrian.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Bergeroniellidae"))
E("Judomia", "genus", "sea", "trilobite", 520, 515, ["as-n", "gl", "na-n"],
  "An Atdabanian trilobite of the Siberian platform, with a pygidium of many segments, from the shelves that ringed the Siberian craton at the equator.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Judomiidae"))
E("Yunnanocephalus", "genus", "sea", "trilobite", 520, 515, ["as-s", "au-e"],
  "A small trilobite of the Chengjiang beds of Yunnan, preserved with its limbs and antennae, among the animals with which South China's trilobite record begins.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Yunnanocephalidae"))
E("Abadiella", "genus", "sea", "trilobite", 520, 514, ["au-e", "an", "as-s"],
  "Australia's first trilobite: Abadiella huoi of the Flinders Ranges and the Stansbury basin, a redlichiid at the base of the Australian trilobite record.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Abadiellidae"))
E("Estaingia", "genus", "sea", "trilobite", 515, 511, ["au-e", "as-s"],
  "The commonest animal of the Emu Bay Shale of Kangaroo Island, a small trilobite preserved by the thousand, some with the bite marks of Anomalocaris.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Estaingiidae"))
E("Balcoracania", "genus", "sea", "trilobite", 515, 511, ["au-e"],
  "A trilobite of the Emu Bay Shale with more thoracic segments than almost any other -- over a hundred -- the record-holder among all trilobites.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Emuellidae"))

# ------------------------------------------------ the Miaolingian (509-497)
E("Kootenia", "genus", "sea", "trilobite", 512, 500, ["na-w", "na-e", "na-n", "gl", "as-n", "au-e"],
  "A corynexochid with a spiny pygidium of the Cambrian shelves of Laurentia, Siberia and Australia, common in the Burgess Shale and the limestones around it.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Dorypygidae"))
E("Olenoides", "genus", "sea", "trilobite", 512, 500, ["na-w", "na-e", "na-n", "gl", "as-n", "as-s"],
  "The big trilobite of the Burgess Shale, a hand long, preserved with its legs, gills and antennae: the animal that showed what a trilobite carried under its shield.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Dorypygidae"))
E("Ogygopsis", "genus", "sea", "trilobite", 510, 505, ["na-w"],
  "The trilobite of the Mount Stephen beds above Field, British Columbia, which lie thick with its moults: found before the Burgess Shale, and the reason Walcott came.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Dolichometopidae"))
E("Bathyuriscus", "genus", "sea", "trilobite", 512, 500, ["na-w", "na-e", "na-n"],
  "A smooth-shelled corynexochid of the Laurentian outer shelf, in the Burgess Shale, the Wheeler Shale and the limestones between them.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Dolichometopidae"))
E("Zacanthoides", "genus", "sea", "trilobite", 510, 500, ["na-w", "na-e"],
  "A spiny trilobite of the middle Cambrian of Laurentia, its pleurae drawn out into long points, from the Wheeler Shale of Utah to the Rockies.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Zacanthoididae"))
E("Peronopsis", "genus", "sea", "agnostid", 510, 497, ["cosmo"],
  "A blind agnostoid a few millimetres long, head and tail nearly identical, drifting or crawling on Cambrian sea floors worldwide; in the Wheeler Shale it is the commonest fossil of all.",
  hab=["shelf", "pelagic"], cls=("Trilobita", "Agnostida", "Peronopsidae"))
E("Oryctocephalus indicus", "species", "sea", "trilobite", 509, 505, ["cosmo"],
  "A spiny-tailed trilobite whose first appearance at Balang in Guizhou defines the base of the Wuliuan and the Miaolingian series, found from India and Siberia to Nevada.",
  hab=["shelf"], cls=("Trilobita", "Corynexochida", "Oryctocephalidae"))
E("Pagetia", "genus", "sea", "agnostid", 512, 500, ["cosmo"],
  "A tiny eodiscid with eyes, a spine on its head and a spine on its tail, of the middle Cambrian on every shelf from Laurentia to Australia.",
  hab=["shelf"], cls=("Trilobita", "Agnostida", "Eodiscidae"))
E("Xystridura", "genus", "sea", "trilobite", 510, 504, ["au-e", "an"],
  "A large flat trilobite of the middle Cambrian of Queensland and the Northern Territory, the zone fossil of the Australian Templetonian.",
  hab=["shelf"], cls=("Trilobita", "Redlichiida", "Xystriduridae"))

# --------------------------------------------------- the Furongian (497-485)
E("Glyptagnostus reticulatus", "species", "sea", "agnostid", 497, 495, ["cosmo"],
  "A net-patterned agnostoid whose first appearance in Hunan defines the base of the Paibian and the Furongian series; found on every continent, the standard of the late Cambrian.",
  hab=["shelf", "pelagic"], cls=("Trilobita", "Agnostida", "Glyptagnostidae"))
E("Agnostotes orientalis", "species", "sea", "agnostid", 494, 492, ["cosmo"],
  "The agnostoid whose first appearance at Duibian in Zhejiang defines the base of the Jiangshanian stage, found from Kazakhstan and Siberia to Laurentia.",
  hab=["shelf", "pelagic"], cls=("Trilobita", "Agnostida", "Agnostidae"))
E("Lotagnostus americanus", "species", "sea", "agnostid", 491, 489, ["cosmo"],
  "An agnostoid of the last Cambrian stage, proposed to define its base, from Quebec and Nevada to Kazakhstan, Australia and China.",
  hab=["shelf", "pelagic"], cls=("Trilobita", "Agnostida", "Agnostidae"))
E("Pseudagnostus", "genus", "sea", "agnostid", 500, 485, ["cosmo"],
  "A long-lived agnostoid of the late Cambrian and earliest Ordovician, on shelves everywhere; the last common agnostoid before the group dwindled.",
  hab=["shelf", "pelagic"], cls=("Trilobita", "Agnostida", "Pseudagnostidae"))
E("Irvingella", "genus", "sea", "trilobite", 494, 490, ["cosmo"],
  "A late Cambrian trilobite with long genal spines and a narrow body, from Laurentia, Siberia, Kazakhstan, Australia and China; a zone fossil across the Jiangshanian.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Elviniidae"))
E("Elvinia", "genus", "sea", "trilobite", 494, 490, ["na-w", "na-e"],
  "The Laurentian trilobite of the Elvinia zone, the standard of the late Cambrian across the Great Basin and the Appalachian shelf.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Elviniidae"))
E("Saukia", "genus", "sea", "trilobite", 492, 485, ["na-w", "na-e", "na-n", "as-ne"],
  "A large late Cambrian trilobite of the Laurentian carbonate shelf, the zone fossil of the last Cambrian stage in North America from Wisconsin to Texas.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Saukiidae"))
E("Dikelocephalus", "genus", "sea", "trilobite", 492, 486, ["na-e", "na-w"],
  "A broad trilobite the size of a hand from the late Cambrian sandstones of Wisconsin and Minnesota, the largest animal of the Laurentian shallows of its day.",
  hab=["shelf", "coast"], cls=("Trilobita", "Asaphida", "Dikelocephalidae"))
E("Proceratopyge", "genus", "sea", "trilobite", 497, 488, ["as-s", "as-ne", "as-c", "au-e", "as-n"],
  "A late Cambrian trilobite of the outer shelves of Cathaysia, Kazakhstan, Australia and Siberia, with a broad flat pygidium; a zone fossil of the Furongian on the Gondwanan and Asian side.",
  hab=["shelf", "deep"], cls=("Trilobita", "Asaphida", "Ceratopygidae"))
E("Chuangia", "genus", "sea", "trilobite", 497, 490, ["as-ne", "as-s", "as-c", "as-n"],
  "A smooth-shelled trilobite of the late Cambrian of North China, Korea and Kazakhstan, the zone fossil of the Changshanian on the North China platform.",
  hab=["shelf"], cls=("Trilobita", "Asaphida", "Chuangiidae"))
E("Kaolishania", "genus", "sea", "trilobite", 492, 488, ["as-ne", "au-e"],
  "A late Cambrian trilobite of Shandong and the North China platform, whose pustular shell names a zone of the Chinese Furongian.",
  hab=["shelf"], cls=("Trilobita", "Ptychopariida", "Kaolishaniidae"))
E("Alum Shale fauna", "informal", "sea", "trilobite", 500, 480, ["eu-n"],
  "The black Alum Shale of Scandinavia: olenid trilobites and agnostoids by the million in an oxygen-starved sea over Baltica, from the late Cambrian into the Ordovician, the source of the Furongian standard.",
  hab=["shelf", "deep"], rep="Olenus", assemblage=True)
E("Kaili biota", "informal", "sea", "cambrianarthropod", 508, 504, ["as-s"],
  "The Kaili Formation of Guizhou: a Burgess Shale-type fauna of soft-bodied arthropods, sponges, echinoderms and algae, at the base of the Miaolingian in South China.",
  hab=["shelf", "deep"], rep="Olenoides", assemblage=True)
E("Wheeler Shale fauna", "informal", "sea", "agnostid", 507, 504, ["na-w"],
  "The Wheeler Shale of the House Range of Utah: Elrathia and Peronopsis by the thousand, and a Burgess Shale-type soft-bodied fauna in the deeper beds, the commonest trilobites ever sold.",
  hab=["shelf", "deep"], rep="Peronopsis", assemblage=True)
E("Sirius Passet fauna", "informal", "sea", "cambrianarthropod", 518, 516, ["gl"],
  "The Sirius Passet locality of North Greenland: Halkieria whole, the earliest lobopods and arthropods, and the first animals with gut contents preserved, five million years before Chengjiang's twin in the west.",
  hab=["shelf", "deep"], rep="Halkieria", assemblage=True)
write("x-cryogenian-cambrian.json")
