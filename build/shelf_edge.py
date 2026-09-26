"""THE SHELF BREAK AS A DISTANCE (3.17): the blue channel of every `_w` field.

WHY. The ocean palette draws the continental shelf pale and the slope and abyss
dark, and the step between them -- the shelf break, where the floor falls from
~150 m to ~2,000 m over a few tens of km -- is the sharpest line in a real
ocean seen from orbit (the Bahamas against the Tongue of the Ocean, the Grand
Banks, the East China Sea). The shader could only draw it from the elevation
field's ~10 km texels, which carry +/-150 m of noise across exactly that depth
band, so a sharp threshold on the raw depth flickered into lace along every
margin; the fix was to threshold a depth smoothed over ~60 km, which traded the
lace for a soft halo ~100 km wide -- "the divide between deep sea floor and
shallower crust looks fuzzy".

WHAT. Per keyframe, the signed distance in km to the BREAK isobath of a
DENOISED bathymetry (median 3x3, then a light Gaussian), positive on the shelf
side, from exact distance transforms with the longitude spacing of each
latitude band, refined to sub-texel near the isobath by the linear estimate
(depth - BREAK) / |gradient|. A distance field interpolates smoothly, so the
shader can put a one-pixel antialiased edge on its zero at any zoom -- the
technique behind crisp text drawn from signed distance fields -- and the noise
never reaches the edge because the isobath came from the denoised field.

ENCODING. 1..255 over +/-RANGE_KM (0.31 km a level); 0 is reserved for "no
field", so a lake file baked before this reads as absent, not as open ocean.
"""
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, median_filter, zoom

BREAK = -180.0          # m: the isobath the shelf ends at
RANGE_KM = 40.0         # encoded +/- range
KM_PER_DEG = 111.2
WORK_W = 2048           # distance transforms at <= this width, then upsampled


def sdf_km(Z):
    """Signed distance (km) to the BREAK isobath of a denoised Z (h, w; row 0
    = north): positive on the shelf (and land) side, negative seaward."""
    h, w = Z.shape
    f = max(1, w // WORK_W)
    Zs = np.asarray(Z, np.float32)
    if f > 1:
        Zs = Zs[: h - h % f, : w - w % f].reshape(h // f, f, w // f, f).mean(axis=(1, 3))
    # (a rank filter takes one mode, so longitude is wrapped by hand)
    Zs = median_filter(np.concatenate([Zs[:, -2:], Zs, Zs[:, :2]], 1), size=3, mode="nearest")[:, 2:-2]
    Zs = gaussian_filter(Zs, 0.8, mode=("nearest", "wrap"))
    hh, ww = Zs.shape
    inside = Zs > BREAK
    dy = 180.0 / hh * KM_PER_DEG
    lat = 90.0 - (np.arange(hh) + 0.5) * 180.0 / hh
    din = np.zeros((hh, ww), np.float32)
    dout = np.zeros((hh, ww), np.float32)
    band, pad = 64, 48
    for b0 in range(0, hh, band):
        b1 = min(hh, b0 + band)
        y0, y1 = max(0, b0 - pad), min(hh, b1 + pad)
        lc = float(lat[(b0 + b1) // 2])
        dx = dy * max(np.cos(np.radians(lc)), 0.05)
        m3 = np.concatenate([inside[y0:y1]] * 3, 1)
        din[b0:b1] = distance_transform_edt(m3, sampling=(dy, dx))[b0 - y0:b1 - y0, ww:2 * ww]
        dout[b0:b1] = distance_transform_edt(~m3, sampling=(dy, dx))[b0 - y0:b1 - y0, ww:2 * ww]
    sdf = np.where(inside, din - 0.5 * dy, -(dout - 0.5 * dy))
    # sub-texel near the isobath: the linear estimate from the local gradient
    gy, gx = np.gradient(Zs)
    cl = np.maximum(np.cos(np.radians(lat)), 0.05)[:, None]
    g = np.hypot(gx / (dy * cl), gy / dy)                         # m per km
    lin = (Zs - BREAK) / np.maximum(g, 1.0)
    wgt = np.clip(1.0 - np.abs(sdf) / (2.0 * dy), 0.0, 1.0) * (g > 3.0)
    sdf = wgt * np.clip(lin, -2.0 * dy, 2.0 * dy) + (1.0 - wgt) * sdf
    sdf = np.clip(sdf, -RANGE_KM, RANGE_KM)
    if f > 1:
        sdf = zoom(sdf, (h / hh, w / ww), order=1, mode="grid-wrap")
    return sdf.astype(np.float32)


def channel(Z):
    """uint8 channel for `_w`.B: 1..255 over +/-RANGE_KM, 0 meaning no field."""
    s = sdf_km(Z)
    return np.clip(np.round(128.0 + s * (127.0 / RANGE_KM)), 1, 255).astype(np.uint8)
