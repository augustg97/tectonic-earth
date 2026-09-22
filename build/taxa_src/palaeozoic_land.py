"""Devonian to Permian land life beyond Euramerica, at genus level.

The coal forests of Euramerica were well served; Gondwana, Cathaysia, Angara
and the Devonian shores of Australia, China and Antarctica were mostly
"Temnospondyli, Odonatoptera, Blattodea". These are the animals and plants the
PBDB menus and the regional literature put there.
"""
from _lib import E, T, write

GOND = ["sa-s", "sa-n", "af-s", "af-e", "af-n", "in", "au", "an", "mg", "ar"]
CATH = ["as-e", "as-se"]                    # North and South China, Indochina
ANG = ["as-n", "as-c", "eu"]                # Siberia, Kazakhstan, the Urals and Pechora

# ------------------------------------------------------ Devonian Gondwana and Asia
E("Aztec fish fauna", "informal", "fresh", "placoderm", 390, 380, ["an", "au"],
  "The Middle Devonian fishes of the Aztec Siltstone in the Transantarctic Mountains -- placoderms, acanthodians, lungfish and early sharks in rivers and lakes at 30 degrees south.",
  hab=["river", "lake"], rep="Bothriolepis", assemblage=True)
E("Groenlandaspis", "genus", "fresh", "placoderm", 385, 359, ["gl", "an", "au", "eu", "na-e", "af-n"],
  "A small placoderm with a tall crest on its trunk armour, in fresh water from Greenland to Antarctica and Australia: the first fish genus shown to span both hemispheres.",
  hab=["river", "lake", "coast"], realms=["fresh", "sea"], cls=("Placodermi", "Arthrodira", "Groenlandaspididae"))
E("Gogonasus", "genus", "sea", "lobefin", 384, 380, ["au"],
  "A lobe-finned fish from the Gogo reef of Western Australia, preserved whole in three dimensions, with the wrist bones and nostrils of a fish on its way to land.",
  hab=["reef", "shelf"], cls=("Sarcopterygii", "Tetrapodomorpha", "Megalichthyidae"))
E("Metaxygnathus", "genus", "fresh", "stemtetrapod", 365, 360, ["au"],
  "A Late Devonian tetrapod known from a jaw found in New South Wales, the first sign that the earliest four-limbed animals were in Gondwana as well as in Greenland.",
  hab=["river", "wetland"], cls=("Stegocephalia", "", ""))
E("Tulerpeton", "genus", "fresh", "stemtetrapod", 365, 360, ["eu"],
  "A six-toed Devonian tetrapod from the Tula region of Russia, with limbs strong enough to walk on the bottom.",
  hab=["coast", "river"], cls=("", "", "Tulerpetontidae"))
E("Leclercqia", "genus", "land", "zosterophyll", 390, 380, ["na-e", "eu", "au", "as-e"],
  "A Middle Devonian clubmoss with hooked leaf tips for climbing, known from New York to Australia: one of the first plants to spread across both hemispheres.",
  hab=["wetland", "coast"], cls=("Lycopodiopsida", "Protolepidodendrales", ""))
E("Drepanophycus", "genus", "land", "zosterophyll", 410, 380, ["eu", "na-e", "as-e", "as-n", "au"],
  "A sprawling Devonian lycopsid with sickle-shaped leaves, among the first plants with true leaves, on the shores of Laurussia and China alike.",
  hab=["wetland", "coast"], cls=("Lycopodiopsida", "Drepanophycales", "Drepanophycaceae"))
E("Guangdedendron", "genus", "land", "lycopod", 372, 365, ["as-e"],
  "The lycopsid of the Xinhang forest of Anhui, the oldest forest known in Asia: thousands of trees preserved standing in a Late Devonian coastal swamp.",
  hab=["wetland", "coast", "forest"], cls=("Lycopodiopsida", "Lepidodendrales", ""))
E("Protolepidodendron", "genus", "land", "zosterophyll", 400, 385, ["as-e", "eu", "na-e"],
  "An early lycopsid of the Devonian of China and Europe, low and branching, before the tree forms of its group.",
  hab=["wetland", "coast"], cls=("Lycopodiopsida", "Protolepidodendrales", ""))
E("Sporogonites", "genus", "land", "moss", 415, 400, ["eu", "au", "as-e"],
  "A Devonian plant known from spore capsules on short stalks, close to the mosses; found in Belgium, China and Australia.",
  hab=["wetland", "coast"], cls=("", "", ""))

# ------------------------------------------------------ Carboniferous beyond Euramerica
E("Hastimima", "genus", "fresh", "eurypterid", 290, 274, ["sa-s"],
  "A eurypterid of the Permian of Brazil, one of the last of its kind, in the rivers and lakes of Gondwana.",
  hab=["river", "lake"], cls=("Merostomata", "Eurypterida", "Hibbertopteridae"))
E("Rhacopteris", "genus", "land", "fern", 345, 300, GOND + ["eu", "na-e"],
  "A fern-like seed plant with fan-shaped leaflets, the signature plant of the Early Carboniferous of eastern Australia and Argentina.",
  hab=["wetland", "forest", "tundra"], cls=("", "Pteridospermales", ""))
E("Lepidodendropsis", "genus", "land", "lycopod", 345, 320, GOND + ["as-e", "na-e", "na-w", "eu"],
  "An early tree lycopsid of Mississippian Gondwana and North Africa, before Lepidodendron proper.",
  hab=["wetland", "coast"], cls=("Lycopodiopsida", "Lepidodendrales", ""))
E("Angaropteridium", "genus", "land", "seedfern", 330, 270, ANG,
  "An Angaran seed fern, its fronds among the commonest plant fossils of the Kuznetsk Basin coal measures.",
  hab=["forest", "wetland"], cls=("", "Pteridospermales", ""))
E("Paracalamites", "genus", "land", "horsetail", 330, 252, ANG + GOND,
  "A horsetail with unbranched stems, the Angaran and Gondwanan counterpart of Calamites, along every Permian riverbank of Siberia and the Glossopteris country.",
  hab=["wetland", "river"], cls=("Equisetopsida", "Equisetales", ""))
E("Lobatannularia", "genus", "land", "horsetail", 300, 252, CATH,
  "A horsetail with whorls of lobed leaves, one of the plants that define the Cathaysian flora of the Permian coal swamps of China.",
  hab=["wetland", "forest"], cls=("Equisetopsida", "Equisetales", ""))

# ------------------------------------------------------------- Permian Cathaysia
E("Emplectopteris", "genus", "land", "seedfern", 295, 260, CATH,
  "A Cathaysian seed fern with netted leaf veins, of the Permian coal swamps of North China.",
  hab=["forest", "wetland"], cls=("", "Gigantopteridales", ""))
E("Tingia", "genus", "land", "progymnosperm", 299, 252, CATH,
  "A Cathaysian plant with two rows of leaves of two sizes, of uncertain kinship; it grew in the wet Permian forests of China and nowhere else.",
  hab=["forest", "wetland"], cls=("", "Noeggerathiales", ""))
E("Sinophoneus", "genus", "land", "dinocephalian", 268, 262, ["as-e"],
  "A dinocephalian therapsid of the Xidagou Formation, Gansu: the Chinese cousin of the Karoo's Moschops.",
  hab=["forest", "grassland"], cls=("Synapsida", "Therapsida", "Anteosauridae"))
E("Bolosaurus", "genus", "land", "lizard", 290, 270, ["na-w", "as-e"],
  "A small early reptile with chewing teeth, of the Permian of Texas and, as its relative Belebey, of Russia and China.",
  hab=["forest", "wetland"], cls=("Reptilia", "", "Bolosauridae"))
E("Shihtienfenia", "genus", "land", "pareiasaur", 259, 254, ["as-e"],
  "A pareiasaur of the Late Permian of Shanxi, a barrel-bodied plant-eater armoured with bony studs.",
  hab=["forest", "wetland"], cls=("Reptilia", "Procolophonomorpha", "Pareiasauridae"))
E("Jimusaria", "genus", "land", "dicynodont", 256, 252, ["as-e", "as-c"],
  "A dicynodont of the Junggar Basin at the very end of the Permian, one of the tusked plant-eaters that were about to inherit the Earth.",
  hab=["forest", "wetland", "grassland"], cls=("Synapsida", "Therapsida", "Dicynodontidae"))

# ------------------------------------------------------------- Permian Gondwana
E("Bradysaurus", "genus", "land", "pareiasaur", 265, 260, ["af-s"],
  "The commonest large animal of the middle Permian Karoo, a two-and-a-half-metre pareiasaur with a warty hide, in herds on the floodplain.",
  hab=["grassland", "wetland", "forest"], cls=("Reptilia", "Procolophonomorpha", "Pareiasauridae"))
E("Diictodon", "genus", "land", "dicynodont", 265, 252, ["af-s", "as-e"],
  "A pig-sized dicynodont that dug spiral burrows in the Karoo floodplain; the most abundant vertebrate fossil of the Late Permian of South Africa.",
  hab=["grassland", "wetland", "forest"], w=2, cls=("Synapsida", "Therapsida", "Pylaecephalidae"))
E("Procynosuchus", "genus", "land", "cynodont", 259, 252, ["af-s", "af-e", "eu"],
  "The earliest well-known cynodont, from the Late Permian of the Karoo, Zambia and Germany, with a paddle-like tail that suggests it swam.",
  hab=["wetland", "forest", "river"], cls=("Synapsida", "Therapsida", "Procynosuchidae"))
E("Endothiodon", "genus", "land", "dicynodont", 262, 254, ["af-s", "af-e", "in", "sa-s"],
  "A large dicynodont with rows of cheek teeth, found from the Karoo to India and Brazil: one of the animals that show Permian Gondwana was one country.",
  hab=["grassland", "wetland", "forest"], cls=("Synapsida", "Therapsida", "Endothiodontidae"))
E("Stereosternum", "genus", "fresh", "mesosaur", 290, 275, ["sa-s", "af-s"],
  "A small mesosaur of the Irati and Whitehill shales, in the inland sea shared by Brazil and South Africa before the Atlantic; with Mesosaurus, early evidence for drift.",
  hab=["lake", "coast"], realms=["fresh", "sea"], cls=("Reptilia", "Mesosauria", "Mesosauridae"))
E("Karoo insect fauna", "informal", "land", "beetle", 265, 252, ["af-s"],
  "Beetles, cockroaches, dragonflies and the first true bugs of the Karoo's Permian, preserved as wings in the lake shales.",
  hab=["wetland", "forest"], rep="Coleoptera", assemblage=True)
E("Sphenophyllum", "genus", "land", "horsetail", 360, 252, ["cosmo"],
  "A slender sphenopsid with wedge-shaped leaves in whorls, a scrambling plant of Carboniferous and Permian swamps on every continent.",
  hab=["wetland", "forest"], cls=("Equisetopsida", "Sphenophyllales", "Sphenophyllaceae"))
E("Buriadia", "genus", "land", "conifer", 290, 260, ["in", "au", "af-s", "sa-s"],
  "An early conifer of the Glossopteris country, in Permian India and Australia, when conifers were still rare south of the tropics.",
  hab=["forest"], cls=("Pinopsida", "Voltziales", "Buriadiaceae"))
E("Schizoneura", "genus", "land", "horsetail", 290, 200, GOND + ["as-e", "eu"],
  "A horsetail with paired leaves fused into sheaths, common through the Permian and Triassic of Gondwana.",
  hab=["wetland", "river"], cls=("Equisetopsida", "Equisetales", ""))

# ----------------------------------------------------- Permian Angara and Russia
E("Kotelnich fauna", "informal", "land", "gorgonopsian", 260, 255, ["eu"],
  "The Late Permian tetrapods of Kotelnich on the Vyatka: pareiasaurs, gorgonopsians and the earliest cynodont-like therapsids, from a riverbank where they are found standing in their burrows.",
  hab=["wetland", "river", "forest"], rep="Inostrancevia", assemblage=True)
E("Deltavjatia", "genus", "land", "pareiasaur", 260, 255, ["eu"],
  "The pareiasaur of Kotelnich, known from dozens of skeletons, a plant-eater the size of a cow.",
  hab=["wetland", "forest"], cls=("Reptilia", "Procolophonomorpha", "Pareiasauridae"))
E("Suminia", "genus", "land", "dicynodont", 260, 255, ["eu"],
  "A small anomodont from Kotelnich with a grasping hand and long tail: the earliest tree-climbing vertebrate known.",
  hab=["forest"], cls=("Synapsida", "Therapsida", "Venyukoviidae"))
E("Kuznetsk flora", "informal", "land", "cordaite", 300, 252, ["as-n"],
  "The Permian coal flora of the Kuznetsk Basin: Rufloria and Cordaites forests with Angaropteridium beneath them, the counterpart in cool Angara of the Glossopteris forests of the south.",
  hab=["forest", "wetland"], rep="Rufloria", assemblage=True)
E("Vojnovskya", "genus", "land", "cordaite", 290, 252, ["as-n", "as-c"],
  "A strap-leaved Angaran gymnosperm with cone-like fertile shoots, of the Permian of Siberia.",
  hab=["forest"], cls=("", "Vojnovskyales", ""))
write("x-palaeozoic-land.json")
