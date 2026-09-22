"""Recompute every entry's PBDB `regions` under the CURRENT region table.

    ../venv/bin/python recode_regions.py            # all files
    ../venv/bin/python recode_regions.py plants.json

`fetch_evidence.py` bins each taxon's collections into crust codes once, when
the evidence is attached. When a code is split (as-e into the four East Asian
blocks, au into east and west, eu into Baltica-Avalonia and the peri-Gondwanan
south) the evidence still says the old code, and `biota.review()` can neither
confirm nor dispute a range written in the new ones. The collection coordinates
are in the PBDB cache, so this rebins them offline; entries whose occurrences
were never fetched (very large clades, or a cache that was cleared) are left as
they are and counted. Network is never touched.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import pbdb                                                  # noqa: E402

REG = os.path.join(BUILD, "taxa")


def cached_occurrences(oid, name):
    """The cached occurrence list, or None if it was never fetched."""
    key = "o-" + pbdb._slug(name) + "-" + pbdb._slug(str(oid))
    fn = os.path.join(pbdb.CACHE, key + ".json")
    if not os.path.exists(fn):
        return None
    return pbdb.occurrences(oid, name)


def main(argv):
    files = [os.path.join(REG, a) for a in argv] or sorted(glob.glob(os.path.join(REG, "*.json")))
    total = changed = missing = 0
    for fn in files:
        with open(fn) as f:
            d = json.load(f)
        touched = False
        for name, e in d["taxa"].items():
            p = e.get("pbdb")
            if not p or not p.get("oid") or "regions" not in p:
                continue
            total += 1
            occs = cached_occurrences(p["oid"], p.get("matched") or name)
            if occs is None:
                missing += 1
                continue
            reg = {}
            for lng, lat, _eag, _lag in occs:
                c = pbdb.region_of(lng, lat) or "sea"
                reg[c] = reg.get(c, 0) + 1
            reg = dict(sorted(reg.items(), key=lambda kv: -kv[1]))
            if reg != p["regions"]:
                p["regions"] = reg
                changed += 1
                touched = True
        if touched:
            with open(fn, "w") as f:
                json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"{total} entries with evidence: {changed} rebinned, {missing} without cached "
          f"occurrences (left as they were)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
