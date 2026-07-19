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
SOURCES = _DATA.get("sources", [])


def intervals():
    return INTERVALS


def supercontinents():
    return SUPERCONTINENTS


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
