"""Deep-time-aware biome classification.

A Whittaker diagram tells you that 20 C and 2000 mm is "tropical rainforest". It
does not tell you what a tropical rainforest was MADE OF in the Carboniferous, and
that is the part Tectonic Earth keeps getting wrong: the app's terms are chosen
per period by hand (no grassland before the Cenozoic, microbial crust before land
plants), which is right in spirit but is a table, not a model.

This module separates the two questions:

    climate_zone(mat, precip)          -> the Whittaker cell: physics, timeless
    biome(mat, precip, age_ma)         -> the zone PLUS what grew there at that age

so that a new age or a new climate field automatically produces defensible
vegetation instead of needing another hand-written row.

    >>> biome(25, 2500, 0).name
    'tropical rainforest'
    >>> biome(25, 2500, 310).name
    'lycopsid coal swamp'
    >>> biome(25, 2500, 600).name
    'microbial crust'

Dependency-free (stdlib only).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["Biome", "climate_zone", "biome", "VEGETATION_ERAS", "ZONES"]


@dataclass(frozen=True)
class Biome:
    zone: str                # the timeless Whittaker cell
    name: str                # what it was called at this age
    dominants: tuple         # characteristic organisms
    height_m: float          # typical canopy height, 0 for non-forest
    note: str = ""
    colour_hint: str = ""    # a sRGB hex the renderer may use as a starting point


# ---------------------------------------------------------------------------
# 1. The timeless part: a Whittaker classification.
#    mat  = mean annual temperature, C
#    prec = mean annual precipitation, mm
# ---------------------------------------------------------------------------

ZONES = (
    "ice sheet", "polar desert", "tundra", "boreal forest",
    "temperate rainforest", "temperate forest", "temperate grassland",
    "cold desert", "mediterranean shrubland", "subtropical desert",
    "savanna", "seasonal tropical forest", "tropical rainforest",
    "wetland",
)


def climate_zone(mat: float, prec: float, permanent_ice: bool = False,
                 waterlogged: bool = False) -> str:
    """Whittaker cell from mean annual temperature and annual precipitation."""
    if permanent_ice:
        return "ice sheet"
    if waterlogged and mat > 0:
        return "wetland"
    if mat < -8:
        return "ice sheet" if prec > 150 else "polar desert"
    if mat < 0:
        return "tundra"
    if mat < 5:
        return "tundra" if prec < 300 else "boreal forest"
    if mat < 10:
        if prec < 200:
            return "cold desert"
        if prec < 450:
            return "temperate grassland"
        return "boreal forest"
    if mat < 20:
        if prec < 250:
            return "cold desert"
        if prec < 500:
            return "temperate grassland"
        if prec < 800:
            return "mediterranean shrubland"
        if prec < 2000:
            return "temperate forest"
        return "temperate rainforest"
    # mat >= 20
    if prec < 250:
        return "subtropical desert"
    if prec < 900:
        return "savanna"
    if prec < 2000:
        return "seasonal tropical forest"
    return "tropical rainforest"


# ---------------------------------------------------------------------------
# 2. The historical part: what occupied each zone, and when.
#    Each era gives, per zone, (display name, dominants, canopy height).
#    Eras are (base, top) in Ma and are searched oldest-first.
# ---------------------------------------------------------------------------

_MICROBIAL = {
    z: ("microbial crust", ("cyanobacterial mat", "possible fungi", "algal film"), 0.0)
    for z in ZONES
}
_MICROBIAL["ice sheet"] = ("bare ice", (), 0.0)
_MICROBIAL["polar desert"] = ("bare regolith", (), 0.0)
_MICROBIAL["subtropical desert"] = ("bare regolith", (), 0.0)
_MICROBIAL["cold desert"] = ("bare regolith", (), 0.0)
_MICROBIAL["wetland"] = ("microbial mat flat", ("cyanobacterial mat", "stromatolites"), 0.0)

VEGETATION_ERAS = [
    # -------------------------------------------------- pre-vegetation
    dict(base=4600, top=470, label="pre-vegetation",
         note="Land is stone. Bare regolith, braided rivers with no banks (no roots to "
              "hold a channel), and at most a microbial and possibly fungal crust on damp "
              "surfaces. Earliest embryophyte spores are Middle Ordovician ~470 Ma.",
         zones=_MICROBIAL),

    # -------------------------------------------------- early vascular
    dict(base=470, top=385, label="early vascular",
         note="Rhyniophyte- and zosterophyll-grade plants, centimetres to a metre, "
              "confined to damp lowlands. Baragwanathia and Cooksonia. No canopy, no "
              "closed cover, so no true forest zone exists yet.",
         zones={
             "ice sheet": ("bare ice", (), 0),
             "polar desert": ("bare regolith", (), 0),
             "tundra": ("bryophyte-grade ground cover", ("liverworts", "mosses"), 0.05),
             "boreal forest": ("low vascular thicket", ("Cooksonia", "Zosterophyllum"), 0.5),
             "temperate rainforest": ("streamside vascular turf", ("Baragwanathia",), 0.6),
             "temperate forest": ("streamside vascular turf", ("Cooksonia", "Aglaophyton"), 0.4),
             "temperate grassland": ("sparse cryptogamic ground", ("liverworts",), 0.05),
             "cold desert": ("bare regolith", (), 0),
             "mediterranean shrubland": ("sparse vascular patches", ("Zosterophyllum",), 0.3),
             "subtropical desert": ("bare regolith", (), 0),
             "savanna": ("sparse vascular patches", ("Cooksonia",), 0.3),
             "seasonal tropical forest": ("low vascular thicket", ("Psilophyton",), 0.8),
             "tropical rainforest": ("low vascular thicket", ("Psilophyton", "Baragwanathia"), 1.0),
             "wetland": ("rhyniophyte marsh", ("Aglaophyton", "Rhynia", "Horneophyton"), 0.3),
         }),

    # -------------------------------------------------- first forests
    dict(base=385, top=323.4, label="Devonian-Mississippian forest",
         note="Archaeopteris to 30 m with real wood and roots to ~1 m; Wattieza ~8 m "
              "slightly earlier; Prototaxites, a probable fungus to 8 m, with no modern "
              "analogue. First seeds (Elkinsia) in the Late Devonian. Deep rooting begins "
              "the silicate-weathering drawdown that ends in the Late Palaeozoic Ice Age.",
         zones={
             "ice sheet": ("bare ice", (), 0),
             "polar desert": ("bare regolith", (), 0),
             "tundra": ("cryptogamic ground", ("bryophytes",), 0.1),
             "boreal forest": ("Archaeopteris woodland", ("Archaeopteris",), 15),
             "temperate rainforest": ("Archaeopteris forest", ("Archaeopteris", "Rhacophyton"), 30),
             "temperate forest": ("Archaeopteris forest", ("Archaeopteris", "Prototaxites"), 25),
             "temperate grassland": ("open herbaceous ground", ("early ferns",), 0.5),
             "cold desert": ("bare regolith", (), 0),
             "mediterranean shrubland": ("progymnosperm scrub", ("Archaeopteris",), 6),
             "subtropical desert": ("bare regolith", (), 0),
             "savanna": ("open progymnosperm woodland", ("Archaeopteris",), 10),
             "seasonal tropical forest": ("progymnosperm forest", ("Archaeopteris", "Wattieza"), 25),
             "tropical rainforest": ("progymnosperm forest", ("Archaeopteris", "Wattieza",
                                                             "Prototaxites"), 30),
             "wetland": ("Rhacophyton marsh", ("Rhacophyton", "Archaeopteris"), 8),
         }),

    # -------------------------------------------------- coal forests
    dict(base=323.4, top=303.7, label="Pennsylvanian coal forest",
         note="Lepidodendron >50 m tall and 2 m across at the base, with DETERMINATE "
              "growth: it grew as a pole, reproduced once, and died. Calamites >10 m. "
              "These are the coal. Atmospheric O2 approaches its ~30% Phanerozoic peak.",
         zones={
             "ice sheet": ("bare ice", (), 0),
             "polar desert": ("bare regolith", (), 0),
             "tundra": ("cold cryptogamic ground", ("bryophytes",), 0.1),
             "boreal forest": ("cordaitalean woodland", ("Cordaites",), 20),
             "temperate rainforest": ("cordaitalean forest", ("Cordaites", "tree ferns"), 30),
             "temperate forest": ("cordaitalean forest", ("Cordaites", "Medullosa"), 25),
             "temperate grassland": ("fern prairie", ("ferns", "sphenopsids"), 1.0),
             "cold desert": ("bare regolith", (), 0),
             "mediterranean shrubland": ("seed-fern scrub", ("Medullosa", "Callipteris"), 5),
             "subtropical desert": ("bare regolith", (), 0),
             "savanna": ("open tree-fern woodland", ("Psaronius",), 8),
             "seasonal tropical forest": ("tree-fern forest", ("Psaronius", "Medullosa"), 15),
             "tropical rainforest": ("lycopsid coal swamp",
                                     ("Lepidodendron", "Sigillaria", "Calamites",
                                      "Psaronius", "Medullosa"), 50),
             "wetland": ("lycopsid coal swamp",
                         ("Lepidodendron", "Sigillaria", "Calamites"), 45),
         }),

    # -------------------------------------------------- post-collapse Permian
    dict(base=303.7, top=251.9, label="Permian",
         note="After the ~305 Ma Euramerican rainforest collapse. Lycopsids crash and "
              "tree ferns and seed ferns take the tropics. FOUR floral provinces now "
              "matter more than the climate zone: Glossopteris in Gondwana, Cordaites in "
              "Angara, gigantopterids in everwet Cathaysia (which does NOT collapse), "
              "conifers and peltasperms in a drying Euramerica. Use "
              "paleobiogeography.province() alongside this.",
         zones={
             "ice sheet": ("Gondwanan ice sheet", (), 0),
             "polar desert": ("periglacial barrens", (), 0),
             "tundra": ("Glossopteris tundra-woodland", ("Glossopteris",), 5),
             "boreal forest": ("cordaitalean taiga", ("Cordaites", "Rufloria"), 25),
             "temperate rainforest": ("Glossopteris swamp forest",
                                      ("Glossopteris", "Vertebraria"), 30),
             "temperate forest": ("Glossopteris / cordaitalean forest",
                                  ("Glossopteris", "Gangamopteris", "Cordaites"), 25),
             "temperate grassland": ("sphenopsid-fern steppe", ("Neocalamites", "ferns"), 1.0),
             "cold desert": ("cold sand sea", (), 0),
             "mediterranean shrubland": ("peltasperm scrub", ("Callipteris", "Lepidopteris"), 4),
             "subtropical desert": ("Pangaean sand sea", (), 0),
             "savanna": ("open conifer woodland", ("Walchia", "Voltzia"), 12),
             "seasonal tropical forest": ("tree-fern and conifer forest",
                                          ("Psaronius", "Walchia"), 20),
             "tropical rainforest": ("gigantopterid everwet forest",
                                     ("Gigantopteris", "Lobatannularia", "Psaronius"), 30),
             "wetland": ("Glossopteris peat swamp", ("Glossopteris", "Vertebraria"), 25),
         }),

    # -------------------------------------------------- Mesozoic gymnosperm
    dict(base=251.9, top=130, label="Mesozoic gymnosperm",
         note="Strikingly cosmopolitan: conifers, cycads, Bennettitales, ginkgoes and "
              "ferns from Greenland to Antarctica. Dicroidium replaces Glossopteris in "
              "Triassic Gondwana. High-latitude forest with a polar light regime is a "
              "real biome with no modern analogue.",
         zones={
             "ice sheet": ("bare ice", (), 0),
             "polar desert": ("polar barrens", (), 0),
             "tundra": ("polar deciduous conifer woodland", ("Podozamites", "Ginkgo"), 12),
             "boreal forest": ("araucarian-podocarp forest", ("Araucaria", "Podocarpus"), 35),
             "temperate rainforest": ("temperate conifer rainforest",
                                      ("Araucaria", "Ginkgo", "ferns"), 45),
             "temperate forest": ("conifer-cycadophyte forest",
                                  ("Araucaria", "Williamsonia", "Ptilophyllum"), 30),
             "temperate grassland": ("fern prairie", ("Coniopteris", "Equisetites"), 1.0),
             "cold desert": ("cold sand sea", (), 0),
             "mediterranean shrubland": ("cheirolepid scrub", ("Frenelopsis", "Brachyphyllum"), 5),
             "subtropical desert": ("erg", (), 0),
             "savanna": ("open bennettitalean woodland", ("Williamsonia", "Cycadeoidea"), 8),
             "seasonal tropical forest": ("cheirolepid conifer forest",
                                          ("Brachyphyllum", "Pagiophyllum"), 25),
             "tropical rainforest": ("cycadophyte-conifer rainforest",
                                     ("Araucaria", "Cycadeoidea", "Dipteridaceae"), 40),
             "wetland": ("horsetail-fern marsh", ("Equisetites", "Weichselia"), 2),
         }),

    # -------------------------------------------------- angiosperm rise
    dict(base=130, top=40, label="angiosperm radiation",
         note="Flowering plants originate and diversify from ~130 Ma; by the Late "
              "Cretaceous >50% of modern orders exist and flowering trees overtake "
              "conifers. NO GRASSLAND: grasses exist but are ecologically marginal. "
              "Paratropical broadleaf forest reaches both poles in the Eocene.",
         zones={
             "ice sheet": ("bare ice", (), 0),
             "polar desert": ("polar barrens", (), 0),
             "tundra": ("polar broadleaf-deciduous forest",
                        ("Metasequoia", "Trochodendroides"), 20),
             "boreal forest": ("mixed conifer-broadleaf forest", ("Metasequoia", "Platanus"), 35),
             "temperate rainforest": ("temperate broadleaf rainforest",
                                      ("Nothofagus", "Lauraceae"), 45),
             "temperate forest": ("broadleaf-conifer forest", ("Platanaceae", "Fagaceae"), 30),
             "temperate grassland": ("herbaceous open ground", ("early Poaceae", "ferns"), 0.6),
             "cold desert": ("cold desert", (), 0),
             "mediterranean shrubland": ("sclerophyll shrubland", ("Myrtaceae", "Proteaceae"), 4),
             "subtropical desert": ("erg", (), 0),
             "savanna": ("open broadleaf woodland", ("Palmae", "Fabaceae"), 12),
             "seasonal tropical forest": ("seasonal broadleaf forest",
                                          ("Lauraceae", "Palmae"), 30),
             "tropical rainforest": ("paratropical rainforest",
                                     ("Lauraceae", "Palmae", "Annonaceae"), 45),
             "wetland": ("Nymphaeales swamp", ("Nymphaeales", "Taxodium"), 25),
         }),

    # -------------------------------------------------- modern
    dict(base=40, top=-1e9, label="modern",
         note="Grasses become ecologically important from ~40 Ma; C4 grasslands expand "
              "in the late Miocene (~8 Ma) under low CO2 and seasonal aridity. Tundra is "
              "one of the largest biomes on Earth and only exists once there is polar ice.",
         zones={
             "ice sheet": ("ice sheet", (), 0),
             "polar desert": ("polar desert", ("lichens", "cyanobacteria"), 0),
             "tundra": ("tundra", ("Cyperaceae", "Salix", "mosses", "lichens"), 0.3),
             "boreal forest": ("boreal forest (taiga)", ("Picea", "Pinus", "Larix"), 25),
             "temperate rainforest": ("temperate rainforest",
                                      ("Sequoia", "Nothofagus", "Tsuga"), 60),
             "temperate forest": ("temperate deciduous forest",
                                  ("Quercus", "Fagus", "Acer"), 30),
             "temperate grassland": ("temperate grassland / steppe",
                                     ("Stipa", "Poa", "Festuca"), 0.6),
             "cold desert": ("cold desert", ("Artemisia", "Ephedra"), 0.5),
             "mediterranean shrubland": ("mediterranean shrubland",
                                         ("Quercus ilex", "Cistus", "Olea"), 4),
             "subtropical desert": ("subtropical desert", ("Cactaceae", "Acacia"), 1),
             "savanna": ("tropical savanna", ("Andropogoneae C4 grasses", "Acacia"), 8),
             "seasonal tropical forest": ("seasonal tropical forest",
                                          ("Dipterocarpaceae", "Tectona"), 30),
             "tropical rainforest": ("tropical rainforest",
                                     ("Dipterocarpaceae", "Fabaceae", "Arecaceae"), 50),
             "wetland": ("wetland", ("Cyperaceae", "Rhizophora", "Sphagnum"), 10),
         }),
]

_COLOURS = {
    "ice sheet": "#eef3f7", "polar desert": "#c9c9c2", "tundra": "#8f9c7c",
    "boreal forest": "#2f5d43", "temperate rainforest": "#1f6b4a",
    "temperate forest": "#3f7f4a", "temperate grassland": "#a9b56a",
    "cold desert": "#b8a882", "mediterranean shrubland": "#8f9a54",
    "subtropical desert": "#d6b98a", "savanna": "#bfae5e",
    "seasonal tropical forest": "#4f8a3f", "tropical rainforest": "#1f6b2c",
    "wetland": "#5d7f5a",
}


def _era_for(age_ma: float) -> dict:
    for era in VEGETATION_ERAS:
        if era["top"] <= age_ma <= era["base"]:
            return era
    return VEGETATION_ERAS[-1]


def biome(mat: float, prec: float, age_ma: float = 0.0,
          permanent_ice: bool = False, waterlogged: bool = False) -> Biome:
    """The biome at a place and a time.

    mat  - mean annual temperature, C
    prec - mean annual precipitation, mm
    age_ma - Ma, positive into the past, negative into the future"""
    zone = climate_zone(mat, prec, permanent_ice, waterlogged)
    era = _era_for(age_ma)
    name, dominants, height = era["zones"][zone]
    return Biome(zone=zone, name=name, dominants=tuple(dominants), height_m=float(height),
                 note=era["note"], colour_hint=_COLOURS[zone])


# ---------------------------------------------------------------------------

def _selftest() -> None:
    # every era covers every zone
    for era in VEGETATION_ERAS:
        missing = set(ZONES) - set(era["zones"])
        assert not missing, f"{era['label']} is missing zones: {sorted(missing)}"
    # eras tile time with no gaps
    for a, b in zip(VEGETATION_ERAS, VEGETATION_ERAS[1:]):
        assert abs(a["top"] - b["base"]) < 1e-9, f"gap between {a['label']} and {b['label']}"
    # the headline cases
    assert biome(25, 2500, 0).name == "tropical rainforest"
    assert biome(25, 2500, 310).name == "lycopsid coal swamp"
    assert biome(25, 2500, 600).name == "microbial crust"
    assert biome(25, 2500, 100).name == "paratropical rainforest"
    # no grassland before the Cenozoic
    for age in (300, 200, 100, 60):
        b = biome(12, 400, age)
        assert "grassland" not in b.name, f"{age} Ma produced {b.name}"
    assert biome(12, 400, 10).name.startswith("temperate grassland")
    # no forest before there are trees
    assert biome(18, 1500, 420).height_m < 2.0
    assert biome(18, 1500, 370).height_m > 20.0
    # deserts stay deserts
    assert "desert" in biome(28, 100, 250).name or biome(28, 100, 250).name == "erg"
    print(f"biome_model selftest OK: {len(ZONES)} zones x {len(VEGETATION_ERAS)} "
          f"vegetation eras")


if __name__ == "__main__":
    _selftest()
    print()
    cases = [("everwet tropics", 26, 3000), ("seasonal tropics", 26, 1200),
             ("temperate wet", 12, 1200), ("temperate dry", 12, 400),
             ("high latitude", -2, 500)]
    ages = [600, 420, 370, 310, 270, 200, 90, 10]
    w = max(len(c[0]) for c in cases)
    print(" " * (w + 2) + "".join(f"{a:>34}" for a in ages))
    for label, mat, prec in cases:
        row = "".join(f"{biome(mat, prec, a).name:>34}" for a in ages)
        print(f"{label:<{w}}  {row}")
