"""Re-skin _e and _o with the mountain relief (relief.py), in parallel, for every
keyframe the relief can change: 55..1000 Ma and the future. Mirrors
reskin_seafloor.py per era (which is the serial equivalent and runs every
keyframe), so the result is what a full rebuild would write.

    ../venv/bin/python bake_relief.py              # all of them (~25 min on 12 workers)
    ../venv/bin/python bake_relief.py 300 -250     # some ages

Then re-derive what depends on _e: ../venv/bin/python rederive_fields.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
import warnings; warnings.filterwarnings("ignore")
import numpy as np

_G = {}


def _setup():
    if _G:
        return _G
    import build_fields as bf
    import paleo_tracks
    _G["bf"] = bf
    idx = bf.index_dems()
    _G["idx"] = idx
    _G["avail"] = np.array(sorted(idx.keys()))
    _G["rec"] = paleo_tracks.Reconstructor() if paleo_tracks.available() else None
    return _G


def dem_for(age):
    G = _setup()
    near = float(G["avail"][np.argmin(np.abs(G["avail"] - age))])
    return G["bf"].read_dem(G["idx"][near])


def save_eo(age, tag, Zhi):
    import relief
    from PIL import Image
    bf = _setup()["bf"]
    Zhi = relief.apply(Zhi, age, tag)
    mot = bf._load_motion(age, tag)
    Z2, ofield = bf.SF.apply(Zhi, age, reconstructor=bf._sf_reconstructor(), motion=mot)
    Z2 = bf.polar_lowpass(Z2)
    for _c in range(ofield.shape[2]):
        ofield[..., _c] = bf.polar_lowpass(ofield[..., _c])
    e = bf._gray(bf.enc_elev(bf.smooth_bathymetry(Z2)))
    o = Image.fromarray((np.clip(ofield, 0, 1) * 255 + 0.5).astype(np.uint8)
                        ).resize((bf.OCEAN_W, bf.OCEAN_H), Image.BILINEAR)
    bf._save(e, os.path.join(bf.OUT, bf.elev_name(tag, age)), bf.ELEV_Q)
    bf._save(o, os.path.join(bf.OUT, f"{tag}_{abs(age):04d}_o.webp"), bf.OCEAN_Q)


def one(age):
    t0 = time.time()
    try:
        G = _setup(); bf = G["bf"]
        if age < 0:
            if "gid" not in G:
                G["gid"] = bf.rasterise_groups()
                G["Zsrc"] = bf.resample_dem(dem_for(0), 900, 1800)
            frac = abs(age) / 250.0
            gh = bf.future_grid(frac, G["gid"], G["Zsrc"], bf.ELEV_H, bf.ELEV_W) - bf.sealevel_for(age)
            save_eo(age, "fut", gh)
        elif age <= 540:
            Zhi = bf.resample_dem(dem_for(age), bf.ELEV_H, bf.ELEV_W)
            Zhi = bf.EP.carve(Zhi, age, G["rec"])
            save_eo(age, "phan", Zhi)
        else:
            if "A_hi" not in G:
                G["A_hi"] = bf.resample_dem(dem_for(540), bf.ELEV_H, bf.ELEV_W)
            hi = bf.PRE.precambrian_grid(age, tw=bf.ELEV_W, th=bf.ELEV_H, flood=140.0)
            wq = float(np.clip((age - 540.0) / 20.0, 0, 1))
            wl = float(np.clip((age - 540.0) / 110.0, 0, 1))
            hi = bf.handoff_blend(G["A_hi"], hi, wq, wl)
            save_eo(age, "pre", hi)
        msg = "ok %5d  %.0fs" % (age, time.time() - t0)
    except Exception as ex:                       # report and go on; the census catches it
        import traceback
        msg = "FAIL %5d  %s\n%s" % (age, ex, traceback.format_exc()[-800:])
    print(msg, flush=True)
    return msg


if __name__ == "__main__":
    ages = [int(a) for a in sys.argv[1:]] or (list(range(55, 1001, 5)) + list(range(-5, -251, -5)))
    # future first (they are the slowest), then oldest first
    ages = sorted(ages, key=lambda a: (a >= 0, -a))
    from multiprocessing import Pool
    t0 = time.time()
    print("relief bake: %d keyframes on 12 workers" % len(ages), flush=True)
    with Pool(12) as pool:
        res = pool.map(one, ages, chunksize=1)
    bad = [r for r in res if not r.startswith("ok")]
    print("RELIEF-BAKE-DONE %d ok, %d failed, %.1f min" % (len(res) - len(bad), len(bad), (time.time() - t0) / 60), flush=True)
