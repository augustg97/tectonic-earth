"""Assemble a self-hosting static site in ../site.

The published-artifact route has a 16 MB ceiling, and base64-inlining every
texture inflates them ~33% and forces the browser to parse the whole payload
before anything renders. Served as ordinary files instead, the same build is
smaller on the wire, cached per file by the browser, fetched in parallel, and
has no size ceiling at all — which is what makes room for future detail.

Output is plain static files: drop the folder on GitHub Pages, Netlify,
Cloudflare Pages, or any web server. No build step, no dependencies.
"""
import os, shutil, json, subprocess, sys

import stamp_data_version

# ASSET BASES (WP-10, D4). `--field-base URL` and `--sheet-base URL` publish a
# site whose per-keyframe fields and world sheets live elsewhere (a GitHub
# release, an object store, a second Pages site -- see publish_assets.py):
# the URLs are stamped into index.html and ambient.html as window.FIELD_BASE
# and window.SHEET_BASE, only the manifests are copied into docs/fields and
# docs/sheets, and the repository stops carrying a gigabyte of textures per
# data revision. Without them the site is self-contained, as before.
def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1].rstrip("/") + "/"
    return ""
FIELD_BASE = _arg("--field-base")
SHEET_BASE = _arg("--sheet-base")

# THE VALIDATORS RUN BEFORE THE DEPLOY, not after it. Every one of them is
# read-only and the whole set takes a few seconds; the alternative is finding out
# from the live site that a card lost its hedge or a label window slipped, which
# is how two of these findings were discovered in the first place. Set
# SKIP_AUDIT=1 to publish anyway -- deliberately awkward, and it says so.
if os.environ.get("SKIP_AUDIT") != "1":
    print("validators:")
    _r = subprocess.run([sys.executable,
                         os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "audit_all.py"), "--quick"])
    if _r.returncode != 0:
        raise SystemExit("build_site: a validator moved backwards (above). Fix it, "
                         "or move the baseline in audit_all.py in the same commit "
                         "and say why. SKIP_AUDIT=1 overrides.")
    # The keyframe-crossing storm gate (perf audit P9). ~90 s because it drives
    # the real app headless -- the stall it protects against is invisible in any
    # static check, and it silently returns the moment a new field kind misses
    # the warm-ahead pipeline. SKIP_PERF=1 skips just this one.
    if os.environ.get("SKIP_PERF") != "1":
        _p = subprocess.run([sys.executable,
                             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "audit_perf.py")])
        if _p.returncode != 0:
            raise SystemExit("build_site: the crossing-storm gate failed (above). "
                             "A keyframe crossing is paying synchronous texture "
                             "uploads again. SKIP_PERF=1 overrides.")

    # THE FIELD AND CHARACTER GATES, which existed for a week as scripts nobody
    # ran. That is exactly how a change that turned Permian Pangaea from 18%
    # green to 64% went out: every metric being watched that round improved, and
    # the one that would have caught it was a file on disk. A validator only
    # protects what it is wired into.
    #
    # audit_biomes reads the shipped rainfall field directly and is fast.
    # audit_deeptime reads SHOTS, so it can only check what has been rendered --
    # it reports honestly and passes when the frames are absent rather than
    # blocking a deploy on a missing screenshot, and the round that changes the
    # climate is the round that owes it fresh ones.
    _here = os.path.dirname(os.path.abspath(__file__))
    # audit_dem_spikes reads every shipped elevation field, so it is the one
    # that catches a source-DEM fill value reaching the screen -- which it did:
    # +10500 m in the Challenger Deep rendered as a tan desert island in the
    # Mariana Trench, and no gate in the suite objected because they all test
    # ranges and distributions and a 10 km spike is inside any range that admits
    # Everest. 22 s over 251 frames.
    for _name, _why in (("audit_biomes.py",
                         "the rainfall field no longer separates the biome classes"),
                        ("audit_deeptime.py",
                         "the deep-time map lost the character it is known for"),
                        ("audit_dem_spikes.py",
                         "a source-DEM fill value is being drawn as terrain"),
                        # audit_island_biomes tests GEOMETRY, not climate, which
                        # is why eighteen continental reference sites all passed
                        # while Cuba, Florida and the Bahamas shipped as desert
                        # on wet ground: the rain lookup's warp is sized for
                        # continents and Cuba is 1.4 degrees tall, so the sample
                        # left the island entirely. Like audit_deeptime it reads
                        # SHOTS and can only check what has been rendered.
                        ("audit_island_biomes.py",
                         "a small landmass draws a climate its field does not "
                         "give it"),
                        # audit_land_grain checks that close-zoom ground still
                        # differs by how rugged it really is, where the shipped
                        # field is too coarse to enforce it. It also self-tests
                        # before reporting, which the metric it replaced could
                        # not have survived: that one answered ~0.09 for the
                        # Alps, for a flat basin, with the detail switched off,
                        # and across a 1.66x change in render scale.
                        ("audit_land_grain.py",
                         "close-zoom ground no longer varies with its relief"),
                        # audit_island_rain guards the SOLVE where
                        # audit_island_biomes guards the shader. The rainfall
                        # solve's final anti-banding averages were unmasked, so
                        # they read the ocean's "no value here" as "zero rain"
                        # and drained every island smaller than the kernel:
                        # Kauai was delivered 1.0000 by the advection and
                        # shipped at 0.0055, the Sahara's number, so the whole
                        # Hawaiian chain drew as desert. audit_island_biomes
                        # passed it, because the render matched the field
                        # faithfully -- the field was what was wrong.
                        ("audit_island_rain.py",
                         "the climate solve is leaking island rainfall into "
                         "the ocean")):
        _q = subprocess.run([sys.executable, os.path.join(_here, _name)])
        if _q.returncode != 0:
            raise SystemExit("build_site: %s failed -- %s (above). SKIP_AUDIT=1 "
                             "overrides." % (_name, _why))

WEB = "../web"
SITE = "../docs"   # GitHub Pages serves main:/docs natively

# Bump the cache-busting stamp BEFORE index.html is copied, or a returning
# viewer keeps whatever JSON their browser already has and the deploy looks like
# it never happened. See stamp_data_version.py.
stamp_data_version.stamp()

os.makedirs(SITE, exist_ok=True)
dst = os.path.join(SITE, "fields")
if os.path.isdir(dst):
    shutil.rmtree(dst)
# The "_lite" elevation copies exist only to squeeze the inlined artifact under
# its 16 MB ceiling; the site serves the full-quality textures.
if FIELD_BASE:
    os.makedirs(dst, exist_ok=True)
    shutil.copy2(os.path.join(WEB, "fields", "manifest.json"), os.path.join(dst, "manifest.json"))
    print(f"fields: manifest only; the files are served from {FIELD_BASE}")
else:
    shutil.copytree(os.path.join(WEB, "fields"), dst,
                    ignore=shutil.ignore_patterns("*_lite.webp"))

DATA_FILES = ("index.html", "ambient.html", "three.min.js", "timeline.json", "boundaries.json",
              "plates_time.json", "plates.json", "hotspots.json", "labels.json",
              "eras.json", "life.json", "art.json", "photos.json", "updatelog.json",
              # per-keyframe plate rotations for the material-coordinate texture (H2)
              "platerot.json",
              # screenshots for the in-app About one-pager overlay
              "about-globe.jpg", "about-map.jpg", "about-pangaea.jpg", "about-hydro.jpg")
# THE ONE-FILE PAGE (WP-10, D5). The source is split -- index.html holds the
# markup, style.css the styles, app.js the application, and web/shaders/*.glsl
# the shaders, which check_shader.py validates and packs into shaders.js -- and
# the deployed page is the three files inlined back into index.html, so the
# site is still a single static page with no load-order or caching subtlety.
_cs = subprocess.run([sys.executable, os.path.join(_here, "check_shader.py")], capture_output=True, text=True)
if _cs.returncode != 0:
    raise SystemExit("build_site: check_shader.py failed:\n" + _cs.stdout[-2000:])
def inline_page(html):
    css = open(os.path.join(WEB, "style.css")).read()
    tag = '<link rel="stylesheet" href="style.css">'
    assert html.count(tag) == 1, "style link"
    html = html.replace(tag, "<style>\n" + css + "</style>")
    for js in ("shaders.js", "app.js"):
        tag = '<script src="%s"></script>' % js
        assert html.count(tag) == 1, js
        body = open(os.path.join(WEB, js)).read()
        assert "</script" not in body, js
        html = html.replace(tag, "<script>\n" + body + "</script>")
    return html

for name in DATA_FILES:
    src = os.path.join(WEB, name)
    # The app degrades gracefully if a data file is missing — the sidebars just
    # stay empty — which means a copy silently dropped from this list would not
    # show up as an error anywhere. Fail the build instead.
    if not os.path.exists(src):
        raise SystemExit(f"build_site: {name} is missing from {WEB}. "
                         f"Run build_webdata.py first.")
    if name == "index.html":
        open(os.path.join(SITE, name), "w").write(inline_page(open(src).read()))
        continue
    shutil.copy2(src, os.path.join(SITE, name))

# GitHub Pages otherwise runs the tree through Jekyll, which ignores files and
# folders beginning with an underscore and slows the build for no benefit.
# Photographs for the feature cards. A directory rather than a file list --
# photos.py adds to it whenever a new feature gets one, and a hard-coded list
# would silently stop shipping the new ones.
# Model-generated figures for the cards. These come out of
# "Deep Research/diagrams and illustrations/make_diagrams.py", which draws them
# FROM the same tables the app ships -- the oxygen curve is climate.py's own O2
# column, the atoll/guyot panel is the subsidence law seamounts.py applies -- so
# they cannot drift away from what the model does. Same directory-not-a-list
# reasoning as the photos below.
fsrc = os.path.join(WEB, "figures")
if os.path.isdir(fsrc):
    fdst = os.path.join(SITE, "figures")
    if os.path.isdir(fdst):
        shutil.rmtree(fdst)
    shutil.copytree(fsrc, fdst)
    print(f"figures: {len(os.listdir(fdst))} model-generated diagrams")

psrc = os.path.join(WEB, "photos")
if os.path.isdir(psrc):
    pdst = os.path.join(SITE, "photos")
    if os.path.isdir(pdst):
        shutil.rmtree(pdst)
    shutil.copytree(psrc, pdst)
    print(f"photos: {len(os.listdir(pdst))} files")

# World sheets (WP-10, plan A3): optional, produced by bake_sheets.py. When
# present the deployed app plays from them instead of running the terrain
# shader per frame, and the ambient build depends on them.
ssrc = os.path.join(WEB, "sheets")
sdst = os.path.join(SITE, "sheets")
if os.path.isdir(sdst):
    shutil.rmtree(sdst)
if os.path.isdir(ssrc) and os.path.exists(os.path.join(ssrc, "manifest.json")):
    if SHEET_BASE:
        os.makedirs(sdst, exist_ok=True)
        shutil.copy2(os.path.join(ssrc, "manifest.json"), os.path.join(sdst, "manifest.json"))
        print(f"sheets: manifest only; the files are served from {SHEET_BASE}")
    else:
        shutil.copytree(ssrc, sdst)
        print(f"sheets: {len(os.listdir(sdst)) - 1} world sheets")

if FIELD_BASE or SHEET_BASE:
    stamp = ("<script>window.FIELD_BASE=%s;window.SHEET_BASE=%s;</script>"
             % (json.dumps(FIELD_BASE), json.dumps(SHEET_BASE)))
    for page in ("index.html", "ambient.html"):
        p = os.path.join(SITE, page)
        html = open(p).read()
        assert html.count("<head>") == 1, page
        open(p, "w").write(html.replace("<head>", "<head>\n" + stamp, 1))
    print("asset bases stamped into index.html and ambient.html")

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
