"""Static file server for local preview.

`python -m http.server` cannot be used here: its argparse setup evaluates
os.getcwd() at import time, which the sandbox refuses, so it dies before it can
serve anything. This binds the directory explicitly instead.
"""
import functools, http.server, os, socketserver, sys, threading


class Threaded(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Serve requests concurrently. The single-threaded default serialises
    every one of the ~750 texture fetches, which stalls a fresh tab at 0% when
    anything else is also loading."""
    daemon_threads = True
    allow_reuse_address = True

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass

    def end_headers(self):
        # index.html loads app.js and shaders.js with no version stamp, and
        # with no cache headers Chrome's heuristic cache served a stale app.js
        # across a plain reload (the display review of 2026-09-03: a knob the
        # new code defined was undefined in the tab). The fields and sheets
        # carry ?v= stamps and are the bulk of a load, so they stay cacheable;
        # everything else -- page, scripts, styles, JSON -- is fetched fresh.
        if not (self.path.startswith("/fields/") or self.path.startswith("/sheets/")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    handler = functools.partial(Quiet, directory=os.path.abspath(ROOT))
    with Threaded(("127.0.0.1", PORT), handler) as httpd:
        print(f"serving {os.path.abspath(ROOT)} on http://127.0.0.1:{PORT}")
        sys.stdout.flush()
        httpd.serve_forever()
