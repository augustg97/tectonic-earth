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
import os

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "data", "merdith2021", "SM2_X")
ROT = os.path.join(MODEL, "1000_0_rotfile_Merdith_et_al.rot")
STATIC = os.path.join(MODEL, "shapes_static_polygons_Merdith_et_al.gpml")


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

    def track(self, lon, lat, age_max, step=5):
        """[[age, lon, lat], ...] from 0 to age_max along the point's plate.

        A single finite rotation per age -- no integration, so no drift or pole
        blow-up. Points are rounded to 0.1 deg; runs of a stationary plate are
        left in so the app can interpolate cleanly.
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
                out.append([int(a), round(lo, 1), round(la, 1)])
            except Exception:
                break
            a += step
        return out, pid
