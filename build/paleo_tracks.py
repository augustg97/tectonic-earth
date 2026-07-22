"""Reconstruct present-day feature positions along real plate motion.

Impact craters and large igneous provinces are catalogued at the coordinates
where we find them today, but the crust they sit on has travelled -- and the
old build (build_webdata.paleo_position) advected them along the block-matched
motion grid, which freezes over featureless ocean, has a poleward bias past
250 Ma, and was clamped to ADVECT_LIMIT=250. So an ocean crater sat still while
its plate moved out from under it.

Here every feature is assigned to the plate it sits on today and carried by that
plate's finite Euler rotation from the Merdith et al. (2021) model -- the same
method GPlates uses. That gives a continuous, physically-real track valid to
1000 Ma, at full plate speed on ocean floor and continent alike: Manicouagan
rides from Quebec to the Pangaean interior near Morocco by 215 Ma, a Pacific
abyssal crater moves ~45 degrees in 80 Myr instead of not at all.

If pyGPlates or the model files are missing this module reports unavailable and
the caller falls back to the old single-point advection, so the build still runs
in a bare environment.
"""
import json
import os

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "data", "merdith2021", "SM2_X")
ROT = os.path.join(MODEL, "1000_0_rotfile_Merdith_et_al.rot")
STATIC = os.path.join(MODEL, "shapes_static_polygons_Merdith_et_al.gpml")
OFFSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frame_offset.json")

# Merdith's absolute frame and Scotese's PaleoDEM frame are NOT the same.
# Paleomagnetism constrains latitude and orientation but says nothing about
# absolute longitude, so every published reconstruction picks its own, and this
# project draws terrain from one model while tracking features with another.
# Uncorrected, names are placed on Merdith's Earth and drawn on Scotese's: at
# 90 Ma the gap is ~9 degrees, by the Ordovician it is ~40, which is how the
# Western Interior Seaway label ended up over the Appalachians.
# frame_offset.py measures the shift per age by fitting back-advected land
# against the DEM's own land; this applies it. Latitude is untouched — the two
# models genuinely agree there and fudging it would hide real disagreement.
def _load_offsets():
    try:
        with open(OFFSET) as f:
            return {int(k): float(v) for k, v in json.load(f).items()}
    except Exception:
        return {}


_OFFSETS = _load_offsets()


def frame_shift(age):
    """Longitude correction from the Merdith frame into the DEM frame."""
    if not _OFFSETS:
        return 0.0
    a = abs(float(age))
    keys = sorted(_OFFSETS)
    if a <= keys[0]:
        return _OFFSETS[keys[0]]
    if a >= keys[-1]:
        return _OFFSETS[keys[-1]]
    for i in range(len(keys) - 1):
        k0, k1 = keys[i], keys[i + 1]
        if k0 <= a <= k1:
            f = 0.0 if k1 == k0 else (a - k0) / (k1 - k0)
            return _OFFSETS[k0] + (_OFFSETS[k1] - _OFFSETS[k0]) * f
    return 0.0


def available():
    if not (os.path.exists(ROT) and os.path.exists(STATIC)):
        return False
    try:
        import pygplates          # noqa: F401
        return True
    except Exception:
        return False


class Reconstructor:
    """Carry present-day points back along their plate's rotation."""

    def __init__(self):
        import pygplates
        self._pg = pygplates
        self.rot = pygplates.RotationModel(ROT)
        self.part = pygplates.PlatePartitioner([STATIC], self.rot,
                                               reconstruction_time=0)

    def plate_id(self, lon, lat):
        pt = self._pg.PointOnSphere(float(lat), float(lon))
        poly = self.part.partition_point(pt)
        return poly.get_feature().get_reconstruction_plate_id() if poly else 0

    def track(self, lon, lat, age_max, step=5, correct_frame=True):
        """[[age, lon, lat], ...] from 0 to age_max along the point's plate.

        A single finite rotation per age -- no integration, so no drift or pole
        blow-up. Points are rounded to 0.1 deg; runs of a stationary plate are
        left in so the app can interpolate cleanly.

        correct_frame applies the measured Merdith->PaleoDEM longitude shift, so
        the result is in the frame the terrain is actually drawn in. Pass False
        to get the raw model position.
        """
        pt = self._pg.PointOnSphere(float(lat), float(lon))
        pid = self.plate_id(lon, lat)
        out = []
        a = 0
        while a <= age_max + 1e-6:
            try:
                fr = self.rot.get_rotation(float(a), pid)
                p = fr * pt
                la, lo = p.to_lat_lon()
                if correct_frame:
                    lo = ((lo + frame_shift(a) + 180.0) % 360.0) - 180.0
                out.append([int(a), round(lo, 1), round(la, 1)])
            except Exception:
                break
            a += step
        return out, pid
