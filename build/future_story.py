"""The future's plate motions, stage by stage (3.16).

Read with Scotese (2018), "Atlas of Future Plate Tectonic Reconstructions:
Modern World to Pangea Proxima (+250 Ma)", PALEOMAP Project. Every keyframe
below cites the stage it draws. Positions are ANCHORS -- a present-day point
on the plate is put against a point on another plate as that plate stands at
the same time -- fitted as rigid rotations; future_tectonics interpolates
between keyframes smoothly and the collision model shortens the margins where
continents meet, so an anchor ~100 km inside another continent is a collision
of that size, not an overlap that stays.

Frame: no-net-rotation, like the NNR-MORVEL56 velocities the first 25 Myr are
extrapolated from. Latitude is what the climate sees, so it is kept close to
Scotese's: Pangea Proxima straddles the equator at +250.

Coordinates are (lon, lat) of TODAY's points.
"""
import math

import numpy as np

# present-day anchor points
GUINEA = (-13.7, 9.5)          # Conakry, West Africa
DAKAR = (-17.4, 14.7)
MOROCCO = (-9.6, 30.4)         # Agadir
LUANDA = (13.2, -8.8)          # south-west Africa
WALVIS = (14.5, -22.9)
AGULHAS = (20.0, -34.8)        # southern tip of Africa
DURBAN = (31.0, -29.9)
MAPUTO = (32.6, -25.9)
GUARDAFUI = (51.3, 11.8)
ST_JOHNS = (-52.7, 47.6)       # Newfoundland
HALIFAX = (-63.6, 44.6)
NEW_YORK = (-74.0, 40.7)
MIAMI = (-80.2, 25.8)
CAPE_FAREWELL = (-43.9, 59.8)  # southern Greenland
RECIFE = (-34.8, -7.1)         # eastern tip of Brazil
SALVADOR = (-38.5, -13.0)
RIO = (-43.2, -22.9)
PUNTA_DEL_ESTE = (-54.9, -34.9)
MAR_DEL_PLATA = (-57.5, -38.0)
QUEEN_MAUD = (10.0, -70.0)     # East Antarctica, Atlantic coast
ENDERBY = (50.0, -66.5)
DAVIS = (93.0, -66.5)          # East Antarctica, Indian Ocean coast
ADELIE = (140.0, -66.7)
CAPE_ADARE = (170.3, -71.3)
PENINSULA = (-57.0, -63.4)     # tip of the Antarctic Peninsula (West Antarctica)
MARIE_BYRD = (-130.0, -74.0)
THURSTON = (-98.0, -72.0)
PADANG = (100.4, -0.9)         # Sumatra, SW coast
BANDA_ACEH = (95.3, 5.5)
JAVA_S = (110.0, -8.2)
HONG_KONG = (114.2, 22.3)
TAIWAN = (121.0, 23.7)
BROOME = (122.2, -18.0)        # NW Australia
EXMOUTH = (114.1, -21.9)
LEEUWIN = (115.1, -34.4)       # SW Australia
DARWIN = (130.8, -12.4)
JAYAPURA = (140.7, -2.5)       # New Guinea, north coast
KANYAKUMARI = (77.5, 8.1)
ANCHORAGE = (-149.9, 61.2)
CABO_SL = (-109.9, 22.9)       # tip of Baja California


def spinz(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def ease(t, t0, t1):
    s = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
    return s * s * (3.0 - 2.0 * s)


def author(FT):
    K = FT.add_key
    I = np.eye(3)
    for p in FT.PLATES:
        K(p, 0.0, I)

    # ---- STAGE 0-25 Myr: today's motion, for everyone (Scotese: "the first 50
    # million years is a simple extrapolation"). Keys at 10 and 25 are the
    # exact constant-rotation positions, so the spline starts on the measured
    # velocity.
    for p in FT.PLATES:
        for t in (10.0, 25.0):
            K(p, t, FT.present_motion(p, t))

    # ---- EURASIA: the frame of the northern half. Today's slow eastward
    # drift to +50, easing to rest by +90, then "the Afro-Asian continent is
    # pulled toward North America" (+100-225): 14 degrees west by +250.
    for t in (50.0,):
        K("EURASIA", t, FT.present_motion("EURASIA", t))
    E50 = FT.rot("EURASIA", 50.0)
    E75 = FT.expm(FT.omega0("EURASIA") * 12.0) @ E50
    K("EURASIA", 75.0, E75)
    K("EURASIA", 100.0, E75)
    for t in (125.0, 150.0, 175.0, 200.0, 225.0, 250.0):
        K("EURASIA", t, spinz(-14.0 * ease(t, 100.0, 250.0)) @ E75)

    def eu_follow(p, t0, times):
        for t in times:
            K(p, t, FT.rot("EURASIA", t) @ FT.rot("EURASIA", t0).T @ FT.rot(p, t0))

    later = (75.0, 100.0, 125.0, 150.0, 175.0, 200.0, 225.0, 250.0)

    # ---- AFRICA: today's NE drift closes the Mediterranean and, against
    # Arabia, the Red Sea (+25-50); the Alps push into Germany and Poland
    # (+75); from there Africa is welded to Eurasia.
    K("AFRICA", 50.0, FT.present_motion("AFRICA", 50.0))
    A75 = FT.expm(FT.omega0("AFRICA") * 8.0) @ FT.rot("AFRICA", 50.0)
    E_rel = FT.rot("EURASIA", 75.0) @ FT.rot("EURASIA", 50.0).T
    K("AFRICA", 75.0, E_rel @ A75)
    eu_follow("AFRICA", 75.0, later[1:])

    # ---- ARABIA: into Iran (the Zagros) at today's rate for 10 Myr, then
    # locked against Eurasia by +40 while Africa closes the Red Sea behind it.
    K("ARABIA", 25.0, FT.expm(FT.omega0("ARABIA") * 6.0) @ FT.present_motion("ARABIA", 10.0))
    eu_follow("ARABIA", 25.0, (50.0,) + later)

    # ---- INDIA: "the collision of India with Asia has stopped" by +50.
    eu_follow("INDIA", 25.0, (50.0,) + later)

    # ---- AUSTRALIA: north at ~7 cm/yr into Indonesia and "begins to collide
    # with southeastern China" (+50), "completely closing the South China Sea"
    # (+75); welded to Asia after, the Sino-Australian mountains wearing down.
    # Today's velocity carries Australia north-north-east, past the Philippines
    # into the open Pacific; Scotese's Australia swings north-west into SE
    # China instead, so from +25 it is steered: by +60 New Guinea's north coast
    # is against Taiwan and the South China Sea is closing, NW Australia
    # against eastern Borneo (the Indonesian archipelago between them is
    # crushed -- "the back-arc basins of SE Asia are replaced by mountain
    # ranges"). Targets are present-day points carried with Eurasia, 150 km
    # short of contact, so the collision model does the rest.
    t_au = 60.0
    tw = FT.offset(FT.at("EURASIA", t_au, *TAIWAN), FT.at("EURASIA", t_au, 125.0, 10.0), 150.0)
    bo = FT.offset(FT.at("EURASIA", t_au, 118.5, 1.0), FT.at("EURASIA", t_au, 128.0, 0.0), 150.0)
    A60 = FT.dock("AUSTRALIA", t_au, [(JAYAPURA, tw), (BROOME, bo)])
    K("AUSTRALIA", 45.0, FT.expm(FT.logm(A60 @ FT.rot("AUSTRALIA", 25.0).T) * 0.62) @ FT.rot("AUSTRALIA", 25.0))
    K("AUSTRALIA", t_au, A60)
    A85 = FT.expm(FT.logm(A60 @ FT.rot("AUSTRALIA", 45.0).T) * 0.35) @ A60   # still converging, slowing
    K("AUSTRALIA", 85.0, FT.rot("EURASIA", 85.0) @ FT.rot("EURASIA", t_au).T @ A85)
    eu_follow("AUSTRALIA", 85.0, later[1:])

    # ---- EAST ANTARCTICA: today's slow turn to +40; "drawn northward by
    # north-directed subduction beneath the Capricorn subduction zone" (+50),
    # "rapidly" (+75-100), "into tropical waters" (+125), and at +150 it
    # "collides with the island arcs of the Capricorn Trench, Sumatra and
    # northwest Australia closing the Indian Ocean". Welded to Asia after.
    K("ANTARCTICA_E", 40.0, FT.present_motion("ANTARCTICA_E", 40.0))
    t_dock = 150.0
    # Its Indian Ocean coast ends up facing north across the remnant sea: Davis
    # Sea just off Sumatra, Queen Maud Land at the far west end -- positions
    # given in Eurasia's frame (today's Indian Ocean carried with Eurasia), so
    # the space between Queen Maud Land and southern Africa is what South
    # America's eastern margin fills at +250.
    sum_q = FT.at("EURASIA", t_dock, 97.0, -5.5)
    qm_q = FT.at("EURASIA", t_dock, 63.0, -22.0)
    AE150 = FT.dock("ANTARCTICA_E", t_dock,
                    [(DAVIS, sum_q), (QUEEN_MAUD, qm_q)])
    AE40 = FT.rot("ANTARCTICA_E", 40.0)
    D = AE150 @ AE40.T
    dlog = FT.logm(D)
    # ...and it slows as it arrives: a continent that meets another does not
    # keep its speed (Scotese: "Antarctica's northward motion is halted due to
    # its collision with the island arcs of the Capricorn Trench")
    for t, s in ((75.0, 0.22), (100.0, 0.52), (125.0, 0.85), (140.0, 0.97)):
        K("ANTARCTICA_E", t, FT.expm(dlog * s) @ AE40)
    K("ANTARCTICA_E", t_dock, AE150)
    eu_follow("ANTARCTICA_E", t_dock, (175.0, 200.0, 225.0, 250.0))

    # ---- WEST ANTARCTICA: with East Antarctica until a rift "forms in the
    # Weddell Sea and Ross Sea" (+75); it lags behind as the Trans-Antarctic
    # Ocean opens (+100-125), is then drawn back ("the Trans-Antarctic Ocean
    # begins to close", +150; "rapidly approaches", +200) and "has collided
    # with southwestern Australia" by +225.
    for t in (40.0, 50.0, 60.0, 70.0, 75.0):
        K("ANTARCTICA_W", t, FT.rot("ANTARCTICA_E", t))
    AW75 = FT.rot("ANTARCTICA_W", 75.0)
    lag = FT.logm(FT.rot("ANTARCTICA_E", 125.0) @ AW75.T)
    K("ANTARCTICA_W", 100.0, FT.expm(lag * 0.25) @ AW75)
    K("ANTARCTICA_W", 125.0, FT.expm(lag * 0.45) @ AW75)
    t_w = 225.0
    swa_q = FT.offset(FT.at("AUSTRALIA", t_w, *LEEUWIN), FT.at("AUSTRALIA", t_w, 125.0, -25.0), -60.0)
    ea_q = FT.offset(FT.at("ANTARCTICA_E", t_w, *CAPE_ADARE), FT.at("ANTARCTICA_E", t_w, 60.0, -80.0), -60.0)
    AW225 = FT.dock("ANTARCTICA_W", t_w, [(PENINSULA, swa_q), (MARIE_BYRD, ea_q)])
    AW125 = FT.rot("ANTARCTICA_W", 125.0)
    D = FT.logm(AW225 @ AW125.T)
    for t, s in ((150.0, 0.25), (175.0, 0.58), (200.0, 0.88), (212.0, 0.97)):
        K("ANTARCTICA_W", t, FT.expm(D * s) @ AW125)
    K("ANTARCTICA_W", t_w, AW225)
    eu_follow("ANTARCTICA_W", t_w, (250.0,))

    # ---- SOUTH AMERICA: today's westward drift eases by +50; the South
    # Atlantic "contracts as ocean floor is subducted beneath eastern South
    # America" and from +100 "the Afro-Asian continent is pulled towards South
    # America"; "the eastern tip of Brazil collides with the southern tip of
    # Africa" (+225), and by +250 "the northeastern and eastern margin of South
    # America has collided with South Africa and East Antarctica".
    K("SOUTH_AMERICA", 50.0, FT.expm(FT.omega0("SOUTH_AMERICA") * 12.0) @ FT.rot("SOUTH_AMERICA", 25.0))
    t_sa = 250.0
    cape = FT.offset(FT.at("AFRICA", t_sa, *AGULHAS), FT.at("AFRICA", t_sa, 22.0, 0.0), -70.0)
    ea_w = FT.offset(FT.at("ANTARCTICA_E", t_sa, *QUEEN_MAUD), FT.at("ANTARCTICA_E", t_sa, 70.0, -80.0), -70.0)
    SA250 = FT.dock("SOUTH_AMERICA", t_sa, [(RECIFE, cape), (MAR_DEL_PLATA, ea_w)])
    SA50 = FT.rot("SOUTH_AMERICA", 50.0)
    D = FT.logm(SA250 @ SA50.T)
    for t in (75.0, 100.0, 125.0, 150.0, 175.0, 200.0, 225.0):
        K("SOUTH_AMERICA", t, FT.expm(D * ease(t, 60.0, 250.0)) @ SA50)
    K("SOUTH_AMERICA", t_sa, SA250)

    # ---- NORTH AMERICA: today's WSW drift eases by +50 ("the North and
    # Central Atlantic begins to contract as the Mid-Atlantic Ridge is subducted
    # beneath Greenland", +25); pulls away from Siberia (the Verkhoyansk Ocean,
    # +100-175); "Newfoundland collides with West Africa" (+225); at +250
    # "Greenland and North America have collided with western Africa" and
    # "Florida and the southeastern United States have collided with
    # southwestern Africa" -- further south than where it rifted away.
    K("NORTH_AMERICA", 50.0, FT.expm(FT.omega0("NORTH_AMERICA") * 12.0) @ FT.rot("NORTH_AMERICA", 25.0))
    t_na = 250.0
    gui = FT.offset(FT.at("AFRICA", t_na, *GUINEA), FT.at("AFRICA", t_na, 15.0, 5.0), -70.0)
    lua = FT.offset(FT.at("AFRICA", t_na, *LUANDA), FT.at("AFRICA", t_na, 25.0, -8.0), -70.0)
    NA250 = FT.dock("NORTH_AMERICA", t_na, [(ST_JOHNS, gui), (MIAMI, lua)])
    NA50 = FT.rot("NORTH_AMERICA", 50.0)
    D = FT.logm(NA250 @ NA50.T)
    for t in (75.0, 100.0, 125.0, 150.0, 175.0, 200.0, 225.0):
        K("NORTH_AMERICA", t, FT.expm(D * ease(t, 60.0, 250.0)) @ NA50)
    K("NORTH_AMERICA", t_na, NA250)

    # ---- PACIFIC: today's motion throughout; its floor goes down beneath Asia.
    for t in (50.0,) + later:
        K("PACIFIC", t, FT.present_motion("PACIFIC", min(t, 250.0)))

    # ---- BAJA and western California: north with the Pacific plate; "begin to
    # collide with southern Alaska" (+75), accreted by +100 ("the Californian
    # mountain ranges are added to southern Alaska"), then part of North America.
    for t in (50.0, 75.0):
        K("BAJA", t, FT.present_motion("BAJA", t))
    K("BAJA", 90.0, FT.expm(FT.omega0("BAJA") * 6.0) @ FT.present_motion("BAJA", 75.0))
    for t in (100.0, 125.0, 150.0, 175.0, 200.0, 225.0, 250.0):
        K("BAJA", t, FT.rot("NORTH_AMERICA", t) @ FT.rot("NORTH_AMERICA", 90.0).T @ FT.rot("BAJA", 90.0))
