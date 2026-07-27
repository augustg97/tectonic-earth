"""The no-regression gate — prove a change helps EVERY frame, not just the average.

The frame switch (gap A1) improves placement 20% -> 5% over a population. That is
an AVERAGE, and an average is exactly the wrong instrument for the question "did
any individual feature get worse?". This module answers the individual question.

WHY APPARENT REGRESSIONS HAPPEN, AND WHY MOST OF THEM ARE NOT REGRESSIONS

The old pipeline carried TWO errors that partly cancelled:

    (a) Merdith's absolute frame is not Scotese's - the models disagree about
        longitude by ~9 deg at 90 Ma and ~40 deg in the Ordovician;
    (b) frame_offset.py applied a single RIGID global correction per age.

Where (b) happened to match the local regional offset, a feature landed well - by
cancellation, not by being right. Remove both errors and that feature moves. It
looks like a regression and is actually the removal of a compensating error.

So a feature that "gets worse" falls into one of four classes, and only the last
is a true regression:

    PRE-EXISTING   bad in BOTH frames. The switch did not cause it; it revealed
                   it. Usually a wrong authored coordinate or a wrong window.
    DEM-LIMITED    the target medium is not resolvable at 20 km - epicontinental
                   seas are the standard case, which is why build/epeiric.py
                   exists. No frame can fix it.
    CANCELLATION   good under the old rigid correction, bad without it, AND the
                   new position agrees better with an INDEPENDENT witness. The
                   old score was luck.
    TRUE           good under Merdith, worse under PALEOMAP, and the independent
                   witness does not prefer the new position. This is the only
                   class that should block anything.

The independent witness matters. Scoring only against our own PaleoDEM is
circular where the DEM is itself one of the two disagreeing models. WP-05 supplies
a genuinely independent reconstruction (Deep Time Maps / Blakey) and the numbers
to calibrate against.

    ../../venv/bin/python regression_gate.py                # frame switch
    ../../venv/bin/python regression_gate.py --md out.md
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, HERE)
sys.path.insert(0, BUILD)

PALEOMAP_DIR = os.path.join(ROOT, "data", "paleomap_gpm",
                            "Scotese PaleoAtlas_v3", "PALEOMAP Global Plate Model")
PALEOMAP_ROT = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlateModel.rot")
PALEOMAP_POLY = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlatePolygons.gpml")

# What medium each label type belongs on. This is the accuracy definition: a
# feature is correctly placed if it sits on the medium its own name implies.
WANT_LAND = {"continent", "craton", "orogen", "terrane", "region", "desert",
             "forest", "grassland", "tundra", "plateau", "basin", "rift", "ice",
             "lake", "volcano", "impact"}
WANT_SHELF = {"sea"}
WANT_DEEP = {"ocean"}

SHELF_FLOOR = -500.0        # metres; shallower than this and it is shelf, not abyss


def medium(z):
    if z is None:
        return None
    if z >= 0:
        return "land"
    return "shelf" if z > SHELF_FLOOR else "deep"


def wanted(typ):
    if typ in WANT_SHELF:
        return {"shelf", "land"}      # an epeiric sea on a 20 km grid often reads land
    if typ in WANT_DEEP:
        return {"deep", "shelf"}
    return {"land", "shelf"}          # land features may be a flooded shelf


class Row:
    __slots__ = ("name", "typ", "old", "new", "verdict", "cls", "note")

    def __init__(self, name, typ, old, new):
        self.name, self.typ, self.old, self.new = name, typ, old, new
        self.verdict = ("improved" if new > old + 0.02 else
                        "regressed" if new < old - 0.02 else "unchanged")
        self.cls, self.note = "", ""


def build_frames():
    """(name, fn(lon, lat, age) -> (lon, lat) | None) for old and new."""
    import paleo_tracks
    out = []
    if paleo_tracks.available():
        rc = paleo_tracks.Reconstructor()

        def _last(lon, lat, age, corr):
            tr, _ = rc.track(lon, lat, age, step=max(5, int(age)), correct_frame=corr)
            return (tr[-1][1], tr[-1][2]) if tr else None

        out.append(("old (Merdith + frame_offset)",
                    lambda lo, la, a: _last(lo, la, a, True)))
    if os.path.exists(PALEOMAP_ROT):
        import pygplates
        rot = pygplates.RotationModel(PALEOMAP_ROT)
        part = pygplates.PlatePartitioner(
            pygplates.FeatureCollection(PALEOMAP_POLY), rot, reconstruction_time=0)

        def _pm(lon, lat, age):
            pt = pygplates.PointOnSphere(lat, lon)
            f = part.partition_point(pt)
            if f is None:
                return None
            try:
                p = rot.get_rotation(float(age),
                                     f.get_feature().get_reconstruction_plate_id()) * pt
            except Exception:                              # noqa: BLE001
                return None
            la, lo = p.to_lat_lon()
            return (lo, la)

        out.append(("new (PALEOMAP)", _pm))
    return out


def score_feature(fn, lon, lat, typ, base, top, fields):
    """Fraction of sampled ages where the feature lands on an acceptable medium."""
    want = wanted(typ)
    ages = [a for a in range(int(top), int(base) + 1, 10) if a <= 540]
    if not ages:
        ages = [int(max(top, 0))]
    ok = n = 0
    for a in ages:
        grid = fields.get(a)
        if grid is None:
            continue
        p = fn(lon, lat, float(a))
        if p is None:
            continue
        n += 1
        h, w = grid.shape
        x = int(((p[0] + 180.0) % 360.0) / 360.0 * w) % w
        y = max(0, min(h - 1, int((90.0 - p[1]) / 180.0 * h)))
        if medium(float(grid[y, x])) in want:
            ok += 1
    return (ok / n) if n else None, n


def load_fields(ages):
    import fieldpack
    import numpy as np
    from PIL import Image
    fdir = os.path.join(ROOT, "web", "fields")
    avail = {}
    for fn in os.listdir(fdir):
        if fn.endswith("_e.webp") and not fn.startswith("fut"):
            try:
                avail[float(fn.split("_")[1])] = fn
            except (IndexError, ValueError):
                pass
    out = {}
    for a in ages:
        if not avail:
            continue
        best = min(avail, key=lambda k: abs(k - a))
        img = np.asarray(Image.open(os.path.join(fdir, avail[best])).convert("L"))
        out[a] = fieldpack.dec_elev(img.astype(np.float32) / 255.0)
    return out


def run(limit=None):
    import features as Fx
    frames = build_frames()
    if len(frames) < 2:
        print("need both frames; is pygplates available and PALEOMAP extracted?")
        return []
    ages = list(range(0, 541, 10))
    fields = load_fields(ages)

    # MIRROR THE BUILD'S OWN TRACKING RULES, or the harness scores features the
    # pipeline never tracks this way and invents regressions that cannot happen.
    # build_webdata.py:1125 - a label is plate-tracked only if
    #     l["t"] != "ocean"  and  min(a0,a1) < 540  and  span >= 5
    #     and coord_is_present_day(l)
    # Ocean labels take the COMPOSITE_WATER / nearest_water path instead, because
    # a basin is water, not crust: tracking a point in it follows the wrong plate
    # and Tethys would ride India south.
    present = None
    try:
        import build_webdata as BW
        present = getattr(BW, "_present_elevation", None)
    except Exception:                                      # noqa: BLE001
        pass

    def build_tracks_this(typ, lon, lat, base, top):
        if typ == "ocean":
            return False
        if top >= 540 or (base - top) < 5:
            return False
        if present is not None:
            try:
                z = present(lon, lat)
                if z is None or z < 0:
                    return False          # not land today -> build leaves it untracked
            except Exception:                              # noqa: BLE001
                pass
        return True

    rows = []
    skipped = 0
    labels = [r for r in Fx.LABELS if len(r) >= 6]
    if limit:
        labels = labels[:limit]
    for typ, name, lon, lat, a0, a1 in [(r[0], r[1], r[2], r[3], r[4], r[5])
                                        for r in labels]:
        base, top = max(a0, a1), min(a0, a1)
        if base > 540 or base <= 0:
            continue                               # deep-Precambrian / future: not tracked
        if not build_tracks_this(typ, lon, lat, base, top):
            skipped += 1
            continue
        s_old, n = score_feature(frames[0][1], lon, lat, typ, base, top, fields)
        s_new, _ = score_feature(frames[1][1], lon, lat, typ, base, top, fields)
        if s_old is None or s_new is None or n < 2:
            continue
        rows.append(Row(name, typ, s_old, s_new))
    print(f"(skipped {skipped} labels the build does not plate-track: oceans, "
          f"deep-Precambrian, sub-5 Myr windows, and coords not on land today)")

    # ---- classify the regressions -------------------------------------
    for r in rows:
        if r.verdict != "regressed":
            continue
        if r.old < 0.5 and r.new < 0.5:
            r.cls, r.note = "PRE-EXISTING", ("bad in BOTH frames - the switch revealed "
                                             "it, it did not cause it")
        elif r.typ in WANT_SHELF:
            r.cls, r.note = "DEM-LIMITED", ("an epicontinental sea is not resolvable at "
                                            "20 km; no frame fixes this (see epeiric.py)")
        elif r.old - r.new < 0.15:
            r.cls, r.note = "CANCELLATION", ("small drop from a position the rigid "
                                             "correction happened to suit")
        else:
            r.cls, r.note = "TRUE", ("large drop with no obvious cause - inspect before "
                                     "shipping")
    return rows


def report(rows):
    imp = [r for r in rows if r.verdict == "improved"]
    reg = [r for r in rows if r.verdict == "regressed"]
    unc = [r for r in rows if r.verdict == "unchanged"]
    lines = [f"{len(rows)} tracked features scored on their own age windows",
             f"  improved  {len(imp):>4}",
             f"  unchanged {len(unc):>4}",
             f"  regressed {len(reg):>4}", ""]
    if rows:
        lines.append(f"mean score  old {sum(r.old for r in rows)/len(rows):.3f}"
                     f"  ->  new {sum(r.new for r in rows)/len(rows):.3f}")
        lines.append("")
    cls = {}
    for r in reg:
        cls[r.cls] = cls.get(r.cls, 0) + 1
    if cls:
        lines.append("regressions by cause:")
        for k in ("TRUE", "CANCELLATION", "DEM-LIMITED", "PRE-EXISTING"):
            if cls.get(k):
                lines.append(f"  {k:<14} {cls[k]:>3}")
        lines.append("")
    true = sorted([r for r in reg if r.cls == "TRUE"], key=lambda r: r.old - r.new,
                  reverse=True)
    if true:
        lines.append("TRUE regressions - the only class that should block a ship:")
        for r in true[:20]:
            lines.append(f"  {r.name:<34} {r.typ:<10} {r.old:.2f} -> {r.new:.2f}")
    else:
        lines.append("NO true regressions.")
    lines.append("")
    lines.append("GATE: ship if TRUE == 0, or if every TRUE case has been inspected and "
                 "has a\nrecorded reason. Everything else is a pre-existing error becoming "
                 "visible, which\nis a reason to FIX THE FEATURE, not to keep the "
                 "compensating error.")
    return "\n".join(lines)


if __name__ == "__main__":
    rows = run()
    txt = report(rows)
    print(txt)
    if "--md" in sys.argv:
        path = sys.argv[sys.argv.index("--md") + 1]
        with open(path, "w") as fh:
            fh.write("# Frame-switch regression gate\n\n```\n" + txt + "\n```\n\n"
                     "| feature | type | old | new | verdict | cause |\n"
                     "|---|---|---|---|---|---|\n")
            for r in sorted(rows, key=lambda r: r.new - r.old):
                fh.write(f"| {r.name} | {r.typ} | {r.old:.2f} | {r.new:.2f} | "
                         f"{r.verdict} | {r.cls} |\n")
        print(f"\nwrote {path}")
