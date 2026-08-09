"""Take verification screenshots, and REFUSE to do it silently wrong.

Every element of this has failed at least once and cost a round:

  * the receiver died between sessions, so shots went nowhere and the next
    comparison failed on a missing file rather than on a missing receiver;
  * a DIFFERENT stale listener held port 8901 and wrote to a working directory
    it no longer had -- so the port was open, the POSTs succeeded, and nothing
    was ever written. **A listening socket is not proof.** The only proof is a
    round-trip: POST a byte, read it back off disk;
  * a probe receiver of mine took 8901 while the shot harness was using it, and
    the images landed in the probe directory. One port, one owner;
  * Chrome served a cached page, so two different builds produced byte-identical
    statistics. Fresh profile every run, no exceptions;
  * the harness stalled part way and left four of six shots, which reads as
    "the sixth framing is broken" rather than "the run did not finish".

So: ensure, PROVE, shoot, then verify every requested name actually arrived and
exit non-zero naming the ones that did not.

    ../venv/bin/python shoot.py NAME,LON,LAT,AGE[,ZOOM] [more...] [--size N]
"""
import base64
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
PAGE = "http://localhost:8899/_verify.html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = "/private/tmp/tectonic-shoot-profile"


def _listening(port):
    out = subprocess.run(["lsof", "-nP", "-iTCP:%d" % port, "-sTCP:LISTEN", "-t"],
                         capture_output=True, text=True).stdout.strip()
    return [int(p) for p in out.split()] if out else []


def _roundtrip():
    """The only honest test: write a byte through the receiver and read it back."""
    probe = os.path.join(VERIFY, "_shoot_selftest.png")
    if os.path.exists(probe):
        os.remove(probe)
    try:
        urllib.request.urlopen(
            urllib.request.Request(RECV + "_shoot_selftest.png",
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


def ensure_receiver():
    if _roundtrip():
        return True
    pids = _listening(8901)
    if pids:
        # Open but not writing HERE -- a stale listener from another session or
        # another tool. It will swallow every shot, so it has to go.
        print("  shoot: port 8901 held by pid(s) %s but not writing to build/verify"
              % pids + " -- replacing")
        for p in pids:
            subprocess.run(["kill", "-9", str(p)])
        time.sleep(1.0)
    py = os.path.join(HERE, "..", "venv", "bin", "python")
    subprocess.Popen([py, os.path.join(HERE, "verify_server.py")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    for _ in range(30):
        time.sleep(0.4)
        if _roundtrip():
            print("  shoot: receiver started and verified by round-trip")
            return True
    return False


def main():
    args = [a for a in sys.argv[1:]]
    size = 760
    nolabels = "--nolabels" in args
    if nolabels:
        args.remove("--nolabels")
    if "--size" in args:
        i = args.index("--size")
        size = int(args[i + 1])
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 2

    if not _listening(8899):
        print("  shoot: FAIL -- nothing serving on 8899; the page cannot load")
        return 1
    if not ensure_receiver():
        print("  shoot: FAIL -- could not get a receiver that writes to build/verify")
        return 1

    names = [s.split(",")[0] for s in args]
    for n in names:
        f = os.path.join(VERIFY, n + ".png")
        if os.path.exists(f):
            os.remove(f)

    if os.path.exists(PROFILE):
        shutil.rmtree(PROFILE, ignore_errors=True)
    url = "%s?shotsize=%d%s&shots=%s" % (PAGE, size,
                                        "&nolabels=1" if nolabels else "",
                                        ";".join(args))
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--use-angle=metal", "--user-data-dir=" + PROFILE,
         "--no-first-run", "--window-size=1280,960", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    deadline = time.time() + 40 + 22 * len(names)
    while time.time() < deadline:
        if all(os.path.exists(os.path.join(VERIFY, n + ".png")) for n in names):
            break
        time.sleep(2)
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

    missing = [n for n in names
               if not os.path.exists(os.path.join(VERIFY, n + ".png"))]
    got = len(names) - len(missing)
    if missing:
        print("  shoot: FAIL -- %d/%d landed; MISSING: %s"
              % (got, len(names), ", ".join(missing)))
        print("  shoot: do NOT read the frames that did land as a result -- the run"
              " did not finish, and a partial set reads like a broken framing.")
        return 1
    print("  shoot: %d/%d landed at %dpx" % (got, len(names), size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
