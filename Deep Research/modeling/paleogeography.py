"""Continental blocks through deep time: what each block was part of, when.

The purpose is narrow and practical. Tectonic Earth draws named labels for
continental entities ("Laurentia", "Cimmeria", "Avalonia", "Gondwana"), and the
recurring failure is that a label is drawn at an age when its entity did not
exist, or is anchored on a coordinate that was not part of it. This module is the
reference table that answers both questions:

    affiliation("Laurentia", 300)   -> 'Laurussia' (inside Pangaea)
    exists("Avalonia", 700)         -> False
    anchors("Cimmeria")             -> the seven present-day fragments

`anchors` returns PRESENT-DAY coordinates on modern land, which is the only kind
of coordinate that can be back-advected by a rotation model. This is the rule the
main build learned the hard way: 18 terranes had been authored at their era
positions and drifted nonsensically.

Everything here is a published-consensus summary with explicit confidence. Where
the literature disagrees (Rodinia configuration, Pannotia's existence, the exact
age of a suture) the entry says so rather than picking silently.

Sources: see research/01-plate-tectonics/01-supercontinent-cycle.md
Dependency-free (stdlib only).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__all__ = [
    "Block", "BLOCKS", "ASSEMBLIES", "OROGENIES",
    "exists", "affiliation", "anchors", "blocks_in", "history", "recognisable_until",
    "rift_events", "accretion_events",
]


@dataclass(frozen=True)
class Block:
    """A continental block: craton, terrane or microcontinent."""
    name: str
    kind: str                     # craton | terrane | microcontinent | composite
    anchors: tuple                # ((lon, lat), ...) present-day, on modern land
    first: float                  # Ma: when it is first identifiable as this entity
    last: float                   # Ma: 0 if it survives to the present
    note: str = ""
    confidence: str = "good"      # good | moderate | contested


# ---------------------------------------------------------------------------
# Blocks. Anchors are present-day coordinates chosen to sit on land TODAY, which
# is the gate the main build's coord_is_present_day() applies.
# ---------------------------------------------------------------------------

_B = [
    # ---- Laurentian realm -------------------------------------------------
    Block("Laurentia", "craton",
          ((-95, 55), (-85, 50), (-113, 64), (-108, 44), (-105, 60), (-95, 66),
           (-62, 56), (-42, 72)),
          1900, 0,
          "Assembled ~2.0-1.8 Ga from Superior, Slave, Wyoming, Hearne, Rae, Nain. "
          "Grenville 1.30-0.95 Ga on its SE margin; Midcontinent Rift ~1.1 Ga nearly "
          "split it. Core of Rodinia.",
          "good"),
    Block("Superior Craton", "craton", ((-85, 50),), 2700, 0, "Archean; Algoman/Kenoran 2.7-2.5 Ga."),
    Block("Slave Craton", "craton", ((-113, 64),), 4030, 0, "Contains the Acasta Gneiss, 4.03-3.58 Ga."),
    Block("Wyoming Craton", "craton", ((-108, 44),), 2900, 0, ""),
    Block("Rae Craton", "craton", ((-95, 66),), 2700, 0, ""),
    Block("Hearne Craton", "craton", ((-105, 60),), 2700, 0, ""),
    Block("Nain Province", "craton", ((-62, 56),), 3800, 0, ""),

    # ---- Baltic realm -----------------------------------------------------
    Block("Baltica", "craton", ((25, 63), (32, 49), (50, 55)),
          1700, 0,
          "Fennoscandia + Sarmatia + Volgo-Uralia; Sarmatia-Volgo-Uralia ~2.0 Ga, "
          "onto Fennoscandia 1.8-1.7 Ga. Timanide margin accreted ~620-550 Ma.",
          "good"),
    Block("Fennoscandia", "craton", ((25, 63),), 1900, 0, ""),
    Block("Sarmatia", "craton", ((32, 49),), 2000, 0, "Ukrainian Shield, Voronezh Massif."),
    Block("Volgo-Uralia", "craton", ((50, 55),), 2000, 0, "Buried under younger cover."),
    Block("Timan-Pechora", "terrane", ((55, 66), (57, 74)), 620, 0,
          "Accreted to N Baltica in the Timanide orogeny ~620-550 Ma.", "good"),

    # ---- Siberian realm ---------------------------------------------------
    Block("Siberia", "craton", ((102, 71), (128, 58), (100, 64)),
          2500, 0,
          "Independent through the early Palaeozoic; collided with Kazakhstania in the "
          "Carboniferous, then with Laurussia in the late Carboniferous-Permian. "
          "Verkhoyansk passive margin on its east.", "good"),
    Block("Kazakhstania", "composite", ((68, 48),), 500, 0,
          "Amalgamated arcs; closes the Ural Ocean against Baltica in the Uralian orogeny.",
          "moderate"),
    Block("Amuria / Mongolia", "composite", ((105, 47),), 500, 0,
          "Central Asian Orogenic Belt collage; Mongol-Okhotsk Ocean closes progressively "
          "west to east through the Jurassic-Cretaceous.", "moderate"),

    # ---- Gondwanan cratons ------------------------------------------------
    Block("Amazonia", "craton", ((-60, -5), (-58, 4), (-52, -12)), 2000, 0, ""),
    Block("Sao Francisco", "craton", ((-42, -12),), 2000, 0, ""),
    Block("Rio de la Plata", "craton", ((-56, -33),), 2000, 0, ""),
    Block("West African Craton", "craton", ((-8, 18), (-8, 8)), 2100, 0, "Eburnean 2.2-2.0 Ga."),
    Block("Congo Craton", "craton", ((22, -2),), 2500, 0, ""),
    Block("Tanzania Craton", "craton", ((34, -5),), 2700, 0, ""),
    Block("Kalahari Craton", "craton", ((25, -25), (28, -27), (30, -19)), 2900, 0,
          "Kaapvaal + Zimbabwe, joined by the Limpopo belt."),
    Block("India", "craton", ((76, 14), (79, 25), (86, 22), (74, 25)), 2500, 0,
          "Dharwar, Bundelkhand, Singhbhum, Aravalli. Rifts from Madagascar ~88-70 Ma, "
          "collides with Asia from ~50 Ma.", "good"),
    Block("Madagascar", "microcontinent", ((47, -19),), 800, 0,
          "Splits from Africa ~150 Ma with India, from India ~88-70 Ma.", "good"),
    Block("Seychelles", "microcontinent", ((55, -4),), 750, 0,
          "Separates from India at ~66 Ma with the Deccan.", "good"),
    Block("Australia", "craton", ((119, -21), (120, -28), (135, -31), (133, -18)), 2700, 0,
          "Pilbara, Yilgarn, Gawler, North Australian. Separates from Antarctica: "
          "rifting 132 Ma, spreading ~96 Ma, gateway open ~33 Ma.", "good"),
    Block("East Antarctica", "craton", ((75, -72), (50, -66), (105, -70)), 3000, 0, ""),
    Block("Arabia", "craton", ((44, 22),), 800, 0, "Arabian-Nubian Shield; rifts from Africa ~25 Ma."),
    Block("Azania", "terrane", ((45, -20), (44, 9)), 900, 0,
          "Central Madagascar, Horn of Africa, parts of Yemen/Arabia. Malagasy orogeny "
          "550-515 Ma.", "moderate"),

    # ---- Peri-Gondwanan terranes -----------------------------------------
    Block("Avalonia", "terrane",
          ((-53, 47), (-63, 45), (-66, 45), (-71, 42), (-1, 52), (-3, 52), (4, 51), (9, 53)),
          650, 0,
          "Volcanic arcs off Rodinia ~800 Ma, onto Gondwana ~650 Ma. Rifts Late Cambrian-"
          "Early Ordovician from ~60S, opening the Rheic. Docks with Baltica 457-449 Ma "
          "at 30S, with Laurentia in the Silurian-Devonian (Acadian).", "good"),
    Block("Armorica", "terrane", ((-3, 48), (-5, 40), (14, 50)), 540, 0,
          "Brittany, Iberia, Bohemia. Rheic closes ahead, Palaeo-Tethys opens behind. "
          "Detaches as an orocline in the Variscan, near the C-P boundary.", "moderate"),
    Block("Cimmeria", "composite",
          ((90, 30), (90, 34), (99, 17), (58, 32), (32, 37), (68, 35), (52, 36)),
          300, 0,
          "A RIBBON, not a block: Lhasa, Qiangtang, Sibumasu, Lut, Taurides, Afghan, "
          "Alborz. Rifts off Gondwana in the Late Carboniferous-Early Permian, opening "
          "Neo-Tethys behind it while Palaeo-Tethys closes ahead. Anchor each fragment "
          "on the ground it BECAME, never on its era position.", "good"),
    Block("Lhasa", "terrane", ((90, 30),), 250, 0, "Rifts Late Triassic-Late Jurassic; docks Early Cretaceous."),
    Block("Qiangtang", "terrane", ((90, 34),), 300, 0, "Rifts Late Carb-Early Permian; docks Early Jurassic."),
    Block("Sibumasu", "terrane", ((99, 17),), 300, 0, "Shan-Thai. Docks Late Permian-Early Jurassic."),
    Block("Indochina", "terrane", ((105, 15),), 500, 0, ""),
    Block("North China", "craton", ((115, 39),), 2500, 0,
          "Rifts from Gondwana in the Devonian; docks with Mongolia/Siberia in the "
          "Carboniferous-Permian. Its everwet CATHAYSIAN flora persists to the end-Permian "
          "when Euramerica's has long dried out.", "good"),
    Block("South China", "craton", ((110, 29),), 2500, 0,
          "Yangtze + Cathaysia. Docks with Asia in the Permian-Triassic. Emeishan Traps on "
          "its western margin at ~260 Ma. Hosts Chengjiang and Qingjiang.", "good"),
    Block("Tarim", "craton", ((82, 40),), 2000, 0, ""),
    Block("Qaidam", "terrane", ((95, 37),), 500, 0, ""),
    Block("Iberia", "terrane", ((-5, 40),), 540, 0, ""),
    Block("Adria / Apulia", "terrane", ((13, 42),), 250, 0,
          "Promontory of Africa; its northward push builds the Alps.", "moderate"),
    Block("Florida", "terrane", ((-82, 28),), 550, 0,
          "A Gondwanan fragment left behind on Laurentia when the central Atlantic opened.",
          "good"),

    # ---- South American accretions ---------------------------------------
    Block("Cuyania / Precordillera", "terrane", ((-69, -31),), 550, 0,
          "Transferred FROM Laurentia; scrapes along SE Laurentia and accretes to Gondwana "
          "in the Ordovician. May continue the Appalachians southward.", "moderate"),
    Block("Chilenia", "terrane", ((-70, -33),), 500, 0, "Accretes after Cuyania."),
    Block("Patagonia", "terrane", ((-68, -45),), 400, 0,
          "Subduction initiates 330-320 Ma; collision Early Permian, ~20 Myr.", "moderate"),
    Block("Falkland / Malvinas", "terrane", ((-59, -52),), 500, 0,
          "Rotated ~90 deg in the Early Jurassic.", "moderate"),

    # ---- Pacific-margin terranes -----------------------------------------
    Block("Wrangellia", "terrane", ((-140, 61), (-127, 52)), 300, 0,
          "Oceanic plateau terrane; accreted to western North America in the Jurassic-"
          "Cretaceous. Anchor on Alaska/Yukon/Vancouver Island.", "good"),
    Block("Stikinia", "terrane", ((-128, 57),), 300, 0, ""),
    Block("Alexander", "terrane", ((-134, 57),), 500, 0, ""),
    Block("Sonomia", "terrane", ((-118, 40),), 350, 0, "Sonoma orogeny, Permo-Triassic."),
    Block("Zealandia", "microcontinent", ((172, -42), (174, -37)), 100, 0,
          "Separates from Australia/Antarctica ~84 Ma; ~94% submerged today. Includes "
          "Campbell Plateau, Chatham Rise, Lord Howe Rise.", "good"),
    Block("Marie Byrd Land", "terrane", ((-120, -77),), 400, 0, "Detaches ~184 Ma with Karoo-Ferrar."),
    Block("Antarctic Peninsula", "terrane", ((-64, -68),), 400, 0, ""),

    # ---- Submerged / plateau blocks --------------------------------------
    Block("Mauritia", "microcontinent", ((57, -20),), 90, 0,
          "Continental sliver between Madagascar and India, now buried under the Mascarene "
          "volcanics. Submerged: cannot be anchored by a land-today test.", "moderate"),
    Block("Kerguelen Plateau", "microcontinent", ((69, -49),), 118, 0,
          "LIP, not continental crust, but it carried land plants when emergent 118-95 Ma.",
          "good"),
]

BLOCKS = {b.name: b for b in _B}


# ---------------------------------------------------------------------------
# Assemblies: which blocks belonged to which larger entity, when.
# (base, top) in Ma. A block can appear in several assemblies at once only if
# they nest (Laurentia in Laurussia in Pangaea).
# ---------------------------------------------------------------------------

ASSEMBLIES = {
    "Rodinia": dict(
        base=1250, top=750, confidence="moderate",
        breakup_onset=825, dispersed=550,
        breakup_note="Breakup runs in four stages from ~825 Ma; the last Laurentia-Amazonia link goes at ~550.",
        note="Configuration actively disputed. Laurentia at the centre; the block off its "
             "present-western margin is the argument (SWEAT/AUSWUS/AUSMEX/Missing-Link).",
        members=["Laurentia", "Baltica", "Amazonia", "West African Craton", "Sao Francisco",
                 "Rio de la Plata", "Congo Craton", "Kalahari Craton", "Australia",
                 "India", "East Antarctica", "Siberia", "North China", "South China", "Tarim"],
        disputed=["Siberia", "North China", "South China", "Tarim"],
    ),
    "Pannotia": dict(
        base=633, top=573, confidence="contested",
        breakup_onset=573, dispersed=530,
        breakup_note="If it existed at all, it was coming apart as it formed.",
        note="May never have been a single coherent mass: Gondwana's assembly overlapped "
             "Laurentia's departure from Amazonia. Several authors reject it outright.",
        members=["Laurentia", "Baltica", "Amazonia", "West African Craton", "Congo Craton",
                 "Kalahari Craton", "Australia", "India", "East Antarctica"],
        disputed=["Laurentia", "Baltica"],
    ),
    "Gondwana": dict(
        base=550, top=180, confidence="good",
        breakup_onset=180, dispersed=30,
        breakup_note="Fragmentation runs 180 Ma (Weddell) to the Drake Passage at ~30 Ma; South America and Africa are still joined at ~120.",
        note="~100 million km2, one fifth of Earth's surface. Assembled by the Pan-African "
             "orogenies; joins Laurussia at ~335 Ma to complete Pangaea but remains a "
             "recognisable half of it until the Jurassic.",
        members=["Amazonia", "Sao Francisco", "Rio de la Plata", "West African Craton",
                 "Congo Craton", "Tanzania Craton", "Kalahari Craton", "India", "Madagascar",
                 "Australia", "East Antarctica", "Arabia", "Azania", "Florida",
                 "Cuyania / Precordillera", "Chilenia", "Patagonia", "Falkland / Malvinas",
                 "Marie Byrd Land", "Antarctic Peninsula", "Seychelles"],
        disputed=[],
    ),
    "Laurussia": dict(
        base=425, top=175, confidence="good",
        breakup_onset=175, dispersed=60,
        breakup_note="Survives inside Pangaea and outlives it; the North Atlantic finishes the job at ~60 Ma.",
        note="Also Euramerica or the Old Red Sandstone Continent. Laurentia + Baltica + "
             "Avalonia after the Caledonian orogeny.",
        members=["Laurentia", "Baltica", "Avalonia", "Timan-Pechora"],
        disputed=[],
    ),
    "Laurasia": dict(
        base=300, top=60, confidence="good",
        breakup_onset=60, dispersed=30,
        breakup_note="North Atlantic opening completes the separation.",
        note="Laurussia + Siberia + Kazakhstania after the Uralian orogeny; the northern "
             "half of Pangaea, and it outlives Pangaea's southern breakup.",
        members=["Laurentia", "Baltica", "Avalonia", "Siberia", "Kazakhstania",
                 "Timan-Pechora", "North China", "Amuria / Mongolia", "Armorica", "Iberia"],
        disputed=["North China"],
    ),
    "Pangaea": dict(
        base=335, top=175, confidence="good",
        breakup_onset=175, dispersed=100,
        breakup_note="Rifting from ~175; the mass is not recognisable as one continent much past the mid-Cretaceous.",
        note="C-shaped around the Tethys embayment, with Panthalassa everywhere else. "
             "Central Pangaean Mountains peak ~295 Ma at Himalayan scale.",
        members=["Laurentia", "Baltica", "Avalonia", "Siberia", "Kazakhstania", "Armorica",
                 "Iberia", "Amazonia", "Sao Francisco", "Rio de la Plata",
                 "West African Craton", "Congo Craton", "Kalahari Craton", "India",
                 "Australia", "East Antarctica", "Arabia", "Madagascar", "Florida",
                 "Patagonia", "Timan-Pechora"],
        disputed=["North China", "South China"],
    ),
}


# ---------------------------------------------------------------------------
# Orogenies that WELD blocks, with what they welded. Ages from topic articles,
# not from Wikipedia's List of orogenies table (which has several bad rows).
# ---------------------------------------------------------------------------

OROGENIES = [
    # (name, base, top, welded, region)
    ("Trans-Hudson", 1850, 1800, ("Superior Craton", "Hearne Craton", "Rae Craton"), "Laurentia"),
    ("Penokean", 1850, 1840, (), "Laurentia"),
    ("Yavapai", 1710, 1680, (), "Laurentia"),
    ("Mazatzal", 1675, 1600, (), "Laurentia"),
    ("Svecofennian", 2000, 1750, ("Fennoscandia",), "Baltica"),
    ("Grenville", 1300, 950, ("Laurentia", "Amazonia"), "Rodinia assembly"),
    ("Sveconorwegian", 1250, 900, ("Baltica",), "Rodinia assembly"),
    ("Musgrave", 1200, 1000, ("Australia",), "Rodinia assembly"),
    ("Sunsas", 1400, 1100, ("Amazonia",), "Rodinia assembly"),
    ("East African", 800, 650, ("India", "Madagascar", "Tanzania Craton", "Congo Craton"),
     "Gondwana assembly - closes the Mozambique Ocean"),
    ("Brasiliano", 660, 530, ("Amazonia", "Sao Francisco", "Rio de la Plata", "Congo Craton",
                              "West African Craton"), "Gondwana assembly"),
    ("Malagasy", 550, 515, ("India", "Azania", "Congo Craton"), "Gondwana assembly"),
    ("Kuunga / Pinjarra", 570, 530, ("Australia", "East Antarctica", "India"), "Gondwana assembly"),
    ("Damara", 530, 500, ("Congo Craton", "Kalahari Craton"), "Gondwana assembly"),
    ("Timanide", 620, 550, ("Baltica", "Timan-Pechora"), "N Baltica"),
    ("Cadomian", 660, 540, ("Avalonia", "Armorica"), "peri-Gondwanan arcs"),
    ("Ross", 550, 480, ("East Antarctica",), "Pacific margin of Gondwana"),
    ("Delamerian", 514, 490, ("Australia",), "Gondwanan margin"),
    ("Taconic", 470, 440, ("Laurentia",), "Laurentian margin - arc collision"),
    ("Caledonian (Scandian)", 490, 390, ("Laurentia", "Baltica", "Avalonia"),
     "Laurussia assembly - closes Iapetus"),
    ("Acadian", 420, 380, ("Laurentia", "Avalonia"), "Laurussia assembly"),
    ("Antler", 350, 320, ("Laurentia",), "western Laurentia"),
    ("Variscan / Hercynian", 380, 290, ("Laurussia", "Gondwana", "Armorica", "Iberia"),
     "Pangaea assembly - closes the Rheic"),
    ("Alleghanian", 325, 260, ("Laurentia", "West African Craton"),
     "Pangaea assembly - Central Pangaean Mountains"),
    ("Ouachita", 320, 280, ("Laurentia", "Gondwana"), "Pangaea assembly"),
    ("Uralian", 320, 250, ("Baltica", "Kazakhstania", "Siberia"),
     "Laurasia assembly - closes the Ural Ocean"),
    ("Gondwanide", 280, 250, ("Patagonia", "Kalahari Craton"), "southern Gondwana margin"),
    ("Sonoma", 260, 240, ("Sonomia", "Laurentia"), "western Laurentia"),
    ("Cimmerian", 250, 150, ("Cimmeria", "Laurasia"), "closes Palaeo-Tethys"),
    ("Nevadan", 175, 140, ("Laurentia",), "western Laurentia"),
    ("Sevier", 140, 50, ("Laurentia",), "western North America"),
    ("Laramide", 80, 40, ("Laurentia",), "Rocky Mountains, flat-slab"),
    ("Alpine", 65, 0, ("Adria / Apulia", "Iberia"), "Europe"),
    ("Himalayan", 50, 0, ("India", "Lhasa"), "Asia"),
    ("Andean", 200, 0, (), "South America - ongoing"),
]


# ---------------------------------------------------------------------------
# Rifting and accretion events for terranes. (block, base, top, kind, from/to)
# ---------------------------------------------------------------------------

_TERRANE_EVENTS = [
    ("Avalonia", 500, 480, "rift", "Gondwana", "opens the Rheic Ocean; starts near 60S"),
    ("Avalonia", 457, 449, "accrete", "Baltica", "closes the Tornquist Sea, at 30S"),
    ("Avalonia", 420, 400, "accrete", "Laurentia", "Acadian orogeny"),
    ("Armorica", 480, 450, "rift", "Gondwana", ""),
    ("Armorica", 340, 300, "accrete", "Laurussia", "Variscan; detaches as an orocline"),
    ("North China", 400, 380, "rift", "Gondwana", "opens Proto-Tethys"),
    ("North China", 320, 250, "accrete", "Siberia / Mongolia", ""),
    ("South China", 400, 380, "rift", "Gondwana", ""),
    ("South China", 260, 230, "accrete", "Asia", ""),
    ("Tarim", 400, 380, "rift", "Gondwana", ""),
    ("Tarim", 300, 260, "accrete", "Asia", ""),
    ("Sibumasu", 300, 280, "rift", "Gondwana", "opens Neo-Tethys"),
    ("Sibumasu", 260, 190, "accrete", "SE Asia", ""),
    ("Qiangtang", 300, 280, "rift", "Gondwana", ""),
    ("Qiangtang", 200, 175, "accrete", "Asia", ""),
    ("Lhasa", 230, 150, "rift", "Gondwana", ""),
    ("Lhasa", 140, 100, "accrete", "Asia", ""),
    ("Cimmeria", 300, 275, "rift", "Gondwana", "Neo-Tethys opens behind, Palaeo-Tethys closes ahead"),
    ("Cuyania / Precordillera", 500, 480, "rift", "Laurentia", "transferred, not Gondwanan in origin"),
    ("Cuyania / Precordillera", 470, 450, "accrete", "Gondwana", "Famatinian"),
    ("Patagonia", 330, 320, "accrete", "Gondwana", "subduction initiates; collision Early Permian"),
    ("Wrangellia", 200, 100, "accrete", "Laurentia", "Cordilleran collage"),
    ("Marie Byrd Land", 184, 180, "rift", "Gondwana", "Karoo-Ferrar plume"),
    ("Falkland / Malvinas", 190, 175, "rotate", "Gondwana", "~90 deg rotation"),
    ("Madagascar", 160, 150, "rift", "Africa", "with India"),
    ("India", 132, 120, "rift", "Australia / Antarctica", ""),
    ("India", 88, 70, "rift", "Madagascar", ""),
    ("Seychelles", 68, 63, "rift", "India", "Deccan"),
    ("India", 55, 40, "accrete", "Asia", "Himalayan collision; hard collision age contested"),
    ("Zealandia", 100, 84, "rift", "Australia / Antarctica", "arc-to-rift switch at ~100 Ma"),
    ("Arabia", 30, 20, "rift", "Africa", "Red Sea"),
]


# ---------------------------------------------------------------------------
# queries
# ---------------------------------------------------------------------------

def exists(block: str, age: float) -> bool:
    """Was `block` a recognisable entity at `age` Ma?"""
    b = BLOCKS.get(block)
    if b is None:
        raise KeyError(f"unknown block {block!r}")
    return b.last <= age <= b.first


def affiliation(block: str, age: float) -> list:
    """Which assemblies contained `block` at `age`, largest last.

    Returns [] if the block was independent (or did not exist)."""
    out = []
    for name, a in ASSEMBLIES.items():
        if a["top"] <= age <= a["base"] and block in a["members"]:
            out.append(name)
    # nest: Laurussia inside Laurasia inside Pangaea
    order = {"Rodinia": 0, "Pannotia": 0, "Gondwana": 1, "Laurussia": 1,
             "Laurasia": 2, "Pangaea": 3}
    return sorted(out, key=lambda n: order.get(n, 9))


def anchors(block: str) -> tuple:
    """Present-day (lon, lat) anchor points for the block. These are what a
    rotation model should back-advect; they are chosen to be on land today."""
    return BLOCKS[block].anchors


def recognisable_until(assembly: str) -> float:
    """The age by which the mass is no longer recognisable as itself.

    ASSEMBLIES["top"] is when BREAKUP BEGINS, which is not the same thing: Pangaea
    starts rifting at ~175 Ma and is still a recognisable single continent for
    another 75 Myr, and South America and Africa are still joined at ~120 Ma long
    after "Gondwana breaks up at 180". A label naming the mass may legitimately
    draw until this later date, so an audit that uses `top` reports false errors.
    """
    a = ASSEMBLIES[assembly]
    return a.get("dispersed", a["top"])


def blocks_in(assembly: str, age: Optional[float] = None) -> list:
    """Member blocks of an assembly, optionally filtered to those existing at `age`."""
    a = ASSEMBLIES[assembly]
    m = list(a["members"])
    if age is None:
        return m
    if not (a["top"] <= age <= a["base"]):
        return []
    return [n for n in m if n in BLOCKS and exists(n, age)]


def rift_events(block: Optional[str] = None) -> list:
    return [e for e in _TERRANE_EVENTS if e[3] == "rift" and (block is None or e[0] == block)]


def accretion_events(block: Optional[str] = None) -> list:
    return [e for e in _TERRANE_EVENTS if e[3] == "accrete" and (block is None or e[0] == block)]


def history(block: str) -> list:
    """A chronological narrative of everything known here about a block."""
    b = BLOCKS[block]
    rows = [(b.first, f"{b.kind} recognisable from ~{b.first:g} Ma. {b.note}".strip())]
    for name, base, top, welded, region in OROGENIES:
        if block in welded:
            rows.append((base, f"{name} orogeny {base:g}-{top:g} Ma: {region}"))
    for blk, base, top, kind, partner, note in _TERRANE_EVENTS:
        if blk == block:
            verb = {"rift": "rifts from", "accrete": "accretes to", "rotate": "rotates within"}[kind]
            rows.append((base, f"{base:g}-{top:g} Ma: {verb} {partner}" + (f" - {note}" if note else "")))
    for name, a in ASSEMBLIES.items():
        if block in a["members"]:
            tag = " (disputed)" if block in a.get("disputed", []) else ""
            rows.append((a["base"], f"part of {name} {a['base']:g}-{a['top']:g} Ma{tag}"))
    return [t for _, t in sorted(rows, key=lambda r: -r[0])]


# ---------------------------------------------------------------------------

def _selftest() -> None:
    # anchors must be plausible lon/lat
    for b in BLOCKS.values():
        assert b.anchors, f"{b.name} has no anchors"
        for lon, lat in b.anchors:
            assert -180 <= lon <= 180 and -90 <= lat <= 90, f"{b.name} bad anchor {lon},{lat}"
        assert b.first > b.last, f"{b.name} first<=last"
    # every assembly member is a known block
    for name, a in ASSEMBLIES.items():
        for m in a["members"]:
            assert m in BLOCKS, f"{name} references unknown block {m!r}"
        for m in a.get("disputed", []):
            assert m in BLOCKS, f"{name} disputed references unknown block {m!r}"
        assert a["base"] > a["top"], name
    # every orogeny welds known blocks
    for name, base, top, welded, region in OROGENIES:
        assert base > top, f"{name} base<=top"
        for w in welded:
            assert w in BLOCKS or w in ASSEMBLIES, f"{name} welds unknown {w!r}"
    # every terrane event names a known block
    for blk, base, top, kind, partner, note in _TERRANE_EVENTS:
        assert blk in BLOCKS, f"unknown block in event: {blk!r}"
        assert base >= top, f"{blk} {kind} base<top"
        assert exists(blk, base) or blk == "Cimmeria", f"{blk} event at {base} outside its life"

    assert affiliation("Laurentia", 300) == ["Laurussia", "Laurasia", "Pangaea"]
    assert affiliation("India", 300) == ["Gondwana", "Pangaea"]
    assert affiliation("India", 100) == []
    assert not exists("Avalonia", 700)
    assert exists("Avalonia", 450)
    assert "Lhasa" in [b for b in BLOCKS]
    print(f"paleogeography selftest OK: {len(BLOCKS)} blocks, {len(ASSEMBLIES)} assemblies, "
          f"{len(OROGENIES)} orogenies, {len(_TERRANE_EVENTS)} terrane events")


if __name__ == "__main__":
    _selftest()
    print()
    for blk in ("Avalonia", "Cimmeria", "Laurentia"):
        print(f"--- {blk} ---")
        for line in history(blk):
            print("   ", line)
        print()
