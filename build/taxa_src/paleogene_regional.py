"""Paleogene land life by place (3.17). Between the dinosaurs and the Miocene the
registry held only 19-29 extinct land taxa alive at any moment, so the cards of
25-66 Ma leaned on pine, royal fern, moss and the dragonfly clade everywhere
(Pinus on 37% of the cards at 25-50 Ma, Osmunda on 49% at 75-100). These are
the mammals, birds, fishes and trees that make each continent's Paleocene,
Eocene and Oligocene its own -- the Green River lakes, Messel, the Fayum, the
White River plains, Tiupampa, Riversleigh -- dated and ranged by their beds."""
from _lib import E, T, write
MA, AV = "Mammalia", "Aves"


def NOW(*boxes, since=2.6):
    return [{"t": [since, 0], "box": [list(b) for b in boxes]}]


# ================================================================== PALEOCENE
E("Pantolambda", "genus", "land", "pantodont", 63, 60, ["na-w"],
  "A sheep-sized early pantodont, one of the first mammals to grow large after the dinosaurs -- a heavy-limbed browser of the Paleocene swamp forests.",
  cls=(MA, "Pantodonta", "Pantolambdidae"))
E("Titanoides", "genus", "land", "pantodont", 60, 57, ["na-w"],
  "A bear-sized pantodont with long tusk-like canines and clawed feet -- a Paleocene browser, among the largest mammals of its time.",
  cls=(MA, "Pantodonta", "Titanoideidae"))
E("Chriacus", "genus", "land", "condylarth", 64, 54, ["na-w"],
  "A raccoon-sized arctocyonid with a long tail and grasping feet -- a climbing omnivore of the Paleocene forests.",
  cls=(MA, "Condylarthra", "Arctocyonidae"))
E("Plesiadapis", "genus", "land", "lemur", 60, 55, ["na-w", "eu"],
  "A squirrel-like relative of primates with big gnawing incisors -- one of the few Paleocene mammals found on both sides of the young North Atlantic.",
  cls=(MA, "Plesiadapiformes", "Plesiadapidae"))
E("Champsosaurus", "genus", "fresh", "crocodile", 75, 50, ["na-w", "na-n", "eu"],
  "A gharial-snouted choristodere -- not a crocodile at all -- that fished the rivers of the latest Cretaceous and Paleocene, and came through the extinction that ended the dinosaurs.",
  cls=("Reptilia", "Choristodera", "Champsosauridae"))
E("Borealosuchus", "genus", "fresh", "crocodile", 72, 50, ["na-w", "na-e", "na-n"],
  "A long-snouted crocodilian that crossed the end-Cretaceous extinction and lived on in the warm Paleocene rivers of North America.",
  cls=("Reptilia", "Crocodylia", ""))
E("Arctocyon", "genus", "land", "condylarth", 60, 56, ["eu", "na-w"],
  "A bear-sized arctocyonid with blunt teeth and a heavy tail -- an omnivore of the Paleocene forests on both sides of the North Atlantic.",
  cls=(MA, "Condylarthra", "Arctocyonidae"))
E("Pleuraspidotherium", "genus", "land", "condylarth", 59, 57, ["eu"],
  "A small hoofed mammal of the Paleocene of France, known from hundreds of individuals in a single quarry.",
  cls=(MA, "Condylarthra", "Pleuraspidotheriidae"))
E("Bemalambda", "genus", "land", "pantodont", 63, 61, ["as-s"],
  "A dog-sized pantodont of the earliest Paleocene of South China, one of the first mammals to take over the plant-eating roles the dinosaurs had left.",
  cls=(MA, "Pantodonta", "Bemalambdidae"))
E("Prodinoceras", "genus", "land", "uintathere", 60, 56, ["as-c", "as-ne"],
  "An early dinocerate from the Paleocene of Mongolia and China -- a tapir-sized ancestor of the horned, tusked uintatheres.",
  cls=(MA, "Dinocerata", "Uintatheriidae"))
E("Heomys", "genus", "land", "rodent", 61, 59, ["as-s"],
  "A small gnawing mammal from the Paleocene of China, close to the common ancestor of rodents and rabbits.",
  cls=(MA, "Mixodontia", "Eurymylidae"))
E("Pucadelphys", "genus", "land", "opossum", 64, 62, ["sa-n"],
  "A mouse-sized marsupial relative from the earliest Paleocene of Bolivia, found as groups of complete skeletons -- perhaps families killed together.",
  cls=(MA, "Metatheria", "Pucadelphyidae"))
E("Mayulestes", "genus", "land", "sparassodont", 64, 62, ["sa-n"],
  "A weasel-sized early sparassodont, a climbing predator at the root of South America's marsupial-line carnivores.",
  cls=(MA, "Sparassodonta", "Mayulestidae"))
E("Eritherium", "genus", "land", "proboscidean", 60, 58, ["af-n"],
  "The oldest known proboscidean: a fox-sized animal from the Paleocene of Morocco, 55 million years before the mammoths.",
  cls=(MA, "Proboscidea", ""))

# ==================================================================== EOCENE
E("Heptodon", "genus", "land", "tapir", 52, 48, ["na-w"],
  "An early tapir the size of a small pony, still without the trunk -- a body plan the line then kept for fifty million years.",
  cls=(MA, "Perissodactyla", "Helaletidae"))
E("Palaeosyops", "genus", "land", "brontothere", 50, 46, ["na-w"],
  "A heavy, hornless brontothere, a browser in the warm Eocene forests before the giant horned kinds.",
  cls=(MA, "Perissodactyla", "Brontotheriidae"))
E("Hyrachyus", "genus", "land", "rhino", 50, 42, ["na-w", "eu", "as-ne", "as-s"],
  "A tapir-sized, hornless early rhinocerotoid, widespread across the Eocene northern continents.",
  cls=(MA, "Perissodactyla", "Hyrachyidae"))
E("Oxyaena", "genus", "land", "hyaenodont", 56, 50, ["na-w"],
  "A wolverine-like oxyaenid, one of the first large mammal predators, of the earliest Eocene of North America.",
  cls=(MA, "Oxyaenodonta", "Oxyaenidae"))
E("Patriofelis", "genus", "land", "hyaenodont", 50, 43, ["na-w"],
  "A lion-sized oxyaenid with a short, heavy skull -- the top predator of the Middle Eocene of Wyoming.",
  cls=(MA, "Oxyaenodonta", "Oxyaenidae"))
E("Mesonyx", "genus", "land", "mesonychid", 50, 43, ["na-w", "as-ne"],
  "A wolf-sized mesonychid with hoofed toes and crushing teeth -- a running, hoofed carnivore unlike anything alive.",
  cls=(MA, "Mesonychia", "Mesonychidae"))
E("Notharctus", "genus", "land", "lemur", 50, 46, ["na-w"],
  "A lemur-like adapiform primate of the Eocene forests of Wyoming, leaping between branches with a long tail.",
  hab=["forest", "rainforest"], cls=(MA, "Primates", "Notharctidae"))
E("Diplomystus", "genus", "fresh", "cod", 55, 45, ["na-w"],
  "A herring relative of the Eocene lakes of Wyoming, often fossilised with a smaller fish -- Knightia -- in its mouth.",
  hab=["lake"], cls=("Actinopterygii", "Clupeiformes", "Ellimmichthyidae"))
E("Mioplosus", "genus", "fresh", "reeffish", 52, 48, ["na-w"],
  "A perch-like predatory fish of the Green River lakes, sometimes preserved choking on its last meal.",
  hab=["lake"], cls=("Actinopterygii", "Perciformes", ""))
E("Heliobatis", "genus", "fresh", "ray", 52, 48, ["na-w"],
  "A freshwater stingray of the Eocene Green River lakes -- a sea animal living far inland.",
  hab=["lake"], cls=("Chondrichthyes", "Myliobatiformes", "Dasyatidae"))
E("Presbyornis", "genus", "air", "waterfowl", 62, 50, ["na-w", "as-c"],
  "A long-legged early relative of ducks that nested in vast colonies on the shores of Eocene soda lakes -- a duck's head on a flamingo's body.",
  hab=["lake", "wetland"], cls=(AV, "Anseriformes", "Presbyornithidae"))
E("Leptictidium", "genus", "land", "smallmammal", 48, 37, ["eu"],
  "A long-tailed, long-snouted insectivore that ran on its hind legs through the undergrowth of the Eocene forests of Europe.",
  cls=(MA, "Leptictida", "Pseudorhyncocyonidae"))
E("Palaeochiropteryx", "genus", "air", "bat", 48, 46, ["eu"],
  "One of the earliest bats: its stomach contents show it hunted moths near the forest floor, and its ear bones show it could echolocate.",
  cls=(MA, "Chiroptera", "Palaeochiropterygidae"))
E("Ailuravus", "genus", "land", "rodent", 50, 46, ["eu"],
  "A squirrel-like early rodent nearly a metre long with its bushy tail, preserved at Messel with leaves in its gut.",
  cls=(MA, "Rodentia", "Ischyromyidae"))
E("Diplocynodon", "genus", "fresh", "crocodile", 50, 15, ["eu"],
  "A small alligator relative, the common crocodilian of Europe's lakes and rivers from the Eocene to the Miocene.",
  cls=("Reptilia", "Crocodylia", "Diplocynodontidae"))
E("Palaeotherium", "genus", "land", "horse", 45, 30, ["eu"],
  "A horse relative that looked more like a tapir, from pony- to horse-sized, which browsed the Eocene forests of Europe's islands.",
  cls=(MA, "Perissodactyla", "Palaeotheriidae"))
E("Gobiatherium", "genus", "land", "uintathere", 45, 40, ["as-c"],
  "A hornless dinocerate with a big, bulbous snout, from the Middle Eocene of Mongolia.",
  cls=(MA, "Dinocerata", "Uintatheriidae"))
E("Indohyus", "genus", "land", "deer", 49, 47, ["in"],
  "A raccoon-sized, chevrotain-like artiodactyl with thick, dense leg bones for wading -- the closest known relative of whales.",
  cls=(MA, "Artiodactyla", "Raoellidae"))
E("Pakicetus", "genus", "land", "archaeocete", 50, 48, ["in"],
  "The earliest whale: a wolf-sized, four-legged land animal of the Eocene of Pakistan, with the ear bones that mark every whale since.",
  realms=["land", "fresh"], cls=(MA, "Cetacea", "Pakicetidae"))
E("Eosimias", "genus", "land", "monkey", 45, 40, ["as-s", "as-ne"],
  "A tiny early anthropoid from the Eocene of China, small enough to sit in a hand -- evidence that the monkey-and-ape line began in Asia.",
  hab=["forest", "rainforest"], cls=(MA, "Primates", "Eosimiidae"))
E("Palaeomastodon", "genus", "land", "proboscidean", 36, 30, ["af-n"],
  "A long-jawed early proboscidean of the Fayum swamps, with short tusks above and below -- a step between Moeritherium and the mastodons.",
  cls=(MA, "Proboscidea", "Palaeomastodontidae"))
E("Saghatherium", "genus", "land", "hyrax", 35, 30, ["af-n", "ar"],
  "A small hyrax of the Fayum -- from a time when hyraxes, not antelopes, were Africa's main grazers and browsers.",
  cls=(MA, "Hyracoidea", "Saghatheriidae"))
E("Titanohyrax", "genus", "land", "hyrax", 35, 30, ["af-n", "ar"],
  "A hyrax as heavy as a small rhinoceros, the giant of the hyraxes that then held Africa's plant-eating niches.",
  cls=(MA, "Hyracoidea", "Titanohyracidae"))
E("Apidium", "genus", "land", "monkey", 34, 29, ["af-n"],
  "A squirrel-monkey-sized early anthropoid of the Fayum, a leaper in the trees that fringed the Oligocene rivers.",
  hab=["forest", "rainforest"], cls=(MA, "Primates", "Parapithecidae"))
E("Thomashuxleya", "genus", "land", "notoungulate", 45, 40, ["sa-s"],
  "A sheep-sized notoungulate -- one of South America's native hoofed mammals, which evolved in isolation for sixty million years.",
  cls=(MA, "Notoungulata", "Isotemnidae"))
E("Branisella", "genus", "land", "monkey", 26, 25, ["sa-n"],
  "The oldest known New World monkey, from Bolivia -- descended from African primates that had crossed the Atlantic, probably on floating vegetation.",
  hab=["forest", "rainforest"], cls=(MA, "Primates", ""))
E("Proborhyaena", "genus", "land", "sparassodont", 29, 26, ["sa-s", "sa-n"],
  "A bear-sized sparassodont, a marsupial-line predator of the Oligocene with ever-growing canines.",
  cls=(MA, "Sparassodonta", "Proborhyaenidae"))
E("Anthropornis", "genus", "sea", "penguin", 45, 33, ["an"],
  "A giant penguin of the Eocene of Antarctica, 1.7 metres tall and up to 90 kilograms, with a bend in its flipper bone.",
  hab=["coast", "shelf"], cls=(AV, "Sphenisciformes", "Spheniscidae"))

# ================================================================== OLIGOCENE
E("Hoplophoneus", "genus", "land", "sabertooth", 38, 28, ["na-w"],
  "A leopard-sized nimravid 'false sabre-tooth', with a bony flange on its jaw to guard its long canines.",
  cls=(MA, "Carnivora", "Nimravidae"))
E("Archaeotherium", "genus", "land", "entelodont", 38, 28, ["na-w"],
  "A cow-sized entelodont, a 'hell pig' of the Oligocene plains; bite marks show it stored the carcasses of early camels to eat later.",
  cls=(MA, "Artiodactyla", "Entelodontidae"))
E("Poebrotherium", "genus", "land", "camel", 38, 30, ["na-w"],
  "A goat-sized early camel of the White River plains -- camels began in North America and stayed there for 35 million years.",
  cls=(MA, "Artiodactyla", "Camelidae"))
E("Leptomeryx", "genus", "land", "deer", 38, 26, ["na-w"],
  "A small, hornless ruminant like a chevrotain, one of the commonest mammals of the Oligocene plains of North America.",
  cls=(MA, "Artiodactyla", "Leptomerycidae"))
E("Subhyracodon", "genus", "land", "rhino", 36, 30, ["na-w"],
  "A hornless, cow-sized rhinoceros of the White River plains -- North America had rhinos of its own until five million years ago.",
  cls=(MA, "Perissodactyla", "Rhinocerotidae"))
E("Hyracodon", "genus", "land", "rhino", 38, 30, ["na-w"],
  "A long-legged 'running rhinoceros', pony-sized and hornless, built for speed on the open Oligocene plains.",
  cls=(MA, "Perissodactyla", "Hyracodontidae"))
E("Palaeolagus", "genus", "land", "rabbit", 38, 26, ["na-w"],
  "An early rabbit of the White River beds, already almost modern -- the rabbit body plan has barely changed in 35 million years.",
  cls=(MA, "Lagomorpha", "Leporidae"))
E("Stylemys", "genus", "land", "tortoise", 38, 28, ["na-w"],
  "A land tortoise of the Oligocene plains, common enough that its shells weather out of the White River badlands by the hundred.",
  cls=("Reptilia", "Testudines", "Testudinidae"))
E("Wakaleo", "genus", "land", "marsupiallion", 23, 12, ["au-e"],
  "A dog-sized marsupial lion of the Miocene rainforests of Queensland, with blade-like premolars for slicing meat.",
  cls=(MA, "Diprotodontia", "Thylacoleonidae"))
E("Nambaroo", "genus", "land", "kangaroo", 25, 15, ["au-e"],
  "A small early kangaroo that probably bounded on all fours rather than hopping on two feet.",
  cls=(MA, "Diprotodontia", "Balbaridae"))
E("Ekaltadeta", "genus", "land", "kangaroo", 25, 15, ["au-e"],
  "A 'killer kangaroo': a rat-kangaroo relative with serrated slicing premolars, probably an omnivore that took small animals.",
  cls=(MA, "Diprotodontia", "Hypsiprymnodontidae"))
E("Litokoala", "genus", "land", "koala", 25, 12, ["au-e"],
  "An early koala of the Miocene rainforests, smaller than today's and with a less specialised diet.",
  hab=["forest", "rainforest"], cls=(MA, "Diprotodontia", "Phascolarctidae"))

# ================================================================== TREES
E("Glyptostrobus", "genus", "land", "conifer", 70, 0,
  [T(70, 2.6, "na", "eu", "as-n", "as-ne", "as-s", "gl"), T(2.6, 0, "as-s", "as-ic")],
  "The Chinese swamp cypress. In the Paleocene and Eocene it lined swamps and coal-forming mires across the northern continents; today a few hundred wild trees survive in southern China, Vietnam and Laos.",
  hab=["wetland", "river", "lake", "forest"], box=NOW([104, 120, 18, 27]),
  cls=("Pinopsida", "Pinales", "Cupressaceae"))
E("Taxodium", "genus", "land", "conifer", 65, 0,
  [T(65, 5.3, "na", "eu", "as-n", "as-ne", "gl"), T(5.3, 0, "na-e", "na-w", "ca")],
  "The bald cypress, whose buttressed trunks and 'knees' stand in swamp water. In the Paleogene it grew across the northern continents; today only in the south-eastern United States and Mexico.",
  hab=["wetland", "river", "lake"], box=NOW([-100, -74, 24, 40.5], [-110, -95, 14, 30]),
  cls=("Pinopsida", "Pinales", "Cupressaceae"))
E("Liquidambar", "genus", "land", "broadleaf", 50, 0,
  [T(50, 2.6, "na", "eu", "as-ne", "as-s", "as-w"), T(2.6, 0, "na-e", "ca", "as-s", "as-w")],
  "Sweetgums, star-leaved trees that spread across the northern continents in the Paleogene; the ice ages cut them back to three refuges -- eastern North America, south-west Turkey and southern China.",
  hab=["forest"], box=NOW([-98, -73, 14, 41], [26, 32, 36, 38.5], [98, 122, 20, 34]),
  cls=("Magnoliopsida", "Saxifragales", "Altingiaceae"))
E("Sabal", "genus", "land", "palm", 66, 0,
  [T(66, 5.3, "na", "eu", "ca"), T(5.3, 0, "na-e", "ca")],
  "Palmettos: fan palms that grew in the Eocene as far north as southern England and the Pacific Northwest; today they reach only the south-eastern United States, Mexico and the Caribbean.",
  lat=[{"t": [66, 34], "lat": [0, 60]}, {"t": [34, 0], "lat": [0, 37]}],
  box=NOW([-100, -75, 14, 36.5], [-86, -60, 10, 24]), cls=("Liliopsida", "Arecales", "Arecaceae"))
E("Cinnamomum", "genus", "land", "broadleaf", 60, 0,
  [T(60, 5.3, "na", "eu", "as"), T(5.3, 0, "as-s", "as-ic", "as-sb", "in", "as-ne")],
  "Cinnamon and camphor laurels, whose three-veined leaves are among the commonest fossils of the warm Paleogene and Miocene forests of Europe and North America; today they grow wild only in tropical and subtropical Asia.",
  hab=["forest", "rainforest"], lat=[{"t": [60, 5.3], "lat": [0, 60]}, {"t": [5.3, 0], "lat": [0, 36]}],
  box=NOW([68, 146, -10, 36]), cls=("Magnoliopsida", "Laurales", "Lauraceae"))

write("x-paleogene-regional.json")
