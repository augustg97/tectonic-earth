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
