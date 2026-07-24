"""Rewrite ONLY the elevation (_e) and the new ocean-structure (_o) fields for
every keyframe, re-applying the redesigned seafloor.py.

The seafloor change touches only what is baked into the bathymetry and the new
_o field the shader grows abyssal hills from; rainfall (_r), motion (_m), lakes
(_w) and surface-process (_d) do not depend on it, so this reproduces each
keyframe's pre-seafloor elevation exactly as build_fields.main() would (same
helpers, same inputs) and re-exports just those two textures. Far cheaper than
re-running the climate solve for ~250 keyframes, and identical in result.

Run from the build/ directory with the project venv:  ../venv/bin/python reskin_seafloor.py
Set ONLY_AGE=<n> to reskin a single Phanerozoic keyframe for a quick check.
"""
import os, sys
import numpy as np
from PIL import Image
import build_fields as bf
import paleo_tracks

OUT = bf.OUT
ELEV_H, ELEV_W = bf.ELEV_H, bf.ELEV_W
OCEAN_H, OCEAN_W = bf.OCEAN_H, bf.OCEAN_W
STEP = bf.STEP


def save_eo(age, tag, Zhi):
    mot = bf._load_motion(age, tag)
    Z2, ofield = bf.SF.apply(Zhi, age, reconstructor=bf._sf_reconstructor(), motion=mot)
    e = bf._gray(bf.enc_elev(bf.smooth_bathymetry(Z2)))
    o = Image.fromarray((np.clip(ofield, 0, 1) * 255 + 0.5).astype(np.uint8)
                        ).resize((OCEAN_W, OCEAN_H), Image.BILINEAR)
    bf._save(e, os.path.join(OUT, f"{tag}_{abs(age):04d}_e.webp"), bf.ELEV_Q)
    bf._save(o, os.path.join(OUT, f"{tag}_{abs(age):04d}_o.webp"), bf.OCEAN_Q)
    return mot is not None


idx = bf.index_dems()
avail = np.array(sorted(idx.keys()))


def dem_for(age):
    near = float(avail[np.argmin(np.abs(avail - age))])
    return bf.read_dem(idx[near])


rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
only = os.environ.get("ONLY_AGE")

# ---- Phanerozoic (0..540) ----
n = withmot = 0
for age in range(0, 541, STEP):
    if only is not None and age != int(only):
        continue
    z = dem_for(age)
    Zhi = bf.resample_dem(z, ELEV_H, ELEV_W)
    Zhi = bf.EP.carve(Zhi, age, rec)
    withmot += save_eo(age, "phan", Zhi)
    n += 1
print(f"phanerozoic: {n} keyframes reskinned ({withmot} had motion)")

if only is not None:
    print("ONLY_AGE set -> stopping after the single keyframe")
    sys.exit(0)

# ---- Future (-5..-250): plate-warped present DEM ----
gid = bf.rasterise_groups()
Zsrc = bf.resample_dem(dem_for(0), 900, 1800)
nf = 0
for age in range(-STEP, -251, -STEP):
    frac = abs(age) / 250.0
    gh = bf.future_grid(frac, gid, Zsrc, ELEV_H, ELEV_W)
    gh = gh - bf.sealevel_for(age)
    save_eo(age, "fut", gh)
    nf += 1
print(f"future: {nf} keyframes reskinned")

# ---- Precambrian (545..1000): anchored to 540 Ma ----
A_hi = bf.resample_dem(dem_for(540), ELEV_H, ELEV_W)
npre = 0
for age in range(540 + STEP, 1001, STEP):
    hi = bf.PRE.precambrian_grid(age, tw=ELEV_W, th=ELEV_H, flood=140.0)
    wq = float(np.clip((age - 540.0) / 60.0, 0, 1))
    hi = bf.handoff_blend(A_hi, hi, wq)
    save_eo(age, "pre", hi)
    npre += 1
print(f"precambrian: {npre} keyframes reskinned")
print("done")
