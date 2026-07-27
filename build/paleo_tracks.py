"""Reconstruct present-day feature positions along real plate motion.

Impact craters and large igneous provinces are catalogued at the coordinates
where we find them today, but the crust they sit on has travelled -- and the
old build (build_webdata.paleo_position) advected them along the block-matched
motion grid, which freezes over featureless ocean, has a poleward bias past
250 Ma, and was clamped to ADVECT_LIMIT=250. So an ocean crater sat still while
its plate moved out from under it.

Here every feature is assigned to the plate it sits on today and carried by that
plate's finite Euler rotation -- the same method GPlates uses. That gives a
continuous, physically-real track, at full plate speed on ocean floor and
continent alike: Manicouagan rides from Quebec to the Pangaean interior off
Morocco by 200 Ma, a Pacific abyssal crater moves ~45 degrees in 80 Myr instead
of not at all.

THE FRAME, AND WHY IT IS SCOTESE'S

Palaeomagnetism fixes palaeolatitude and orientation and says NOTHING about
absolute longitude, so every published reconstruction picks its own frame. This
pipeline draws terrain from Scotese & Wright's PaleoDEMs; tracking features in
anybody else's frame therefore places names on one Earth and draws them on
another. Through 2026 the tracks came from Merdith et al. (2021) and the gap was
patched with a smoothed RIGID longitude shift per age (frame_offset.py), which
helped -- craters on plausible terrain 80% -> 90% -- and could not close it,
because the real difference is regional, not rigid.

Scotese publishes his own rotations, and has since 2016. Using them makes the
mismatch zero BY CONSTRUCTION, and the rigid patch not merely unnecessary but
harmful: with one frame there is nothing left for it to correct and it would
inject the error it used to remove.

Measured over 53 present-day land points at ten ages against our own shipped
elevation field (Deep Research/modeling/frame_experiment.py), land-today crust
landing on abyssal plain -- which means the frame put it in the wrong ocean --
falls from 20% to 5%, better at every one of the ten ages and by most in the
Palaeozoic where the gap was worst (500 Ma: 40% -> 8%). Scored per feature
rather than on the average (modeling/regression_gate.py), the switch improves 58
tracked features, leaves 79 unchanged and moves 21 the other way, of which the
great majority are pre-existing errors it exposes rather than causes.

MERDITH IS STILL USED, for a different object: build_plates_gplates.py needs
resolved continuously-closing TOPOLOGIES to derive plate boundaries, and
PALEOMAP's polygon set does not provide them. Each model does what it is good
at -- Merdith the boundaries, PALEOMAP the frame the terrain is drawn in.

If pyGPlates or the model files are missing this module reports unavailable and
the caller falls back to the old single-point advection, so the build still runs
in a bare environment.
"""
import math
import os

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "data", "paleomap_gpm", "Scotese PaleoAtlas_v3",
                     "PALEOMAP Global Plate Model")
ROT = os.path.join(MODEL, "PALEOMAP_PlateModel.rot")
STATIC = os.path.join(MODEL, "PALEOMAP_PlatePolygons.gpml")

# PALEOMAP Plate Model m15g60_v2d3, CR Scotese 2016, CC-BY 4.0.
# 258 plate IDs, -250 -> 1100 Ma: the app's entire range, future included.
# The polygon set covers 100% of a 5-degree global grid at 0 Ma and leaves only
# 0.08% of it on plate 0 (the anchor, which never moves) -- checked, because a
# point that falls outside every polygon silently stays put instead of failing.


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
        self._polys = pygplates.FeatureCollection(STATIC)
        self.part = pygplates.PlatePartitioner(self._polys, self.rot,
                                               reconstruction_time=0)
        self._parts = {0: self.part}
        self._plume_cache = {}

    def plate_id(self, lon, lat):
        pt = self._pg.PointOnSphere(float(lat), float(lon))
        poly = self.part.partition_point(pt)
        return poly.get_feature().get_reconstruction_plate_id() if poly else 0

    def plume_plates(self, plon, plat, ring_deg=3.0):
        """Plate ids fed by a plume at (plon, plat) today.

        Usually one. Two where the plume sits on or beside a spreading axis, and
        that is not an edge case to tidy away -- it is why Tristan da Cunha built
        Walvis Ridge on the African plate AND the Rio Grande Rise on the South
        American one, why Galapagos built both the Cocos and the Carnegie ridges,
        and why Iceland's trail runs onto Greenland and the Faroes alike. Sample
        a small ring as well as the centre and take the distinct ids.
        """
        # Memoised: the answer depends only on the present-day partition, so it
        # is the same at every keyframe, and this is called for 53 plumes on each
        # of 251 of them -- nine partition_point calls apiece against a 471-
        # feature collection, which is most of a minute per full rebuild.
        key = (round(float(plon), 3), round(float(plat), 3), round(float(ring_deg), 3))
        hit = self._plume_cache.get(key)
        if hit is not None:
            return hit
        ids, order = set(), []
        pts = [(plon, plat)] + [
            (plon + ring_deg * math.cos(math.radians(b)) /
             max(math.cos(math.radians(plat)), 0.2),
             max(-89.0, min(89.0, plat + ring_deg * math.sin(math.radians(b)))))
            for b in range(0, 360, 45)]
        for lo, la in pts:
            pid = self.plate_id(lo, la)
            if pid and pid not in ids:
                ids.add(pid)
                order.append(pid)
        out = order or [0]
        self._plume_cache[key] = out
        return out

    def plume_track(self, plon, plat, T, max_age=110, step=5, pid=None):
        """Where a mantle-fixed plume's volcanoes have got to by time T.

        THE POINT OF A HOTSPOT is that it does not move with the plate. The plume
        sits in the mantle; the plate slides over it; the volcano built last is
        carried away while a new one grows in its place. So the chain is not a
        line drawn outward from the plume in the plate-motion direction -- that
        looks similar in one frame and is quite wrong across time, because the
        volcanoes stay pinned to the map while the plate slides under them.

        It is the set of volcanoes BORN AT the plume at times T+A, each carried
        forward to T on the plate that was over the plume then.

        WHICH PLATE, AND WHY IT IS ASKED AT THE PRESENT DAY. The natural question
        is "what covered the mantle point at the birth time", and with PALEOMAP
        it cannot be asked that way: its polygon set tiles the globe at 0 Ma and,
        reconstructed to any earlier age, covers only about 45% of it -- ocean
        basins open and the static polygons do not fill them. Measured: at 10, 40
        and 90 Ma the Hawaiian plume falls in a hole, so a birth-time partition
        returns nothing for the entire Hawaiian-Emperor chain. (This is exactly
        why build_plates_gplates keeps Merdith: resolved TOPOLOGIES tile the
        sphere at every age and static polygons do not.) So the plate is
        identified at the present day, where the coverage is complete, and held
        for the trail -- which is what a hotspot's own definition assumes anyway,
        and `plume_plates` above supplies the second plate where the assumption
        genuinely breaks.

        Returns [(lon, lat, edifice_age_Myr), ...], youngest first.
        """
        pt = self._pg.PointOnSphere(float(plat), float(plon))
        if pid is None:
            pid = self.plume_plates(plon, plat)[0]
        if not pid:
            return []
        out = []
        for A in range(0, int(max_age) + 1, int(step)):
            tb = int(round(T)) + A          # when this volcano was built
            if tb > 1000 or tb < 0:
                break
            if A == 0:
                out.append((float(plon), float(plat), 0.0))
                continue
            try:
                # born at tb, carried to T on that plate
                fr = self.rot.get_rotation(float(T), int(pid), float(tb))
            except Exception:
                continue
            if fr is None:
                continue
            p = fr * pt
            la, lo = p.to_lat_lon()
            out.append((float(lo), float(la), float(A)))
        return out

    def track(self, lon, lat, age_max, step=5):
        """[[age, lon, lat], ...] from 0 to age_max along the point's plate.

        A single finite rotation per age -- no integration, so no drift or pole
        blow-up. Points are rounded to 0.1 deg; runs of a stationary plate are
        left in so the app can interpolate cleanly.

        The result is already in the frame the terrain is drawn in, so there is
        no correction to apply and no `correct_frame` switch to get wrong.
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
