"""Replace the hand-drawn icons with real traced silhouettes, and give as many
individual taxa as possible their own.

Two passes:

  GROUPS   - the 68 existing icon keys, each mapped to the taxon whose
             silhouette should stand for it. "theropod" fetches Tyrannosaurus,
             "placoderm" fetches Dunkleosteus, "lycopod" fetches Lepidodendron.
             A hand-drawn icon is kept wherever PhyloPic has nothing usable, or
             where the subject is not an organism at all -- a reef is an
             assemblage and a stromatolite is a sedimentary structure, and
             neither has a silhouette to trace.

  TAXA     - every distinct taxon name in life_data.json, looked up directly.
             Where PhyloPic has it, that taxon gets its OWN drawing under a
             "t:" key, so Triceratops stops sharing a picture with every other
             ceratopsian and Glossopteris stops sharing one with every other
             seed fern. Where it does not, the taxon falls back to its group.

Both passes record attribution and licence per image into life_credits.json.
Silhouettes are only accepted under CC0, Public Domain Mark, or CC-BY (see
phylopic.py); CC-BY-SA and CC-BY-NC are refused.

Run:  python3 build_silhouettes.py [groups|taxa|all]
Then: python3 -c "import build_webdata as b; b.build_life()"
"""
import json
import os
import re
import sys

import phylopic

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")
CREDITS = os.path.join(HERE, "life_credits.json")
DATA = os.path.join(HERE, "life_data.json")
HANDDRAWN = os.path.join(HERE, "life_icons_handdrawn.json")

# icon key -> taxa to try, in order. First one that resolves wins.
GROUP_TERMS = {
    "acritarch":    [],                       # no silhouette to trace
    "algae":        ["Fucus", "Laminaria", "Sargassum", "Phaeophyceae"],
    "ammonite":     ["Dactylioceras", "Perisphinctes", "Hoploscaphites",
                     "Placenticeras", "Ammonoidea", "Ammonitida", "Baculites",
                     "Ceratites", "Goniatites"],
    "anomalocaris": ["Anomalocaris"],
    "bird":         ["Aves", "Corvus"],
    "bivalve":      ["Pecten", "Mytilus", "Inoceramus", "Bivalvia"],
    "brachiopod":   ["Terebratulida", "Spiriferida", "Productida", "Lingula"],
    "broadleaf":    ["Quercus", "Acer", "Magnoliopsida"],
    "carnivore":    ["Canis lupus", "Carnivora", "Panthera"],
    "ceratopsian":  ["Triceratops", "Ceratopsidae"],
    "charnia":      ["Charnia", "Rangea", "Charniodiscus"],
    "conifer":      ["Picea", "Pinus", "Pinophyta"],
    "coral":        ["Acropora", "Scleractinia", "Anthozoa"],
    "crab":         ["Brachyura", "Cancer pagurus"],
    "crinoid":      ["Crinoidea", "Encrinus", "Pentacrinites", "Antedon"],
    "cycad":        ["Cycas", "Cycadales"],
    "cynodont":     ["Thrinaxodon", "Cynodontia"],
    "dickinsonia":  ["Dickinsonia"],
    "eurypterid":   ["Pterygotus", "Eurypterida", "Eurypterus"],
    "fern":         ["Pteridium", "Polypodiopsida", "Osmunda"],
    "fish":         ["Actinopterygii", "Perca"],
    "flower":       ["Helianthus", "Magnolia", "Rosa", "Magnoliophyta"],
    "fungus":       ["Agaricus", "Amanita", "Fungi"],
    "ginkgo":       ["Ginkgo biloba", "Ginkgo"],
    "graptolite":   ["Didymograptus", "Monograptus", "Graptolithina"],
    "grass":        ["Poaceae", "Zea mays"],
    "hadrosaur":    ["Parasaurolophus", "Edmontosaurus", "Hadrosauridae"],
    "horse":        ["Equus", "Equus ferus caballus"],
    "horsetail":    ["Equisetum"],
    "ichthyosaur":  ["Ichthyosaurus", "Ophthalmosaurus", "Ichthyosauria"],
    "insect":       ["Odonata", "Insecta", "Anisoptera"],
    "jawless":      ["Cephalaspis", "Osteostraci", "Petromyzon"],
    "jellyfish":    ["Chrysaora", "Cyanea", "Scyphozoa", "Aurelia"],
    "lobefin":      ["Eusthenopteron", "Latimeria", "Sarcopterygii"],
    "lycopod":      ["Lepidodendron", "Lycopodium"],
    "mammal":       ["Didelphis", "Mammalia"],
    "marsupial":    ["Macropus", "Thylacinus", "Vombatus", "Diprotodon", "Notoryctes"],
    "microbe":      [],                       # no silhouette to trace
    "mosasaur":     ["Mosasaurus", "Tylosaurus", "Mosasauridae"],
    "moss":         ["Polytrichum", "Sphagnum", "Bryophyta"],
    "myriapod":     ["Arthropleura", "Myriapoda", "Scolopendra"],
    "nautiloid":    ["Orthoceras", "Cameroceras", "Endoceras", "Nautilus"],
    "palm":         ["Cocos nucifera", "Arecaceae"],
    "placoderm":    ["Dunkleosteus", "Bothriolepis", "Placodermi"],
    "plankton":     ["Globigerina", "Radiolaria", "Nummulites", "Foraminifera"],
    "plesiosaur":   ["Plesiosaurus", "Elasmosaurus", "Plesiosauria"],
    "primate":      ["Gorilla", "Primates", "Pan troglodytes"],
    "proboscidean": ["Mammuthus", "Loxodonta", "Proboscidea"],
    "prototaxites": ["Prototaxites"],
    "pterosaur":    ["Pteranodon", "Pterosauria", "Rhamphorhynchus"],
    "reef":         [],                       # an assemblage, not an organism
    "reptile":      ["Varanus", "Lacertilia", "Squamata"],
    "rodent":       ["Mus musculus", "Rodentia"],
    "sauropod":     ["Brachiosaurus", "Diplodocus", "Sauropoda"],
    "seedfern":     ["Glossopteris", "Dicroidium", "Medullosa", "Pteridospermatophyta"],
    "shark":        ["Carcharodon carcharias", "Selachimorpha"],
    "snail":        ["Helix", "Conus", "Gastropoda"],
    "sponge":       ["Demospongiae", "Porifera", "Hexactinellida"],
    "stegosaur":    ["Stegosaurus", "Stegosauria"],
    "stromatolite": [],                       # a sedimentary structure
    "synapsid":     ["Dimetrodon", "Synapsida"],
    "temnospondyl": ["Eryops", "Mastodonsaurus", "Temnospondyli", "Metoposaurus"],
    "tetrapod":     ["Ichthyostega", "Acanthostega"],
    "theropod":     ["Tyrannosaurus", "Allosaurus", "Theropoda"],
    "trilobite":    ["Trilobita", "Olenellus"],
    "turtle":       ["Testudines", "Chelonia mydas"],
    "whale":        ["Balaenoptera", "Physeter", "Megaptera", "Cetacea"],
    "worm":         ["Annelida", "Riftia", "Polychaeta"],
}

# Names in the data that are not taxa -- assemblages, floral provinces,
# Lagerstaetten. Never worth a lookup; they keep their group icon.
NOT_A_TAXON = re.compile(
    r"\b(biota|fauna|flora|lagerst|shale|chert|reef|sea|beds?|forest|"
    r"grassland|swamp|rainforest|vegetation|province|amber|corridor)\b", re.I)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def taxa_names():
    d = json.load(open(DATA))
    names = set()
    for e in d.get("life", []):
        for t in e["taxa"]:
            names.add(t[0] if isinstance(t, list) else t["name"])
    for spans in d.get("region_taxa", {}).values():
        for s in spans:
            for t in s["taxa"]:
                names.add(t[0] if isinstance(t, list) else t["name"])
    return sorted(names)


def search_terms(name):
    """What to ask PhyloPic for. A binomial also gets tried as its genus, and
    a parenthetical qualifier -- 'Poaceae (C4 grasses)' -- is dropped."""
    base = re.sub(r"\s*\([^)]*\)", "", name).strip()
    terms = [base]
    parts = base.split()
    if len(parts) >= 2 and parts[0][:1].isupper():
        terms.append(parts[0])
    return [t for i, t in enumerate(terms) if t and t not in terms[:i]]


def run(do_groups, do_taxa):
    build = phylopic.build_number()
    print(f"PhyloPic build {build}")
    icons = load(ICONS, {})
    credits = load(CREDITS, {})

    # Keep an untouched copy of the hand-drawn set: it is the fallback for
    # everything PhyloPic has no silhouette for, and it must survive a rerun.
    if not os.path.exists(HANDDRAWN):
        json.dump(icons, open(HANDDRAWN, "w"))
        print(f"saved hand-drawn originals -> {os.path.basename(HANDDRAWN)}")
    hand = load(HANDDRAWN, {})

    if do_groups:
        hit = kept = 0
        for key, terms in GROUP_TERMS.items():
            if not terms:
                kept += 1
                continue
            for term in terms:
                path, cand = phylopic.silhouette(term, build)
                if path:
                    icons[key] = path
                    credits[key] = {k: cand[k] for k in
                                    ("attribution", "licence", "licence_url",
                                     "uuid", "taxon")}
                    print(f"  {key:14s} <- {cand['taxon']:26s} "
                          f"{cand['licence']:9s} {cand['attribution']}")
                    hit += 1
                    break
            else:
                icons[key] = hand.get(key, icons.get(key))
                credits.pop(key, None)
                kept += 1
                print(f"  {key:14s} .. no silhouette, keeping hand-drawn")
        print(f"groups: {hit} traced, {kept} hand-drawn")

    if do_taxa:
        names = taxa_names()
        print(f"taxa: {len(names)} distinct names")
        hit = 0
        for i, name in enumerate(names):
            if NOT_A_TAXON.search(name):
                continue
            for term in search_terms(name):
                path, cand = phylopic.silhouette(term, build)
                if path:
                    icons["t:" + slug(name)] = path
                    credits["t:" + slug(name)] = {
                        k: cand[k] for k in ("attribution", "licence",
                                             "licence_url", "uuid", "taxon")}
                    hit += 1
                    print(f"  [{i+1}/{len(names)}] {name:34s} <- "
                          f"{cand['taxon']:24s} {cand['licence']}")
                    break
        print(f"taxa: {hit} of {len(names)} got their own silhouette")

    json.dump(icons, open(ICONS, "w"))
    json.dump(credits, open(CREDITS, "w"), indent=1, sort_keys=True)
    total = sum(len(v) for v in icons.values())
    print(f"\n{len(icons)} icons, {total/1024:.0f} kB of markup; "
          f"{len(credits)} credited")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    run(what in ("groups", "all"), what in ("taxa", "all"))
