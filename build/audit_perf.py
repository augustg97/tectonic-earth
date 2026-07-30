"""The keyframe-crossing storm gate (perf audit P9, MODEL-GAPS section P).

WHAT IT PROTECTS. The 2026-07-30 audit measured a ~153 ms main-thread stall on
EVERY keyframe crossing: ten field kinds per keyframe, decoded and uploaded
synchronously at first bind, behind a texture cache sized for six kinds. The
fix is a pipeline (decode off-thread, byte-budgeted cache, idle-time warmers,
budgeted cold binds) whose whole value is that a crossing binds textures that
are ALREADY resident. Nothing about that is visible in a still, and the next
field kind added to FIELD_KINDS would silently re-create the stall -- this
gate is how it shows up before a deploy instead of on the live site.

WHAT IT MEASURES. Drives the real app headless, warms a keyframe pair the way
playback would, then crosses three boundaries and counts texture uploads that
land inside the crossing frame itself. Count-based, not time-based, so it is
valid even when headless Chrome falls back to software GL.

PASS: every crossing carries <= 2 synchronous uploads (0 is typical; slack for
a straggler the warmer had not reached). The numbers print on pass as well --
a gate that is silent when green is unreadable exactly when it matters.

    ../venv/bin/python audit_perf.py           # exits non-zero on failure

Needs Google Chrome. If Chrome is missing the gate SKIPS LOUDLY and exits 0 --
a deploy from a machine without Chrome should not be blocked, but the skip has
to be impossible to mistake for a pass.
"""
import base64
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
OUT = os.path.join(HERE, "verify", "audit_storm.json.png")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SERVE_PORT = 8899
RECV_PORT = 8901
MAX_UPLOADS = 2


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


def main():
    if not os.path.exists(CHROME):
        print("audit_perf: SKIPPED -- Google Chrome not found at the expected "
              "path, so the crossing-storm gate DID NOT RUN.")
        return 0

    procs = []
    try:
        if not _port_up(SERVE_PORT):
            procs.append(subprocess.Popen(
                [sys.executable, os.path.join(HERE, "serve.py"), str(SERVE_PORT)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if not _port_up(RECV_PORT):
            procs.append(subprocess.Popen(
                [sys.executable, os.path.join(HERE, "verify_server.py")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(1.0)

        if os.path.exists(OUT):
            os.remove(OUT)
        chrome = subprocess.Popen(
            [CHROME, "--headless=new", "--no-first-run",
             "--user-data-dir=/tmp/tectonic-audit-perf-profile",
             "--window-size=1400,1100",
             f"http://127.0.0.1:{SERVE_PORT}/_verify.html?storm=audit_storm"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 150
        while time.time() < deadline and not os.path.exists(OUT):
            time.sleep(2)
        chrome.kill()

        if not os.path.exists(OUT):
            print("audit_perf: FAIL -- the headless run produced no result "
                  "inside 150 s (boot failure or a hung crossing).")
            return 1

        data = json.loads(open(OUT, "rb").read().decode())
        worst = 0
        print("audit_perf: keyframe-crossing storm gate")
        for c in data["crossings"]:
            worst = max(worst, c["uploads"])
            print(f"  cross to {c['age']:>6} Ma: {c['uploads']} synchronous "
                  f"uploads, {c['ms']} ms step")
        if worst > MAX_UPLOADS:
            print(f"audit_perf: FAIL -- a crossing paid {worst} synchronous "
                  f"uploads (limit {MAX_UPLOADS}). The warm-ahead pipeline is "
                  f"not covering a field kind; see MODEL-GAPS section P.")
            return 1
        print(f"audit_perf: PASS -- worst crossing paid {worst} synchronous "
              f"uploads (limit {MAX_UPLOADS}).")
        return 0
    finally:
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    sys.exit(main())
