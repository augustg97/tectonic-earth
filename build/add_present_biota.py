"""Give the present-day regions their OWN characteristic biota.

An audit of the labels visible at the present found 131 of 148 falling back to
the interval's global list -- so the Amazon, the Sahara, the Himalaya and the
Serengeti all showed the same handful of Quaternary megafauna. The fix is
coverage, not code: each distinctive region gets the organisms it is actually
known for, so the card says something true about THAT place.

Windows run 0-2.6 Ma (the Quaternary) unless the region only makes sense today.
Idempotent: re-running replaces these entries rather than duplicating them, so
it is safe to extend and re-run. Same merge pattern as add_marine_life.py.

Run:  ../venv/bin/python add_present_biota.py && ../venv/bin/python -c "import build_webdata as b; b.build_life()"
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "life_data.json")

Q = (0, 2.6)          # Quaternary: the window nearly all of these share

# region -> (a0, a1, [ [name, rank, realm, note], ... ])
BIOTA = {
 # ---- South America ----------------------------------------------------
 "Amazon Rainforest": (0, 10, [
   ["Ceiba pentandra", "species", "land", "The kapok, an emergent tree standing above the canopy with buttress roots metres tall."],
   ["Panthera onca", "species", "land", "The jaguar, the Americas' largest cat and the forest's apex predator."],
   ["Arapaima gigas", "species", "fresh", "One of the world's largest freshwater fish, an air-breather in oxygen-poor floodplain water."],
   ["Inia geoffrensis", "species", "fresh", "The Amazon river dolphin, pink-skinned and flexible enough to hunt in flooded forest."],
   ["Eciton burchellii", "species", "land", "Army ants whose swarm raids drive the understorey's whole insect economy."],
   ["Bromeliaceae", "family", "land", "Epiphytic bromeliads holding tank-pools in the canopy, each its own small ecosystem."]]),
 "Guiana Shield": (0, 25, [
   ["Rapateaceae", "family", "land", "An ancient plant family largely confined to the shield, radiating on the tepui summits."],
   ["Oreophrynella", "genus", "land", "Pebble toads endemic to individual tepui tops, which roll away from predators."],
   ["Heliamphora", "genus", "land", "Sun-pitcher plants trapping insects on nutrient-starved sandstone summits."],
   ["Harpia harpyja", "species", "air", "The harpy eagle, taking sloths and monkeys out of the canopy."]]),
 "Brazilian Shield": (0, 25, [
   ["Cerrado flora", "class", "land", "Fire-adapted savanna woodland with thick corky bark and vast root systems."],
   ["Myrmecophaga tridactyla", "species", "land", "The giant anteater, a specialist on the shield's termite mounds."],
   ["Chrysocyon brachyurus", "species", "land", "The maned wolf, long-legged for seeing over cerrado grass."]]),
 "Andes": (0, 15, [
   ["Vultur gryphus", "species", "air", "The Andean condor, riding ridge updraughts on a three-metre wingspan."],
   ["Vicugna vicugna", "species", "land", "The vicuna, grazing the altiplano on the finest wool of any mammal."],
   ["Polylepis", "genus", "land", "Paper-bark trees forming the highest true forests on Earth, above 4,000 m."],
   ["Telmatobius", "genus", "fresh", "Aquatic water frogs breathing through skin folds in cold high-altitude lakes."]]),
 "Patagonian Batholith": (0, 20, [
   ["Nothofagus", "genus", "land", "Southern beech, the signature Gondwanan tree of the temperate south."],
   ["Hippocamelus bisulcus", "species", "land", "The huemul, a stocky Andean deer of the southern forests."]]),
 "Sierras Pampeanas": Q + ([],),
 # ---- Africa -----------------------------------------------------------
 "African Savanna": (0, 8, [
   ["Loxodonta africana", "species", "land", "The African bush elephant, whose feeding keeps the savanna from closing to woodland."],
   ["Connochaetes taurinus", "species", "land", "The blue wildebeest, whose migration is the largest surviving land-mammal movement."],
   ["Panthera leo", "species", "land", "The lion, the only truly social big cat."],
   ["Acacia", "genus", "land", "Flat-topped thorn trees, browsed to their characteristic silhouette by giraffe."],
   ["Poaceae (C4)", "family", "land", "C4 grasses, whose Miocene spread built this biome and reshaped grazing teeth."]]),
 "Congo Basin": (0, 20, [
   ["Gorilla gorilla", "species", "land", "The western gorilla, a folivore of dense secondary forest."],
   ["Okapia johnstoni", "species", "land", "The okapi, the giraffe family's last forest-dwelling member, endemic here."],
   ["Raphia", "genus", "land", "Swamp palms bearing the longest leaves of any plant, along the flooded interior."],
   ["Protopterus", "genus", "fresh", "African lungfish, surviving the dry season encased in mud."]]),
 "Sahara": (0, 7, [
   ["Addax nasomaculatus", "species", "land", "The addax, an antelope that can live without drinking free water."],
   ["Fennecus zerda", "species", "land", "The fennec fox, radiating heat through outsized ears."],
   ["Tamarix", "genus", "land", "Salt-excreting shrubs holding the fringes of oases and wadis."],
   ["Cyanobacterial crust", "class", "land", "Biological soil crust binding sand between rains, the desert's living skin."]]),
 "Namib": (0, 15, [
   ["Welwitschia mirabilis", "species", "land", "A two-leaved gymnosperm that lives a thousand years on fog alone."],
   ["Onymacris unguicularis", "species", "land", "The fog-basking beetle, standing head-down to drink condensation off its own back."],
   ["Oryx gazella", "species", "land", "The gemsbok, tolerating body temperatures that would kill most mammals."]]),
 "Ethiopian Highlands": (0, 25, [
   ["Theropithecus gelada", "species", "land", "The gelada, the last grass-eating primate, endemic to these escarpments."],
   ["Canis simensis", "species", "land", "The Ethiopian wolf, Africa's rarest carnivore, hunting Afroalpine rodents."],
   ["Lobelia rhynchopetalum", "species", "land", "Giant rosette lobelias of the Afroalpine moorland."]]),
 "Okavango Rift": (0, 3, [
   ["Hippopotamus amphibius", "species", "land", "Hippos, whose channels through papyrus keep the inland delta's waterways open."],
   ["Cyperus papyrus", "species", "fresh", "Papyrus sedge, the delta's dominant emergent plant."],
   ["Balaeniceps rex", "species", "air", "The shoebill, ambushing lungfish in papyrus swamp."]]),
 "Taoudeni Basin": Q + ([],),
 "Hoggar Massif": (0, 10, [
   ["Olea laperrinei", "species", "land", "The Laperrine's olive, a relict of wetter Sahara clinging to the massif's heights."],
   ["Acinonyx jubatus hecki", "species", "land", "The critically endangered Saharan cheetah, ranging vast arid territories."]]),
 # ---- Eurasia ----------------------------------------------------------
 "Himalaya": (0, 20, [
   ["Panthera uncia", "species", "land", "The snow leopard, hunting blue sheep across cliff and scree."],
   ["Rhododendron", "genus", "land", "Rhododendron forests banding the wet southern slopes by altitude."],
   ["Gyps himalayensis", "species", "air", "The Himalayan griffon, soaring the highest of any vulture."],
   ["Pseudois nayaur", "species", "land", "The bharal, the snow leopard's principal prey."]]),
 "Tibetan Alpine Tundra": (0, 10, [
   ["Bos mutus", "species", "land", "The wild yak, dense-coated for the plateau's thin cold air."],
   ["Pantholops hodgsonii", "species", "land", "The chiru, migrating hundreds of km across the plateau to calve."],
   ["Kobresia", "genus", "land", "Sedge turf forming the plateau's vast alpine meadow."]]),
 "Eurasian Steppe": (0, 12, [
   ["Saiga tatarica", "species", "land", "The saiga, its bulbous nose filtering dust and warming winter air."],
   ["Equus ferus", "species", "land", "The wild horse, the steppe's defining grazer."],
   ["Stipa", "genus", "land", "Feather grasses whose awns drill their own seed into the soil."],
   ["Marmota bobak", "species", "land", "The bobak marmot, whose burrowing turns over the steppe soil."]]),
 "Alps": (0, 20, [
   ["Capra ibex", "species", "land", "The Alpine ibex, grazing near-vertical rock."],
   ["Larix decidua", "species", "land", "The European larch, a deciduous conifer at the timberline."],
   ["Marmota marmota", "species", "land", "The Alpine marmot, hibernating eight months of the year."]]),
 "Ural Mountains": (0, 20, [
   ["Picea obovata", "species", "land", "Siberian spruce, the taiga's dominant tree across the range."],
   ["Gulo gulo", "species", "land", "The wolverine, ranging the boreal forest and tundra edge."]]),
 "Taklamakan": (0, 5, [
   ["Populus euphratica", "species", "land", "The desert poplar, surviving on groundwater along dry river courses."],
   ["Camelus ferus", "species", "land", "The wild Bactrian camel, drinking salt water no other large mammal tolerates."]]),
 "Caledonides": (0, 20, [
   ["Calluna vulgaris", "species", "land", "Heather moorland covering the worn roots of the old range."],
   ["Rangifer tarandus", "species", "land", "Reindeer, grazing lichen on the Scandinavian uplands."]]),
 "Verkhoyansk Belt": (0, 20, [
   ["Larix gmelinii", "species", "land", "Dahurian larch, the only tree that forms forest on continuous permafrost."],
   ["Ovis nivicola", "species", "land", "The snow sheep, isolated on the range's high plateaus."]]),
 # ---- North America ----------------------------------------------------
 "Great Plains": (0, 12, [
   ["Bison bison", "species", "land", "The American bison, whose herds shaped the whole grassland before 1870."],
   ["Cynomys ludovicianus", "species", "land", "Black-tailed prairie dogs, whose towns are the grassland's keystone."],
   ["Bouteloua gracilis", "species", "land", "Blue grama, the shortgrass prairie's dominant sod-former."],
   ["Antilocapra americana", "species", "land", "The pronghorn, still outrunning a predator that went extinct 12,000 years ago."]]),
 "Rocky Mountains": (0, 20, [
   ["Ursus arctos horribilis", "species", "land", "The grizzly, ranging from valley floor to alpine tundra."],
   ["Pinus contorta", "species", "land", "Lodgepole pine, whose cones open only in fire."],
   ["Oreamnos americanus", "species", "land", "The mountain goat, on cliffs no predator can follow."]]),
 "Canadian Shield": (0, 20, [
   ["Picea mariana", "species", "land", "Black spruce, dominating the shield's cold wet muskeg."],
   ["Alces alces", "species", "land", "The moose, browsing willow along shield lakes and bogs."],
   ["Gavia immer", "species", "air", "The common loon, nesting on the shield's countless glacial lakes."]]),
 "Cordillera": (0, 25, [
   ["Sequoia sempervirens", "species", "land", "The coast redwood, the tallest tree on Earth, in the fog belt."],
   ["Canis lupus", "species", "land", "The grey wolf, ranging the whole western mountain system."]]),
 "Appalachians": (0, 25, [
   ["Plethodontidae", "family", "land", "Lungless salamanders -- these mountains hold the greatest diversity anywhere."],
   ["Quercus", "genus", "land", "Oaks of the eastern deciduous forest, one of the richest temperate floras."],
   ["Ursus americanus", "species", "land", "The American black bear, the range's largest surviving carnivore."]]),
 "Nearctic Tundra": (0, 3, [
   ["Rangifer tarandus", "species", "land", "Caribou, migrating between taiga wintering ground and tundra calving ground."],
   ["Ovibos moschatus", "species", "land", "The muskox, a survivor of the Pleistocene mammoth steppe."],
   ["Salix arctica", "species", "land", "Arctic willow, a centuries-old tree growing flat against the ground."]]),
 "Arctic Tundra": (0, 3, [
   ["Vulpes lagopus", "species", "land", "The Arctic fox, changing coat colour with the season."],
   ["Lemmus", "genus", "land", "Lemmings, whose population cycles drive the whole tundra food web."],
   ["Cladonia rangiferina", "species", "land", "Reindeer lichen, the tundra's dominant winter forage."]]),
 "Beringian Steppe-Tundra": (0, 2.6, [
   ["Mammuthus primigenius", "species", "land", "The woolly mammoth, the mammoth steppe's dominant grazer until ~4,000 years ago."],
   ["Bison priscus", "species", "land", "The steppe bison, ranging the land bridge between continents."],
   ["Panthera spelaea", "species", "land", "The cave lion, hunting across Beringia's cold grassland."]]),
 # ---- Australasia / Antarctica -----------------------------------------
 "Yilgarn Craton": (0, 30, [
   ["Eucalyptus", "genus", "land", "Eucalypts, fire-adapted and dominant across the ancient craton's soils."],
   ["Banksia", "genus", "land", "Banksias of the kwongan heath, one of the world's richest floras on the poorest soil."],
   ["Notoryctes typhlops", "species", "land", "The marsupial mole, blind and swimming through sand."]]),
 "Antarctica": (0, 15, [
   ["Aptenodytes forsteri", "species", "air", "The emperor penguin, the only bird that breeds through the Antarctic winter."],
   ["Deschampsia antarctica", "species", "land", "Antarctic hairgrass, one of just two flowering plants on the continent."],
   ["Belgica antarctica", "species", "land", "A flightless midge, the largest wholly terrestrial animal on the continent."],
   ["Umbilicaria", "genus", "land", "Rock-clinging lichens, the dominant life of ice-free nunataks."]]),
 "Transantarctic Mts": (0, 20, [
   ["Cryptoendolithic community", "class", "land", "Microbes living INSIDE sandstone grains, the driest-limit ecosystem on Earth."],
   ["Umbilicaria", "genus", "land", "Lichens on wind-scoured nunatak rock."]]),
}


def main():
    d = json.load(open(DATA))
    rt = d.setdefault("region_taxa", {})
    added = skipped = 0
    for name, spec in BIOTA.items():
        a0, a1, taxa = spec
        if not taxa:
            skipped += 1
            continue
        entry = {"a0": a0, "a1": a1, "taxa": taxa}
        cur = [e for e in rt.get(name, [])
               if not (e.get("a0") == a0 and e.get("a1") == a1)]
        rt[name] = cur + [entry]
        added += 1
    json.dump(d, open(DATA, "w"), indent=1)
    print("present-day biota: %d regions written, %d left for later" % (added, skipped))
    print("region_taxa now covers %d regions" % len(rt))


if __name__ == "__main__":
    main()
