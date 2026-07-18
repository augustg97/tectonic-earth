"""CPU simulation of the GLSL terrain shader.

Used to validate the field-based architecture before writing any GLSL: it
decodes the same compressed textures the browser will receive, interpolates
them, and reproduces the colouring, ice and relief per output pixel. If this
looks right, the shader port is a translation rather than an experiment.
"""
import numpy as np
from PIL import Image
import render as R
from fieldpack import dec_elev, RF_MAX
from climate import climate_at


def _up(a, H, W):
    """Bilinear upsample a field to the output raster (what a sampler2D does)."""
    h, w = a.shape
    yi = np.linspace(0, h - 1, H); xi = np.linspace(0, w - 1, W)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, h - 1); fy = (yi - y0)[:, None]
    x0 = np.floor(xi).astype(int); x1 = np.minimum(x0 + 1, w - 1); fx = (xi - x0)[None, :]
    top = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx
    bot = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
    return top * (1 - fy) + bot * fy


def shade(elev_tex, rain_tex, age, H=1024, W=2048, detail=1.0):
    """elev_tex / rain_tex are decoded 0..1 fields at their own resolutions."""
    cl = climate_at(age)
    Z = _up(dec_elev(elev_tex), H, W)
    Rf = _up(rain_tex, H, W) * RF_MAX

    lat = np.linspace(90, -90, H)[:, None] * np.ones((1, W))
    s2 = np.sin(np.radians(lat)) ** 2

    # Procedural micro-relief: the elevation texture carries the real
    # large-scale terrain, this restores high-frequency roughness at output
    # resolution so upsampling doesn't read as soft.
    n1 = R._fbm((H, W), seed=11, octaves=7) - 0.5
    n2 = R._fbm((H, W), seed=29, octaves=6) - 0.5
    land0 = Z > 0
    relief = (n1 * 260.0 + n2 * 120.0) * detail * np.clip(Z / 900.0, 0.15, 1.0)
    Zd = Z + np.where(land0, relief, relief * 0.10)

    zpos = np.clip(Zd, 0, None)
    T = (26.0 - 24.0 * s2 - 26.0 * s2 ** 3) \
        + (cl["temp"] - R.TEMP_REF) * (4.0 + 15.0 * s2) - zpos * 0.0058

    sea = Zd < 0
    land = ~sea
    img = np.empty((H, W, 3), float)
    img[sea] = R._ramp(Zd[sea], R.OCEAN)

    w = np.clip((T + 6.0) / 30.0, 0, 1)
    pet = np.clip((T + 12.0) / 34.0, 0.16, 1.35)
    h = np.clip(Rf / (0.46 * pet), 0, 1)

    dry = R._L3(R._b3(R.TUNDRA, H, W), R._b3(R.DESERT, H, W), w)
    mid = R._L3(R._b3(R.GRASS, H, W), R._b3(R.SAVANNA, H, W), w)
    cold_wet = R._L3(R._b3(R.BOREAL, H, W), R._b3(R.TEMPF, H, W), np.clip(w * 2, 0, 1))
    warm_wet = R._L3(R._b3(R.TEMPF, H, W), R._b3(R.RAINF, H, W), np.clip((w - 0.5) * 2, 0, 1))
    wet = np.where((w < 0.5)[..., None], cold_wet, warm_wet)
    base = np.where((h < 0.45)[..., None],
                    R._L3(dry, mid, np.clip(h / 0.45, 0, 1)),
                    R._L3(mid, wet, np.clip((h - 0.45) / 0.55, 0, 1)))
    core = np.clip((0.30 - h) / 0.30, 0, 1) * np.clip((w - 0.45) * 2.2, 0, 1)
    base = R._L3(base, R._b3(R.DESERT_D, H, W), core * 0.5)

    veg = cl["veg"]
    if veg < 0.999:
        barren = R._L3(R._b3(R.BARREN, H, W), R._b3(R.BARREN_D, H, W),
                       np.clip(zpos / 2400.0, 0, 1))
        bf = (1 - veg) ** 0.5 * np.clip(0.92 + 0.08 * (1 - h) + zpos / 9000.0, 0, 1)
        base = R._L3(base, barren, np.clip(bf, 0, 1))

    rock = np.clip((zpos - 1700) / 1500.0, 0, 1)
    base = R._L3(base, R._L3(R._b3(R.ROCK, H, W), R._b3(R.ROCK_D, H, W),
                             np.clip((zpos - 2600) / 1800.0, 0, 1)), rock * 0.85)
    snowline = 2600.0 + 190.0 * np.clip(T, -20, 30)
    base = R._L3(base, R._b3(R.SNOW, H, W), np.clip((zpos - snowline) / 420.0, 0, 1))
    img[land] = base[land]

    ice_T, sea_ice_T = R.glaciation(cl)
    lobe = (R._fbm((H, W), seed=17, octaves=5) - 0.5) * 3.4
    ice_amt = np.clip((ice_T - (T + lobe)) / 4.5, 0, 1)
    packn = R._fbm((H, W), seed=53, octaves=5)
    sea_amt = np.clip((sea_ice_T - (T + lobe * 2.6 + (packn - 0.5) * 5.0)) / 3.5, 0, 1) \
        * np.clip((packn - 0.30) / 0.14, 0, 1)
    ice_col = R._b3(R.ICE * 0.55 + R.SNOW * 0.45, H, W)
    pack_col = R._b3(R._c("cfe0e8"), H, W) * (0.94 + 0.10 * packn)[..., None]
    img = np.where(land[..., None], R._L3(img, ice_col, ice_amt),
                                    R._L3(img, pack_col, sea_amt))

    hs = R._hillshade(Zd, H, W)
    shade_f = 0.70 + 0.62 * hs
    hw = np.where(land, 1.0, 0.30)
    img *= ((1 - hw) + hw * shade_f)[..., None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)
