"""Which biogeographic province each label sits in, at every age it is drawn.

THE PROBLEM THIS CLOSES. 336 labels show a biota panel and 101 of them have a
curated list, so **235 fell straight through to ONE GLOBAL LIST for the whole
interval**. A Verkhoyansk Belt card at 250 Ma showed "the world's Late Permian
biota" -- true of the world, and not an answer to what lived there. The heading
said so honestly, which made it a stated gap rather than an error, but it was
still the same list on two hundred different cards.

THE DECISION (2026-07-26). The MODEL decides; a curated list is a flagged
EXCEPTION. `Deep Research/modeling/paleobiogeography.py` returns a named province
for every cell in 0-1000 Ma -- 49 distinct ones, from the Sturtian snowball ocean
through the five named Ordovician shelf provinces to the Cathaysian coal flora --
so the panel can say WHICH province a place was in instead of listing the world.
Where the model still cannot place a point, the global list stays, under a
heading that says it is global.

WHAT THIS MODULE DOES. Walks every label across its own age window, takes its
palaeolatitude from the track the build already computes, asks the province model,
and emits RUNS -- [age_lo, age_hi, province_id] -- because a province changes on
the scale of a period while the timeline steps every 5 Myr, so 336 labels x 251
ages compresses to a few hundred runs. The app then looks up a province in
constant time with no biogeography ported into JavaScript.

The catalogue is imported, not copied: `paleobiogeography` is stdlib-only for
exactly this reason, and a second copy would drift from the one the audits check.
"""
import math
import os
import sys

_MODELING = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "Deep Research", "modeling")

_PB = _PG = _TD = None

# The province model's markers are bare NAMES, and a card that prints a bullet
# list of bare names is not the same object as a card that shows an organism.
# The curated lists have an icon, a rank, a realm and a sentence about each
# animal or plant, and the province tier has to match them or it reads as a
# lesser thing on the same panel.
#
# `taxa_db` in the research folder covers 42 of the 96 markers. These are the
# other 54 -- the ones that are groups, sediments and floras rather than the
# single genera a taxon database collects. Rank and realm as well as the note,
# because the card prints all three.
# The land animals, listed explicitly. This exists so the B13 check in _selftest
# can ask "does this land province name anything that MOVES" without guessing
# from the name -- see the note at the check itself for why guessing fails.
ANIMAL_MARKERS = frozenset({
    "Pneumodesmus", "Kampecaris", "trigonotarbids", "Rhyniella", "Palaeocharinus",
    "Rhyniognatha", "Ichthyostega", "Acanthostega", "Eoarthropleura",
    "Arthropleura", "Meganeura", "Palaeodictyoptera", "Eryops", "Dimetrodon",
    "Sinophoneus", "Estemmenosuchus", "Inostrancevia", "Kotlassia",
    "Lystrosaurus", "Dicynodon", "Mesosaurus", "Cynognathus", "Proterosuchus",
    "Plateosaurus", "Coelophysis", "Placerias", "Allosaurus", "Stegosaurus",
    "Archaeopteryx", "Iguanodon", "Repenomamus", "Confuciusornis",
    "Rangifer", "Ovibos", "Mammuthus", "Alces", "Ursus", "Gulo",
    "Equus", "Bison", "Cervus", "Camelus", "Oryx", "Struthio",
    "primates", "Panthera", "frugivorous birds",
    # already present before B13, in the modern-realm lists
    "Antilocapra", "Loxodonta", "Megatherium", "Toxodon", "Phorusrhacids",
    "Elephas", "Macropodidae", "Belgica antarctica", "springtails and mites",
    "Pteropus", "Partulidae",
})

MARKER_NOTES = {
    # --- LAND ANIMALS (B13) -------------------------------------------------
    # Every terrestrial scheme in paleobiogeography.py is named _*_flora, and it
    # was one: the land provinces listed plants and nothing else, so a card for a
    # continent said what grew there and never what lived there. That is not a
    # gap in the data, it is the shape of the model -- a "flora" scheme cannot
    # return fauna -- which is why the fix is here and in every terrestrial
    # province rather than in the panel that displays them.
    "Pneumodesmus": ("genus", "land", "A millipede from ~425 Ma Scotland with open spiracles -- the oldest direct evidence of an animal breathing air."),
    "Kampecaris": ("genus", "land", "A stubby Silurian millipede of the earliest land litter, feeding on decaying plant matter beside water."),
    "trigonotarbids": ("order", "land", "Extinct spider relatives, and the first land predators. They hunted without silk -- webs come later."),
    "Rhyniella": ("genus", "land", "A springtail from the Rhynie chert, ~410 Ma: the oldest known hexapod, and effectively a modern-looking one."),
    "Palaeocharinus": ("genus", "land", "A Rhynie chert trigonotarbid preserved in such detail that its book lungs and leg joints can be counted."),
    "Rhyniognatha": ("genus", "land", "Rhynie chert jaws of disputed affinity, argued to be the oldest insect -- possibly even a winged one."),
    "Ichthyostega": ("genus", "land", "An early tetrapod with seven toes and a ribcage stiff enough to prop its body up out of water."),
    "Acanthostega": ("genus", "land", "Eight toes, internal gills, and limbs that were for moving through weed rather than walking: limbs evolved IN water, before land."),
    "Eoarthropleura": ("genus", "land", "A Devonian relative of Arthropleura, an early millipede-grade detritivore of the first forest floors."),
    "Arthropleura": ("genus", "land", "A millipede up to 2.5 m long -- the largest land invertebrate ever -- browsing the Carboniferous coal forests under high oxygen."),
    "Meganeura": ("genus", "land", "A griffinfly with a 70 cm wingspan. Insects this size need the Carboniferous oxygen peak to supply their tracheae."),
    "Palaeodictyoptera": ("order", "land", "Extinct beaked insects with a third pair of winglets, sucking on Carboniferous plant reproductive organs."),
    "Eryops": ("genus", "land", "A two-metre temnospondyl amphibian of Early Permian swamps: a crocodile-shaped ambush predator that still needed water to breed."),
    "Dimetrodon": ("genus", "land", "A sail-backed synapsid -- nearer to us than to any dinosaur, and the apex predator of the Early Permian before dinosaurs existed."),
    "Sinophoneus": ("genus", "land", "A Chinese dinocephalian therapsid: the Cathaysian block's own big Middle Permian predator, on a landmass separated from the rest."),
    "Estemmenosuchus": ("genus", "land", "A bull-sized Russian dinocephalian carrying horn-like bosses on its skull -- a signature Angaran animal."),
    "Inostrancevia": ("genus", "land", "The largest gorgonopsian, with 15 cm sabre canines. Russian, Late Permian, and gone at the end-Permian extinction."),
    "Kotlassia": ("genus", "land", "A Late Permian reptiliomorph of the Angaran wetlands, close to the ancestry of amniotes."),
    "Lystrosaurus": ("genus", "land", "A tusked, barrel-chested dicynodont that survived the end-Permian and then dominated it: for a while, most land vertebrates on Earth were this one animal."),
    "Dicynodon": ("genus", "land", "A beaked, two-tusked herbivorous therapsid, abundant across Gondwana until the end-Permian extinction removed it."),
    "Mesosaurus": ("genus", "land", "A small freshwater reptile found in Brazil and South Africa and nowhere else -- one of Wegener's original arguments that the two coasts were joined."),
    "Cynognathus": ("genus", "land", "A dog-jawed cynodont with differentiated teeth and probably fur: a Triassic animal already most of the way to being a mammal."),
    "Proterosuchus": ("genus", "land", "A hook-snouted archosauriform of the earliest Triassic, an early member of the line that produces crocodiles, dinosaurs and birds."),
    "Plateosaurus": ("genus", "land", "A 10 m sauropodomorph found in bonebeds across Late Triassic Europe -- the first dinosaur to get really large."),
    "Coelophysis": ("genus", "land", "A slender, hollow-boned Late Triassic theropod, preserved by the hundred at Ghost Ranch."),
    "Placerias": ("genus", "land", "One of the last dicynodonts, a two-tonne Late Triassic herbivore living alongside the earliest dinosaurs."),
    "Allosaurus": ("genus", "land", "The common large theropod of the Late Jurassic, with a lightly built skull it used like a hatchet."),
    "Stegosaurus": ("genus", "land", "Plated and spike-tailed. The plates were probably display and thermoregulation rather than armour -- they are too thin to stop a bite."),
    "Archaeopteryx": ("genus", "land", "Feathered, winged, and still toothed and long-tailed: the fossil that made the dinosaur ancestry of birds hard to argue with."),
    "Iguanodon": ("genus", "land", "A bulky Early Cretaceous ornithopod with a thumb spike, chewing with a jaw that flexed sideways -- one of the first dinosaurs ever named."),
    "Repenomamus": ("genus", "land", "A badger-sized Cretaceous mammal found with a young dinosaur in its stomach. Mesozoic mammals were not all shrews in the dark."),
    "Confuciusornis": ("genus", "land", "An Early Cretaceous bird with a true horny beak and no teeth, known from thousands of specimens in the Jehol lake beds."),
    "Rangifer": ("genus", "land", "Reindeer: the only deer where both sexes carry antlers, and the large herbivore that makes tundra a grazed system rather than a frozen one."),
    "Ovibos": ("genus", "land", "The muskox, a survivor of the Pleistocene mammoth steppe that rings its calves with horns against wolves."),
    "Mammuthus": ("genus", "land", "Mammoths. Their grazing kept the steppe open, and the last of them died on Wrangel Island around 4,000 years ago."),
    "Alces": ("genus", "land", "The moose: the largest deer, browsing willow and feeding in boreal lakes, its splayed hooves suited to bog and snow."),
    "Ursus": ("genus", "land", "Bears. Omnivorous, wide-ranging, and one of the few large carnivores that hibernates through a boreal winter."),
    "Gulo": ("genus", "land", "The wolverine: a mustelid that kills prey many times its size and caches it in the frozen ground."),
    "Equus": ("genus", "land", "Horses and zebras. Their high-crowned teeth and single toe are the standard example of an animal rebuilt by the spread of grass."),
    "Camelus": ("genus", "land", "Camels -- which evolved in North America and only later reached the deserts they are now the emblem of."),
    "Oryx": ("genus", "land", "Desert antelope able to let their body temperature rise through the day rather than spend water cooling it."),
    "Struthio": ("genus", "land", "The ostrich: a flightless bird that answered open ground by running rather than hiding, and the largest bird alive."),
    "primates": ("order", "land", "Grasping hands, forward-facing eyes and large brains -- a group built by and largely confined to closed forest canopy."),
    "Panthera": ("genus", "land", "The big roaring cats: lion, tiger, leopard, jaguar. Ambush predators that track the large herbivores of each continent."),
    "frugivorous birds": ("informal", "land", "Fruit-eating birds -- hornbills, toucans, pigeons. Tropical trees largely depend on them to move seeds, so the forest needs them to regenerate."),
    "Belgica antarctica": ("species", "land", "A wingless midge about 5 mm long: the largest animal that lives its whole life on land in Antarctica."),
    "springtails and mites": ("informal", "land", "The entire Antarctic land fauna above the microscopic -- a few dozen species surviving in moss and under stones."),
    "Pteropus": ("genus", "land", "Flying foxes. Large fruit bats that cross open ocean under their own power, so they reach islands almost nothing else does."),
    "Partulidae": ("family", "land", "Pacific tree snails, each island valley evolving its own species -- and a textbook case of extinction by an introduced predator."),
    "bivalves": ("class", "sea", "Clams, mussels, oysters and scallops. They take over the shallow sea floor from brachiopods after the end-Permian and never give it back."),
    "bryozoans": ("phylum", "sea", "Colonial filter feeders building lace-like and twiggy crusts. Small individually, and rock-forming in bulk."),
    "graptolites": ("class", "sea", "Colonial plankton preserved as pencil marks on black shale. They evolved so fast that they date Ordovician and Silurian rock better than anything else."),
    "nautiloids": ("subclass", "sea", "Straight-shelled cephalopods, some to 6 m -- the largest animals of the Ordovician and its top predators."),
    "stromatoporoids": ("informal", "sea", "Calcified sponges that built the reefs of the Ordovician through Devonian, in the long gap between the archaeocyaths and the modern corals."),
    "tabulate corals": ("order", "sea", "Colonial corals built from stacked tubes with floors across them. Palaeozoic reef framework, extinct at the end-Permian."),
    "kelp": ("informal", "sea", "Large brown algae forming underwater forests on cool rocky coasts. A Neogene novelty, and the habitat sea otters and abalone depend on."),
    "trilobites": ("class", "sea", "Armoured arthropods with calcite eye lenses, and the dominant animal of the Cambrian sea floor. Gone at the end-Permian after 270 million years."),
    "brachiopods": ("phylum", "sea", "Two-shelled filter feeders whose valves are top-and-bottom rather than left-and-right. They ruled the Palaeozoic shelf and never recovered from the end-Permian."),
    "crinoids": ("class", "sea", "Sea lilies: stalked echinoderms filtering from the current. Their broken stems make whole Palaeozoic limestones."),
    "hyoliths": ("class", "sea", "Small conical Cambrian shells with a lid and a pair of props. What they actually were was argued for 175 years -- probably relatives of brachiopods."),
    # --- Ediacaran and Precambrian ------------------------------------------
    "Rangea": ("genus", "sea", "The type rangeomorph: a frond built from one branching unit repeated at four scales, with no mouth, gut or limbs."),
    "Bradgatia": ("genus", "sea", "A bush-shaped rangeomorph, its fronds radiating from a common base rather than standing on a stalk."),
    "Pteridinium": ("genus", "sea", "A three-vaned erniettomorph that lived half-buried in sand, its body a set of quilted tubes."),
    "Spriggina": ("genus", "sea", "A segmented Ediacaran animal with a crescentic head shield -- one of the oldest bilaterally organised body plans known."),
    "stromatolites": ("informal", "sea", "Layered buildups made by microbial mats trapping and binding sediment. The dominant reef of the first three billion years."),
    "microbialites": ("informal", "sea", "Sediment bound by microbial mats. They come back in force after every mass extinction, when the grazers that normally crop them are gone."),
    "cyanobacteria": ("phylum", "sea", "Oxygenic photosynthetic bacteria: the organisms that put oxygen in the atmosphere, and the builders of stromatolites."),
    "banded iron formation": ("informal", "sea", "Alternating iron-rich and silica-rich layers precipitated from a ferruginous ocean. They largely stop forming by 1.85 Ga, once the deep sea holds oxygen."),
    "cap carbonates": ("informal", "sea", "Sheets of carbonate laid straight on top of glacial debris as a snowball Earth ended, under an atmosphere carrying hundreds of times today's CO2."),
    # --- named by the province model and previously DROPPED -----------------
    # These are markers the model emits for its block-keyed Palaeozoic provinces.
    # Every one of them was being discarded by marker_taxon() for want of a
    # description, so the Baltic, Eastern Americas, Mediterranean, Olenellid,
    # Redlichiid and Bigotinid provinces showed a card with NO organisms on it
    # at all -- the model named them and the app said nothing.
    "Asaphus": ("genus", "sea", "A large asaphid trilobite of the Baltic cool-water carbonate shelf, some species carrying their eyes on long stalks to see over soft mud."),
    "Megistaspis": ("genus", "sea", "A big asaphid trilobite of the Baltoscandian Ordovician, common in the orthoceratite limestones."),
    "orthoceratid nautiloids": ("order", "sea", "Straight-shelled cephalopods whose conchs pave the Baltic orthoceratite limestone -- the rock takes its name from them."),
    "Bigotina": ("genus", "sea", "An early Cambrian trilobite of the West Gondwanan shelves, and the marker of the Bigotinid province."),
    "Tropidoleptus": ("genus", "sea", "A brachiopod almost confined to the Devonian Eastern Americas Realm -- one of the clearest single-genus markers of a marine province."),
    "Mucrospirifer": ("genus", "sea", "A winged spiriferide brachiopod of the Middle Devonian Appalachian seas, its hinge drawn out into long points."),
    "Australospirifer": ("genus", "sea", "A spiriferide brachiopod of the cold Malvinokaffric shelves of southern Gondwana."),
    "Burmeisteria": ("genus", "sea", "A homalonotid trilobite of the Malvinokaffric Realm, heavy-shelled and adapted to cold siliciclastic bottoms."),
    "Neseuretus": ("genus", "sea", "A calymenid trilobite of the cold peri-Gondwanan shelves, and one of the defining animals of the Mediterranean province."),
    "calymenid trilobites": ("family", "sea", "Robust, strongly enrolling trilobites that dominate the cold high-latitude Ordovician shelves where reefs are absent."),
    "Hirnantia fauna": ("informal", "sea", "The cold-water brachiopod assemblage that spread worldwide during the end-Ordovician glaciation, then vanished with it -- a fauna used as a global time marker."),
    "Holmia": ("genus", "sea", "An olenellid trilobite of the early Cambrian Baltic and Laurentian shelves."),
    "Schmidtiellus": ("genus", "sea", "One of the oldest trilobites of Baltica, from the earliest Cambrian shelly faunas."),
    "Kjerulfia": ("genus", "sea", "A large olenellid trilobite of the early Cambrian Scandinavian shelf."),
    "Eoredlichia": ("genus", "sea", "An early redlichiid trilobite of South China, found in the Chengjiang Lagerstaette alongside soft-bodied animals."),
    "Cyrtospirifer": ("genus", "sea", "A spiriferide brachiopod that spread almost worldwide in the Late Devonian, as the earlier provincial faunas merged."),
    # --- the modern biogeographic realms ------------------------------------
    "Bison": ("genus", "land", "The last of North America's Ice Age megafauna to survive in numbers; a Eurasian immigrant that crossed Beringia."),
    "Antilocapra": ("genus", "land", "The pronghorn: sole survivor of a family found nowhere but North America, and still fast enough to outrun a predator that has been extinct for 10,000 years."),
    "Sequoiadendron": ("genus", "land", "The giant sequoia, largest tree on Earth by volume and a relict of a family once spread across the northern continents."),
    "Cervus": ("genus", "land", "Red deer and their relatives, the characteristic large browsers of the Palearctic woodland and steppe."),
    "Betula": ("genus", "land", "Birch: a pioneer tree that follows retreating ice, and one of the first to colonise ground left bare by a glacier."),
    "Loxodonta": ("genus", "land", "The African elephant, and the reason the Afrotropical realm still has an intact large-mammal fauna when every other realm lost one."),
    "Adansonia": ("genus", "land", "The baobab, storing water in a massively swollen trunk -- the signature tree of seasonally arid Africa."),
    "Vachellia": ("genus", "land", "The flat-topped thorn trees of African savanna, whose spread tracks the Miocene expansion of grassland."),
    "Bromeliaceae": ("family", "land", "Bromeliads: almost entirely Neotropical, and largely epiphytic -- a family that exists because there is a canopy to live on."),
    "Dipterocarpaceae": ("family", "land", "Dipterocarps, which dominate South-East Asian rainforest to a degree no family manages anywhere else, and mast-fruit across whole regions at once."),
    "Elephas": ("genus", "land", "The Asian elephant, the surviving elephant of the Indomalayan realm."),
    "Eucalyptus": ("genus", "land", "Gum trees: a genus that made fire part of its own life cycle, and with it remade the Australian vegetation."),
    "Macropodidae": ("family", "land", "Kangaroos and wallabies -- the marsupial answer to the deer and antelope that never reached Australia."),
    "Deschampsia antarctica": ("species", "land", "Antarctic hair grass: one of only two flowering plants native to the continent, and a measure of how little land biota is left there."),
    "Metrosideros": ("genus", "land", "A tree that colonises bare lava and disperses across open ocean -- which is why it is on almost every Pacific island group."),
    "Calymenella": ("genus", "sea", "A calymenid trilobite of the cold peri-Gondwanan Ordovician shelves."),
    "Boreogadus saida": ("species", "sea", "Polar cod: it lives in and under the sea ice and is the link between Arctic plankton and everything larger."),
    "Mytilus": ("genus", "sea", "The blue mussel, a Pacific native that crossed into the Atlantic when the Bering Strait opened."),
    "sea-ice algae": ("informal", "sea", "Diatoms growing in brine channels within the ice itself, which bloom months before the open water does and start the polar year."),
    "Porites": ("genus", "sea", "A massive, slow-growing reef coral whose skeleton records annual bands like tree rings."),
    "Halimeda": ("genus", "sea", "A calcified green alga that breaks down into carbonate sand -- much of a tropical beach is dead Halimeda."),
    "seagrass meadows": ("informal", "sea", "Flowering plants that returned to the sea in the Cretaceous, binding shallow sediment and nursing juvenile fish and turtles."),
    "Inoceramus": ("genus", "sea", "A thick-shelled bivalve of Cretaceous shelf muds, some species reaching a metre across, and often the only large fossil in an otherwise barren chalk."),
    "Clarkeia": ("genus", "sea", "A brachiopod of the cold Silurian shelves of southern Gondwana, and one of the type animals of the Malvinokaffric Realm."),
    "Malvinokaffric brachiopods": ("informal", "sea", "The low-diversity, cold-water brachiopod assemblage of high-latitude Gondwana -- no reefs, few species, and quite unlike the tropical shelves of the same age."),
    # --- Palaeozoic marine ---------------------------------------------------
    "Lingula": ("genus", "sea", "An inarticulate brachiopod that has burrowed in nearshore mud since the Cambrian -- among the most conservative animals known."),
    "Pentamerus": ("genus", "sea", "A large Silurian brachiopod that formed dense shell banks across carbonate shelves."),
    "Amphipora": ("genus", "sea", "A rod-shaped stromatoporoid sponge that grew in dense thickets in the lagoons behind Devonian reefs."),
    "Claraia": ("genus", "sea", "A thin-shelled bivalve that carpeted oxygen-poor sea floors after the end-Permian extinction: a disaster taxon, abundant because almost nothing else survived."),
    "Otoceras": ("genus", "sea", "The ammonoid whose first appearance defines the base of the Triassic."),
    "Verbeekina": ("genus", "sea", "A large spherical fusulinid foraminifer, up to a centimetre across, and an index fossil of the warm Permian Tethyan shelves."),
    "Waagenophyllum": ("genus", "sea", "A rugose coral of Permian Tethyan reefs, colonial and thickly walled."),
    "Deltopecten": ("genus", "sea", "A scallop-like bivalve of the cool Permian shelves of Gondwana, found with glacial dropstones in the same beds."),
    # --- Mesozoic and Cenozoic marine ---------------------------------------
    "Daonella": ("genus", "sea", "A flat, paper-thin bivalve of Triassic deep-shelf muds, often found in mass-mortality pavements."),
    "ceratitid ammonoids": ("order", "sea", "The ammonoid group that radiated through the Triassic from the handful of lineages that survived the end-Permian bottleneck."),
    "Dachstein reef fauna": ("informal", "sea", "The Late Triassic reef community of the Tethyan carbonate platforms -- scleractinian corals, calcareous sponges and encrusting problematica."),
    "belemnites": ("order", "sea", "Squid-like cephalopods with an internal bullet-shaped guard, abundant enough in Jurassic and Cretaceous seas to make rock."),
    "orbitolinids": ("group", "sea", "Large conical foraminifera of Cretaceous carbonate platforms, big enough to see without a lens."),
    "Discocyclina": ("genus", "sea", "A large disc-shaped foraminifer of Palaeogene tropical shelves, whose tests build limestone."),
    "Acropora": ("genus", "sea", "The fast-growing staghorn and table corals that build most of the framework of a modern reef."),
    "giant clams": ("genus", "sea", "Tridacna and its relatives, which farm symbiotic algae inside their own mantle tissue on shallow tropical reefs."),
    "reef fish radiation": ("informal", "sea", "The Cenozoic diversification of the fish families that live on and around coral -- wrasses, damselfish, butterflyfish."),
    "diatom ooze": ("informal", "sea", "Sea-floor sediment made of siliceous diatom skeletons, under the high-productivity belts of the Southern Ocean and the North Pacific."),
    "krill": ("order", "sea", "Swarming shrimp-like crustaceans. In the Southern Ocean they are the single link between diatoms and everything larger."),
    "notothenioid fish": ("group", "sea", "Antarctic fish carrying antifreeze glycoproteins in their blood, which radiated into an empty ocean as it froze."),
    # --- early land plants ---------------------------------------------------
    "Rhynia": ("genus", "land", "A leafless, rootless early vascular plant -- essentially a green stem with sporangia on top, preserved whole in the Rhynie chert."),
    "Asteroxylon": ("genus", "land", "An early lycophyte with leaf-like enations along a branching stem, and rooting structures that are not yet true roots."),
    "Zosterophyllum": ("genus", "land", "An early vascular plant carrying sporangia along the sides of its stems, on the line that leads to the lycophytes."),
    "lichens": ("informal", "land", "A fungus farming algae or cyanobacteria inside itself. Among the first things to colonise bare rock, and still the pioneer on newly exposed ground."),
    # --- Carboniferous-Permian floras ---------------------------------------
    "Cathaysiodendron": ("genus", "land", "A lycopsid tree of the Cathaysian coal forests of South China -- the rainforests that kept growing after the Euramerican ones collapsed."),
    "Lobatannularia": ("genus", "land", "A horsetail relative with whorls of broad leaves, characteristic of the Cathaysian flora."),
    "Noeggerathiopsis": ("genus", "land", "A strap-leaved cordaitalean of the Angaran flora: the cool-temperate Permian vegetation of Siberia."),
    "Vojnovskya": ("genus", "land", "A gymnosperm of the Angaran flora, from a Permian Siberia too cold for the coal swamps of the tropics."),
    # --- Triassic-Jurassic floras -------------------------------------------
    "Voltzia": ("genus", "land", "An early conifer of the Triassic, spreading across ground left empty when every peat-forming plant lineage died at the end of the Permian."),
    "Neocalamites": ("genus", "land", "A large Triassic and Jurassic horsetail, successor to the Calamites of the Carboniferous swamps."),
    "Umkomasia": ("genus", "land", "The seed-bearing organ of Dicroidium, the seed fern that dominated Triassic Gondwana."),
    "Ptilophyllum": ("genus", "land", "A bennettitalean with stiff fern-like fronds, common through Jurassic and Cretaceous floras."),
    # --- angiosperms and modern vegetation ----------------------------------
    "Nymphaeales": ("order", "land", "Water lilies -- one of the earliest-branching flowering plant lineages, and among the first angiosperms in the record."),
    "Platanaceae": ("family", "land", "The plane-tree family, among the first flowering plants to become common in Cretaceous floras."),
    "angiosperm canopy trees": ("group", "land", "Flowering trees closing a canopy overhead. That structure is what makes a rainforest a rainforest, and it does not exist before the Late Cretaceous."),
    "Poaceae": ("family", "land", "The grasses. Present from the Late Cretaceous, and ecologically almost invisible until about 40 Ma, when open grassland begins."),
    "C4 grasses": ("group", "land", "Grasses using the C4 photosynthetic pathway, which is efficient in warm, dry, low-CO2 air. They build tropical savanna from about 8 Ma."),
    "sedges": ("family", "land", "Cyperaceae: grass-like plants of wet ground, marsh and tundra, where true grasses do less well."),
    "Quercus": ("genus", "land", "Oak. With beech, the backbone of Northern Hemisphere temperate deciduous forest."),
    "Fagus": ("genus", "land", "Beech, a dominant temperate deciduous tree casting shade too deep for most competitors."),
    "Pinus": ("genus", "land", "Pine: the most widespread conifer genus, holding poor soils and fire-prone ground since the Cretaceous."),
    "Picea": ("genus", "land", "Spruce, a defining conifer of the boreal forest."),
    "Larix": ("genus", "land", "Larch -- the deciduous conifer, dropping its needles to survive the extreme continental winters of interior Siberia."),
    "dwarf birch": ("species", "land", "A low, ground-hugging birch of tundra and the ragged edge of the boreal forest."),
    "Acacia": ("genus", "land", "Thorny legume trees and shrubs of the seasonally dry tropics, and a defining element of savanna woodland."),
    "succulents": ("group", "land", "Water-storing plants of arid ground -- cacti in the Americas, euphorbias in Africa -- which spread as deserts do."),
    "epiphytes": ("group", "land", "Plants growing on other plants: orchids, bromeliads, ferns. They need a canopy to live in, so they date it."),
    "lianas": ("group", "land", "Woody climbers using trees as scaffolding to reach the light. Like epiphytes, they exist only where there is a canopy."),
}

# The province model is banded and block-aware, and `block` is what turns
# "tropical" into "Cathaysian Province".
MARINE_TYPES = {"ocean", "sea"}

# --- WHICH BLOCK IS A LABEL STANDING ON? ----------------------------------
# The best provinces in the model are keyed on the BLOCK, not on latitude. The
# Ordovician alone names the Laurentian, Baltic, Siberian and Mediterranean
# shelves -- four faunas that are the entire point of the interval, because the
# Ordovician is the most provincial stretch of the Palaeozoic.
#
# `block` used to be resolved by NAME, so it fired only for the 56 labels that
# ARE cratons. The other 280 -- every mountain belt, sea, basin and desert --
# handed the model a None and fell through to its two latitude bands. The
# measured effect: at 450-470 Ma the app offered 3 provinces, against 12 today,
# so the most provincial interval in the record came out the least provincial on
# screen. The model was never the problem; nothing was reaching it.
#
# Matching on present-day position does NOT work: a label's lon/lat is its
# PALAEO-position (Avalonia is filed at 18W 35S, off Gondwana, not in
# Newfoundland), while a block's anchors are present-day. So the anchors are
# reconstructed into the same frame the labels are tracked in -- the same
# rotations, from paleo_tracks -- and the match is made at the age being asked
# about. Cratons drift apart; two points that share a plate today shared it then,
# which is what makes this well posed at all.
# How far an anchor speaks for its block. Anchors are sparse (1-8 a block), so
# this is a reach, not a boundary. Chosen by measurement against 17 labels whose
# block is not in doubt: 1200 km scores 11, 1400 scores 13, 1700 scores 14 and
# nothing above it scores better. Weighting every anchor of a block by distance
# instead of taking the nearest was tried and is WORSE (13) -- it hands the
# Tornquist Sea to Avalonia -- so the simple rule stays.
BLOCK_REACH_KM = 1700.0
_BT_CACHE = None


def _load():
    global _PB, _PG, _TD
    if _PB is None:
        try:
            if _MODELING not in sys.path:
                sys.path.insert(0, _MODELING)
            import paleobiogeography                       # noqa: PLC0415
            import paleogeography                          # noqa: PLC0415
            _PB, _PG = paleobiogeography, paleogeography
        except Exception:                                  # noqa: BLE001
            _PB, _PG = False, False
    if _TD is None:
        try:
            import taxa_db                                 # noqa: PLC0415
            _TD = taxa_db
        except Exception:                                  # noqa: BLE001
            _TD = False
    return (_PB or None), (_PG or None)


def marker_taxon(name, realm):
    """A province marker as a full taxon record, or None if it cannot be one.

    Same shape the curated lists ship in -- {n, r, realm, note, ic} -- so the
    province tier of the biota panel renders through the SAME lifeHTML as
    everything else: an icon, a rank, a realm and a sentence. A card that lists
    bare names beside cards that show organisms reads as the poor relation, and
    it is also less useful: "Lepidodendron" tells a reader nothing they did not
    already know from not knowing it.

    Source order: taxa_db (42 of the 96 markers, with size, habit and diet
    behind them), then MARKER_NOTES above for the groups and sediments a taxon
    database does not collect. Anything in neither is dropped rather than shown
    bare -- that is the honest failure, and the selftest counts it so a new
    province marker cannot slip through undescribed.
    """
    default_realm = "sea" if realm == "marine" else "land"
    rec = _TD.by_name(name) if _TD else None
    if rec is not None:
        note = rec.note or (rec.habit or "").capitalize()
        if not note:
            return None
        out = {"n": name, "r": rec.rank, "realm": rec.realm or default_realm,
               "note": note}
        # B4: size, habit and diet, where the database has them. The 273
        # silhouettes were a long way ahead of the text -- a card could draw an
        # animal accurately and not say how big it was or what it ate, which are
        # the first two things anyone asks. Only emitted when present, so the
        # card gains a line rather than a row of blanks.
        if rec.size_m:
            out["sz"] = round(float(rec.size_m), 4)
        if rec.habit and rec.habit != note.lower():
            out["hb"] = rec.habit
        if rec.diet:
            out["dt"] = rec.diet
        return out
    hit = MARKER_NOTES.get(name)
    if hit is None:
        return None
    rank, rlm, note = hit
    return {"n": name, "r": rank, "realm": rlm, "note": note}


def _icon(name, realm):
    """The illustration id, from life.py's own ordered first-match table, so a
    province marker and a curated taxon of the same name get the same drawing."""
    try:
        import life                                        # noqa: PLC0415
        return life.icon_for(name, realm) or ""
    except Exception:                                      # noqa: BLE001
        return ""


def _lat_at(lab, age):
    """Palaeolatitude of a label at `age`, from its own track."""
    tr = lab.get("tr")
    if not tr:
        return lab.get("lat")
    if age <= tr[0][0]:
        return tr[0][2]
    if age >= tr[-1][0]:
        return tr[-1][2]
    for (a0, _x0, y0), (a1, _x1, y1) in zip(tr, tr[1:]):
        if a0 <= age <= a1:
            f = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return y0 + (y1 - y0) * f
    return tr[-1][2]


def _lon_at(lab, age):
    """Palaeolongitude of a label at `age`, from the same track as _lat_at."""
    tr = lab.get("tr")
    if not tr:
        return lab.get("lon")
    if age <= tr[0][0]:
        return tr[0][1]
    if age >= tr[-1][0]:
        return tr[-1][1]
    for (a0, x0, _y0), (a1, x1, _y1) in zip(tr, tr[1:]):
        if a0 <= age <= a1:
            f = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            d = ((x1 - x0) + 180.0) % 360.0 - 180.0    # go the short way round
            return x0 + d * f
    return tr[-1][1]


def _block_tracks(step=5, age_max=1000):
    """{age: [(block, lon, lat), ...]} -- every block anchor, reconstructed.

    Built once. ~340 anchors over 201 ages is a few seconds of pyGPlates, against
    a whole interval's worth of provinces, so it is not worth being clever about.
    Returns {} if pyGPlates is unavailable, and the caller then behaves exactly
    as it did before -- name matching only.
    """
    global _BT_CACHE
    if _BT_CACHE is not None:
        return _BT_CACHE
    _pb, pg = _load()
    _BT_CACHE = {}
    try:
        import paleo_tracks                                  # noqa: PLC0415
        if pg is None or not paleo_tracks.available():
            return _BT_CACHE
        rec = paleo_tracks.Reconstructor()
    except Exception:                                        # noqa: BLE001
        return _BT_CACHE
    by_age = {}
    for name, b in pg.BLOCKS.items():
        for (x, y) in b.anchors:
            try:
                tr, _pid = rec.track(float(x), float(y), age_max, step)
            except Exception:                                # noqa: BLE001
                continue
            for a, lo, la in tr:
                by_age.setdefault(a, []).append((name, lo, la))
    _BT_CACHE = by_age
    return _BT_CACHE


def _gc_km(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return 6371.0 * math.acos(max(-1.0, min(1.0, c)))


def _block_at(lon, lat, age, tracks):
    """The block whose reconstructed anchor is nearest, or None if none is close.

    None is a real answer, not a failure. Open ocean sits on no craton, and the
    caller does not even ask for one: Panthalassa's label was landing 860 km from
    the reconstructed Antarctic Peninsula and being handed it.
    """
    pts = tracks.get(int(round(age / 5.0) * 5))
    if not pts:
        return None
    best, bd = None, 1e18
    for name, blon, blat in pts:
        d = _gc_km(lon, lat, blon, blat)
        if d < bd:
            best, bd = name, d
    return best if bd <= BLOCK_REACH_KM else None


def build(labels, step=5):
    """({province_id: record}, {label_name: [[a_lo, a_hi, id], ...]}).

    Runs are inclusive at both ends and cover only the label's own window, so a
    name is never given a province at an age it is not drawn.
    """
    pb, pg = _load()
    if pb is None:
        return {}, {}
    blocks = set(getattr(pg, "BLOCKS", ()) or ())
    tracks = _block_tracks(step=step)

    ids, recs = {}, {}
    out = {}
    for lab in labels:
        name = lab.get("n")
        a0, a1 = lab.get("a0", 0), lab.get("a1", 0)
        lo, hi = min(a0, a1), max(a0, a1)
        if hi <= 0 or lo > 1000:
            continue                       # future-only, or off the model's range
        lo = max(lo, 0)
        hi = min(hi, 1000)
        realm = "marine" if lab.get("t") in MARINE_TYPES else "terrestrial"
        # A label that IS a craton keeps its own name -- exact beats nearest.
        own = name if name in blocks else None
        runs = []
        a = lo
        while a <= hi + 1e-9:
            lat = _lat_at(lab, a)
            if lat is None:
                a += step
                continue
            block = own
            # An OCEAN basin sits on no craton by definition, so it is never
            # offered one; it takes the latitude band, which is the honest answer
            # for open water. A `sea` is usually epicontinental here and does ask.
            if block is None and tracks and lab.get("t") != "ocean":
                lon = _lon_at(lab, a)
                if lon is not None:
                    block = _block_at(float(lon), float(lat), a, tracks)
            try:
                p = pb.province(float(a), float(lat), realm, block)
            except Exception:                              # noqa: BLE001
                a += step
                continue
            # A province with confidence 'none' is a climate band wearing a
            # province's clothes; say nothing rather than dress it up.
            if p is None or p.confidence == "none":
                a += step
                continue
            key = (p.name, p.realm)
            pid = ids.get(key)
            if pid is None:
                pid = ids[key] = len(ids)
                mk = []
                for m in list(p.markers)[:8]:
                    t = marker_taxon(m, p.realm)
                    if t is None:
                        continue
                    t["ic"] = _icon(t["n"], t["realm"])
                    mk.append(t)
                recs[pid] = {"n": p.name, "r": p.realm, "b": p.basis,
                             "c": p.confidence, "note": p.note, "mk": mk}
            if runs and runs[-1][2] == pid and abs(runs[-1][1] - (a - step)) < 1e-6:
                runs[-1][1] = a
            else:
                runs.append([a, a, pid])
            a += step
        if runs:
            out[name] = runs
    return recs, out


def _selftest():
    pb, _pg = _load()
    assert pb is not None, "Deep Research/modeling/paleobiogeography.py did not import"
    labs = [{"n": "Siberia", "t": "continent", "a0": 0, "a1": 540, "lon": 100, "lat": 65},
            {"n": "Tethys Ocean", "t": "ocean", "a0": 120, "a1": 260, "lon": 90, "lat": 5},
            {"n": "Verkhoyansk Belt", "t": "orogen", "a0": 0, "a1": 300,
             "lon": 130, "lat": 65}]
    recs, runs = build(labs)
    assert runs, "no runs produced"
    for lab in labs:
        assert lab["n"] in runs, f"{lab['n']} got no province at any age"
        for a_lo, a_hi, pid in runs[lab["n"]]:
            assert a_lo <= a_hi and pid in recs
    n = sum(len(v) for v in runs.values())
    print(f"provinces OK: {len(recs)} distinct provinces, {n} runs over "
          f"{len(runs)} labels")
    for name, rr in runs.items():
        print(f"  {name}: " + "; ".join(
            f"{a1:g}-{a0:g} Ma {recs[p]['n']}" for a0, a1, p in rr[:4]))
    # EVERY marker the model can emit must be describable, or the province tier
    # quietly shows fewer organisms than the province actually has. Walk the
    # whole model, not just the provinces these three test labels happen to hit.
    pb, _pg = _load()
    missing, total = set(), set()
    # WALK WITH BLOCKS TOO. The block-keyed provinces are the model's best ones --
    # the Ordovician shelf faunas, the Devonian realms, every modern realm -- and
    # a walk that only ever passes block=None never reaches a single one of them.
    # That is how the Baltic, Eastern Americas, Mediterranean, Olenellid,
    # Redlichiid and Bigotinid provinces came to ship with every marker silently
    # dropped: this check said "95 of 96 describable" and never looked at them.
    _, _pg2 = _load()
    blocks = [None] + list(getattr(_pg2, "BLOCKS", ()) or ())
    floraonly = {}
    for realm in ("marine", "terrestrial"):
        for age in list(range(0, 1001, 10)):
            for lat in (-80, -55, -30, -10, 0, 10, 30, 55, 80):
              for _blk in blocks:
                try:
                    p = pb.province(float(age), float(lat), realm, _blk)
                except Exception:                          # noqa: BLE001
                    continue
                for m in p.markers:
                    total.add(m)
                    if marker_taxon(m, p.realm) is None:
                        missing.add(m)
                # B13: a LAND province that lists no animal is the defect the
                # user reported -- cards showing flora and never fauna. Checked
                # against an explicit set, NOT a keyword rule: a classifier that
                # guesses from the name scored Picea, Quercus, Cooksonia and
                # Archaeopteris as animals, which would have reported no problem
                # exactly where the problem was worst.
                if realm == "terrestrial" and p.markers:
                    if not any(m in ANIMAL_MARKERS for m in p.markers):
                        floraonly[p.name] = tuple(p.markers)
    print(f"  markers: {len(total)} distinct across the whole model, "
          f"{len(total) - len(missing)} describable")
    # A single machine-readable number, so audit_all can gate on it. The assert
    # below is the developer-facing form; this line is the harness-facing one.
    print(f"  province markers undescribable: {len(missing)}")
    assert not missing, ("province markers with no icon/rank/description -- add "
                         f"them to MARKER_NOTES: {sorted(missing)}")
    # Printed whether or not it is zero. A check that shows its number only when
    # it fails is unreadable exactly when it passes, and cannot be trended.
    print(f"  terrestrial provinces with no fauna: {len(floraonly)}")
    assert not floraonly, ("land provinces listing plants and no animals: "
                           f"{sorted(floraonly)}")


if __name__ == "__main__":
    _selftest()
