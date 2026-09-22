"""The biota of every card, composed from one registry.

WHAT WAS WRONG (2026-09). Three unconnected places said what lived where:

  life_data.json   curated lists per label and per interval (names + a note)
  paleobiogeography  province markers: a static tuple of names per province
  provinces.MARKER_NOTES / taxa_db   the descriptions those markers needed

None of them said WHEN a taxon lived or WHERE, so nothing could check either. A
province is a tuple held for as long as the province lasts, so "Nearctic" --
0 to 60 Ma -- listed Bison (arrived ~0.2 Ma) for North America at 60 Ma; the
latitude bands that catch every label without a named realm put moose, bears and
wolverines on any land poleward of 48 degrees in EITHER hemisphere (Patagonia),
camels, oryx and ostriches in every desert on Earth at every Cenozoic age
(the Atacama, central Australia), and mammoths in Antarctica. Whether a card
showed any animal at all, or any plant, was whatever six names happened to come
first. And the drawing was chosen from the letters of the name (biota_forms.py).

WHAT THIS IS. One registry -- build/taxa/*.json -- in which every organism any
card can show is declared ONCE, with what a card needs to be right about it:

    kind + form    what it is, so FAUNA and FLORA can be balanced on purpose and
                   the drawing follows from the body plan
    fad .. lad     when it lived
    range          where: present-day crust codes (pbdb.REGIONS), optionally in
                   time slices, because taxa disperse -- Equus is North American
                   until 2.6 Ma and absent from it after 0.012
    hab, lat       optional habitat and palaeolatitude affinity
    note           the sentence the card prints

and one function, compose(label, age), which every card goes through:

    candidates   the label's curated occurrences, then its province's markers,
                 then every registry taxon at home on this crust at this age
    filtered     alive at this age; at home on this label's crust; right realm;
                 compatible habitat and latitude
    chosen       fauna and flora balanced, no body form repeated while another
                 is on offer, the most place- and time-specific first

Curated lists and province markers keep their authority over WHICH taxa are
characteristic; they have lost the ability to be wrong about when and where,
because those are no longer theirs to say. The output is run-length encoded per
label and shipped in life.json, so the app looks a card up and draws it and
audit_biota.py replays exactly what a reader sees.

WHY CRUST CODES. A fossil is found in the crust its animal lived on, and a
label's crust has a present-day address too. Matching the two is independent of
the plate model and the reference frame and valid at any age, which no test on
palaeo-coordinates is.

    python3 biota.py --check                 validate the registry
    python3 biota.py --card "Patagonian Desert" 0 10 40
    python3 biota.py --coverage              where the registry is thin
"""
import glob
import json
import math
import os
import re
import sys

from biota_forms import FORMS, chain

HERE = os.path.dirname(os.path.abspath(__file__))
REG_DIR = os.environ.get("BIOTA_REG_DIR") or os.path.join(HERE, "taxa")
WEB = os.path.join(HERE, "..", "web")

REALMS = ("sea", "land", "air", "fresh")
RANKS = ("subspecies", "species", "genus", "subtribe", "tribe", "subfamily", "family",
         "superfamily", "infraorder", "suborder", "order", "superorder", "infraclass",
         "subclass", "class", "superclass", "subphylum", "phylum", "kingdom", "domain",
         "clade", "group", "informal", "assemblage")
HABITATS = ("desert", "forest", "rainforest", "grassland", "tundra", "alpine",
            "wetland", "lake", "river", "coast", "island", "cave", "reef", "shelf",
            "pelagic", "deep", "vent", "ice")
FAUNA_KINDS = ("animal",)
FLORA_KINDS = ("plant", "fungus", "alga")

# ---------------------------------------------------------------- regions --
LAND_CODES = ("na-w", "na-e", "na-n", "ca", "gl", "sa-n", "sa-s", "eu", "af-n", "af-e",
              "af-w", "af-s", "mg", "ar", "as-w", "as-n", "as-c", "as-e", "as-se", "in",
              "au", "ng", "nz", "oc", "an")
#: Ocean basins, for the marine taxa and labels that belong to water rather
#: than to any crust. The Palaeozoic names are here because their faunas were
#: real and distinct, not because anything survives of their floors.
BASINS = ("pac", "atl", "ind", "arc", "sou", "med", "tet", "pan", "iap", "rhe", "ura", "mir")
ALIASES = {
    "na": ["na-w", "na-e", "na-n"],
    "sa": ["sa-n", "sa-s"],
    "af": ["af-n", "af-e", "af-w", "af-s"],
    "as": ["as-w", "as-n", "as-c", "as-e", "as-se"],
    "laurentia": ["na-w", "na-e", "na-n", "gl"],
    "euramerica": ["na-w", "na-e", "na-n", "gl", "eu"],
    "laurasia": ["na-w", "na-e", "na-n", "gl", "eu", "as-n", "as-c", "as-e"],
    "holarctic": ["na-w", "na-e", "na-n", "gl", "eu", "as-n", "as-c", "as-e", "as-w"],
    "gondwana": ["sa-n", "sa-s", "af-n", "af-e", "af-w", "af-s", "mg", "ar", "in", "au",
                 "ng", "nz", "an"],
    "afro-arabia": ["af-n", "af-e", "af-w", "af-s", "ar"],
    "sahul": ["au", "ng"],
    "old-world": ["eu", "af-n", "af-e", "af-w", "af-s", "ar", "as-w", "as-n", "as-c",
                  "as-e", "as-se", "in"],
    "new-world": ["na-w", "na-e", "na-n", "ca", "sa-n", "sa-s"],
    "neotropics": ["ca", "sa-n", "sa-s"],
    "cosmo": ["*"],
}


def expand(codes):
    """Aliases and continent prefixes out to leaf codes. '*' is everywhere."""
    out = set()
    for c in codes or ():
        if c in ALIASES:
            out.update(ALIASES[c])
        elif c in LAND_CODES or c in BASINS:
            out.add(c)
        else:
            raise ValueError(f"unknown region code {c!r}")
    return out


# ---------------------------------------------------------------- registry --
_REG = None


def registry_files():
    return sorted(glob.glob(os.path.join(REG_DIR, "*.json")))


def load(force=False):
    """{name: entry}, merged across build/taxa/*.json, ranges expanded.

    A name defined twice is an error rather than a merge: two authors who each
    believed they owned Smilodon is how the three old tables drifted apart.
    """
    global _REG
    if _REG is not None and not force:
        return _REG
    _ALIVE.clear()
    _PLACED.clear()
    reg, where = {}, {}
    for fn in registry_files():
        with open(fn) as f:
            d = json.load(f)
        for name, e in (d.get("taxa") or {}).items():
            if name in reg:
                raise ValueError(f"{name!r} is defined in both {where[name]} and "
                                 f"{os.path.basename(fn)}")
            e = dict(e)
            e["n"] = name
            e["_file"] = os.path.basename(fn)
            reg[name] = e
            where[name] = os.path.basename(fn)
    for e in reg.values():
        _prepare(e)
    # aliases: alternate display names that resolve to one entry
    aka = {}
    for name, e in reg.items():
        for a in e.get("aka", ()):
            if a in reg or a in aka:
                raise ValueError(f"alias {a!r} of {name!r} collides with another name")
            aka[a] = name
    _REG = {"taxa": reg, "aka": aka}
    return _REG


def _prepare(e):
    """Normalise one entry in place: slices, kind, habitat sets."""
    form = e.get("form")
    e["kind"] = e.get("kind") or (FORMS[form]["kind"] if form in FORMS else None)
    slices = []
    plain = [c for c in e.get("range", []) if isinstance(c, str)]
    if plain:
        slices.append((float(e.get("fad", 0)), float(e.get("lad", 0)), expand(plain)))
    for s in e.get("range", []):
        if isinstance(s, dict):
            t = s.get("t") or [e.get("fad", 0), e.get("lad", 0)]
            slices.append((float(max(t)), float(min(t)), expand(s.get("in", []))))
    e["_slices"] = slices
    e["_hab"] = set(e.get("hab", ()))
    # Windows in which the AUTHOR named Antarctica, as opposed to reaching it
    # through "cosmo" or "gondwana". After the ice, only these count (at_home).
    an = []
    if "an" in plain:
        an.append((float(e.get("fad", 0)), float(e.get("lad", 0))))
    for s in e.get("range", []):
        if isinstance(s, dict) and "an" in (s.get("in") or ()):
            t = s.get("t") or [e.get("fad", 0), e.get("lad", 0)]
            an.append((float(max(t)), float(min(t))))
    e["_an"] = an
    # lat: [lo, hi] for the whole lifetime, or slices {"t": [old, young], "lat": [lo, hi]}
    lat = e.get("lat")
    if lat and isinstance(lat[0], dict):
        e["_lat"] = [(float(max(x["t"])), float(min(x["t"])), float(x["lat"][0]), float(x["lat"][1]))
                     for x in lat]
    elif lat:
        e["_lat"] = [(float("inf"), 0.0, float(lat[0]), float(lat[1]))]
    else:
        e["_lat"] = []
    # box: [w, e, s, n] for the whole lifetime, or {"t": [old, young], "box": [[...]]}
    # -- a relict's last stand is not where its fossils lie (Sequoiadendron is a
    # Sierra Nevada tree today and was a Nevada, Idaho and Greenland one before)
    boxes = []
    for b in e.get("box", ()):
        if isinstance(b, dict):
            for bb in b["box"]:
                boxes.append((float(max(b["t"])), float(min(b["t"])), tuple(float(v) for v in bb)))
        else:
            boxes.append((float("inf"), 0.0, tuple(float(v) for v in b)))
    e["_box"] = boxes


def get(name):
    R = load()
    return R["taxa"].get(name) or R["taxa"].get(R["aka"].get(name, ""))


def alive(e, age):
    """Was this taxon living at `age`? Extant taxa (lad 0) are alive at 0."""
    return e["lad"] - 1e-9 <= age <= e["fad"] + 1e-9


#: Antarctica has carried an ice sheet since the Eocene-Oligocene boundary. A
#: range of "cosmo" or "gondwana" is a statement about the inhabited continents,
#: and after the ice it does not reach this one: ants, frogs and water lilies
#: are everywhere except here. From ICE_FROM on, a taxon is at home on a label
#: whose only crust is Antarctic only where its author named Antarctica.
ICE_FROM = 34.0
_ICE_HOME = frozenset({"an"})


def at_home(e, home, age, ice=True, sea_card=None):
    """Does the taxon's range, at this age, include any of the label's codes?
    `ice=False` asks the plain question of the range, for a curated list, whose
    author has already said the taxon is here."""
    if ice and age < ICE_FROM and home and set(home) <= _ICE_HOME:
        return any(young - 1e-9 <= age <= old + 1e-9 for old, young in e["_an"])
    # "Cosmopolitan" on land means every continent. It does not mean Kerguelen or
    # the summit of a seamount: a home that is ocean basin and nothing else is
    # reached by a land taxon only when its author named that ocean.
    # ice=False is the author's word (a curated list): neither the ice rule nor
    # the ocean-crust rule second-guesses it -- Kerguelen's curated conifers are
    # "cosmo" and its home is ocean, and that is exactly why they are curated
    oceanic = ice and bool(home) and "*" not in home and set(home) <= set(BASINS)
    for old, young, codes in e["_slices"]:
        if young - 1e-9 <= age <= old + 1e-9:
            # '*' on either side: a cosmopolitan taxon is at home anywhere, and
            # a label that IS everywhere (Pangaea) is home to anything alive.
            if "*" in home or (home & codes):
                return True
            # `sea_card` False = the card is a LAND card: then a world-wide range
            # does not carry even a sea taxon with a freshwater or land side onto
            # it (bony fishes on the Seychelles). Unknown = judge by primary realm.
            landward = (sea_card is False) or (sea_card is None and e["realm"] != "sea")
            if "*" in codes and not (oceanic and landward):
                return True
    return False


def _ever_home(e, home):
    """Does the range include this crust at ANY time?"""
    return any("*" in codes or "*" in home or (home & codes) for _o, _y, codes in e["_slices"])


def breadth(e, age):
    """How many top-level regions the range covers at this age (0 = everywhere)."""
    tops = set()
    for old, young, codes in e["_slices"]:
        if young - 1e-9 <= age <= old + 1e-9:
            if "*" in codes:
                return 0
            tops.update(c.split("-")[0] for c in codes)
    return len(tops)


_LABEL_NAMES = None


def _label_names():
    global _LABEL_NAMES
    if _LABEL_NAMES is None:
        try:
            with open(os.path.join(WEB, "labels.json")) as f:
                _LABEL_NAMES = {l["n"] for l in json.load(f)}
        except OSError:
            _LABEL_NAMES = set()
    return _LABEL_NAMES


# -------------------------------------------------------------- validation --
def validate(reg=None):
    """Every structural rule an entry must meet. Returns a list of findings.

    These are the FAILURES: the build refuses to ship while any stands. The
    judgement calls -- an authored range that disagrees with the PBDB's, a form
    the classification cannot confirm -- are reported by review() instead.
    """
    reg = reg or load()["taxa"]
    bad = []
    for name, e in reg.items():
        def f(msg):
            bad.append(f"{name}: {msg}  [{e.get('_file')}]")
        for k in ("rank", "realm", "form", "fad", "lad", "range", "note"):
            if e.get(k) in (None, "", []):
                f(f"missing {k}")
        if e.get("realm") not in REALMS:
            f(f"realm {e.get('realm')!r}")
        for r_ in e.get("realms") or ():
            if r_ not in REALMS:
                f(f"realms has {r_!r}")
        if e.get("form") not in FORMS:
            f(f"form {e.get('form')!r} is not in biota_forms.FORMS")
            continue
        try:
            fad, lad = float(e["fad"]), float(e["lad"])
        except (KeyError, TypeError, ValueError):
            f("fad/lad not numeric")
            continue
        if not (fad >= lad >= 0):
            f(f"fad {fad} < lad {lad}, or negative")
        if fad > 3800:
            f(f"fad {fad} is older than life")
        if not e["_slices"]:
            f("range is empty")
        for old, young, codes in e["_slices"]:
            if not codes:
                f("a range slice names no region")
            if old > fad + 1e-6 or young < lad - 1e-6:
                f(f"range slice {old}-{young} lies outside fad-lad {fad}-{lad}")
        covered = any(young <= lad + 1e-6 for _o, young, _c in e["_slices"]) and \
            any(old >= fad - 1e-6 for old, _y, _c in e["_slices"])
        if e["_slices"] and not covered:
            f("range slices do not reach both fad and lad: the taxon is homeless "
              "for part of its own lifetime")
        for h in e["_hab"]:
            if h not in HABITATS:
                f(f"habitat {h!r}")
        for _o, _y, lo, hi in e["_lat"]:
            if not 0 <= lo <= hi <= 90:
                f(f"lat {e.get('lat')} is not [min_abs, max_abs]")
        if e.get("avoid"):
            known = _label_names()
            for nm in e["avoid"]:
                if known and nm not in known:       # a misspelt label is a silent no-op
                    f(f"avoid names {nm!r}, which is not a label")
        for _o, _y, b in e["_box"]:
            if not (len(b) == 4 and -180 <= b[0] < b[1] <= 180 and -90 <= b[2] < b[3] <= 90):
                f(f"box {list(b)} is not [lon_w, lon_e, lat_s, lat_n] (split one that "
                  f"crosses the date line)")
        note = e.get("note") or ""
        if len(note) > 320:
            f(f"note is {len(note)} chars (max 320)")
        if e.get("rep") and not get(e["rep"]) and e["rep"] != name:
            f(f"rep {e['rep']!r} is not in the registry")
        kind = e.get("kind")
        fk = FORMS[e["form"]]["kind"]
        if e.get("assemblage"):
            continue
        if kind != fk:
            f(f"kind {kind!r} but its form {e['form']!r} is a {fk}")
        # an air-realm plant, a sea-realm songbird
        if fk in ("plant", "fungus") and e.get("realm") == "air":
            f("a plant or fungus cannot have realm 'air'")
    return bad


#: The PBDB files most non-mammalian synapsids and several early tetrapods under
#: class "Osteichthyes" and order "Cotylosauria" -- Cynognathus, Thrinaxodon and
#: Inostrancevia are all, on its books, bony fish. Neither name says anything
#: true about them, so neither is allowed to vouch for or against a form.
_PBDB_JUNK_ORDERS = {"Cotylosauria"}
_TETRAPOD_ORDERS = {"Cotylosauria", "Therocephalia", "Dicynodontia", "Kannemeyeriiformes",
                    "Gorgonopsia", "Dinocephalia", "Cynodontia", "Pelycosauria", "Therapsida",
                    "Anomodontia", "Biarmosuchia", "Seymouriamorpha", "Anthracosauria",
                    "Chroniosuchia", "Embolomeri", "Diadectomorpha", "Temnospondyli"}


def lineage(e):
    """Clade names the classification evidence gives, most specific first.

    An authored `cls` REPLACES the PBDB's classification rather than adding to
    it: it is there precisely because the PBDB's was missing or wrong.
    """
    out = []
    src = e.get("cls") or {}
    if not src:
        src = dict(e.get("pbdb") or {})
        if src.get("order") in _TETRAPOD_ORDERS and src.get("class") == "Osteichthyes":
            src.pop("class")
        if src.get("order") in _PBDB_JUNK_ORDERS:
            src.pop("order")
    for k in ("genus", "family", "order", "class", "phylum"):
        v = src.get(k)
        if v and not str(v).startswith("NO_") and v not in out:
            out.append(v)
    return out


#: Broad clades, and every form that may legitimately stand for a member. They
#: decide only when nothing more specific in the lineage is known to any form.
def _section_forms(first, last):
    keys = list(FORMS)
    return set(keys[keys.index(first): keys.index(last) + 1])


_MAMMALS = _section_forms("bear", "smallmammal")
_BIRDS = _section_forms("songbird", "earlybird")
_REPTILES = _section_forms("lizard", "pareiasaur")
_SYNAPSIDS = _section_forms("sailback", "cynodont")
_AMPHIBIANS = _section_forms("temnospondyl", "reptiliomorph")
_FISHES = _section_forms("ostracoderm", "cod")
BROAD = {
    "Mammalia": _MAMMALS, "Aves": _BIRDS,
    "Reptilia": _REPTILES | _BIRDS | _SYNAPSIDS | {"reptiliomorph"},
    "Saurischia": {"theropod", "spinosaur", "smalltheropod", "sauropod", "prosauropod"} | _BIRDS,
    "Ornithischia": {"ceratopsian", "stegosaur", "ankylosaur", "hadrosaur", "ornithopod"},
    "Amphibia": _AMPHIBIANS, "Synapsida": _SYNAPSIDS | _MAMMALS,
    "Osteichthyes": _FISHES, "Actinopterygii": _FISHES, "Sarcopterygii": _FISHES | {"stemtetrapod"},
    "Chondrichthyes": {"shark", "ray"},
    "Carnivora": {"bear", "cat", "sabertooth", "canid", "hyena", "mustelid", "seal", "carnivoran"},
    "Primates": {"ape", "hominin", "monkey", "lemur"},
    "Diprotodontia": {"kangaroo", "diprotodont", "koala", "marsupiallion"},
    "Artiodactyla": {"bison", "antelope", "caprine", "deer", "moose", "giraffe", "camel", "llama",
                     "pig", "entelodont", "oreodont", "hippo", "whale", "dolphin", "archaeocete"},
    "Perissodactyla": {"horse", "rhino", "indricothere", "brontothere", "chalicothere", "tapir",
                       "condylarth"},
    "Xenarthra": {"groundsloth", "treesloth", "glyptodont", "armadillo", "anteater"},
    "Cingulata": {"glyptodont", "armadillo"}, "Pilosa": {"groundsloth", "treesloth", "anteater"},
    "Rodentia": {"rodent", "bigrodent"}, "Cetacea": {"whale", "dolphin", "archaeocete"},
    "Bovidae": {"bison", "antelope", "caprine"}, "Cervidae": {"deer", "moose"},
    "Camelidae": {"camel", "llama"}, "Felidae": {"cat", "sabertooth"},
    "Theropoda": {"theropod", "spinosaur", "smalltheropod"} | _BIRDS,
    "Dinosauria": {"theropod", "spinosaur", "smalltheropod", "sauropod", "prosauropod",
                   "ceratopsian", "stegosaur", "ankylosaur", "hadrosaur", "ornithopod"},
    "Testudines": {"seaturtle", "turtle", "tortoise"}, "Squamata": {"lizard", "snake", "mosasaur"},
    "Crocodylia": {"crocodile", "gharial"}, "Sauropterygia": {"plesiosaur", "pliosaur", "nothosaur",
                                                              "placodont"},
    "Plesiosauria": {"plesiosaur", "pliosaur"},
    "Trilobita": {"trilobite", "agnostid"}, "Bivalvia": {"bivalve", "clam", "mussel", "oyster",
                                                         "rudist", "giantclam"},
    "Gastropoda": {"seasnail", "snail"}, "Cephalopoda": {"ammonite", "heteromorph", "orthocone",
                                                         "nautilus", "belemnite", "squid"},
    "Anthozoa": {"coral", "horncoral", "tabulate"}, "Brachiopoda": {"brachiopod", "lingulid"},
    "Echinodermata": {"crinoid", "blastoid", "seaurchin", "starfish"},
    "Insecta": {"dragonfly", "beetle", "cockroach", "ant", "butterfly", "fly", "grasshopper"},
    "Arachnida": {"spider", "scorpion", "springtail"}, "Malacostraca": {"crab", "lobster", "shrimp"},
    "Foraminifera": {"foram", "largeforam"}, "Porifera": {"sponge", "archaeocyath", "stromatoporoid"},
}


def _deciders(clade):
    got = {f for f, v in FORMS.items() if clade in v["of"]}
    return got | BROAD.get(clade, set())


def check_form(e):
    """None if the classification confirms the form, else a finding string.

    The MOST SPECIFIC clade in the lineage that any form claims decides it:
    Ursus is decided by Ursidae, which only "bear" depicts, so Ursus-as-canid is
    a finding however many broader clades the two share; Allosaurus, which the
    PBDB files no deeper than Reptilia, is decided by Reptilia and may be any
    reptile form. A lineage no form recognises vouches for nothing.
    """
    if e.get("assemblage") or e.get("form_ok"):
        return None
    for clade in lineage(e):
        forms = _deciders(clade)
        if forms:
            if e["form"] in forms:
                return None
            return (f"form {e['form']!r}, but {clade} is drawn as "
                    f"{', '.join(sorted(forms)[:5])}")
    return None


def review(reg=None):
    """Judgement calls: (severity, name, message). Reported, counted, ratcheted."""
    reg = reg or load()["taxa"]
    out = []
    for name, e in reg.items():
        if e.get("form") not in FORMS:
            continue
        m = check_form(e)
        if m:
            out.append(("FORM", name, m))
        p = e.get("pbdb") or {}
        if p.get("fea") is not None and p.get("lla") is not None and not e.get("pbdb_ok"):
            fea, lla = float(p["fea"]), float(p["lla"])
            fad, lad = float(e["fad"]), float(e["lad"])
            if fad < lla - 1e-6 or lad > fea + 1e-6:
                out.append(("RANGE", name, f"authored {fad}-{lad} Ma does not overlap "
                            f"the PBDB's {fea}-{lla}"))
            elif fad > fea * 1.3 + 8 and p.get("exact", True):
                out.append(("RANGE-OLD", name, f"authored first appearance {fad} Ma is far "
                            f"older than the PBDB's {fea}"))
        # WHERE, against where it has actually been dug up. Only for extinct taxa
        # with enough collections to mean something: the fossil record says
        # nothing about a living range, and three collections prove no absence.
        regs = p.get("regions") or {}
        total = sum(regs.values())
        if total >= 8 and not p.get("extant") and not e.get("place_ok") and p.get("exact", True):
            tops_auth, everywhere = set(), False
            for _o, _y, codes in e["_slices"]:
                if "*" in codes:
                    everywhere = True
                tops_auth.update(c.split("-")[0] for c in codes)
            if not everywhere:
                heavy = {c.split("-")[0] for c, n in regs.items() if n >= max(3, 0.12 * total)}
                # "sea" is the PBDB's collections on no continent -- ocean floor
                # cores, islands, and the Arctic shelf; any basin code answers it
                if any(c in BASINS for _o, _y, codes in e["_slices"] for c in codes):
                    heavy.discard("sea")
                miss = sorted(heavy - tops_auth)
                if miss:
                    out.append(("PLACE", name, f"{', '.join(miss)} hold a large share of its "
                                f"PBDB collections but are not in the authored range"))
    return out


# ------------------------------------------------------------------- icons --
def icon_for(name, icons):
    """(icon_key, how) for a registered taxon. Never a realm fallback.

    how: 'own'     a silhouette traced for this very taxon
         'rep'     its declared representative's silhouette
         'form'    its form's drawing
         'parent'  a parent form's drawing: a declared approximation, counted
         None      nothing resolves -- the build fails
    """
    e = get(name)
    if e is None:
        return None, None
    own = "t:" + re.sub(r"[^a-z0-9]+", "-", e["n"].lower()).strip("-")
    if own in icons and not e.get("no_own_icon"):
        return own, "own"
    if e.get("rep"):
        r = "t:" + re.sub(r"[^a-z0-9]+", "-", e["rep"].lower()).strip("-")
        if r in icons:
            return r, "rep"
    for i, form in enumerate(chain(e["form"])):
        key = FORMS[form]["icon"] or form
        if key in icons:
            return key, ("form" if i == 0 else "parent")
    return None, None


# ------------------------------------------------------------ label context --
MARINE_TYPES = {"ocean", "sea"}
CARD_TYPES = {"continent", "ocean", "sea", "forest", "grassland", "tundra", "island",
              "region", "lake", "orogen", "basin", "rift", "desert", "plateau",
              "craton", "terrane"}

#: Habitat a label TYPE implies. None = no constraint (a continent holds every
#: habitat). Names refine it below.
TYPE_HABITAT = {
    "desert": {"desert"}, "forest": {"forest", "rainforest", "wetland"},
    "grassland": {"grassland"}, "tundra": {"tundra", "ice"},
    "lake": {"lake", "wetland", "river"}, "orogen": {"alpine", "forest"},
    "plateau": {"alpine", "grassland", "desert"}, "island": {"island", "coast", "forest"},
    "sea": {"shelf", "reef", "pelagic", "coast"}, "ocean": {"pelagic", "deep", "shelf"},
}
#: A sea label whose card takes more than the sea: the Eocene Arctic was capped
#: with fresh water, and the fern that covered it is the point of the label.
LABEL_REALMS = {"Arctic Azolla Bloom": ["fresh", "sea"]}

NAME_HABITAT = {
    "Arctic Azolla Bloom": {"lake", "wetland", "pelagic", "shelf", "coast"},
    "Amazon Rainforest": {"rainforest", "river", "wetland"},
    # a lake at 3,800 m is not a lowland wetland: capybara and swamp palms stay out
    "Lake Titicaca": {"lake", "alpine"}, "Lake Tauca": {"lake", "alpine"},
    "Mid-Atlantic Ridge": {"vent", "deep", "pelagic"},
    "East Pacific Rise": {"vent", "deep", "pelagic"},
    "Beringian Steppe-Tundra": {"tundra", "grassland"},
    "Tibetan Plateau": {"alpine", "grassland"},
    "Tibetan Alpine Tundra": {"alpine", "tundra", "grassland"},
    "Pebas Mega-Wetland": {"wetland", "river", "lake", "rainforest"},
    "East African Rift soda lakes": {"lake", "wetland", "grassland"},
}

#: A habitat with a DATE. These labels are typed for their tectonics -- a block,
#: a basin, a rift -- and that says nothing about what grows there; what they are
#: today they have been only since the age given, so the habitat binds only from
#: then. Without it the Tarim Block (the Taklamakan) showed oaks and red deer.
HABITAT_SINCE = {
    "Tarim Block": (5, {"desert"}), "Junggar Basin": (5, {"desert", "grassland"}),
    "Qaidam Basin": (5, {"desert", "alpine"}), "Ordos Basin": (3, {"grassland", "desert"}),
    "Taoudeni Basin": (7, {"desert"}), "Hoggar Massif": (7, {"desert", "alpine"}),
    "Basin and Range": (8, {"desert", "alpine", "grassland"}),
    "Rio Grande Rift": (8, {"desert", "grassland", "alpine"}),
    "Colorado Plateau": (8, {"desert", "alpine", "forest"}),
    "Amuria": (3, {"forest", "grassland"}), "Williston Basin": (8, {"grassland"}),
    "Solimoes Basin": (10, {"rainforest", "river", "wetland"}),
    "Congo Basin": (10, {"rainforest", "river", "wetland", "forest"}),
    "Parana Basin": (5, {"forest", "grassland", "wetland", "river"}),
    "West Siberian Basin": (3, {"forest", "wetland", "tundra"}),
    "Canadian Shield": (3, {"forest", "tundra", "lake", "wetland"}),
    "Fennoscandian Shield": (3, {"forest", "tundra", "lake", "wetland"}),
    "Yilgarn Craton": (5, {"desert", "grassland", "forest"}),
    "Tethyan Himalaya": (10, {"alpine"}), "Deccan Traps": (5, {"forest", "grassland"}),
    "Deccan Plateau (basement)": (5, {"forest", "grassland"}),
    "Anatolide-Tauride Block": (5, {"grassland", "forest", "alpine"}),
    "Okavango Rift": (3, {"wetland", "river", "grassland"}),
    "Rhine Graben": (3, {"forest", "river", "wetland"}),
    "Baikal Rift": (5, {"forest", "lake", "alpine"}),
    "Patagonian Batholith": (5, {"forest", "alpine", "ice"}),
    "Guiana Shield": (10, {"rainforest", "alpine", "river", "forest"}),
    "Brazilian Shield": (5, {"grassland", "forest", "river"}),
    "Maracaibo Basin": (5, {"wetland", "forest", "lake", "river"}),
    "Sichuan Basin": (5, {"forest", "river", "wetland"}),
    "Annamia": (5, {"rainforest", "forest", "river"}),
    "Sundaland": (3, {"rainforest", "forest", "river", "wetland", "coast"}),
    "Wallacea": (5, {"rainforest", "forest", "island", "coast"}),
    "Greenland": (2.6, {"tundra", "ice", "coast"}),
    "Kolyma-Omolon Terrane": (2.6, {"tundra", "forest"}),
    "Yakutat Terrane": (2.6, {"forest", "ice", "coast", "alpine"}),
    "Doggerland": (1, {"grassland", "wetland", "forest", "river", "tundra"}),
    "Beringia": (3, {"tundra", "grassland"}),
    "Sahul": (3, {"grassland", "forest", "rainforest", "wetland", "desert"}),
}

#: The home crust of every label whose own coordinate cannot say it. Three kinds
#: of label need this. OCEANS belong to a basin, not to crust. PALAEO-FRAME
#: labels are authored where the feature sat in its own era (the Karoo Basin at
#: 58 S), so their coordinate names no present-day crust -- or, worse, names the
#: WRONG one: the Acadian Belt's authored (-48,-10) is Brazil. And CONTINENTS
#: are larger than any one code. Everything else is read off the coordinate.
LABEL_HOME = {
    # --- supercontinents and continents
    "Pangaea": ["cosmo"], "Rodinia": ["cosmo"], "Pannotia": ["cosmo"],
    "Gondwana": ["gondwana"], "Gondwana (assembling)": ["gondwana"],
    "Laurasia": ["laurasia"], "Laurussia (Euramerica)": ["euramerica"],
    "Laurentia": ["laurentia"], "North America": ["na", "gl"], "South America": ["sa"],
    "Africa": ["af"], "Eurasia": ["eu", "as"], "Antarctica": ["an"], "Australia": ["au", "ng"],
    "India": ["in"], "Greater India": ["in"], "Siberia": ["as-n"], "Baltica": ["eu"],
    "Avalonia": ["eu", "na-e"], "Kazakhstania": ["as-c"], "Amuria": ["as-e", "as-c", "as-n"],
    "North China": ["as-e"], "South China": ["as-e"], "Tarim Block": ["as-c"],
    "Cimmeria": ["as-w", "as-c", "as-se"], "Annamia": ["as-se"],
    "Anatolide-Tauride Block": ["as-w"], "Amazonia": ["sa-n"],
    "Sao Francisco Craton": ["sa-n", "sa-s"], "Congo Craton": ["af-w", "af-e"],
    "Kalahari Craton": ["af-s"], "West Africa Craton": ["af-w", "af-n"],
    "Australia-East Antarctica": ["au", "an"],
    # --- palaeo-frame labels: the crust the feature is actually found in
    "Acadian Belt": ["na-e"], "Taconic Belt": ["na-e"], "Gilboa Forest": ["na-e"],
    "Grenville Belt": ["na-e"], "Midcontinent Rift": ["na-e"], "Michigan Basin": ["na-e"],
    "Permian Basin": ["na-w"], "Coconino Erg": ["na-w"], "Navajo Erg": ["na-w"],
    "Amundsen Basin": ["na-n"], "Mackenzie Mountains Basin": ["na-n", "na-w"],
    "Euramerican Coal Forests": ["na-e", "eu"], "Central Pangaean Mts": ["na-e", "eu", "af-n"],
    "Rotliegend Desert": ["eu"], "Oslo Rift": ["eu"], "Zechstein Sea": ["eu"],
    "Solnhofen Lagoon": ["eu"], "Sveconorwegian Belt": ["eu"], "Timanian Belt": ["eu"],
    "Hun Superterrane": ["eu", "as-w", "as-c"], "Hispanic Corridor": ["ca", "na-e", "af-n", "sa-n"],
    "Cathaysian Coal Forests": ["as-e"], "Karoo Basin": ["af-s"],
    "Glossopteris Flora": ["af-s", "in", "au", "an", "sa-s", "sa-n", "mg"],
    "Gondwanan Polar Tundra": ["an", "af-s", "sa-s", "au", "in"],
    "Botucatu Erg": ["sa-s"], "Brasiliano Belt": ["sa-n", "sa-s"], "Sunsas Belt": ["sa-n"],
    "Pan-African Belt": ["af"], "East African Orogen": ["af-e", "mg", "ar"],
    "Irumide Belt": ["af-s", "af-e"], "Benue Trough": ["af-w"], "Namib": ["af-s"],
    "Centralian Superbasin": ["au"], "Officer Basin": ["au"], "Adelaide Rift Complex": ["au"],
    "Antarctic Nothofagus Forest": ["an"], "West Antarctic Rift": ["an"],
    "Arctic Azolla Bloom": ["arc", "na-n", "gl", "as-n", "eu"],
    "Avalon Deep-Water Realm": ["na-e", "eu", "iap"], "White Sea Realm": ["eu", "au"],
    # a rift is dry land until the sea gets in: the Red Sea flooded in the early
    # Miocene, the Gulf of California about 7 Ma (SUBMERGED carries the same dates)
    "Red Sea Rift": [{"t": [25, 20], "in": ["ar", "af-e", "af-n"]},
                     {"t": [20, 0], "in": ["ind", "ar", "af-e", "af-n"]}],
    "Gulf of California": [{"t": [12, 7], "in": ["ca", "na-w"]},
                           {"t": [7, 0], "in": ["pac", "ca", "na-w"]}],
    "Old Red Sandstone Continent": ["euramerica"],
    # the Caledonian belt ran through three continents; the CALEDONIDES on the
    # map today are Scotland and Norway, and a composite home put Titanis and
    # Megalonyx on them
    "Caledonides": [{"t": [490, 180], "in": ["eu", "gl", "na-e"]}, {"t": [180, 55], "in": ["eu", "gl"]},
                    {"t": [55, 0], "in": ["eu"]}],
    "Andes": ["sa"], "Himalaya": ["as-c", "in"], "Cordillera": ["na-w", "na-n"],
    "Zagros Mts": ["as-w", "ar"],
    "Ural Mountains": ["eu", "as-n"], "Variscan Belt": ["eu"], "Beringia": ["na-n", "as-n"],
    "Beringian Steppe-Tundra": ["na-n", "as-n"], "Arctic Tundra": ["as-n", "eu", "na-n"],
    "Eurasian Steppe": ["as-c", "eu", "as-n"], "Sahul": ["au", "ng"],
    "Wallacea": ["as-se"], "Sundaland": ["as-se"],
    "Central Asian Orogenic Belt": ["as-c", "as-n", "as-e"],
    "Australasian Belt": ["au", "ng", "as-se"],
    # --- drowned fragments and ocean-floor features with no crust code
    # A microcontinent is its parent's crust until it leaves, and an ocean island
    # after: Mauritia and the Seychelles were Madagascar-India until the Deccan
    # rifting, and what lives on Mauritius now did not walk there from either.
    "Mauritia": [{"t": [85, 66], "in": ["mg", "in"]}, {"t": [66, 0], "in": ["ind"]}],
    "Seychelles Microcontinent": [{"t": [90, 63], "in": ["mg", "in"]},
                                  {"t": [63, 0], "in": ["ind"]}],
    "Mascarene Plateau": ["ind"], "Agulhas Plateau": ["ind", "sou"],
    "Broken Ridge": ["ind"], "Ninetyeast Ridge": ["ind"],
    # an isolated plateau throughout: its Cretaceous forest is curated, its
    # animals are what flew or swam there (a home of "an, in" had it borrowing
    # Antarctica's marsupials and India's bats)
    "Kerguelen Microcontinent": ["ind", "sou"],
    "Rio Grande Rise": ["atl"], "Walvis Ridge": ["atl"], "Shatsky Rise": ["pac"],
    "Ontong Java Plateau": ["pac"], "Manihiki Plateau": ["pac"], "Emperor Seamounts": ["pac"],
    "East Tasman Plateau": ["pac", "sou", "au"],
    "Argoland": [{"t": [165, 155], "in": ["au"]}, {"t": [155, 0], "in": ["ind", "au"]}],
    "Jan Mayen Microcontinent": [{"t": [55, 25], "in": ["gl"]}, {"t": [25, 0], "in": ["atl", "arc"]}],
    "Zealandia": ["nz"],
    # --- oceans: a basin, and the crust whose shelves faced it
    "Pacific Ocean": ["pac", "na-w", "ca", "sa-n", "sa-s", "as-e", "as-se", "au", "ng", "nz", "oc", "as-n"], "Atlantic Ocean": ["atl", "na-e", "ca", "gl", "eu", "af-n", "af-w", "af-s", "sa-n", "sa-s"], "Indian Ocean": ["ind", "af-e", "af-s", "mg", "ar", "in", "as-se", "au"],
    "Arctic Ocean": ["arc", "na-n", "gl", "eu", "as-n"], "Southern Ocean": ["sou", "an", "sa-s", "nz", "au", "af-s"], "Tethys Ocean": ["tet", "eu", "af-n", "ar", "as-w", "as-c", "in", "as-se", "as-e"],
    "Neotethys": ["tet", "eu", "af-n", "ar", "as-w", "in", "as-se"], "Palaeo-Tethys": ["tet", "as-e", "as-c", "as-w"],
    "Panthalassa": ["pan", "na-w", "as-e", "as-n", "au", "nz", "sa-s", "an"], "Panthalassic Ocean": ["pan", "na-w", "as-e", "as-n", "au", "sa-s", "an"], "Panthalassic (proto)": ["pan", "mir"],
    "Neo-Panthalassa": ["pac"], "Mirovia": ["mir"],
    "Iapetus Ocean": ["iap", "na-e", "gl", "eu"], "Rheic Ocean": ["rhe", "eu", "af-n", "na-e"],
    "Ural Ocean": ["ura", "eu", "as-n", "as-c"], "Mongol-Okhotsk Ocean": ["pan", "as-n", "as-e"],
    "Piedmont-Ligurian Ocean": ["tet", "eu"], "Mozambique Ocean": ["mir", "af-e", "mg", "in"],
    "Adamastor Ocean": ["mir", "sa-s", "af-s"], "Tornquist Sea": ["iap", "eu"],
    "Mid-Atlantic Ridge": ["atl"], "East Pacific Rise": ["pac"], "Reykjanes Ridge": ["atl"],
    "Gakkel Ridge": ["arc"], "Carlsberg Ridge": ["ind"], "Southwest Indian Ridge": ["ind", "sou"],
    "Pacific-Antarctic Ridge": ["pac", "sou"], "Nazca Ridge": ["pac"],
    # --- seas: the basin they opened onto, and the crust they flooded
    "Mediterranean": ["med", "eu", "af-n", "as-w"], "Mediterranean (closing)": ["med"],
    "Messinian Salt Basin": ["med", "eu", "af-n"],
    "Lago Mare (Messinian Mediterranean)": ["med", "eu"],
    "Paratethys": ["tet", "eu", "as-w", "as-c"], "Gulf of Mexico": ["atl", "ca", "na-e"],
    "Central American Sea": ["atl", "pac", "ca"], "Tasman Sea": ["pac", "au", "nz"],
    "Sea of Japan": ["pac", "as-e"], "South China Sea": ["pac", "as-se", "as-e"],
    "Okhotsk Sea": ["pac", "as-n"], "Boreal Sea": ["arc", "eu", "as-n"],
    "Viking Corridor": ["arc", "atl", "eu"], "Turgai Strait": ["tet", "arc", "as-c", "as-n"],
    "West Siberian Sea": ["arc", "as-n"], "Trans-Saharan Sea": ["tet", "atl", "af-n", "af-w"],
    "Western Interior Seaway": ["na-w", "na-e", "arc"], "Hudson Seaway": ["na-e", "na-n", "arc"],
    "Mowry Sea": ["na-w", "arc"], "Bearpaw Sea": ["na-w"], "Cannonball Sea": ["na-w", "na-e"],
    "Sundance Sea": ["na-w"], "Absaroka Sea": ["na-w", "na-e"], "Kaskaskia Sea": ["na-e", "na-w"],
    "Tippecanoe Sea": ["na-e", "na-w"], "Sauk Sea": ["na-e", "na-w"],
    "Eromanga Sea": ["au"], "Muschelkalk Sea": ["eu", "tet"], "Nama Sea": ["af-s"],
    "Bitter Springs Sea": ["au"],
}


def label_home(lab, features=None, age=None):
    """The crust and basin codes a label is at home on, expanded to leaves.

    Authored first; then the modern fragments of a composite; then the label's
    own coordinate, but ONLY where that coordinate is a present-day one -- the
    label is plate-tracked, or lives in the last 20 Myr. None means the label
    has no home and must be given one in LABEL_HOME: audit_biota fails on it.
    """
    import pbdb                                            # noqa: PLC0415
    name = lab["n"]
    if name in LABEL_HOME:
        spec = LABEL_HOME[name]
        if spec and isinstance(spec[0], dict):
            # time-sliced: the slice holding `age`, or every slice when none is asked
            hit = [x for x in spec
                   if age is None or min(x["t"]) - 1e-9 <= age <= max(x["t"]) + 1e-9]
            if not hit:
                hit = [min(spec, key=lambda x: min(abs(age - x["t"][0]), abs(age - x["t"][1])))]
            return expand([c for x in hit for c in x["in"]])
        return expand(spec)
    codes = set()
    if features is not None:
        spec = (getattr(features, "COMPOSITE_LABELS", {}).get(name)
                or getattr(features, "COMPOSITE_BELTS", {}).get(name) or {})
        for x, y in spec.get("modern") or []:
            c = pbdb.region_of(x, y)
            if c:
                codes.add(c)
    hi = max(lab.get("a0", 0), lab.get("a1", 0))
    if not codes and (lab.get("tr") or hi <= 20):
        c = pbdb.region_of(lab.get("lon"), lab.get("lat"))
        if c:
            codes.add(c)
    return codes or None


#: Labels typed for what they are TECTONICALLY -- an oceanic plateau, a drowned
#: continental ribbon, a rift the sea has entered -- whose surface is water. Their
#: cards are sea cards for the ages given (old, young; None = always), whatever
#: the type says. The app draws them under water; ants, termites and crocodiles
#: on the Shatsky Rise was the card contradicting the globe it sits on.
#: audit_biota checks the present-day DEM for any the list has missed.
SUBMERGED = {
    "Ontong Java Plateau": None, "Manihiki Plateau": None, "Shatsky Rise": None,
    "Agulhas Plateau": None, "Mascarene Plateau": None, "Rio Grande Rise": None,
    "Walvis Ridge": None, "Broken Ridge": None, "East Tasman Plateau": None,
    "Argoland": (155, 0), "Red Sea Rift": (20, 0), "Gulf of California": (7, 0),
    # a drowned sliver until its volcano broke the surface: Mauritius is about
    # 8 Myr old, Jan Mayen's Beerenberg under one
    "Mauritia": (66, 9), "Jan Mayen Microcontinent": (25, 1),
    # an oceanic plateau and its island arc: nothing walked to it
    "Wrangellia Terrane": None,
    # Wallacea's islands rose from the sea in the Pliocene; before that the label
    # marks a strait
    "Wallacea": (15, 5),
}
#: Below sea level on the DEM and rightly a LAND card: crust under an ice sheet,
#: and drowned microcontinents whose card is the life of the islands still above
#: water. Listed so the DEM check in audit_biota can tell them from an omission.
DROWNED_LAND_OK = {"West Antarctic Rift", "Zealandia", "Kerguelen Microcontinent",
                   "Mauritia", "Jan Mayen Microcontinent", "Seychelles Microcontinent"}
#: The submerged labels that are not deep water: shallow banks and young seas.
SUBMERGED_HAB = {"Mascarene Plateau": {"reef", "shelf", "pelagic"},
                 "Wrangellia Terrane": {"reef", "shelf", "pelagic", "coast"},
                 "Wallacea": {"reef", "shelf", "pelagic", "coast"},
                 "Red Sea Rift": {"reef", "shelf", "pelagic", "coast"},
                 "Gulf of California": {"shelf", "pelagic", "coast", "reef"}}

_DEEP_NAME = re.compile(r"\b(Ridge|Rise|Seamounts?|Plateau|Trench|Fracture Zone)\b")
#: Hotspot tracks, plateaus and other highs that never spread: deep water, no vents.
_NO_VENTS = {"Ninetyeast Ridge", "Nazca Ridge", "Emperor Seamounts", "Walvis Ridge",
             "Broken Ridge", "Rio Grande Rise", "Shatsky Rise"}
POLAR_LAT = 70.0
ARCTIC_ICE_FROM = 2.6
#: Antarctica kept a Nothofagus tundra under its first ice sheets; the mid-Miocene
#: cooling (about 14 Ma) ended it, and the interior has been polar desert since.
ANTARCTIC_DESERT_FROM = 14.0
LPIA = (335.0, 290.0)     # the peak: by the Sakmarian, Glossopteris forest stood at 70 S


def submerged(lab, age):
    if lab["n"] not in SUBMERGED:
        return False
    span = SUBMERGED[lab["n"]]
    return span is None or min(span) - 1e-9 <= age <= max(span) + 1e-9


def is_marine(lab, age):
    return lab["t"] in MARINE_TYPES or submerged(lab, age)


def is_polar(lab, age, plat):
    """Ice-age ground poleward of 70 degrees: tundra or ice, whatever the label's
    type implies. The Ellesmerian Belt is an orogen and its type says "alpine,
    forest"; at 80 N in the Quaternary that put beaver, bison and lodgepole pine
    on Ellesmere Island. Before the ice the same ground WAS forest, so the rule
    has a date on each pole."""
    if plat is None or abs(plat) < POLAR_LAT or is_marine(lab, age):
        return False
    # the Late Palaeozoic ice age: Gondwana's pole under ice from the
    # Serpukhovian to the early Permian (335-260 Ma)
    if LPIA[1] <= age <= LPIA[0]:
        return True
    return age <= (ANTARCTIC_DESERT_FROM if plat < 0 else ARCTIC_ICE_FROM)


def label_habitats(lab, age=0.0, plat=None):
    if is_polar(lab, age, plat) and lab["t"] != "lake":
        return {"tundra", "ice"} | ({"coast", "island"} if lab["t"] == "island" else set())
    if lab["n"] in NAME_HABITAT:
        return NAME_HABITAT[lab["n"]]
    since = HABITAT_SINCE.get(lab["n"])
    if since and age <= since[0] and not is_marine(lab, age):
        return since[1]
    if submerged(lab, age) and lab["n"] in SUBMERGED_HAB:
        return SUBMERGED_HAB[lab["n"]]
    if is_marine(lab, age) and _DEEP_NAME.search(lab["n"]):
        deep = {"deep", "pelagic"}
        if lab["t"] in MARINE_TYPES and lab["n"] not in _NO_VENTS:
            deep.add("vent")
        return deep
    if submerged(lab, age):
        return {"deep", "pelagic"}
    return TYPE_HABITAT.get(lab["t"])


# ------------------------------------------------------------ the footprint --
#: How far, in degrees, a label of each type reaches from its own point. A region
#: code is continent-sized, and inside one a narrow endemic needs a finer address:
#: `box` on a taxon is that address, in present-day coordinates like the codes
#: themselves, and a label whose point lies further from every box than its reach
#: does not show the taxon. None = the label is as wide as its codes and boxes do
#: not apply (a continent is home to all its endemics; so is an ocean).
TYPE_REACH = {"continent": 6.0, "ocean": None, "orogen": 3.0, "plateau": 4.0, "desert": 5.0,
              "forest": 5.0, "grassland": 6.0, "tundra": 8.0, "basin": 3.0, "rift": 4.0,
              "region": 4.0, "craton": 4.0, "terrane": 3.0, "island": 2.0, "lake": 1.5,
              "sea": 5.0}
#: Long or wide features whose single point says little about their extent.
NAME_REACH = {"North America": None, "South America": None, "Africa": None, "Eurasia": None,
              "Australia": None, "Antarctica": None, "India": None, "Siberia": None,
              # a number is a radius in degrees; a pair is (half-width in degrees of
              # longitude, half-height in degrees of latitude) for features that are
              # long one way and narrow the other
              "Andes": (7.0, 38.0), "Cordillera": (9.0, 22.0), "Rocky Mountains": (7.0, 12.0),
              "Himalaya": (14.0, 3.5), "Tibetan Plateau": (12.0, 4.5),
              "Tibetan Alpine Tundra": (12.0, 4.5), "Kunlun Belt": (12.0, 2.5),
              "Tien Shan": (10.0, 3.0), "Altai Belt": (6.0, 3.0), "Qilian Belt": (5.0, 2.5),
              "Ural Mountains": (3.5, 10.0), "Appalachians": (7.0, 7.0), "Atlas": (8.0, 3.0),
              "Alps": (6.0, 2.5), "Carpathians": (5.0, 3.0), "Apennines": (3.5, 3.5),
              "Pyrenees": (3.5, 1.5), "Greater Caucasus": (5.0, 2.0), "Zagros Mts": (6.0, 5.0),
              "Alborz Belt": (5.0, 2.0), "Pontide Arc": (7.0, 2.0), "Caledonides": (14.0, 8.0),
              "Verkhoyansk Belt": (12.0, 7.0), "Southern Alps": (3.5, 3.0),
              "Cape Fold Belt": (6.0, 2.5), "Qinling-Dabie Belt": (7.0, 3.0),
              "Ellesmerian Belt": (30.0, 5.0), "Transantarctic Mts": (180.0, 12.0),
              "Great Dividing Range": (5.0, 14.0), "Lachlan Orogen": (5.0, 5.0),
              "East African Rift": (5.0, 14.0), "Eurasian Steppe": (42.0, 6.0),
              "Sahara": (24.0, 8.0), "Amazon Rainforest": (14.0, 9.0),
              "African Savanna": (14.0, 14.0), "Arctic Tundra": (70.0, 6.0),
              "Nearctic Tundra": (40.0, 8.0), "Great Plains": (6.0, 12.0),
              "Australian Desert": (14.0, 8.0), "Arabian Desert": (9.0, 9.0),
              "Canadian Shield": (25.0, 8.0), "Brazilian Shield": (10.0, 10.0),
              "Guiana Shield": (8.0, 4.0), "Sundaland": (12.0, 9.0), "Sahul": (16.0, 12.0),
              "Wallacea": (9.0, 7.0), "Beringia": (16.0, 6.0),
              "Beringian Steppe-Tundra": (16.0, 6.0), "Zealandia": (10.0, 10.0),
              "Greenland": (16.0, 11.0), "Congo Basin": (8.0, 7.0), "Kalahari Desert": (6.0, 6.0),
              "Patagonian Desert": (5.0, 8.0), "West Siberian Basin": (12.0, 8.0),
              "Fennoscandian Shield": (12.0, 6.0), "Amuria": (12.0, 5.0),
              "Tarim Block": (8.0, 3.0), "Annamia": (5.0, 7.0),
              "Anatolide-Tauride Block": (7.0, 2.5), "Central Asian Orogenic Belt": (30.0, 6.0),
              "Mauritia": 6.0, "Seychelles Microcontinent": 3.0,
              "Kerguelen Microcontinent": 8.0, "Jan Mayen Microcontinent": 3.0}


def label_point(lab):
    """The label's PRESENT-DAY point (lon, lat), or None when it has none: a
    track that starts at 0 Ma, or an untracked label of the last 20 Myr. A
    palaeo-frame label's coordinate is where the feature sat in its own era and
    says nothing about today's map."""
    tr = lab.get("tr")
    if tr:
        return (tr[0][1], tr[0][2]) if tr[0][0] <= 0.011 else None
    if lab.get("lon") is None:
        return None
    if min(lab.get("a0", 0), lab.get("a1", 0)) <= 0.011 or \
            max(lab.get("a0", 0), lab.get("a1", 0)) <= 20:
        return lab["lon"], lab["lat"]
    return None


def label_reach(lab):
    if lab["n"] in NAME_REACH:
        return NAME_REACH[lab["n"]]
    if lab["t"] == "ocean" and _DEEP_NAME.search(lab["n"]):
        return 12.0                       # a ridge is a line on the map, not a basin
    return TYPE_REACH.get(lab["t"], 4.0)


def in_reach(e, lab, age=0.0):
    """Does this label's footprint touch any of the taxon's boxes at this age?
    `avoid` is the blunt instrument for what a point and a reach cannot say: the
    Alps and the northern Apennines are two degrees apart and share no ibex."""
    if lab["n"] in (e.get("avoid") or ()):
        return False
    live = [b for old, young, b in e["_box"] if young - 1e-9 <= age <= old + 1e-9]
    if not live:
        return True
    reach = label_reach(lab)
    pt = label_point(lab)
    if reach is None or pt is None:
        return True
    x, y = pt
    if isinstance(reach, tuple):
        rx, ry = reach
    else:
        ry = reach
        rx = reach / max(0.35, math.cos(math.radians(max(-80.0, min(80.0, y)))))
    for w, east, south, north in live:
        if south - ry <= y <= north + ry:
            if w - rx <= x <= east + rx or w - rx <= x + 360 <= east + rx \
                    or w - rx <= x - 360 <= east + rx:
                return True
    return False


def lat_at(lab, age):
    """Palaeolatitude from the label's own track, as provinces.py reads it."""
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


# ---------------------------------------------------------------- composer --
#: The first land animals are Silurian and the first land plants Middle
#: Ordovician; before them a "land" card has nothing of its own to show, and
#: what a reader wants is the life of the seas that lay across it.
NO_LAND_LIFE_BEFORE = 470.0
SHELF_TOO_BEFORE = 385.0          # until forests, a continent's card also shows its seas
N_FAUNA, N_FLORA, N_OTHER = 4, 4, 2
N_TOTAL = 8


def realm_ok(e, want):
    """A penguin is a land animal on an Antarctic card and a sea animal on a
    Southern Ocean one. `realms` lists every realm a taxon belongs on; `realm`
    alone is the one it is tinted as."""
    return any(r in want for r in (e.get("realms") or (e["realm"],)))


#: Trees. One with no stated habitat is still not at home in a desert, on
#: tundra or on an ice sheet, and "no habitat given" must not be read as "any".
_TREE_FORMS = {"broadleaf", "conifer", "pine", "araucaria", "redwood", "ginkgo", "eucalypt",
               "baobab", "palm", "treefern", "lycopod", "progymnosperm", "cordaite", "mangrove",
               "vine", "bromeliad", "bamboo"}
_TREELESS = {"desert", "tundra", "ice"}


def hab_ok(e, habs, strict=False):
    """A taxon with a stated habitat does not appear on a card of another one.
    A taxon with none, or a card with none, is unconstrained -- except that a
    tree is never assumed onto treeless ground."""
    if not habs:
        return True
    if not e["_hab"]:
        # Polar ground takes nothing on trust: "no habitat stated" has meant
        # dragonflies on Jan Mayen and water lilies under the Antarctic ice.
        if strict:
            return False
        return not (habs <= _TREELESS and e["form"] in _TREE_FORMS)
    return bool(habs & e["_hab"])


def lat_ok(e, plat, age=0.0):
    """Within its latitude band at this age. The band may be sliced by time:
    palms stood at 70 degrees in the Eocene and stop near 40 today."""
    if not e["_lat"] or plat is None:
        return True
    hit = [(lo, hi) for old, young, lo, hi in e["_lat"] if young - 1e-9 <= age <= old + 1e-9]
    if not hit:
        return True
    return any(lo - 1e-9 <= abs(plat) <= hi + 1e-9 for lo, hi in hit)


def _score(e, age, habs):
    s = 0.0
    b = breadth(e, age)
    s += 40.0 / b if b else 0.0                       # place-specific first
    if habs and e["_hab"] and (habs & e["_hab"]):
        s += 25.0
    elif habs and not e["_hab"] and e["lad"] == 0:
        # On a card that names its habitat, "no habitat stated" is the weakest
        # claim there is -- it is how a capuchin monkey reached the Atacama. Only
        # for LIVING taxa, whose habitats are known: a Permian reptile, or a
        # ground sloth, has no habitat tag because nobody can give it one.
        s -= 35.0
    if habs and "lake" in habs and e["realm"] == "fresh":
        s += 20.0
    s += 10.0 * float(e.get("w", 2))
    span = max(1.0, float(e["fad"]) - float(e["lad"]))
    s += 15.0 / (1.0 + math.log10(span))              # time-specific next
    # A class or a phylum is true of everywhere and says nothing about here.
    s += {"species": 8, "subspecies": 8, "genus": 8, "family": 3, "subfamily": 3,
          "tribe": 3, "order": -4, "suborder": -4, "class": -14, "subclass": -12,
          "phylum": -18, "kingdom": -20, "domain": -20, "clade": -8,
          "informal": -4}.get(e.get("rank"), 0)
    # What lived here THEN and does not now is the more telling half of a past
    # card: at 1 Ma a Patagonian card should lead with Megatherium, not only with
    # the guanaco that is still there.
    if float(e["lad"]) > 0:
        s += 26.0
    if e.get("assemblage"):
        s -= 30.0
    return s


def _section(e):
    k = e.get("kind")
    if e.get("assemblage"):
        k = FORMS[e["form"]]["kind"]
    if k in FAUNA_KINDS:
        return "fauna"
    if k in FLORA_KINDS:
        return "flora"
    return "other"


def _pick(cands, quota, age, habs, chosen):
    """Greedy, best first, with a penalty for repeating a body form."""
    forms, genera, reps = {}, set(), set()
    for e in chosen:
        forms[e["form"]] = forms.get(e["form"], 0) + 1
        genera.add(_genus(e))
        if e.get("rep"):
            reps.add(e["rep"])
    out = []
    pool = list(cands)
    while pool and len(out) < quota:
        best, bs = None, -1e18
        # "Alces" beside "Alces alces" is one animal listed twice; so is "kelp"
        # beside the Macrocystis that stands for it
        pool = [(e, b) for e, b in pool if _genus(e) not in genera
                and e.get("rep") not in genera and e["n"] not in reps]
        for e, base in pool:
            s = base - 30.0 * forms.get(e["form"], 0)
            if s > bs or (s == bs and best is not None and e["n"] < best[0]["n"]):
                best, bs = (e, base), s
        if best is None:
            break
        pool.remove(best)
        out.append(best[0])
        forms[best[0]["form"]] = forms.get(best[0]["form"], 0) + 1
        genera.add(_genus(best[0]))
        if best[0].get("rep"):
            reps.add(best[0]["rep"])
    return out


def _genus(e):
    """First word of a Latin name; the whole name for anything informal."""
    n = e["n"]
    w = n.split()[0]
    return w if w[:1].isupper() and w[1:].islower() and e.get("rank") in (
        "genus", "species", "subspecies", "subgenus") else n


_ALIVE, _PLACED = {}, {}


def _alive_at(age):
    """Registry taxa alive at `age` that may be used as general fill."""
    if age not in _ALIVE:
        _ALIVE[age] = [e for e in load()["taxa"].values()
                       if e.get("fill") is not False and alive(e, age)]
    return _ALIVE[age]


def _placed(home, age, want):
    """Fill candidates alive at `age`, of the right realm, at home on `home`.

    Cached: three hundred labels share a few dozen home crusts, and asking the
    whole registry the same question for each of them at each of a thousand
    ages is most of what a build would otherwise spend its time on.
    """
    key = (frozenset(home), age, tuple(want))
    if key not in _PLACED:
        _PLACED[key] = [e for e in _alive_at(age)
                        if realm_ok(e, want) and at_home(e, home, age, sea_card="sea" in want)]
    return _PLACED[key]


def compose(lab, age, home, prov_markers=(), curated=None, exception=False, only=False):
    """The organisms this label's card shows at this age.

    Returns {"groups": [(key, [entries])], "src": {name: 'curated'|'province'|
    'registry'}, "dropped": [(name, why)]}. Group keys: fauna, flora, other for
    the label's own realm; and for a land label before the forests, the same
    three again prefixed "shelf-" for the seas that covered it.
    """
    reg = load()["taxa"]
    marine = is_marine(lab, age)
    lake = lab["t"] == "lake"
    plat = lat_at(lab, age)
    habs = label_habitats(lab, age, plat)
    polar = is_polar(lab, age, plat)
    dropped, src = [], {}

    def eligible(e, want, strict_place=True, use_hab=True):
        if not alive(e, age):
            return "not alive at this age"
        if not realm_ok(e, want):
            return "wrong realm"
        if strict_place and home is not None and \
                not at_home(e, home, age, sea_card="sea" in want):
            return "not at home on this crust"
        if strict_place and not in_reach(e, lab, age):
            return "outside its own range within this region"
        if not lat_ok(e, plat, age):
            return "outside its latitude band"
        if use_hab and not hab_ok(e, habs, polar):
            return "wrong habitat"
        return None

    def gather(want, use_hab=True, curated_only=False, skip=()):
        ranked, seen = [], set(skip)
        # 1. curated: authority over place, none over time
        for name in curated or ():
            e = get(name)
            if e is None:
                dropped.append((name, "not in the registry"))
                continue
            why = eligible(e, want, strict_place=False, use_hab=False)
            # A curated list has authority over WHERE -- but not over a taxon
            # the registry says arrives here later or has already left. Hipparion
            # is Eurasian from 11 Ma and a list spanning 5-23 Ma does not make
            # it Eurasian at 15.
            if not why and home is not None and not at_home(e, home, age, ice=False) \
                    and _ever_home(e, home):
                why = "not here yet, or already gone"
            if why:
                if why != "wrong realm":
                    dropped.append((name, why))
                continue
            if e["n"] not in seen:
                seen.add(e["n"])
                src[e["n"]] = "curated"
                ranked.append((e, 1000.0 - len(ranked)))
        # An exception locality speaks for itself -- unless its own taxa are
        # not alive at this age, in which case saying nothing is worse than
        # letting the model fill in around it.
        if curated_only or (exception and len(ranked) >= 4):
            return ranked
        # "only": the curated list is ALL there is (Lake Vostok, sealed under the
        # ice), and the model must not furnish the place with plausible neighbours
        if only and ranked:
            return ranked
        # 2. the province's markers, where they really were and when
        for name in prov_markers:
            e = get(name)
            if e is None:
                dropped.append((name, "province marker not in the registry"))
                continue
            if e["n"] in seen:
                continue
            why = eligible(e, want, use_hab=use_hab)
            if why:
                if why != "wrong realm":
                    dropped.append((name, why))
                continue
            seen.add(e["n"])
            src[e["n"]] = "province"
            ranked.append((e, 500.0 + _score(e, age, habs)))
        # 3. everything else the registry places here and now
        if home is not None:
            for e in _placed(home, age, want):
                if e["n"] in seen:
                    continue
                if not lat_ok(e, plat, age) or (use_hab and not hab_ok(e, habs, polar)):
                    continue
                if not in_reach(e, lab, age):
                    continue
                seen.add(e["n"])
                src[e["n"]] = "registry"
                ranked.append((e, _score(e, age, habs)))
        return ranked

    def split(ranked, n_total=N_TOTAL, sea=False):
        by = {"fauna": [], "flora": [], "other": []}
        for e, s in ranked:
            by[_section(e)].append((e, s))
        for k in by:
            by[k].sort(key=lambda t: (-t[1], t[0]["n"]))
        quota = {"fauna": N_FAUNA, "flora": N_FLORA, "other": N_OTHER}
        # One assemblage at most, and never ahead of a real organism.
        for k in by:
            seen_asm = False
            kept = []
            for e, s in by[k]:
                if e.get("assemblage"):
                    if seen_asm:
                        continue
                    seen_asm = True
                kept.append((e, s))
            by[k] = kept
        # Unused slots pass to whichever section has more to show.
        have = {k: min(len(by[k]), quota[k]) for k in by}
        spare = n_total - sum(have.values())
        for k in ("fauna", "flora", "other"):
            extra = min(spare, len(by[k]) - have[k], 2)
            if extra > 0:
                have[k] += extra
                spare -= extra
        # microbes and sediment only count when there is little else to show:
        # nobody opens a card for Holocene North America to read about amoebae
        if have["fauna"] + have["flora"] >= 6 and not sea:
            have["other"] = 0
        elif have["fauna"] + have["flora"] >= 5:
            have["other"] = min(have["other"], 1)
        # A phylum is true of every sea there has ever been. Where the card can be
        # filled with something more particular, the generic entries stand down;
        # where it cannot (much of the Precambrian), they are what there is.
        _GENERIC = ("phylum", "kingdom", "domain", "class", "subphylum", "subclass")
        spec = {k: [(e, sc) for e, sc in by[k]
                    if e.get("rank") not in _GENERIC or src.get(e["n"]) == "curated"]
                for k in by}
        if sum(min(len(spec[k]), have[k]) for k in ("fauna", "flora")) >= 5:
            by = spec
        # A CURATED class-level name ("Brachiopoda", "Ichthyosauria") is a
        # reader's note about the place, and it keeps one slot; but when the
        # registry can name four animals of that sea by genus, the rest of the
        # card is theirs. A sea whose every fauna is a phylum reads as a lesson.
        _BROAD = _GENERIC + ("order", "superorder", "infraorder", "suborder")
        real = [(e, sc) for e, sc in by["fauna"] if e.get("rank") not in _BROAD]
        if len(real) >= 4:
            gen = [(e, sc) for e, sc in by["fauna"] if e.get("rank") in _BROAD]
            by["fauna"] = sorted(real + gen[:1], key=lambda t: (-t[1], t[0]["n"]))
        chosen, groups = [], []
        for k in ("fauna", "flora", "other"):
            got = _pick(by[k], have[k], age, habs, chosen)
            chosen += got
            # a Lagerstaette is where the animals were found, not one of them
            got = [e for e in got if not e.get("assemblage")] + \
                  [e for e in got if e.get("assemblage")]
            if got:
                groups.append((k, got))
        return groups

    groups = []
    if marine:
        groups = split(gather(LABEL_REALMS.get(lab["n"], ["sea"])), sea=True)
        if lab["t"] not in MARINE_TYPES:
            # a sea card on a label the app does not know to be sea: say so in the key
            groups = [("sea-" + k, v) for k, v in groups]
        # A lagoon's fame can be what fell into it. Curated land and air taxa on
        # a sea card (Archaeopteryx at Solnhofen) were being dropped as "wrong
        # realm"; they are the author's statement and get their own heading.
        # skip everything the main pass already weighed (src), not only what it
        # kept: a curated plankter the quota cut must not resurface as shore life
        shore = split(gather(["land", "air", "fresh"], use_hab=False, curated_only=True, skip=set(src)), 4)
        groups += [("shore-" + k, v) for k, v in shore]
    elif age > NO_LAND_LIFE_BEFORE:
        land = split(gather(["land", "fresh"], use_hab=False), 2)
        shelf = split(gather(["sea"], use_hab=False), sea=True)
        groups = land + [("shelf-" + k, v) for k, v in shelf]
    elif age > SHELF_TOO_BEFORE:
        land = split(gather(["land", "air", "fresh"], use_hab=False), 5)
        shelf = split(gather(["sea"], use_hab=False), 4, sea=True)
        groups = land + [("shelf-" + k, v) for k, v in shelf]
    else:
        want = ["fresh", "land", "air"] if lake else ["land", "air", "fresh"]
        groups = split(gather(want))
        # ... and the seas a curated list says lay across this land: Basilosaurus
        # in the Fayum on Africa's Eocene card, the Muschelkalk's nothosaurs on
        # Eurasia's Triassic one. Curated only; the model never invents a sea.
        shelf = split(gather(["sea"], use_hab=False, curated_only=True, skip=set(src)), 4, sea=True)
        groups += [("shelf-" + k, v) for k, v in shelf]
    return {"groups": groups, "src": src, "dropped": dropped}


# ------------------------------------------------------------- card builder --
#: A Pleistocene feature drawn on the present-day frame is still a Pleistocene
#: feature. Each frame stands for a million years, so Beringia and Lake
#: Bonneville are both on the map at "0 Ma"; their cards should show the
#: mammoth steppe and the pluvial lake, not what lives in the Bering Strait
#: today. The biota age is never younger than this -- and never younger than the
#: label's own window, which is what gives every ice-dammed lake its true age
#: without being listed here.
LABEL_BIOTA_AGE = {
    "Beringia": 0.02, "Beringian Steppe-Tundra": 0.02, "Sundaland": 0.02,
    "Sahul": 0.05, "Doggerland": 0.012,
}


def label_window(lab):
    lo, hi = min(lab["a0"], lab["a1"]), max(lab["a0"], lab["a1"])
    return lo, hi


def app_ages(lab):
    """The whole-Myr ages at which the app can show this label's card."""
    lo, hi = label_window(lab)
    if hi < 0:
        return []
    lo = max(lo, 0.0)
    a0, a1 = int(math.floor(lo)), int(math.ceil(hi))
    return list(range(a0, a1 + 1))


def biota_age(lab, app_age):
    """The age the biota is composed for, given the age on the slider."""
    lo, hi = label_window(lab)
    floor_ = max(lo, LABEL_BIOTA_AGE.get(lab["n"], 0.0), 0.0)
    return min(max(float(app_age), floor_), max(hi, floor_))


def _province_at(runs, age):
    """Province id from provinces.build() runs, with the app's own tolerance."""
    best = None
    for a0, a1, pid in runs or ():
        if a0 - 2.5 <= age <= a1 + 2.5:
            return pid
        d = min(abs(age - a0), abs(age - a1))
        if best is None or d < best[0]:
            best = (d, pid)
    return None


def curated_at(spans, age):
    """Every curated span holding `age`, merged: a label's spans were authored
    at different times by different hands and twelve pairs overlap (Africa
    30-56 and 33-56). Taking the first silently lost the second's taxa --
    Basilosaurus never reached Africa's Eocene card. Order is kept; a name
    appears once; `exception` and `only` hold if any span says so."""
    hits = [s for s in spans or ()
            if min(s["a0"], s["a1"]) - 1e-9 <= age <= max(s["a0"], s["a1"]) + 1e-9]
    if not hits:
        return None
    if len(hits) == 1:
        return hits[0]
    merged = dict(hits[0])
    seen, taxa = set(), []
    for h in hits:
        for t in h.get("taxa", []):
            nm = t[0] if isinstance(t, (list, tuple)) else t["name"]
            if nm not in seen:
                seen.add(nm)
                taxa.append(t)
    merged["taxa"] = taxa
    merged["exception"] = any(h.get("exception") for h in hits)
    merged["only"] = any(h.get("only") for h in hits)
    shared = [h["shared"] for h in hits if h.get("shared")]
    if shared:
        merged["shared"] = " ".join(dict.fromkeys(shared))
    return merged


def build_cards(labels, prov_recs, prov_runs, curated, icons, features=None, log=print):
    """(taxa_table, cards, stats) for life.json.

    cards[label] = {"r": [[a_lo, a_hi, tier, prov_id, groups, shared?], ...],
                    "n": {taxon id: note local to this label}} over whole-Myr APP
    ages, run-length encoded; groups = [[key, [taxon ids]], ...].
    tier: 'x' curated exception, 'c' curated + model, 'p' province + model,
    'r' regional (no named province).
    """
    reg = load()["taxa"]
    ids, table = {}, []

    def tid(e):
        if e["n"] not in ids:
            ids[e["n"]] = len(table)
            ic, how = icon_for(e["n"], icons)
            rec = {"n": e["n"], "r": e.get("rank"), "realm": e["realm"],
                   "k": _section(e), "kd": e.get("kind") or "",
                   "note": e.get("note", ""), "ic": ic or ""}
            for k_src, k_dst in (("sz", "sz"), ("dt", "dt"), ("hb", "hb")):
                if e.get(k_src):
                    rec[k_dst] = e[k_src]
            table.append(rec)
        return ids[e["n"]]

    cards, stats = {}, {"labels": 0, "runs": 0, "homeless": [], "dropped": {}}
    for lab in labels:
        if lab["t"] not in CARD_TYPES:
            continue
        ages = app_ages(lab)
        if not ages:
            continue
        if label_home(lab, features) is None:
            stats["homeless"].append(lab["n"])
        spans = curated.get(lab["n"])
        runs, label_notes = [], {}
        # ages an earlier label of the same name already answers for
        taken = {x for r in (cards.get(lab["n"]) or {}).get("r", ()) for x in range(r[0], r[1] + 1)}
        for a in ages:
            if a in taken:
                continue
            ba = biota_age(lab, a)
            home = label_home(lab, features, ba)
            span = curated_at(spans, ba)
            names, local = [], {}
            if span:
                for t in span.get("taxa", []):
                    nm = t[0] if isinstance(t, (list, tuple)) else t["name"]
                    note = t[3] if isinstance(t, (list, tuple)) else t.get("note")
                    names.append(nm)
                    if note:
                        local[nm] = note
            pid = _province_at(prov_runs.get(lab["n"]), ba)
            prec = prov_recs.get(pid) if pid is not None else None
            marine = is_marine(lab, ba)
            if prec and (prec.get("r") == "marine") != marine and ba <= SHELF_TOO_BEFORE:
                prec, pid = None, None
            # An ocean island belongs to no continental realm: Jan Mayen was headed
            # "Nearctic", with a paragraph about Beringia.
            if prec and not marine and home and set(home) <= set(BASINS):
                prec, pid = None, None
            # A LATITUDE band is a statement about lowland climate, and printed
            # over a label that names its own habitat it contradicts the card it
            # heads: "subtropical desert and savanna belt" over the Himalaya,
            # "tropical rainforest belt" over the African Savanna. Named provinces
            # -- decided by block or by age -- stay; a bare band gives way to a
            # label that already says what kind of place it is. Its markers still
            # feed the composer.
            dated = HABITAT_SINCE.get(lab["n"])
            if prec and prec.get("b") == "latitude" and ba <= 66 and \
                    (lab["t"] in ("orogen", "plateau", "desert", "grassland", "forest",
                                  "tundra", "lake", "island")
                     or (dated and ba <= dated[0]) or is_polar(lab, ba, lat_at(lab, ba))):
                markers_only = prec
                prec, pid = None, None
            else:
                markers_only = None
            # A suppressed band's markers are not given a province's priority:
            # they are generic to a latitude, every one of them is in the registry
            # anyway, and there they compete on the merits with what is local.
            c = compose(lab, ba, home,
                        prov_markers=(prec or {}).get("markers", ()),
                        curated=names, exception=bool(span and span.get("exception")),
                        only=bool(span and span.get("only")))
            for nm, why in c["dropped"]:
                stats["dropped"].setdefault(why, set()).add((lab["n"], nm))
            if not c["groups"]:
                continue
            any_cur = any(v == "curated" for v in c["src"].values())
            tier = ("x" if span and span.get("exception") else
                    "c" if any_cur else "p" if pid is not None else "r")
            groups, notes = [], {}
            for key, es in c["groups"]:
                groups.append([key, [tid(e) for e in es]])
                for e in es:
                    ln = local.get(e["n"])
                    if ln is None:
                        for aka in e.get("aka", ()):
                            ln = ln or local.get(aka)
                    if ln and ln != e.get("note"):
                        notes[str(ids[e["n"]])] = ln
            label_notes.update(notes)
            rec = [a, a, tier, pid, groups]
            cur_ids = sorted(ids[n] for n, v in c["src"].items() if v == "curated" and n in ids
                             and str(ids[n]) in notes)
            if (span and span.get("shared")) or cur_ids:
                rec.append(span.get("shared") if span else None)
            if cur_ids:
                rec.append(cur_ids)
            if runs and runs[-1][2:] == rec[2:] and runs[-1][1] == a - 1:
                runs[-1][1] = a
            else:
                runs.append(rec)
        if runs:
            # Local notes are hoisted to the label: a curated sentence about a
            # taxon AT THIS PLACE is the same in every run it appears in, and
            # repeating it per run was half the payload.
            # A name can be on the map twice (North China is one label to 420 Ma
            # and another before it), and the app looks a card up by name, so the
            # two windows have to share one entry rather than overwrite it.
            prev = cards.get(lab["n"])
            if prev:
                prev["r"] = sorted(prev["r"] + runs, key=lambda r: r[0])
                if label_notes:
                    prev.setdefault("n", {}).update(label_notes)
            else:
                cards[lab["n"]] = ({"r": runs, "n": label_notes} if label_notes
                                   else {"r": runs})
            stats["labels"] += 1
            stats["runs"] += len(runs)
    log(f"  biota: {stats['labels']} labels carry composed cards in {stats['runs']} runs, "
        f"drawing on {len(table)} of {len(reg)} registry taxa")
    if stats["homeless"]:
        log(f"  biota: {len(stats['homeless'])} labels have NO home crust and get no "
            f"registry fill -- add them to biota.LABEL_HOME: "
            + ", ".join(sorted(stats["homeless"])[:8]))
    for why, hits in sorted(stats["dropped"].items()):
        log(f"  biota: {len(hits)} curated/province listings withheld ({why}), e.g. "
            + "; ".join(f"{n} on {l}" for l, n in sorted(hits)[:3]))
    return table, cards, stats


# ---------------------------------------------------------------------- CLI --
def _labels():
    with open(os.path.join(WEB, "labels.json")) as f:
        return json.load(f)


def check_file(path, evidence=None):
    """Validate ONE registry file on its own -- what an author runs before
    handing it in. Cross-file rules (duplicate names, `rep` targets defined
    elsewhere) are left to the full --check."""
    with open(path) as f:
        d = json.load(f)
    side = {}
    if evidence and os.path.exists(evidence):
        with open(evidence) as f:
            side = json.load(f)
    reg = {}
    for name, e in (d.get("taxa") or {}).items():
        e = dict(e)
        e["n"] = name
        e["_file"] = os.path.basename(path)
        if "pbdb" not in e and side.get(name):
            e["pbdb"] = side[name]
        try:
            _prepare(e)
        except ValueError as err:
            print(f"  INVALID {name}: {err}")
            e["_slices"], e["_hab"] = [], set()
        reg[name] = e
    bad = [b for b in validate(reg) if " rep " not in b]
    rev = review(reg)
    for b in bad:
        print("  INVALID", b)
    for sev, name, msg in rev:
        print(f"  {sev:9s} {name}: {msg}")
    print(f"{os.path.basename(path)}: {len(reg)} taxa, {len(bad)} invalid, "
          f"{len(rev)} to review")
    return 1 if bad else 0


def _main(argv):
    if "--check-file" in argv:
        ev = argv[argv.index("--evidence") + 1] if "--evidence" in argv else None
        return check_file(argv[argv.index("--check-file") + 1], ev)
    if "--check" in argv:
        reg = load()["taxa"]
        bad = validate(reg)
        rev = review(reg)
        by = {}
        for e in reg.values():
            by[e.get("kind")] = by.get(e.get("kind"), 0) + 1
        print(f"registry: {len(reg)} taxa in {len(registry_files())} files  "
              + ", ".join(f"{v} {k}" for k, v in sorted(by.items(), key=lambda kv: -kv[1])))
        for b in bad[:60]:
            print("  INVALID", b)
        for sev, name, msg in rev[:80]:
            print(f"  {sev:9s} {name}: {msg}")
        print(f"registry invalid entries: {len(bad)}")
        print(f"registry form findings: {sum(1 for r in rev if r[0] == 'FORM')}")
        print(f"registry range findings: {sum(1 for r in rev if r[0].startswith('RANGE'))}")
        print(f"registry place findings: {sum(1 for r in rev if r[0] == 'PLACE')}")
        return 1 if bad else 0
    if "--card" in argv:
        i = argv.index("--card")
        name, ages = argv[i + 1], [float(a) for a in argv[i + 2:]] or [0.0]
        import features                                       # noqa: PLC0415
        lab = next(l for l in _labels() if l["n"] == name)
        print(f"{name} [{lab['t']}] point={label_point(lab)} reach={label_reach(lab)}")
        for a in ages:
            home = label_home(lab, features, a)
            c = compose(lab, a, home)
            print(f"  --- {a:g} Ma (palaeolat {lat_at(lab, a)}) home={sorted(home or [])} "
                  f"habitats={sorted(label_habitats(lab, a, lat_at(lab, a)) or [])}"
                  f"{' SEA' if is_marine(lab, a) else ''}")
            for k, es in c["groups"]:
                print(f"    {k:12s} " + "; ".join(f"{e['n']} [{e['form']}]" for e in es))
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
