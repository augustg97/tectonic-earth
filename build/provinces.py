"""Which biogeographic province each label sits in, at every age it is drawn.

THE PROBLEM THIS CLOSES. 336 labels show a biota panel and 101 of them have a
curated list, so **235 fell straight through to ONE GLOBAL LIST for the whole
interval**. A Verkhoyansk Belt card at 250 Ma showed "the world's Late Permian
biota" -- true of the world, and not an answer to what lived there. The heading
said so honestly, which made it a stated gap rather than an error, but it was
still the same list on two hundred different cards.

THE DECISION (2026-07-26). The MODEL decides; a curated list is a flagged
EXCEPTION. `Deep Research/modeling/paleobiogeography.py` returns a named province
for every cell in 0-1000 Ma -- 49 distinct ones, from the Sturtian snowball ocean
through the five named Ordovician shelf provinces to the Cathaysian coal flora --
so the panel can say WHICH province a place was in instead of listing the world.
Where the model still cannot place a point, the global list stays, under a
heading that says it is global.

WHAT THIS MODULE DOES. Walks every label across its own age window, takes its
palaeolatitude from the track the build already computes, asks the province model,
and emits RUNS -- [age_lo, age_hi, province_id] -- because a province changes on
the scale of a period while the timeline steps every 5 Myr, so 336 labels x 251
ages compresses to a few hundred runs. The app then looks up a province in
constant time with no biogeography ported into JavaScript.

The catalogue is imported, not copied: `paleobiogeography` is stdlib-only for
exactly this reason, and a second copy would drift from the one the audits check.
"""
import os
import sys

_MODELING = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "Deep Research", "modeling")

_PB = _PG = None

# The province model is banded and block-aware, and `block` is what turns
# "tropical" into "Cathaysian Province". Only labels that ARE a named block can
# supply one; everything else gets the latitude band, which is what the model is
# built to fall back on.
MARINE_TYPES = {"ocean", "sea"}


def _load():
    global _PB, _PG
    if _PB is None:
        try:
            if _MODELING not in sys.path:
                sys.path.insert(0, _MODELING)
            import paleobiogeography                       # noqa: PLC0415
            import paleogeography                          # noqa: PLC0415
            _PB, _PG = paleobiogeography, paleogeography
        except Exception:                                  # noqa: BLE001
            _PB, _PG = False, False
    return (_PB or None), (_PG or None)


def _lat_at(lab, age):
    """Palaeolatitude of a label at `age`, from its own track."""
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


def build(labels, step=5):
    """({province_id: record}, {label_name: [[a_lo, a_hi, id], ...]}).

    Runs are inclusive at both ends and cover only the label's own window, so a
    name is never given a province at an age it is not drawn.
    """
    pb, pg = _load()
    if pb is None:
        return {}, {}
    blocks = set(getattr(pg, "BLOCKS", ()) or ())

    ids, recs = {}, {}
    out = {}
    for lab in labels:
        name = lab.get("n")
        a0, a1 = lab.get("a0", 0), lab.get("a1", 0)
        lo, hi = min(a0, a1), max(a0, a1)
        if hi <= 0 or lo > 1000:
            continue                       # future-only, or off the model's range
        lo = max(lo, 0)
        hi = min(hi, 1000)
        realm = "marine" if lab.get("t") in MARINE_TYPES else "terrestrial"
        block = name if name in blocks else None
        runs = []
        a = lo
        while a <= hi + 1e-9:
            lat = _lat_at(lab, a)
            if lat is None:
                a += step
                continue
            try:
                p = pb.province(float(a), float(lat), realm, block)
            except Exception:                              # noqa: BLE001
                a += step
                continue
            # A province with confidence 'none' is a climate band wearing a
            # province's clothes; say nothing rather than dress it up.
            if p is None or p.confidence == "none":
                a += step
                continue
            key = (p.name, p.realm)
            pid = ids.get(key)
            if pid is None:
                pid = ids[key] = len(ids)
                recs[pid] = {"n": p.name, "r": p.realm, "b": p.basis,
                             "c": p.confidence, "note": p.note,
                             "mk": list(p.markers)[:8]}
            if runs and runs[-1][2] == pid and abs(runs[-1][1] - (a - step)) < 1e-6:
                runs[-1][1] = a
            else:
                runs.append([a, a, pid])
            a += step
        if runs:
            out[name] = runs
    return recs, out


def _selftest():
    pb, _pg = _load()
    assert pb is not None, "Deep Research/modeling/paleobiogeography.py did not import"
    labs = [{"n": "Siberia", "t": "continent", "a0": 0, "a1": 540, "lon": 100, "lat": 65},
            {"n": "Tethys Ocean", "t": "ocean", "a0": 120, "a1": 260, "lon": 90, "lat": 5},
            {"n": "Verkhoyansk Belt", "t": "orogen", "a0": 0, "a1": 300,
             "lon": 130, "lat": 65}]
    recs, runs = build(labs)
    assert runs, "no runs produced"
    for lab in labs:
        assert lab["n"] in runs, f"{lab['n']} got no province at any age"
        for a_lo, a_hi, pid in runs[lab["n"]]:
            assert a_lo <= a_hi and pid in recs
    n = sum(len(v) for v in runs.values())
    print(f"provinces OK: {len(recs)} distinct provinces, {n} runs over "
          f"{len(runs)} labels")
    for name, rr in runs.items():
        print(f"  {name}: " + "; ".join(
            f"{a1:g}-{a0:g} Ma {recs[p]['n']}" for a0, a1, p in rr[:4]))


if __name__ == "__main__":
    _selftest()
