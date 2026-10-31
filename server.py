#!/usr/bin/env python3
"""Bridge PBN replay page, served from Render as a Web Service.

Python standard library only -- no third-party packages.

Endpoints:
  GET /                -> index.html
  GET /api/pbn-list    -> {"files": [{"name", "size", "url"}, ...]},
                          sorted by filename, *.pbn files directly in pbn/
  GET /pbn/<name>      -> that .pbn file as text/plain; charset=utf-8
  GET /health          -> {"ready": true}  (Render health check)
  GET /<static file>   -> other static files in the package root
                          (.html/.css/.js/.json/.png/.jpg/.svg/.ico only)

Security notes:
  * /pbn/<name> rejects directory traversal, absolute paths, and
    non-.pbn names. Files are only ever served from inside pbn/.
  * server.py itself, Dockerfile, render.yaml and .dockerignore are
    never served as static files.
  * CORS Access-Control-Allow-Origin * is added to /api and /pbn
    responses; it is harmless for same-origin fetches (the page calls
    the same origin) and lets the same files be fetched from elsewhere.

Run:  PORT=10000 python3 server.py   (Render sets $PORT itself)
"""

import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PBN_DIR = ROOT / "pbn"
STATIC_EXTS = {".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".svg", ".ico"}
NEVER_SERVE = {"server.py", "Dockerfile", "render.yaml", ".dockerignore"}


def pbn_files():
    """List *.pbn files directly in pbn/, sorted by filename."""
    if not PBN_DIR.is_dir():
        return []
    out = []
    for entry in sorted(PBN_DIR.iterdir(), key=lambda e: e.name):
        if not entry.is_file():
            continue
        if entry.name.startswith("."):
            continue
        if entry.suffix.lower() != ".pbn":
            continue
        out.append({
            "name": entry.name,
            "size": entry.stat().st_size,
            "url": "/pbn/" + urllib.parse.quote(entry.name),
        })
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "bridge-pbn-render/1.0"

    def log_message(self, fmt, *args):  # keep Render logs readable
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def _send(self, status, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _send_json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def _send_file(self, path, content_type):
        try:
            data = path.read_bytes()
        except OSError:
            self._send_json(404, {"error": "not found"})
            return
        self._send(200, data, content_type)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._send_file(ROOT / "index.html", "text/html; charset=utf-8")
            return

        if path == "/health":
            self._send_json(200, {"ready": True})
            return

        if path == "/api/pbn-list":
            self._send_json(200, {"files": pbn_files()})
            return

        if path.startswith("/pbn/"):
            raw = urllib.parse.unquote(path[len("/pbn/"):])
            # Reject traversal, separators, absolute paths, non-.pbn names.
            if (not raw or raw != raw.strip() or "/" in raw or "\\" in raw
                    or raw in (".", "..") or raw.startswith(".")
                    or not raw.lower().endswith(".pbn")):
                self._send_json(400, {"error": "invalid pbn filename"})
                return
            candidate = (PBN_DIR / raw).resolve()
            try:
                candidate.relative_to(PBN_DIR.resolve())
            except ValueError:
                self._send_json(400, {"error": "invalid pbn filename"})
                return
            if not candidate.is_file():
                self._send_json(404, {"error": "pbn file not found"})
                return
            self._send_file(candidate, "text/plain; charset=utf-8")
            return

        # Other static files in the package root only.
        name = urllib.parse.unquote(path.lstrip("/"))
        if (not name or "/" in name or "\\" in name or name.startswith(".")
                or name in NEVER_SERVE
                or Path(name).suffix.lower() not in STATIC_EXTS):
            self._send_json(404, {"error": "not found"})
            return
        candidate = (ROOT / name).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            self._send_json(404, {"error": "not found"})
            return
        if not candidate.is_file():
            self._send_json(404, {"error": "not found"})
            return
        ext = candidate.suffix.lower()
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".ico": "image/x-icon",
        }[ext]
        self._send_file(candidate, ctype)

    do_HEAD = do_GET


def main():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"bridge-pbn-render listening on 0.0.0.0:{port} (pbn dir: {PBN_DIR})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
