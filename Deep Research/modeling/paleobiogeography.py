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
    basis: str                 # what decided it: 'block', 'latitude', 'both',
                               # 'age' (a genuinely cosmopolitan interval), or
                               # 'default' (nothing resolved - see confidence)
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
        return Province("Early vascular flora", "terrestrial", "age", "good",
                        "Low, rhyniophyte- and zosterophyll-grade vegetation confined to "
                        "damp lowlands. No canopy, no soil profile worth the name, "
                        "no provinces.", ("Cooksonia", "Aglaophyton", "Zosterophyllum",
                                          "Baragwanathia"))
    if age > 358.9:
        return Province("Archaeopteris forest flora", "terrestrial", "age", "good",
                        "The first forests, and near-cosmopolitan. Archaeopteris to 30 m "
                        "with real wood and roots to ~1 m; Wattieza ~8 m earlier. "
                        "Prototaxites, a probable fungus to 8 m, has no modern analogue. "
                        "First seeds (Elkinsia) in the Late Devonian.",
                        ("Archaeopteris", "Wattieza", "Prototaxites", "Elkinsia",
                         "Rhacophyton"))
    return None


# Base of the Givetian. Boucot, Johnson & Talent (1969) is explicit that the
# three-realm structure is an EARLY Devonian one: by the Givetian the
# Malvinokaffric Realm has gone, the Eastern Americas Realm is much reduced, and
# the Old World Realm has expanded over most of what the other two held. The
# Devonian trend is toward cosmopolitanism, and a model that keeps all three
# realms to the Famennian draws the opposite of what the record shows.
_GIVETIAN = 387.7


def _devonian_marine(age, lat, block):
    """Devonian marine realms, after Boucot, Johnson & Talent (1969), *Early
    Devonian Brachiopod Zoogeography*, GSA Special Paper 119 -- the paper that
    established these three units and still the framework the field uses.

    B11 asked for these names to be checked against a primary source rather than
    general literature. They check out; the AGES did not. The realms were being
    held constant across the whole period when the source describes them
    collapsing into one another through it.
    """
    if (age > _GIVETIAN
            and block in ("Amazonia", "Sao Francisco", "Rio de la Plata",
                          "Kalahari Craton", "Falkland / Malvinas", "Patagonia")
            and lat < -30):
        return Province("Malvinokaffric Realm", "marine", "both", "good",
                        "Cold-water, high southern latitude Gondwana. Low diversity, NO "
                        "reefs, distinctive brachiopod and trilobite assemblages. This is "
                        "a MARINE realm - 'Malvinokaffric flora' is a misnomer. An EARLY "
                        "Devonian realm: it is gone by the Givetian.",
                        ("Australocoelia", "Australospirifer", "Burmeisteria"))
    if block in ("Laurentia", "Avalonia") and abs(lat) < 35:
        note = ("Appalachian basin and the epeiric seas of eastern Laurussia."
                if age > _GIVETIAN else
                "Appalachian basin and the epeiric seas of eastern Laurussia -- by now "
                "much reduced, as Old World faunas spread into what it used to hold.")
        return Province("Eastern Americas Realm", "marine", "both", "moderate",
                        note, ("Tropidoleptus", "Mucrospirifer"))
    if abs(lat) < 35:
        return Province("Old World Realm", "marine", "both", "moderate",
                        "Europe, North Africa, Asia. Stromatoporoid-coral reefs at their "
                        "Phanerozoic maximum until the Frasnian-Famennian collapse."
                        + ("" if age > _GIVETIAN else " By the Late Devonian it has "
                           "expanded over most of what the other two realms held."),
                        ("Stringocephalus", "Amphipora"))
    # High latitude, and after the Malvinokaffric has gone. Saying nothing here
    # would make the realm's disappearance look like a hole in the model rather
    # than the cosmopolitanism it actually was.
    if age <= _GIVETIAN and lat < -35:
        return Province("Southern cool-water shelf (Late Devonian)", "marine",
                        "latitude", "moderate",
                        "Cool, high-latitude Gondwanan shelf after the Malvinokaffric "
                        "Realm's endemics are gone. The Devonian ends far more "
                        "cosmopolitan than it began: the same brachiopod and coral "
                        "genera turn up from Europe to Australia to South America.",
                        ("Cyrtospirifer",))
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



# ---------------------------------------------------------------------------
# EXTENDED SCHEMES (2026-07-26). The first version placed only 67 of 198 curated
# spans; 121 fell to an unnamed climate band. The gaps were, in order of size:
# no Ediacaran scheme at all, the Ordovician and Silurian lumped together, no
# habitat dimension (an epicontinental sea is not an open shelf), and a Cenozoic
# scheme that stopped at three latitude bands. All four are addressed below.
# ---------------------------------------------------------------------------

def _tonian_cryogenian_marine(age, lat, block, habitat=None):
    """1000-635 Ma. Provinces in the shelf-fauna sense do not exist yet - there
    are no skeletal animals to zone - so the meaningful divisions are the state of
    the OCEAN itself: its redox structure and whether it is under ice."""
    if 717.4 >= age >= 661.7:
        return Province("Sturtian snowball ocean", "marine", "age", "good",
                        "Ice to near-tropical latitudes for some 56 Myr. The marine "
                        "biosphere survives, probably in cryoconite meltponds on the ice "
                        "surface and in narrow open-water bands near the equator. "
                        "Eukaryotic diversity drops hard and rebounds after the thaw.",
                        ("cyanobacteria", "cryoconite communities"))
    if 650 >= age >= 635.5:
        return Province("Marinoan snowball ocean", "marine", "age", "good",
                        "The second Cryogenian glaciation, ending at ~12% atmospheric "
                        "CO2 with a cap-carbonate super-greenhouse. Banded iron "
                        "formations briefly reappear after a billion-year absence, which "
                        "means the deep ocean went ferruginous again under the ice.",
                        ("cap carbonates", "banded iron formation"))
    if age > 717.4:
        return Province("Mirovian shelf sea", "marine", "age", "moderate",
                        "Warm, stratified, and run by cyanobacteria and small algae, with "
                        "stromatolite reefs on every shelf. Below a thin oxygenated "
                        "surface layer the water is anoxic and often sulphidic. "
                        "Eukaryotes exist and are diversifying - red and green algae, "
                        "testate amoebae, the first fungi - but nothing is skeletal, so "
                        "there is nothing to build a shelly province out of.",
                        ("stromatolites", "acritarchs", "Bangiomorpha"))
    return Province("Post-Marinoan recovery sea", "marine", "age", "moderate",
                    "Between the Marinoan thaw and the Ediacaran biota: oxygen rising, "
                    "the deep ocean ventilating for the first time, and the water column "
                    "becoming habitable for something larger than a cell.", ())


def _ediacaran_marine(age, lat, block, habitat=None):
    """Avalon / White Sea / Nama - as much temporal as spatial, and both.

    These are the three Ediacaran assemblages, and the honest position is that
    they are partly a succession in time and partly an environmental gradient.
    The model reports the time slice and names the environment, rather than
    pretending they are geographic provinces."""
    if age >= 565:
        return Province("Avalon Assemblage", "marine", "both", "good",
                        "Deep water, below the photic zone. Fractal rangeomorph fronds "
                        "standing in the dark, feeding osmotrophically on dissolved "
                        "organic matter. Type localities Mistaken Point and Charnwood.",
                        ("Charnia", "Fractofusus", "Rangea", "Bradgatia"))
    if age >= 550:
        return Province("White Sea Assemblage", "marine", "both", "good",
                        "Shallow water on microbial mats, and the most diverse of the "
                        "three. Dickinsonia reaches 1.4 m; Kimberella grazes the mat "
                        "with something like a radula and leaves paired scratch marks.",
                        ("Dickinsonia", "Kimberella", "Yorgia", "Spriggina",
                         "Tribrachidium"))
    return Province("Nama Assemblage", "marine", "both", "good",
                    "Sandy, three-dimensionally preserved, and the interval in which "
                    "skeletons appear: Cloudina and Namacalathus build the first "
                    "mineralised hard parts, and some Cloudina tubes carry predatory "
                    "boreholes - the earliest direct evidence of predation.",
                    ("Cloudina", "Namacalathus", "Ernietta", "Pteridinium"))


_LAURENTIAN_BLOCKS = ("Laurentia", "Superior Craton", "Slave Craton", "Wyoming Craton",
                      "Rae Craton", "Hearne Craton", "Nain Province")
_BALTIC_BLOCKS = ("Baltica", "Fennoscandia", "Sarmatia", "Volgo-Uralia", "Timan-Pechora")
_SIBERIAN_BLOCKS = ("Siberia", "Kazakhstania", "Amuria / Mongolia")
_PERIGONDWANAN = ("Avalonia", "Armorica", "Iberia", "Adria / Apulia")
_GONDWANAN_BLOCKS = ("Amazonia", "Sao Francisco", "Rio de la Plata", "West African Craton",
                     "Congo Craton", "Tanzania Craton", "Kalahari Craton", "India",
                     "Australia", "East Antarctica", "Arabia", "Madagascar", "Azania",
                     "Patagonia", "Falkland / Malvinas")


def _ordovician_marine(age, lat, block, habitat=None):
    """The Ordovician is the most PROVINCIAL interval of the Palaeozoic, because
    the continents are maximally scattered across latitude. Named shelf provinces
    are well established and they map onto our own blocks directly."""
    if block in _LAURENTIAN_BLOCKS:
        return Province("Laurentian Province", "marine", "block", "good",
                        "Equatorial carbonate platform - the great American "
                        "epicontinental sea. Warm, shallow, and dominated by "
                        "stromatoporoid-tabulate-rugose reef framework, which is the "
                        "Ordovician's new invention.",
                        ("Isotelus", "Receptaculites", "Halysites", "Cameroceras"))
    if block in _BALTIC_BLOCKS:
        return Province("Baltic Province", "marine", "block", "good",
                        "Cool-water carbonate on a temperate shelf; famous for its "
                        "orthoceratite limestones and for the completeness of its "
                        "graptolite record.",
                        ("Asaphus", "Megistaspis", "orthoceratid nautiloids"))
    if block in _SIBERIAN_BLOCKS:
        return Province("Siberian Province", "marine", "block", "moderate",
                        "An isolated equatorial platform with a distinctive endemic "
                        "shelly fauna.", ())
    if block in _PERIGONDWANAN or (block in _GONDWANAN_BLOCKS and abs(lat) > 40):
        return Province("Mediterranean (peri-Gondwanan) Province", "marine", "block",
                        "good",
                        "High-latitude, cold-water, siliciclastic. Low diversity, no "
                        "reefs, and a distinctive trilobite-brachiopod association. This "
                        "is the fauna that sits over the South Pole as the Hirnantian "
                        "ice sheet grows.",
                        ("Neseuretus", "calymenid trilobites", "Hirnantia fauna"))
    if abs(lat) < 30:
        return Province("Tropical shelf (Ordovician)", "marine", "latitude", "moderate",
                        "Carbonate platform in the warm belt.", ())
    return Province(f"{_hemisphere(lat).title()} temperate shelf (Ordovician)",
                    "marine", "latitude", "moderate", "", ())


def _silurian_marine(age, lat, block, habitat=None):
    """After the End-Ordovician the shelf faunas are strikingly COSMOPOLITAN - the
    extinction removed the endemics and the survivors spread. That is a real and
    reportable fact, not an absence of information."""
    if abs(lat) > 55 and block in _GONDWANAN_BLOCKS:
        return Province("Malvinokaffric Realm", "marine", "both", "good",
                        "Cold-water, high southern latitude, low diversity, no reefs. "
                        "South America, southern Africa and the Falklands. Named for the "
                        "Malvinas and the Kaffrarian region of South Africa.",
                        ("Clarkeia", "Malvinokaffric brachiopods", "Australocoelia"))
    if abs(lat) < 35:
        return Province("Silurian cosmopolitan tropical shelf", "marine", "latitude",
                        "good",
                        "Unusually uniform worldwide. The End-Ordovician extinction "
                        "removed the provincial endemics and the survivors spread across "
                        "the warm shelves; pentamerid brachiopods and the first true "
                        "coral-stromatoporoid barrier reefs are found nearly everywhere.",
                        ("Pentamerus", "Favosites", "Halysites", "eurypterids"))
    return Province(f"{_hemisphere(lat).title()} temperate shelf (Silurian)", "marine",
                    "latitude", "moderate", "", ())


def _triassic_marine(age, lat, block, habitat=None):
    """The Early Triassic is the flattest biogeography in the Phanerozoic - the
    end-Permian left so few survivors that the same handful is found everywhere.
    Provinciality returns through the period."""
    if age > 247:
        return Province("Post-extinction cosmopolitan sea", "marine", "latitude", "good",
                        "The aftermath of the largest extinction: a depauperate, "
                        "worldwide-uniform fauna of disaster taxa. Claraia and Lingula "
                        "beds blanket shelves on every continent, and reefs are absent "
                        "from the record for several million years.",
                        ("Claraia", "Lingula", "Otoceras", "microbialites"))
    if abs(lat) < 35:
        return Province("Tethyan Realm (Triassic)", "marine", "latitude", "good",
                        "The warm Tethys embayment; reefs recover here first, built by "
                        "scleractinian corals and calcisponges.",
                        ("Dachstein reef fauna", "ceratitid ammonoids", "Daonella"))
    return Province("Boreal Realm (Triassic)" if lat > 0 else "Austral Realm (Triassic)",
                    "marine", "latitude", "moderate", "", ())


def _cenozoic_marine_extended(age, lat, block, habitat=None):
    """The modern marine realms are a product of CENOZOIC GATEWAY TECTONICS, so the
    scheme has to change as the gateways do - that is the whole point."""
    if age > 34:
        return Province("Circumglobal Tethyan tropical belt", "marine", "latitude",
                        "good",
                        "Before Drake and Tasman open, a warm circumglobal current runs "
                        "through the Tethys and there is no thermally isolated Southern "
                        "Ocean. Larger benthic foraminifera (nummulites) build "
                        "limestones from Spain to Indonesia.",
                        ("Nummulites", "Discocyclina")) if abs(lat) < 35 else \
               Province(("Boreal" if lat > 0 else "Austral") + " Realm (Palaeogene)",
                        "marine", "latitude", "moderate", "", ())
    if abs(lat) > 55 and lat < 0:
        return Province("Southern Ocean Realm", "marine", "latitude", "good",
                        "Created by tectonics: the Antarctic Circumpolar Current, "
                        "established once Drake Passage and the Tasman Gateway are open "
                        "(34-23 Ma), thermally isolates Antarctica and produces a "
                        "distinct cold, highly productive, endemic realm.",
                        ("notothenioid fish", "krill", "diatom ooze"))
    if abs(lat) > 55:
        return Province("Arctic Realm", "marine", "latitude", "good",
                        "Young and species-poor - the Arctic basin was only connected "
                        "to the Pacific when the Bering Strait opened at ~5.5-5.3 Ma, "
                        "and the trans-Arctic interchange follows.", ())
    if abs(lat) < 30:
        if age > 14:
            return Province("Tethyan tropical belt (Neogene)", "marine", "both", "good",
                            "Still one tropical ocean: the Tethys closes at the "
                            "Gomphotherium land bridge ~19-14 Ma and Panama shoals from "
                            "~10 Ma. Before that, Atlantic and Indo-Pacific shallow "
                            "faunas are continuous.", ())
        return Province("Indo-Pacific Realm", "marine", "both", "good",
                        "The world's richest shallow-marine fauna, cut off from the "
                        "Atlantic by the Tethys closure and then by Panama. The Coral "
                        "Triangle is its centre.",
                        ("Acropora", "giant clams", "reef fish radiation")) \
            if (block is None or True) and lat > -30 else None
    return Province(("North" if lat > 0 else "South") + " temperate shelf", "marine",
                    "latitude", "moderate", "", ())


def _silurian_devonian_flora(age, lat, block, habitat=None):
    """The land is being colonised, and the flora is COSMOPOLITAN because it is
    tiny, spore-dispersed and low-diversity. Provinciality on land needs forests,
    and forests do not exist yet."""
    if age > 419:
        return Province("Early tracheophyte ground cover", "terrestrial", "latitude",
                        "good",
                        "Centimetre-scale leafless axes on damp ground beside water: "
                        "Cooksonia, rhyniophytes, early lycophytes. Spore-dispersed and "
                        "effectively worldwide - there is not enough plant to be "
                        "provincial with.",
                        ("Cooksonia", "Baragwanathia", "Rhynia"))
    if age > 385:
        return Province("Early Devonian rhyniophyte-zosterophyll flora", "terrestrial",
                        "latitude", "good",
                        "Still knee-high. Trimerophytes and zosterophylls, with the "
                        "Rhynie chert preserving a whole ecosystem including the first "
                        "arthropod herbivores and mycorrhizal fungi.",
                        ("Zosterophyllum", "Asteroxylon", "Aglaophyton"))
    return Province("Archaeopteris forest", "terrestrial", "latitude", "good",
                    "The first forests. Archaeopteris reaches 30 m with real wood and "
                    "roots a metre deep, and its arrival changes weathering, soils, "
                    "river form and atmospheric CO2 permanently.",
                    ("Archaeopteris", "Wattieza", "Prototaxites", "Elkinsia"))


MARINE_SCHEMES = [
    (1000.0, 635.0, _tonian_cryogenian_marine),
    (635.0, 538.8, _ediacaran_marine),
    (538.8, 485.4, _cambrian_marine),
    (485.4, 443.8, _ordovician_marine),
    (443.8, 419.6, _silurian_marine),
    (419.6, 358.9, _devonian_marine),
    (358.9, 251.9, _late_paleozoic_marine),
    (251.9, 201.4, _triassic_marine),
    (201.4, 66.0, _mesozoic_marine),
    (66.0, -260.0, _cenozoic_marine_extended),
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


def _fallback_marine(age, lat, label=""):
    """A named latitudinal marine province, so no Phanerozoic cell is ever unnamed.

    This is deliberately a CLIMATE band and says so, but it is a real statement
    about the water, not a shrug: shelf faunas have always been zoned by
    temperature, and naming the zone is more useful to a reader than 'unknown'.
    """
    suffix = f" ({label})" if label else ""
    if abs(lat) > 60:
        return Province("Polar sea" + suffix, "marine", "latitude", "moderate",
                        "Cold, seasonally ice-influenced, low diversity, no reefs.", ())
    if abs(lat) > 35:
        return Province(("Boreal" if lat > 0 else "Austral") + " Realm" + suffix,
                        "marine", "latitude", "moderate",
                        "Cool-temperate shelf: siliciclastic rather than carbonate, "
                        "and reef-free.", ())
    if abs(lat) > 23:
        return Province("Warm-temperate shelf" + suffix, "marine", "latitude", "moderate",
                        "The transition belt; its position is the single most sensitive "
                        "indicator of a warm or cold world.", ())
    return Province("Tropical shelf" + suffix, "marine", "latitude", "moderate",
                    "Carbonate platform, reef-building where the water is clear and "
                    "shallow enough.", ())


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
        return Province("Cosmopolitan Jurassic gymnosperm flora", "terrestrial", "age",
                        "good",
                        "Strikingly uniform pole to pole: conifers, cycads, Bennettitales, "
                        "ginkgoes, ferns. The same forest type from Greenland to Antarctica "
                        "- a real and drawable fact about a dispersing but still connected world.",
                        ("Araucaria", "Ginkgo", "Williamsonia", "Ptilophyllum"))
    return Province("Early angiosperm flora", "terrestrial", "age", "good",
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
    # Without a block we cannot name a REALM - a realm is defined by its barriers -
    # but we can still name the vegetation province, which is what a card needs.
    # Returning None here left 35 Cenozoic cells unnamed.
    if abs(lat) > 66:
        return Province("Polar tundra and ice desert", "terrestrial", "latitude", "good",
                        "Treeless. Continuous permafrost below; a short intense growing "
                        "season above. One of the largest biomes on Earth by area and "
                        "younger than almost any other - it barely exists before the "
                        "Late Cenozoic ice age.", ("dwarf birch", "sedges", "lichens"))
    if abs(lat) > 48:
        return Province("Boreal conifer forest", "terrestrial", "latitude", "good",
                        "The taiga: a near-monotypic conifer belt circling the northern "
                        "continents. Also a Cenozoic novelty - it needs both cold winters "
                        "and the modern conifer families.",
                        ("Picea", "Larix", "Pinus"))
    if abs(lat) > 30:
        return Province("Temperate mixed forest and grassland", "terrestrial", "latitude",
                        "good",
                        "Deciduous broadleaf where wet, grassland where seasonally dry. "
                        "The grassland half is late: grasses matter ecologically only "
                        "from ~40 Ma and C4 grassland expands from ~8 Ma.",
                        ("Quercus", "Fagus", "Poaceae"))
    if abs(lat) > 15:
        return Province("Subtropical desert and savanna belt", "terrestrial", "latitude",
                        "good",
                        "Under the descending limb of the Hadley cell. Deserts here are a "
                        "permanent feature of a rotating planet, not an accident of any "
                        "one geography.", ("Acacia", "succulents", "C4 grasses"))
    return Province("Tropical rainforest belt", "terrestrial", "latitude", "good",
                    "Everwet equatorial forest - the most species-rich terrestrial biome, "
                    "and after the Cretaceous an angiosperm one.",
                    ("angiosperm canopy trees", "epiphytes", "lianas"))


TERRESTRIAL_SCHEMES = [
    (470.0, 358.9, _silurian_devonian_flora),
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

    # No named scheme resolved. Inside the Phanerozoic that should not happen for
    # a habitable realm, so fall back to a NAMED climate-band province rather than
    # an unnamed shrug - a reader is better served by "Tropical shelf" than by
    # "tropical", and the confidence field still says it is a band.
    if realm == "marine" and -260.0 <= age <= 635.0:
        return _fallback_marine(age, lat)
    if realm == "terrestrial" and -260.0 <= age <= _NO_LAND_FLORA_BEFORE:
        return _cenozoic_flora(age, lat, None)
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
    assert province(10, -70, "marine").name == "Southern Ocean Realm"
    assert "Southern Ocean" not in province(60, -70, "marine").name
    # provinciality follows the supercontinent cycle
    assert provinciality(280)["state"] == "assembled"      # Pangaea
    assert provinciality(90)["index"] > provinciality(280)["index"]
    # The Ordovician now has its OWN scheme, so an equatorial point resolves to a
    # named province instead of an unnamed band. Keep an honest-fallback test, but
    # point it somewhere the model genuinely does not reach.
    # the Tonian now HAS a scheme, so the honest-fallback test moves to a realm
    # the model genuinely refuses: terrestrial life before land plants
    assert province(600, 0, "terrestrial").name == "no terrestrial biosphere"
    assert province(900, 0, "marine").name == "Mirovian shelf sea"

    # --- extended coverage, added 2026-07-26 -----------------------------
    # Ediacaran: three assemblages, temporal as much as spatial
    assert province(570, 0, "marine").name == "Avalon Assemblage"
    assert province(555, 0, "marine").name == "White Sea Assemblage"
    assert province(542, 0, "marine").name == "Nama Assemblage"
    # Ordovician provinces map onto our own blocks
    assert province(460, 5, "marine", "Laurentia").name == "Laurentian Province"
    assert province(460, 30, "marine", "Baltica").name == "Baltic Province"
    assert "Mediterranean" in province(460, -60, "marine", "Avalonia").name
    # Silurian is cosmopolitan, which is a REPORTABLE fact not an absence
    assert "cosmopolitan" in province(430, 10, "marine").name.lower()
    assert province(430, -65, "marine", "Kalahari Craton").name == "Malvinokaffric Realm"
    # Early Triassic post-extinction flattening
    assert "cosmopolitan" in province(250, 0, "marine").name.lower()
    assert province(230, 10, "marine").name.startswith("Tethyan")
    # Cenozoic gateways change the scheme as they open
    assert "Circumglobal" in province(45, 10, "marine").name
    assert province(10, -70, "marine").name == "Southern Ocean Realm"
    # land colonisation sequence
    assert province(425, 0, "terrestrial").name == "Early tracheophyte ground cover"
    assert province(400, 0, "terrestrial").name.startswith("Early Devonian")
    assert province(370, 0, "terrestrial").name == "Archaeopteris forest"
    # EVERY Phanerozoic age must now resolve to SOMETHING named for both realms
    unnamed = []
    for a in range(0, 1001, 10):
        for la in (-70, -30, 0, 30, 70):
            q = province(float(a), la, "marine")
            if q.confidence == "none":
                unnamed.append((a, "marine", la, q.name))
    for a in range(0, 539, 10):
        for r in ("marine", "terrestrial"):
            for la in (-70, -30, 0, 30, 70):
                q = province(float(a), la, r)
                if q.confidence == "none":
                    unnamed.append((a, r, la, q.name))
    assert not unnamed, f"{len(unnamed)} unnamed cells, e.g. {unnamed[:3]}"
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
