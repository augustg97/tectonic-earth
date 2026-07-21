"""Bake the PRESENT-day lake field from real lake outlines (Natural Earth 10m).

For deep time and the future the lakes are modelled (bake_lakes.py's water
balance), because there is no map of a world that no longer exists. But TODAY we
know exactly where the lakes are and what they look like -- so the present frame
(phan_0000) uses the real polygons: the Great Lakes and Baikal render as their
true selves, and the set is the real one, not an over-produced estimate.

Only lakes large enough to read at the 20 km grid are kept, so the map is the
handful of genuine lakes rather than every pond. Depth is distance-to-shore
(deep in the middle) with a boost for the famously deep rift/craton lakes, and
ships in the same sqrt-encoded `_w` field the shader already samples.

    ../venv/bin/python bake_present_lakes.py
"""
import os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

FIELDS = os.path.join(os.path.dirname(__file__), "..", "web", "fields")
LAKES = os.path.join(os.path.dirname(__file__), "..", "data", "ne_10m_lakes.geojson")
# The present lake field is baked at DOUBLE the elevation grid so real coastlines
# (Great Lakes, Baikal) come out crisp, not gridded. The shader samples it exactly
# like any _w field; only this frame carries the extra detail.
W, H = 4096, 2048
DMAX = 2600.0            # must match bake_lakes.DMAX / shader LAKE_DMAX
PX_DEPTH = 27.5          # metres of depth per pixel of distance from shore (~10 km/px)
DEPTH_CAP = 900.0
MIN_PX = 55             # keep only genuine, readable lakes (~130 worldwide)
# Famously deep lakes: give them a darker, deeper reading than distance alone.
DEEP_NAMED = {"Lake Baikal": 3.0, "Lake Tanganyika": 2.6, "Lake Malawi": 2.4,
              "Lake Nyasa": 2.4, "Issyk Kul": 1.8, "Lake Tahoe": 2.0,
              "Crater Lake": 2.5, "Great Slave Lake": 1.6, "Lake Toba": 2.2}


def enc_depth(d):
    return np.clip(np.sqrt(np.clip(d / DMAX, 0.0, 1.0)), 0.0, 1.0)


def rings_to_px(ring):
    return [((lon + 180.0) / 360.0 * W, (90.0 - lat) / 180.0 * H) for lon, lat in ring]


def polys_of(geom):
    """Yield polygons (each a list of rings) from Polygon / MultiPolygon."""
    if geom["type"] == "Polygon":
        yield geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        for p in geom["coordinates"]:
            yield p


def rasterize(rings_list):
    """Filled mask for one lake (exterior rings minus holes)."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    for poly in rings_list:                       # list of rings
        d.polygon(rings_to_px(poly[0]), fill=1)   # exterior
        for hole in poly[1:]:
            d.polygon(rings_to_px(hole), fill=0)  # islands
    return np.asarray(im, np.uint8)


def main():
    feats = json.load(open(LAKES))["features"]
    mask = np.zeros((H, W), np.uint8)
    deep = np.ones((H, W), np.float32)
    kept = 0
    for f in feats:
        name = f["properties"].get("name")
        polys = list(polys_of(f["geometry"]))
        m = rasterize(polys)
        if m.sum() < MIN_PX:
            continue
        kept += 1
        mask |= m
        if name in DEEP_NAMED:
            deep[m > 0] = DEEP_NAMED[name]
    # depth = distance to the nearest shore, deeper for the deep-named lakes
    edt = distance_transform_edt(mask)
    depth = np.clip(edt * PX_DEPTH * deep, 0.0, DEPTH_CAP)
    depth[mask == 0] = 0.0
    enc = (enc_depth(depth) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(enc, "L").save(os.path.join(FIELDS, "phan_0000_w.webp"),
                                   "WEBP", lossless=True, method=6)
    print(f"present: {kept} real lakes rasterized  max depth {depth.max():.0f} m  "
          f"cover {100.0*(mask>0).mean():.2f}% of grid  -> phan_0000_w.webp")


if __name__ == "__main__":
    main()
