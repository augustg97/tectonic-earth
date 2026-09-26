"""Bake fut_XXXX_p.webp + future entries in platerot.json -- the crust's own
coordinate frame (H2) for the future series.

The future frames shipped no material-coordinate field, so uMat stayed 0 past
the present: every ridge, crest and valley was evaluated at a pure function of
POSITION, and a continent slid out from under its own texture as it drifted --
exactly the defect H2 was built to remove, still alive in the future era.

The rotation is exact. Each group turns about ONE axis by an angle proportional
to frac, so "the plate's rotation from 0 Ma to this age" -- which is what
build_platefield stores for the Phanerozoic -- is simply (that axis,
frac x total angle). Consistency with the Phanerozoic definition is what makes
the shader's matDir() mean the same thing on both sides of the present.

Slots are group indices (ten groups against 48 slots), and cells no group
claims take their nearest claimed neighbour's slot, exactly as the Phanerozoic
bake assigns the microplate tail: unrotated patches would show as texture that
does not ride.
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

import build_fields as BF
import bake_future_v as BV

PW, PH = 1024, 512
SLOTS = 48
STEP = BF.STEP


def bake(age, gid=None, Zsrc=None, quiet=False):
    """Slots and rotations for one future keyframe, from future_tectonics (3.16).

    The slot is the plate that owns each cell (the engine's owner map); the
    rotation is the one the shader's matDir needs: from where the crust sits
    at this keyframe BACK TO TODAY, exactly what build_platefield stores for the
    past (age -> 0 Ma). Until 3.15 this stored the forward rotation (today ->
    keyframe), so every future texture moved the wrong way round its axis --
    at twice the plate's speed relative to the crust it belonged to.
    """
    import future_tectonics as FT
    t0 = time.time()
    myr = abs(age)
    _z, own, _src, _E, _cw = FT.render(myr, PH, PW, fray=True)
    miss = own < 0
    if miss.any() and (~miss).any():
        _, idx = distance_transform_edt(miss, return_indices=True)
        own = own[idx[0], idx[1]]
    elif miss.all():
        own = np.zeros_like(own)
    arr = np.zeros((PH, PW, 3), np.uint8)
    arr[:, :, 0] = np.clip(own, 0, SLOTS - 1).astype(np.uint8)
    path = os.path.join(BF.OUT, "fut_%04d_p.webp" % myr)
    Image.fromarray(arr).save(path, "WEBP", lossless=True, method=6)
    quats = []
    for p in FT.PLATES:
        r = FT.logm(FT.rot(p, myr).T)          # keyframe -> today
        ang = float(np.linalg.norm(r))
        if ang < 1e-9:
            quats.append([0.0, 0.0, 1.0, 0.0]); continue
        ax = r / ang
        quats.append([round(float(ax[0]), 6), round(float(ax[1]), 6),
                      round(float(ax[2]), 6), round(ang, 6)])
    while len(quats) < SLOTS:
        quats.append([0.0, 0.0, 1.0, 0.0])
    if not quiet:
        print("  %+5d Myr  slots used %2d  %5.1f kB  [%.0fs]"
              % (-myr, int(own.max()) + 1, os.path.getsize(path) / 1024.0,
                 time.time() - t0), flush=True)
    return quats


def main():
    t0 = time.time()
    ppath = os.path.join(BF.OUT, "..", "platerot.json")
    data = json.load(open(ppath))
    print("baking future material coordinates at %dx%d" % (PW, PH), flush=True)
    n = 0
    for age in range(-STEP, -251, -STEP):
        data["rot"][str(age)] = bake(age)
        n += 1
    json.dump(data, open(ppath, "w"), separators=(",", ":"))
    print("DONE %d fields + %d rotation tables in %.1f min"
          % (n, n, (time.time() - t0) / 60.0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
