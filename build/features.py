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
    ("Galapagos",          -91.5,  -0.4, 0,   90,  "plume", None),
    ("Reunion",             55.7, -21.2, 0,   67,  "plume", None),
    ("Afar",                40.0,  11.5, 0,   30,  "plume", None),
    ("Tristan da Cunha",   -12.3, -37.1, 0,  134,  "plume", None),
    ("Kerguelen",           69.0, -49.6, 0,  132,  "plume", None),
    ("Louisville",        -141.0, -51.0, 0,  125,  "plume", None),
    ("St. Helena",          -9.9, -16.5, 0,  83,  "plume", None),
    ("Marquesas",         -139.0,  -9.0, 0,   6,  "plume", None),
    ("Easter",            -109.3, -27.1, 0,   30,  "plume", None),
    ("Azores",             -25.7,  37.9, 0,   36,  "plume", None),
    ("Canary",             -17.9,  28.3, 0,   68,  "plume", None),
    ("Cape Verde",         -24.0,  15.0, 0,   26,  "plume", None),
    ("Cameroon Line",        9.2,   4.2, 0,   65,  "plume", None),
    ("Tibesti",             17.5,  21.0, 0,   35,  "plume", None),
    ("Erebus",             167.2, -77.5, 0,   19,  "plume", None),
    ("Bouvet",               3.4, -54.4, 0,   55,  "plume", None),
    ("Crozet",              51.0, -46.4, 0,   54,  "plume", None),
    # --- Cenozoic ---
    ("Columbia River Basalts", -118.0, 45.0, 6,  17.2, "lip",  16.2),
    ("Ethiopian Traps",      39.0,  10.0,  28,  33, "lip",  30),
    ("Sierra Madre Occidental", -107.0, 27.0, 18, 38, "lip", 28),
    ("North Atlantic Igneous", -20.0, 63.0, 54,  63, "lip",  56),
    ("Deccan Traps",         74.0,  19.0,  65,  67.4, "lip",  66.1),
    # --- Mesozoic ---
    ("Madagascar Traps",     46.0, -20.0,  84,  92, "lip",  89.5),
    ("Caribbean LIP",       -75.0,  12.0,  83,  95, "lip",  89),
    ("Ontong Java Plateau", 159.0,  -5.0, 118, 126, "lip", 122),
    ("Manihiki Plateau",   -162.5, -10.0, 116, 126, "lip", 121),
    ("Hikurangi Plateau",   179.0, -40.0, 84, 126, "lip", 122),
    ("High Arctic (HALIP)", -100.0,  82.0,  60, 130, "lip", 123),
    ("Whitsunday",          149.0, -20.0,  95, 132, "lip", 112),
    ("Rajmahal Traps",       87.0,  24.0, 115, 120, "lip", 118),
    ("Parana-Etendeka",     -50.0, -25.0, 131, 136, "lip", 134),
    ("Karoo",         25, -28, 181, 185, "lip", 183),
    ("Chon Aike",           -69.0, -48.0, 153, 188, "lip", 184),
    ("Wrangellia",         -136,  57, 224, 233, "lip", 230.5),
    ("Shatsky Rise",        158.1,  32.0, 128, 147, "lip", 144.6),
    ("Central Atlantic (CAMP)", -30.0, 12.0, 195, 202, "lip", 201.5),
    # --- Paleozoic ---
    ("Siberian Traps",      90,  67, 250.2, 252.3, "lip", 252),
    ("Emeishan Traps",      103.0,  27.0, 256, 263, "lip", 259.5),
    ("Panjal Traps",         75.0,  34.0, 286, 292, "lip", 289),
    ("Tarim LIP",            80.0,  40.0, 272, 300, "lip", 290),
    ("Skagerrak-Centred",    10.0,  57.0, 295, 300, "lip", 297),
    ("Kola-Dnieper",         35.0,  60.0, 360, 380, "lip", 370),
    ("Altay-Sayan",          88.0,  52.0, 390, 410, "lip", 400),
    ("Suordakh",            138.0,  62.0, 444, 464, "lip", 454),
    ("Sette-Daban",         138.0,  62.0, 970, 982, "lip", 975),
    ("Yakutsk-Vilyui Traps", 125.0,  63.0, 362, 380, "lip", 373),
    ("Kalkarindji",         130.0, -18.0, 505, 512, "lip", 511),
    # --- Neoproterozoic (positions are in the authored reconstruction frame) ---
    ("Central Iapetus",     -35.0,  20.0, 550, 620, "lip", 590),
    ("Franklin LIP",        -25.0,  12.0, 716, 721, "lip", 719),
    ("Gunbarrel",           -30.0,   2.0, 775, 785, "lip", 780),
    ("Willouran / Gairdner",  60.0, -38.0, 820, 832, "lip", 827),
    ("Guibei / South China",  75.0, -18.0, 810, 835, "lip", 826),
    ("Bahia-Gangila",       -30.0,  -9.0, 900, 925, "lip", 912),
    ("Mundine Well",        116.0, -23.0, 750, 762, "lip", 755),
    # --- future: rifting and collision volcanism ---
    ("East African rift volcanism", 36.0, 5.0, -60, 0, "plume", None),
    ("Afro-European collision arc", 22.0, 30.0, -170, -40, "plume", None),
    ("Neo-Tethyan arc",      55.0,  18.0, -250, -120, "plume", None),
    # ---------- imported from the volcanism audit ----------
    ("Dashigou (N. China)", 112.5, 39.5, 915, 935, "lip", 925),
    ("Suxiong-Xiaofeng", 111.2, 30.9, 792, 812, "lip", 802),
    ("Kangding", 102.0, 29.9, 768, 779, "lip", 773),
    ("Malani Igneous Suite", 72.3, 25.5, 751, 771, "lip", 768),
    ("Irkutsk LIP", 103.0, 54.5, 712, 730, "lip", 720),
    ("Gannakouriep", 17.0, -29.0, 706, 728, "lip", 717),
    ("Volyn Flood Basalts", 25.0, 51.0, 551, 580, "lip", 570),
    ("Seiland Igneous Province", 22.7, 70.4, 560, 570, "lip", 566),
    ("Wichita / S. Oklahoma", -98.3, 34.6, 530, 539, "lip", 532),
    ("Kharaulakh", 130.0, 71.0, 510, 530, "lip", 520),
    ("Alborz LIP", 55.0, 36.5, 425, 469, "lip", 445),
    ("Ferrar", 160.0, -78.0, 182.2, 183.0, "lip", 182.6),
    ("Comei LIP", 90.0, 28.5, 130, 145, "lip", 132),
    ("Magellan Rise", -176.8, 7.1, 128, 145, "lip", 135),
    ("Bunbury Basalt", 115.6, -33.3, 123, 137, "lip", 132.2),
    ("Gough", -10.0, -40.3, 0, 134, "plume", None),
    ("Mid-Pacific Mountains", -178.0, 20.0, 100, 125, "lip", 110),
    ("Great Meteor", -28.4, 29.4, 0, 124, "plume", None),
    ("S. Kerguelen Plateau", 76.0, -58.0, 110, 120, "lip", 115),
    ("Arago (Rurutu)", -150.7, -23.4, 0, 120, "plume", None),
    ("Sylhet Traps", 91.0, 25.3, 115, 119, "lip", 117.5),
    ("Hess Rise", -178.0, 35.0, 99, 115, "lip", 105),
    ("C. Kerguelen Plateau", 75.0, -50.0, 100, 110, "lip", 105),
    ("Agulhas Plateau", 26.0, -39.0, 94, 100, "lip", 97),
    ("Maud Rise", 3.0, -66.0, 94, 100, "lip", 97),
    ("Broken Ridge", 95.0, -31.0, 94, 96, "lip", 95),
    ("Marion", 37.6, -46.9, 0, 92, "plume", None),
    ("Trindade", -28.8, -20.5, 0, 85, "plume", None),
    ("Afanasy Nikitin", 83.0, -3.0, 0, 80, "plume", None),
    ("Madeira", -17.3, 32.6, 0, 70, "plume", None),
    ("Bermuda", -64.3, 32.6, 0, 47, "plume", None),
    ("N. Kerguelen Plateau", 69.0, -49.0, 34, 40, "lip", 35),
    ("Discovery", -2.7, -43.0, 0, 40, "plume", None),
    ("Macdonald", -140.3, -29.0, 0, 34, "plume", None),
    ("Cobb", -130.1, 46.0, 0, 33, "plume", None),
    ("East Australia", 143.0, -38.0, 0, 33, "plume", None),
    ("Yemen Traps", 44.5, 15.0, 27, 31, "lip", 30),
    ("Caroline", 164.4, 4.8, 0, 30, "plume", None),
    ("Juan Fernandez", -81.8, -33.9, 0, 30, "plume", None),
    ("Marie Byrd Land", -126.0, -77.0, 0, 30, "plume", None),
    ("Fernando de Noronha", -32.4, -3.8, 0, 30, "plume", None),
    ("Lord Howe", 159.2, -34.7, 0, 28, "plume", None),
    ("Samoa", -168.2, -14.5, 0, 24, "plume", None),
    ("Bowie", -134.8, 53.0, 0, 24, "plume", None),
    ("Tasmantid", 155.5, -40.4, 0, 24, "plume", None),
    ("Foundation", -111.1, -37.7, 0, 21, "plume", None),
    ("Comores", 43.3, -11.5, 0, 20, "plume", None),
    ("Pitcairn", -129.3, -25.4, 0, 11, "plume", None),
    ("Society (Tahiti)", -148.4, -18.2, 0, 5, "plume", None),
]


def hotspots():
    return [{"n": n, "lon": lo, "lat": la, "a0": a0, "a1": a1, "k": k,
             **({"peak": p} if p is not None else {})}
            for (n, lo, la, a0, a1, k, p) in HOTSPOTS]


# ------------------------------------------------------------------ labels --
# t: continent | ocean | sea | orogen ; a0/a1 = age window (future negative)
# Coordinates here are PRESENT-DAY positions, and that is load-bearing: it is
# what lets build_labels back-advect a name along the plate that carries it.
# Eighteen terranes had been authored at their PALAEO-positions instead --
# where they sat in their own era -- which the "is this land today" gate
# correctly rejected, so they went untracked and fell back to snapLabel's
# 90-degree search for any matching terrain. That search finds whatever is
# nearest, not whatever is right. Anchor a terrane on the ground it BECAME.
# A window that ends before 0 is a claim that the feature is GONE. Ten belts
# that are still standing said so -- the Urals, the Pyrenees, the
# Transantarctics, the Caledonian remnant in Scotland and Norway -- and
# simply vanished off the map partway through the Cenozoic. Eroded is not
# the same as absent, and the Appalachians (470-0) already had it right.
# Supercontinent label windows are kept in step with the spans their cards
# claim in the left rail. They had drifted apart -- the panel said Gondwana
# was still breaking up at 30 Ma while its name left the map at 150, and
# every one of the nine disagreed at one end or the other. A reader who
# checks one against the other should not find two different answers.
LABELS = [
    # ---------- present / Cenozoic ----------
    ("continent", "North America", -100,  45,  -30,  150),
    ("continent", "South America",  -60, -15,  -30, 110),
    ("continent", "Africa",          20,   5,  -40, 150),
    ("continent", "Eurasia",         90,  55,  -20,  250),
    ("continent", "Australia",      135, -25,  -20,  45),
    ("continent", "Antarctica",     135, -82,  -40, 160),
    ("continent", "India",           78,  22,    0,  130),
    ("ocean", "Pacific Ocean",     -150,   0,  -10, 160),
    ("ocean", "Atlantic Ocean",     -30,  10,    0, 175),
    ("ocean", "Indian Ocean",        75, -30,    0, 120),
    ("ocean", "Southern Ocean",       0, -62,    0,  30),
    ("ocean", "Arctic Ocean",         0,  85,    0,  55),
    ("sea", "Mediterranean",         18,  36,    0,  28),
    ("sea", "Paratethys",            45,  45,   5,  34),
    ("orogen", "Himalaya",           85,  30,    0,  55),
    ("orogen", "Andes",             -70, -20,    0,  60),
    ("orogen", "Rocky Mountains",  -112,  43,    0,  60),
    ("orogen", "Alps",               10,  46,    0,  35),
    ("orogen", "Atlas",              -4,  32,    0,  40),
    # ---------- Mesozoic ----------
    ("continent", "Laurasia",        40,  50,  150, 250),
    ("continent", "Gondwana",        30, -40,  120, 650),
    ("ocean", "Tethys Ocean",        90,   5,  120, 260),
    ("ocean", "Panthalassa",       -150,   0,  160, 320),
    ("sea", "Western Interior Seaway", -95, 45, 72, 100),
    ("sea", "Turgai Strait",         65,  50,   29, 160),
    ("sea", "Eromanga Sea",         140, -28,   95, 125),
    ("orogen", "Cordillera",       -115,  40,   0, 150),
    ("orogen", "Sevier-Laramide",  -108,  42,   55,  95),
    # ---------- Pangaea ----------
    ("continent", "Pangaea",         10,   5,  130, 340),
    ("ocean", "Paleo-Tethys",       100,   0,  200, 420),
    ("sea", "Zechstein Sea",         12,  25,  252, 262),
    ("orogen", "Central Pangaean Mts", -5, 10, 250, 330),
    ("orogen", "Ural Mountains",     58,  55,  0, 320),
    ("orogen", "Appalachians",      -80,  38,  0, 470),
    ("orogen", "Variscan Belt",       5,  22,  280, 360),
    # ---------- Paleozoic ----------
    ("continent", "Laurussia (Euramerica)", -20, 10, 175, 430),
    ("continent", "Laurentia",      -60,   5,  430, 600),
    ("continent", "Baltica",         10,  -35,  430, 540),
    ("continent", "Siberia",         90,  20,  430, 600),
    ("continent", "Avalonia",       -18,  -35,  430, 490),
    ("continent", "Cimmeria",        60,  25,  180, 290),
    ("ocean", "Iapetus Ocean",      -30,  20,  400, 600),
    ("ocean", "Rheic Ocean",        -10, -20,  320, 490),
    ("ocean", "Panthalassic Ocean", -150,  0,  330, 540),
    ("sea", "Sauk Sea",             -70,  10,  480, 530),
    ("orogen", "Caledonides",       -12,  25,  0, 440),
    ("orogen", "Acadian Belt",      -48,  -10,  355, 420),
    ("orogen", "Taconic Belt",      -55,  12,  440, 470),
    # ---------- Precambrian ----------
    ("continent", "Gondwana (assembling)", 25, -45, 540, 600),
    ("continent", "Pannotia",        10, -40,  540, 650),
    ("continent", "Rodinia",        -10,   0,  700, 1000),
    ("ocean", "Mirovia",           -140,   0,  720, 1000),
    ("ocean", "Panthalassic (proto)", 150, -10, 600, 720),
    ("orogen", "Pan-African Belt",   20, -25,  550, 650),
    ("orogen", "Grenville Belt",    -25,  15,  900, 1000),
    # ---------- future ----------
    ("continent", "Pangaea Proxima", 30,   5, -250, -80),
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
    # Ends at 10 Ma, not 3 Ma, because that is where THIS MAP closes it. The
    # last shallow connection really did survive to ~2.8 Ma, but a strait a few
    # tens of km wide is finer than a 20 km global DEM can hold, so a label
    # running to 3 Ma sat over a seaway the viewer could not see. The remaining
    # history is in the description instead of being asserted by a label.
    ("sea",   "Central American Sea", -80,  9,   10,  40),
    ("sea",   "Hudson Seaway",      -85,  58,   66, 100),
    ("orogen", "Alleghanian Belt",  -80,  36,  258, 325),
    ("orogen", "Ouachita Belt",     -94,  34,  278, 320),
    ("orogen", "Antler Belt",      -117,  40,  318, 360),
    ("orogen", "Transantarctic Mts", 160, -80,  0, 560),
    ("orogen", "Verkhoyansk Belt",   130,  67,  0, 162),
    ("orogen", "Cadomian Belt",       -2,  48,  538, 650),
    ("orogen", "Timanian Belt",       -8, -14,  548, 620),
    ("orogen", "Cimmerian Belt",      55,  35,  190, 250),
    ("orogen", "Innuitian Belt",     -85,  78,  340, 385),
    ("continent", "Amazonia",        -55, -10,  545, 900),
    ("continent", "Congo Craton",     20,  -3,  545, 950),
    ("continent", "Kalahari Craton", 24, -26, 545, 700),
    ("continent", "Kalahari Craton", 30, -50, 700, 950),
    # Reaches into the Early Cretaceous so the Jehol biota (~135-120 Ma) is
    # clickable where it belongs: the block is a recognisable part of Asia
    # through the Mesozoic even after it welds on.
    ("continent", "North China", 115, 39, 120, 420),
    ("continent", "North China", 130, 5, 420, 900),
    ("continent", "South China", 110, 26, 200, 420),
    ("continent", "South China", 125, -10, 420, 900),
    # ---------- imported from the paleogeographic-feature audit ----------
    # Deserts, seaways, forests, ice sheets, basins, rifts and named regions:
    # the categories the original catalogue had no entries for at all.
    # -- basin --
    ("basin", "Amundsen Basin", -40, 18, 780, 1000),
    ("basin", "Mackenzie Mountains Basin", -50, 10, 780, 1000),
    ("basin", "Officer Basin", 120, -28, 700, 834),
    ("basin", "Centralian Superbasin", 112, -18, 700, 830),
    ("basin", "Michigan Basin", -85, 5, 350, 445),
    ("basin", "Catskill Delta", -45, -14, 358, 385),
    ("basin", "Permian Basin", -102, 2, 251, 305),
    ("basin", "Karoo Basin", 22, -58, 180, 300),
    ("basin", "Songliao Basin", 124, 45, 80, 135),
    ("basin", "Green River Lakes", -109, 41, 48, 54),
    # -- continent --
    ("continent", "West Africa Craton", -12, -5, 545, 1000),
    ("continent", "Australia-East Antarctica", 130, -30, 700, 1000),
    ("continent", "Sao Francisco Craton", -42, -13, 545, 950),
    ("continent", "Amasia", 70, 75, -250, -150),
    # -- desert --
    ("desert", "Rotliegend Desert", 10, 16, 288, 299),
    ("desert", "Coconino Erg", -105, 6, 272, 285),
    ("desert", "Navajo Erg", -110, 15, 190, 200),
    ("desert", "Botucatu Erg", -48, -27, 132, 148),
    ("desert", "Gobi Erg", 103, 42, 70, 86),
    ("desert", "Namib", 14, -24, 0, 30),
    ("desert", "Sahara", 12, 22, 0, 7),
    ("desert", "Taklamakan", 83, 39, 0, 7),
    ("desert", "Proxima Interior Desert", 10, 18, -250, -130),
    # -- forest --
    ("forest", "Gilboa Forest", -45, -18, 382, 392),
    ("forest", "Euramerican Coal Forests", -35, 0, 299, 325),
    ("forest", "Cathaysian Coal Forests", 110, 3, 255, 310),
    ("forest", "Angaran Flora Belt", 95, 55, 250, 305),
    ("forest", "Glossopteris Flora", 30, -58, 250, 298),
    ("forest", "Jehol Forests", 120, 43, 121, 135),
    ("forest", "Antarctic Nothofagus Forest", -60, -67, 30, 58),
    ("forest", "Arctic Azolla Bloom", 10, 84, 48, 50),
    ("forest", "Pebas Mega-Wetland", -70, -5, 10, 23),
    ("forest", "Amazon Rainforest", -62, -4, 0, 10),
    # -- grassland --
    ("grassland", "Great Plains", -100, 41, 0, 18),
    ("grassland", "Eurasian Steppe", 65, 48, 0, 14),
    ("grassland", "African Savanna", 30, -3, 0, 10),

    # Tundra. Treeless ground where the growing season is too short and too
    # cold for wood, not simply "cold desert" -- it is one of the largest
    # biomes on Earth and the app had no name for any of it. Coordinates are
    # present-day and ride the plate tracks like every other land label.
    ("tundra", "Arctic Tundra", 100, 71, 0, 5),
    ("tundra", "Nearctic Tundra", -95, 67, 0, 5),
    # On the Alaskan side, not in the strait: Beringia was land only while sea
    # level was low, so a label at 170W today sits in 44 m of water.
    ("tundra", "Beringian Steppe-Tundra", -157, 66, 0, 2.6),
    ("tundra", "Tibetan Alpine Tundra", 88, 33, 0, 15),
    ("tundra", "Antarctic Tundra", 65, -70, 16, 34),
    ("tundra", "Gondwanan Polar Tundra", 25, -75, 285, 320),
    # -- ice --
    ("ice", "Sturtian Snowball Earth", 0, 0, 661, 717),
    ("ice", "Marinoan Snowball Earth", 120, 0, 635, 650),
    ("ice", "Gaskiers Glaciation", -30, -45, 579, 582),
    ("ice", "Hirnantian Ice Sheet", 0, -80, 443, 447),
    # The Famennian ice on high-latitude Gondwana. Anchored on the Parana
    # Basin, whose crust sat at 73 S at 360 Ma -- the Andean deposits are
    # closer to the type sections but their crust tracks back to open ocean.
    # Contested, and labelled as such. The Early Cretaceous glendonites and
    # dropstones are in SE Australia, whose crust sat inside the Antarctic
    # circle at 145 Ma. No continental sheet is accepted -- this marks a cold
    # polar region, not an ice age.
    ("ice", "Cretaceous Polar Ice (disputed)", 145, -38, 125, 152),
    ("ice", "Late Devonian Ice Sheet", -50, -25, 355, 368),
    ("ice", "Karoo Ice Sheet", 20, -70, 258, 340),
    ("ice", "East Antarctic Ice Sheet", 90, -78, 0, 34),
    ("ice", "Laurentide Ice Sheet", -90, 58, 0, 3),
    ("ice", "Fennoscandian Ice Sheet", 20, 63, 0, 3),
    # future projection only: "East Antarctic Ice Sheet" already covers 0-34 Ma,
    # and letting this one reach 0 printed both names on the present-day map
    ("ice", "Antarctic Ice Sheet", 20, -84, -35, -1),
    # -- island --
    ("island", "Carolina Terrane", -80, 35, 470, 600),
    ("island", "Oaxaquia", -96, 17, 450, 540),
    ("island", "Perunica", 14, 50, 440, 500),
    ("island", "Armorica", -3, 48, 380, 470),
    ("island", "Hun Superterrane", 20, -30, 380, 455),
    ("island", "Sibumasu", 99, 17, 210, 300),
    ("island", "Lhasa Terrane", 91, 30, 130, 250),
    ("island", "Greater Adria", 16, 41, 140, 240),
    ("island", "Wrangellia Terrane", -142, 61, 150, 232),
    ("island", "Greater India", 78, 22, 60, 130),
    ("island", "Kerguelen Microcontinent", 72, -52, 90, 118),
    ("island", "Zealandia", 172, -43, 0, 80),
    ("island", "Baja Island", -118, 34, -40, -5),
    ("island", "Somalia", 48, 0, -100, -15),
    # -- ocean --
    ("ocean", "Neotethys", 62, 0, 45, 270),
    ("ocean", "East African Ocean", 42, -3, -130, -25),
    # -- orogen --
    ("orogen", "Sveconorwegian Belt", 5, 25, 900, 1000),
    ("orogen", "Sunsas Belt", -60, -20, 940, 1000),
    ("orogen", "Irumide Belt", 25, -12, 950, 1000),
    ("orogen", "Brasiliano Belt", -45, -25, 540, 650),
    ("orogen", "East African Orogen", 42, -10, 550, 650),
    ("orogen", "Damara Belt", 16, -22, 530, 590),
    ("orogen", "Kuunga Orogen", 80, 7, 500, 570),
    ("orogen", "Central Asian Orogenic Belt", 88, 40, 250, 420),
    ("orogen", "Famatinian Belt", -66, -29, 440, 482),
    ("orogen", "Cape Fold Belt", 21, -33, 0, 290),
    ("orogen", "Qinling-Dabie Belt", 110, 25, 0, 250),
    ("orogen", "Sierra Nevada Arc", -119, 37, 0, 160),
    ("orogen", "Australasian Belt", 128, 3, -80, -10),
    # -- plateau --
    ("plateau", "Tibetan Plateau", 88, 33, 0, 40),
    ("plateau", "Colorado Plateau", -111, 37, 0, 30),
    ("plateau", "Altiplano", -67, -19, 0, 25),
    # -- region --
    ("region", "Avalon Deep-Water Realm", -30, -50, 559, 580),
    ("region", "White Sea Realm", 40, -35, 550, 560),
    ("region", "Old Red Sandstone Continent", -3, 52, 360, 418),
    ("region", "Wallacea", 122, -3, 0, 15),
    ("region", "Beringia", -168, 65, 0, 3),
    ("region", "Sundaland", 108, 3, 0, 3),
    # -- rift --
    ("rift", "Midcontinent Rift", -35, 18, 985, 1000),
    ("rift", "Adelaide Rift Complex", 125, -30, 660, 830),
    ("rift", "Oslo Rift", 10, 14, 288, 300),
    ("rift", "Newark Rift Valleys", -68, 12, 190, 232),
    ("rift", "Benue Trough", 9, -5, 80, 130),
    ("rift", "Rhine Graben", 8, 49, 0, 35),
    ("rift", "East African Rift", 36, 2, 0, 30),
    ("rift", "Red Sea Rift", 38, 20, 0, 25),
    ("rift", "Baikal Rift", 108, 53, 0, 25),
    ("rift", "Pan-Asian Rift", 80, 55, -90, -15),
    # -- sea --
    ("sea", "Bitter Springs Sea", 118, -15, 780, 812),
    ("sea", "Nama Sea", 16, -35, 538, 551),
    ("sea", "Tippecanoe Sea", -62, 10, 418, 490),
    ("sea", "Kaskaskia Sea", -60, 0, 360, 418),
    ("sea", "Absaroka Sea", -75, 3, 252, 330),
    ("sea", "Muschelkalk Sea", 12, 22, 237, 247),
    ("sea", "Viking Corridor", 2, 42, 155, 195),
    ("sea", "Hispanic Corridor", -55, 5, 150, 190),
    ("sea", "Boreal Sea", 45, 70, 90, 190),
    ("sea", "Solnhofen Lagoon", 11, 25, 149, 152),
    ("sea", "Mowry Sea", -100, 50, 95, 103),
    ("sea", "Bearpaw Sea", -104, 50, 72, 78),
    ("sea", "Cannonball Sea", -100, 47, 58, 62),
    ("sea", "Lake Pannon", 19, 46, 4, 11),
    ("sea", "Messinian Salt Basin", 16, 37, 5, 6),
    ("sea", "Afar Seaway", 41, 13, -35, -3),
    ("sea", "Pangaea Proxima Inland Sea", 28, 8, -250, -140),
    # ---------- named palaeolakes (research: lakes are point features at
    # this resolution; sea level and lake level are decoupled) ----------
    ("lake", "Songliao Palaeolake", 124.0, 45.0, 80.0, 135.0),
    ("lake", "Jehol Lakes", 120.0, 42.0, 120.0, 135.0),
    ("lake", "Lake Gosiute", -109.0, 41.5, 48.5, 53.5),
    ("lake", "Lake Uinta", -110.0, 39.8, 43.0, 53.5),
    ("lake", "Fossil Lake", -110.8, 41.9, 50.0, 52.0),
    ("lake", "Messel Lake", 8.75, 49.9, 47.0, 48.0),
    ("lake", "Lake Baikal", 108.0, 53.5, 0.0, 30.0),
    ("lake", "Pebas Mega-Wetland", -70.0, -5.0, 10.0, 23.0),
    ("lake", "Lake Vostok", 106.0, -77.0, 0.0, 15.0),
    ("lake", "Lake Tanganyika", 29.5, -6.0, 0.0, 12.0),
    ("lake", "Lake Pannon", 19.0, 46.0, 4.5, 11.6),
    ("lake", "East African Rift soda lakes", 36.0, 0.5, 0.0, 7.0),
    ("lake", "Lago Mare (Messinian Mediterranean)", 16.0, 37.0, 5.33, 5.6),
    ("lake", "Caspian Sea (Paratethys remnant)", 51.0, 42.0, 0.0, 5.5),
    ("lake", "Black Sea (Paratethys remnant)", 34.0, 43.0, 0.0, 5.5),
    ("lake", "Lake Titicaca", -69.5, -15.8, 0.0, 3.0),
    ("lake", "Lake Victoria", 33.0, -1.0, 0.0, 0.4),
    ("lake", "Palaeolake Makgadikgadi", 25.5, -20.5, 0.01, 0.3),
    ("lake", "Lake Manly", -117.0, 36.3, 0.01, 0.186),
    ("lake", "Lake Lisan", 35.5, 31.5, 0.014, 0.07),
    ("lake", "Lake Bonneville", -113.0, 40.5, 0.013, 0.03),
    ("lake", "Lake Lahontan", -119.0, 40.0, 0.013, 0.03),
    ("lake", "Lake Tauca", -68.0, -19.5, 0.0141, 0.0181),
    ("lake", "Lake Agassiz", -95.0, 50.0, 0.0082, 0.015),
    # Proglacial lakes: meltwater dammed BY the ice itself, against the sheet's
    # own margin or behind the moraine it left. They exist only while the ice is
    # going, which makes them the shortest-lived large lakes there are -- and
    # the most violent, because the dam is made of the thing that is melting.
    ("lake", "Glacial Lake Missoula", -114.5, 47.3, 0.0135, 0.0185),
    ("lake", "Glacial Lake Ojibway", -79.5, 50.5, 0.0082, 0.0105),
    ("lake", "Lake Algonquin", -83.5, 45.5, 0.0102, 0.0135),
    ("lake", "Baltic Ice Lake", 19.0, 58.5, 0.0116, 0.0143),
    ("lake", "West Siberian Ice-Dammed Lake", 72.0, 61.0, 0.058, 0.09),
    ("lake", "Karoo Proglacial Lakes", 24.0, -31.0, 292.0, 302.0),
    ("lake", "Laurentian Great Lakes", -84.0, 45.5, 0.0, 0.014),
    ("lake", "Lake Mega-Chad", 15.0, 13.0, 0.005, 0.011),
    # ---------- timeline audit additions: key features that were missing.
    # Present-day coordinates; the app relocates drifting ones. Large igneous
    # provinces (Deccan, Siberian Traps, Ontong Java, Shatsky, Manihiki,
    # Caribbean, Columbia River, Parana-Etendeka, CAMP, Kerguelen) are NOT here
    # -- they already live in the volcanism / hotspot layer. ----------
    # -- Alpine-Himalayan and other orogens --
    ("orogen", "Zagros Mts", 50, 32, 0, 35),
    ("orogen", "Greater Caucasus", 44, 43, 0, 30),
    ("orogen", "Pyrenees", 1, 43, 0, 83),
    ("orogen", "Carpathians", 24, 48, 0, 34),
    ("orogen", "Apennines", 13, 43, 0, 23),
    ("orogen", "Sonoma Orogeny", -117, 41, 240, 260),
    ("orogen", "Lachlan Orogen", 148, -35, 0, 485),
    # -- rifts / extensional provinces --
    ("rift", "Rio Grande Rift", -106, 34, 0, 36),
    ("rift", "Basin and Range", -117, 39, 0, 36),
    ("rift", "Gulf of California", -111, 27, 0, 12),
    ("rift", "West Antarctic Rift", 180, -80, 0, 105),
    # -- seas / marginal basins --
    ("sea", "Gulf of Mexico", -90, 25, 0, 170),
    ("sea", "West Siberian Sea", 75, 62, 30, 100),
    ("sea", "Tasman Sea", 160, -38, 0, 85),
    ("sea", "South China Sea", 115, 14, 0, 33),
    # -- named mid-ocean ridges (linear features, marked at a mid-point) --
    ("ocean", "Mid-Atlantic Ridge", -30, 0, 0, 170),
    ("ocean", "East Pacific Rise", -108, -15, 0, 30),
    # -- deserts --
    ("desert", "Atacama Desert", -69, -24, 0, 15),
    ("desert", "Arabian Desert", 50, 20, 0, 23),
    ("desert", "Kalahari Desert", 22, -23, 0, 30),
    ("desert", "Australian Desert", 133, -26, 0, 15),
    ("desert", "Patagonian Desert", -69, -46, 0, 15),
    # -- ice sheets (Pleistocene pairs of the Laurentide) --
    ("ice", "Cordilleran Ice Sheet", -125, 54, 0, 2.6),
    ("ice", "Greenland Ice Sheet", -42, 72, 0, 3.5),
    ("ice", "Patagonian Ice Sheet", -73, -48, 0, 2.6),
    # -- plateaus / uplifts --
    # Named for the flood basalt, not just the landform. The Deccan Traps have
    # a marker in the volcanism layer, but that layer is OFF by default, so
    # with it hidden the largest igneous province on the map had no name at
    # all -- only "Deccan Plateau", which reads as ordinary high ground.
    # A fill pass for the thin parts of the timeline. The map carried 88
    # names at the present and 40 at 36 Ma, 26 at 200 Ma and 11 at 1000 --
    # so travelling back felt like the world emptying out rather than
    # changing. These are all well-attested and mostly Eurasian, which is
    # where the gap was worst.
    ("continent", "Kazakhstania", 68, 48, 300, 540),
    ("ocean", "Mongol-Okhotsk Ocean", 115, 50, 130, 330),
    ("continent", "Tarim Block", 84, 40, 0, 540),
    ("continent", "Amuria", 122, 47, 0, 300),
    ("continent", "Annamia", 105, 17, 0, 400),
    ("basin", "Junggar Basin", 87, 45, 0, 300),
    ("basin", "Ordos Basin", 108, 37, 0, 250),
    ("basin", "Sichuan Basin", 105, 30, 0, 230),
    ("basin", "Qaidam Basin", 95, 37, 0, 50),
    ("basin", "West Siberian Basin", 73, 60, 0, 250),
    ("orogen", "Tien Shan", 80, 42, 0, 320),
    ("orogen", "Altai Belt", 89, 49, 0, 400),
    ("orogen", "Kunlun Belt", 90, 36, 0, 250),
    ("orogen", "Qilian Belt", 99, 38, 0, 420),
    ("orogen", "Alborz Belt", 52, 36, 0, 40),
    ("orogen", "Pontide Arc", 35, 41, 0, 90),
    ("orogen", "Bohemian Massif", 14, 49, 0, 340),
    ("orogen", "Iberian Massif", -6, 40, 0, 340),
    ("orogen", "Massif Central", 3, 45, 0, 340),
    ("orogen", "Rhodope Massif", 25, 41, 0, 120),
    ("orogen", "Ellesmerian Belt", -85, 79, 0, 360),
    ("region", "Fennoscandian Shield", 25, 64, 0, 540),
    ("continent", "Anatolide-Tauride Block", 32, 38, 0, 250),
    ("island", "Kolyma-Omolon Terrane", 155, 65, 0, 250),
    ("ocean", "Piedmont-Ligurian Ocean", 8, 45, 35, 170),
    ("sea", "Okhotsk Sea", 148, 55, 0, 30),
    ("sea", "Sea of Japan", 135, 40, 0, 25),
    ("region", "Tethyan Himalaya", 88, 29, 0, 250),
    ("region", "Morrison Floodplain", -108, 40, 145, 157),
    ("island", "Yakutat Terrane", -140, 60, 0, 50),
    ("orogen", "Baikalian Belt", 105, 55, 300, 850),
    ("orogen", "Hangai Uplift", 99, 47, 0, 30),
    ("plateau", "Deccan Traps", 76, 18, 0, 66),
    ("plateau", "Ethiopian Highlands", 39, 9, 0, 31),
    ("plateau", "East African Plateau", 35, -2, 0, 25),
    # -- basins / regions --
    ("basin", "Williston Basin", -103, 48, 0, 400),
    ("region", "Sahul", 140, -12, 0.01, 2.6),
    ("region", "Doggerland", 3, 55, 0.008, 0.02),
]


def labels():
    return [{"t": t, "n": n, "lon": lo, "lat": la, "a0": a0, "a1": a1}
            for (t, n, lo, la, a0, a1) in LABELS]


# Approximate rendered radius (degrees) for each named lake, so the app can draw
# it as a water body sized roughly to its real extent, with a small floor so the
# tiny ones stay visible at global scale. Unlisted lakes use LAKE_R_DEF.
LAKE_R_DEF = 0.6
LAKE_R = {
    "Caspian Sea (Paratethys remnant)": 3.0, "Black Sea (Paratethys remnant)": 2.2,
    "Laurentian Great Lakes": 2.2,
    "Lake Agassiz": 3.2, "Lake Bonneville": 1.4,
    "Glacial Lake Missoula": 1.5, "Glacial Lake Ojibway": 2.6,
    "Lake Algonquin": 2.0, "Baltic Ice Lake": 2.8,
    "West Siberian Ice-Dammed Lake": 4.2, "Karoo Proglacial Lakes": 2.4,
    "Lake Lahontan": 1.2, "Lake Mega-Chad": 2.6, "Lake Pannon": 2.6,
    "Pebas Mega-Wetland": 3.2, "Songliao Palaeolake": 2.0, "Jehol Lakes": 1.6,
    "Lake Baikal": 0.9, "Lake Victoria": 1.2, "Lake Tanganyika": 0.9,
    "Lake Titicaca": 0.5, "Lake Vostok": 0.6, "Lake Gosiute": 1.0,
    "Lake Uinta": 0.9, "Fossil Lake": 0.4, "Messel Lake": 0.3,
    "Lago Mare (Messinian Mediterranean)": 3.5, "East African Rift soda lakes": 1.3,
    "Lake Manly": 0.9, "Lake Lisan": 0.6, "Lake Tauca": 1.1,
    "Palaeolake Makgadikgadi": 1.4,
}


def lake_radius(name):
    return LAKE_R.get(name, LAKE_R_DEF)


# Real morphology so lakes read as their actual shapes, not symmetric blobs.
# Each lake is one or more LOBES; a lobe is
#   (dlon, dlat, length_km, width_km, azimuth_deg)
# where (dlon,dlat) offsets the lobe from the label's coordinate (degrees), the
# ellipse is length_km by width_km, and azimuth is the long axis measured
# clockwise from north. Multi-lobe entries capture clusters (the Great Lakes are
# five separate lakes; the Jehol biota sat in a string of rift lakes). The app
# adds the lobe to the lake's plate-relocated position and draws an oriented,
# irregular-shored water body. Dimensions are real where the lake is real and
# reconstructed from the basin where it is a palaeolake.
LAKE_SHAPE = {
    "Lake Baikal":            [(0, 0, 636, 55, 25)],
    "Lake Tanganyika":        [(0, 0, 676, 55, 345)],
    "Lake Victoria":          [(0, 0, 337, 250, 5)],
    "Lake Titicaca":          [(0, 0, 190, 80, 320)],
    "Lake Vostok":            [(0, 0, 250, 55, 30)],
    "East African Rift soda lakes": [(0, 0, 650, 90, 358)],
    "Laurentian Great Lakes": [(-3.6, 2.3, 600, 250, 104),   # Superior (clearly largest)
                               (-3.1, -1.5, 500, 175, 4),    # Michigan (N-S body)
                               (-4.7, 0.1, 200, 52, 36),     # Green Bay (Michigan's NW arm)
                               (1.9, -0.5, 300, 205, 150),   # Huron (main body)
                               (3.5, 0.5, 205, 100, 140),    # Georgian Bay (Huron's NE lobe)
                               (2.9, -3.3, 400, 90, 71),     # Erie (elongated ENE-WSW)
                               (6.3, -1.7, 320, 86, 80)],    # Ontario (E-W)
    "Songliao Palaeolake":    [(0, 0, 820, 380, 20)],
    "Jehol Lakes":            [(-0.9, 0.6, 130, 60, 40),
                               (0.6, -0.4, 110, 55, 25),
                               (-0.2, -1.3, 95, 48, 55)],
    "Lake Gosiute":           [(0, 0, 240, 130, 65)],
    "Lake Uinta":             [(0, 0, 250, 120, 90)],
    "Fossil Lake":            [(0, 0, 80, 40, 0)],
    "Messel Lake":            [(0, 0, 30, 22, 0)],
    "Palaeolake Makgadikgadi":[(0, 0, 300, 250, 50)],
    "Lake Manly":             [(0, 0, 160, 20, 340)],
    "Lake Lisan":             [(0, 0, 220, 17, 2)],
    "Lake Bonneville":        [(0, 0, 520, 220, 358)],
    "Lake Lahontan":          [(0, 0, 430, 260, 340)],
    "Lake Tauca":             [(0, 0, 660, 210, 340)],
    "Lake Agassiz":           [(0, 0, 1100, 400, 335)],
    # Missoula filled the Clark Fork valleys behind an ice dam in the Purcell
    # Trench -- a branching lake in mountain valleys, not an open sheet.
    "Glacial Lake Missoula":  [(0, 0, 330, 60, 300), (-0.6, -0.5, 210, 55, 20),
                               (0.9, 0.4, 190, 50, 345)],
    "Glacial Lake Ojibway":   [(0, 0, 900, 320, 285)],
    "Lake Algonquin":         [(0, 0, 520, 190, 300), (1.6, -0.9, 330, 150, 260)],
    "Baltic Ice Lake":        [(0, 0, 950, 330, 30)],
    # The Barents-Kara ice sheet blocked every north-flowing Siberian river at
    # once, so the Ob and Yenisei backed up into a lake the size of a sea.
    "West Siberian Ice-Dammed Lake": [(0, 0, 1600, 750, 10)],
    "Karoo Proglacial Lakes": [(0, 0, 620, 240, 275), (-3.5, 1.2, 420, 180, 300)],
    "Lake Mega-Chad":         [(0, 0, 700, 620, 0)],
    "Pebas Mega-Wetland":     [(0, 0, 1050, 720, 340)],
    "Caspian Sea (Paratethys remnant)": [(0, 0, 1200, 320, 358)],
    "Black Sea (Paratethys remnant)":   [(0, 0, 1150, 380, 90)],
    "Lago Mare (Messinian Mediterranean)": [(0, 0, 3200, 1400, 90)],
}


def lake_shape(name):
    """Lobes as [dlon, dlat, semiMajorDeg, semiMinorDeg, azimuthDeg]."""
    lobes = LAKE_SHAPE.get(name)
    if lobes is None:                       # unlisted: a mildly elongated blob
        r = lake_radius(name)
        return [[0.0, 0.0, r, r * 0.72, 0.0]]
    return [[dl, da, lk / 222.0, wk / 222.0, az]      # km -> semi-axis in degrees
            for (dl, da, lk, wk, az) in lobes]


# ------------------------------------------------------------ descriptions --
# Narrative context for the info panel. The panel also reports live measured
# motion and elevation, so these supply the story the numbers cannot.
# A paleocontinent is not a point. Gondwana, Laurentia, Baltica and the rest were
# authored here as single (lon, lat) coordinates in nobody's particular frame,
# and the app then hunted outward from them for any matching terrain -- up to 90
# degrees. That search is unstable by construction: it re-runs against whichever
# keyframe field the age happens to sample, so a name hops between landmasses as
# the age crosses a keyframe. Measured before this table existed: the Gondwana
# label sat on the EQUATOR from 430 to 420 Ma and then jumped 54 degrees south;
# Siberia moved 72 then 101 degrees between Cambrian frames; and Laurentia --
# whose coordinate (-60, 5) is in the Amazon basin -- was tracked on SOUTH
# AMERICAN crust and drawn near Antarctica, south of Gondwana, through the whole
# early Palaeozoic.
#
# So define each one the way a geologist would locate it: by where the crust of
# its MODERN FRAGMENTS actually sat at that age. build_webdata.build_labels
# back-advects every anchor below along the Merdith rotation model (with the
# PaleoDEM frame correction applied) and takes the spherical centroid, giving a
# smooth per-age track instead of a search.
#
#   modern  - present-day points on the craton, which must be LAND today so the
#             rotation model can assign them a plate. Pick craton interior, not
#             accreted margin: the Cordillera and the Appalachians were not part
#             of Laurentia in the Cambrian.
#   cratons - the equivalents in build_synthetic.PRE_KEYS, used past 540 Ma where
#             the map is the authored Precambrian composite rather than a real
#             DEM, blended across the same 540-600 handoff the terrain uses.
# Assignment order, biggest first. Each name claims a landmass and no two share
# one, so whoever goes first gets the pick -- a supercontinent must claim the
# supercontinent before a craton-sized name can take it. Pannotia and Gondwana
# were last in this list and ended up on leftovers, in open water.

# --- water features and belts, positioned the same way -------------------------
# An ocean basin has no surviving crust to track, but its MARGINS do: put anchors
# on both shores and the centroid falls in the basin between them. An
# epicontinental sea sits on crust that is dry land today, so its own footprint
# works. "target": "sea" snaps to water instead of land.
#
# Before this, every one of these was a static present-day coordinate evaluated
# in a reconstruction frame, so the Gulf of Mexico label sat at (-90, 25) at
# every age -- which at 170 Ma is open Panthalassa, not a gulf.
COMPOSITE_WATER = {
    "Gulf of Mexico": {
        "modern": [(-89, 20), (-82, 28), (-95, 29), (-91, 30), (-86, 22)],
        "target": "sea"},
    "Hudson Seaway": {
        "modern": [(-95, 58), (-78, 58), (-85, 52), (-88, 64)],
        "target": "sea"},
    "Central American Sea": {
        # the seaway between the Americas, before the isthmus closed it
        "modern": [(-80, 9), (-84, 10), (-76, 8), (-85, 12)],
        "target": "sea"},
    "Cannonball Sea": {
        "modern": [(-100, 47), (-101, 48), (-99, 46)], "target": "sea"},
    "Trans-Saharan Sea": {
        "modern": [(0, 18), (8, 16), (3, 13), (-2, 16)], "target": "sea"},
    "Western Interior Seaway": {
        "modern": [(-100, 45), (-104, 50), (-97, 40), (-101, 55)],
        "target": "sea"},
    "Turgai Strait": {
        "modern": [(65, 52), (68, 48), (62, 55)], "target": "sea"},
    "West Siberian Sea": {
        "modern": [(72, 62), (78, 65), (68, 58)], "target": "sea"},
    "Paratethys": {
        "modern": [(40, 45), (48, 44), (32, 46)], "target": "sea"},
    "Iapetus Ocean": {
        # Laurentian shore + Baltic/Avalonian shore: the centroid is the ocean
        "modern": [(-70, 47), (-55, 50), (-30, 70), (10, 60), (-3, 54), (16, 62)],
        "target": "sea"},
    "Rheic Ocean": {
        # north Gondwana against Avalonia and Laurussia
        "modern": [(-7, 32), (-12, 20), (5, 12), (-3, 52), (-63, 45), (2, 50)],
        "target": "sea"},
    "Paleo-Tethys": {
        # north Gondwana / Cimmeria against Laurasia
        "modern": [(33, 39), (55, 32), (88, 32), (68, 48), (95, 58), (78, 45)],
        "target": "sea"},
    "Ural Ocean": {
        "modern": [(52, 58), (58, 55), (85, 62), (75, 60), (65, 50)],
        "target": "sea"},
    "Tornquist Sea": {
        "modern": [(14, 55), (20, 52), (8, 58), (-3, 52)], "target": "sea"},
    "Adamastor Ocean": {
        # Precambrian: between the South American and African cratons
        "cratons": ["Amazonia", "SaoFrancisco", "WestAfrica", "Congo", "Kalahari"],
        "target": "sea"},
    "Mozambique Ocean": {
        # Precambrian: between the Congo/Kalahari side and India/East Antarctica
        "cratons": ["Congo", "Kalahari", "India", "EAntarctica"],
        "target": "sea"},
}

# Belts are land, but a single point cannot stand for a 5000 km orogen that
# assembled piecemeal. The Central Asian Orogenic Belt's coordinate sat off its
# terrain at every sampled age and jumped 30-40 degrees between frames.
COMPOSITE_BELTS = {
    "Central Asian Orogenic Belt": {
        "modern": [(60, 44), (68, 45), (80, 46), (90, 48), (103, 48)]},
}

COMPOSITE_ORDER = ["Pannotia", "Gondwana", "Gondwana (assembling)",
                   "Laurussia (Euramerica)", "Laurentia", "Siberia",
                   "Baltica", "Avalonia", "Cimmeria"]

COMPOSITE_LABELS = {
    # Cimmeria is a RIBBON: a string of fragments that rifted off the northern
    # margin of Gondwana in the Permian and drifted north across Palaeo-Tethys,
    # closing it ahead and opening Neotethys behind. Its pieces are Turkey,
    # Iran, Afghanistan, the Pamir, Tibet (Lhasa and Qiangtang) and Indochina.
    #
    # As a single authored coordinate it was untracked -- (60,25) is the Gulf of
    # Oman, so it failed the "is this land today" gate -- and snapLabel then
    # searched 90 degrees for any matching terrain and attached it to Laurasia
    # beside the Urals, a continent it had not reached and would collide with
    # rather than belong to. At 243 Ma the search found somewhere better and the
    # name jumped the width of an ocean.
    "Cimmeria": {
        "modern": [(33, 39), (52, 33), (65, 34), (72, 37),     # Turkey, Iran, Afghan
                   (88, 31), (95, 32), (101, 30),              # Lhasa, Qiangtang, E Tibet
                   (103, 20)],                                 # Indochina
    },
    "Gondwana": {
        "modern": [(-60, -5), (-55, -20), (-64, -33), (-45, -12),      # S America
                   (15, 5), (25, -20), (-6, 12), (33, 2), (28, -28),   # Africa
                   (45, 22), (47, -20),                                # Arabia, Madagascar
                   (78, 22), (133, -25), (120, -28),                   # India, Australia
                   (25, -75), (100, -75), (-60, -80)],                 # Antarctica
        "cratons": ["Amazonia", "WestAfrica", "Congo", "Kalahari", "Arabia",
                    "India", "Australia", "EAntarctica"],
    },
    "Gondwana (assembling)": {
        "modern": [(-60, -5), (-55, -20), (15, 5), (25, -20), (33, 2),
                   (78, 22), (133, -25), (25, -75), (100, -75)],
        "cratons": ["Amazonia", "WestAfrica", "Congo", "Kalahari", "Arabia",
                    "India", "Australia", "EAntarctica"],
    },
    "Laurentia": {
        "modern": [(-95, 55), (-105, 63), (-85, 50), (-75, 58), (-110, 55),
                   (-42, 72), (-50, 68)],
        "cratons": ["Laurentia"],
    },
    "Baltica": {
        "modern": [(16, 62), (28, 60), (38, 55), (24, 57), (32, 65)],
        "cratons": ["Baltica"],
    },
    "Siberia": {
        "modern": [(105, 64), (115, 60), (95, 67), (125, 65), (110, 70)],
        "cratons": ["Siberia"],
    },
    "Avalonia": {
        # rifted off Gondwana in the Ordovician; its fragments are now split
        # between Britain, Belgium and maritime Canada
        "modern": [(-2, 52), (-3, 51), (4, 51), (-63, 45), (-53, 47)],
    },
    "Laurussia (Euramerica)": {
        # Laurentia + Baltica welded by the Caledonian collision, plus Avalonia
        "modern": [(-95, 55), (-85, 50), (-75, 58), (-42, 72),
                   (16, 62), (28, 60), (24, 57), (-2, 52), (-56, 47)],
        "cratons": ["Laurentia", "Baltica"],
    },
    "Pannotia": {
        # the latest-Precambrian assembly: essentially everything at once
        "modern": [],
        "cratons": ["Laurentia", "Baltica", "Siberia", "Amazonia", "WestAfrica",
                    "Congo", "Kalahari", "India", "Australia", "EAntarctica"],
    },
}


DESCRIPTIONS = {

 "Mozambique Ocean": "The ocean between eastern and western Gondwana, closing in stages between about 600 and 550 Ma. Its closure welded the two halves together along the East African Orogeny, one of the great mountain-building events of the Precambrian.",
 "Adamastor Ocean": "The water that separated the Congo and Rio de la Plata cratons before Gondwana assembled -- how much of it was true oceanic crust rather than a wide continental rift is still argued. It closed along what is now the Brazil-Namibia suture -- and hundreds of millions of years later the South Atlantic reopened along almost the same line.",
 "Tornquist Sea": "The narrow sea between Baltica and Avalonia. Its closure was the first stage of the Caledonian collision, before Iapetus itself shut.",
 "Ural Ocean": "The ocean between Baltica and Siberia. Closing it raised the Urals and welded the last major piece of Pangaea into place.",
 "Sundance Sea": "A Jurassic arm of the Arctic reaching south into western North America, leaving the marine shales that underlie the Rocky Mountain foreland.",
 "Trans-Saharan Sea": "A shallow seaway flooding across West Africa during the Cretaceous high-stand, briefly separating the Sahara into islands.",
 "Central American Sea": "The open gap between North and South America, and the "
   "last place the Atlantic and Pacific were one ocean at the equator. The volcanic "
   "arc rising through it shoaled the seaway from the Miocene onward, which is where "
   "this map loses it; a narrow, shallow and probably intermittent connection "
   "survived until final closure around 2.8 Ma. Shutting it rerouted the Gulf "
   "Stream, and the land bridge that replaced it let the two continents swap their "
   "mammals -- the Great American Biotic Interchange.",
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

 # ---- descriptions for the imported features ----
 "Absaroka Sea": "The last great Palaeozoic flooding of North America, oscillating in and out with the "
  "growth and melting of Gondwana's ice sheets. Each cycle left a coal seam.",
 "Adelaide Rift Complex": "A deep rift trough that opened as Laurentia tore away from Australia, filling with "
  "over ten kilometres of sediment. Its upper beds hold the Ediacara fossils that gave "
  "the Ediacaran period its name.",
 "Afar Seaway": "The first stage of Africa's split, as the Red Sea and Gulf of Aden connect through the "
  "Afar depression and salt water pours into the rift. Much of Afar already sits below "
  "sea level, held back only by young lava.",
 "African Savanna": "Tropical grassland with scattered trees, expanded by late Miocene drying and by fire. "
  "It is the habitat in which upright walking and the human lineage appeared.",
 "Altiplano": "The world's second-highest plateau, lifted between two branches of the Andes as the "
  "crust thickened above the subducting Nazca plate. Its uplift began around 25 million "
  "years ago.",
 "Amasia": "A rival forecast: instead of the Atlantic closing, the Pacific does, and the northern "
  "continents crowd together over the Arctic. Which future happens depends on whether the "
  "Atlantic develops subduction zones.",
 "Amazon Rainforest": "The largest rainforest on Earth, established once the Andes rose high enough to turn "
  "the Amazon's drainage eastward and drain the old Pebas wetland.",
 "Amundsen Basin": "A broad epicratonic sea on Rodinia's northwestern margin, whose Shaler Supergroup "
  "carbonates -- over a kilometre thick -- record shallow, stromatolite-building water "
  "intermittently mixed with the open ocean.",
 "Angaran Flora Belt": "Cool-temperate forest across Siberia, dominated by the seed plant Cordaites and "
  "dropping leaves seasonally -- the first clearly deciduous vegetation, adapted to a "
  "polar light regime.",
 "Antarctic Ice Sheet": "The largest body of ice on Earth, and the reason global sea level sits where it does. "
  "In warming projections it is the one feature on this map with a clock running.",
 "Antarctic Nothofagus Forest": "Southern beech forest with a fern understorey grew across Antarctica while the "
  "continent already sat over the pole -- proof that polar darkness alone does not make "
  "ice. Only the circumpolar current and falling CO2 did that.",
 "Arctic Azolla Bloom": "For roughly 800,000 years a freshwater fern covered a nearly enclosed Arctic Ocean, "
  "capped by river runoff. As it died and sank it locked away enough carbon to help tip "
  "the planet out of its Eocene hothouse.",
 "Armorica": "A terrane of Gondwanan origin -- Brittany, the Massif Central, Iberia and parts of "
  "Germany -- that crossed the Rheic Ocean and was caught up in the Variscan collision.",
 "Australasian Belt": "Australia's northward sprint ends in collision with Southeast Asia, crushing the "
  "islands of Indonesia and raising a mountain chain where the Coral Triangle is now.",
 "Australia-East Antarctica": "A single combined block through the Neoproterozoic, sitting next to Laurentia in most "
  "Rodinia reconstructions. Australia and Antarctica stayed joined until 45 million years "
  "ago -- one of the longest-lived continental partnerships on record.",
 "Avalon Deep-Water Realm": "Deep, dark seafloor off a volcanic arc, where the oldest large complex organisms known "
  "-- fractal, fern-like rangeomorphs -- were buried in place by ash falls at Mistaken "
  "Point.",
 "Baikal Rift": "A continental rift that has been pulling apart for 25 million years, holding the "
  "world's deepest and oldest lake -- and a fifth of its unfrozen fresh water.",
 "Baja Island": "Baja California and coastal California are already riding north on the Pacific plate "
  "along the San Andreas system. Run the motion forward and they detach as a long, narrow "
  "island off the North American coast.",
 "Bearpaw Sea": "The last major flooding of the Western Interior Seaway before it drained, its dark "
  "shales draped over the coal swamps and dinosaur beds of Alberta and Montana.",
 "Benue Trough": "The failed third arm of the rift that split South America from Africa. The other two "
  "arms became the South Atlantic; this one stalled and filled with sediment across "
  "Nigeria.",
 "Beringia": "Dry land where the Bering Strait now is, exposed whenever ice sheets locked up enough "
  "water to drop sea level. Mammoths, horses, bison and people all crossed it.",
 "Bitter Springs Sea": "The shallow epeiric sea across central Australia where the Bitter Springs cherts "
  "formed, preserving microbial cells in three dimensions. Its carbon isotopes swing so "
  "far between 810 and 780 Ma that the anomaly is used as a global time marker.",
 "Boreal Sea": "The cool northern ocean of the Mesozoic, ringed by Siberia, Greenland and Scandinavia. "
  "Its distinctive cold-water faunas are how stratigraphers tell northern rocks from "
  "Tethyan ones.",
 "Botucatu Erg": "The largest desert known in Earth's history: a sand sea of well over a million square "
  "kilometres across what is now Brazil, Uruguay, Paraguay and Namibia. The Parana- "
  "Etendeka basalts poured over its dunes and froze them in place.",
 "Brasiliano Belt": "The South American half of the Pan-African collision network, welding the Amazon, Sao "
  "Francisco and Rio de la Plata cratons into western Gondwana.",
 "Cannonball Sea": "The final Paleocene remnant of the Western Interior Seaway, a shrinking gulf in the "
  "Dakotas -- the last time salt water reached the middle of North America.",
 "Cape Fold Belt": "A mountain chain raised along Gondwana's southern edge, its folded quartzites now the "
  "ranges behind Cape Town. Matching folds appear in Argentina and the Falklands -- one "
  "belt, torn apart.",
 "Carolina Terrane": "A volcanic arc terrane that rifted from Gondwana and later docked with Laurentia, "
  "carrying its own distinctive trilobites. It now underlies the Carolina Piedmont.",
 "Cathaysian Coal Forests": "Tropical swamp forest on the Chinese blocks, isolated from Euramerica by ocean and so "
  "evolving its own flora. It kept producing coal into the Permian, after the western "
  "swamps had collapsed.",
 "Catskill Delta": "A vast wedge of river and delta sediment shed westward from the rising Acadian "
  "mountains into an inland sea. Its red beds preserve the earliest tetrapod trackways of "
  "North America.",
 "Central Asian Orogenic Belt": "The Altaids: the largest belt of accreted island arcs on Earth, built as arcs, microcontinents and seamounts were swept together between Baltica and Siberia through the Devonian to Permian, and welded when those two continents finally closed on each other. Much of central Asia is crust that was never part of an older continent.",
 "Centralian Superbasin": "A single vast basin across central Australia, later broken into the Amadeus, Officer, "
  "Ngalia, Georgina and Savory basins by Palaeozoic mountain building. It began sagging "
  "around 830 Ma as Rodinia stretched.",
 "Coconino Erg": "A Sahara-scale sand sea across the Permian tropics of western Laurentia, its dunes "
  "driven by northerly winds. Its frozen dune faces form the pale cliff band midway up "
  "the Grand Canyon.",
 "Colorado Plateau": "A block of crust a kilometre and a half high that somehow rode out the Laramide "
  "mountain building almost undeformed. The Colorado River has been carving down through "
  "it ever since.",
 "Damara Belt": "The suture where the Congo and Kalahari cratons collided, closing the Adamastor-Khomas "
  "ocean. It carries the classic Snowball Earth glacial and cap-carbonate sections of "
  "Namibia.",
 "East African Ocean": "In the projection, the East African Rift finishes its work: the Somali block tears "
  "free and a new ocean floods the gap. Basins that are dry rift valleys today become "
  "abyssal plains.",
 "East African Orogen": "The great north-south suture of Gondwana's assembly, running from Arabia down through "
  "East Africa to Antarctica, formed as the Mozambique Ocean closed.",
 "East African Rift": "A continent splitting in slow motion. The rift floor drops in a chain of long lakes "
  "and volcanic basins, and the hominin fossil record was preserved almost entirely in "
  "its sediment traps.",
 "East Antarctic Ice Sheet": "Established around 34 Ma when the circumpolar current cut Antarctica off from warm "
  "water. It has been more or less continuously present ever since -- the longest-lived "
  "ice on Earth.",
 "Euramerican Coal Forests": "Equatorial swamp forest of thirty-metre lycopod trees, running from Appalachia through "
  "Britain into Poland. Its buried peat became the coal that powered the Industrial "
  "Revolution -- and its burial drew down enough CO2 to help freeze Gondwana.",
 "Arctic Tundra": "Treeless ground ringing the Arctic Ocean, on permafrost that "
   "thaws only at the surface each summer. Nothing woody can hold on -- the growing "
   "season is too short and the frozen layer beneath blocks roots and drainage alike -- "
   "so it is moss, sedge, lichen and dwarf willow over waterlogged, patterned ground.",
 "Nearctic Tundra": "The North American arm of the circumpolar tundra, across the "
   "Canadian Shield and the Arctic islands. It sits on ground the Laurentide ice sheet "
   "scraped to bedrock and left barely drained, which is why so much of it is lake.",
 "Beringian Steppe-Tundra": "The mammoth steppe: a cold, DRY grassland-tundra "
   "stretching from Iberia to Yukon during the glacials, with no modern counterpart. "
   "Low sea level joined Siberia to Alaska across a plain of grass and herbs that "
   "supported mammoth, horse and bison at densities no living tundra approaches. It "
   "existed at the glacial maxima, far briefer than the 5-Myr keyframes this map steps "
   "through.",
 "Tibetan Alpine Tundra": "Tundra held up by altitude rather than latitude. The "
   "plateau stands so high that it is above the tree line at 33 degrees north, and its "
   "cold, thin, arid air supports alpine steppe and cushion plants across an area the "
   "size of Western Europe.",
 "Antarctic Tundra": "What came between the forest and the ice. As Antarctica cooled "
   "after the Eocene, its southern beech woodland thinned to tundra -- mosses, cushion "
   "plants and dwarf shrubs -- before the ice sheet finally overran it in the Miocene.",
 "Gondwanan Polar Tundra": "The periglacial fringe of the Karoo ice sheet, poleward of "
   "the Glossopteris forests. Cold, seasonal, and marked in the rock by frost-shattered "
   "debris, permafrost wedges and growth rings on stumps that had to survive a dark "
   "polar winter.",
 "Eurasian Steppe": "An unbroken grassland corridor from Hungary to Manchuria, opened as Central Asia dried "
  "behind the rising Tibetan Plateau. It became the highway along which horses, peoples "
  "and languages crossed the continent.",
 "Famatinian Belt": "An Ordovician arc collision along the proto-Andean margin of Gondwana, welding "
  "terranes onto what is now northwestern Argentina.",
 "Fennoscandian Ice Sheet": "The European ice dome, centred on Scandinavia and reaching Germany and Poland. It "
  "scoured the Baltic basin and dammed the lakes that became the Baltic Sea.",
 "Gaskiers Glaciation": "A short glaciation around 580 Ma, far briefer than the Snowball events and probably "
  "not global. Complex macroscopic life appears in the record almost immediately "
  "afterwards.",
 "Gilboa Forest": "The oldest forest known: stands of tree-fern-like Wattieza up to eight metres tall, "
  "their stumps preserved in growth position in New York State. Roots like these began "
  "breaking rock into soil and pulling CO2 out of the air.",
 "Glossopteris Flora": "The tongue-leaved seed fern that carpeted high-latitude Gondwana. Finding the same "
  "leaves in South America, Africa, India, Australia and Antarctica was one of Wegener's "
  "original arguments for continental drift.",
 "Gobi Erg": "The dune fields and playas of the Late Cretaceous Gobi, where sudden sand collapses "
  "buried animals alive -- including the fighting Velociraptor and Protoceratops, locked "
  "together mid-fight.",
 "Great Plains": "Grassland that spread across the North American interior as the Rockies cast a rain "
  "shadow and the Miocene climate dried. Grazing mammals evolved high-crowned teeth to "
  "cope with its silica-rich grasses.",
 "Greater Adria": "A Greenland-sized continent that rifted off North Africa, then was shoved beneath "
  "southern Europe. Its carbonate cover was scraped off to build the Alps, Apennines and "
  "Dinarides; the rest went down the subduction zone.",
 "Greater India": "India plus a large northern extension of continental crust, now missing. Whether it "
  "was thrust under Tibet or subducted outright is one of the standing arguments about "
  "the Himalayan collision.",
 "Green River Lakes": "Three great lakes -- Gosiute, Uinta and Fossil Lake -- filled the basins between the "
  "young Rocky Mountains for five million years. Their varved bottom muds preserve fish, "
  "birds, bats and insects in extraordinary detail.",
 "Hirnantian Ice Sheet": "A short, brutal glaciation centred on what is now the Sahara, then sitting over the "
  "South Pole. It dropped sea level enough to drain the world's continental shelves and "
  "drove the first of the big five mass extinctions.",
 "Hispanic Corridor": "A narrow equatorial seaway opening between North and South America as Pangaea split, "
  "linking Tethys to the Pacific. Marine animals used it to spread right around the "
  "world.",
 "Hun Superterrane": "A long ribbon of continental slivers that rifted off northern Gondwana in the "
  "Devonian, opening Palaeo-Tethys behind them. Their names survive scattered through the "
  "basement of Europe and Turkey.",
 "Irumide Belt": "A Mesoproterozoic to early Neoproterozoic belt across Zambia, marking collisions along "
  "the margins of the Congo craton as Rodinia came together.",
 "Jehol Forests": "Conifer and ginkgo woodland around volcanic lakes in northeastern China, repeatedly "
  "smothered by ash falls. The result is the world's best window on feathered dinosaurs, "
  "early birds, mammals and the first flowers.",
 "Karoo Basin": "A foreland basin in southern Gondwana that filled continuously for a hundred million "
  "years, from glacial tillite through coal swamps to desert. Its strata contain the best "
  "record anywhere of the end-Permian extinction on land.",
 "Cretaceous Polar Ice (disputed)": "The most contested ice on this map. Glendonites -- a mineral that only forms near freezing -- and scattered dropstones in what is now southeastern Australia and the Arctic point to ice at high latitudes during the Early Cretaceous cool intervals. No continental ice sheet is accepted for the Cretaceous, and the world either side of this was among the hottest of the last 200 million years. Shown as small polar ice because the field evidence is real even where its interpretation is not agreed.",
 "Late Devonian Ice Sheet": "Ice on high-latitude Gondwana at the end of the Devonian, recorded by diamictites and striated pavements now exposed across Bolivia, Peru and Brazil. Shorter and smaller than the ice ages either side of it, and probably a consequence of the forests: deep-rooted trees weather rock far faster than anything before them, and burying their carbon pulled CO2 down hard. The greening that made the land habitable also made the world cold.",
 "Karoo Ice Sheet": "The ice of the Late Palaeozoic Ice Age, spread across southern Gondwana for some "
  "eighty million years. Its striated pavements and tillites turn up in South Africa, "
  "Brazil, India, Australia and Antarctica -- once continuous, now scattered across five "
  "continents.",
 "Kaskaskia Sea": "The Devonian-Mississippian flooding of North America, laying down black shale and then "
  "the crinoid limestone that underlies much of the Midwest.",
 "Kerguelen Microcontinent": "A continent-sized volcanic plateau in the southern Indian Ocean, built by the Kerguelen plume as India tore away from Antarctica. Parts of it stood above sea level for tens of millions of years -- drill cores have brought up wood, spores and coal from a Late Cretaceous conifer forest growing on it -- before it subsided.\n\nIT IS NOT DRAWN ON THIS MAP, and the reason is worth stating: almost all of it now lies one to two kilometres below sea level, so it is submarine terrain, and the elevation field this globe is built from resolves about 20 km per pixel. A drowned plateau reads as ordinary sea floor at that scale, and the reconstruction this app uses does not restore its Cretaceous height either. The label carries it because an island the map cannot draw is still better named than silently missing.",
 "Kuunga Orogen": "The last suture of Gondwana, closing between India-Antarctica and Australia. It "
  "finished welding the southern supercontinent together only as the Cambrian explosion "
  "was underway.",
 "Lake Pannon": "A vast brackish lake filling the Carpathian Basin after the Alps and Carpathians "
  "sealed it off from the sea. Isolated for millions of years, its molluscs radiated into "
  "hundreds of species found nowhere else.",
 "Laurentide Ice Sheet": "A dome of ice up to three kilometres thick covering Canada and the northern United "
  "States, gone in a few thousand years. Its weight is still rebounding: Hudson Bay rises "
  "a centimetre a year.",
 "Lhasa Terrane": "A strip of Gondwanan crust that drifted north across Tethys and welded onto Asia in "
  "the Cretaceous. India then slammed into its southern edge, and it became the spine of "
  "southern Tibet.",
 "Mackenzie Mountains Basin": "A second great Tonian carbonate basin on Laurentia's western margin, its strata "
  "recording the carbon-isotope swings that punctuate the run-up to Snowball Earth.",
 "Marinoan Snowball Earth": "The second Snowball, ending abruptly at 635 Ma. Its cap carbonates -- laid down "
  "worldwide in the extreme greenhouse that followed deglaciation -- sit directly on "
  "glacial debris, recording a swing from freezing to scorching in geological moments.",
 "Messinian Salt Basin": "For roughly 600,000 years the Mediterranean was cut off at Gibraltar and evaporated "
  "almost dry, leaving a kilometre-deep salt desert three kilometres below sea level. It "
  "refilled catastrophically at 5.33 Ma, when the Atlantic breached the sill.",
 "Michigan Basin": "A near-circular sag in the middle of the continent that subsided steadily for a "
  "hundred million years, filling with reef limestone and thick salt. Its layers nest "
  "like a stack of bowls.",
 "Midcontinent Rift": "A 3,000-kilometre crack that nearly split North America in two around 1.1 billion "
  "years ago, erupting up to twenty kilometres of basalt before the Grenville collision "
  "squeezed it shut. Its buried arc still shows as one of the strongest gravity anomalies "
  "on the continent.",
 "Mowry Sea": "The first pulse of the Western Interior Seaway: an arm of the Arctic reaching south "
  "over western North America, its bottom mud rich in volcanic ash and organic carbon.",
 "Muschelkalk Sea": "A shallow, hypersaline sea that flooded central Europe through narrow gates from "
  "Tethys. Its limestones and salt beds record repeated cycles of connection and "
  "evaporation.",
 "Nama Sea": "A shallow shelf sea in southern Gondwana holding the last Ediacaran communities -- and "
  "the first animals to build mineralised skeletons, just before the Cambrian began.",
 "Namib": "Arid since the Eocene and hyperarid for much of the Neogene, kept dry by the cold "
  "Benguela current offshore. Its dunes are among the tallest in the world.",
 "Navajo Erg": "A sand sea covering 400,000 square kilometres of western North America in the Early "
  "Jurassic, with dunes hundreds of metres high. Its cross-bedded sandstone is the rock "
  "of Zion and Arches.",
 "Neotethys": "The ocean that opened behind the Cimmerian terranes as they rifted from Gondwana, and "
  "closed as Africa, Arabia and India drove north. Nearly all the world's giant oil "
  "fields sit on its former shelves.",
 "Newark Rift Valleys": "A chain of rift basins from Nova Scotia to the Carolinas, opened as Pangaea began to "
  "tear. Their lake beds record orbital climate cycles so cleanly that they anchor the "
  "Triassic time scale.",
 "Oaxaquia": "A Precambrian block, now the basement of much of Mexico, that travelled between "
  "Gondwana and Laurentia through the early Palaeozoic.",
 "Officer Basin": "The western lobe of the Centralian Superbasin, holding a nearly continuous "
  "Neoproterozoic record of shallow seas, evaporites and glacial deposits.",
 "Old Red Sandstone Continent": "The great red floodplain of Devonian Laurussia, shed off the eroding Caledonides. It "
  "hosted the first forests, the first insects and, in its river channels, the fish that "
  "walked out onto land.",
 "Oslo Rift": "A Permian rift through southern Norway, filled with lava and coarse alkaline "
  "intrusions. It is the type locality for a whole family of igneous rocks.",
 "Pan-Asian Rift": "A projected rift reopening the old suture that joined Europe to Asia. In the Aurica "
  "model it becomes an ocean and Asia splits in two -- one of several competing futures, "
  "and far from certain.",
 "Pangaea Proxima Inland Sea": "A remnant sea trapped inside the next supercontinent as the Indian Ocean closes -- the "
  "deepest scar in an otherwise fused landmass, and the only water for thousands of "
  "kilometres.",
 "Pebas Mega-Wetland": "A million square kilometres of swamp, shallow lake and river across western Amazonia, "
  "fed by the rising Andes and episodically connected to the Caribbean. Its waters held "
  "caimans twelve metres long and the largest freshwater turtles ever known.",
 "Permian Basin": "A deep tropical basin in western Pangaea, ringed by the Capitan reef -- one of the "
  "best-preserved fossil reefs on Earth. As it evaporated it laid down kilometres of salt "
  "and became the richest oil province in North America.",
 "Perunica": "A small terrane carrying the classic Barrandian fossil sequence of Bohemia, drifting "
  "in the Rheic Ocean off Gondwana's northern margin.",
 "Proxima Interior Desert": "The dead heart of the next supercontinent. So far from any coast that no weather "
  "system reaches it, with modelled interior temperatures above 50 degrees Celsius -- a "
  "repeat of what Pangaea's interior was like.",
 "Qinling-Dabie Belt": "The suture where North and South China finally collided in the Triassic. It exhumed "
  "rocks from 100 kilometres deep, carrying diamonds and coesite -- the first proof that "
  "continental crust can be subducted that far.",
 "Red Sea Rift": "A rift that has already become an ocean: seafloor spreading began along its axis "
  "within the last five million years, prising Arabia away from Africa.",
 "Rhine Graben": "A rift valley running from Basel to Frankfurt, opened as the Alpine collision flexed "
  "the crust to the north. Its steep flanks make the Vosges and Black Forest mirror "
  "images.",
 "Rotliegend Desert": "A trade-wind desert of wadis, dunes and salt flats across northern Pangaea, from "
  "England to Poland, while ice sheets still covered the far south. Its sandstone is the "
  "reservoir for most North Sea gas.",
 "Sahara": "The largest hot desert on Earth, in its present phase for roughly seven million years, "
  "though it swings between desert and green savanna every twenty thousand years as the "
  "Earth's orbit wobbles.",
 "Sao Francisco Craton": "An ancient block in eastern Brazil, joined to the Congo craton until the South "
  "Atlantic split them. Its cover carries Neoproterozoic glacial deposits and cap "
  "carbonates.",
 "Sibumasu": "A Cimmerian terrane -- Sumatra, Malaya, Burma, western Thailand -- carrying Gondwanan "
  "glacial deposits north into the tropics, a mismatch that helped prove it had "
  "travelled.",
 "Sierra Nevada Arc": "A volcanic arc built where the Farallon plate dived beneath North America. The "
  "volcanoes are long gone; what is left is the granite of their magma chambers, exhumed "
  "as Yosemite.",
 "Solnhofen Lagoon": "A set of stagnant, hypersaline lagoons behind a reef in the Tethyan archipelago. "
  "Nothing lived on their airless floors, so anything that sank in was preserved "
  "perfectly -- including Archaeopteryx.",
 "Somalia": "The eastern horn of Africa, projected as an island continent after the rift floods "
  "behind it -- a Madagascar-scale fragment drifting into the Indian Ocean.",
 "Songliao Basin": "A huge rift basin in northeast China holding one of the largest lakes of the "
  "Cretaceous. Its cored sediments give an almost annual record of greenhouse-world "
  "climate.",
 "Sturtian Snowball Earth": "The longest glaciation in Earth's history: roughly 57 million years, from 717 to 661 "
  "Ma, with glaciers reaching sea level at the equator. Weathering of the fresh Franklin "
  "flood basalts in the tropics is the leading trigger.",
 "Sundaland": "The exposed continental shelf joining Borneo, Sumatra and Java to mainland Asia at low "
  "sea levels -- an area larger than India, alternately land and sea through the ice "
  "ages.",
 "Sunsas Belt": "The South American segment of the Grenville-age collisions, along the southwestern "
  "edge of the Amazon craton -- a key tie-point for placing Amazonia inside Rodinia.",
 "Sveconorwegian Belt": "The Baltic counterpart of the Grenville orogeny, and evidence that Baltica and "
  "Laurentia were joined in Rodinia. Its deformed gneisses run through southern Norway "
  "and Sweden.",
 "Taklamakan": "A sand sea filling the Tarim Basin, sealed off from every ocean by the Tibetan "
  "Plateau, the Pamirs and the Tian Shan. Its dryness is a direct consequence of "
  "Himalayan uplift.",
 "Tibetan Plateau": "Five kilometres high and over a thousand kilometres wide, raised by India's collision "
  "with Asia. It is big enough to steer the jet stream and generate the Asian monsoon.",
 "Tippecanoe Sea": "The Ordovician-Silurian flooding of Laurentia, which buried the continent in tropical "
  "carbonate and built reef belts across what is now the Great Lakes.",
 "Viking Corridor": "The gap between Greenland and Scandinavia that let the cold Boreal ocean mix with warm "
  "Tethyan water. Its width governed Jurassic climate and the distribution of ammonites.",
 "Wallacea": "The belt of islands between the Asian and Australian shelves that was never joined to "
  "either. Its permanent water gaps are Wallace's Line, the sharpest biogeographic "
  "boundary on Earth.",
 "West Africa Craton": "One of the oldest stable blocks on Earth, its Archean core exposed in the Reguibat and "
  "Man shields. It has drifted through every supercontinent since without deforming "
  "internally.",
 "White Sea Realm": "Shallow shelf and delta settings holding the richest Ediacaran communities: "
  "Dickinsonia, Kimberella and the first clear trails of animals that could move.",
 "Wrangellia Terrane": "An oceanic plateau erupted in the middle of Panthalassa and later rammed onto North "
  "America. Its rocks now stretch from Vancouver Island to Alaska, thousands of "
  "kilometres from where they formed.",
 "Zealandia": "A continent 94 percent underwater. Thinned to the point of drowning as it unzipped "
  "from Antarctica, it now shows above the waves only as New Zealand and New Caledonia.",

 # ---- palaeolake descriptions ----
 "Lake Bonneville": "The largest of the Ice Age lakes of the American West, filling the Utah desert to a "
  "depth of over 300 metres while the sea stood 125 metres lower than today. It drained "
  "catastrophically northward through Red Rock Pass around 18,000 years ago. The Great "
  "Salt Lake is its shrunken, saline remnant.",
 "Lake Lahontan": "Bonneville's western twin, a branching lake filling the valleys of northwestern Nevada "
  "at the height of the last glaciation. Its shorelines are still cut into the hillsides "
  "above Pyramid Lake, hundreds of metres above the modern water.",
 "Lake Manly": "A lake 130 kilometres long and 180 metres deep in what is now the driest place in "
  "North America. Death Valley sat at the end of a chain of overflowing pluvial lakes, "
  "and filled whenever the chain upstream ran full.",
 "Glacial Lake Missoula": "Meltwater held back by a finger of the Cordilleran ice "
   "sheet that blocked the Clark Fork. The dam floated and failed again and again -- "
   "each time releasing some 2,000 cubic kilometres of water in a couple of days, at a "
   "flow greater than every river on Earth combined, which is what carved the "
   "Channeled Scablands of eastern Washington.",
 "Glacial Lake Ojibway": "The last great lake against the dying Laurentide sheet, "
   "merged with Agassiz behind an ice dam over Hudson Bay. When that dam failed around "
   "8,200 years ago the whole volume drained to the North Atlantic at once, freshening "
   "the surface enough to slow the overturning circulation -- the 8.2 ka cold event, "
   "the sharpest climate lurch of the Holocene.",
 "Lake Algonquin": "The ancestral upper Great Lakes as one body of water, ponded "
   "between the retreating ice front and the height of land. As the ice uncovered "
   "lower outlets it drained in stages, and the crust it had been pressing down has "
   "been rebounding ever since -- tilting its old shorelines, which now run uphill to "
   "the north.",
 "Baltic Ice Lake": "Fresh meltwater trapped in the Baltic depression between the "
   "Fennoscandian ice margin and the land to the south. It drained catastrophically "
   "through central Sweden when the ice cleared Billingen, dropping about 25 m in a "
   "year or two; the basin then flipped between fresh and brackish several times "
   "before becoming the sea it is now.",
 "West Siberian Ice-Dammed Lake": "Siberia's great rivers run north, and during the "
   "glacials the Barents-Kara ice sheet blocked every one of their mouths at once. The "
   "Ob and Yenisei backed up over the West Siberian Plain into a lake of continental "
   "size, which overflowed south and drained across Eurasia to the Caspian and Black "
   "Sea instead -- reversing the drainage of a third of a continent.",
 "Karoo Proglacial Lakes": "Meltwater lakes along the margin of the Gondwana ice "
   "sheet, in the basin that became the Karoo. Their floors preserve varves -- paired "
   "light and dark layers, one couplet a year -- with dropstones punched into them "
   "where icebergs floated over and melted. It is some of the best direct evidence "
   "that the Late Palaeozoic Ice Age was seasonal, and how long it lasted.",
 "Lake Agassiz": "Meltwater ponded against the southern edge of the Laurentide ice sheet, larger than "
  "all the modern Great Lakes combined. When it finally burst north into Hudson Strait "
  "around 8,200 years ago it released some 163,000 cubic kilometres of fresh water into "
  "the North Atlantic and cooled the northern hemisphere for a century.",
 "West Siberian Glacial Lake": "The Ob and Yenisei drain north to the Arctic. Block their mouths with an ice sheet and "
  "the whole of western Siberia ponds up behind it -- possibly the largest lake that has "
  "ever existed, draining south and west across Eurasia instead of into the Arctic Ocean.",
 "Lake Lisan": "The Dead Sea's Ice Age ancestor, filling the Jordan Rift some 200 metres above the "
  "modern shore. Its finely laminated marls record each wet and dry year of the last "
  "glaciation as a separate couplet.",
 "Laurentian Great Lakes": "A fifth of the world's surface fresh water, sitting in basins the ice gouged out of "
  "Precambrian rock and abandoned only about 14,000 years ago. Geologically they are "
  "brand new, and on any longer view they are temporary.",
 "Lake Mega-Chad": "During the African Humid Period the Sahara was grassland and lake, and Chad held 160 "
  "metres of water over an area the size of the Caspian. Fish bones and hippo remains sit "
  "in the open desert hundreds of kilometres from the modern shore. What is left is a "
  "shallow pond a hundredth the size.",
 "Palaeolake Makgadikgadi": "A lake the size of Lake Victoria in the middle of the Kalahari, fed by rivers that now "
  "vanish into the Okavango Delta before reaching it. Its floor is a salt pan so flat and "
  "so bare that it is visible from orbit as a white smear.",
 "Lake Dieri (Lake Eyre megalake)": "Australia's dead centre drains inward to a salt pan below sea level. In wetter phases "
  "of the Quaternary the pan and its neighbours merged into a single inland sea, which is "
  "why the continent's interior is ringed with the bones of giant marsupials.",
 "Lake Baikal": "The oldest and deepest lake on Earth, 1,642 metres down in a rift that is still "
  "opening at about two centimetres a year. It holds a fifth of the planet's unfrozen "
  "surface fresh water and a fauna -- including a freshwater seal -- found nowhere else.",
 "Lake Tanganyika": "The second deepest lake in the world, filling a segment of the East African Rift. Its "
  "lower waters have not mixed with the surface in over a thousand years, and its cichlid "
  "fishes are a textbook case of explosive evolution in isolation.",
 "Lake Victoria": "Africa's largest lake is not a rift lake at all -- it is rainwater ponded in a shallow "
  "sag between the two arms of the rift, after uplift reversed the rivers that used to "
  "drain west. It dried out completely as recently as 17,000 years ago, which makes the "
  "hundreds of cichlid species now living in it a startlingly fast radiation.",
 "East African Rift soda lakes": "Where the rift floor has no outlet and volcanic rock supplies the chemistry, the lakes "
  "turn caustic -- brine so alkaline it preserves the carcasses of birds that land on it. "
  "They are also where much of the early hominin record was buried.",
 "Lake Pannon": "A vast brackish lake filling the Carpathian Basin after the Alps and Carpathians "
  "sealed it off from the sea. Isolated for millions of years, its molluscs radiated into "
  "hundreds of species found nowhere else. The Danube now runs across its dried floor.",
 "Caspian Sea (Paratethys remnant)": "The last open piece of the Paratethys, an ocean that once ran from the Alps to central "
  "Asia. Cut off as the mountains rose, it has been drying, refilling and changing "
  "salinity ever since, and it still holds seals and sturgeon descended from marine "
  "ancestors.",
 "Black Sea (Paratethys remnant)": "A basin that has flipped between lake and sea again and again, depending on whether "
  "global sea level stood above or below the shallow sill at the Bosphorus. Below 150 "
  "metres its water is anoxic and sulphidic -- and preserves whatever sinks into it.",
 "Lago Mare (Messinian Mediterranean)": "In the last act of the Messinian Salinity Crisis the desiccated Mediterranean refilled "
  "-- not from the Atlantic, but with brackish water spilling in from the rivers and from "
  "Paratethys to the northeast. For a few hundred thousand years the Mediterranean was a "
  "lake, kilometres below the ocean outside it.",
 "Lake Gosiute": "The largest of the three Green River lakes, filling the Greater Green River Basin "
  "between the young Rocky Mountains. In its closed, evaporating phases it precipitated "
  "trona -- the world's largest deposit of soda ash lies under Wyoming.",
 "Lake Uinta": "Gosiute's southern neighbour, spilling across the Uinta and Piceance basins. Its "
  "bottom muds are the richest oil shale on Earth -- algal organic matter that never "
  "decayed because the deep water had no oxygen in it.",
 "Fossil Lake": "The smallest of the three Green River lakes and by far the most productive fossil "
  "site. Its laminated limestone preserves fish, birds, bats, insects and flowers in such "
  "numbers and such detail that whole museum halls are furnished from one quarry.",
 "Lake Idaho": "A long-lived lake in the graben the Yellowstone hotspot left behind as it burned its "
  "way east under Idaho. It held a rich freshwater fish fauna until the Snake River cut "
  "through Hells Canyon and drained it.",
 "Lake Tauca": "A lake 600 kilometres long on the Bolivian Altiplano at four kilometres' altitude, at "
  "the same time as the northern ice sheets stood at their maximum. When it evaporated it "
  "left the Salar de Uyuni -- the largest salt flat in the world.",
 "Lake Titicaca": "The highest large lake on Earth, held in a basin between two arms of the Andes as the "
  "range rose around it. It is the deepest surviving piece of a series of far larger Ice "
  "Age lakes that once covered the Altiplano.",
 "Pebas Mega-Wetland": "Before the Amazon flowed east, western Amazonia was a million square kilometres of "
  "shallow lake and swamp draining north to the Caribbean, with tides reaching far "
  "inland. Andean uplift eventually tipped the continent the other way and drained it.",
 "Lake Vostok": "A lake the size of Lake Ontario, sealed under four kilometres of Antarctic ice and "
  "kept liquid by the pressure and the heat of the rock beneath. It is one of roughly "
  "four hundred subglacial lakes, and it has been cut off from the sky for millions of "
  "years.",
 "Messel Lake": "A maar -- a lake in a volcanic explosion pit, less than a kilometre across and "
  "hundreds of metres deep. Its anoxic bottom preserved Eocene horses, bats and birds "
  "complete with stomach contents, fur and the colour of their feathers.",
 "Songliao Palaeolake": "One of the largest lakes of the Mesozoic, filling a rift-and-sag basin in northeast "
  "China for fifty million years. Twice it rose high enough to meet the Pacific and take "
  "in seawater, and its black anoxic muds became China's biggest oil field.",
 "Jehol Lakes": "Dozens of small lakes among active volcanoes in northeastern China, buried again and "
  "again under ash and pyroclastic flows. The result is the finest window anywhere on "
  "feathered dinosaurs, early birds and mammals, and the first flowers -- preserved down "
  "to the melanin in individual feathers.",
 "Crato Lake": "A lake in the rift that was tearing South America away from Africa, its bottom waters "
  "so salty and still that insects, fish and pterosaurs sank into them intact. A rare "
  "Gondwanan lacustrine Lagerstatte, from an ocean that had barely begun to open.",
 "Newark Rift Lakes": "As Pangaea began to tear along the line of the future Atlantic, a chain of deep, "
  "narrow lakes formed in the rift valleys. They rose and fell with the wobble of Earth's "
  "orbit so regularly that their layered beds are used to calibrate the Triassic "
  "timescale itself -- and they record the end-Triassic extinction and the flood basalts "
  "that caused it.",
 "Palaeo-Lake Junggar": "One of the largest lakes of the entire Phanerozoic, in a basin caught between the "
  "growing mountain belts of central Asia. Its floor holds the thickest organic-rich lake "
  "sediments known anywhere on Earth, laid down while the Early Permian world was warming "
  "sharply.",
 "Lake Orcadie": "A great lake in the collapsing wreckage of the Caledonian mountains, rising and "
  "falling to the beat of Earth's orbit for ten million years. Each time it deepened it "
  "laid down a bed of dark laminated mudstone packed with fish -- the flagstones of "
  "Caithness and Orkney, quarried for pavements and full of Devonian armoured fish.",
 "Torridonian Lakes": "River and lake beds a billion years old in northwest Scotland, laid down on a barren "
  "continent long before anything lived on land. Their muds hold some of the oldest known "
  "non-marine life: cyanobacteria and early eukaryotes living in fresh water, hundreds of "
  "millions of years before plants.",

 # ---- timeline-audit additions (2026-07-20) ----
 "Zagros Mts": "The long fold-and-thrust belt raised as Arabia drove into Eurasia from the Oligocene onward, closing the last of Neotethys. Its parallel ridges trap the richest oil province on Earth, and the collision is still shortening the crust today.",
 "Greater Caucasus": "The northern front of the Arabia-Eurasia collision, thrown up as the ocean between them was consumed. It carries the highest peaks in Europe and rose largely within the last five to ten million years.",
 "Pyrenees": "Raised as the small Iberian plate collided with Europe through the Late Cretaceous and Palaeogene. A textbook doubly-vergent belt, its ancient core was pushed up and exhumed by Eocene shortening.",
 "Carpathians": "An arc of thrust sheets swept into place during the Miocene as continental fragments rolled into the European margin, curving around the subsiding Pannonian Basin behind them.",
 "Apennines": "The spine of Italy, built through the Neogene as the Adriatic plate sank and its sedimentary cover peeled off into a migrating thrust belt, while back-arc extension opened the Tyrrhenian Sea behind it.",
 "Sonoma Orogeny": "A collision along the western edge of North America near the Permian-Triassic boundary, as the Sonomia island-arc terrane docked against the continent -- the successor to the earlier Antler event along the same margin.",
 "Lachlan Orogen": "A vast accretionary belt of eastern Gondwana, assembled from the Ordovician to the Carboniferous as slice after slice of ocean floor and volcanic arc was plastered onto the Australian margin. It forms the basement of southeastern Australia.",
 "Rio Grande Rift": "A continental rift tearing the southwestern United States open since the late Palaeogene, as the crust behind the Cordillera stretched and dropped a chain of basins from Colorado into Mexico.",
 "Basin and Range": "The type example of wide continental extension: the crust of the western United States pulled apart into dozens of tilted mountain blocks and intervening valleys, stretching to nearly twice its original width since the mid-Cenozoic.",
 "Gulf of California": "A young oblique rift where Baja California has been torn from mainland Mexico over the last dozen million years, the spreading having jumped inland from the dying offshore ridge to open a narrow new sea.",
 "West Antarctic Rift": "One of the largest rift systems on Earth, splitting West from East Antarctica and almost wholly buried under ice. Active since the Cretaceous, its stretched crust holds much of West Antarctica below sea level.",
 "Gulf of Mexico": "A marginal ocean basin opened in the Jurassic as North America pulled away from Gondwana. It began as a restricted basin that dried to leave the thick Louann salt, later buried under kilometres of river sediment.",
 "West Siberian Sea": "A vast, shallow sea that flooded the West Siberian lowland through the Late Cretaceous and Palaeogene, linking the Arctic to the Tethys by way of the narrow Turgai Strait.",
 "Tasman Sea": "The basin that opened in the Late Cretaceous as the drowned continent of Zealandia rifted away from Australia, spreading new ocean floor for some thirty million years before it stalled.",
 "South China Sea": "The largest marginal sea of the western Pacific, opened by back-arc spreading from the Oligocene into the Miocene as the South China margin stretched and continental blocks slid southward.",
 "Mid-Atlantic Ridge": "The slow-spreading ridge along which the Atlantic has been widening since the Jurassic, adding sea floor to either side a few centimetres a year and tracing the line the continents rifted apart along.",
 "East Pacific Rise": "The fastest-spreading ridge on Earth, making Pacific sea floor at more than ten centimetres a year. It is the living successor to the ancestral Pacific-Farallon spreading system.",
 "Atacama Desert": "The driest place on Earth, held arid for millions of years between the Andean rain shadow and the cold, upwelling Humboldt Current. Parts of it may not have seen real rain in centuries.",
 "Arabian Desert": "The great sand sea of Arabia, including the Rub' al Khali or Empty Quarter, the largest unbroken body of sand on the planet -- arid since the peninsula drifted into the subtropical high after splitting from Africa.",
 "Kalahari Desert": "A huge semi-arid sand basin across southern Africa, its dunes and dry pans spread over the interior plateau through the Cenozoic.",
 "Australian Desert": "The arid heart of Australia, its long parallel dunefields and stony plains spreading as the continent drifted north into the subtropics and dried through the late Cenozoic.",
 "Patagonian Desert": "A cold, wind-scoured steppe in the rain shadow east of the Andes, dry ever since the mountains rose high enough in the Miocene to wring the moisture from the Pacific westerlies.",
 "Cordilleran Ice Sheet": "The ice cap that repeatedly buried the mountains of western North America during the Pleistocene, meeting the Laurentide sheet along its eastern edge before both melted away.",
 "Greenland Ice Sheet": "The last great ice sheet of the Northern Hemisphere, in place since the late-Cenozoic cooling and holding enough ice to raise sea level about seven metres were it to melt.",
 "Patagonian Ice Sheet": "The ice sheet that mantled the southern Andes through the Pleistocene -- the largest ice mass in the Southern Hemisphere outside Antarctica -- its outlet glaciers carving the Patagonian fjords.",
 "Kazakhstania": "A Palaeozoic continent in its own right, assembled from island arcs between Siberia, Baltica and Tarim, and finally caught between them as Pangaea closed. Its crust underlies most of Kazakhstan and the Tien Shan.",
 "Mongol-Okhotsk Ocean": "The last piece of Palaeo-Asian ocean, closing like a zip from west to east through the Jurassic as Siberia rotated against the Amurian block. Its suture runs for three thousand kilometres across Mongolia and Transbaikalia.",
 "Tarim Block": "An old, rigid block of continental crust that has resisted deformation while everything around it crumpled -- which is why the Tarim Basin sits flat and undeformed between the Tien Shan and the Kunlun.",
 "Amuria": "A composite of arcs and microcontinents that welded onto Siberia as the Mongol-Okhotsk Ocean closed, carrying much of Mongolia and northeast China.",
 "Annamia": "The Indochina block: a fragment that rifted from Gondwana, crossed Palaeo-Tethys with Cimmeria and docked with South China in the Triassic.",
 "Junggar Basin": "A basin floored by trapped oceanic crust, sealed in when the Palaeo-Asian ocean closed around it and filled ever since.",
 "Ordos Basin": "A stable block within the North China Craton, subsiding gently for 250 million years and collecting the loess that now blankets it.",
 "Sichuan Basin": "A fault-bounded basin in the lee of the Tibetan Plateau, filled with red beds and famously fog-bound because the surrounding ranges trap the air in it.",
 "Qaidam Basin": "A high, closed basin inside the Tibetan Plateau, three kilometres up and utterly arid -- its floor is salt because nothing that falls there ever leaves.",
 "West Siberian Basin": "One of the largest sedimentary basins on Earth, floored by the failed Siberian rift and flooded repeatedly by shallow seas since.",
 "Tien Shan": "A Palaeozoic belt that was worn flat and then RE-RAISED by the India collision a thousand kilometres away -- an old suture reactivated, which is why it stands so high so far from any plate margin.",
 "Altai Belt": "Part of the accretionary collage between Siberia and Kazakhstania, rebuilt by the same far-field stresses that revived the Tien Shan.",
 "Kunlun Belt": "The northern edge of the Tibetan Plateau, a suture where successive Gondwanan fragments docked with Asia through the Mesozoic.",
 "Qilian Belt": "An early Palaeozoic suture on the north side of Tibet, marking where a small ocean closed long before India arrived.",
 "Alborz Belt": "The range along the southern Caspian, raised where Arabia's push into Iran is taken up hundreds of kilometres north of the collision front.",
 "Pontide Arc": "The Black Sea's southern rim: a volcanic arc built above the subducting Tethys, later shoved against Anatolia.",
 "Bohemian Massif": "A block of Variscan basement in central Europe, exposed where later cover has been stripped away -- the eroded heart of the mountain belt that ran through Pangaea.",
 "Iberian Massif": "The Variscan basement of Iberia, folded into a great arc -- the Ibero-Armorican orocline -- as the belt was bent after it formed.",
 "Massif Central": "Variscan basement in France, later domed and split by young volcanoes as the Alpine collision stretched the crust behind it.",
 "Rhodope Massif": "A stack of metamorphic sheets in the southern Balkans, exhumed from deep in the Alpine collision as the Aegean pulled apart above it.",
 "Ellesmerian Belt": "A Devonian collision along the northern edge of Laurentia, now in the Canadian Arctic islands -- the same event that raised the Old Red Sandstone mountains.",
 "Fennoscandian Shield": "Baltica's ancient core: two billion years of crust planed flat by repeated glaciation, and still rising a centimetre a year now the ice has gone.",
 "Anatolide-Tauride Block": "A Gondwanan fragment that crossed Tethys and now forms most of Turkey, caught between the Pontides to the north and the Arabian collision to the south.",
 "Kolyma-Omolon Terrane": "A composite terrane that closed the Anyui Ocean against Siberia in the Cretaceous, welding on what is now far northeastern Russia.",
 "Piedmont-Ligurian Ocean": "The narrow Alpine branch of Tethys, opened as Africa and Europe drifted apart in the Jurassic and consumed again as they closed -- its sea floor is now in the Alps as ophiolite.",
 "Okhotsk Sea": "A back-arc basin behind the Kuril arc, opened as the Pacific plate rolled back beneath Asia.",
 "Sea of Japan": "Opened in the Miocene when the Japanese arc rifted away from Asia and rotated -- the whole archipelago swung out like a door.",
 "Tethyan Himalaya": "The stack of shallow-marine rock that lay on India's northern shelf, scraped off and piled up when India hit Asia -- the summit of Everest is made of it.",
 "Morrison Floodplain": "A broad seasonal floodplain east of the rising Cordillera, and the richest dinosaur-bearing formation in North America.",
 "Yakutat Terrane": "A fragment of thickened ocean floor riding north on the Pacific plate and jamming into southern Alaska -- which is why the St Elias Mountains are the highest coastal range on Earth.",
 "Baikalian Belt": "A Neoproterozoic belt along the southern edge of the Siberian craton, named for the lake that now sits in its reactivated grain.",
 "Hangai Uplift": "A broad dome in central Mongolia, lifted by hot mantle rather than by collision -- there is no suture under it.",
 "Deccan Traps": "The basalt tableland of peninsular India and one of the largest volcanic outpourings in Earth history: something like a million cubic kilometres of lava, erupted in pulses as the subcontinent passed over the Reunion plume across the Cretaceous-Palaeogene boundary. The gas that came with it is one of the two things -- with Chicxulub -- argued over as the cause of the extinction. What is left is a step-sided tableland, worn into the terraces the Swedish word trappa gave their name to.",
 "Ethiopian Highlands": "The roof of Africa: a domed plateau of flood basalts erupted over the Afar plume in the Oligocene and lifted as the East African and Red Sea rifts began to tear the region apart.",
 "East African Plateau": "A broad Cenozoic upwarp of the African interior, raised over hot mantle and split by the East African Rift, its high cool surface holding the great lakes and the headwaters of the Nile.",
 "Williston Basin": "A long-lived, gently sinking bowl on the North American craton that gathered sediment through most of the Phanerozoic, from Palaeozoic carbonates and evaporites to later oil-rich shales.",
 "Sahul": "The single landmass of Australia and New Guinea, joined whenever Pleistocene sea levels fell, across which the first people crossed into Australia.",
 "Doggerland": "The low plain that once linked Britain to mainland Europe across the southern North Sea, a rich hunting ground for Mesolithic people until the rising seas of the early Holocene drowned it.",
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
    ("Chicxulub",        -89.5,  21.3,   66.04, 180),
    ("Popigai",          111.0,  71.6,   35.7,  100),
    ("Manicouagan",      -68.7,  51.4,  215.5,  100),
    ("Acraman",          135.5, -32.0,  580.0,   90),
    ("Morokweng",         23.5, -26.47,  146.1,   70),
    ("Kara",              64.2,  69.1,   70.7,   65),
    ("Beaverhead",      -113.0,  44.6,  600.0,   60),
    ("Tookoonooka",      142.8, -27.0,  125.0,   55),
    ("Charlevoix",       -70.3,  47.5,  450.0,   54),
    ("Siljan",            14.9,  61.0,  380.9,   52),
    ("Karakul",           73.5,  39.0,   25.0,   52),
    ("Montagnais",       -64.2,  42.9,   51.1,   45),
    ("Steen River",     -117.6,  59.5,  141.0,   25),
    ("Chesapeake Bay",   -76.0,  37.3,   34.9,   85),
    ("Araguainha",       -53.0, -16.8,  254.7,   40),
    ("Mjolnir",           29.7,  73.8,  142.0,   40),
    ("Woodleigh",        114.7, -26.1,  364.0,   60),
    ("Saint Martin",     -98.5,  51.8,  227.8,   40),
    ("Puchezh-Katunki",   43.7,  57.0,  195.9,   40),
    ("Carswell",        -109.5,  58.4,  481.5,   39),
    ("Clearwater West",  -74.5,  56.2,  286.2,   36),
    ("Manson",           -94.6,  42.6,   75.9,   35),
    ("Strangways",       133.6, -15.2,  657,   25),
    ("Hiawatha",         -66.18,  78.8,   58.0,   31),
    ("Slate Islands",    -87.0,  48.7,  450.0,   30),
    ("Mistastin",        -63.3,  55.9,   37.91,   28),
    ("Clearwater East",  -74.1,  56.1,  465.0,   26),
    ("Tunnunik",        -114.0,  72.5,  440.0,   26),
    ("Uhackatik",      -64.7,  51.2,  390.0,   25),
    ("Kamensk",           40.5,  48.4,   50.4,   25),
    ("Ries",              10.6,  48.9,   14.8,   24),
    ("Boltysh",           32.3,  48.9,   65.4,   24),
    ("Rochechouart",       0.9,  45.8,  206.9,   23),
    ("Lappajarvi",        23.7,  63.2,   77.9,   23),
    ("Gosses Bluff",     132.3, -23.8,  142.5,   22),
    ("Haughton",         -89.7,  75.4,   31.04,   23),
    # ---------- added by the impact-structure audit ----------
    # Every confirmed structure >= 12 km across and younger than
    # 1000 Ma that the original catalogue did not carry.
    ("Talundilly", 144.5, -24.83, 125.0, 84),
    ("Saqqar", 38.7, 29.59, 240.0, 34),
    ("Shoemaker", 120.89, -25.87, 784.0, 30),
    ("Alhama de Almeria", -2.55, 36.98, 8.0, 22),
    ("Gweni-Fada", 21.75, 17.42, 345.0, 22),
    ("Amelia Creek", 134.89, -20.84, 830.0, 20),
    ("Logancha", 95.97, 65.52, 40.0, 20),
    ("Neugrund", 23.62, 59.33, 535.0, 20),
    ("Sierra Madera", -102.91, 30.6, 100.0, 20),
    ("Dellen", 16.68, 61.85, 140.8, 19),
    ("Glikson", 121.56, -23.98, 500.0, 19),
    ("Obolon", 32.93, 49.57, 169.0, 19),
    ("El'gygytgyn", 172.07, 67.49, 3.58, 18),
    ("Logoisk", 27.8, 54.2, 30.0, 17),
    ("Lawn Hill", 138.65, -18.68, 476.0, 17),
    ("Ames", -98.19, 36.25, 468.0, 16),
    ("Aorounga", 19.24, 19.09, 345.0, 16),
    ("Eagle Butte", -110.51, 49.7, 60.0, 16),
    ("Oasis", 24.41, 24.58, 120.0, 16),
    ("Cleanskin", 137.94, -18.17, 760.0, 15),
    ("Kaluga", 36.2, 54.5, 388.0, 15),
    ("Luizi", 28.0, -10.17, 550.0, 15),
    ("Ternovka", 33.53, 48.14, 280.0, 15),
    ("Janisjarvi", 30.92, 61.97, 687.0, 14),
    ("Pantasma", -85.95, 13.37, 0.8, 14),
    ("Serra da Cangalha", -46.86, -8.08, 250.0, 14),
    ("Wells Creek", -87.66, 36.38, 200.0, 14),
    ("Cerro do Jarau", -56.53, -30.2, 125.0, 13.5),
    ("Lockne", 14.85, 63.04, 455.0, 13.5),
    ("Deep Bay", -102.99, 56.4, 99.0, 13),
    ("Spider", 126.09, -16.74, 740.0, 13),
    ("Zhamanshin", 60.94, 48.37, 0.91, 13),
    ("Marquez", -96.29, 31.28, 58.3, 12.7),
    ("Nicholson", -102.67, 62.66, 387.0, 12.5),
    ("Vargeao Dome", -52.17, -26.82, 123.0, 12.4),
    ("Karla", 48.03, 54.92, 5.0, 12),
    ("Yallalie", 115.77, -30.34, 86.7, 12),
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
    "Woodleigh": "A crater buried under the Carnarvon Basin east of Shark Bay, known only from "
     "drilling into its central uplift. Its age is genuinely unknown -- the only "
     "radiometric date is on authigenic clay and was formally disputed -- so the "
     "stratigraphy allows anything from the Devonian to the Proterozoic.",
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

    # ---- notes for the imported provinces and plumes ----
    "Afanasy Nikitin": "A chain of seamounts in the central Indian Ocean, and one of the harder features to "
     "reconcile with a fixed-plume model.",
    "Agulhas Plateau": "A basalt plateau south of Africa, erupted as the last threads between Africa and "
     "Antarctica parted. It still rises two and a half kilometres above the surrounding "
     "seafloor.",
    "Alborz LIP": "Ordovician volcanism along the northern edge of Gondwana, and one of very few "
     "candidates in a stretch of time otherwise almost empty of large igneous provinces.",
    "Arago (Rurutu)": "A South Pacific plume whose track can be followed back through the Cook-Austral chain "
     "into the Tuvalu, Gilbert and Marshall islands -- possibly the oldest hotspot still "
     "erupting in the Pacific.",
    "Bermuda": "A plume that never built a chain but lifted a broad swell of seafloor. Bermuda itself "
     "is a single drowned volcano capped by limestone.",
    "Bowie": "A Gulf of Alaska plume whose seamount chain bends north toward the Aleutian trench, "
     "mirroring the Hawaiian track on a smaller scale.",
    "Broken Ridge": "The rifted-off northern edge of the Kerguelen Plateau, carried away when a spreading "
     "ridge cut the plateau in two during the Eocene.",
    "Bunbury Basalt": "The Australian half of the Kerguelen plume's arrival, erupted just before the "
     "continent tore away and now buried beneath the Perth Basin.",
    "C. Kerguelen Plateau": "The middle segment of the Kerguelen edifice, built as the plume continued to feed the "
     "growing plateau after India had moved on.",
    "Caroline": "A western Pacific plume whose track runs through the Caroline Islands and carries some "
     "of the ocean's deepest-rooted volcanic chemistry.",
    "Cobb": "A north-east Pacific plume whose seamount chain runs into the Juan de Fuca Ridge, "
     "where plume and ridge have been interacting for tens of millions of years.",
    "Comei LIP": "The Kerguelen plume's opening act on the Gondwanan side, now folded into southern "
     "Tibet -- carried half the world from the province it was erupted with.",
    "Comores": "A plume between Africa and Madagascar; its newest volcano grew from the seafloor off "
     "Mayotte within the last decade, and was detected by the earthquakes it made on the way "
     "up.",
    "Dashigou (N. China)": "A dyke swarm across the North China craton, and the likely conjugate of the Bahia- "
     "Gangila dykes in South America and Africa -- evidence for how those blocks were joined "
     "a billion years ago.",
    "Discovery": "A South Atlantic plume near the ridge, one of a cluster whose chemistry samples the "
     "edge of the African deep-mantle pile.",
    "East Australia": "A hotspot Australia has been sliding over for thirty million years, leaving the "
     "longest continental volcanic track on Earth -- a line of dead volcanoes from "
     "Queensland to Victoria.",
    "Fernando de Noronha": "A small Atlantic plume off north-east Brazil, its islands the eroded necks of "
     "volcanoes that never grew large.",
    "Ferrar": "The Antarctic half of the Karoo-Ferrar event: dolerite sheets injected the length of "
     "the Transantarctic Mountains, whose dark banded cliffs are this magma frozen in place.",
    "Foundation": "A southern Pacific plume whose seamount chain runs from near the East Pacific Rise "
     "toward the Tuamotus.",
    "Gannakouriep": "A dyke swarm in southern Africa of the same age as the Franklin eruptions in Arctic "
     "Canada, on the other side of a world about to freeze over.",
    "Gough": "The southern twin of the Tristan plume. The two built the Walvis Ridge together and "
     "then separated into distinct chemical lineages -- evidence that a single plume can be "
     "striped.",
    "Great Meteor": "One of the longest hotspot tracks on Earth, running from the Monteregian Hills of "
     "Quebec through the White Mountains and the New England Seamounts to a drowned volcano "
     "in the mid-Atlantic. North America slid clean over it.",
    "Hess Rise": "A mid-Cretaceous plateau on the Pacific floor, built while the ocean was making new "
     "crust faster than at any time since. Its lavas erupted into air, not water -- it stood "
     "above the sea before it sank.",
    "Irkutsk LIP": "Magmatism on the southern edge of the Siberian craton, proposed as a continuation of "
     "the Franklin event and so as part of what tipped Earth into the Sturtian glaciation.",
    "Juan Fernandez": "A plume off Chile whose islands are carried east toward the trench, where the ridge it "
     "built jams into the Andean subduction zone.",
    "Kangding": "One of a series of magmatic pulses beneath South China as Rodinia came apart, feeding "
     "the rift basins that later filled with glacial debris.",
    "Kharaulakh": "Cambrian sills near the mouth of the Lena, erupted at roughly the same time as "
     "Australia's Kalkarindji basalts on the far side of the world.",
    "Lord Howe": "A plume in the Tasman Sea whose oldest island has eroded to a spire of rock rising six "
     "hundred metres straight out of the ocean.",
    "Macdonald": "The most active volcano in the Austral chain, a seamount that occasionally boils the "
     "sea surface without ever quite breaching it.",
    "Madeira": "A slow plume off Iberia whose track runs north-east along the Tore Rise; like the "
     "Canaries, it stays active because Africa barely moves.",
    "Magellan Rise": "A small Late Jurassic plateau, and one of the oldest surviving pieces of seafloor "
     "topography anywhere on the planet.",
    "Malani Igneous Suite": "One of the largest silicic provinces of the Precambrian: rhyolites and granites across "
     "Rajasthan, erupted as Rodinia stretched. Its rocks record where India sat inside the "
     "supercontinent.",
    "Marie Byrd Land": "A plume beneath West Antarctica, feeding volcanoes that erupt through the ice sheet "
     "and melt it from below.",
    "Marion": "The plume that split Madagascar from India and erupted the Madagascar flood basalts, "
     "leaving the island alone in the Indian Ocean with its own evolutionary experiment.",
    "Maud Rise": "The Antarctic counterpart of the Agulhas Plateau, split from it as the Southern Ocean "
     "opened. Its bulk still steers the currents above it, opening a recurring hole in the "
     "winter sea ice.",
    "Mid-Pacific Mountains": "A broad Cretaceous rise whose volcanoes once broke the surface as islands with coral "
     "reefs; they have since subsided into flat-topped seamounts drowned a kilometre down.",
    "N. Kerguelen Plateau": "The youngest segment, still fed by the plume and still carrying islands above water in "
     "the far southern Indian Ocean.",
    "Pitcairn": "A young Pacific plume whose islands are so isolated they were the last refuge of the "
     "Bounty mutineers.",
    "S. Kerguelen Plateau": "The main body of a drowned volcanic continent a third the size of Australia. Cores "
     "drilled from it contain wood and coal -- it had forests before it sank.",
    "Samoa": "A Pacific plume with an unusual twist: it sits beside the tearing corner of the Tonga "
     "trench, which pulls its magma sideways.",
    "Seiland Igneous Province": "A deep-crustal magmatic province in Arctic Norway, emplaced as the Iapetus Ocean began "
     "to open. What is exposed is its plumbing, not its volcanoes.",
    "Society (Tahiti)": "A plume beneath French Polynesia, building the high volcanic islands that subside into "
     "the ring-shaped atolls Darwin explained.",
    "Suxiong-Xiaofeng": "Bimodal volcanism on the Yangtze craton, part of the long sequence of eruptions that "
     "accompanied Rodinia's breakup in South China.",
    "Sylhet Traps": "The eastern twin of the Rajmahal Traps, erupted in the same pulse over the Kerguelen "
     "plume and now buried under the sediment of the Bengal delta.",
    "Tasmantid": "A hotspot that printed a line of seamounts down the Tasman Sea while the Australian "
     "plate raced north over it.",
    "Trindade": "A plume beneath the South Atlantic that first surfaced inland, erupting diamond- "
     "bearing kimberlites across Brazil before the continent carried on west and left it "
     "offshore.",
    "Volyn Flood Basalts": "Ediacaran flood basalts across what is now Ukraine, erupted as Baltica pulled away "
     "from the rest of Rodinia -- and close in time to the first large, soft-bodied animals.",
    "Wichita / S. Oklahoma": "Cambrian rift volcanism and layered intrusions along a failed arm of the opening "
     "Iapetus. Buried for 300 million years, then shoved back into daylight as the Wichita "
     "Mountains when Pangaea assembled.",
    "Yemen Traps": "The other half of the Afar flood basalts, erupted at the same moment as the Ethiopian "
     "Traps and then torn away from them as the Red Sea opened. The two plateaus now face "
     "each other across the water.",

    # ---- notes for the craters added by the audit ----
    "Alhama de Almeria": "Confirmed only in 2023, and buried: a small Miocene crater in southern Spain whose "
     "22 km footprint is mostly collapsed ground around a true crater a quarter that size.",
    "Amelia Creek": "A crater in the Northern Territory with no crater shape left -- it is recognised "
     "entirely from shatter cones and sheared rock. Its age could be anywhere in a "
     "billion-year window.",
    "Ames": "Buried nearly three kilometres deep in Oklahoma, and productive: oil accumulated in "
     "the shattered rock of the crater fill, which is how it was found.",
    "Aorounga": "Concentric rings in the Chadian Sahara, combed into stripes by wind-carved yardangs. "
     "One of the most photographed craters on Earth from orbit, and possibly one of a "
     "chain.",
    "Cerro do Jarau": "One of only about three craters on Earth punched into flood basalt. Its central core "
     "rises out of the flat Pampas of southern Brazil.",
    "Cleanskin": "Confirmed in 2021 on shocked quartz alone, straddling the Northern Territory- "
     "Queensland border. Nothing about the landscape suggests a crater; the rock does.",
    "Deep Bay": "A circular bay 220 metres deep at the south end of Reindeer Lake, Saskatchewan. "
     "Glaciation cleaned it out rather than erasing it, leaving one of the sharpest crater "
     "outlines visible from orbit.",
    "Dellen": "Two lakes in Sweden filling a Cretaceous crater. Long thought to be 89 million years "
     "old, it was redated to 141 -- one of the larger single-crater corrections in the "
     "catalogue.",
    "Eagle Butte": "A crater buried without trace under southern Alberta, mapped only by seismic surveys "
     "and drilling.",
    "El'gygytgyn": "An almost perfectly circular lake in Chukotka. Because it has never been glaciated, "
     "its sediments hold an unbroken 3.6-million-year record of Arctic climate -- the "
     "longest that exists on land.",
    "Glikson": "A crater in the Little Sandy Desert defined mostly by a ring-shaped magnetic "
     "anomaly. Named for Andrew Glikson, who spent a career arguing that Australia was "
     "full of unrecognised impact structures.",
    "Gweni-Fada": "A ring of hills on Chad's Ennedi Plateau. The Sahara's hyperaridity has kept a "
     "crater of roughly Devonian age legible as surface topography, which almost nowhere "
     "else on Earth manages.",
    "Janisjarvi": "A Karelian lake filling a crater 687 million years old -- the oldest impact "
     "structure on Earth that still holds a lake.",
    "Kaluga": "A Devonian crater buried under central Russia, known only from boreholes.",
    "Karla": "A small, buried crater on the Russian platform, a few million years old.",
    "Lawn Hill": "A ring of dolomite hills in Queensland marking a mid-Ordovician impact. The crater "
     "is gone; the shatter cones and impact diamonds are not.",
    "Lockne": "A Swedish crater formed on a shallow Ordovician sea floor, which is why its resurge "
     "deposits -- the sediment that washed back in -- are the best preserved anywhere. It "
     "belongs to the Ordovician meteorite shower that followed the break-up of the "
     "L-chondrite parent body.",
    "Logancha": "A Siberian crater punched through the Siberian Traps themselves, so its target rock "
     "is the largest flood basalt province on Earth.",
    "Logoisk": "A crater buried under Belarus, found by drilling in the 1970s. Its published age was "
     "wrong by 12 million years until Ar-Ar dating moved it to 30 Ma.",
    "Luizi": "The first impact structure ever confirmed in the Democratic Republic of the Congo, "
     "found in 2011. Its rim rises 300 metres above the interior on the Kundelungu Plateau "
     "and is unmistakable from space.",
    "Marquez": "A buried Palaeocene dome in Texas, its central uplift showing at the surface as a "
     "low rise.",
    "Neugrund": "A submarine crater in the Gulf of Finland whose ejecta layer is more useful than the "
     "crater: it sits in Early Cambrian rocks laid down before trilobites appeared, and is "
     "the only reason we know when it struck.",
    "Nicholson": "A lake full of islands in the Northwest Territories, scoured by ice until little of "
     "the crater form was left.",
    "Oasis": "A crater in the Libyan desert whose rim has been stripped down to an inner ring of "
     "hills. It sits close to the small BP structure, and the two may be related.",
    "Obolon": "A Jurassic crater buried beneath the Dnieper-Donets basin in Ukraine, with no trace "
     "at the surface.",
    "Pantasma": "A young crater in the Nicaraguan highlands, and the likely source of the impact "
     "glass scattered across Belize 800,000 years ago.",
    "Saqqar": "The largest confirmed impact structure on the Arabian Peninsula, exposed in the "
     "northern Saudi desert and confirmed by shocked quartz. Its age is pinned only "
     "between 410 and 70 million years.",
    "Serra da Cangalha": "Brazil's second-largest crater, cut into flat-lying Parnaiba Basin sandstone. Its "
     "central uplift ring is about as clean a textbook example as exists.",
    "Shoemaker": "Concentric rings of salt lakes in the Western Australian desert, named for Gene "
     "Shoemaker, who did more than anyone to establish that craters like this exist. Its "
     "age is bracketed only between 1300 and 568 million years -- it may not even belong "
     "in this timeline.",
    "Sierra Madera": "The central uplift of a West Texas crater, standing as a cluster of hills on "
     "otherwise flat plains. Erosion has cut so deep that the crater floor is gone and the "
     "plumbing beneath it is exposed.",
    "Spider": "Named for the radiating ridges of shatter-coned sandstone that spread from its "
     "centre across the Kimberley -- the legs are visible from the air after something "
     "like 700 million years.",
    "Talundilly": "A buried structure in Queensland, 84 km across, sitting 300 km from Tookoonooka and "
     "apparently the same age. If both are impacts they are the largest known doublet on "
     "Earth -- but Talundilly has only ever been seen in seismic data, never drilled, so "
     "it remains unproven.",
    "Ternovka": "A Permian crater in Ukraine visible only inside the Krivoy Rog iron-ore pits, where "
     "mining has cut through the buried structure.",
    "Uhackatik": "Spotted on Google Maps by an amateur, confirmed by shatter cones and impact melt in "
     "2025, and named in consultation with the Ekuanitshit Innu. A ring basin 25 km across "
     "on Quebec's Cote-Nord that nobody had recognised until someone looked at a satellite "
     "image properly.",
    "Vargeao Dome": "A crater blasted into the Parana flood basalts, 225 metres deep with a rim so intact "
     "that three Brazilian municipalities sit inside it.",
    "Wells Creek": "A Tennessee crater with a superbly exposed central uplift and shatter cones, long "
     "used as a field-teaching site. Its age is bracketed only between 323 and 100 million "
     "years.",
    "Woodleigh": "A crater buried under the Carnarvon Basin east of Shark Bay, known only from "
     "drilling into its central uplift. Its age is genuinely unknown -- the only "
     "radiometric date is on authigenic clay and was formally disputed -- so the "
     "stratigraphy permits anything from the Devonian to the Proterozoic.",
    "Yallalie": "Australia's first confirmed Late Cretaceous impact, buried under the Perth Basin and "
     "betrayed only by shocked quartz in its breccia.",
    "Zhamanshin": "The youngest crater of its size on Earth, in Kazakhstan, and the source of "
     "irghizites -- glass droplets thrown from the impact and still lying loose on the "
     "surface.",
}


def event_notes():
    return EVENT_NOTES


# ------------------------------------------------- descriptions through time --
# A feature that exists for 300 million years is not doing the same thing at
# both ends of that window. The Appalachians are a rising arc-collision belt at
# 450 Ma, a Himalayan-scale range at 290 Ma, and a worn stump at 150 Ma; a
# single description has to either pick one and be wrong for the rest, or stay
# so vague it says nothing. So the long-lived features carry a list of phases,
# and the app shows whichever one contains the displayed age, falling back to
# the timeless entry in DESCRIPTIONS when none matches.
#
# Each phase is (a0, a1, text) with a0 <= age <= a1, matching the convention
# used everywhere else in this file (future ages negative). A phase window that
# falls outside its own label's window can never be reached, so build_webdata
# checks that on export rather than letting it fail silently.
PHASES = {

 "Pangaea": [
  (300, 330, "Still welding shut. Gondwana has driven into Laurussia and the Central Pangaean "
             "Mountains are rising along the suture, but the Palaeo-Tethys gulf is still open to "
             "the east and Siberia has not yet docked."),
  (260, 300, "Complete, and at its most extreme. A single landmass from pole to pole means the "
             "interior lies thousands of kilometres from any coast: no rain reaches it, and the "
             "heart of the continent becomes one of the driest landscapes Earth has known."),
  (230, 260, "Past the great dying. The end-Permian extinction has stripped the supercontinent of "
             "its forests -- there is no coal anywhere on Earth for the next ten million years -- "
             "and a megamonsoon drives violent seasonal rain against a still-desert interior."),
  (175, 230, "Beginning to fail. Rift valleys are tearing along the line where North America meets "
             "Africa, filling with lakes and flood basalt, and the Atlantic is about to open along "
             "the crack."),
 ],

 "Gondwana": [
  (480, 540, "Newly assembled and enormous. The Pan-African sutures that welded it are still fresh "
             "mountain belts, and its shallow shelves are where animals with hard skeletons are "
             "radiating for the first time."),
  (420, 480, "Drifting across the South Pole. Ice caps grow over what is now the Sahara, and the "
             "end-Ordovician glaciation drops sea level worldwide and empties the shelves."),
  (330, 420, "Converging on Laurussia. The Rheic Ocean between them is closing, and the collision "
             "that will raise the Appalachians and build Pangaea is under way."),
  (250, 330, "Locked inside Pangaea as its southern half, and carrying an ice sheet across the "
             "South Pole through the Late Palaeozoic Ice Age. Its Glossopteris flora is the same "
             "on every fragment, which is how the continent was reconstructed."),
  (150, 250, "Coming apart. Africa, India, Antarctica and Australia are separating, and the "
             "Karoo and Ferrar basalts mark where the rifting began."),
 ],

 "Rodinia": [
  (900, 1000, "Assembling around a Laurentian core along the Grenville belts -- a mountain chain of "
              "Himalayan scale running through what is now eastern Canada and Scandinavia."),
  (800, 900, "Fully assembled and geologically quiet. Life is entirely microbial; stromatolite "
             "reefs line the shelves and the land is bare rock."),
  (700, 800, "Rifting apart. Dyke swarms are tearing the interior open, and the weathering of all "
             "that fresh basalt in the tropics is drawing carbon out of the air -- one of the "
             "leading explanations for the Snowball Earth that follows."),
 ],

 "Appalachians": [
  (390, 460, "Early growth. An island arc has collided with Laurentia's eastern margin in the "
             "Taconic orogeny, thrusting deep-water rock over the shelf and shedding the first "
             "great wedge of sediment west into the continent."),
  (330, 390, "The Acadian phase. Avalonia has docked, the range is high enough to feed the Catskill "
             "delta, and its rain shadow is beginning to dry the continental interior."),
  (260, 330, "The Alleghanian climax. Gondwana is driving into Laurussia and this chain rivals the "
             "modern Himalaya, standing at the centre of Pangaea with rivers draining off it into "
             "coal swamps on both flanks."),
  (150, 260, "Dying back. The collision is over and the range is unloading -- erosion strips it "
             "kilometres deep and the crust rebounds beneath, exposing the metamorphic roots that "
             "form the modern crest."),
  (0, 150, "A worn root, not a mountain range. What stands today is the eroded core of a chain that "
           "was alpine 300 million years ago, its matching halves now in Scotland, Scandinavia and "
           "Morocco."),
 ],

 "Atlantic Ocean": [
  (140, 175, "Not yet an ocean -- a chain of rift valleys and lakes along the failing seam of "
             "Pangaea, flooded episodically by seawater and repeatedly evaporating to salt."),
  (90, 140, "Opening in two halves. The central Atlantic is a narrow seaway while the South "
            "Atlantic is still a lake-filled rift between Brazil and Namibia; they will not link "
            "into one ocean until the mid-Cretaceous."),
  (30, 90, "A true ocean, widening steadily, with the Mid-Atlantic Ridge running its full length "
           "and no subduction zone anywhere to consume it."),
  (0, 30, "Still widening a few centimetres a year -- but the first subduction zones have appeared "
          "at its margins, in the Lesser Antilles and the Scotia arc, which is how ocean basins "
          "begin to die."),
 ],

 "Pacific Ocean": [
  (100, 160, "The vast remnant of Panthalassa, floored by crust that is being consumed at every "
             "margin faster than its ridges can replace it."),
  (40, 100, "Shrinking. Subduction rings the entire basin, and the plateaus riding on its floor -- "
            "Ontong Java, Shatsky, Hess -- are too buoyant to sink and are jamming the trenches."),
  (0, 40, "The oldest and largest surviving ocean, and the only one that is closing. Almost none of "
          "its original Panthalassic floor is left; the oldest crust in it is Jurassic."),
 ],

 "India": [
  (90, 130, "Still attached to Gondwana's eastern flank, with Madagascar alongside and the "
            "Kerguelen plume erupting the Rajmahal basalts along its edge."),
  (66, 90, "An island continent alone in the Tethys, drifting north faster than any landmass known "
           "-- its flora and fauna evolving in isolation for tens of millions of years."),
  (50, 66, "Passing over the Reunion plume. The Deccan Traps erupt across the subcontinent within "
           "a few hundred thousand years of the Chicxulub impact."),
  (0, 50, "Colliding with Asia and refusing to subduct -- continental crust is too buoyant, so it "
          "crumples instead, raising the Himalaya and the Tibetan Plateau and slowing from a sprint "
          "to a crawl."),
 ],

 "Iapetus Ocean": [
  (520, 600, "Newly opened, as Rodinia's fragments separate and rift volcanism floods the margins "
             "of Laurentia and Baltica."),
  (460, 520, "At its widest -- thousands of kilometres of open ocean, with distinct faunas on either "
             "shore that would later be the evidence the ocean had ever existed."),
  (420, 460, "Closing fast. Island arcs are colliding with both margins, and the trilobite faunas "
             "of the two shores are beginning to mix."),
  (400, 420, "Gone. Laurentia and Baltica have collided in the Caledonian orogeny, and the suture "
             "runs through what is now Scotland, Scandinavia and Greenland."),
 ],

 "Tethys Ocean": [
  (200, 260, "A wedge-shaped gulf biting westward into Pangaea, opening as the Cimmerian terranes "
             "rift off Gondwana and drift north."),
  (145, 200, "A wide tropical seaway between Laurasia and Gondwana. Its warm, shallow carbonate "
             "shelves are laying down the limestone that becomes the Alps and the Middle East's "
             "oil reservoirs."),
  (120, 145, "Beginning to be squeezed as Africa starts north, while the Atlantic opening to the "
             "west changes the whole circulation of the globe."),
 ],

 "Panthalassa": [
  (250, 320, "The world-ocean, wrapped around Pangaea and covering more of the planet than all "
             "modern oceans combined. Its interior is so far from any shore that almost nothing is "
             "known of it -- the crust that floored it has been entirely subducted."),
  (160, 250, "Still the dominant ocean, but Pangaea is splitting and new basins are opening inside "
             "the land it once surrounded. The Pacific is what will be left of it."),
 ],

 "Himalaya": [
  (35, 55, "The first contact. India's leading edge has met the Asian margin and the Tethys is "
           "shutting, but the range is still low -- marine sediments are only beginning to be "
           "thrust up."),
  (10, 35, "Rising hard. The crust doubles in thickness, the Tibetan Plateau lifts behind the "
           "front, and the monsoon strengthens as the barrier grows."),
  (0, 10, "The highest mountains on Earth and still growing about a centimetre a year, built "
          "entirely of crumpled continental crust with marine limestone at the summits."),
 ],

 "Antarctica": [
  (100, 160, "Attached to Australia and South America, forested and ice-free despite sitting near "
             "the pole -- southern beech and conifers grow through months of winter darkness."),
  (35, 100, "Isolating. South America and Australia are pulling clear, and the gaps that open "
            "between them will let a current circle the continent for the first time."),
  (0, 35, "Refrigerated. The Antarctic Circumpolar Current has thermally sealed the continent off "
          "from the warm oceans to the north, and the ice sheet that grew in response has been "
          "here ever since."),
 ],

 "Africa": [
  (100, 150, "The core of Gondwana, shedding South America to the west as the South Atlantic opens "
             "and India and Madagascar to the east."),
  (30, 100, "Drifting north and nearly ringed by spreading ridges, so it moves slowly. Its northern "
            "margin is beginning to close the Tethys against Europe."),
  (0, 30, "Colliding with Europe -- the Alps and Atlas are the result -- while the East African Rift "
          "tears the continent's own eastern flank away along a line of volcanoes and lakes."),
 ],

 "North America": [
  (100, 150, "Separating from Africa and Europe as the Atlantic opens behind it, while terranes "
             "sweep in and weld onto its western edge."),
  (55, 100, "Split down the middle by the Western Interior Seaway, with the Sevier-Laramide "
            "mountains rising along the west and shedding sediment east into that sea."),
  (0, 55, "Riding west over Pacific crust, its western margin a collage of accreted terranes and "
          "its interior drained by rivers that only reorganised into their modern courses under "
          "the Pleistocene ice sheets."),
 ],

 "Eurasia": [
  (150, 250, "Not yet one continent. Siberia, North China, South China and a train of Cimmerian "
             "fragments are still separate blocks converging on the Laurasian core."),
  (50, 150, "Assembling by collision. The Cimmerian terranes dock, the Turgai Strait floods the "
            "join between Europe and Asia, and the Verkhoyansk belt rises in the far east."),
  (0, 50, "The largest continental plate, still being built along its southern rim as India, "
          "Arabia and Africa drive into it -- the Himalaya, Zagros and Alps are all one collision "
          "front."),
 ],

 "Western Interior Seaway": [
  (90, 100, "Opening. Arctic and Gulf waters have met across the continent for the first time, "
            "flooding the foreland basin behind the rising Sevier mountains."),
  (75, 90, "At its widest -- a thousand kilometres of shallow sea splitting North America in two, "
           "warm, oxygen-poor at depth, and full of mosasaurs, plesiosaurs and giant fish."),
  (72, 75, "Draining away as sea level falls and the Laramide uplifts rise through its floor. "
           "The Bearpaw flooding is its last, and by about 70 Ma the through-going connection "
           "from Arctic to Gulf is gone, leaving the chalk and shale under the Great Plains."),
 ],

 "Mediterranean": [
  (15, 28, "The last open remnant of Tethys, still connected to the Indian Ocean at its eastern "
           "end -- but Arabia is closing that gate."),
  (6, 15, "Cut off from Tethys and fed only through narrowing Atlantic gateways, with the "
          "Paratethys stranded behind the rising Alps."),
  (0, 6, "A basin that very nearly ceased to exist: when the Atlantic connection closed around six "
         "million years ago it evaporated almost completely, leaving kilometres of salt on its "
         "floor before the Atlantic broke back in."),
 ],

 "Andes": [
  (30, 60, "A volcanic arc along South America's western edge, but not yet high -- subduction is "
           "building magma, not much topography."),
  (0, 30, "Rising fast as the Nazca plate shallows beneath the continent, thickening the crust into "
          "the Altiplano and lifting a barrier high enough to redirect the Amazon eastward."),
 ],

 "Rocky Mountains": [
  (40, 60, "Being built far inland from any plate margin, as the shallowly subducting Farallon slab "
           "transmits compression hundreds of kilometres into the continent -- a mountain range "
           "with no ocean beside it."),
  (0, 40, "Uplifted again by regional doming and then carved by Pleistocene glaciers into the "
          "cirques and horns that give the range its modern profile."),
 ],

 "Laurentia": [
  (500, 600, "Newly rifted from Rodinia and sitting astride the equator, its margins flooded by the "
             "first great transgression as the Iapetus opens."),
  (430, 500, "Drowned. The Sauk sea has covered nearly the whole craton in clear tropical water, "
             "laying sheets of quartz sand and limestone across a continent with no plants on it."),
 ],

 "East Antarctic Ice Sheet": [
  (14, 34, "Present but unstable -- the ice waxes and wanes with orbital cycles, and there are "
           "still southern beech forests in the coastal valleys between glaciations."),
  (0, 14, "Permanent and thick. The ice sheet reaches its modern configuration, locking up enough "
          "water to hold global sea level roughly sixty metres below an ice-free world."),
 ],

 "East African Ocean": [
  (-60, -25, "A young sea flooding the rift that split Africa, narrow and hot, much as the Red Sea "
             "is today."),
  (-130, -60, "A fully developed ocean basin with its own spreading ridge, separating the Somali "
              "fragment from the African mainland."),
 ],
}


def phases():
    return PHASES


# --------------------------------------------------- how long a scar shows --
# The volcanism layer used to draw a large igneous province only while it was
# erupting, so a feature that reshaped a continent vanished one frame after its
# eruption window closed. That is backwards: the eruption is brief and the
# landform is not. The Deccan still covers half a million square kilometres and
# holds up the Western Ghats; the Karoo basalts are the roof of Lesotho.
#
# The controlling variable turns out not to be size but SETTING. Erupt onto
# stable craton and the basalt armours itself and stands in inverted relief for
# a hundred million years -- summit lowering on flood basalt runs about 6 m per
# million years, so a kilometre takes 150 Myr to strip. Erupt into a subsiding
# rift and it is buried almost as it forms: CAMP is the largest continental
# province ever and is a landform essentially nowhere, because most of it was
# never extrusive at all and the rest drowned in rift-basin sediment before
# being rifted apart.
#
# `age` is how young the province stays visible as a topographic feature;
# 0 means it is still one today.
VISIBLE_UNTIL = {
 "Agulhas Plateau": (0,
     "300,000 km2 standing 2.5 km above the surrounding seafloor with a summit at "
     "2,500 m depth and crust 20-25 km thick."),
 "Alborz LIP": (300,
     "Deformed into the Alborz range during Cimmerian and later collisions."),
 "Altay-Sayan": (300,
     "Dismembered and buried by the accretionary tectonics of the Central Asian "
     "Orogenic Belt."),
 "Bahia-Gangila": (850,
     "Dyke swarms across the Sao Francisco and Congo cratons; the volcanic carapace "
     "is entirely gone."),
 "Broken Ridge": (0,
     "A shallow bathymetric ridge in the eastern Indian Ocean, rifted off the "
     "Central Kerguelen Plateau in the Eocene; its flank stood ~2,000 m above sea "
     "level at the moment of rifting."),
 "Bunbury Basalt": (100,
     "Largely buried under the Perth Basin's Cretaceous-Cenozoic fill."),
 "C. Kerguelen Plateau": (0,
     "Still bathymetrically prominent, with Heard Island (Mont Ross, 1,850 m) and "
     "the Kerguelen archipelago emergent above it."),
 "Caribbean LIP": (60,
     "The oceanic plateau that stops being a plateau. Its crust is 10-20 km thick, "
     "straddling the ~17 km threshold below which plateaus subduct normally, so its "
     "margins were obducted onto Colombia, Ecuador, Costa Rica and Curacao while the "
     "interior was trapped in an enclosed basin and smoothed flat by terrigenous "
     "fill. Still thickened crust; no longer bathymetric relief. LOW CONFIDENCE on "
     "the date."),
 "Central Atlantic (CAMP)": (195,
     "The key negative result, and the largest province by area (~11 million km2) "
     "with almost no topographic legacy at all. It was never a plateau: Newark Basin "
     "flows are sandwiched between lacustrine formations, buried by rift-basin "
     "subsidence within ~100,000 years of eruption; the Amazonian sills were "
     "emplaced at depth; the Moroccan basalts survive precisely BECAUSE they were "
     "buried. The Palisades cliffs are an intrusion exhumed in the Pleistocene, not "
     "a preserved lava surface. Show CAMP erupting and then vanishing almost at once "
     "- that is what actually happened."),
 "Central Iapetus": (450,
     "Rift volcanics along the Iapetan margins were buried by the passive margin "
     "sequence, then caught in the Appalachian-Caledonian orogenies."),
 "Chon Aike": (0,
     "Ignimbrite plateaus of the Deseado Massif and the Antarctic Peninsula still "
     "stand with moderate relief after 150 Myr, though much is buried under the "
     "Austral-Magallanes and San Jorge basins. LOW CONFIDENCE - not verified against "
     "a primary source."),
 "Columbia River Basalts": (0,
     "Still visible, but draw it as a LAVA PLAIN, not a highland. The crust sagged "
     "into the space vacated as the lava rose, so the Columbia 'Plateau' is really a "
     "slightly depressed basin; the topographic highs are the Yakima folds, not the "
     "basalt surface itself."),
 "Comei LIP": (60,
     "Carried into the Himalayan collision zone and deformed; no plateau survives, "
     "only tectonised basalt and dykes in southern Tibet."),
 "Dashigou (N. China)": (850,
     "A dyke swarm on the North China craton with no extrusive remnant."),
 "Deccan Traps": (0,
     "About 500,000 km2 of the original ~1.5 million km2 survives - roughly a third "
     "- still over 2 km thick, and its western edge IS the Western Ghats escarpment: "
     "900-1,500 m of relief running ~1,600 km, rising to Anamudi at 2,695 m."),
 "Emeishan Traps": (0,
     "Over 250,000 km2 survives - about half - up to 5.5 km thick. But note the "
     "modern Yunnan-Guizhou Plateau elevation is Cenozoic and Tibet-related: the "
     "basalt is resistant caprock on a young plateau, re-exhumed, not a continuously "
     "surviving Permian landform."),
 "Ethiopian Traps": (0,
     "The Ethiopian Highlands ARE the flood basalt pile - the surface is almost "
     "entirely above 1,500 m and culminates at Ras Dashen, 4,550 m. The Main "
     "Ethiopian Rift now bisects it."),
 "Ferrar": (0,
     "Dolerite sills armour the Transantarctic Mountains the length of the range, "
     "preserved by polar-desert conditions for 183 Myr."),
 "Franklin LIP": (700,
     "Draw as a DYKE PROVINCE, not a plateau. The Franklin dyke swarm, Coronation "
     "sills and Natkusiak basalts survive, and the sills form ramparts and linear "
     "sets of islands - but that is Phanerozoic differential erosion picking out "
     "resistant intrusions, not a surviving 719 Ma landform. Its climatic importance "
     "is front-loaded anyway: the CO2 drawdown came from weathering FRESH tropical "
     "basalt within ~2 Myr of eruption."),
 "Gannakouriep": (600,
     "A dyke swarm in the Gariep belt, deformed by Pan-African orogeny."),
 "Guibei / South China": (750,
     "Volcanics and intrusions in the Jiangnan belt, buried beneath Cryogenian "
     "glacial and Sinian marine sequences."),
 "Gunbarrel": (700,
     "A dyke swarm; whatever volcanic cover existed was removed before the Cambrian."),
 "Hess Rise": (0,
     "Strongly asymmetric: crest at ~2,161 m in the south deepening to 4,637 m in "
     "the north. Vesicular non-pillowed trachyte flows show it was probably above "
     "sea level early in its history."),
 "High Arctic (HALIP)": (0,
     "The Alpha Ridge carries 38 km of crust - thicker than Ontong Java - with 2,700 "
     "m of relief and a crest at ~1,250 m. Worth splitting in the renderer: Alpha "
     "and Mendeleev ridges submarine, Svalbard, Franz Josef Land and Ellesmere "
     "subaerial."),
 "Hikurangi Plateau": (0,
     "Still a plateau but the most damaged of the three: ~400,000 km2 survives of an "
     "original ~800,000. It jammed the Chatham Rise at ~100 Ma and is now partly "
     "subducting beneath the North Island, imaged 37-140 km down."),
 "Irkutsk LIP": (650,
     "Sills and volcanics on the southern Siberian craton margin, buried and then "
     "caught in Baikalide deformation."),
 "Kalkarindji": (0,
     "If confirmed, the record-holder for flood-basalt landform longevity at ~511 "
     "Myr: the Antrim Plateau Volcanics sit on arid, stable Australian craton, the "
     "single most favourable preservation setting there is. MEDIUM CONFIDENCE - "
     "verify against a primary source before shipping, since a 511 Myr surviving "
     "landform is a strong claim."),
 "Kangding": (700,
     "Mafic-ultramafic intrusions along the western Yangtze margin, buried beneath "
     "Sinian cover."),
 "Karoo-Ferrar": (0,
     "The Drakensberg is capped by ~1,600 m of erosion-resistant basalt - that "
     "caprock is precisely why it survives - reaching Thabana Ntlenyana at 3,482 m."),
 "Kharaulakh": (400,
     "Sills near the Lena mouth, incorporated into the Verkhoyansk belt."),
 "Kola-Dnieper": (300,
     "Mostly buried under the Dnieper-Donets and Pripyat basin fills; the Kola "
     "alkaline complexes survive as intrusive roots only."),
 "Madagascar Traps": (60,
     "Survives as coastal strips (Androy, Mailaka, Analalava). Crucially, "
     "Madagascar's central highlands are Precambrian basement, NOT the 88 Ma basalts "
     "- so this province is not the island's defining relief and should not be drawn "
     "as such. LOW CONFIDENCE."),
 "Magellan Rise": (0,
     "A small but intact Late Jurassic Pacific plateau - among the oldest surviving "
     "seafloor topography anywhere."),
 "Malani Igneous Suite": (500,
     "Silicic volcanics and granites still crop out in Rajasthan, but as low desert "
     "inselbergs; the original ignimbrite plateau was stripped by the early "
     "Paleozoic."),
 "Manihiki Plateau": (0,
     "770,000 km2 with a crest at 2,500-3,000 m and crust 21-25 km thick; rifted "
     "from Ontong Java Nui."),
 "Maud Rise": (0,
     "The Antarctic third of the same 1.2 million km2 plateau, whose relief still "
     "steers the Weddell Gyre and opens the recurring Weddell Polynya."),
 "Mid-Pacific Mountains": (0,
     "A broad guyot-capped rise; the flat tops record subsidence from sea level, so "
     "it was once an island chain and is now a drowned one."),
 "Mundine Well": (700,
     "A dyke swarm in the Pilbara with no preserved extrusive component; valuable as "
     "a paleomagnetic anchor, not as a landform."),
 "N. Kerguelen Plateau": (0,
     "The youngest and shallowest segment, carrying the Kerguelen Islands."),
 "North Atlantic Igneous": (0,
     "Revised to 0 - the remnants ARE landforms, even though the Thulean plateau as "
     "a whole was split and drowned by the rift it caused. East Greenland preserves "
     "up to 2.5 km of basalt over 65,000 km2, the Faroes a ~6 km succession reaching "
     "882 m, and Antrim ~3,086 km2. Iceland is new crust, not preserved 62 Ma "
     "plateau."),
 "Ontong Java Plateau": (0,
     "Still the largest and thickest oceanic plateau on Earth: 1.5-1.86 million km2, "
     "crust 33 km, crest ~1,700 m against a 4,500-5,000 m abyssal floor. Draw it "
     "WHOLE - over 90 percent is intact. It did not subduct; it jammed the Vitiaz "
     "trench and forced a subduction polarity reversal, with only the SW margin "
     "deforming and slices obducted onto Malaita and Santa Isabel."),
 "Panjal Traps": (280,
     "Only 105 km2 of lava flows are exposed today. Pillow lavas and hyaloclastites "
     "show partly submarine emplacement, followed by progressive thermo-tectonic "
     "subsidence of the Indian passive margin. The modern Pir Panjal elevation is "
     "Neogene Himalayan tectonics re-using old rock, NOT a surviving Permian "
     "landform - correcting an easy misreading."),
 "Parana-Etendeka": (0,
     "The Brazilian Serra Geral remains a major plateau and escarpment; Etendeka is "
     "a much smaller severed remnant. Split by South Atlantic opening, with the "
     "Walvis Ridge and Rio Grande Rise marking the join."),
 "Rajmahal Traps": (100,
     "Only ~4,100 km2 is exposed against ~200,000 km2 buried under the Bengal Basin "
     "- about 2 percent visible. Killed by burial, not erosion: the rock is fine, "
     "the landform is gone."),
 "S. Kerguelen Plateau": (0,
     "The main body of a 1.23 million km2 edifice rising 2,000 m above the "
     "surrounding basins. Note it was LAND: ODP recovered fossil wood, charcoal- "
     "bearing soils and river-transported clasts, and at its peak this was an island "
     "of ~500,000 km2 with peaks 1,000-2,000 m above sea level. Final drowning ~20 "
     "Ma."),
 "Seiland Igneous Province": (400,
     "A deep-crustal intrusive complex exhumed only by Caledonian orogeny; it never "
     "had a preserved surface expression. Also allochthonous - it sits in the Kalak "
     "Nappe, so its present coordinates are not where it formed."),
 "Sette-Daban": (900,
     "A sill province on the Siberian craton margin; ~975 Myr of burial and "
     "Verkhoyansk deformation leave no topographic trace."),
 "Shatsky Rise": (0,
     "The oldest surviving oceanic plateau, and empirical proof that isostatic "
     "relief outlasts thermal subsidence: Tamu Massif's summit is at ~1,980 m "
     "against a ~6,400 m base, giving ~4,460 m of relief after 145 Myr, on 26 km of "
     "crust."),
 "Siberian Traps": (0,
     "The Putorana Plateau is the surviving high ground, 800 x 500 km with Mount "
     "Kamen at 1,678 m and the classic trap step-topography intact after 252 Myr on "
     "cold, dead craton - the longest-surviving flood basalt landform of the "
     "Phanerozoic bar Kalkarindji."),
 "Sierra Madre Occidental": (0,
     "The most intact silicic LIP landform on Earth: 1,500 x 240 km broadly above "
     "1,800 m, reaching ~3,340 m, with the Barranca del Cobre cut deeper into it "
     "than the Grand Canyon. Welded ignimbrite is at least as durable as basalt."),
 "Skagerrak-Centred": (250,
     "Preserved as dyke swarms and sills around the Oslo Rift and Skagerrak; the "
     "volcanic edifice did not survive Permian-Triassic rifting and burial."),
 "Suordakh": (350,
     "A small sill-and-volcanic province caught up in the Verkhoyansk fold belt; no "
     "primary landform survives."),
 "Suxiong-Xiaofeng": (750,
     "Bimodal volcanics on the Yangtze craton, buried by the Nanhua rift fill."),
 "Sylhet Traps": (50,
     "Buried beneath the Bengal Basin's Himalayan sediment load; only the Shillong "
     "Plateau margin still exposes it."),
 "Tarim LIP": (280,
     "Largely buried under Tarim Basin sediment, cropping out only at the Keping and "
     "Bachu uplifts. LOW CONFIDENCE."),
 "Volyn Flood Basalts": (450,
     "Preserved but buried beneath the East European Platform cover."),
 "Whitsunday": (60,
     "After CAMP, the best example of a giant province that is not a landform. Its "
     "main surviving record is reworked volcanic detritus in the Eromanga and Great "
     "Artesian basins; Coral Sea rifting at ~62-52 Ma removed most of the rest."),
 "Wichita / S. Oklahoma": (400,
     "Buried under the Anadarko Basin, then partly exhumed as the Wichita Mountains "
     "during the Pennsylvanian - a re-exposed root, not a surviving plateau."),
 "Willouran / Gairdner": (750,
     "Dyke swarms and thin volcanics within the Adelaide Rift Complex; no surviving "
     "relief."),
 "Wrangellia": (150,
     "Ceased to be a plateau when it accreted, but survives in a way no other "
     "province does: it kept its full 25-30 km crustal thickness (usually accretion "
     "strips plateaus to 8-15 km) and is now the Wrangell-St Elias Mountains, "
     "Vancouver Island and Haida Gwaii. Accretion age genuinely spans 160-100 Ma in "
     "the literature. Caveat: its exposed section includes subaerial flows, so it "
     "may never have been a classic deep-ocean plateau."),
 "Yakutsk-Vilyui Traps": (350,
     "Dominantly the Vilyui and Chara-Sinsk dyke swarms plus basalts buried under "
     "the Vilyui Basin. LOW CONFIDENCE."),
 "Yemen Traps": (0,
     "The conjugate half of the same 30 Ma plateau, severed by Red Sea and Gulf of "
     "Aden opening and now standing as the Yemen highlands."),
}


def visible_until():
    return VISIBLE_UNTIL


# ------------------------------------------- plumes and the provinces they made --
# A large igneous province is the opening act of a plume, so the plume has to
# exist on the frame its own province erupts. That is not automatic here: the
# two are catalogued independently, and the audit found four pairs where it
# failed. The worst was Galapagos, drawn as active only from 20 Ma while the
# Caribbean LIP it erupted was being drawn at 95-88 Ma -- the plume was absent
# from the very frames that were its whole reason for existing.
#
# build_webdata checks this on export rather than trusting it.
PLUME_PROVINCE = {
    "Reunion":          ["Deccan Traps"],
    "Kerguelen":        ["Rajmahal Traps", "Comei LIP", "S. Kerguelen Plateau"],
    "Tristan da Cunha": ["Parana-Etendeka"],
    "Galapagos":        ["Caribbean LIP"],
    "Marion":           ["Madagascar Traps"],
    "Iceland":          ["North Atlantic Igneous"],
    "Afar":             ["Ethiopian Traps", "Yemen Traps"],
    "Yellowstone":      ["Columbia River Basalts"],
    "Louisville":       ["Ontong Java Plateau"],
}


def coupling_problems():
    """Plume/province pairs where the plume is not yet active when it erupts."""
    hs = {h[0]: h for h in HOTSPOTS}
    out = []
    for plume, provinces in PLUME_PROVINCE.items():
        p = hs.get(plume)
        if not p:
            out.append(f"{plume}: plume missing from the catalogue")
            continue
        oldest = max(p[3], p[4])
        for prov in provinces:
            q = hs.get(prov)
            if not q:
                out.append(f"{prov}: province missing from the catalogue")
                continue
            erupted = q[6] if q[6] is not None else max(q[3], q[4])
            if oldest < erupted:
                out.append(f"{plume} active only from {oldest} Ma but "
                           f"{prov} erupts at {erupted} Ma")
    return out


# ------------------------------------------- how long a crater shows --
# The layer used to fade every crater over a flat 90 Myr, which is wrong at
# both ends and wrong systematically. A marine or basin impact is buried in
# geological moments -- Chicxulub was invisible within about two million
# years, the worst case here -- while a crater on dry, stable craton vastly
# outlives the average: Manicouagan is 215 Myr old and still the most
# recognisable impact structure on Earth.
#
# `myr` is how long the crater stayed a recognisable surface feature.
SCAR_LIFE = {
 "Acraman": (580, "STILL, in outline. Deeply eroded into the Gawler Range Volcanics, but the circular "
  "playa of Lake Acraman is obvious from orbit after ~580 Myr."),
 "Alhama de Almeria": (3, "Buried and confirmed by drilling; the 22 km figure is exterior collapse terrain, not "
  "a visible crater."),
 "Amelia Creek": (30, "Structurally deformed with no crater morphology left; recognised from shatter cones "
  "and strike-slip-style deformation."),
 "Ames": (5, "Buried ~2.7 km deep in Oklahoma and now a productive oil reservoir in the crater "
  "fill."),
 "Aorounga": (345, "STILL. Concentric rings striped by wind-carved yardangs in the Sahara; a classic "
  "Landsat and SIR-C image. Hyperaridity has preserved a Devonian crater as surface "
  "topography."),
 "Araguainha": (150, "STILL, in fact -- a well-exposed granite central uplift with concentric ring "
  "valleys, obvious from orbit after 255 Myr. South America's largest."),
 "Beaverhead": (30, "TOPOGRAPHY ENTIRELY GONE. Tectonically dismembered by Cordilleran thrusting; there "
  "is no crater form left anywhere. It is known almost solely from a huge shatter-cone "
  "field smeared across thrust sheets, and even its centre is inferred -- published "
  "positions disagree by over a degree."),
 "Boltysh": (5, "Buried under sediment -- which is precisely why its crater-lake record survived "
  "intact enough to log a hyperthermal."),
 "Carswell": (150, "Survives as an exposed ring of Carswell Formation dolomite. Notable for a practical "
  "reason: impact-remobilised uranium ore hosts the Cluff Lake mine."),
 "Cerro do Jarau": (125, "STILL. A central elevated core rising out of the flat Pampas -- highly legible from "
  "orbit."),
 "Charlevoix": (200, "Partially survives as the semicircular St Lawrence embayment, with Mont des "
  "Eboulements as the central uplift. Still a seismically active zone -- the weakened "
  "rock localises modern earthquakes 450 Myr later."),
 "Chesapeake Bay": (5, "Buried under 300-500 m of Coastal Plain sediment. But it never stopped MATTERING: it "
  "still steers the modern bay, drives a groundwater salinity anomaly and causes "
  "measurable land subsidence. A case where 'scar' and 'influence' diverge."),
 "Chicxulub": (2, "BURIED ALMOST IMMEDIATELY. A submarine crater on the Yucatan carbonate shelf, "
  "blanketed within a couple of million years and now under ~1 km of carbonate. It is "
  "traced only by a gravity anomaly and the ring of cenotes. Rendering it as a visible "
  "scar for 90 Myr is the layer's biggest persistence error -- although its GLOBAL "
  "signature (see GLOBAL_EFFECT) is permanent, which is the opposite lesson."),
 "Cleanskin": (30, "~15 km apparent structure with a 6 km central uplift; confirmed on PDFs, planar "
  "fractures and feather features in quartz rather than on any surviving landform."),
 "Clearwater East": (465, "STILL. Lake-filled after 465 Myr -- remarkable persistence, again thanks to glacial "
  "excavation of the weakened rock."),
 "Clearwater West": (286, "STILL. A lake with a central ring of melt-rock islands. Glacial scour sharpened "
  "rather than erased it."),
 "Deep Bay": (99, "STILL. A near-perfect circular bay 220 m deep on Reindeer Lake; one of the sharpest "
  "crater outlines visible from orbit."),
 "Dellen": (140.8, "STILL. Lakes Norra and Sodra Dellen occupy it after 140 Myr."),
 "Eagle Butte": (5, "Fully buried in southern Alberta; imaged by seismic and drilling only."),
 "El'gygytgyn": (3.58, "STILL. A near-perfect circular lake in Chukotka, essentially pristine."),
 "Glikson": (50, "Eroded in the Little Sandy Desert; defined largely by a ring-shaped aeromagnetic "
  "anomaly plus shatter cones."),
 "Gosses Bluff": (142, "STILL. The 5 km central-uplift ring stands 180 m above the desert floor. A textbook "
  "orbital image after 142 Myr."),
 "Gweni-Fada": (345, "STILL. A clear annular ridge on the Ennedi Plateau, preserved by Saharan "
  "hyperaridity."),
 "Haughton": (31, "STILL. Superbly preserved in polar desert on Devon Island -- so well preserved that "
  "NASA runs the Haughton-Mars Project and the Flashline Mars station inside it."),
 "Hiawatha": (58, "A special case: superbly preserved BENEATH ~930 m of the Greenland Ice Sheet. It was "
  "a surface feature in a rainforest landscape for tens of Myr, then sealed by ice "
  "rather than eroded. The only known subglacial crater."),
 "Janisjarvi": (687, "STILL. A lake-filled basin in Karelia after 687 Myr -- the oldest crater on Earth "
  "still holding a lake."),
 "Kaluga": (10, "Buried under Devonian-Carboniferous cover; known from boreholes."),
 "Kamensk": (10, "Buried under Neogene cover."),
 "Kara": (30, "Deeply eroded on Pay-Khoy and partly submerged under the Kara Sea. Carries impact "
  "diamonds."),
 "Karakul": (60, "STILL. Lake Karakul at 3,900 m in the Pamirs fills most of the structure. High- "
  "altitude aridity has preserved it, whatever its true age."),
 "Karla": (5, "Small, buried, minimal expression."),
 "Lappajarvi": (77.9, "STILL. Lake Lappajarvi fills the crater."),
 "Lawn Hill": (100, "Expressed as an 18 km annulus of dolomite hills; the crater form itself is gone but "
  "shatter cones, PDFs and impact diamonds remain."),
 "Lockne": (455, "Partially. Exhumed by Quaternary glaciation after being buried; the resurge deposits "
  "are exceptionally well preserved."),
 "Logancha": (20, "Exposed but heavily eroded on the Siberian Traps."),
 "Logoisk": (5, "Entirely buried in Belarus; found by drilling in the 1970s."),
 "Luizi": (550, "STILL. The rim stands 300-350 m above the interior on the Kundelungu Plateau -- "
  "clearly visible in satellite imagery."),
 "Manicouagan": (215, "STILL. The 'Eye of Quebec' -- an annular reservoir ring around Ile Rene-Levasseur. "
  "215 Myr old and the most recognisable crater on Earth from orbit. Proof that a large "
  "crater in stable Grenvillian basement can outlast the fade window by a factor of "
  "two."),
 "Manson": (10, "The largest fully-onshore US structure and completely buried under glacial drift; "
  "known only from drillcore."),
 "Marquez": (20, "Buried Texas dome; the central uplift is faintly expressed as a topographic high."),
 "Mistastin": (37.9, "STILL. Lake Kamestastin with a central-uplift island; the prime terrestrial analogue "
  "site for lunar impact melt."),
 "Mjolnir": (5, "On the floor of the Barents Sea, entirely submarine and now buried. Known only from "
  "seismic and drilling."),
 "Montagnais": (3, "Submarine on the Scotian Shelf; buried beneath the seafloor and found only by "
  "petroleum drilling."),
 "Morokweng": (15, "Completely buried beneath Kalahari sand. Found by its magnetic signature -- "
  "literally invisible."),
 "Neugrund": (30, "Submarine in the Gulf of Finland; the ejecta layer is better known than the crater."),
 "Nicholson": (50, "An island-studded lake in the NWT, but heavily glacially scoured -- the crater form "
  "is largely gone."),
 "Oasis": (120, "STILL. An ~11.5 km central ring of hills in the Libyan desert."),
 "Obolon": (10, "Buried beneath Dnieper-Donets sediments; no surface expression."),
 "Pantasma": (0.8, "STILL. A young crater basin in the Nicaraguan highlands."),
 "Popigai": (35.7, "STILL. An eroded but well-exposed tundra basin, now a UNESCO geopark."),
 "Puchezh-Katunki": (15, "Buried under Neogene and Quaternary cover; impactites crop out only in Volga bank "
  "cuts."),
 "Ries": (14.8, "STILL. The best-preserved mid-size crater on Earth; the town of Nordlingen is built "
  "inside it and the rim is a visible ring of hills."),
 "Rochechouart": (206.9, "Structure survives, topography does not. No topographic rim is left after 207 Myr, "
  "but the impactites are so well preserved they were quarried as building stone for "
  "the local chateaux. Scar life as topography: ~50 Myr."),
 "Saint Martin": (30, "Buried under Jurassic red beds and glacial till, though Lake St Martin's outline "
  "partly reflects it."),
 "Saqqar": (100, "Exposed in Saudi desert and confirmed on shocked quartz; the largest confirmed "
  "structure on the Arabian Peninsula."),
 "Serra da Cangalha": (250, "STILL. Excellent exposure and a prominent central uplift ring in near-undeformed "
  "Parnaiba Basin sediments."),
 "Shoemaker": (200, "STILL, oddly. Concentric ring synclines with salt lakes, strikingly visible from "
  "orbit despite an age that may exceed a billion years -- Australian cratonic aridity "
  "at its most extreme."),
 "Sierra Madera": (100, "STILL. The central uplift stands out as hills on the West Texas plains, though the "
  "crater is deeply eroded."),
 "Siljan": (380.9, "STILL, partially. Sweden's ring of lakes traces the rim depression around the "
  "central uplift after 380 Myr -- the crater floor was eroded away but the ring of "
  "softer downfaulted sediment survives as topography."),
 "Slate Islands": (100, "Only the central uplift survives, emerging as an archipelago in Lake Superior. The "
  "rest is drowned and eroded. The islands' rocks are full of shatter cones."),
 "Spider": (740, "STILL. The radiating shatter-cone-bearing sandstone ridges that give it its name are "
  "visible from the air after ~740 Myr."),
 "Steen River": (10, "Buried ~200 m deep in Alberta and now a producing oil and gas field."),
 "Strangways": (100, "Deeply eroded in remote Arnhem Land; a prominent central uplift with a >=20 km "
  "collar of upturned and overturned beds is all that remains."),
 "Talundilly": (10, "Same burial history as its neighbour Tookoonooka; seismic-only, never drilled."),
 "Ternovka": (5, "Buried; exposed only inside the Krivoy Rog iron-ore open pits and mine workings."),
 "Tookoonooka": (10, "Buried under ~900 m of Eromanga Basin sediment. Known from seismic plus 31 petroleum "
  "wells -- there is no surface expression at all."),
 "Tunnunik": (50, "Deeply eroded on Victoria Island with no topographic rim; recognised in 2010 only "
  "from shatter-coned bedrock and ring-disturbed strata visible from the air."),
 "Uhackatik": (150, "The reason it was found at all: a ring-shaped basin with 200-300 m rim-to-floor "
  "relief, spotted on Google Maps by an amateur. Survives as topography after ~390 Myr."),
 "Vargeao Dome": (123, "STILL. A 225 m deep depression with a sharp circular rim; three Brazilian "
  "municipalities sit inside it."),
 "Wells Creek": (200, "STILL, as structure. A well-exposed central uplift with classic shatter cones in "
  "Tennessee."),
 "Woodleigh": (20, "Not exposed; buried under the Carnarvon Basin and known only from drilling into the "
  "central uplift."),
 "Yallalie": (5, "Buried under Perth Basin sediments; expressed only as a subtle basin."),
 "Zhamanshin": (0.91, "STILL. The youngest structure of its size on Earth; exposed and fresh."),
}


# A hole in the ground is not the only thing an impact leaves. These are the
# structures whose mark on the world outlasted their own topography --
# an ejecta layer, an extinction, a climate excursion in the record.
GLOBAL_EFFECT = {
 "Acraman": "A distal ejecta horizon traced over 300 km into the Bunyeroo Formation of the "
  "Flinders Ranges. The layer is stratigraphically interleaved with early acritarch and "
  "Ediacaran biotic change, which is why the crater is dated from the ejecta rather "
  "than the other way round.",
 "Araguainha": "Falls within uncertainty of the Permian-Triassic boundary, and the association is "
  "much discussed. But at 40 km it is roughly two orders of magnitude too small in "
  "energy to drive the end-Permian extinction; the Siberian Traps are. The existing "
  "EVENT_NOTES entry already states this correctly and should be kept.",
 "Boltysh": "Not a cause but a RECORDER, and a valuable one. It struck ~0.65 Myr AFTER the K-Pg "
  "extinction, and its crater-lake sediments log the Lower C29n (Dan-C2) hyperthermal "
  "in fine detail -- a direct archive of how the post-extinction world was recovering, "
  "and of a climate excursion that had nothing to do with the impact that made the "
  "lake. Pickersgill et al. (2021) raise the possibility that even a 24 km impact could "
  "perturb an already-stressed recovery.",
 "Chesapeake Bay": "Source of the North American tektite/microtektite strewn field, a global marker "
  "horizon. Separately and unusually, it still exerts a physical influence today: it "
  "controls the shape of the modern Chesapeake Bay, drives a deep groundwater salinity "
  "anomaly across the lower Delmarva Peninsula, and causes measurable ongoing land "
  "subsidence -- 35 Myr after the fact.",
 "Chicxulub": "The only unambiguous impact-driven mass extinction in the record. A worldwide ejecta "
  "and iridium layer at 66.052 +/- 0.043 Ma, sulphate aerosol loading from the "
  "anhydrite-rich target, an impact winter lasting years, and the end of the non-avian "
  "dinosaurs. The topography vanished in ~2 Myr; the boundary clay is permanent and is "
  "found on every continent. If the app renders one thing that outlives its crater, it "
  "is this.",
 "El'gygytgyn": "No ejecta layer, but a globally important scientific consequence: the ICDP core "
  "through its lake sediments yields a continuous 3.6 Myr record of Arctic climate -- "
  "the longest terrestrial Arctic palaeoclimate archive that exists.",
 "Lockne": "One of the craters of the mid-Ordovician meteorite shower, the ~470 Ma spike in "
  "impact flux following the L-chondrite parent-body breakup. That event is recorded "
  "worldwide as fossil meteorites in Swedish and Chinese limestones and is the clearest "
  "evidence of a sustained, non-random change in Earth's impact rate. Ames, Clearwater "
  "East, Carswell, Tunnunik, Slate Islands and possibly Charlevoix all fall in or near "
  "this window -- if the app can cluster events, this Ordovician spike is the one worth "
  "showing.",
 "Manicouagan": "A candidate source for a Late Triassic (Rhaetian/Norian) distal spherule bed "
  "reported from the Bristol Channel, UK (Walkden et al. 2002). The correlation is "
  "reasonable but not as tight as the Chicxulub or Popigai cases, and Manicouagan is "
  "NOT a mass-extinction trigger -- it predates the end-Triassic event by ~14 Myr.",
 "Mjolnir": "Impact into the shallow Jurassic-Cretaceous Barents seaway generated a documented "
  "resurge and tsunami signature in the surrounding basin, and an iridium anomaly is "
  "reported in the Volgian nearby. A claimed correlative tsunami deposit in Sweden is "
  "speculative. Regional, not global -- the existing EVENT_NOTES wording ('triggered a "
  "tsunami across the shallow Jurassic seaway') is appropriately scoped.",
 "Neugrund": "Its ejecta layer, sitting in the pre-trilobite Platysolenites antiquissimus biozone "
  "of the Baltic Early Cambrian, is better known and more useful than the crater -- it "
  "is the sole basis for the ~535 Ma age.",
 "Pantasma": "Probable source of the Belize impact glass (0.769 +/- 0.016 Ma). Schmieder & Kring "
  "list the source crater as unknown with Pantasma as the candidate, so state this as "
  "likely rather than established.",
 "Popigai": "Source of the older late Eocene clinopyroxene-bearing spherule layer, geochemically "
  "tied to the crater (Whitehead et al. 2000, EPSL). A global stratigraphic marker. "
  "Note this is a DIFFERENT layer from the North American tektites -- Popigai and "
  "Chesapeake Bay are separated by at least ~0.5 and possibly ~3 Myr, so the late "
  "Eocene 'cluster' is a sequence, not a pair.",
 "Ries": "Threw moldavite tektites across central Europe -- a regional strewn field several "
  "hundred km east of the crater -- at 14.808 +/- 0.038 Ma.",
 "Tookoonooka": "A distal ejecta blanket across roughly 400,000 km2 of the Eromanga Basin, pinned to "
  "the Barremian/Aptian boundary. The ejecta is the only reason the age is known at all "
  "-- the crater itself is undated. Impact into a shallow epicontinental sea, so there "
  "is a resurge and tsunami signature too.",
}


# How well the age is actually pinned. "poor" covers the ones with no
# radiometric age at all -- Karakul's 25 Ma is an early guess with no
# standing, and Woodleigh's only date is on authigenic clay and was
# formally disputed -- so the app can show those differently rather than
# presenting them with the same authority as a U-Pb age.
IMPACT_CONFIDENCE = {
 "Acraman": ("moderate", "~580 Ma; Impact Earth brackets 541-635 Ma. Age is INDIRECT -- from the Bunyeroo Fm "
  "ejecta horizon, not the crater"),
 "Alhama de Almeria": ("moderate", "~8 Ma, Late Tortonian. Confirmed only in 2023 on a single paper (Sanchez Gomez et "
  "al.); the 22 km is exterior collapse terrain, the true crater is ~5 km"),
 "Amelia Creek": ("poor", "660-1660 Ma. A 1000 Myr window that straddles the cutoff and cannot be resolved"),
 "Ames": ("moderate", "458-478 Ma bracket (Ordovician)"),
 "Aorounga": ("poor", "Middle Devonian-Early Mississippian target bracket, ~345-370 Ma. Impact Earth's "
  "'0.0035-383 Ma' is effectively no constraint at all"),
 "Araguainha": ("moderate", "254.7 +/- 2.5 Ma (Tohver et al. 2012, U-Pb + Ar-Ar). Supersedes 244.4 Ma. Impact "
  "Earth brackets 248-264 Ma"),
 "Beaverhead": ("poor", "470-900 Ma bracket. Structure is tectonically dismembered; no direct date exists"),
 "Boltysh": ("precise", "65.39 +/- 0.14 Ma (Ar-Ar, Pickersgill et al. 2021)"),
 "Carswell": ("precise", "481.5 +/- 0.8 Ma (Ar-Ar adularia). Caveat: dates hydrothermal circulation, a close "
  "minimum"),
 "Cerro do Jarau": ("poor", "<=135 Ma maximum age only (post-Serra Geral basalts). No direct date"),
 "Charlevoix": ("moderate", "450 +/- 20 Ma (U-Pb shocked zircon, Schmieder et al. 2019); S&K bracket ~453-430 Ma"),
 "Chesapeake Bay": ("precise", "34.86 +/- 0.32 Ma (Ar-Ar on melt rock and tektites)"),
 "Chicxulub": ("precise", "66.038 +/- 0.098 Ma (Ar-Ar + U-Pb); boundary ejecta 66.052 +/- 0.043 Ma"),
 "Cleanskin": ("poor", "520-1400 Ma stratigraphic bracket; straddles the cutoff. Confirmed as an impact by "
  "Kenkmann et al. 2021 but undated"),
 "Clearwater East": ("moderate", "460-470 Ma apparent ages. 465 is a computed midpoint, NOT a published value"),
 "Clearwater West": ("precise", "286.2 +/- 2.6 Ma (Ar-Ar plateau)"),
 "Deep Bay": ("moderate", "95-102 Ma (Albian-Cenomanian palynology)"),
 "Dellen": ("precise", "140.82 +/- 0.51 Ma (Ar-Ar). Sharply revised from the legacy 89 Ma"),
 "Eagle Butte": ("poor", "<65 Ma maximum age only"),
 "El'gygytgyn": ("precise", "3.58 +/- 0.04 Ma (Layer 2000). Independently corroborated by ICDP "
  "magnetostratigraphy tuned to 3.580-3.596 Ma. S&K recalculate to 3.65 +/- 0.08 Ma"),
 "Glikson": ("poor", "<513 Ma maximum age only, from Neoproterozoic-Cambrian cover"),
 "Gosses Bluff": ("precise", "142.5 +/- 0.8 Ma (Ar-Ar, Milton & Sutter 1987), corroborated by U-Pb zircon 139 +/- "
  "4 Ma. NOTE: the '165-383 Ma' on Wikipedia's global list is a TARGET-ROCK bracket "
  "that leaked into the age column -- it is an error"),
 "Gweni-Fada": ("poor", "<=383 Ma maximum age only (Devonian-Carboniferous target)"),
 "Haughton": ("precise", "31.04 +/- 0.37 Ma (Ar-Ar shocked K-feldspar, Erickson et al. 2021)"),
 "Hiawatha": ("precise", "57.99 +/- 0.54 Ma (Ar-Ar + U-Pb, Kenny et al. 2022)"),
 "Janisjarvi": ("precise", "687 +/- 5 Ma (Ar-Ar)"),
 "Kaluga": ("moderate", "383-394 Ma bracket (Late Devonian)"),
 "Kamensk": ("precise", "50.37 +/- 0.40 Ma (Ar-Ar)"),
 "Kara": ("moderate", "70.7 +/- 2.2 Ma (Ar-Ar, Trieloff et al. 1998, recalc. S&K 2020). Reject the uncited "
  "75.34 +/- 0.66 Ma"),
 "Karakul": ("poor", "NO radiometric age exists. Only '<60 Ma'. The 25 Ma in the list has no standing; "
  "legacy EID said '<5 Ma'"),
 "Karla": ("poor", "4-6 Ma bracket"),
 "Lappajarvi": ("precise", "77.85 +/- 0.78 Ma (Ar-Ar, ~1%)"),
 "Lawn Hill": ("precise", "476 +/- 8 Ma. Supersedes the stale '>515 Ma' still in circulation"),
 "Lockne": ("moderate", "~455 Ma, tied to Ordovician marine stratigraphy; part of the Ordovician meteorite "
  "shower"),
 "Logancha": ("poor", "40 +/- 20 Ma (50% uncertainty); Impact Earth brackets 23-66 Ma"),
 "Logoisk": ("precise", "29.71 +/- 0.48 Ma (Ar-Ar, Sherlock et al. 2009). The 42.3 +/- 1.1 Ma still on "
  "Wikipedia is the superseded pre-2006 EID value"),
 "Luizi": ("poor", "<=573 Ma maximum age only (post-Neoproterozoic Kundelungu Group)"),
 "Manicouagan": ("precise", "215.56 +/- 0.05 Ma (U-Pb zircon) -- among the best-dated craters on Earth"),
 "Manson": ("precise", "75.9 +/- 0.1 Ma (Ar-Ar) -- one of the tightest in the catalogue"),
 "Marquez": ("moderate", "58.3 +/- 3.1 Ma (~5%)"),
 "Mistastin": ("precise", "37.91 +/- 0.05 Ma (Ar-Ar)"),
 "Mjolnir": ("moderate", "142 +/- 2.6 Ma; Impact Earth brackets 141-145 Ma"),
 "Montagnais": ("moderate", "51.1 +/- 1.6 Ma (~3%)"),
 "Morokweng": ("precise", "146.06 +/- 0.16 Ma (U-Pb); sits on the Jurassic-Cretaceous boundary"),
 "Neugrund": ("moderate", "~535 Ma, Early Cambrian, BIOSTRATIGRAPHIC only -- ejecta sits in the pre-trilobite "
  "Platysolenites antiquissimus biozone. No radiometric date. An older ~470 Ma estimate "
  "is superseded"),
 "Nicholson": ("precise", "387 +/- 5 Ma (~1.3%)"),
 "Oasis": ("poor", "<120 Ma maximum age only"),
 "Obolon": ("moderate", "169 +/- 7 Ma (~4%)"),
 "Pantasma": ("precise", "0.804 +/- 0.009 Ma (Ar-Ar)"),
 "Popigai": ("precise", "35.7 +/- 0.2 Ma (Bottomley et al. 1997); 36.63 +/- 0.92 Ma recalculated by S&K 2020"),
 "Puchezh-Katunki": ("precise", "195.9 +/- 1.0 Ma (Holm-Alwmark et al. 2019)"),
 "Ries": ("precise", "14.808 +/- 0.038 Ma -- the single most precisely dated impact structure on Earth"),
 "Rochechouart": ("precise", "206.92 +/- 0.32 Ma (Ar-Ar)"),
 "Saint Martin": ("precise", "227.8 +/- 0.9 Ma (Ar-Ar)"),
 "Saqqar": ("poor", "70-410 Ma stratigraphic bracket only. A 340 Myr window"),
 "Serra da Cangalha": ("poor", "<=250 Ma maximum age only (Parnaiba Basin stratigraphy)"),
 "Shoemaker": ("poor", "568-1300 Ma. Ar-Ar K-feldspar older limit ~1300 Ma, K-Ar illite-smectite younger "
  "limit ~568 Ma; the authors caution 568 Ma may be a tectonothermal reset. Cannot be "
  "placed on either side of 1000 Ma. NO post-2015 redating exists; the '~836 Ma' figure "
  "in circulation has no traceable source"),
 "Sierra Madera": ("poor", "<113 Ma (Albian or younger) maximum age only"),
 "Siljan": ("moderate", "380.9 +/- 4.6 Ma (Ar-Ar), ~1.2%"),
 "Slate Islands": ("poor", "~450 Ma, poorly constrained, no formal uncertainty published"),
 "Spider": ("poor", "580-900 Ma. Younger than the ~900 Ma Yampi Orogeny syncline, older than ~570 Ma "
  "cover"),
 "Steen River": ("poor", "Three live candidates: ~91, ~132 +/- 1.3, ~141 Ma. S&K bracket ~383-108 Ma. Impact "
  "Earth: 108-383 Ma"),
 "Strangways": ("poor", "657 +/- 43 Ma (~6.5%)"),
 "Talundilly": ("poor", "~125 Ma inferred by correlation with Tookoonooka. STRUCTURE ITSELF IS UNCONFIRMED -- "
  "seismic only, never drilled"),
 "Ternovka": ("moderate", "280 +/- 10 Ma (~3.5%)"),
 "Tookoonooka": ("moderate", "125 +/- 1 Ma, but a STRATIGRAPHIC tie to the Barremian/Aptian boundary, not a "
  "radiometric date. Impact Earth: 121.8-123.8 Ma"),
 "Tunnunik": ("moderate", "430-450 Ma bracket (Ar-Ar)"),
 "Uhackatik": ("poor", "~390 Ma, provisional. Conference abstract only (MetSoc 2026 #5369); no peer-reviewed "
  "paper, no stated uncertainty"),
 "Vargeao Dome": ("precise", "123 +/- 1.4 Ma"),
 "Wells Creek": ("poor", "100-323 Ma bracket; ~200 Ma is a commonly quoted midpoint with no direct support"),
 "Woodleigh": ("poor", "NO reliable age. 364 +/- 8 Ma is K-Ar on authigenic clay, formally disputed. "
  "S&K/Impact Earth: 168-2005 Ma bracket"),
 "Yallalie": ("moderate", "83.6-89.8 Ma (Coniacian-Santonian stratigraphic bracket). Australia's first "
  "confirmed Late Cretaceous impact"),
 "Zhamanshin": ("moderate", "0.91 +/- 0.14 Ma (~15%, but on an absolute scale this is very tightly placed)"),
}


def scar_life():
    return SCAR_LIFE


def global_effect():
    return GLOBAL_EFFECT


def impact_confidence():
    return IMPACT_CONFIDENCE
