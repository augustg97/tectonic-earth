"""Fetch reference diagrams from Wikimedia Commons under an explicit licence policy.

Policy is the SAME one the main build already applies in build/photos.py and
build/build_silhouettes.py, and it is deliberately strict:

    ACCEPT   public domain, CC0, PDM, CC-BY
    REFUSE   CC-BY-SA  (share-alike would reach the whole project)
    REFUSE   CC-BY-NC  (non-commercial)
    REFUSE   anything with no machine-readable licence

Two traps recorded from the earlier photo round apply here as well and are
handled:
  1. A 429 looks exactly like "no such image". Back off and retry; never read an
     empty result as an absence.
  2. Correct licence does NOT mean correct subject. Everything fetched must be
     eyeballed on a contact sheet before it is used.

    python fetch_reference_figures.py            # fetch into ./collected
    python fetch_reference_figures.py --list     # show the query set only
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "collected")
API = "https://commons.wikimedia.org/w/api.php"
UA = "TectonicEarth-DeepResearch/1.0 (research figure collection; contact via repo)"

OK_LICENCES = ("public domain", "cc0", "pdm", "cc by 4.0", "cc by 3.0", "cc by 2.5",
               "cc by 2.0", "cc-by-4.0", "cc-by-3.0", "attribution")
BAD_TOKENS = ("share alike", "sharealike", "-sa", "noncommercial", "non-commercial", "-nc",
              "fair use", "non-free")

# (slug, search query, why we want it)
WANTED = [
    ("supercontinent-cycle", "Supercontinent cycle diagram",
     "the gather-disperse loop and its sea-level/climate consequences"),
    ("wilson-cycle", "Wilson Cycle diagram",
     "ocean basin opening and closing - the mechanism behind our rift and trench labels"),
    ("seafloor-age", "Age of oceanic lithosphere map",
     "the crustal age pattern our seafloor.py synthesises"),
    ("plate-boundaries", "Tectonic plates boundaries map",
     "surveyed present-day boundaries - the anchor for the advected label raster"),
    ("subduction-zone", "Subduction zone cross section diagram",
     "arc, back-arc and trench anatomy for the feature_art cross-sections"),
    ("mid-ocean-ridge", "Mid ocean ridge spreading diagram",
     "axial valley, transform, fracture zone geometry"),
    ("continental-margin", "Passive continental margin diagram",
     "shelf-slope-rise anatomy; the canyon comb"),
    ("phanerozoic-co2", "Phanerozoic Carbon Dioxide graph",
     "the CO2 curve to check climate.py against"),
    ("phanerozoic-temperature", "Phanerozoic climate change graph",
     "temperature record; superseded by PhanDA but useful for shape"),
    ("oxygen-history", "Oxygenation atmosphere graph",
     "the GOE, the boring billion and the NOE"),
    ("sea-level-phanerozoic", "Phanerozoic sea level graph",
     "first-order eustatic curve"),
    ("extinction-intensity", "Extinction intensity graph Phanerozoic",
     "the Big Five in their stratigraphic context"),
    ("glossopteris-distribution", "Gondwana fossil distribution map Glossopteris",
     "Suess's original continental-drift evidence, and a province map"),
    ("pangaea-map", "Pangaea map 250 Ma",
     "reference reconstruction to audit our own frames against"),
    ("rodinia-map", "Rodinia reconstruction map",
     "the disputed configuration, for the Precambrian frames"),
    ("hotspot-tracks", "Hotspot volcano track map Pacific",
     "plume trails - the fix for our scattered seamounts"),
    ("thermohaline-circulation", "Thermohaline circulation conveyor belt diagram",
     "the global conveyor for the ocean-current model"),
    ("whittaker-biomes", "Whittaker biome classification diagram",
     "the temperature-precipitation cells behind biome_model.py"),
    ("carbon-cycle", "Long term carbon cycle diagram silicate weathering",
     "the feedback that sets CO2 over 10^6 yr"),
    ("geologic-time-scale", "Geologic time scale chart ICS",
     "the chronostratigraphic reference"),
]


def _get(params, tries=4):
    """GET with backoff. A 429 must not be read as 'no such image'."""
    url = API + "?" + urllib.parse.urlencode(params)
    delay = 2.0
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as fh:
                return json.load(fh)
        except Exception as exc:                      # noqa: BLE001
            code = getattr(exc, "code", None)
            if attempt == tries - 1:
                print(f"    ! give up after {tries}: {exc}")
                return None
            print(f"    . retry {attempt+1} ({code or exc}) in {delay:.0f}s")
            time.sleep(delay)
            delay *= 2
    return None


def _licence_ok(meta):
    txt = " ".join(str(meta.get(k, {}).get("value", "")).lower()
                   for k in ("LicenseShortName", "License", "UsageTerms",
                             "Copyrighted", "Permission"))
    if any(b in txt for b in BAD_TOKENS):
        return False, txt.strip()[:90]
    if any(g in txt for g in OK_LICENCES):
        return True, txt.strip()[:90]
    return False, (txt.strip()[:90] or "no machine-readable licence")


def search(query, limit=12):
    r = _get(dict(action="query", format="json", generator="search",
                  gsrsearch=f'filetype:bitmap|drawing {query}',
                  gsrnamespace=6, gsrlimit=limit,
                  prop="imageinfo", iiprop="url|extmetadata|size|mime",
                  iiurlwidth=1200))
    if not r or "query" not in r:
        return []
    out = []
    for page in r["query"]["pages"].values():
        ii = (page.get("imageinfo") or [{}])[0]
        if not ii.get("thumburl") and not ii.get("url"):
            continue
        meta = ii.get("extmetadata", {})
        ok, lic = _licence_ok(meta)
        out.append(dict(title=page.get("title", ""),
                        url=ii.get("thumburl") or ii.get("url"),
                        page=ii.get("descriptionurl", ""),
                        mime=ii.get("mime", ""),
                        width=ii.get("thumbwidth") or ii.get("width"),
                        licence=lic, ok=ok,
                        author=_plain(meta.get("Artist", {}).get("value", "")),
                        credit=_plain(meta.get("Credit", {}).get("value", ""))))
    return out


def _plain(html):
    out, depth = [], 0
    for ch in html or "":
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return " ".join("".join(out).split())[:160]


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh, open(path, "wb") as out:
        out.write(fh.read())
    return os.path.getsize(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for slug, query, why in WANTED:
        print(f"[{slug}] {query}")
        hits = search(query)
        if not hits:
            print("    no results (could be a rate limit - do NOT record as absent)")
            manifest.append(dict(slug=slug, query=query, why=why, status="no-results"))
            time.sleep(2.0)
            continue
        good = [h for h in hits if h["ok"]]
        print(f"    {len(hits)} hits, {len(good)} acceptably licensed")
        if not good:
            manifest.append(dict(slug=slug, query=query, why=why,
                                 status="no-acceptable-licence",
                                 rejected=[h["licence"] for h in hits[:4]]))
            time.sleep(2.0)
            continue
        h = good[0]
        ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/svg+xml": ".svg",
               "image/gif": ".gif"}.get(h["mime"], ".png")
        path = os.path.join(OUT, slug + ext)
        try:
            size = download(h["url"], path)
        except Exception as exc:                      # noqa: BLE001
            print("    ! download failed:", exc)
            manifest.append(dict(slug=slug, query=query, why=why,
                                 status="download-failed", error=str(exc)))
            time.sleep(2.0)
            continue
        print(f"    -> {os.path.basename(path)} ({size:,} B) {h['licence']}")
        manifest.append(dict(slug=slug, query=query, why=why, status="ok",
                             file=os.path.basename(path), title=h["title"],
                             source=h["page"], licence=h["licence"],
                             author=h["author"], credit=h["credit"],
                             verified_subject=False))
        time.sleep(2.0)

    mpath = os.path.join(OUT, "MANIFEST.json")
    with open(mpath, "w") as fh:
        json.dump({"policy": {"accept": list(OK_LICENCES), "refuse": list(BAD_TOKENS)},
                   "warning": "verified_subject is false until a human has looked at "
                              "the contact sheet. Correct licence does NOT mean correct "
                              "subject - about a third came back wrong in the earlier "
                              "photo round.",
                   "items": manifest}, fh, indent=1)
    ok = sum(1 for m in manifest if m["status"] == "ok")
    print(f"\n{ok}/{len(WANTED)} collected. Manifest: {mpath}")
    print("NEXT: build a contact sheet, look at it, and drop the wrong subjects.")


if __name__ == "__main__":
    if "--list" in sys.argv:
        for slug, q, why in WANTED:
            print(f"{slug:28s} {q:58s} {why}")
    else:
        main()
