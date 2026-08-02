"""Catch two labels drawn for one feature at one moment.

THE DEFECT THIS EXISTS FOR. `features.py` grew by accretion: a feature added
early as one kind (Lake Pannon as a "sea", when lakes were not yet modelled)
and added again later as the kind it really is (a "lake") leaves BOTH entries
in the shipped file. Both then render -- and worse, they render in different
places, because each type has its own snapping rule: a sea-typed label is
pulled to the nearest open water, so the stale Lake Pannon walked out of the
Carpathian Basin and into the western Mediterranean, 1,500 km from the lake it
names (user report, 2026-08-01).

WHAT COUNTS AS A DUPLICATE. Same name AND overlapping age windows. A feature
carried at two positions for two DIFFERENT windows is not a duplicate -- that
is how a drifting craton is supposed to be described (North China at 120-420
and again at 420-900), and flagging it would train the reader to ignore this
check.

Exit code 1 if any are found, so the build refuses to publish them.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")


def overlaps(a0, a1, b0, b1):
    lo1, hi1 = min(a0, a1), max(a0, a1)
    lo2, hi2 = min(b0, b1), max(b0, b1)
    return lo1 < hi2 and lo2 < hi1


def main():
    rows = json.load(open(os.path.join(WEB, "labels.json")))
    by = defaultdict(list)
    for r in rows:
        by[r["n"]].append(r)
    bad = []
    for n, lst in by.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, b = lst[i], lst[j]
                if overlaps(a["a0"], a["a1"], b["a0"], b["a1"]):
                    bad.append((n, a, b))
    for n, a, b in bad:
        print("  %-34s %s %s-%s  vs  %s %s-%s"
              % (n[:33], a["t"], a["a0"], a["a1"], b["t"], b["a0"], b["a1"]))
    print("label duplicates (same name, overlapping windows): %d of %d labels"
          % (len(bad), len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
