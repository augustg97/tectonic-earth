"""Export the terrain + climate field textures the web build interpolates.

Per keyframe we ship two grayscale WebPs -- elevation (coastline-critical, so
high res) and rainfall (smooth, so low res) -- plus a few scalars in the
manifest. Temperature is NOT shipped: it is a closed form of latitude,
elevation and the era anomaly, so the shader recomputes it for free.

Three eras, three sources:
  * Phanerozoic 0-540 Ma -- Scotese & Wright paleoDEMs, straight through.
  * Future 0 -> +250 Myr -- the PRESENT DEM rigidly rotated by plate group.
    At age 0 every rotation is the identity, so the future series begins as an
    exact copy of the present frame and inherits its full detail; there is no
    seam and no drop in fidelity.
  * Precambrian 540-1000 Ma -- authored craton reconstruction, blended onto the
    real 540 Ma DEM across the youngest 60 Myr so the handoff into the
    Phanerozoic is continuous instead of popping.
"""
import os, re, json, glob, io
import numpy as np
import netCDF4
from PIL import Image

import render as R
from render import compute_fields, resample_dem, smooth_bathymetry, glaciation
from climate import climate_at
from fieldpack import enc_elev, RF_MAX
from build_frames import period_for, sealevel_for, index_dems, read_dem
import build_synthetic as BS
import precambrian as PRE

OUT = "../web/fields"
os.makedirs(OUT, exist_ok=True)

ELEV_H, ELEV_W = 768, 1536      # coastline resolution
RAIN_H, RAIN_W = 192, 384       # rainfall is smooth; this is plenty
CLIM_H, CLIM_W = 384, 768       # resolution the wind solve runs at
ELEV_Q, RAIN_Q = 86, 86
STEP = 5                         # Myr between keyframes, everywhere


def _gray(a01):
    return Image.fromarray((np.clip(a01, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGB")


def _save(img, path, q):
    img.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)


def export(age, Z_hi, z_for_climate, tag):
    """Z_hi: elevation at ELEV res. z_for_climate: lat-ascending DEM for the wind solve."""
    cl = climate_at(age)
    _, _, Rf, _, _ = compute_fields(z_for_climate, age, CLIM_H, CLIM_W)
    rain = np.asarray(Image.fromarray(
        (np.clip(Rf / RF_MAX, 0, 1) * 255).astype(np.uint8)).resize(
        (RAIN_W, RAIN_H), Image.LANCZOS)) / 255.0

    e = _gray(enc_elev(smooth_bathymetry(Z_hi)))
    r = _gray(rain)
    ef = f"{tag}_{abs(age):04d}_e.webp"
    rf = f"{tag}_{abs(age):04d}_r.webp"
    n = _save(e, os.path.join(OUT, ef), ELEV_Q) + _save(r, os.path.join(OUT, rf), RAIN_Q)
    ice_T, sea_T = glaciation(cl)
    ep, per = period_for(age)
    return {"age": age, "e": ef, "r": rf, "epoch": ep, "period": per,
            "sealevel": sealevel_for(age),
            "temp": round(cl["temp"], 3), "veg": round(cl["veg"], 3),
            "iceT": round(ice_T, 2), "seaT": round(sea_T, 2)}, n


# ---------------------------------------------------------------- future ----
GROUP_TARGET = {          # where each group's centroid heads by +250 Myr, and its spin
    "AFRICA":        (20, 2, 0),
    "EURASIA":       (46, 30, -16),
    "NORTH_AMERICA": (4, 40, 52),
    "SOUTH_AMERICA": (-8, -12, 34),
    "INDIA":         (44, 20, 14),
    "AUSTRALIA":     (62, 8, 118),
    "ANTARCTICA":    (25, -42, 26),
    "ARABIA":        (33, 18, 8),
    "PACIFIC":       (-150, 5, 0),
}
PLATE_GROUP = {
    "Africa": "AFRICA", "Somalia": "AFRICA", "Lwandle": "AFRICA",
    "Eurasia": "EURASIA", "Amur": "EURASIA", "Okhotsk": "EURASIA",
    "Aegean Sea": "EURASIA", "Anatolia": "EURASIA", "Yangtze": "EURASIA",
    "Okinawa": "EURASIA", "Sunda": "EURASIA", "Burma": "EURASIA",
    "Philippine Sea": "EURASIA", "Timor": "AUSTRALIA", "Banda Sea": "EURASIA",
    "Molucca Sea": "EURASIA", "Mariana": "PACIFIC", "Caroline": "PACIFIC",
    "North America": "NORTH_AMERICA", "Juan de Fuca": "NORTH_AMERICA",
    "Rivera": "NORTH_AMERICA", "Cocos": "NORTH_AMERICA",
    "Caribbean": "NORTH_AMERICA", "Panama": "NORTH_AMERICA",
    "South America": "SOUTH_AMERICA", "Nazca": "SOUTH_AMERICA",
    "Altiplano": "SOUTH_AMERICA", "North Andes": "SOUTH_AMERICA",
    "Juan Fernandez": "SOUTH_AMERICA", "Easter": "SOUTH_AMERICA",
    "Galapagos": "SOUTH_AMERICA",
    "India": "INDIA", "Capricorn": "INDIA",
    "Australia": "AUSTRALIA", "Macquarie": "AUSTRALIA", "Birds Head": "AUSTRALIA",
    "Maoke": "AUSTRALIA", "Woodlark": "AUSTRALIA", "Solomon Sea": "AUSTRALIA",
    "New Hebrides": "AUSTRALIA", "Conway Reef": "AUSTRALIA",
    "Balmoral Reef": "AUSTRALIA", "Kermadec": "AUSTRALIA", "Tonga": "AUSTRALIA",
    "Niuafo'ou": "AUSTRALIA", "Futuna": "AUSTRALIA",
    "Antarctica": "ANTARCTICA", "Scotia": "ANTARCTICA", "Shetland": "ANTARCTICA",
    "Sandwich": "ANTARCTICA", "Sur": "ANTARCTICA",
    "Arabia": "ARABIA",
    "Pacific": "PACIFIC", "Manus": "PACIFIC", "North Bismarck": "PACIFIC",
    "South Bismarck": "PACIFIC",
}
GROUPS = sorted(set(GROUP_TARGET))


def rasterise_groups(h=360, w=720):
    """Group id per cell on the present-day sphere (-1 = unassigned ocean)."""
    plates = json.load(open("../web/plates.json"))
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    LON, LAT = np.meshgrid(lon, lat)
    gid = np.full((h, w), -1, np.int16)
    for p in plates:
        g = PLATE_GROUP.get(p["name"])
        if g is None:
            continue
        gi = GROUPS.index(g)
        inside = np.zeros((h, w), bool)
        for ring in p["rings"]:
            ring = np.asarray(ring, float)
            x, y = ring[:, 0], ring[:, 1]
            acc = np.zeros((h, w), bool)
            for i in range(len(ring)):
                j = (i - 1) % len(ring)
                cond = ((y[i] > LAT) != (y[j] > LAT)) & \
                       (LON < (x[j] - x[i]) * (LAT - y[i]) / (y[j] - y[i] + 1e-12) + x[i])
                acc ^= cond
            inside |= acc
        gid[inside & (gid < 0)] = gi
    return gid


def axis_angle_scale(Rm, frac):
    """Scale a rotation matrix's angle by frac (identity at frac=0)."""
    c = np.clip((np.trace(Rm) - 1.0) / 2.0, -1, 1)
    ang = np.arccos(c)
    if ang < 1e-8:
        return np.eye(3)
    ax = np.array([Rm[2, 1] - Rm[1, 2], Rm[0, 2] - Rm[2, 0], Rm[1, 0] - Rm[0, 1]])
    ax /= (2 * np.sin(ang))
    return BS.rodrigues(ax, np.degrees(ang) * frac)


def future_grid(frac, gid, Zsrc, h, w):
    """Inverse-warp the present DEM by per-group rotation. frac 0 -> identity."""
    gh, gw = gid.shape
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    LON, LAT = np.meshgrid(lon, lat)
    T = BS.unit(LON.ravel(), LAT.ravel())
    out = np.full((h, w), -5200.0)

    # present centroid of each group, on the sphere
    cent = {}
    glon = (np.arange(gw) + 0.5) / gw * 360 - 180
    glat = 90 - (np.arange(gh) + 0.5) / gh * 180
    GLON, GLAT = np.meshgrid(glon, glat)
    for i, g in enumerate(GROUPS):
        m = gid == i
        if not m.any():
            continue
        v = BS.unit(GLON[m], GLAT[m]).mean(axis=1)
        v /= np.linalg.norm(v)
        cent[g] = v

    for i, g in enumerate(GROUPS):
        if g not in cent:
            continue
        tl, tb, spin = GROUP_TARGET[g]
        s = cent[g]; t = BS.unit(tl, tb)
        Rfull = BS.rodrigues(t, spin) @ BS.rot_from_to(s, t)
        Rm = axis_angle_scale(Rfull, frac)
        S = Rm.T @ T
        slat = np.degrees(np.arcsin(np.clip(S[2], -1, 1)))
        slon = np.degrees(np.arctan2(S[1], S[0]))
        gy = np.clip(((90 - slat) / 180 * gh).astype(int), 0, gh - 1)
        gx = np.clip(((slon + 180) / 360 * gw).astype(int), 0, gw - 1)
        claims = gid[gy, gx] == i
        if not claims.any():
            continue
        sy = np.clip(((90 - slat) / 180 * Zsrc.shape[0]).astype(int), 0, Zsrc.shape[0] - 1)
        sx = np.clip(((slon + 180) / 360 * Zsrc.shape[1]).astype(int), 0, Zsrc.shape[1] - 1)
        z = np.where(claims, Zsrc[sy, sx], -9999.0).reshape(h, w)
        out = np.maximum(out, z)          # overlap -> collision keeps the high ground
    return out


# ------------------------------------------------------------------ main ----
def main():
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    manifest, total = [], 0

    def dem_for(age):
        near = float(avail[np.argmin(np.abs(avail - age))])
        return read_dem(idx[near])

    # ---- Phanerozoic ----
    for age in range(0, 541, STEP):
        z = dem_for(age)
        m, n = export(age, resample_dem(z, ELEV_H, ELEV_W), z, "phan")
        manifest.append(m); total += n
    print(f"Phanerozoic: {len(manifest)} keyframes")

    # ---- Future: plate-warped present DEM ----
    gid = rasterise_groups()
    z0 = dem_for(0)
    Zsrc = resample_dem(z0, 900, 1800)      # north-up source for warping
    nfut = 0
    for age in range(-STEP, -251, -STEP):
        frac = abs(age) / 250.0
        gh = future_grid(frac, gid, Zsrc, ELEV_H, ELEV_W)
        gl = future_grid(frac, gid, Zsrc, CLIM_H, CLIM_W)
        m, n = export(age, gh, gl[::-1], "fut")   # export wants lat-ascending
        manifest.append(m); total += n; nfut += 1
    print(f"Future: {nfut} keyframes (plate-warped present DEM)")

    # ---- Precambrian: authored, anchored onto the real 540 Ma map ----
    z540 = dem_for(540)
    A_hi = resample_dem(z540, ELEV_H, ELEV_W)
    A_lo = resample_dem(z540, CLIM_H, CLIM_W)
    npre = 0
    for age in range(540 + STEP, 1001, STEP):
        hi = PRE.precambrian_grid(age, tw=ELEV_W, th=ELEV_H, flood=140.0)
        lo = PRE.precambrian_grid(age, tw=CLIM_W, th=CLIM_H, flood=140.0)
        # ramp from the real 540 Ma reconstruction into the authored one
        wq = float(np.clip((age - 540.0) / 60.0, 0, 1))
        hi = A_hi * (1 - wq) + hi * wq
        lo = A_lo * (1 - wq) + lo * wq
        m, n = export(age, hi, lo[::-1], "pre")
        manifest.append(m); total += n; npre += 1
    print(f"Precambrian: {npre} keyframes (anchored to 540 Ma)")

    manifest.sort(key=lambda m: m["age"])
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"),
              separators=(",", ":"))
    print(f"TOTAL {len(manifest)} keyframes, {total/1e6:.2f} MB of field textures")


if __name__ == "__main__":
    main()
