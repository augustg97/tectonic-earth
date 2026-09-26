"""Re-derive every field that depends on _e, for all 251 keyframes, after an
elevation re-skin (bake_relief.py, reskin_seafloor.py): _t for the past (the
future's comes from rebuild_future.py), _q, _x, _d, _w and the present day's
real lakes, _f with the relief deficit, then the manifest. Ends with a census:
every derived file must be newer than its _e.

    ../venv/bin/python rederive_fields.py          # ~15 min on 12 workers

Guarded by __main__: macOS starts pool workers by re-importing the script, and
an unguarded driver re-ran every step in each worker.
"""
import os, sys, time, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
import warnings; warnings.filterwarnings("ignore")

F = "../web/fields/"
ALL = list(range(-250, 0, 5)) + list(range(0, 1001, 5))
PAST = list(range(0, 1000, 5))          # build_tectonic's own range (the oldest has no displacement)


def stem(a):
    return "fut_%04d" % abs(a) if a < 0 else ("phan_%04d" % a if a <= 540 else "pre_%04d" % a)


_ROT = {}


def tect(a):
    import build_tectonic as BT
    if "rot" not in _ROT:
        import pygplates as pg, paleo_tracks as PT
        _ROT["rot"] = pg.RotationModel(PT.ROT)
    BT.bake(a, _ROT["rot"], quiet=True)
    return a


def surface(a):
    import build_surface as BS
    return BS.build_one(stem(a), verbose=False) is not None


def lakes(a):
    import bake_lakes as BL
    BL.bake_one(F + stem(a) + "_e.avif")
    return a


def fore(a):
    import build_foreland as BFL
    BFL.bake(a, quiet=True)
    return a


def main():
    """--future: only the 50 future keyframes (after rebuild_future.py, which
    writes their _t itself); the past's _t and the present-day lakes are
    left alone."""
    from multiprocessing import Pool
    global ALL
    future_only = "--future" in sys.argv
    if future_only:
        ALL = list(range(-250, 0, 5))
    # --ages A,B,...: only these (e.g. the 0-35 Ma the rain anchor rewrote;
    # lakes and surface drainage read the rain field)
    if "--ages" in sys.argv:
        ALL = [int(x) for x in sys.argv[sys.argv.index("--ages") + 1].split(",")]
        future_only = all(a < 0 for a in ALL)
    t0 = time.time()
    st = lambda m: print("[%5.0fs] %s" % (time.time() - t0, m), flush=True)
    if not future_only and "--ages" not in sys.argv:
        with Pool(12) as p:
            p.map(tect, PAST, chunksize=4)
        st("tectonic _t: %d" % len(PAST))
    import build_foldphase as BFP, build_drainphase as BDP
    with Pool(12) as p:
        q = [r for r in p.map(BFP.bake, ALL, chunksize=4) if r]
    st("fold coordinates _q: %d" % len(q))
    with Pool(12) as p:
        x = [r for r in p.map(BDP.bake, ALL, chunksize=4) if r]
    st("drainage coordinates _x: %d" % len(x))
    with Pool(12) as p:
        d = sum(p.map(surface, ALL, chunksize=4))
    st("surface _d: %d" % d)
    with Pool(12) as p:
        p.map(lakes, ALL, chunksize=4)
    st("lakes _w: %d" % len(ALL))
    if not future_only and 0 in ALL:
        import subprocess
        subprocess.check_call([sys.executable, "bake_present_lakes.py"])
        st("present-day lakes (Natural Earth) rewritten")
    with Pool(12) as p:
        p.map(fore, ALL, chunksize=4)
    st("foreland + deficit _f: %d" % len(ALL))
    import refresh_manifest as RM
    RM.main()
    st("manifest refreshed")
    # census: every derived file must be newer than its _e
    stale = []
    for a in ALL:
        te = os.path.getmtime(F + stem(a) + "_e.avif")
        kinds = ("q", "x", "d", "w", "f") + (("t",) if a < 1000 else ())
        for k in kinds:
            p = F + stem(a) + "_" + k + ".webp"
            if not os.path.exists(p) or os.path.getmtime(p) < te:
                stale.append(stem(a) + "_" + k)
    print("STALE:", stale[:20], len(stale))
    print("RELIEF-CHAIN-DONE" if not stale else "RELIEF-CHAIN-INCOMPLETE", flush=True)


if __name__ == "__main__":
    main()
