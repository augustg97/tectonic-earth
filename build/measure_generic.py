"""How much of the marine cards is still a class or an order?

    ../venv/bin/python measure_generic.py [web/life.json ...]

Counts every marine-realm taxon on every card at every whole-Myr age of its
run (a "slot-age") and reports the share whose rank is class, subclass, order,
suborder, phylum, kingdom, domain or clade, by era. Two files side by side is
the comparison a release wants. Earlier releases quoted a different, unrecorded
counting (README 3.7-3.8: "33 / 40 / 43 / 36 / 77"); those numbers are not
comparable with these, which is why this script exists.
"""
import collections
import json
import os
import sys

GENERIC = {"class", "subclass", "order", "suborder", "phylum", "kingdom", "domain", "clade"}
ERAS = [("Cz", 66), ("Mz", 252), ("late Pz", 419), ("early Pz", 541), ("Pc", 1e9)]


def era(age):
    for name, top in ERAS:
        if age <= top:
            return name
    return "Pc"


def measure(path):
    life = json.load(open(path))
    taxa = life["taxa"]
    tot, gen = collections.Counter(), collections.Counter()
    for card in life["cards"].values():
        for run in card["r"]:
            for _key, ids in run[4]:
                for i in ids:
                    t = taxa[i]
                    if t["realm"] != "sea":
                        continue
                    for a in range(run[0], run[1] + 1):
                        tot[era(a)] += 1
                        if t.get("r") in GENERIC:
                            gen[era(a)] += 1
    return {e: (gen[e], tot[e]) for e, _ in ERAS}


def main(paths):
    paths = paths or [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "life.json")]
    for p in paths:
        m = measure(p)
        row = "  ".join(f"{e} {100 * g / max(1, t):.0f}%" for e, (g, t) in m.items())
        print(f"{os.path.basename(p):>14}: {row}   (marine slot-ages at class/order level)")


if __name__ == "__main__":
    main(sys.argv[1:])
