"""THE PLATE OVERLAY IN THE TERRAIN'S FRAME (3.17).

plates_time.json -- the boundary lines and plate names the app draws with the
boundaries layer -- comes from Merdith et al. (2021), in Merdith's own
reference frame; the terrain comes from PALEOMAP's. The two agree at 0 Ma and
part fast: the share of trench vertices that fall on dry land is 19% at 0 Ma,
33% at 20 and 41% at 150, and at 100 Ma no boundary runs along North
America's Pacific coast at all. So the overlay drew subduction zones across
continents and ridges beside the ones in the sea floor.

THE FIX IS A RUBBER SHEET, fitted per keyframe. Continental ground is sampled
at the present day and placed at the keyframe by BOTH models -- Merdith's
rotation of the plate that holds it today, and PALEOMAP's. A single best-fit
rotation takes Merdith's placement to PALEOMAP's (the difference of reference
frames); what it leaves over (relative motions the two models disagree about)
is carried as a residual displacement, spread from the samples with a
Gaussian of SIGMA_KM and fading to the pure rotation in open ocean, where no
continent says otherwise. Every boundary vertex and plate label is moved
through it. Near a continent the lines land where that continent is; in mid
ocean they keep the model's own geometry, rotated.

The FUTURE keeps its engine's own lines, already in the terrain's frame. The
PRECAMBRIAN is left as it was: its terrain is authored craton poses, a third
model (MODEL-GAPS).

The raw Merdith file is kept at cache/plates_time_merdith.json (made from the
current plates_time.json on first run; build_plates_gplates.py rewrites it),
so the reframe is idempotent.

    ../venv/bin/python reframe_plates.py            # every Phanerozoic keyframe
    ../venv/bin/python reframe_plates.py --stats    # trench vertices on land, before and after
"""
import json
import os
import shutil
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
PT_JSON = os.path.join(WEB, "plates_time.json")
RAW = os.path.join(HERE, "cache", "plates_time_merdith.json")
MERDITH = os.path.join(HERE, "..", "data", "merdith2021", "SM2_X")
R_KM = 6371.0
SIGMA_KM = 700.0
SAMPLE_STEP = 3            # every n-th cell of the plate raster
LAST = 540


def _unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def _lonlat(v):
    v = v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)
    return np.degrees(np.arctan2(v[..., 1], v[..., 0])), np.degrees(np.arcsin(np.clip(v[..., 2], -1, 1)))


class Frames:
    """Both models' placements of present-day continental ground at an age."""

    def __init__(self):
        import pygplates
        import plate_field as PF
        import paleo_tracks as PT
        import trench_field as TF
        self.pg, self.PF = pygplates, PF
        self.rot_pm = pygplates.RotationModel(PT.ROT)
        self.rot_m = pygplates.RotationModel(os.path.join(MERDITH, "1000_0_rotfile_Merdith_et_al.rot"))
        ids, cov = PF.plate_raster(0.0)
        h, w = ids.shape
        Z = TF.elevation(0, w, h)
        lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
        lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
        LON, LAT = np.meshgrid(lon, lat)
        keep = cov & (Z > -1000.0)
        keep[::SAMPLE_STEP, :] &= True
        sub = np.zeros_like(keep)
        sub[::SAMPLE_STEP, ::SAMPLE_STEP] = True
        keep &= sub
        # poleward rows are oversampled on an equirectangular grid: thin them
        keep &= np.random.default_rng(7).random(keep.shape) < np.cos(np.radians(LAT)) + 0.05
        self.x0 = _unit(LON[keep], LAT[keep])
        self.pm_ids = ids[keep]
        # Merdith's plate for each point today: the resolved topologies at 0 Ma
        topo = [os.path.join(MERDITH, f) for f in (
            "1000-410-Topologies_Merdith_et_al.gpml", "1000-410-Convergence_Merdith_et_al.gpml",
            "1000-410-Divergence_Merdith_et_al.gpml", "1000-410-Transforms_Merdith_et_al.gpml",
            "410-250_plate_boundaries_Merdith_et_al.gpml", "250-0_plate_boundaries_Merdith_et_al.gpml",
            "TopologyBuildingBlocks_Merdith_et_al.gpml")]
        resolved = []
        pygplates.resolve_topologies(topo, self.rot_m, resolved, 0.0)
        part = pygplates.PlatePartitioner(resolved, self.rot_m)
        self._resolved0, self._part0 = resolved, part
        mids = np.zeros(len(self.x0), np.int64)
        lo, la = _lonlat(self.x0)
        for i in range(len(self.x0)):
            p = part.partition_point(pygplates.PointOnSphere(float(la[i]), float(lo[i])))
            mids[i] = p.get_feature().get_reconstruction_plate_id() if p is not None else -1
        self.m_ids = mids
        print("  frames: %d continental samples, %d PALEOMAP plates, %d Merdith plates"
              % (len(self.x0), len(np.unique(self.pm_ids)), len(np.unique(mids))), flush=True)

    def _place(self, rot, ids, age):
        out = np.full_like(self.x0, np.nan)
        for pid in np.unique(ids):
            if pid < 0:
                continue
            m = ids == pid
            ax, an = self.PF.euler(rot, int(pid), float(age), 0.0)
            if ax is None and an == 0.0 and pid != 0:
                continue
            out[m] = self.PF.rodrigues(self.x0[m], ax, an)
        return out

    def pairs(self, age):
        if age > LAST:
            return self._pre_pairs(age)
        pm = self._place(self.rot_pm, self.pm_ids, age)
        mm = self._place(self.rot_m, self.m_ids, age)
        ok = np.isfinite(pm).all(1) & np.isfinite(mm).all(1)
        return mm[ok], pm[ok]

    # ---- the Precambrian: the terrain is the authored craton poses (a third
    # model), so the pairs come from the crust frame build_preframe.py built:
    # a craton's 540 Ma footprint goes to the present by its handoff rotation
    # Q_k, and back out to the keyframe both by Merdith (the plate that holds
    # that ground today) and by the craton's own poses.
    def _pre_setup(self):
        if getattr(self, "_pre", None) is not None:
            return
        import build_preframe as BP
        import precambrian as PRE
        w, h = 512, 256
        own = PRE.craton_owner(BP.HANDOFF, w, h)
        lon = (np.arange(w) + 0.5) / w * 360.0 - 180.0
        lat = 90.0 - (np.arange(h) + 0.5) / h * 180.0
        LON, LAT = np.meshgrid(lon, lat)
        keep = (own >= 0) & (np.random.default_rng(3).random(own.shape) < np.cos(np.radians(LAT)) + 0.05)
        X540 = _unit(LON[keep], LAT[keep])
        kk = own[keep]
        Q = BP._handoff_frames()
        P540 = BP._poses(BP.HANDOFF)
        names = PRE.CRATON_NAMES
        x0 = np.zeros_like(X540)
        for k, n in enumerate(names):
            m = kk == k
            if m.any():
                x0[m] = X540[m] @ Q[n].T
        mids = np.zeros(len(x0), np.int64)
        lo, la = _lonlat(x0)
        part = self._part0
        for i in range(len(x0)):
            p = part.partition_point(self.pg.PointOnSphere(float(la[i]), float(lo[i])))
            mids[i] = p.get_feature().get_reconstruction_plate_id() if p is not None else -1
        self._pre = (X540, kk, x0, mids, P540, names, BP)

    def _pre_pairs(self, age):
        self._pre_setup()
        X540, kk, x0, mids, P540, names, BP = self._pre
        Pa = BP._poses(age)
        app = np.full_like(X540, np.nan)
        for k, n in enumerate(names):
            m = kk == k
            if m.any() and n in Pa:
                app[m] = X540[m] @ (Pa[n] @ P540[n].T).T
        save = self.x0
        self.x0 = x0
        try:
            mm = self._place(self.rot_m, mids, age)
        finally:
            self.x0 = save
        ok = np.isfinite(app).all(1) & np.isfinite(mm).all(1)
        return mm[ok], app[ok]


def _kabsch(A, B):
    """Rotation R minimising sum |R a - b|^2."""
    H = A.T @ B
    U, _S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, 1.0, d])
    return Vt.T @ D @ U.T


class Sheet:
    def __init__(self, mm, pm):
        self.R = _kabsch(mm, pm)
        self.src = mm
        self.res = pm - mm @ self.R.T
        self.tree = cKDTree(mm)
        self.sig = SIGMA_KM / R_KM

    def __call__(self, V):
        V = np.asarray(V, np.float64)
        out = V @ self.R.T
        chord = 2.0 * np.sin(3.0 * self.sig / 2.0)
        idx = self.tree.query_ball_point(V, chord)
        for i, nb in enumerate(idx):
            if not nb:
                continue
            nb = np.asarray(nb)
            d = np.arccos(np.clip(self.src[nb] @ V[i], -1.0, 1.0))
            w = np.exp(-0.5 * (d / self.sig) ** 2)
            out[i] += (w[:, None] * self.res[nb]).sum(0) / (w.sum() + 1.0)
        return out / np.linalg.norm(out, axis=1, keepdims=True)


def _raw():
    if not os.path.exists(RAW):
        os.makedirs(os.path.dirname(RAW), exist_ok=True)
        shutil.copy(PT_JSON, RAW)
        print("  kept the raw Merdith file at", os.path.relpath(RAW, HERE))
    return json.load(open(RAW))


def _split(pts):
    runs, cur = [], []
    for p in pts:
        if cur and abs(p[0] - cur[-1][0]) > 180:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    return runs


def reframe(frames, raw, age):
    fr = raw[str(age)]
    if age == 0:
        return fr
    mm, pm = frames.pairs(age)
    sheet = Sheet(mm, pm)
    out = {"b": [], "p": []}
    for b in fr["b"]:
        P = np.asarray(b["p"], np.float64)
        lo, la = _lonlat(sheet(_unit(P[:, 0], P[:, 1])))
        pts = [[round(float(x), 2), round(float(y), 2)] for x, y in zip(lo, la)]
        for run in _split(pts):
            out["b"].append({"c": b["c"], "p": run})
    for p in fr["p"]:
        q = dict(p)
        lo, la = _lonlat(sheet(_unit(np.array([float(p["lon"])]), np.array([float(p["lat"])]))))
        q["lon"], q["lat"] = round(float(lo[0]), 1), round(float(la[0]), 1)
        out["p"].append(q)
    return out


def craton_share(fr, age):
    """Precambrian: the share of boundary vertices of any class that fall inside
    a craton the terrain draws (lower is better: boundaries run between them)."""
    import precambrian as PRE
    own = PRE.craton_owner(age, 720, 360)
    P = [np.asarray(b["p"], np.float64) for b in fr["b"]]
    P = np.concatenate(P)
    x = np.clip(((P[:, 0] + 180.0) / 360.0 * 720).astype(int), 0, 719)
    y = np.clip(((90.0 - P[:, 1]) / 180.0 * 360).astype(int), 0, 359)
    inner = own >= 0
    from scipy.ndimage import binary_erosion
    inner = binary_erosion(inner, iterations=6)          # deep inside, not on a margin
    return float(inner[y, x].mean())


def land_share(fr, age):
    import trench_field as TF
    Z = TF.elevation(age, 1024, 512)
    P = [np.asarray(b["p"], np.float64) for b in fr["b"] if b.get("c") == "trench"]
    if not P:
        return float("nan")
    P = np.concatenate(P)
    z = TF._sample(Z, _unit(P[:, 0], P[:, 1]))
    return float((z > 0).mean())


def main(argv):
    raw = _raw()
    frames = Frames()
    if "--pre-stats" in argv:
        for age in (545, 600, 700, 800, 900, 1000):
            new = reframe(frames, raw, age)
            print("  %4d Ma  boundary vertices deep inside a craton: Merdith frame %2.0f%%  reframed %2.0f%%"
                  % (age, 100 * craton_share(raw[str(age)], age), 100 * craton_share(new, age)), flush=True)
        return 0
    if "--stats" in argv:
        for age in (0, 20, 50, 100, 150, 250, 400, 540):
            new = reframe(frames, raw, age)
            print("  %4d Ma  trench vertices on land: Merdith frame %2.0f%%  reframed %2.0f%%"
                  % (age, 100 * land_share(raw[str(age)], age), 100 * land_share(new, age)), flush=True)
        return 0
    t0 = time.time()
    cur = json.load(open(PT_JSON))
    n = 0
    for age in range(5, LAST + 1, 5):
        cur[str(age)] = reframe(frames, raw, age)
        n += 1
    with open(PT_JSON, "w") as fh:
        json.dump(cur, fh, separators=(",", ":"))
    print("plates_time.json: %d Phanerozoic keyframes reframed onto the terrain, %.1f min"
          % (n, (time.time() - t0) / 60.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
