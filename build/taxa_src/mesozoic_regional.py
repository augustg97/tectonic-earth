"""Mesozoic land life by place (3.17): the genera that make one basin at one
moment recognisable, so a card at 180 Ma is not the same springtail, cypress and
cynodont on every continent. Before this batch 58 cards at 175-200 Ma shared 53
taxa between them (Collembola on 86% of them); the fix is not a rule but more
organisms that were really there -- each dated to its formation and ranged on
the crust its fossils lie in."""
from _lib import E, T, write
R, S, O = "Reptilia", "Saurischia", "Ornithischia"
SY, AM, MA = "Synapsida", "Amphibia", "Mammalia"

# ============================================================ TRIASSIC FLORA
E("Lepidopteris", "genus", "land", "seedfern", 260, 201.4, ["eu", "gl", "af-s", "mg", "an", "au-e", "as-n", "sa-s"],
  "Peltasperm seed ferns with pimpled leaves and seeds carried under umbrella-like discs. One of the few plant lines to ride through the end-Permian extinction, they mark the earliest Triassic and again the Rhaetian, just before the end-Triassic extinction took them.",
  w=1, cls=("Pteridospermatopsida", "Peltaspermales", "Peltaspermaceae"))
E("Scytophyllum", "genus", "land", "seedfern", 245, 215, ["eu", "as-c", "as-n"],
  "A peltasperm seed fern with long, leathery, deeply toothed leaves -- the characteristic plant of Middle and Late Triassic floras from the Alps to Central Asia and the Urals.",
  cls=("Pteridospermatopsida", "Peltaspermales", "Peltaspermaceae"))
E("Heidiphyllum", "genus", "land", "conifer", 237, 205, ["af-s", "sa-s", "an", "au-e"],
  "Strap-leaved conifer shrubs of the voltzialean line, the commonest plant on many Late Triassic Gondwanan floodplains: thickets of it lined the channels while Dicroidium forest stood behind.",
  cls=("Pinopsida", "Voltziales", "Voltziaceae"))
E("Rissikia", "genus", "land", "conifer", 247, 201.4, ["af-s", "an", "au-e", "sa-s"],
  "An early podocarp relative with flat needles in two ranks, like a yew's -- evidence that the southern conifer family that still dominates New Zealand and the Andes was already Gondwanan in the Triassic.",
  cls=("Pinopsida", "Pinales", "Podocarpaceae"))
E("Equisetites arenaceus", "species", "land", "horsetail", 240, 215, ["eu"],
  "A giant Triassic horsetail with stems up to ten centimetres thick and several metres tall -- the scouring rush scaled up, standing in reed beds along the river plains.",
  hab=["wetland", "river", "lake"], cls=("Equisetopsida", "Equisetales", "Equisetaceae"))
E("Anomopteris", "genus", "land", "fern", 250, 240, ["eu"],
  "A tall fern of the red Buntsandstein plains -- among the first plants to re-vegetate a landscape that the end-Permian extinction had stripped bare.",
  cls=("Polypodiopsida", "", ""))
E("Glossophyllum", "genus", "land", "ginkgo", 237, 220, ["eu-s", "as-c"],
  "A ginkgophyte with long, tongue-shaped leaves instead of fans -- one of several experiments in the Ginkgo line that did not outlast the Triassic.",
  cls=("Ginkgoopsida", "Ginkgoales", ""))
E("Dictyophyllum", "genus", "land", "fern", 230, 165, ["eu", "gl", "as-ne", "as-s", "as-ic", "as-c", "na-w", "ca", "sa-s", "au-e", "an"],
  "A dipterid fern with a fan of broad, net-veined leaflets. Its only living relatives are the umbrella ferns of South-East Asian clearings; in the Late Triassic and Early Jurassic the family was one of the commonest on Earth.",
  w=1, cls=("Polypodiopsida", "Gleicheniales", "Dipteridaceae"))
E("Clathropteris", "genus", "land", "fern", 230, 165, ["eu", "gl", "as-ne", "as-s", "as-c", "na-e", "sa-s"],
  "A dipterid fern whose large leaves spread like the fingers of a hand, meshed with a fine grid of veins -- a hallmark of the humid Late Triassic and Early Jurassic in both hemispheres.",
  w=1, cls=("Polypodiopsida", "Gleicheniales", "Dipteridaceae"))
E("Phlebopteris", "genus", "land", "fern", 230, 100, ["eu", "gl", "na-w", "as-ne", "as-s", "as-c", "sa-s", "an", "in"],
  "A fern of the Matoniaceae, a family now reduced to two genera on Malaysian mountains, but widespread from the Late Triassic to the mid-Cretaceous -- often the first ground cover on fresh river sands.",
  w=1, cls=("Polypodiopsida", "Gleicheniales", "Matoniaceae"))

# ============================================================ TRIASSIC FAUNA
E("Thrinaxodon", "genus", "land", "cynodont", 251.9, 247, ["af-s", "an"],
  "A cat-sized cynodont of the earliest Triassic that lived in burrows -- one was found curled up in its tunnel beside an injured amphibian. Its ribs suggest a diaphragm, a step toward the mammalian way of breathing.",
  cls=(SY, "Cynodontia", "Thrinaxodontidae"))
E("Erythrosuchus", "genus", "land", "archosaur", 247, 242, ["af-s"],
  "A five-metre, big-headed archosauriform, the heaviest land predator of the early Middle Triassic -- a sign of how fast large hunters came back after the end-Permian extinction.",
  cls=(R, "Archosauriformes", "Erythrosuchidae"))
E("Euparkeria", "genus", "land", "archosaur", 247, 242, ["af-s"],
  "A 60-centimetre, lightly armoured reptile close to the root of the archosaurs, the group of crocodiles, pterosaurs and dinosaurs. It could probably rise onto its hind legs to run.",
  cls=(R, "Archosauriformes", "Euparkeriidae"))
E("Kannemeyeria", "genus", "land", "dicynodont", 247, 237, ["af-s"],
  "A three-metre, beaked dicynodont, the big plant-eater of the Middle Triassic; a tall crest on its skull anchored the jaw muscles that sheared tough seed-fern leaves.",
  cls=(SY, "Dicynodontia", "Kannemeyeriidae"))
E("Teleocrater", "genus", "land", "archosaur", 247, 242, ["af-e"],
  "A long-necked carnivore two to three metres long, one of the earliest members of the bird line of archosaurs -- still walking on all fours, with a crocodile-like ankle, before dinosaurs existed.",
  cls=(R, "Archosauria", "Aphanosauria"))
E("Asilisaurus", "genus", "land", "archosaur", 245, 242, ["af-e"],
  "A metre-long silesaurid, a close cousin of the dinosaurs, from the Anisian -- proof that the dinosaur line had split off at least ten million years before the first dinosaur fossils.",
  cls=(R, "Archosauria", "Silesauridae"))
E("Prestosuchus", "genus", "land", "archosaur", 238, 232, ["sa-s"],
  "A seven-metre crocodile-line predator with a deep skull, walking erect on pillar legs -- the top carnivore of the Middle to Late Triassic river plains of southern Brazil.",
  cls=(R, "Pseudosuchia", "Prestosuchidae"))
E("Staurikosaurus", "genus", "land", "theropod", 233, 225, ["sa-s"],
  "A two-metre, slender predator among the first dinosaurs of all -- like Herrerasaurus, a hunter from the time when dinosaurs were still a small part of the fauna.",
  cls=(S, "Theropoda", "Herrerasauridae"))
E("Ischigualastia", "genus", "land", "dicynodont", 233, 229, ["sa-s"],
  "A hippo-sized dicynodont that shared its floodplain with the first dinosaurs -- among the last big beaked herbivores of a line that had been on land since the Permian.",
  cls=(SY, "Dicynodontia", "Stahleckeriidae"))
E("Hyperodapedon", "genus", "land", "rhynchosaur", 237, 225, ["eu-n", "in", "sa-s", "af-s", "af-e", "mg"],
  "A pig-sized rhynchosaur with a hooked beak and grinding plates of teeth. In the Carnian it was so common that it makes up most of the fossils in the same beds in Scotland, India, Brazil and Argentina.",
  cls=(R, "Rhynchosauria", "Hyperodapedontidae"))
E("Silesaurus", "genus", "land", "archosaur", 232, 226, ["eu-n"],
  "A slim, two-metre dinosaur cousin with a beak-tipped jaw; droppings attributed to it are full of small beetles, so it ate insects as well as plants.",
  cls=(R, "Archosauria", "Silesauridae"))
E("Lisowicia", "genus", "land", "dicynodont", 211, 205, ["eu-n"],
  "An elephant-sized dicynodont of the latest Triassic -- perhaps nine tonnes, walking erect -- the last and largest of a line that had been on land since the Permian.",
  cls=(SY, "Dicynodontia", "Stahleckeriidae"))
E("Stagonolepis", "genus", "land", "archosaur", 232, 225, ["eu-n"],
  "A three-metre aetosaur: an armoured, pig-snouted plant-eater of the crocodile line, rooting in the soil of Late Triassic river plains.",
  cls=(R, "Aetosauria", "Stagonolepididae"))
E("Aetosaurus", "genus", "land", "archosaur", 225, 205, ["eu-s", "gl", "na-w"],
  "A small aetosaur, a metre to a metre and a half long, armoured in rows of plates; one slab holds 24 juveniles buried together.",
  cls=(R, "Aetosauria", "Stagonolepididae"))
E("Typothorax", "genus", "land", "archosaur", 222, 205, ["na-w"],
  "A broad, flat-backed aetosaur -- a three-metre armoured plant-eater of the crocodile line, common on the Late Triassic floodplains of the American Southwest.",
  cls=(R, "Aetosauria", "Stagonolepididae"))
E("Smilosuchus", "genus", "fresh", "crocodile", 225, 212, ["na-w"],
  "A seven-metre phytosaur, crocodile-shaped but not a crocodile: its nostrils sat on a mound in front of its eyes, not at the tip of its snout.",
  realms=["fresh", "land"], cls=(R, "Phytosauria", "Phytosauridae"))
E("Mystriosuchus", "genus", "fresh", "crocodile", 222, 205, ["eu-s"],
  "A slender-snouted phytosaur of the Late Triassic Tethys coasts; some lie in marine limestones, so it may have fished at sea as well as in rivers.",
  realms=["fresh", "sea"], cls=(R, "Phytosauria", "Phytosauridae"))
E("Tawa", "genus", "land", "smalltheropod", 215, 212, ["na-w"],
  "A two-metre early theropod from New Mexico -- one of the fossils showing that dinosaurs spread north from southern Pangaea within a few million years of their origin.",
  cls=(S, "Theropoda", ""))
E("Effigia", "genus", "land", "archosaur", 212, 205, ["na-w"],
  "A toothless, beaked, two-legged reptile of the crocodile line that looks exactly like an ostrich dinosaur -- 80 million years before the ostrich dinosaurs.",
  cls=(R, "Pseudosuchia", "Shuvosauridae"))
E("Mussaurus", "genus", "land", "prosauropod", 194, 192, ["sa-s"],
  "A six-metre sauropodomorph named 'mouse lizard' for its tiny hatchlings; nest sites with eggs and young of many ages show it lived in herds.",
  cls=(S, "Sauropodomorpha", ""))
E("Mastodonsaurus", "genus", "fresh", "temnospondyl", 242, 235, ["eu"],
  "One of the largest amphibians that ever lived: a six-metre, flat-headed temnospondyl of Middle Triassic lakes, with fangs that poked up through holes in the top of its snout.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Mastodonsauridae"))
E("Gerrothorax", "genus", "fresh", "temnospondyl", 240, 201.4, ["eu", "gl"],
  "A flat, broad-headed plagiosaurid amphibian that lay on lake beds like a flatfish, gulping prey that swam over it; it kept external gills all its life.",
  realms=["fresh"], cls=(AM, "Temnospondyli", "Plagiosauridae"))
E("Cyclotosaurus", "genus", "fresh", "temnospondyl", 235, 205, ["eu", "gl", "as-ic"],
  "A three-metre capitosaur whose ear notch closed into a ring -- a top predator of Late Triassic lakes and rivers from Europe to Greenland and Thailand.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Mastodonsauridae"))
E("Paracyclotosaurus", "genus", "fresh", "temnospondyl", 245, 237, ["au-e", "in", "af-s"],
  "A two-and-a-half-metre capitosaur of Gondwana's Middle Triassic rivers; a complete skeleton was dug out of a Sydney brick pit.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Mastodonsauridae"))
E("Triadobatrachus", "genus", "fresh", "frog", 251, 249, ["mg"],
  "The oldest frog-like animal known: a ten-centimetre salientian of the Early Triassic, with a frog's skull but still a short tail and a long back.",
  realms=["fresh", "land"], cls=(AM, "Salientia", "Triadobatrachidae"))
E("Proganochelys", "genus", "land", "turtle", 210, 205, ["eu", "as-ic"],
  "One of the first turtles with a complete shell: a metre-long, toothless reptile with a spiked, clubbed tail, which could not yet pull its head in.",
  cls=(R, "Testudinata", "Proganochelyidae"))
E("Trilophosaurus", "genus", "land", "lizard", 230, 215, ["na-w"],
  "A stout, beaked reptile two metres long with broad three-cusped cheek teeth -- a Late Triassic plant-eater that looks like a lizard but belongs to the archosaur side of the reptile tree.",
  cls=(R, "Allokotosauria", "Trilophosauridae"))
E("Titanoptera", "order", "land", "grasshopper", 245, 201.4, ["as-c", "au-e"],
  "Giant Triassic relatives of grasshoppers with wings spanning up to 36 centimetres and grasping forelegs; patches on their wings may have flashed or rattled like a cicada's.",
  cls=("Insecta", "Titanoptera", ""))
E("Semionotus", "genus", "fresh", "fish", 225, 195, ["na-e", "na-av", "eu"],
  "Deep-bodied, armour-scaled fishes that split into species flocks in the rift lakes that opened as Pangaea began to break apart -- as cichlids have in the African lakes today.",
  cls=("Actinopterygii", "Semionotiformes", "Semionotidae"))

# ============================================================ JURASSIC FLORA
E("Coniopteris", "genus", "land", "fern", 190, 110, ["eu", "gl", "as-n", "as-c", "as-ne", "as-s", "na-n"],
  "A ground fern of the Dicksoniaceae, the tree ferns' low-growing kin, and the commonest fern of the Middle Jurassic of Laurasia, carpeting delta flats from England to Siberia and northern China.",
  w=1, cls=("Polypodiopsida", "Cyatheales", "Dicksoniaceae"))
E("Czekanowskia", "genus", "land", "ginkgo", 200, 100, ["as-n", "as-c", "as-ne", "eu", "gl"],
  "A shrub of the extinct Czekanowskiales, near relatives of Ginkgo, whose needle-thin leaves grew in bunches on short shoots; it covered the cool, wet lowlands of Jurassic Siberia and Mongolia in deciduous thickets.",
  w=1, cls=("Ginkgoopsida", "Czekanowskiales", "Czekanowskiaceae"))
E("Podozamites", "genus", "land", "conifer", 230, 100, ["as-n", "as-c", "as-ne", "as-s", "eu", "gl", "na-n"],
  "A conifer with broad, lance-shaped leaves spaced along slender shoots that it shed whole each autumn -- the typical tree of the seasonally cold Jurassic forests of Siberia and East Asia.",
  w=1, cls=("Pinopsida", "Voltziales", ""))
E("Nilssonia", "genus", "land", "cycad", 230, 66, ["na", "gl", "eu", "as-n", "as-c", "as-ne", "as-s", "an", "in", "au-e"],
  "Cycad-like leaves with the blade set on top of the midrib. The plant that bore them, long taken for a cycad, was deciduous and grew as far north as the Cretaceous Arctic.",
  w=1, cls=("Cycadopsida", "Nilssoniales", "Nilssoniaceae"))
E("Sagenopteris", "genus", "land", "seedfern", 230, 100, ["eu", "gl", "as-n", "as-c", "as-ne", "as-s", "na", "an", "in", "au-e", "sa-s"],
  "Leaves of the caytonialean seed ferns, four leaflets on a stalk like a clover; their seeds grew enclosed in small berry-like capsules (Caytonia), once argued to be close to the origin of flowering plants.",
  aka=["Caytonia"], w=1, cls=("Pteridospermatopsida", "Caytoniales", "Caytoniaceae"))

# ============================================================ JURASSIC FAUNA
E("Megazostrodon", "genus", "land", "smallmammal", 201.4, 190, ["af-s"],
  "A ten-centimetre, shrew-like morganucodontan of the earliest Jurassic -- one of the first near-mammals: nocturnal, insect-eating and probably furred.",
  cls=(MA, "Morganucodonta", "Megazostrodontidae"))
E("Haramiyavia", "genus", "land", "smallmammal", 208, 201.4, ["gl"],
  "A mouse-sized haramiyid of the latest Triassic with many-cusped grinding teeth -- part of the first wave of mammal-like animals.",
  cls=(MA, "Haramiyida", "Haramiyaviidae"))
E("Kuehneotherium", "genus", "land", "smallmammal", 205, 195, ["eu-n"],
  "A tiny insect-eater known from teeth washed into cave fissures on limestone islands of the Early Jurassic sea; its triangle of cusps is an early step toward the teeth of all later mammals.",
  cls=(MA, "Symmetrodonta", "Kuehneotheriidae"))
E("Lesothosaurus", "genus", "land", "ornithopod", 200, 190, ["af-s"],
  "A metre-long, lightly built early ornithischian, fast and bipedal, with leaf-shaped teeth; two found curled together suggest it may have slept out the dry seasons in shelter.",
  cls=(O, "", "Lesothosauridae"))
E("Dimorphodon", "genus", "air", "pterosaur", 199, 191, ["eu-n"],
  "A big-headed early pterosaur with a 1.4-metre wingspan and two kinds of teeth; its legs and claws suggest it climbed well and hunted on the ground as much as in the air.",
  cls=(R, "Pterosauria", "Dimorphodontidae"))
E("Dorygnathus", "genus", "air", "pterosaur", 184, 180, ["eu-s"],
  "A long-tailed pterosaur of the Toarcian with a one-metre wingspan and interlocking fangs at the tip of its jaws for seizing fish.",
  cls=(R, "Pterosauria", "Rhamphorhynchidae"))
E("Cryolophosaurus", "genus", "land", "theropod", 194, 188, ["an"],
  "A six-metre predator with a crest running across its skull from side to side, from the Early Jurassic of the Transantarctic Mountains -- dug out at 4,000 metres, 650 km from the South Pole.",
  cls=(S, "Theropoda", ""))
E("Barapasaurus", "genus", "land", "sauropod", 190, 178, ["in"],
  "One of the earliest true sauropods, fourteen metres long, from a single Early Jurassic bone bed in central India holding at least six individuals.",
  cls=(S, "Sauropoda", ""))
E("Tazoudasaurus", "genus", "land", "sauropod", 182, 175, ["af-n"],
  "A nine-metre early sauropod of the Toarcian, known from a skeleton preserved almost complete, skull and all.",
  cls=(S, "Sauropoda", "Vulcanodontidae"))
E("Patagosaurus", "genus", "land", "sauropod", 182, 177, ["sa-s"],
  "A fifteen-metre sauropod of the Early to Middle Jurassic, found with juveniles in a lake-margin community that also held the predator Piatnitzkysaurus.",
  cls=(S, "Sauropoda", "Cetiosauridae"))
E("Piatnitzkysaurus", "genus", "land", "theropod", 182, 177, ["sa-s"],
  "A four-to-five-metre megalosauroid, one of the southern cousins of Megalosaurus from the Early to Middle Jurassic of Patagonia.",
  cls=(S, "Theropoda", "Piatnitzkysauridae"))
E("Shunosaurus", "genus", "land", "sauropod", 170, 160, ["as-s"],
  "A ten-metre sauropod with a spiked bony club on the end of its tail -- one of the commonest dinosaurs of the Middle Jurassic of Sichuan.",
  cls=(S, "Sauropoda", ""))
E("Omeisaurus", "genus", "land", "sauropod", 165, 158, ["as-s"],
  "A fifteen-to-twenty-metre sauropod with a neck of seventeen vertebrae, one of the mamenchisaurids that kept East Asia's giants distinct while it was cut off from the rest of Pangaea.",
  cls=(S, "Sauropoda", "Mamenchisauridae"))
E("Monolophosaurus", "genus", "land", "theropod", 165, 158, ["as-c"],
  "A five-metre theropod with a single hollow crest running from its nose to behind its eyes, from the Junggar Basin, then a well-watered lowland.",
  cls=(S, "Theropoda", ""))
E("Sinraptor", "genus", "land", "theropod", 161, 157, ["as-c"],
  "A seven-to-eight-metre metriacanthosaurid; bite wounds on its skull show that big theropods fought one another face to face.",
  cls=(S, "Theropoda", "Metriacanthosauridae"))
E("Limusaurus", "genus", "land", "smalltheropod", 161, 157, ["as-c"],
  "A toothless ceratosaur whose young had teeth and lost them as they grew into beaked plant-eaters -- a change no other dinosaur is known to have made.",
  cls=(S, "Theropoda", "Noasauridae"))
E("Eustreptospondylus", "genus", "land", "theropod", 165, 162, ["eu-n"],
  "A five-metre megalosauroid of the Callovian, found in marine clay near Oxford -- its body had drifted from one of the islands that Jurassic Europe was broken into.",
  cls=(S, "Theropoda", "Megalosauridae"))
E("Dacentrurus", "genus", "land", "stegosaur", 154, 146, ["eu"],
  "A stegosaur up to eight metres long with paired spikes rather than broad plates along its back -- the commonest stegosaur of Late Jurassic Europe.",
  cls=(O, "Stegosauria", "Stegosauridae"))
E("Miragaia", "genus", "land", "stegosaur", 152, 148, ["eu-s"],
  "A stegosaur with a neck of at least seventeen vertebrae -- longer for its body than some sauropods' -- from the Late Jurassic of Portugal.",
  cls=(O, "Stegosauria", "Stegosauridae"))
E("Hesperosaurus", "genus", "land", "stegosaur", 156, 150, ["na-w"],
  "A short-skulled stegosaur of the early Morrison with low, oval back plates; one skeleton preserves the horny sheath that covered a plate.",
  cls=(O, "Stegosauria", "Stegosauridae"))
E("Gargoyleosaurus", "genus", "land", "ankylosaur", 154, 150, ["na-w"],
  "One of the first ankylosaurs, three metres long, with a skull roof of fused armour and a body studded with cone-shaped spikes.",
  cls=(O, "Ankylosauria", "Ankylosauridae"))
E("Dicraeosaurus", "genus", "land", "sauropod", 157, 150, ["af-e"],
  "A short-necked sauropod with a double row of tall spines along its neck and back, which may have held up a ridge or sail.",
  cls=(S, "Sauropoda", "Dicraeosauridae"))
E("Dysalotosaurus", "genus", "land", "ornithopod", 155, 150, ["af-e"],
  "A small, fast ornithopod found by the hundreds in one bone bed -- a herd of all ages killed together, perhaps by drought.",
  cls=(O, "Ornithopoda", "Dryosauridae"))
E("Turiasaurus", "genus", "land", "sauropod", 152, 145, ["eu-s"],
  "A turiasaurian sauropod of the latest Jurassic of eastern Spain, some thirty metres long and perhaps forty tonnes -- one of the largest animals ever to live in Europe.",
  cls=(S, "Sauropoda", "Turiasauria"))
E("Dryosaurus", "genus", "land", "ornithopod", 155, 148, ["na-w"],
  "A three-metre, long-legged, fast plant-eater of the Morrison plains -- a gazelle among the giants.",
  cls=(O, "Ornithopoda", "Dryosauridae"))
E("Torvosaurus", "genus", "land", "theropod", 155, 148, ["na-w", "eu-s"],
  "A ten-metre megalosaurid, one of the largest predators of the Late Jurassic, on both sides of the young Atlantic; its eggs, with embryos inside, were found in Portugal.",
  cls=(S, "Theropoda", "Megalosauridae"))
E("Docodon", "genus", "land", "smallmammal", 155, 148, ["na-w"],
  "A shrew-sized docodont with complex grinding molars -- a side branch of the mammals that could chew as well as shear.",
  cls=(MA, "Docodonta", "Docodontidae"))
E("Fruitafossor", "genus", "land", "smallmammal", 152, 150, ["na-w"],
  "A chipmunk-sized burrowing mammal of the Late Jurassic with simple peg teeth like an aardvark's -- probably a digger into insect nests.",
  cls=(MA, "", "Fruitafossoridae"))
E("Juramaia", "genus", "land", "smallmammal", 161, 159, ["as-ne"],
  "A shrew-sized climber of the Late Jurassic claimed as the oldest eutherian -- the line leading to placental mammals -- though its age and its place in the tree are debated.",
  cls=(MA, "Eutheria", ""))
E("Darwinopterus", "genus", "air", "pterosaur", 161, 159, ["as-ne"],
  "A pterosaur that combined the long tail of the early kind with the head and neck of the later -- a 'modular' intermediate; one was preserved with an egg.",
  cls=(R, "Pterosauria", "Wukongopteridae"))
E("Jeholopterus", "genus", "air", "pterosaur", 165, 160, ["as-ne"],
  "A frog-mouthed anurognathid pterosaur covered in fuzz, which hawked insects at dusk in the Jurassic forests of northern China.",
  cls=(R, "Pterosauria", "Anurognathidae"))
E("Sordes", "genus", "air", "pterosaur", 157, 150, ["as-c"],
  "A small pterosaur whose fossils first showed that pterosaurs were furred: its body was covered in hair-like fibres.",
  cls=(R, "Pterosauria", "Rhamphorhynchidae"))
E("Karaurus", "genus", "fresh", "salamander", 157, 152, ["as-c"],
  "One of the oldest true salamanders, twenty centimetres long, from the lake beds of the Late Jurassic of Kazakhstan.",
  realms=["fresh", "land"], cls=(AM, "Caudata", "Karauridae"))
E("Prosalirus", "genus", "fresh", "frog", 190, 185, ["na-w"],
  "The oldest known frog with the long hind legs and hips of a jumper, from the Early Jurassic of Arizona.",
  realms=["fresh", "land"], cls=(AM, "Anura", ""))
E("Vieraella", "genus", "fresh", "frog", 188, 183, ["sa-s"],
  "A three-centimetre frog from the Early Jurassic of Patagonia, one of the oldest that looks entirely modern.",
  realms=["fresh", "land"], cls=(AM, "Anura", ""))
E("Kayentachelys", "genus", "land", "turtle", 190, 185, ["na-w"],
  "One of the oldest turtles with a modern-looking shell and jaw, from the Early Jurassic of Arizona.",
  cls=(R, "Testudinata", ""))
E("Eileanchelys", "genus", "fresh", "turtle", 168, 166, ["eu-n"],
  "One of the earliest water-dwelling turtles, from the Middle Jurassic lagoons of the Isle of Skye -- evidence that turtles took to the water early.",
  realms=["fresh"], cls=(R, "Testudinata", ""))
E("Homoeosaurus", "genus", "land", "lizard", 152, 145, ["eu-s"],
  "A slender sphenodontian of the Solnhofen lagoon shores -- a cousin of the living tuatara, whose group was then one of the most varied among small reptiles.",
  cls=(R, "Rhynchocephalia", "Sphenodontidae"))
E("Protosuchus", "genus", "land", "crocodile", 203, 192, ["na-w", "na-av", "af-s"],
  "A metre-long crocodylomorph of the Early Jurassic with long legs for running on land -- the kind of animal all crocodiles descend from.",
  cls=(R, "Crocodylomorpha", "Protosuchidae"))
E("Goniopholis", "genus", "fresh", "crocodile", 150, 125, ["eu"],
  "A broad-snouted crocodyliform of Late Jurassic and Early Cretaceous swamps -- among the first to look and live like the alligators of today.",
  realms=["fresh", "land"], cls=(R, "Crocodyliformes", "Goniopholididae"))
E("Dakosaurus", "genus", "sea", "seacroc", 155, 137, ["eu", "ca", "sa-s"],
  "A metriorhynchid sea crocodile with a deep, short skull and serrated teeth -- a macropredator that fed on marine reptiles, the killer whale of its seas.",
  cls=(R, "Thalattosuchia", "Metriorhynchidae"))

# ====================================================== EARLY CRETACEOUS FAUNA
E("Mantellisaurus", "genus", "land", "ornithopod", 126, 122, ["eu-n"],
  "A lighter cousin of Iguanodon, about seven metres long, and the commonest large plant-eater of the Barremian of the Isle of Wight and Belgium.",
  cls=(O, "Ornithopoda", "Iguanodontia"))
E("Polacanthus", "genus", "land", "ankylosaur", 130, 122, ["eu-n"],
  "A four-to-five-metre armoured dinosaur with spikes along its flanks and a solid shield of fused armour over its hips.",
  cls=(O, "Ankylosauria", "Nodosauridae"))
E("Neovenator", "genus", "land", "theropod", 127, 122, ["eu-n"],
  "A seven-metre allosauroid, the top predator of the Barremian of the Isle of Wight; its snout was threaded with nerve canals, perhaps for sensing prey.",
  cls=(S, "Theropoda", "Neovenatoridae"))
E("Eotyrannus", "genus", "land", "theropod", 127, 122, ["eu-n"],
  "A four-metre, long-armed, lightly built early tyrannosauroid -- a sketch of Tyrannosaurus sixty million years before it.",
  cls=(S, "Theropoda", "Tyrannosauroidea"))
E("Pelecanimimus", "genus", "land", "smalltheropod", 127, 125, ["eu-s"],
  "An early ostrich-dinosaur with more than 200 tiny teeth, the most of any theropod, and a throat pouch preserved in the rock.",
  cls=(S, "Theropoda", "Ornithomimosauria"))
E("Concavenator", "genus", "land", "theropod", 127, 125, ["eu-s"],
  "A six-metre carcharodontosaurid with a strange tall hump over its hips, raised on two lengthened vertebrae.",
  cls=(S, "Theropoda", "Carcharodontosauridae"))
E("Iberomesornis", "genus", "air", "earlybird", 127, 125, ["eu-s"],
  "A sparrow-sized enantiornithine of the Barremian wetlands -- one of the 'opposite birds' that were the commonest birds of the Cretaceous.",
  cls=("Aves", "Enantiornithes", ""))
E("Istiodactylus", "genus", "air", "pterosaur", 126, 122, ["eu-n"],
  "A pterosaur with a five-metre wingspan and a rounded beak edged with interlocking triangular teeth -- perhaps a scavenger.",
  cls=(R, "Pterosauria", "Istiodactylidae"))
E("Sinornithosaurus", "genus", "land", "smalltheropod", 125, 122, ["as-ne"],
  "A turkey-sized feathered dromaeosaur of the Jehol forests; its fossils keep pigment cells that suggest reddish-brown and black plumage.",
  cls=(S, "Theropoda", "Dromaeosauridae"))
E("Caudipteryx", "genus", "land", "smalltheropod", 125, 122, ["as-ne"],
  "A peacock-sized oviraptorosaur with a fan of long feathers on its tail and short feathered arms -- a dinosaur built for display, not flight.",
  cls=(S, "Theropoda", "Oviraptorosauria"))
E("Beipiaosaurus", "genus", "land", "smalltheropod", 125, 122, ["as-ne"],
  "A two-metre therizinosaur with long, stiff filament feathers, among the first dinosaurs found with a feathery coat.",
  cls=(S, "Theropoda", "Therizinosauridae"))
E("Dilong", "genus", "land", "smalltheropod", 127, 122, ["as-ne"],
  "A two-metre early tyrannosauroid with a coat of protofeathers -- evidence that the tyrannosaur line was fuzzy from the start.",
  cls=(S, "Theropoda", "Proceratosauridae"))
E("Jeholosaurus", "genus", "land", "ornithopod", 125, 122, ["as-ne"],
  "A metre-long, fast, bipedal plant-eater with pointed front teeth -- possibly an omnivore -- from the forests of the Jehol.",
  cls=(O, "Ornithopoda", "Jeholosauridae"))
E("Eomaia", "genus", "land", "smallmammal", 125, 122, ["as-ne"],
  "A ten-centimetre climbing mammal preserved with its fur; once called the oldest eutherian, it is now placed just off the placental line.",
  cls=(MA, "Eutheria", "Eomaiidae"))
E("Lycoptera", "genus", "fresh", "bigfish", 130, 120, ["as-ne", "as-n"],
  "A small bony-tongued fish that filled the Jehol lakes by the million -- the commonest vertebrate fossil of the Early Cretaceous of north-east Asia.",
  cls=("Actinopterygii", "Osteoglossiformes", "Lycopteridae"))
E("Sauroposeidon", "genus", "land", "sauropod", 113, 110, ["na-w"],
  "A brachiosaurid with a twelve-metre neck that could reach seventeen metres up -- one of the tallest dinosaurs, from the Albian coastal plain of Oklahoma and Texas.",
  cls=(S, "Sauropoda", "Brachiosauridae"))
E("Sauropelta", "genus", "land", "ankylosaur", 116, 108, ["na-w"],
  "A five-metre nodosaur with long spikes on its neck and shoulders, the commonest armoured dinosaur of the Albian of Montana and Wyoming.",
  cls=(O, "Ankylosauria", "Nodosauridae"))
E("Gastonia", "genus", "land", "ankylosaur", 126, 122, ["na-w"],
  "A five-metre, heavily spiked polacanthid, found in the same Utah bone bed as the giant raptor Utahraptor.",
  cls=(O, "Ankylosauria", "Nodosauridae"))
E("Falcarius", "genus", "land", "smalltheropod", 139, 133, ["na-w"],
  "A four-metre early therizinosaur, known from thousands of bones in one bone bed -- caught between a meat-eating theropod and the pot-bellied plant-eaters to come.",
  cls=(S, "Theropoda", "Therizinosauria"))
E("Malawisaurus", "genus", "land", "sauropod", 125, 113, ["af-e"],
  "An early titanosaur, one of the first known from a skull -- a clue to how the last great group of sauropods began.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Eocarcharia", "genus", "land", "theropod", 115, 110, ["af-n"],
  "A carcharodontosaurid with a thick bony brow over each eye, an early relative of the giant Carcharodontosaurus.",
  cls=(S, "Theropoda", "Carcharodontosauridae"))
E("Irritator", "genus", "land", "spinosaur", 115, 110, ["sa-n"],
  "A spinosaurid with a long, crocodile-like fishing snout; its name records the irritation of scientists given a skull that fossil dealers had 'improved' with plaster.",
  cls=(S, "Theropoda", "Spinosauridae"))
E("Santanaraptor", "genus", "land", "smalltheropod", 115, 110, ["sa-n"],
  "A small coelurosaur, one of the few dinosaurs preserved with soft tissue -- muscle fibres and skin among its bones.",
  cls=(S, "Theropoda", "Coelurosauria"))
E("Tupandactylus", "genus", "air", "pterosaur", 115, 112, ["sa-n"],
  "A tapejarid pterosaur with an enormous sail-like head crest, taller than its skull was long.",
  cls=(R, "Pterosauria", "Tapejaridae"))
E("Tupuxuara", "genus", "air", "pterosaur", 115, 110, ["sa-n"],
  "A thalassodromid pterosaur with a five-metre wingspan and a tall, rounded head crest, from the lagoon beds of north-east Brazil.",
  cls=(R, "Pterosauria", "Thalassodromidae"))
E("Mawsonia", "genus", "fresh", "coelacanth", 150, 95, ["sa-n", "sa-s", "af-n", "af-w"],
  "A giant coelacanth of the rivers and lagoons of Gondwana -- up to five metres long and more, the largest coelacanth known.",
  cls=("Sarcopterygii", "Coelacanthiformes", "Mawsoniidae"))
E("Onchopristis", "genus", "fresh", "ray", 113, 93, ["af-n", "na-w", "na-e", "eu-s", "as-w"],
  "A sawskate up to eight metres long with barbed tooth-spikes along its saw -- in North Africa, the fish Spinosaurus is thought to have hunted.",
  cls=("Chondrichthyes", "Rajiformes", "Sclerorhynchidae"))
E("Minmi", "genus", "land", "ankylosaur", 125, 115, ["au-e"],
  "A small ankylosaur, about three metres long, from the Early Cretaceous of Queensland, with extra bony rods along its backbone.",
  cls=(O, "Ankylosauria", ""))

# ======================================================= LATE CRETACEOUS FAUNA
E("Oviraptor", "genus", "land", "smalltheropod", 75, 71, ["as-c"],
  "Found on a nest in 1923 and named 'egg thief', it was later shown to be brooding its own eggs -- a toothless, beaked oviraptorosaur of the Gobi dunes.",
  cls=(S, "Theropoda", "Oviraptoridae"))
E("Citipati", "genus", "land", "smalltheropod", 75, 71, ["as-c"],
  "An emu-sized oviraptorid known from adults sitting on their nests, arms spread over the eggs like a brooding bird, smothered by sand where they sat.",
  cls=(S, "Theropoda", "Oviraptoridae"))
E("Struthiomimus", "genus", "land", "smalltheropod", 76, 66, ["na-w"],
  "A toothless, fast ornithomimid four metres long, built like an ostrich, of the Late Cretaceous plains of western North America.",
  cls=(S, "Theropoda", "Ornithomimidae"))
E("Albertosaurus", "genus", "land", "theropod", 71, 68, ["na-w"],
  "A nine-metre tyrannosaur; a bone bed of 26 individuals of all ages suggests it lived, or at least died, in groups.",
  cls=(S, "Theropoda", "Tyrannosauridae"))
E("Daspletosaurus", "genus", "land", "theropod", 77, 74, ["na-w"],
  "A heavily built nine-metre tyrannosaur of Campanian Alberta and Montana, a forerunner of Tyrannosaurus in build and bite.",
  cls=(S, "Theropoda", "Tyrannosauridae"))
E("Gorgosaurus", "genus", "land", "theropod", 76.6, 75, ["na-w"],
  "A lighter, longer-legged tyrannosaur, the commonest big predator in one of the richest dinosaur faunas known.",
  cls=(S, "Theropoda", "Tyrannosauridae"))
E("Maiasaura", "genus", "land", "hadrosaur", 77, 76, ["na-w"],
  "The 'good mother lizard': nesting colonies of this duckbill, nests a body-length apart and nestlings with worn teeth, first showed that dinosaurs fed their young.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Lambeosaurus", "genus", "land", "hadrosaur", 76, 75, ["na-w"],
  "A duckbill with a hatchet-shaped hollow crest that housed its nasal passages -- probably a resonator for deep calls.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Corythosaurus", "genus", "land", "hadrosaur", 77, 75.5, ["na-w"],
  "A helmet-crested duckbill nine metres long; mummified skeletons keep the imprint of its pebbly skin.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Saurolophus", "genus", "land", "hadrosaur", 70, 68, ["na-w", "as-c"],
  "A solid-crested duckbill found on both sides of the Late Cretaceous land bridge across the Bering region, in Alberta and in Mongolia.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Olorotitan", "genus", "land", "hadrosaur", 67, 66, ["as-n"],
  "A swan-necked lambeosaurine with a fan-shaped crest, from the very end of the Cretaceous on the Amur.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Telmatosaurus", "genus", "land", "hadrosaur", 70, 66, ["eu-s"],
  "A small, primitive duckbill of the Hațeg island in the latest Cretaceous -- dwarfed, like much of the island's fauna, and a relic of an older lineage.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Zalmoxes", "genus", "land", "ornithopod", 70, 66, ["eu-s"],
  "A pig-sized rhabdodontid, one of the dwarfed dinosaurs of the Hațeg island whose small size first suggested 'island dwarfing' to Baron Nopcsa a century ago.",
  cls=(O, "Ornithopoda", "Rhabdodontidae"))
E("Magyarosaurus", "genus", "land", "sauropod", 70, 66, ["eu-s"],
  "A dwarf titanosaur of the Hațeg island, six metres long and about the weight of a horse -- a sauropod shrunk by island life.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Balaur", "genus", "land", "smalltheropod", 70, 66, ["eu-s"],
  "A stocky island paravian of Hațeg -- a dromaeosaur or a flightless bird -- with two big sickle claws on each foot.",
  cls=(S, "Theropoda", "Dromaeosauridae"))
E("Euoplocephalus", "genus", "land", "ankylosaur", 76.5, 75, ["na-w"],
  "A six-metre ankylosaurid armoured down to its eyelids, with a heavy bony club at the end of its tail.",
  cls=(O, "Ankylosauria", "Ankylosauridae"))
E("Saichania", "genus", "land", "ankylosaur", 75, 70, ["as-c"],
  "A Mongolian ankylosaurid of the arid Late Cretaceous, with looping nasal passages that may have cooled or moistened the air it breathed.",
  cls=(O, "Ankylosauria", "Ankylosauridae"))
E("Styracosaurus", "genus", "land", "ceratopsian", 75.5, 75, ["na-w"],
  "A horned dinosaur with a crown of long spikes around its frill and a single tall nose horn; bone beds show it lived in herds.",
  cls=(O, "Ceratopsia", "Ceratopsidae"))
E("Centrosaurus", "genus", "land", "ceratopsian", 76.5, 75.5, ["na-w"],
  "The commonest horned dinosaur of the Dinosaur Park Formation; one bone bed in Alberta holds thousands, probably drowned together crossing a river in flood.",
  cls=(O, "Ceratopsia", "Ceratopsidae"))
E("Chasmosaurus", "genus", "land", "ceratopsian", 76.5, 75.5, ["na-w"],
  "A horned dinosaur with a long, heart-shaped frill framing skin-covered windows -- a display structure rather than a shield.",
  cls=(O, "Ceratopsia", "Ceratopsidae"))
E("Pachyrhinosaurus", "genus", "land", "ceratopsian", 73.5, 69, ["na-w", "na-n"],
  "A horned dinosaur with a thick bony boss where a nose horn would be; it herded as far north as Alaska's North Slope, through months of polar darkness.",
  cls=(O, "Ceratopsia", "Ceratopsidae"))
E("Opisthocoelicaudia", "genus", "land", "sauropod", 70, 68, ["as-c"],
  "A twelve-metre titanosaur known from a headless skeleton; its tail vertebrae suggest it could rear up on its tail like a tripod.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Kryptobaatar", "genus", "land", "smallmammal", 75, 71, ["as-c"],
  "A mouse-sized multituberculate of the Gobi dunes -- one of the rodent-like mammals that outnumber all others in the Late Cretaceous.",
  cls=(MA, "Multituberculata", "Djadochtatheriidae"))
E("Zalambdalestes", "genus", "land", "smallmammal", 75, 71, ["as-c"],
  "A long-snouted, long-legged hopper twenty centimetres long -- an early eutherian built like an elephant shrew.",
  cls=(MA, "Eutheria", "Zalambdalestidae"))
E("Didelphodon", "genus", "land", "opossum", 69, 66, ["na-w"],
  "An otter-sized metatherian of the last of the Cretaceous with one of the strongest bites for its size of any mammal -- it crushed snails and small vertebrates.",
  cls=(MA, "Metatheria", "Stagodontidae"))
E("Vintana", "genus", "land", "smallmammal", 72, 66, ["mg"],
  "A groundhog-sized gondwanatherian, one of an extinct southern group of mammals, known from a single remarkable skull.",
  cls=(MA, "Gondwanatheria", "Sudamericidae"))
E("Adalatherium", "genus", "land", "smallmammal", 72, 66, ["mg"],
  "The 'crazy beast': a badger-sized gondwanatherian with a skeleton so odd it is hard to compare with any other mammal.",
  cls=(MA, "Gondwanatheria", ""))
E("Masiakasaurus", "genus", "land", "smalltheropod", 70, 66, ["mg"],
  "A two-metre noasaurid whose front teeth jutted forward almost horizontally -- probably for snatching fish and small prey.",
  cls=(S, "Theropoda", "Noasauridae"))
E("Rahonavis", "genus", "land", "smalltheropod", 70, 66, ["mg"],
  "A raven-sized paravian with a sickle claw like a raptor-dinosaur's and long wing bones with quill knobs -- it could probably fly.",
  cls=(S, "Theropoda", ""))
E("Najash", "genus", "land", "snake", 100, 96, ["sa-s"],
  "A snake with a hip bone and working hind legs, from the Cenomanian of Patagonia -- evidence that snakes lost their legs on land, not in the sea.",
  cls=(R, "Squamata", "Najashidae"))
E("Kaprosuchus", "genus", "land", "crocodile", 96, 93, ["af-n"],
  "The 'boar croc': a land-going crocodyliform with three pairs of tusk-like fangs and an armoured snout, perhaps for ramming.",
  cls=(R, "Crocodyliformes", "Mahajangasuchidae"))
E("Araripesuchus", "genus", "land", "crocodile", 115, 88, ["sa-n", "sa-s", "af-n"],
  "A small, long-legged, dog-like crocodyliform that ran on land across Cretaceous Gondwana, found from Brazil and Niger to Patagonia.",
  cls=(R, "Crocodyliformes", "Uruguaysuchidae"))
E("Baurusuchus", "genus", "land", "crocodile", 84, 70, ["sa-s"],
  "A deep-snouted land crocodyliform with blade-like teeth, one of the top predators of the Late Cretaceous of Brazil, where big theropods were scarce.",
  cls=(R, "Crocodyliformes", "Baurusuchidae"))
E("Mapusaurus", "genus", "land", "theropod", 97, 93, ["sa-s"],
  "A twelve-metre carcharodontosaurid; a bone bed of seven individuals of different ages hints that it hunted the giant sauropods in groups.",
  cls=(S, "Theropoda", "Carcharodontosauridae"))
E("Aucasaurus", "genus", "land", "theropod", 84, 80, ["sa-s"],
  "A six-metre abelisaurid with tiny arms and low bumps instead of horns, known from one of the most complete abelisaurid skeletons.",
  cls=(S, "Theropoda", "Abelisauridae"))
E("Buitreraptor", "genus", "land", "smalltheropod", 100, 96, ["sa-s"],
  "A chicken-sized, long-snouted dromaeosaur of the southern unenlagiine branch, which probably caught small prey and fish.",
  cls=(S, "Theropoda", "Unenlagiidae"))
E("Dreadnoughtus", "genus", "land", "sauropod", 77, 66, ["sa-s"],
  "A titanosaur about 26 metres long, known from a remarkably complete skeleton -- and still growing when it died.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Talenkauen", "genus", "land", "ornithopod", 75, 68, ["sa-s"],
  "A four-metre elasmarian ornithopod with thin bony plates along its ribs -- one of a family of southern plant-eaters that reached Antarctica and Australia.",
  cls=(O, "Ornithopoda", "Elasmaria"))
E("Rugops", "genus", "land", "theropod", 96, 93, ["af-n"],
  "A six-metre abelisaurid with a wrinkled, pitted face -- perhaps more a scavenger than a hunter.",
  cls=(S, "Theropoda", "Abelisauridae"))
E("Deltadromeus", "genus", "land", "theropod", 96, 93, ["af-n"],
  "A long-limbed, eight-metre theropod of the mid-Cretaceous river systems of North Africa -- a fast runner beside the fish-eating Spinosaurus.",
  cls=(S, "Theropoda", ""))
E("Mansourasaurus", "genus", "land", "sauropod", 80, 75, ["af-n"],
  "A titanosaur of Campanian Egypt, the first good Late Cretaceous dinosaur from mainland Africa, whose kin link its fauna to Europe's.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Alanqa", "genus", "air", "pterosaur", 100, 95, ["af-n"],
  "An azhdarchoid pterosaur with a straight, pointed, spear-like beak and a wingspan of about six metres.",
  cls=(R, "Pterosauria", "Azhdarchidae"))
E("Alioramus", "genus", "land", "theropod", 70, 68, ["as-c"],
  "A long-snouted tyrannosaur with a row of bony bumps along its nose -- a slender cousin of the giant Tarbosaurus.",
  cls=(S, "Theropoda", "Tyrannosauridae"))
E("Zhuchengtyrannus", "genus", "land", "theropod", 74, 70, ["as-ne"],
  "A ten-metre tyrannosaur of Shandong, from bone beds that also hold the giant duckbill Shantungosaurus.",
  cls=(S, "Theropoda", "Tyrannosauridae"))
E("Tsintaosaurus", "genus", "land", "hadrosaur", 76, 70, ["as-ne"],
  "A Chinese lambeosaurine with a tall, forward-pointing crest -- long thought a single unicorn horn, since rebuilt as a larger hollow crest.",
  cls=(O, "Ornithopoda", "Hadrosauridae"))
E("Vegavis", "genus", "air", "waterfowl", 67, 66, ["an"],
  "The oldest undisputed member of the modern bird groups: a relative of ducks and geese from the last of the Cretaceous in Antarctica, with a voice box that could honk.",
  cls=("Aves", "Anseriformes", "Vegaviidae"))
E("Asteriornis", "genus", "air", "gamebird", 67, 66.7, ["eu-n"],
  "The 'wonderchicken': the oldest skull of a modern bird, a quail-sized relative of both chickens and ducks from the last Cretaceous shores of Europe.",
  hab=["coast"], cls=("Aves", "Galliformes", ""))

# ================================================== CRETACEOUS FLORA
E("Frenelopsis", "genus", "land", "conifer", 140, 90, ["eu", "na-e", "na-w", "af-n", "ar", "as-ne", "as-s", "sa-n"],
  "A cheirolepid conifer with jointed, almost leafless succulent stems -- a salt-tolerant tree of Cretaceous coastal flats and lagoon margins, a mangrove before mangroves.",
  cls=("Pinopsida", "Pinales", "Cheirolepidiaceae"))
E("Tempskya", "genus", "land", "treefern", 125, 90, ["na-w", "na-e", "eu", "as-ne", "as-c", "sa-s"],
  "A tree fern that built its 'trunk' from a mass of its own tangled stems and roots, up to half a metre thick -- a way of growing tall that no living plant uses.",
  cls=("Polypodiopsida", "", "Tempskyaceae"))
E("Sapindopsis", "genus", "land", "broadleaf", 113, 98, ["na-e"],
  "Among the first flowering-plant leaves to look like a tree's -- lobed, leathery and compound -- from early relatives of the plane trees that colonised disturbed river banks in the Albian.",
  cls=("Magnoliopsida", "Proteales", "Platanaceae"))
E("Credneria", "genus", "land", "broadleaf", 100, 72, ["eu", "na-w", "na-e"],
  "Large leaves of Late Cretaceous trees related to the planes -- part of the broadleaf forest that spread through the northern continents after the mid-Cretaceous.",
  cls=("Magnoliopsida", "Proteales", ""))
E("Nelumbites", "genus", "fresh", "waterlily", 113, 95, ["na-e"],
  "An early relative of the lotus: round leaves held on central stalks above the water of oxbow lakes, 110 million years before the sacred lotus -- the line has hardly changed since.",
  hab=["lake", "wetland", "river"], cls=("Magnoliopsida", "Proteales", "Nelumbonaceae"))


# ============================ EARLY-MIDDLE JURASSIC AND EARLY CRETACEOUS, MORE
# (the thinnest interval: 58 cards at 175-200 Ma had 74 taxa between them)
E("Sarahsaurus", "genus", "land", "prosauropod", 192, 186, ["na-w"],
  "A four-metre sauropodomorph with big clawed hands -- evidence that the early long-necks reached North America from the south more than once.",
  cls=(S, "Sauropodomorpha", ""))
E("Kayentatherium", "genus", "land", "cynodont", 190, 185, ["na-w"],
  "A beaver-sized tritylodontid, a plant-eating near-mammal; one was found with 38 babies -- a reptile-sized litter in an animal close to mammals.",
  cls=(SY, "Cynodontia", "Tritylodontidae"))
E("Anchisaurus", "genus", "land", "prosauropod", 195, 190, ["na-e"],
  "A two-metre sauropodomorph whose bones, found in 1818, were the first dinosaur skeleton discovered in North America -- though not recognised as one for decades.",
  cls=(S, "Sauropodomorpha", "Anchisauridae"))
E("Yunnanosaurus", "genus", "land", "prosauropod", 199, 183, ["as-s"],
  "A seven-metre sauropodomorph of the Lufeng beds with self-sharpening, spoon-shaped teeth like a sauropod's.",
  cls=(S, "Sauropodomorpha", "Yunnanosauridae"))
E("Sinosaurus", "genus", "land", "theropod", 199, 190, ["as-s"],
  "A five-metre crested theropod of the Lufeng beds, the Asian cousin of Dilophosaurus.",
  cls=(S, "Theropoda", ""))
E("Bienotherium", "genus", "land", "cynodont", 199, 190, ["as-s"],
  "A rabbit-sized tritylodontid, a gnawing plant-eater among the last of the non-mammal cynodonts.",
  cls=(SY, "Cynodontia", "Tritylodontidae"))
E("Hadrocodium", "genus", "land", "smallmammal", 199, 190, ["as-s"],
  "A two-gram mammaliaform with a large brain for its size and the ear bones separated from the jaw, as in true mammals.",
  cls=(MA, "Mammaliaformes", ""))
E("Berberosaurus", "genus", "land", "theropod", 183, 175, ["af-n"],
  "A five-metre early ceratosaur of the Toarcian High Atlas, near the root of the line that led to the abelisaurids.",
  cls=(S, "Theropoda", "Abelisauridae"))
E("Kotasaurus", "genus", "land", "sauropod", 190, 180, ["in"],
  "A nine-metre early sauropod from a single Early Jurassic bone bed in India, with the lightly built limbs of a transitional form.",
  cls=(S, "Sauropoda", ""))
E("Siderops", "genus", "fresh", "temnospondyl", 185, 175, ["au-e"],
  "A two-and-a-half-metre temnospondyl of the Early Jurassic -- a late survivor of the big amphibians in the cool rivers of southern Gondwana.",
  realms=["fresh", "land"], cls=(AM, "Temnospondyli", "Chigutisauridae"))
E("Proceratosaurus", "genus", "land", "smalltheropod", 167, 165, ["eu-n"],
  "A three-metre, nose-crested early tyrannosauroid from the Bathonian of England, near the root of the tyrannosaur line.",
  cls=(S, "Theropoda", "Proceratosauridae"))
E("Lexovisaurus", "genus", "land", "stegosaur", 166, 163, ["eu"],
  "A stegosaur of the Middle Jurassic of England and France with tall spines on its shoulders and tail.",
  cls=(O, "Stegosauria", "Stegosauridae"))
E("Borealestes", "genus", "land", "smallmammal", 168, 165, ["eu-n"],
  "A shrew-sized docodont of the Middle Jurassic lagoon shores, known from nearly complete skeletons from the Isle of Skye.",
  cls=(MA, "Docodonta", "Docodontidae"))
E("Stereognathus", "genus", "land", "cynodont", 168, 165, ["eu-n"],
  "A tritylodontid -- a plant-eating near-mammal -- among the last of its line, from the Bathonian of England and Scotland.",
  cls=(SY, "Cynodontia", "Tritylodontidae"))
E("Amphitherium", "genus", "land", "smallmammal", 168, 165, ["eu-n"],
  "A tiny Middle Jurassic mammal known from jaws found at Stonesfield in Oxfordshire -- among the first Mesozoic mammals ever recognised.",
  cls=(MA, "Dryolestida", "Amphitheriidae"))
E("Spinophorosaurus", "genus", "land", "sauropod", 170, 166, ["af-n"],
  "A thirteen-metre early sauropod of the Middle Jurassic of Niger, once reconstructed with tail spikes like Shunosaurus's.",
  cls=(S, "Sauropoda", ""))
E("Atlasaurus", "genus", "land", "sauropod", 168, 163, ["af-n"],
  "A fifteen-metre sauropod of the Moroccan High Atlas with unusually long legs for its body -- a brachiosaur-like build reached independently.",
  cls=(S, "Sauropoda", ""))
E("Gasosaurus", "genus", "land", "theropod", 170, 163, ["as-s"],
  "A four-metre tetanuran of the Middle Jurassic of Sichuan, named for the gas company whose digging found it.",
  cls=(S, "Theropoda", ""))
E("Kulindadromeus", "genus", "land", "ornithopod", 170, 164, ["as-n"],
  "A metre-and-a-half plant-eater from Transbaikalia whose body was covered in filaments and whose legs had scales -- a sign that feather-like fuzz was widespread among dinosaurs.",
  cls=(O, "Neornithischia", ""))
E("Kileskus", "genus", "land", "smalltheropod", 168, 165, ["as-n"],
  "A small early tyrannosauroid from the Middle Jurassic of Siberia, a proceratosaurid like Guanlong.",
  cls=(S, "Theropoda", "Proceratosauridae"))
E("Tianyulong", "genus", "land", "ornithopod", 161, 158, ["as-ne"],
  "A cat-sized heterodontosaurid with long bristle-like filaments along its back and tail.",
  cls=(O, "", "Heterodontosauridae"))
E("Tuojiangosaurus", "genus", "land", "stegosaur", 165, 157, ["as-s"],
  "A seven-metre stegosaur of the Late Jurassic of Sichuan with pointed plates in pairs along its back.",
  cls=(O, "Stegosauria", "Stegosauridae"))
E("Fukuiraptor", "genus", "land", "theropod", 125, 115, ["as-ne"],
  "A four-metre megaraptoran with large hand claws, from the Early Cretaceous of Japan.",
  cls=(S, "Theropoda", "Megaraptora"))
E("Phuwiangosaurus", "genus", "land", "sauropod", 130, 125, ["as-ic"],
  "A twenty-metre titanosaur-line sauropod of the Early Cretaceous of north-east Thailand.",
  cls=(S, "Sauropoda", "Titanosauria"))
E("Siamosaurus", "genus", "land", "spinosaur", 130, 125, ["as-ic"],
  "A spinosaurid known from its conical, fluted fish-catching teeth, from the Early Cretaceous rivers of Thailand.",
  cls=(S, "Theropoda", "Spinosauridae"))
E("Lurdusaurus", "genus", "land", "ornithopod", 115, 110, ["af-n"],
  "A squat, heavy iguanodontian of Niger with a thumb spike and a body built low like a hippo's -- perhaps half-aquatic.",
  cls=(O, "Ornithopoda", "Iguanodontia"))
E("Bajadasaurus", "genus", "land", "sauropod", 140, 130, ["sa-s"],
  "A dicraeosaurid with very long, forward-curving spines on its neck -- a defensive palisade, or the frame of a display.",
  cls=(S, "Sauropoda", "Dicraeosauridae"))
E("Qantassaurus", "genus", "land", "ornithopod", 125, 115, ["au-e"],
  "A small, short-faced ornithopod of the polar forests of Early Cretaceous Victoria, then well inside the Antarctic Circle.",
  cls=(O, "Ornithopoda", ""))
E("Ruffordia", "genus", "land", "fern", 145, 110, ["eu", "na-e", "as-ne", "as-n"],
  "A climbing schizaeaceous fern with finely divided fronds, one of the characteristic ferns of the Early Cretaceous floodplains of Laurasia.",
  cls=("Polypodiopsida", "Schizaeales", "Anemiaceae"))

write("x-mesozoic-regional.json")
