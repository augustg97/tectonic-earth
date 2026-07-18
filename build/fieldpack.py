"""Pack/unpack the terrain+climate fields shipped to the web build.

One RGB texture per keyframe:
    R = elevation, signed-sqrt encoded so precision concentrates near sea level
        (the coastline is the one contour that must interpolate cleanly)
    G = rainfall   0 .. 1.3
    B = temperature -40 .. +45 C

The shader decodes these, interpolates between two keyframes, and derives
land/sea, biome, ice and hillshade per pixel.
"""
import numpy as np

Z_RANGE = 8000.0
RF_MAX = 1.3
T_LO, T_HI = -40.0, 45.0


def enc_elev(z):
    s = np.sign(z)
    return np.clip(0.5 + 0.5 * s * np.sqrt(np.clip(np.abs(z) / Z_RANGE, 0, 1)), 0, 1)


def dec_elev(e):
    d = e * 2.0 - 1.0
    return np.sign(d) * (d * d) * Z_RANGE


def pack(Z, Rf, T):
    """-> uint8 HxWx3"""
    r = enc_elev(Z)
    g = np.clip(Rf / RF_MAX, 0, 1)
    b = np.clip((T - T_LO) / (T_HI - T_LO), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255.0 + 0.5).astype(np.uint8)


def unpack(img):
    a = img.astype(float) / 255.0
    Z = dec_elev(a[..., 0])
    Rf = a[..., 1] * RF_MAX
    T = a[..., 2] * (T_HI - T_LO) + T_LO
    return Z, Rf, T
