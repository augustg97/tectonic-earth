"""Bake every keyframe's WORLD SHEET on this machine's GPU and ship it (WP-10, plan A3).

A sheet is one keyframe's whole shaded world -- the terrain shader rendered
once into a 4096x2048 equirect target with the ocean mask in alpha -- and the
app's lite material draws the globe and the map from two of them per frame at
a few texture reads a pixel. The app can bake its own sheets on the fly; this
script bakes all 251 once, on a real GPU, and encodes them so that playback
and the ambient build never run the terrain shader at all.

    python3 bake_sheets.py                    # all keyframes, 4096 wide, into ../web/sheets
    python3 bake_sheets.py --range 90-110     # a slice
    python3 bake_sheets.py --width 2048       # the lean set (the ambient build's)
    python3 bake_sheets.py --quality 80       # AVIF quality (default 82)

It drives the real app headless through _verify.html?bake= (the same driver
the screenshot harness uses), waits for every requested sheet to land in
build/verify/, then encodes each PNG to AVIF with alpha into web/sheets/ and
writes web/sheets/manifest.json ({w, h, files: {age: file}}). build_site.py
copies web/sheets/ to docs/. Chrome is found at CHROME (env) or the usual
macOS / Linux paths; the bake needs a real GPU -- software GL takes minutes
per sheet and is only for verifying the pipeline.

A shader change invalidates every sheet: re-run this (about a minute of GPU
for the render, ten to twenty for the encode) and bump SHEET_V in index.html.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
VERIFY = os.path.join(HERE, "verify")
OUT = os.path.join(WEB, "sheets")
SERVE_PORT, RECV_PORT = 8899, 8901
CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/opt/pw-browsers/chromium",
]


def _port_up(port):
    import socket
    s = socket.socket(); s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port)); return True
    except OSError:
        return False
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=4096)
    ap.add_argument("--range", default=None, help="i0-i1 keyframe indices (timeline order)")
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--keep-png", action="store_true")
    ap.add_argument("--software", action="store_true", help="allow SwiftShader (very slow)")
    a = ap.parse_args()

    manifest = json.load(open(os.path.join(WEB, "fields", "manifest.json")))
    n = len(manifest)
    i0, i1 = (0, n - 1) if not a.range else [int(x) for x in a.range.split("-")]
    chrome = next((c for c in CHROME_CANDIDATES if c and os.path.exists(c)), None)
    if not chrome:
        raise SystemExit("bake_sheets: no Chrome found; set CHROME=/path/to/chrome")

    procs = []
    try:
        if not _port_up(SERVE_PORT):
            procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "serve.py"), str(SERVE_PORT)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if not _port_up(RECV_PORT):
            procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "verify_server.py")],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(1.0)
        os.makedirs(VERIFY, exist_ok=True)
        for i in range(i0, i1 + 1):
            p = os.path.join(VERIFY, "sheet_%03d.png" % i)
            if os.path.exists(p):
                os.remove(p)
        flags = ["--headless=new", "--no-first-run", "--user-data-dir=/tmp/tectonic-bake-profile",
                 "--window-size=1400,1000"]
        if a.software:
            flags += ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
        url = "http://127.0.0.1:%d/_verify.html?bake=%d-%d&sheet=%d" % (SERVE_PORT, i0, i1, a.width)
        print("bake_sheets: %d sheets at %dx%d via %s" % (i1 - i0 + 1, a.width, a.width // 2, chrome))
        chrome_p = subprocess.Popen([chrome] + flags + [url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        per = 240 if a.software else 6
        deadline = time.time() + 180 + per * (i1 - i0 + 1)
        want = ["sheet_%03d.png" % i for i in range(i0, i1 + 1)]
        while time.time() < deadline:
            have = [w for w in want if os.path.exists(os.path.join(VERIFY, w))]
            print("\r  %d / %d sheets landed" % (len(have), len(want)), end="", flush=True)
            if len(have) == len(want):
                break
            time.sleep(3)
        print()
        chrome_p.kill()
        missing = [w for w in want if not os.path.exists(os.path.join(VERIFY, w))]
        if missing:
            print("bake_sheets: %d sheet(s) never arrived: %s ..." % (len(missing), missing[:5]))
    finally:
        for p in procs:
            p.terminate()

    # Encode. AVIF with alpha: the ocean mask survives, and a shaded world is
    # photographic content, which is where AV1 earns its keep (README 7.13).
    from PIL import Image
    try:
        import pillow_avif  # noqa: F401
    except ImportError:
        raise SystemExit("bake_sheets: pip install pillow-avif-plugin")
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(OUT, "manifest.json")
    m = json.load(open(mpath)) if os.path.exists(mpath) else {"w": a.width, "h": a.width // 2, "files": {}}
    if m.get("w") != a.width:
        m = {"w": a.width, "h": a.width // 2, "files": {}}
    total = 0
    for i in range(i0, i1 + 1):
        src = os.path.join(VERIFY, "sheet_%03d.png" % i)
        if not os.path.exists(src):
            continue
        age = manifest[i]["age"]
        name = manifest[i]["e"].replace("_e.avif", "_s.avif").replace("_e.webp", "_s.avif")
        im = Image.open(src).convert("RGBA")
        im.save(os.path.join(OUT, name), "AVIF", quality=a.quality, speed=6)
        total += os.path.getsize(os.path.join(OUT, name))
        m["files"][str(age)] = name
        if not a.keep_png:
            os.remove(src)
        print("\r  encoded %s (%d/%d)" % (name, i - i0 + 1, i1 - i0 + 1), end="", flush=True)
    print()
    json.dump(m, open(mpath, "w"), separators=(",", ":"))
    print("bake_sheets: %d sheets in manifest, %.1f MB this run -> %s" % (len(m["files"]), total / 1e6, OUT))
    print("Now bump SHEET_V in web/index.html if sheets already shipped, and run build_site.py.")


if __name__ == "__main__":
    main()
