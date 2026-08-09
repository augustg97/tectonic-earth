"""Batch-render paleogeographic frames from Scotese/Wright paleoDEMs.

Picks the nearest available DEM for each target age, renders with render.py,
writes WebP frames + frames_manifest.json (age, era, period, sealevel, file).
"""
import os, re, glob, json, sys, warnings
import numpy as np
import netCDF4
from PIL import Image
from render import render_u8

DEM_DIR = "../data/paleodems_6min"
OUT_DIR = "../web/frames"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_W, OUT_H = 1024, 512
WEBP_Q = 70

# ---- geologic period lookup (age Ma -> period/epoch label) ----------------
PERIODS = [
    (0, 0.012, "Holocene", "Quaternary"),
    (0.012, 2.58, "Pleistocene", "Quaternary"),
    (2.58, 5.33, "Pliocene", "Neogene"),
    (5.33, 23.0, "Miocene", "Neogene"),
    (23.0, 33.9, "Oligocene", "Paleogene"),
    (33.9, 56.0, "Eocene", "Paleogene"),
    (56.0, 66.0, "Paleocene", "Paleogene"),
    (66.0, 100.5, "Late Cretaceous", "Cretaceous"),
    (100.5, 145.0, "Early Cretaceous", "Cretaceous"),
    (145.0, 163.5, "Late Jurassic", "Jurassic"),
    (163.5, 174.1, "Middle Jurassic", "Jurassic"),
    (174.1, 201.4, "Early Jurassic", "Jurassic"),
    (201.4, 237.0, "Late Triassic", "Triassic"),
    (237.0, 247.2, "Middle Triassic", "Triassic"),
    (247.2, 251.9, "Early Triassic", "Triassic"),
    (251.9, 259.5, "Lopingian", "Permian"),
    (259.5, 273.0, "Guadalupian", "Permian"),
    (273.0, 298.9, "Cisuralian", "Permian"),
    (298.9, 323.2, "Pennsylvanian", "Carboniferous"),
    (323.2, 358.9, "Mississippian", "Carboniferous"),
    (358.9, 382.7, "Late Devonian", "Devonian"),
    (382.7, 393.3, "Middle Devonian", "Devonian"),
    (393.3, 419.2, "Early Devonian", "Devonian"),
    (419.2, 443.8, "Silurian", "Silurian"),
    (443.8, 485.4, "Ordovician", "Ordovician"),
    (485.4, 538.8, "Cambrian", "Cambrian"),
    (538.8, 635.0, "Ediacaran", "Neoproterozoic"),
    (635.0, 720.0, "Cryogenian", "Neoproterozoic"),
    (720.0, 1000.0, "Tonian", "Neoproterozoic"),
]

def period_for(age):
    a = abs(age)
    for lo, hi, ep, per in PERIODS:
        if lo <= a < hi:
            return ep, per
    return "—", "—"

# ---- eustatic sea level (m vs present), for the readout --------------------
# This follows the HAQ family of curves (Haq & Schutter 2008; van der Meer's
# tectono-glacio-eustatic curve agrees closely). The competing Miller
# backstripping family puts the Cretaceous peak at roughly half this. The two
# barely overlap, so the rule is to pick one and stay in it -- mixing them
# produces a curve that matches neither.
SEALEVEL = [
    (0, 0), (20, 40), (40, 80), (66, 110), (80, 250), (90, 240), (100, 200),
    (120, 150), (145, 110), (160, 90), (200, 60), (230, 40), (250, 20),
    (270, -20), (300, -40), (340, 60), (360, 90), (400, 140), (420, 160),
    (445, 200), (460, 220), (480, 180), (500, 120), (540, 60),
    # Precambrian: there is NO published quantitative eustatic curve before
    # 541 Ma -- Haq & Schutter and Miller both start at the Cambrian base, and
    # the one model-derived attempt (van der Meer 2017) reaches only ~825 Ma
    # through a long inference chain its own authors flag as least reliable
    # exactly there. These are plausible values, not readings, and the app
    # marks them as modelled.
    # Snowball sea level is the one Neoproterozoic value with a real
    # constraint on it: with ~1 km of sea-level-equivalent water locked into
    # ice sheets, levels "must have been very low (lower than -200 m)"
    # (van der Meer et al. 2022). The interglacials rebound sharply.
    (600, 30), (628, 20), (637, -210), (648, -260), (658, 15),
    (665, -250), (690, -280), (712, -230), (721, 25),
    (750, 30), (850, 40), (1000, 30),
    # Future: the present icehouse ends. Melting Antarctica and Greenland alone
    # is ~65 m of sea level (NASA/NSIDC), and the projection warms into a
    # hothouse, so seas rise steeply and then ebb as the assembling
    # supercontinent and ageing, deepening ocean basins take water back down --
    # the same reason Pangaea sat at a low stand.
    (-10, 12), (-30, 40), (-70, 65), (-120, 70), (-170, 50), (-250, 15),
]
def sealevel_for(age):
    pts = [p for p in SEALEVEL if (p[0] <= 0) == (age <= 0)] or SEALEVEL
    pts = sorted(pts, key=lambda p: p[0])
    ages = [p[0] for p in pts]
    if age <= ages[0]: return pts[0][1]
    if age >= ages[-1]: return pts[-1][1]
    for i in range(len(pts) - 1):
        a0, a1 = ages[i], ages[i+1]
        if a0 <= age <= a1:
            t = (age - a0) / (a1 - a0 + 1e-9)
            return round(pts[i][1] * (1 - t) + pts[i+1][1] * t)
    return 0

# ---- index available DEMs by age ------------------------------------------
def index_dems():
    idx = {}
    for f in glob.glob(os.path.join(DEM_DIR, "**", "*.nc"), recursive=True):
        m = re.search(r"_([0-9]+(?:\.[0-9]+)?)Ma", os.path.basename(f))
        if m:
            idx[float(m.group(1))] = f
    return idx

def read_dem(f):
    """Return the grid with latitude ASCENDING (row 0 = south pole).

    The Zenodo sets disagree: the 1-degree files store latitude ascending,
    the 6-minute files store it descending (north first). render() assumes
    ascending and flips once, so normalise here or the map comes out
    upside down.
    """
    ds = netCDF4.Dataset(f)
    v = "z" if "z" in ds.variables else list(ds.variables.keys())[-1]
    z = np.asarray(ds.variables[v][:], dtype=np.float32)
    latname = "lat" if "lat" in ds.variables else "latitude"
    lat = np.asarray(ds.variables[latname][:])
    if lat[0] > lat[-1]:          # descending (north first) -> flip to ascending
        z = z[::-1]
    return make_periodic(repair_spikes(z))


# Metres a cell may stand off the median of its own 9-cell neighbourhood.
#
# CALIBRATED, and the first two attempts were both wrong in ways worth keeping:
#
#   * an absolute ceiling of +9,000 m caught the fill but also flattened the
#     real 30 Ma Himalaya, which reaches 9,300-9,600 m continuous with a 9,000 m
#     rim. The source's tectonics are not this function's business.
#   * a jump threshold of 5,000 m caught real island-arc margins -- Sulawesi at
#     10 Ma drops 5,760 m in one 10 km cell, and so do trench walls. Flattening
#     every steep margin on the map to fix one island is a far worse trade.
#
# Measured over 22 sampled ages, excursion from a 9-cell median, after excluding
# cells that ARE fill and cells ADJACENT to fill (a valid -9000 sitting inside a
# run of +10200 reads as a 19,200 m excursion and contaminated the first
# calibration):
#
#     real terrain   median 3,540 m   p90 6,148   max 6,240   (a 425 Ma range)
#     fill cells     min 12,100 m     median 16,350   max 17,500
#
# 8,000 sits between them with about 30% margin on each side. Note the fill is
# not one family: besides +10200/+10500 in the trenches there are isolated
# +8,400 m spikes in 5 km water, which no absolute ceiling below 8,400 would
# reach and this test catches at 12,400.
SPIKE_JUMP = 8000.0


def repair_spikes(z, jump=SPIKE_JUMP):
    """Remove fill values that the PaleoDEMs leave in the deepest trenches.

    FOUND ON SCREEN: a tan desert island in the middle of the Mariana Trench.
    The 6-minute PaleoDEM stores the Challenger Deep axis as +10500 m -- the
    magnitude of the depth with the sign lost -- flanked on both sides by -9000.
    Our pipeline carried it through, and the shipped field renders +3349 m of dry
    land at the deepest point on Earth. 2,219 such cells across 21 of the 109
    source ages, in the Mariana and Tonga trenches, the south Pacific at 100 Ma
    and elsewhere.

    THE TEST IS THE JUMP, NOT A CEILING, and the distinction matters because
    there are two different things above 9,000 m in this data:

      * the fill: +10500 sitting on a rim of -8000. An 18.5 km step across one
        6-minute cell, which is 10 km wide. Nothing on Earth does that.
      * real reconstruction output: the 30 Ma Himalaya reaches 9,300-9,600 m on
        a rim of 9,000. Higher than Everest, but continuous with its own
        surroundings, and it is not this function's business to overrule the
        source's tectonics.

    A ceiling of 9,000 m would have flattened the second along with the first.
    The jump test separates them: 18,500 m against 300.

    Repaired by the median of the VALID cells around them, grown outward until
    every hole is filled. That is a claim about nothing except locality -- it
    turns the Mariana fill into deep ocean at roughly its rim depth. The
    magnitudes do look like a lost sign (10500 against a real 10,935), and
    negating them would recover the true axis, but that is a guess about an
    upstream bug and the neighbourhood median cannot be wrong by more than the
    local relief.
    """
    from scipy.ndimage import median_filter
    out = np.asarray(z, dtype=np.float32).copy()
    # ITERATED, because a 9-cell window cannot see out of a big fill patch.
    # The 100 Ma south-Pacific patch is 307 cells -- about 20 across -- so for
    # every cell in its middle the neighbourhood median IS the fill value, the
    # excursion is zero, and a single pass repairs only the rim and leaves an
    # 18,200 m core behind. Each pass eats one rim; five or so passes reach the
    # centre. Ages with nothing wrong exit on the first test.
    for _ in range(8):
        bg = median_filter(out, size=9, mode="nearest")
        bad = (np.abs(out - bg) > jump) | _needles(out)
        if not bad.any():
            return out
        out = _fill_holes(out, bad)
    return out


NEEDLE_DROP = 3000.0     # metres a cell must fall on BOTH sides to be a needle


def _needles(z, drop=NEEDLE_DROP):
    """Cells that are a local maximum with a big drop on EVERY side.

    THE SECOND FILL FAMILY, and magnitude alone cannot reach it. Six rebaked
    Phanerozoic frames still carried spikes after the excursion test: a 6,452 m
    cell between neighbours of 692 and 889 in the west Pacific at 50 Ma, an
    8,000 m one (the Z_RANGE clamp, which is itself a tell) between 3,942 and
    3,514 at 20 Ma. Their excursion from a 9-cell median is 5,900-7,000 m, which
    sits UNDER the 8,000 m threshold -- and that threshold cannot be lowered,
    because real island-arc margins reach 5,760 m and flattening every steep
    coast to catch these would cost far more than it fixes.

    Shape separates them where size cannot. A fill is a NEEDLE: high in the
    middle, falling away on all four sides. A margin is MONOTONE: land on one
    side, water on the other, and never a local maximum. So require the cell to
    exceed all four neighbours by `drop`, which Sulawesi's coast does not do at
    any threshold, and no ridge crest does either at 10 km per cell -- a real
    crest has a neighbour within a few hundred metres of it along strike.
    """
    n = np.roll(z, 1, 0); s = np.roll(z, -1, 0)
    e = np.roll(z, 1, 1); w = np.roll(z, -1, 1)
    return ((z - n > drop) & (z - s > drop)
            & (z - e > drop) & (z - w > drop))


def _fill_holes(out, bad):
    """Replace `bad` cells with the median of their valid neighbours.

    PER PATCH, INSIDE ITS OWN BOUNDING BOX, and that is not a micro-optimisation
    -- the whole-array version stalled a full re-bake. Filling grows one ring
    per iteration, so a 20-cell patch needs ~10 iterations, and each one
    nan-medianed a 9 x 6.5M stack: about 100 s per repair pass, times 8 passes,
    times 21 affected ages. Four and a half hours of the bake would have gone to
    repairing 2,219 cells. The patches are tiny and local; the arithmetic should
    be too.
    """
    from scipy.ndimage import find_objects, label
    out = out.copy()
    lab, n = label(bad)
    if not n:
        return out
    for sl in find_objects(lab):
        # Pad by the fill radius so every hole has valid neighbours to draw on,
        # clipped to the array. Longitude wrap is not handled: a patch straddling
        # the antimeridian just fills from the side it can see, which is a
        # neighbour median either way.
        r0 = max(0, sl[0].start - 12); r1 = min(out.shape[0], sl[0].stop + 12)
        c0 = max(0, sl[1].start - 12); c1 = min(out.shape[1], sl[1].stop + 12)
        sub = out[r0:r1, c0:c1].astype(np.float64)
        hole0 = bad[r0:r1, c0:c1]
        sub[hole0] = np.nan
        for _ in range(40):
            holes = np.isnan(sub)
            if not holes.any():
                break
            stack = np.stack([np.roll(np.roll(sub, dr, 0), dc, 1)
                              for dr in (-1, 0, 1) for dc in (-1, 0, 1)])
            # An interior cell of a large patch has no valid neighbour yet, so
            # its slice is all-NaN on this pass and fills on a later one. That
            # is the algorithm working, but nanmedian warns every time and the
            # noise buries real warnings from the rest of the build.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                m = np.nanmedian(stack, axis=0)
            if not np.isfinite(m[holes]).any():
                break
            sub = np.where(holes & np.isfinite(m), m, sub)
        out[r0:r1, c0:c1] = np.where(np.isnan(sub), out[r0:r1, c0:c1], sub)
    if np.isnan(out).any():
        good = out[np.isfinite(out)]
        out[np.isnan(out)] = float(np.median(good)) if good.size else 0.0
    return out


def make_periodic(z, taper_deg=4.0):
    """Make the longitude axis genuinely periodic.

    The PaleoDEMs are stored on lon -180..+180 INCLUSIVE -- 3601 columns for
    3600 cells (361 for the 1-degree set) -- so the first and last columns are
    the SAME meridian stored twice. They disagree: by ~550 m at 150 Ma, and at
    100 Ma the final column is plain corrupt, 4352 m from its own twin while its
    neighbour sits 565 m away. Rendered on a sphere that is a false cliff from
    the Bering Strait past New Zealand to Antarctica -- a stationary north-south
    line down the Pacific that terrain visibly distorts across.

    The duplicated column is identified STRUCTURALLY, by the grid having an odd
    width, not by comparing values. A value test looks reasonable and fails
    exactly where the data is worst: at 100 Ma it decided the corrupt column was
    NOT a duplicate, kept it, and welded the corruption into the seam.

    So: drop the duplicate, then split whatever mismatch remains between the two
    sides and taper it to nothing over a few degrees. The correction works out at
    a few metres per column, far below the DEM's own uncertainty, and it only
    touches the band either side of 180.
    """
    if z.shape[1] < 8:
        return z
    if z.shape[1] % 2 == 1:            # inclusive grid: last column repeats the first
        z = z[:, :-1].copy()
    else:
        z = z.copy()
    delta = (z[:, 0] - z[:, -1]) * 0.5
    W = z.shape[1]
    band = max(2, int(round(taper_deg / 360.0 * W)))
    ramp = np.linspace(1.0, 0.0, band, endpoint=False)
    z[:, :band] -= delta[:, None] * ramp[None, :]
    z[:, W - band:] += delta[:, None] * ramp[::-1][None, :]
    return z


def main():
    idx = index_dems()
    avail = np.array(sorted(idx.keys()))
    # Every 5 Myr, matching the native spacing of the PALEOMAP series. Plate
    # motion is only a few degrees per step at this cadence, so consecutive
    # frames cross-fade as motion rather than as a visible cut.
    targets = list(range(0, 541, 5))
    manifest = []
    for age in targets:
        # nearest available DEM
        near = float(avail[np.argmin(np.abs(avail - age))])
        f = idx[near]
        z = read_dem(f)
        img, _ = render_u8(z, age, out_h=OUT_H, out_w=OUT_W)
        fn = f"phan_{age:04d}.webp"
        Image.fromarray(img).save(os.path.join(OUT_DIR, fn), "WEBP", quality=WEBP_Q, method=5)
        ep, per = period_for(age)
        manifest.append({"age": age, "file": fn, "epoch": ep, "period": per,
                         "sealevel": sealevel_for(age), "src_age": near})
        sz = os.path.getsize(os.path.join(OUT_DIR, fn)) // 1024
        print(f"  {age:4d} Ma  <- {near:6.1f}Ma  {ep:16s} {sz}KB")
    json.dump(manifest, open(os.path.join(OUT_DIR, "manifest_phan.json"), "w"), indent=0)
    total = sum(os.path.getsize(os.path.join(OUT_DIR, m["file"])) for m in manifest)
    print(f"Phanerozoic: {len(manifest)} frames, {total/1e6:.2f} MB")

if __name__ == "__main__":
    main()
