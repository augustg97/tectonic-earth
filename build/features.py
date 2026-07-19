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
    ("Sierra Madre Occidental", -107.0, 27.0, 18, 38, "lip", 28),
    ("North Atlantic Igneous", -20.0, 63.0, 55,  62, "lip",  61),
    ("Deccan Traps",         74.0,  19.0,  63,  68, "lip",  66),
    # --- Mesozoic ---
    ("Madagascar Traps",     46.0, -20.0,  86,  92, "lip",  88),
    ("Caribbean LIP",       -75.0,  12.0,  88,  95, "lip",  92),
    ("Ontong Java Plateau", 159.0,  -5.0, 118, 126, "lip", 122),
    ("Manihiki Plateau",   -162.5, -10.0, 116, 126, "lip", 121),
    ("Hikurangi Plateau",   179.0, -40.0, 118, 126, "lip", 122),
    ("High Arctic (HALIP)", -100.0,  82.0,  80, 130, "lip", 120),
    ("Whitsunday",          149.0, -20.0,  95, 132, "lip", 112),
    ("Rajmahal Traps",       87.0,  24.0, 115, 120, "lip", 118),
    ("Parana-Etendeka",     -50.0, -25.0, 130, 138, "lip", 134),
    ("Karoo-Ferrar",         28.0, -28.0, 181, 185, "lip", 183),
    ("Chon Aike",           -69.0, -48.0, 153, 188, "lip", 178),
    ("Wrangellia",         -138.0,  60.0, 225, 232, "lip", 229),
    ("Shatsky Rise",        158.1,  32.0, 143, 147, "lip", 145),
    ("Central Atlantic (CAMP)", -30.0, 12.0, 198, 204, "lip", 201),
    # --- Paleozoic ---
    ("Siberian Traps",      100.0,  65.0, 249, 254, "lip", 252),
    ("Emeishan Traps",      103.0,  27.0, 259, 263, "lip", 260),
    ("Panjal Traps",         75.0,  34.0, 286, 292, "lip", 289),
    ("Tarim LIP",            80.0,  40.0, 275, 292, "lip", 288),
    ("Skagerrak-Centred",    10.0,  57.0, 295, 300, "lip", 297),
    ("Kola-Dnieper",         35.0,  60.0, 370, 380, "lip", 375),
    ("Altay-Sayan",          88.0,  52.0, 390, 400, "lip", 395),
    ("Suordakh",            138.0,  62.0, 440, 452, "lip", 446),
    ("Sette-Daban",         138.0,  62.0, 950, 990, "lip", 975),
    ("Yakutsk-Vilyui Traps", 125.0,  63.0, 362, 380, "lip", 373),
    ("Kalkarindji",         130.0, -18.0, 505, 512, "lip", 510),
    # --- Neoproterozoic (positions are in the authored reconstruction frame) ---
    ("Central Iapetus",     -35.0,  20.0, 550, 620, "lip", 590),
    ("Franklin LIP",        -25.0,  12.0, 714, 726, "lip", 719),
    ("Gunbarrel",           -30.0,   2.0, 775, 785, "lip", 780),
    ("Willouran / Gairdner",  60.0, -38.0, 820, 832, "lip", 827),
    ("Guibei / South China",  75.0, -18.0, 810, 835, "lip", 822),
    ("Bahia-Gangila",       -30.0,  -9.0, 900, 925, "lip", 912),
    ("Mundine Well",        116.0, -23.0, 750, 762, "lip", 755),
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
    # ---------- filling gaps the era audit turned up ----------
    ("ocean", "Mozambique Ocean",    45,  -5,  550, 800),
    ("ocean", "Adamastor Ocean",    -15, -25,  545, 780),
    ("sea",   "Tornquist Sea",       15,  50,  450, 600),
    ("ocean", "Ural Ocean",          58,  50,  255, 490),
    ("sea",   "Sundance Sea",      -108,  44,  155, 172),
    ("sea",   "Trans-Saharan Sea",    5,  20,   50, 100),
    ("sea",   "Central American Sea", -80,  9,    3,  40),
    ("sea",   "Hudson Seaway",      -85,  58,   66, 100),
    ("orogen", "Alleghanian Belt",  -80,  36,  258, 325),
    ("orogen", "Ouachita Belt",     -94,  34,  278, 320),
    ("orogen", "Antler Belt",      -117,  40,  318, 360),
    ("orogen", "Transantarctic Mts", 160, -80,  480, 560),
    ("orogen", "Verkhoyansk Belt",   130,  67,  118, 162),
    ("orogen", "Cadomian Belt",       -2,  48,  538, 650),
    ("orogen", "Timanian Belt",       55,  66,  548, 620),
    ("orogen", "Cimmerian Belt",      55,  35,  190, 250),
    ("orogen", "Innuitian Belt",     -85,  78,  340, 385),
    ("continent", "Amazonia",        -55, -10,  545, 900),
    ("continent", "Congo Craton",     20,  -3,  545, 950),
    ("continent", "Kalahari Craton",  24, -26,  545, 950),
    ("continent", "North China",     114,  38,  200, 900),
    ("continent", "South China",     110,  26,  200, 900),
]


def labels():
    return [{"t": t, "n": n, "lon": lo, "lat": la, "a0": a0, "a1": a1}
            for (t, n, lo, la, a0, a1) in LABELS]


# ------------------------------------------------------------ descriptions --
# Narrative context for the info panel. The panel also reports live measured
# motion and elevation, so these supply the story the numbers cannot.
DESCRIPTIONS = {

 "Mozambique Ocean": "The ocean between eastern and western Gondwana, closing in stages between about 600 and 550 Ma. Its closure welded the two halves together along the East African Orogeny, one of the great mountain-building events of the Precambrian.",
 "Adamastor Ocean": "The water that separated the Congo and Rio de la Plata cratons before Gondwana assembled -- how much of it was true oceanic crust rather than a wide continental rift is still argued. It closed along what is now the Brazil-Namibia suture -- and hundreds of millions of years later the South Atlantic reopened along almost the same line.",
 "Tornquist Sea": "The narrow sea between Baltica and Avalonia. Its closure was the first stage of the Caledonian collision, before Iapetus itself shut.",
 "Ural Ocean": "The ocean between Baltica and Siberia. Closing it raised the Urals and welded the last major piece of Pangaea into place.",
 "Sundance Sea": "A Jurassic arm of the Arctic reaching south into western North America, leaving the marine shales that underlie the Rocky Mountain foreland.",
 "Trans-Saharan Sea": "A shallow seaway flooding across West Africa during the Cretaceous high-stand, briefly separating the Sahara into islands.",
 "Central American Sea": "The open gap between North and South America. Its closure by the Isthmus of Panama rerouted ocean currents and let the two continents exchange their animals.",
 "Hudson Seaway": "A Cretaceous arm of the sea across what is now Hudson Bay, splitting the eastern remnant of North America off from the rest and linking the Western Interior Seaway toward the opening Labrador Sea.",
 "Alleghanian Belt": "The final Appalachian collision, as Gondwana drove into Laurussia to close Pangaea. At its peak this chain rivalled the Himalaya; what remains is its worn-down root.",
 "Ouachita Belt": "The south-western continuation of the Alleghanian collision, now largely buried beneath the Gulf coastal plain.",
 "Antler Belt": "A collision along the western margin of Laurentia as an island arc docked, thrusting deep-water rocks over the continental shelf.",
 "Transantarctic Mts": "Raised along the Pacific margin of Gondwana during the Ross Orogeny, and still today the range that divides East from West Antarctica.",
 "Verkhoyansk Belt": "Raised where the Kolyma block collided with Siberia, closing the ocean between them.",
 "Cadomian Belt": "An arc along the northern margin of Gondwana. Its fragments were later rifted away as Avalonia and carried across Iapetus.",
 "Timanian Belt": "A collision along the north-eastern edge of Baltica, predating the Uralian orogeny along nearly the same margin.",
 "Cimmerian Belt": "Raised as the Cimmerian terranes -- rifted off Gondwana -- collided with Asia, closing Palaeo-Tethys and opening Neotethys behind them.",
 "Innuitian Belt": "A Devonian mountain chain across the Canadian Arctic islands, formed as northern terranes collided with Laurentia.",
 "Amazonia": "One of the great cratons of Gondwana, and among the oldest continuously stable crust on Earth. Its shield still forms the highlands of northern South America.",
 "Congo Craton": "An ancient block at the heart of Africa, rimmed by Pan-African mountain belts where other cratons collided with it.",
 "Kalahari Craton": "A southern African block carrying some of the best-preserved evidence of the Snowball Earth glaciations in its sedimentary cover.",
 "North China": "A craton that drifted independently for much of the Palaeozoic before finally colliding with South China and joining Asia.",
 "South China": "A block whose rifting margins record the breakup of Rodinia, and which carries the classic Cryogenian glacial sections.",
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


# ------------------------------------------------------------- impacts -----
# Confirmed impact structures, present-day coordinates, age in Ma and rim
# diameter in km. Ages and sizes follow the Earth Impact Database / Wikipedia's
# list of impact structures. Vredefort (2023 Ma) and Sudbury (1849 Ma) are the
# two largest known but predate this timeline entirely.
IMPACTS = [
    # Ages follow Schmieder & Kring (2020) recommended values where they exist,
    # otherwise the primary redating paper. Several widely-circulated ages are
    # superseded -- Charlevoix and Carswell are Ordovician, not Palaeozoic-late
    # or Cretaceous, and Clearwater East and West are two craters ~180 Myr
    # apart, not a binary-impact doublet.
    ("Chicxulub",        -89.5,  21.3,   66.05, 180),
    ("Popigai",          111.0,  71.6,   35.7,  100),
    ("Manicouagan",      -68.7,  51.4,  215.6,  100),
    ("Acraman",          135.5, -32.0,  580.0,   90),
    ("Morokweng",         23.5, -26.5,  146.1,   70),
    ("Kara",              64.2,  69.1,   70.7,   65),
    ("Beaverhead",      -113.0,  44.6,  600.0,   60),
    ("Tookoonooka",      142.8, -27.0,  125.0,   55),
    ("Charlevoix",       -70.3,  47.5,  450.0,   54),
    ("Siljan",            14.9,  61.0,  380.9,   52),
    ("Karakul",           73.5,  39.0,   25.0,   52),
    ("Montagnais",       -64.2,  42.9,   51.1,   45),
    ("Steen River",     -117.6,  59.5,  141.0,   25),
    ("Chesapeake Bay",   -76.0,  37.3,   34.9,   40),
    ("Araguainha",       -53.0, -16.8,  254.7,   40),
    ("Mjolnir",           29.7,  73.8,  142.0,   40),
    ("Woodleigh",        114.7, -26.1,  364.0,   40),
    ("Saint Martin",     -98.5,  51.8,  227.8,   40),
    ("Puchezh-Katunki",   43.7,  57.0,  194.0,   40),
    ("Carswell",        -109.5,  58.4,  481.5,   39),
    ("Clearwater West",  -74.5,  56.2,  286.2,   36),
    ("Manson",           -94.6,  42.6,   75.9,   35),
    ("Strangways",       133.6, -15.2,  646.0,   25),
    ("Hiawatha",         -67.3,  78.8,   58.0,   31),
    ("Slate Islands",    -87.0,  48.7,  450.0,   30),
    ("Mistastin",        -63.3,  55.9,   37.8,   28),
    ("Clearwater East",  -74.1,  56.1,  465.0,   26),
    ("Tunnunik",        -114.0,  72.5,  440.0,   26),
    ("Lake Marsal",      -64.7,  51.2,  390.0,   25),
    ("Kamensk",           40.5,  48.4,   50.4,   25),
    ("Ries",              10.6,  48.9,   14.8,   24),
    ("Boltysh",           32.3,  48.9,   65.4,   24),
    ("Rochechouart",       0.9,  45.8,  206.9,   23),
    ("Lappajarvi",        23.7,  63.2,   77.9,   23),
    ("Gosses Bluff",     132.3, -23.8,  142.5,   22),
    ("Haughton",         -89.7,  75.4,   31.0,   23),
]


def impacts():
    return [{"n": n, "lon": lo, "lat": la, "age": a, "d": d, "k": "impact"}
            for (n, lo, la, a, d) in IMPACTS]


# ---------------------------------------------------- event descriptions ----
# One or two sentences per volcanic province, plume and crater: what it is,
# and what it did to the world. Keyed by name; anything without an entry falls
# back to a generated line.
EVENT_NOTES = {
    # --- large igneous provinces ---
    "Siberian Traps": "The largest continental flood basalt known: perhaps four million cubic kilometres of lava across Siberia in under a million years, and — as it burned through coal and evaporite — enough carbon and sulphur to acidify the oceans and drive the end-Permian extinction, the worst in Earth's history.",
    "Deccan Traps": "Vast basalt flows across western India, erupting as the subcontinent drove north over the Reunion plume. Their peak brackets the Chicxulub impact, and the two together ended the Cretaceous.",
    "Central Atlantic (CAMP)": "Magmatism spread across four continents as Pangaea began to split, opening the crack that became the Atlantic. It coincides with the end-Triassic extinction.",
    "Ontong Java Plateau": "The largest oceanic plateau on Earth, erupted onto the floor of the Pacific in a few million years. It helped push the mid-Cretaceous into an extreme greenhouse and starved the oceans of oxygen.",
    "Ethiopian Traps": "Flood basalts over the Afar plume that domed up East Africa and began tearing it open — the rifting still going on today.",
    "North Atlantic Igneous": "Eruptions as Greenland and Europe parted. Carbon released here is a leading suspect for the Paleocene-Eocene Thermal Maximum, the sharpest warming of the Cenozoic.",
    "Karoo-Ferrar": "Basalts stretched from southern Africa to Antarctica as Gondwana started to break apart, and coincide with the Early Jurassic ocean anoxic event.",
    "Parana-Etendeka": "One province split in two: its halves now sit in Brazil and Namibia, torn apart by the opening South Atlantic.",
    "Emeishan Traps": "Flood basalts in South China, associated with the end-Guadalupian extinction some eight million years before the far larger end-Permian crisis.",
    "Columbia River Basalts": "The youngest continental flood basalt province, laid down across the Pacific Northwest as the Yellowstone plume arrived beneath the continent.",
    "Caribbean LIP": "A thick oceanic plateau that proved too buoyant to subduct; it jammed between the Americas and became the floor of the Caribbean.",
    "Madagascar Traps": "Eruptions as Madagascar separated from India, leaving the island isolated — and its life to evolve alone.",
    "Kalkarindji": "Australia's Cambrian flood basalts, linked to an early-Cambrian extinction pulse not long after animals first diversified.",
    "Franklin LIP": "Enormous eruptions across what is now Arctic Canada at the threshold of the Sturtian glaciation. Weathering of fresh basalt in the tropics is thought to have drawn down enough CO2 to help freeze the planet.",
    "Central Iapetus": "Rift volcanism as Rodinia's fragments finally separated and the Iapetus Ocean opened between them.",
    "Rajmahal Traps": "The Kerguelen plume's first arrival under eastern India, before the plate carried the continent onward.",
    # --- plumes ---
    "Hawaii": "A plume fixed in the mantle while the Pacific plate slides over it, printing a chain of volcanoes that gets older to the north-west — the clearest ruler we have for plate motion.",
    "Iceland": "The only place a mid-ocean ridge rises above sea level, held up by a plume beneath the spreading Atlantic.",
    "Yellowstone": "The North American plate riding south-west over a plume, leaving a track of calderas across the Snake River Plain.",
    "Afar": "Three rifts meet over a plume here; two are opening the Red Sea and Gulf of Aden, the third is splitting Africa itself.",
    "Reunion": "The plume that erupted the Deccan Traps, still burning under the Indian Ocean 66 million years later.",
    # --- impact structures ---
    "Chicxulub": "The asteroid that ended the Cretaceous. A ten-kilometre body struck the Yucatan shelf, throwing enough rock and sulphur into the atmosphere to darken and chill the planet for years, and taking the non-avian dinosaurs with it.",
    "Vredefort": "The largest confirmed impact structure on Earth, though far older than this timeline.",
    "Popigai": "A Siberian crater whose impact shocked graphite into diamond across the surrounding rock. It falls in a late Eocene cluster of strikes.",
    "Manicouagan": "A Late Triassic crater, its ring-shaped lake now one of the most recognisable features from orbit.",
    "Chesapeake Bay": "A late Eocene strike on the North American shelf; the buried crater still steers the modern bay and its groundwater.",
    "Acraman": "An Ediacaran impact in South Australia. Its ejecta layer sits in rocks alongside some of the earliest complex organisms.",
    "Araguainha": "Brazil's largest crater, its age falling within uncertainty of the end-Permian extinction, though it is far too small to be its cause.",
    "Morokweng": "A Jurassic-Cretaceous boundary crater buried under the Kalahari, found only by its magnetic signature.",
    "Siljan": "A Devonian crater in Sweden, the largest in Europe, its ring of lakes still visible in the landscape.",
    "Ries": "A Miocene crater in Bavaria. Its ejecta scattered glass across central Europe, and the town of Nordlingen is built inside it.",
    "Charlevoix": "An Ordovician crater on the St. Lawrence; the modern river follows the weakened rock around its rim. Long dated to the Carboniferous, it was reassigned to ~450 Ma by U-Pb on shocked zircon.",
    "Boltysh": "A Ukrainian crater that struck roughly 650,000 years AFTER Chicxulub, into a world still recovering from it. Its lake sediments record that recovery in fine detail.",
    "Hiawatha": "Buried under a kilometre of the Greenland ice sheet and found by radar. It is far older than the ice: when it formed, the target was rainforest.",
    "Manson": "An Iowa crater once proposed as the killer of the dinosaurs, until redating placed it about ten million years too early.",
    "Puchezh-Katunki": "A large Early Jurassic structure on the Russian platform, now almost entirely buried.",
    "Clearwater West": "The larger of the two Clearwater lakes. The pair look like a classic double impact, but their ages differ by nearly 200 million years -- they are unrelated.",
    "Clearwater East": "The smaller Clearwater lake, and the older by far. Its Ordovician age is what disproved the twin-impact story its shape suggests.",
    "Tunnunik": "An Arctic crater recognised only in 2010, its rim visible from the air as a ring of disturbed strata.",
    "Slate Islands": "An archipelago in Lake Superior that is the central uplift of an Ordovician crater, its rocks full of shatter cones.",
    "Lake Marsal": "Confirmed as an impact structure only in 2025, after shatter cones were found around a ring-shaped basin spotted on satellite imagery.",
    "Mjolnir": "A crater on the floor of the Barents Sea, which triggered a tsunami across the shallow Jurassic seaway.",
    "Beaverhead": "One of the oldest large craters in North America, its structure dismembered and scattered by later mountain building.",
    "Woodleigh": "A buried Devonian crater in Western Australia, near in age to a major extinction pulse.",
    "Tookoonooka": "An Early Cretaceous impact into a shallow Australian sea, now buried under the Eromanga Basin.",
    "Sierra Madre Occidental": "The largest silicic volcanic province on Earth: ignimbrite sheets across northern Mexico, erupted as the subducting Farallon slab rolled back and the crust above it began to tear open into the Gulf of California.",
    "Manihiki Plateau": "One of three fragments of Ontong Java Nui, a single Cretaceous mega-plateau that a spreading triple junction later split apart.",
    "Hikurangi Plateau": "The third fragment of Ontong Java Nui. Too buoyant to sink easily, it is now jamming into the subduction zone beneath New Zealand.",
    "High Arctic (HALIP)": "Magmatism spanning the Arctic as the Amerasia Basin opened, from Svalbard to the Sverdrup Basin and the Alpha Ridge.",
    "Whitsunday": "A vast silicic province along eastern Australia. Unusually for a province this size it is driven by slab rollback rather than a mantle plume.",
    "Chon Aike": "One of the largest silicic provinces known, erupted across Patagonia and the Antarctic Peninsula as the Weddell Sea began to open.",
    "Wrangellia": "An oceanic plateau erupted in Panthalassa and later rammed into North America, where it now forms a belt of accreted crust from Vancouver Island to Alaska. It is the leading suspect for the Carnian Pluvial Episode.",
    "Shatsky Rise": "A huge Pacific plateau built at a three-way junction of spreading ridges. Whether a plume or the junction itself made it is still argued.",
    "Panjal Traps": "Flood basalts in Kashmir that rifted the Cimmerian terranes off Gondwana and opened the Neotethys Ocean behind them.",
    "Tarim LIP": "Early Permian magmatism beneath what is now the Tarim Basin, erupted through the heart of central Asia.",
    "Sette-Daban": "Magmatism on the eastern Siberian craton around a billion years ago, at the far edge of this reconstruction.",
    "Yakutsk-Vilyui Traps": "Late Devonian flood basalts that tore open the eastern Siberian platform, and the leading candidate for the Frasnian-Famennian extinction that removed most reef-building life.",
    "Bahia-Gangila": "Dykes and sills across the joined Sao Francisco and Congo cratons, erupted as Rodinia stretched after assembling.",
    "Mundine Well": "A dyke swarm across the Pilbara of Western Australia, and one of the anchor points for reconstructing where Australia sat within Rodinia.",
    "Galapagos": "A plume beneath the equatorial Pacific whose islands are young enough that their species are still visibly diverging.",
    "Tristan da Cunha": "The plume that erupted the Parana-Etendeka basalts and then wrote its track across the seafloor as the Walvis Ridge while the South Atlantic opened.",
    "Kerguelen": "A plume that built one of the largest oceanic plateaus on Earth, and briefly gave the southern Indian Ocean a drowned micro-continent with forests on it.",
    "Louisville": "A long Pacific seamount chain, the southern counterpart to Hawaii's track.",
    "St. Helena": "A South Atlantic plume with a distinctive deep-mantle chemical signature.",
    "Marquesas": "A Pacific plume whose islands rise steeply from deep water with almost no reef fringe.",
    "Easter": "A plume close to the East Pacific Rise; the interaction between the two builds an unusually broad volcanic ridge.",
    "Azores": "A plume sitting on the Mid-Atlantic Ridge, thickening the crust and lifting the islands above the sea.",
    "Canary": "A slow-moving plume off north-west Africa; because the African plate barely moves over it, the islands stay volcanically active far longer than Hawaii's.",
    "Cape Verde": "A plume beneath one of the largest swells on the ocean floor, raising the seabed more than two kilometres.",
    "Cameroon Line": "A chain of volcanoes running from the Atlantic onto the African continent -- unusually, it crosses the ocean-continent boundary without a break.",
    "Tibesti": "Volcanism in the central Sahara that built mountains rising from the desert to over three kilometres.",
    "Erebus": "The southernmost active volcano on Earth, holding a permanent lake of molten lava through the Antarctic winter.",
    "Bouvet": "A plume near a triple junction in the South Atlantic, and the most remote island on the planet.",
    "Crozet": "A southern Indian Ocean plume; iron shed from its islands fertilises one of the largest plankton blooms in the world.",
    "East African rift volcanism": "The rift that is currently splitting Africa. Projected forward, it floods and becomes an ocean.",
    "Afro-European collision arc": "Projected volcanism where Africa drives into Europe and the Mediterranean closes, raising a mountain chain along the suture.",
    "Neo-Tethyan arc": "Projected arc volcanism along the closing ocean between the converging continents of the future supercontinent.",

    # --- remaining provinces ---
    "Skagerrak-Centred": "Late Carboniferous magmatism across northern Europe as Pangaea finished assembling and the crust behind the collision began to pull apart.",
    "Kola-Dnieper": "Late Devonian rift volcanism across the East European craton, close in age to the Frasnian-Famennian extinction.",
    "Altay-Sayan": "Devonian plume volcanism in central Asia, erupted through the collage of arcs and terranes that would become Siberia's southern margin.",
    "Suordakh": "Ordovician magmatism on the Siberian platform, roughly contemporary with the great diversification of marine life.",
    "Gunbarrel": "Rift magmatism along the edge of Laurentia as Rodinia began to come apart, well before the supercontinent finally broke.",
    "Willouran / Gairdner": "Early Neoproterozoic dyke swarms across Australia, marking the first tearing of Rodinia's interior.",
    "Guibei / South China": "Plume magmatism beneath the South China block during Rodinia's breakup, in the run-up to the Cryogenian glaciations.",
}


def event_notes():
    return EVENT_NOTES
