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


# ------------------------------------------------------------ descriptions --
# Narrative context for the info panel. The panel also reports live measured
# motion and elevation, so these supply the story the numbers cannot.
DESCRIPTIONS = {
 # oceans
 "Pacific Ocean": "The largest and oldest surviving ocean basin, the shrunken remnant of Panthalassa. Subduction consumes its margins faster than its ridges create new floor, so it has been closing for 180 million years.",
 "Atlantic Ocean": "Young and still opening. Born when Pangaea split, it widens a few centimetres a year at the Mid-Atlantic Ridge and has almost no subduction zones to consume it.",
 "Indian Ocean": "Opened as Gondwana broke apart and India tore north. Its floor records that sprint as a trail of ridges and the Ninetyeast fracture line.",
 "Southern Ocean": "Opened when South America and Australia finally cleared Antarctica, letting a current circle the pole unobstructed — the event that refrigerated the continent.",
 "Arctic Ocean": "A small, nearly enclosed basin ringed by continents, capped by sea ice through the present icehouse.",
 "Panthalassa": "The world-ocean wrapped around Pangaea, covering more of the planet than every modern ocean combined. The Pacific is what is left of it.",
 "Panthalassic Ocean": "The vast single ocean facing Pangaea's outer shore, floored by crust that has since been almost entirely subducted.",
 "Panthalassic (proto)": "The early world-ocean surrounding the assembling southern continents, ancestor of Panthalassa.",
 "Tethys Ocean": "A warm tropical gulf biting into the eastern flank of Pangaea. Its shallow shelves built the limestone that became the Alps and the Middle East's oil.",
 "Paleo-Tethys": "The older Tethyan ocean, closing as the Cimmerian terranes rifted off Gondwana and drifted north to collide with Asia.",
 "Iapetus Ocean": "The ocean between Laurentia and Baltica whose closure raised the Caledonian and Appalachian mountains — a mountain belt now split across the Atlantic.",
 "Rheic Ocean": "Opened behind Avalonia as it rifted from Gondwana, then closed as Gondwana and Laurussia converged to finish Pangaea.",
 "Mirovia": "The ocean encircling Rodinia. Its name means 'global' — beyond the supercontinent there was little else.",
 "Neo-Panthalassa": "The projected world-ocean on the far side of the next supercontinent, as the Atlantic closes and the Pacific's descendants take over.",
 # seas
 "Mediterranean": "The last surviving scrap of Tethys, squeezed between Africa and Europe and slowly being closed by their convergence.",
 "Mediterranean (closing)": "Africa's northward push is shutting this basin. In the projection it becomes a suture with mountains, not a sea.",
 "Paratethys": "A brackish inland sea left behind as the Alps rose and cut it off from Tethys; the Black and Caspian seas are its last remnants.",
 "Western Interior Seaway": "A shallow sea that split North America in two from the Arctic to the Gulf, drowning the continental interior at the Cretaceous sea-level peak.",
 "Turgai Strait": "A north-south seaway flooding western Siberia, separating Europe from Asia for much of the Mesozoic and early Cenozoic.",
 "Eromanga Sea": "An epeiric sea flooding central Australia during the Cretaceous highstand.",
 "Sauk Sea": "The great early-Palaeozoic flooding of Laurentia, laying down sheets of clean quartz sand across a drowned, lifeless continent.",
 "Zechstein Sea": "A hypersaline sea in Pangaea's arid interior that repeatedly evaporated, leaving thick salt beds beneath the North Sea.",
 # continents / terranes
 "Pangaea": "The last true supercontinent: nearly all land fused into one mass reaching pole to pole. Its interior lay so far from any ocean that it became one of the most arid landscapes in Earth's history.",
 "Pangaea Proxima": "A projected future supercontinent, assembled as the Atlantic closes and the continents crowd back together around Africa.",
 "Rodinia": "A Precambrian supercontinent of the Neoproterozoic world, assembled around a Laurentian core roughly a billion years ago. Its breakup may have helped trigger the Cryogenian glaciations.",
 "Pannotia": "A short-lived latest-Precambrian supercontinent, already coming apart as the Cambrian explosion began.",
 "Gondwana": "The southern supercontinent — South America, Africa, India, Australia and Antarctica as one landmass — which drifted across the South Pole and carried ice sheets with it.",
 "Gondwana (assembling)": "The southern continents welding together along the Pan-African belts, forming the mass that would dominate the Palaeozoic.",
 "Laurasia": "Pangaea's northern half after Tethys opened: North America and Eurasia still joined, drifting north into temperate and polar latitudes.",
 "Laurussia (Euramerica)": "The 'Old Red Sandstone continent', formed when Laurentia and Baltica collided and raised the Caledonides. Its vast red floodplains hosted the first forests.",
 "Laurentia": "The ancient core of North America, sitting astride the equator for much of the early Palaeozoic and repeatedly drowned by shallow seas.",
 "Baltica": "The Precambrian core of northern Europe, converging on Laurentia across the closing Iapetus.",
 "Siberia": "An independent continent for most of the Palaeozoic, drifting in northern latitudes before docking with Laurussia to complete Pangaea.",
 "Avalonia": "A slender terrane that rifted off Gondwana and rafted north across the Rheic Ocean; fragments now form eastern New England, Nova Scotia and southern Britain.",
 "Cimmeria": "A ribbon of continental fragments that peeled off Gondwana and drifted north, closing Palaeo-Tethys ahead and opening Tethys behind.",
 "North America": "Drifting west, overriding Pacific crust along its leading edge while the Atlantic widens behind it.",
 "South America": "Carried west by Atlantic spreading, its Pacific margin overriding the Nazca plate to raise the Andes.",
 "Africa": "Nearly ringed by spreading ridges, so it moves slowly. It is splitting along the East African Rift and pushing north into Europe.",
 "Eurasia": "The largest continental plate, assembled from a long history of collisions and still being built as India, Arabia and Africa drive into its southern edge.",
 "Australia": "The fastest-moving major continental plate, racing north from Antarctica toward the Asian margin.",
 "Antarctica": "Isolated over the South Pole and thermally sealed off by the circumpolar current, which turned a forested continent into an ice sheet.",
 "India": "Rifted from Gondwana and sprinted north faster than any continent known, then collided with Asia to raise the Himalaya.",
 # orogens
 "Himalaya": "Still rising as India drives into Asia — the youngest and highest mountains on Earth, built entirely of crumpled continental crust.",
 "Andes": "Raised by the subduction of oceanic crust beneath South America's western edge; a volcanic spine running the length of the continent.",
 "Rocky Mountains": "Built far inland from the plate margin, when a shallowly subducting slab transmitted stress deep into the continent.",
 "Alps": "Thrown up by Africa's collision with Europe as Tethys closed, stacking former seafloor high above sea level.",
 "Atlas": "The northwest African expression of the same Africa-Europe convergence that raised the Alps.",
 "Cordillera": "The long belt of ranges along western North America, assembled from terranes swept in and welded onto the continental margin.",
 "Sevier-Laramide": "The mountain-building episode that thickened western North America and shed sediment east into the Western Interior Seaway.",
 "Central Pangaean Mts": "A Himalayan-scale range along Pangaea's suture, running from what is now Appalachia through Iberia into central Europe.",
 "Ural Mountains": "The suture where Siberia met Laurussia, closing the last ocean inside Pangaea. Erosion has since worn it low.",
 "Appalachians": "Built in several collisions culminating in Pangaea's assembly; once alpine, now deeply eroded roots.",
 "Variscan Belt": "The European half of the Pangaean collision zone, its worn stumps preserved across France, Iberia and central Europe.",
 "Caledonides": "Raised by the closure of Iapetus; the same range now stands split between Scotland, Scandinavia and eastern Greenland.",
 "Acadian Belt": "A mid-Palaeozoic collision along Laurussia's margin, shedding sand into vast river plains.",
 "Taconic Belt": "An early Palaeozoic arc collision along Laurentia's eastern edge, the first step toward the Appalachians.",
 "Pan-African Belt": "The web of sutures created as Gondwana welded together, running through Africa, Arabia and Brazil.",
 "Grenville Belt": "A billion-year-old collisional belt marking Rodinia's assembly, traceable from Mexico through eastern Canada to Scandinavia.",
 "Afro-European Belt": "In the projection, the mountain chain thrown up where Africa finishes closing the Mediterranean against Europe.",
 "Neo-Himalaya": "The projected continuation of Himalayan building as the remaining Tethyan gap is consumed.",
 "Trans-Atlantic Belt": "The suture in the projection where the Americas rejoin Africa and Europe, closing the Atlantic entirely.",
}


def descriptions():
    return DESCRIPTIONS
