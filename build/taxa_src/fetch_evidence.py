"""Attach the PBDB's evidence to every registry entry that lacks it.

`biota.review()` cross-checks form, range and place against `pbdb` on each
entry, and an entry written by hand has none until this runs -- so a batch
that passes --check has only been checked against itself. Cached in data/pbdb;
a second run is free. Robust dates (the 4th-96th percentiles of occurrence
midpoints) are stored beside the raw extremes as `fea_r`/`lla_r`.

    python3 fetch_evidence.py            # every file
    python3 fetch_evidence.py x-marine-depth.json
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import pbdb                                                     # noqa: E402

REG = os.path.join(HERE, "..", "taxa")


def robust_dates(oid, term):
    mids = sorted((e + l) / 2.0 for _x, _y, e, l in pbdb.occurrences(oid, term))
    if len(mids) < 8:
        return None, None
    k = len(mids)
    return round(mids[int(0.96 * (k - 1))], 2), round(mids[int(0.04 * (k - 1))], 2)


def main(argv):
    files = [os.path.join(REG, a) for a in argv] or sorted(glob.glob(os.path.join(REG, "*.json")))
    for fn in files:
        with open(fn) as f:
            d = json.load(f)
        got = skipped = 0
        for name, e in d["taxa"].items():
            if "pbdb" in e or e.get("assemblage") or not re.match(r"^[A-Z][a-z]+", name):
                continue
            try:
                ev = pbdb.evidence(name)
            except Exception as ex:                                # noqa: BLE001
                print(f"  {name}: {ex}")
                continue
            if not ev:
                skipped += 1
                continue
            regs = ev.pop("regions", None)
            if regs:
                ev["regions"] = {k: v[0] for k, v in regs.items()}
                fr, lr = robust_dates(ev["oid"], ev["matched"])
                if fr is not None:
                    ev["fea_r"], ev["lla_r"] = fr, lr
            for k in ("env", "motility", "habit", "diet", "homonyms"):
                ev.pop(k, None)
            e["pbdb"] = ev
            got += 1
        if got:
            with open(fn, "w") as f:
                json.dump(d, f, indent=1, ensure_ascii=False)
        print(f"{os.path.basename(fn)}: {got} evidence records added, {skipped} names the PBDB does not know")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
