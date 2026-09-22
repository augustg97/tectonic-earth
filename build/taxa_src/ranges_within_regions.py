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

#: Mongolia shares the as-ne code with North China but was Angaran ground in
#: the Permian: the Cathaysian flora stops at the Solonker suture.
_NOT_CATHAYSIA = ["Amuria", "Central Asian Orogenic Belt", "Mongol-Okhotsk Ocean"]
#: Baltica's own labels, for the Avalonian trilobites that share its code.
_NOT_BALTICA = ["Baltica", "Fennoscandian Shield", "Tornquist Sea", "Oslo Rift"]
#: The Avalon Peninsula: the Carolina slate belt shares na-av and had no deep-water fronds.
_AVALON = [[-56, -52.5, 46.3, 48.5]]

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
    "Crocodylia": {"lat": [{"t": [250, 34], "lat": [0, 84]}, {"t": [34, 0], "lat": [0, 36]}]},
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
    # ======================= the deep-time placement review, 2026-09-22 ==========
    # Read from `audit_biota.py --placements` at 3, 20 and 50 Ma. Each entry is
    # one thing a rule could not see: an endemic leaking across a code, a
    # lineage shown before it reached a continent, a lowland form on the ice.
    # --- 3 Ma
    "Australopithecus": {"box": [[28, 42, -5, 15], [22, 32, -30, -22], [14, 20, 13, 18]]},
    "Macaca sylvanus": {"box": [{"t": [5, 0.02], "box": [[-10, 30, 30, 53]]},
                                {"t": [0.02, 0], "box": [[-9.5, 9.5, 30.5, 37]]}]},
    "Metasequoia": {"range": [{"t": [100, 20], "in": ["na-w", "na-n", "na-e", "gl", "eu", "as-n", "as-e"]},
                              {"t": [20, 2.6], "in": ["na-w", "na-e", "eu", "as-e", "as-n"]},
                              {"t": [2.6, 0], "in": ["as-e"]}],
                    "lat": [{"t": [100, 20], "lat": [0, 90]}, {"t": [20, 0], "lat": [0, 66]}]},
    "Quercus": {"range": [{"t": [56, 0], "in": ["na-w", "na-e", "ca", "eu", "as-w", "as-c", "as-e", "as-se"]},
                          {"t": [56, 5], "in": ["gl", "na-n", "as-n"]},
                          {"t": [23, 0], "in": ["af-n", "in"]}],
                "lat": [{"t": [56, 34], "lat": [0, 80]}, {"t": [34, 5], "lat": [0, 66]}, {"t": [5, 0], "lat": [0, 62]}],
                "box": [{"t": [23, 0], "box": [[-125, -60, 8, 50], [-12, 60, 28, 62], [98, 146, 5, 52], [70, 98, 25, 33]]}]},
    "Anthracotheriidae": {"lat": [0, 55]},
    "Titanis walleri": {"box": [[-100, -78, 24, 34]]},
    "Megalonychidae": {"lat": [0, 64]},
    "Odocoileus": {"lat": [8, 62]},
    "Ginkgo": {"range": [{"t": [170, 66], "in": ["cosmo"]}, {"t": [66, 15], "in": ["holarctic"]},
                         {"t": [15, 2.6], "in": ["eu", "as-e"]}, {"t": [2.6, 0], "in": ["as-e"]}],
               "lat": [{"t": [170, 34], "lat": [0, 90]}, {"t": [34, 0], "lat": [0, 66]}]},
    "Kobresia": {"hab": ["alpine", "tundra"]},
    "Phorusrhacids": {"box": [[-75, -38, -55, -10], [-100, -78, 24, 34]], "hab": ["grassland", "forest", "wetland"],
                      "avoid": HIGH_ANDES},
    "Thylacosmilus": {"box": [[-70, -50, -40, -20]]},
    "Josephoartigasia": {"box": [[-60, -52, -36, -30]]},
    "Megatherium": {"hab": ["grassland", "forest"], "box": [[-80, -40, -56, -8]], "avoid": HIGH_ANDES},
    "Nothofagus": {"box": [{"t": [23, 0], "box": [[-76, -60, -56, -30], [135, 155, -44, -15], [164, 180, -48, -34],
                                                  [130, 152, -10, 0], [-180, 180, -90, -60]]}]},
    "Araucaria": {"box": [{"t": [23, 0], "box": [[-76, -45, -45, -18], [140, 155, -40, -10], [130, 152, -10, 0],
                                                 [164, 180, -48, -34], [-180, 180, -90, -60]]}]},
    "C4 grasses": {"lat": [0, 38]},
    "Prosopis": {"box": [[-118, -95, 20, 38], [-75, -50, -45, -5]]},
    "Agave": {"box": [[-118, -95, 14, 37]]},
    "Boswellia sacra": {"box": [[42, 60, 10, 20]]},
    "Congeria": {"box": [[10, 60, 36, 50]]},
    "Melanopsis": {"box": [[-10, 60, 25, 52], [164, 180, -48, -34]]},
    "Sargassum natans": {"box": [[-100, -10, 5, 42]]},
    "Larix": {"lat": [{"t": [50, 23], "lat": [55, 85]}, {"t": [23, 5], "lat": [30, 80]}, {"t": [5, 0], "lat": [43, 75]}]},
    "Stipa": {"lat": [20, 58]},
    "Equidae": {"lat": [{"t": [56, 2.6], "lat": [0, 62]}, {"t": [2.6, 0], "lat": [0, 80]}]},
    "Bovidae": {"lat": [{"t": [20, 5], "lat": [0, 55]}, {"t": [5, 0], "lat": [0, 75]}]},
    # --- 20 Ma
    "Teratornithidae": {"range": [{"t": [25, 0.011], "in": ["sa-s", "sa-n"]}, {"t": [12, 0.011], "in": ["na-w", "na-e"]}]},
    "Hyaenodon": {"range": [{"t": [42.9, 23], "in": ["as-e", "as-w", "eu", "na-w"]}, {"t": [23, 18.21], "in": ["as-e", "as-c"]}]},
    "Acacia": {"range": ["au", "ng"]},
    "Notosuchia": {"range": [{"t": [130, 66], "in": ["sa-n", "sa-s", "af-n", "af-e", "mg", "in", "eu"]},
                             {"t": [66, 40], "in": ["sa-n", "sa-s", "eu", "af-n"]},
                             {"t": [40, 11], "in": ["sa-n", "sa-s"]}]},
    "Gryposuchus": {"fad": 16, "box": AMAZONIA + [[-73, -60, 3, 11]], "avoid": HIGH_ANDES},
    "Bromeliaceae": {"box": [[-125, -34, -40, 38]]},
    "Heliamphora": {"avoid": ["Andes"]}, "Oreophrynella": {"avoid": ["Andes"]},
    "Obdurodon": {"box": [[137, 155, -30, -15]]},
    "Rhizophora": {"hab": ["coast"]},
    # --- 50 Ma
    "Rhododendron": {"range": [{"t": [55, 0], "in": ["as-e", "as-c", "eu", "as-w", "na-w", "na-e", "as-n"]},
                               {"t": [15, 0], "in": ["in", "as-se", "ng"]}]},
    "Gondwanatheria": {"range": [{"t": [84, 66], "in": ["sa-s", "mg", "in", "af-e"]}, {"t": [84, 40], "in": ["an", "sa-s"]}]},
    "Rhinocerotidae": {"fad": 46},
    "Cetacea": {"range": [{"t": [53, 45], "in": ["tet", "in", "ar", "af-n", "as-w"]}, {"t": [45, 0], "in": ["cosmo"]}]},
    # --- 100 Ma
    # the PBDB's four "as-w" collections are Sinai and the Egyptian side of the
    # Gulf of Suez, which the region boxes assign to Arabia; the animal is North
    # African, and the Anatolide-Tauride Block should not have had it
    "Spinosaurus aegyptiacus": {"range": ["af-n"], "place_ok": True},
    "Cynodontia": {"range": [{"t": [260, 252], "in": ["af-s", "af-e", "eu", "as-n", "sa-s"]},
                             {"t": [252, 201], "in": ["af-s", "af-e", "an", "in", "as-e", "as-c", "as-n", "eu", "sa-s", "mg", "au", "na-e", "na-w"]},
                             {"t": [201, 100], "in": ["as-e", "as-c", "as-n", "na-w", "eu", "af-s"]}]},
    "Tritylodontidae": {"range": [{"t": [210, 180], "in": ["af-s", "as-c", "as-e", "as-n", "eu", "na-w", "an", "sa-s"]},
                                  {"t": [180, 110], "in": ["as-c", "as-e", "as-n", "na-w", "eu"]}]},
    "Steropodon": {"box": [[137, 155, -35, -18]]}, "Kunbarrasaurus": {"box": [[137, 155, -35, -18]]},
    "Muttaburrasaurus": {"box": [[137, 155, -35, -18]]},
    "Giganotosaurus": {"box": [[-72, -62, -45, -35]]}, "Patagotitan": {"box": [[-72, -62, -45, -35]]},
    "Isoptera": {"lat": [{"t": [130, 34], "lat": [0, 66]}, {"t": [34, 0], "lat": [0, 46]}]},
    # --- 150 Ma
    "Archaeopteryx": {"box": [[8, 14, 47, 51]]}, "Compsognathus": {"box": [[5, 14, 43, 51]]},
    "Allosaurus": {"box": [[-115, -98, 30, 48], [-10, -6, 38, 42]]},
    "Stegosaurus": {"box": [[-115, -98, 30, 48], [-10, -6, 38, 42]]},
    "Mamenchisaurus": {"avoid": ["Lhasa Terrane"]},
    "Temnospondyli": {"range": [{"t": [330, 201], "in": ["cosmo"]}, {"t": [201, 120], "in": ["au", "as-e", "as-c", "as-n", "an"]},
                                {"t": [201, 190], "in": ["sa-s", "af-s", "in", "eu", "na-w"]}]},
    "Megalosauridae": {"range+": ["as-c"]},
    "Nodosauridae": {"range": [{"t": [155, 66], "in": ["na-w", "na-e", "eu"]}, {"t": [120, 66], "in": ["au", "an", "sa-s"]}]},
    # --- 250 Ma
    "Lystrosaurus": {"range": ["af-s", "in", "an", "as-c", "as-e", "as-n", "eu"], "box": [[35, 60, 50, 62], [-180, 180, -90, 20]]},
    "Dicynodontia": {"range": [{"t": [270, 252], "in": ["cosmo"]},
                               {"t": [252, 201], "in": ["af-s", "af-e", "an", "in", "as-e", "as-c", "as-n", "eu", "sa-s", "au", "na-w", "as-se"]}]},
    "Megalodontidae": {"fad": 237, "range": ["tet", "eu", "as-c", "as-se", "na-w", "pan"]},
    # --- 300 Ma
    "Lepidodendron": {"range": [{"t": [345, 295], "in": ["euramerica", "as-c", "af-n"]}, {"t": [345, 252], "in": ["as-e"]}]},
    "Cordaites": {"range": ["euramerica", "as-c", "as-e", "as-n"]},
    "Calamites": {"range": ["euramerica", "as-e", "as-c", "af-n"]},
    "Callipteris (Autunia)": {"range": ["euramerica", "af-n"]},
    "Rufloria": {"range": ["as-n", "as-c", "eu"]},
    "Walchia": {"range": ["euramerica", "af-n"]},
    "Psaronius": {"range": ["euramerica", "as-e"]},
    "Embolomeri": {"range": ["euramerica"]},
    "Medullosales": {"range": ["euramerica", "as-e", "as-c", "af-n"]},
    "Diplocaulus": {"range": [{"t": [300, 270], "in": ["na-w", "na-e"]}, {"t": [268, 255], "in": ["af-n"]}]},
    "Captorhinidae": {"range": [{"t": [300, 290], "in": ["na-w", "na-e"]},
                                {"t": [290, 252], "in": ["na-w", "na-e", "eu", "af-n", "af-s", "af-e", "as-e", "in", "sa-s"]}]},
    "Voltziales": {"range": [{"t": [300, 200], "in": ["euramerica", "as-e", "as-c"]}, {"t": [285, 200], "in": ["af-s", "mg", "sa-s", "in", "au", "an"]}]},
    "lichens": {"hab": ["tundra", "ice", "alpine", "desert", "forest", "coast", "island"]},
    "Botrychiopsis": {"hab": ["tundra", "wetland", "forest"], "fad": 320},
    "Gangamopteris": {"hab": ["tundra", "wetland", "forest"]},
    "Marchantiophyta": {"hab": ["wetland", "forest", "rainforest", "tundra", "alpine", "coast", "island"]},
    "Eurydesma": {"hab": ["shelf", "coast", "ice"]},
    "Small shelly fauna": {"range": ["cosmo"]},
    "Tillites": {"fad": 717, "range": [{"t": [717, 660], "in": ["cosmo"]}, {"t": [650, 635], "in": ["cosmo"]},
                           {"t": [582, 579], "in": ["cosmo"]}, {"t": [445, 443], "in": ["gondwana"]},
                           {"t": [335, 260], "in": ["gondwana"]},
                           {"t": [2.6, 0], "in": ["na-n", "na-e", "na-w", "eu", "as-n", "gl", "an", "sa-s", "nz"]}]},
    # --- 400 Ma
    "Amphipora": {"fad": 393},
    "Tardigrada": {"fad": 360},
    # ======================= placement review, second pass (2026-09-22) ==========
    # 10, 35, 80, 120, 200, 230, 280, 350, 450, 500 and 600 Ma.
    # --- 10 Ma
    # its fossils lie on the coasts of every continent, as a seabird's do; the
    # range is the water it flew over, so a continent's interior never shows it
    "Pelagornithidae": {"range": ["pac", "atl", "ind", "sou", "arc", "tet", "med", "pan"], "place_ok": True},
    # the PBDB's African "Sivapithecus" are old referrals of Kenyapithecus and its kin
    "Sivapithecus": {"range": ["in", "as-w"], "box": [[65, 80, 28, 35], [28, 42, 36, 42]], "place_ok": True},
    "Mourasuchus": {"box": AMAZONIA + [[-73, -60, 3, 11]], "avoid": HIGH_ANDES},
    "Stupendemys": {"box": AMAZONIA + [[-73, -60, 3, 11]], "avoid": HIGH_ANDES},
    "Purussaurus": {"box": [[-82, -45, -15, 12]], "avoid": HIGH_ANDES},
    "Adansonia": {"box": [[-18, 52, -30, 20], [42, 51, -26, -12], [122, 132, -19, -13]]},
    "Eucalyptus": {"range": [{"t": [52, 40], "in": ["sa-s"]}, {"t": [45, 0], "in": ["au"]}, {"t": [3, 0], "in": ["ng", "as-se"]}]},
    "Hominidae": {"box": [{"t": [23, 7], "box": [[28, 42, -5, 15], [-10, 30, 35, 50], [65, 80, 28, 35], [98, 125, 20, 35]]}]},
    "Sequoiadendron": {"range": ["na-w"],
                       "box": [{"t": [40, 2.6], "box": [[-125, -105, 35, 48]]}, {"t": [2.6, 0], "box": SIERRA}],
                       "avoid": ["Basin and Range", "Rocky Mountains", "Colorado Plateau", "Rio Grande Rift", "Gulf of California", "Williston Basin"]},
    # --- 35 Ma
    "Amphicyonidae": {"range": [{"t": [45, 8], "in": ["na-w", "na-e", "eu", "as-e", "as-c"]}, {"t": [23, 8], "in": ["af-e", "af-n", "in"]}]},
    "Rhinocerotidae": {"lat": [{"t": [46, 23], "lat": [0, 58]}, {"t": [23, 0], "lat": [0, 75]}]},
    "Moeritherium": {"range": ["af-n"]},
    # --- 80 Ma
    "Hadrosauridae": {"range": [{"t": [86, 66], "in": ["na-w", "na-e", "na-n", "as-e", "as-c", "as-n"]},
                                {"t": [72, 66], "in": ["eu", "sa-s", "sa-n", "an", "af-n"]}]},
    "Abelisauridae": {"range": [{"t": [145, 66], "in": ["sa-n", "sa-s", "af-n", "af-e", "mg", "in"]}, {"t": [75, 66], "in": ["eu"]}]},
    "Ceratopsidae": {"range": [{"t": [83, 66], "in": ["na-w", "na-n", "na-e"]}, {"t": [74, 72], "in": ["as-e"]}]},
    "Hesperornis": {"range": ["na-w", "na-e", "na-n", "eu", "arc", "as-n"], "lat": [30, 80]},
    "Belemnitella": {"lat": [30, 72]},
    "Ornithomimosauria": {"range": [{"t": [140, 66], "in": ["as-e", "as-c", "na-w", "eu"]}, {"t": [140, 125], "in": ["af-s"]}]},
    "Gasparinisaura": {"box": [[-72, -62, -45, -35]]},
    "Elasmosaurus": {"range": ["na-w", "na-e"]}, "Protostega": {"range": ["na-w", "na-e"]},
    "Toxochelys": {"range": ["na-w", "na-e"]}, "Platecarpus": {"range": ["na-w", "na-e", "eu", "af-n", "atl"]},
    "Uintacrinus": {"range": ["na-w", "na-e", "eu"]}, "Bananogmius": {"range": ["na-w", "na-e"]},
    "Nyctosaurus": {"range": ["na-w", "na-e"]}, "Ichthyornis": {"range": ["na-w", "na-e"]},
    # --- 120 Ma
    "Tritylodontidae": {"lad": 100, "range": [{"t": [210, 180], "in": ["af-s", "as-c", "as-e", "eu", "na-w", "an", "sa-s"]},
                                  {"t": [180, 130], "in": ["as-c", "as-e", "na-w", "eu"]},
                                  {"t": [130, 100], "in": ["as-e", "as-n"]}]},
    "Cynodontia": {"range": [{"t": [260, 252], "in": ["af-s", "af-e", "eu", "as-n", "sa-s"]},
                             {"t": [252, 201], "in": ["af-s", "af-e", "an", "in", "as-e", "as-c", "as-n", "eu", "sa-s", "mg", "au", "na-e", "na-w"]},
                             {"t": [201, 180], "in": ["af-s", "an", "sa-s"]},
                             {"t": [201, 130], "in": ["as-e", "as-c", "na-w", "eu"]},
                             {"t": [130, 100], "in": ["as-e", "as-n"]}]},
    "Koolasuchus": {"box": [[140, 150, -40, -35]]},
    # --- 200 and 230 Ma
    "Scelidosaurus": {"box": [[-6, 2, 49, 52]], "avoid": ["Caledonides", "Ural Mountains", "Bohemian Massif", "Massif Central",
                                                        "Iberian Massif", "Rhodope Massif", "Fennoscandian Shield", "Greater Adria"]},
    # --- 280 Ma: Angara stays in Angara, Cathaysia in Cathaysia. The Cathaysian
    # taxa are ranged on the blocks the flora grew on (North China, South China,
    # Indochina); Gondwanan Sibumasu is a different code now, so no avoid lists.
    "Angaropteridium": {"box": [[45, 120, 45, 75]]}, "Rufloria": {"box": [[45, 130, 40, 75]]},
    "Vojnovskya": {"box": [[45, 130, 40, 75]]},
    "Lobatannularia": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    "Emplectopteris": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    "Tingia": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    "Gigantopteris": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    "Cathaysian flora": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    "Cathaysiodendron": {"range": ["as-ne", "as-s", "as-ic"], "avoid": _NOT_CATHAYSIA},
    # --- 450 Ma: the warm Laurentian shelf does not reach the cold Gondwanan margin
    "Astraspis": {"lat": [0, 45]}, "Constellaria": {"lat": [0, 45]}, "Isorophus": {"lat": [0, 45]},
    "Flexicalymene": {"lat": [0, 45]}, "Rafinesquina": {"lat": [0, 50]}, "Platystrophia": {"lat": [0, 45]},
    "Streptelasma": {"lat": [0, 45]}, "Isotelus": {"lat": [0, 45]}, "Elrathia": {"lat": [0, 45]},
    "Marrella": {"lat": [0, 45]}, "Opabinia": {"lat": [0, 45]}, "Pikaia": {"lat": [0, 45]}, "Ottoia": {"lat": [0, 45]},
    # --- the two Chinas, by block, now that the codes can say which
    "Lantian biota": {"range": ["as-s"]}, "Doushantuo biota": {"range": ["as-s"]},
    "Chengjiang Biota": {"range": ["as-s"]}, "Myllokunmingia": {"range": ["as-s"]},
    "Haikouichthys": {"range": ["as-s"]}, "Eoredlichia": {"range": ["as-s", "au"]},
    "Luoping biota": {"range": ["as-s"]}, "Keichousaurus": {"range": ["as-s"]},
    "Meishan fauna": {"range": ["as-s"]}, "Guangdedendron": {"range": ["as-s"]},
    "Liulaobei biota": {"range": ["as-ne"]}, "Longfengshania": {"range": ["as-ne"]},
    "Shihtienfenia": {"range": ["as-ne"]}, "Bolosaurus": {"range": ["na-w", "as-ne"]},
    "Lufengosaurus": {"range": ["as-s"]},
    "Mamenchisaurus": {"range": ["as-s", "as-c"], "avoid": ["Lhasa Terrane"]},
    "Confuciusornis": {"range": ["as-ne"]}, "Repenomamus": {"range": ["as-ne"]},
    "Sinosauropteryx": {"range": ["as-ne"]}, "Microraptor": {"range": ["as-ne"]},
    "Jehol Biota": {"range": ["as-ne"]},
    "Toxaster": {"lat": [0, 55]},
    # Sibumasu was Gondwanan crust: the Glossopteris flora and its cold-water sea reach it
    "Glossopteris": {"range+": ["as-sb"]}, "Gangamopteris": {"range+": ["as-sb"]},
    "Noeggerathiopsis": {"range+": ["as-sb"]}, "Vertebraria": {"range+": ["as-sb"]},
    "Glossopteris flora": {"range+": ["as-sb"]}, "Botrychiopsis": {"range+": ["as-sb"]},
    "Paracalamites": {"range+": ["as-sb"]}, "Eurydesma": {"range+": ["as-sb"]},
    # Wallacea's endemics stay east of Wallace's Line
    "Babyrousa": {"range": ["as-ic"], "avoid": ["Sundaland"]},
    "Bubalus depressicornis": {"range": ["as-ic"], "avoid": ["Sundaland"]},
    "Ailurops ursinus": {"range": ["as-ic"], "avoid": ["Sundaland"]},
    "Macrocephalon maleo": {"range": ["as-ic"], "avoid": ["Sundaland"]},
    # -------------------------------------------------------------- ocean islands
    "Pandanus": {"range+": ["ind"]},
    "Saxifraga oppositifolia": {"range+": ["arc"]},
    "Birgus latro": {"lat": [0, 26]},
    # ------------------------------------------------ the ages between the samples
    # The placement listing had been read at twenty ages, every 25-50 Myr. Read
    # at the fourteen between them (5, 15, 40, 60, 90, 110, 170, 190, 215, 265,
    # 320, 375, 420, 480 Ma), which is where a genus with a short span and a
    # single home shows up on the wrong crust.
    # --- 5 Ma: the Pliocene Arctic was forest, not a home for hipparions
    "Hipparion": {"lat": [0, 55]}, "Chalicotheriidae": {"lat": [0, 55]},
    "Chalicotherium": {"lat": [0, 55]}, "Mammut": {"lat": [5, 62]},
    "Anthracotheriidae": {"range": [
        {"t": [45, 15], "in": ["eu", "as-ne", "as-s", "as-ic", "in", "af-n", "af-e", "na-w"]},
        {"t": [15, 2], "in": ["in", "as-ic", "as-s", "af-n", "af-e"]}]},
    # the swimming sloth of the Pisco coast. An ocean card has no footprint, so
    # a box cannot keep a coastal species off the basins its LAND codes touch:
    # a shore animal of one coast gets that ocean's code and nothing else.
    "Thalassocnus": {"range": ["pac"], "box": [[-82, -69, -18, -4]], "hab": ["coast", "shelf"],
                     "place_ok": True, "conf_note": "PBDB collections are the Pisco coast of Peru; the range is that coast's ocean, by design"},
    # the Lago Mare ostracod lives in brackish water, so it can reach a lake card
    "Cyprideis": {"realms": ["sea", "fresh"], "hab": ["coast", "lake"]},
    # --- 40-60 Ma: families with one continent at a time
    "Brontotheriidae": {"box": [[-170, -55, 25, 75], [65, 150, 20, 52], [20, 30, 40, 45]]},
    "Entelodontidae": {"range": [
        {"t": [46, 38], "in": ["as-ne", "as-s", "as-c"]},
        {"t": [38, 16], "in": ["as-ne", "as-s", "as-c", "na-w", "na-e"]},
        {"t": [38, 23], "in": ["eu"]}]},
    "Andrewsarchus": {"box": [[100, 125, 38, 48]]},
    "Embolotherium": {"box": [[88, 120, 38, 52]]},
    "Phenacodus": {"range": [{"t": [60, 48], "in": ["na-w"]}, {"t": [56, 48], "in": ["eu"]}]},
    "Gastornis": {"range": [{"t": [60.5, 48], "in": ["eu"]},
                            {"t": [56, 48], "in": ["na-w", "na-e", "na-n", "as-ne"]}]},
    "Notosuchia": {"lat": [0, 52]},
    "Cheirolepidiaceae": {"range": [{"t": [230, 66], "in": ["cosmo"]},
                                    {"t": [66, 60], "in": ["sa-s", "au", "nz", "an"]}]},
    # --- 90-110 Ma
    "Carcharodontosauridae": {"range": [
        {"t": [130, 120], "in": ["eu"]}, {"t": [116, 98], "in": ["na-w"]},
        {"t": [130, 90], "in": ["sa-s", "sa-n"]}, {"t": [130, 90], "in": ["af-n", "af-e"]},
        {"t": [125, 90], "in": ["as-c", "as-ne"]}]},
    "Brachiosauridae": {"range": [{"t": [160, 125], "in": ["eu"]}, {"t": [160, 100], "in": ["na-w"]},
                                  {"t": [160, 110], "in": ["af-e", "af-n"]}]},
    "Spinosauridae": {"box": [[-10, 25, 36, 53], [-20, 55, -35, 37], [-82, -34, -56, 13],
                              [95, 125, 10, 45], [140, 150, -40, -35]], "avoid": ["Caledonides"]},
    "Psittacosaurus": {"range": ["as-ne", "as-s", "as-c", "as-n", "as-ic"],
                       "box": [[75, 135, 25, 58], [98, 106, 12, 20]]},
    "Tritylodontidae": {"box": [{"t": [130, 100], "box": [[75, 140, 30, 58]]}]},
    "Nigersaurus": {"box": [[-5, 20, 10, 25]]},
    "Anhanguera": {"range": ["sa-n", "eu"], "box": [[-45, -34, -12, -3], [-2, 2, 50, 54]], "avoid": ["Caledonides"]},
    "Tapejara": {"box": [[-45, -34, -12, -3]]},
    "Leaellynasaura": {"box": [[140, 150, -40, -36]]},
    "Kronosaurus": {"box": [[138, 152, -30, -18], [-78, -70, 3, 8]]},
    # --- 170-215 Ma: the Triassic and Jurassic genera of one formation
    "Coelophysoidea": {"range": [{"t": [228, 190], "in": ["na-w", "na-e", "eu", "af-s"]},
                                 {"t": [201, 190], "in": ["as-s"]}]},
    "Massospondylidae": {"range": ["af-s", "sa-s", "an", "na-w", "in", "as-s"]},
    "Dicynodontia": {"range": [
        {"t": [270, 252], "in": ["af-s", "af-e", "eu", "as-c", "as-ne", "sa-s", "in"]},
        {"t": [252, 227], "in": ["af-s", "af-e", "an", "in", "as-ne", "as-s", "as-c", "as-n", "eu", "sa-s", "au", "na-w", "as-ic", "as-sb"]},
        {"t": [227, 201], "in": ["na-w", "na-e", "sa-s", "af-s", "eu", "in"]}]},
    "Cynodontia": {"range": [
        {"t": [260, 252], "in": ["af-s", "af-e", "eu", "as-n", "sa-s"]},
        {"t": [252, 201], "in": ["af-s", "af-e", "in", "as-ne", "as-s", "as-c", "as-n", "eu", "sa-s", "mg", "na-e", "na-w"]},
        {"t": [252, 235], "in": ["an"]},
        {"t": [201, 180], "in": ["af-s", "an", "sa-s"]},
        {"t": [201, 130], "in": ["as-ne", "as-s", "as-c", "na-w", "eu"]},
        {"t": [130, 100], "in": ["as-ne", "as-n"]}],
                   "box": [{"t": [130, 100], "box": [[75, 140, 30, 58]]}]},
    "Rauisuchia": {"range": ["na-w", "na-e", "sa-s", "sa-n", "eu", "af-s", "af-e", "af-n", "in",
                             "as-ne", "as-s"]},
    "Podocarpaceae": {"lat": [{"t": [240, 66], "lat": [0, 62]}]},
    "Lithiotis": {"lat": [0, 40]},
    "Plateosaurus": {"box": [[-10, 25, 42, 62], [-30, -18, 68, 73]]},
    "Eudimorphodon": {"box": [[5, 20, 42, 50], [-30, -18, 68, 73]]},
    "Metoposaurus": {"box": [[-10, 25, 36, 55]]},
    "Placerias": {"range": ["na-w"], "box": [[-115, -100, 30, 40]]},
    "Coelophysis": {"range": ["na-w"], "box": [[-115, -100, 30, 40]]},
    "Coelophysis bauri": {"range": ["na-w"], "box": [[-115, -100, 30, 40]]},
    "Desmatosuchus": {"box": [[-115, -96, 30, 40]]}, "Postosuchus": {"box": [[-115, -96, 30, 40]]},
    "Araucarioxylon": {"box": [[-115, -100, 30, 40]]}, "Dilophosaurus": {"box": [[-115, -105, 32, 40]]},
    # --- 265-320 Ma: the Permian of one basin each
    "Gorgonopsia": {"box": [[42, 62, 50, 62], [10, 42, -36, -4], [100, 120, 30, 45]]},
    "Estemmenosuchus": {"box": [[50, 62, 54, 60]]},
    "Sinophoneus": {"range": ["as-ne"], "box": [[95, 105, 35, 42]], "avoid": ["Cathaysian Coal Forests"]},
    "Diictodon": {"range": ["af-s", "as-c", "as-ne"]},
    "Dinocephalia": {"range": ["af-s", "eu", "as-ne", "sa-s"]},
    "Therocephalia": {"range": [{"t": [265, 240], "in": ["af-s", "eu", "as-ne", "as-c"]},
                                {"t": [252, 240], "in": ["an"]}]},
    "Diplocaulus": {"box": [[-100, -94, 32, 37], [-12, 0, 29, 35]]},
    "Temnospondyli": {"range": [{"t": [330, 300], "in": ["na-w", "na-e", "na-n", "eu"]},
                                {"t": [300, 201], "in": ["cosmo"]},
                                {"t": [201, 120], "in": ["au", "as-ne", "as-s", "as-c", "as-n", "an"]},
                                {"t": [201, 190], "in": ["sa-s", "af-s", "in", "eu", "na-w"]}]},
    "Xenacanthus": {"range": [{"t": [360, 300], "in": ["euramerica"]},
                              {"t": [300, 252], "in": ["euramerica", "as-ne", "as-s", "in", "au", "sa-s"]}]},
    # --- 420-480 Ma: the first land floras were one place each
    "Treptichnus pedum": {"lad": 515},
    # --- Australia is two codes now (au-w / au-e). The genera of one formation
    # go to their half; the Broome tracks are the west's only Mesozoic dinosaurs.
    "Arkarua": {"range": ["au-e"]}, "Spriggina": {"range": ["au-e"]},
    "Dickinsonia": {"range": ["au-e", "eu"]}, "Kimberella": {"range": ["ar", "au-e", "eu"]},
    "Tribrachidium": {"range": ["au-e", "eu"]}, "Yorgia": {"range": ["au-e", "eu"]},
    "Parvancorina": {"range": ["as-n", "au-e", "eu"]},
    "Pteridinium": {"range": ["af-s", "au-e", "eu", "na-e"]}, "Rangea": {"range": ["af-s", "au-e", "eu"]},
    "Charnia": {"range": ["as-n", "au-e", "eu", "na-e"]},
    "Charniodiscus": {"range": ["au-e", "eu", "iap", "na-e"]},
    "Anomalocaris": {"range": ["as-s", "au-e", "na-e", "na-w"]}, "Eoredlichia": {"range": ["as-s", "au-e"]},
    "Redlichia": {"range": ["an", "as-c", "as-ne", "as-s", "au-e", "in"]},
    "Sacabambaspis": {"range": ["au-e", "sa-n", "sa-s"]},
    "Metaxygnathus": {"range": ["au-e"]}, "Bitter Springs microbiota": {"range": ["au-e"]},
    "Gogonasus": {"range": ["au-w"]}, "Canning Basin reef fauna": {"range": ["au-w"]},
    "Rhoetosaurus": {"range": ["au-e"]}, "Australovenator": {"range": ["au-e"]},
    "Diamantinasaurus": {"range": ["au-e"]}, "Kunbarrasaurus": {"range": ["au-e"]},
    "Steropodon": {"range": ["au-e"]}, "Muttaburrasaurus": {"range": ["au-e"]},
    "Leaellynasaura": {"range": ["au-e"]}, "Koolasuchus": {"range": ["au-e"]},
    "Umoonasaurus": {"range": ["au-e"]}, "Kronosaurus": {"range": ["au-e", "sa-n"]},
    "Ptyktoptychion": {"range": ["au-e", "pan"]},
    "Nimbadon": {"range": ["au-e"]}, "Obdurodon": {"range": ["au-e"]},
    "Ornithocheiridae": {"range": ["af-n", "as-c", "as-ne", "as-s", "as-n", "au-e", "eu", "na-e", "sa-n"]},
    "Allosauroidea": {"range": ["na-w", "eu", "af-n", "af-e", "sa-s", "as-ne", "as-s", "au-e"]},
    "Nodosauridae": {"range": [{"t": [155, 66], "in": ["na-w", "na-e", "eu"]},
                               {"t": [120, 66], "in": ["au-e", "an", "sa-s"]}]},
    "Titanosauria": {"range": [{"t": [140, 66], "in": ["sa", "af", "mg", "in", "au-e", "an", "eu", "as-ne", "as-s", "as-c", "as-se"]},
                               {"t": [70, 66], "in": ["na-w"]}]},
    "Baragwanathia": {"range": [{"t": [427, 410], "in": ["au-e"]}, {"t": [410, 393], "in": ["au-e", "na-e", "na-n"]}],
                      "box": [[140, 152, -40, -33], [-70, -60, 46, 50]]},
    # --- Europe is two codes now (eu-n Baltica-Avalonia / eu-s the peri-Gondwanan
    # south). Before the Rheic Ocean closed they were two crusts, so every
    # pre-Carboniferous entry whose PBDB collections fall in one half (>= 5 there,
    # <= 2 in the other, rebinned by taxa_src/recode_regions.py) is narrowed to
    # it, plus the one-locality names whose place is known: Rhynie, East Kirkton,
    # Cowie Harbour, the White Sea, Charnwood. From the Carboniferous on Europe is
    # one continent and "eu" stays.
    "Tortotubus protuberans": {"range": ["eu-n", "na-e", "af-n", "ar"]},
    "East Kirkton tetrapods": {"range": ["eu-n"]},
    "Gotland reef fauna": {"range": ["eu-n"]}, "Orsten fauna": {"range": ["eu-n"]},
    "Rhynie chert biota": {"range": ["eu-n"]},
    "Bothriolepis": {"range": ["an", "as-e", "as-n", "au", "eu-n", "gl", "na-e", "na-w"]},
    "Cephalaspis": {"range": ["eu-n", "na-e", "na-n", "na-w"]},
    "Dunkleosteus": {"range": ["na-e", "eu-n", "af-n"]},
    "Eusthenopteron": {"range": ["na-e", "eu-n"]},
    "Osteostraci": {"range": ["as-n", "eu-n", "na-e", "na-n"]},
    "Rhizodus": {"range": ["eu-n", "na-e"]}, "Eoarthropleura": {"range": ["eu-n", "na-e"]},
    "Kampecaris": {"range": ["eu-n"], "box": [[-9, 2, 50, 59]]},
    "Pneumodesmus": {"range": ["eu-n"], "box": [[-9, 2, 50, 59]]},
    "Meganeura": {"range": ["eu-s"]},
    "Palaeocharinus": {"range": ["eu-n"]}, "Rhyniella": {"range": ["eu-n"]},
    "Rhyniognatha": {"range": ["eu-n"]},
    "Agnostus": {"range": ["eu-n", "na-e", "na-w", "as-n", "as-e", "as-c"]},
    "Asaphus": {"range": ["eu-n"]}, "Bigotina": {"range": ["eu-s", "af-n"]},
    "Cloudina": {"range": ["af-s", "ar", "as-e", "as-n", "eu-s", "na-w", "sa-n", "sa-s"]},
    "Dickinsonia": {"range": ["au-e", "eu-n"]},
    "Endoceras": {"range": ["as-e", "eu-n", "na-e", "na-n", "na-w", "sa-s"]},
    "Eurypterus": {"range": ["na-e", "eu-n"]}, "Holmia": {"range": ["eu-n"]},
    "Kimberella": {"range": ["ar", "au-e", "eu-n"]}, "Kjerulfia": {"range": ["eu-n"]},
    "Schmidtiellus": {"range": ["eu-n"]}, "Tribrachidium": {"range": ["au-e", "eu-n"]},
    "Yorgia": {"range": ["au-e", "eu-n"]}, "Aglaophyton": {"range": ["eu-n"]},
    "Asteroxylon": {"range": ["eu-n"]}, "Rhynia": {"range": ["eu-n"]},
    "Zosterophyllopsida": {"range": ["as-c", "eu-n", "na-e", "na-n"]},
    "Westlothiana lizziae": {"range": ["eu-n"]},
    "Anarcestes": {"range": ["af-n", "eu-s", "rhe", "as-ne", "as-s"]},
    "Parvancorina": {"range": ["as-n", "au-e", "eu-n"]},
    "Reedops": {"range": ["af-n", "eu-s", "rhe"]},
    "Archaeocyathus": {"range": ["au", "sa-s", "na-w", "as-n", "af-n", "an", "as-e", "eu-s"]},
    "Cheirolepis": {"range": ["eu-n", "gl", "na-e"]}, "Coccosteus": {"range": ["eu-n", "gl", "na-e"]},
    "Dalmanites": {"range": ["eu-n", "na-e", "iap", "af-n", "sa-s"]},
    "Platystrophia": {"range": ["na-w", "na-e", "na-n", "gl", "iap", "eu-n"]},
    "Stethacanthus": {"range": ["na-e", "na-w", "eu-n", "as-n", "au"]},
    "Streptelasma": {"range": ["na-w", "na-e", "na-n", "gl", "iap", "eu-n"]},
    "Pulmonoscorpius": {"range": ["eu-n"]},
    "Groenlandaspis": {"range": ["gl", "an", "au", "eu-n", "na-e", "af-n"]},
    "Sporogonites": {"range": ["eu-n", "au", "as-e"]}, "Tulerpeton": {"range": ["eu-n"]},
    "Melanocyrillium": {"range": ["na-w", "na-e", "au", "eu-n", "as-n"]},
    "Proterocladus": {"range": ["as-e", "na-n", "eu-n"]},
    "Svanbergfjellet biota": {"range": ["eu-n", "gl"]},
    # Silurian Zosterophyllum is Laurussian, Kazakh and South Chinese; the Devonian
    # records add the peri-Gondwanan south
    "Zosterophyllum": {"range": [{"t": [425, 419], "in": ["eu-n", "as-c", "as-ne", "as-s", "na-n"]},
                                 {"t": [419, 390], "in": ["eu-n", "eu-s", "as-c", "as-ne", "as-s", "as-ic", "as-sb", "na-n"]}],
                       "avoid": ["Gondwana"]},
    "Gymnotoceras": {"range+": ["eu-n"]},
    # the PBDB files these under Problematica, which it draws as anything
    # --- eastern North America is two codes now: the Laurentian craton (na-e)
    # and the Avalon-Carolina terranes (na-av), Gondwanan until the Silurian.
    # Mistaken Point, Charnwood's twin, is na-av; so are the Avalonian Cambrian
    # trilobites of Newfoundland and Nova Scotia and the Carolina Ediacarans.
    "Fractofusus": {"range": ["na-av"], "box": _AVALON}, "Beothukis": {"range": ["na-av"], "box": _AVALON},
    "Trepassia": {"range": ["na-av"], "box": _AVALON}, "Pectinifrons": {"range": ["na-av"], "box": _AVALON},
    "Thectardis": {"range": ["na-av"], "box": _AVALON},
    "Haootia quadriformis": {"range": ["na-av"], "box": _AVALON},
    # Baltica's own trilobites do not reach Avalonia, which shared eu-n's code
    # and sat 30 degrees of latitude away until the Silurian
    "Asaphus": {"range": ["eu-n"], "avoid": ["Avalonia"]},
    "Holmia": {"range": ["eu-n"], "avoid": ["Avalonia"]}, "Kjerulfia": {"range": ["eu-n"], "avoid": ["Avalonia"]},
    "Schmidtiellus": {"range": ["eu-n"], "avoid": ["Avalonia"]},
    "Ogygiocaris": {"avoid": ["Avalonia"]},
    "Bradgatia": {"range": ["eu-n", "na-av"]}, "Charnia": {"range": ["as-n", "au-e", "eu-n", "na-av"]},
    "Charniodiscus": {"range": ["au-e", "eu-n", "iap", "na-av"]},
    "Aspidella": {"range": ["na-av", "eu-n", "au-e", "as-n"], "form_ok": True},
    "Rangeomorpha": {"range": ["na-av", "eu-n", "au-e", "as-n", "af-s", "na-n"]},
    "Pteridinium": {"range": ["af-s", "au-e", "eu-n", "na-av"]},
    "Ediacaran biota": {"range": ["au", "eu-n", "na-av", "af-s", "as-n", "as-e", "in"]},
    "Paradoxides": {"range": ["eu", "na-av", "af-n"]},
    "Olenus": {"range": ["eu-n", "iap", "na-av", "as-c", "as-e"]},
    "Trilobite provinces": {"range": ["eu", "na-e", "na-av", "gl"]},
    # the re-read at 455-475 Ma: the warm-water Ordovician of Baltica and
    # Laurentia does not reach the Gondwanan terranes at 60-70 S
    "Megistaspis": {"range": ["eu-n"], "avoid": ["Avalonia"]},
    "Cameroceras": {"range": ["as-c", "as-e", "eu-n", "na-e"], "lat": [0, 50]},
    "Receptaculites": {"lat": [0, 55]},
    "Neseuretus": {"range": ["eu", "af-n", "ar", "sa-s", "as-s"]},
    # the mirror of the Baltic list: Avalonia's and the Mediterranean province's
    # Ordovician trilobites do not reach Baltica, which shares eu-n's code
    "Trinucleus": {"avoid": _NOT_BALTICA}, "Selenopeltis": {"avoid": _NOT_BALTICA},
    "Placoparia": {"avoid": _NOT_BALTICA}, "Colpocoryphe": {"avoid": _NOT_BALTICA},
    "Ectillaenus": {"avoid": _NOT_BALTICA}, "Onnia": {"avoid": _NOT_BALTICA},
    "Neseuretus": {"avoid": _NOT_BALTICA},
    # warm-water larger forams and rudists stop where the Tethyan platforms did
    "Orbitolina": {"lat": [0, 35]}, "Nummulites": {"lat": [0, 43]}, "Durania": {"lat": [0, 35]},
    # sponges: the Cryogenian sterane biomarkers are the oldest evidence anyone
    # accepts; body fossils are Ediacaran at the earliest. Not the Tonian.
    "Porifera": {"fad": 660},
    "Cyclomedusa": {"form_ok": True},
    # sclerites, tubes and protoconodonts: the PBDB's classes for these are
    # Problematica, Scyphozoa and Chaetognatha, drawn as anything
    "Coleoloides": {"form_ok": True}, "Corumbella werneri": {"form_ok": True},
    "Lapworthella": {"form_ok": True}, "Sunnaginia": {"form_ok": True}, "Tommotia": {"form_ok": True},
    "Protohertzina": {"form_ok": True}, "Watsonella crosbyi": {"form_ok": True},
    "Megasphaera": {"form_ok": True}, "Shaanxilithes": {"form_ok": True},
}


def _patch_merged():
    """PATCH is a dict literal, and Python keeps only the LAST entry for a name
    written twice -- which silently dropped Quercus's box when a later round
    gave it a range, and Streptelasma's latitude band when it got a range. The
    table is read from its own source and duplicates are merged field by
    field, later over earlier, so each round's refinement adds to the last."""
    import ast                                                 # noqa: PLC0415
    with open(__file__) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and \
                any(getattr(t, "id", None) == "PATCH" for t in node.targets):
            merged, dups = {}, set()
            for k, v in zip(node.value.keys, node.value.values):
                name = ast.literal_eval(k)
                val = eval(compile(ast.Expression(v), __file__, "eval"), globals())
                if name in merged:
                    dups.add(name)
                merged.setdefault(name, {}).update(val)
            if dups:
                print(f"{len(dups)} names refined in more than one round, merged")
            return merged
    return PATCH


def main():
    files = {}
    where = {}
    for fn in sorted(glob.glob(os.path.join(REG, "*.json"))):
        with open(fn) as f:
            files[fn] = json.load(f)
        for n in files[fn]["taxa"]:
            where[n] = fn
    missing, touched = [], set()
    patch = _patch_merged()
    for name, fields in patch.items():
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
    print(f"{len(patch) - len(missing)} entries refined in {len(touched)} files")
    if missing:
        print("NOT IN THE REGISTRY:", ", ".join(missing))


if __name__ == "__main__":
    main()
