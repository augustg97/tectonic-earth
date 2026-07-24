"""Give the ocean floor real, evolving structure -- and put the plateaus back.

The ocean floor was a flat synthetic depth at every age but the present, so the
abyss read as a dead sheet however much procedural texture the shader laid over
it. That texture was static: it did not rift, spread or subduct with the rest
of the world. This bakes STRUCTURE into the elevation field itself, per
keyframe, so it travels and changes like the continents do.

Two things are added, both into the shipped `_e` elevation texture so they run
through the ordinary terrain shader and evolve because they are regenerated
every keyframe:

  1. AGE-GRADED ABYSS. Sea floor deepens as it ages away from a spreading
     ridge -- the half-space cooling law, depth ~ 2600 + 350*sqrt(age_Myr).
     There is no crustal-age grid for deep time, so age is inferred from the
     motion field's DIVERGENCE: a ridge is where crust pulls apart, so distance
     from the nearest divergent line is a proxy for age. Ridges come out
     shallow and banded, the abyssal plains deep and smooth, with ridge-parallel
     abyssal-hill fabric and transform-fault fracture zones cutting across.

  2. OCEANIC PLATEAUS AND MICROCONTINENTS. Kerguelen, Ontong Java, the
     Seychelles, Mauritia, Argoland and the rest are real crustal highs the
     20 km DEM does not resolve. Each is seeded from present-day anchors,
     back-advected on the plate rotations, with an elevation curve that carries
     it from emergent land, through a shallow drowned bank, to a deep old
     plateau -- so Kerguelen is an ISLAND in the Cretaceous and a pale plateau
     on the sea floor now, and you can watch it drown.

Everything is applied ONLY to ocean (z < 0) except where a plateau is authored
to stand above water, and a plateau can only ever RAISE the floor, never carve
a hole in a continent.

Wired into build_fields.py's export and rerender_ages.py, after epeiric.carve.
"""
import math

import numpy as np

# --- age-depth (half-space cooling, Parsons & Sclater style) ---------------
RIDGE_DEPTH = 2600.0        # m: crest of a mid-ocean ridge
DEPTH_PER_SQRT_MYR = 350.0  # m per sqrt(Myr): how fast it deepens with age
MAX_ABYSS = 6000.0


def _blob(LON, LAT, plon, plat, radius_km):
    r = math.degrees(radius_km / 6371.0)
    dlon = ((LON - plon + 180.0) % 360.0) - 180.0
    d = np.sqrt((dlon * np.cos(np.radians(LAT))) ** 2 + (LAT - plat) ** 2)
    return np.clip(1.0 - (d / r) ** 2, 0.0, 1.0)


def _curve(age, points):
    pts = sorted(points, key=lambda p: p[0])
    if age <= pts[0][0]:
        return pts[0][1]
    if age >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        a0, v0 = pts[i]
        a1, v1 = pts[i + 1]
        if a0 <= age <= a1:
            t = 0.0 if a1 == a0 else (age - a0) / (a1 - a0)
            return v0 + (v1 - v0) * t
    return pts[-1][1]


# ---------------------------------------------------------------------------
# Oceanic plateaus and microcontinents. Present-day anchor(s) + radius(km), and
# an elevation curve (age_Ma, metres): positive is land, negative is submarine.
# Ages and settings from the oceanic-plateau / continental-fragment literature.
PLATEAUS = {
    # --- microcontinents that were once emergent -------------------------
    "Kerguelen": {
        "anchors": [(69.0, -49.0, 620), (75.0, -53.0, 520), (64.0, -46.0, 400)],
        "elev": [(120, -1400), (110, 300), (95, 250), (85, -200), (60, -900),
                 (30, -1300), (0, -1400)]},
    "Seychelles": {
        "anchors": [(55.5, -5.0, 220)],
        "elev": [(90, 200), (66, 400), (60, 300), (40, 60), (0, 20)]},
    "Mauritia": {
        "anchors": [(59.0, -22.0, 300), (63.0, -27.0, 240)],
        "elev": [(85, 120), (75, 60), (65, -300), (40, -1200), (0, -1800)]},
    "JanMayen": {
        "anchors": [(-8.0, 70.5, 220), (-10.0, 68.0, 180)],
        "elev": [(55, 100), (40, -300), (30, -700), (25, -1100), (0, -1300)]},
    "Zealandia": {
        "anchors": [(170.0, -42.0, 700), (166.0, -33.0, 520),
                    (174.0, -47.0, 480), (159.0, -30.0, 420)],
        "elev": [(85, 200), (75, 120), (55, -400), (35, -900), (23, -1000),
                 (0, -1100)]},
    "Argoland": {
        "anchors": [(112.0, -15.0, 340), (117.0, -18.0, 280)],
        "elev": [(165, 100), (155, 50), (130, -800), (100, -2500), (0, -4000)]},
    # --- large igneous province plateaus (submarine highs) ---------------
    "OntongJava": {
        "anchors": [(160.0, -3.0, 700), (165.0, 2.0, 520), (158.0, -8.0, 420)],
        "elev": [(126, 200), (120, -700), (100, -1300), (60, -1700), (0, -2000)]},
    "Manihiki": {
        "anchors": [(-161.0, -11.0, 380)],
        "elev": [(125, -500), (118, -1200), (60, -2000), (0, -2600)]},
    "Shatsky": {
        "anchors": [(159.0, 33.0, 420)],
        "elev": [(147, -1000), (140, -2200), (60, -3000), (0, -3400)]},
    "HessRise": {
        "anchors": [(178.0, 34.0, 360)],
        "elev": [(110, -1200), (99, -2400), (0, -3400)]},
    "Agulhas": {
        "anchors": [(26.0, -40.0, 320)],
        "elev": [(100, -1500), (90, -2200), (0, -2800)]},
    "BrokenRidge": {
        "anchors": [(96.0, -31.0, 300)],
        "elev": [(100, 100), (90, -400), (43, -1000), (0, -1600)]},
    "RioGrandeRise": {
        "anchors": [(-33.0, -31.0, 300)],
        "elev": [(85, 100), (80, -400), (45, -900), (0, -1400)]},
    "WalvisRidge": {
        "anchors": [(3.0, -25.0, 260), (8.0, -20.0, 220)],
        "elev": [(120, -500), (80, -1500), (0, -2400)]},
    "Naturaliste": {
        "anchors": [(110.0, -34.0, 240)],
        "elev": [(130, -600), (95, -1800), (0, -2500)]},
    "MascarenePlateau": {
        "anchors": [(60.0, -12.0, 380)],
        "elev": [(45, -100), (34, -800), (10, -1500), (0, -1800)]},
    # --- volcanic island chains, as shallow submarine ridges -------------
    "HawaiianRidge": {
        "anchors": [(-155.0, 20.0, 160), (-170.0, 26.0, 220),
                    (172.0, 31.0, 260)],
        "elev": [(80, -2500), (43, -1800), (20, -1200), (0, -800)]},
    "EastTasman": {
        "anchors": [(156.0, -44.0, 220)],
        "elev": [(80, -400), (55, -900), (0, -1500)]},
    "LineIslands": {
        "anchors": [(-160.0, 0.0, 400), (-162.0, 8.0, 300)],
        "elev": [(90, -700), (70, -1500), (0, -2200)]},
}


def emergent_names(age):
    """Plateaus standing above sea level at this age, for optional labelling."""
    return [n for n, sp in PLATEAUS.items() if _curve(age, sp["elev"]) > 0]


def _plateau_field(shape, age, reconstructor):
    """Target elevation and mask for every seeded plateau at this age."""
    h, w = shape
    lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
    LON, LAT = np.meshgrid(lon, lat)
    target = np.full(shape, -1e9, np.float32)
    mask = np.zeros(shape, np.float32)
    for name, spec in PLATEAUS.items():
        elev = _curve(age, spec["elev"])
        m = np.zeros(shape, np.float32)
        for alon, alat, radius in spec["anchors"]:
            plon, plat = alon, alat
            if reconstructor is not None and age > 0:
                try:
                    tr, _ = reconstructor.track(float(alon), float(alat),
                                                min(540, max(age, 5)))
                    if tr:
                        best = min(tr, key=lambda r: abs(r[0] - age))
                        plon, plat = best[1], best[2]
                except Exception:
                    pass
            m = np.maximum(m, _blob(LON, LAT, plon, plat, radius))
        # feather the rim so the plateau grades into the abyss
        here = m > 0.02
        target[here] = np.maximum(target[here], elev)
        mask = np.maximum(mask, m)
    return target, mask


def apply(z, age, reconstructor=None, motion=None, verbose=False):
    """Add evolving sea-floor structure and plateaus to an elevation grid.

    z is (H, W), row 0 = north. Returns a new grid. `motion` is an optional
    (vx, vy) tuple on the same grid, used to find spreading ridges; if absent,
    the age-depth grading is skipped and only the plateaus are seeded.
    """
    out = z.astype(np.float32).copy()
    h, w = out.shape
    sea = out < 0

    # 1) age-graded abyssal relief from ridge distance --------------------
    if motion is not None:
        vx, vy = motion
        # the motion field ships at a coarser resolution than the elevation
        # grid; bring it up so the masks below line up cell for cell
        if vx.shape != out.shape:
            from PIL import Image as _I
            def _up(a):
                return np.asarray(_I.fromarray(a.astype(np.float32)).resize(
                    (w, h), _I.BILINEAR), np.float32)
            vx, vy = _up(vx), _up(vy)
        # divergence of the velocity field -> spreading centres are maxima
        dvx = np.gradient(vx, axis=1)
        dvy = np.gradient(vy, axis=0)
        div = dvx + dvy
        ridge = div > np.percentile(div[sea], 88) if sea.any() else div > 1e9
        # geodesic-ish distance to the nearest ridge cell, in degrees
        try:
            from scipy import ndimage
            # distance transform on the non-ridge cells
            dist = ndimage.distance_transform_edt(~ridge).astype(np.float32)
            dist *= 180.0 / h                       # cells -> degrees
        except Exception:
            dist = np.full(out.shape, 20.0, np.float32)
        # degrees -> crude crustal age: spreading ~40 mm/yr => ~0.36 deg/Myr,
        # so age_Myr ~ dist_deg / 0.36, capped where the abyss saturates
        age_myr = np.clip(dist / 0.36, 0.0, 180.0)
        model_depth = -(RIDGE_DEPTH + DEPTH_PER_SQRT_MYR * np.sqrt(age_myr))
        model_depth = np.clip(model_depth, -MAX_ABYSS, -RIDGE_DEPTH)
        # Poleward of ~72 degrees the equirectangular grid is so compressed that
        # the ridge-distance transform is meaningless and threw bright speckle
        # all round the poles. Fade the whole model out there and keep whatever
        # the DEM already had.
        lat1d = 90.0 - (np.arange(h) + 0.5) / h * 180.0
        polefade = np.clip((72.0 - np.abs(lat1d)) / 12.0, 0.0, 1.0)[:, None]
        # blend the model depth in over deep ocean only, leaving shelves and any
        # real bathymetry (the present day) alone
        deep = np.clip((-out - 3000.0) / 2500.0, 0.0, 1.0) * sea * polefade
        out = out * (1.0 - deep * 0.55) + model_depth * (deep * 0.55)

        # ridge-parallel abyssal-hill fabric. The grain must run ALONG the ridge
        # (perpendicular to the distance gradient), and it has to be smooth --
        # the first version keyed the wave off a per-cell gradient direction,
        # which is noisy and threw isolated spikes rather than long hills. Use
        # the distance field itself as the phase, so the corrugations are
        # parallel to the ridge by construction, then blur so they read as hills
        # rather than a grating.
        from scipy import ndimage as _nd
        raw = np.sin(dist * 4.2) * np.sin(dist * 1.7 + 0.5)
        fab = _nd.gaussian_filter(raw, sigma=(1.2, 1.2)) * 70.0
        fab *= np.clip(1.0 - age_myr / 110.0, 0.12, 1.0) * polefade
        out = out + np.where(sea & (out < -2600), fab, 0.0)

    # 2) plateaus and microcontinents ------------------------------------
    if PLATEAUS:
        target, pmask = _plateau_field(out.shape, age, reconstructor)
        valid = target > -1e8
        # raise the floor toward the plateau target where the blob is, but never
        # pull a continent DOWN: only apply where the target is higher than the
        # ground, or the ground is ocean
        raise_to = (valid & ((target > out) | sea))
        blend = np.clip(pmask, 0.0, 1.0) * raise_to
        out = np.where(raise_to, out * (1.0 - blend) + target * blend, out)
        if verbose:
            em = emergent_names(age)
            print(f"    plateaus: {int((pmask > 0.05).sum())} cells seeded, "
                  f"emergent: {em or 'none'}")

    return out
