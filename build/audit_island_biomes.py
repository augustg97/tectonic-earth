"""Do small landmasses draw the climate the field gives them?

THE DEFECT THIS EXISTS FOR. `rainAt` warps its lookup so biome edges wander
instead of running ruler-straight. Sized for continents, the displacement
reached 12.8 degrees of longitude and 6.4 of latitude -- and Cuba is 1.4 degrees
tall. The warp did not perturb the sample at the island's edge, it moved it into
the open Atlantic, so the shader read a rainfall of 0.01 where the field stores
0.383. Cuba, Florida and the Bahamas all drew as desert on wet ground, in the
shipped build, for as long as the warp has existed.

Nothing caught it. `audit_biomes` has eighteen reference sites and every one is
on a continent, because the sites were chosen to span CLIMATE and small islands
are not a distinct climate -- they are a distinct GEOMETRY, and geometry is what
broke.

So this checks the render against the field on land small enough for a lookup
warp to miss: islands, peninsulas, isthmuses. It compares what the shader drew
with what the field says it should have drawn, which is a different question
from "is the field right" -- that one is audit_biomes'.

    ../venv/bin/python shoot.py --nolabels isl_carib,-77,20,0,1.6 \\
        isl_seasia,120,5,0,1.8 isl_medit,16,38,0,2.0 isl_tyrrh,9.1,40.1,0,2.4
    ../venv/bin/python audit_island_biomes.py
"""
import os
import sys

import numpy as np
from PIL import Image

try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = os.path.join(HERE, "..", "web", "fields")
VERIFY = os.path.join(HERE, "verify")
RF_MAX = 1.6

# (shot, centre lon, centre lat) -- half-width is DERIVED per shot, never
# assumed; guessing it once cost nine rounds of wrong measurements elsewhere.
#
# AND EVERY SITE WANTS A CENTRE NEAR IT. The lon/lat -> pixel mapping below is
# linear, the globe's projection is not, and the error grows with angular
# distance from the shot centre. Sardinia sits 7 degrees west of the
# Mediterranean shot's centre -- further than any other site -- and the mapping
# put it in the Tyrrhenian Sea, where "not desert" is true of water and the test
# passed having measured nothing. It gets its own centred framing. A site more
# than about 5 degrees off-centre should get one too.
SHOTS = [("isl_carib", -77.0, 20.0), ("isl_seasia", 120.0, 5.0),
         ("isl_medit", 16.0, 38.0), ("isl_tyrrh", 9.1, 40.1)]

# (shot, name, lon, lat) -- land small enough that a warped lookup can leave it
SITES = [
    ("isl_carib", "Cuba", -79.0, 21.8),
    ("isl_carib", "Jamaica", -77.3, 18.1),
    ("isl_carib", "Hispaniola", -70.5, 19.0),
    ("isl_seasia", "Java", 110.0, -7.3),
    ("isl_seasia", "Sulawesi", 120.5, -2.0),
    ("isl_seasia", "Luzon", 121.0, 16.0),
    ("isl_medit", "Sicily", 14.2, 37.6),
    ("isl_tyrrh", "Sardinia", 9.1, 40.1),
    ("isl_medit", "Crete", 24.8, 35.2),
]


def field(name):
    p = os.path.join(FIELDS, "phan_0000_%s" % name)
    return np.asarray(Image.open(p).convert("L")).astype(float)


def derive_half(shot, lon0, lat0, land_field):
    """Fit the framing's half-width from the shot's own land-mask row profile."""
    im = np.asarray(Image.open(os.path.join(VERIFY, shot + ".png")).convert("RGB")).astype(float)
    shot_land = ~((im[:, :, 2] > im[:, :, 1] + 4) & (im[:, :, 2] > im[:, :, 0] + 10))
    prof = shot_land.mean(axis=1)
    eh, ew = land_field.shape
    best = None
    for half in np.arange(2.0, 20.01, 0.25):
        r0 = int((90 - (lat0 + half)) / 180 * eh); r1 = int((90 - (lat0 - half)) / 180 * eh)
        c0 = int((lon0 - half + 180) / 360 * ew); c1 = int((lon0 + half + 180) / 360 * ew)
        if r1 <= r0 or c1 <= c0:
            continue
        lm = (land_field[r0:r1, c0:c1] > 0).astype(np.float32)
        p = np.array(Image.fromarray(lm).resize((1, len(prof)), Image.BILINEAR)).ravel()
        e = float(np.mean((p - prof) ** 2))
        if best is None or e < best[0]:
            best = (e, half)
    return best[1] if best else None, im


def main():
    rain = field("r.webp") / 255.0 * RF_MAX
    e = field("e.avif") / 255.0
    d = e * 2.0 - 1.0
    elev = np.sign(d) * d * d * 8000.0

    bad, checked, skipped, missed = [], 0, [], []
    print("  small-land biome lookup: does the render match the field?")
    print("    %-12s %8s %10s %8s"
          % ("site", "field Rf", "rendered", "verdict"))
    for shot, lon0, lat0 in SHOTS:
        if not os.path.exists(os.path.join(VERIFY, shot + ".png")):
            print("    %-12s no shot" % shot)
            continue
        half, im = derive_half(shot, lon0, lat0, elev)
        if half is None:
            continue
        for s, name, lon, lat in SITES:
            if s != shot:
                continue
            eh, ew = rain.shape
            rf = float(rain[int((90 - lat) / 180 * eh), int((lon + 180) / 360 * ew) % ew])
            x = int((lon - (lon0 - half)) / (2 * half) * im.shape[1])
            y = int(((lat0 + half) - lat) / (2 * half) * im.shape[0])
            if not (0 <= x < im.shape[1] and 0 <= y < im.shape[0]):
                # NEVER skip silently. A site that falls outside its framing is
                # a site not tested, and a validator that prints "all ok" while
                # quietly dropping one is worse than no validator. Sardinia did
                # exactly this on the first run.
                skipped.append(name)
                continue
            c = im[y, x]
            # THE PIXEL MUST BE ON LAND, or the test passes for free: water is
            # never red-dominant, so a site that lands offshore reports "ok"
            # while testing nothing. Sardinia and Crete both did this once the
            # framing moved. Checked against the shipped elevation field AND
            # against the pixel's own colour, because either alone can lie.
            eh2, ew2 = elev.shape
            on_land_field = elev[int((90 - lat) / 180 * eh2),
                                 int((lon + 180) / 360 * ew2) % ew2] > 0.0
            looks_wet = (c[2] > c[1] + 4) and (c[2] > c[0] + 10)
            if on_land_field and looks_wet:
                # Framing derivation is good to a fraction of a degree, which on
                # a 60 km island can be the difference between the coast and the
                # water beside it. Search a few pixels for the island before
                # giving up -- tolerating that error is fair; skipping the site
                # silently is not.
                for rad in range(1, 8):
                    found = False
                    for dy in range(-rad, rad + 1):
                        for dx in range(-rad, rad + 1):
                            yy, xx = y + dy, x + dx
                            if not (0 <= xx < im.shape[1] and 0 <= yy < im.shape[0]):
                                continue
                            cc = im[yy, xx]
                            if not ((cc[2] > cc[1] + 4) and (cc[2] > cc[0] + 10)):
                                c, looks_wet, found = cc, False, True
                                break
                        if found:
                            break
                    if found:
                        break
            if on_land_field and looks_wet:
                missed.append(name)
                print("    %-12s %8.3f %10s %8s"
                      % (name, rf, "%.0f,%.0f,%.0f" % tuple(c),
                         "SAMPLED WATER -- site not tested"))
                continue
            checked += 1
            # A wet field must not render as bare ground: red far above green.
            desert = (c[0] > c[1] + 25) and (c[0] > c[2] + 45)
            wet = rf > 0.30
            fail = wet and desert
            if fail:
                bad.append(name)
            print("    %-12s %8.3f %10s %8s"
                  % (name, rf, "%.0f,%.0f,%.0f" % tuple(c),
                     "DESERT ON WET GROUND" if fail else "ok"))
    if not checked:
        print("  audit_island_biomes: no shots -- see the usage in the docstring")
        return 1
    if missed:
        print("  %d site(s) sampled open water and were NOT tested: %s"
              % (len(missed), ", ".join(missed)))
    if skipped:
        print("  %d site(s) fell outside their framing and were NOT tested: %s"
              % (len(skipped), ", ".join(skipped)))
    if bad:
        print("  %d of %d small landmasses draw as desert on wet ground: %s"
              % (len(bad), checked, ", ".join(bad)))
        return 1
    print("  all %d small landmasses draw the climate their field gives them"
          % checked)
    return 1 if (skipped or missed) else 0


if __name__ == "__main__":
    sys.exit(main())
