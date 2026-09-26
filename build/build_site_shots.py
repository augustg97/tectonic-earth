"""Re-take the screenshots the render audits read, whenever they are stale.

audit_deeptime, audit_island_biomes and audit_land_grain measure SHOTS on disk,
not the app, so they only protect what was last rendered. For seven weeks they
read files from 9 and 11 August while the shader changed under them: the
Permian desert check "passed" on an August picture (2026-09-26). A shot older
than the shader, the app or any field is no test at all, so the build re-takes
every shot whose file is missing or older than the newest of those, and
refuses to go on if one does not land.

Framings live in each audit as SHOTS = [(name, lon, lat, age, zoom)]; they are
taken with clouds off on the live terrain path (the ground is what is audited),
at the 760 px the audits were written for.

    ../venv/bin/python -c "import build_site_shots as B; B.refresh(force=True)"
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
VERIFY = os.path.join(HERE, "verify")
QUERY = "nolabels=1&clouds=0&shotsize=760&lite=0&quick=1&settle=3000"


def framings():
    import audit_deeptime, audit_island_biomes, audit_land_grain   # noqa: E401
    out = list(audit_deeptime.SHOTS) + list(audit_land_grain.SHOTS)
    out += [(n, lon, lat, 0, z) for n, lon, lat, z in audit_island_biomes.SHOTS]
    return out


def newest_input():
    """The newest mtime among what a shot depends on: the shader, the app, the
    per-keyframe fields and the labels -- and the audits themselves, so that
    editing a framing in SHOTS re-takes it (a file shot at the old framing is
    fresh by date and wrong by place)."""
    t = 0.0
    for p in ("shaders.js", "app.js", "labels.json"):
        t = max(t, os.path.getmtime(os.path.join(WEB, p)))
    for p in ("audit_deeptime.py", "audit_island_biomes.py", "audit_land_grain.py"):
        t = max(t, os.path.getmtime(os.path.join(HERE, p)))
    with os.scandir(os.path.join(WEB, "fields")) as it:
        for e in it:
            if e.is_file():
                t = max(t, e.stat().st_mtime)
    return t


def stale(shots, since):
    bad = []
    for n, *_ in shots:
        p = os.path.join(VERIFY, n + ".png")
        if not os.path.exists(p) or os.path.getmtime(p) < since:
            bad.append(n)
    return bad


def refresh(force=False):
    shots = framings()
    since = newest_input()
    todo = [s for s in shots if force or s[0] in stale(shots, since)]
    if not todo:
        print("  audit shots: all %d newer than the shader, app and fields" % len(shots), flush=True)
        return True
    print("  audit shots: re-taking %d of %d (older than the shader, app or fields)"
          % (len(todo), len(shots)), flush=True)
    jobs = []
    for k in range(0, len(todo), 5):
        chunk = todo[k:k + 5]
        q = "shots=" + ";".join("%s.png,%g,%g,%g,%g" % s for s in chunk) + "&" + QUERY
        jobs.append({"name": "auditshots_%d" % k, "query": q,
                     "expect": [s[0] + ".png" for s in chunk], "timeout": 600})
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(jobs, f)
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "verify_run.py"), path])
    finally:
        os.remove(path)
    left = stale(shots, since) if not force else [s[0] for s in todo
                                                   if not os.path.exists(os.path.join(VERIFY, s[0] + ".png"))]
    if r.returncode != 0 or left:
        print("  audit shots: NOT all landed: %s" % (left or "(runner failed)"), flush=True)
        return False
    return True


if __name__ == "__main__":
    sys.exit(0 if refresh(force="--force" in sys.argv) else 1)
