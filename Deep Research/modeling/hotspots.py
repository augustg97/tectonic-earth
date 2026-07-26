"""D1 / D3 / D4 — a hotspot catalogue with coordinates, chains and LIP roots.

Closes three linked gaps in one table:

  D1  `features.HOTSPOTS` carries LIP age windows and long-lived plumes but no
      plume COORDINATES through time and no chain geometry, so plume positions in
      the app are hashed rather than catalogued.
  D2  `seamounts.field()` already takes a `hotspot` input and it is not wired up.
      Seamounts are seeded by crustal age, so they scatter where a real ocean
      shows chains.
  D3  Aseismic ridges - Ninetyeast, Walvis, Rio Grande, Chagos-Laccadive, Cocos,
      Carnegie, Emperor - are "absent or generic" (README §10). Every one of them
      is a plume trail, so ONE catalogue closes D1, D2 and D3 together.
  D4  Guyots then fall out for free: a seamount that grew above sea level and
      subsided with the cooling plate is flat-topped, which is a drawable
      prediction rather than a texture.

HOW TO USE IT FOR SEAMOUNTS. A chain is not a smear along plate motion. Take the
hotspot's present position, hold it fixed in the mantle, and reconstruct the
PLATE over it: the locus of points that passed over the plume is the chain, and
each point's age is when it was there. Edifice height then decays with the age of
the crust beneath it (`edifice_height` below), so the young end is islands, the
middle is shallow banks and atolls, and the old end is drowned guyots.

  IMPORTANT CAVEAT to put on any plume card (D7): hotspots are NOT fixed.
  Inter-hotspot motion is demonstrable before ~90 Ma, and the Hawaii-Emperor bend
  is now widely read as PLUME motion rather than a change in Pacific plate
  direction. A track drawn before ~90 Ma is a model output, not a measurement.

Coordinates are present-day positions of the inferred melting anomaly, in degrees
(lon, lat). Confidence: 'strong' = age-progressive chain plus a deep seismic
anomaly; 'moderate' = clear age progression; 'weak' = a melting anomaly whose
deep-plume origin is contested. Only Yellowstone is consistently imaged from the
deep mantle to the surface, which is the calibration for how confident any plume
card should sound.

Dependency-free (stdlib only).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

__all__ = ["Hotspot", "HOTSPOTS", "by_name", "active_at", "with_lip",
           "edifice_height", "chain_points", "ASEISMIC_RIDGES"]


@dataclass(frozen=True)
class Hotspot:
    name: str
    lon: float
    lat: float
    plate: str                 # the plate riding over it today
    chain: str = ""            # the trail it has built
    lip: str = ""              # the large igneous province it began with, if any
    lip_age: Optional[float] = None
    started: Optional[float] = None   # Ma, oldest dated edifice on the trail
    buoyancy: float = 0.0      # Mg/s, plume flux where published; 0 = unknown
    confidence: str = "moderate"
    note: str = ""


# ---------------------------------------------------------------------------
# The catalogue. Ordered roughly by how much they matter to what the app draws.
# ---------------------------------------------------------------------------

HOTSPOTS = [
    # ---- Pacific -----------------------------------------------------------
    Hotspot("Hawaii", -155.3, 18.9, "Pacific",
            "Hawaiian Ridge -> Emperor Seamounts", "", None, 85.0, 8.7, "strong",
            "The type example. The BEND at ~47 Ma is now widely read as plume motion, "
            "not a change in Pacific plate direction. Meiji Seamount at the far end is "
            "~85 Ma and about to subduct into the Kuril trench."),
    Hotspot("Louisville", -141.2, -53.6, "Pacific",
            "Louisville Seamount Chain", "", None, 80.0, 0.9, "strong",
            "The southern counterpart of Hawaii; its old end meets the Tonga-Kermadec "
            "trench at the Osbourn Trough."),
    Hotspot("Easter / Salas y Gomez", -109.3, -26.4, "Nazca",
            "Easter Seamount Chain / Nazca Ridge", "", None, 30.0, 3.0, "moderate"),
    Hotspot("Galapagos", -91.6, -0.4, "Nazca",
            "Cocos Ridge + Carnegie Ridge", "Caribbean LIP", 92.0, 95.0, 1.0, "strong",
            "One plume, TWO aseismic ridges, because it sits under a spreading centre "
            "and feeds both flanks. Its LIP is now the thick crust under the Caribbean."),
    Hotspot("Marquesas", -138.0, -10.5, "Pacific", "Marquesas Islands", "", None, 6.0,
            0.0, "moderate"),
    Hotspot("Society / Tahiti", -148.4, -18.2, "Pacific", "Society Islands", "", None,
            5.0, 0.0, "moderate"),
    Hotspot("Macdonald", -140.3, -29.0, "Pacific", "Cook-Austral chain", "", None, 30.0,
            0.0, "moderate",
            "The Cook-Austral trail is not one chain: several overlapping age "
            "progressions, which is a standard argument against strict plume fixity."),
    Hotspot("Pitcairn", -129.3, -25.4, "Pacific", "Pitcairn-Gambier chain", "", None,
            11.0, 0.0, "moderate"),
    Hotspot("Samoa", -168.1, -14.5, "Pacific", "Samoan chain", "", None, 24.0, 0.0,
            "moderate"),
    Hotspot("Caroline", 164.4, 4.8, "Pacific", "Caroline Islands", "", None, 30.0, 0.0,
            "weak"),
    Hotspot("Cobb", -130.1, 46.0, "Juan de Fuca", "Cobb-Eickelberg Seamounts", "", None,
            43.0, 0.0, "moderate"),
    Hotspot("Bowie", -135.0, 53.0, "Pacific", "Kodiak-Bowie Seamounts", "", None, 24.0,
            0.0, "moderate"),
    Hotspot("Guadalupe", -114.5, 27.7, "Pacific", "Mathematician Ridge", "", None, 20.0,
            0.0, "weak"),
    Hotspot("Socorro", -111.0, 18.8, "Pacific", "Revillagigedo Islands", "", None, 5.0,
            0.0, "weak"),
    Hotspot("Juan Fernandez", -81.8, -33.9, "Nazca", "Juan Fernandez Ridge", "", None,
            30.0, 0.0, "moderate"),
    Hotspot("Tasmantid", 155.5, -40.4, "Australia", "Tasmantid Seamounts", "", None,
            24.0, 0.0, "moderate"),
    Hotspot("Lord Howe", 159.8, -34.7, "Australia", "Lord Howe Seamount Chain", "", None,
            30.0, 0.0, "moderate"),
    Hotspot("Balleny", 164.8, -67.6, "Antarctic", "Balleny Islands", "", None, 10.0, 0.0,
            "weak"),

    # ---- Indian ------------------------------------------------------------
    Hotspot("Reunion", 55.7, -21.1, "Somalia",
            "Deccan -> Laccadive-Chagos -> Maldives -> Mascarene -> Reunion",
            "Deccan Traps", 66.0, 68.5, 1.9, "strong",
            "The cleanest LIP-to-island-chain trail on Earth: flood basalt at 66 Ma, "
            "then 5,000 km of ridge and atoll, then an active volcano."),
    Hotspot("Kerguelen", 69.2, -49.6, "Antarctic",
            "Kerguelen Plateau + Ninetyeast Ridge + Broken Ridge",
            "Kerguelen Plateau", 118.0, 118.0, 0.5, "strong",
            "Built a plateau AND the longest straight aseismic ridge on Earth - "
            "Ninetyeast, ~5,000 km, from ~100 Ma - as India raced north over it."),
    Hotspot("Marion", 37.8, -46.9, "Antarctic", "Madagascar Ridge", "Madagascar", 88.0,
            92.0, 0.0, "moderate"),
    Hotspot("Crozet", 50.2, -46.1, "Antarctic", "Del Cano Rise", "", None, 40.0, 0.5,
            "moderate"),
    Hotspot("Amsterdam-St Paul", 77.5, -38.7, "Antarctic", "", "", None, 10.0, 0.0,
            "weak"),
    Hotspot("Comoros", 43.3, -11.5, "Somalia", "Comoro Islands", "", None, 10.0, 0.0,
            "weak"),
    Hotspot("Afar", 42.5, 11.5, "Africa", "Ethiopian-Yemen traps",
            "Ethiopian Traps", 30.0, 31.0, 1.2, "strong",
            "A plume under a CONTINENT, splitting it three ways: the Red Sea, the Gulf "
            "of Aden and the East African Rift meet over it."),
    Hotspot("Hainan", 110.0, 20.0, "Eurasia", "", "", None, 10.0, 0.0, "weak"),

    # ---- Atlantic ----------------------------------------------------------
    Hotspot("Iceland", -17.3, 64.4, "Eurasia / North America",
            "Greenland-Iceland-Faroe Ridge", "North Atlantic Igneous Province", 62.0,
            62.0, 1.4, "strong",
            "Sits ON the ridge, so it builds a trail on BOTH plates and thickens the "
            "crust to ~20 km. Its LIP is implicated in the PETM."),
    Hotspot("Tristan da Cunha", -12.3, -37.1, "African",
            "Walvis Ridge (Africa) + Rio Grande Rise (S America)",
            "Parana-Etendeka", 133.0, 135.0, 1.7, "strong",
            "Rooted in the flood basalt that opened the South Atlantic, and then wrote "
            "the opening into TWO mirror-image aseismic ridges on the two plates."),
    Hotspot("Gough", -9.9, -40.3, "African", "Walvis Ridge southern track", "", None,
            70.0, 0.0, "moderate",
            "Tristan and Gough split the Walvis trail into two sub-tracks after ~70 Ma."),
    Hotspot("St Helena", -9.5, -16.5, "African", "St Helena Seamount Chain", "", None,
            80.0, 0.5, "moderate"),
    Hotspot("Ascension", -14.3, -7.9, "African", "", "", None, 6.0, 0.0, "weak"),
    Hotspot("Trindade", -28.8, -20.5, "South American", "Vitoria-Trindade Ridge", "",
            None, 85.0, 0.0, "moderate"),
    Hotspot("Fernando de Noronha", -32.4, -3.8, "South American", "", "", None, 12.0,
            0.0, "weak"),
    Hotspot("Cape Verde", -24.0, 16.0, "African", "Cape Verde Rise", "", None, 20.0, 1.6,
            "moderate",
            "A near-stationary plate over a plume: a swell with almost no age "
            "progression, which is why it is a bathymetric RISE rather than a chain."),
    Hotspot("Canary", -18.0, 28.2, "African", "Canary Islands", "", None, 68.0, 1.0,
            "moderate"),
    Hotspot("Madeira", -17.0, 32.6, "African", "Madeira-Tore Rise", "", None, 70.0, 0.0,
            "weak"),
    Hotspot("Azores", -26.0, 37.9, "Eurasia", "Azores Plateau", "", None, 36.0, 1.1,
            "moderate"),
    Hotspot("Bermuda", -64.3, 32.6, "North American", "Bermuda Rise", "", None, 45.0,
            0.0, "weak"),
    Hotspot("Great Meteor / New England", -29.2, 29.4, "African",
            "New England Seamounts -> Great Meteor", "", None, 120.0, 0.9, "moderate",
            "Its trail crosses the whole North Atlantic and continues onto the North "
            "American plate as the Monteregian Hills - a plume track that runs from "
            "continent to abyssal plain."),
    Hotspot("Jan Mayen", -8.3, 71.0, "Eurasia", "", "", None, 40.0, 0.0, "weak"),
    Hotspot("Vema", 6.3, -32.1, "African", "", "", None, 30.0, 0.0, "weak"),
    Hotspot("Discovery", 0.4, -42.0, "African", "Discovery Seamounts", "", None, 40.0,
            0.0, "weak"),
    Hotspot("Shona", -1.0, -51.4, "African", "", "", None, 40.0, 0.0, "weak"),
    Hotspot("Bouvet", 3.4, -54.4, "Antarctic", "", "", None, 40.0, 0.0, "weak"),

    # ---- Continental -------------------------------------------------------
    Hotspot("Yellowstone", -110.7, 44.4, "North American",
            "Snake River Plain", "Columbia River Basalt", 16.5, 17.0, 0.3, "strong",
            "The ONLY hotspot consistently imaged from the deep mantle to the surface. "
            "Its trail is a caldera track burned across a continent, and its LIP is the "
            "Columbia River flood basalt."),
    Hotspot("Anahim", -123.7, 52.9, "North American", "Anahim Volcanic Belt", "", None,
            13.0, 0.0, "moderate"),
    Hotspot("Raton", -104.1, 36.8, "North American", "Jemez Lineament", "", None, 10.0,
            0.0, "weak"),
    Hotspot("Eifel", 6.7, 50.2, "Eurasia", "", "", None, 40.0, 0.0, "weak"),
    Hotspot("Hoggar", 5.6, 23.3, "African", "", "", None, 35.0, 0.0, "weak"),
    Hotspot("Tibesti", 17.5, 20.8, "African", "", "", None, 25.0, 0.0, "weak"),
    Hotspot("Darfur", 24.2, 13.0, "African", "", "", None, 30.0, 0.0, "weak"),
    Hotspot("Cameroon", 9.2, 4.2, "African", "Cameroon Volcanic Line", "", None, 65.0,
            0.0, "moderate",
            "A line that runs from oceanic islands straight onto the continent, which no "
            "simple fixed-plume model explains."),
    Hotspot("East Africa / Kenya", 37.4, -3.0, "African", "", "", None, 25.0, 0.0,
            "moderate"),
]

# Aseismic ridges named as absent or generic in README §10, and the plume that
# built each. This is the D3 mapping.
ASEISMIC_RIDGES = {
    "Ninetyeast Ridge": ("Kerguelen", 100.0, 38.0,
                         "~5,000 km, the longest straight ridge on Earth; India raced "
                         "north over the plume"),
    "Walvis Ridge": ("Tristan da Cunha", 133.0, 0.0, "African-plate half of the pair"),
    "Rio Grande Rise": ("Tristan da Cunha", 133.0, 60.0,
                        "South American-plate half; the mirror of Walvis"),
    "Chagos-Laccadive Ridge": ("Reunion", 66.0, 10.0, "Deccan to Maldives"),
    "Mascarene Plateau": ("Reunion", 45.0, 10.0, ""),
    "Cocos Ridge": ("Galapagos", 20.0, 0.0, "Cocos-plate half"),
    "Carnegie Ridge": ("Galapagos", 20.0, 0.0, "Nazca-plate half"),
    "Emperor Seamounts": ("Hawaii", 85.0, 47.0, "the pre-bend limb"),
    "Hawaiian Ridge": ("Hawaii", 47.0, 0.0, "the post-bend limb"),
    "Louisville Ridge": ("Louisville", 80.0, 0.0, ""),
    "Nazca Ridge": ("Easter / Salas y Gomez", 30.0, 0.0, ""),
    "Greenland-Iceland-Faroe Ridge": ("Iceland", 62.0, 0.0, "built on both plates"),
    "New England Seamounts": ("Great Meteor / New England", 120.0, 80.0, ""),
    "Vitoria-Trindade Ridge": ("Trindade", 85.0, 0.0, ""),
    "Broken Ridge": ("Kerguelen", 118.0, 43.0, "rifted from the Kerguelen Plateau"),
}

_BY_NAME = {h.name: h for h in HOTSPOTS}


def by_name(name):
    return _BY_NAME.get(name)


def active_at(age):
    """Hotspots whose trail had begun by `age` Ma."""
    return [h for h in HOTSPOTS if h.started is not None and h.started >= age]


def with_lip():
    return [h for h in HOTSPOTS if h.lip]


def edifice_height(crust_age_at_edifice, initial_km=4.0):
    """Height of a seamount above the surrounding sea floor, in km.

    The edifice is built at the ridge-crest height of the plume and then rides
    down as the plate cools and contracts, following the same half-space law the
    sea floor itself uses. `crust_age_at_edifice` is how long ago the seamount
    formed, in Myr.

    This is what makes the D4 guyot prediction fall out for free: subtract the
    subsidence from the initial height and an old edifice's summit ends up
    hundreds of metres below sea level, wave-planed flat.
    """
    a = max(0.0, float(crust_age_at_edifice))
    subsidence_km = 0.350 * math.sqrt(a)
    return max(0.0, initial_km - subsidence_km)


def summit_depth(crust_age_at_edifice, ridge_depth_km=2.6, initial_km=4.0):
    """Depth of a seamount summit below sea level, km. NEGATIVE means an island.

    The edifice is built at the ridge, where the floor is `ridge_depth_km` deep,
    and stands `initial_km` above it - so its summit starts at
    `ridge_depth_km - initial_km` (negative, i.e. above water, for a tall one).
    Then the WHOLE THING - floor and edifice together - subsides as the plate
    cools, by the same 350*sqrt(Myr) metres the sea floor uses:

        summit_depth = (ridge_depth - initial) + 0.350 * sqrt(age)

    With the defaults a new edifice stands 1.4 km above the sea and drowns at
    about 16 Myr, which is the right order for the Hawaiian chain (Midway, at
    ~28 Ma, is an atoll). That crossover is the whole of the D4 prediction.
    """
    a = max(0.0, float(crust_age_at_edifice))
    return (ridge_depth_km - initial_km) + 0.350 * math.sqrt(a)


def chain_points(hotspot, ages, plate_motion):
    """The trail a plume writes, given a function that moves the plate.

    `plate_motion(lon, lat, age) -> (lon, lat)` must carry a PRESENT-DAY point
    back to where it was at `age`. The plume is held fixed, so the point of the
    plate that sat over it at `age` is found by asking which present-day point
    reconstructs onto the plume. In practice the app already has this: run
    paleo_tracks in reverse, or reconstruct a dense grid and pick the nearest.

    Returned as [(lon, lat, age, summit_depth_km), ...] at PRESENT-DAY positions,
    which is what the seamount seeder needs.
    """
    h = _BY_NAME[hotspot] if isinstance(hotspot, str) else hotspot
    out = []
    for a in ages:
        if h.started is not None and a > h.started:
            continue
        p = plate_motion(h.lon, h.lat, a)
        if p is None:
            continue
        out.append((p[0], p[1], a, summit_depth(a)))
    return out


def _selftest():
    seen = set()
    for h in HOTSPOTS:
        assert -180 <= h.lon <= 180, f"{h.name} lon {h.lon}"
        assert -90 <= h.lat <= 90, f"{h.name} lat {h.lat}"
        assert h.name not in seen, f"duplicate {h.name}"
        seen.add(h.name)
        assert h.confidence in ("strong", "moderate", "weak"), h.name
        if h.lip:
            assert h.lip_age is not None, f"{h.name} names a LIP with no age"
            assert h.started >= h.lip_age - 1, \
                f"{h.name}: trail starts {h.started} but its LIP is {h.lip_age}"
    for ridge, (hs, old, young, _n) in ASEISMIC_RIDGES.items():
        assert hs in _BY_NAME, f"{ridge} names unknown hotspot {hs}"
        assert old >= young, ridge
    # the guyot prediction: young edifices are islands, old ones are drowned
    assert summit_depth(0) < 0, "a new seamount should be an island"
    assert summit_depth(80) > 0, "an 80 Myr edifice should be drowned"
    n_strong = sum(1 for h in HOTSPOTS if h.confidence == "strong")
    print(f"hotspots selftest OK: {len(HOTSPOTS)} hotspots ({n_strong} strong), "
          f"{len(ASEISMIC_RIDGES)} aseismic ridges mapped to plumes, "
          f"{len(with_lip())} rooted in a LIP")


if __name__ == "__main__":
    _selftest()
    print("\nsummit depth vs edifice age (the D4 guyot prediction):")
    for a in (0, 5, 10, 20, 40, 60, 80, 100, 140):
        d = summit_depth(a)
        kind = "island" if d < 0 else ("atoll/bank" if d < 0.5 else "guyot")
        print(f"  {a:>4.0f} Myr  summit {d:+6.2f} km   {kind}")
    print("\nplume-rooted LIPs:")
    for h in with_lip():
        print(f"  {h.name:<28} {h.lip} at {h.lip_age:g} Ma -> {h.chain}")
