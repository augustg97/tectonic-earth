"""Assemble a self-hosting static site in ../site.

The published-artifact route has a 16 MB ceiling, and base64-inlining every
texture inflates them ~33% and forces the browser to parse the whole payload
before anything renders. Served as ordinary files instead, the same build is
smaller on the wire, cached per file by the browser, fetched in parallel, and
has no size ceiling at all — which is what makes room for future detail.

Output is plain static files: drop the folder on GitHub Pages, Netlify,
Cloudflare Pages, or any web server. No build step, no dependencies.
"""
import os, shutil, json

WEB = "../web"
SITE = "../docs"   # GitHub Pages serves main:/docs natively

os.makedirs(SITE, exist_ok=True)
dst = os.path.join(SITE, "fields")
if os.path.isdir(dst):
    shutil.rmtree(dst)
# The "_lite" elevation copies exist only to squeeze the inlined artifact under
# its 16 MB ceiling; the site serves the full-quality textures.
shutil.copytree(os.path.join(WEB, "fields"), dst,
                ignore=shutil.ignore_patterns("*_lite.webp"))

DATA_FILES = ("index.html", "three.min.js", "timeline.json", "boundaries.json",
              "plates_time.json", "plates.json", "hotspots.json", "labels.json",
              "eras.json", "life.json",
              # screenshots for the in-app About one-pager overlay
              "about-globe.jpg", "about-map.jpg", "about-pangaea.jpg", "about-hydro.jpg")
for name in DATA_FILES:
    src = os.path.join(WEB, name)
    # The app degrades gracefully if a data file is missing — the sidebars just
    # stay empty — which means a copy silently dropped from this list would not
    # show up as an error anywhere. Fail the build instead.
    if not os.path.exists(src):
        raise SystemExit(f"build_site: {name} is missing from {WEB}. "
                         f"Run build_webdata.py first.")
    shutil.copy2(src, os.path.join(SITE, name))

# GitHub Pages otherwise runs the tree through Jekyll, which ignores files and
# folders beginning with an underscore and slows the build for no benefit.
open(os.path.join(SITE, ".nojekyll"), "w").close()

open(os.path.join(SITE, "README.md"), "w").write(
    "# Tectonic Earth\n\n"
    "Interactive deep-time reconstruction of Earth's surface, 1000 Ma to +250 Myr.\n\n"
    "A WebGL terrain engine interpolates per-keyframe elevation and rainfall\n"
    "fields, so coastlines migrate continuously rather than cross-fading, and\n"
    "relief is shaded per pixel. Climate (winds, moisture advection, orographic\n"
    "rain shadows, monsoons) is derived rather than painted on.\n\n"
    "## Running locally\n\n"
    "It is a static site — any web server will do:\n\n"
    "```sh\npython3 -m http.server 8000\n```\n\n"
    "then open <http://localhost:8000>.\n\n"
    "## Data sources\n\n"
    "- Paleogeography & elevation — Scotese & Wright (2018), *PALEOMAP PaleoDEMs*, CC-BY 4.0\n"
    "- Present plate motions — NNR-MORVEL56 (Argus, Gordon & DeMets, 2011)\n"
    "- Plate boundaries — Bird (2003), *PB2002*\n\n"
    "Pre-540 Ma and future frames are authored reconstructions and are\n"
    "illustrative rather than exact.\n")

total = 0
for root, _, files in os.walk(SITE):
    for f in files:
        total += os.path.getsize(os.path.join(root, f))
n = sum(len(fs) for _, _, fs in os.walk(SITE))
print(f"site/: {n} files, {total/1e6:.2f} MB (vs a 16 MB inlined-artifact ceiling)")
