"""Deep-time chronology utilities.

Stage-level ICS timescale (v2024/12) plus the non-chronostratigraphic structures
that a deep-time Earth model actually needs: climate states, glaciations,
extinctions, oceanic anoxic events and large igneous provinces.

Deliberately dependency-free (stdlib only) so it can be imported from anywhere in
the Tectonic Earth build without pulling numpy in.

Convention throughout the Deep Research folder, matching the app:
    age in Ma, positive into the past, NEGATIVE into the future.
    An interval is (base, top) = (older, younger), so base > top.

    >>> stage_at(66.5).name
    'Maastrichtian'
    >>> period_at(300).name
    'Carboniferous'
    >>> climate_state(93).name
    'hothouse'
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field
from typing import Iterable, Optional

__all__ = [
    "Interval", "Event",
    "EONS", "ERAS", "PERIODS", "EPOCHS", "STAGES",
    "eon_at", "era_at", "period_at", "epoch_at", "stage_at", "interval_at",
    "CLIMATE_STATES", "climate_state",
    "GLACIATIONS", "EXTINCTIONS", "ANOXIC_EVENTS", "LIPS", "HYPERTHERMALS",
    "events_at", "events_in",
]


# ---------------------------------------------------------------------------
# core types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Interval:
    """A named span of time. base > top, both in Ma."""
    name: str
    base: float
    top: float
    rank: str = "stage"
    parent: Optional[str] = None

    @property
    def duration(self) -> float:
        return self.base - self.top

    @property
    def midpoint(self) -> float:
        return 0.5 * (self.base + self.top)

    def contains(self, age: float) -> bool:
        # half-open on the young side so a boundary age belongs to the older unit,
        # which is the ICS convention (the GSSP defines the *base*).
        return self.top < age <= self.base

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{self.rank} {self.name} {self.base}-{self.top} Ma>"


@dataclass(frozen=True)
class Event:
    """A dated happening: extinction, glaciation, LIP, anoxic event, hyperthermal."""
    name: str
    kind: str
    base: float                      # older bound, Ma
    top: float                       # younger bound, Ma
    magnitude: str = ""              # free text; deliberately not a number
    note: str = ""
    confidence: str = "good"         # good | moderate | contested
    links: tuple = ()                # names of other events causally implicated

    @property
    def duration(self) -> float:
        return self.base - self.top

    def contains(self, age: float) -> bool:
        return self.top <= age <= self.base


# ---------------------------------------------------------------------------
# ICS chronostratigraphy, v2024/12
# Ages are the ICS ratified numeric ages. Where the ICS gives an uncertainty the
# central value is used. Precambrian units below the Ediacaran are chronometric
# (defined by round numbers), not chronostratigraphic.
# ---------------------------------------------------------------------------

EONS = [
    Interval("Phanerozoic", 538.8, 0.0, "eon"),
    Interval("Proterozoic", 2500.0, 538.8, "eon"),
    Interval("Archean", 4031.0, 2500.0, "eon"),
    Interval("Hadean", 4567.0, 4031.0, "eon"),
]

ERAS = [
    Interval("Cenozoic", 66.0, 0.0, "era", "Phanerozoic"),
    Interval("Mesozoic", 251.902, 66.0, "era", "Phanerozoic"),
    Interval("Paleozoic", 538.8, 251.902, "era", "Phanerozoic"),
    Interval("Neoproterozoic", 1000.0, 538.8, "era", "Proterozoic"),
    Interval("Mesoproterozoic", 1600.0, 1000.0, "era", "Proterozoic"),
    Interval("Paleoproterozoic", 2500.0, 1600.0, "era", "Proterozoic"),
]

PERIODS = [
    Interval("Quaternary", 2.58, 0.0, "period", "Cenozoic"),
    Interval("Neogene", 23.04, 2.58, "period", "Cenozoic"),
    Interval("Paleogene", 66.0, 23.04, "period", "Cenozoic"),
    Interval("Cretaceous", 143.1, 66.0, "period", "Mesozoic"),
    Interval("Jurassic", 201.4, 143.1, "period", "Mesozoic"),
    Interval("Triassic", 251.902, 201.4, "period", "Mesozoic"),
    Interval("Permian", 298.9, 251.902, "period", "Paleozoic"),
    Interval("Carboniferous", 358.86, 298.9, "period", "Paleozoic"),
    Interval("Devonian", 419.62, 358.86, "period", "Paleozoic"),
    Interval("Silurian", 443.1, 419.62, "period", "Paleozoic"),
    Interval("Ordovician", 486.85, 443.1, "period", "Paleozoic"),
    Interval("Cambrian", 538.8, 486.85, "period", "Paleozoic"),
    Interval("Ediacaran", 635.0, 538.8, "period", "Neoproterozoic"),
    Interval("Cryogenian", 720.0, 635.0, "period", "Neoproterozoic"),
    Interval("Tonian", 1000.0, 720.0, "period", "Neoproterozoic"),
    Interval("Stenian", 1200.0, 1000.0, "period", "Mesoproterozoic"),
    Interval("Ectasian", 1400.0, 1200.0, "period", "Mesoproterozoic"),
    Interval("Calymmian", 1600.0, 1400.0, "period", "Mesoproterozoic"),
    Interval("Statherian", 1800.0, 1600.0, "period", "Paleoproterozoic"),
    Interval("Orosirian", 2050.0, 1800.0, "period", "Paleoproterozoic"),
    Interval("Rhyacian", 2300.0, 2050.0, "period", "Paleoproterozoic"),
    Interval("Siderian", 2500.0, 2300.0, "period", "Paleoproterozoic"),
]

EPOCHS = [
    Interval("Holocene", 0.0117, 0.0, "epoch", "Quaternary"),
    Interval("Pleistocene", 2.58, 0.0117, "epoch", "Quaternary"),
    Interval("Pliocene", 5.333, 2.58, "epoch", "Neogene"),
    Interval("Miocene", 23.04, 5.333, "epoch", "Neogene"),
    Interval("Oligocene", 33.9, 23.04, "epoch", "Paleogene"),
    Interval("Eocene", 56.0, 33.9, "epoch", "Paleogene"),
    Interval("Paleocene", 66.0, 56.0, "epoch", "Paleogene"),
    Interval("Late Cretaceous", 100.5, 66.0, "epoch", "Cretaceous"),
    Interval("Early Cretaceous", 143.1, 100.5, "epoch", "Cretaceous"),
    Interval("Late Jurassic", 161.5, 143.1, "epoch", "Jurassic"),
    Interval("Middle Jurassic", 174.7, 161.5, "epoch", "Jurassic"),
    Interval("Early Jurassic", 201.4, 174.7, "epoch", "Jurassic"),
    Interval("Late Triassic", 237.0, 201.4, "epoch", "Triassic"),
    Interval("Middle Triassic", 246.7, 237.0, "epoch", "Triassic"),
    Interval("Early Triassic", 251.902, 246.7, "epoch", "Triassic"),
    Interval("Lopingian", 259.51, 251.902, "epoch", "Permian"),
    Interval("Guadalupian", 274.4, 259.51, "epoch", "Permian"),
    Interval("Cisuralian", 298.9, 274.4, "epoch", "Permian"),
    Interval("Pennsylvanian", 323.4, 298.9, "epoch", "Carboniferous"),
    Interval("Mississippian", 358.86, 323.4, "epoch", "Carboniferous"),
    Interval("Late Devonian", 382.31, 358.86, "epoch", "Devonian"),
    Interval("Middle Devonian", 393.47, 382.31, "epoch", "Devonian"),
    Interval("Early Devonian", 419.62, 393.47, "epoch", "Devonian"),
    Interval("Pridoli", 425.0, 419.62, "epoch", "Silurian"),
    Interval("Ludlow", 427.4, 425.0, "epoch", "Silurian"),
    Interval("Wenlock", 432.9, 427.4, "epoch", "Silurian"),
    Interval("Llandovery", 443.1, 432.9, "epoch", "Silurian"),
    Interval("Late Ordovician", 458.2, 443.1, "epoch", "Ordovician"),
    Interval("Middle Ordovician", 471.3, 458.2, "epoch", "Ordovician"),
    Interval("Early Ordovician", 486.85, 471.3, "epoch", "Ordovician"),
    Interval("Furongian", 497.0, 486.85, "epoch", "Cambrian"),
    Interval("Miaolingian", 521.0, 497.0, "epoch", "Cambrian"),
    Interval("Cambrian Series 2", 529.0, 521.0, "epoch", "Cambrian"),
    Interval("Terreneuvian", 538.8, 529.0, "epoch", "Cambrian"),
]

# Stages: complete for the Mesozoic and Cenozoic (where event dating is stage-level
# and matters most), representative for the Paleozoic. Extend as needed.
STAGES = [
    Interval("Meghalayan", 0.0042, 0.0, "stage", "Holocene"),
    Interval("Northgrippian", 0.0082, 0.0042, "stage", "Holocene"),
    Interval("Greenlandian", 0.0117, 0.0082, "stage", "Holocene"),
    Interval("Late Pleistocene", 0.129, 0.0117, "stage", "Pleistocene"),
    Interval("Chibanian", 0.774, 0.129, "stage", "Pleistocene"),
    Interval("Calabrian", 1.8, 0.774, "stage", "Pleistocene"),
    Interval("Gelasian", 2.58, 1.8, "stage", "Pleistocene"),
    Interval("Piacenzian", 3.6, 2.58, "stage", "Pliocene"),
    Interval("Zanclean", 5.333, 3.6, "stage", "Pliocene"),
    Interval("Messinian", 7.246, 5.333, "stage", "Miocene"),
    Interval("Tortonian", 11.63, 7.246, "stage", "Miocene"),
    Interval("Serravallian", 13.82, 11.63, "stage", "Miocene"),
    Interval("Langhian", 15.98, 13.82, "stage", "Miocene"),
    Interval("Burdigalian", 20.44, 15.98, "stage", "Miocene"),
    Interval("Aquitanian", 23.04, 20.44, "stage", "Miocene"),
    Interval("Chattian", 27.29, 23.04, "stage", "Oligocene"),
    Interval("Rupelian", 33.9, 27.29, "stage", "Oligocene"),
    Interval("Priabonian", 37.71, 33.9, "stage", "Eocene"),
    Interval("Bartonian", 41.03, 37.71, "stage", "Eocene"),
    Interval("Lutetian", 47.8, 41.03, "stage", "Eocene"),
    Interval("Ypresian", 56.0, 47.8, "stage", "Eocene"),
    Interval("Thanetian", 59.24, 56.0, "stage", "Paleocene"),
    Interval("Selandian", 61.66, 59.24, "stage", "Paleocene"),
    Interval("Danian", 66.0, 61.66, "stage", "Paleocene"),
    Interval("Maastrichtian", 72.2, 66.0, "stage", "Late Cretaceous"),
    Interval("Campanian", 83.6, 72.2, "stage", "Late Cretaceous"),
    Interval("Santonian", 86.3, 83.6, "stage", "Late Cretaceous"),
    Interval("Coniacian", 89.39, 86.3, "stage", "Late Cretaceous"),
    Interval("Turonian", 93.9, 89.39, "stage", "Late Cretaceous"),
    Interval("Cenomanian", 100.5, 93.9, "stage", "Late Cretaceous"),
    Interval("Albian", 113.2, 100.5, "stage", "Early Cretaceous"),
    Interval("Aptian", 121.4, 113.2, "stage", "Early Cretaceous"),
    Interval("Barremian", 125.77, 121.4, "stage", "Early Cretaceous"),
    Interval("Hauterivian", 132.6, 125.77, "stage", "Early Cretaceous"),
    Interval("Valanginian", 137.05, 132.6, "stage", "Early Cretaceous"),
    Interval("Berriasian", 143.1, 137.05, "stage", "Early Cretaceous"),
    Interval("Tithonian", 149.2, 143.1, "stage", "Late Jurassic"),
    Interval("Kimmeridgian", 154.8, 149.2, "stage", "Late Jurassic"),
    Interval("Oxfordian", 161.5, 154.8, "stage", "Late Jurassic"),
    Interval("Callovian", 165.3, 161.5, "stage", "Middle Jurassic"),
    Interval("Bathonian", 168.2, 165.3, "stage", "Middle Jurassic"),
    Interval("Bajocian", 170.9, 168.2, "stage", "Middle Jurassic"),
    Interval("Aalenian", 174.7, 170.9, "stage", "Middle Jurassic"),
    Interval("Toarcian", 184.2, 174.7, "stage", "Early Jurassic"),
    Interval("Pliensbachian", 192.9, 184.2, "stage", "Early Jurassic"),
    Interval("Sinemurian", 199.5, 192.9, "stage", "Early Jurassic"),
    Interval("Hettangian", 201.4, 199.5, "stage", "Early Jurassic"),
    Interval("Rhaetian", 205.7, 201.4, "stage", "Late Triassic"),
    Interval("Norian", 227.0, 205.7, "stage", "Late Triassic"),
    Interval("Carnian", 237.0, 227.0, "stage", "Late Triassic"),
    Interval("Ladinian", 242.0, 237.0, "stage", "Middle Triassic"),
    Interval("Anisian", 246.7, 242.0, "stage", "Middle Triassic"),
    Interval("Olenekian", 249.9, 246.7, "stage", "Early Triassic"),
    Interval("Induan", 251.902, 249.9, "stage", "Early Triassic"),
    Interval("Changhsingian", 254.14, 251.902, "stage", "Lopingian"),
    Interval("Wuchiapingian", 259.51, 254.14, "stage", "Lopingian"),
    Interval("Capitanian", 264.28, 259.51, "stage", "Guadalupian"),
    Interval("Wordian", 266.9, 264.28, "stage", "Guadalupian"),
    Interval("Roadian", 274.4, 266.9, "stage", "Guadalupian"),
    Interval("Kungurian", 283.5, 274.4, "stage", "Cisuralian"),
    Interval("Artinskian", 290.1, 283.5, "stage", "Cisuralian"),
    Interval("Sakmarian", 293.5, 290.1, "stage", "Cisuralian"),
    Interval("Asselian", 298.9, 293.5, "stage", "Cisuralian"),
    Interval("Gzhelian", 303.7, 298.9, "stage", "Pennsylvanian"),
    Interval("Kasimovian", 307.0, 303.7, "stage", "Pennsylvanian"),
    Interval("Moscovian", 315.2, 307.0, "stage", "Pennsylvanian"),
    Interval("Bashkirian", 323.4, 315.2, "stage", "Pennsylvanian"),
    Interval("Serpukhovian", 330.3, 323.4, "stage", "Mississippian"),
    Interval("Visean", 346.7, 330.3, "stage", "Mississippian"),
    Interval("Tournaisian", 358.86, 346.7, "stage", "Mississippian"),
    Interval("Famennian", 371.1, 358.86, "stage", "Late Devonian"),
    Interval("Frasnian", 382.31, 371.1, "stage", "Late Devonian"),
    Interval("Hirnantian", 445.2, 443.1, "stage", "Late Ordovician"),
]

_ALL = {"eon": EONS, "era": ERAS, "period": PERIODS, "epoch": EPOCHS, "stage": STAGES}


def interval_at(age: float, rank: str = "period") -> Optional[Interval]:
    """The interval of `rank` containing `age` (Ma). None outside coverage."""
    for iv in _ALL[rank]:
        if iv.contains(age):
            return iv
    return None


def eon_at(age: float) -> Optional[Interval]:
    return interval_at(age, "eon")


def era_at(age: float) -> Optional[Interval]:
    return interval_at(age, "era")


def period_at(age: float) -> Optional[Interval]:
    return interval_at(age, "period")


def epoch_at(age: float) -> Optional[Interval]:
    return interval_at(age, "epoch")


def stage_at(age: float) -> Optional[Interval]:
    return interval_at(age, "stage")


# ---------------------------------------------------------------------------
# Climate states, after Judd et al. (2024) Science 385 eadk3705 (PhanDA).
# GMST bands; the state names follow the paper's five-state scheme.
# ---------------------------------------------------------------------------

CLIMATE_STATES = [
    Interval("icehouse", 18.0, -273.0, "climate-state"),      # GMST below 18
    Interval("cool greenhouse", 24.0, 18.0, "climate-state"),
    Interval("warm greenhouse", 30.0, 24.0, "climate-state"),
    Interval("hothouse", 40.0, 30.0, "climate-state"),
]
# NOTE these Interval objects are re-used with GMST on the "age" axis. Ugly but it
# keeps one containment rule. base = warmer bound, top = cooler bound.


def climate_state(gmst_c: float) -> Interval:
    """Name the PhanDA-style climate state for a global mean surface temperature."""
    for st in CLIMATE_STATES:
        if st.contains(gmst_c):
            return st
    return CLIMATE_STATES[-1] if gmst_c >= 30 else CLIMATE_STATES[0]


PHANDA = {
    "coverage": (485.0, 0.0),
    "gmst_min": 11.0,      # Late Pleistocene glacial
    "gmst_max": 36.0,      # Turonian, 93.9-89.39 Ma
    "apparent_earth_system_sensitivity_C_per_doubling": 8.0,
    "citation": "Judd, Tierney et al. 2024, Science 385, eadk3705",
}


# ---------------------------------------------------------------------------
# Event catalogues
# ---------------------------------------------------------------------------

GLACIATIONS = [
    Event("Huronian", "glaciation", 2450, 2220, "global?",
          "Follows the Great Oxidation Event; methane greenhouse destroyed.",
          "moderate", ("Great Oxidation Event",)),
    Event("Sturtian", "glaciation", 717.4, 661.7, "snowball",
          "~56 Myr, low-latitude ice. Ends with a CO2 spike near the ~350x modern escape threshold.",
          "good"),
    Event("Marinoan", "glaciation", 650.0, 635.5, "snowball",
          "Second Cryogenian snowball; terminated at ~12% CO2 by volume; cap carbonates.",
          "good"),
    Event("Gaskiers", "glaciation", 580.9, 579.6, "regional",
          "<=340 kyr and regional. NOT a snowball.", "good"),
    Event("Hirnantian", "glaciation", 445.2, 443.1, "major",
          "South Pole over North Africa. Drove the End-Ordovician extinction.", "good"),
    Event("Late Devonian glaciation", "glaciation", 372.0, 358.9, "moderate",
          "Diamictites and striated pavements in Bolivia, Peru, Brazil. Two pulses.",
          "moderate"),
    Event("Late Palaeozoic Ice Age", "glaciation", 360.0, 255.0, "major",
          "The longest Phanerozoic icehouse. Gondwanan ice sheets drive the coal-measure cyclothems.",
          "good"),
    Event("Early Cretaceous cool snap", "glaciation", 137.0, 125.0, "minor",
          "Contested: whether there was any ice at all is genuinely open.", "contested"),
    Event("Late Cenozoic Ice Age", "glaciation", 34.0, 0.0, "major",
          "Antarctic glaciation from ~34 Ma at ~760 ppm CO2; N Hemisphere sheets from ~2.7 Ma.",
          "good"),
]

EXTINCTIONS = [
    Event("End-Ordovician", "extinction", 445.2, 443.1, "~85% species",
          "Two pulses: glacial onset then deglaciation. Driven by the Hirnantian ice sheet.",
          "good", ("Hirnantian",)),
    Event("Late Devonian", "extinction", 382.0, 358.9, "~75% species",
          "Protracted; Kellwasser (F-F, ~372) and Hangenberg (D-C, ~359) pulses. Reef collapse.",
          "good", ("Kellwasser", "Hangenberg")),
    Event("End-Permian", "extinction", 251.94, 251.88, "~81% marine species",
          "The largest. Siberian Traps -> runaway CO2, ocean deoxygenation, equatorial dead zone. "
          "Land flora (Glossopteris) collapses ~350 kyr BEFORE the marine event.",
          "good", ("Siberian Traps",)),
    Event("End-Triassic", "extinction", 201.6, 201.3, "~76% species",
          "CAMP emplacement.", "good", ("CAMP",)),
    Event("End-Cretaceous (K-Pg)", "extinction", 66.05, 66.0, "~76% species",
          "Chicxulub impact; Deccan Traps overlapping. Impact winter then a warm pulse.",
          "good", ("Deccan Traps",)),
    Event("Capitanian", "extinction", 262.0, 259.0, "moderate",
          "Emeishan Traps; sometimes counted as a separate crisis before the End-Permian.",
          "moderate", ("Emeishan Traps",)),
    Event("Carboniferous rainforest collapse", "extinction", 307.0, 303.7, "minor, terrestrial",
          "Aridification + glaciation fragment the Euramerican coal forest. Lycopsids crash, "
          "tree ferns replace them. Amniotes favoured over labyrinthodonts. Cathaysian "
          "rainforest is UNAFFECTED and persists to the end-Permian.", "good"),
    Event("End-Ediacaran", "extinction", 545.0, 538.8, "biota turnover",
          "Ediacaran biota vanish. Cause contested: predation, substrate revolution, "
          "competition, environmental change.", "contested"),
    Event("Holocene / Anthropocene", "extinction", 0.06, -0.6, "in progress",
          "100-1000x background rate, but not yet at the Big Five ~75% threshold.",
          "contested"),
]

ANOXIC_EVENTS = [
    Event("SPICE", "anoxia", 497.0, 494.0, "", "Steptoean positive carbon isotope excursion.", "moderate"),
    Event("Hirnantian anoxia", "anoxia", 445.2, 443.1, "", "Repetitive, oxic-interspersed.", "moderate"),
    Event("Ireviken", "anoxia", 433.4, 432.0, "", "", "moderate"),
    Event("Lau", "anoxia", 424.0, 423.0, "", "", "moderate"),
    Event("Kellwasser", "anoxia", 372.5, 371.1, "", "Frasnian-Famennian; reef crisis.", "good"),
    Event("Hangenberg", "anoxia", 359.3, 358.9, "", "Devonian-Carboniferous boundary.", "good"),
    Event("P-Tr deoxygenation", "anoxia", 252.0, 250.0, "", "Siberian Traps CO2; euxinic upwelling.", "good"),
    Event("T-OAE (Toarcian)", "anoxia", 183.4, 182.6, "<1 Myr", "Karoo-Ferrar.", "good", ("Karoo-Ferrar",)),
    Event("OAE 1a (Selli)", "anoxia", 120.5, 119.3, "1.0-1.3 Myr", "Ontong Java Plateau.",
          "good", ("Ontong Java",)),
    Event("OAE 1b (Paquier)", "anoxia", 113.0, 111.0, "", "Albian.", "moderate"),
    Event("OAE 2 (Bonarelli)", "anoxia", 94.3, 93.5, "~820 kyr",
          "Cenomanian-Turonian boundary. Caribbean / Madagascar LIPs.", "good",
          ("Caribbean LIP",)),
    Event("OAE 3", "anoxia", 88.0, 84.0, "", "Coniacian-Santonian; more regional.", "moderate"),
]

HYPERTHERMALS = [
    Event("PETM", "hyperthermal", 56.0, 55.8, "+5-8 C",
          "Onset in ~20 kyr, recovery ~200 kyr. Arctic Ocean reaches temperate SSTs.",
          "good", ("North Atlantic Igneous Province",)),
    Event("ETM-2 (ELMO)", "hyperthermal", 54.1, 54.0, "+3 C", "", "good"),
    Event("EECO", "hyperthermal", 53.0, 49.0, "Cenozoic peak", "Early Eocene Climatic Optimum.", "good"),
    Event("MECO", "hyperthermal", 40.5, 40.0, "+4-6 C", "Middle Eocene Climatic Optimum.", "good"),
    Event("MMCO", "hyperthermal", 17.0, 14.0, "", "Mid-Miocene Climatic Optimum.", "good"),
    Event("Cretaceous Thermal Maximum", "hyperthermal", 93.9, 89.39, "GMST ~36 C",
          "The PhanDA global maximum, in the Turonian.", "good"),
]

LIPS = [
    #    name                         base   top    area/volume note
    Event("Siberian Traps", "lip", 252.3, 250.2, "1.5-3.9 Mkm2 / 0.9-2.0 Mkm3",
          "End-Permian extinction.", "good", ("End-Permian",)),
    Event("Emeishan Traps", "lip", 260.0, 257.0, "", "Capitanian crisis.", "good", ("Capitanian",)),
    Event("CAMP", "lip", 201.6, 197.0, "11 Mkm2 / 2.5 Mkm3",
          "Largest continental LIP; buried in its own rift basins, so a landform almost nowhere.",
          "good", ("End-Triassic",)),
    Event("Karoo-Ferrar", "lip", 184.0, 178.0, "", "Toarcian OAE.", "good", ("T-OAE (Toarcian)",)),
    Event("Parana-Etendeka", "lip", 135.0, 130.0, "", "South Atlantic opening; Tristan plume.", "good"),
    Event("Ontong Java", "lip", 124.0, 120.0, "1.86 Mkm2 / 8.4 Mkm3",
          "Largest oceanic plateau. OAE 1a.", "good", ("OAE 1a (Selli)",)),
    Event("Kerguelen Plateau", "lip", 118.0, 95.0, "", "Kerguelen plume; Ninetyeast Ridge from ~100 Ma.", "good"),
    Event("Caribbean LIP", "lip", 95.0, 88.0, "", "Galapagos plume. OAE 2.", "good", ("OAE 2 (Bonarelli)",)),
    Event("Madagascar", "lip", 92.0, 84.0, "", "", "good"),
    Event("Deccan Traps", "lip", 68.5, 65.5, "0.5-0.8 Mkm2 / 0.5-1.0 Mkm3",
          "Reunion plume. Overlaps Chicxulub; predates it by ~1 Myr, so it cannot have been "
          "triggered by it.", "good", ("End-Cretaceous (K-Pg)",)),
    Event("North Atlantic Igneous Province", "lip", 62.0, 55.0, "1.3 Mkm2 / 6.6 Mkm3",
          "Iceland plume. PETM.", "good", ("PETM",)),
    Event("Columbia River Basalt", "lip", 16.7, 15.9, "", "Yellowstone plume.", "good"),
]

_CATALOGUES = {
    "glaciation": GLACIATIONS,
    "extinction": EXTINCTIONS,
    "anoxia": ANOXIC_EVENTS,
    "hyperthermal": HYPERTHERMALS,
    "lip": LIPS,
}


def events_at(age: float, kinds: Optional[Iterable[str]] = None) -> list:
    """Every catalogued event whose window contains `age`."""
    kinds = list(kinds) if kinds else list(_CATALOGUES)
    out = []
    for k in kinds:
        out.extend(e for e in _CATALOGUES[k] if e.contains(age))
    return sorted(out, key=lambda e: -e.base)


def events_in(base: float, top: float, kinds: Optional[Iterable[str]] = None) -> list:
    """Every catalogued event overlapping the window [top, base] Ma."""
    kinds = list(kinds) if kinds else list(_CATALOGUES)
    out = []
    for k in kinds:
        out.extend(e for e in _CATALOGUES[k] if e.base >= top and e.top <= base)
    return sorted(out, key=lambda e: -e.base)


# ---------------------------------------------------------------------------

def _selftest() -> None:
    assert stage_at(66.5).name == "Maastrichtian", stage_at(66.5)
    assert period_at(300.0).name == "Carboniferous"
    assert epoch_at(93.0).name == "Late Cretaceous"
    assert era_at(200.0).name == "Mesozoic"
    assert climate_state(36.0).name == "hothouse"
    assert climate_state(11.0).name == "icehouse"
    assert climate_state(26.0).name == "warm greenhouse"
    # A GSSP defines the BASE of a unit, so the boundary instant is the first
    # instant of the YOUNGER unit: 66.0 Ma is Paleogene, 66.001 Ma is Cretaceous.
    assert period_at(66.0).name == "Paleogene", period_at(66.0)
    assert period_at(66.001).name == "Cretaceous", period_at(66.001)
    # every stage sits inside its parent epoch
    epochs = {e.name: e for e in EPOCHS}
    for s in STAGES:
        p = epochs.get(s.parent)
        if p is None:
            continue
        assert p.top <= s.top and s.base <= p.base, f"{s.name} escapes {s.parent}"
    # every epoch sits inside its parent period
    periods = {p.name: p for p in PERIODS}
    for e in EPOCHS:
        p = periods.get(e.parent)
        if p is None:
            continue
        assert p.top <= e.top and e.base <= p.base, f"{e.name} escapes {e.parent}"
    # no gaps or overlaps in the period column across the Phanerozoic
    phan = sorted([p for p in PERIODS if p.base <= 538.8], key=lambda p: p.top)
    for a, b in zip(phan, phan[1:]):
        assert abs(a.base - b.top) < 1e-6, f"gap/overlap {a.name}|{b.name}"
    # events resolve
    assert any(e.name == "End-Cretaceous (K-Pg)" for e in events_at(66.02))
    assert any(e.name == "Late Palaeozoic Ice Age" for e in events_at(300))
    print("deeptime selftest OK:",
          f"{len(STAGES)} stages, {len(EPOCHS)} epochs, {len(PERIODS)} periods, "
          f"{sum(len(v) for v in _CATALOGUES.values())} events")


if __name__ == "__main__":
    _selftest()
