"""Browsable geological intervals and supercontinents.

Two things the app could not do before: say in words what interval you are
looking at, and let you navigate BY that structure instead of scrubbing a
slider and hoping. Both new sidebars read from here.

Boundary ages follow ICS v2024/12. Several differ from figures still in wide
circulation -- base Ordovician is 486.85 Ma (not 485.4), base Cretaceous 143.1
(not 145.0), base Silurian 443.1, base Guadalupian 274.4, base Devonian 419.62.

Window convention matches the rest of the project: a0 <= age <= a1 with future
ages negative, so Near Future is a0=-30, a1=0 and a plain range test works
everywhere without special-casing the sign.

The bulk content lives in eras_data.json rather than inline, because it is
several tens of kilobytes of prose and burying the module's logic under it
would make this file unreadable.
"""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eras_data.json")
with open(_PATH) as _f:
    _DATA = json.load(_f)

INTERVALS = _DATA["intervals"]
SUPERCONTINENTS = _DATA["supercontinents"]
GLACIATIONS = _DATA.get("glaciations", [])
CLIMATE_EVENTS = _DATA.get("climate_events", [])
INTERCHANGES = _DATA.get("interchanges", [])
SOURCES = _DATA.get("sources", [])


def intervals():
    return INTERVALS


def supercontinents():
    return SUPERCONTINENTS


def glaciations():
    """Named icehouses and snowballs, youngest first when displayed.

    Separate from intervals and supercontinents because a glaciation is
    neither: it cuts across the timescale's divisions and it is a state of the
    whole system rather than a piece of geography. Each carries what caused it,
    what ended it, what it did to life, and what about it is still argued over
    -- the last one matters, because several of these are not settled.
    """
    return GLACIATIONS


def interchanges():
    """Biotic interchanges -- what happened when two separated faunas met.

    The SIXTH navigable structure, and like the climate events it exists because
    the map cannot show it. A land bridge is a few tens of kilometres of ground:
    the Isthmus of Panama and the Bering Strait are both far below what a 20 km
    grid can resolve, so the app can draw the continents approaching and never
    draw the moment they connect -- which is the only moment that matters.

    They are also the clearest demonstration in the record that geography IS
    biology. Two of these are the same event: the Isthmus rose and closed a
    seaway at almost exactly the moment the Bering Strait flooded and opened one,
    and the consequences run in opposite directions on land and in the sea.
    """
    return INTERCHANGES


def climate_events():
    """Named climate events -- hyperthermals, ocean anoxic events, carbon drawdowns.

    The FIFTH navigable structure, and it exists for a reason the other four do
    not have: every one of these is SHORTER THAN A KEYFRAME. The PETM lasts
    200,000 years and the keyframes are 5 Myr apart, so no amount of field
    resolution will ever draw it -- the app can only carry it as a card. The
    card audit found eleven such gaps (PETM, Azolla, OAE 1a/1b/2/3, EECO, MECO,
    MMCO, the GOE and the Hirnantian anoxia) and they are covered by the seven
    entries here, the smaller ones as companions on the card of their relative.

    The Great Oxidation Event carries `offmap`: at 2.46-2.06 Ga it is a billion
    years older than this map's oldest frame, so it is listed and described and
    never drawn or jumped to. Saying "this happened and it is off the edge of
    this map" is more honest than omitting the largest change in the history of
    Earth's surface.
    """
    return CLIMATE_EVENTS


def interval_at(age):
    """The named interval containing `age`, or None.

    The present is a boundary case: Near Future runs (-30, 0] and the
    Quaternary runs [0, 2.58), so age 0 satisfies both. Split on the sign
    first -- at or after the present you want the real geological interval,
    not the projection that happens to end there.
    """
    projected = age < 0
    for i in INTERVALS:
        if (i["rank"] == "projected") != projected:
            continue
        if min(i["a0"], i["a1"]) <= age <= max(i["a0"], i["a1"]):
            return i
    return None


if __name__ == "__main__":
    for a in [0, -1, 25, 100, 300, 650, -200]:
        i = interval_at(a)
        print(f"{a:>6} Ma -> {i['name'] if i else 'NONE'}")
