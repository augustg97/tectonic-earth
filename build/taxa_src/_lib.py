"""Compact authoring helper for registry batches (see build/taxa/SCHEMA.md).

Each batch is a Python file of E(...) calls -- terse to write and to review --
which writes build/taxa/<name>.json. A name the registry already has is SKIPPED
and reported, never overwritten: one organism, one entry.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
OUT = {}
def T(old, young, *codes):
    return {"t": [old, young], "in": list(codes)}
def E(name, rank, realm, form, fad, lad, rng, note, hab=None, lat=None, w=None, cls=None,
      rep=None, realms=None, aka=None, box=None, fill=None, pic=None):
    e = {"rank": rank, "realm": realm, "form": form, "fad": fad, "lad": lad,
         "range": rng if isinstance(rng, list) else [rng], "note": note}
    if hab: e["hab"] = hab if isinstance(hab, list) else [hab]
    if lat: e["lat"] = lat
    if w: e["w"] = w
    if cls: e["cls"] = {k: v for k, v in zip(("class", "order", "family"), cls) if v}
    if rep: e["rep"] = rep
    if realms: e["realms"] = realms
    if aka: e["aka"] = aka
    if box: e["box"] = box if isinstance(box[0], (list, tuple)) else [box]
    if fill is False: e["fill"] = False
    if pic: e["pic"] = pic
    OUT[name] = e
def write(fname):
    import glob
    have = {}
    for f in glob.glob(os.path.join(HERE, "..", "taxa", "*.json")):
        if os.path.basename(f) == fname:
            continue
        d = json.load(open(f))
        for n, e in d["taxa"].items():
            have[n] = f
            for a in e.get("aka", ()):
                have[a] = f
    skip = [n for n in OUT if n in have]
    keep = {n: e for n, e in OUT.items() if n not in have}
    json.dump({"taxa": dict(sorted(keep.items()))},
              open(os.path.join(HERE, "..", "taxa", fname), "w"), indent=1, ensure_ascii=False)
    print(f"{fname}: {len(keep)} written; {len(skip)} already registered: {', '.join(skip[:30])}")
