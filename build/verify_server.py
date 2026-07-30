"""Receive rendered frames from the running app and write them to disk.

WHY THIS EXISTS. Visual verification of this project kept failing, and never for
the reason it appeared to. Three separate causes, all of which produce the same
symptom -- a screenshot that does not show what you just asked for:

  1. A hidden browser pane gets no requestAnimationFrame, so the app never draws
     and the capture returns the PREVIOUS frame. (APP.step() drives a frame by
     hand; it existed all along and was not being used.)
  2. A hidden pane also has a 0x0 VIEWPORT. innerWidth is 0, the camera aspect
     is NaN, and any screen-space check silently returns null. This is the one
     that mattered most, because it makes the page look frozen when it is simply
     the wrong size.
  3. Anchor-click downloads need a visible document, so even a correct capture
     could not reach the filesystem.

APP.lookAt and APP.snap fix (1) and (2). This fixes (3): the page POSTs the PNG
here and it lands in build/verify/, where it can be opened and actually looked
at. No pane visibility, no user gesture, no download folder involved.

    ../venv/bin/python verify_server.py &        # port 8901

Then, in the page:

    APP.lookAt(16, 37, {age: 5, zoom: 1.7})      # returns {ok, offNDC, ...}
    APP.shoot('med_5Ma', 620)                    # POSTs; returns the path

ALWAYS check lookAt's ok flag before believing the image. A camera pointed at
the wrong place renders perfectly happily.
"""
import base64
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify")
PORT = 8901


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", self.path.lstrip("/")) or "shot"
        if not name.endswith(".png"):
            name += ".png"
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, name)
        with open(path, "wb") as f:
            f.write(base64.b64decode(body))
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(path.encode())
        print(f"  wrote {path}  ({len(body) // 1024} KB b64)", flush=True)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(f"verify receiver on http://127.0.0.1:{PORT}  ->  {OUT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
