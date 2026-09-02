"""Stamp a fresh DATA_V into the app so a deploy cannot serve stale JSON.

GitHub Pages sends the data files with max-age=600 and an ETag, which sounds
short enough not to matter. In practice it is not: a returning viewer can sit on
a cached copy well past that window (bfcache, a tab that never revalidates, the
browser's own heuristic freshness), and the failure is silent — the app runs
perfectly and shows yesterday's data. This project has hit it three times now,
on labels.json, plates_time.json and life.json, and each time it looked like the
change had not been deployed at all.

So the JSON fetches carry ?v=DATA_V and this rewrites DATA_V at build time. The
field textures deliberately do NOT get a version: there are ~750 of them, they
almost never change, and busting them would re-download ~24 MB after a one-line
data edit.

Run standalone, or let build_site.py call it.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# DATA_V lives in the application source (web/app.js since the page split,
# WP-10 D5) and in the deployed single-file page.
PAGES = [os.path.join(HERE, "..", "web", "app.js"),
         os.path.join(HERE, "..", "docs", "index.html")]
PAT = re.compile(r"(const DATA_V=')([^']*)(')")


def stamp(version=None):
    version = version or datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y%m%d-%H%M")
    done = []
    for p in PAGES:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            s = f.read()
        if not PAT.search(s):
            print(f"  ! no DATA_V constant in {os.path.relpath(p, HERE)}")
            continue
        s2, n = PAT.subn(lambda m: m.group(1) + version + m.group(3), s, count=1)
        if n:
            with open(p, "w") as f:
                f.write(s2)
            done.append(os.path.relpath(p, HERE))
    print(f"DATA_V = {version}  ({', '.join(done) if done else 'nothing stamped'})")
    return version


if __name__ == "__main__":
    stamp(sys.argv[1] if len(sys.argv) > 1 else None)
