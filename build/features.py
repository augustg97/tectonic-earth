"""Time-varying map features: volcanic provinces and era labels.

Both layers previously only had present-day content, so they vanished as soon
as you scrubbed back. Each entry now carries an age window and a position in
the reconstruction's own coordinate frame, so the layers stay populated across
the whole timeline.

Positions in deep time are approximate: they are read off the reconstruction
frame rather than rotated from a plate model, so treat them as "about here in
this world", not as surveyed coordinates.
"""

# ---------------------------------------------------------------- hotspots --
# Large igneous provinces (short, cataclysmic) and long-lived plume tracks.
# a0/a1 = age window in Ma (future negative). `kind`: lip | plume
# `peak` marks the main eruptive pulse for LIPs, which the app flags.
HOTSPOTS = [
    # --- long-lived plumes, present positions, still active ---
    ("Hawaii",            -155.3,  19.4, 0,   85,  "plume", None),
    ("Iceland",            -17.0,  64.8, 0,   62,  "plume", None),
    ("Yellowstone",       -110.7,  44.4, 0,   17,  "plume", None),
    ("Galapagos",          -91.5,  -0.4, 0,   20,  "plume", None),
    ("Reunion",             55.7, -21.2, 0,   66,  "plume", None),
    ("Afar",                40.0,  11.5, 0,   30,  "plume", None),
    ("Tristan da Cunha",   -12.3, -37.1, 0,  134,  "plume", None),
    ("Kerguelen",           69.0, -49.6, 0,  120,  "plume", None),
    ("Louisville",        -141.0, -51.0, 0,  120,  "plume", None),
    ("St. Helena",          -9.9, -16.5, 0,  145,  "plume", None),
    ("Marquesas",         -139.0,  -9.0, 0,   45,  "plume", None),
    ("Easter",            -109.3, -27.1, 0,   30,  "plume", None),
    ("Azores",             -25.7,  37.9, 0,   36,  "plume", None),
    ("Canary",             -17.9,  28.3, 0,   68,  "plume", None),
    ("Cape Verde",         -24.0,  15.0, 0,   40,  "plume", None),
    ("Cameroon Line",        9.2,   4.2, 0,   65,  "plume", None),
    ("Tibesti",             17.5,  21.0, 0,   35,  "plume", None),
    ("Erebus",             167.2, -77.5, 0,   25,  "plume", None),
    ("Bouvet",               3.4, -54.4, 0,   55,  "plume", None),
    ("Crozet",              51.0, -46.4, 0,   65,  "plume", None),
    # --- Cenozoic ---
    ("Columbia River Basalts", -118.0, 45.0, 14,  18, "lip",  16),
    ("Ethiopian Traps",      39.0,  10.0,  28,  33, "lip",  30),
    ("North Atlantic Igneous", -20.0, 63.0, 55,  62, "lip",  61),
    ("Deccan Traps",         74.0,  19.0,  63,  68, "lip",  66),
    # --- Mesozoic ---
    ("Madagascar Traps",     46.0, -20.0,  86,  92, "lip",  88),
    ("Caribbean LIP",       -75.0,  12.0,  88,  95, "lip",  92),
    ("Ontong Java Plateau", 159.0,  -5.0, 118, 126, "lip", 122),
    ("Rajmahal Traps",       87.0,  24.0, 115, 120, "lip", 118),
    ("Parana-Etendeka",     -50.0, -25.0, 130, 138, "lip", 134),
    ("Karoo-Ferrar",         28.0, -28.0, 178, 186, "lip", 183),
    ("Central Atlantic (CAMP)", -30.0, 12.0, 198, 204, "lip", 201),
    # --- Paleozoic ---
    ("Siberian Traps",      100.0,  65.0, 249, 254, "lip", 252),
    ("Emeishan Traps",      103.0,  27.0, 257, 262, "lip", 260),
    ("Skagerrak-Centred",    10.0,  57.0, 295, 300, "lip", 297),
    ("Kola-Dnieper",         35.0,  60.0, 370, 380, "lip", 375),
    ("Altay-Sayan",          88.0,  52.0, 390, 400, "lip", 395),
    ("Suordakh",            135.0,  65.0, 455, 462, "lip", 458),
    ("Kalkarindji",         130.0, -18.0, 505, 512, "lip", 510),
    # --- Neoproterozoic (positions are in the authored reconstruction frame) ---
    ("Central Iapetus",     -35.0,  20.0, 605, 620, "lip", 615),
    ("Franklin LIP",        -25.0,  12.0, 713, 725, "lip", 718),
    ("Gunbarrel",           -30.0,   2.0, 775, 785, "lip", 780),
    ("Willouran / Gairdner",  60.0, -38.0, 820, 832, "lip", 827),
    ("Guibei / South China",  75.0, -18.0, 795, 810, "lip", 802),
    # --- future: rifting and collision volcanism ---
    ("East African rift volcanism", 36.0, 5.0, -60, 0, "plume", None),
    ("Afro-European collision arc", 22.0, 30.0, -170, -40, "plume", None),
    ("Neo-Tethyan arc",      55.0,  18.0, -250, -120, "plume", None),
]


def hotspots():
    return [{"n": n, "lon": lo, "lat": la, "a0": a0, "a1": a1, "k": k,
             **({"peak": p} if p is not None else {})}
            for (n, lo, la, a0, a1, k, p) in HOTSPOTS]


# ------------------------------------------------------------------ labels --
# t: continent | ocean | sea | orogen ; a0/a1 = age window (future negative)
LABELS = [
    # ---------- present / Cenozoic ----------
    ("continent", "North America", -100,  45,  -30,  75),
    ("continent", "South America",  -60, -15,  -30, 110),
    ("continent", "Africa",          20,   5,  -40, 150),
    ("continent", "Eurasia",         90,  55,  -20,  60),
    ("continent", "Australia",      135, -25,  -20,  45),
    ("continent", "Antarctica",     135, -82,  -40, 160),
    ("continent", "India",           78,  22,    0,  45),
    ("ocean", "Pacific Ocean",     -150,   0,  -10, 160),
    ("ocean", "Atlantic Ocean",     -30,  10,    0, 140),
    ("ocean", "Indian Ocean",        75, -30,    0, 120),
    ("ocean", "Southern Ocean",       0, -62,    0,  30),
    ("ocean", "Arctic Ocean",         0,  85,    0,  55),
    ("sea", "Mediterranean",         18,  36,    0,  28),
    ("sea", "Paratethys",            45,  45,   10,  34),
    ("orogen", "Himalaya",           85,  30,    0,  45),
    ("orogen", "Andes",             -70, -20,    0,  60),
    ("orogen", "Rocky Mountains",  -112,  43,    0,  60),
    ("orogen", "Alps",               10,  46,    0,  35),
    ("orogen", "Atlas",              -4,  32,    0,  40),
    # ---------- Mesozoic ----------
    ("continent", "Laurasia",        40,  50,  150, 250),
    ("continent", "Gondwana",        30, -40,  150, 540),
    ("ocean", "Tethys Ocean",        90,   5,  120, 260),
    ("ocean", "Panthalassa",       -150,   0,  160, 320),
    ("sea", "Western Interior Seaway", -95, 45, 70, 105),
    ("sea", "Turgai Strait",         65,  50,   70, 130),
    ("sea", "Eromanga Sea",         140, -28,   95, 125),
    ("orogen", "Cordillera",       -115,  40,   60, 150),
    ("orogen", "Sevier-Laramide",  -108,  42,   55,  95),
    # ---------- Pangaea ----------
    ("continent", "Pangaea",         10,   5,  250, 320),
    ("ocean", "Paleo-Tethys",       100,   0,  300, 420),
    ("sea", "Zechstein Sea",         12,  48,  252, 262),
    ("orogen", "Central Pangaean Mts", -5, 10, 250, 330),
    ("orogen", "Ural Mountains",     58,  55,  240, 320),
    ("orogen", "Appalachians",      -75,  30,  250, 400),
    ("orogen", "Variscan Belt",       5,  22,  280, 360),
    # ---------- Paleozoic ----------
    ("continent", "Laurussia (Euramerica)", -20, 10, 340, 420),
    ("continent", "Laurentia",      -60,   5,  430, 600),
    ("continent", "Baltica",         10,  30,  430, 540),
    ("continent", "Siberia",         90,  45,  430, 600),
    ("continent", "Avalonia",       -18,  -5,  430, 490),
    ("continent", "Cimmeria",       105, -20,  230, 310),
    ("ocean", "Iapetus Ocean",      -30,  20,  440, 540),
    ("ocean", "Rheic Ocean",        -10, -20,  360, 440),
    ("ocean", "Panthalassic Ocean", -150,  0,  330, 540),
    ("sea", "Sauk Sea",             -70,  10,  480, 530),
    ("orogen", "Caledonides",       -12,  25,  390, 440),
    ("orogen", "Acadian Belt",      -48,  15,  360, 400),
    ("orogen", "Taconic Belt",      -55,  12,  440, 470),
    # ---------- Precambrian ----------
    ("continent", "Gondwana (assembling)", 25, -45, 540, 600),
    ("continent", "Pannotia",        10, -40,  580, 620),
    ("continent", "Rodinia",        -10,   0,  700, 1000),
    ("ocean", "Mirovia",           -140,   0,  720, 1000),
    ("ocean", "Panthalassic (proto)", 150, -10, 600, 720),
    ("orogen", "Pan-African Belt",   20, -25,  550, 650),
    ("orogen", "Grenville Belt",    -25,  15,  900, 1000),
    # ---------- future ----------
    ("continent", "Pangaea Proxima", 30,   5, -250, -120),
    ("ocean", "Neo-Panthalassa",  -150,    0, -250,  -60),
    ("sea", "Mediterranean (closing)", 18, 36, -90,  -20),
    ("orogen", "Afro-European Belt", 20,  34, -200,  -50),
    ("orogen", "Neo-Himalaya",       60,  25, -250, -100),
    ("orogen", "Trans-Atlantic Belt", 0,  25, -250, -140),
]


def labels():
    return [{"t": t, "n": n, "lon": lo, "lat": la, "a0": a0, "a1": a1}
            for (t, n, lo, la, a0, a1) in LABELS]
