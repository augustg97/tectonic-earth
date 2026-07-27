"""A1 / A3 / A4 — does tracking in the PaleoDEMs' OWN frame beat correcting Merdith?

The app's largest residual error is that 27 tracked labels sit on the wrong medium
for more than a third of their span. The diagnosed cause is a two-frame problem:
terrain comes from the Scotese & Wright PaleoDEMs, feature tracks come from
Merdith et al. (2021), and palaeomagnetism never constrains absolute longitude, so
the two models place the same continent at different longitudes. `frame_offset.py`
patches it with a smoothed rigid longitude shift per age. That helped (craters on
plausible terrain 80% -> 90%) but cannot close it, because the real difference is
regional, not rigid.

Gap item A1 asked whether Scotese publishes his own rotations. **He does** -
PALEOMAP_PlateModel.rot ships inside Scotese_PaleoAtlas_v3.zip, CC-BY 4.0, spanning
+250 Ma (future) to 1100 Ma, 258 plate IDs. If features are tracked with THAT model
the frame mismatch is identically zero by construction, and A3 (regional frame
correction) and A4 become unnecessary.

This script measures whether that is actually true, on the app's own shipped
elevation field, over a population - never on a favourite feature.

METHOD
  Sample N present-day points that are land today. For each age, back-advect each
  point three ways and ask the shipped `_e` texture what medium it lands on:
      raw       Merdith, no correction        (what the app did before)
      corrected Merdith + frame_offset        (what the app does now)
      paleomap  Scotese PALEOMAP rotations    (the candidate)
  Score = fraction still on land. Land-today crust should still be continental
  crust in the past: it may be flooded shelf, but it should not be abyssal plain.

  READ-ONLY. Changes nothing in build/.

    ../../venv/bin/python frame_experiment.py            # the comparison
    ../../venv/bin/python frame_experiment.py --ages 100,300,500
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, BUILD)

PALEOMAP_DIR = os.path.join(ROOT, "data", "paleomap_gpm",
                            "Scotese PaleoAtlas_v3", "PALEOMAP Global Plate Model")
PALEOMAP_ROT = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlateModel.rot")
PALEOMAP_POLY = os.path.join(PALEOMAP_DIR, "PALEOMAP_PlatePolygons.gpml")

MERDITH_DIR = os.path.join(ROOT, "data", "merdith2021", "SM2_X")
MERDITH_ROT = os.path.join(MERDITH_DIR, "1000_0_rotfile_Merdith_et_al.rot")
MERDITH_POLY = os.path.join(MERDITH_DIR, "shapes_static_polygons_Merdith_et_al.gpml")
FRAME_OFFSET = os.path.join(HERE, "frame_offset_merdith.json")

AGES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
# A coarse global sample of present-day continental interiors and margins. These
# are all land today, spread over every craton, so the score is a population
# statistic and not a story about one feature.
SAMPLE = [
    (-100, 45), (-90, 35), (-110, 55), (-75, 45), (-120, 60), (-85, 60), (-105, 65),
    (-60, -10), (-50, -20), (-65, -30), (-45, -5), (-70, -15),
    (10, 10), (25, 5), (20, -20), (30, -25), (0, 20), (35, 10), (15, 25),
    (10, 50), (25, 60), (5, 45), (30, 50), (40, 55), (60, 55), (80, 60),
    (100, 60), (120, 60), (130, 50), (110, 40), (90, 45),
    (78, 22), (80, 12), (75, 28),
    (115, 39), (110, 29),
    (135, -25), (120, -28), (145, -20), (130, -18),
    (25, -30), (30, -20), (20, -28),
    (35, 0), (40, -5), (45, -15),
    (-8, 12), (-5, 20), (-10, 8),
    (170, -43), (-150, 65), (-45, 70), (-20, 65),
]


def load_field(age):
    """The shipped elevation texture nearest `age`, in metres."""
    import fieldpack
    from PIL import Image
    import numpy as np
    fields = os.path.join(ROOT, "web", "fields")
    best, bestd = None, 1e9
    for fn in os.listdir(fields):
        if not fn.endswith("_e.webp") or fn.startswith("fut"):
            continue
        try:
            a = float(fn.split("_")[1])
        except (IndexError, ValueError):
            continue
        if abs(a - age) < bestd:
            best, bestd = fn, abs(a - age)
    if best is None:
        return None, None
    img = np.asarray(Image.open(os.path.join(fields, best)).convert("L")).astype(np.float32)
    # The function is dec_elev, not decode. The hasattr guard here was always
    # False, so this quietly used the local _decode fallback - which is how a
    # wrong Z_RANGE survived in it. Call the real one.
    return fieldpack.dec_elev(img / 255.0), best


def _decode(img):
    """signed-sqrt decode, matching build/fieldpack.py.

    Z_RANGE IS 8000.0. This said 11000.0 until WP-05 caught it, and the A5/F1
    handoff prompt propagated the error by telling that session to decode "exactly
    as _decode() does". Consequence for the WP-04 result: none to the headline -
    the land/abyss ranking is scored with ONE threshold across all three frames, so
    a monotonic rescale of every value cannot reorder them - but the "shelf" band
    boundary was really -364 m, not -500 m. Prefer fieldpack.decode() outright.
    """
    import numpy as np
    t = img / 255.0 * 2.0 - 1.0
    return np.sign(t) * (t * t) * 8000.0


def sample(grid, lon, lat):
    h, w = grid.shape
    x = int(((lon + 180.0) % 360.0) / 360.0 * w) % w
    y = int((90.0 - lat) / 180.0 * h)
    y = max(0, min(h - 1, y))
    return float(grid[y, x])


def build_reconstructors():
    """(name, callable(lon, lat, age) -> (lon, lat) or None) for each frame.

    All three frames are pinned here BY NAME rather than read out of
    build/paleo_tracks.py. This experiment's whole content is a three-way
    comparison, and once the build adopted PALEOMAP (which is what the experiment
    recommended) importing the build's reconstructor would have silently made all
    three columns the same model and reported a dead heat. Same reason
    regression_gate.py pins both of its frames. See frame_offset_merdith.json for
    the retired rigid correction, kept here because build/frame_offset.json is
    deleted with the switch.
    """
    import json
    out = []

    if os.path.exists(MERDITH_ROT) and os.path.exists(MERDITH_POLY):
        import pygplates
        m_rot = pygplates.RotationModel(MERDITH_ROT)
        m_part = pygplates.PlatePartitioner(
            pygplates.FeatureCollection(MERDITH_POLY), m_rot, reconstruction_time=0)

        try:
            with open(FRAME_OFFSET) as fh:
                tab = {int(k): float(v) for k, v in json.load(fh).items()}
        except Exception:                                  # noqa: BLE001
            tab = {}
        keys = sorted(tab)

        def shift(age):
            if not keys:
                return 0.0
            a = abs(float(age))
            if a <= keys[0]:
                return tab[keys[0]]
            if a >= keys[-1]:
                return tab[keys[-1]]
            for i in range(len(keys) - 1):
                k0, k1 = keys[i], keys[i + 1]
                if k0 <= a <= k1:
                    f = 0.0 if k1 == k0 else (a - k0) / (k1 - k0)
                    return tab[k0] + (tab[k1] - tab[k0]) * f
            return 0.0

        def _merd(lon, lat, age, corr):
            pt = pygplates.PointOnSphere(float(lat), float(lon))
            f = m_part.partition_point(pt)
            pid = f.get_feature().get_reconstruction_plate_id() if f else 0
            try:
                p = m_rot.get_rotation(float(age), pid) * pt
            except Exception:                              # noqa: BLE001
                return None
            la, lo = p.to_lat_lon()
            if corr:
                lo = ((lo + shift(age) + 180.0) % 360.0) - 180.0
            return (lo, la)

        def merdith_raw(lon, lat, age):
            return _merd(lon, lat, age, False)

        def merdith_corr(lon, lat, age):
            return _merd(lon, lat, age, True)

        out.append(("merdith-raw", merdith_raw))
        out.append(("merdith-corrected", merdith_corr))

    if os.path.exists(PALEOMAP_ROT) and os.path.exists(PALEOMAP_POLY):
        import pygplates
        rot = pygplates.RotationModel(PALEOMAP_ROT)
        polys = pygplates.FeatureCollection(PALEOMAP_POLY)
        # Partition present-day points onto PALEOMAP plate polygons at t=0.
        partitioner = pygplates.PlatePartitioner(polys, rot, reconstruction_time=0)

        def paleomap(lon, lat, age, rot=rot, partitioner=partitioner):
            pt = pygplates.PointOnSphere(lat, lon)
            found = partitioner.partition_point(pt)
            if found is None:
                return None
            pid = found.get_feature().get_reconstruction_plate_id()
            try:
                fr = rot.get_rotation(float(age), pid)
            except Exception:                              # noqa: BLE001
                return None
            p = fr * pt
            la, lo = p.to_lat_lon()
            return (lo, la)

        out.append(("paleomap", paleomap))
    return out


def main():
    ages = AGES
    if "--ages" in sys.argv:
        ages = [float(a) for a in sys.argv[sys.argv.index("--ages") + 1].split(",")]

    recons = build_reconstructors()
    if not recons:
        print("no reconstructors available (pygplates / model files missing)")
        return
    print("frames under test:", ", ".join(n for n, _ in recons))
    print(f"{len(SAMPLE)} present-day land points, {len(ages)} ages\n")

    hdr = f"{'age':>6} {'frame':>20} {'on land':>9} {'shelf':>7} {'abyss':>7} {'lost':>6}"
    print(hdr)
    print("-" * len(hdr))
    totals = {n: [0, 0, 0, 0] for n, _ in recons}

    for age in ages:
        grid, fn = load_field(age)
        if grid is None:
            continue
        for name, fn_rec in recons:
            land = shelf = abyss = lost = 0
            for lon, lat in SAMPLE:
                p = fn_rec(lon, lat, age)
                if p is None:
                    lost += 1
                    continue
                z = sample(grid, p[0], p[1])
                if z >= 0:
                    land += 1
                elif z > -500:
                    shelf += 1
                else:
                    abyss += 1
            n = len(SAMPLE)
            print(f"{age:>6.0f} {name:>20} {land/n:>8.0%} {shelf/n:>6.0%} "
                  f"{abyss/n:>6.0%} {lost:>5}")
            t = totals[name]
            t[0] += land; t[1] += shelf; t[2] += abyss; t[3] += lost
        print()

    print("=" * len(hdr))
    n = len(SAMPLE) * len(ages)
    rows = []
    for name, _ in recons:
        land, shelf, abyss, lost = totals[name]
        rows.append((land + shelf, name, land, shelf, abyss, lost))
        print(f"{'ALL':>6} {name:>20} {land/n:>8.0%} {shelf/n:>6.0%} "
              f"{abyss/n:>6.0%} {lost:>5}")
    rows.sort(reverse=True)
    best = rows[0]
    print(f"\nBEST on land-or-shelf: {best[1]} at {best[0]/n:.0%}")
    print("Land-today crust should be continental crust in the past. It may be a "
          "flooded shelf,\nbut landing on ABYSSAL PLAIN means the frame put it in "
          "the wrong ocean.")


if __name__ == "__main__":
    main()
