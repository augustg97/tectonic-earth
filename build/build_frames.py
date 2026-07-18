"""Batch-render paleogeographic frames from Scotese/Wright paleoDEMs.

Picks the nearest available DEM for each target age, renders with render.py,
writes WebP frames + frames_manifest.json (age, era, period, sealevel, file).
"""
import os, re, glob, json, sys
import numpy as np
import netCDF4
from PIL import Image
from render import render_u8

DEM_DIR = "../data/paleodems_6min"
OUT_DIR = "../web/frames"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_W, OUT_H = 1024, 512
WEBP_Q = 70

# ---- geologic period lookup (age Ma -> period/epoch label) ----------------
PERIODS = [
    (0, 0.012, "Holocene", "Quaternary"),
    (0.012, 2.58, "Pleistocene", "Quaternary"),
    (2.58, 5.33, "Pliocene", "Neogene"),
    (5.33, 23.0, "Miocene", "Neogene"),
    (23.0, 33.9, "Oligocene", "Paleogene"),
    (33.9, 56.0, "Eocene", "Paleogene"),
    (56.0, 66.0, "Paleocene", "Paleogene"),
    (66.0, 100.5, "Late Cretaceous", "Cretaceous"),
    (100.5, 145.0, "Early Cretaceous", "Cretaceous"),
    (145.0, 163.5, "Late Jurassic", "Jurassic"),
    (163.5, 174.1, "Middle Jurassic", "Jurassic"),
    (174.1, 201.4, "Early Jurassic", "Jurassic"),
    (201.4, 237.0, "Late Triassic", "Triassic"),
    (237.0, 247.2, "Middle Triassic", "Triassic"),
    (247.2, 251.9, "Early Triassic", "Triassic"),
    (251.9, 259.5, "Lopingian", "Permian"),
    (259.5, 273.0, "Guadalupian", "Permian"),
    (273.0, 298.9, "Cisuralian", "Permian"),
    (298.9, 323.2, "Pennsylvanian", "Carboniferous"),
    (323.2, 358.9, "Mississippian", "Carboniferous"),
    (358.9, 382.7, "Late Devonian", "Devonian"),
    (382.7, 393.3, "Middle Devonian", "Devonian"),
    (393.3, 419.2, "Early Devonian", "Devonian"),
    (419.2, 443.8, "Silurian", "Silurian"),
    (443.8, 485.4, "Ordovician", "Ordovician"),
    (485.4, 538.8, "Cambrian", "Cambrian"),
    (538.8, 635.0, "Ediacaran", "Neoproterozoic"),
    (635.0, 720.0, "Cryogenian", "Neoproterozoic"),
    (720.0, 1000.0, "Tonian", "Neoproterozoic"),
]

def period_for(age):
    a = abs(age)
    for lo, hi, ep, per in PERIODS:
        if lo <= a < hi:
            return ep, per
    return "—", "—"

# ---- eustatic sea level (m vs present), Haq/Hallam-style, for readout ------
SEALEVEL = [
    (0, 0), (20, 40), (40, 80), (66, 110), (80, 250), (90, 240), (100, 200),
    (120, 150), (145, 110), (160, 90), (200, 60), (230, 40), (250, 20),
    (270, -20), (300, -40), (340, 60), (360, 90), (400, 140), (420, 160),
    (445, 200), (460, 220), (480, 180), (500, 120), (540, 60),
    (600, 30), (700, -10), (850, 40), (1000, 30),
    (-30, -10), (-70, 20), (-120, 60), (-170, 30), (-250, -20),
]
def sealevel_for(age):
    pts = [p for p in SEALEVEL if (p[0] <= 0) == (age <= 0)] or SEALEVEL
    pts = sorted(pts, key=lambda p: p[0])
    ages = [p[0] for p in pts]
    if age <= ages[0]: return pts[0][1]
    if age >= ages[-1]: return pts[-1][1]
    for i in range(len(pts) - 1):
        a0, a1 = ages[i], ages[i+1]
        if a0 <= age <= a1:
            t = (age - a0) / (a1 - a0 + 1e-9)
            return round(pts[i][1] * (1 - t) + pts[i+1][1] * t)
    return 0

# ---- index available DEMs by age ------------------------------------------
def index_dems():
    idx = {}
    for f in glob.glob(os.path.join(DEM_DIR, "**", "*.nc"), recursive=True):
        m = re.search(r"_([0-9]+(?:\.[0-9]+)?)Ma", os.path.basename(f))
        if m:
            idx[float(m.group(1))] = f
    return idx

def read_dem(f):
    """Return the grid with latitude ASCENDING (row 0 = south pole).

    The Zenodo sets disagree: the 1-degree files store latitude ascending,
    the 6-minute files store it descending (north first). render() assumes
    ascending and flips once, so normalise here or the map comes out
    upside down.
    """
    ds = netCDF4.Dataset(f)
    v = "z" if "z" in ds.variables else list(ds.variables.keys())[-1]
    z = np.asarray(ds.variables[v][:], dtype=np.float32)
    latname = "lat" if "lat" in ds.variables else "latitude"
    lat = np.asarray(ds.variables[latname][:])
    if lat[0] > lat[-1]:          # descending (north first) -> flip to ascending
        z = z[::-1]
    return z

def main():
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    # Every 5 Myr, matching the native spacing of the PALEOMAP series. Plate
    # motion is only a few degrees per step at this cadence, so consecutive
    # frames cross-fade as motion rather than as a visible cut.
    targets = list(range(0, 541, 5))
    manifest = []
    for age in targets:
        # nearest available DEM
        near = float(avail[np.argmin(np.abs(avail - age))])
        f = idx[near]
        z = read_dem(f)
        img, _ = render_u8(z, age, out_h=OUT_H, out_w=OUT_W)
        fn = f"phan_{age:04d}.webp"
        Image.fromarray(img).save(os.path.join(OUT_DIR, fn), "WEBP", quality=WEBP_Q, method=5)
        ep, per = period_for(age)
        manifest.append({"age": age, "file": fn, "epoch": ep, "period": per,
                         "sealevel": sealevel_for(age), "src_age": near})
        sz = os.path.getsize(os.path.join(OUT_DIR, fn)) // 1024
        print(f"  {age:4d} Ma  <- {near:6.1f}Ma  {ep:16s} {sz}KB")
    json.dump(manifest, open(os.path.join(OUT_DIR, "manifest_phan.json"), "w"), indent=0)
    total = sum(os.path.getsize(os.path.join(OUT_DIR, m["file"])) for m in manifest)
    print(f"Phanerozoic: {len(manifest)} frames, {total/1e6:.2f} MB")

if __name__ == "__main__":
    main()
