"""Per-era climate state for paleogeographic coloring.

Values are literature-informed (Scotese PaleoClimate atlas, Boucot et al.,
Royer CO2 curves). Each entry: age (Ma), with:
  temp   : global mean-temp anomaly proxy, -1 (icehouse) .. +1 (hothouse)
  iceN   : |lat| poleward of which N-hemisphere land carries ice (None=none)
  iceS   : |lat| poleward of which S-hemisphere land carries ice (None=none)
  veg    : land vegetation level 0 (barren rock) .. 1 (fully vegetated)
  arid   : subtropical-desert intensity 0..1 (supercontinent interiors high)
Intermediate ages are linearly interpolated.
"""

CLIMATE = [
    # age  temp   iceN   iceS   veg   arid   note
    (0,   -0.55,  68,    62,   1.00, 0.55),  # Holocene icehouse, bipolar ice
    (5,   -0.50,  70,    62,   1.00, 0.55),
    (15,  -0.30,  74,    64,   1.00, 0.52),
    (25,  -0.15,  78,    66,   1.00, 0.50),  # late Oligocene
    (34,  -0.05,  None,  68,   1.00, 0.48),  # Eocene-Oligocene: EAIS grows
    (40,   0.45,  None,  None, 1.00, 0.45),  # late Eocene, near ice-free
    (50,   0.75,  None,  None, 1.00, 0.42),  # early Eocene hothouse
    (56,   0.85,  None,  None, 1.00, 0.42),  # PETM
    (66,   0.55,  None,  None, 1.00, 0.45),  # K-Pg
    (90,   0.85,  None,  None, 1.00, 0.42),  # mid-Cretaceous hothouse, ice-free
    (120,  0.55,  None,  None, 1.00, 0.45),
    (145,  0.35,  None,  85,   1.00, 0.50),  # J-K boundary, cool snap
    (160,  0.35,  None,  None, 1.00, 0.52),
    (200,  0.55,  None,  None, 0.95, 0.62),  # Tr-J, Pangaea, arid
    (230,  0.60,  None,  None, 0.90, 0.70),  # Late Triassic megamonsoon
    (250,  0.70,  None,  None, 0.80, 0.78),  # P-Tr hothouse, hyperarid interior
    (260,  0.30,  None,  None, 0.92, 0.68),
    (280,  -0.30, None,  60,   0.95, 0.58),  # early Permian, waning Gondwana ice
    (300,  -0.70, 72,    58,   0.95, 0.50),  # LPIA peak, bipolar-ish coal forests
    (315,  -0.65, 74,    58,   0.98, 0.48),  # Carboniferous coal swamps
    (330,  -0.25, None,  64,   0.95, 0.48),
    (340,   0.05, None,  None, 0.90, 0.50),
    (360,   0.10, None,  None, 0.82, 0.52),  # Devono-Carb, early forests
    (380,   0.30, None,  None, 0.60, 0.55),  # Devonian greening underway
    (400,   0.35, None,  None, 0.35, 0.58),  # early Devonian, sparse land plants
    (420,   0.30, None,  None, 0.18, 0.58),  # Silurian, first vascular plants
    (440,  -0.20, None,  62,   0.05, 0.55),  # end-Ordovician recovery
    (445,  -0.65, None,  58,   0.03, 0.52),  # Hirnantian glaciation, barren land
    (460,   0.15, None,  70,   0.02, 0.55),  # Ordovician warm, barren
    (490,   0.35, None,  None, 0.00, 0.58),  # Cambrian, barren rock land
    (520,   0.30, None,  None, 0.00, 0.58),
    (540,   0.20, None,  75,   0.00, 0.55),  # Ediacaran/Cambrian boundary
    # ---- Precambrian (authored keyframes) ----
    (600,  -0.10, 70,    70,   0.00, 0.50),  # Pannotia, post-Gaskiers
    # The Cryogenian needs a far deeper anomaly than the rest of the record:
    # these events froze the ocean to near-tropical latitudes, which a -1..+1
    # scale cannot express. Onset and recovery are ramped over several
    # keyframes; dropping straight into it made one frame boundary lurch.
    (630,  -1.20, 58,    58,   0.00, 0.45),  # recovering out of the icehouse
    (650,  -4.00, 35,    35,   0.00, 0.45),  # Marinoan snowball aftermath
    (700,  -6.00, 20,    20,   0.00, 0.45),  # Sturtian/Marinoan snowball Earth
    (730,  -1.50, 52,    52,   0.00, 0.48),  # sliding into the Sturtian
    (750,   0.10, None,  None, 0.00, 0.55),  # Rodinia rifting, warm
    (850,   0.20, None,  None, 0.00, 0.58),  # Rodinia
    (900,   0.15, None,  None, 0.00, 0.58),  # Rodinia assembled
    (1000,  0.10, None,  80,   0.00, 0.55),  # Rodinia
    # ---- Future (Pangaea Proxima scenario, Scotese) ----
    (-30,  -0.30, 74,    64,   1.00, 0.55),  # +30 Myr, near-modern icehouse waning
    (-70,   0.20, None,  70,   1.00, 0.60),  # +70, Mediterranean closed, warming
    (-120,  0.55, None,  None, 1.00, 0.66),  # +120, Atlantic closing
    (-170,  0.70, None,  None, 0.95, 0.74),  # +170, assembling
    (-250,  0.85, None,  None, 0.85, 0.82),  # +250, Pangaea Proxima hothouse
]


def _interp(age, idx):
    pts = sorted([(a, e[idx]) for a, e in [(c[0], c) for c in CLIMATE]])
    # split future (negative) and past (positive) so we don't interpolate across 0 wrongly
    return None  # placeholder; real interp in climate_at


def climate_at(age):
    """age in Ma; future is negative (e.g. -90 = +90 Myr). Returns dict."""
    # choose the correct branch
    if age < 0:
        pts = [c for c in CLIMATE if c[0] <= 0]
        pts = sorted(pts, key=lambda c: c[0], reverse=True)  # 0, -30, -70...
    else:
        pts = [c for c in CLIMATE if c[0] >= 0]
        pts = sorted(pts, key=lambda c: c[0])
    ages = [c[0] for c in pts]
    # clamp
    if age <= min(ages):
        lo = hi = pts[ages.index(min(ages))]
        t = 0
    elif age >= max(ages):
        lo = hi = pts[ages.index(max(ages))]
        t = 0
    else:
        for i in range(len(pts) - 1):
            a0, a1 = ages[i], ages[i + 1]
            if (a0 <= age <= a1) or (a1 <= age <= a0):
                lo, hi = pts[i], pts[i + 1]
                span = (a1 - a0)
                t = 0 if span == 0 else (age - a0) / span
                break
        else:
            lo = hi = pts[-1]; t = 0

    def lerp_num(x0, x1):
        return x0 + (x1 - x0) * t

    def lerp_ice(x0, x1):
        # treat None as 91 (no ice) so it blends smoothly
        a = 91 if x0 is None else x0
        b = 91 if x1 is None else x1
        v = a + (b - a) * t
        return None if v >= 90 else v

    return {
        "age": age,
        "temp": lerp_num(lo[1], hi[1]),
        "iceN": lerp_ice(lo[2], hi[2]),
        "iceS": lerp_ice(lo[3], hi[3]),
        "veg": lerp_num(lo[4], hi[4]),
        "arid": lerp_num(lo[5], hi[5]),
    }


if __name__ == "__main__":
    for a in [0, 34, 90, 250, 300, 445, 540, -70, -250]:
        print(a, climate_at(a))


# ---------------------------------------------------------------------------
# Global system curves. These are digitised approximations of published
# reconstructions, sampled coarsely and interpolated:
#   GMST  - global mean surface temperature, deg C (Scotese et al. GAT curve)
#   CO2   - atmospheric CO2, ppm (GEOCARB III / Royer compilations)
#   O2    - atmospheric O2, % by volume (Berner GEOCARBSULF / COPSE)
# Precambrian oxygen is the big one: before the Neoproterozoic Oxygenation
# Event the atmosphere held a few percent at most, which is why the deep-time
# end of the record reads so low.
# ---------------------------------------------------------------------------
SYSTEM = [
    # age    GMST  CO2     O2
    (0,      14.4,  420,   20.9),
    (5,      15.5,  400,   20.9),
    (20,     17.0,  450,   20.8),
    (34,     19.0,  700,   20.5),
    (40,     23.0, 1000,   20.0),
    (50,     26.5, 1400,   19.5),
    (56,     27.5, 1600,   19.2),
    (66,     25.0, 1000,   19.0),
    (90,     28.0, 1200,   18.5),
    (120,    25.0, 1100,   17.5),
    (145,    22.0,  900,   16.5),
    (160,    21.5, 1000,   16.0),
    (200,    23.0, 1800,   14.0),
    (230,    24.0, 1900,   14.5),
    (250,    27.0, 2000,   16.0),
    (260,    22.0, 1000,   23.0),
    (280,    16.0,  400,   30.0),
    (300,    13.5,  300,   32.0),
    (315,    13.0,  350,   35.0),
    (330,    16.0,  700,   30.0),
    (360,    19.0, 1800,   22.0),
    (380,    21.0, 2600,   18.0),
    (400,    21.5, 3300,   16.0),
    (420,    22.0, 4000,   15.0),
    (440,    17.0, 4400,   14.0),
    (445,    14.5, 4000,   13.5),
    (460,    22.0, 5000,   13.0),
    (490,    23.0, 5500,   12.0),
    (520,    23.5, 6000,   10.0),
    (540,    22.0, 6000,    8.0),
    (600,    16.0, 4000,    3.0),
    (630,    12.0, 3000,    2.0),
    (650,    -2.0, 1500,    1.5),
    (700,    -8.0, 1200,    1.0),
    (730,    12.0, 3000,    1.0),
    (750,    20.0, 4000,    0.8),
    (850,    21.0, 4500,    0.5),
    (1000,   20.0, 5000,    0.3),
    # future: a warm world that slowly relaxes as the supercontinent assembles
    (-30,    17.5,  600,   20.9),
    (-70,    21.0,  900,   20.8),
    (-120,   24.0, 1200,   20.6),
    (-170,   25.5, 1500,   20.3),
    (-250,   27.0, 1800,   20.0),
]


def system_at(age):
    """Global mean temperature (C), CO2 (ppm) and O2 (%) for an age."""
    pts = [p for p in SYSTEM if (p[0] <= 0) == (age <= 0)] or SYSTEM
    pts = sorted(pts, key=lambda p: p[0])
    ages = [p[0] for p in pts]
    if age <= ages[0]:
        lo = hi = pts[0]; t = 0.0
    elif age >= ages[-1]:
        lo = hi = pts[-1]; t = 0.0
    else:
        i = max(i for i, a in enumerate(ages) if a <= age)
        lo, hi = pts[i], pts[min(i + 1, len(pts) - 1)]
        span = hi[0] - lo[0]
        t = 0.0 if span == 0 else (age - lo[0]) / span
    return {"gmst": round(lo[1] + (hi[1] - lo[1]) * t, 1),
            "co2":  int(round(lo[2] + (hi[2] - lo[2]) * t)),
            "o2":   round(lo[3] + (hi[3] - lo[3]) * t, 1)}
