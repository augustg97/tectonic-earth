"""Measure how much ice the app actually draws, keyframe by keyframe.

The ice model is spread across three places -- the climate table's ice lines,
`render.glaciation()` turning those into thresholds, and the GLSL that applies
them -- and nothing has ever checked what comes out the far end against what the
literature says was there. "Looks about right on the globe" is not a measurement:
ice at the pole is squeezed to nothing in the map projection and exaggerated on
the globe's limb, so the eye is the worst available instrument for this.

So this replicates the shader's ice arithmetic on the shipped textures and
integrates it properly, weighting every cell by cos(latitude). It reports, per
keyframe:

    land ice   % of land area, and Mkm^2
    glacier    % of land carrying mountain ice above the ELA
    sea ice    % of ocean area

against a target table assembled from the literature. The fbm lobe/tongue noise
is left out: it is zero-mean and shifts a margin either way by a degree or two,
which does not move an area integral.

    ../venv/bin/python ice_audit.py            # every keyframe with a target
    ../venv/bin/python ice_audit.py --all      # every keyframe
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

from climate import climate_at

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
Z_RANGE = 8000.0
RF_MAX = 1.3
TEMP_REF = -0.55
EARTH = 5.101e8      # km^2, total surface

# What the record says, as a fraction of LAND area covered by ice sheets.
# Ranges, not points: ice volume in deep time is reconstructed from sea-level
# fall and the extent of glacial deposits, and both are loose.
TARGETS = {
    0: (0.08, 0.13, "Antarctica 13.9 + Greenland 1.8 Mkm2 of ~149 Mkm2 land"),
    5: (0.08, 0.13, "late Pliocene, both sheets established"),
    15: (0.06, 0.11, "mid-Miocene, EAIS only, no substantial NH sheet"),
    25: (0.05, 0.10, "late Oligocene, EAIS waxing and waning"),
    34: (0.03, 0.09, "Eocene-Oligocene: EAIS grows in <100 kyr"),
    40: (0.00, 0.02, "late Eocene, near ice-free"),
    50: (0.00, 0.01, "early Eocene hothouse"),
    90: (0.00, 0.01, "mid-Cretaceous hothouse, no ice at either pole"),
    145: (0.00, 0.03, "J-K cool snap; possible small polar ice"),
    200: (0.00, 0.01, "Tr-J, ice-free"),
    260: (0.01, 0.06, "LPIA waning; Gondwana ice retreating to Australia"),
    280: (0.03, 0.10, "early Permian, last Gondwana sheets"),
    300: (0.10, 0.22, "LPIA peak -- ice volume at or above LGM"),
    315: (0.10, 0.22, "LPIA peak"),
    330: (0.02, 0.09, "mid-Carboniferous, ice building"),
    360: (0.01, 0.07, "late Famennian glaciation, high-latitude Gondwana"),
    445: (0.05, 0.16, "Hirnantian: Gondwana sheet, ~100 m of sea-level fall"),
    460: (0.00, 0.03, "Ordovician warm"),
    570: (0.02, 0.10, "late Ediacaran cool interval"),
    637: (0.55, 1.00, "Marinoan snowball"),
    665: (0.55, 1.00, "Sturtian snowball"),
    690: (0.70, 1.00, "Sturtian deepest -- ice reaching the tropics"),
    721: (0.01, 0.08, "pre-Sturtian, Franklin LIP erupting"),
    750: (0.00, 0.01, "Rodinia rifting, warm"),
    -100: (0.00, 0.01, "future: ice caps gone by ~+70 Myr"),
    -250: (0.00, 0.01, "Pangaea Proxima, hot"),
}


def _field(name):
    p = os.path.join(FIELDS, name)
    if not os.path.exists(p):
        return None
    return np.asarray(Image.open(p).convert("L"), np.float32) / 255.0


def _resize(a, H, W):
    """Nearest-neighbour to a common grid -- an area integral does not need
    bilinear, and this keeps the audit cheap enough to run over 251 keyframes."""
    yi = (np.linspace(0, a.shape[0] - 1, H)).astype(int)
    xi = (np.linspace(0, a.shape[1] - 1, W)).astype(int)
    return a[yi][:, xi]


def fields(base, H=512, W=1024):
    e = _field(base + "_e.avif")
    if e is None:
        return None, None
    s = 2.0 * _resize(e, H, W) - 1.0
    z = np.sign(s) * s * s * Z_RANGE
    r = _field(base + "_r.webp")
    rf = _resize(r, H, W) * RF_MAX if r is not None else np.full((H, W), 0.5)
    return z, rf


LAND_RAMP = 6.0
SEA_RAMP = 4.5
MARGIN_W = 3.2
LOBE_AMP = 0.0      # audit runs noise-free; the app perturbs the margin


def ice_masks(z, rf, age, iceT, seaT, lobe=0.0):
    """The shader's ice arithmetic, minus the zero-mean noise.

    Kept deliberately literal -- same constants, same order -- so that a change
    to the GLSL and a change here can be checked against each other.
    """
    H, W = z.shape
    lat = np.linspace(90, -90, H)[:, None] * np.ones((1, W))
    s2 = np.sin(np.radians(lat)) ** 2
    temp = climate_at(age)["temp"]
    zp = np.clip(z, 0, None)
    base = (26.0 - 24.0 * s2 - 26.0 * s2 ** 3) + (temp - TEMP_REF) * (4.0 + 15.0 * s2)
    T = base - zp * 0.0058

    land = z >= 0.0
    # There is no accumulation term here any more. One was added -- a swing of
    # the threshold with local rainfall, on the reasoning that a polar desert
    # glaciates reluctantly -- and it made the ice WORSE. Polar rainfall in
    # these fields is both tiny and noisy (medians 0.005 to 0.04), so the term
    # did not separate dry interiors from wet margins; it jittered the
    # threshold by a couple of degrees from cell to neighbouring cell and broke
    # the ice into patches. The effect it was reaching for is real but it is
    # the size of the Dry Valleys, which a 20 km grid cannot resolve anyway.
    ice_thr = iceT
    # Ragged margins, solid interiors. The lobe noise used to be added to the
    # temperature everywhere, and at +-1.7 C against a 4.5 C ramp it was wide
    # enough to punch holes clean through ground that should be solid ice --
    # which is why the ice looked splotchy and why low polar ground came out
    # bare while the mountains beside it were white. Scale it by how close the
    # cell is to its own threshold instead, so it frays the edge and leaves
    # the middle alone.
    dT = ice_thr - T
    near = np.exp(-(dT * dT) / (2.0 * MARGIN_W * MARGIN_W))
    land_ice = np.clip((dT + lobe * near) / LAND_RAMP, 0, 1) * land
    # Sea ice is PACK ice -- a thin skin, not a sheet -- and it forms more
    # readily than an ice sheet does, not less. Where the water is shallow
    # enough for a sheet to ground on it, the land threshold applies instead:
    # that is the real land/ocean asymmetry, and it is about thickness and
    # what the ice is sitting on, not about the ocean resisting freezing.
    shelf = np.clip((z + 2400.0) / 2250.0, 0, 1) * (~land)
    sea_thr = seaT + (ice_thr - seaT) * shelf
    dS = sea_thr - T
    nearS = np.exp(-(dS * dS) / (2.0 * MARGIN_W * MARGIN_W))
    sea_ice = np.clip((dS + lobe * nearS * 1.6) / SEA_RAMP, 0, 1) * (~land)

    arid = 1.0 - np.clip(rf / 0.85, 0, 1)
    ela = np.clip((base - (-5.0 - 7.0 * arid)) / 0.0058, 300.0, 6200.0)
    glac = np.clip((zp - ela) / 520.0 + 0.08, 0, 1) * land
    snowfall = np.clip(0.30 + 0.70 * np.clip((rf - 0.04) / 0.38, 0, 1), 0, 1)
    snow = np.maximum(np.clip((zp - (ela - 380.0)) / 400.0, 0, 1) * snowfall, glac)
    return land, land_ice, sea_ice, glac, snow, T


def measure(base, age, iceT, seaT):
    z, rf = fields(base)
    if z is None:
        return None
    land, li, si, gl, sn, T = ice_masks(z, rf, age, iceT, seaT)
    H, W = z.shape
    lat = np.linspace(90, -90, H)[:, None] * np.ones((1, W))
    wgt = np.cos(np.radians(lat))
    tot = wgt.sum()
    land_a = (wgt * land).sum()
    sea_a = tot - land_a
    f = lambda m: float((wgt * m).sum())
    return {
        "land_frac": land_a / tot,
        "ice_of_land": f(li) / land_a if land_a else 0.0,
        "glac_of_land": f(np.maximum(gl - li, 0)) / land_a if land_a else 0.0,
        "snow_of_land": f(np.maximum(sn - li, 0)) / land_a if land_a else 0.0,
        "seaice_of_sea": f(si) / sea_a if sea_a else 0.0,
        "ice_Mkm2": f(li) / tot * EARTH / 1e6,
        "land_Mkm2": land_a / tot * EARTH / 1e6,
    }


def main():
    man = json.load(open(os.path.join(FIELDS, "manifest.json")))
    by_age = {m["age"]: m for m in man}
    show_all = "--all" in sys.argv
    ages = sorted(by_age) if show_all else sorted(a for a in by_age if a in TARGETS)

    print(f"{'age':>6} {'iceT':>6} {'land':>6} {'ICE %land':>10} {'target':>12} "
          f"{'Mkm2':>7} {'glac':>6} {'snow':>6} {'seaice':>7}  verdict")
    bad = []
    for age in ages:
        rec = by_age[age]
        base = ("fut_%04d" % abs(age)) if age < 0 else (
            "pre_%04d" % age if age > 540 else "phan_%04d" % age)
        m = measure(base, age, rec["iceT"], rec["seaT"])
        if m is None:
            continue
        tgt = TARGETS.get(age)
        verdict, tstr = "", ""
        if tgt:
            lo, hi, _ = tgt
            tstr = f"{lo*100:.0f}-{hi*100:.0f}%"
            v = m["ice_of_land"]
            if v < lo * 0.999:
                verdict = f"TOO LITTLE ({v/max(lo,1e-9):.2f}x low bound)"
                bad.append((age, "low", v, lo, hi))
            elif v > hi * 1.001:
                verdict = f"TOO MUCH ({v/max(hi,1e-9):.2f}x high bound)"
                bad.append((age, "high", v, lo, hi))
            else:
                verdict = "ok"
        print(f"{age:6d} {rec['iceT']:6.1f} {m['land_frac']*100:5.0f}% "
              f"{m['ice_of_land']*100:9.1f}% {tstr:>12} {m['ice_Mkm2']:7.1f} "
              f"{m['glac_of_land']*100:5.1f}% {m['snow_of_land']*100:5.1f}% {m['seaice_of_sea']*100:6.1f}%  {verdict}")
    print(f"\n{len(bad)} of {len([a for a in ages if a in TARGETS])} checked "
          f"keyframes fall outside the literature range")
    for age, how, v, lo, hi in bad:
        print(f"  {age:>5} Ma  {how:4s}  {v*100:5.1f}%  vs {lo*100:.0f}-{hi*100:.0f}%"
              f"   {TARGETS[age][2]}")


if __name__ == "__main__":
    main()
