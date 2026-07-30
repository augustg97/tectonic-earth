"""Biomes, life through time, and the regional fossil record.

The app showed tectonics and climate and said nothing about what was living in
any of it, which for most of this timeline is the more interesting half. Three
layers land here:

  BIOMES    - what kinds of environment existed at a given age, in rough order
              of global extent, using terms that are not anachronistic. Before
              land plants the terrestrial "biomes" are microbial crust and bare
              regolith; grassland does not appear until the Cenozoic.
  LIFE      - per geological interval: a summary, a handful of representative
              taxa at whatever rank is actually informative for that time, and
              what first appeared or died out.
  REGIONAL  - what the fossil record of a particular landmass shows at a
              particular time, so clicking Gondwana in the Permian tells you
              about Glossopteris and Mesosaurus rather than repeating the
              global summary.

Bulk content lives in life_data.json; this module holds the illustration set
and the logic that binds a taxon name to a drawing.
"""
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "life_data.json")) as _f:
    _DATA = json.load(_f)
with open(os.path.join(_HERE, "life_icons.json")) as _f:
    ICONS = json.load(_f)
# Attribution and licence for every traced silhouette. PhyloPic images are
# individually licensed and the CC-BY ones REQUIRE credit, so this ships to the
# app and is rendered in the About panel. Absent for hand-drawn icons.
_CREDITS_PATH = os.path.join(_HERE, "life_credits.json")
CREDITS = {}
if os.path.exists(_CREDITS_PATH):
    with open(_CREDITS_PATH) as _f:
        CREDITS = json.load(_f)


# Which drawing stands for which taxon. Matched as lowercase substrings against
# the taxon name, FIRST RULE WINS, so the table is ordered specific -> general:
# "Glossopteris" has to be caught by the seed-fern rule before the generic
# "fern" rule sees the same letters.
ICON_RULES = [
    # --- named genera and species, which no group rule would ever catch ---
    ("archaefructus", "flower"), ("azolla", "fern"), ("bangiomorpha", "algae"),
    ("bothriolepis", "placoderm"), ("cameroceras", "nautiloid"),
    ("castorocauda", "mammal"), ("chaohusaurus", "ichthyosaur"),
    ("claraia", "bivalve"), ("cloudina", "worm"), ("enaliarctos", "whale"),
    ("eryops", "temnospondyl"), ("eurypterus", "eurypterid"),
    ("fusulin", "plankton"), ("globigerin", "plankton"),
    ("globotruncan", "plankton"), ("orthocerat", "nautiloid"),
    ("vase-shaped", "plankton"),
    ("hallucigenia", "worm"), ("halysites", "coral"),
    ("helicoprion", "shark"), ("hexactinellid", "sponge"),
    ("hirnantia", "brachiopod"), ("hyneria", "lobefin"),
    ("liopleurodon", "plesiosaur"), ("macrocystis", "algae"),
    ("namacalathus", "sponge"), ("nummulites", "plankton"),
    ("obdurodon", "marsupial"), ("ourasphaira", "fungus"),
    ("placodont", "plesiosaur"), ("pterygotus", "eurypterid"),
    ("rhizodus", "lobefin"), ("rugosa", "coral"),
    ("shonisaurus", "ichthyosaur"), ("tabulata", "coral"),
    ("tanystropheus", "reptile"), ("thalassocnus", "mammal"),
    ("titanoboa", "reptile"), ("tullimonstrum", "worm"), ("wiwaxia", "worm"),
    ("arcellinid", "plankton"),
    ("aegyptopithecus", "primate"), ("araucarioxylon", "conifer"),
    ("baragwanathia", "lycopod"), ("carpolestes", "primate"),
    ("cetiosaurus", "sauropod"), ("coelodonta", "horse"),
    ("cryolophosaurus", "theropod"), ("cynognathus", "cynodont"),
    ("darwinius", "primate"), ("deinotherium", "proboscidean"),
    ("dicynodon", "cynodont"), ("dilophosaurus", "theropod"),
    ("dinocephal", "cynodont"), ("docodont", "rodent"),
    ("edaphosaurus", "synapsid"), ("elkinsia", "seedfern"),
    ("gastornis", "bird"), ("genyornis", "bird"),
    ("gigantopteris", "seedfern"), ("hyracotherium", "horse"),
    ("inostrancevia", "cynodont"), ("marchantiophyt", "moss"),
    ("megacerops", "horse"), ("megalosaurus", "theropod"),
    ("megatherium", "mammal"), ("mesohippus", "horse"),
    ("multituberculat", "rodent"), ("platyrrhin", "primate"),
    ("plesiadapi", "primate"), ("pleuromeia", "lycopod"),
    ("proconsul", "primate"), ("progymnosperm", "broadleaf"),
    ("repenomamus", "mammal"), ("sahelanthropus", "primate"),
    ("scelidosaurus", "stegosaur"), ("seymouria", "tetrapod"),
    ("sinosauropteryx", "theropod"), ("titanis", "bird"),
    ("uintatherium", "mammal"), ("walchia", "conifer"),
    ("wattieza", "fern"), ("zosterophyll", "lycopod"),
    ("anchiornis", "bird"), ("eudimorphodon", "pterosaur"),
    ("icaronycteris", "mammal"), ("microraptor", "theropod"),
    ("ornithocheir", "pterosaur"), ("volaticotherium", "mammal"),
    ("mammuthus", "proboscidean"), ("rhyniognatha", "insect"),
    # --- 2026-07 audit: FLORA that fell back to a reptile icon (realm "land"
    #     covers plants AND animals, so an unmatched plant drew an animal), plus
    #     animals that fell back to a generic reptile. Specific phrases first so
    #     the group rules further down cannot grab them. ---
    ("malvinokaffric flora", "lycopod"), ("malvinokaffric fauna", "trilobite"),
    ("cathaysian", "seedfern"), ("podocarp", "conifer"),
    ("eospermatopteris", "fern"), ("rhynie", "moss"),
    # dinosaurs -> their own body plan, not a lump "reptile"
    ("massospondylus", "sauropod"), ("vulcanodon", "sauropod"),
    ("argentinosaur", "sauropod"), ("paralititan", "sauropod"),
    ("rukwatitan", "sauropod"), ("isisaurus", "sauropod"),
    ("giganotosaur", "theropod"), ("carnotaurus", "theropod"),
    ("carcharodontosaur", "theropod"), ("rajasaurus", "theropod"),
    ("compsognathus", "theropod"), ("ouranosaurus", "hadrosaur"),
    ("edmontosaurus", "hadrosaur"), ("morrosaurus", "hadrosaur"),
    ("antarctopelta", "stegosaur"),
    ("phorusrhac", "bird"), ("palaeeudyptes", "bird"),
    # mammals -> proboscidean / horse / marsupial / carnivore / primate
    ("mammut", "proboscidean"), ("moeritherium", "proboscidean"),
    ("stegodon", "proboscidean"), ("elephas", "proboscidean"),
    ("pyrother", "proboscidean"), ("arsinoither", "mammal"),
    ("eohippus", "horse"), ("propalaeother", "horse"), ("teleoceras", "horse"),
    ("aepycamelus", "mammal"), ("merycoidodon", "mammal"),
    ("entelodont", "mammal"), ("ectoconus", "mammal"), ("cambaytherium", "mammal"),
    ("megalonyx", "mammal"), ("astrapother", "mammal"), ("macrauchenia", "mammal"),
    ("doedicurus", "mammal"), ("notoungulat", "mammal"), ("litoptern", "mammal"),
    ("sparassodont", "carnivore"), ("canis", "carnivore"), ("ursus", "carnivore"),
    ("thylacoleo", "marsupial"), ("macropod", "marsupial"),
    ("procoptodon", "marsupial"), ("nimbadon", "marsupial"),
    ("polydolop", "marsupial"),
    ("sivapithecus", "primate"), ("paranthropus", "primate"),
    ("tritylodont", "cynodont"),
    # Lagerstätten / collective faunas -> a representative organism
    ("tendaguru", "sauropod"), ("morrison fauna", "sauropod"),
    ("jehol", "bird"), ("messel", "mammal"), ("tingamarra", "marsupial"),
    ("chinchilla fauna", "marsupial"),
    # --- marine genera that were drawing a generic FISH: give them their group
    ("agnostus", "trilobite"), ("olenell", "trilobite"), ("paradoxides", "trilobite"),
    ("redlichia", "trilobite"), ("neseuretus", "trilobite"), ("ampyx", "trilobite"),
    ("asaphid", "trilobite"),
    ("clarkeia", "brachiopod"), ("orthida", "brachiopod"),
    ("tropidoleptus", "brachiopod"),
    ("buchia", "bivalve"), ("cucullaea", "bivalve"), ("eurydesma", "bivalve"),
    ("gryphaea", "bivalve"), ("halobia", "bivalve"), ("inoceram", "bivalve"),
    ("posidonia", "bivalve"), ("congeria", "bivalve"), ("dreissena", "bivalve"),
    ("bathymodiolus", "bivalve"), ("calyptogena", "bivalve"),
    ("endocer", "nautiloid"), ("nautilus", "nautiloid"),
    ("placenticeras", "ammonite"), ("ammolite", "ammonite"),
    ("porites", "coral"), ("waagenophyll", "coral"), ("fenestrata", "coral"),
    ("encrinus", "crinoid"), ("pentacrinites", "crinoid"),
    ("monograptus", "graptolite"),
    ("haikouichthys", "jawless"), ("myllokunmingia", "jawless"),
    ("osteostrac", "jawless"), ("cephalaspi", "jawless"),
    ("enchodus", "fish"), ("knightia", "fish"), ("palaeoniscum", "fish"),
    ("xiphactinus", "fish"), ("notothenioid", "fish"), ("osteichthy", "fish"),
    ("latimeria", "lobefin"),
    ("keichousaurus", "plesiosaur"), ("kronosaurus", "plesiosaur"),
    ("platypterygius", "ichthyosaur"), ("tylosaurus", "mosasaur"),
    ("archaeocet", "whale"), ("balaena", "whale"), ("mysticet", "whale"),
    ("sirenia", "whale"), ("ambulocetus", "whale"), ("carcharocles", "shark"),
    ("bacillariophy", "plankton"), ("calpionell", "plankton"),
    ("discoaster", "plankton"), ("nummulit", "plankton"),
    ("euphausiac", "crab"), ("cyprideis", "crab"), ("rimicaris", "crab"),
    ("mesolimulus", "crab"), ("orsten", "crab"),
    ("alvinella", "worm"), ("riftia", "worm"),
    ("pteridinium", "charnia"), ("rangea", "charnia"),
    # freshwater / air strays
    ("carbonemys", "turtle"), ("diplocaulus", "temnospondyl"),
    ("metoposaur", "temnospondyl"), ("melanopsis", "snail"),
    ("purussaurus", "reptile"),
    ("confuciusornis", "bird"), ("hesperornis", "bird"), ("vegavis", "bird"),
    # Lagerstätten -> the organism each is famous for
    ("burgess", "anomalocaris"), ("chengjiang", "anomalocaris"),
    ("emu bay", "trilobite"), ("fezouata", "trilobite"),
    ("doushantuo", "acritarch"), ("luoping", "fish"),
    ("meishan", "brachiopod"), ("sinsk", "sponge"),
    ("small shelly", "snail"), ("dwyka", "bivalve"),
    # --- fungi. Nothing here had a drawing before, because nothing here had a
    #     rule: every fungus in the data fell through to a reptile or a fish.
    ("prototaxites", "prototaxites"), ("ourasphaira", "fungus"),
    ("tortotubus", "fungus"), ("agaricomycet", "fungus"),
    ("agaracites", "fungus"), ("agaricus", "fungus"),
    ("reduviasporonites", "fungus"), ("termitomyces", "fungus"),
    ("armillaria", "fungus"), ("myces", "fungus"), ("mycota", "fungus"),
    # --- trees and other land plants, by name ---
    ("archaeopteris", "broadleaf"), ("callixylon", "broadleaf"),
    ("cordaites", "conifer"), ("psaronius", "fern"),
    ("archaeocalamites", "horsetail"), ("stigmaria", "lycopod"),
    ("aglaophyton", "moss"), ("calamophyton", "fern"),
    ("voltzia", "conifer"), ("walchia", "conifer"),
    ("cheirolepid", "conifer"), ("araucari", "conifer"),
    ("sequoia", "conifer"), ("larix", "conifer"), ("pinaceae", "conifer"),
    ("bennettital", "cycad"), ("cycadeoidea", "cycad"), ("williamsonia", "cycad"),
    ("ginkgoal", "ginkgo"), ("baiera", "ginkgo"),
    ("nypa", "palm"), ("arecaceae", "palm"), ("palmae", "palm"),
    ("mauritia", "palm"),
    ("magnoliopsida", "flower"), ("angiosperm", "flower"),
    ("magnolia", "flower"), ("platanus", "flower"),
    ("eucalyptus", "broadleaf"), ("dipterocarp", "broadleaf"),
    ("betula", "broadleaf"), ("quercus", "broadleaf"), ("acer ", "broadleaf"),
    ("weichselia", "fern"), ("coniopteris", "fern"), ("osmunda", "fern"),
    ("vertebraria", "seedfern"), ("botrychiopsis", "seedfern"),
    ("callipteris", "seedfern"), ("autunia", "seedfern"),
    ("pleuromeia", "lycopod"), ("sigillaria", "lycopod"),
    # --- land invertebrates and small vertebrates that had no rule ---
    ("pneumodesmus", "myriapod"), ("attercopus", "insect"),
    ("spriggina", "worm"), ("castorocauda", "mammal"),
    # --- explicitly named organisms that a generic rule would mis-file ---
    ("glossopteris", "seedfern"), ("pteridosperm", "seedfern"),
    ("dicroidium", "seedfern"), ("medullosa", "seedfern"),
    # Catch-all so a plant can NEVER fall through to the animal fallback: any
    # remaining "<place> flora" / vegetation word is foliage, not a reptile.
    # Placed after the named plants above so those keep their specific drawing.
    ("flora", "seedfern"), ("vegetation", "seedfern"),
    ("woodland", "broadleaf"), ("rainforest", "broadleaf"),
    ("mangrove", "broadleaf"), ("peat", "lycopod"), ("swamp forest", "lycopod"),
    # fungi
    ("mycorrhiz", "fungus"), ("mushroom", "fungus"),
    ("basidiomyc", "fungus"), ("ascomyc", "fungus"), ("myco", "fungus"),
    ("lepidodendr", "lycopod"), ("sigillaria", "lycopod"),
    ("lycopsid", "lycopod"), ("lycophyte", "lycopod"), ("clubmoss", "lycopod"),
    ("calamites", "horsetail"), ("sphenophyt", "horsetail"),
    ("equiset", "horsetail"), ("horsetail", "horsetail"),
    ("prototaxites", "fungus"), ("fung", "fungus"), ("lichen", "fungus"),
    ("cooksonia", "moss"), ("rhynia", "moss"), ("bryophyt", "moss"),
    ("liverwort", "moss"), ("moss", "moss"),
    ("nothofagus", "broadleaf"), ("angiosperm", "flower"),
    ("magnolia", "flower"), ("flowering", "flower"), ("eudicot", "flower"),
    ("poaceae", "grass"), ("grass", "grass"), ("c4 ", "grass"),
    ("palm", "palm"), ("arecac", "palm"),
    ("ginkgo", "ginkgo"), ("cycad", "cycad"), ("bennettit", "cycad"),
    ("araucaria", "conifer"), ("conifer", "conifer"), ("pinac", "conifer"),
    ("cordait", "conifer"), ("voltzia", "conifer"), ("taxod", "conifer"),
    ("fern", "fern"), ("filic", "fern"), ("pteridoph", "fern"),
    ("archaeopteris", "broadleaf"), ("tree", "broadleaf"), ("forest", "broadleaf"),
    # --- microbial / protist ---
    ("stromatolite", "stromatolite"), ("cyanobacter", "stromatolite"),
    ("acritarch", "acritarch"), ("diatom", "plankton"),
    ("coccolith", "plankton"), ("foramin", "plankton"),
    ("radiolar", "plankton"), ("plankton", "plankton"), ("nannofossil", "plankton"),
    ("dinoflagell", "plankton"),
    ("archaea", "microbe"), ("bacteri", "microbe"), ("prokaryot", "microbe"),
    ("eukaryot", "microbe"), ("protist", "microbe"), ("microb", "microbe"),
    ("algae", "algae"), ("algal", "algae"), ("seaweed", "algae"),
    ("rhodophyt", "algae"), ("chlorophyt", "algae"), ("charophyt", "algae"),
    # --- Ediacaran ---
    ("charnia", "charnia"), ("rangeomorph", "charnia"), ("frond", "charnia"),
    ("dickinsonia", "dickinsonia"), ("ediacar", "charnia"),
    ("kimberella", "snail"), ("vendobiont", "dickinsonia"),
    # --- invertebrates ---
    ("trilobit", "trilobite"), ("anomalocar", "anomalocaris"),
    ("radiodont", "anomalocaris"), ("opabinia", "anomalocaris"),
    ("eurypterid", "eurypterid"), ("sea scorpion", "eurypterid"),
    ("brachiopod", "brachiopod"), ("lingul", "brachiopod"),
    ("productid", "brachiopod"), ("spirifer", "brachiopod"),
    ("rudist", "bivalve"), ("bivalv", "bivalve"), ("pelecypod", "bivalve"),
    ("inoceramus", "bivalve"), ("oyster", "bivalve"), ("mussel", "bivalve"),
    ("ammonoid", "ammonite"), ("ammonit", "ammonite"), ("goniatit", "ammonite"),
    ("ceratit", "ammonite"), ("baculit", "ammonite"),
    ("nautiloid", "nautiloid"), ("orthocon", "nautiloid"),
    ("endocerid", "nautiloid"), ("belemnit", "nautiloid"),
    ("cephalopod", "ammonite"),
    ("gastropod", "snail"), ("snail", "snail"), ("ammonium", "snail"),
    ("crinoid", "crinoid"), ("blastoid", "crinoid"), ("echinoderm", "crinoid"),
    ("echinoid", "crinoid"), ("sea urchin", "crinoid"), ("starfish", "crinoid"),
    ("graptolit", "graptolite"), ("conodont", "jawless"),
    ("rugose", "coral"), ("tabulate", "coral"), ("scleractin", "coral"),
    ("coral", "coral"), ("stromatoporoid", "reef"), ("reef", "reef"),
    ("archaeocyath", "sponge"), ("sponge", "sponge"), ("porifer", "sponge"),
    ("jellyfish", "jellyfish"), ("cnidar", "jellyfish"), ("medusa", "jellyfish"),
    ("scyphozo", "jellyfish"),
    ("bryozoa", "coral"), ("crustac", "crab"), ("ostracod", "crab"),
    ("decapod", "crab"), ("crab", "crab"), ("shrimp", "crab"),
    ("arthropleura", "myriapod"), ("myriapod", "myriapod"),
    ("millipede", "myriapod"), ("centipede", "myriapod"),
    ("meganeura", "insect"), ("insect", "insect"), ("odonat", "insect"),
    ("dragonfly", "insect"), ("hymenopter", "insect"), ("coleopter", "insect"),
    ("beetle", "insect"), ("hexapod", "insect"), ("bee", "insect"),
    ("arachnid", "insect"), ("trigonotarb", "insect"), ("spider", "insect"),
    ("annelid", "worm"), ("worm", "worm"), ("polychaet", "worm"),
    ("mollusc", "snail"),
    # --- fish ---
    ("placoderm", "placoderm"), ("dunkleosteus", "placoderm"),
    ("ostracoderm", "jawless"), ("agnath", "jawless"), ("jawless", "jawless"),
    ("lamprey", "jawless"), ("hagfish", "jawless"), ("cephalaspid", "jawless"),
    ("shark", "shark"), ("chondrichth", "shark"), ("selachi", "shark"),
    ("megalodon", "shark"), ("ray", "shark"),
    ("tiktaalik", "lobefin"), ("sarcopterygi", "lobefin"),
    ("coelacanth", "lobefin"), ("lobe-fin", "lobefin"), ("lungfish", "lobefin"),
    ("eusthenopteron", "lobefin"), ("panderichthys", "lobefin"),
    ("actinopterygi", "fish"), ("teleost", "fish"), ("ray-finned", "fish"),
    ("acanthod", "fish"), ("fish", "fish"), ("pikaia", "fish"),
    ("chordate", "fish"), ("vertebrate", "fish"),
    # --- tetrapods ---
    ("ichthyostega", "tetrapod"), ("acanthostega", "tetrapod"),
    ("temnospondyl", "temnospondyl"), ("labyrinthodont", "temnospondyl"),
    ("amphibian", "temnospondyl"), ("lissamphib", "temnospondyl"),
    ("frog", "temnospondyl"), ("salamander", "temnospondyl"),
    ("tetrapod", "tetrapod"),
    ("dimetrodon", "synapsid"), ("pelycosaur", "synapsid"),
    ("cynodont", "cynodont"), ("therapsid", "cynodont"),
    ("dicynodont", "cynodont"), ("gorgonops", "cynodont"),
    ("lystrosaurus", "cynodont"), ("synapsid", "synapsid"),
    ("mesosaurus", "reptile"), ("archosaur", "reptile"),
    ("crocodyl", "reptile"), ("crocodile", "reptile"), ("phytosaur", "reptile"),
    ("lepidosaur", "reptile"), ("squamat", "reptile"), ("lizard", "reptile"),
    ("snake", "reptile"), ("rhynchosaur", "reptile"), ("diapsid", "reptile"),
    ("amniote", "reptile"), ("reptil", "reptile"), ("hylonomus", "reptile"),
    ("turtle", "turtle"), ("testudin", "turtle"), ("chelon", "turtle"),
    ("ichthyosaur", "ichthyosaur"), ("plesiosaur", "plesiosaur"),
    ("pliosaur", "plesiosaur"), ("elasmosaur", "plesiosaur"),
    ("mosasaur", "mosasaur"), ("nothosaur", "plesiosaur"),
    ("pterosaur", "pterosaur"), ("pterodactyl", "pterosaur"),
    ("quetzalcoatlus", "pterosaur"), ("rhamphorhynch", "pterosaur"),
    # --- dinosaurs ---
    ("tyrannosaur", "theropod"), ("theropod", "theropod"),
    ("velociraptor", "theropod"), ("allosaur", "theropod"),
    ("spinosaur", "theropod"), ("coelophys", "theropod"),
    ("eoraptor", "theropod"), ("herrerasaur", "theropod"),
    ("sauropod", "sauropod"), ("diplodoc", "sauropod"),
    ("brachiosaur", "sauropod"), ("titanosaur", "sauropod"),
    ("apatosaur", "sauropod"), ("prosauropod", "sauropod"),
    ("plateosaur", "sauropod"),
    ("triceratops", "ceratopsian"), ("ceratops", "ceratopsian"),
    ("protoceratops", "ceratopsian"),
    ("stegosaur", "stegosaur"), ("ankylosaur", "stegosaur"),
    ("hadrosaur", "hadrosaur"), ("iguanodon", "hadrosaur"),
    ("ornithopod", "hadrosaur"), ("ornithisch", "hadrosaur"),
    ("dinosaur", "theropod"), ("saurisch", "sauropod"),
    # --- birds and mammals ---
    ("archaeopteryx", "bird"), ("avian", "bird"), ("bird", "bird"),
    ("penguin", "bird"), ("aves", "bird"), ("enantiornith", "bird"),
    ("mammoth", "proboscidean"), ("proboscid", "proboscidean"),
    ("elephant", "proboscidean"), ("mastodon", "proboscidean"),
    ("gomphother", "proboscidean"),
    ("equus", "horse"), ("equid", "horse"), ("horse", "horse"),
    ("hipparion", "horse"), ("merychippus", "horse"),
    ("perissodactyl", "horse"), ("rhino", "horse"), ("brontother", "horse"),
    ("indricother", "horse"), ("paraceratherium", "horse"),
    ("whale", "whale"), ("cetacea", "whale"), ("basilosaurus", "whale"),
    ("pakicetus", "whale"), ("dolphin", "whale"), ("pinniped", "whale"),
    ("smilodon", "carnivore"), ("sabertooth", "carnivore"),
    ("sabre-tooth", "carnivore"), ("carnivor", "carnivore"),
    ("creodont", "carnivore"), ("felid", "carnivore"), ("canid", "carnivore"),
    ("bear", "carnivore"), ("hyaenodon", "carnivore"),
    ("diprotodon", "marsupial"), ("marsupial", "marsupial"),
    ("metatheri", "marsupial"), ("kangaroo", "marsupial"),
    ("thylacin", "marsupial"), ("monotrem", "marsupial"),
    ("homo ", "primate"), ("australopith", "primate"), ("hominin", "primate"),
    ("hominid", "primate"), ("primate", "primate"), ("ape", "primate"),
    ("human", "primate"), ("purgatorius", "primate"), ("lemur", "primate"),
    ("rodent", "rodent"), ("glires", "rodent"), ("lagomorph", "rodent"),
    ("multituberc", "rodent"), ("morganucodon", "rodent"),
    ("artiodactyl", "mammal"), ("ruminant", "mammal"), ("bovid", "mammal"),
    ("ungulate", "mammal"), ("condylarth", "mammal"), ("notoungulate", "mammal"),
    ("placental", "mammal"), ("eutheri", "mammal"), ("mammal", "mammal"),
    ("megafauna", "proboscidean"), ("sloth", "mammal"), ("glyptodon", "mammal"),
]

# Rank alone is a decent last resort: a "kingdom" called Plantae should not
# fall back to a generic animal.
RANK_FALLBACK = {"sea": "fish", "land": "reptile", "air": "bird",
                 "fresh": "fish"}


# Rules that are MEANT to match inside a word. Everything else must match at a
# word start, because a bare substring test does not know the difference between
# "Ceratites" and "OrthoCERATITe", or between a canid and GlobotrunCANIDae --
# which is how a Cretaceous planktonic foraminifer came to be drawn as a fox.
INFIX_OK = {"sequoia", "agaracites", "fusulin", "myces", "mycota", "myco",
            "basidiomyc", "ascomyc", "mycorrhiz", "graptus", "pteris",
            "phyt", "saur", "cerat"}


def _rule_hits(key, n):
    """Does this rule match the taxon name? At a word start unless allowed."""
    i = n.find(key)
    if i < 0:
        return False
    if key in INFIX_OK:
        return True
    while i >= 0:
        if i == 0 or not n[i - 1].isalpha():
            return True
        i = n.find(key, i + 1)
    return False


def taxon_key(name):
    """The per-taxon icon key, if this taxon has a silhouette of its own."""
    return "t:" + re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


def icon_for(name, realm="sea"):
    """The illustration key for a taxon name.

    Most specific first: a silhouette traced for THIS taxon beats the group
    drawing, which is the whole point of fetching them -- Triceratops should
    not share a picture with every other ceratopsian. Then the group rules,
    then the per-realm fallback.
    """
    own = taxon_key(name)
    if own in ICONS:
        return own
    n = (name or "").lower()
    for key, icon in ICON_RULES:
        if _rule_hits(key, n):
            return icon
    return RANK_FALLBACK.get(realm, "microbe")


def credits():
    """Only the credits actually referenced by an icon in the build."""
    return CREDITS


def biomes():
    return _DATA["biomes"]


def life():
    """Per-interval life, with an illustration bound to every taxon."""
    out = []
    for e in _DATA["life"]:
        taxa = []
        for t in e["taxa"]:
            win = None
            if isinstance(t, (list, tuple)):
                if len(t) >= 5:
                    name, rank, realm, note, win = t[0], t[1], t[2], t[3], t[4]
                else:
                    name, rank, realm, note = t
            else:
                name, rank, realm, note = (t["name"], t["rank"], t["realm"], t["note"])
                win = t.get("win")
            rec = {"n": name, "r": rank, "realm": realm, "note": note,
                   "ic": icon_for(name, realm)}
            # Optional per-taxon age window [appear, disappear], TIGHTER than the
            # interval -- so Homo sapiens can sit inside the 2.58-Myr Quaternary
            # but only show for its real last 0.3 Myr, and only where the record
            # puts it. The app hides the taxon outside this.
            if win:
                rec["w"] = [max(win), min(win)]
            taxa.append(rec)
        out.append({"interval": e["interval"], "a0": e["a0"], "a1": e["a1"],
                    "summary": e["summary"], "taxa": taxa,
                    "first": e.get("first_appearances", []),
                    "ext": e.get("extinctions", [])})
    return out


def regional():
    return _DATA.get("regional", {})


def region_taxa():
    """Per-place, per-interval characteristic biota, with icons bound.

    Clicking any two features at the same age used to show the same four
    organisms, because there was only ever one global list. This is what makes
    Permian Gondwana show Glossopteris and Mesosaurus while Permian Siberia
    does not. Realm is enforced on the way out: a marine region may only carry
    marine taxa, which is the defect this exists to fix.
    """
    out = {}
    for region, spans in _DATA.get("region_taxa", {}).items():
        marine = region in MARINE_REGIONS
        rows = []
        for s in spans:
            taxa = []
            for t in s.get("taxa", []):
                name, rank, realm, note = (
                    t if isinstance(t, (list, tuple))
                    else (t["name"], t["rank"], t["realm"], t["note"]))
                if marine and realm != "sea":
                    print(f"  WARNING dropped {realm} taxon {name!r} "
                          f"from marine region {region!r}")
                    continue
                taxa.append({"n": name, "r": rank, "realm": realm,
                             "note": note, "ic": icon_for(name, realm)})
            if taxa:
                # `exception` says this locality is atypical FOR ITS PROVINCE and
                # the province model must never speak over it -- Solnhofen, the
                # Zechstein, the Nama Sea, the Messinian salt basin, Lake Pannon,
                # the two ridge-vent faunas. Everything else is province-typical,
                # so the model owns the claim about WHICH province and the
                # curated list supplies the detail inside it.
                # modeling/audit_curated_biota.py classifies all 198 spans and is
                # the check that a new curated entry declares itself.
                rows.append({"a0": s["a0"], "a1": s["a1"], "taxa": taxa,
                             **({"shared": s["shared"]} if s.get("shared") else {}),
                             **({"exception": True} if s.get("exception") else {})})
        if rows:
            out[region] = rows
    return out


def sparse():
    return _DATA.get("sparse", {})


# Anything named here may only ever carry realm="sea" taxa. NOTE deliberately
# absent: Solnhofen Lagoon and Hudson Seaway (their key fossils are the birds /
# pterosaurs / dinosaurs they preserved), and Lake Pannon (brackish, endemic
# freshwater molluscs) — realm-locking those would strip exactly what makes them
# worth naming.
MARINE_REGIONS = {
    "Panthalassa", "Panthalassic Ocean", "Panthalassic (proto)", "Iapetus Ocean",
    "Rheic Ocean", "Tethys Ocean", "Paleo-Tethys", "Mirovia", "Pacific Ocean",
    "Atlantic Ocean", "Indian Ocean", "Southern Ocean", "Arctic Ocean",
    "Mediterranean", "Mediterranean (closing)", "Western Interior Seaway",
    "Sauk Sea", "Zechstein Sea", "Turgai Strait", "Eromanga Sea", "Paratethys",
    "Mozambique Ocean", "Adamastor Ocean", "Ural Ocean", "Tornquist Sea",
    "Neo-Panthalassa", "Sundance Sea", "Trans-Saharan Sea",
    "Central American Sea", "East African Ocean",
    # marine features added 2026-07 to end the "every ocean shows the same fauna"
    "Muschelkalk Sea", "Mowry Sea", "Boreal Sea", "Bearpaw Sea", "Neotethys",
    "Nama Sea", "Tippecanoe Sea", "Kaskaskia Sea", "Absaroka Sea",
    "Messinian Salt Basin", "West Siberian Sea", "South China Sea", "Tasman Sea",
    "Gulf of Mexico", "Mid-Atlantic Ridge", "East Pacific Rise", "Cannonball Sea",
    "Viking Corridor", "Hispanic Corridor",
}


def icons():
    return ICONS


def biomes_at(age):
    """Biomes for the nearest sampled age."""
    if not _DATA["biomes"]:
        return []
    best = min(_DATA["biomes"], key=lambda b: abs(b["age"] - age))
    return best["biomes"]


if __name__ == "__main__":
    miss = {}
    for e in life():
        for t in e["taxa"]:
            if t["ic"] in ("fish", "reptile", "bird", "microbe"):
                # only flag when the name itself never matched a rule
                if not any(k in t["n"].lower() for k, _ in ICON_RULES):
                    miss.setdefault(t["ic"], []).append(t["n"])
    print("intervals:", len(life()), " biome samples:", len(biomes()),
          " regions:", len(regional()), " icons:", len(ICONS))
    for k, v in miss.items():
        print(f"  fell through to {k}: {sorted(set(v))}")


# --------------------------------------------------------------- endemism --
#: Taxa in the GLOBAL per-interval list that were NOT global. The global list is
#: what the app falls back to when a clicked landmass has no biota of its own,
#: and without this it will happily list Proconsul -- an African ape -- under
#: North America, which is what it did. Tagging the clear cases lets the
#: fallback drop anything that plainly did not live there.
#:
#: Only unambiguous restrictions are listed. A taxon absent from here is treated
#: as unrestricted, which is the safe default: over-filtering would silently
#: hide real animals, and the fallback already announces itself as a global list.
ENDEMIC = {
    # Hominins and other post-Cretaceous land taxa that were NOT global.
    # Homo erectus is the one that was reported: it was being listed for a Lake
    # Titicaca card at 1 Ma, and it never reached the Americas -- no hominin did
    # until Homo sapiens, around 20,000 years ago. The taxon carried an age
    # window and no region, and an unrestricted entry is shown everywhere the
    # age matches, so "when" was right and "where" was unconstrained.
    "Homo erectus": {"af", "as", "eu"},
    "Paranthropus boisei": {"af"},
    "Armillaria ostoyae": {"na"},          # one clone, in Oregon
    # Homo sapiens reached everywhere, but not at once, and the entry's own note
    # already says the map should not show it before it arrived.
    "Homo sapiens": {"af", "as", "eu", "au", "na", "sa"},
    "Metasequoia": {"as", "na", "eu"},     # northern-hemisphere dawn redwood
    "Multituberculata": {"na", "eu", "as"},
    "Condylarthra": {"na", "eu", "as"},
    "Plesiadapiformes": {"na", "eu"},
    "Nypa": {"as", "au"},                  # mangrove palm, Indo-Pacific
    "Hipparion": {"na", "eu", "as", "af"},  # never South America or Australia
    # Africa
    "Proconsul": {"af"}, "Sahelanthropus tchadensis": {"af"},
    "Aegyptopithecus": {"af"}, "Australopithecus afarensis": {"af"},
    "Homo habilis": {"af"}, "Deinotherium": {"af", "eu", "as"},
    # South America
    "Megatherium": {"sa"}, "Glyptodon": {"sa"}, "Titanoboa cerrejonensis": {"sa"},
    "Platyrrhini": {"sa"}, "Titanis walleri": {"sa", "na"},
    "Phorusrhacos longissimus": {"sa"}, "Macrauchenia patachonica": {"sa"},
    "Pyrotherium": {"sa"}, "Doedicurus clavicaudatus": {"sa"},
    "Cladosictis patagonica": {"sa"}, "Toxodon": {"sa"},
    # North America
    "Megacerops": {"na"}, "Mesohippus": {"na"}, "Uintatherium": {"na"},
    "Smilodon": {"na", "sa"}, "Smilodon fatalis": {"na", "sa"},
    "Aepycamelus giraffinus": {"na"}, "Merychippus insignis": {"na"},
    "Teleoceras proterum": {"na"}, "Hyracotherium": {"na", "eu"},
    "Icaronycteris": {"na"}, "Carpolestes": {"na"},
    # Australia and New Guinea
    "Diprotodon": {"au"}, "Diprotodon optatum": {"au"},
    "Thylacoleo carnifex": {"au"}, "Obdurodon": {"au"},
    "Varanus priscus": {"au"}, "Genyornis newtoni": {"au"},
    "Procoptodon goliah": {"au"}, "Nimbadon lavarackorum": {"au"},
    "Macropus fuliginosus": {"au"},
    # Eurasia
    "Coelodonta antiquitatis": {"eu", "as"},
    "Mammuthus primigenius": {"na", "eu", "as"}, "Mammuthus": {"na", "eu", "as", "af"},
"Megaloceros giganteus": {"eu", "as"},
    "Ursus spelaeus": {"eu"}, "Panthera spelaea": {"na", "eu", "as"},
    "Gastornis": {"na", "eu"}, "Hyaenodon horridus": {"na"},
    "Basilosaurus isis": {"af"}, "Pakicetus attocki": {"as"},
    "Ambulocetus natans": {"as"}, "Aegyptopithecus": {"af"}, "Paraceratherium": {"as", "eu"},
    "Darwinius masillae": {"eu"}, "Homo neanderthalensis": {"eu", "as"},
    "Elephas maximus": {"as"}, "Mammut americanum": {"na"},
    # Southern-hemisphere plants
    "Nothofagus": {"sa", "au", "an"},
    "Sequoiadendron giganteum": {"na"},
}

#: Broad region tags for the LANDMASS labels the app can show a card for. Deep
#: time makes this fuzzy on purpose -- a Palaeozoic continent is not a modern
#: one -- so only names with an unambiguous modern descendant are mapped, and
#: anything unmapped skips the filter entirely.
LABEL_REGION = {
    "North America": {"na"}, "Laurentia": {"na"}, "Laurussia (Euramerica)": {"na", "eu"},
    "South America": {"sa"}, "Amazonia": {"sa"}, "Patagonia": {"sa"},
    "Africa": {"af"}, "Congo Craton": {"af"}, "Kalahari Craton": {"af"},
    "West Africa Craton": {"af"}, "Sao Francisco Craton": {"sa"},
    "Eurasia": {"eu", "as"}, "Europe": {"eu"}, "Baltica": {"eu"},
    "Siberia": {"as"}, "North China": {"as"}, "South China": {"as"},
    "India": {"as"}, "Greater India": {"as"},
    "Australia": {"au"}, "Sahul": {"au"}, "Zealandia": {"au"},
    "Antarctica": {"an"}, "Australia-East Antarctica": {"au", "an"},
}


def endemic(name):
    """Region tags a taxon is restricted to, or None if unrestricted."""
    return sorted(ENDEMIC.get(name, [])) or None


def label_region(name):
    return sorted(LABEL_REGION.get(name, [])) or None
