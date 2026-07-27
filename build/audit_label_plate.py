"""Does a label ride the continent its own text says it is on?

THE BUG THIS CATCHES. build_labels() decides how to treat a coordinate by asking
one question: is it land today? If yes it is taken as a present-day position and
plate-tracked. If no, it is understood to be authored in its own era's frame
(Gondwana at 30E 40S) and left alone. That rule is right, and it has a blind
spot: a PALAEO coordinate that happens to fall on modern land is tracked anyway,
silently, on whatever plate now occupies that spot.

Nothing complains. The label still draws, still moves, still looks plausible --
it is simply riding the wrong continent. Found this way, in one pass:

    Laurentia          authored at its Ordovician equator -> Guyana  -> S AMERICA
    Sauk, Tippecanoe, Kaskaskia and Absaroka Seas, all four of Sloss's
                       floodings of Laurentia          -> Caribbean  -> S AMERICA
    Catskill Delta     (New York)                      -> Brazil     -> S AMERICA
    Variscan Belt      (France, Iberia, Bohemia)       -> Sahara     -> AFRICA
    Caledonides        (Scotland, Norway, Greenland)   -> W Sahara   -> AFRICA
    Muschelkalk Sea    (Germany)                       -> Libya      -> AFRICA
    Sveconorwegian Blt (southern Norway)                -> Algeria    -> AFRICA

Eleven labels, the same defect as the Newark Rift Valleys, which was found by
hand. This finds them by machine.

HOW. Every label that is land today is plate-tracked, so its plate id is knowable.
PALEOMAP uses the standard GPlates id blocks -- 1xx North America, 2xx South
America, 3xx/4xx/6xx Eurasia, 5xx India and Arabia, 7xx Africa, 8xx Australia and
Antarctica -- which this verifies empirically at startup rather than trusting.
Then the label's own name and description are scanned for continent names. If the
text commits to a continent and the plate says a different one, that is a finding.

WHAT IT DELIBERATELY DOES NOT FLAG. Plenty of features genuinely span continents:
Laurasia IS North America plus Eurasia, Beringia IS both sides of the strait, the
Central Pangaean Mountains run from the Appalachians through Iberia into Morocco.
Those are listed in ACCEPTED with a reason each, so the check stays at zero and a
new one has to be argued for rather than absorbed.

    ../venv/bin/python audit_label_plate.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Plate-id block -> continent. Verified against known present-day points in
# _verify_blocks() below; a rotation file that renumbered its plates would fail
# there rather than quietly mis-grouping every label.
BLOCK = {1: "North America", 2: "South America", 3: "Eurasia", 4: "Eurasia",
         5: "India/Arabia", 6: "Eurasia", 7: "Africa", 8: "Australia/Antarctica",
         9: "oceanic"}

PROBE = {"North America": [(-100, 45), (-90, 40), (-110, 40), (-95, 55)],
         "South America": [(-60, -15), (-50, -10), (-70, -30)],
         "Eurasia": [(10, 50), (30, 55), (100, 60), (130, 50)],
         "India/Arabia": [(78, 22), (75, 15), (50, 20)],
         "Africa": [(20, 5), (10, 20), (25, -20)],
         "Australia/Antarctica": [(135, -25), (0, -80), (90, -75)]}

# A term commits a label to a continent only if it names a place, not an event.
# "collided with India" says nothing about where the label sits, so India's own
# terms are the subcontinent's name and its parts.
TERMS = [
    ("North America", ("laurentia", "north america", "canadian shield",
                       "appalachian", "midcontinent", "mississipp", "catskill")),
    ("South America", ("south america", "amazon", "brazil", "andes", "patagonia")),
    ("Eurasia", ("siberia", "baltica", "europe", "european", "scandinav",
                 "kazakh", "germany", "iberia", "bohemia", "scotland")),
    ("India/Arabia", ("india", "deccan", "arabia", "arabian")),
    ("Africa", ("africa", "african", "sahara", "congo", "kalahari", "karoo")),
    ("Australia/Antarctica", ("australia", "australian", "antarctic", "tasman")),
]

# Genuinely trans-continental, or named for a collision rather than a place.
# Each is allowed to sit on any ONE of the continents it spans.
ACCEPTED = {
    "Laurasia": "is North America AND Eurasia; either is a fair anchor",
    "Eurasia": "the label for the continent, anchored in Siberia",
    "Beringian Steppe-Tundra": "spanned the strait; Alaska and Chukotka both",
    "Gondwanan Polar Tundra": "Gondwana's pole sat in what is now Antarctica",
    "Central Pangaean Mts": "one chain from the Appalachians through Iberia to "
                            "Morocco; every anchor is on some other part of it",
    "Hun Superterrane": "a peri-Gondwanan strip that RIFTS off Africa and ends "
                        "up as southern Europe; both are true, at different ages",
    "Kuunga Orogen": "the India-Antarctica/Australia suture: it is on both",
    "Wallacea": "the boundary itself, between Sundaland and Sahul",
    "Greater Caucasus": "raised by Arabia's collision and riding its plate",
    "Arabian Desert": "Arabia is African crust on a plate of its own",
    "Tethyan Himalaya": "the Indian margin, now thrust onto the Eurasian side",
    "Himalaya": "the collision itself; GPlates carries it on the Eurasian plate",
    "Sundaland": "Eurasia's SE promontory, named for its Indian-Ocean margin",
    "Tien Shan": "Asian, described by the collision that reactivated it",
    "Broken Ridge": "rifted from Kerguelen; Indian Ocean floor, not a continent",
    "Indian Ocean": "an ocean, named for the subcontinent it borders",
    "Mascarene Plateau": "Indian-Ocean floor on the African plate",
    "Mauritia": "an Indian fragment left behind on African crust",
    "Seychelles Microcontinent": "Indian crust stranded on the African plate",
    "Australasian Belt": "the arcs between Eurasia and Australia",
    "Gulf of Mexico": "its own small plate, between the two Americas",
    "Lhasa Terrane": "rifted from Gondwana, welded to Asia; it is Asian now",
    "Tibetan Plateau": "Asian crust, raised by India arriving under it",
    "Qilian Belt": "in China, described by the collisions that closed it",
    "Pangaea Proxima Inland Sea": "a future sea, sited on Africa as India arrives",
}


def _load():
    import build_webdata as BW                               # noqa: PLC0415
    import features                                          # noqa: PLC0415
    import paleo_tracks                                      # noqa: PLC0415
    if not paleo_tracks.available():
        return None, None, None, None
    return (features, paleo_tracks.Reconstructor(),
            BW._present_elevation(), BW._elev_lookup)


def _verify_blocks(rec):
    """The id->continent map is an assumption. Check it before relying on it."""
    bad = []
    for cont, pts in PROBE.items():
        for lon, lat in pts:
            got = BLOCK.get(rec.plate_id(lon, lat) // 100)
            if got != cont:
                bad.append(f"({lon},{lat}) is {cont} but plate says {got}")
    return bad


def main():
    features, rec, present, elev = _load()
    if features is None:
        print("pyGPlates unavailable; cannot check plate ids")
        return 0
    bad = _verify_blocks(rec)
    if bad:
        print("PLATE-ID BLOCKS DO NOT MATCH THE ROTATION FILE:")
        for b in bad:
            print("   ", b)
        print(f"\n{len(bad)} findings")
        return len(bad)

    findings, tracked, exempt = [], 0, 0
    for e in features.LABELS:
        typ, name, lon, lat = e[0], e[1], e[2], e[3]
        if elev(present, lon, lat) <= 0:
            continue                       # not tracked; authored in its own frame
        tracked += 1
        text = (name + " " + features.DESCRIPTIONS.get(name, "")).lower()
        want = {c for c, ks in TERMS if any(k in text for k in ks)}
        if not want:
            continue                       # says nothing about where it is
        pid = rec.plate_id(lon, lat)
        got = BLOCK.get(pid // 100, "?")
        if got in ("oceanic", "?") or got in want:
            continue
        if name in ACCEPTED:
            exempt += 1
            continue
        findings.append((name, typ, lon, lat, pid, got, sorted(want)))

    print(f"{tracked} labels are land today and therefore plate-tracked; "
          f"{exempt} trans-continental by design")
    for name, typ, lon, lat, pid, got, want in findings:
        print(f"  {name:<28} [{typ:<9}] ({lon:>7},{lat:>6}) rides plate {pid} "
              f"= {got}, but its text says {' or '.join(want)}")
    print(f"\n{len(findings)} findings")
    return len(findings)


if __name__ == "__main__":
    # Non-zero on findings, so it is useful on its own. audit_all.py reads the
    # printed count rather than the exit code, so this does not gate the build.
    sys.exit(1 if main() else 0)
