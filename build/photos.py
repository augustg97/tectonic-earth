"""Fetch real photographs for feature cards from Wikimedia Commons.

The schematics say what KIND of thing a feature is. A photograph says what it
looks like, and for anything with a modern counterpart that is the fastest way
to understand it -- the Appalachians card can show the Appalachians. These are
in ADDITION to the diagrams, not instead of them.

LICENSING, and why this is stricter than it needs to be. Commons is mostly
CC BY-SA, and share-alike is refused here for the same reason it is refused for
the PhyloPic silhouettes: this project would rather not reason about how far an
adaptation clause reaches. So only PUBLIC DOMAIN, CC0 and plain CC-BY are
accepted, which means most searches have to look past their own best results.
That is a real cost -- some features get no photo -- and it is the right trade.
United States government work is public domain, so NPS, USGS, NASA and USFWS
carry a lot of this set.

Every image ships with its title, author, licence and a link back to the file
page, and the app shows all four under the picture. Attribution is not optional
for CC-BY, and it is good manners for public domain.

    ../venv/bin/python photos.py            # fetch everything missing
    ../venv/bin/python photos.py --list     # what is wanted vs what is here
    ../venv/bin/python photos.py --force    # refetch even if present
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "web", "photos")
INDEX = os.path.join(HERE, "..", "web", "photos.json")
API = "https://commons.wikimedia.org/w/api.php"
UA = "TectonicEarth/1.0 (educational paleogeography viewer; contact via repo)"

#: Licences this project will ship. Everything else is skipped, loudly.
OK_LICENCE = re.compile(
    r"^(cc0|cc-zero|pd|public domain|pdm|cc-by-\d|cc by \d|attribution$)", re.I)
BAD_LICENCE = re.compile(r"(sa|nc|nd)\b", re.I)

#: feature name -> (search terms, what the picture is showing and why)
#: Kept to features with a real modern counterpart. A photograph of a place
#: that no longer exists would be a lie, however pretty.
WANT = {
    # --- mountain belts -----------------------------------------------------
    "Appalachians": ("Appalachian Mountains ridge forest",
                     "The modern Appalachians. What is left of a range that "
                     "once rivalled the Himalaya, worn down for 250 million "
                     "years since the collision that raised it."),
    "Himalaya": ("Himalaya Everest range NASA",
                 "The Himalaya today, still rising as India drives into Asia."),
    "Alps": ("Alps peaks snow landscape",
             "The Alps, raised by Africa closing against Europe and consuming "
             "the Tethys between them."),
    "Andes": ("Andes mountains Chile NASA",
              "The Andes: a subduction belt, built by the Nazca plate sinking "
              "beneath South America rather than by two continents colliding."),
    "Rocky Mountains": ("Rocky Mountains Colorado NPS",
                        "The Rockies, raised far inland from any plate margin "
                        "by a shallow-angle slab under North America."),
    "Ural Mountains": ("Ural mountains range landscape",
                       "The Urals: the suture where Siberia met Baltica to "
                       "complete Pangaea, still marking the join."),
    "Atlas": ("Atlas Mountains Morocco",
              "The Atlas, on the leading edge of Africa's collision with Europe."),
    "Zagros Mts": ("Zagros Mountains Iran NASA",
                   "The Zagros, where Arabia is currently colliding with Iran -- "
                   "a collision belt caught in the act."),
    "Transantarctic Mts": ("Transantarctic mountains glacier landscape",
                           "The Transantarctic Mountains, dividing the East "
                           "Antarctic shield from the West Antarctic rift."),
    "Caledonides": ("Scottish Highlands mountains",
                    "The Scottish Highlands: the eroded stump of the "
                    "Caledonian belt, whose other half is in Norway and "
                    "Appalachia."),
    # --- rifts --------------------------------------------------------------
    "East African Rift": ("East African Rift valley NASA",
                          "The East African Rift, a continent in the act of "
                          "splitting -- the same process that opened the "
                          "Atlantic, caught early."),
    "Red Sea Rift": ("Red Sea NASA satellite",
                     "The Red Sea: a rift that has gone all the way, now "
                     "flooded and making new ocean floor."),
    "Basin and Range": ("Nevada basin range valley landscape",
                        "Basin and Range: crust stretched until it broke into "
                        "parallel blocks, each tilted, with the valleys "
                        "between them filling with their own debris."),
    "Baikal Rift": ("Baikal rift valley satellite image",
                    "The Baikal Rift, holding the deepest and oldest lake on "
                    "Earth in its trough."),
    # --- deserts and drylands ----------------------------------------------
    "Sahara": ("Sahara desert dunes NASA",
               "The Sahara. A continental interior far from any ocean, under "
               "descending dry air -- the same recipe that made the Pangaean "
               "heart a desert."),
    "Patagonian Desert": ("Patagonia steppe landscape arid",
                          "The Patagonian Desert, dry because the Andes take "
                          "the rain before it can arrive."),
    "Great Plains": ("tallgrass prairie North America",
                     "The Great Plains: grassland that spread only in the "
                     "Cenozoic, as the world cooled and dried."),
    "African Savanna": ("African savanna acacia grassland",
                        "Savanna -- grass with scattered trees, the biome that "
                        "grazing mammals and, later, hominins evolved into."),
    "Eurasian Steppe": ("Eurasian steppe grassland Mongolia",
                        "The Eurasian steppe, an unbroken grass corridor from "
                        "Hungary to Manchuria."),
    # --- ice ----------------------------------------------------------------
    "East Antarctic Ice Sheet": ("Antarctica ice sheet NASA",
                                 "The East Antarctic ice sheet, the largest "
                                 "body of ice on Earth and the oldest, "
                                 "established at the Eocene-Oligocene boundary."),
    "Greenland Ice Sheet": ("Greenland ice sheet NASA",
                            "The Greenland ice sheet, which presses the crust "
                            "beneath it hundreds of metres down."),
    "Patagonian Ice Sheet": ("Patagonian ice field glacier",
                             "What remains of the Patagonian ice: the "
                             "Southern Patagonian Ice Field, the largest "
                             "outside the poles."),
    "Arctic Tundra": ("tundra Alaska landscape summer",
                      "Arctic tundra, with the polygonal ground that "
                      "freeze-thaw cycles sort into shape."),
    # --- lakes --------------------------------------------------------------
    "Lake Baikal": ("Baikal lake shore landscape",
                    "Lake Baikal: a rift lake holding a fifth of the world's "
                    "unfrozen fresh water."),
    "Laurentian Great Lakes": ("Great Lakes Michigan Huron satellite image",
                               "The Great Lakes, sitting in basins the "
                               "Laurentide ice sheet scoured out, and only "
                               "14,000 years old."),
    "Lake Tanganyika": ("Tanganyika lake shore water",
                        "Lake Tanganyika, in the western branch of the East "
                        "African Rift."),
    # --- impact and volcanism ----------------------------------------------
    "Manicouagan": ("Manicouagan reservoir crater satellite",
                    "Manicouagan, 215 million years old and still the most "
                    "recognisable crater on Earth -- cratonic rock keeps a "
                    "scar that a marine impact loses in a couple of million "
                    "years."),
    "Chicxulub": ("cenote Yucatan sinkhole",
                  "Chicxulub has no surface expression -- it was buried within "
                  "about two million years. The ring of cenotes over its rim "
                  "is the only thing you can see from the ground."),
    "Deccan Traps": ("Deccan plateau India landscape",
                     "The Deccan Traps: flood basalt in stacked sheets, "
                     "erupted across western India at the end of the "
                     "Cretaceous."),
    "Columbia River Basalts": ("Columbia river gorge basalt cliffs",
                              "Columbia River flood basalts, the youngest "
                              "large igneous province on land."),
    "Siberian Traps": ("Putorana plateau landscape",
                       "The Putorana Plateau, the surviving heart of the "
                       "Siberian Traps -- the eruption that sits at the "
                       "end-Permian extinction."),
    # --- other --------------------------------------------------------------
    "Amazon Rainforest": ("Amazon rainforest canopy trees",
                          "The Amazon: closed equatorial rainforest, the "
                          "wettest and darkest end of the biome range."),
    "Tibetan Plateau": ("Tibetan Plateau landscape NASA",
                        "The Tibetan Plateau, held up by doubled crust and "
                        "high enough to sit above the tree line at 33 degrees "
                        "north."),
    "Mid-Atlantic Ridge": ("Thingvellir rift Iceland",
                           "Thingvellir in Iceland, where the Mid-Atlantic "
                           "Ridge runs above sea level and the spreading "
                           "boundary can be walked across."),
    "Gulf of California": ("Gulf of California NASA satellite",
                           "The Gulf of California: a rift that has opened far "
                           "enough to let the sea in, tearing Baja from the "
                           "mainland."),
    "Zealandia": ("Southern Alps New Zealand",
                  "New Zealand -- the six per cent of Zealandia that is above "
                  "water."),
    "Iceland": ("Iceland landscape volcanic NASA",
                "Iceland, where a mantle plume sits under a spreading ridge "
                "and builds enough crust to stand above the sea."),
}


def _get(url, tries=5):
    """Commons rate-limits hard, and a 429 looks exactly like "no such image"
    if you do not handle it -- the first run of this reported thirty features
    as having no acceptable licence when the server had simply stopped
    answering. Back off and retry."""
    delay = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or attempt == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2.0
    raise RuntimeError("unreachable")


def _clean(s):
    """Commons metadata is HTML. Strip it to plain text for the caption line."""
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def search(term, limit=30):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": term + " filetype:bitmap", "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": "640",
    })
    d = json.loads(_get(API + "?" + q))
    pages = (d.get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        g = lambda k: _clean((em.get(k) or {}).get("value", ""))
        lic = g("LicenseShortName") or g("License")
        out.append({
            "title": p.get("title", ""),
            "licence": lic,
            "artist": g("Artist") or "(unattributed)",
            "credit": g("Credit"),
            "desc": g("ImageDescription"),
            "page": ii.get("descriptionurl", ""),
            "thumb": ii.get("thumburl", ""),
            "w": ii.get("width", 0), "h": ii.get("height", 0),
            "index": p.get("index", 99),
        })
    out.sort(key=lambda c: c["index"])
    return out


#: Words that mean the file is a specimen shot, a map or a historic document
#: rather than a picture of the place. Searching Commons by relevance and
#: filtering by licence turned up a painting of a sailing boat for Lake Baikal,
#: a 1930s seaplane for Tanganyika and a hand specimen on white card for the
#: Siberian Traps -- all correctly licensed, none of them the subject.
REJECT_TITLE = re.compile(
    r"(specimen|sample|hand ?sample|thin ?section|museum|logo|coat of arms|"
    r"stamp|banknote|postcard|painting|drawing|engraving|portrait|"
    r"seaplane|aircraft|boat|ship|locomotive|railway|church|monument|"
    r"diagram|chart|graph|\bflag\b)", re.I)


def relevant(c, keywords):
    """The file title must mention what we asked for."""
    t = c["title"].lower()
    if REJECT_TITLE.search(t):
        return False
    return any(k in t for k in keywords)


def acceptable(c):
    lic = (c["licence"] or "").strip()
    if not lic or not c["thumb"]:
        return False
    if BAD_LICENCE.search(lic.replace("CC BY", "").replace("cc-by", "")):
        return False
    if not OK_LICENCE.match(lic):
        return False
    # a card figure is landscape; a tall portrait crops badly
    return c["w"] >= c["h"] * 0.92


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch(name, term, caption, force=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, slug(name) + ".jpg")
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else {}
    if not force and name in idx and os.path.exists(path):
        return idx[name], "have"
    try:
        cands = search(term)
    except Exception as e:
        return None, f"search failed: {e}"
    # distinctive words from the feature name and the query, 4+ letters
    keys = [w for w in re.findall(r"[a-z]{4,}", (name + " " + term).lower())
            if w not in {"mountains", "mountain", "aerial", "satellite", "nasa",
                         "landscape", "public", "domain", "photo", "range"}]
    ok = [c for c in cands if acceptable(c) and relevant(c, keys)]
    if not ok:                      # relax the title gate before giving up
        ok = [c for c in cands if acceptable(c)]
    if not ok:
        lics = ", ".join(sorted({c['licence'] for c in cands if c['licence']})[:4])
        return None, f"no acceptable licence among {len(cands)} (saw: {lics})"
    c = ok[0]
    try:
        blob = _get(c["thumb"])
    except Exception as e:
        return None, f"download failed: {e}"
    with open(path, "wb") as f:
        f.write(blob)
    rec = {"file": "photos/" + slug(name) + ".jpg",
           "title": c["title"].replace("File:", ""),
           "artist": c["artist"][:120], "licence": c["licence"],
           "page": c["page"], "caption": caption,
           "bytes": len(blob)}
    return rec, "fetched"


def main():
    force = "--force" in sys.argv
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else {}
    if "--list" in sys.argv:
        for n in WANT:
            print(f"  {'HAVE' if n in idx else '    '}  {n}")
        print(f"\n{len(idx)} of {len(WANT)} wanted features have a photo")
        return
    got = skipped = 0
    for name, (term, caption) in WANT.items():
        rec, how = fetch(name, term, caption, force=force)
        if rec:
            idx[name] = rec
            if how == "fetched":
                got += 1
                print(f"  + {name:28s} {rec['licence']:16s} {rec['bytes']//1024:4d} kB "
                      f" {rec['artist'][:34]}")
            time.sleep(2.2)
        else:
            skipped += 1
            print(f"  - {name:28s} {how}")
    json.dump(idx, open(INDEX, "w"), indent=1, sort_keys=True)
    print(f"\n{got} fetched, {len(idx)} total, {skipped} without an acceptable image")


if __name__ == "__main__":
    main()
