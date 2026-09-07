"""Compare two verification frames: mean absolute RGB difference and the share
of pixels that moved, over the whole image or a crop.

    ../venv/bin/python verify_diff.py A.png B.png [--crop x0,y0,x1,y1] [--out diff.png]

Two uses in the Atlas port (2026-09-07): the terrain-preservation check
(old-page against new-page cloud-off frames at one framing must be near
zero; the harness itself differs by up to ~0.85/255 mean between two renders
of one page under contention, README 7.16) and the cloud-motion check (two
frames of one camera some seconds apart must differ where the clouds are).
Prints its numbers unconditionally: a comparison that only speaks when it
fails cannot be read when it passes.
"""
import sys

import numpy as np
from PIL import Image


def load(p, crop=None):
    im = Image.open(p).convert("RGB")
    if crop:
        im = im.crop(crop)
    return np.asarray(im).astype(np.float32)


def main():
    args = sys.argv[1:]
    crop = None
    out = None
    if "--crop" in args:
        i = args.index("--crop")
        crop = tuple(int(v) for v in args[i + 1].split(","))
        del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        return 2
    a, b = load(args[0], crop), load(args[1], crop)
    if a.shape != b.shape:
        print("verify_diff: shapes differ %s vs %s" % (a.shape, b.shape))
        return 1
    d = np.abs(a - b)
    mean = d.mean(axis=(0, 1))
    moved = (d.max(axis=2) > 8).mean() * 100
    moved40 = (d.max(axis=2) > 40).mean() * 100
    print("verify_diff: %s vs %s%s" % (args[0].split("/")[-1], args[1].split("/")[-1],
                                       " crop %s" % (crop,) if crop else ""))
    print("  mean |dRGB| = %.2f / %.2f / %.2f  (of 255)   pixels moved >8: %.1f%%   >40: %.1f%%"
          % (mean[0], mean[1], mean[2], moved, moved40))
    if out:
        Image.fromarray(np.clip(d * 4, 0, 255).astype(np.uint8)).save(out)
        print("  difference image (x4) -> %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
