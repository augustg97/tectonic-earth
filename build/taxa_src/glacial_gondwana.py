"""Life of glaciated Gondwana, 335-290 Ma: the Late Palaeozoic Ice Age at the
pole. The polar rule (biota.is_polar) now applies through this window, so a
card at 75 S in the Pennsylvanian shows only what is at home on tundra and ice
-- and the registry had almost nothing to offer it but mosses."""
from _lib import E, T, write

G = ["sa-s", "sa-n", "af-s", "af-e", "in", "au", "an", "mg"]

E("Nothorhacopteris", "genus", "land", "fern", 345, 300, G,
  "A fern-like seed plant of Carboniferous Gondwana, the commonest fossil of the cold country between the ice sheets; its name is a flora as much as a plant.",
  hab=["tundra", "wetland", "forest"], cls=("", "Pteridospermales", ""))
E("Bumbudendron", "genus", "land", "lycopod", 330, 300, ["sa-s"],
  "A small tree lycopsid of Carboniferous Argentina, growing in the outwash plains in front of Gondwana's glaciers.",
  hab=["tundra", "wetland"], cls=("Lycopodiopsida", "Lepidodendrales", ""))
E("Paranocladus", "genus", "land", "conifer", 299, 270, ["sa-s", "af-s"],
  "An early conifer of Permian Gondwana, in the Parana and Karoo basins as the ice withdrew.",
  hab=["forest", "tundra"], cls=("Pinopsida", "Voltziales", ""))
E("Collembola", "order", "land", "springtail", 410, 0, ["cosmo", "an"],
  "Springtails, among the first land animals -- Rhyniella from the Rhynie chert is Early Devonian -- and among the last to give up before the ice; they live in every soil on Earth.",
  hab=["forest", "rainforest", "tundra", "ice", "wetland", "alpine", "grassland", "desert", "island", "coast"],
  cls=("Collembola", "", ""))
E("Oribatida", "suborder", "land", "spider", 380, 0, ["cosmo", "an"],
  "Oribatid mites, the slow armoured grazers of leaf litter and moss, in the soil of every land ecosystem since the Devonian.",
  hab=["forest", "rainforest", "tundra", "ice", "wetland", "alpine", "grassland", "island", "coast"],
  cls=("Arachnida", "Sarcoptiformes", ""))
E("Tillites", "informal", "land", "strata", 3000, 0, ["cosmo"],
  "Tillite: the unsorted rubble a glacier leaves, cemented to rock. Gondwana's Carboniferous-Permian tillites lie on five continents, and their scratched pavements were among the first evidence that those continents had once been one.",
  hab=["ice", "tundra"], fill=None)
write("x-glacial-gondwana.json")
