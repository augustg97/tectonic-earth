"""Static file server for local preview.

`python -m http.server` cannot be used here: its argparse setup evaluates
os.getcwd() at import time, which the sandbox refuses, so it dies before it can
serve anything. This binds the directory explicitly instead.
"""
import functools, http.server, os, socketserver, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass


if __name__ == "__main__":
    handler = functools.partial(Quiet, directory=os.path.abspath(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"serving {os.path.abspath(ROOT)} on http://127.0.0.1:{PORT}")
        sys.stdout.flush()
        httpd.serve_forever()
