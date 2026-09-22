"""A cached client for the Paleobiology Database, and the evidence it gives us.

WHY THIS EXISTS. Every organism on a card makes three claims at once: WHAT it
is (so which drawing stands for it), WHEN it lived, and WHERE. For two months
those were authored by hand in three unconnected places, and nothing checked any
of them -- which is how Bison came to be listed for North America at 60 Ma, a
bear came to be drawn as a coyote and kelp as a fish. The registry
(taxa_registry.json, see biota.py) makes each claim exactly once; this module is
the independent evidence each claim is checked against.

The PBDB answers all three from the fossil record itself:

    classification   phylum / class / order / family  -> which body FORM, so the
                     icon follows from what the animal IS, not from a substring
                     of its name
    fea .. lla       first and last appearance, Ma
    occurrences      present-day lng/lat of every collection that yielded it

The last is the useful one. A fossil is found in the crust the animal lived on,
and a label's crust has a present-day address too (build_webdata.region_tags),
so "did this taxon live where this label is" reduces to comparing two
present-day region codes -- independent of which plate model or reference frame
the map is drawn in, at any age. That is the same trick the endemism filter
already used for seven continents; REGIONS below is the finer version.

Evidence, not truth. PBDB ranges carry misidentified and mis-dated occurrences
(it has Megatherium starting in the Oligocene), so the registry's authored range
is what ships and this is what it has to be reconcilable with; biota.py reports
every disagreement rather than silently taking either side.

Cache lives in data/pbdb/ (gitignored, like the PhyloPic cache). Everything the
build needs from it is copied INTO the registry, so a clone with no cache and no
network still builds and still audits.

    python3 pbdb.py Ursus Megatherium         # look up, print the evidence
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "pbdb")
API = "https://paleobiodb.org/data1.2/"
UA = "tectonic-earth-build/1.0 (https://augustg97.github.io/tectonic-earth/)"

# ---------------------------------------------------------------- regions --
#: Present-day crust regions, FIRST MATCH WINS, so the list runs from the small
#: and particular to the large and general. Codes are hierarchical: "af-e" is
#: inside "af", and a taxon ranged to "af" is at home on any "af-*" label while
#: one ranged to "af-e" is at home only there. Boxes are (code, lon0, lon1,
#: lat0, lat1) on PRESENT-DAY coordinates.
#:
#: Why these and not the seven continents the endemism filter used. India and
#: Madagascar are Gondwanan until the Eocene and Arabia is African until the
#: Miocene, so filing them under "Asia" puts Lystrosaurus-grade errors back in
#: by construction; New Zealand, New Guinea and the Pacific islands each ran
#: their own experiment; and Africa, Asia and the Americas are each too large
#: for one code to say anything about a desert card versus a rainforest card.
REGIONS = [
    ("mg", 42.5, 51.0, -26.5, -11.5),          # Madagascar
    ("nz", 164.0, 180.0, -53.0, -28.0),        # Zealandia above water
    ("nz", 163.0, 169.0, -23.5, -19.0),        # New Caledonia (Zealandian crust)
    ("ng", 129.0, 156.0, -11.5, 0.5),          # New Guinea
    ("gl", -60.0, -11.0, 59.0, 84.0),          # Greenland
    ("gl", -74.0, -60.0, 75.5, 79.5),          # its north-west corner
    ("in", 66.0, 93.0, 5.0, 29.0),             # peninsular India, Sri Lanka
    ("in", 69.0, 81.0, 29.0, 35.5),            # Indus plain, Himalayan foreland
    ("ar", 34.0, 60.0, 12.0, 32.5),            # the Arabian plate
    ("oc", -180.0, -120.0, -30.0, 30.0),       # Polynesia, Hawaii
    ("oc", 155.0, 180.0, -23.0, 20.0),         # Melanesia east, Micronesia
    ("oc", -120.0, -85.0, -28.0, 5.0),         # Galapagos, Easter, Juan Fernandez
    # Australia is two records: the Yilgarn, Pilbara and Kimberley of the west
    # (Gogo, the Canning reefs, Pilbara stromatolites) and the Flinders, Emu Bay,
    # Winton and Riversleigh of the east. One code put Muttaburra on the Yilgarn.
    # "au" survives as an ALIAS for the pair (biota.ALIASES).
    ("au-w", 110.0, 129.0, -45.0, -9.5),        # Western Australia
    ("au-e", 129.0, 156.0, -45.0, -9.5),        # the rest, and Tasmania
    # East and South-East Asia are four blocks with four Palaeozoic-Mesozoic
    # histories, and one code for each pair put the Chengjiang fauna on North
    # China and the Cathaysian coal flora on Gondwanan Sibumasu (2026-09-22).
    # "as-e" and "as-se" survive as ALIASES for the pair (biota.ALIASES).
    ("as-sb", 92.0, 100.5, 5.0, 29.0),          # Sibumasu: Myanmar, western Thailand
    ("as-sb", 95.0, 106.0, -6.5, 7.5),          # ... the Malay peninsula and Sumatra
    ("as-s", 106.5, 123.0, 18.0, 33.0),         # the South China block's coast, Hainan, Taiwan
    ("as-ic", 92.0, 129.0, -11.5, 23.5),        # Indochina, Borneo, Java, the Philippines
    ("as-s", 100.0, 123.0, 18.0, 33.0),         # the South China block, south of the Qinling
    ("as-ne", 100.0, 150.0, 33.0, 50.0),        # North China, Korea, Japan
    ("as-ne", 123.0, 150.0, 18.0, 33.0),        # ... Kyushu, the Ryukyus, Taiwan
    ("as-c", 46.0, 120.0, 28.0, 50.0),         # Turan, Kazakhstan, Tarim, Tibet, Mongolia
    ("as-w", 25.0, 66.0, 24.0, 44.0),          # Anatolia, Caucasus, Iran, Afghanistan
    ("as-n", 58.0, 180.0, 50.0, 82.0),         # Siberia and the Russian Far East
    ("as-n", -180.0, -168.0, 60.0, 72.0),      # Chukotka across the dateline
    ("ca", -118.0, -77.0, 7.0, 24.5),          # Mexico south of the Tropic, Central America
    ("ca", -85.5, -59.0, 17.2, 24.5),          # Greater Antilles
    ("ca", -65.0, -59.0, 12.0, 17.2),          # Lesser Antilles
    ("na-n", -170.0, -52.0, 60.0, 84.0),       # Alaska, Arctic Canada
    ("na-n", -180.0, -168.0, 50.0, 72.0),
    ("na-w", -170.0, -100.0, 24.5, 60.0),      # Cordillera and high plains
    ("na-e", -100.0, -52.0, 24.5, 60.0),       # shield, Appalachians, coastal plain
    ("sa-n", -82.0, -34.0, -18.0, 13.0),       # Amazonia, the northern and central Andes
    ("sa-s", -76.0, -39.0, -56.0, -18.0),      # southern cone, Patagonia
    ("sa-s", -62.0, -57.0, -53.0, -51.0),      # Falklands / Malvinas
    ("eu", -25.0, 58.0, 35.0, 72.0),           # Europe to the Urals, Iceland
    ("af-n", -18.0, 40.0, 15.0, 38.0),         # Maghreb, Sahara, Egypt
    ("af-e", 28.0, 52.0, -12.0, 15.0),         # the Rift, Ethiopia, the Horn
    ("af-w", -18.0, 28.0, -12.0, 15.0),        # Guinea, Congo basin
    ("af-s", 10.0, 41.0, -36.0, -12.0),        # Karoo, Kalahari, Zambezi
    ("an", -180.0, 180.0, -90.0, -60.0),       # Antarctica
]
CODES = sorted({r[0] for r in REGIONS})


def region_of(lon, lat):
    """The crust region of a present-day coordinate, or None (open ocean)."""
    if lon is None or lat is None:
        return None
    for code, lo0, lo1, la0, la1 in REGIONS:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            return code
    return None


# ------------------------------------------------------------------ fetch --
def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _get(path, params, key):
    """GET with an on-disk cache. A miss is cached too: a 404 is an answer."""
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, key + ".json")
    if os.path.exists(fn):
        with open(fn) as f:
            return json.load(f)
    url = API + path + "?" + urllib.parse.urlencode(params)
    out = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                out = {"records": [], "miss": e.code}
                break
            time.sleep(2 + 3 * attempt)
        except Exception:                                   # noqa: BLE001
            time.sleep(2 + 3 * attempt)
    if out is None:
        return None                     # network trouble: do NOT cache
    with open(fn, "w") as f:
        json.dump(out, f)
    time.sleep(0.15)
    return out


def taxa(name):
    """Every PBDB taxon carrying this name (homonyms included), most-occurring first."""
    d = _get("taxa/list.json",
             {"name": name, "show": "app,class,ecospace", "rel": "exact"},
             "t-" + _slug(name))
    recs = (d or {}).get("records", [])
    out = []
    for r in recs:
        if r.get("flg") and "V" in r.get("flg", ""):
            pass                        # a variant spelling still resolves; keep
        out.append(r)
    out.sort(key=lambda r: -(r.get("noc") or 0))
    return out


def occurrences(oid, name, limit=4000):
    """Where and when it has been collected: [(lng, lat, early, late), ...]."""
    d = _get("occs/list.json",
             {"base_id": oid, "show": "coords", "limit": limit},
             "o-" + _slug(name) + "-" + _slug(str(oid)))
    out = []
    for r in (d or {}).get("records", []):
        try:
            out.append((float(r["lng"]), float(r["lat"]),
                        float(r["eag"]), float(r["lag"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


RANKS = {2: "subspecies", 3: "species", 4: "subgenus", 5: "genus", 6: "subtribe",
         7: "tribe", 8: "subfamily", 9: "family", 10: "superfamily",
         11: "infraorder", 12: "suborder", 13: "order", 14: "superorder",
         15: "infraclass", 16: "subclass", 17: "class", 18: "superclass",
         19: "subphylum", 20: "phylum", 21: "superphylum", 22: "subkingdom",
         23: "kingdom", 25: "unranked clade", 26: "informal"}


def search_terms(name):
    """What to ask for. A parenthetical is dropped and a binomial also tries
    its genus, because PBDB knows many genera whose species it does not."""
    base = re.sub(r"\s*\([^)]*\)", "", name).strip()
    terms = [base]
    parts = base.split()
    if len(parts) >= 2 and parts[0][:1].isupper() and parts[1][:1].islower():
        terms.append(parts[0])
    return [t for i, t in enumerate(terms) if t and t not in terms[:i]]


def evidence(name, with_occs=True, max_noc=6000):
    """All the PBDB has to say about one card name, or None if it has nothing.

    `regions` is {code: [n, oldest, youngest]} from present-day collection
    coordinates. Skipped for very large clades: "Trilobita" has 60,000
    occurrences and its distribution is "everywhere", which costs a minute to
    learn and tells a card nothing.
    """
    for term in search_terms(name):
        if not re.match(r"^[A-Z][a-z]+( [a-z\-]+){0,2}$", term):
            continue                    # informal ("kelp", "Burgess Shale biota")
        recs = taxa(term)
        if not recs:
            continue
        r = recs[0]
        ev = {"asked": name, "matched": r.get("nam"), "exact": term == name,
              "oid": r.get("oid"), "rank": RANKS.get(r.get("rnk"), str(r.get("rnk"))),
              "extant": r.get("ext") == "1", "noc": r.get("noc") or 0,
              "fea": r.get("fea"), "lla": r.get("lla"),
              "phylum": r.get("phl"), "class": r.get("cll"), "order": r.get("odl"),
              "family": r.get("fml"), "genus": r.get("gnl"),
              "env": r.get("jev"), "motility": r.get("jmo"), "habit": r.get("jlh"),
              "diet": r.get("jdt"),
              "homonyms": [{"oid": h.get("oid"), "class": h.get("cll"),
                            "phylum": h.get("phl"), "noc": h.get("noc")}
                           for h in recs[1:4]]}
        if with_occs and 0 < ev["noc"] <= max_noc:
            reg = {}
            for lng, lat, eag, lag in occurrences(r["oid"], term):
                c = region_of(lng, lat) or "sea"
                s = reg.setdefault(c, [0, lag, eag])
                s[0] += 1
                s[1] = max(s[1], eag)
                s[2] = min(s[2], lag)
            ev["regions"] = {k: [v[0], round(v[1], 2), round(v[2], 2)]
                             for k, v in sorted(reg.items(), key=lambda kv: -kv[1][0])}
        return ev
    return None


def top_genera(code, max_ma, min_ma, base_name, n=40):
    """The genera most often collected from one crust region in one time window.

    This is the authoring worklist for a thin cell: asked "what should a
    Miocene Patagonian card show", the record's own answer is whatever was dug
    up there most -- which is how a card gets Astrapotherium and Peltephilus
    rather than the three South American mammals everyone already knows.
    Counts are collections, not abundance, so treat the order as a guide.
    """
    boxes = [r for r in REGIONS if r[0] == code or r[0].startswith(code + "-")]
    tally = {}
    for _c, lo0, lo1, la0, la1 in boxes:
        d = _get("occs/taxa.json",
                 {"base_name": base_name, "max_ma": max_ma, "min_ma": min_ma,
                  "lngmin": lo0, "lngmax": lo1, "latmin": la0, "latmax": la1,
                  "rank": "genus", "show": "class", "limit": 6000},
                 "g-" + _slug(f"{base_name}-{max_ma}-{min_ma}-{lo0}-{lo1}-{la0}-{la1}"))
        for r in (d or {}).get("records", []):
            nm = r.get("nam")
            if not nm or " " in nm:
                continue
            t = tally.setdefault(nm, [0, r.get("cll"), r.get("odl"), r.get("fml")])
            t[0] += r.get("noc") or 0
    rows = sorted(tally.items(), key=lambda kv: -kv[1][0])[:n]
    return [(nm, v[0], v[1], v[2], v[3]) for nm, v in rows]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--top":
        # pbdb.py --top sa-s 23 5.3 Mammalia [n]
        code, mx, mn, base = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
        n = int(sys.argv[6]) if len(sys.argv) > 6 else 40
        for nm, noc, cl, od, fm in top_genera(code, mx, mn, base, n):
            print(f"{noc:5d}  {nm:26s} {cl or ''} / {od or ''} / {fm or ''}")
    else:
        for nm in sys.argv[1:]:
            print(json.dumps(evidence(nm), indent=1))
