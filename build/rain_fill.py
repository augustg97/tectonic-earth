"""THE SEA'S RAINFALL, FILLED FROM THE LAND (3.19).

Rainfall is defined only on land, and the field stored zero over the sea. Every
reader near a coast then mixed that zero in -- the texture's bilinear filter
(one texel is ~26 km), the shader's five-tap blur, and above all its moisture
warp, which moves a lookup up to ~10 degrees so biome edges wander -- and a wet
coast read as a dry one. The Atlantic coastal plain of the United States drew
as a 30-50 km orange strip of desert, the Sierra Leone coast (3 m of rain a
year) as a sandy band 150 km long, and every small island got a tan rim. It is
the fault "unmasked averages eat small land" names, at the scale of every
coastline, and the shader cannot undo it: bilinear interpolation happens inside
the texture unit, and the warp's reach is continental.

So the data carries a value everywhere. Land keeps its rainfall exactly; every
sea texel takes a smooth average of the land around it, by pull-push (a
normalised-convolution pyramid: pull weighted means down to a 3 x 6 grid, push
them back up, each level keeping what it knows and borrowing the rest from the
level above). A coast is continuous with the sea beside it, so no reader at any
reach sees a false desert, and a smooth field is also cheaper to encode than a
field with a cliff at every coastline.

What reads rain over water has to say so. The sediment plumes read the coast's
rain on the near-shore sea and relied on the zero for their offshore fade; they
now take the shore's nearness explicitly (`landRing`, index__FRAG). The cloud
shader's climate average was already normalised by land and now weights rain by
land, so the fill is not counted twice.
"""
import numpy as np


def _pull(v, w):
    """One level down: 2 x 2 weighted means, weights clamped to 1."""
    h, W = v.shape
    vw = (v * w).reshape(h // 2, 2, W // 2, 2).sum((1, 3))
    ws = w.reshape(h // 2, 2, W // 2, 2).sum((1, 3))
    return np.where(ws > 0, vw / np.maximum(ws, 1e-12), 0.0), np.minimum(ws, 1.0)


def _up(c, shape):
    """Bilinear x2, longitude periodic, latitude clamped."""
    e = 0.75 * c + 0.25 * np.roll(c, 1, axis=1)        # even columns
    o = 0.75 * c + 0.25 * np.roll(c, -1, axis=1)       # odd columns
    r = np.empty((c.shape[0], c.shape[1] * 2)); r[:, 0::2] = e; r[:, 1::2] = o
    up = np.vstack([r[:1], r[:-1]]); dn = np.vstack([r[1:], r[-1:]])
    out = np.empty((r.shape[0] * 2, r.shape[1]))
    out[0::2] = 0.75 * r + 0.25 * up; out[1::2] = 0.75 * r + 0.25 * dn
    return out[:shape[0], :shape[1]]


def apply(rain, land):
    """rain (h, w), land (h, w) bool, h and w divisible down to a 3 x 6 top.
    Returns a copy: land exact, sea filled. Same dtype family as `rain`."""
    rain = np.asarray(rain)
    v = np.where(land, rain, 0.0).astype(np.float64)
    w = land.astype(np.float64)
    pyr = [(v, w)]
    while pyr[-1][0].shape[0] % 2 == 0 and pyr[-1][0].shape[0] > 3:
        pyr.append(_pull(*pyr[-1]))
    vt, wt = pyr[-1]
    mean = float((vt * wt).sum() / max(wt.sum(), 1e-12))
    est = np.where(wt > 0, vt, mean)
    for vl, wl in reversed(pyr[:-1]):
        est = wl * vl + (1.0 - wl) * _up(est, vl.shape)
    out = np.where(land, rain, est)
    return out.astype(rain.dtype) if np.issubdtype(rain.dtype, np.floating) else out
