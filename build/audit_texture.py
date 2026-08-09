"""Is our land texture ORGANISED like the real Earth's, or just noisy?

The standing brief is Google-Earth equivalence, and for land texture that had
never been a number -- only an impression, which is how three false defects got
chased this month. This measures both halves of it against NASA's Blue Marble,
which ships in the repo already and is public domain:

    high-pass sigma    how much texture there is
    tiled coherence    how DIRECTIONAL it is, averaged over 32 px tiles so a
                       range curving through the frame is not penalised for
                       curving (the global form of this measure is dominated by
                       whether one orientation happens to fill the crop)

Real terrain is organised: ridges run in lines, dunes comb, drainage is
dendritic. Isotropic noise has coherence near zero however much of it there is,
and that is the difference between texture and landform.

WHAT THIS REFERENCE IS AND IS NOT, because it was over-read once already.
Blue Marble is a TRUE-COLOUR COMPOSITE and it carries essentially no hillshade:
measured, the correlation between its luminance structure and the actual relief
in the same box is +0.29, and the Andes -- second-highest relief of five test
boxes -- show the second-LOWEST luminance variation. Our render is albedo TIMES
shading. So:

  * CHROMA is a fair comparison. Both sides are albedo colour, and the finding
    that our biome chroma ran twice the Earth's (iteration 81) stands.
  * LUMINANCE AMPLITUDE is NOT. Comparing a shaded render against an unshaded
    photograph will always show us carrying more, most obviously where the real
    albedo is uniform -- which is exactly the "Africa at 231% of reference"
    claim of iteration 80, and it is withdrawn.
  * COHERENCE, which is what this script reports, sits in between and should be
    read as indicative. It is scale-free and both images do show
    terrain-organised pattern, but one organises albedo and the other organises
    shading, so the 60% figure is a useful direction and not a calibrated debt.

Measured at the time of writing:

    region              Blue Marble        ours
    Siberia             0.347 / 25.1       0.117 / 21.9
    Sahara              0.240 /  8.7       0.125 / 17.7
    N American interior 0.220 / 22.4       0.112 / 21.1

So the amplitude is roughly right and the ORGANISATION is two to three times
too low -- except in desert, where we draw twice the texture the real thing has.

    ../venv/bin/python audit_texture.py        # after shooting the ref framings
"""
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
BM = os.path.join(HERE, "..", "data", "bluemarble.jpg")
VERIFY = os.path.join(HERE, "verify")

# (our shot name, blue-marble lon, lat, box degrees, label)
PAIRS = [
    ("rf_sib", 100.0, 62.0, 30.0, "Siberia"),
    ("rf_sah", 15.0, 23.0, 30.0, "Sahara"),
    ("rf_prairie", -98.0, 42.0, 30.0, "N American interior"),
]


def stats(g, tile=32):
    """High-pass amplitude, and how directional it is per tile."""
    small = (max(g.shape[1] // 8, 2), max(g.shape[0] // 8, 2))
    lo = np.array(Image.fromarray(g).resize(small, Image.BILINEAR)
                  .resize((g.shape[1], g.shape[0]), Image.BILINEAR))
    hp = g - lo
    vals = []
    for r in range(0, hp.shape[0] - tile, tile):
        for c in range(0, hp.shape[1] - tile, tile):
            b = hp[r:r + tile, c:c + tile]
            gy, gx = np.gradient(b)
            jxx, jyy, jxy = (gx * gx).mean(), (gy * gy).mean(), (gx * gy).mean()
            if jxx + jyy > 1e-6:
                vals.append(np.sqrt(max((jxx - jyy) ** 2 + 4 * jxy * jxy, 0))
                            / (jxx + jyy))
    return float(hp.std()), (float(np.mean(vals)) if vals else float("nan"))


def main():
    if not os.path.exists(BM):
        print("  audit_texture: no data/bluemarble.jpg to compare against")
        return 1
    B = np.asarray(Image.open(BM).convert("RGB")).astype(float).mean(axis=2)
    H, W = B.shape
    missing = [n for n, *_ in PAIRS
               if not os.path.exists(os.path.join(VERIFY, n + ".png"))]
    if missing:
        print("  audit_texture: shoot the reference framings first -- missing %s"
              % ", ".join(missing))
        return 1

    print("  land texture against Blue Marble (%.1f km/px):" % (40075.0 / W))
    print("    %-22s %-20s %-20s" % ("region", "reference sig/coh", "ours sig/coh"))
    ratios = []
    for name, lon, lat, span, label in PAIRS:
        r0 = int((90 - lat - span / 2) / 180 * H)
        r1 = int((90 - lat + span / 2) / 180 * H)
        c0 = int((lon - span / 2 + 180) / 360 * W)
        c1 = int((lon + span / 2 + 180) / 360 * W)
        bs, bc = stats(B[r0:r1, c0:c1])
        a = np.asarray(Image.open(os.path.join(VERIFY, name + ".png"))
                       .convert("L")).astype(float)
        g = a[a.shape[0] // 4:3 * a.shape[0] // 4,
              a.shape[1] // 4:3 * a.shape[1] // 4]
        os_, oc = stats(g)
        ratios.append(oc / bc if bc else 0.0)
        print("    %-22s %6.2f / %.3f        %6.2f / %.3f    organisation %3.0f%% of real"
              % (label, bs, bc, os_, oc, 100 * oc / bc if bc else 0))
    print("  MEAN ORGANISATION: %.0f%% of the real Earth's"
          % (100 * float(np.mean(ratios))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
