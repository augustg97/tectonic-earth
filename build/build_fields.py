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
  * Precambrian 540-1000 Ma -- generated cratons (see precambrian.py), blended
    onto the real 540 Ma DEM across the youngest 60 Myr so the handoff into the
    Phanerozoic is continuous instead of popping.

A third texture per keyframe carries derived plate motion (see motion.py),
which drives both the motion-vector arrows and the plate boundaries at every
age rather than only near the present.
"""
import os, re, json, glob, io, math
import numpy as np
import netCDF4
from PIL import Image

import render as R
from render import compute_fields, resample_dem, smooth_bathymetry, glaciation
from climate import climate_at, system_at
from fieldpack import enc_elev, RF_MAX
from build_frames import period_for, sealevel_for, index_dems, read_dem
import build_synthetic as BS
import precambrian as PRE
import epeiric as EP
import seafloor as SF
import motion as MO
import paleo_tracks

OUT = "../web/fields"
os.makedirs(OUT, exist_ok=True)

# 2048x4096, doubled in July 2026. The source PaleoDEMs are 6 arc-minute --
# 0.1 degrees, 11.1 km at the equator -- and at 1024x2048 a texel was 19.5 km,
# so HALF the resolution that exists was being thrown away before anything else
# happened. Everything downstream inherited that: a continental slope drops
# 3 km across two texels and arrives as a staircase of near-vertical facets, a
# seamount is three texels across, and the shader has to reconstruct what the
# grid could not carry. 2048 rows puts a texel at 9.8 km, which is the source
# resolution and therefore the point at which more pixels stop buying anything.
#
# Cost, measured on the 0 Ma frame against a lossless encode: 439 kB at q=94
# against 198 kB at 1024x2048/q=96, and the same steep-ground error (0.71 levels
# mean, 3 at the 99th percentile). Across 251 keyframes that is about 51 MB
# against 25, so the elevation roughly doubles and the whole payload goes from
# 118 to ~144 MB. Quality drops 96 -> 94 because the finer grid needs less help:
# there is less real content per texel for the encoder to ring around.
ELEV_H, ELEV_W = 2048, 4096     # coastline resolution; matches the 6' source DEM
# Rainfall drives biome colour, the glacier equilibrium line AND the weighting
# on the drainage network, so it is the field that decides how varied a
# continent looks -- and at 768x384 it was the coarsest input in the pipeline,
# a quarter the linear resolution of the elevation it is painted over. That
# mismatch is most of why large landmasses came out in flat patches.
#
# CLIM is the resolution the wind solve actually RUNS at, and raising only the
# export would have bought nothing: the detail has to exist before it can be
# saved. Both go up together.
RAIN_H, RAIN_W = 768, 1536      # rainfall texture, 4x the pixels
CLIM_H, CLIM_W = 768, 1536      # the wind solve runs here too, or there is
                                # no new detail to export
# Ocean-structure field: crustal age + spreading direction. It is smooth (the
# fine abyssal-hill fabric is synthesised in the shader from it, not stored), so
# a quarter of the elevation resolution is ample and keeps the extra webp small.
# Deliberately NOT raised with the elevation: this field's limit is precision,
# not resolution -- see the companding note in seafloor.py -- and more pixels
# would cost real bytes to store a field that is already smooth between them.
OCEAN_H, OCEAN_W = 1024, 2048
# ELEV_Q is 94, and the reason is measurable rather than a matter of
# taste. WebP's lossy path rings around sharp edges, and the elevation field is
# encoded signed-sqrt so that one 8-bit level is 55 m at 1.5 km depth and 105 m
# at 5.5 km. Measured against a lossless encode of the same field, q=92 puts a
# mean error of 0.97 levels and a 99th percentile of FOUR on steep submarine
# ground (against 0.06 on flat abyss) -- i.e. a couple of hundred metres of
# invented relief, spatially organised as ringing, which the hillshade renders
# as the granular black speckle that covered every ridge flank and shelf edge.
# It is not visible on the abyssal plains because there is no edge there to ring
# around, which is exactly why it took so long to attribute.
#
# It buys the one thing the shader cannot: the shader's dequantisation shrinkage
# knows the size of a QUANTISATION step and can remove it exactly, but ringing is
# several steps and indistinguishable from real relief once it is in the file.
#
# 94 rather than 96 because the grid doubled at the same time. Measured on the
# 0 Ma frame, 2048x4096/q=94 lands at the same steep-ground error as
# 1024x2048/q=96 -- 0.71 levels mean, 3 at the 99th percentile -- for 439 kB
# against 198. Finer texels hold less real content each, so there is less for
# the encoder to ring around and the quality can come back down.
ELEV_Q, RAIN_Q, OCEAN_Q = 90, 90, 90   # ELEV_Q is now an AVIF quality
STEP = 5                         # Myr between keyframes, everywhere


def polar_lowpass(z, strength=1.0):
    """Band-limit the poleward rows of an equirectangular grid along longitude.

    THE ROOT CAUSE OF POLAR WARPING. An equirectangular grid stores the same
    number of longitude columns in every latitude row, so approaching a pole
    those columns crowd into a vanishing circle: at 89.9 degrees the 2048
    columns of a row span about 70 km of ground, a third of a kilometre each,
    while the rows stay ~20 km apart. Nothing in the source data resolves that,
    so the surplus is pure resampling noise -- and because it varies with
    longitude, a globe renders it as a radial starburst fanning out of the pole.
    Every downstream consumer inherits it: relief shading, ice, the depth ramp.

    Averaging each row over 1/cos(lat) columns removes exactly that surplus and
    nothing else. One column at the equator (a no-op), ~3 at 70 degrees, ~11 at
    85, most of the row inside the last tenth of a degree -- which is right,
    because there those columns really are all the same few kilometres of
    ground. Real geography survives: a coastline at 85 degrees still spans
    hundreds of columns.

    Doing it HERE rather than in the shader means it is fixed once, for every
    field and every consumer, at no per-pixel cost.
    """
    from scipy.ndimage import uniform_filter1d
    h, w = z.shape
    out = np.asarray(z, np.float32).copy()
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    al = np.abs(lat)
    coslat = np.maximum(np.cos(np.radians(lat)), 1e-6)
    # The window widens from one cell to three across the last 15 degrees. One
    # cell is the strict anti-alias criterion and is right through the
    # mid-latitudes, but it leaves the innermost rows merely SMOOTHED when they
    # need to CONVERGE: a pole is a single point, every meridian meets there, so
    # any residual variation around the last ring is drawn as a starburst no
    # matter how small it is. Ramping to three cells makes the final rows
    # average essentially the whole ring, which is what the geometry demands,
    # while 60-75 degrees is left almost untouched.
    t = np.clip((al - 75.0) / 15.0, 0.0, 1.0)
    k = strength * (1.0 + 2.0 * (t * t * (3.0 - 2.0 * t)))
    for i in range(h):
        win = int(round(k[i] / coslat[i]))
        if win > 1:
            # mode="wrap": longitude is periodic, so the average must be circular
            out[i] = uniform_filter1d(out[i], size=min(win, w), mode="wrap")
    # Final convergence. Inside the last two degrees the whole ring is one
    # ~200 km patch of ground, and every meridian of it is drawn meeting at a
    # single screen point -- so ANY variation left around that ring renders as a
    # starburst, however small and however real. Fade each of those rows into
    # its own mean, reaching full only exactly at the pole. This is a ring
    # average, but a legitimate one: it is bounded to two degrees and its weight
    # ramps smoothly to 1, unlike the earlier version that clamped a ring radius
    # and stamped a hard-edged disc across the whole cap.
    conv = np.clip((al - 88.0) / 2.0, 0.0, 1.0) ** 2
    for i in np.nonzero(conv > 0.001)[0]:
        out[i] = out[i] * (1.0 - conv[i]) + out[i].mean() * conv[i]
    return out


def _gray(a01):
    return Image.fromarray((np.clip(a01, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGB")


def _save(img, path, q):
    """Encode by EXTENSION, so the format lives in the filename and nowhere else."""
    if path.endswith(".avif"):
        img.convert("RGB").save(path, "AVIF", quality=q, speed=6)
    else:
        img.save(path, "WEBP", quality=q, method=6)
    return os.path.getsize(path)


# --- ELEVATION SHIPS AS AVIF, AND THE REASON IS MEASURED -------------------
# WebP's lossy path transforms in 4x4 blocks, and it quantises each block's DC
# level independently. On the deep sea floor -- smooth, low-contrast, and using
# only ~27 of the 256 encoded levels below 3.5 km -- neighbouring blocks land on
# DIFFERENT levels, so the decoded field carries a 4-pixel grid of one-level
# steps that was never in the data. The shader then DIFFERENTIATES elevation to
# light it, and one level at abyssal depth is a 19-degree normal tilt (section
# 2.4), so each block edge is drawn as a facet. That is the staircase.
#
# Measured on the float array before it is ever saved, as excess gradient energy
# at exactly the 4-pixel period:
#
#     clean array                   0.0-0.4x
#     WebP q94 (what we shipped)   29.5x (Precambrian)  37.8x (present day)
#     AVIF q90                      2.3x               15.8x
#     WebP lossless                 0.4x                0.0x
#
# AVIF wins on every axis that matters here: AV1's larger transforms and much
# better prediction of smooth gradients cut the artefact 2.4-13x, the files come
# out SMALLER (0.56-1.0x), the mean error is lower (18 m against 27), and it
# decodes at the same speed -- measured in the browser at 3.3 ms against WebP's
# 3.6 on a 4096x2048 frame, so the fetch-on-demand scrubbing is unaffected.
# Lossless WebP would take the artefact to zero but costs 3.7x the bytes
# (+149 MB), which would undo the loading work for a field that is already
# band-limited by smooth_bathymetry.
#
# Only the ELEVATION moves. It is the field the shader differentiates, so it is
# the one whose block edges become geometry; rainfall and ocean structure are
# read as values and stay WebP.
ELEV_EXT = ".avif"


def elev_name(tag, age):
    return f"{tag}_{abs(age):04d}_e{ELEV_EXT}"


def sibling(ef, kind):
    """The _r/_m/_o/_w/_d file that belongs with an elevation file.

    Everything used to be `ef.replace("_e.webp", ...)`, which silently returns
    the string UNCHANGED once elevation stops being a .webp -- so the app would
    have asked for the elevation file six times over and nothing would have said
    so. Split on the suffix instead, and assert.
    """
    base, _sep, _ext = ef.rpartition("_e")[0], "_e", ""
    assert base, f"not an elevation filename: {ef}"
    return f"{base}_{kind}.webp"


_SF_REC = None


def _sf_reconstructor():
    """One reconstructor for the whole run, or None if pyGPlates is absent."""
    global _SF_REC
    if _SF_REC is None:
        try:
            _SF_REC = paleo_tracks.Reconstructor() if paleo_tracks.available() else False
        except Exception:
            _SF_REC = False
    return _SF_REC or None


def _load_motion(age, tag):
    """(vx, vy) for this age from the shipped _m field, or None if not built yet.

    seafloor needs the divergence of the plate-motion field to find spreading
    ridges. The _m texture is derived from the elevation keyframes by motion.py,
    so on a re-render it already exists; on a cold first build it does not, and
    seafloor falls back to seeding only the plateaus.
    """
    mf = os.path.join(OUT, f"{tag}_{abs(age):04d}_m.webp")
    if not os.path.exists(mf):
        return None
    a = np.asarray(Image.open(mf).convert("RGB"), np.float32) / 255.0
    vx = (a[..., 0] * 2 - 1) * 160.0
    vy = (a[..., 1] * 2 - 1) * 160.0
    return vx, vy


def export(age, Z_hi, z_for_climate, tag):
    """Z_hi: elevation at ELEV res, row 0 = north. z_for_climate: the raw
    lat-ascending DEM, kept as a fallback for callers that have no carved grid."""
    cl = climate_at(age)
    # THE CLIMATE SOLVE SEES THE TERRAIN THAT IS DRAWN, not the raw DEM.
    #
    # This ran on `z_for_climate` -- the source grid, before epeiric.carve -- so
    # every seeded sea changed the coastline and the map without making the air
    # over it any wetter. Harmless when the module seeded two named seas; not
    # harmless once it also supplies the continental shelf that ringed Pangaea,
    # which is several percent of the globe. Moisture recharges over water in
    # compute_fields, so a shelf sea upwind is exactly the thing that should be
    # feeding the Triassic megamonsoon's windward margins.
    #
    # ORIENTATION IS THE HAZARD HERE and it is the one that renders the whole
    # world upside down: read_dem returns latitude ASCENDING, resample_dem
    # returns row 0 = NORTH, epeiric.carve assumes north-first, and
    # compute_fields wants ascending again. Hence the flip -- verified by
    # measuring that rainfall still peaks at the equator and not at the poles.
    _, _, Rf, _, _ = compute_fields(z_for_climate, age, CLIM_H, CLIM_W)
    rain = np.asarray(Image.fromarray(
        (np.clip(Rf / RF_MAX, 0, 1) * 255).astype(np.uint8)).resize(
        (RAIN_W, RAIN_H), Image.LANCZOS)) / 255.0
    # THE PRESENT-DAY ANCHOR (rain_anchor.py): observed rainfall calibrates the
    # model's own within 35 Myr of the present, riding the crust; a no-op past it.
    import rain_anchor as _RA
    rain = _RA.apply(rain, age, _RA.land_mask(Z_hi, RAIN_H, RAIN_W), RF_MAX)

    # Evolving sea-floor structure and the oceanic plateaus: age-graded abyss
    # from ridge distance, fracture zones, and Kerguelen / Ontong Java / the
    # Seychelles seeded so they drown and re-emerge on cue. See seafloor.py.
    # THE MOUNTAIN RELIEF (relief.py): the belts the source drew as smooth
    # envelopes, eroded -- a wedge toward the foreland, a steady-state drainage
    # network under this age's rainfall, and every band matched to real belts.
    # Land only; before 55-70 Ma and on the future's smooth belts; a no-op
    # elsewhere. Before the sea floor, which it never touches.
    import relief as _RELIEF
    Z_hi = _RELIEF.apply(Z_hi, age, tag, rain=rain * RF_MAX)
    mot = _load_motion(age, tag)
    Z_hi, ofield = SF.apply(Z_hi, age, reconstructor=_sf_reconstructor(), motion=mot)
    # Kill the polar longitude surplus BEFORE encoding, in true metres, so every
    # consumer of the elevation field is clean at the poles. See polar_lowpass.
    Z_hi = polar_lowpass(Z_hi)
    for _c in range(ofield.shape[2]):
        ofield[..., _c] = polar_lowpass(ofield[..., _c])
    e = _gray(enc_elev(smooth_bathymetry(Z_hi)))
    # Rain was the other field going out unfiltered. It drives biomes, cloud and
    # vegetation colour, so its polar surplus lands on screen too.
    r = _gray(polar_lowpass(rain))
    # ocean-structure field: R = crustal age, G/B = spreading direction. The
    # shader grows the abyssal-hill fabric from it, so it need only be smooth.
    o = Image.fromarray((np.clip(ofield, 0, 1) * 255 + 0.5).astype(np.uint8)
                        ).resize((OCEAN_W, OCEAN_H), Image.BILINEAR)
    ef = elev_name(tag, age)
    rf = f"{tag}_{abs(age):04d}_r.webp"
    of = f"{tag}_{abs(age):04d}_o.webp"
    n = (_save(e, os.path.join(OUT, ef), ELEV_Q) + _save(r, os.path.join(OUT, rf), RAIN_Q)
         + _save(o, os.path.join(OUT, of), OCEAN_Q))
    ice_T, sea_T = glaciation(cl)
    ep, per = period_for(age)
    sysd = system_at(age)
    return {"age": age, "e": ef, "r": rf, "m": sibling(ef, "m"),
            "epoch": ep, "period": per, "sealevel": sealevel_for(age),
            "temp": round(cl["temp"], 3), "veg": round(cl["veg"], 3),
            "iceT": round(ice_T, 2), "seaT": round(sea_T, 2),
            "snowball": round(R.snowball_at(cl), 3),
            "gmst": sysd["gmst"], "co2": sysd["co2"], "o2": sysd["o2"]}, n


# ---------------------------------------------------------------- future ----
# The future's plate motions, collisions and deformation live in
# future_tectonics.py (the engine) and future_story.py (the stages, after
# Scotese 2018). Until 3.15 this block held ten rigid plate groups with packed
# +250 Myr targets, a zone-orogen uplift and a suture weld; all of that is
# replaced. What remains here is what happens to the carried surface.

# S3: inherited relief wears down (Scotese: the Himalaya and Tibet under half
# their height by +125, the size of the Appalachians by +200)
EROSION_TAU_RELIEF = 220.0    # Myr, local excess above the regional mean
EROSION_TAU_REGION = 260.0    # Myr, the regional mean itself
EROSION_FLOOR = 300.0         # m, the peneplain a worn craton tends toward
EROSION_REGION_DEG = 8.0      # radius defining "regional"
# collision-reworked crust (distortion of the deformation map, see future_grid)
REWORK_D0, REWORK_D1 = 0.35, 1.0   # distortion over which the carried surface is reworked
REWORK_DEG = 1.2              # radius of the regional height a reworked surface keeps
FLEX_DEG = 0.7                # flexural scale over which thickened crust is supported
# S5: young rifted margins subside into the ocean they opened
RIFT_SUBSIDE = 700.0          # m at the margin by +250 Myr
RIFT_DEG = 2.5                # how far inboard the flexural moat reaches
# S7: coasts are worked into bays and headlands over the interval
COASTGEN = 0.46               # blend fraction at frac=1 in the heart of the band
COASTGEN_DEG = 1.2            # half-width of the coastal band
COASTGEN_REG_DEG = 2.0        # smoothing radius of the target surface
LAST_BELT = {}                # filled by future_grid; read by rebuild_future for the _t bake
STAGES = None                 # set to {} to capture future_grid's surface after each stage (debug)


def _stage(name, out, contw):
    if STAGES is not None:
        STAGES[name] = (np.array(out, np.float32), np.array(contw, bool))


def rasterise_groups(h=1440, w=2880):
    """Kept for the callers that still pass its result to future_grid, which no
    longer uses it: the future engine rasterises its own plates (3.16)."""
    return None


def future_grid(frac, gid, Zsrc, h, w):
    """The future terrain at frac*250 Myr, on an h x w grid (row 0 = north).

    3.16: carried by future_tectonics -- plate kinematics that follow today's
    motions and then Scotese's Pangea Proxima, with continents that SHORTEN
    where they collide instead of sliding under each other. `gid` is kept for
    the callers' sake and unused: the engine has its own plates. `Zsrc` is the
    present DEM (north-up, any resolution) that is carried forward.

    What stays from the old warp is what happens to the carried surface:
    inherited relief erodes (S3), the new collisional thickening is added as
    isostatic uplift under a plateau ceiling, young rifted margins subside
    (S5), and coasts are worked into bays and headlands (S7). New ocean (no
    plate claims the cell) gets the smooth ridge-and-basin backdrop.
    """
    import future_tectonics as FT
    from scipy.ndimage import gaussian_filter
    myr = float(frac) * 250.0
    lon = (np.arange(w) + 0.5) / w * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    LON, LAT = np.meshgrid(lon, lat)
    fx = np.sin(np.radians(LON) * 2.0 + 0.7) + 0.6 * np.sin(np.radians(LON) * 5.0 + 2.1)
    fy = np.sin(np.radians(LAT) * 3.1 + 1.3) + 0.5 * np.cos(np.radians(LAT) * 6.7)
    backdrop = (-4300.0 + 700.0 * fx * fy).astype(np.float32)
    if myr <= 0.0:
        return np.asarray(Zsrc, np.float32)
    carried, owner, src, Ew, contw, Dw = FT.render(myr, h, w, source=Zsrc, strain=True)
    out = np.where(np.isnan(carried), backdrop, carried).astype(np.float32)
    claimed = ~np.isnan(carried)
    arc, keep = FT.margin_fields(myr, owner, src, contw)

    _stage("carried", out, contw)
    # ---- REWORKED CRUST (3.16). Where a collision has squeezed or sheared the
    # crust to a third of its width (the map's distortion, FT._frame_fields),
    # what it carried from today is not its surface any more: Indonesia's
    # islands and marginal seas, each pushed by its own contact, came out
    # combed into a hundred fingers of land and sea between Asia and
    # Australia. Reworked crust keeps its regional height and loses the
    # carried detail -- the relief bake grows a belt's own ranges on it -- and
    # whether it is land or sea is the MAJORITY's over ~2 degrees: a sea
    # enclosed in it closes, as the Banda and Celebes seas would, and a
    # sheared-out sliver of continent in a sea sinks to the sea round it.
    rw = np.clip((Dw - REWORK_D0) / (REWORK_D1 - REWORK_D0), 0.0, 1.0)
    rw = rw * rw * (3.0 - 2.0 * rw)
    # ...and the ZONE's rework, from the continental crust round each cell: a
    # sea sliver that no strained plate claims still lies in the zone its
    # neighbours define
    sz = max(1.0, 0.75 / (180.0 / h))
    cden = gaussian_filter(contw.astype(np.float32), sz, mode=("nearest", "wrap"))
    rz = gaussian_filter((rw * contw).astype(np.float32), sz, mode=("nearest", "wrap")) / np.maximum(cden, 1e-3)
    rw = np.maximum(gaussian_filter(rw, max(1.0, 0.4 / (180.0 / h)), mode=("nearest", "wrap")),
                    rz * np.clip((cden - 0.15) / 0.2, 0.0, 1.0))
    if (rw > 0.01).any():
        rr2 = max(1.0, REWORK_DEG / (180.0 / h))
        cf = contw.astype(np.float32)
        num = gaussian_filter(np.where(contw, out, 0.0).astype(np.float32), rr2, mode=("nearest", "wrap"))
        den = gaussian_filter(cf, rr2, mode=("nearest", "wrap"))
        regC = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 0.0)
        oc = (~contw).astype(np.float32)
        num = gaussian_filter(np.where(contw, 0.0, out).astype(np.float32), rr2, mode=("nearest", "wrap"))
        den = gaussian_filter(oc, rr2, mode=("nearest", "wrap"))
        regO = np.where(den > 1e-3, num / np.maximum(den, 1e-3), -3000.0)
        out = np.where(contw, out + (regC - out) * rw, out).astype(np.float32)
        frac_c = gaussian_filter(cf, max(1.0, 2.0 / (180.0 / h)), mode=("nearest", "wrap"))
        # THE MASK IS THE MAJORITY'S TOO. Sinking a sliver's height is not
        # enough: everything downstream -- the arcs, erosion, and above all
        # the thickening uplift -- reads `contw`, and lifted the sunk slivers
        # straight back out of the sea as blades of land.
        maj = frac_c > 0.5
        tgt = np.where(maj, np.maximum(regC, 150.0), np.minimum(regO, -200.0))
        wrong = (contw != maj).astype(np.float32) * rw
        out = (out + (tgt - out) * wrong).astype(np.float32)
        contw = np.where(rw > 0.5, maj, contw)

    _stage("reworked", out, contw)
    # ---- ANTARCTICA WITHOUT ITS ICE. The present DEM gives Antarctica as its
    # BEDROCK, pressed down by 2-4 km of ice. Carried out of the polar cap the
    # sheet melts, and the bed rebounds by about a third of the ice's thickness
    # (Airy, ice 0.92 against mantle 3.3) -- modelled as the rebound of an
    # average 2.2 km sheet, ~650 m, arriving over the ~15 Myr after the crust
    # leaves 60 degrees. Until then the ice stays and so does the depression.
    ant = (owner == FT.PI["ANTARCTICA_E"]) | (owner == FT.PI["ANTARCTICA_W"])
    if ant.any():
        slat = np.degrees(np.arcsin(np.clip(src[2], -1.0, 1.0)))
        left = np.clip((65.0 - np.abs(LAT)) / 10.0, 0.0, 1.0) * float(min(1.0, myr / 60.0))
        out = np.where(ant & contw & (slat < -60.0), out + 650.0 * left, out)

    _stage("antarctic", out, contw)
    # ---- THE SUTURES ARE WELDED. Where two continents are in collision the
    # thin slivers neither plate claims -- the last of the ocean between them,
    # and the claim test's own crenulation -- drew as cracks of abyss along
    # every new suture. Inside ~130 km of crust that collision has thickened,
    # between two different plates, a sliver is crust: it takes the smoothed
    # height of the land round it. Young rifts are not touched (no thickening).
    col_zone = gaussian_filter((Ew > 0.04).astype(np.float32) * contw, 1.2 / (180.0 / h),
                               mode=("nearest", "wrap")) > 0.02
    near_n = np.zeros((h, w), np.int16)
    rr = max(1.0, 1.2 / (180.0 / h))
    for p in FT.PLATES:
        cp = contw & (owner == FT.PI[p])
        if cp.any():
            near_n += (gaussian_filter(cp.astype(np.float32), rr, mode=("nearest", "wrap")) > 0.08)
    gap = (~contw) & (near_n >= 2) & col_zone
    if gap.any():
        lf = (contw & (out > 0.0)).astype(np.float32)
        num = gaussian_filter(np.where(lf > 0, out, 0.0).astype(np.float32), rr, mode=("nearest", "wrap"))
        den = gaussian_filter(lf, rr, mode=("nearest", "wrap"))
        fillz = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 200.0)
        out = np.where(gap, np.maximum(fillz, 150.0), out).astype(np.float32)
        contw = contw | gap

    _stage("welded", out, contw)
    # ---- S3: the inherited relief wears down (Scotese: the Himalaya and Tibet
    # "less than half their original height" by +125, "comparable to the
    # Appalachians" by +200) ----
    land0 = out >= 0.0
    lf = land0.astype(np.float32)
    rs = EROSION_REGION_DEG / (180.0 / h)
    num = gaussian_filter(np.where(land0, out, 0.0).astype(np.float32), rs, mode=("nearest", "wrap"))
    den = gaussian_filter(lf, rs, mode=("nearest", "wrap"))
    region = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 0.0)
    relief = out - region
    kR = float(np.exp(-myr / EROSION_TAU_RELIEF))
    kG = float(np.exp(-myr / EROSION_TAU_REGION))
    # an active margin (the Andes, the Cordillera, Japan) is renewed as fast as
    # it wears: `keep` holds it near its present height
    kRe = kR + (1.0 - kR) * keep
    kGe = kG + (1.0 - kG) * keep
    worn = (EROSION_FLOOR + (region - EROSION_FLOOR) * kGe) + relief * kRe
    out = np.where(land0, worn, out)
    # ...and a newly active one (the Americas' Atlantic coasts from +25) grows
    # an Andean-type range
    out = np.where(contw, out + arc, out)

    _stage("eroded+arcs", out, contw)
    # ---- the collisions: excess crust thickness as isostatic uplift, where the
    # crust is continental, under a plateau ceiling (gravitational collapse
    # keeps the highest plateau near 5.5 km) ----
    # ...supported REGIONALLY: the lithosphere's flexural rigidity spreads the
    # load of thickened crust over ~100 km, and E, advected with the material,
    # carries the collision's shear streaks cell by cell -- lifted as they
    # were, they drew the reworked belt back as blades of land and sea.
    sf = max(1.0, FLEX_DEG / (180.0 / h))
    cwf = contw.astype(np.float32)
    Ew = np.where(contw, gaussian_filter(Ew * cwf, sf, mode=("nearest", "wrap"))
                  / np.maximum(gaussian_filter(cwf, sf, mode=("nearest", "wrap")), 1e-3), Ew)
    up = FT.H_ISO * Ew * contw
    zc = out + up
    ceil0, span = 4200.0, 1600.0
    zc = np.where(zc > ceil0, ceil0 + span * np.tanh((zc - ceil0) / span), zc)
    out = np.where(contw & (Ew > 0.0), np.maximum(zc, out), out).astype(np.float32)
    LAST_BELT["belt"] = np.clip(Ew / 0.9, 0.0, 1.0) * (out >= 0.0) * contw
    LAST_BELT["shape"] = (h, w)
    LAST_BELT["owner"] = owner

    _stage("uplifted", out, contw)
    # ---- S5: young rifted margins subside ----
    land = out >= 0.0
    newocean = (~claimed).astype(np.float32)
    near = gaussian_filter(newocean, max(1.0, RIFT_DEG / (180.0 / h)), mode=("nearest", "wrap"))
    near = np.clip(near / max(float(near.max()), 1e-6), 0.0, 1.0)
    out = out - RIFT_SUBSIDE * frac * near * land

    _stage("rifts", out, contw)
    # ---- S7: coastal evolution ----
    landf = (out >= 0.0).astype(np.float32)
    cgs = gaussian_filter(landf, max(1.0, COASTGEN_DEG / (180.0 / h)), mode=("nearest", "wrap"))
    coastw = np.clip((1.0 - np.abs(cgs * 2.0 - 1.0)) * 1.4 - 0.08, 0.0, 1.0)
    regC = gaussian_filter(out.astype(np.float32), COASTGEN_REG_DEG / (180.0 / h), mode=("nearest", "wrap"))
    out = out + (regC - out) * (COASTGEN * frac * coastw)
    _stage("final", out, contw)
    return out.astype(np.float32)


def handoff_blend(A, B, wq, wl=None):
    """Cross-fade the real 540 Ma DEM into the authored Precambrian composite.

    Blending elevations in METRES destroys land. Ocean floor is about -4000 m
    and a continental interior only a few hundred, so mixing in even 8 percent
    of "ocean" drowns most land: measured, the world went from 18.6 percent land
    at 540 Ma to 7.5 percent one keyframe later and bottomed out at 4.3 percent
    mid-handoff, before a whole southern continent reappeared out of it. That is
    the "continents flood then a new continent arises" the map showed between
    595 and 545 Ma, and it is an artefact of the cross-fade, not geology.

    Two corrections. Blend in the SIGNED-SQRT domain the shader already
    interpolates keyframes in, which compresses the abyss so a coastline
    survives a partial mix. Then re-level the result so its land fraction is the
    interpolation of the two endpoints' land fractions, instead of collapsing to
    wherever the two happen to agree. The handoff is still a morph between two
    reconstructions -- it cannot be anything else -- but land area now moves
    smoothly from one world to the other.
    """
    """WHERE the continents are and HOW MUCH land there is now ride separate
    ramps, and they have to, because they were fighting.

    `wq` mixes the two GEOMETRIES and is deliberately short (20 Myr). The 540 Ma
    DEM is a snapshot of one instant; held at two-thirds weight 20 Myr away it
    was putting -3640 m of ocean under Siberia's label, which by then had moved
    with its plate -- so a continent appeared to swim across the sea and its name
    swam with it. Measured under the label: the generated world says +489 m at
    every age in the window and the static map says -3640, and the blend is what
    drowned it.

    `wl` sets the LAND-FRACTION target and is long (110 Myr), because that is the
    quantity a short ramp wrecks: at 20 Myr land jumped 18.5% -> 28.6% and back
    to 24.1%, which is the same "continents flood then a continent arises"
    artefact this function was written to kill, running in reverse. On the long
    ramp it rises smoothly and never turns round.

    Defaults to wl = wq, so any caller that does not care gets the old
    behaviour.
    """
    if wl is None:
        wl = wq
    if wq <= 0 and wl <= 0:
        return A

    def enc(z):
        return 0.5 + 0.5 * np.sign(z) * np.sqrt(np.clip(np.abs(z) / 8000.0, 0, 1))

    def dec(e):
        s = 2 * e - 1
        return np.sign(s) * s * s * 8000.0

    h, w = A.shape
    wlat = np.cos(np.radians(90 - (np.arange(h) + 0.5) / h * 180))[:, None]
    denom = wlat.sum() * w

    def landfrac(z):
        return float(((z > 0) * wlat).sum() / denom)

    # At wq >= 1 the geometry is purely B, but the shim below STILL runs: that
    # is the whole point of splitting the ramps, and returning B early here is
    # what used to make the land-fraction curve step.
    out = B if wq >= 1 else dec(enc(A) * (1 - wq) + enc(B) * wq)
    target = landfrac(A) * (1 - wl) + landfrac(B) * wl
    lo, hi = -3000.0, 3000.0
    for _ in range(40):                      # bisect the sea-level shim
        mid = (lo + hi) / 2
        if landfrac(out + mid) < target:
            lo = mid
        else:
            hi = mid
    return out + (lo + hi) / 2


# ------------------------------------------------------------------ main ----
def main():
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    manifest, total = [], 0
    coarse = {}          # age -> motion-grid elevation, for the matching pass

    def dem_for(age):
        near = float(avail[np.argmin(np.abs(avail - age))])
        return read_dem(idx[near])

    # ---- Phanerozoic ----
    _rec = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    for age in range(0, 541, STEP):
        z = dem_for(age)
        Zhi = resample_dem(z, ELEV_H, ELEV_W)
        # flood the epicontinental seas this grid cannot resolve (see epeiric.py)
        Zhi = EP.carve(Zhi, age, _rec)
        coarse[age] = MO.coarsen(Zhi)
        # Zhi[::-1], not z: the climate solve must see the terrain that is DRAWN.
        # resample_dem returns row 0 = north and compute_fields wants latitude
        # ascending, hence the flip. Only the Phanerozoic path does this -- the
        # future and Precambrian branches build their own climate-resolution
        # grids (gl, lo) with their own eustatic corrections already applied, and
        # substituting the high-res one there would quietly change what those
        # eras solve for.
        m, n = export(age, Zhi, Zhi[::-1], "phan")
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
        # The future series warps TODAY's terrain, which is referenced to
        # today's sea level, so the era's eustatic level has to be applied by
        # hand. Without this the coastline never moves and low ground such as
        # Florida, Bangladesh and the Netherlands stays dry through a hothouse
        # that has melted every ice sheet. (The Phanerozoic DEMs are already
        # relative to their own contemporaneous sea level; adjusting those too
        # would double-count.)
        sl = sealevel_for(age)
        gh = gh - sl
        gl = gl - sl
        coarse[age] = MO.coarsen(gh)
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
        wq = float(np.clip((age - 540.0) / 20.0, 0, 1))    # geometry: short
        wl = float(np.clip((age - 540.0) / 110.0, 0, 1))   # land fraction: long
        hi = handoff_blend(A_hi, hi, wq, wl)
        lo = handoff_blend(A_lo, lo, wq)
        coarse[age] = MO.coarsen(hi)
        m, n = export(age, hi, lo[::-1], "pre")
        manifest.append(m); total += n; npre += 1
    print(f"Precambrian: {npre} keyframes (anchored to 540 Ma)")

    # ---- motion: match each keyframe's neighbours across a wide baseline ----
    ages = sorted(coarse)
    for rec in manifest:
        a = rec["age"]
        older = min(ages, key=lambda x: abs(x - (a + MO.BASE_MYR)))
        younger = min(ages, key=lambda x: abs(x - (a - MO.BASE_MYR)))
        dt = max(5.0, older - younger)
        vx, vy, cf = MO.displacement(coarse[older], coarse[younger], dt)
        p = os.path.join(OUT, rec["m"])
        MO.encode(vx, vy, cf).save(p, "WEBP", quality=94, method=6)
        total += os.path.getsize(p)
    print(f"motion: {len(manifest)} fields derived")

    manifest.sort(key=lambda m: m["age"])
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"),
              separators=(",", ":"))
    print(f"TOTAL {len(manifest)} keyframes, {total/1e6:.2f} MB of field textures")


if __name__ == "__main__":
    main()
