"""A province model for deep-time biogeography.

Tectonic Earth currently assigns biota to named labels one region at a time. That
does not scale and leaves gaps: 32 of 55 marine labels once fell through to a
single global list, so every ocean showed the same animals. The fix required by
the project's standing rule ("fix the system, not the instance") is a MODEL:

    province(age, lat, realm)                 -> which biogeographic province
    provinciality(age)                        -> how differentiated the world is
    expected_provinces(age, realm)            -> the full province list for an age

Provinces are set by BARRIERS first and GRADIENTS second. Barriers come from the
plate model (which is why `block=` may be supplied); gradients come from latitude.
Where the record does not support a named province the model says so instead of
inventing one - `Province.confidence == 'none'` is a legitimate answer.

Sources: research/06-paleobiology/01-biogeographic-provinces-through-time.md
Depends only on the sibling modules deeptime.py and paleogeography.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import deeptime
import paleogeography as pg

__all__ = ["Province", "province", "expected_provinces", "provinciality",
           "MARINE_SCHEMES", "TERRESTRIAL_SCHEMES"]


@dataclass(frozen=True)
class Province:
    name: str
    realm: str                 # marine | terrestrial
    basis: str                 # what decided it: 'block', 'latitude', 'both', 'default'
    confidence: str            # good | moderate | none
    note: str = ""
    markers: tuple = ()        # diagnostic taxa or assemblages

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.realm} province {self.name} ({self.confidence})>"


# ---------------------------------------------------------------------------
# Latitude bands. These are the fallback gradient when no named scheme applies,
# and the input to most named schemes as well.
# ---------------------------------------------------------------------------

def _band(lat: float) -> str:
    a = abs(lat)
    if a >= 66.5:
        return "polar"
    if a >= 45:
        return "cool temperate"
    if a >= 30:
        return "warm temperate"
    if a >= 15:
        return "subtropical"
    return "tropical"


def _hemisphere(lat: float) -> str:
    return "north" if lat >= 0 else "south"


# ---------------------------------------------------------------------------
# Named MARINE schemes, oldest first. Each is (base, top, resolver).
# A resolver takes (age, lat, block) and returns a Province or None.
# ---------------------------------------------------------------------------

_OLENELLID = ("Laurentia", "Baltica", "Siberia")


def _cambrian_marine(age, lat, block):
    if block in _OLENELLID:
        return Province("Olenellid Province", "marine", "block", "good",
                        "Endemic olenellid trilobites (Olenellus, Holmia, Schmidtiellus, "
                        "Kjerulfia) plus pandemic ellipsocephaloids and eodiscids.",
                        ("Olenellus", "Holmia", "Schmidtiellus", "Kjerulfia"))
    if block and block in pg.ASSEMBLIES["Gondwana"]["members"] + ["South China", "North China"]:
        return Province("Redlichiid Province", "marine", "block", "good",
                        "Endemic redlichiid trilobites; Gondwana and its margins.",
                        ("Redlichia", "Eoredlichia"))
    if block in ("Avalonia", "Armorica", "Iberia"):
        return Province("Bigotinid Province", "marine", "block", "moderate",
                        "Intermediate peri-Gondwanan province where both faunas overlap "
                        "(Pillola 1991).", ("Bigotina",))
    return None


def _ordovician_silurian_marine(age, lat, block):
    """Provinciality is HIGH here - the continents are maximally scattered across
    latitude and Late Ordovician diversification is explicitly described as slowing
    because endemism rose. Named realms follow the continents, not bands."""
    if block == "Laurentia":
        return Province("Laurentian (North American) Province", "marine", "block", "moderate",
                        "Equatorial, warm, epeiric carbonate seas ~60 m deep over the "
                        "whole craton. Stromatoporoid-tabulate-rugose reefs replace the "
                        "Cambrian archaeocyath/microbial mounds.",
                        ("Receptaculites", "Halysites", "Isotelus"))
    if block == "Baltica":
        return Province("Baltic Province", "marine", "block", "moderate",
                        "Southern mid-latitude, drifting north; its shelf moves into "
                        "oligotrophic water during the GOBE and its reef biota diversify.",
                        ("Asaphus", "Megistaspis"))
    if block == "Siberia":
        return Province("Siberian Province", "marine", "block", "moderate", "", ())
    if block in ("Avalonia", "Armorica", "Iberia") or (block and lat < -40):
        return Province("Mediterranean (peri-Gondwanan) Province", "marine", "both",
                        "moderate",
                        "Cold, high-latitude Gondwanan margin; the Hirnantian ice sheet "
                        "sits on it. Low-diversity, cool-water assemblages.",
                        ("Neseuretus", "Calymenella"))
    return None


def _devonian_carboniferous_flora(age, lat, block):
    """The first forests, and they are cosmopolitan - a low-diversity flora spreads.
    Provinciality only appears once the flora is rich enough to differ."""
    if age > 385:
        return Province("Early vascular flora", "terrestrial", "default", "good",
                        "Low, rhyniophyte- and zosterophyll-grade vegetation confined to "
                        "damp lowlands. No canopy, no soil profile worth the name, "
                        "no provinces.", ("Cooksonia", "Aglaophyton", "Zosterophyllum",
                                          "Baragwanathia"))
    if age > 358.9:
        return Province("Archaeopteris forest flora", "terrestrial", "default", "good",
                        "The first forests, and near-cosmopolitan. Archaeopteris to 30 m "
                        "with real wood and roots to ~1 m; Wattieza ~8 m earlier. "
                        "Prototaxites, a probable fungus to 8 m, has no modern analogue. "
                        "First seeds (Elkinsia) in the Late Devonian.",
                        ("Archaeopteris", "Wattieza", "Prototaxites", "Elkinsia",
                         "Rhacophyton"))
    return None


def _devonian_marine(age, lat, block):
    if block in ("Amazonia", "Sao Francisco", "Rio de la Plata", "Kalahari Craton",
                 "Falkland / Malvinas", "Patagonia") and lat < -30:
        return Province("Malvinokaffric Realm", "marine", "both", "good",
                        "Cold-water, high southern latitude Gondwana. Low diversity, NO "
                        "reefs, distinctive brachiopod and trilobite assemblages. This is "
                        "a MARINE realm - 'Malvinokaffric flora' is a misnomer.",
                        ("Australocoelia", "Australospirifer", "Burmeisteria"))
    if block in ("Laurentia", "Avalonia") and abs(lat) < 35:
        return Province("Eastern Americas Realm", "marine", "both", "moderate",
                        "Appalachian basin and the epeiric seas of eastern Laurussia.",
                        ("Tropidoleptus", "Mucrospirifer"))
    if abs(lat) < 35:
        return Province("Old World Realm", "marine", "both", "moderate",
                        "Europe, North Africa, Asia. Stromatoporoid-coral reefs at their "
                        "Phanerozoic maximum until the Frasnian-Famennian collapse.",
                        ("Stringocephalus", "Amphipora"))
    return None


def _late_paleozoic_marine(age, lat, block):
    if abs(lat) < 30:
        return Province("Tethyan Realm", "marine", "latitude", "good",
                        "Warm equatorial. Fusulinid foraminifera are the diagnostic "
                        "marker; reef-rich.", ("Fusulinids", "Verbeekina", "Waagenophyllum"))
    if lat >= 30:
        return Province("Boreal Realm", "marine", "latitude", "good",
                        "Cool northern shelves; no fusulinids.", ())
    return Province("Gondwanan (Austral) Realm", "marine", "latitude", "good",
                    "Cool southern shelves under the Late Palaeozoic Ice Age; "
                    "glacially influenced, Eurydesma fauna.", ("Eurydesma", "Deltopecten"))


def _mesozoic_marine(age, lat, block):
    if abs(lat) < 35:
        return Province("Tethyan Realm", "marine", "latitude", "good",
                        "Warm equatorial. Rudist reefs (Cretaceous), ammonite-rich, "
                        "larger benthic foraminifera.", ("rudists", "orbitolinids"))
    if lat >= 35:
        return Province("Boreal Realm", "marine", "latitude", "good",
                        "Cool northern. Belemnite- and Buchia-dominated. The Viking and "
                        "Hispanic Corridors switch its exchange with Tethys on and off.",
                        ("Buchia", "belemnites"))
    return Province("Austral Realm", "marine", "latitude", "moderate",
                    "Cool southern; increasingly isolated as Gondwana fragments.", ())


def _cenozoic_marine(age, lat, block):
    acc = age <= 23.0   # Antarctic Circumpolar Current fully established
    if lat <= -55 and acc:
        return Province("Southern Ocean", "marine", "latitude", "good",
                        "Thermally isolated behind the Antarctic Circumpolar Current, "
                        "which exists only because Drake Passage and the Tasman Gateway "
                        "are open (crust 34-29 Ma; full ACC ~23 Ma).", ())
    if lat >= 66:
        return Province("Arctic", "marine", "latitude", "good", "", ())
    if abs(lat) < 30:
        return Province("Tropical", "marine", "latitude", "good",
                        "Split into Indo-Pacific and Atlantic provinces once the Tethys "
                        "seaway closes (~19-14 Ma) and Panama shoals (~10-2.7 Ma).", ())
    return Province(f"{_hemisphere(lat).title()} temperate", "marine", "latitude", "moderate", "", ())


MARINE_SCHEMES = [
    (538.8, 485.4, _cambrian_marine),
    (485.4, 419.6, _ordovician_silurian_marine),
    (419.6, 358.9, _devonian_marine),
    (358.9, 251.9, _late_paleozoic_marine),
    (251.9, 66.0, _mesozoic_marine),
    (66.0, -260.0, _cenozoic_marine),
]


# ---------------------------------------------------------------------------
# Named TERRESTRIAL schemes.
# ---------------------------------------------------------------------------

_CATHAYSIAN = ("North China", "South China")
_ANGARAN = ("Siberia", "Kazakhstania", "Amuria / Mongolia")
_EURAMERICAN = ("Laurentia", "Baltica", "Avalonia", "Armorica", "Iberia")


def _carboniferous_permian_flora(age, lat, block):
    """The canonical four-province world. Cathaysia is the interesting one: its
    everwet rainforest survives the 305 Ma Euramerican collapse and persists to
    the end-Permian, so the SAME AGE needs different vegetation on different blocks."""
    if block in _CATHAYSIAN:
        return Province("Cathaysian Province", "terrestrial", "block", "good",
                        "Everwet tropical. Gigantopterids. Coal continues here when it "
                        "has stopped everywhere else - the Carboniferous rainforest "
                        "collapse at ~305 Ma is a EURAMERICAN event only.",
                        ("Gigantopteris", "Lobatannularia", "Cathaysiodendron"))
    if block in _ANGARAN or (lat > 30 and block not in _EURAMERICAN):
        return Province("Angaran Province", "terrestrial", "both", "good",
                        "Northern mid-to-high latitude, cool temperate. Cordaitalean-"
                        "dominated, deciduous, strong growth rings.",
                        ("Rufloria", "Cordaites", "Vojnovskya"))
    if lat < -30:
        return Province("Gondwanan Province", "terrestrial", "latitude", "good",
                        "Glossopteris flora. Wet-soil seed-fern forest to 30 m, tolerant "
                        "of a polar light regime; the source of Gondwanan coal.",
                        ("Glossopteris", "Gangamopteris", "Vertebraria", "Noeggerathiopsis"))
    if block in _EURAMERICAN or abs(lat) <= 30:
        return Province("Euramerican Province", "terrestrial", "both", "good",
                        "Low, tropical. Carboniferous lycopsid coal forest (Lepidodendron "
                        ">50 m tall, 2 m across), then increasingly seasonally dry after "
                        "the ~305 Ma rainforest collapse: tree ferns, conifers, peltasperms.",
                        ("Lepidodendron", "Sigillaria", "Calamites", "Medullosa", "Cordaites"))
    return None


def _mesozoic_flora(age, lat, block):
    if age > 201.4:
        if lat < -20:
            return Province("Dicroidium Flora", "terrestrial", "latitude", "good",
                            "Triassic Gondwana. Replaces Glossopteris, which died out "
                            "BEFORE 252.3 Ma - some 350 kyr ahead of the marine extinction.",
                            ("Dicroidium", "Umkomasia", "Pleuromeia"))
        return Province("Northern Triassic conifer flora", "terrestrial", "latitude",
                        "moderate", "Voltzialean conifers, cycadophytes, seed ferns.",
                        ("Voltzia", "Pleuromeia", "Neocalamites"))
    if age > 130:
        return Province("Cosmopolitan Jurassic gymnosperm flora", "terrestrial", "default",
                        "good",
                        "Strikingly uniform pole to pole: conifers, cycads, Bennettitales, "
                        "ginkgoes, ferns. The same forest type from Greenland to Antarctica "
                        "- a real and drawable fact about a dispersing but still connected world.",
                        ("Araucaria", "Ginkgo", "Williamsonia", "Ptilophyllum"))
    return Province("Early angiosperm flora", "terrestrial", "default", "good",
                    "Angiosperms originate and diversify from ~130 Ma; by the Late "
                    "Cretaceous >50% of modern orders exist and the clade is ~70% of "
                    "species, and flowering trees overtake conifers. As Gondwana "
                    "fragments each piece begins its own experiment.",
                    ("Archaefructus", "Nymphaeales", "Platanaceae"))


_REALM_BOXES = [
    # (name, lon0, lon1, lat0, lat1) - present-day WWF realms, coarse boxes.
    ("Palearctic", -12, 180, 30, 82),
    ("Palearctic", -25, 60, 20, 40),        # N Africa + Arabia
    ("Nearctic", -170, -52, 25, 84),
    ("Neotropical", -118, -34, -56, 25),
    ("Afrotropical", -18, 52, -35, 20),
    ("Indomalayan", 60, 130, 5, 30),
    ("Indomalayan", 95, 128, -11, 10),
    ("Australasian", 128, 180, -48, 0),
    ("Australasian", 110, 155, -45, -10),
    ("Oceanian", -180, -130, -30, 30),
    ("Antarctic", -180, 180, -90, -60),
]


def _cenozoic_flora(age, lat, block):
    """Modern realms only become meaningful as their barriers form. Before the
    relevant tectonic event the realm name is an anachronism."""
    realm_ages = {          # Ma at which the realm becomes a distinct entity
        "Australasian": 35, "Neotropical": 60, "Antarctic": 34,
        "Nearctic": 60, "Palearctic": 60, "Afrotropical": 30,
        "Indomalayan": 40, "Oceanian": 20,
    }
    if block:
        guess = {"Australia": "Australasian", "East Antarctica": "Antarctic",
                 "India": "Indomalayan", "Amazonia": "Neotropical",
                 "Laurentia": "Nearctic", "Baltica": "Palearctic",
                 "Siberia": "Palearctic", "Congo Craton": "Afrotropical",
                 "Kalahari Craton": "Afrotropical"}.get(block)
        if guess and age <= realm_ages[guess]:
            return Province(guess, "terrestrial", "block", "good", "", ())
    return None


TERRESTRIAL_SCHEMES = [
    (470.0, 358.9, _devonian_carboniferous_flora),
    (358.9, 251.9, _carboniferous_permian_flora),
    (251.9, 66.0, _mesozoic_flora),
    (66.0, -260.0, _cenozoic_flora),
]


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

_NO_LAND_FLORA_BEFORE = 470.0   # cryptospores, Middle Ordovician
_NO_FORESTS_BEFORE = 385.0      # Wattieza; Archaeopteris forests by ~375
_NO_GRASSLAND_BEFORE = 40.0     # grasses ecologically important from ~40 Ma
_NO_C4_GRASSLAND_BEFORE = 8.0


def province(age: float, lat: float, realm: str = "marine",
             block: Optional[str] = None) -> Province:
    """The biogeographic province at (age, palaeolatitude), in `realm`.

    `block` is the continental block the point sits on, if known - it is what lets
    the model use a BARRIER rather than only a gradient, and it is the difference
    between "tropical" and "Cathaysian Province"."""
    if realm not in ("marine", "terrestrial"):
        raise ValueError("realm must be 'marine' or 'terrestrial'")

    if realm == "terrestrial" and age > _NO_LAND_FLORA_BEFORE:
        return Province("no terrestrial biosphere", "terrestrial", "default", "good",
                        "Land is bare regolith with at most a microbial and possibly "
                        "fungal crust on damp surfaces. Earliest embryophyte spores are "
                        "Middle Ordovician (~470 Ma); there is no vegetation to zone.", ())

    schemes = MARINE_SCHEMES if realm == "marine" else TERRESTRIAL_SCHEMES
    for base, top, resolver in schemes:
        if top <= age <= base:
            p = resolver(age, lat, block)
            if p is not None:
                return p

    # fallback: the latitude gradient, honestly labelled
    return Province(_band(lat) + (" (" + _hemisphere(lat) + ")" if abs(lat) >= 30 else ""),
                    realm, "latitude", "none",
                    "No named province scheme is established for this interval here; "
                    "this is a climate band, not a biogeographic province.", ())


def expected_provinces(age: float, realm: str = "marine") -> list:
    """Every province the model can produce at this age. Use this to check that a
    curated dataset (life_data.json region_taxa) covers the world it claims to."""
    lats = [-80, -60, -40, -20, 0, 20, 40, 60, 80]
    blocks = [None] + sorted(pg.BLOCKS)
    seen = {}
    for lat in lats:
        for b in blocks:
            if b is not None and not pg.exists(b, max(age, 0)):
                continue
            p = province(age, lat, realm, b)
            seen.setdefault(p.name, p)
    return sorted(seen.values(), key=lambda p: p.name)


def provinciality(age: float) -> dict:
    """Predicted degree of biotic differentiation, from the supercontinent state.

    This is the testable prediction of section 1 of the province research note:
    dispersal makes cosmopolitans, isolation makes endemics. A curated dataset
    should be MORE differentiated where this is high."""
    assembled = []
    for name, a in pg.ASSEMBLIES.items():
        if a["top"] <= age <= a["base"] and name in ("Pangaea", "Rodinia", "Pannotia"):
            assembled.append(name)
    if assembled:
        return dict(index=0.25, state="assembled", assembly=assembled[0],
                    terrestrial="cosmopolitan - one landmass, no ocean barriers; "
                                "Lystrosaurus after the P-Tr is the type case",
                    marine="provincial - one long coast plus isolated interior seas")
    # partial: Gondwana or Laurasia exists but not a supercontinent
    partial = [n for n, a in pg.ASSEMBLIES.items()
               if a["top"] <= age <= a["base"] and n in ("Gondwana", "Laurasia", "Laurussia")]
    if partial:
        return dict(index=0.6, state="partly assembled", assembly=partial[0],
                    terrestrial="regionally differentiated",
                    marine="two to four latitude-banded realms")
    return dict(index=0.9, state="dispersed", assembly=None,
                terrestrial="highly endemic - each fragment runs its own experiment",
                marine="connected by open gateways; fewer, broader realms")


# ---------------------------------------------------------------------------

def _selftest() -> None:
    # Cambrian trilobite realms resolve off the block
    assert province(520, 10, "marine", "Laurentia").name == "Olenellid Province"
    assert province(520, -40, "marine", "Australia").name == "Redlichiid Province"
    assert province(520, -50, "marine", "Avalonia").name == "Bigotinid Province"
    # Permian floral provinces
    assert province(280, 5, "terrestrial", "South China").name == "Cathaysian Province"
    assert province(280, -60, "terrestrial", "Australia").name == "Gondwanan Province"
    assert province(280, 60, "terrestrial", "Siberia").name == "Angaran Province"
    assert province(280, 5, "terrestrial", "Laurentia").name == "Euramerican Province"
    # the Cathaysian exception at the age of the Euramerican collapse
    assert province(300, 3, "terrestrial", "North China").name == "Cathaysian Province"
    assert province(300, 3, "terrestrial", "Laurentia").name == "Euramerican Province"
    # no vegetation before land plants
    assert province(600, 0, "terrestrial").name == "no terrestrial biosphere"
    assert province(500, 0, "terrestrial").name == "no terrestrial biosphere"
    # Malvinokaffric is marine and southern
    p = province(390, -50, "marine", "Kalahari Craton")
    assert p.name == "Malvinokaffric Realm" and p.realm == "marine"
    # Southern Ocean only after the ACC
    assert province(10, -70, "marine").name == "Southern Ocean"
    assert province(60, -70, "marine").name != "Southern Ocean"
    # provinciality follows the supercontinent cycle
    assert provinciality(280)["state"] == "assembled"      # Pangaea
    assert provinciality(90)["index"] > provinciality(280)["index"]
    # honest fallback
    fb = province(460, 10, "marine")
    assert fb.confidence == "none"
    n_m = len(expected_provinces(280, "marine"))
    n_t = len(expected_provinces(280, "terrestrial"))
    print(f"paleobiogeography selftest OK: at 280 Ma the model expects "
          f"{n_m} marine and {n_t} terrestrial provinces")


if __name__ == "__main__":
    _selftest()
    print()
    for age in (520, 390, 280, 150, 90, 10):
        pr = provinciality(age)
        print(f"{age:>4} Ma  provinciality {pr['index']:.2f} ({pr['state']})")
        for realm in ("marine", "terrestrial"):
            names = [p.name for p in expected_provinces(age, realm)]
            print(f"        {realm:12s} {', '.join(names)}")
        print()
