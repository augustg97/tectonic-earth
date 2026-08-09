"""Hunt axis-aligned seams -- the artefact you cannot see until you can.

A seam is a single column or row where the image changes far more than its
neighbours do: a texture wrap, a branch threshold crossing on a lat/lon
boundary, a field edge. It is invisible to every metric used so far, because
whole-frame statistics average it away -- one bad column in 760 moves a mean by
nothing at all.

The detector: take the mean absolute gradient down each column and across each
row, high-pass it against a local median, and report any line standing more than
N sigma above its neighbourhood. Reported in the units that matter -- how many
times the typical line's gradient the worst line carries.

Task 23 ("find and fix the ocean-fabric rectangular seam") has been open since
the first week and was never reproduced by looking.

    ../venv/bin/python audit_seam.py PREFIX [PREFIX...]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify")


def lines(g, axis):
    """Mean |gradient| per column (axis=0) or row (axis=1), and its local excess."""
    gy, gx = np.gradient(g)
    m = np.hypot(gx, gy)
    prof = m.mean(axis=axis)
    # local median over 21 lines: a seam is narrow, the background is not
    k = 21
    pad = np.r_[prof[:k][::-1], prof, prof[-k:][::-1]]
    med = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(len(prof))])
    resid = prof - med
    sd = np.median(np.abs(resid - np.median(resid))) * 1.4826
    return prof, med, resid / max(sd, 1e-9)


def main():
    names = sys.argv[1:]
    if not names:
        print(__doc__)
        return 2
    worst = []
    for n in names:
        p = os.path.join(VERIFY, n + ".png")
        if not os.path.exists(p):
            print("  %-16s (no shot)" % n)
            continue
        g = np.asarray(Image.open(p).convert("L")).astype(float)
        # Trim generously. The globe limb is a real discontinuity and so is the
        # terminator, and both live near the frame edge -- the first run flagged
        # row 0 twice, which is the trim boundary and not a seam.
        g = g[90:-90, 90:-90]
        out = []
        for axis, what in ((0, "column"), (1, "row")):
            prof, med, z = lines(g, axis)
            i = int(np.argmax(z))
            out.append((float(z[i]), what, i, float(prof[i] / max(med[i], 1e-9))))
        out.sort(reverse=True)
        zmax, what, idx, ratio = out[0]
        # A seam is NARROW and STRONG. Sigma alone flags any broad gradient
        # ramp; require the line to carry a real multiple of its neighbours'
        # gradient as well, which a coastline or a terminator does not.
        flag = "   <-- SEAM" if (zmax > 8.0 and ratio > 2.0) else ""
        print("  %-16s worst %-6s %3d   %5.1f sigma above neighbours, %.2fx their gradient%s"
              % (n, what, idx, zmax, ratio, flag))
        worst.append((zmax, n))
    if worst:
        worst.sort(reverse=True)
        print("  worst overall: %s at %.1f sigma  (seam needs BOTH >8 sigma and >2x)"
              % (worst[0][1], worst[0][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
