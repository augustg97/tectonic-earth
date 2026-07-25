"""Fuse the surveyed and modelled age grids, and derive what the sea floor needs.

Two sources with different standing (see realage.py and crustage.py): surveyed
crust where it survives, modelled isochrons everywhere else. They disagree --
correlation 0.41 -- so simply preferring one where it exists would put a step of
tens of Myr along the edge of the surveyed region, and since depth goes as the
square root of age that step would draw itself across the sea floor as a visible
wall.

So blend in the GRADIENT DOMAIN instead of the value domain. Take the difference
between the two where both exist, spread that difference smoothly into the
region where only the model exists, and add it back. The result equals the
surveyed grid exactly where the surveyed grid is trustworthy, follows the
model's structure where it is not, and has no seam anywhere -- the correction is
smooth by construction, so it moves the modelled ages without disturbing their
relative arrangement, which is the part of the model actually worth keeping.

Three fields come out, and between them they replace distance-to-ridge:

  AGE          the coordinate everything is keyed to. Its gradient is
               1/(spreading rate) and does not decay with range, which is what
               lets abyssal-hill spacing stay uniform from the axis to the
               trench, as it does in nature.
  AZIMUTH      the isochron tangent -- the direction the fabric runs. Correct
               everywhere, because it is the ridge as it WAS, frozen into the
               crust, rather than the ridge as it is now.
  FRACTURE     age offset measured ALONG the isochron. That is precisely what a
               fracture zone is: two pieces of crust of different ages side by
               side, separated by a flowline-parallel scar. Derived rather than
               drawn, and it works for surveyed and modelled crust alike.
"""
import os

import numpy as np

import crustage
import realage

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "ocean")

MAX_AGE = 200.0


def _spread(diff, mask, sigma=14.0, rounds=3):
    """Carry a correction from where it is known into where it is not.

    Normalised convolution: blur the masked values and the mask together and
    divide, which extends the field outward without letting the empty region
    pull it toward zero. Repeated at shrinking radius so the near field follows
    the data closely and the far field stays smooth.
    """
    from scipy.ndimage import gaussian_filter
    v = np.where(mask, diff, 0.0).astype(np.float64)
    m = mask.astype(np.float64)
    out = np.zeros_like(v)
    for k in range(rounds):
        s = sigma / (1.6 ** k)
        # wrap in longitude, reflect in latitude -- the grid is a sphere in x only
        num = gaussian_filter(v, s, mode=("reflect", "wrap"))
        den = gaussian_filter(m, s, mode=("reflect", "wrap"))
        est = np.where(den > 1e-4, num / np.maximum(den, 1e-9), 0.0)
        out = np.where(den > 1e-4, est, out)
    return np.where(mask, diff, out)


def fuse(T, h=512, w=1024):
    """(age, azimuth_deg, fz, surveyed) for time T."""
    from scipy.ndimage import gaussian_filter
    model, arc, dst, pid = crustage.cached(T, h, w)
    if T >= 0:
        surv, ok = realage.cached(T, h, w)
    else:
        surv, ok = np.full((h, w), np.nan, np.float32), np.zeros((h, w), bool)

    model = np.where(np.isfinite(model), model, MAX_AGE).astype(np.float64)
    both = ok & np.isfinite(surv)
    if both.sum() > 256:
        age = model + _spread(np.where(both, surv - model, 0.0), both)
        age = np.where(both, surv, age)
    else:
        age = model
    age = np.clip(age, 0.0, MAX_AGE).astype(np.float32)

    # --- isochron direction, from the age gradient -----------------------
    # Smoothed first: the gradient of a nearest-neighbour field is dominated by
    # its own cell boundaries, which are an artefact of the search and not a
    # property of the crust.
    sm = gaussian_filter(age.astype(np.float64), 1.6, mode=("reflect", "wrap"))
    lat1d = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    coslat = np.clip(np.cos(np.radians(lat1d)), 0.08, 1.0)[:, None]
    gy, gx = np.gradient(sm)
    ge, gn = gx / coslat, -gy                 # spreading direction: age increases away
    mag = np.hypot(ge, gn) + 1e-9
    # the fabric runs at right angles to the age gradient
    azi = np.degrees(np.arctan2(ge / mag, -gn / mag)).astype(np.float32)

    # --- fracture zones: age offset ALONG the isochron -------------------
    # Project the age gradient onto the isochron direction. On ordinary crust
    # age barely changes along an isochron, so this is ~0; across a fracture
    # zone two ages sit side by side and it spikes. Because it is measured on
    # the fused age field it works for surveyed and modelled crust alike, and
    # because age travels with the crust the trace persists -- which is what
    # makes real fracture zones thousands of km long.
    # It has to be measured over a FINITE offset, not as a derivative: the
    # tangential component of a gradient is identically zero, so projecting one
    # onto the other returns nothing at all. A fracture zone is a step, and a
    # step is only visible across a baseline wide enough to straddle it.
    from scipy.ndimage import map_coordinates
    tx, ty = -gn / mag, ge / mag              # unit vector along the isochron
    dpc = 180.0 / h
    L = 0.9                                    # deg: wide enough to straddle a scar
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    dcol = L * tx / coslat / dpc
    drow = -L * ty / dpc
    def samp(sgn):
        c = (xx + sgn * dcol) % w
        r = np.clip(yy + sgn * drow, 0, h - 1)
        return map_coordinates(age.astype(np.float64), [r, c], order=1, mode="nearest")
    jump = np.abs(samp(1) - samp(-1))
    # Scale against how fast age changes ACROSS the isochron over the same
    # baseline -- on ordinary crust the two are comparable, on a fracture zone
    # the along-isochron jump is far larger, so the ratio isolates the scar
    # without needing an absolute threshold that would drift between eras.
    across = np.abs(mag) * 2.0 * L + 1e-6
    fz = np.clip(jump / (2.5 * across) - 0.35, 0.0, 1.0)
    fz = gaussian_filter(fz, 0.9, mode=("reflect", "wrap")).astype(np.float32)

    return age, azi, fz, both


def cached(T, h=512, w=1024):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"ocn_{int(round(T)):05d}_{h}x{w}.npz")
    if os.path.exists(f):
        z = np.load(f)
        return z["age"], z["azi"], z["fz"], z["surveyed"]
    a, az, fz, sv = fuse(T, h, w)
    np.savez_compressed(f, age=a, azi=az, fz=fz, surveyed=sv)
    return a, az, fz, sv


if __name__ == "__main__":
    import sys, math
    from PIL import Image
    SP = ("/private/tmp/claude-501/-Users-augustgweon-Tectonic-Plate-Model/"
          "724fe10f-3191-46ee-9599-28adbf4259f2/scratchpad")
    for T in [float(x) for x in (sys.argv[1:] or ["0", "60", "300"])]:
        age, azi, fz, sv = fuse(T)
        print(f"T={T:.0f} Ma  surveyed {100*sv.mean():.0f}%  "
              f"age {age.min():.0f}..{age.max():.0f} mean {age.mean():.0f}  "
              f"fz>0.5 on {100*(fz>0.5).mean():.1f}% of cells")
        v = np.clip(age / MAX_AGE, 0, 1)
        rgb = np.stack([np.clip(1.5 - 2.0 * v, 0, 1),
                        np.clip(1.15 - abs(v - 0.5) * 2.3, 0, 1),
                        np.clip(0.2 + 1.5 * v, 0, 1)], -1)
        rgb *= (0.80 + 0.20 * (np.sin(age * math.pi / 10.0) > 0))[..., None]
        rgb *= (1.0 - 0.75 * fz)[..., None]          # fracture zones as dark scars
        Image.fromarray((rgb * 255).astype(np.uint8)).save(f"{SP}/fused_{int(T)}.png")
        print(f"  wrote fused_{int(T)}.png")
