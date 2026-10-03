"""Read-only dashboard. Only explicit public endpoints are served."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from .readiness import status

def make_server(root: Path, host="127.0.0.1", port=8765):
    static = Path(__file__).parent/"web"
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?",1)[0]
            if path == "/api/status":
                body = json.dumps(status(root),allow_nan=False).encode()
                content_type = "application/json"
            elif path in ("/","/app.js","/style.css"):
                file = static/("index.html" if path=="/" else path[1:])
                body = file.read_bytes()
                content_type = {"html":"text/html","js":"text/javascript","css":"text/css"}[file.suffix[1:]]
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type",content_type+"; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    return ThreadingHTTPServer((host,port),Handler)
