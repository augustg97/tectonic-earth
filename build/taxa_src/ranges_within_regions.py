"""A finer address for the taxa a region code is too coarse for.

The codes are continent-sized: "na-w" is Alaska to Baja, "sa-n" is the Andes and
Amazonia together, "as-c" is the Tien Shan and Tibet. Inside one, every narrow
endemic showed on every label -- giant sequoia on the Gulf of California, Amazon
river dolphins in Lake Titicaca, edelweiss on the Urals, alligators in the Great
Lakes. This file gives those taxa a `box` (present-day lon/lat, like the codes;
[w, e, s, n]), a latitude band, a habitat, or a corrected range, and writes the
change into whichever registry file holds the entry.

Run:  python3 ranges_within_regions.py      (idempotent; re-run after editing)

A boxed taxon still shows on its whole continent's and ocean's cards -- boxes
bind only labels with a local footprint (biota.label_reach). A relict with a
wider fossil range gets a TIME-SLICED box, NOW(...), so its past is untouched.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "..", "taxa")


def NOW(*boxes, since=0.02):
    """Boxes that bind only from `since` Ma to the present."""
    return [{"t": [since, 0], "box": [list(b) for b in boxes]}]


# ---- shared geography -------------------------------------------------------
ANDES = [[-80, -71.5, -2, 11.5], [-81, -75, -10, -2], [-78, -63, -24, -10],
         [-74, -66, -40, -24], [-76, -66, -56, -40]]
PUNA = [[-77, -69, -18, -9], [-70.5, -65, -30, -17]]
AMAZONIA = [[-78, -48, -10, 6], [-66.5, -48, -16, -10]]
HIGH_ANDES = ["Lake Titicaca", "Altiplano", "Andes", "Lake Tauca"]
TEPUIS = [[-67.5, -59, 1, 7]]
PATAGONIA = [[-74, -62, -55, -36]]
ALPS = [5.5, 16.5, 43.5, 48.2]
CARPATHIANS = [17.5, 27, 44.8, 49.8]
PYRENEES = [-2, 3.2, 42, 43.3]
TIBET = [[77, 104, 27.5, 39.5]]
TIEN_SHAN = [[69, 95, 40.5, 45.5]]
BAIKAL = [[103, 110.5, 51, 56.2]]
SIERRA = [[-121.5, -117.8, 35.3, 40.5]]
IWP = [[30, 180, -35, 35], [-180, -140, -30, 30]]
CARIB = [-98, -58, 8, 31]

PATCH = {
    # ------------------------------------------------------------ North America
    "Sequoiadendron": {"box": NOW(*SIERRA, since=2.6),
                       "avoid": ["Basin and Range", "Rocky Mountains", "Colorado Plateau", "Rio Grande Rift"]},
    "Sequoia sempervirens": {"box": NOW([-124.6, -121.3, 35.8, 42.4], since=2.6)},
    "Pinus longaeva": {"box": [[-119.5, -110.5, 36, 41.5]]},
    "Yucca brevifolia": {"box": [[-118.5, -113, 33.5, 38]]},
    "Carnegiea gigantea": {"box": [[-114.6, -109, 27.5, 35]]},
    "Gopherus agassizii": {"box": [[-118, -112, 33, 38]]},
    "Heloderma suspectum": {"box": [[-116, -107, 26, 38]]},
    "Artemisia tridentata": {"box": [[-123, -103, 32, 50]]},
    "Centrocercus urophasianus": {"box": [[-122, -102, 37, 50]]},
    "Oreamnos americanus": {"box": [[-152, -109, 44, 64]]},
    "Ochotona princeps": {"box": [[-125, -104, 35, 56]]},
    "Ovis canadensis": {"box": [[-125, -100, 24, 56]]},
    "Ursus arctos horribilis": {"box": [[-168, -95, 30, 70]], "hab": ["forest", "alpine", "tundra", "grassland"]},
    "Bison bison": {"box": [[-160, -75, 27, 68]]},
    "Antilocapra": {"box": NOW([-122, -96, 22, 52])},
    "Antilocapra americana": {"box": [[-122, -96, 22, 52]]},
    "Cynomys ludovicianus": {"box": [[-113, -96, 29, 50]]},
    "Bouteloua gracilis": {"box": [[-118, -92, 20, 54]]},
    "Taxidea taxus": {"box": [[-125, -82, 18, 56]]},
    "Pseudotsuga menziesii": {"box": [[-130, -103, 19, 55]]},
    "Pinus contorta": {"box": [[-140, -104, 31, 64]]},
    "Picea glauca": {"box": [[-165, -53, 43, 69]]},
    "Picea mariana": {"box": [[-165, -53, 41, 69]]},
    "Haliaeetus leucocephalus": {"box": [[-170, -55, 25, 70]]},
    "Castor canadensis": {"box": [[-165, -55, 27, 69]]},
    "Ursus americanus": {"box": [[-165, -55, 20, 68]]},
    "Gavia immer": {"box": [[-170, -10, 40, 76]]},
    "Taxodium distichum": {"box": [[-99, -74, 25, 40]]},
    "Alligator mississippiensis": {"box": [[-99, -75, 25, 37]]},
    "Acer saccharum": {"box": [[-96, -60, 35, 49]]},
    "Zizania palustris": {"box": [[-100, -64, 40, 53]]},
    "Acipenser fulvescens": {"box": [[-108, -70, 33, 58]]},
    "Salvelinus namaycush": {"box": [[-165, -60, 41, 72]]},
    "Oncorhynchus clarkii": {"box": [[-135, -103, 38.5, 60]]},
    "Lepus arcticus": {"box": [[-130, -15, 55, 84]]},
    "Pharomachrus mocinno": {"box": [[-98, -80, 8, 18]]},
    "Solenodon": {"box": [[-85, -68, 17.5, 23.5]]},
    "Tapirus bairdii": {"box": [[-98, -75, 0, 20]]},
    # ------------------------------------------------------------ South America
    "Arapaima gigas": {"box": AMAZONIA, "avoid": HIGH_ANDES},
    "Inia geoffrensis": {"box": AMAZONIA + [[-73, -60, 3, 9]], "avoid": HIGH_ANDES},
    "Pteronura brasiliensis": {"box": AMAZONIA + [[-62, -45, -28, -16]], "avoid": HIGH_ANDES},
    "Victoria amazonica": {"box": AMAZONIA, "avoid": HIGH_ANDES},
    "Melanosuchus niger": {"box": AMAZONIA, "avoid": HIGH_ANDES},
    "Eunectes murinus": {"box": [[-80, -40, -25, 11]], "avoid": HIGH_ANDES},
    "Bertholletia excelsa": {"box": [[-72, -46, -13, 6]]},
    "Mauritia": {"box": NOW([-80, -40, -20, 11], since=2.6), "hab": ["wetland", "rainforest", "river"],
                 "avoid": HIGH_ANDES,
                 "note": "The moriche palm, forming swamp stands across lowland tropical South America; its pollen marks the great Miocene wetland of western Amazonia."},
    "Heliamphora": {"box": TEPUIS},
    "Oreophrynella": {"box": TEPUIS},
    "Espeletia": {"box": [[-79, -69, -1, 11.5]], "hab": ["alpine"]},
    "Puya raimondii": {"box": [[-78.5, -66, -18, -8]], "hab": ["alpine"]},
    "Tremarctos ornatus": {"box": ANDES[:3]},
    "Vultur gryphus": {"box": ANDES},
    "Polylepis": {"box": [[-80, -63, -33, 11]], "hab": ["alpine"]},
    "Vicugna vicugna": {"box": PUNA},
    "Chinchilla": {"box": [[-71.5, -66.5, -33, -14]]},
    "Orestias": {"box": [[-72, -66, -23, -13]]},
    "Telmatobius": {"box": [[-80, -64, -30, 0]]},
    "Rollandia microptera": {"box": [[-70.5, -66, -20, -14.5]]},
    "Lama guanicoe": {"box": [[-76, -62, -55, -8]]},
    "Lycalopex culpaeus": {"box": ANDES + PATAGONIA},
    "Liolaemus": {"box": [[-78, -56, -55, -9]]},
    "Hippocamelus bisulcus": {"box": [[-74, -70, -54, -34]]},
    "Pudu puda": {"box": [[-75, -70.5, -47, -35]]},
    "Fitzroya cupressoides": {"box": [[-74.5, -71, -43.5, -39.5]]},
    "Araucaria araucana": {"box": [[-73.5, -70.2, -40.5, -37]]},
    "Dolichotis patagonum": {"box": [[-71, -62, -50, -28]]},
    "Zaedyus pichiy": {"box": [[-72, -60, -52, -32]]},
    "Mulinum spinosum": {"box": [[-73, -64, -52, -32]]},
    "Rhea pennata": {"box": [[-73, -63, -54, -35], [-71, -65, -28, -14]]},
    "Rhea americana": {"box": [[-66, -35, -40, -5]]},
    "Chrysocyon brachyurus": {"box": [[-64, -42, -32, -7]]},
    "Cortaderia selloana": {"box": [[-65, -48, -42, -25]]},
    "Hydrochoerus hydrochaeris": {"box": [[-80, -40, -38, 11]]},
    "Megatherium": {"hab": ["grassland", "forest", "alpine"]},
    "Doedicurus": {"box": [[-68, -50, -42, -28]]},
    # -------------------------------------------------------------------- Europe
    "Leontopodium nivale": {"box": [PYRENEES, ALPS, CARPATHIANS, [13, 14.5, 41.8, 42.8], [20, 24, 41, 43]],
                            "hab": ["alpine"]},
    "Capra ibex": {"box": [ALPS], "avoid": ["Apennines", "Bohemian Massif", "Massif Central"]},
    "Marmota marmota": {"box": [ALPS, [19.5, 25.5, 45, 49.5], PYRENEES]},
    "Rupicapra rupicapra": {"box": [[5, 27, 41, 50], [36, 48, 40, 44]]},
    "Abies alba": {"box": [PYRENEES, [2, 27, 40, 51], [13, 16.5, 38, 43]]},
    "Larix decidua": {"box": [ALPS, [17, 26, 45.5, 50.5]]},
    "Bison bonasus": {"box": [[14, 40, 46, 56], [38, 48, 41, 45]], "avoid": ["Alps", "Apennines", "Pontide Arc"]},
    "Gulo gulo": {"box": [[5, 180, 58, 75], [-168, -60, 48, 72], [-125, -105, 37, 49]]},
    "Tetrao urogallus": {"box": [[-7, 1, 42, 43.5], [5, 27, 43, 51], [4, 140, 55, 70]]},
    "Calluna vulgaris": {"box": [[-10, 40, 40, 71]], "hab": ["coast", "alpine", "forest"]},
    "Macaca sylvanus": {"box": NOW([-9.5, 9.5, 30.5, 37])},
    # ----------------------------------------------------- north and central Asia
    "Picea obovata": {"box": [[40, 160, 55, 70]]},
    "Pinus sibirica": {"box": [[55, 125, 48.5, 67]]},
    "Larix gmelinii": {"box": [[95, 165, 47, 73]]},
    "Picea schrenkiana": {"box": TIEN_SHAN},
    "Ovis ammon": {"box": [[66, 112, 28, 52]]},
    "Equus kiang": {"box": TIBET},
    "Bos mutus": {"box": [[78, 102, 29, 39]]},
    "Pantholops hodgsonii": {"box": [[78, 98, 30, 38.5]]},
    "Pseudois nayaur": {"box": [[73, 106, 26.5, 40]]},
    "Panthera uncia": {"range": ["as-c", "in", "as-n"], "box": [[66, 105, 26.5, 52]], "hab": ["alpine"]},
    "Gyps himalayensis": {"box": [[68, 105, 26, 44]]},
    "Moschus moschiferus": {"box": [[85, 145, 43, 68]]},
    "Martes zibellina": {"box": [[55, 160, 46, 70]]},
    "Procapra gutturosa": {"box": [[95, 125, 42, 52]]},
    "Camelus ferus": {"box": [[86, 105, 38.5, 45.5]]},
    "Kobresia": {"box": [[66, 106, 26, 52], [-180, 180, 58, 84], [-125, -104, 36, 58], [5, 27, 42, 49]]},
    "Leucogeranus leucogeranus": {"box": [[60, 160, 55, 73]]},
    "Pusa sibirica": {"box": BAIKAL},
    "Coregonus migratorius": {"box": BAIKAL},
    "Comephorus": {"box": BAIKAL},
    "Acanthogammarus": {"box": BAIKAL},
    "Lubomirskia baicalensis": {"box": BAIKAL},
    "Pusa caspica": {"box": [[46.5, 54.5, 36.5, 47.2]]},
    "Huso huso": {"box": [[27, 54.5, 36.5, 48]]},
    "Capra caucasica": {"box": [[40.5, 48.5, 41, 44.5]]},
    "Capra aegagrus": {"box": [[26, 70, 25, 44]]},
    "Haloxylon": {"box": [[44, 112, 28, 48]]},
    "Saiga tatarica": {"box": NOW([42, 110, 42, 52])},
    "Marmota bobak": {"box": [[30, 80, 46, 56]]},
    # ---------------------------------------------------------- east, south Asia
    "Panthera tigris": {"box": NOW([68, 122, -9, 32], [125, 142, 40, 54])},
    "Macaca fuscata": {"box": [[129, 142, 30, 41.6]]},
    "Nipponia nippon": {"box": [[103, 142, 30, 46]]},
    "Ailuropoda": {"box": NOW([102, 109, 28, 34.5])},
    "Rhinopithecus roxellana": {"box": [[102, 112, 28, 35]]},
    "Davidia involucrata": {"box": [[98, 112, 25, 33]]},
    "Metasequoia": {"box": NOW([107, 110.5, 29, 31.5], since=2.6)},
    "Ginkgo": {"box": NOW([104, 122, 26, 32], since=2.6)},
    "Elaphurus davidianus": {"box": [[110, 122, 28, 40]]},
    "Andrias davidianus": {"box": [[100, 120, 22, 36]]},
    "Phyllostachys": {"box": [[97, 123, 18, 38]]},
    "Fagus": {"box": NOW([100, 123, 23, 33.5], [127, 146, 30, 43.5], [-10, 52, 36, 60],
                         [-98, -60, 28, 48], [-101, -96, 18, 24], since=2.6)},
    "Pavo cristatus": {"box": [[68, 90, 6, 32]]},
    "Boselaphus tragocamelus": {"box": [[68, 89, 12, 32]]},
    "Semnopithecus": {"box": [[66, 95, 6, 35]]},
    "Shorea robusta": {"box": [[76, 94, 17, 32]]},
    "Ficus benghalensis": {"box": [[68, 93, 8, 30]]},
    "Rhinoceros unicornis": {"box": [[67, 96, 23, 32]]},
    "Gavialis gangeticus": {"box": [[67, 96, 20, 32]]},
    "Tectona grandis": {"box": [[73, 105, 9, 26]]},
    "Bos gaurus": {"box": [[73, 108, 2, 29]]},
    "Buceros": {"box": [[73, 127, -9, 28]]},
    "Nepenthes": {"box": [[92, 160, -15, 26], [43, 51, -26, -12], [79, 82, 5.5, 10], [55, 56, -5, -4]],
                  "avoid": ["Tethyan Himalaya", "Himalaya"]},
    "Pongo": {"box": NOW([95, 119, -5, 7])},
    "Babyrousa": {"box": [[119, 128, -3.5, 2]]},
    "Varanus komodoensis": {"box": NOW([118.5, 123.5, -9.5, -8], since=0.05)},
    "Tarsius": {"box": [[104, 128, -7, 12]]},
    "Rafflesia": {"box": [[95, 127, -9, 19]]},
    "Tapirus indicus": {"box": NOW([95, 106, -6, 18])},
    "Agathis dammara": {"box": [[115, 132, -10, 20]]},
    "Eucalyptus deglupta": {"box": [[120, 153, -8, 9]]},
    "Crocodylus porosus": {"lat": [0, 25]},
    # -------------------------------------------------------------------- Africa
    "Dendrosenecio": {"box": [[29, 38.5, -4.5, 2]], "hab": ["alpine"]},
    "Lobelia rhynchopetalum": {"box": [[36, 42, 6, 14.5]], "hab": ["alpine"]},
    "Hagenia abyssinica": {"box": [[29, 42, -15, 15]]},
    "Canis simensis": {"box": [[36, 41, 6, 14]]},
    "Theropithecus gelada": {"box": [[37, 40.5, 9, 14]]},
    "Cedrus atlantica": {"box": [[-7, 7, 32, 37]]},
    "Olea laperrinei": {"box": [[3, 10, 18, 27]]},
    "Addax nasomaculatus": {"box": [[-17, 35, 14, 30]]},
    "Termitomyces": {"range": ["af-e", "af-s", "af-w", "mg", "in", "as-se"]},
    "Welwitschia mirabilis": {"box": [[11.5, 16, -24, -14]]},
    "Aloidendron dichotomum": {"box": [[15, 22, -31.5, -21]]},
    "Onymacris unguicularis": {"box": [[11.5, 16, -27, -17]]},
    "Vachellia erioloba": {"box": [[14, 29, -30, -16]]},
    "Oryx gazella": {"box": [[11, 30, -32, -14]]},
    "Antidorcas marsupialis": {"box": [[11, 30, -34, -14]]},
    "Parahyaena brunnea": {"box": [[11, 33, -34, -15]]},
    "Suricata suricatta": {"box": [[14, 30, -34, -17]]},
    "Equus zebra": {"box": [[12, 27, -34.5, -15]]},
    "Protea": {"box": [[17, 33, -35, -22]]},
    "Gorilla gorilla": {"box": [[8, 19, -6, 7]]},
    "Mandrillus sphinx": {"box": [[8.5, 15, -4.5, 4]]},
    "Loxodonta cyclotis": {"box": [[-15, 30, -6, 9]]},
    "Psittacus erithacus": {"box": [[-10, 35, -8, 10]]},
    "Pan troglodytes": {"box": [[-16, 32, -9, 13]]},
    "Okapia johnstoni": {"box": [[24, 31, -3, 4]]},
    "Balaeniceps rex": {"box": [[25, 35, -15, 10]]},
    "Alcolapia": {"box": [[35.5, 36.8, -3, -1.5]]},
    "Lavigeria": {"box": [[29, 31.5, -9, -3]]},
    "Lates niloticus": {"box": [[-17, 40, -3, 32]]},
    # ----------------------------------------------------------------- Australasia
    "Phascolarctos cinereus": {"box": [[138, 154, -39, -15]]},
    "Sarcophilus harrisii": {"box": NOW([144.5, 148.5, -43.7, -40.5])},
    "Vombatus ursinus": {"box": [[140, 154, -44, -27]]},
    "Ornithorhynchus anatinus": {"box": [[138, 154, -44, -15]]},
    "Wollemia nobilis": {"box": NOW([150, 150.8, -33.5, -32.5], since=2.6)},
    "Notoryctes typhlops": {"box": [[118, 140, -31, -18]]},
    "Moloch horridus": {"box": [[113, 142, -33, -18]]},
    "Varanus giganteus": {"box": [[114, 142, -30, -17]]},
    "Osphranter rufus": {"box": [[114, 150, -35, -17]]},
    "Acacia aneura": {"box": [[114, 150, -33, -19]]},
    "Banksia": {"hab": ["forest", "coast"]},
    "Casuarius casuarius": {"box": [[130, 150, -20, 0]]},
    "Dendrolagus": {"box": [[130, 150, -19, 0]]},
    "Zaglossus": {"box": [[130, 148, -9, 0]]},
    "Ornithoptera alexandrae": {"box": [[147.5, 149, -9.5, -8]]},
    # ------------------------------------------------------ the sea, within a basin
    "Latimeria": {"box": [[38, 52, -35, -2], [118, 128, -3, 5]], "hab": ["deep", "reef"]},
    "Tridacna": {"box": IWP}, "giant clams": {"box": IWP}, "Nautilus": {"box": [[90, 180, -30, 20]]},
    "Acropora": {"box": NOW(*IWP, CARIB, since=5)},
    "Porites": {"box": NOW(*IWP, CARIB, [-115, -77, -5, 30], since=5)},
    "Calyptogena": {"hab": ["vent"]}, "Bathymodiolus": {"hab": ["vent"]},
    "Chlorophyta": {"hab": ["coast", "shelf", "reef", "lake", "river", "wetland"]},
    "Rhodophyta": {"hab": ["coast", "shelf", "reef"]},
    "Hexactinellida": {"hab": ["deep", "shelf", "reef"]},
    "kelp": {"lat": [30, 75]},
    "Macrocystis": {"range": ["pac", "sou", "na-w", "sa-s", "af-s", "au", "nz"], "lat": [28, 62],
                    "box": [[-135, -108, 26, 60], [-82, -55, -57, -5], [10, 35, -38, -28],
                            [110, 180, -56, -30], [35, 80, -56, -45], [-45, -25, -56, -50]]},
    "Balaena mysticetus": {"lat": [60, 90]}, "Monodon monoceros": {"lat": [62, 90]},
    "Boreogadus saida": {"lat": [60, 90]},
    # ------------------------------ cosmopolitan fill that is not cosmopolitan enough
    "Arecaceae (palms)": {"lat": [{"t": [95, 34], "lat": [0, 78]}, {"t": [34, 0], "lat": [0, 40]}]},
    "Crocodylia": {"lat": [{"t": [250, 34], "lat": [0, 78]}, {"t": [34, 0], "lat": [0, 36]}]},
    "Isoptera": {"lat": [{"t": [250, 34], "lat": [0, 75]}, {"t": [34, 0], "lat": [0, 46]}]},
    "Azolla": {"lat": [{"t": [250, 34], "lat": [0, 90]}, {"t": [34, 0], "lat": [0, 48]}]},
    "Nymphaeales": {"lat": [{"t": [250, 34], "lat": [0, 85]}, {"t": [34, 0], "lat": [0, 66]}]},
    "Anura": {"lat": [{"t": [250, 34], "lat": [0, 85]}, {"t": [34, 0], "lat": [0, 70]}]},
    "Odonatoptera": {"lat": [{"t": [330, 34], "lat": [0, 85]}, {"t": [34, 0], "lat": [0, 70]}]},
    "Blattodea": {"lat": [{"t": [330, 34], "lat": [0, 85]}, {"t": [34, 0], "lat": [0, 58]}]},
    "Formicidae": {"lat": [{"t": [250, 34], "lat": [0, 85]}, {"t": [34, 0], "lat": [0, 69]}]},
    "Phragmites australis": {"lat": [0, 68]},
    # ----------------------------------------------------------- Antarctica's ice
    "Nothofagus": {"range": [{"t": [83, 0], "in": ["sa-s", "au", "nz", "ng"]}, {"t": [83, 14], "in": ["an"]}],
                   "hab": ["alpine", "forest", "tundra"]},
    "Astrapotheria": {"range": [{"t": [59, 34], "in": ["sa-n", "sa-s", "an"]},
                                {"t": [34, 12], "in": ["sa-n", "sa-s"]}]},
    "Podocarpaceae": {"range+": [{"t": [66, 20], "in": ["an"]}, {"t": [34, 5], "in": ["sou"]}]},
    "Araucariaceae": {"range+": [{"t": [34, 5], "in": ["sou"]}]},
    # ------------------------------------------- second pass, from the placement review
    "Bison": {"box": NOW([-160, -75, 27, 68], [14, 40, 46, 56], [38, 48, 41, 45])},
    "Panthera onca": {"box": NOW([-112, -34, -40, 33])},
    "Lynx lynx": {"box": [[5, 180, 40, 72], [26, 60, 30, 45]]},
    "Quercus": {"box": NOW([-125, -60, 8, 50], [-10, 60, 28, 62], [98, 146, 5, 52], [70, 98, 25, 33],
                           since=2.6), "avoid": ["Kunlun Belt", "Qilian Belt", "Tibetan Plateau"]},
    "Camelidae": {"avoid": ["Tethyan Himalaya", "Himalaya"]},
    "Phrynocephalus": {"hab": ["desert", "grassland"]},
    "Tamarix": {"lat": [12, 50]},
    "Dreissena": {"box": [[27, 62, 36, 50]]},
    "Aphanius": {"box": [[-10, 60, 12, 46]]},
    "Zalophus californianus": {"range": ["pac"]},
    "Armillaria ostoyae": {"hab": ["forest"], "w": 0},
    "Ovis nivicola": {"box": [[88, 180, 52, 72]]},
    "Bacteria": {"realms": ["sea", "fresh", "land"]}, "Archaea": {"realms": ["sea", "fresh", "land"]},
    "Agaricomycetes": {"note": "The mushroom-forming fungi. Molecular clocks put the origin of their lignin-digesting white rot in the late Carboniferous; before it dead wood simply piled up, which is much of the reason most of the world's coal is older."},
    "Osteichthyes": {"note": "Bony fishes, which split early into ray-fins and lobe-fins; one branch of the lobe-fins leads to everything with four limbs."},
    "Carpolestes": {"note": "A small primate relative with a grasping foot and a nail in place of a claw: the beginning of primate hands."},
    "Okapia johnstoni": {"note": "The okapi, the giraffe family's last forest-dwelling member, confined to the Ituri rainforest of the Congo."},
    "Porifera": {"note": "Sponges. Molecular clocks and disputed biomarkers place their origin in the Tonian or Cryogenian; unambiguous body fossils come later."},
    "Rollandia microptera": {"hab": ["lake", "alpine"]},
    "Schoenoplectus californicus": {"hab": ["lake", "wetland", "alpine"]},
    # ------------------ notes that named one place for a taxon found in many
    "Anhinga": {"note": "The darter, a spear-fishing bird of warm fresh waters that swims with only its snake-like neck above the surface."},
    "Bison": {"note": "Bison: steppe grazers that arose in Eurasia and crossed Beringia in the Ice Age; they survive as the American bison and the European wisent."},
    "Enchodus": {"note": "The 'saber-toothed herring', a fanged predatory fish found in Late Cretaceous seas world-wide."},
    "Platypterygius": {"note": "A large, late ichthyosaur found world-wide in Early Cretaceous seas; some Australian specimens are preserved as opal."},
    "Metasequoia": {"note": "The dawn redwood, a conifer that drops its needles: it grew inside the Arctic Circle in the Paleocene warmth, and was thought extinct until living trees were found in central China in the 1940s."},
    "Calyptogena": {"note": "Big white clams clustered in the warm sulphide flow around vents and seeps, fed by chemosynthetic bacteria in their gills."},
    "Rimicaris": {"note": "Swarming eyeless vent shrimp that crowd Atlantic and Indian Ocean chimneys, farming bacteria on their shells."},
    "Posidonia": {"note": "A thin-shelled bivalve that paves the black, oxygen-poor shales of Jurassic Europe -- the 'Posidonia Shale' -- by the million."},
    "Diomedea exulans": {"box": [[-180, 180, -70, -25]]},
    "Trichodesmium erythraeum": {"note": "'Sea sawdust', a nitrogen-fixing cyanobacterium whose rust-coloured blooms streak warm, nutrient-poor seas."},
    "Tardigrada": {"note": "Water bears, microscopic animals that survive freezing and drying alike; in Antarctica they are among the few permanent land animals."},
    # -------------------------------------------------------------- ocean islands
    "Pandanus": {"range+": ["ind"]},
    "Saxifraga oppositifolia": {"range+": ["arc"]},
    "Birgus latro": {"lat": [0, 26]},
}


def main():
    files = {}
    where = {}
    for fn in sorted(glob.glob(os.path.join(REG, "*.json"))):
        with open(fn) as f:
            files[fn] = json.load(f)
        for n in files[fn]["taxa"]:
            where[n] = fn
    missing, touched = [], set()
    for name, fields in PATCH.items():
        fn = where.get(name)
        if not fn:
            missing.append(name)
            continue
        e = files[fn]["taxa"][name]
        for k, v in fields.items():
            if k.endswith("+"):
                base = list(e.get(k[:-1], []))
                for item in v:
                    if item not in base:
                        base.append(item)
                e[k[:-1]] = base
            else:
                e[k] = v
        touched.add(fn)
    for fn in touched:
        with open(fn, "w") as f:
            json.dump(files[fn], f, indent=1, ensure_ascii=False)
    print(f"{len(PATCH) - len(missing)} entries refined in {len(touched)} files")
    if missing:
        print("NOT IN THE REGISTRY:", ", ".join(missing))


if __name__ == "__main__":
    main()
