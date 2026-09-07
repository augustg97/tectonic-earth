"""Run _verify.html jobs headless on this machine's GPU, ONE AT A TIME, and
wait for each job's output files BY NAME.

    ../venv/bin/python verify_run.py jobs.json          # a list of jobs
    ../venv/bin/python verify_run.py NAME 'query' out1 [out2 ...]

jobs.json is a list of {"name", "query", "expect": [...], "timeout": s}; the
query is the part after `_verify.html?` and the expected files are names under
build/verify/. Every job gets a fresh Chrome profile (a cached page has produced
byte-identical "A/B" statistics before), Chrome runs on ANGLE Metal (the real
GPU), and it is killed by the PID this script launched -- never by a pattern,
which matches the shell that runs it (README 7.11). A job that does not
produce its files inside the timeout is reported as MISSING, and the run goes
on to the next job; the exit status says whether every job landed.

The receiver is proved by round-trip, not by an open port (see shoot.py).
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify")
RECV = "http://127.0.0.1:8901/"
PAGE = "http://127.0.0.1:8899/_verify.html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = "/private/tmp/tectonic-verify-run-profile"


def _roundtrip():
    probe = os.path.join(VERIFY, "_verify_run_selftest.png")
    if os.path.exists(probe):
        os.remove(probe)
    try:
        urllib.request.urlopen(
            urllib.request.Request(RECV + "_verify_run_selftest.png",
                                   data=base64.b64encode(b"ok"), method="POST"),
            timeout=4).read()
    except (urllib.error.URLError, OSError):
        return False
    for _ in range(20):
        if os.path.exists(probe):
            os.remove(probe)
            return True
        time.sleep(0.1)
    return False


def _port_up(port):
    import socket
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def run_job(job):
    name, query = job["name"], job["query"]
    expect = job.get("expect") or [name + ".json.png"]
    timeout = job.get("timeout", 150)
    paths = [os.path.join(VERIFY, e) for e in expect]
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(PROFILE):
        shutil.rmtree(PROFILE, ignore_errors=True)
    url = PAGE + "?" + query
    t0 = time.time()
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--use-angle=metal", "--user-data-dir=" + PROFILE,
         "--no-first-run", "--window-size=1400,1100", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = False
    while time.time() - t0 < timeout:
        if all(os.path.exists(p) for p in paths):
            ok = True
            break
        if proc.poll() is not None:
            break
        time.sleep(1.0)
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    missing = [e for e, p in zip(expect, paths) if not os.path.exists(p)]
    print("  %-28s %5.0f s  %s" % (name, time.time() - t0,
                                   "landed" if ok else "MISSING: " + ", ".join(missing)),
          flush=True)
    if ok:
        for e, p in zip(expect, paths):
            if e.endswith(".json.png"):
                try:
                    d = json.loads(open(p, "rb").read().decode())
                    print("    " + json.dumps(d)[:600], flush=True)
                except Exception as ex:  # a PNG-named JSON that is not JSON
                    print("    (unreadable: %s)" % ex, flush=True)
    return ok


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if len(args) == 1 and args[0].endswith(".json"):
        jobs = json.load(open(args[0]))
    else:
        jobs = [{"name": args[0], "query": args[1], "expect": args[2:] or None}]
    if not os.path.exists(CHROME):
        print("verify_run: no Chrome at %s" % CHROME)
        return 1
    if not _port_up(8899):
        print("verify_run: nothing serving on 8899 (build/serve.py 8899)")
        return 1
    if not _roundtrip():
        print("verify_run: the receiver on 8901 is not writing to build/verify "
              "(build/verify_server.py)")
        return 1
    print("verify_run: %d job(s), Chrome on ANGLE Metal, receiver proved by round-trip" % len(jobs), flush=True)
    bad = 0
    for job in jobs:
        if not run_job(job):
            bad += 1
    print("verify_run: %d/%d landed  VERIFY-RUN-DONE" % (len(jobs) - bad, len(jobs)), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
