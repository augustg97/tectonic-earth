"""Author Precambrian (Rodinia -> Pannotia) and Future (Pangaea Proxima) frames.

Real cratons are cut from the present-day paleoDEM and rigidly rotated into
supercontinent configurations, so authored eras keep real topography and match
the data-driven Phanerozoic frames in fidelity.

Positions are defined at a handful of keyframes and then INTERPOLATED, so the
series can be rendered at any cadence.  That matters: sampling only the
keyframes made continents appear to teleport between them, whereas
interpolating lets the same trajectories play as continuous drift.
"""
import os, json, glob
import numpy as np
import netCDF4
from PIL import Image
from render import render_u8, _smooth, _fbm

OUT_DIR = "../web/frames"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_W, OUT_H = 1024, 512
WEBP_Q = 70


def load_present():
    f = sorted(glob.glob("../data/paleodems_1deg/**/Map01_*0Ma.nc", recursive=True))[0]
    ds = netCDF4.Dataset(f)
    z = np.asarray(ds.variables["z"][:], float)
    lat = np.asarray(ds.variables["lat"][:], float)
    lon = np.asarray(ds.variables["lon"][:], float)
    if lat[0] > lat[-1]:
        z = z[::-1]; lat = lat[::-1]
    return z, lat, lon


Z0, LAT0, LON0 = load_present()

# Craton source boxes on the present map (lon0, lon1, lat0, lat1).
CRATONS = {
    "Laurentia":   (-140, -55,  25, 83),
    "Baltica":     (   4,  60,  48, 78),
    "Siberia":     (  60, 140,  50, 78),
    "Amazonia":    ( -82, -34, -35, 12),
    "WestAfrica":  ( -18,  10,   0, 35),
    "Congo":       (  10,  32, -15, 10),
    "Kalahari":    (  12,  36, -35, -15),
    "Arabia":      (  33,  60,  12, 32),
    "India":       (  68,  90,   6, 34),
    "Australia":   ( 112, 155, -40, -10),
    "EAntarctica": (  30, 165, -90, -66),
    "WAntarctica": (-140, -55, -90, -68),
    "NChina":      ( 100, 125,  32, 46),
    "SChina":      ( 100, 122,  20, 32),
    "Kazakh":      (  55,  92,  40, 55),
    # blocks that only matter for the near-future frames, so that a projection
    # at +10 Myr still looks like Earth rather than Earth with pieces missing
    "Sunda":       (  95, 142, -11, 23),
    "NewGuinea":   ( 130, 152, -11,   0),
    "Madagascar":  (  42,  52, -27, -11),
    "CentralAm":   ( -95, -58,   5,  20),
    "NewZealand":  ( 163, 180, -48, -33),
}


def unit(lon, lat):
    la = np.radians(lat); lo = np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def rot_from_to(s, t):
    v = np.cross(s, t); c = float(np.dot(s, t))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


def rodrigues(axis, ang):
    axis = axis / np.linalg.norm(axis); a = np.radians(ang)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)


def box_center(box):
    return (0.5 * (box[0] + box[1]), 0.5 * (box[2] + box[3]))


def _sample_src(slon, slat):
    fx = (slon - LON0[0]) / (LON0[-1] - LON0[0]) * (len(LON0) - 1)
    fy = (slat - LAT0[0]) / (LAT0[-1] - LAT0[0]) * (len(LAT0) - 1)
    x0 = np.clip(np.floor(fx).astype(int), 0, len(LON0) - 1)
    y0 = np.clip(np.floor(fy).astype(int), 0, len(LAT0) - 1)
    x1 = np.clip(x0 + 1, 0, len(LON0) - 1); y1 = np.clip(y0 + 1, 0, len(LAT0) - 1)
    tx = np.clip(fx - x0, 0, 1); ty = np.clip(fy - y0, 0, 1)
    top = Z0[y0, x0] * (1 - tx) + Z0[y0, x1] * tx
    bot = Z0[y1, x0] * (1 - tx) + Z0[y1, x1] * tx
    return top * (1 - ty) + bot * ty


def compose_grid(placements, tw=720, th=360, flood=0.0):
    """Inverse-warp each craton onto the target grid (hole-free, crisp).

    `flood` (metres) lowers the land to emulate the era's eustatic sea level.
    Cratons are cut from the modern map, which is unusually high and dry; the
    Ediacaran-Cambrian world was drowned under broad epeiric seas, so without
    this the authored frames read as compact continents next to the genuinely
    flooded 540 Ma reconstruction they dissolve into.

    Returns an elevation grid (th,tw) with lat +90..-90 top->bottom.
    """
    grid = np.full((th, tw), -4800.0)
    tlon = ((np.arange(tw) + 0.5) / tw * 360 - 180)
    tlat = (90 - (np.arange(th) + 0.5) / th * 180)
    LON, LAT = np.meshgrid(tlon, tlat)
    T = unit(LON.ravel(), LAT.ravel())
    jx = (_fbm((th, tw), seed=41, octaves=5) - 0.5).ravel()
    jy = (_fbm((th, tw), seed=97, octaves=5) - 0.5).ravel()
    for name, tglon, tglat, spin in placements:
        box = CRATONS[name]
        clon, clat = box_center(box)
        s = unit(clon, clat); t = unit(tglon, tglat)
        R = rodrigues(t, spin) @ rot_from_to(s, t)
        S = R.T @ T
        slat = np.degrees(np.arcsin(np.clip(S[2], -1, 1)))
        slon = np.degrees(np.arctan2(S[1], S[0]))
        # fractal domain-warp so box edges cut craton crust on a wavy line
        wl = slon + jx * 7.0
        wt = slat + jy * 7.0
        inbox = ((wl >= box[0]) & (wl <= box[1]) & (wt >= box[2]) & (wt <= box[3]))
        if not inbox.any():
            continue
        zc = np.full(slon.shape, -9999.0)
        zc[inbox] = _sample_src(slon[inbox], slat[inbox])
        crust = inbox & (zc > -1500)
        grid = np.where(crust.reshape(th, tw) & (zc.reshape(th, tw) > grid),
                        zc.reshape(th, tw), grid)

    # Continental shelf apron: real cratons are ringed by shallow shelf that
    # ramps into the abyss. Without it the composite drops from beach to 4800 m
    # in one pixel and loses the pale shelf seas that define these maps.
    crustmask = (grid > -1500).astype(float)
    apron = crustmask
    for k in (2, 4, 7):
        apron = np.maximum(apron, _smooth(apron, k))
    grid = np.maximum(grid, -4800.0 + 4500.0 * np.clip(apron, 0, 1))

    # Drop the land toward the era's sea level so low ground floods.
    if flood:
        land = grid > 0
        grid = np.where(land, grid * 0.78 - flood, grid)
    return grid


# ---------------- Precambrian keyframes ------------------------------------
# age -> {craton: (lon, lat, spin)}.  Rodinia holds, rifts through the
# Cryogenian, then reassembles as Gondwana/Pannotia toward the Cambrian.
PRE_KEYS = {
    1000: {
        "Laurentia": (-20, 10, 180), "Baltica": (-60, 35, 120), "Siberia": (-35, 55, 150),
        "Amazonia": (-55, -10, 20), "WestAfrica": (-40, -30, 30), "Congo": (-18, -35, 10),
        "Kalahari": (-5, -50, 0), "India": (30, -30, 200), "Australia": (55, -35, 170),
        "EAntarctica": (40, -60, 30), "NChina": (70, -10, 160), "SChina": (78, -20, 150),
        "Kazakh": (-50, 50, 120), "Arabia": (-30, -45, 15),
    },
    850: {
        "Laurentia": (-22, 11, 179), "Baltica": (-63, 36, 120), "Siberia": (-34, 57, 150),
        "Amazonia": (-56, -12, 20), "WestAfrica": (-42, -31, 30), "Congo": (-19, -36, 10),
        "Kalahari": (-6, -52, 0), "India": (33, -31, 200), "Australia": (59, -36, 170),
        "EAntarctica": (43, -61, 30), "NChina": (74, -11, 160), "SChina": (82, -21, 150),
        "Kazakh": (-52, 51, 120), "Arabia": (-31, -46, 15),
    },
    750: {
        "Laurentia": (-35, 15, 175), "Baltica": (-75, 40, 120), "Siberia": (-30, 62, 150),
        "Amazonia": (-60, -20, 20), "WestAfrica": (-48, -35, 30), "Congo": (-22, -42, 10),
        "Kalahari": (-8, -58, 0), "India": (45, -35, 200), "Australia": (75, -40, 170),
        "EAntarctica": (55, -66, 30), "NChina": (88, -15, 160), "SChina": (96, -25, 150),
        "Kazakh": (-60, 56, 120), "Arabia": (-35, -52, 15),
    },
    650: {
        "Laurentia": (-52, 20, 172), "Baltica": (-92, 26, 120), "Siberia": (-70, 54, 150),
        "Amazonia": (-45, -24, 15), "WestAfrica": (-28, -28, 25), "Congo": (-8, -38, 8),
        "Kalahari": (2, -57, 0), "India": (42, -38, 195), "Australia": (72, -48, 165),
        "EAntarctica": (52, -72, 25), "NChina": (72, -22, 160), "SChina": (80, -31, 150),
        "Kazakh": (-80, 44, 120), "Arabia": (-6, -26, 8),
    },
    560: {
        "Laurentia": (-70, 25, 170), "Baltica": (-110, 15, 120), "Siberia": (-120, 45, 150),
        "Amazonia": (-30, -25, 10), "WestAfrica": (-12, -20, 20), "Congo": (5, -35, 5),
        "Kalahari": (10, -55, 0), "India": (40, -40, 190), "Australia": (70, -55, 160),
        "EAntarctica": (50, -78, 20), "NChina": (60, -30, 160), "SChina": (68, -38, 150),
        "Kazakh": (-95, 35, 120), "Arabia": (25, -18, 0),
    },
}


def _ang_lerp(a, b, t):
    """Interpolate along the shorter arc so a wrap at +/-180 doesn't spin."""
    d = ((b - a + 180.0) % 360.0) - 180.0
    return a + d * t


def pre_placement(age):
    keys = sorted(PRE_KEYS.keys())
    age = float(np.clip(age, keys[0], keys[-1]))
    lo = max(k for k in keys if k <= age)
    hi = min(k for k in keys if k >= age)
    t = 0.0 if hi == lo else (age - lo) / (hi - lo)
    A, B = PRE_KEYS[lo], PRE_KEYS[hi]
    out = []
    for name in A:
        a = A[name]; b = B.get(name, a)
        out.append((name,
                    _ang_lerp(a[0], b[0], t),
                    a[1] + (b[1] - a[1]) * t,
                    _ang_lerp(a[2], b[2], t)))
    return out


# ---------------- Future: assembly of Pangaea Proxima ------------------------
def future(frac):
    """frac 0->1 spans present -> +250 Myr as the Atlantic closes and the
    continents re-fuse around Africa."""
    def L(a, b):
        return a + (b - a) * frac
    return [
        ("WestAfrica",  L(-4, 5),     L(17, 8),    L(0, 0)),
        ("Congo",       L(21, 12),    L(-2, -6),   L(0, 0)),
        ("Kalahari",    L(24, 18),    L(-25, -18), L(0, 5)),
        ("Arabia",      L(46, 30),    L(22, 16),   L(0, 10)),
        ("Madagascar",  L(47, 33),    L(-19, -14), L(0, 8)),
        ("Baltica",     L(32, 25),    L(63, 44),   L(0, -15)),
        ("Siberia",     L(100, 70),   L(64, 40),   L(0, -20)),
        ("Kazakh",      L(73, 52),    L(47, 34),   L(0, -14)),
        ("India",       L(79, 40),    L(20, 22),   L(0, 20)),
        ("NChina",      L(112, 78),   L(39, 30),   L(0, -25)),
        ("SChina",      L(111, 74),   L(26, 20),   L(0, -25)),
        ("Sunda",       L(118, 66),   L(6, 14),    L(0, -30)),
        ("Australia",   L(133, 55),   L(-25, 12),  L(0, 130)),
        ("NewGuinea",   L(141, 60),   L(-5, 20),   L(0, 100)),
        ("NewZealand",  L(171, 78),   L(-40, 2),   L(0, 90)),
        ("EAntarctica", L(97, 40),    L(-78, -30), L(0, 40)),
        ("WAntarctica", L(-97, 14),   L(-79, -34), L(0, 40)),
        ("Laurentia",   L(-97, 20),   L(54, 30),   L(0, 55)),
        ("CentralAm",   L(-76, 8),    L(12, 6),    L(0, 45)),
        ("Amazonia",    L(-58, 0),    L(-11, -8),  L(0, 40)),
    ]


def main():
    from build_frames import period_for, sealevel_for
    manifest = []
    frames = []
    # Precambrian every 10 Myr, 1000 -> 560 Ma. The Cryogenian glaciations
    # swing the climate hard, so this stretch needs fine sampling too.
    for age in range(1000, 559, -10):
        frames.append((age, pre_placement(age), "pre"))
    # Future every 10 Myr, +10 -> +250
    for step in range(1, 26):
        age = -10 * step
        frames.append((age, future(step / 25.0), "fut"))

    for age, placement, tag in frames:
        # deep time was drowned; the future is closer to today's sea level
        flood = 210.0 if tag == "pre" else 60.0
        grid = compose_grid(placement, flood=flood)
        # render() wants latitude ascending; compose_grid returns north-on-top
        img, _ = render_u8(grid[::-1], age, out_h=OUT_H, out_w=OUT_W)
        fn = f"{tag}_{abs(age):04d}.webp"
        Image.fromarray(img).save(os.path.join(OUT_DIR, fn), "WEBP",
                                  quality=WEBP_Q, method=5)
        ep, per = period_for(age)
        manifest.append({"age": age, "file": fn, "epoch": ep, "period": per,
                         "sealevel": sealevel_for(age), "src_age": None})
        print(f"  {age:+6d} Ma  {fn}  {os.path.getsize(os.path.join(OUT_DIR, fn))//1024}KB")
    json.dump(manifest, open(os.path.join(OUT_DIR, "manifest_synth.json"), "w"), indent=0)
    total = sum(os.path.getsize(os.path.join(OUT_DIR, m["file"])) for m in manifest)
    print(f"authored: {len(manifest)} frames, {total/1e6:.2f} MB")


if __name__ == "__main__":
    main()
